---
title: formation 충전 cut-off 는 200 사이클 성능과 열화 메커니즘을 어떻게 바꾸는가
description: "핵심 질문 — 3.6–4.6 V vs. Li/Li⁺ formation cut-off 가 4.4 V main cycle 의 retention·저항 성장·CEI·SE 분해·격자 산소·접촉 손실을 어떻게 가르는가. 가설 H1–H5"
created: 2026-09-11
updated: 2026-09-11
type: research-question
tags: [formation, cutoff-voltage, nca721, cei, lpscl-oxidation, contact-loss]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: empirical
evidenceScope: user-original
status: active
feedsInto: "[[nca721-formation-project]] 의 논문 main concept (pre-conditioning 사이클 설계) · [[formation-cutoff-doe]] 해석"
---

# formation 충전 cut-off 는 200 사이클 성능과 열화 메커니즘을 어떻게 바꾸는가

> [!question] NCA721 건식 복합양극 | LPSCl | Li-In 셀에서 formation(0.1C/0.1C 2 cycles) 충전 cut-off 를
> 3.6 / 3.8 / 4.0 / 4.2 / 4.4 / 4.6 V vs. Li/Li⁺ 로 바꾸면, 2.5–4.4 V vs. Li/Li⁺ · 0.5C · 45 °C · 200 사이클의
> 성능(retention, 저항 성장, hysteresis)과 열화 메커니즘(CEI 형성, LPSCl 산화 분해, lattice oxygen 관여,
> 계면 contact loss)이 어떻게 달라지는가?

## 왜 중요한가
논문 main concept 의 후반부 — "메커니즘 기반 pre-conditioning 사이클 설계" — 가 성립하려면 cut-off 가 **메커니즘을
바꾼다**는 것과 **그 차이가 200 사이클 뒤에도 남는다**는 것을 둘 다 보여야 한다. 둘 중 하나라도 아니면 formation 은
설계 변수가 아니다.

## 가설
- **H1 (pre-designed CEI)**: 중간 cut-off(4.0–4.2 V vs. Li/Li⁺)가 얇고 안정한 CEI 를 먼저 만들어 main cycle 4.4 V 에서의 성장을
  늦춘다 → retention 이 **비단조**(중간 최적). [[cei-formation-sulfide-cathode]].
- **H2 (higher is worse, 단조)**: cut-off ↑ → SE 산화·격자 산소·접촉 손실 ↑ → retention 단조 감소.
  [[lpscl-oxidative-decomposition-by-voltage]] · [[ni-co-o-redox-and-oxygen-release]].
- **H3 (erased, 귀무)**: main cycle 4.4 V vs. Li/Li⁺ 가 매 사이클 계면을 다시 만들어 formation 이력이 지워진다 → 차이 없음.
- **H4 (chemo-mechanical 문턱)**: 4.6 V vs. Li/Li⁺ 만 큰 격자 수축/상전이 영역을 지나 균열 씨앗을 얻는다 → 4.6 V 만 뚜렷이 나쁨,
  나머지는 비슷. [[h2-h3-phase-transition-identification]].
- **H5 (healing 이 기계 축을 가린다)**: 100 MPa 구동압이 접촉 손실을 되돌려 **화학적 차이(CEI 조성)** 만 남는다 →
  retention 차이는 작지만 XPS/ToF-SIMS 에는 차이가 보인다. [[mechano-electrochemical-healing]].

## Evidence For
- (아직 없음 — 위키에 논문이 0편이고 실험 요약도 registry 가 비어 있다.)

## Evidence Against
- (아직 없음)

## 답하는 방법 (설계)
1. **비용 0**: 이미 있는 formation 충전 곡선의 dQ/dV 를 cut-off 별로 겹쳐 4.4–4.6 V 구간의 봉우리 유무를 본다 (H4 의 첫 판별).
2. formation ICE · 2 사이클 비가역 용량 vs cut-off (H1/H2 의 방향).
3. 2번째 main cycle EIS + 3-전극 DRT (양극/음극 분리) → 초기 저항의 cut-off 의존성 ([[contact-loss-vs-cei-growth-attribution]]).
4. 200 사이클 retention (분모 정의 고정) — H3 의 판정. n≥2/수준이 없으면 결론을 유보한다 ([[cell-registry]] 의 n).
5. 사후 XPS/ToF-SIMS/STEM — H5 의 판정 (retention 은 같은데 표면 화학이 다른가).

## Status Log
- [2026-09-11] active — 카드 개설. 근거는 사용자 진술뿐. 다음: 투입 예정 논문 10편 ingest 로 H1–H5 각각에 문헌 근거
  붙이기 ([[formation-cutoff-vs-degradation-literature]]); registry 채우고 dQ/dV 부터.
