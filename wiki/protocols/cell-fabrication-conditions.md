---
title: 셀 제작 조건 — NCA721 건식 복합양극 | LPSCl | Li-In (10Φ 몰드)
description: "표준 펠릿 셀의 제작·가압 조건 — 양극+SE 462 MPa 2.5 min, 음극(In 9Φ + Li 4Φ) 277 MPa 5 min, 구동압 100 MPa (사용자 진술 사본)"
created: 2026-09-11
updated: 2026-09-11
type: protocol
tags: [nca721, sulfide-electrolyte, dry-electrode, pressure, anode-interface]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
---

# 셀 제작 조건

## 목적
모든 DOE 셀이 공유하는 **고정 조건**의 정의. 논문과 비교할 때 가장 먼저 짚어야 할 차이(제작압·구동압·loading·
음극 종류)가 여기 있다 — [[formation-cutoff-vs-degradation-literature]] 의 비교 축이기도 하다.

## 조건 (사용자 진술의 사본 — 정본은 실험 노트·registry)

| 항목 | 값 | 비고 |
|---|---|---|
| 양극 | **NCA721** 건식(dry-processed) 복합양극, **2 mAh cm⁻² 기준** | 조성비(NCA721 : LPSCl : 도전재 : 바인더)·mg cm⁻² 로딩은 미기재 (Q2) |
| 고체전해질 | argyrodite **LPSCl (Li6PS5Cl)** | |
| 음극 | **Li-In 합금** — In foil 9Φ + Li foil 4Φ | Li/In 몰비·두께 미기재 (Q3) |
| 몰드 | **10Φ** | |
| 양극 + 전해질 가압 | **462 MPa · 2.5 min** | 제작압 (fab pressure) |
| 음극 가압 | **277 MPa · 5 min** | 제작압 |
| 구동압 | **100 MPa** | operating (stack) pressure — 사이클 중 유지 |

## 절차
1. 10Φ 몰드에 LPSCl 층을 성형하고 그 위에 건식 복합양극을 얹어 **462 MPa 에서 2.5 min** 가압한다.
2. 반대면에 In foil(9Φ) 을 놓고 Li foil(4Φ) 을 얹어 **277 MPa 에서 5 min** 가압해 Li-In 합금 음극을 만든다.
3. 셀 홀더에서 **100 MPa** 구동압으로 고정하고 [[formation-preconditioning-protocol]] 로 넘어간다.

## 기록해야 할 것 (registry 열과 대응 — [[cell-registry]])
- 활물질 질량(mg) — 전극 질량과 구분한다. 파일명의 질량은 제안값일 뿐이다.
- 펀칭 지름, 제작압(양극/음극), 구동압, 제작일, 배치(LPSCl lot·NCA721 lot).
- 압력은 **제작압과 구동압을 반드시 구분**한다 — 논문 비교표의 `pressure_fab_mpa` / `pressure_op_mpa`
  두 필드가 그래서 따로 있다.

## 왜 압력이 축인가 (배경 — 근거 논문 없음)
> [!note] 미검증 배경 — 근거 논문이 ingest 되기 전에는 인용 근거가 아니다.

황화물 ASSB 의 복합양극은 액체 전해질이 없어 **입자 간 고체 접촉이 곧 이온 경로**다. 충방전 중 활물질의
부피 변화로 접촉이 끊기면 저항이 오르고([[interface-degradation-cathode-electrolyte-anode]]), 충분한 구동압은
그 손실을 일부 되돌린다는 보고가 있다([[mechano-electrochemical-healing]]). 따라서 같은 cut-off 라도 구동압이
다른 논문의 결과를 우리 100 MPa 셀에 그대로 옮길 수 없다.

## 관련
- [[formation-preconditioning-protocol]] · [[main-cycle-protocol]]
- [[nca721-formation-project]] — 프로젝트 카드 (`ours:` 블록의 정본은 이 페이지)
