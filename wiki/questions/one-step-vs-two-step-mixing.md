---
title: One-step 일괄 ball milling 과 two-step(Li2S–C 선제작) 중 어느 쪽이 Li2S 이용률을 높이는가
description: "세 성분을 한 번에 가는가, Li2S–C 계면을 먼저 만들고 SE 를 나중에 붙이는가 — 같은 장비·같은 총 에너지에서 순서만 바꿨을 때 무엇이 달라지는가"
created: 2026-09-11
updated: 2026-09-11
type: research-question
tags: [mixing-process, composite-cathode, li2s, sulfide-electrolyte]
sources: [raw/transcripts/2026-09-11-li2s-wiki-kickoff-session.md, raw/papers/kim2023_reinforced-electrical-networking-high-loading-li2s-cathode.md]
confidence: low
explored: false
verificationStatus: unverified
claimType: empirical
evidenceScope: multi-source-mixed
status: open
feedsInto: "[[li2s-assb-reference-cell]] 의 혼합 공정 선택 · [[composite-cathode-mixing-routes]] 표의 결론 칸"
---

# One-step vs two-step 혼합

> [!question] Li2S·LPSCl·AB 를 **한 번에** ball milling 하는 것과, **Li2S–C 나노복합체를 먼저**
> 만든 뒤 LPSCl 을 mild mixing/BM 으로 더하는 것 중 어느 쪽이 pristine Li2S 의 이용률
> (첫 충전 활성화량·이후 비용량)을 높이는가? 그 차이는 **SE 보호** 때문인가 **Li2S–C 계면**
> 때문인가?

## 왜 중요한가

[[composite-cathode-mixing-routes]] 의 네 경로 중 셋(②③④)이 "Li2S–C 먼저, SE 나중" 구조다.
이 카드가 답하면 그 셋의 공통 전제가 서거나 무너진다. 또 one-step 이 이긴다면 공정이 가장
짧다는 실용적 이득이 있다.

## 가설

- **H1 (two-step 우세, 계면 이유)**: 탄소가 Li2S 를 먼저 감싸야 절연체 표면의 전자 접촉이 확보되고,
  SE 는 그 바깥에서 이온 경로만 맡는다 → [[carbon-dimensionality-electron-network]].
- **H2 (two-step 우세, SE 보호 이유)**: 고에너지 BM 이 LPSCl 을 손상(비정질화·전도도 저하·탄소와
  부반응)하므로 SE 를 고에너지 단계에서 빼는 것이 이득 — **이 위키에 근거 없음 (가설)**.
- **H3 (one-step 우세)**: 세 상을 나노 스케일로 동시에 섞어야 삼상 계면 밀도가 최대; two-step 의
  mild mixing 은 SE 를 Li2S–C 도메인 바깥에만 둔다.
- **H0 (차이 없음)**: 총 에너지가 같으면 순서는 무관.

## Evidence For

- **[2026-09-11] H1 방향의 액체계 선례 — Kim 2023.** 탄소 골격(Gr/CNT)을 용매 분산으로 먼저
  얽고 Li2S 와 BM 한 뒤 1 GPa 성형 → micro-Li2S(1–5 µm) 를 75 wt% 에서 `[도표]` ≈ 1150 mAh g⁻¹(S)
  로 활성화. 다만 **SE 가 없는 계**라 H2 와는 무관하고, BM 조건이 미기재라(G1) 에너지 비교도 불가.

## Evidence Against

- (아직 없음)

## 답하는 방법 (설계)

1. 같은 planetary BM, 같은 용기·볼·BPR·총 시간으로 (a) one-step, (b) Li2S+AB 먼저 → LPSCl 을
   같은 밀에서 짧게, (c) Li2S+AB 먼저 → LPSCl 을 Thinky 로 mild. 조건은
   [[mixing-equipment-ball-mill-thinky]] 양식으로 전부 기록.
2. 지표: 첫 충전 활성화량(mAh g⁻¹(Li2S)), 이후 비용량, 탄소+SE 펠릿 전자 전도도, SE 의 XRD/
   이온 전도도(H2 분리용).
3. H2 를 가르려면 **LPSCl 만** 같은 BM 조건에 노출한 뒤 이온 전도도를 재는 대조가 필요하다.

## Status Log
- [2026-09-11] open — 카드 개설. 근거는 액체계 선례 하나. ASSB 혼합 공정 논문 ingest 가 다음.
