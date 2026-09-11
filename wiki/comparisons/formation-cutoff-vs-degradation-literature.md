---
title: 논문 비교 — formation cut-off / 상한 전압 vs 열화 거동
description: "논문 간 조건·성능 비교의 축 정의와, 초기 투입 예정 논문 10편의 자리 (아직 DB 에 없음). 실제 표는 webapp /compare 가 papers/ 노트의 paper: 블록에서 만든다"
created: 2026-09-11
updated: 2026-09-11
type: comparison
tags: [cutoff-voltage, formation, mid-ni, high-ni, sulfide-electrolyte, units]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: low
explored: false
verificationStatus: unverified
claimType: mixed
evidenceScope: user-original
---

# 논문 비교 — formation cut-off / 상한 전압 vs 열화 거동

## 비교 이유
우리 DOE([[formation-cutoff-doe]])의 축은 **formation 충전 cut-off (3.6–4.6 V vs. Li/Li⁺)** 이고, main cycle 창은
**2.5–4.4 V vs. Li/Li⁺** 다. 논문들은 대개 formation 을 따로 설계하지 않고 **상한 전압(upper cut-off)** 을 바꾼다.
그래서 비교의 1차 축은 "**formation cut-off 또는 상한 전압** vs **열화 거동**(retention, 저항 성장, CEI 산물,
rock-salt, 균열)" 이고, 2차 축은 우리 조건과의 차이(전압 기준전극·양극 조성·온도·압력·loading)다.

정본은 각 논문 노트(`papers/<slug>.md`)의 `paper:` 블록이며, webapp `/compare` 가 그것을 평탄화해 표로 펴고
**내 DOE 창과의 겹침**(안 / 위로 벗어남 / 아래·좁음 / 미상)을 표시한다. 이 페이지는 축의 정의와 판단을 적는 자리다.

## 비교표 (축 정의 — 값은 webapp 이 채운다)

| 축 | 열 (paper: 키) | 비교 시 반드시 짚을 것 |
|---|---|---|
| 상한 전압 / formation cut-off | `main_cycle.window_vs_li` · `formation.cutoff_v_li` | **원문 기준전극** (`voltage.reference_raw`) 과 offset — vs. Li-In 값을 그대로 비교하면 0.62 V 틀린다 |
| 양극 | `cathode.composition_verbatim` · `crystal` · `coating` | 원문 표기 그대로 (NCA↔NCM 변환 금지) — Ni 함량이 다르면 상전이 전압이 다르다 |
| 전극·loading | `electrode_process` · `loading_mg_cm2` · `loading_mah_cm2` · `composite_ratio` | 우리는 건식 2 mAh cm⁻² — 슬러리·저로딩 결과와 저항 성장 속도가 다르다 |
| 전해질·음극 | `electrolyte.type` · `anode.type` | LGPS 는 산화 창이 다르고, Li 금속 음극은 음극 계면 저항이 섞인다 |
| 온도·압력 | `main_cycle.temperature_c` · `pressure_fab_mpa` · `pressure_op_mpa` | 우리는 45 °C · 462/277 MPa 제작 · 100 MPa 구동 — 압력이 낮은 논문은 healing 이 약하다 ([[mechano-electrochemical-healing]]) |
| 성능 | `performance.*` | retention 의 분모·사이클 수 정의를 맞춘다; 비용량 분모(활물질 vs 복합체) 확인 |
| 열화 거동 | `mechanisms[]` (태그·산물·전압대·근거) | figure/page 근거 없는 주장은 표에 넣지 않는다 |

## 초기 투입 예정 논문 (제목 기준 — 사용자 진술 F12; **아직 DB 에 없음**)

| # | 논문 (파일 제목 기준) | 걸리는 메커니즘 페이지 (예상) | 상태 |
|---|---|---|---|
| 1 | Chemo-Mechanical Behavior of High- and Mid-Ni Cathodes in Sulfide-Based ASSBs (Small Structures 2026, Suppl. 포함) | [[mid-ni-vs-high-ni-degradation]] · [[h2-h3-phase-transition-identification]] · [[interface-degradation-cathode-electrolyte-anode]] | 미투입 |
| 2 | Compromise between energy density and stability (capacity balancing) | [[mid-ni-vs-high-ni-degradation]] | 미투입 |
| 3 | Engineering Stable Decomposition Products on Cathode Surfaces to Enable High Voltage | [[lpscl-oxidative-decomposition-by-voltage]] · [[cei-formation-sulfide-cathode]] | 미투입 |
| 4 | Mechanoelectrochemical healing at NCM/LPSCl interfaces | [[mechano-electrochemical-healing]] | 미투입 |
| 5 | Interfacial degradation of the NMC/Li6PS5Cl composite cathode | [[cei-formation-sulfide-cathode]] · [[interface-degradation-cathode-electrolyte-anode]] | 미투입 |
| 6 | Decoupling first-cycle capacity loss mechanisms in sulfide SSBs | [[cei-formation-sulfide-cathode]] · [[formation-preconditioning-protocol]] | 미투입 |
| 7 | Li10GeP2S12/NCM622 interface stability | [[lpscl-oxidative-decomposition-by-voltage]] (LGPS 대조) | 미투입 |
| 8 | Failure mechanisms of dry-processed thick electrodes | [[interface-degradation-cathode-electrolyte-anode]] | 미투입 |
| 9 | Dual-ion modification for high-voltage mid-Ni single-crystal cathode | [[ni-co-o-redox-and-oxygen-release]] · [[mid-ni-vs-high-ni-degradation]] | 미투입 |
| 10 | High/Mid-Ni Nano Convergence modeling paper | [[mid-ni-vs-high-ni-degradation]] · [[h2-h3-phase-transition-identification]] | 미투입 |

각 논문은 `/paper` 로 들어오면서 `papers/<slug>.md` 노트가 생기고 이 표의 "상태" 가 "노트 있음" 으로 바뀐다.
같은 논문이 파일명만 다르게 다시 들어오면 DOI 로 잡아 기존 노트를 갱신한다 ([[paper-agent-workflow]]).

## 결론
아직 없다 — DB 에 논문이 0편이다. 첫 결론은 논문 3편 이상이 들어와 `/compare` 표에 상한 전압 축으로 정렬된 뒤
이 절에 날짜와 함께 적는다.

## 불확실성
- "상한 전압" 과 "formation cut-off" 는 같은 물리량이 아니다 — 논문의 상한 전압은 매 사이클 반복되고 우리 cut-off 는
  2 사이클뿐이다. 표에서 두 열을 섞지 않는다.
- 논문의 loading·압력이 우리와 다르면 같은 전압에서도 열화 속도가 다르다 — 겹침 표시는 전압 창만 본다.

## 관련
- [[formation-cutoff-doe]] · [[formation-cutoff-vs-long-term-degradation]] · [[paper-agent-workflow]]
