---
title: 무엇이 reference cell 을 500–600 mAh g⁻¹ 에서 막는가
description: "pristine Li2S ASSB reference cell 이 문헌 수준(500–600, 기준 미확인)에 못 미친다면 병목은 활성화인가, 퍼콜레이션인가, 입자인가, 아니면 단위 착시인가"
created: 2026-09-11
updated: 2026-09-11
type: research-question
tags: [li2s, assb, activation, composite-cathode, units]
sources: [raw/transcripts/2026-09-11-li2s-wiki-kickoff-session.md, raw/papers/kim2023_reinforced-electrical-networking-high-loading-li2s-cathode.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: empirical
evidenceScope: multi-source-mixed
status: active
feedsInto: "[[li2s-assb-reference-cell]] 의 실험 설계 · [[anode-free-li2s-assb]] 의 Li 재고 상한"
---

# 무엇이 reference cell 을 500–600 mAh g⁻¹ 에서 막는가

> [!question] Li2S:LPSCl:AB = 30:50:20 pristine Li2S 셀에서 문헌 수준 500–600 mAh g⁻¹
> (기준 미확인) 을 재현하지 못한다면, 병목은 **첫 충전 활성화**인가, **전자/이온 퍼콜레이션**인가,
> **Li2S 입자 상태**인가, 아니면 **단위 정규화의 착시**인가?

## 왜 중요한가

이 답이 [[li2s-assb-reference-cell]] 의 다음 실험을 정하고, 활성화량은 곧
[[anode-free-li2s-assb]] 의 Li 재고 상한이다. 병목을 모르면 혼합 경로를 바꿔도
([[composite-cathode-mixing-routes]]) 무엇을 고쳤는지 모른다.

## 가설

- **H1 (활성화 제한)**: 첫 충전에서 Li2S 의 일부만 활성화되고, 활성화 안 된 몫은 뒤 사이클에서
  깨어나지 않는다 → 이후 용량 = 첫 충전 용량의 함수. [[li2s-activation-first-charge]].
- **H2 (퍼콜레이션 제한)**: AB 단일 탄소가 접촉 또는 두께 방향 네트워크 중 하나를 못 채우거나,
  탄소·SE 가 서로를 밀어내 삼상 계면이 부족 → [[carbon-dimensionality-electron-network]].
- **H3 (입자 제한)**: pristine Li2S 의 입자 크기·결정성이 커서 표면적이 부족; 나노화 정도가
  혼합 경로에 따라 다름.
- **H4 (단위 착시)**: 목표 500–600 이 `(S)` 기준인데 우리는 `(Li2S)` 기준으로 재고 있거나 그
  반대 → [[capacity-normalization-li2s-vs-sulfur]].

## Evidence For

- **[2026-09-11] H1 을 지지하는 액체계 선례 — Kim 2023 Fig. S1.** 첫 충전 용량을 25/50/75/100 %
  로 제한하자 이후 방전이 `[도표]` ≈ 270/530/730/930 mAh g⁻¹(S) 로 **20 사이클 동안 층 유지**.
  활성화 안 된 Li2S 는 안 깨어난다 (`raw/papers/kim2023_…` §9.1). 단 액체·Li 금속·LiNO3 조건.
- **[2026-09-11] H2 를 지지하는 액체계 선례 — Kim 2023 Fig. 4A/S4/5.** 접촉 탄소(Gr)와
  네트워크 탄소(CNT 3 wt%)를 나누자 활성화·수명이 함께 늘었고, 어느 하나만으로는 부족했다
  (CNT-only 는 활성화 실패, Gr-only 는 50 사이클 급사).
- **[2026-09-11] H4 는 사용자 진술 자체가 근거다** — 목표의 단위 기준이 명시되지 않았다
  (킥오프 기록 F4). Kim 2023 의 0.5 C 값도 (S) 기준 899.6 ↔ (Li2S) 기준 628 로 갈린다.

## Evidence Against

- (아직 없음) — 특히 **H3 에 대한 근거가 위키에 하나도 없다.** ASSB Li2S 논문 ingest 필요.

## 답하는 방법 (설계)

1. **H4 먼저** — 비용 0. 목표 값의 출처 논문을 가져와 분모를 확인한다.
2. **H1** — 우리 셀에서 Fig. S1 재현: 첫 충전을 25/50/75/100 % 로 끊고 이후 방전을 본다.
   층이 유지되면 H1; 뒤 사이클에서 따라 올라오면 활성화가 아니라 **동역학**(H2/H3) 이다.
3. **H2** — 탄소+SE 만의 펠릿 전자 전도도(두께 방향) 와 AB→AB+CNT(소량) 치환 비교.
4. **H3** — 혼합 경로별 Li2S 입도·XRD 를 [[mixing-equipment-ball-mill-thinky]] 양식으로 기록하고
   활성화량과 대응.

## Status Log
- [2026-09-11] active — 카드 개설. 근거는 Kim 2023(액체계) 하나와 사용자 진술뿐. 다음: ASSB
  Li2S 논문 ingest 로 H3 근거·목표 단위 확인.
