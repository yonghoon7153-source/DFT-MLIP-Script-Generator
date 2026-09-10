"""데이터 로더 — BMS 쪽 원자료는 **저장소에 넣지 않는다.**

원자료(반쪽전지·풀셀 xlsx, 문헌 OCP)는 규진팀 것이고 공개 저장소에 올릴지는
우리가 정할 일이 아니다. 그래서 이 하네스는 경로를 밖에서 받는다:

    export BMS_DATA_ROOT=/…/electrode_balancing_blend
    python -m bms_balancing.verify …

`--data-root` 인자가 있으면 그것이 이긴다. 산출은 요약 표(CSV/MD)만 남긴다.
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

STATES = ["pristine", "100", "200", "300_0009", "300_0147"]

#: 풀셀 워크북(`현차_풀셀_정리.xlsx`)의 상태별 컬럼쌍 (0-based, main_blend_final.m 의 1-based 와 대응)
FULL_COL = {"pristine": 0, "100": 1, "200": 2, "300_0009": 3, "300_0147": 4}

#: 반쪽전지 파일 이름 — 소스마다 다르다
HALF_FILE = {
    "GITT": {s: f"{s}.xlsx" for s in STATES},
    "step_005C": {s: f"{s}_005C.xlsx" for s in STATES},
}

SI_SOURCES = ["Baggetto", "Friedrich", "Jiang", "Kunz", "Li", "Lu",
              "Sethuraman", "Wetjen"]


def data_root(explicit: str | None = None) -> Path:
    root = explicit or os.environ.get("BMS_DATA_ROOT")
    if not root:
        raise SystemExit(
            "BMS 원자료 경로를 모른다. --data-root 또는 BMS_DATA_ROOT 로 "
            "electrode_balancing_blend 디렉터리를 가리켜라.")
    p = Path(root)
    if not (p / "data" / "literature").is_dir():
        raise SystemExit(f"{p} 아래에 data/literature 가 없다 — 경로가 맞나?")
    return p


def half_cell_path(root: Path, source: str, state: str) -> Path:
    return root / "data" / "half_cell" / source / HALF_FILE[source][state]


def full_cell_workbook(root: Path) -> Path:
    d = root / "data" / "full_cell" / "large_cell_033C"
    cands = [p for p in d.glob("*.xlsx")
             if "pristine" not in p.name and "300cycle" not in p.name]
    if not cands:
        raise SystemExit(f"{d} 에서 상태별 풀셀 워크북을 못 찾았다")
    return cands[0]


def load_full_cell(root: Path, state: str):
    """2행 헤더(1행=상태명, 2행=단위) 워크북에서 그 상태의 (capacity, voltage)."""
    df = pd.read_excel(full_cell_workbook(root), header=None, skiprows=2)
    col = FULL_COL[state]
    c = pd.to_numeric(df[2 * col], errors="coerce")
    v = pd.to_numeric(df[2 * col + 1], errors="coerce")
    ok = c.notna() & v.notna()
    return c[ok].to_numpy(float), v[ok].to_numpy(float)


def load_literature(root: Path, si_source: str = "Li"):
    """Gr 은 항상 Si_Gr_literature_OCP.xlsx, Si 만 선택 소스로 교체."""
    lit = root / "data" / "literature"
    gr = pd.read_excel(lit / "Si_Gr_literature_OCP.xlsx")
    gr_c = gr["Gr_capacity"].dropna().to_numpy(float)
    gr_v = gr["Gr_voltage"].dropna().to_numpy(float)
    si = pd.read_csv(lit / "Si_OCP_sources" / f"{si_source}.csv")
    return (si["normalizedCapacity"].to_numpy(float),
            si["voltage"].to_numpy(float), gr_c, gr_v)
