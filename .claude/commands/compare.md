---
description: 논문 비교 — digest 들의 compare: 블록을 한 축으로 대조하고, 재사용 가치가 있으면 comparisons/ 에 file-back
---

논문들을 비교한다. 대상/축: $ARGUMENTS (예: "kim2023 vs 다음 논문, 첫 충전 활성화 조건" — 비우면 `compare:` 를 가진 digest 전부를 전 축으로).

절차:

1. `wiki/raw/papers/*.md` 의 frontmatter `compare:` 를 읽는다 (webapp `/compare` 가 보는 것과 같은 정본). 우리 자신은 `wiki/entities/li2s-assb-reference-cell.md` 의 `compare:`.
2. 요청한 축으로 표를 만든다. **빈 칸은 빈 칸**으로 둔다 — 논문이 안 준 값을 추정해 채우지 않는다. 비용량은 (S)/(Li2S) 둘 다, 면적용량은 로딩과 함께.
3. 표 아래에 판단을 적는다: 무엇이 같은 조건이고 무엇이 다른 조건인지(액체 vs ASSB, 로딩, 온도, 전압창), 그래서 **직접 비교 가능한 셀 짝**은 어디까지인지. `[도표]` 값이 섞였으면 표시한다.
4. 열린 질문 카드에 근거가 되면 Evidence For/Against 에 append (가설 번호·날짜).
5. **File-back 판단**: 비교가 한 번 쓰고 버리기 아까우면 `python3 wiki/tools/new-page.py comparison <slug>` 로 `wiki/comparisons/` 에 저장 (frontmatter `type: comparison`, `sources` 에 digest 들, `evidenceScope: multi-source-primary`), `wiki/index.md` 등록, `wiki/log.md` `## [날짜] query | 비교: …`, `python3 wiki/tools/lint.py` 0 errors.
6. 새 축이 반복해서 필요하면 `wiki/SCHEMA.md` 의 `compare:` 키 목록과 `webapp/content.py` 의 `COMPARE_COLUMNS` 를 함께 늘린다 (둘이 같아야 한다).
