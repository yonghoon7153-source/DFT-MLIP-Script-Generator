---
title: 용량 정규화 — mAh g⁻¹(S) vs mAh g⁻¹(Li2S) vs 복합체 기준
description: "Li2S 문헌은 황 질량 기준(1675)과 Li2S 질량 기준(1166)을 섞어 쓴다 — 환산 0.698, Kim 2023 수치의 양단위 표, 우리 500–600 목표가 어느 기준인지의 문제, 이 위키의 표기 규율"
created: 2026-09-11
updated: 2026-09-11
type: concept
tags: [units, li2s, composite-cathode]
sources: [raw/papers/kim2023_reinforced-electrical-networking-high-loading-li2s-cathode.md, raw/transcripts/2026-09-11-li2s-wiki-kickoff-session.md]
confidence: high
explored: false
verificationStatus: unverified
claimType: definition
evidenceScope: multi-source-mixed
---

# 용량 정규화 — mAh g⁻¹(S) vs mAh g⁻¹(Li2S) vs 복합체 기준

## 정의

Li2S 양극의 비용량은 세 가지 분모로 보고된다. 분모를 적지 않은 숫자는 **비교 불가**다.

| 기준 | 이론용량 | 근거 (산술) |
|---|---|---|
| 황 질량 `(S)` | **1675 mAh g⁻¹** | 2 F / M(S) = 2 × 26801 mAh mol⁻¹ / 32.065 g mol⁻¹ |
| Li2S 질량 `(Li2S)` | **1166 mAh g⁻¹** | 2 F / M(Li2S) = 53602 / 45.95 |
| 환산 인자 | (Li2S) = (S) × **0.6978** | M(S)/M(Li2S) = 32.065/45.95 |
| 복합체 질량 `(composite)` | 활물질 분율 × (Li2S) | 우리 30 wt% 조성: (composite) = 0.30 × (Li2S) |

면적용량: `mAh cm⁻²` = 비용량 × 로딩. 로딩이 **Li2S 질량**인지 **S 질량**인지도 적는다
(15 mg cm⁻²(Li2S) = 10.47 mg cm⁻²(S)).

## Kim 2023 수치를 두 단위로 (`[재현]`, 원문은 전부 `(S)` 기준)

| 조건 | (S) | (Li2S) | 면적 (mAh cm⁻²) | 출처 |
|---|---|---|---|---|
| 반쪽셀 첫 방전, 0.1 C, 15 mg cm⁻²(Li2S) | `[도표]` ≈ 1150 | ≈ 800 | 11.5 `[인쇄]` | Fig. 4A, Table S1 |
| 반쪽셀 사이클, 0.5 C | 899.6 `[인쇄]` | **628** | 9.3–9.4 | p.8, Table S1 |
| Full cell 사이클, 0.2 C, 10 mg cm⁻²(Li2S) | ≈ 760 | **530** | 5.3 `[인쇄]` | Fig. 4D, Table S1 |
| Full cell 800 사이클 후 | ≈ 330 | ≈ 230 | ≈ 2.3 `[도표]` | Fig. 4D |
| 파우치 반쪽셀, 0.05 C | ≈ 915 | ≈ 640 | 6.7 `[인쇄]` | Fig. 8B, Table S2 |
| Lean 7 µL mg⁻¹, 0.2 C | ≈ 930 | ≈ 650 | ~9.7 `[인쇄]` | Fig. S11 |

주의: 원문 p.8 의 "899.6 mAh g⁻¹ (11.5 mAh cm⁻²)" 는 괄호 안이 0.1 C 값이다 (digest G3).

## 우리 목표 "500–600 mAh g⁻¹" 은 어느 기준인가 (미결 Q1)

| 목표가 이 기준이면 | (S) 환산 | (Li2S) 환산 | (composite, 30 wt%) |
|---|---|---|---|
| (Li2S) 기준 500–600 | 716–860 | 500–600 | 150–180 |
| (S) 기준 500–600 | 500–600 | 349–419 | 105–126 |

`[해석]` "문헌에서 주로 보고되는 값" 이라면 ASSB Li2S 논문은 대체로 **Li2S 질량 기준**으로
적는 경우가 많다고 알려져 있으나, 이것은 **다음 ingest 로 확인할 사항**이다. 확인 전에는
위키의 목표를 "500–600 mAh g⁻¹ (기준 미확인)" 으로만 적는다.

## 이 위키의 규율 (SCHEMA 특칙)

1. 비용량에는 항상 `(S)` / `(Li2S)` / `(composite)` 중 하나를 붙인다.
2. 면적용량에는 로딩과 그 로딩의 질량 기준을 붙인다.
3. 논문 digest 의 `compare:` 블록은 `_mAh_gS` 와 `_mAh_gLi2S` 두 필드를 **둘 다** 둔다
   (원문이 하나만 주면 다른 하나는 `[재현]` 으로 환산해 채운다).

## 관련

- [[li2s-assb-reference-cell]] — 목표 단위 확인이 첫 미결
- [[li2s-assb-composite-cathode]] — 복합체 기준 환산의 분모(30 wt%)
- [[kim2023-seminar-prep]] — 발표에서 단위를 어떻게 말할지
