---
description: 위키 카운트, 논문/DOI 커버리지, 검증 커버리지, 열린 질문, 최근 log 스냅샷
---

> 이 위키는 repo root `wiki/` 하위다 (킷 원본과 배치가 다름 — `wiki/README.md` 참조). 아래 절차의 모든 경로는 repo root 기준이다. 절대 규칙(루트 `CLAUDE.md` 맨 아래)을 지킨다.

이 LLM Wiki 의 현재 상태를 보고한다.

1. `python3 wiki/tools/status.py` 를 실행한다.
2. 출력을 요약해 보고한다: 페이지 수(유형별), 논문 노트/digest/DOI 커버리지, confidence/verificationStatus/explored 분포, 미검증 배경
   페이지 수, 열린 질문, verify 대기 큐, 최근 log. 셀 데이터는 `data/registry/cells.csv` 행 수와 `data/cells/*/summary.json` 수.
3. 마지막에 **다음 행동 1가지**를 추천한다 — 예: "투입 예정 논문 중 X 를 /paper 로", "unverified 페이지 Y 를 /wiki-verify",
   "registry 가 비어 있다 — 셀 N개 등록", "N일째 ingest 없음".
