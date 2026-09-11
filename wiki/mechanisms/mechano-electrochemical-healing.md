---
title: Mechano-electrochemical healing — 구동압 아래에서 계면 접촉이 되살아나는가
description: "황화물 SE 의 소성 변형과 스택 압력이 사이클 중 끊긴 양극/SE 접촉을 되돌린다는 개념, 우리 100 MPa 구동압 셀에서의 의미와 판별 지표 (미검증 배경)"
created: 2026-09-11
updated: 2026-09-11
type: mechanism
tags: [healing, contact-loss, pressure, sulfide-electrolyte, eis]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: low
explored: false
verificationStatus: unverified
claimType: theoretical
evidenceScope: synthesis-only
---

# Mechano-electrochemical healing

> [!note] 미검증 배경 — 이 페이지의 설명은 아직 근거 논문이 ingest 되지 않은 **일반 지식**이다. 인용 근거가 아니며, `/chat` 은 이를 "DB 외 일반 지식/추론" 으로 표시한다. 논문이 들어오면 `sources` 에 digest 를 추가하고 등급을 올린다.

## 정의
황화물 고체전해질(LPSCl 등)은 산화물 SE 보다 무르고 소성 변형이 쉬워, 스택 압력 아래에서 **활물질의 부피 변화로
생긴 틈을 SE 가 다시 메우는** 현상이 보고된다 — 이를 mechano-electrochemical healing 이라 부르는 문헌이 있다
(투입 예정 논문 제목 "Mechanoelectrochemical healing at NCM/LPSCl interfaces" 가 그 예). 반대 방향은
contact loss: delithiation 시 수축한 입자가 SE 와 떨어지고, lithiation 시 다시 팽창해도 완전히 붙지 않아 공극과
저항이 누적되는 것 ([[interface-degradation-cathode-electrolyte-anode]]).

## 왜 이 연구에서 중요한가
우리 셀은 **구동압 100 MPa** ([[cell-fabrication-conditions]])로 사이클한다 — healing 이 일어나기에 충분한지,
아니면 formation 에서 생긴 접촉 손실이 그대로 남는지가 cut-off 효과의 해석을 가른다. 만약 healing 이 강하면
formation 의 기계적 손상은 지워지고 남는 것은 **화학적 흔적(CEI 조성)** 뿐이다. 후순위의 **anode-free 저압
파우치셀**([[followup-high-ni-and-anode-free-pouch]])에서는 압력이 낮아 healing 이 약해질 것이므로 같은 formation
효과가 다르게 나타날 수 있다 — 압력을 비교표의 필수 열로 두는 이유.

## 관측 지표
| 지표 | 측정 | 해석 |
|---|---|---|
| 저항의 **가역** 성분 | 사이클 중 EIS 를 SOC 를 맞춰 반복 (SOC 100 % 기준) | 사이클마다 늘었다 줄면 접촉 축, 단조 증가면 CEI 축 — [[contact-loss-vs-cei-growth-attribution]] |
| 압력 응답 | operando 압력 (LTO 셀) — 충방전 비대칭·잔류 압력 | 부피 이력의 비가역 부분 |
| 단면 공극 | FIB-SEM (200 cycle) | 누적 결과; 압력 해제 후 시료 준비가 공극을 키울 수 있다 |
| hysteresis 추세 | 사이클 요약 (평균 충·방전 전압 차) | 접촉 손실과 CEI 모두 올린다 — 단독 근거 아님 |

## formation cut-off 와의 관계 (가설)
- **H-MH-a**: 높은 cut-off 로 첫 충전 수축이 클수록 초기 접촉 손실이 크지만 100 MPa 에서 대부분 회복된다 → 200 사이클
  retention 차이는 작다 (healing 이 cut-off 효과를 지운다).
- **H-MH-b**: 회복은 부분적이고, 첫 충전에서 생긴 공극 자리에 SE 산화물이 채워져 **영구 저항**이 된다 → cut-off 효과가 남는다.

## 근거 상태
- 위키에 근거 논문: **없음**.
- 투입 예정: "Mechanoelectrochemical healing at NCM/LPSCl interfaces" · "Chemo-Mechanical Behavior of High- and Mid-Ni
  Cathodes in Sulfide-Based ASSBs" · "Failure mechanisms of dry-processed thick electrodes".

## 관련
- [[interface-degradation-cathode-electrolyte-anode]] · [[cell-fabrication-conditions]] · [[auxiliary-measurements]]
