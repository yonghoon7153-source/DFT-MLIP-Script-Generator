---
title: New Project Kickoff
description: "새 실험 프로젝트(satellite)를 이 mothership 에 등록하는 킥오프 프롬프트 — repo-root 상대 경로 적응판"
created: 2026-07-30
updated: 2026-09-11
type: guide
tags: [satellite, wiki]
sources: [raw/transcripts/kit-provenance-260730.md, raw/transcripts/2026-09-11-li2s-wiki-kickoff-session.md]
confidence: high
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: multi-source-mixed
---

# New Project Kickoff

## 용도
새 실험 프로젝트(예: anode-free 착수, 새 혼합 경로 시리즈)를 시작할 때 Claude 세션에 붙여넣는
킥오프 프롬프트. 이 위키는 repo root `wiki/` 에 있으므로 킷 원본의 `<MOTHERSHIP>` 절대 경로
치환이 필요 없다 — **repo-root 상대 경로**를 쓴다.

## 킥오프 프롬프트 (복사해서 [ ] 채우고 붙여넣기)

```
새 프로젝트 시작. 아래대로 세팅해줘.

[프로젝트 정보]
- 이름/슬러그: [예: anode-free-li2s-assb]
- 위치: [예: 이 저장소 experiments/<슬러그>/ 또는 외부 실험 노트 경로]
- 목표 (1~3줄): [ ]
- 선행 프로젝트: [예: li2s-assb-reference-cell]

[세팅 순서]
1. wiki/SCHEMA.md 먼저 읽기 (특히 "이 저장소 특칙" — 단위 규율)
2. python3 wiki/tools/new-page.py entity <슬러그> → 개요·핵심 사실·상태·
   "이 프로젝트가 답해야 할 질문"·미결 채우기, [[wikilink]] 2개 이상
3. 열린 질문이 있으면 python3 wiki/tools/new-page.py research-question <슬러그>
4. wiki/index.md 등록 + wiki/log.md append + python3 wiki/tools/lint.py 0 errors
5. 이 킥오프 대화의 설계 결정은 wiki/raw/transcripts/<슬러그>-kickoff-YYMMDD.md 로
   봉인 (sha256)
6. 커밋 prefix create(wiki): — push 브랜치는 루트 CLAUDE.md 하드룰 1
```

## 규칙 요약
- 실험 수치는 위키에 **사본**으로만 (정본은 실험 노트·원 데이터). 상태 절에 날짜와 함께 append.
- 상태가 바뀌면 entity 의 `updated` 와 상태 절을 갱신하고 관련 research-question 의 Status Log 에도 적는다.
- 페이지에 모델 식별자를 적지 않는다.

## 관련
- [[li2s-assb-reference-cell]] — 이 절차로 등록된 첫 satellite
- [[anode-free-li2s-assb]] — 다음에 이 절차를 쓸 프로젝트
- [[paper-ingest-mode]] — 프로젝트가 특정 논문의 수치·정의를 반복 참조하면 제안하는 opt-in 모드
- [[wsl-li2s-setup]] — 새 기계에서 저장소·webapp·alias 를 세팅하는 절차
