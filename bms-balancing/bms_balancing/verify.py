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
from scipy.optimize import minimize

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
               x0: np.ndarray | None = None):
    """fmincon+MultiStart 대응 — L-BFGS-B 다중 시작."""
    rng = np.random.default_rng(seed)
    starts = [np.asarray(x0, dtype=float)] if x0 is not None else []
    starts += list(LB5 + rng.random((n_starts, 5)) * (UB5 - LB5))
    best, best_val = None, np.inf
    all_sols = []
    bounds = list(zip(LB5, UB5))
    for s in starts:
        try:
            r = minimize(obj, s, method="L-BFGS-B", bounds=bounds,
                         options={"maxiter": 500, "ftol": 1e-12, "gtol": 1e-10})
        except Exception:                               # noqa: BLE001
            continue
        if not np.isfinite(r.fun):
            continue
        all_sols.append((float(r.fun), r.x.copy()))
        if r.fun < best_val:
            best, best_val = r.x.copy(), float(r.fun)
    return best, best_val, all_sols


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

    best, val, _ = multistart(obj, n_starts=args.starts, seed=args.seed,
                              x0=np.array(rep, dtype=float) if rep and all(
                                  x is not None for x in rep) else None)
    out["our_p"] = [float(x) for x in best]
    out["our_obj"] = val
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
    for k, v in arr.items():
        out[f"{k}_percent"] = {"min": float(v.min()), "max": float(v.max()),
                               "span": float(v.max() - v.min()),
                               "median": float(np.median(v))}
    print(json.dumps(out, ensure_ascii=False, indent=2, default=float))


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
                rows.append({
                    "half_cell": hc, "si": si, "w_dqdv": w,
                    "obj": val, "rmse_pocv": o.rmse_pocv(p),
                    "a_PE": p[0], "b_PE": p[1], "a_NE": p[2], "b_NE": p[3],
                    "gamma_Si": p[4],
                    "bounds": ",".join(active_bounds(p)) or "-",
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
    rows = []
    for g in gammas:
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
    summary = {"state": args.state, "si_source": args.si_source,
               "half_cell": args.source, "best_obj": best_val,
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
                     ("profile", cmd_profile)):
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
        p.set_defaults(func=fn)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
