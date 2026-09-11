---
title: Paper Ingest Mode
description: "논문 수치·정의를 verbatim atom 으로 분해하는 opt-in 모드 — 이 저장소의 기본은 /paper 의 전문 digest 이며 이 모드는 그 위에 얹는 부분 atomization"
created: 2026-08-06
updated: 2026-09-11
type: guide
tags: [wiki]
sources: [raw/articles/2026-08-06-cmds-llm-wiki-changelog.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: single-source
---

# Paper Ingest Mode

## 목적
논문의 수치·정의·인용문을 나중에 **verbatim 재사용**할 수 있는 atom 페이지로 분해하는 ingest
모드. 원본 패턴: cmds-llm-wiki v1.10.0 "12-step paper atomization" 의 lite 채택판.

**이 저장소에서의 위치**: 기본 논문 처리는 `/paper` (논문 에이전트)의 **절별 전문 digest**
(`raw/papers/`, `[인쇄]/[도표]/[해석]/[재현]` 4구분, `compare:` frontmatter)다. 그것만으로
"그 논문의 그 값이 뭐였지" 는 대부분 해결된다. 이 모드는 **집필 단계**에서 특정 논문의
수치·정의를 반복 인용할 때만 추가로 쓴다.

## 발동 조건 (opt-in — 자동 실행 금지)
1. 기본값: 논문은 `/paper` 로 처리한다.
2. 에이전트는 **프로젝트가 이 논문의 수치·정의를 반복 참조할 것 같을 때만** 이 모드를 제안한다.
3. **사용자 승인 후 실행.** 승인 없이는 절대 실행하지 않는다.
4. 논문 전체가 아니라 **필요한 좌표만** 부분 atomization 한다.

## 절차
1. **감지·분류**: DOI 확인, 논문 유형(quantitative / mixed 등).
2. **범위 합의**: 좌표 세트 — `citation` `method` `results`(verbatim 수치) `definitions`
   `limitations` `writing-value` 중 필요한 것.
3. **Raw**: digest 가 이미 있으면 그것이 raw 다 (새 raw 를 만들지 않는다).
4. **Hub + atom**: concept 1페이지(hub) 안의 절로 두는 것이 기본. 페이지 남발 금지.
5. **인용 검증**: 모든 verbatim 인용·수치를 digest 의 `[인쇄]` 항목과 대조한다. `[도표]` 값은
   atom 에 넣을 때도 `[도표]` 를 유지한다.
6. **RQ 라우팅**: 열린 research-question 카드에 근거를 준다면 Evidence For/Against 에 추가.

## 한계·불확실성
- 원본 v1.10.0 의 정식 12좌표 전체는 미확보 — 위 좌표 세트는 릴리스 노트 기반 adapted 버전.
- 수백 편 자동 처리는 범위가 아니다.

## 관련
- [[new-project-kickoff]] — satellite 등록 절차
- [[seminar-prep-from-digest]] — digest 를 발표 자료로 옮기는 절차 (이 모드와 달리 기본 워크플로)
