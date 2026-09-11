# data/raw — 원 데이터 (git 에 넣지 않는다)

여기에 장비가 낸 raw 충방전 CSV(utf-8-sig)와 사이클 요약 CSV 를 둔다. `.gitignore` 로 이 README 만 추적된다.
정본은 이 파일들과 실험 노트다. 파일명은 registry(`data/registry/cells.csv`) 의 `raw_file`/`summary_file` 열에 적는다.

```bash
python3 tools/cells/import_cell.py --propose data/raw/<file>.csv    # 파일명 → 제안값 (registry 에는 사람이 적는다)
python3 tools/cells/import_cell.py --cell <cell_id>                 # registry 기준 → data/cells/<cell_id>/
```
