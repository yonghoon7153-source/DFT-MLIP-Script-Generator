---
title: NCA721 formation cut-off 프로젝트 (satellite)
description: "sulfide ASSB 에서 NCA721 건식 복합양극 | LPSCl | Li-In 셀의 formation 충전 cut-off 최적화 — 우리 자신의 프로젝트 카드. ours: 블록이 /compare 의 첫 행이다"
created: 2026-09-11
updated: 2026-09-11
type: entity
tags: [project, satellite, nca721, formation, cutoff-voltage]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
ours:
  bib:
    first_author: "우리"
    year: 2026
    journal: null
    title: "NCA721 formation cut-off DOE (sulfide ASSB)"
    doi: null
  cathode:
    composition_verbatim: "NCA721"
    ni_content: "mid-Ni (몰비 원문 미기재)"
    crystal: null
    coating: null
    coating_type: null
    electrode_process: "dry"
    loading_mg_cm2: null
    loading_mah_cm2: 2
    composite_ratio: null
  electrolyte:
    type: "LPSCl (Li6PS5Cl, argyrodite)"
    detail: null
  anode:
    type: "Li-In"
    composition: "In foil 9Φ + Li foil 4Φ (몰비 미기재)"
  voltage:
    raw_text: "2.5–4.4 V (main) / 3.6–4.6 V (formation cut-off)"
    reference_raw: "vs. Li/Li+"
    window_vs_li: [2.5, 4.4]
    offset_applied_v: 0.0
    notes: "raw CSV 는 vs. In/Li-In 이며 +0.62 V 로 환산 (config/cells.yaml)"
  formation:
    described: true
    cutoff_v_raw: "3.6 / 3.8 / 4.0 / 4.2 / 4.4 / 4.6 V vs. Li/Li+"
    cutoff_v_li: null
    c_rate: "0.1C/0.1C"
    cycles: 2
    rest_h: 24
    temperature_c: null
  main_cycle:
    window_raw: "2.5–4.4 V vs. Li/Li+"
    window_vs_li: [2.5, 4.4]
    c_rate: "0.5C"
    temperature_c: 45
    pressure_fab_mpa: 462
    pressure_op_mpa: 100
    cycles: 200
  performance:
    initial_discharge_mah_g: null
    ice_pct: null
    retention_pct: null
    retention_cycles: 200
    overpotential_trend: null
    hysteresis_trend: null
    notes: "실측값은 위키에 적지 않는다 — 정본은 data/registry 와 data/cells 요약"
  techniques: [EIS, DRT, dQ/dV, operando-pressure, XRD, XPS, ToF-SIMS, FIB-SEM, HAADF-STEM, Raman]
  mechanisms: []
---

# NCA721 formation cut-off 프로젝트 (satellite)

## 개요
이 위키의 **첫 번째 satellite** — 사용자가 지금 수행 중인 실험 프로젝트. 논문 main concept은 "4.4 V 고전압 구동을
위한 Mid-/High-Ni 양극재 열화 메커니즘 규명 및 해당 메커니즘 기반 pre-conditioning 사이클 설계" 이고, 핵심 질문은
[[formation-cutoff-vs-long-term-degradation]] 이다. 후순위 프로젝트는 [[followup-high-ni-and-anode-free-pouch]].

## 핵심 사실 (사용자 진술, 2026-09-11 — 정본은 프로토콜 페이지·registry)

| 항목 | 값 | 페이지 |
|---|---|---|
| 셀 | NCA721 건식 복합양극 (2 mAh cm⁻²) \| LPSCl (Li6PS5Cl) \| Li-In (In 9Φ + Li 4Φ) | [[cell-fabrication-conditions]] |
| 제작압 / 구동압 | 462 MPa 2.5 min (양극+SE) · 277 MPa 5 min (음극) / 100 MPa | [[cell-fabrication-conditions]] |
| Formation | 0.1C/0.1C 2 cycles · 충전 cut-off 3.6 / 3.8 / 4.0 / 4.2 / 4.4 / 4.6 V vs. Li/Li⁺ | [[formation-preconditioning-protocol]] |
| Main cycle | 2.5–4.4 V vs. Li/Li⁺ · 0.5C · 45 °C · 200 cycles | [[main-cycle-protocol]] |
| 보조 측정 | EIS(2nd cycle SOC 100 %, RT) · 24 h rest · 3-전극 EIS/DRT · operando 압력(LTO) · 사후분석 | [[auxiliary-measurements]] |
| 데이터 | raw 전압 vs. In/Li-In (+0.62 V → vs. Li/Li⁺), 용량 mAh g⁻¹ | [[voltage-reference-and-capacity-conventions]] |

## 상태
- **2026-09-11** — 위키에 등록. 셀별 진행 상태는 registry 가 비어 있어 아직 없다 (Q6). 상태가 바뀌면 이 절에
  날짜와 함께 append 한다 (수치는 사본이며 정본은 `data/`).

## 이 프로젝트가 답해야 할 질문
- [[formation-cutoff-vs-long-term-degradation]] — cut-off 가 200 사이클 성능·메커니즘을 어떻게 바꾸는가 (H1–H5).
- [[lattice-oxygen-involvement-at-high-cutoff]] — 4.4–4.6 V 에서 격자 산소가 관여하는가.
- [[contact-loss-vs-cei-growth-attribution]] — 저항 증가를 어느 계면·어느 축에 귀속할 것인가.

## 미결 (사용자 확인 필요 — 킥오프 기록 §4)
- Q1 파일명 질량의 정체 · Q2 복합양극 조성비와 mg cm⁻² · Q3 Li-In 조성 · Q4 formation 방전 cut-off·rest·온도 ·
  Q5 사후분석 SOC 100 % 정의 · Q6 완료된 셀 목록.

## 관련
- [[formation-cutoff-doe]] · [[cell-registry]] · [[nca721-mid-ni-cathode]]
