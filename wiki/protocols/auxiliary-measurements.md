---
title: 보조 측정 — 24 h rest tracking · 3-전극 EIS/DRT · operando 압력 · 사후분석
description: "formation 효과의 메커니즘을 가르기 위한 보조 실험 목록 — 무엇을 어느 시점에 재고 어느 메커니즘 페이지로 보내는가 (사용자 진술 사본)"
created: 2026-09-11
updated: 2026-09-11
type: protocol
tags: [eis, reference-electrode, post-mortem, pressure, nca721]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
---

# 보조 측정

## 목적
[[formation-cutoff-doe]] 의 주 산출물(200 사이클 retention)만으로는 **왜** 달라졌는지 모른다. 아래 측정들이
각각 다른 메커니즘 축을 겨냥한다. 진행/계획 여부는 사용자 진술 기준이며 상태는 [[nca721-formation-project]] 에
날짜와 함께 갱신한다.

## 목록 (사용자 진술의 사본)

| # | 측정 | 시점·조건 | 겨냥하는 메커니즘 | 상태 |
|---|---|---|---|---|
| A1 | **EIS** (full cell) | main cycle 2번째 사이클 **SOC 100 %**, RT 로 옮겨 온도 평형 후 | 계면 저항의 초기값 — CEI·SE 분해층 ([[cei-formation-sulfide-cathode]]) vs 접촉 손실 ([[interface-degradation-cathode-electrolyte-anode]]) | 진행/계획 |
| A2 | **24 h rest 전압 tracking** | formation 직후 | 자가방전·이완 — 고전압 cut-off 후 SE 산화 부반응이 계속되는지 ([[lpscl-oxidative-decomposition-by-voltage]]) | 진행/계획 |
| A3 | **3-전극 셀 EIS/DRT** — NCA721 양극 \| Ag-C 음극 \| **Ag wire 기준전극** | formation 조건별 | 양극/음극 기여 분리 — 저항 증가가 양극 계면인지 음극인지 ([[contact-loss-vs-cei-growth-attribution]]) | 진행/계획 |
| A4 | **operando 압력** — Mid-Ni \|\| **LTO** 셀, **0.05C 로 4.6 V 까지 충전** | 첫 충전 | 부피 변화·상전이(H2–H3 여부) 와 압력 응답 ([[h2-h3-phase-transition-identification]]) | 진행/계획 |
| A5 | **사후분석** — 200 cycle 후 **SOC 100 %** 수득 양극: XRD · XPS · ToF-SIMS depth profiling · FIB-SEM · HAADF-STEM/FFT · Raman | main cycle 종료 후 | 표면 상(rock-salt), CEI 조성·두께, 균열/공극, 격자 산소 ([[ni-co-o-redox-and-oxygen-release]]) | 계획 |

⚠ A4 의 "4.6 V" 는 LTO 음극 셀의 **full-cell 전압인지 vs. Li/Li⁺ 환산값인지 미기재** — LTO 는 ≈1.55 V vs. Li/Li⁺ 의
평탄 전위를 가지므로(일반 지식, 미검증 배경) 어느 기준인지에 따라 양극 전위가 크게 달라진다. 기록 시 반드시
기준을 적는다 ([[voltage-reference-and-capacity-conventions]]).

## 각 측정이 답해야 할 질문
- A1·A3: 저항 증가의 **어느 부분이 어느 계면**인가 — DRT 의 시간상수 대역별 귀속은 기준전극 없이는 추정에
  머문다. 3-전극 결과가 full-cell EIS 해석의 기준이 된다.
- A2: cut-off 가 높을수록 rest 중 전압 강하가 큰가 — 크면 계속되는 산화 부반응 또는 SOC 재분포.
- A4: mid-Ni 에서 4.6 V vs. Li/Li⁺ 부근까지 압력(부피) 응답에 꺾임이 있는가 — 있으면 상전이/격자 수축의 지표.
- A5: cut-off 별로 CEI 조성(sulfate·phosphate·polysulfide 계열)과 두께가 단조 증가하는가, rock-salt 층 두께와
  균열 밀도는 어떤가 — [[mid-ni-vs-high-ni-degradation]] 의 비교 축과 같은 지표를 쓴다.

## 기록해야 할 것
- 모든 EIS: 주파수 범위, 진폭, SOC 정의, 온도 평형 시간. DRT: 정칙화 파라미터.
- 사후분석 시료: 셀 ID(registry), 수득 SOC, 해체 후 보관 조건(Ar, 시간).

## 관련
- [[formation-cutoff-doe]] · [[main-cycle-protocol]] · [[cell-registry]]
