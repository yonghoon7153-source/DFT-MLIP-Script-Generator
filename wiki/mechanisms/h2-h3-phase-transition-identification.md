---
title: H2–H3 상전이 판별 분석법 — dQ/dV · XRD · 압력(부피) 응답
description: "Ni-rich 층상 양극의 고전압 H2→H3 전이를 무엇으로 판별하는가, mid-Ni NCA721 에서 4.4–4.6 V vs. Li/Li⁺ 안에 그 전이가 있는지 어떻게 확인하는가 (미검증 배경)"
created: 2026-09-11
updated: 2026-09-11
type: mechanism
tags: [h2-h3, crack, pressure, mid-ni, high-ni]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: low
explored: false
verificationStatus: unverified
claimType: theoretical
evidenceScope: synthesis-only
---

# H2–H3 상전이 판별 분석법

> [!note] 미검증 배경 — 이 페이지의 설명은 아직 근거 논문이 ingest 되지 않은 **일반 지식**이다. 인용 근거가 아니며, `/chat` 은 이를 "DB 외 일반 지식/추론" 으로 표시한다. 논문이 들어오면 `sources` 에 digest 를 추가하고 등급을 올린다.

## 정의
Ni-rich 층상 양극은 delithiation 이 깊어지면 H1→M→H2→H3 순의 상전이를 거치고, 마지막 **H2→H3** 전이에서 c 축
격자 파라미터가 **급격히 수축**해 입자 내부에 큰 변형·미세균열(microcrack)을 일으킨다는 것이 일반적인 설명이다.
전이 전압은 Ni 함량이 높을수록 낮아지고(따라서 사이클 창 안에 들어오고), mid-Ni 로 갈수록 전이가 약해지거나
창 밖(더 높은 전위)으로 밀린다고 보고된다. **NCA721 에서 4.4 V, 4.6 V vs. Li/Li⁺ 가 이 전이의 어느 쪽인지**는
우리가 직접 확인해야 할 사실이지 가정할 것이 아니다.

## 판별 분석법 (각각이 보는 것)
| 방법 | 신호 | 우리 실험에서의 자리 |
|---|---|---|
| **dQ/dV** (충전 곡선 미분) | 고전압 쪽의 뾰족한 산화 봉우리 (가역이면 방전에도 대응 봉우리) | formation·main cycle 데이터에서 바로 계산 ([[cell-data-module]]) — SE 산화의 비가역 꼬리와 구분해야 한다 |
| **XRD** (사후, SOC 100 %) | (003) 봉우리 이동 → c 축 수축; H3 상 공존 | operando 가 아니라 **한 시점**뿐 — 수득 SOC 정의 필수 (Q5) |
| **operando 압력** (LTO 셀, 0.05C, 4.6 V 까지) | 부피 수축이 스택 압력 응답의 기울기 변화로 | [[auxiliary-measurements]] A4 — 전압 기준 표기 필수 (LTO 는 vs. Li/Li⁺ 로 환산해 적는다) |
| FIB-SEM 단면 | 입자 내 균열 밀도 | 200 사이클 누적 결과 — 원인 귀속은 별도 |
| 3-전극 DRT | 전이 전후의 전하전달 저항 변화 | 정성 보조 |

## 왜 이 연구에서 중요한가
formation cut-off 6 수준 중 어느 수준부터 H2–H3 영역에 **처음 진입**하는지가 곧 "첫 충전에서 기계적 손상을
입혔는가" 의 경계다. 만약 4.6 V vs. Li/Li⁺ 만 그 영역에 들어간다면 4.6 V 셀의 열화는 CEI 축이 아니라 **chemo-mechanical
축**([[interface-degradation-cathode-electrolyte-anode]] · [[mechano-electrochemical-healing]])으로 먼저 의심해야 한다.

## formation cut-off 와의 관계 (가설)
- **H-PT-a**: NCA721 의 H2–H3 는 4.4 V vs. Li/Li⁺ 위, 4.6 V 아래에 있다 → 4.6 V formation 셀만 첫 충전에서 균열 씨앗을 얻는다.
- **H-PT-b**: mid-Ni 라 4.6 V 까지도 뚜렷한 전이가 없다 → dQ/dV·압력 응답에 봉우리가 없고, cut-off 효과는 표면 화학 축뿐이다.
- 판별의 첫 단계는 **비용 0**: 이미 있는 formation 충전 곡선의 dQ/dV 를 cut-off 별로 겹쳐 보는 것.

## 근거 상태
- 위키에 근거 논문: **없음**.
- 투입 예정: "Chemo-Mechanical Behavior of High- and Mid-Ni Cathodes in Sulfide-Based ASSBs" · "High/Mid-Ni Nano
  Convergence modeling paper" · "Dual-ion modification for high-voltage mid-Ni single-crystal cathode".

## 관련
- [[mid-ni-vs-high-ni-degradation]] · [[ni-co-o-redox-and-oxygen-release]] · [[formation-cutoff-doe]]
