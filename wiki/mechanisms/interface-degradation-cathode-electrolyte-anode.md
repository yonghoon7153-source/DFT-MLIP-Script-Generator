---
title: 계면 열화 지도 — 양극/전해질/음극 세 계면에서 무엇이 어떻게 나빠지는가
description: "NCA721 | LPSCl | Li-In 셀의 세 계면(양극–SE, SE 벌크·입계, SE–음극)에서 보고되는 열화 형태(CEI·rock-salt·균열/공극·contact loss·음극 계면)를 한 지도로 (미검증 배경)"
created: 2026-09-11
updated: 2026-09-11
type: mechanism
tags: [contact-loss, crack, rock-salt, anode-interface, cei, dry-electrode]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: low
explored: false
verificationStatus: unverified
claimType: theoretical
evidenceScope: synthesis-only
---

# 계면 열화 지도 — 양극/전해질/음극

> [!note] 미검증 배경 — 이 페이지의 설명은 아직 근거 논문이 ingest 되지 않은 **일반 지식**이다. 인용 근거가 아니며, `/chat` 은 이를 "DB 외 일반 지식/추론" 으로 표시한다. 논문이 들어오면 `sources` 에 digest 를 추가하고 등급을 올린다.

## 정의
황화물 ASSB 펠릿 셀의 저항 성장은 한 곳에서 오지 않는다. 문헌이 나누는 자리는 셋이다.

| 계면 | 열화 형태 (문헌의 일반적 서술) | 우리 셀에서의 특수성 |
|---|---|---|
| **양극 활물질 – SE** | CEI 형성([[cei-formation-sulfide-cathode]]) · SE 산화([[lpscl-oxidative-decomposition-by-voltage]]) · 표면 rock-salt 재구성([[ni-co-o-redox-and-oxygen-release]]) · 부피 변화에 따른 contact loss / 공극 · 입자 균열([[h2-h3-phase-transition-identification]]) | 건식 복합양극 2 mAh cm⁻² — 바인더·도전재 조성 미기재(Q2). 두꺼운 건식 전극은 두께 방향 불균일이 실패 원인이 될 수 있다 (투입 예정 "Failure mechanisms of dry-processed thick electrodes") |
| **SE 층 (벌크·입계)** | 입계 저항, 덴드라이트(Li 금속 음극일 때), 압력 이력 | Li-In 음극이라 덴드라이트 축은 약함; 462 MPa 성형 |
| **SE – 음극 (Li-In)** | Li-In 은 Li 금속보다 SE 환원 분해가 완만하다고 보고되나, 합금 조성·전류밀도에 따라 계면 저항·공극이 생긴다 | In 9Φ + Li 4Φ 의 국소 조성 불균일 가능성; 3-전극(Ag-C \| Ag wire) 셀로 양극/음극 기여를 분리 ([[auxiliary-measurements]] A3) |

## 왜 이 연구에서 중요한가
formation cut-off 는 **양극–SE 계면**에만 작용하는 변수처럼 보이지만, full-cell 저항에는 음극 계면 변화도 섞여
들어온다. cut-off 별 차이를 양극 계면 탓으로 돌리려면 음극 기여가 cut-off 와 무관함을 **먼저** 보여야 한다 —
3-전극 EIS/DRT 가 그 대조군이고, [[contact-loss-vs-cei-growth-attribution]] 카드가 그 논리를 관리한다.

## 관측 지표 요약
- 계면별 저항: 3-전극 DRT (양극 vs 음극), full-cell EIS 의 사이클 추세.
- 형태: FIB-SEM 단면 (공극·균열·박리), HAADF-STEM (표면 상).
- 화학: XPS·ToF-SIMS (CEI), Raman.
- 기계: operando 압력 (부피 이력), healing 여부 ([[mechano-electrochemical-healing]]).

## formation cut-off 와의 관계 (가설)
- 낮은 cut-off (3.6–3.8 V vs. Li/Li⁺): 첫 충전 수축이 작아 접촉 손실은 작지만 CEI 가 덜 형성 → main cycle 4.4 V 에서
  뒤늦은 CEI 성장 + 접촉 손실 동시 발생.
- 높은 cut-off (4.4–4.6 V vs. Li/Li⁺): 첫 충전에서 CEI·접촉 손실이 함께 크게 생기고, 이후 안정화(또는 healing)될지 여부가 관건.
- 중간 (4.0–4.2 V vs. Li/Li⁺): "충분한 CEI, 작은 기계적 손상" 의 최적점이 있을 수 있다 — DOE 의 기대 결과 형태.

## 근거 상태
- 위키에 근거 논문: **없음**.
- 투입 예정: "Interfacial degradation of the NMC/Li6PS5Cl composite cathode" · "Failure mechanisms of dry-processed
  thick electrodes" · "Chemo-Mechanical Behavior of High- and Mid-Ni Cathodes in Sulfide-Based ASSBs" ·
  "Decoupling first-cycle capacity loss mechanisms in sulfide SSBs".

## 관련
- [[cell-fabrication-conditions]] · [[formation-cutoff-vs-long-term-degradation]] · [[mid-ni-vs-high-ni-degradation]]
