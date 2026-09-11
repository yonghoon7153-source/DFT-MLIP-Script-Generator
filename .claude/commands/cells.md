---
description: 셀 데이터 — raw CSV 파일명에서 제안값을 읽고(registry 에는 사람이 적는다), registry 기준으로 사이클 요약을 import 하고, 요약 통계만으로 해석한다
---

셀 데이터를 다룬다. 대상: $ARGUMENTS (예: "data/raw/Dcell14_….csv 제안", "Dcell14 import", "cut-off 별 retention 요약")

규칙 (절대 규칙 + [4] 셀 데이터 모듈):
- **registry(`data/registry/cells.csv`) 가 정본.** 파일명 파싱은 제안값일 뿐이다 — 질량이 전극인지 활물질인지, 전압의 기준전극이
  무엇인지 파일명은 말하지 않는다. registry 에 적는 것은 **사용자**다 (에이전트는 제안만 하고, 사용자가 확정값을 말해 주면
  그때 registry 행을 쓴다).
- 전압: raw 는 vs. In/Li-In, 변환은 `config/cells.yaml` 의 offset(+0.62 V) 하나. 용량: mAh g⁻¹ (활물질 질량). 절대용량 보고 금지.
- LLM 컨텍스트에 raw CSV 를 통째로 넣지 않는다 — `summary.json`/`cycles.csv` 의 요약만 본다. 해석은 요약 통계 위에서.

절차:
1. **제안**: `python3 tools/cells/import_cell.py --propose <csv>` → cell_id·cut-off·질량 제안과 경고를 보이고, registry 에 적을
   확정값(cut-off vs. Li/Li⁺, active_mass_mg, loading, 펀칭 지름, 제작압/음극압/구동압, status, raw_file, notes)을 **한 번에** 묻는다.
2. **등록**: 사용자가 확정하면 `data/registry/cells.csv` 에 행을 append 한다 (`data/registry/README.md` 열 정의).
3. **import**: `python3 tools/cells/import_cell.py --cell <cell_id>` → `data/cells/<cell_id>/cycles.csv` + `summary.json`.
   질량이 없으면 mAh g⁻¹ 이 비어 있다고 알린다.
4. **해석**: `summary.json` 들만 읽어 cut-off 별 n·첫/마지막 방전 비용량·retention·CE·hysteresis 추세를 표로. 같은 cut-off 의
   n 이 1 이면 "재현 없음" 을 명시. 논문과 비교하면 기준전극·조성·온도·압력·loading 차이를 먼저 짚는다.
5. **기록**: 의미 있는 결과는 `wiki/entities/nca721-formation-project.md` 상태 절(날짜 + 요약, 수치는 사본이라고 표시)과
   관련 질문 카드 Status Log 에. `python3 wiki/tools/lint.py` 0 errors. 커밋 prefix `cells:` (데이터) / `update(wiki):` (위키).
6. 검증: `.venv/bin/python -m unittest tests/test_cells.py` 통과 · webapp `/cells` 에서 보이는지 (`python3 webapp/smoke.py`).
