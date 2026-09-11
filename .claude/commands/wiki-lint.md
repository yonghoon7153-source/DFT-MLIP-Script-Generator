---
description: 위키 건강 점검 (read-only) — 오류 보고와 수정 제안까지만
---

> 이 위키는 repo root `wiki/` 하위다 (킷 원본과 배치가 다름 — `wiki/README.md` 참조). 아래 절차의 모든 경로는 repo root 기준이다. 절대 규칙(루트 `CLAUDE.md` 맨 아래)을 지킨다.

이 LLM Wiki 의 건강을 점검한다.

1. `python3 wiki/tools/lint.py` 를 실행한다. (webapp 도 같이 보려면 `python3 webapp/smoke.py`, 셀 모듈은 `.venv/bin/python -m unittest discover -s tests`.)
2. 결과를 해석해 보고한다:
   - **ERRORS**: 깨진 링크, index 누락/불일치, frontmatter 누락, raw hash 불일치, 하드코딩된 브랜치 이름, 모델 식별자, parity 위반,
     **절대 규칙 위반**(`no-ncm721` · `canonical-offset` · `doi-unique` · `paper-note-voltage`) — 각각 원인과 수정 방법을 제시한다.
   - **WARNINGS**: orphan, stale(90일), 링크 2개 미만, single-source+high, **기준전극 없는 전압**, **절대용량 표기** — 조치가 필요한지 판단 근거와 함께.
   - **NOTES**: confidence:high 인데 Bias Check/불확실성 섹션이 없는 페이지.
3. 추가로 `explored: false` 와 `verificationStatus: unverified` backlog, 미검증 배경(`synthesis-only`) 페이지 수를 요약하고, 다음 검증 대상을
   1~2개 추천한다 (열린 research-question 에 물린 페이지 우선).

**Read-only 원칙**: 이 command 는 보고와 제안까지만 한다. 실제 수정은 사용자가 승인한 뒤에만 수행하고, 수정했다면 `wiki/log.md` 에
`## [YYYY-MM-DD] lint | {수정 요약}` 을 기록한다.
