---
title: Li2S ASSB reference cell
description: "pristine Li2S · LPSCl · AB = 30:50:20 복합양극 + Li–In 음극으로 문헌 수준 500–600 mAh g⁻¹ 을 재현하는 1단계 실험 프로젝트 (satellite)"
created: 2026-09-11
updated: 2026-09-11
type: entity
tags: [project, satellite, li2s, assb, composite-cathode, li-in]
sources: [raw/transcripts/2026-09-11-li2s-wiki-kickoff-session.md, raw/papers/kim2023_reinforced-electrical-networking-high-loading-li2s-cathode.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
compare:
  system: "ASSB Li–S (sulfide)"
  electrolyte: "argyrodite LPSCl (조성 미확인)"
  cathode: "Li2S : LPSCl : AB = 30 : 50 : 20 wt, binder-free pellet"
  li2s_source: "pristine (commercial) Li2S"
  mixing: "one-step BM (주) / two-step / 탄화 / 에탄올 — 비교 중"
  li2s_wt_pct: 30
  anode: "Li–In (→ anode-free 계획)"
  cycle_capacity_mAh_gLi2S: "목표 500–600 (기준 미확인)"
  our_axis: "우리 자신 — 사본, 실험 노트가 정본"
---

# Li2S ASSB reference cell

## 개요

이 위키의 **첫 번째 satellite** — 사용자가 지금 수행 중인 실험 프로젝트. pristine(상용, 미처리)
Li2S 를 양극 활물질로 쓰는 all-solid-state Li–S 셀에서, 문헌이 주로 보고하는
**500–600 mAh g⁻¹** 을 reference 로 재현하는 것이 목표다. 이것이 끝나면
[[anode-free-li2s-assb]] 로 넘어간다.

## 핵심 사실 (사용자 진술, 2026-09-11)

| 항목 | 값 |
|---|---|
| 활물질 | pristine Li2S |
| 고체전해질 | argyrodite LPSCl (정확한 조성 미확인 — 미결 Q2) |
| 도전재 | acetylene black (AB) |
| 복합양극 조성 | **Li2S : LPSCl : AB = 30 : 50 : 20 (질량)** → [[li2s-assb-composite-cathode]] |
| 음극 | Li–In |
| 목표 | 500–600 mAh g⁻¹ — **정규화 기준 미확인** (미결 Q1) → [[capacity-normalization-li2s-vs-sulfur]] |
| 혼합 경로 후보 | one-step BM / two-step(Li2S–C 선제작 + LPSCl) / Li2SO4–PVP 탄화 / 에탄올 용액 → [[composite-cathode-mixing-routes]] |
| 장비 | ball mill · planetary(high-energy) ball mill · Thinky ARE-310 → [[mixing-equipment-ball-mill-thinky]] |

## 상태

- **2026-09-11** — 위키에 등록. 실험 진행 상태·지금까지의 최고 비용량은 아직 위키에 없다
  (미결 Q4). 상태가 바뀌면 이 절에 날짜와 함께 append 한다 (수치는 사본이며 정본은 실험 노트).

## 이 프로젝트가 답해야 할 질문

- [[reference-cell-500-600-mahg]] — 무엇이 500–600 을 막는가 (활성화? 퍼콜레이션? 입자? 단위?).
- [[one-step-vs-two-step-mixing]] — 혼합 순서가 활물질 이용률을 바꾸는가.

## 이 위키와의 관계

- 첫 ingest 논문 Kim et al. 2023 (`raw/papers/kim2023_…`)은 액체 전해질이지만 **같은 문제**
  (절연체 Li2S 의 활성화와 전자 네트워크)를 다룬다. 이식 가능한 것/불가능한 것의 표는
  digest §10 에 있고, 요지는 [[li2s-activation-first-charge]] 와
  [[carbon-dimensionality-electron-network]] 로 컴파일했다.
- 다음 ingest 후보(사용자 보유 논문 중): **ASSB Li2S 양극 논문** — 이것들이 들어와야
  "문헌의 500–600" 이 어떤 조건(조성·로딩·전압창·온도·압력)의 값인지 비교표(`/compare`)가 선다.

## 미결 (사용자 확인 필요)

- Q1 목표 용량의 단위 기준 · Q2 LPSCl 조성/공급원 · Q3 사이클 프로토콜(전압창 vs Li–In,
  C-rate, 온도, 스택 압력) · Q4 현재까지의 최고치와 그 혼합 경로.
