---
title: New Project Kickoff
description: "새 실험 프로젝트(satellite)를 이 위키에 등록하는 킥오프 프롬프트 — repo-root 상대 경로판"
created: 2026-07-30
updated: 2026-09-11
type: guide
tags: [satellite, wiki]
sources: [raw/transcripts/kit-provenance-260730.md, raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: multi-source-mixed
---

# New Project Kickoff

## 목적
새 실험 프로젝트(예: 후순위의 High-Ni 비교, anode-free 저압 파우치 — [[followup-high-ni-and-anode-free-pouch]])를
시작할 때 그 세션에 붙여넣는 킥오프 프롬프트. 킷 원본의 `<MOTHERSHIP>` 절대 경로 대신 **repo-root 상대 경로**를
쓴다 (WSL·서버 clone 경로가 다르다).

## 킥오프 프롬프트 (복사해서 [ ] 채우고 붙여넣기)

```
새 실험 프로젝트 시작. 아래대로 세팅해줘.

[프로젝트 정보]
- 이름/슬러그: [예: high-ni-comparison]
- 목표 (1~3줄): [ ]
- 셀 구성·프로토콜에서 NCA721 프로젝트와 다른 것: [ ]

[세팅 순서]
1. wiki/SCHEMA.md 를 먼저 읽는다 (특히 "이 저장소 특칙" — 절대 규칙, 논문 두 파일, ours: 블록).
2. python3 wiki/tools/new-page.py entity <슬러그> → 개요·핵심 사실(사용자 진술 사본)·상태·질문 채우기,
   [[wikilink]] 2개 이상. 우리 셀이면 ours: 블록 (paper: 와 같은 구조) 을 채운다.
3. 프로토콜이 다르면 wiki/protocols/ 에 새 페이지, DOE 는 wiki/experiments/ 에.
4. wiki/index.md 등록 + wiki/log.md append + python3 wiki/tools/lint.py 0 errors + commit (create(wiki):)
5. 이 킥오프 대화의 설계 결정과 사용자 진술 원문은 wiki/raw/transcripts/<슬러그>-kickoff-YYMMDD.md 로
   기록하고 wiki/tools/seal.py 로 봉인한다.
```

## 이미 진행 중인 프로젝트를 등록할 때
위 프롬프트 5번을 먼저 하고(사용자 진술 원문 보존), 그 파일을 entity 의 `sources` 로 삼는다.

## 한계·불확실성
- 프로젝트 세션의 Claude 는 다른 세션의 메모리를 못 본다 — 이 프롬프트가 자기완결이어야 하는 이유.
- 첫 satellite 는 [[nca721-formation-project]] 이며 이 절차의 선례다.

## 관련
- [[nca721-formation-project]] · [[paper-ingest-mode]]
