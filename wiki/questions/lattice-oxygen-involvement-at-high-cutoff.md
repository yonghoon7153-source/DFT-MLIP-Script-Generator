---
title: 4.4–4.6 V vs. Li/Li⁺ formation 에서 NCA721 의 격자 산소가 관여하는가
description: "mid-Ni 에서 고전압 formation 이 산소 redox·산소 손실을 일으켜 CEI 에 산소 함유 종(sulfate/phosphate)을 남기는가, 아니면 그 문턱 아래인가"
created: 2026-09-11
updated: 2026-09-11
type: research-question
tags: [lattice-oxygen, cutoff-voltage, mid-ni, post-mortem, rock-salt]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: low
explored: false
verificationStatus: unverified
claimType: empirical
evidenceScope: user-original
status: open
feedsInto: "[[formation-cutoff-vs-long-term-degradation]] 의 H2/H4 판별 · 사후분석 계획"
---

# 4.4–4.6 V vs. Li/Li⁺ formation 에서 NCA721 의 격자 산소가 관여하는가

> [!question] formation cut-off 4.4 V 와 4.6 V vs. Li/Li⁺ 에서 NCA721 표면의 격자 산소가 전하 보상·산소 손실에
> 참여하고, 그 결과가 CEI 조성(sulfate/phosphate)·표면 rock-salt 두께·초기 비가역 용량으로 남는가?

## 왜 중요한가
사용자의 핵심 질문에 "lattice oxygen 관여" 가 명시돼 있다. 관여한다면 4.4 V vs. Li/Li⁺ main cycle 자체가 매 사이클 산소 축을
건드리는 것이고, 관여하지 않는다면 cut-off 효과는 SE 산화 축([[lpscl-oxidative-decomposition-by-voltage]])으로
좁혀진다. 두 경우의 pre-conditioning 설계가 다르다.

## 가설
- **H1**: 4.6 V vs. Li/Li⁺ 만 문턱을 넘는다 — 4.6 V 셀의 XPS O 1s / S 2p 에 산소 함유 황·인 종이 뚜렷하고 STEM 에 rock-salt 층이 두껍다.
- **H2**: 4.4 V vs. Li/Li⁺ 부터 이미 관여한다 — 4.4 V 와 4.6 V 가 비슷하게 나쁘고 4.2 V 이하와 갈린다.
- **H3**: mid-Ni 라 4.6 V vs. Li/Li⁺ 까지 관여가 미미하다 — 산소 관련 지표에 cut-off 의존성이 없다.

## Evidence For
- (아직 없음)

## Evidence Against
- (아직 없음)

## 답하는 방법 (설계)
1. 사후 XPS (O 1s, S 2p, P 2p) 와 ToF-SIMS depth profiling 을 cut-off 별로 — 대기 노출 통제.
2. HAADF-STEM/FFT 로 표면 재구성 층 두께 vs cut-off.
3. operando 압력(LTO 셀, 0.05C, 4.6 V 까지)의 고전압 응답 — 부피·가스 발생 힌트 (전압 기준 표기).
4. 관련 배경: [[ni-co-o-redox-and-oxygen-release]] · [[mid-ni-vs-high-ni-degradation]].

## Status Log
- [2026-09-11] open — 카드 개설. 문헌 근거 없음. 투입 예정 논문 중 "Dual-ion modification for high-voltage mid-Ni
  single-crystal cathode" 와 "Chemo-Mechanical Behavior…" 가 첫 근거 후보.
