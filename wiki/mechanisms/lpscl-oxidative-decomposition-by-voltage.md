---
title: LPSCl 산화 분해 — 전압대별 분해 산물
description: "Li6PS5Cl 이 양극 전위에서 산화될 때 문헌이 보고하는 산물(S, P2Sx, LiCl, sulfate/phosphate …)과 발생 전압대를 정리할 자리 — 지금은 미검증 배경, 논문이 들어오면 표를 채운다"
created: 2026-09-11
updated: 2026-09-11
type: mechanism
tags: [lpscl-oxidation, sulfide-electrolyte, cutoff-voltage, cei, units]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: low
explored: false
verificationStatus: unverified
claimType: theoretical
evidenceScope: synthesis-only
---

# LPSCl 산화 분해 — 전압대별 분해 산물

> [!note] 미검증 배경 — 이 페이지의 설명은 아직 근거 논문이 ingest 되지 않은 **일반 지식**이다. 인용 근거가 아니며, `/chat` 은 이를 "DB 외 일반 지식/추론" 으로 표시한다. 논문이 들어오면 `sources` 에 digest 를 추가하고 등급을 올린다.

## 정의
argyrodite Li6PS5Cl 은 열역학적으로 좁은 전기화학 창을 갖고, 양극 전위(수 V vs. Li/Li⁺)에서는 **산화 분해**가
일어난다고 문헌이 일관되게 보고한다. 산화는 주로 황(S²⁻)의 산화이며, 분해 산물로는 원소 황(S), 다황화물·P₂Sₓ
계열, LiCl, 그리고 산화물 양극과 접한 자리에서는 산소가 관여한 황산염(sulfate)·인산염(phosphate) 계열이
거론된다. 실제 분해가 **어느 전압대에서 어느 산물**로 진행되는지는 논문마다 측정법(XPS 깊이·ToF-SIMS·operando
XAS·전기화학 산화 전류)과 셀 구성(도전재 유무·전압 기준)에 따라 다르게 보고되므로, **이 페이지의 표는 논문
digest 에서 [인쇄] 값으로만 채운다**.

## 전압대별 산물 표 (채울 자리 — 아직 근거 없음)

| 전압대 (vs. Li/Li⁺ — 원문 기준 병기) | 보고된 산물 | 측정법 | 근거 (1저자 연도, Fig./page) |
|---|---|---|---|
| — | — | — | (논문 ingest 후 기입) |

규칙: 원문이 vs. Li-In 이나 vs. In/Li-In 으로 적었으면 **원문 값 + 기준을 그대로** 적고 변환값은 +0.62 V 를
병기한다 ([[voltage-reference-and-capacity-conventions]]). 도전재(카본) 유무는 산화 전류를 크게 바꾸므로 표에
적는다 — 우리 건식 복합양극의 도전재 조성은 아직 미기재(Q2).

## 왜 이 연구에서 중요한가
formation cut-off 6 수준(3.6–4.6 V vs. Li/Li⁺)은 곧 **SE 가 첫 충전에서 노출되는 최고 전위**의 6 수준이다.
4.6 V formation 셀은 main cycle 상한(4.4 V) 위 구간의 산화를 한 번 겪은 유일한 셀이다 ([[formation-cutoff-doe]]).
분해 산물의 종류가 전압대에 따라 달라진다면, cut-off 는 CEI 의 **조성**을 바꾸는 손잡이가 된다
([[cei-formation-sulfide-cathode]]).

## 관측 지표
- formation 충전 곡선의 **고전압 plateau/전류 꼬리** (CV 단계 전류, dQ/dV 의 비가역 봉우리) — 산화 전하량의 대리.
- 24 h rest 전압 강하 ([[auxiliary-measurements]] A2) — 계속되는 산화 부반응.
- 사후 XPS S 2p / P 2p (sulfate·phosphate·polysulfide 성분비), ToF-SIMS depth profiling.
- Raman (S–S, P–S 진동).

## formation cut-off 와의 관계 (가설)
- **H-SE-a**: 산화 전하량은 cut-off 에 대해 단조 증가하지만, **어느 문턱 위에서 급증**한다 (산물이 바뀌는 지점).
  그 문턱이 4.4 V vs. Li/Li⁺ 아래에 있으면 main cycle 만으로도 매번 겪는 것이고, 4.4–4.6 V 사이면 4.6 V 셀만 겪는다.
- **H-SE-b**: 일부 산물(예: 안정한 산화층)은 이후 산화를 **막는** 보호막으로 작동할 수 있다 — "Engineering Stable
  Decomposition Products…" 류의 논문이 이 가설의 근거 후보다.

## 근거 상태
- 위키에 근거 논문: **없음**.
- 투입 예정: "Engineering Stable Decomposition Products on Cathode Surfaces to Enable High Voltage" ·
  "Interfacial degradation of the NMC/Li6PS5Cl composite cathode" · "Li10GeP2S12/NCM622 interface stability"
  (LGPS 비교) · "Decoupling first-cycle capacity loss mechanisms in sulfide SSBs".

## 관련
- [[cei-formation-sulfide-cathode]] · [[ni-co-o-redox-and-oxygen-release]] (산소가 관여한 산물)
- [[formation-cutoff-vs-long-term-degradation]]
