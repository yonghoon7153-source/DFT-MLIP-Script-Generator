---
title: Main cycle 프로토콜 — 2.5–4.4 V vs. Li/Li⁺, 0.5C, 45 °C, 200 cycles
description: "formation 뒤 장기 사이클 조건과 2번째 사이클 SOC 100 % EIS 시점 (사용자 진술 사본)"
created: 2026-09-11
updated: 2026-09-11
type: protocol
tags: [nca721, cutoff-voltage, eis, units]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
---

# Main cycle 프로토콜

## 목적
formation cut-off 의 효과를 **장기 성능**으로 읽어 내는 구간. 모든 DOE 셀이 같은 창·같은 C-rate·같은 온도로
돌아가므로, 셀 간 차이는 formation 이력(그리고 셀 제작 산포)에서만 온다.

## 조건 (사용자 진술의 사본 — 정본은 실험 노트·registry)

| 항목 | 값 | 비고 |
|---|---|---|
| 전압창 | **2.5–4.4 V vs. Li/Li⁺** | 장비 설정은 1.88–3.78 V vs. In/Li-In (−0.62 V — [[voltage-reference-and-capacity-conventions]]) |
| C-rate | **0.5C** (충·방전) | 1C 정의 미기재 |
| 온도 | **45 °C** | formation 온도는 미기재 |
| 사이클 수 | **200 cycles** | 종료 후 SOC 100 % 로 수득 → 사후분석 |
| 구동압 | 100 MPa ([[cell-fabrication-conditions]]) | |
| EIS | **2번째 main cycle, SOC 100 %** 에서 — 셀을 RT 로 옮겨 **온도 평형 후** 측정 | [[auxiliary-measurements]] |

## 절차
1. formation([[formation-preconditioning-protocol]]) 과 24 h rest 뒤 45 °C 챔버에서 0.5C 사이클 시작.
2. 2번째 사이클 충전 종료(SOC 100 %) 시점에 RT 로 옮겨 온도 평형을 기다린 뒤 EIS → 다시 45 °C 로 복귀.
3. 200 사이클 후 SOC 100 % 상태로 셀을 해체해 양극을 수득 → 사후분석 ([[auxiliary-measurements]]).

## 기록해야 할 것
- 사이클별 방전 비용량(mAh g⁻¹), CE, 평균 충·방전 전압, voltage hysteresis, 에너지 효율 — 사이클 요약 CSV
  ([[cell-data-module]]).
- **200 사이클 후 capacity retention (%)** — 첫 main cycle 방전 비용량 대비로 정의하는지, formation 첫 방전
  대비인지 **정의를 registry 비고에 적는다** (논문마다 다르므로 비교표에서 명시).
- 과전압/hysteresis 추세: 사이클에 따른 증가 기울기 (계면 저항 성장의 대리 지표 — [[cei-formation-sulfide-cathode]]).

## 불확실성
- 4.4 V vs. Li/Li⁺ 상한은 formation cut-off 6 수준 중 4.6 V 보다 낮다 — 즉 4.6 V formation 셀만 main cycle
  창 밖(위)까지 한 번 갔다 온 셀이다. 이 비대칭이 설계의 핵심이며 해석 시 항상 짚는다
  ([[formation-cutoff-doe]]).

## 관련
- [[formation-cutoff-doe]] · [[auxiliary-measurements]] · [[nca721-formation-project]]
