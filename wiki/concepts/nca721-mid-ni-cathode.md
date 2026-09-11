---
title: NCA721 — 우리 양극재의 이름과 표기 규칙 (절대 규칙 1)
description: "우리 실험 데이터의 양극재는 전부 NCA721 이다. NCM721 로 바꿔 부르거나 해석하지 않으며, 논문 조성은 원문 표기 그대로 둔다 — 그 규칙의 이유와 적용"
created: 2026-09-11
updated: 2026-09-11
type: concept
tags: [nca721, mid-ni, units]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
---

# NCA721 — 우리 양극재의 이름과 표기 규칙

## 정의
사용자 진술(킥오프 기록 F1·F13): 우리 실험의 양극재는 **NCA721** (mid-Ni, Li–Ni–Co–Al 계 층상 산화물) 이다.
정확한 몰비·공급원·코팅 여부는 위키에 아직 없다 — 추측해 적지 않는다.

## 규칙
1. 우리 데이터·페이지·대화에서 이 재료는 언제나 **NCA721** 이다. 파일명(`Dcell14_mid_Ni___…`)의 `mid_Ni` 도
   NCA721 을 뜻한다. NCM721 로 바꿔 부르거나 그렇게 해석하는 것은 금지다 (lint `no-ncm721` 가 위키·webapp·루트
   문서 전체를 검사한다 — 금지 규칙을 말하는 줄만 예외).
2. 논문 속 양극 조성은 **원문 표기 그대로** (NCM622, NCM85, NCA, LiNi₀.₈Co₀.₁Mn₀.₁O₂, LCO …) 적는다.
   NCA↔NCM 간 임의 변환 금지 — Al 과 Mn 은 상전이·표면 화학이 다르므로 이름을 바꾸면 비교가 틀어진다
   ([[mid-ni-vs-high-ni-degradation]]).
3. 논문 노트의 `cathode.composition_verbatim` 과 `ni_content` 는 원문 문자열이며, 비교표에서 "mid-Ni/high-Ni"
   분류는 사람이 읽고 붙인다 — 자동 변환하지 않는다.

## 왜 중요한가
mid-Ni 의 정의(Ni ≈ 0.6–0.7)와 high-Ni 의 정의(Ni ≳ 0.8)는 논문마다 조금씩 다르다. 이름을 통일하려다 조성을
바꿔 적으면 상전이 전압([[h2-h3-phase-transition-identification]])·산소 손실 문턱
([[ni-co-o-redox-and-oxygen-release]]) 비교가 무의미해진다. 그래서 이 위키는 **이름을 통일하지 않고 원문을 보존**한다.

## 이 위키에서의 적용
- 프로젝트 카드 [[nca721-formation-project]] 의 `ours.cathode.composition_verbatim` = "NCA721".
- `/chat` 은 논문과 우리를 비교할 때 양극 조성 차이를 자동으로 짚는다 ([[chat-citation-rules]]).

## 관련
- [[voltage-reference-and-capacity-conventions]] · [[nca721-formation-project]]
