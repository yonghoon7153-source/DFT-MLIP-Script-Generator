---
title: 저항 증가를 접촉 손실과 CEI 성장 중 어디에, 양극과 음극 중 어디에 귀속할 것인가
description: "full-cell EIS 의 저항 성장을 3-전극 DRT·압력 응답·사후 형태로 분해해 formation cut-off 효과의 자리를 찾는 방법론 질문"
created: 2026-09-11
updated: 2026-09-11
type: research-question
tags: [eis, reference-electrode, contact-loss, cei, healing]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: low
explored: false
verificationStatus: unverified
claimType: empirical
evidenceScope: user-original
status: open
feedsInto: "[[formation-cutoff-vs-long-term-degradation]] 의 H1/H5 판별 · [[auxiliary-measurements]] A1·A3 설계"
---

# 저항 증가를 접촉 손실과 CEI 성장 중 어디에, 양극과 음극 중 어디에 귀속할 것인가

> [!question] cut-off 별 full-cell 저항 차이(2번째 main cycle SOC 100 % EIS)가 (a) 양극–SE 계면의 CEI 성장인지
> (b) 부피 변화에 따른 접촉 손실인지 (c) Li-In 음극 계면인지를, 3-전극(Ag-C | Ag wire) DRT · 압력 응답 ·
> 사후 단면으로 분리할 수 있는가?

## 왜 중요한가
귀속 없이는 "cut-off 가 CEI 를 바꿨다" 는 문장이 성립하지 않는다. 특히 Li-In 음극 계면이 cut-off 와 무관하게
사이클마다 변한다면 full-cell 저항 차이의 일부는 잡음이다 ([[interface-degradation-cathode-electrolyte-anode]]).

## 가설
- **H1**: 3-전극 DRT 에서 양극 쪽 시간상수 대역만 cut-off 에 따라 움직인다 (음극은 불변) → 귀속 가능.
- **H2**: 접촉 손실 성분은 SOC 를 맞춘 반복 EIS 에서 **가역**으로, CEI 성분은 단조 증가로 갈린다
  ([[mechano-electrochemical-healing]]).
- **H3**: 두 성분의 시간상수가 겹쳐 DRT 로는 못 가른다 → 사후 단면(FIB-SEM 공극)과 XPS(CEI) 의 조합만이 답이다.

## Evidence For
- (아직 없음)

## Evidence Against
- (아직 없음)

## 답하는 방법 (설계)
1. 3-전극 셀에서 formation 조건 2~3개(예: 3.8 · 4.2 · 4.6 V)를 골라 양극/음극 EIS 를 따로 얻고 DRT 를 계산한다.
2. full-cell 2번째 사이클 EIS 와 같은 SOC·온도 조건으로 맞춘다 (RT 평형 시간 기록).
3. 사후 FIB-SEM 공극 분율 vs EIS 저항 — 상관이 있으면 접촉 축, 없으면 CEI 축.
4. 배경: [[cei-formation-sulfide-cathode]].

## Status Log
- [2026-09-11] open — 카드 개설. 3-전극 셀 결과 없음.
