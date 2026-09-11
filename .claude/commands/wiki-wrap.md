---
description: 세션 마무리 — lint·smoke·tests, log 정리, git commit + push 원터치
---

> 이 위키는 repo root `wiki/` 하위다 (킷 원본과 배치가 다름 — `wiki/README.md` 참조). 아래 절차의 모든 경로는 repo root 기준이다. 절대 규칙(루트 `CLAUDE.md` 맨 아래)을 지킨다.

이 세션의 위키·webapp·데이터 작업을 마무리한다.

절차:

1. **검증**: `python3 wiki/tools/lint.py` (0 errors) · webapp 을 고쳤으면 `python3 webapp/smoke.py` (0 failures) · 셀 모듈을 고쳤으면
   `.venv/bin/python -m unittest discover -s tests`. ERRORS 가 있으면 사용자 승인 하에 고치고 재실행 — 통과할 때까지 커밋하지 않는다.
2. **Log 확인**: `git status` 로 이번 세션의 변경 파일을 보고, `wiki/log.md` 에 대응하는 항목이 있는지 확인한다. 빠진 작업이 있으면
   `## [YYYY-MM-DD] action | subject` 형식으로 append 한다.
3. **Index 확인**: 새 페이지가 있었다면 `wiki/index.md` 등록과 Total pages 카운트를 확인한다 (lint 가 잡아준다).
4. **Commit**: 변경을 스테이지하고 커밋한다. 메시지는 세션의 지배적 작업에 맞는 prefix (`ingest(wiki):` `update(wiki):` `create(wiki):`
   `lint(wiki):` `verify(wiki):` `webapp:` `cells:`) + 한 줄 요약 + 필요하면 본문 bullet. 논리적으로 다른 작업이 섞여 있으면 나눠 커밋한다.
   커밋 메시지에 모델 식별자를 넣지 않는다 (하네스가 붙이는 트레일러는 예외).
5. **Push**: 루트 `CLAUDE.md` 하드룰 1의 브랜치로 push 한다 (`git push -u origin <branch>`, 네트워크 실패만 2s/4s/8s/16s 재시도).
6. **스냅샷**: `python3 wiki/tools/status.py` 를 실행해 현재 상태와 다음 추천 행동 1가지로 마무리 보고한다.
