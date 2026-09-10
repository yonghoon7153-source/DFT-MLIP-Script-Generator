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
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import NonlinearConstraint, minimize

from . import data as D
from .model import LB5, UB5, Blend, HalfCell, Objective, degradation_modes


def build(root: Path, source: str, state: str, si_source: str,
          w_dqdv: float = 0.0, use_peak_weight: bool = True,
          scale_seed: int = 0) -> Objective:
    half = HalfCell(D.half_cell_path(root, source, state), window=11, poly_order=3)
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
                         seed: int = 0):
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
        grid = np.unique(np.concatenate([np.linspace(v_lo, v_hi, n_grid), [v_best]]))
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
                    "n_grid_attainable": int(a.size), "n_grid": int(grid.size),
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
    prof = mode_profile_extrema(obj, ref_best, ref_obj.c_cell, obj.c_cell,
                                best, best_val, args.tol,
                                n_grid=getattr(args, "grid", 21),
                                n_starts=3, seed=args.seed)
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
    ("E_PE_0p5",       "반쪽전지 적재 (electrode_ocv) — PE OCP"),
    ("E_NE_0p5_0p25",  "문헌 적재 + build_blend_functions — 블렌드 OCP"),
    ("dv_PE_0p5",      "반쪽전지 differential — PE dV/dQ"),
    ("dv_NE_0p5_0p25", "블렌드 differential — NE dV/dQ"),
]


def dd_eval_anchors(obj: Objective) -> list[tuple[str, float]]:
    """`matlab/dd_eval.m` 이 CSV 앞머리에 적는 앵커와 **같은 이름·같은 순서**."""
    return [
        ("c_cell",         float(obj.c_cell)),
        ("dv_lo",          float(obj.dv_window[0])),
        ("dv_hi",          float(obj.dv_window[1])),
        ("dv_n",           float(len(obj.cap_dv_fit))),
        ("dq_lo",          float(obj.dq_window[0])),
        ("dq_hi",          float(obj.dq_window[1])),
        ("E_PE_0p5",       float(np.atleast_1d(obj.half.E_PE(0.5))[0])),
        ("E_NE_0p5_0p25",  float(np.atleast_1d(obj.blend.E(np.atleast_1d(0.5), 0.25))[0])),
        ("dv_PE_0p5",      float(np.atleast_1d(obj.half.dv_PE(0.5))[0])),
        ("dv_NE_0p5_0p25", float(np.atleast_1d(obj.blend.dv(np.atleast_1d(0.5), 0.25))[0])),
    ]


def read_dd_eval_csv(path):
    """dd_eval.m 산출(`# 이름,값` 앞머리 + 파라미터 행)을 읽는다."""
    anchors, rows = {}, []
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line.startswith("#") and "," in line:
            k, _, v = line.lstrip("# ").partition(",")
            try:
                anchors[k.strip()] = float(v)
            except ValueError:
                pass
        elif line and not line.startswith("#") and not line.startswith("a_PE"):
            try:
                rows.append([float(x) for x in line.split(",")])
            except ValueError:
                pass
    return anchors, rows


def printed_abs_tol(path, default_decimals: int = 10) -> float:
    """CSV 에 **적힌 자리수**가 허용하는 절대 오차.

    ⚠ 2026-09-10 실측: `dd_eval.m` 은 rmse 를 `%.10f` 로 쓴다. 그러면 절대
      양자화가 ±0.5e-10 이고, rmse_pocv≈0.0117 에서 그것만으로 **상대 4.3e-9**
      가 된다. 그 파일을 상대 1e-9 문턱으로 재면 **없는 불일치를 보고**한다
      (실제로 그랬다). 양쪽 다 반올림하므로 한계는 그 두 배로 잡는다.
    """
    d = default_decimals
    try:
        for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("a_PE"):
                continue
            for field in line.split(",")[5:]:
                if "e" in field.lower():
                    d = min(d, 17)          # 전정밀도 — 상대문턱이 지배한다
                elif "." in field:
                    d = min(d, len(field.split(".")[1]))
            break
    except OSError:
        pass
    return 10.0 ** (-d)


def cmd_eval(args):
    """적합 없이 주어진 p 에서 rmse 를 찍고, 원하면 MATLAB 산출과 대조한다.

    툴박스가 없는 기계에서도 포팅 대조를 할 수 있게 만든 우회로다:
    포팅이 맞는지 묻는 데 정말 필요한 것은 최적화기가 아니라 **모델**이므로,
    같은 p 에서 두 구현이 같은 rmse 를 내는지만 보면 된다.
    """
    root = D.data_root(args.data_root)
    obj = build(root, args.source, args.state, args.si_source,
                w_dqdv=args.w_dqdv, scale_seed=args.seed)

    anchors = dd_eval_anchors(obj)
    print(f"# dd_eval  state={args.state}  halfcell=data/half_cell/{args.source}/  "
          f"Si={args.si_source}  w_dqdv={args.w_dqdv:g}")
    for k, v in anchors:
        print(f"# {k},{v:.17g}")

    P = np.array(DD_EVAL_P, dtype=float)
    lines = ["a_PE,b_PE,a_NE,b_NE,gamma_Si,rmse_pocv,rmse_dvdq"]
    print(lines[0])
    for q in P:
        r = f"{q[0]:.6f},{q[1]:.6f},{q[2]:.6f},{q[3]:.6f},{q[4]:.6f}," \
            f"{obj.rmse_pocv(q):.10f},{obj.rmse_dvdq(q):.10f}"
        lines.append(r)
        print(r)

    if args.out:
        head = [f"# dd_eval  state={args.state}  halfcell=data/half_cell/{args.source}/  "
                f"Si={args.si_source}  w_dqdv={args.w_dqdv:g}"]
        head += [f"# {k},{v:.17g}" for k, v in anchors]
        Path(args.out).write_text("\n".join(head + lines) + "\n", encoding="utf-8")
        print(f"\nwrote {args.out}")

    if args.compare:
        _compare_dd_eval(dict(anchors), [list(q) + [obj.rmse_pocv(q), obj.rmse_dvdq(q)]
                                         for q in P], args.compare)


def _compare_dd_eval(py_anchors, py_rows, matlab_csv):
    """MATLAB 산출과 대조하고, **갈린 첫 단계**를 이름으로 말한다."""
    m_anchors, m_rows = read_dd_eval_csv(matlab_csv)
    atol = printed_abs_tol(matlab_csv)
    print(f"\n=== dd_eval.m 대조: {matlab_csv} ===")
    print(f"  (적힌 자리수가 허용하는 절대 한계 {atol:.1e} — 이보다 작은 차이는"
          f" 두 구현의 차이가 아니라 출력 반올림이다)")
    if not m_anchors and not m_rows:
        print("  ! 읽을 내용이 없다 — 경로가 맞나?")
        return

    def rel(a, b):
        return abs(a - b) / max(abs(b), 1e-30)

    print(f"  {'앵커':<16} {'MATLAB':>22} {'Python':>22} {'상대차':>10}   단계")
    first_bad = None
    for k, stage in ANCHOR_STAGE:
        if k not in m_anchors:
            print(f"  {k:<16} {'(없음)':>22} — 옛 dd_eval.m 산출인가?")
            continue
        a, b = m_anchors[k], py_anchors[k]
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
    if len(m_rows) != len(py_rows):
        print(f"  ! 행 수가 다르다: MATLAB {len(m_rows)} vs Python {len(py_rows)}")
    else:
        print(f"  {'p 행':<5} {'rmse_pocv 상대차':>18} {'rmse_dvdq 상대차':>18}   판정")
        for i, (mr, pr) in enumerate(zip(m_rows, py_rows)):
            if len(mr) < 7:
                continue
            if max(abs(mr[j] - pr[j]) for j in range(5)) > 1e-6:
                print(f"  {i:<5} ! 파라미터가 다른 행이다 — 격자가 어긋났다")
                continue
            d1, d2 = abs(mr[5] - pr[5]), abs(mr[6] - pr[6])
            r1, r2 = rel(mr[5], pr[5]), rel(mr[6], pr[6])
            # 적힌 자리수 안이면 "차이" 가 아니다
            eff = max(r1 if d1 > atol else 0.0, r2 if d2 > atol else 0.0)
            worst_row = max(worst_row, eff)
            tag = "" if eff == 0.0 else "  ←"
            print(f"  {i:<5} {r1:>18.2e} {r2:>18.2e}"
                  f"   {'적힌 자리수 안' if eff == 0.0 else '자리수 밖'}{tag}")

    print()
    if first_bad:
        k, stage = first_bad
        print(f"판정: **{k}** 에서 처음 갈린다 → 범인 단계는 「{stage}」")
        print("      그 앞 앵커는 맞았으므로 그 앞 단계는 용의선상에서 빠진다.")
    elif worst_row > 1e-9:
        print(f"판정: 앵커는 전부 맞는데 rmse 가 갈린다 (최대 상대차 {worst_row:.2e})")
        print("      → 곡선은 같고 **목적함수 산술**이 다르다는 뜻이다.")
    else:
        print("판정: 앵커 10개와 rmse 16개가 **적힌 자리수 안에서 전부 일치**.")
        print(f"      남은 차이는 전부 CSV 출력 반올림({atol:.0e}) 안이다 —")
        print("      이 파일로는 그보다 정밀하게 비교할 수 없다.")
        print("      같은 p 에서 두 구현이 같은 목적함수를 낸다 = 포팅이 그들 모델이다.")


# ── D. scale 비결정성 ──────────────────────────────────────────────────

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
    rows = []
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
        for s in starts:
            try:
                r = minimize(f, s, method="L-BFGS-B", bounds=bnds,
                             options={"maxiter": 400, "ftol": 1e-12})
            except Exception:                            # noqa: BLE001
                continue
            if np.isfinite(r.fun) and r.fun < bv:
                bv, bx = float(r.fun), r.x.copy()
        if bx is None:
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
                     "LLI_pct": m["LLI"] * 100})
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
               "n_inside": len(inside)}
    for k in ("a_NE", "LAM_NE_pct", "LAM_PE_pct", "LLI_pct"):
        if inside:
            v = np.array([r[k] for r in inside], dtype=float)
            summary[k + "_span_inside_tol"] = float(v.max() - v.min())
    print("\nSUMMARY " + json.dumps(summary, ensure_ascii=False, default=float))
    if args.out:
        import csv
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            w_ = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w_.writeheader(); w_.writerows(rows)
        print(f"wrote {args.out}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bms_balancing.verify")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("port", cmd_port), ("degeneracy", cmd_degeneracy),
                     ("scale-noise", cmd_scale_noise), ("matrix", cmd_matrix),
                     ("profile", cmd_profile), ("eval", cmd_eval)):
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
                       help="dd_eval.m 이 낸 CSV 와 대조한다 (eval 전용)")
        p.set_defaults(func=fn)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
