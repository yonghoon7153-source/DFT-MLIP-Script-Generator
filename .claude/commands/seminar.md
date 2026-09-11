---
description: digest 하나를 논문 세미나 발표 자료로 — 한 줄 메시지·스토리라인·슬라이드별 그림·양단위 숫자표·비판·예상 질문 (wiki/queries/<slug>-seminar-prep.md)
---

논문 세미나 준비 페이지를 만든다. 대상 digest slug: $ARGUMENTS (예: `kim2023_reinforced-electrical-networking-high-loading-li2s-cathode`; `--pptx` 가 붙으면 pptx 초안도).

절차는 `wiki/guides/seminar-prep-from-digest.md` 를 따른다:

1. digest 가 없으면 먼저 `/paper`. 있으면 digest 의 **공백표**와 **그림 판독 기록**을 읽는다 — 안 본 그림을 쓰려면 먼저 Read.
2. `wiki/queries/<slug-short>-seminar-prep.md` (type: query) 에 쓴다 — 선례 `wiki/queries/kim2023-seminar-prep.md` 의 절 구조 그대로:
   0 한 줄 메시지 · 1 청중·시간 · 2 스토리라인 5막 · 3 슬라이드 표(제목 / 그림 파일·패널 / 말할 것 3 / 노트 / 분, ★ 표시로 15분 판) · 4 핵심 숫자표(**(S)·(Li2S) 양단위**, 로딩 병기) · 5 비판 3+3 · 6 우리 연구 연결 표 · 7 예상 질문 10 + 답(근거 위치) · 8 발표 체크리스트 · Status.
3. 모든 수치는 digest 를 거친다 (PDF 에서 바로 옮기지 않는다). `[도표]` 값은 그대로 `[도표]`.
4. `wiki/index.md` Queries 절 등록 + `wiki/log.md` `## [날짜] query | …` + `python3 wiki/tools/lint.py` 0 errors.
5. `--pptx`: pptx 스킬로 슬라이드 표를 초안 덱으로 만들되 텍스트는 이 페이지에서만 가져오고 그림은 `wiki/raw/figures/<slug>/` 의 PNG 를 넣는다. 사용자에게 파일로 전달.
6. 사용자에게: 한 줄 메시지, 가장 위험한 실수 3개(단위·오기·"안정" 의 뜻), 발표 후 이 페이지의 Status 에 실제 질문을 append 하라고 안내.
