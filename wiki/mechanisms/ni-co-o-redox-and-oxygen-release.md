---
title: Ni/Co/O redox 와 산소 방출 — 고전압에서 격자 산소가 관여하는가
description: "층상 산화물 양극의 고 SOC 에서 전이금속 redox 가 산소 redox·격자 산소 손실로 이어지는 배경, 황화물 SE 와 만났을 때의 특수성, 우리 DOE 에서의 판별 지표 (미검증 배경)"
created: 2026-09-11
updated: 2026-09-11
type: mechanism
tags: [lattice-oxygen, rock-salt, cutoff-voltage, mid-ni, post-mortem]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: low
explored: false
verificationStatus: unverified
claimType: theoretical
evidenceScope: synthesis-only
---

# Ni/Co/O redox 와 산소 방출

> [!note] 미검증 배경 — 이 페이지의 설명은 아직 근거 논문이 ingest 되지 않은 **일반 지식**이다. 인용 근거가 아니며, `/chat` 은 이를 "DB 외 일반 지식/추론" 으로 표시한다. 논문이 들어오면 `sources` 에 digest 를 추가하고 등급을 올린다.

## 정의
층상 Li(Ni,Co,Al/Mn)O₂ 계 양극에서 delithiation 이 깊어질수록 Ni³⁺→Ni⁴⁺(그리고 Co) 산화가 진행되고, 높은 SOC 에서는
전이금속 3d 와 O 2p 밴드의 겹침 때문에 **산소가 전하 보상에 참여**(산소 redox)한다는 것이 일반적인 설명이다.
그 극단이 **격자 산소의 손실**이며, 표면에서는 산소가 빠진 자리가 스피넬형·암염(rock-salt)형으로 재구성되고
([[interface-degradation-cathode-electrolyte-anode]]), 방출된 산소(또는 반응성 산소종)는 접해 있는 전해질을 산화한다.
황화물 SE 와 접한 경우 그 산화가 **sulfate/phosphate 형성**으로 나타날 수 있다는 것이 우리 질문의 핵심 연결고리다
([[lpscl-oxidative-decomposition-by-voltage]]).

## 왜 이 연구에서 중요한가
"4.4 V 고전압 구동" 이 논문의 전제이고, formation 4.6 V vs. Li/Li⁺ 수준은 격자 산소가 관여할 가능성이 가장 높은 조건이다.
격자 산소가 관여한다면 (a) 첫 충전 비가역 용량이 커지고, (b) 표면 rock-salt 층이 두꺼워지며, (c) CEI 에 산소 함유
황산염·인산염이 늘고, (d) 이후 사이클의 저항 성장이 빨라진다는 예측이 따라온다 —
[[lattice-oxygen-involvement-at-high-cutoff]] 카드가 이 예측들을 가설로 관리한다.

## 관측 지표
| 지표 | 측정 | 주의 |
|---|---|---|
| 표면 rock-salt 층 두께 | HAADF-STEM/FFT (사후) | 시료 준비 손상·빔 손상과 구분 |
| 산소 함유 CEI 종 | XPS O 1s·S 2p, ToF-SIMS depth profiling | 대기 노출 오염과 구분 |
| 격자 파라미터 변화 (c 축 수축) | XRD (사후, SOC 100 %) — operando 는 계획 없음 | H2–H3 와 겹침 ([[h2-h3-phase-transition-identification]]) |
| 첫 충전 고전압 비가역 용량 | dQ/dV, formation ICE | SE 산화 전하와 분리 불가 — 3-전극·LTO 셀로 보조 |
| 부피 변화 | operando 압력 (LTO 셀, 0.05C, 4.6 V 까지 — [[auxiliary-measurements]] A4) | 전압 기준 표기 필수 |

## formation cut-off 와의 관계 (가설)
- **H-O-a**: NCA721(mid-Ni) 은 4.4 V vs. Li/Li⁺ 까지는 격자 산소 관여가 제한적이고 4.6 V 에서 문턱을 넘는다 →
  4.6 V formation 셀만 뚜렷이 나쁘다.
- **H-O-b**: 반대로 mid-Ni 에서는 4.6 V 도 문턱 아래라 산소 축은 이 DOE 에서 **보이지 않는다** — 그러면 cut-off
  효과는 전부 SE 산화·CEI 축([[cei-formation-sulfide-cathode]])으로 설명된다.

## 근거 상태
- 위키에 근거 논문: **없음**.
- 투입 예정: "Dual-ion modification for high-voltage mid-Ni single-crystal cathode" · "High/Mid-Ni Nano Convergence
  modeling paper" · "Chemo-Mechanical Behavior of High- and Mid-Ni Cathodes in Sulfide-Based ASSBs".

## 관련
- [[mid-ni-vs-high-ni-degradation]] — Ni 함량이 이 문턱을 어떻게 옮기는가
- [[lattice-oxygen-involvement-at-high-cutoff]] — 열린 질문
