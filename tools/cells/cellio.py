"""cellio.py — 셀 데이터 모듈의 핵심 (스키마·읽기·요약·변환). webapp/cells.py 와 import_cell.py 가 함께 쓴다.

절대 규칙의 적용
  · 전압: raw 는 vs. In/Li-In 원본. 변환은 config/cells.yaml 의 `voltage.in_to_li_offset_v` **하나**만 쓴다
    (vs. Li/Li+ = vs. In/Li-In + offset). 요약에는 원본과 변환값을 **둘 다** 싣고 offset 을 병기한다.
  · 용량: 비용량 mAh g⁻¹ (분모 = registry 의 active_mass_mg, 활물질). 질량이 없으면 mAh g⁻¹ 열을 **비운다**.
    절대용량(mAh)은 계산 중간값으로만 둔다.
  · 파일명 파싱(`propose_from_filename`)은 **제안값**이다. registry(`data/registry/cells.csv`)만 정본.
  · LLM 에는 `llm_summary()` 의 요약 문자열만 넘어간다 — raw CSV 는 넘기지 않는다.

의존성: pandas (import 시), PyYAML (config). 둘 다 없으면 함수 호출 시점에 명확한 예외를 낸다.
"""
from __future__ import annotations

import csv
import io
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "cells.yaml"

# config 가 깨졌을 때의 최후 기본값 — **정본은 config/cells.yaml** 이다. 여기 값을 바꾸지 말 것.
_DEFAULT_CFG = {
    "voltage": {"in_to_li_offset_v": 0.62, "raw_reference": "vs. In/Li-In", "target_reference": "vs. Li/Li+"},
    "doe": {"formation_cutoffs_v_li": [3.6, 3.8, 4.0, 4.2, 4.4, 4.6], "main_window_v_li": [2.5, 4.4],
            "overlap_tolerance_v": 0.05},
    "colors": {"default": "#7f7f7f"},
    "mass": {"registry_mass_is": "active_material", "active_fraction": None},
    "csv": {"encoding": "utf-8-sig"},
    "paths": {"registry": "data/registry/cells.csv", "raw_dir": "data/raw", "cells_dir": "data/cells"},
}


# ─────────────────────────────────────────────────────────────────────────
# 설정
# ─────────────────────────────────────────────────────────────────────────
def load_config(path: Path | None = None) -> dict:
    """config/cells.yaml → dict. PyYAML 이 없으면 최소 파서(우리 파일 형식만)로 읽는다."""
    p = path or CONFIG_PATH
    text = p.read_text(encoding="utf-8") if p.is_file() else ""
    cfg: dict = {}
    try:
        import yaml  # type: ignore
        cfg = yaml.safe_load(text) or {}
    except ImportError:
        cfg = _mini_yaml(text)
    out = json.loads(json.dumps(_DEFAULT_CFG))
    for k, v in (cfg or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k].update(v)
        else:
            out[k] = v
    return out


def _mini_yaml(text: str) -> dict:
    """PyYAML 없을 때의 2단 YAML 파서 (key: value / 들여쓴 key: value / [a, b] 목록 / 따옴표 문자열)."""
    out: dict = {}
    cur = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip() if not raw.strip().startswith('"') else raw.rstrip()
        if not line.strip():
            continue
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            k, v = m.group(1), m.group(2).strip()
            if v == "":
                out[k] = {}
                cur = k
            else:
                out[k] = _yaml_scalar(v)
                cur = None
            continue
        m = re.match(r'^\s+("?[\w.\-]+"?):\s*(.*)$', line)
        if m and cur is not None:
            k = m.group(1).strip('"')
            out[cur][k] = _yaml_scalar(m.group(2).strip())
    return out


def _yaml_scalar(v: str):
    if v.startswith("[") and v.endswith("]"):
        return [_yaml_scalar(x.strip()) for x in v[1:-1].split(",") if x.strip()]
    if v.startswith('"') and v.endswith('"'):
        return v[1:-1]
    if v.lower() in ("null", "~", ""):
        return None
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            return v


def offset_v(cfg: dict | None = None) -> float:
    cfg = cfg or load_config()
    return float(cfg["voltage"]["in_to_li_offset_v"])


def to_li(v_in: float, cfg: dict | None = None) -> float:
    """vs. In/Li-In → vs. Li/Li+ (더한다). 방향 혼동 금지."""
    return float(v_in) + offset_v(cfg)


def to_in(v_li: float, cfg: dict | None = None) -> float:
    """vs. Li/Li+ → vs. In/Li-In (뺀다)."""
    return float(v_li) - offset_v(cfg)


def color_for_cutoff(cutoff_v_li, cfg: dict | None = None) -> str:
    cfg = cfg or load_config()
    colors = cfg.get("colors") or {}
    if cutoff_v_li is None or cutoff_v_li == "":
        return str(colors.get("default", "#7f7f7f"))
    try:
        key = f"{float(cutoff_v_li):.1f}"
    except (TypeError, ValueError):
        key = str(cutoff_v_li)
    return str(colors.get(key) or colors.get("default", "#7f7f7f"))


# ─────────────────────────────────────────────────────────────────────────
# 파일명 파싱 — 제안값 (정본 아님)
# ─────────────────────────────────────────────────────────────────────────
_ID_RE = re.compile(r"^(D?cell\s?\d+)", re.I)
_V_RE = re.compile(r"(\d(?:\.\d+)?)\s?V(?![a-zA-Z])", re.I)
_MASS_RE = re.compile(r"(\d+(?:\.\d+)?)\s?(mg|g)(?![a-zA-Z])", re.I)


def propose_from_filename(name: str) -> dict:
    """파일명에서 cell_id · 전압 · 질량을 **제안**한다. 무엇을 뜻하는지(전극/활물질, 기준전극)는 모른다고 적는다."""
    stem = Path(name).stem
    out = {"file": Path(name).name, "cell_id": None, "cutoff_v_hint": None, "mass_mg_hint": None,
           "mass_hint_raw": None, "notes": []}
    m = _ID_RE.match(stem)
    if m:
        out["cell_id"] = re.sub(r"\s+", "", m.group(1))
        out["cell_id"] = out["cell_id"][0].upper() + out["cell_id"][1:] if out["cell_id"].lower().startswith("dcell") else out["cell_id"].lower()
    else:
        out["notes"].append("cell ID 를 파일명에서 못 읽었다")
    mv = _V_RE.search(stem)
    if mv:
        out["cutoff_v_hint"] = float(mv.group(1))
        out["notes"].append("전압의 기준전극(vs. Li/Li+ 인지 vs. In/Li-In 인지)은 파일명이 말하지 않는다 — registry 에는 vs. Li/Li+ 로 적는다")
    mm = _MASS_RE.search(stem)
    if mm:
        val, unit = float(mm.group(1)), mm.group(2).lower()
        out["mass_hint_raw"] = f"{mm.group(1)}{unit}"
        out["mass_mg_hint"] = val * 1000.0 if unit == "g" else val
        out["notes"].append("이 질량이 전극 질량인지 활물질 질량인지 파일명은 말하지 않는다 — 확인 후 active_mass_mg 에 적는다")
    if "cont" in stem.lower():
        out["notes"].append("'CONT' 표기 — 대조군(control)으로 추정, 확인 필요")
    return out


# ─────────────────────────────────────────────────────────────────────────
# registry
# ─────────────────────────────────────────────────────────────────────────
REGISTRY_COLUMNS = ["cell_id", "formation_cutoff_v_li", "active_mass_mg", "loading_mah_cm2", "loading_mg_cm2",
                    "punch_diameter_mm", "fab_pressure_mpa", "anode_fab_pressure_mpa", "op_pressure_mpa",
                    "status", "raw_file", "summary_file", "notes"]
STATUS_VOCAB = ["planned", "cycling", "eis", "rest", "harvested", "post-mortem", "done"]


def _num(v):
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    try:
        f = float(s)
        return None if math.isnan(f) else f
    except ValueError:
        return None


def load_registry(path: Path | None = None, cfg: dict | None = None) -> list[dict]:
    cfg = cfg or load_config()
    p = path or (ROOT / cfg["paths"]["registry"])
    if not p.is_file():
        return []
    rows = []
    with p.open(encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            cid = (r.get("cell_id") or "").strip()
            if not cid:
                continue
            row = {k: (r.get(k) or "").strip() for k in REGISTRY_COLUMNS}
            row["cell_id"] = cid
            row["formation_cutoff_v_li_num"] = _num(row["formation_cutoff_v_li"])
            row["active_mass_mg_num"] = _num(row["active_mass_mg"])
            row["color"] = color_for_cutoff(row["formation_cutoff_v_li_num"], cfg)
            row["status_ok"] = (row["status"] in STATUS_VOCAB) if row["status"] else True
            rows.append(row)
    return rows


# ─────────────────────────────────────────────────────────────────────────
# raw CSV → 사이클 요약 (pandas)
# ─────────────────────────────────────────────────────────────────────────
RAW_REQUIRED = ["cycle_index", "voltage", "current", "charge_q", "discharge_q"]
SUMMARY_COLUMNS = ["cycle", "charge_capacity_mah_g", "discharge_capacity_mah_g", "charge_capacity_mah",
                   "discharge_capacity_mah", "coulombic_efficiency", "charge_energy_wh", "discharge_energy_wh",
                   "energy_efficiency", "mean_charge_voltage", "mean_discharge_voltage", "voltage_hysteresis",
                   "v_max", "v_min", "duration_s", "points", "complete"]


def _norm_col(c: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower()).strip("_")


def read_raw_csv(path: Path, cfg: dict | None = None):
    """raw 충방전 CSV → pandas DataFrame (열 이름 정규화, utf-8-sig)."""
    import pandas as pd
    cfg = cfg or load_config()
    enc = (cfg.get("csv") or {}).get("encoding", "utf-8-sig")
    df = pd.read_csv(path, encoding=enc)
    df.columns = [_norm_col(c) for c in df.columns]
    missing = [c for c in RAW_REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"raw CSV 에 필요한 열이 없다: {missing} (있는 열: {list(df.columns)[:12]}…)")
    for c in ("cycle_index", "voltage", "current", "charge_q", "discharge_q", "charge_e", "discharge_e",
              "test_time_s", "step_time_s", "cycle_time_s", "temperature"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def cycle_summary(df, active_mass_mg: float | None, cfg: dict | None = None):
    """raw DataFrame → 사이클별 요약 DataFrame (SUMMARY_COLUMNS).

    전압 열은 **원본(vs. In/Li-In)** 이다 — 변환값은 `summary_dict` 에서 offset 과 함께 따로 준다.
    용량: charge_q/discharge_q 는 Ah 누적값 → 사이클 내 최대값을 그 사이클의 용량으로 본다 (장비가
    사이클마다 0 부터 다시 센다는 전제; 누적형이면 사이클 시작값을 뺀다 — 둘 다 처리).
    """
    import pandas as pd
    cfg = cfg or load_config()
    rows = []
    for cyc, g in df.groupby("cycle_index", sort=True):
        g = g.sort_values("test_time_s") if "test_time_s" in g.columns else g
        q_c = _span_ah(g["charge_q"])
        q_d = _span_ah(g["discharge_q"])
        e_c = _span_ah(g["charge_e"]) if "charge_e" in g.columns else None
        e_d = _span_ah(g["discharge_e"]) if "discharge_e" in g.columns else None
        chg = g[g["current"] > 0]
        dch = g[g["current"] < 0]
        mean_vc = _mean_v(chg)
        mean_vd = _mean_v(dch)
        cap_c_mah = q_c * 1000.0 if q_c is not None else None
        cap_d_mah = q_d * 1000.0 if q_d is not None else None
        mass_g = (active_mass_mg / 1000.0) if active_mass_mg else None
        rows.append({
            "cycle": int(cyc),
            "charge_capacity_mah_g": (cap_c_mah / mass_g) if (mass_g and cap_c_mah is not None) else None,
            "discharge_capacity_mah_g": (cap_d_mah / mass_g) if (mass_g and cap_d_mah is not None) else None,
            "charge_capacity_mah": cap_c_mah,
            "discharge_capacity_mah": cap_d_mah,
            "coulombic_efficiency": (cap_d_mah / cap_c_mah * 100.0) if (cap_c_mah and cap_d_mah is not None) else None,
            "charge_energy_wh": e_c,
            "discharge_energy_wh": e_d,
            "energy_efficiency": (e_d / e_c * 100.0) if (e_c and e_d is not None) else None,
            "mean_charge_voltage": mean_vc,
            "mean_discharge_voltage": mean_vd,
            "voltage_hysteresis": (mean_vc - mean_vd) if (mean_vc is not None and mean_vd is not None) else None,
            "v_max": float(g["voltage"].max()) if len(g) else None,
            "v_min": float(g["voltage"].min()) if len(g) else None,
            "duration_s": _duration(g),
            "points": int(len(g)),
            "complete": bool(len(chg) > 0 and len(dch) > 0),
        })
    return pd.DataFrame(rows, columns=SUMMARY_COLUMNS)


def _span_ah(s):
    s = s.dropna()
    if s.empty:
        return None
    return float(s.max() - min(0.0, float(s.min())))


def _mean_v(g):
    """전하량 가중 평균 전압 (dQ 가중). 전하량 열이 없으면 단순 평균."""
    if g.empty:
        return None
    v = g["voltage"].astype(float)
    return float(v.mean())


def _duration(g):
    for c in ("test_time_s", "cycle_time_s"):
        if c in g.columns and g[c].notna().any():
            return float(g[c].max() - g[c].min())
    return None


def read_summary_csv(path: Path, cfg: dict | None = None):
    """장비가 만든 사이클 요약 CSV 를 우리 열 이름으로 정규화해 읽는다 (없는 열은 비운다)."""
    import pandas as pd
    cfg = cfg or load_config()
    enc = (cfg.get("csv") or {}).get("encoding", "utf-8-sig")
    df = pd.read_csv(path, encoding=enc)
    df.columns = [_norm_col(c) for c in df.columns]
    alias = {
        "cycle_index": "cycle", "charge_capacity_mah_g": "charge_capacity_mah_g",
        "charge_capacity_mahg": "charge_capacity_mah_g", "discharge_capacity_mahg": "discharge_capacity_mah_g",
        "charge_capacity": "charge_capacity_mah", "discharge_capacity": "discharge_capacity_mah",
        "charge_energy": "charge_energy_wh", "discharge_energy": "discharge_energy_wh",
        "duration": "duration_s", "ce": "coulombic_efficiency",
    }
    df = df.rename(columns={k: v for k, v in alias.items() if k in df.columns})
    for c in SUMMARY_COLUMNS:
        if c not in df.columns:
            df[c] = None
    return df[SUMMARY_COLUMNS]


# ─────────────────────────────────────────────────────────────────────────
# summary.json — 화면과 LLM 이 읽는 요약 (raw 는 여기 없다)
# ─────────────────────────────────────────────────────────────────────────
def summary_dict(cell: dict, cycles_df, cfg: dict | None = None, source: str = "") -> dict:
    cfg = cfg or load_config()
    off = offset_v(cfg)
    d = cycles_df
    n = int(len(d))
    dis = d["discharge_capacity_mah_g"].dropna() if "discharge_capacity_mah_g" in d else []
    first = float(dis.iloc[0]) if len(dis) else None
    last = float(dis.iloc[-1]) if len(dis) else None
    ce = d["coulombic_efficiency"].dropna() if "coulombic_efficiency" in d else []
    hyst = d["voltage_hysteresis"].dropna() if "voltage_hysteresis" in d else []
    vmax = float(d["v_max"].max()) if n and d["v_max"].notna().any() else None
    vmin = float(d["v_min"].min()) if n and d["v_min"].notna().any() else None
    ret = (last / first * 100.0) if (first and last is not None) else None
    return {
        "cell_id": cell["cell_id"],
        "formation_cutoff_v_li": cell.get("formation_cutoff_v_li_num"),
        "active_mass_mg": cell.get("active_mass_mg_num"),
        "status": cell.get("status") or "",
        "source": source,
        "n_cycles": n,
        "capacity_unit": "mAh g^-1 (active material)" if cell.get("active_mass_mg_num") else "mAh (질량 미등록 — 비용량 미계산)",
        "first_discharge_mah_g": first,
        "last_discharge_mah_g": last,
        "retention_pct_last_over_first": ret,
        "retention_definition": "마지막 사이클 방전 비용량 / 첫 사이클 방전 비용량 × 100 (formation 포함 여부는 raw 의 cycle_index 정의에 따른다)",
        "ce_mean_pct": float(ce.mean()) if len(ce) else None,
        "ce_last_pct": float(ce.iloc[-1]) if len(ce) else None,
        "hysteresis_first_v": float(hyst.iloc[0]) if len(hyst) else None,
        "hysteresis_last_v": float(hyst.iloc[-1]) if len(hyst) else None,
        "voltage": {
            "raw_reference": cfg["voltage"]["raw_reference"],
            "v_max_raw": vmax, "v_min_raw": vmin,
            "target_reference": cfg["voltage"]["target_reference"],
            "offset_applied_v": off,
            "v_max_vs_li": (vmax + off) if vmax is not None else None,
            "v_min_vs_li": (vmin + off) if vmin is not None else None,
        },
        "cycles_head": d.head(3).where(d.head(3).notna(), None).to_dict(orient="records") if n else [],
    }


def llm_summary(summaries: list[dict], registry: list[dict], cfg: dict | None = None) -> str:
    """/chat 에 넘길 텍스트 — 요약 통계만. 한 셀당 두 줄."""
    cfg = cfg or load_config()
    lines = [f"[우리 셀 요약 — 정본은 data/registry/cells.csv 와 data/cells/*/summary.json; 전압 offset +{offset_v(cfg)} V (vs. In/Li-In → vs. Li/Li+); 용량 mAh g^-1]"]
    by_id = {s["cell_id"]: s for s in summaries}
    if not registry and not summaries:
        lines.append("(등록된 셀 없음)")
    for r in registry:
        s = by_id.get(r["cell_id"])
        head = f"- {r['cell_id']}: formation cut-off {r['formation_cutoff_v_li'] or '?'} V vs. Li/Li+ · status {r['status'] or '?'} · active mass {r['active_mass_mg'] or '?'} mg"
        lines.append(head)
        if s:
            lines.append(f"    cycles {s['n_cycles']} · first discharge {_f(s['first_discharge_mah_g'])} · last {_f(s['last_discharge_mah_g'])} mAh g^-1 · retention(last/first) {_f(s['retention_pct_last_over_first'])} % · CE mean {_f(s['ce_mean_pct'])} % · hysteresis {_f(s['hysteresis_first_v'])}→{_f(s['hysteresis_last_v'])} V · v_max {_f(s['voltage']['v_max_raw'])} V vs. In/Li-In (= {_f(s['voltage']['v_max_vs_li'])} V vs. Li/Li+)")
    for s in summaries:
        if s["cell_id"] not in {r["cell_id"] for r in registry}:
            lines.append(f"- {s['cell_id']}: (registry 에 없음 — import 산출물만 있음) cycles {s['n_cycles']}")
    return "\n".join(lines)


def _f(v, nd=1):
    if v is None:
        return "?"
    try:
        return f"{float(v):.{nd}f}"
    except (TypeError, ValueError):
        return str(v)


def load_summaries(cfg: dict | None = None) -> list[dict]:
    cfg = cfg or load_config()
    d = ROOT / cfg["paths"]["cells_dir"]
    out = []
    if not d.is_dir():
        return out
    for j in sorted(d.glob("*/summary.json")):
        try:
            out.append(json.loads(j.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
    return out


def load_cycles(cell_id: str, cfg: dict | None = None) -> list[dict]:
    """data/cells/<id>/cycles.csv → 행 목록 (pandas 없이 읽는다 — webapp 이 가볍게 쓰도록)."""
    cfg = cfg or load_config()
    p = ROOT / cfg["paths"]["cells_dir"] / cell_id / "cycles.csv"
    if not p.is_file():
        return []
    with p.open(encoding="utf-8", newline="") as fh:
        rows = []
        for r in csv.DictReader(fh):
            rows.append({k: (_num(v) if k != "complete" else (str(v).lower() == "true")) for k, v in r.items()})
        return rows
