"""`dd_eval.m` 의 **줄 단위 Python 전사본** — 배관 대조용.

`synth/` 의 해석적 대역품과 같은 식을 Python 으로 다시 적는다. 두 전사본이
같은 합성 데이터에서 같은 수를 내면, `dd_eval.m` 의 배관(인덱싱·마스크·
파라미터 변환·RMSE 식)에 실수가 없다는 뜻이다. 모델 정확도와는 무관하다 —
`synth/README_SYNTH.md` 참고.
"""
from __future__ import annotations
import argparse, pathlib, sys
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from bms_balancing.model import matlab_quantile, average_duplicates   # noqa: E402

STATES = ["pristine", "100", "200", "300_0009", "300_0147"]


def g17(v: float) -> str:
    """MATLAB `%.17g` 와 같은 문자열 — 앵커를 바이트 단위로 대조하려고."""
    return f"{v:.17g}"


def read_csvtable(p: pathlib.Path):
    """oct_stubs/readtable.m 과 같은 규약 — 헤더 한 줄 + 숫자."""
    names = p.read_text().splitlines()[0].split(",")
    M = np.atleast_2d(np.loadtxt(p, delimiter=",", skiprows=1))
    return {n.strip(): M[:, k] for k, n in enumerate(names)}


# ── synth/ 의 해석적 대역품을 그대로 옮긴다 ─────────────────────────────
def synth_electrode_ocv(dirpath: pathlib.Path, filename: str, dp: dict):
    f = dirpath / filename
    if not f.is_file():
        raise SystemExit(f"electrode_ocv(mirror): 파일이 없다: {f}")
    T = read_csvtable(f)
    s = float(np.mean(T["PE_capacity"][np.isfinite(T["PE_capacity"])]))
    w = dp["window"]
    return {
        "E_PE":  lambda x: 3.90 - 0.70 * np.asarray(x) + 0.02 * s * np.sin(2 * np.asarray(x)),
        "dv_PE": lambda x: -0.70 + 0.05 * np.cos(w * np.asarray(x) / 10),
    }


def synth_build_blend(si_c, si_v, gr_c, gr_v, dp: dict):
    a = float(np.mean(si_c[np.isfinite(si_c)]))
    b = float(np.mean(gr_v[np.isfinite(gr_v)]))
    w = dp["poly_order"]
    E_NE = lambda x, g: 0.25 + 0.35 * np.asarray(x) - 0.20 * g + 0.05 * a * g * np.asarray(x) + 0.01 * b  # noqa: E731
    dv_NE = lambda x, g: 0.10 * np.cos(2 * np.asarray(x)) + 0.05 * g + 0.001 * w                          # noqa: E731
    return E_NE, dv_NE


def synth_differential(capacity, voltage, window, poly_order):
    capacity, voltage = np.asarray(capacity, float), np.asarray(voltage, float)
    ok = np.isfinite(capacity) & np.isfinite(voltage)
    capacity, voltage = capacity[ok], voltage[ok]
    n, k = 500, window + 0.1 * poly_order
    c2 = np.linspace(capacity.min(), capacity.max(), n)
    v1 = np.linspace(voltage.min(), voltage.max(), n)
    return {"capacity_uniform2": c2, "voltage_uniform2": 4.1 - 0.8 * c2,
            "dvdq": -0.8 + 0.3 * np.sin(k * c2),
            "voltage_uniform": v1,
            "capacity_uniform": (v1 - v1.min()) / (v1.max() - v1.min()),
            "dqdv": -1.25 + 0.4 * np.cos(k * v1)}


# ── dd_eval.m 본문의 전사 ───────────────────────────────────────────────
def local_halfcell_name(dirpath: str, state: str) -> str:
    return f"{state}_005C.xlsx" if "005C" in dirpath else f"{state}.xlsx"


def local_fullcell(root: pathlib.Path, state: str):
    d = sorted((root / "data/full_cell/large_cell_033C").glob("*.xlsx"))
    f = next((p for p in d if "pristine" not in p.name and "300cycle" not in p.name), None)
    if f is None:
        raise SystemExit("mirror: 풀셀 워크북을 못 찾았다")
    col = STATES.index(state) + 1                      # MATLAB 1-based
    M = np.loadtxt(f, delimiter=",", skiprows=2)
    c, v = M[:, 2 * col - 2], M[:, 2 * col - 1]        # MATLAB M(:,2c-1), M(:,2c)
    ok = ~np.isnan(c) & ~np.isnan(v)
    return c[ok], v[ok]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--half-cell-dir", default="data/half_cell/GITT/")
    ap.add_argument("--si-source", default="Li")
    ap.add_argument("--state", default="pristine")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    root = pathlib.Path(a.root)
    dp = {"window": 11, "poly_order": 3}

    ro = synth_electrode_ocv(root / a.half_cell_dir,
                             local_halfcell_name(a.half_cell_dir, a.state), dp)
    g = read_csvtable(root / "data/literature/Si_Gr_literature_OCP.xlsx")
    s = read_csvtable(root / f"data/literature/Si_OCP_sources/{a.si_source}.csv")
    E_NE, dv_NE = synth_build_blend(s["normalizedCapacity"], s["voltage"],
                                    g["Gr_capacity"][np.isfinite(g["Gr_capacity"])],
                                    g["Gr_voltage"][np.isfinite(g["Gr_voltage"])], dp)

    cap, vol = local_fullcell(root, a.state)
    cap, vol = average_duplicates(cap, vol)
    c_cell = float(cap[-1])
    cap = cap / c_cell if vol[0] < vol[-1] else 1.0 - cap / c_cell

    d = synth_differential(cap, vol, dp["window"], dp["poly_order"])
    lo = matlab_quantile(d["capacity_uniform2"], 0.15)
    hi = matlab_quantile(d["capacity_uniform2"], 0.85)
    idx = (d["capacity_uniform2"] >= lo) & (d["capacity_uniform2"] <= hi)
    cap_dv, dv_dat = d["capacity_uniform2"][idx], d["dvdq"][idx]
    vlo = matlab_quantile(d["voltage_uniform"], 0.05)
    vhi = matlab_quantile(d["voltage_uniform"], 0.95)

    # dd_eval.m 과 **같은 순서·같은 형식**의 이분 앵커
    anchors = [("c_cell", c_cell), ("dv_lo", lo), ("dv_hi", hi),
               ("dv_n", float(idx.sum())), ("dq_lo", vlo), ("dq_hi", vhi),
               ("E_PE_0p5", float(ro["E_PE"](0.5))),
               ("E_NE_0p5_0p25", float(E_NE(0.5, 0.25))),
               ("dv_PE_0p5", float(ro["dv_PE"](0.5))),
               ("dv_NE_0p5_0p25", float(dv_NE(0.5, 0.25)))]
    for k, v in anchors:
        print(f"{k:<16} = {g17(v)}")
    print()

    P = np.array([
        [1.077218, -0.022949, 1.001342, 0.000309, 0.295099],
        [1.076074, -0.022129, 1.001279, 0.000299, 0.295298],
        [1.181472, -0.141171, 1.080759, -0.000775, 0.239466],
        [1.080000, -0.040000, 1.050000, -0.030000, 0.250000],
        [1.100000, -0.050000, 1.100000, -0.010000, 0.100000],
        [1.100000, -0.050000, 1.100000, -0.010000, 0.200000],
        [1.100000, -0.050000, 1.100000, -0.010000, 0.300000],
        [1.100000, -0.050000, 1.100000, -0.010000, 0.400000]])
    lines = [f"# dd_eval  state={a.state}  halfcell={a.half_cell_dir}  "
             f"Si={a.si_source}  w_dqdv={0:g}"]
    lines += [f"# {k},{g17(v)}" for k, v in anchors]
    lines.append("a_PE,b_PE,a_NE,b_NE,gamma_Si,rmse_pocv,rmse_dvdq")
    for q in P:
        e_model = ro["E_PE"]((cap - q[1]) / q[0]) - E_NE((cap - q[3]) / q[2], q[4])
        r_pocv = float(np.sqrt(np.mean((vol - e_model) ** 2)))
        dv_model = ro["dv_PE"]((cap_dv - q[1]) / q[0]) - dv_NE((cap_dv - q[3]) / q[2], q[4])
        r_dvdq = float(np.sqrt(np.mean((dv_dat - dv_model) ** 2)))
        lines.append(",".join([f"{x:.6f}" for x in q] + [f"{r_pocv:.10f}", f"{r_dvdq:.10f}"]))
    print("\n".join(lines))
    if a.out:
        pathlib.Path(a.out).write_text("\n".join(lines) + "\n")
        print(f"wrote {a.out}")
    return anchors


if __name__ == "__main__":
    main()
