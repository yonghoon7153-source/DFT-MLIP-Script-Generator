---
title: "양극 코팅 계산 계보 — Wolverton → Ceder → Mo 라인과 우리 LPSCl 산화축의 관계"
date: 2026-09-11
updated: 2026-09-12
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
| 1 | **Aykol 2014** AENM `10.1002/aenm.201400690` — Thermodynamic Aspects of Cathode Coatings for LIB (Wolverton) | 액체전해질 LIB 코팅을 **4속성 열역학**(HF 포획 −ΔH_s-HF · Ω_V · Ω_G · **가역 Li 손실**)으로 형식화. 이원 산화물/불화물 **81쌍** 전수 DFT → 조합 설계도표. 계보의 뿌리 | **답: 아니다 — 우리 `oxidation_stability` 의 조상이 아니다.** μ 를 안 열고(닫힌계), 산물을 가정하며, **eV per HF** 로 정규화하고, 전압은 **평균 전환전압**이다. 우리 2.256 V 의 계보는 Mo/Ong/Ceder 2012 → [Zhu15] → [Xiao19]. 접점은 `V=−ΔH/ne` 변환(Aydinol/Ceder 1997)과 **U 계보(Wang2006)** 둘뿐 | ✅ `papers/aykol2014_cathode_coating_thermodynamics.md` (2026-09-11) |
| 2 | **Aykol 2016** Nat Commun 7:13779 `10.1038/ncomms13779` — *High-throughput computational design of cathode coatings for Li-ion batteries* (Aykol, Kim, Hegde, Snydacker, Lu, Hao, Kirklin, **Morgan**, **Wolverton**) | 1번을 **OQMD 기반 고속 스크리닝 + MOOP 다목적 최적화**로. 물리장벽 / HF-장벽 / HF-scavenger 세 역할로 후보를 가른다 | 스크리닝 판정 규칙(무엇을 '안정' 이라 부르나) · **csv 2개에 후보 랭킹·속성이 기계판독 형태로 다 있다** → 우리 스크리닝(③)의 문헌 대조표로 바로 쓸 수 있다 | ⏳ 대기 (본문 2026-09-12 수령) |
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

## Answer — #1 digest 가 답한 것 (2026-09-11)

> 아래는 **Aykol 2014 digest 에서 확정된 것**이고, 나머지 6편의 digest 가 나오면 각 편이 자기 몫을 채운다.

- **Q1 "안정" 의 조작적 정의** — 편마다 다르고, **#1 은 구간이 아예 아니다**:
  · **Aykol 2014** = **스칼라 문턱 2개** (`0.30 ≤ −ΔH_s-HF ≤ 1.50 eV HF⁻¹` **and** `V(MₓF) ≤ 3.0 V`). 닫힌계 0 K 반응엔탈피.
  · **Aykol 2016** = 같은 기호 `G_s-HF`, 같은 단위인데 **ΔG°(298 K) + 액체 H₂O·희박 HF 기준**이라 **값이 최대 2배 다르다**(Al₂O₃ 0.76 → 0.380). ⛔ 세대 혼용 금지.
  · **Xiao 2019** = 진짜 창 (`V_ox ≥ 4.0` & `V_red ≤ 2.7 V`, grand potential) + pseudo-binary `|ΔE_rxt| < 100 meV/atom`.
  · **우리** = grand-potential **개시 전압** (ox **2.256** / red **1.242 V**) + `interface_reactivity` **eV/atom**.
  ⇒ **우리 2.256 V 와 같은 양은 [Xiao19]/[Zhu15] 쪽이고, Aykol 두 편은 *다른 양*이다.**
- **Q2 기준** — Aykol 은 **vs Li/Li⁺**(금속 Li 기준 전환전압)이라 축 이름은 우리와 같지만 **DB 가 OQMD**(우리는 MP)이고 **평균 ≤ 개시**라 절대값 비교 불가. 순서 감각까지만.
- **Q3 액체/고체** — #1·#2 는 **액체 LiPF₆**, 적은 **HF**. 우리 계엔 HF 가 없다. 이식 가능한 것은 **문법 3개**뿐:
  ① 산물이 **상온 안정 고체**여야 보호가 된다 ② 코팅이 **가역 Li 를 먹으면 안 된다** ③ **평형 후에도 기능하나**(2016 Eq 5–6: 완전 반응한 Al₂O₃ 는 더 이상 HF-scavenger 가 아니다).
- **Q4 양극/음극** — #1 은 **양극 코팅**이 맞다(양극 5종의 HF 공격 엔탈피를 하한 게이트로 씀).
- 🔑 **우리 쪽 작업거리 2건**(추가 계산 0): `interface_reactivity` 산물에 **ⓐ 기체·저융점 상 표시 열**, **ⓑ Li 소모 몰수 열**. 근거는 digest §7c.

## Counter-arguments

- **"계보를 세워 봐야 우리 값은 우리 값이다."** — 맞다. 이 카드는 우리 값을 바꾸지 않는다.
  다만 원고에서 *"우리 onset 은 문헌의 코팅 안정성 기준과 같은 틀"* 이라고 쓰려면 그 문장이 참인지 확인해야 하고,
  그 확인이 이 카드의 용도다. (반박 병기: 확인 결과 **다른 틀**로 나오면 그 문장을 버리는 것이 결론이다.)
- **"리뷰(7·8)는 digest 가치가 낮다."** — 원 논문의 정의가 흩어져 있을 때 리뷰가 **정의를 한곳에 모아 둔다**.
  다만 리뷰의 수치는 2차 인용이라 **우리 db 에 값으로 넣지 않는다** — 정의·용어 확인용이다.

## Gap

- ~~Aykol 2016 본문이 없다~~ → **2026-09-12 수령** (12 p, `10.1038/ncomms13779`). 세트가 8편 중 7편 본문 확보.
- **Lu et al. "Superior Low-Temperature ASSB" 본문이 없다** (SI 만). 이 세트에 왜 들어왔는지도 미확인 —
  1저자에게 확인할 것.
- 우리 `oxidation_stability.json` 의 반응에너지 정의가 문서 어디에 적혀 있는지 아직 이 카드에 안 옮겼다.
- 8편 중 **6편**의 digest 가 아직 없다(#1 완료, #3 기존) — 순차 진행 중.

## 출처

- `litdb/inbox/106..113` (2026-09-11 수령, inbox 는 gitignore)
- `litdb/papers/xiao2019_cathode_coating_screening.md` (세트 중 유일한 기존 digest)
- `litdb/papers/zuo2022_chlorination_cathode_interface.md` (기준전극 혼용 사고의 선례)
- `db/properties/constrained_esw_cl_scan.json` · `db/properties/oxidation_stability.json`
