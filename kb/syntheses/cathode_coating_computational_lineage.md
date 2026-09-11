---
title: "양극 코팅 계산 계보 — Wolverton → Ceder → Mo 라인과 우리 LPSCl 산화축의 관계"
date: 2026-09-11
updated: 2026-09-11
tags: [litdb, lineage, cathode-coating, oxidation, interface, dft, screening]
status: 진행
confidence: medium
verificationStatus: unverified
explored: false
authoredBy: agent
effort: medium
claimType: mixed
evidenceScope: multi-source-primary
targetVenue: 
---

## Thesis

우리가 LPSCl 계열에 쓰는 **산화 onset(grand-potential) · 분해 산물 · 계면 반응에너지** 는 새로 만든 방법이 아니라
**2014→2021 양극 코팅 계산 문헌이 세운 틀의 한 적용**이다 — 그래서 이 계보를 정확히 세워야 우리 값이
*"같은 양의 다른 계 값"* 인지 *"다른 양"* 인지가 갈린다.

## 계보 — 1저자가 한 세트로 올린 8편 (2026-09-11 수령)

> ⛔ 아래 **역할 배정은 첫 페이지·DOI·초록 수준의 읽기**로 쓴 것이다. 각 편의 digest 가 나오면
> 그 digest 가 이긴다 — 이 카드는 **작업 순서와 물어볼 질문**을 정하는 뼈대지 판정이 아니다.

| # | 논문 | 무엇을 세웠나 (잠정) | 우리와 닿는 곳 | litdb |
|---|---|---|---|---|
| 1 | **Aykol 2014** AENM `10.1002/aenm.201400690` — Thermodynamic Aspects of Cathode Coatings for LIB (Wolverton) | 액체전해질 LIB 에서 코팅의 **열역학 조건**(HF·금속용출 억제). 계보의 뿌리 | 우리 `oxidation_stability` 의 반응에너지 틀이 여기서 왔는가 | ⏳ 진행 중 |
| 2 | **Aykol 2016** Nat Commun 13779 — HT computational design of cathode coatings | 1번을 **고속 스크리닝**으로 | 스크리닝 판정 규칙(무엇을 '안정' 이라 부르나) | ⛔ **본문 없음 — SI 만 올라왔다** |
| 3 | **Xiao 2019** Joule `10.1016/j.joule.2019.02.006` (Ceder × Samsung) | **SSB** 로 무대를 옮긴 첫 대규모 코팅 스크리닝 | 우리 계(황화물 SE)와 같은 무대 | ✅ `xiao2019_cathode_coating_screening.md` (474줄) |
| 4 | **Nolan 2019** ACS Energy Lett `10.1021/acsenergylett.9b01703` (Mo) | 고전압 양극과 **양립하는 고체 화학**의 목록화 | 우리 산화 onset 2.256 V 와 **같은 축** | ⏳ 대기 |
| 5 | **Nolan 2021** ENSM `10.1016/j.ensm.2021.06.027` (Mo × Wachsman) | **가넷** SE 용 코팅 — 산화물 계 | 계가 다르다(가넷 vs 황화물) — 방법만 전이 | ⏳ 대기 |
| 6 | **Honrao 2021** Sci Rep `10.1038/s41598-021-94275-5` | **해석가능 ML** + HT 다물성 스크리닝 (SSE·**음극** 코팅) | cascade 축의 방법 참고 · 양극 아님 | ⏳ 대기 |
| 7 | **Nolan/Zhu/He/Bai/Mo** — Computation-Accelerated Design (리뷰, 31 p) | 4·5 의 **방법 교과서** | 정의를 확인할 때 여기부터 | ⏳ 대기 |
| 8 | **Banerjee/Wang/Meng** — Understanding interface stability in SSB (리뷰, 22 p) | 계면 안정성의 **실험·계산 통합 지도** | Cronk 2026(같은 Meng 그룹)과 이어진다 | ⏳ 대기 |

**흐름 한 줄**: 액체전해질 코팅 열역학(1) → 고속 스크리닝(2) → **고체전해질로 이식**(3) → 고전압 양극 양립성 목록(4)
→ 계 확장(5, 가넷) · 방법 확장(6, ML) · 교과서화(7·8).

## Argument — 이 세트를 먹일 때 **반드시 물어야 할 것 넷**

1. **"안정" 의 조작적 정의가 편마다 같은가.** hull 위 거리 · 반응에너지 ΔE_rxn · 전압창 · grand-potential onset 은
   이름이 비슷하고 **값이 다르다**. 우리 `constrained_esw_cl_scan.json` 의 2.256 V 가 이들 중 **어느 정의**와 같은
   양인지 확정해야 인용이 성립한다. (Zuo 2023 에서 이미 겪었다 — 그쪽 CV 창이 vs In/InLi 라 우리 값이 창 아래 0.34 V 였다.)
2. **기준 전극·화학 퍼텐셜 기준.** vs Li⁺/Li · vs In/InLi · μ_Li 기준. 섞으면 바로 틀린다.
3. **무대가 액체인가 고체인가.** 1·2 는 액체 LIB 다. 우리 계는 황화물 SE 다. 같은 수식을 써도 **막으려는 실패 모드**
   (HF 용출 vs 계면 분해층)가 다르다.
4. **양극 코팅인가 음극 코팅인가.** 6 은 음극 코팅이다 — 1저자 요청은 *"양극 관련"* 이었으므로 그 사실을 적고 분류한다.

## Counter-arguments

- **"계보를 세워 봐야 우리 값은 우리 값이다."** — 맞다. 이 카드는 우리 값을 바꾸지 않는다.
  다만 원고에서 *"우리 onset 은 문헌의 코팅 안정성 기준과 같은 틀"* 이라고 쓰려면 그 문장이 참인지 확인해야 하고,
  그 확인이 이 카드의 용도다. (반박 병기: 확인 결과 **다른 틀**로 나오면 그 문장을 버리는 것이 결론이다.)
- **"리뷰(7·8)는 digest 가치가 낮다."** — 원 논문의 정의가 흩어져 있을 때 리뷰가 **정의를 한곳에 모아 둔다**.
  다만 리뷰의 수치는 2차 인용이라 **우리 db 에 값으로 넣지 않는다** — 정의·용어 확인용이다.

## Gap

- **Aykol 2016 본문이 없다** (SI·csv 만). 스크리닝 판정 규칙이 본문에 있을 가능성이 크다 → 본문 PDF 필요.
- **Lu et al. "Superior Low-Temperature ASSB" 본문이 없다** (SI 만). 이 세트에 왜 들어왔는지도 미확인 —
  1저자에게 확인할 것.
- 우리 `oxidation_stability.json` 의 반응에너지 정의가 문서 어디에 적혀 있는지 아직 이 카드에 안 옮겼다.
- 8편 중 7편의 digest 가 아직 없다 — 순차 진행 중.

## 출처

- `litdb/inbox/106..113` (2026-09-11 수령, inbox 는 gitignore)
- `litdb/papers/xiao2019_cathode_coating_screening.md` (세트 중 유일한 기존 digest)
- `litdb/papers/zuo2022_chlorination_cathode_interface.md` (기준전극 혼용 사고의 선례)
- `db/properties/constrained_esw_cl_scan.json` · `db/properties/oxidation_stability.json`
