"""α·β 검증 하네스 — "이 답이 데이터로 정해지는가" 를 숫자로 묻는다.

물음 넷:

  A. **포팅 충실도** — 그들이 보고한 파라미터를 우리 목적함수에 넣으면
     최적점 근처인가. (아니면 이 하네스로 잰 것은 그들 모델이 아니다.)
  B. **경계** — 최적해가 상자 경계에 붙는가. 붙으면 그 좌표는 데이터가 아니라
     상자가 정한 것이다.
  C. **축퇴** — 최적 RMSE 의 (1+ε) 안에 드는 파라미터들이 만드는 LAM/LLI 의
     폭. 폭이 크면 "α·β 가 맞다" 를 말할 수 없다.
  D. **비결정성** — 원본은 목적함수의 scale 을 `rand` 50 개로 잡는데 seed 가
     없다. seed 를 바꾸면 목적함수 자체가 달라진다. 그 크기를 잰다.

실행:

    python -m bms_balancing.verify port --data-root … --state pristine
    python -m bms_balancing.verify degeneracy --data-root … --state 300_0009
    python -m bms_balancing.verify scale-noise --data-root … --state pristine
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import NonlinearConstraint, minimize

from . import data as D
from .model import (LB5, UB5, Blend, HalfCell, Objective, average_duplicates,
                    degradation_modes)


def build(root: Path, source: str, state: str, si_source: str,
          w_dqdv: float = 0.0, use_peak_weight: bool = True,
          scale_seed: int = 0) -> Objective:
    # ⚠ 입력이 없으면 **적합을 시작하기 전에** 죽는다. 2026-09-10 실측:
    #   `degeneracy --state 300_0147 --source GITT` 가 기준(pristine) 적합
    #   24 회를 다 돌린 **뒤에** 대상 파일이 없다는 걸 알았다 (23 초 낭비, 그리고
    #   로그 첫 줄이 성공한 multistart 라 실패 원인이 가려졌다).
    hc = D.half_cell_path(root, source, state)
    if not hc.is_file():
        have = sorted(s2 for s2 in D.STATES
                      if D.half_cell_path(root, source, s2).is_file())
        other = [src for src in D.HALF_FILE if src != source
                 and D.half_cell_path(root, src, state).is_file()]
        raise SystemExit(
            f"반쪽전지 파일이 없다: {hc}\n"
            f"  `{source}` 에 있는 상태: {', '.join(have) or '(없음)'}\n"
            + (f"  `{state}` 는 `--source {other[0]}` 에는 있다.\n" if other else "")
            + "  (상태마다 반쪽전지를 따로 재는 파이프라인이라 없는 상태는 못 돈다)")
    half = HalfCell(hc, window=11, poly_order=3)
    si_c, si_v, gr_c, gr_v = D.load_literature(root, si_source)
    blend = Blend(si_c, si_v, gr_c, gr_v, window=11, poly_order=3)
    c, v = D.load_full_cell(root, state)
    return Objective(half, blend, c, v, window=11, poly_order=3,
                     w_pocv=1.0, w_dvdq=1.0, w_dqdv=w_dqdv,
                     use_peak_weight=use_peak_weight, scale_seed=scale_seed)


def multistart(obj: Objective, n_starts: int = 24, seed: int = 0,
               x0: np.ndarray | None = None, require_success: bool = True):
    """fmincon+MultiStart 대응 — L-BFGS-B 다중 시작.

    ⚠ 2026-09-10 리뷰 [A3]: 전 판은 `OptimizeResult.success` 를 보지 않아
      **비정상 종료한 결과를 성공한 fit 으로 채택**했다. 합성 반례에서
      success=False 결과가 그대로 best 와 all_sols 에 들어갔다. 이제
      기본으로 거른다. 거른 개수는 `multistart.last_stats` 와 stderr 에 남긴다
      — 조용히 버리면 그것대로 감사가 안 된다.
    """
    rng = np.random.default_rng(seed)
    starts = [np.asarray(x0, dtype=float)] if x0 is not None else []
    starts += list(LB5 + rng.random((n_starts, 5)) * (UB5 - LB5))
    best, best_val = None, np.inf
    all_sols = []
    stats = {"tried": 0, "raised": 0, "not_success": 0, "nonfinite": 0, "accepted": 0}
    bounds = list(zip(LB5, UB5))
    for s in starts:
        stats["tried"] += 1
        try:
            r = minimize(obj, s, method="L-BFGS-B", bounds=bounds,
                         options={"maxiter": 500, "ftol": 1e-12, "gtol": 1e-10})
        except Exception:                               # noqa: BLE001
            stats["raised"] += 1
            continue
        if not np.isfinite(r.fun):
            stats["nonfinite"] += 1
            continue
        if require_success and not bool(getattr(r, "success", True)):
            stats["not_success"] += 1
            continue
        stats["accepted"] += 1
        all_sols.append((float(r.fun), r.x.copy()))
        if r.fun < best_val:
            best, best_val = r.x.copy(), float(r.fun)
    multistart.last_stats = stats
    if stats["not_success"] or stats["raised"] or stats["nonfinite"]:
        print(f"[multistart] 시작점 {stats['tried']}개 중 채택 {stats['accepted']} — "
              f"비정상종료 {stats['not_success']} · 예외 {stats['raised']} · "
              f"비유한 {stats['nonfinite']}", file=sys.stderr)
    return best, best_val, all_sols


multistart.last_stats = {}


def active_bounds(p, tol=1e-6):
    names = ["a_PE", "b_PE", "a_NE", "b_NE", "gamma_Si"]
    hits = []
    for i, n in enumerate(names):
        if abs(p[i] - LB5[i]) < tol:
            hits.append(f"{n}=lb")
        if abs(p[i] - UB5[i]) < tol:
            hits.append(f"{n}=ub")
    return hits


# ── A. 포팅 충실도 ──────────────────────────────────────────────────────

#: 그들이 보고한 값 (exp10_si_source_sensitivity.csv, 반쪽전지=GITT)
REPORTED = {
    ("Li", "pristine"): [1.077218, -0.022949, 1.001342, 0.000309, 0.295099],
    ("Li", "300_0009"): [1.181472, -0.141171, 1.080759, None, 0.239466],
    ("Kunz", "pristine"): [1.097789, -0.038349, 1.058563, -0.013455, 0.260566],
    ("Kunz", "300_0009"): [1.190057, -0.147223, 1.162316, -0.014875, 0.186959],
}


def cmd_port(args):
    root = D.data_root(args.data_root)
    obj = build(root, args.source, args.state, args.si_source,
                w_dqdv=args.w_dqdv, scale_seed=args.seed)
    out = {"state": args.state, "si_source": args.si_source,
           "half_cell": args.source, "c_cell": obj.c_cell,
           "scales": obj.scales,
           "raw_len_mismatch": obj.half.raw_len_mismatch,
           "pe_direction": obj.half.pe_direction,
           "ne_direction": obj.half.ne_direction,
           "dv_window_quantile_15_85": obj.dv_window,
           "dq_window_quantile_05_95": obj.dq_window}

    rep = REPORTED.get((args.si_source, args.state))
    if rep and all(x is not None for x in rep):
        p = np.array(rep, dtype=float)
        out["reported_p"] = rep
        out["reported_rmse_pocv"] = obj.rmse_pocv(p)
        out["reported_rmse_dvdq"] = obj.rmse_dvdq(p)
        out["reported_obj"] = obj(p)

    # ⚠ 2026-09-10 리뷰 [A2]: 전 판은 보고값을 **항상** 첫 시작점으로 넣고
    #   그 결과를 "독립 재적합" 이라고 불렀다. 그건 독립이 아니다.
    #   `--blind` 는 보고값을 시작점에서 빼고 무작위 시작만으로 다시 찾는다.
    seed_x0 = None
    if rep and all(x is not None for x in rep) and not args.blind:
        seed_x0 = np.array(rep, dtype=float)
    out["blind"] = bool(args.blind)
    out["reported_used_as_start"] = seed_x0 is not None
    best, val, _ = multistart(obj, n_starts=args.starts, seed=args.seed, x0=seed_x0)
    out["multistart_stats"] = dict(multistart.last_stats)
    out["our_p"] = [float(x) for x in best]
    out["our_obj"] = val
    # 산문 대신 **실제 차이**를 적는다 (리뷰 [A2]: 자릿수 주장이 사실과 달랐다)
    if rep and all(x is not None for x in rep):
        d = np.abs(np.array(rep, dtype=float) - np.asarray(best, float))
        out["abs_diff_vs_reported"] = [float(x) for x in d]
        out["max_abs_diff_vs_reported"] = float(d.max())
        out["obj_abs_diff_vs_reported"] = float(abs(out.get("reported_obj", np.nan) - val))
    out["our_rmse_pocv"] = obj.rmse_pocv(best)
    out["our_rmse_dvdq"] = obj.rmse_dvdq(best)
    out["active_bounds"] = active_bounds(best)
    # 반쪽전지 곡선의 어느 구간을 실제로 쓰는가 (0~1 밖이면 외삽이다)
    for tag, a, b in (("PE", best[0], best[1]), ("NE", best[2], best[3])):
        lo, hi = (0 - b) / a, (1 - b) / a
        out[f"{tag}_argument_range"] = [float(lo), float(hi)]
        out[f"{tag}_extrapolated"] = bool(lo < 0 or hi > 1)
    print(json.dumps(out, ensure_ascii=False, indent=2, default=float))


# ── C. 축퇴 ────────────────────────────────────────────────────────────

def near_optimal_extrema(obj: Objective, ref_p, ref_c, c_cell, best, best_val,
                         tol: float, seeds: list, n_starts: int = 8, seed: int = 0):
    """근최적 집합 {p : obj(p) ≤ best_obj·(1+tol)} 위에서 각 mode 의 min·max.

    ⚠ 2026-09-10 리뷰 [B1]: 전 판은 최적점 둘레에 등방 Gaussian 400점을 뿌리고
      **관측된** min·max 를 '폭' 이라고 불렀다. 그건 폭이 아니라 표집 하한이다.
      정확히 평평한 굽은 ridge(참 폭 40 %p)를 넣은 반례에서 그 방식은 0 %p 를
      보고했다 — 식별성이 아니라 표집 실패를 식별성으로 보고한 것이다.
      더 결정적으로, **우리가 커밋한 γ 프로파일 자신**이 같은 설정에서 1 % 안
      두 점만으로 1.59 %p 를 보인다 (문서의 0.87 %p 보다 넓다).

    그래서 무작위 대신 제약 최적화로 각 방향의 극값을 직접 민다:
        maximize / minimize  mode(p)   s.t.  obj(p) ≤ best_val·(1+tol),  lb ≤ p ≤ ub

    이것도 전역 보장은 아니다 (SLSQP 는 국소 해법이다). 여러 시작점에서 밀어
    가장 넓은 것을 취하므로 **여전히 하한**이지만, 등방 구름보다 훨씬 조인다.
    반환값에 `is_lower_bound: True` 를 같이 실어 그 사실을 지운 채 인용하지
    못하게 한다.
    """
    limit = best_val * (1.0 + tol)
    bounds = list(zip(LB5, UB5))
    rng = np.random.default_rng(seed + 7)
    # 시작점은 **상자 전체**에 뿌린다. 최적점 둘레에만 뿌리면 멀리 뻗은
    # 골짜기 끝을 못 민다 — 그게 전 판이 0 %p 를 보고한 이유다.
    starts = [np.asarray(best, float)]
    starts += [np.asarray(x, float) for x in seeds[:n_starts]]
    for i in range(5):                               # 각 축의 양 끝에서 한 번씩
        for frac in (0.02, 0.98):
            q = np.asarray(best, float).copy()
            q[i] = LB5[i] + frac * (UB5[i] - LB5[i])
            starts.append(q)
    starts += list(LB5 + rng.random((n_starts, 5)) * (UB5 - LB5))

    def mode_of(p, key):
        return degradation_modes(ref_p, ref_c, np.asarray(p, float), c_cell)[key]

    con = NonlinearConstraint(lambda p: limit - obj(np.asarray(p, float)), 0.0, np.inf)

    # ── 1단계: 실현가능성 복원 ──
    #   시작점이 제약 밖이면 SLSQP 가 목적 개선과 복원을 동시에 하다 실패한다
    #   (합성 ridge 에서 min 방향 시도가 **전부** 버려졌다). 그래서 먼저
    #   obj 를 낮춰 근최적 집합 안으로 들여보낸 뒤 극값을 민다. 복원된 점
    #   자체도 집합의 원소이므로 후보에 같이 넣는다.
    feasible = []
    for s0 in starts:
        q = np.asarray(s0, float)
        if obj(q) > limit:
            try:
                r0 = minimize(obj, q, method="L-BFGS-B", bounds=bounds,
                              options={"maxiter": 300, "ftol": 1e-14})
                if np.isfinite(r0.fun):
                    q = np.asarray(r0.x, float)
            except Exception:                        # noqa: BLE001
                continue
        if obj(q) <= limit * (1 + 1e-9):
            feasible.append(q)
    if not feasible:
        feasible = [np.asarray(best, float)]

    out = {}
    for key in ("LAM_PE", "LAM_NE", "LLI"):
        vals = [mode_of(best, key)] + [mode_of(q, key) for q in feasible]
        for sign in (+1.0, -1.0):                    # +1: 최대화, -1: 최소화
            for s0 in feasible:
                try:
                    r = minimize(lambda p: -sign * mode_of(p, key), s0,
                                 method="SLSQP", bounds=bounds, constraints=[con],
                                 options={"maxiter": 200, "ftol": 1e-12})
                except Exception:                    # noqa: BLE001
                    continue
                if not np.isfinite(r.fun):
                    continue
                # 제약을 실제로 지키는지 직접 확인한다 (SLSQP 는 살짝 넘길 수 있다)
                if obj(np.asarray(r.x, float)) <= limit * (1 + 1e-9):
                    vals.append(mode_of(r.x, key))
        v = np.array(vals, dtype=float) * 100.0
        out[key] = {"min": float(v.min()), "max": float(v.max()),
                    "span": float(v.max() - v.min()), "n_points": int(v.size),
                    "is_lower_bound": True}
    return out


def mode_profile_extrema(obj: Objective, ref_p, ref_c, c_cell, best, best_val,
                         tol: float, n_grid: int = 21, n_starts: int = 3,
                         seed: int = 0, hint: dict | None = None):
    """각 mode 값 v 가 근최적 집합 안에서 **도달 가능한가**를 직접 묻는다.

        for v in grid:   min_p obj(p)  s.t.  mode(p) = v,  lb ≤ p ≤ ub
        v 가 도달 가능 ⟺ 그 최소값 ≤ best_obj·(1+tol)

    왜 이쪽이 옳은가 (리뷰 B1 의 ridge 반례가 가르쳐 준 것):
      제약을 `obj(p) ≤ limit` 로 걸고 mode 를 최적화하면, 정확히 평평한
      골짜기 위에서 **제약의 기울기가 0 이 된다** (g = limit − 1 − (Δ/ε)²,
      Δ=0 에서 ∇g=0). LICQ 가 깨져서 SLSQP 가 골짜기를 따라 못 미끄러진다.
      실측: 참 폭 40 %p 인 ridge 에서 19.9 %p 만 나왔다.
      반대로 mode 를 **등식 제약**으로 묶고 obj 를 최소화하면 mode 제약은
      a 에 대해 선형이라 조건수가 좋고, obj 는 골짜기로 곧장 내려간다.

    반환값은 여전히 **하한**이다 (국소 해법 + 격자). `is_lower_bound` 를 같이
    실어 그 사실을 지운 채 인용하지 못하게 한다.
    """
    limit = best_val * (1.0 + tol)
    bounds = list(zip(LB5, UB5))
    rng = np.random.default_rng(seed + 11)
    box = LB5 + rng.random((256, 5)) * (UB5 - LB5)

    def mode_of(p, key):
        return degradation_modes(ref_p, ref_c, np.asarray(p, float), c_cell)[key]

    out = {}
    for key in ("LAM_PE", "LAM_NE", "LLI"):
        vals_box = np.array([mode_of(q, key) for q in box])
        v_lo, v_hi = float(vals_box.min()), float(vals_box.max())
        v_best = mode_of(best, key)

        # ⚠ 2026-09-10 실측: 상자 전체에 격자를 깔면 근최적 집합 근처가 성기다.
        #   LLI 는 22 개 중 **1 개**, LAM_PE 는 2 개만 도달 가능했다 — 방법이
        #   실패한 게 아니라 격자가 엉뚱한 데 깔린 것이다. 제약 최적화가 이미
        #   찾아 놓은 범위를 힌트로 받아 그 둘레(폭의 ±50 %)에 격자를 모은다.
        #   힌트 밖으로도 밀 수 있게 넓혀서 깔아야 하한이 더 조여진다.
        if hint and key in hint:
            h_lo, h_hi = hint[key]
            h_lo, h_hi = h_lo / 100.0, h_hi / 100.0        # % → 분수
            pad = max((h_hi - h_lo) * 0.5, 1e-4)
            g_lo = max(v_lo, h_lo - pad)
            g_hi = min(v_hi, h_hi + pad)
            if g_hi <= g_lo:
                g_lo, g_hi = v_lo, v_hi
        else:
            g_lo, g_hi = v_lo, v_hi
        grid = np.unique(np.concatenate([np.linspace(g_lo, g_hi, n_grid), [v_best]]))
        starts = [np.asarray(best, float)]
        starts += list(LB5 + rng.random((n_starts, 5)) * (UB5 - LB5))

        attainable = []
        for v in grid:
            con = {"type": "eq", "fun": (lambda p, _v=v, _k=key: mode_of(p, _k) - _v)}
            hit = np.inf
            for s0 in starts:
                try:
                    r = minimize(obj, s0, method="SLSQP", bounds=bounds,
                                 constraints=[con],
                                 options={"maxiter": 200, "ftol": 1e-12})
                except Exception:                    # noqa: BLE001
                    continue
                if not np.isfinite(r.fun):
                    continue
                q = np.asarray(r.x, float)
                # 등식 제약을 실제로 지켰는지 확인 — SLSQP 는 살짝 어긴다
                if abs(mode_of(q, key) - v) > 1e-6 * max(1.0, abs(v)):
                    continue
                hit = min(hit, float(obj(q)))
            if hit <= limit * (1 + 1e-9):
                attainable.append(v)

        if not attainable:
            attainable = [v_best]
        a = np.array(attainable, dtype=float) * 100.0
        out[key] = {"min": float(a.min()), "max": float(a.max()),
                    "span": float(a.max() - a.min()),
                    # ⚠ Codex R2-05: 외곽 [min,max] 만으로는 가능집합이 비연결인지 모른다.
                    #   도달한 격자점을 그대로 남겨 "공유 가능값" 을 나중에 물을 수 있게.
                    "attainable_pct": [float(x) for x in a],
                    "grid_pct": [float(x) * 100.0 for x in grid],
                    "n_grid_attainable": int(a.size), "n_grid": int(grid.size),
                    "grid_range_pct": [g_lo * 100.0, g_hi * 100.0],
                    "grid_from_hint": bool(hint and key in hint),
                    "is_lower_bound": True}
    return out


def cmd_degeneracy(args):
    root = D.data_root(args.data_root)
    ref_obj = build(root, args.source, "pristine", args.si_source,
                    w_dqdv=args.w_dqdv, scale_seed=args.seed)
    ref_best, _, _ = multistart(ref_obj, n_starts=args.starts, seed=args.seed)

    obj = build(root, args.source, args.state, args.si_source,
                w_dqdv=args.w_dqdv, scale_seed=args.seed)
    best, best_val, sols = multistart(obj, n_starts=args.starts, seed=args.seed)

    # 최적점 주변 무작위 탐색 — 목적함수가 (1+tol) 배 안에 드는 점을 모은다
    rng = np.random.default_rng(args.seed + 1)
    keep = [(best_val, best)]
    span = UB5 - LB5
    for _ in range(args.samples):
        scale = 10 ** rng.uniform(-3, -0.7)             # 0.1 % ~ 20 % 폭
        cand = np.clip(best + rng.normal(0, scale, 5) * span, LB5, UB5)
        v = obj(cand)
        if v <= best_val * (1 + args.tol):
            keep.append((v, cand))
    # 다중 시작이 찾은 국소해도 후보다
    keep += [(v, p) for v, p in sols if v <= best_val * (1 + args.tol)]

    modes = [degradation_modes(ref_best, ref_obj.c_cell, p, obj.c_cell)
             for _, p in keep]
    arr = {k: np.array([m[k] for m in modes]) * 100 for k in ("LAM_PE", "LAM_NE", "LLI")}
    out = {
        "state": args.state, "si_source": args.si_source,
        "half_cell": args.source, "w_dqdv": args.w_dqdv,
        "tol_percent_of_best": args.tol * 100,
        # ⚠ 설정을 산출 **안에** 남긴다. 2026-09-11 자체 리뷰: 파우치 100·200·
        #   300_0009 산출에 starts·seed 가 어디에도 없어서(meta 사이드카는 그
        #   뒤에 생겼다) 나머지 행과 같은 설정이었다는 것을 증명할 수 없었다.
        "n_starts": args.starts, "seed": args.seed,
        "n_accepted": len(keep),
        "best_obj": best_val,
        "best_p": [float(x) for x in best],
        "best_active_bounds": active_bounds(best),
        "ref_p": [float(x) for x in ref_best],
        "ref_active_bounds": active_bounds(ref_best),
        "best_modes_percent": {k: float(v * 100) for k, v in
                               degradation_modes(ref_best, ref_obj.c_cell,
                                                 best, obj.c_cell).items()},
    }
    # ── 2차 진단: 무작위 구름의 **관측** 폭. 폭이 아니라 표집 하한이다 ──
    for k, v in arr.items():
        out[f"{k}_percent_observed_cloud"] = {
            "min": float(v.min()), "max": float(v.max()),
            "span": float(v.max() - v.min()), "median": float(np.median(v)),
            "warning": "무작위 표집의 관측 폭 — 근최적 집합의 폭이 아니다"}

    # ── 1차: 두 방법의 **합집합**. 둘 다 하한이므로 넓은 쪽이 더 나은 하한이다 ──
    ext = near_optimal_extrema(obj, ref_best, ref_obj.c_cell, obj.c_cell,
                               best, best_val, args.tol,
                               seeds=[p for _, p in keep[1:]],
                               n_starts=8, seed=args.seed)
    # 제약 최적화를 **먼저** 돌려 그 범위를 프로파일 격자의 힌트로 준다.
    prof = mode_profile_extrema(obj, ref_best, ref_obj.c_cell, obj.c_cell,
                                best, best_val, args.tol,
                                n_grid=getattr(args, "grid", 21),
                                n_starts=3, seed=args.seed,
                                hint={k: (v["min"], v["max"]) for k, v in ext.items()})
    for k in ("LAM_PE", "LAM_NE", "LLI"):
        lo = min(ext[k]["min"], prof[k]["min"])
        hi = max(ext[k]["max"], prof[k]["max"])
        out[f"{k}_percent"] = {
            "min": lo, "max": hi, "span": hi - lo, "is_lower_bound": True,
            "from_constrained_extrema": ext[k], "from_mode_profile": prof[k]}
    out["span_method"] = (
        "근최적 집합 {obj ≤ best·(1+tol)} 위에서 (a) mode 등식 제약 프로파일과 "
        "(b) 직접 제약 최적화를 둘 다 돌려 **합집합**을 취한다. 둘 다 국소 "
        "해법이므로 결과는 여전히 **하한**이다 — 정확한 폭도, 신뢰구간도 아니다.")
    print(json.dumps(out, ensure_ascii=False, indent=2, default=float))


# ── A2. dd_eval.m 대조 — **적합 없이** 같은 p 에서 목적함수만 ──────────

#: `matlab/dd_eval.m` 의 기본 격자와 **같은 순서·같은 값**이어야 한다.
#: 한쪽만 고치면 대조가 조용히 어긋나므로 둘을 같이 고칠 것.
DD_EVAL_P = [
    [1.077218, -0.022949, 1.001342, 0.000309, 0.295099],
    [1.076074, -0.022129, 1.001279, 0.000299, 0.295298],
    [1.181472, -0.141171, 1.080759, -0.000775, 0.239466],
    [1.080000, -0.040000, 1.050000, -0.030000, 0.250000],
    [1.100000, -0.050000, 1.100000, -0.010000, 0.100000],
    [1.100000, -0.050000, 1.100000, -0.010000, 0.200000],
    [1.100000, -0.050000, 1.100000, -0.010000, 0.300000],
    [1.100000, -0.050000, 1.100000, -0.010000, 0.400000],
]

#: 앵커 → 그 값이 갈리면 **어느 단계**가 범인인가. 순서가 곧 이분 순서다.
ANCHOR_STAGE = [
    ("c_cell",         "풀셀 적재 + averageDuplicates + 방향 정규화"),
    ("dv_lo",          "풀셀 differential + quantile(0.15)"),
    ("dv_hi",          "풀셀 differential + quantile(0.85)"),
    ("dv_n",           "dV/dQ 창 마스크가 먹은 격자점 수"),
    ("dq_lo",          "풀셀 differential + quantile(0.05)"),
    ("dq_hi",          "풀셀 differential + quantile(0.95)"),
    ("dq_n",           "dQ/dV 창 마스크가 먹은 격자점 수"),
    ("n_peaks",        "findpeaks(prominence=0.1·range) 가 찾은 피크 수"),
    ("w_peak_sum",     "피크 가중 합 — peak_weight·sigma_ratio·피크 위치"),
    ("w_peak_max",     "피크 가중 최댓값 — 가중 봉우리가 겹쳤는지"),
    ("dq_nuniq_p1",    "첫 행 p 에서 unique(v_smooth) 뒤 남은 점 (모델 단조성)"),
    ("dq_nin_p1",      "첫 행 p 에서 보간 범위에 든 실측 점 (5 미만이면 1e6)"),
    ("E_PE_0p5",       "반쪽전지 적재 (electrode_ocv) — PE OCP"),
    ("E_NE_0p5_0p25",  "문헌 적재 + build_blend_functions — 블렌드 OCP"),
    ("dv_PE_0p5",      "반쪽전지 differential — PE dV/dQ"),
    ("dv_NE_0p5_0p25", "블렌드 differential — NE dV/dQ"),
]


def dd_eval_anchors(obj: Objective, p1=None) -> list[tuple[str, float]]:
    """`matlab/dd_eval.m` 이 CSV 앞머리에 적는 앵커와 **같은 이름·같은 순서**.

    `p1` 은 dQ/dV 쪽 앵커(`dq_nuniq_p1`·`dq_nin_p1`)를 재는 파라미터 —
    dd_eval.m 은 격자의 **첫 행**에서 잰다. 그 둘은 원본이 점을 조용히
    버리는 두 자리(비단조 모델전압 · 보간범위 밖)를 각각 드러낸다.
    """
    p1 = np.array(DD_EVAL_P[0], dtype=float) if p1 is None else np.asarray(p1, float)
    v_u, _ = obj._model_dqdv(p1)
    nin = int(((obj.vol_dq_fit >= v_u.min()) & (obj.vol_dq_fit <= v_u.max())).sum())
    return [
        ("c_cell",         float(obj.c_cell)),
        ("dv_lo",          float(obj.dv_window[0])),
        ("dv_hi",          float(obj.dv_window[1])),
        ("dv_n",           float(len(obj.cap_dv_fit))),
        ("dq_lo",          float(obj.dq_window[0])),
        ("dq_hi",          float(obj.dq_window[1])),
        ("dq_n",           float(len(obj.vol_dq_fit))),
        ("n_peaks",        float(len(obj.peak_locs))),
        ("w_peak_sum",     float(obj.w_peak.sum())),
        ("w_peak_max",     float(obj.w_peak.max())),
        ("dq_nuniq_p1",    float(len(v_u))),
        ("dq_nin_p1",      float(nin)),
        ("E_PE_0p5",       float(np.atleast_1d(obj.half.E_PE(0.5))[0])),
        ("E_NE_0p5_0p25",  float(np.atleast_1d(obj.blend.E(np.atleast_1d(0.5), 0.25))[0])),
        ("dv_PE_0p5",      float(np.atleast_1d(obj.half.dv_PE(0.5))[0])),
        ("dv_NE_0p5_0p25", float(np.atleast_1d(obj.blend.dv(np.atleast_1d(0.5), 0.25))[0])),
    ]


def read_dd_eval_csv(path):
    """dd_eval.m 산출(`# 이름,값` 앞머리 + 헤더 + 파라미터 행)을 읽는다.

    ⚠ 열 구성이 판마다 다르다. 2026-09-10 이전 산출은 `rmse_pocv`·`rmse_dvdq`
      둘뿐이고 그 뒤는 dQ/dV 두 열이 더 붙는다. **헤더를 읽어서** 양쪽에 다
      있는 열만 대조한다 — 그래야 옛 산출 4개(104 값 일치)가 무효가 되지 않는다.
    """
    anchors, rows, header = {}, [], []
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line.startswith("#") and "," in line:
            k, _, v = line.lstrip("# ").partition(",")
            try:
                anchors[k.strip()] = float(v)
            except ValueError:
                pass
        elif line.startswith("a_PE"):
            header = [c.strip() for c in line.split(",")]
        elif line and not line.startswith("#"):
            try:
                rows.append([float(x) for x in line.split(",")])
            except ValueError:
                pass
    return anchors, rows, header


#: 이보다 큰 상대차는 **모델·산술의 차이**로 본다. 앵커에 쓰는 문턱과 같다.
#: 그 아래는 구현 수준의 부동소수점 차이 — 같은 식을 두 언어로 쓰면 남는 양이다.
MODEL_REL = 1e-9


def _token_precision(f: str):
    """토큰 하나의 (소수 자리수, 유효 자리수). 정수 토큰은 (None, n), nan/inf 는 (None, 0)."""
    f = f.strip().lower()
    if not f or f in ("nan", "inf", "-inf", "+inf"):
        return None, 0
    mant, _, exp = f.partition("e")
    dec = len(mant.split(".")[1]) if "." in mant else None
    sig = len(mant.replace("-", "").replace("+", "").replace(".", "").lstrip("0")) or 1
    if dec is not None and exp:
        dec = dec - int(exp)
    return dec, sig


def printed_abs_tols(path, default_decimals: int = 10) -> dict:
    """**열마다** 적힌 자리수가 허용하는 절대 한계.

    ⚠ 2026-09-11 Codex R2-02: 전 판은 파일 전체에서 소수 자리수의 **최솟값**을
      한계로 썼다. 그러면 `%.17g` 파일에 정확한 `1.5` 하나만 있어도 파일 전체
      한계가 0.1 이 되어, 다른 행의 163 % 차이가 "적힌 자리수 안" 으로 덮였다.
      짧은 토큰은 값이 정확히 표현된다는 뜻이지 producer 의 정밀도가 낮다는
      뜻이 아니다. 그래서 (1) 열마다 따로 보고, (2) 유효 15자리 이상 토큰이 하나라도
      있는 열은 **전정밀도 producer**(dd_eval.m 의 `%.17g`)로 보아 한계 0 — 차이는
      상대 띠(`MODEL_REL`)로만 판정한다. 고정 소수 producer(`%.10f` 등)만 열의 최대
      자리수로 한계를 준다.
    """
    cols, decs, sigs = None, {}, {}
    try:
        for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("a_PE"):
                cols = [c.strip() for c in line.split(",")][5:]
                continue
            fields = line.split(",")[5:]
            names = cols if cols and len(cols) == len(fields) else [f"col{j}" for j in range(len(fields))]
            for name, field in zip(names, fields):
                dec, sig = _token_precision(field)
                if sig:
                    sigs[name] = max(sigs.get(name, 0), sig)
                if dec is not None:
                    decs[name] = max(decs.get(name, 0), dec)
    except (OSError, ValueError):
        pass
    out = {}
    for name in set(sigs) | set(decs):
        if sigs.get(name, 0) >= 15:
            out[name] = 0.0
        elif name in decs:
            out[name] = 10.0 ** (-decs[name])
        else:
            out[name] = 10.0 ** (-default_decimals)
    return out


def printed_abs_tol(path, default_decimals: int = 10) -> float:
    """파일 전체 한 값이 필요할 때 — 열별 한계의 **최솟값**(가장 빡빡한 열)."""
    tols = printed_abs_tols(path, default_decimals)
    return min(tols.values()) if tols else 10.0 ** (-default_decimals)


#: `# printed_format,%.17g` — dd_eval.m 과 `eval --out` 이 CSV 앞머리에 적는 **형식 선언**.
PRINTED_FORMAT_KEY = "printed_format"


def read_dd_eval_meta(path) -> dict:
    """앞머리 `# 이름,값` 중 **숫자가 아닌** 것 (`impl_*`, `printed_format` …). 앵커와 분리해 읽는다."""
    meta = {}
    try:
        for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line.startswith("#") and "," in line:
                k, _, v = line.lstrip("# ").partition(",")
                try:
                    float(v)
                except ValueError:
                    meta[k.strip()] = v.strip()
    except OSError:
        pass
    return meta


def _precision_spec_to_tols(path, spec: str) -> dict:
    """`g17`/`full` → 모든 열 전정밀도(0), `fixed:N` → 모든 열 10^-N. 열 이름은 파일 헤더에서."""
    cols = []
    try:
        for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
            if line.strip().startswith("a_PE"):
                cols = [c.strip() for c in line.strip().split(",")][5:]
                break
    except OSError:
        pass
    cols = cols or ["rmse_pocv", "rmse_dvdq"]
    spec = spec.strip().lower()
    if spec in ("g17", "full"):
        return {c: 0.0 for c in cols}
    m = re.fullmatch(r"fixed:(\d+)", spec)
    if not m:
        raise ValueError(f"--precision 은 auto | g17 | full | fixed:N 중 하나다: {spec!r}")
    return {c: 10.0 ** (-int(m.group(1))) for c in cols}


def declared_precision(path):
    """파일의 `# printed_format,…` 선언 → 'g17' | 'fixed:N' | None (선언 없음/해석 불가).

    `%.Ng` 는 N ≥ 15 일 때만 전정밀도로 본다. 그보다 짧은 `%g` 는 절대 한계가 값의 크기에
    따라 달라 열별 추정으로 넘긴다 (선언 자체는 `precision_label` 에 남는다).
    """
    fmt = read_dd_eval_meta(path).get(PRINTED_FORMAT_KEY)
    if not fmt:
        return None
    m = re.fullmatch(r"%\.(\d+)([fg])", fmt.strip())
    if not m:
        return None
    n, kind = int(m.group(1)), m.group(2)
    if kind == "g":
        return "g17" if n >= 15 else None
    return f"fixed:{n}"


def resolve_precision(path, precision=None):
    """대조에 쓸 열별 절대 한계와 **그 출처** → (tols, source, label).

    ⚠ 2026-09-11 Codex R3-06: 값의 길이로 producer 형식을 추정하는 것은 증거가 아니라 추정이다 —
      `%.17g` 열의 값이 전부 짧으면(정확한 0.125) 추정 한계 1e-3 이 1/1024 의 실제 차이를 지웠다.
      우선순위: ① 명시 옵션(`--precision g17|full|fixed:N`) ② 파일의 `# printed_format` 선언
      ③ 추정 — 그리고 ③ 일 때는 **추정이라고 말한다**.
    """
    if precision and str(precision).lower() != "auto":
        return _precision_spec_to_tols(path, str(precision)), "option", f"--precision {precision}"
    dec = declared_precision(path)
    if dec:
        return (_precision_spec_to_tols(path, dec), "declared",
                f"# {PRINTED_FORMAT_KEY},{read_dd_eval_meta(path)[PRINTED_FORMAT_KEY]}")
    raw = read_dd_eval_meta(path).get(PRINTED_FORMAT_KEY)
    label = "값의 자리수에서 **추정** (파일에 형식 선언 없음)" if not raw else \
        f"값의 자리수에서 **추정** (선언 `{raw}` 은 열별 절대 한계로 못 옮긴다)"
    return printed_abs_tols(path), "inferred", label


def cmd_eval(args):
    """적합 없이 주어진 p 에서 rmse 를 찍고, 원하면 MATLAB 산출과 대조한다.

    툴박스가 없는 기계에서도 포팅 대조를 할 수 있게 만든 우회로다:
    포팅이 맞는지 묻는 데 정말 필요한 것은 최적화기가 아니라 **모델**이므로,
    같은 p 에서 두 구현이 같은 rmse 를 내는지만 보면 된다.
    """
    root = D.data_root(args.data_root)
    obj = build(root, args.source, args.state, args.si_source,
                w_dqdv=args.w_dqdv, scale_seed=args.seed)

    P = np.array(DD_EVAL_P, dtype=float)
    anchors = dd_eval_anchors(obj, P[0])
    print(f"# dd_eval  state={args.state}  halfcell=data/half_cell/{args.source}/  "
          f"Si={args.si_source}  w_dqdv={args.w_dqdv:g}")
    print(f"# {PRINTED_FORMAT_KEY},%.17g")          # R3-06: 형식은 선언한다, 추정시키지 않는다
    for k, v in anchors:
        print(f"# {k},{v:.17g}")

    # ⚠ 열 이름·순서는 `matlab/dd_eval.m` 의 `hdr` 과 **같아야 한다**.
    cols = ["rmse_pocv", "rmse_dvdq", "rmse_dqdv", "rmse_dqdv_w"]
    vals = {"rmse_pocv":   [obj.rmse_pocv(q) for q in P],
            "rmse_dvdq":   [obj.rmse_dvdq(q) for q in P],
            "rmse_dqdv":   [obj.rmse_dqdv(q, False) for q in P],
            "rmse_dqdv_w": [obj.rmse_dqdv(q, True) for q in P]}
    lines = ["a_PE,b_PE,a_NE,b_NE,gamma_Si," + ",".join(cols)]
    print(lines[0])
    for i, q in enumerate(P):
        r = ",".join([f"{x:.6f}" for x in q] + [f"{vals[c][i]:.17g}" for c in cols])
        lines.append(r)
        print(r)

    if args.out:
        head = [f"# dd_eval  state={args.state}  halfcell=data/half_cell/{args.source}/  "
                f"Si={args.si_source}  w_dqdv={args.w_dqdv:g}",
                f"# {PRINTED_FORMAT_KEY},%.17g"]
        head += [f"# {k},{v:.17g}" for k, v in anchors]
        Path(args.out).write_text("\n".join(head + lines) + "\n", encoding="utf-8")
        print(f"\nwrote {args.out}")

    if args.compare:
        # ⚠ 2026-09-11 Codex R3-07: 전 판은 여기서 dict 를 버리고 None 을 올려 `sys.exit(None)` = 0 —
        #   "rmse 가 갈린다" 를 찍고도 명령은 성공이었다. 판정이 곧 종료 코드다.
        try:
            result = _compare_dd_eval(dict(anchors), P, vals, args.compare,
                                      precision=getattr(args, "precision", None))
        except ValueError as e:                      # 잘못된 --precision 은 대조 미완이다
            print(f"! {e}\n종료 코드 2 (invalid)")
            return 2
        rc = EXIT_BY_STATUS.get(result["status"], 2)
        note = ""
        if rc == 3 and getattr(args, "allow_partial", False):
            rc, note = 0, " — `--allow-partial` 로 옛 스키마의 부분 대조를 허용했다"
        print(f"종료 코드 {rc} ({result['status']}{note})")
        return rc
    return 0


#: 대조 판정 → process 종료 코드 (R3-07). 완전한 지원 범위의 일치만 0 이다.
#:   1 = 갈렸다(앵커/목적함수)  2 = 대조 미완·빈 파일(성공 아님)  3 = 부분(옛 스키마: 앵커·열 누락) —
#:   3 은 `--allow-partial` 을 **명시**했을 때만 0 이 된다.
EXIT_BY_STATUS = {"complete": 0, "anchor_mismatch": 1, "model_mismatch": 1,
                  "incomplete": 2, "empty": 2, "partial": 3}


def _compare_dd_eval(py_anchors, py_P, py_vals, matlab_csv, precision=None):
    """MATLAB 산출과 대조하고, **갈린 첫 단계**를 이름으로 말한다.

    `py_vals` 는 열이름 → 값 목록. MATLAB CSV 의 **헤더에 있는 열만** 댄다
    (옛 산출은 rmse 두 열뿐이다). 반환 dict 의 `status`:
      complete        앵커 16 · 행 8 · 열 4 전부 비교했고 전부 일치 (유일한 성공)
      partial         비교한 것은 전부 일치하지만 옛 스키마라 앵커/열이 빠졌다 (성공 아님)
      incomplete      비교 못 한 값이 있다 — 행 누락·격자 불일치·비유한(NaN) 앵커/파라미터/metric
      anchor_mismatch 앵커가 갈린다 (단계 이름을 말한다) / model_mismatch 목적함수가 갈린다
    `precision` 은 `--precision` (R3-06): None/'auto' 면 파일 선언 → 추정 순.
    """
    m_anchors, m_rows, m_header = read_dd_eval_csv(matlab_csv)
    atols, prec_source, prec_label = resolve_precision(matlab_csv, precision)
    atol = min(atols.values()) if atols else 1e-10
    print(f"\n=== dd_eval.m 대조: {matlab_csv} ===")
    print(f"  (정밀도: {prec_label})")
    print("  (열별로 적힌 자리수가 허용하는 절대 한계: "
          + ", ".join(f"{k} {v:.0e}" if v else f"{k} 전정밀도" for k, v in atols.items())
          + " — 그 안의 차이는 두 구현의 차이가 아니라 출력 반올림이다)")
    if prec_source == "inferred":
        print("  ⚠ 한계는 **추정**이다 — 값의 길이는 producer 형식의 증거가 아니다 (Codex R3-06)."
              " dd_eval.m 의 `# printed_format` 선언이 있는 파일을 쓰거나 `--precision g17` 로 명시할 것.")
    # ⚠ 2026-09-11 Codex R2-01: 전 판은 비교하지 **않은** 셀(행 누락·격자 불일치·
    #   NaN)도 "전부 일치" 로 인증했다. 이제 기대 셀 수와 실제 비교한 셀 수를 세고,
    #   하나라도 못 비교했으면 성공 문장을 내지 않는다.
    # ⚠ 2026-09-11 Codex R3-05: 그 개수·유한성 검사가 metric 에만 있었다 — 누락 앵커는 `continue`,
    #   NaN 앵커는 `r > 1e-9` 가 거짓, NaN 파라미터는 `max(...) > tol` 이 거짓이라 셋 다 complete.
    #   앵커도 기대 16 개를 세고, 비유한 값은 어디서든 성공이 아니다.
    result = {"status": "complete", "expected": 0, "compared": 0, "problems": [],
              "worst_rel": 0.0, "first_bad": None,
              "anchors_expected": len(ANCHOR_STAGE), "anchors_compared": 0, "missing_anchors": [],
              "partial": False, "precision_source": prec_source, "precision_label": prec_label}
    if not m_anchors and not m_rows:
        print("  ! 읽을 내용이 없다 — 경로가 맞나?")
        result.update(status="empty"); return result

    def rel(a, b):
        return abs(a - b) / max(abs(b), 1e-30)

    hard = result["problems"]
    print(f"  {'앵커':<16} {'MATLAB':>22} {'Python':>22} {'상대차':>10}   단계")
    first_bad = None
    for k, stage in ANCHOR_STAGE:
        if k not in m_anchors:
            print(f"  {k:<16} {'(없음)':>22} — 옛 dd_eval.m 산출인가?")
            result["missing_anchors"].append(k)
            continue
        a, b = m_anchors[k], py_anchors.get(k, float("nan"))
        if not (np.isfinite(a) and np.isfinite(b)):
            print(f"  {k:<16} {a!s:>22} {b!s:>22} {'비유한':>10}   {stage}")
            hard.append(f"앵커 {k} 비유한 (MATLAB {a!r}, Python {b!r})")
            continue
        result["anchors_compared"] += 1
        if k == "dv_n":
            mark = "" if a == b else "  ← 다르다"
            print(f"  {k:<16} {a:>22.0f} {b:>22.0f} {'':>10}{mark}   {stage}")
            if a != b and first_bad is None:
                first_bad = (k, stage)
            continue
        r = rel(a, b)
        mark = "  ←" if r > 1e-9 else ""
        print(f"  {k:<16} {a:>22.12g} {b:>22.12g} {r:>10.2e}{mark}   {stage}")
        if r > 1e-9 and first_bad is None:
            first_bad = (k, stage)

    print()
    worst_row = 0.0
    shared = [c for c in m_header[5:] if c in py_vals] if m_header else []
    if not m_header:
        shared = ["rmse_pocv", "rmse_dvdq"]        # 헤더 없는 아주 옛 산출
        print("  (헤더가 없다 — 앞 두 열만 rmse 로 본다)")
    missing = [c for c in py_vals if c not in shared]
    if missing:
        print(f"  (MATLAB 산출에 없는 열은 건너뛴다: {', '.join(missing)}"
              f" — 옛 dd_eval.m 산출이다 → **부분 대조**)")
    if result["missing_anchors"]:
        print(f"  (MATLAB 산출에 없는 앵커 {len(result['missing_anchors'])} 개: "
              f"{', '.join(result['missing_anchors'])} → **부분 대조**)")
    schema_partial = bool(missing) or bool(result["missing_anchors"])
    result["partial"] = schema_partial
    result["expected"] = len(py_P) * len(shared)
    if len(m_rows) != len(py_P):
        print(f"  ! 행 수가 다르다: MATLAB {len(m_rows)} vs Python {len(py_P)} — 대조 미완")
        hard.append(f"행 수 {len(m_rows)} vs {len(py_P)}")
    n_rows = min(len(m_rows), len(py_P))
    if n_rows:
        head = "  " + f"{'p 행':<5}" + "".join(f"{c + ' 상대차':>22}" for c in shared) + "   판정"
        print(head)
        for i, mr in enumerate(m_rows[:n_rows]):
            pp = [float(x) for x in py_P[i][:5]]
            if len(mr) < 5 or not all(np.isfinite(mr[:5])) or not all(np.isfinite(pp)):
                print(f"  {i:<5} ! 파라미터에 비유한 값이 있다 — 이 행은 비교하지 않았다")
                hard.append(f"행 {i} 파라미터 비유한")
                continue
            if max(abs(mr[j] - pp[j]) for j in range(5)) > 1e-6:
                print(f"  {i:<5} ! 파라미터가 다른 행이다 — 격자가 어긋났다 (이 행은 비교하지 않았다)")
                hard.append(f"행 {i} 파라미터 불일치")
                continue
            cells, eff = [], 0.0
            for c in shared:
                j = m_header.index(c) if m_header else (5 + shared.index(c))
                mv = mr[j] if j < len(mr) else float("nan")
                pv = py_vals[c][i] if i < len(py_vals[c]) else float("nan")
                if not (np.isfinite(mv) and np.isfinite(pv)):
                    cells.append(f"{'비유한':>22}")
                    hard.append(f"행 {i} {c} 비유한")
                    continue
                r = rel(mv, pv)
                cells.append(f"{r:>22.2e}")
                result["compared"] += 1
                # 적힌 자리수 안이면 "차이" 가 아니다 — **그 열의** 한계로
                if abs(mv - pv) > atols.get(c, atol):
                    eff = max(eff, r)
            worst_row = max(worst_row, eff)
            if eff == 0.0:
                verdict = "적힌 자리수 안"
            elif eff <= MODEL_REL:
                verdict = "수치 잡음"
            else:
                verdict = "모델 차이  ←"
            print(f"  {i:<5}" + "".join(cells) + f"   {verdict}")

    print()
    result["worst_rel"] = worst_row
    result["first_bad"] = first_bad
    n_a, n_e = result["anchors_compared"], result["anchors_expected"]
    tag = (f"판정(부분 — 앵커 {n_a}/{n_e} · 열 {len(shared)}/{len(py_vals)}):"
           if schema_partial else "판정:")
    if first_bad:
        k, stage = first_bad
        print(f"판정: **{k}** 에서 처음 갈린다 → 범인 단계는 「{stage}」")
        print("      그 앞 앵커는 맞았으므로 그 앞 단계는 용의선상에서 빠진다.")
        result["status"] = "anchor_mismatch"
    elif hard:
        print(f"판정: **대조 미완 — 성공 아님** (비교한 앵커 {n_a}/{n_e}, rmse {result['compared']}/{result['expected']}).")
        for pmsg in hard[:12]:
            print(f"      - {pmsg}")
        print("      비교하지 못한 값이 있으면 이 파일로는 '일치' 를 말할 수 없다.")
        result["status"] = "incomplete"
    elif worst_row > MODEL_REL:
        print(f"{tag} 앵커는 전부 맞는데 rmse 가 갈린다 (최대 상대차 {worst_row:.2e})")
        print("      → 곡선은 같고 **목적함수 산술**이 다르다는 뜻이다.")
        result["status"] = "model_mismatch"
    elif worst_row > 0.0:
        n_rmse = result["compared"]
        print(f"{tag} 앵커 {n_a}개가 전부 맞고, rmse {n_rmse}개는")
        print(f"      **적힌 자리수보다는 크고 {MODEL_REL:.0e} 보다는 작은**")
        print(f"      차이만 남는다 (최대 상대차 {worst_row:.2e}).")
        print(f"      이 파일은 {atol:.0e} 까지 담으므로 이건 출력 반올림이 아니라")
        print("      **실제 수치 차이**다 — 같은 식을 MATLAB 과 Python 으로 각각")
        print("      쓰면 남는 양(평활·보간·누산 순서)이고, 모델의 차이가 아니다.")
        print("      같은 p 에서 두 구현이 같은 목적함수를 낸다 = 포팅이 그들 모델이다.")
        result["status"] = "partial" if schema_partial else "complete"
    else:
        n_rmse = result["compared"]
        print(f"{tag} 앵커 {n_a}개와 rmse {n_rmse}개가"
              f" **적힌 자리수 안에서 전부 일치**.")
        result["status"] = "partial" if schema_partial else "complete"
        print(f"      남은 차이는 전부 CSV 출력 반올림({atol:.0e}) 안이다 —")
        print("      이 파일로는 그보다 정밀하게 비교할 수 없다.")
        print("      같은 p 에서 두 구현이 같은 목적함수를 낸다 = 포팅이 그들 모델이다.")
    if schema_partial and result["status"] == "partial":
        print("      ⚠ **부분 대조**다 — 빠진 앵커/열은 이 파일로 검증되지 않았다 (성공 아님).")
    return result


# ── D. scale 비결정성 ──────────────────────────────────────────────────
    return result

def cmd_scale_noise(args):
    root = D.data_root(args.data_root)
    rows = []
    for seed in range(args.repeats):
        obj = build(root, args.source, args.state, args.si_source,
                    w_dqdv=args.w_dqdv, scale_seed=seed)
        best, val, _ = multistart(obj, n_starts=args.starts, seed=seed)
        rows.append({"seed": seed, "scales": obj.scales,
                     "p": [float(x) for x in best], "obj": val,
                     "rmse_pocv": obj.rmse_pocv(best),
                     "bounds": active_bounds(best)})
    P = np.array([r["p"] for r in rows])
    out = {"state": args.state, "si_source": args.si_source,
           "repeats": args.repeats, "rows": rows,
           "scale_pocv_spread": [min(r["scales"]["pocv"] for r in rows),
                                 max(r["scales"]["pocv"] for r in rows)],
           "scale_dvdq_spread": [min(r["scales"]["dvdq"] for r in rows),
                                 max(r["scales"]["dvdq"] for r in rows)],
           "param_span": {n: float(P[:, i].max() - P[:, i].min())
                          for i, n in enumerate(["a_PE", "b_PE", "a_NE",
                                                 "b_NE", "gamma_Si"])}}
    print(json.dumps(out, ensure_ascii=False, indent=2, default=float))


# ── E. 모델 선택 매트릭스 ──────────────────────────────────────────────

def cmd_matrix(args):
    """같은 데이터에 **모델 선택만** 바꿔 가며 답이 얼마나 움직이는지.

    축: 문헌 Si 소스 8 × 반쪽전지 소스 2 × dQ/dV 포함 여부 2.
    각 조합에서 pristine 과 대상 상태를 **같은 조합으로** 적합해 LAM/LLI 를 낸다
    (원본 파이프라인이 그렇게 한다 — 기준도 그 조합의 pristine 이다).
    """
    root = D.data_root(args.data_root)
    rows = []
    sources = ([args.source] if args.only_source else list(D.HALF_FILE))
    for hc in sources:
        if args.state not in D.HALF_FILE[hc]:
            continue
        if not D.half_cell_path(root, hc, args.state).is_file():
            continue
        for si in D.SI_SOURCES:
            for w in ([args.w_dqdv] if args.only_wdqdv else [0.0, 1.0]):
                try:
                    ro = build(root, hc, "pristine", si, w_dqdv=w, scale_seed=args.seed)
                    rp, _, _ = multistart(ro, n_starts=args.starts, seed=args.seed)
                    o = build(root, hc, args.state, si, w_dqdv=w, scale_seed=args.seed)
                    p, val, _ = multistart(o, n_starts=args.starts, seed=args.seed)
                except Exception as e:                  # noqa: BLE001
                    rows.append({"half_cell": hc, "si": si, "w_dqdv": w,
                                 "error": f"{type(e).__name__}: {e}"})
                    continue
                m = degradation_modes(rp, ro.c_cell, p, o.c_cell)
                # ⚠ 리뷰 [B4-4]: 전 판은 `ref_bounds` 만 남겼다. 그러면
                #   LAM = 1 − state/ref 의 변화가 **기준이 움직인 것인지 대상이
                #   움직인 것인지 분리할 수 없다** (둘 다 같은 LAM 을 낸다).
                #   기준 적합의 전체 파라미터·목적함수·c_cell 을 같이 남긴다.
                rows.append({
                    "half_cell": hc, "si": si, "w_dqdv": w,
                    "obj": val, "rmse_pocv": o.rmse_pocv(p),
                    "a_PE": p[0], "b_PE": p[1], "a_NE": p[2], "b_NE": p[3],
                    "gamma_Si": p[4], "c_cell": o.c_cell,
                    "bounds": ",".join(active_bounds(p)) or "-",
                    "ref_a_PE": rp[0], "ref_b_PE": rp[1], "ref_a_NE": rp[2],
                    "ref_b_NE": rp[3], "ref_gamma_Si": rp[4],
                    "ref_obj": float(ro(rp)), "ref_rmse_pocv": ro.rmse_pocv(rp),
                    "ref_c_cell": ro.c_cell,
                    "ref_bounds": ",".join(active_bounds(rp)) or "-",
                    "LAM_PE_pct": m["LAM_PE"] * 100,
                    "LAM_NE_pct": m["LAM_NE"] * 100,
                    "LLI_pct": m["LLI"] * 100})
                print(json.dumps(rows[-1], ensure_ascii=False, default=float),
                      flush=True)
    ok = [r for r in rows if "error" not in r]
    summary = {"state": args.state, "n_combinations": len(rows),
               "n_ok": len(ok),
               "n_with_active_bound": sum(1 for r in ok if r["bounds"] != "-"),
               "n_negative_LAM": sum(1 for r in ok if min(r["LAM_PE_pct"],
                                                          r["LAM_NE_pct"]) < 0)}
    for k in ("LAM_PE_pct", "LAM_NE_pct", "LLI_pct"):
        v = np.array([r[k] for r in ok], dtype=float)
        if v.size:
            summary[k] = {"min": float(v.min()), "max": float(v.max()),
                          "span": float(v.max() - v.min()),
                          "median": float(np.median(v))}

    # ── 축별 폭은 **분모를 제목에 적어서** 낸다 (리뷰 B4) ──
    #   전 판은 "경계에 안 붙은 10" 과 "그중 6" 사이에서 기준을 설명 없이
    #   바꿨다. 사후선택 집합과 전체를 나란히 적어 그 일이 다시 없게 한다.
    def _span(g, k):
        v = [r[k] for r in g]
        return (float(max(v) - min(v)), len(g)) if v else (None, 0)

    axes = {}
    for hc in sorted({r["half_cell"] for r in ok}):
        g = [r for r in ok if r["half_cell"] == hc and r["w_dqdv"] == 0.0]
        if g:
            sp, n = _span(g, "LLI_pct")
            axes[f"{hc}_dqdv_off_all_Si"] = {
                "n": n, "si_sources": sorted({r["si"] for r in g}),
                "LLI_span_pct": sp,
                "LAM_NE_span_pct": _span(g, "LAM_NE_pct")[0],
                "LAM_PE_span_pct": _span(g, "LAM_PE_pct")[0]}
    interior = [r for r in ok
                if r["bounds"] == "-" and r["ref_bounds"] == "-" and r["w_dqdv"] == 0.0]
    if interior:
        sp, n = _span(interior, "LLI_pct")
        axes["dqdv_off_BOTH_interior_only"] = {
            "n": n, "half_cells": sorted({r["half_cell"] for r in interior}),
            "si_sources": sorted({r["si"] for r in interior}),
            "LLI_span_pct": sp,
            "warning": "사후선택 집합이다 — '문헌 곡선 선택' 축의 값이 아니다"}
    summary["axes_with_denominator"] = axes

    # ── dQ/dV on/off 는 **같은 조합의 대응쌍**으로만 (리뷰 B4) ──
    by = {(r["half_cell"], r["si"], r["w_dqdv"]): r for r in ok}
    matched, all_pairs = [], []
    for hc in sorted({r["half_cell"] for r in ok}):
        for si in sorted({r["si"] for r in ok}):
            a, b = by.get((hc, si, 0.0)), by.get((hc, si, 1.0))
            if a is None or b is None:
                continue
            d = b["LLI_pct"] - a["LLI_pct"]
            all_pairs.append(d)
            if all(r["bounds"] == "-" and r["ref_bounds"] == "-" for r in (a, b)):
                matched.append({"half_cell": hc, "si": si, "delta_LLI_pct": d})
    if all_pairs:
        v = np.array(all_pairs, dtype=float)
        summary["dqdv_paired_contrast"] = {
            "all_pairs": {"n": int(v.size), "n_positive": int((v > 0).sum()),
                          "n_negative": int((v < 0).sum()),
                          "median_pct": float(np.median(v)),
                          "min_pct": float(v.min()), "max_pct": float(v.max())},
            "both_endpoints_interior": {
                "n": len(matched), "rows": matched,
                "delta_range_pct": [min(m["delta_LLI_pct"] for m in matched),
                                    max(m["delta_LLI_pct"] for m in matched)]
                if matched else None},
            "note": "비대응 비교는 부호가 섞인다 — 대응쌍으로만 말할 것"}
    print("\nSUMMARY " + json.dumps(summary, ensure_ascii=False, default=float))
    if args.out:
        import csv
        keys = sorted({k for r in rows for k in r})
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            w_ = csv.DictWriter(fh, fieldnames=keys)
            w_.writeheader()
            w_.writerows(rows)
        print(f"wrote {args.out}")



# ── F. γ_Si ↔ a_NE 프로파일 (Schmitt 2022 가 "같은 서명" 이라 쓰고 안 잰 자리) ──

def cmd_profile(args):
    """γ_Si 를 고정하고 나머지 넷을 다시 적합 — 프로파일 목적함수.

    평평하면 γ 와 나머지가 서로를 대신할 수 있다는 뜻이고, 그때 LAM_NE 는
    데이터가 아니라 **γ 를 준 사람**이 정한 값이다.
    """
    root = D.data_root(args.data_root)
    ref = build(root, args.source, "pristine", args.si_source,
                w_dqdv=args.w_dqdv, scale_seed=args.seed)
    ref_p, _, _ = multistart(ref, n_starts=args.starts, seed=args.seed)
    obj = build(root, args.source, args.state, args.si_source,
                w_dqdv=args.w_dqdv, scale_seed=args.seed)
    best, best_val, _ = multistart(obj, n_starts=args.starts, seed=args.seed)

    gammas = np.linspace(LB5[4], UB5[4], args.grid)
    per_gamma_scale = getattr(args, "profile_scale", "global") == "per-gamma"
    global_scales = dict(obj.scales)
    rows, skipped = [], []
    for g in gammas:
        if per_gamma_scale:
            # MATLAB 검증기 절차: lb(5)=ub(5)=g 를 넘겨서 fit 을 부르므로,
            # 원 scale 식이 넘겨받은 경계를 쓰면 γ 마다 scale 이 달라진다 [A1].
            # ⚠ 그러면 행마다 **다른 목적함수**라서 obj_ratio_to_best 를 행끼리
            #   비교할 수 없다. 그 사실을 산출에 같이 적는다.
            lbg, ubg = LB5.copy(), UB5.copy()
            lbg[4] = ubg[4] = g
            obj.scales = obj._auto_scales(args.seed, obj.n_scale_samples,
                                          lb=lbg, ub=ubg)
        f = lambda q: obj(np.array([q[0], q[1], q[2], q[3], g]))   # noqa: E731
        bnds = list(zip(LB5[:4], UB5[:4]))
        bv, bx = np.inf, None
        rng = np.random.default_rng(args.seed)
        starts = [best[:4]] + list(LB5[:4] + rng.random((args.starts, 4))
                                   * (UB5[:4] - LB5[:4]))
        # ⚠ 2026-09-11 Codex R2-03: 이 loop 는 multistart 의 success 필터를 안 받아
        #   비정상 종료 결과를 완료 적합처럼 저장했다 (리뷰 A3 의 미종결 경로).
        #   같은 정책으로 거르고, 시도/성공 수를 행에 남기며, 전부 실패한 γ 는
        #   저장하지 않는다.
        n_tried = n_ok = 0
        for s in starts:
            n_tried += 1
            try:
                r = minimize(f, s, method="L-BFGS-B", bounds=bnds,
                             options={"maxiter": 400, "ftol": 1e-12})
            except Exception:                            # noqa: BLE001
                continue
            if not np.isfinite(r.fun) or not bool(getattr(r, "success", True)):
                continue
            n_ok += 1
            if r.fun < bv:
                bv, bx = float(r.fun), r.x.copy()
        if bx is None:
            print(f"[profile] γ={g:.4f}: 시작점 {n_tried}개 전부 실패 (not_success/비유한) — "
                  f"이 γ 는 저장하지 않는다 (skipped)", flush=True)
            skipped.append(float(g))
            continue
        p = np.array([bx[0], bx[1], bx[2], bx[3], g])
        m = degradation_modes(ref_p, ref.c_cell, p, obj.c_cell)
        rows.append({"gamma_Si": float(g), "obj": bv,
                     "obj_ratio_to_best": bv / best_val,
                     "rmse_pocv": obj.rmse_pocv(p),
                     "a_PE": float(p[0]), "b_PE": float(p[1]),
                     "a_NE": float(p[2]), "b_NE": float(p[3]),
                     "bounds": ",".join(active_bounds(p)) or "-",
                     "LAM_PE_pct": m["LAM_PE"] * 100,
                     "LAM_NE_pct": m["LAM_NE"] * 100,
                     "LLI_pct": m["LLI"] * 100,
                     "n_ok": n_ok, "n_tried": n_tried})
        print(json.dumps(rows[-1], ensure_ascii=False, default=float), flush=True)

    inside = [r for r in rows if r["obj_ratio_to_best"] <= 1 + args.tol]
    obj.scales = global_scales
    summary = {"state": args.state, "si_source": args.si_source,
               "half_cell": args.source, "best_obj": best_val,
               "profile_scale": "per-gamma" if per_gamma_scale else "global",
               "ratio_comparable_across_rows": not per_gamma_scale,
               "scale_note": (
                   "per-gamma 는 행마다 목적함수가 달라 obj_ratio_to_best 를 "
                   "행끼리 비교할 수 없다. global 은 비교는 되지만 MATLAB "
                   "검증기가 넘기는 경계와 다르다 [리뷰 A1 — 미결]."
                   if per_gamma_scale else
                   "global: 모든 행이 같은 목적함수라 비교는 되지만, MATLAB "
                   "검증기는 γ 를 묶은 경계를 넘긴다 [리뷰 A1 — 미결]."),
               "best_gamma": float(best[4]),
               "tol_percent": args.tol * 100,
               "gamma_inside_tol": [float(min(r["gamma_Si"] for r in inside)),
                                    float(max(r["gamma_Si"] for r in inside))]
               if inside else None,
               "n_inside": len(inside),
               "gamma_all_failed": skipped}
    for k in ("a_NE", "LAM_NE_pct", "LAM_PE_pct", "LLI_pct"):
        if inside:
            v = np.array([r[k] for r in inside], dtype=float)
            summary[k + "_span_inside_tol"] = float(v.max() - v.min())
    print("\nSUMMARY " + json.dumps(summary, ensure_ascii=False, default=float))
    # ⚠ 2026-09-11 Codex R3-08: 전 판은 전부 실패하면 파일을 안 쓰고 **정상 반환**했다 — 같은
    #   경로에 옛 CSV 가 있으면 wrapper 가 그것을 새 성공으로 읽었다. 이제 (i) 산출은 임시 파일에
    #   쓴 뒤 한 번에 옮기고(반쯤 쓰인 파일이 남지 않는다), (ii) 저장할 행이 없으면 종료 코드 2 —
    #   옛 파일은 지우지 않지만(보존) 이번 실행의 결과가 아니다.
    if args.out and rows:
        import csv
        out = Path(args.out)
        part = out.with_name(out.name + ".part")
        with open(part, "w", newline="", encoding="utf-8") as fh:
            w_ = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w_.writeheader(); w_.writerows(rows)
        os.replace(part, out)
        print(f"wrote {args.out}")
        return 0
    if not rows:
        print(f"[profile] 저장할 행이 없다 (모든 γ 가 실패)"
              + (f" — {args.out} 를 쓰지 않는다 (기존 파일이 있어도 이번 실행의 산출이 아니다)"
                 if args.out else "") + " → 종료 코드 2")
        return 2
    return 0



# ── G. 측정 잡음 규모 — "1 % 띠" 를 정확도 언어로 쓸 수 있나 ──────────────

def diff_sigma(y: np.ndarray, order: int = 2, stride: int = 1) -> float:
    """m 차 차분 잡음 추정 — **모델도 반복측정도 필요 없다.**

        sigma^2 = sum (D^m y)^2 / ( (n-m) * C(2m, m) )

    m=2 가 고전적인 Rice/GSJS 추정기다 (C(4,2)=6). 왜 되나: 참 곡선이
    매끄러우면 m 차 차분이 그 부분을 거의 지우고(다항식 차수 m-1 까지는
    정확히 0) 잡음만 남는다. 계수 C(2m,m) 은 독립 잡음의 m 차 차분 분산이다.

    `order` 를 올리면 곡률 오염이 줄고, `stride` 를 올리면 **상관된 잡음이
    분리된다.** 둘을 같이 훑는 것이 `noise_diagnosis` 의 판정이다.
    """
    from math import comb
    y = np.asarray(y, dtype=float)[::max(1, int(stride))]
    m = int(order)
    if y.size <= m + 1:
        return float("nan")
    d = y
    for _ in range(m):
        d = np.diff(d)
    return float(np.sqrt(np.sum(d ** 2) / (d.size * comb(2 * m, m))))


def rice_sigma(y: np.ndarray) -> float:
    """m=2 고정 — 옛 이름 유지."""
    return diff_sigma(y, order=2, stride=1)


def noise_diagnosis(y: np.ndarray) -> dict:
    """sigma 를 재고, **이 방법이 어디서 멈추는지**를 같이 적는다.

    2026-09-10. 이 함수는 네 번 고쳐 쓴 끝에 "가르지 않는다" 로 끝났다.
    실패의 기록을 남긴다 — 같은 길을 다시 걷지 않게.

    (1) 1 차 차분의 lag-1 자기상관이 양수면 "평활된 신호" 라고 단정했다.
        못 가른다. 촘촘히 표본된 깨끗한 신호에서도, 표본 간 전압 변화가 잡음과
        같은 규모면 양수가 된다. 실측(`300_0009`)이 정확히 그 경계였다
        (표본당 dV 약 20 uV, sigma 약 28 uV, 자기상관 +0.417).
    (2) 스트라이드 스캔을 넣고 "커지면 평활" 이라 했다. **곡률도 커진다.**
        잡음 0 인 해석 곡선에서 406 배 커졌다.
    (3) 배증당 성장률로 세 경우를 가르려 했다. 문턱이 합성 경계에서 흔들렸다
        (독립 1.00 / 평활 1.41 / 해석곡선 2.46 — 뒤의 둘이 안 갈린다).
    (4) 스캔 최댓값을 상한으로 쓰려 했다. **상관 길이보다 스캔이 짧으면
        상한이 못 된다** (savgol(201) 신호를 k<=64 로 훑으면 참 0.500 mV 를
        0.033 mV 로 본다). 멀리까지 훑으면 이번엔 곡률이 먼저 올라와서
        평탄부가 안 생긴다 — 네 합성 케이스 전부 평탄 판정 실패.

    **구조적인 이유**: 한 곡선에서 "측정 잡음" 과 "매끄러운 신호" 를 가르려면
    둘의 주파수 대역이 갈라져 있어야 한다. 잡음이 이미 필터링됐고 신호에 그와
    비슷한 스케일의 곡률이 있으면, **한 곡선만으로는 원리적으로 못 가른다.**
    이 프로젝트가 다루는 축퇴와 같은 종류의 문제다.

    그래서 판정하지 않고 **두 해석을 다 적는다**:

        원자료(필터 안 걸림)이면  -> k=1 의 sigma 가 잡음. 비율을 그대로 씀
        필터 걸린 자료면          -> k=1 의 sigma 는 하한, 비율은 **상한**

    어느 쪽인지는 **곡선이 아니라 계측 쪽에 물어야 답이 나온다** — 그 질문을
    `FOR_BMS_TEAM.md` 에 넣었다. 원자료 export 가 따로 있으면 거기에 이 명령을
    걸어 보는 것이 곧바로 답이다.

    차수 스캔(m=1..4)은 여전히 쓸모가 있다: k=1 에서 m 을 올려도 sigma 가 거의
    안 변하면 **그 지점에서는 곡률 오염이 없다**는 뜻이다 (합성 독립잡음:
    0.0328 / 0.0299 / 0.0299 / 0.0299).
    """
    orders = {m: diff_sigma(y, order=m) for m in (1, 2, 3, 4)}
    n = int(np.asarray(y).size)
    ks, k = [], 1
    while k <= max(1, n // 64) and k <= 1024:
        ks.append(k); k *= 2
    strides = {k: diff_sigma(y, order=4, stride=k) for k in ks}
    o = [orders[m] for m in (2, 3, 4) if orders[m] == orders[m] and orders[m] > 0]
    order_flat = bool(o and max(o) / min(o) < 1.15)
    return {
        "sigma_by_order_V": orders,
        "sigma_by_stride_order4_V": strides,
        "sigma_at_k1_V": strides.get(1, float("nan")),
        "order_scan_flat": order_flat,
        "order_scan_reading": (
            "m=2..4 에서 sigma 가 15 % 안에서 같다 -> k=1 에서 **곡률 오염은 없다**."
            if order_flat else
            "m 을 올리면 sigma 가 15 % 넘게 줄어든다 -> k=1 에 **곡률이 섞여 있다** "
            "(참 잡음은 더 작다)."),
        "note": ("이 값이 잡음인지 필터의 잔재인지는 **한 곡선으로 못 가른다** "
                 "(머리말 참조). 원자료 export 에 같은 명령을 걸면 곧바로 답이 "
                 "나온다."),
    }


def cmd_noise(args):
    """측정 잡음 σ 를 재고, 모델 부적합과 견준다.

    이 명령이 답하는 질문: **"최적의 1 % 안" 을 오차막대라고 불러도 되나?**

    안 된다는 것을 보이는 방식이 중요하다. 잡음을 못 재서가 아니라, 재고 나면
    **부적합이 잡음보다 압도적으로 크다**는 것이 드러나기 때문이다. 그러면
    목적함수를 likelihood 로 바꿔 신뢰구간을 만드는 절차 자체가 성립하지 않는다
    (χ² 이 자유도보다 훨씬 커서 곡률 기반 구간이 **거짓으로 좁아진다**).
    """
    root = D.data_root(args.data_root)
    obj = build(root, args.source, args.state, args.si_source,
                w_dqdv=args.w_dqdv, scale_seed=args.seed)

    cap_raw, vol_raw = D.load_full_cell(root, args.state)
    cap_ad, vol_ad = average_duplicates(cap_raw, vol_raw)
    order = np.argsort(cap_ad)
    v_ad = vol_ad[order]

    best, best_val, _ = multistart(obj, n_starts=args.starts, seed=args.seed)
    resid = obj.voltage - obj.E_cell(best, obj.capacity)
    misfit = float(np.sqrt(np.mean(resid ** 2)))

    s_raw = rice_sigma(v_ad)
    s_res = rice_sigma(resid)
    d1 = np.diff(v_ad)
    ac1 = float(np.corrcoef(d1[:-1], d1[1:])[0, 1]) if d1.size > 2 else float("nan")
    diag = noise_diagnosis(v_ad)
    s_k1 = diag["sigma_at_k1_V"]

    out = {
        "state": args.state, "si_source": args.si_source, "half_cell": args.source,
        "n_points_raw": int(cap_raw.size), "n_points_after_avg": int(v_ad.size),
        "sigma_meas_from_raw_V": s_raw,
        "sigma_meas_from_residual_V": s_res,
        "lag1_autocorr_of_first_diff": ac1,
        "misfit_rmse_pocv_V": misfit,
        "misfit_over_sigma": misfit / s_raw if s_raw > 0 else float("inf"),
        "sigma_at_k1_V": s_k1,
        "misfit_over_sigma_if_raw_data": misfit / s_k1 if s_k1 > 0 else float("inf"),
        "diagnosis": diag,
        "best_p": [float(x) for x in best], "best_obj": float(best_val),
    }
    # lag-1 자기상관은 **단독으로는 판정 못 한다** (noise_diagnosis 머리말).
    # 판정은 스트라이드 스캔이 한다. 자기상관은 참고로만 남긴다.
    # 어느 오염 방향이든 결론이 같은가 — 그것만 본다 (noise_diagnosis 머리말)
    r = out["misfit_over_sigma_if_raw_data"]
    out["verdict"] = (
        "**원자료라면** 부적합이 잡음보다 {:.0f} 배 크다. 목적함수를 likelihood 로 바꿔 신뢰구간을 "
        "만들면 χ² 이 자유도보다 {:.0f}² 배 커서 **거짓으로 좁은** 구간이 나온다. "
        "그러므로 '1 % 띠' 는 오차막대가 아니라 **분석자 선택 민감도**로만 읽어야 "
        "한다 — 이것은 잡음을 못 재서가 아니라, 재고 나서 내린 결론이다."
    ).format(r, r) if r > 3 else (
        "부적합이 잡음과 같은 규모다 ({:.1f} 배). 이 경우에는 likelihood 기반 "
        "구간을 논의할 여지가 있다.".format(r))
    out["caveat"] = (
        "σ 는 **고주파** 성분만 잡는다. 드리프트·오프셋 같은 저주파 측정오차는 "
        "이 방법으로 안 잡히므로 σ 는 **하한**이고 따라서 misfit/σ 는 **상한**이다. "
        "잡음이 상관돼 있으면 k=1 의 σ 는 더 작게 나오므로 스캔이 평평해지는 "
        "값을 쓴다.")
    print(json.dumps(out, ensure_ascii=False, indent=2, default=float))



def main(argv=None):
    ap = argparse.ArgumentParser(prog="bms_balancing.verify")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("port", cmd_port), ("degeneracy", cmd_degeneracy),
                     ("scale-noise", cmd_scale_noise), ("matrix", cmd_matrix),
                     ("profile", cmd_profile), ("eval", cmd_eval),
                     ("noise", cmd_noise)):
        p = sub.add_parser(name)
        p.add_argument("--data-root", default=None)
        p.add_argument("--source", default="GITT", choices=list(D.HALF_FILE))
        p.add_argument("--state", default="pristine", choices=D.STATES)
        p.add_argument("--si-source", default="Li", choices=D.SI_SOURCES)
        p.add_argument("--w-dqdv", type=float, default=0.0)
        p.add_argument("--starts", type=int, default=24)
        p.add_argument("--seed", type=int, default=0)
        p.add_argument("--samples", type=int, default=400)
        p.add_argument("--tol", type=float, default=0.01)
        p.add_argument("--repeats", type=int, default=5)
        p.add_argument("--out", default=None)
        p.add_argument("--only-source", action="store_true")
        p.add_argument("--only-wdqdv", action="store_true")
        p.add_argument("--grid", type=int, default=21)
        p.add_argument("--blind", action="store_true",
                       help="port: 보고값을 시작점에서 뺀다 (독립 재적합)")
        p.add_argument("--profile-scale", choices=["global", "per-gamma"],
                       default="global",
                       help="profile: 목적함수 scale 을 전역 경계에서 한 번 "
                            "뽑을지(기본 — 원 파이프라인과 같다), γ 를 묶은 "
                            "경계에서 행마다 다시 뽑을지. per-gamma 는 그들 "
                            "절차가 아니라 dd_verify.m profile 모드의 부작용을 "
                            "재현하는 진단용이다 (행끼리 비교 불가)")
        p.add_argument("--compare", default=None,
                       help="dd_eval.m 이 낸 CSV 와 대조한다 (eval 전용). 종료 코드: 0 complete · "
                            "1 갈림 · 2 미완 · 3 부분(옛 스키마)")
        p.add_argument("--precision", default="auto",
                       help="eval --compare: CSV 의 출력 정밀도. auto(파일의 `# printed_format` "
                            "선언 → 없으면 자리수 추정) | g17 | full | fixed:N")
        p.add_argument("--allow-partial", action="store_true",
                       help="eval --compare: 옛 스키마(앵커·열 누락)의 부분 대조를 종료 코드 0 으로 "
                            "허용한다 — 판정문에는 그대로 '부분' 이 남는다")
        p.set_defaults(func=fn)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
