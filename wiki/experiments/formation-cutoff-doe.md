---
title: DOE — formation 충전 cut-off 6 수준 × 200 사이클
description: "조작 변수 하나(formation 충전 cut-off 3.6–4.6 V vs. Li/Li⁺), 고정 조건, 산출물, 가설 연결을 한 장에 정리한 실험 설계"
created: 2026-09-11
updated: 2026-09-11
type: experiment
tags: [formation, cutoff-voltage, nca721, cell-data]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
---

# DOE — formation 충전 cut-off

## 설계
**단일 변수 설계**: formation 충전 cut-off 만 바꾸고 나머지는 전부 고정한다. 셀 제작·formation·main cycle 조건은
각각 [[cell-fabrication-conditions]] · [[formation-preconditioning-protocol]] · [[main-cycle-protocol]] 이 정본이다.

## 변수와 고정 조건

| 변수 | 수준 |
|---|---|
| formation 충전 cut-off (vs. Li/Li⁺) | **3.6 · 3.8 · 4.0 · 4.2 · 4.4 · 4.6 V** (6 수준) |

| 고정 조건 | 값 |
|---|---|
| formation | 0.1C/0.1C · 2 cycles |
| main cycle | 2.5–4.4 V vs. Li/Li⁺ · 0.5C · 45 °C · 200 cycles |
| 셀 | NCA721 건식 복합양극 (2 mAh cm⁻²) \| LPSCl \| Li-In · 구동압 100 MPa |

수준의 구조를 미리 읽어 둔다:
- **3.6 · 3.8 · 4.0 · 4.2 V** — main cycle 상한(4.4 V) **아래**에서 formation. 첫 delithiation 깊이가 얕다.
- **4.4 V** — main cycle 상한과 **같다** (기준 조건 역할).
- **4.6 V** — main cycle 상한 **위**로 한 번 다녀온 유일한 조건. 이 셀만 4.4–4.6 V 구간의 SE 산화·격자 산소 반응을
  formation 에서 겪는다 ([[lpscl-oxidative-decomposition-by-voltage]] · [[ni-co-o-redox-and-oxygen-release]]).

## 측정·산출물

| 산출물 | 정의 (registry 비고에 정의를 적는다) | 페이지 |
|---|---|---|
| 초기 방전 비용량 (mAh g⁻¹) | formation 1 사이클 / main 1 사이클 두 값을 따로 | [[cell-data-module]] |
| ICE (%) | formation 1 사이클 방전/충전 | |
| 200 사이클 retention (%) | 분모 정의 필수 (main 1 사이클 방전 기준 권장) | [[main-cycle-protocol]] |
| 과전압·hysteresis 추세 | 사이클 vs 평균 충·방전 전압 차 | |
| EIS (2번째 main cycle SOC 100 %) | R_SEI/CEI·R_ct 대역 | [[auxiliary-measurements]] |
| 24 h rest 전압 | formation 후 | |
| 사후분석 (200 cycle, SOC 100 %) | XRD·XPS·ToF-SIMS·FIB-SEM·STEM·Raman | |

## 가설 연결 (질문 카드)
- 주 가설은 [[formation-cutoff-vs-long-term-degradation]] 의 H1–H5.
- 격자 산소 축은 [[lattice-oxygen-involvement-at-high-cutoff]], 저항 귀속은 [[contact-loss-vs-cei-growth-attribution]].

## 셀 등록
각 셀은 [[cell-registry]] (`data/registry/cells.csv`) 에 `formation_cutoff_v_li` 와 함께 등록한다. 파일명의
전압(예: `_4.0V_`)은 제안값이며 registry 가 정본이다. 반복(n) 수는 registry 를 세어 알 수 있게 한다 —
**같은 cut-off 에 셀이 몇 개인지가 곧 통계적 신뢰의 전부**이므로 화면(`/cells`)이 cut-off 별 n 을 표시한다.

## 상태
- **2026-09-11** — 위키에 설계 등록. 어떤 수준의 셀이 완료됐는지는 registry 가 비어 있어 아직 모른다 (Q6).

## 관련
- [[formation-preconditioning-protocol]] · [[main-cycle-protocol]] · [[nca721-formation-project]]
