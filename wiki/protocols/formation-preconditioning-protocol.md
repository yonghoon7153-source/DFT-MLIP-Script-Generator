---
title: Formation (pre-conditioning) 프로토콜 — 0.1C/0.1C 2 cycles, 충전 cut-off 3.6–4.6 V vs. Li/Li⁺
description: "우리 셀의 formation 절차 — C-rate·사이클 수는 고정, 충전 cut-off 만 6 수준으로 바꾸는 DOE 의 프로토콜 정의 (사용자 진술 사본)"
created: 2026-09-11
updated: 2026-09-11
type: protocol
tags: [formation, cutoff-voltage, nca721, sulfide-electrolyte, units]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
---

# Formation (pre-conditioning) 프로토콜

## 목적
이 연구의 **조작 변수 하나**를 정의하는 절차다. formation 은 셀이 처음 delithiation(충전)·lithiation(방전)을
겪는 구간이고, 여기서 **충전 cut-off 전압**을 바꾸면 이후 main cycle([[main-cycle-protocol]])의 성능과
열화 경로가 달라진다는 것이 핵심 가설이다 ([[formation-cutoff-vs-long-term-degradation]]).

## 조건 (사용자 진술의 사본 — 정본은 실험 노트·registry)

| 항목 | 값 | 비고 |
|---|---|---|
| 셀 | [[cell-fabrication-conditions]] 의 표준 셀 (NCA721 건식 복합양극 \| LPSCl \| Li-In) | 구동압 100 MPa |
| C-rate | **0.1C 충전 / 0.1C 방전** | 고정 |
| 사이클 수 | **2 cycles** | 고정 |
| 충전 cut-off | **3.6 · 3.8 · 4.0 · 4.2 · 4.4 · 4.6 V vs. Li/Li⁺** | 조작 변수 (6 수준) — [[formation-cutoff-doe]] |
| 방전 cut-off | 미기재 (main cycle 과 같은 2.5 V vs. Li/Li⁺ 로 추정 — **미확인**, 킥오프 기록 Q4) | 확인 필요 |
| 온도 | 미기재 (main cycle 은 45 °C) | 확인 필요 |
| formation 후 | **24 h rest 전압 tracking** → [[auxiliary-measurements]] | |

기록 기준: 원 데이터의 전압은 **vs. In/Li-In** 이다. vs. Li/Li⁺ 로 읽으려면 **+0.62 V** 를 더한다
(정본 상수 `config/cells.yaml` — [[voltage-reference-and-capacity-conventions]]). 즉 cut-off 4.0 V vs. Li/Li⁺ 는
장비에는 3.38 V vs. In/Li-In 으로 설정된 값이다 (변환은 항상 방향을 적는다).

## 절차
1. 셀 제작 후 구동압 100 MPa 를 걸고 OCV 를 기록한다 (vs. In/Li-In 원본 보존).
2. 0.1C 로 지정 cut-off 까지 충전(delithiation) → 0.1C 로 방전(lithiation). 2회 반복.
3. formation 종료 후 24 h rest — 전압을 tracking 한다 (자가방전·이완 거동, [[auxiliary-measurements]]).
4. [[main-cycle-protocol]] 로 넘어간다.
5. 데이터: raw CSV(utf-8-sig) → `tools/cells/import_cell.py` → 사이클 요약 (비용량 mAh g⁻¹). registry 에
   `formation_cutoff_v_li` 를 적는다 ([[cell-registry]]).

## 기록해야 할 것
- 각 formation 사이클의 충전/방전 비용량(mAh g⁻¹), ICE, 충전 종지 시 전류 프로파일(CV 단계가 있는지),
  평균 충·방전 전압, voltage hysteresis.
- 1 사이클과 2 사이클의 차이 (2 사이클에서 비가역 용량이 남는지 — CEI·SE 분해가 계속되는지의 첫 신호,
  [[cei-formation-sulfide-cathode]] · [[lpscl-oxidative-decomposition-by-voltage]]).
- cut-off 가 높을수록 첫 충전에서 H2–H3 영역에 진입하는지 (dQ/dV) — [[h2-h3-phase-transition-identification]].

## 불확실성
- 방전 cut-off·온도·rest 시간 등 미기재 항목은 위키가 채우지 않는다 — 사용자 확인 후 이 표를 갱신하고
  `updated` 를 올린다.
- C-rate 의 기준 용량(1C 정의: 이론용량인지 설계 면적용량 2 mAh cm⁻² 기준인지)도 미기재.

## 관련
- [[formation-cutoff-doe]] — 이 프로토콜을 변수로 쓰는 실험 설계
- [[main-cycle-protocol]] — 이어지는 장기 사이클
- [[nca721-formation-project]] — 프로젝트 카드
