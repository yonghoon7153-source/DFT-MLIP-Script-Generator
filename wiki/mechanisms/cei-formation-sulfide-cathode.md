---
title: CEI 형성 — 황화물 전해질 복합양극의 cathode–electrolyte interphase
description: "NCA721 | LPSCl 계면에서 formation 중 생기는 CEI 의 정의, 무엇으로 관측하는가, formation cut-off 와의 가설적 관계 (미검증 배경)"
created: 2026-09-11
updated: 2026-09-11
type: mechanism
tags: [cei, lpscl-oxidation, sulfide-electrolyte, formation, post-mortem]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: low
explored: false
verificationStatus: unverified
claimType: theoretical
evidenceScope: synthesis-only
---

# CEI 형성 — 황화물 전해질 복합양극의 cathode–electrolyte interphase

> [!note] 미검증 배경 — 이 페이지의 설명은 아직 근거 논문이 ingest 되지 않은 **일반 지식**이다. 인용 근거가 아니며, `/chat` 은 이를 "DB 외 일반 지식/추론" 으로 표시한다. 논문이 들어오면 `sources` 에 digest 를 추가하고 등급을 올린다.

## 정의
CEI(cathode–electrolyte interphase)는 양극 활물질 표면과 전해질이 만나는 자리에 **전기화학적·화학적 반응으로
생긴 층**이다. 액체계의 CEI 와 달리 황화물 ASSB 에서는 (a) 고체전해질(LPSCl)의 **산화 분해 산물**
([[lpscl-oxidative-decomposition-by-voltage]])과 (b) 산화물 양극과 황화물 사이의 **화학 반응 산물**(황산염·인산염
계열, 전이금속 황화물)이 겹쳐 쌓이는 것으로 문헌이 설명한다. 이 층은 이온 전도가 낮아 **계면 저항**을 만들고,
두께·조성은 첫 충전(delithiation)의 상한 전위와 노출 시간에 좌우된다고 보고된다.

## 왜 이 연구에서 중요한가
formation 은 CEI 가 **처음 만들어지는** 구간이다. cut-off 가 다르면 첫 충전에서 SE 가 노출되는 최고 전위가 다르고,
따라서 초기 CEI 의 조성·두께가 달라질 수 있다. 우리 핵심 질문([[formation-cutoff-vs-long-term-degradation]])의
가설 H1 이 바로 "낮은 cut-off 로 만든 CEI 가 더 얇고 안정해 이후 4.4 V 사이클에서도 성장이 느리다" 이고,
반대 가설은 "어차피 main cycle 4.4 V 에서 다시 만들어지므로 formation 의 차이는 지워진다" 다.

## 관측 지표 (무엇을 재면 보이는가)
| 지표 | 측정 | 해석 시 주의 |
|---|---|---|
| 계면 저항 초기값·성장률 | EIS (2번째 main cycle SOC 100 %), 3-전극 DRT ([[auxiliary-measurements]]) | 접촉 손실과 겹친다 — [[contact-loss-vs-cei-growth-attribution]] |
| 표면 화학종 (S, P 산화 상태, sulfate/phosphate) | XPS (S 2p·P 2p), ToF-SIMS depth profiling | 수득 SOC·보관 조건에 민감; 기준전극 표기 없는 전압 비교 금지 |
| 층 두께·형태 | HAADF-STEM, FIB-SEM 단면 | 시료 준비 손상과 구분 |
| 비가역 용량 (formation 1→2 사이클) | 사이클 요약 (ICE, [[cell-data-module]]) | SE 산화 전하량은 비용량에 섞여 들어온다 |

## formation cut-off 와의 관계 (가설)
- **H-CEI-a**: cut-off ↑ → 첫 충전 CEI 두께 ↑ (SE 산화 전하량 ↑) → 초기 저항 ↑.
- **H-CEI-b**: 그러나 어떤 cut-off 이하에서는 CEI 가 **불완전**해서 main cycle 4.4 V vs. Li/Li⁺ 에서 뒤늦게 크게 자란다 —
  "pre-conditioning" 이라는 이름이 노리는 최적점이 여기 있을 수 있다.
- 판별: cut-off 별 formation ICE 와 2번째 main cycle EIS 를 나란히 놓고, 사후 XPS 의 sulfate/phosphate 비를 대응시킨다.

## 근거 상태
- 위키에 근거 논문: **없음** (이 페이지 전체가 미검증 배경).
- 투입 예정 논문 (제목 기준, 킥오프 기록 F12): "Interfacial degradation of the NMC/Li6PS5Cl composite cathode" ·
  "Engineering Stable Decomposition Products on Cathode Surfaces to Enable High Voltage" · "Decoupling first-cycle
  capacity loss mechanisms in sulfide SSBs" · "Li10GeP2S12/NCM622 interface stability" — 들어오면 이 페이지의
  `sources` 와 [[formation-cutoff-vs-degradation-literature]] 를 갱신한다.

## 관련
- [[lpscl-oxidative-decomposition-by-voltage]] — CEI 의 재료가 되는 SE 분해
- [[interface-degradation-cathode-electrolyte-anode]] — 세 계면 전체 지도
- [[formation-preconditioning-protocol]] — 이 층이 처음 생기는 구간
