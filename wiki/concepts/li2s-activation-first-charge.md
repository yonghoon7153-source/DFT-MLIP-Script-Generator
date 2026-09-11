---
title: Li2S 첫 충전 활성화
description: "절연체 Li2S 의 첫 탈리튬화 장벽 — 첫 충전에서 활성화한 만큼만 이후 용량이 된다(Kim 2023 Fig. S1), 3.2 V 단조 plateau 와 직접 전환, 활성화를 정하는 요인"
created: 2026-09-11
updated: 2026-09-11
type: concept
tags: [activation, li2s, carbon, liquid-electrolyte]
sources: [raw/papers/kim2023_reinforced-electrical-networking-high-loading-li2s-cathode.md, raw/transcripts/2026-09-11-li2s-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: empirical
evidenceScope: single-source
---

# Li2S 첫 충전 활성화

## 정의

Li2S 는 전자·이온 모두 절연에 가깝고(`[인쇄]` ~10⁻¹³ S cm⁻¹, Kim 2023 도입부가 refs 21·22 를
인용), 첫 충전(탈리튬화)에 높은 활성화 에너지가 필요하다. **"첫 충전에서 활성화된 Li2S 가
이후의 에너지밀도와 사이클 용량을 지배한다"** — Kim et al. 2023 이 도입부에 명시하고 Fig. S1
로 보인 명제 (`raw/papers/kim2023_…` §2.2, §9.1).

## 근거 (Kim 2023 — 액체 에테르 전해질, Li 금속 반쪽셀)

1. **Fig. S1 (★)**: 첫 충전 용량을 25/50/75/100 % 로 제한한 네 셀의 이후 방전 용량이
   `[도표]` ≈ 270 / 530 / 730 / 930 mAh g⁻¹(S) 로 **20 사이클 동안 네 층 그대로** 유지된다.
   활성화 안 된 Li2S 는 뒤 사이클에서 자발적으로 깨어나지 않았다.
2. **곡선 모양**: Gr/CNT 양극의 첫 충전은 `[도표]` ~3.4 V 스파이크 후 **3.15–3.2 V 에서 시작해
   완만히 상승**하며 3.6 V 컷오프까지 이어진다. 통상의 Li2S 곡선(초기 고전압 → LiPs 가 redox
   mediator 로 작동하며 전압 하강)과 달리 **내려가지 않는다** — 저자는 이를 LiPs 없는
   **직접 전환 Li2S → S8** 의 서명으로 읽고 in situ Raman(S8 12 % SoC 조기 출현, LiPs 밴드 부재)·
   in situ OM(노란 LiPs 없음)·cryo-TEM(50 % SoC 에 β-S8 + Li2S 공존)으로 뒷받침한다.
3. **활성화를 늘린 요인** (저자 귀속): 2D 그래핀의 큰 접촉면적, 소량 CNT 의 네트워크(전기적
   고립부 제거), 1 GPa compact geometry, 고압 성형으로 생긴 준안정 orthorhombic Li2S.
   → [[carbon-dimensionality-electron-network]].

## 활성화를 정하는 변수 (이 위키의 작업 목록)

| 변수 | Kim 2023 에서 | 우리 ASSB 에서 |
|---|---|---|
| 전자 접촉·네트워크 | Gr 접촉 + CNT 3 wt% 네트워크 | AB 20 wt%; 탄소 차원 분리 미시도 |
| 입자 크기 | micro 1–5 µm 그대로 | ball milling 으로 나노화 시도 ([[composite-cathode-mixing-routes]]) |
| 이온 접근 | 액체 전해질이 어디든 닿음 | **LPSCl 이 Li2S 표면에 닿아야만** 반응 — 삼상 계면 |
| 전압 컷오프 | 3.6 V vs Li/Li⁺ | SE 산화 한계 안에서 — 값은 ingest 후 (미검증) |
| C-rate | 0.1 C (활성화), 0.05 C(파우치) | 미결 Q3 |
| 매개체 | LiNO3 0.8 M (고농도), LiPs 미형성 | 고체라 LiPs 매개 없음 — 직접 전환이 **기본 경로** |

`[해석]` 마지막 줄이 핵심이다: 액체계에서 "특이" 하다고 보고된 직접 전환이 고체계에서는
**유일한 경로**다. 따라서 Kim 2023 의 in situ 관측은 우리 활성화 과정의 **정성적 모델**로
쓸 수 있다 (다만 LiNO3·에테르가 만든 환경은 뺀 채로).

## 이 위키에서의 적용

- [[reference-cell-500-600-mahg]] 의 H1(활성화 제한) 이 이 개념 위에 선다: 우리 셀의 **첫 충전
  용량 vs 이후 방전 용량** 관계를 Fig. S1 방식으로 찍어 보는 것이 가장 값싼 진단이다.
- [[anode-free-li2s-assb]] 에서는 활성화량 = Li 재고 상한.

## 한계·불확실성

- 근거가 논문 하나(액체계)뿐이다 — `single-source`, confidence 는 medium 을 넘기지 않는다.
- Fig. S1 의 셀 조건(어느 양극·로딩)이 캡션에 없다.
- ASSB 에서 같은 "활성화 후 층 유지" 가 성립하는지는 **미검증** — ingest 대상.
