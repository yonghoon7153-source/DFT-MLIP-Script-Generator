---
title: Paper Ingest Mode
description: "논문의 수치·정의·인용문을 verbatim atom 으로 분해하는 opt-in ingest 모드 — 이 저장소의 기본은 /paper 의 digest + 노트이며 이 모드는 사용자 승인 후에만"
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
논문의 수치·정의·인용문을 나중에 **verbatim 재사용**할 수 있는 atom 페이지로 분해하는 ingest 모드. 원본 패턴은
cmds-llm-wiki v1.10.0 "12-step paper atomization" 의 lite 채택판이다. **이 저장소의 기본 논문 처리는 `/paper`
의 digest(절별 전문) + 논문 노트(`paper:` 스키마)** 이며 대부분의 재조회는 그것으로 해결된다
([[paper-agent-workflow]]). 이 모드는 그 위에 얹는 선택지다.

## 발동 조건 (opt-in — 자동 실행 금지)
1. 기본값: 논문은 `/paper` 로 처리한다.
2. 에이전트는 **프로젝트가 이 논문의 수치·정의를 반복 참조할 것 같을 때만** 이 모드를 사용자에게 제안한다.
3. **사용자 승인 후 실행.** 승인 없이는 절대 실행하지 않는다.
4. 논문 전체가 아니라 **필요한 좌표만** 부분 atomization 한다.

## 절차
1. **분류**: 논문 유형 (quantitative / qualitative / theory / mixed / meta-analysis).
2. **범위 합의**: 좌표 세트 중 필요한 것만 — `citation` · `method` · `results`(수치 verbatim) · `definitions` ·
   `limitations` · `writing-value`.
3. **Raw 저장**: digest 가 이미 있으면 그것을 쓴다 (`raw/papers/<slug>.md`).
4. **Hub + atom 컴파일**: hub 는 논문 노트(`papers/<slug>.md`) 본문의 절로, atom 은 소수면 그 안의 절로 충분하다
   (페이지 남발 금지, Page Thresholds 준수).
5. **인용 검증**: 모든 verbatim 인용·수치를 digest 원문과 대조한다. 원문에 없는 문자열은 atom 에 넣지 않는다.
6. **RQ 라우팅**: 열린 research-question 카드에 근거를 준다면 Evidence For/Against 에 추가.

## 한계·불확실성
- 원본 v1.10.0 의 정식 12좌표 이름 전체(S01~S12)는 미확보 — 위 좌표 세트는 릴리스 노트 기반 adapted 버전이다.
- 대량 자동 처리는 이 모드의 범위가 아니다 — 사람이 정독할 소수 논문 전용.

## 관련
- [[paper-agent-workflow]] — 이 저장소의 기본 논문 처리
- [[new-project-kickoff]] — satellite 등록 절차
