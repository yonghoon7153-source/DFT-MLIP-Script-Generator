#!/usr/bin/env python3
"""import_cell.py — raw 충방전 CSV → 사이클 요약 (prototype: 스키마 + import 까지).

  python3 tools/cells/import_cell.py --propose data/raw/<file>.csv     # 파일명에서 제안값만 (registry 에 쓰지 않는다)
  python3 tools/cells/import_cell.py --cell Dcell14                     # registry 기준 import → data/cells/Dcell14/
  python3 tools/cells/import_cell.py --all                              # registry 의 raw_file/summary_file 이 있는 셀 전부
  python3 tools/cells/import_cell.py --cell Dcell14 --raw data/raw/x.csv   # registry 의 raw_file 대신 지정 (registry 는 안 고친다)

규칙: registry(data/registry/cells.csv) 가 정본. 질량이 registry 에 없으면 mAh g⁻¹ 을 계산하지 않는다.
전압은 원본(vs. In/Li-In)을 보존하고 summary.json 에 변환값(+offset, config 정본)을 함께 쓴다.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.cells import cellio as C  # noqa: E402


def do_propose(path: str) -> int:
    p = C.propose_from_filename(path)
    print(f"파일: {p['file']}")
    print(f"  cell_id 제안      : {p['cell_id'] or '(못 읽음)'}")
    print(f"  cut-off 제안      : {p['cutoff_v_hint'] if p['cutoff_v_hint'] is not None else '(없음)'}  ← 기준전극 미상 (registry 에는 vs. Li/Li+ 로)")
    print(f"  질량 제안         : {p['mass_hint_raw'] or '(없음)'} → {C._f(p['mass_mg_hint'])} mg  ← 전극/활물질 미상")
    for n in p["notes"]:
        print(f"  ⚠ {n}")
    print("이 값은 제안이다. data/registry/cells.csv 에 사람이 확정값을 적는다.")
    return 0


def do_import(cell_id: str, raw_override: str | None, cfg: dict) -> int:
    reg = {r["cell_id"]: r for r in C.load_registry(cfg=cfg)}
    cell = reg.get(cell_id)
    if not cell:
        print(f"✗ registry 에 {cell_id} 가 없다 — data/registry/cells.csv 에 먼저 등록한다 (--propose 로 제안값 확인)", file=sys.stderr)
        return 2
    raw_dir = C.ROOT / cfg["paths"]["raw_dir"]
    out_dir = C.ROOT / cfg["paths"]["cells_dir"] / cell_id
    src = None
    if raw_override:
        src = Path(raw_override)
    elif cell.get("raw_file"):
        src = raw_dir / cell["raw_file"]
    if src is not None and src.is_file():
        df = C.read_raw_csv(src, cfg)
        cyc = C.cycle_summary(df, cell.get("active_mass_mg_num"), cfg)
        source = f"raw:{src.name}"
    elif cell.get("summary_file") and (raw_dir / cell["summary_file"]).is_file():
        cyc = C.read_summary_csv(raw_dir / cell["summary_file"], cfg)
        source = f"summary:{cell['summary_file']}"
    else:
        print(f"✗ {cell_id}: raw_file/summary_file 이 data/raw/ 에 없다 (registry: raw_file={cell.get('raw_file')!r})", file=sys.stderr)
        return 3
    out_dir.mkdir(parents=True, exist_ok=True)
    cyc.to_csv(out_dir / "cycles.csv", index=False, encoding="utf-8")
    summ = C.summary_dict(cell, cyc, cfg, source=source)
    (out_dir / "summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1), encoding="utf-8")
    if not cell.get("active_mass_mg_num"):
        print(f"⚠ {cell_id}: registry 에 active_mass_mg 가 없어 mAh g⁻¹ 을 계산하지 않았다 (절대용량만 중간값으로 저장)")
    print(f"· {cell_id}: {summ['n_cycles']} cycles ← {source} → {out_dir.relative_to(C.ROOT)}/cycles.csv, summary.json")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--propose", metavar="FILE", help="파일명에서 제안값만 출력")
    ap.add_argument("--cell", metavar="CELL_ID", help="registry 의 셀 하나를 import")
    ap.add_argument("--raw", metavar="FILE", help="--cell 과 함께: registry 의 raw_file 대신 이 파일")
    ap.add_argument("--all", action="store_true", help="registry 의 파일이 있는 셀 전부")
    a = ap.parse_args(argv)
    cfg = C.load_config()
    if a.propose:
        return do_propose(a.propose)
    if a.cell:
        return do_import(a.cell, a.raw, cfg)
    if a.all:
        rc = 0
        for r in C.load_registry(cfg=cfg):
            if r.get("raw_file") or r.get("summary_file"):
                rc |= do_import(r["cell_id"], None, cfg)
        return rc
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
