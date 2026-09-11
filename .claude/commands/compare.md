---
description: 논문 비교 — papers/ 노트의 paper: 블록을 한 축(formation cut-off / 상한 전압 vs 열화 거동)으로 대조하고 내 DOE 와의 겹침을 표시, 재사용 가치가 있으면 comparisons/ 에 file-back
---

논문들을 비교한다. 대상/축: $ARGUMENTS (예: "상한 전압 4.3 V 이상 논문의 CEI 산물" — 비우면 `paper:` 를 가진 노트 전부를 기본 축으로).

절차:

1. `wiki/papers/*.md` 의 frontmatter `paper:` 를 읽는다 (webapp `/compare` 가 보는 것과 같은 정본). 우리 자신은
   `wiki/entities/nca721-formation-project.md` 의 `ours:`. 내 DOE 창은 `config/cells.yaml` `doe` (main 2.5–4.4 V ·
   formation 3.6–4.6 V vs. Li/Li⁺).
2. 표를 만든다 — 행 = 논문(+우리), 열 = 요청한 축. **빈 칸은 빈 칸**으로 둔다 (물음표 금지). 전압은 원문 값+기준과
   vs. Li/Li⁺ 변환값(offset)을 나란히. 양극 조성은 원문 표기 그대로.
3. 표 아래에 판단을 적는다: 어느 논문이 **내 DOE 창 안/위/아래**인지, 그 밖에 무엇이 같은 조건이고 무엇이 다른지
   (기준전극·양극 조성·온도·압력(제작/구동)·loading·전해질·음극), 그래서 **직접 비교 가능한 짝**은 어디까지인지.
   `[도표]` 값이 섞였으면 표시한다.
4. 열린 질문 카드에 근거가 되면 Evidence For/Against 에 append (가설 번호·날짜). 메커니즘 페이지의 근거 상태도.
5. **File-back 판단**: 한 번 쓰고 버리기 아까우면 `python3 wiki/tools/new-page.py comparison <slug>` 로 `wiki/comparisons/` 에
   저장 (`sources` 에 digest 들, `evidenceScope: multi-source-primary`), `wiki/index.md` 등록, `wiki/log.md`
   `## [날짜] query | 비교: …`, `python3 wiki/tools/lint.py` 0 errors.
6. 새 축이 반복해서 필요하면 `wiki/SCHEMA.md` 의 `paper:` 스키마와 `webapp/content.py` 의 `COMPARE_COLUMNS`/`flatten_paper`
   를 함께 늘린다 (둘이 같아야 한다).
