"""cells.py — /cells 화면용 (registry + import 요약 + cut-off 별 색 차트). 읽기 전용.

정본: data/registry/cells.csv (메타) · data/cells/<id>/summary.json, cycles.csv (import 산출물) ·
config/cells.yaml (offset·DOE·색). 이 모듈은 그것들을 **읽어서** 화면 자료구조로만 만든다.
차트는 서버가 SVG 좌표를 계산한다 (CSP 로 JS 차트 라이브러리를 못 쓴다 — 선행 브랜치와 같은 방식).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from tools.cells import cellio as C
except Exception:  # pandas 등이 없어도 앱은 뜬다 — 화면이 "모듈 비활성" 을 알린다
    C = None


def available() -> bool:
    return C is not None


def overview() -> dict:
    if C is None:
        return {"ok": False, "rows": [], "by_cutoff": [], "chart": None, "cfg": {}, "n": 0}
    cfg = C.load_config()
    reg = C.load_registry(cfg=cfg)
    summ = {s["cell_id"]: s for s in C.load_summaries(cfg)}
    rows = []
    for r in reg:
        s = summ.get(r["cell_id"])
        rows.append({**r, "summary": s, "url": f"/cell/{r['cell_id']}"})
    # registry 에 없는 import 산출물도 보인다 (등록을 잊었을 때 사라지지 않게)
    for cid, s in summ.items():
        if cid not in {r["cell_id"] for r in reg}:
            rows.append({"cell_id": cid, "formation_cutoff_v_li": "", "formation_cutoff_v_li_num": s.get("formation_cutoff_v_li"),
                         "active_mass_mg": "", "status": "(registry 없음)", "notes": "", "raw_file": "", "summary_file": "",
                         "color": C.color_for_cutoff(s.get("formation_cutoff_v_li"), cfg), "status_ok": False,
                         "summary": s, "url": f"/cell/{cid}", "orphan": True})
    # cut-off 별 n — 통계적 신뢰의 전부
    counts: dict[str, int] = {}
    for r in rows:
        k = _cut_key(r.get("formation_cutoff_v_li_num"))
        counts[k] = counts.get(k, 0) + 1
    doe = [float(x) for x in (cfg.get("doe") or {}).get("formation_cutoffs_v_li", [])]
    by_cutoff = [{"cutoff": f"{c:.1f}", "n": counts.get(f"{c:.1f}", 0), "color": C.color_for_cutoff(c, cfg)} for c in doe]
    others = sorted(k for k in counts if k not in {f"{c:.1f}" for c in doe})
    for k in others:
        by_cutoff.append({"cutoff": k if k != "none" else "미기재", "n": counts[k], "color": C.color_for_cutoff(None if k == "none" else k, cfg)})
    return {"ok": True, "rows": rows, "by_cutoff": by_cutoff, "chart": chart(rows, cfg), "cfg": cfg, "n": len(rows),
            "offset": C.offset_v(cfg), "registry_path": cfg["paths"]["registry"], "cells_dir": cfg["paths"]["cells_dir"]}


def _cut_key(v) -> str:
    try:
        return f"{float(v):.1f}"
    except (TypeError, ValueError):
        return "none"


def detail(cell_id: str) -> dict | None:
    if C is None:
        return None
    cfg = C.load_config()
    reg = {r["cell_id"]: r for r in C.load_registry(cfg=cfg)}
    summ = {s["cell_id"]: s for s in C.load_summaries(cfg)}
    r = reg.get(cell_id)
    s = summ.get(cell_id)
    if not r and not s:
        return None
    cycles = C.load_cycles(cell_id, cfg)
    off = C.offset_v(cfg)
    for c in cycles:
        for k in ("mean_charge_voltage", "mean_discharge_voltage", "v_max", "v_min"):
            v = c.get(k)
            c[k + "_li"] = (v + off) if isinstance(v, (int, float)) else None
    row = {**(r or {"cell_id": cell_id, "formation_cutoff_v_li": "", "formation_cutoff_v_li_num": (s or {}).get("formation_cutoff_v_li"),
                     "active_mass_mg": "", "status": "(registry 없음)", "notes": "", "color": C.color_for_cutoff((s or {}).get("formation_cutoff_v_li"), cfg)}),
           "summary": s, "cycles": cycles, "offset": off, "cfg": cfg}
    one = chart([row], cfg) if cycles else None
    row["chart"] = one
    return row


# ─────────────────────────────────────────────────────────────────────────
# 차트 — 방전 비용량 vs 사이클, cut-off 별 색 (config). 좌표는 서버가 계산한다.
# ─────────────────────────────────────────────────────────────────────────
def _nice_ticks(lo: float, hi: float, target: int = 6) -> list[float]:
    if hi <= lo:
        hi = lo + 1.0
    raw = (hi - lo) / max(1, target)
    mag = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1.0
    step = next((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw), 10 * mag)
    start = math.floor(lo / step) * step
    n = max(1, math.ceil((hi - start) / step - 1e-9))
    return [round(start + i * step, 10) for i in range(n + 1)]


def _fmt(v: float) -> str:
    s = f"{v:.10g}"
    return "0" if s in ("-0", "0") else s


def chart(rows: list[dict], cfg: dict, w: int = 760, h: int = 400) -> dict | None:
    series = []
    for r in rows:
        cyc = r.get("cycles")
        if cyc is None:
            cyc = C.load_cycles(r["cell_id"], cfg) if C is not None else []
        pts = [(c["cycle"], c["discharge_capacity_mah_g"]) for c in cyc
               if isinstance(c.get("cycle"), (int, float)) and isinstance(c.get("discharge_capacity_mah_g"), (int, float))]
        if not pts:
            continue
        pts.sort()
        series.append({"cell_id": r["cell_id"], "color": r.get("color", "#7f7f7f"),
                       "cutoff": r.get("formation_cutoff_v_li") or "", "pts": pts})
    if not series:
        return None
    ml, mr, mt, mb = 66, 120, 18, 54
    pw, ph = w - ml - mr, h - mt - mb
    xs = [x for s in series for x, _ in s["pts"]]
    ys = [y for s in series for _, y in s["pts"]]
    xt = _nice_ticks(min(xs), max(xs))
    yt = _nice_ticks(min(0.0, min(ys)), max(ys))
    x0, x1, y0, y1 = xt[0], xt[-1], yt[0], yt[-1]

    def px(x):
        return round(ml + (x - x0) / (x1 - x0) * pw, 2)

    def py(y):
        return round(mt + (y1 - y) / (y1 - y0) * ph, 2)

    out = []
    for s in series:
        xy = [(px(x), py(y)) for x, y in s["pts"]]
        out.append({**s, "path": "M " + " L ".join(f"{a} {b}" for a, b in xy),
                    "end": {"cx": xy[-1][0], "cy": xy[-1][1]}, "n": len(xy),
                    "pts_svg": [{"cx": a, "cy": b, "x": x, "y": y} for (a, b), (x, y) in zip(xy, s["pts"])][:400]})
    return {"w": w, "h": h, "ml": ml, "mt": mt, "pw": pw, "ph": ph,
            "x_ticks": [{"label": _fmt(t), "px": px(t)} for t in xt if x0 <= t <= x1],
            "y_ticks": [{"label": _fmt(t), "py": py(t)} for t in yt if y0 <= t <= y1],
            "series": out, "x_label": "cycle", "y_label": "discharge capacity [mAh g⁻¹ (active material)]"}
