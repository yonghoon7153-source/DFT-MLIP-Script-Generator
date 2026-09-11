---
title: Li2S ASSB 복합양극 (30:50:20)
description: "Li2S:LPSCl:AB = 30:50:20 복합양극의 설계 논리 — 전자·이온·활물질 삼상 퍼콜레이션, 액체 Li–S 양극(75:25)과의 차이, 전압창 제약"
created: 2026-09-11
updated: 2026-09-11
type: concept
tags: [li2s, assb, composite-cathode, sulfide-electrolyte, carbon]
sources: [raw/transcripts/2026-09-11-li2s-wiki-kickoff-session.md, raw/papers/kim2023_reinforced-electrical-networking-high-loading-li2s-cathode.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: mixed
evidenceScope: user-original
---

# Li2S ASSB 복합양극 (30:50:20)

## 정의

[[li2s-assb-reference-cell]] 이 쓰는 복합양극: **Li2S 30 · argyrodite LPSCl 50 · acetylene black
20 (wt%)**. 바인더 없이 분말을 혼합·압축한다. 액체 전해질 셀과 달리 **이온 경로도 고체(SE)
분말이 만들어야** 하므로, 양극 안에서 세 네트워크가 동시에 퍼콜레이션해야 한다:

| 네트워크 | 담당 | 이 조성에서 |
|---|---|---|
| 전자 (e⁻) | AB (20 wt%) | 절연체 Li2S(~10⁻¹³ S cm⁻¹, Kim 2023 도입부 인용)를 감싸야 한다 |
| 이온 (Li⁺) | LPSCl (50 wt%) | Li2S 입자 표면까지 SE 가 닿아야 한다 |
| 활물질 | Li2S (30 wt%) | 반응 계면 = Li2S / AB / LPSCl **삼중점** 근방 |

## 액체 Li–S 양극과 무엇이 다른가

Kim et al. 2023 (`raw/papers/kim2023_…`) 의 양극은 **Li2S 75 : 탄소 25**, 바인더 없이 1 GPa 펠릿.
전해질이 액체라 이온 경로를 양극 분말이 만들 필요가 없어 활물질을 75 % 까지 올릴 수 있었다.
우리는 그 25 % 자리가 아니라 **70 %** 를 비활물질(SE 50 + C 20)이 차지한다. 따라서:

- 같은 `mAh g⁻¹(Li2S)` 라도 **복합체 기준 비용량은 0.3 배**다 (600 mAh g⁻¹(Li2S) = 180 mAh g⁻¹(composite)).
  단위는 [[capacity-normalization-li2s-vs-sulfur]] 규율대로 적는다.
- 탄소의 역할은 같다(접촉 + 네트워크, [[carbon-dimensionality-electron-network]]) — 다만 탄소가
  SE 를 밀어내면 이온 경로가 끊긴다. Kim 2023 에서 CNT 과량이 활성화를 해친 것(Fig. S4)과
  **다른 이유**로 탄소 과량이 해로울 수 있다.
- **압축 성형**은 닮았다 (Kim 2023 은 1 GPa 5 min; 우리 펠릿 압력은 미기재 — 미결 Q3).

## 전압창 제약 (미검증 배경 — 근거 논문 ingest 필요)

Kim 2023 은 첫 충전을 **3.6 V vs Li/Li⁺** 까지 올려 활성화했다. 황화물 SE 는 그 전위에서
산화 분해되는 것으로 알려져 있으나 **이 위키에는 아직 그 근거 raw 가 없다** — 그래서 여기서는
"제약이 있을 수 있다" 까지만 적고, LPSCl 산화 한계·Li–In 기준전위(≈ +0.62 V vs Li/Li⁺) 는
논문 ingest 후 수치를 채운다. 결론: Kim 2023 의 활성화 프로토콜은 **그대로 옮길 수 없다**.

## 이 위키에서의 적용

- 혼합 순서·에너지에 따라 세 네트워크의 형성이 달라진다 → [[composite-cathode-mixing-routes]],
  [[one-step-vs-two-step-mixing]].
- 500–600 을 못 넘는 원인 후보(활성화 / 퍼콜레이션 / 입자 / 단위)는 [[reference-cell-500-600-mahg]].

## 한계·불확실성

- 조성 30:50:20 이 왜 그 값인지의 근거(문헌·선행 실험)가 위키에 없다.
- LPSCl 정확한 조성·입도, AB 의 종류(BET, 입경)가 미기재 — 미세구조 논의는 그것 없이는 정성적이다.
