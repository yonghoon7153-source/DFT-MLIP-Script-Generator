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

## 계보 — 1저자가 한 세트로 올린 8편 + 별건 1편 (2026-09-11~12 수령)

> ⛔ 아래 **역할 배정은 첫 페이지·DOI·초록 수준의 읽기**로 쓴 것이다. 각 편의 digest 가 나오면
> 그 digest 가 이긴다 — 이 카드는 **작업 순서와 물어볼 질문**을 정하는 뼈대지 판정이 아니다.

| # | 논문 | 무엇을 세웠나 (잠정) | 우리와 닿는 곳 | litdb |
|---|---|---|---|---|
| 1 | **Aykol 2014** AENM `10.1002/aenm.201400690` — Thermodynamic Aspects of Cathode Coatings for LIB (Wolverton) | 액체전해질 LIB 코팅을 **4속성 열역학**(HF 포획 −ΔH_s-HF · Ω_V · Ω_G · **가역 Li 손실**)으로 형식화. 이원 산화물/불화물 **81쌍** 전수 DFT → 조합 설계도표. 계보의 뿌리 | **답: 아니다 — 우리 `oxidation_stability` 의 조상이 아니다.** μ 를 안 열고(닫힌계), 산물을 가정하며, **eV per HF** 로 정규화하고, 전압은 **평균 전환전압**이다. 우리 2.256 V 의 계보는 Mo/Ong/Ceder 2012 → [Zhu15] → [Xiao19]. 접점은 `V=−ΔH/ne` 변환(Aydinol/Ceder 1997)과 **U 계보(Wang2006)** 둘뿐 | ✅ `papers/aykol2014_cathode_coating_thermodynamics.md` (2026-09-11) |
| 2 | **Aykol 2016** Nat Commun 7:13779 `10.1038/ncomms13779` — *High-throughput computational design of cathode coatings for Li-ion batteries* (Aykol, Kim, Hegde, Snydacker, Lu, Hao, Kirklin, **Morgan**, **Wolverton**) | 1번을 **OQMD 13만종 고속 스크리닝 + MOOP**(weighted-sum + rank aggregation)로. **산물을 더 이상 가정하지 않는다**(hull 최소화). 역할 3분할: 물리장벽 / **HF-barrier(신설)** / HF-scavenger. HHI(공급위험) 축 신설. **Eq 4–6: 양극과 평형시킨 뒤에도 기능하나** | 🔑 **"안정"의 조작적 정의 확정** — `E_d` = **리튬화 개시**(평균 아님) · `E_c` = **액체로의 양이온 용출**(NBS 수용액 전위표) · 기준 vs Li/Li⁺ · DB **OQMD**. **csv 2본(속성 5,225행 + weighted-sum top-100×3)으로 깔때기·랭킹을 독립 재현**했고 `Fig. 1` 의 **숨은 필터 1개**를 찾아냈다 | ✅ `papers/aykol2016_ht_cathode_coating_design.md` (2026-09-12) |
| 3 | **Xiao 2019** Joule `10.1016/j.joule.2019.02.006` (Ceder × Samsung) | **SSB** 로 무대를 옮긴 첫 대규모 코팅 스크리닝 | 우리 계(황화물 SE)와 같은 무대 | ✅ `xiao2019_cathode_coating_screening.md` (474줄) |
| 4 | **Nolan 2019** ACS Energy Lett `10.1021/acsenergylett.9b01703` (Nolan/Liu/**Mo**, UMD) — *Solid-State Chemistries Stable with High-Energy Cathodes* | **"안정"을 *전압이 아니라* `E_d = 0` 불리언으로 형식화** — 유사이원 상호분해에너지(끝점 준안정성 제거, **eV/atom**) 의 최솟값이 0 인가를, **양극의 리튬화·탈리튬화 두 이산 상태 각각**에 대해. **자체 DFT 0회**, **Materials Project** 에너지 + 상평형 조합론. 양극 8상태 × 접촉 고체 236종 = **1,888 쌍** 전수 | 🔑🔑 **계보 8편 중 처음으로 우리 *두 양*을 둘 다 갖고 있다.** ① **E_d ↔ 우리 `interface_reactivity`(−0.3227 eV/atom)** = **같은 양 + 같은 구현**(pymatgen `InterfacialReactivity(use_hull_energy=True)`) ⇒ 그 값의 **1차 문헌 원전이 [Zhu16]→본 논문으로 확정** ② **anodic limit(`Fig. S7`·`S9`·`S10` 축) ↔ 우리 2.256 V** = 같은 grand-potential·같은 기준(vs Li/Li⁺) — **그러나 정의를 안 적고 값도 안 준다**([Zhu15] 인용 승계, boxplot figure-read 뿐) ⇒ **2.256 V 의 직계 원전은 여전히 [Zhu15]→Mo/Ong/Ceder 2012**, 본 논문은 **형제 적용** ⛔ Ed 데이터셋에 **황화물 0·염화물 0** — 우리 계는 목록에 **없다** | ✅ `papers/nolan2019_chemistries_stable_high_energy_cathodes.md` (2026-09-12) |
| 5 | **Nolan 2021** ENSM `10.1016/j.ensm.2021.06.027` (Mo × Wachsman) | **가넷** SE 용 코팅 — 산화물 계 | 계가 다르다(가넷 vs 황화물) — 방법만 전이 | ⏳ 대기 |
| 6 | **Honrao 2021** Sci Rep `10.1038/s41598-021-94275-5` | **해석가능 ML** + HT 다물성 스크리닝 (SSE·**음극** 코팅) | cascade 축의 방법 참고 · 양극 아님 | ⏳ 대기 |
| 7 | **Nolan/Zhu/He/Bai/Mo** — Computation-Accelerated Design (리뷰, 31 p) | 4·5 의 **방법 교과서** | 정의를 확인할 때 여기부터 | ⏳ 대기 |
| 8 | **Banerjee/Wang/Meng** — Understanding interface stability in SSB (*Nat. Rev. Mater.* `10.1038/s41578-019-0157-5`, 22 p · 1저자 Yihan Xiao) | 계면 안정성의 **실험·계산 통합 지도** | Cronk 2026(같은 Meng 그룹)과 이어진다 | ⏳ 대기 |
| **9** | **Lu 2024** *ACS Nano* **18, 7334−7345** — *Superior Low-Temperature ASSB Enabled by High-Ionic-Conductivity and Low-Energy-Barrier Interface* (Pushun Lu · Sheng Gong 공동1 … Hong Li, **Fan Wu\*** · IOP CAS) | ⚠ **축이 다르다** — 양극 코팅 설계가 아니라 **저온(−30 °C) ASSB 계면 동역학**. Ni90(LiNi₀.₉Co₀.₀₅Mn₀.₀₅O₂) + **Li₆PS₅Cl** 계면이 불안정 → CEI 나쁨 → Li⁺ 수송 느림. **Li₂ZrO₃ 코팅**으로 계면 Ea **60.19 → 41.39 kJ/mol**, **Li₃InCl₆ 할라이드 SE** 로 바꾸면 **25.79 kJ/mol** (÷96.485 = 0.624 → 0.429 → **0.267 eV**), −30 °C 용량유지 26.9 % | ⭐ **우리 계다** — comp1 과 같은 SE, 고Ni 양극 상대(Zuo 2023 과 같은 자리). ⛔ 이 Ea 는 **EIS 계면 전하이동** 이고 우리 0.180 eV 는 **벌크 Li 확산**이다 — 같은 표 금지, 방향·메커니즘만 소환값 | ⏳ 대기 (본문 2026-09-12 수령, zip 경로) |

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
  · **Aykol 2016** = **세 개의 다른 양을 한 프레임에 붙인 것**(#2 digest 2026-09-12 확정): ⓐ 열역학 = **OQMD hull 위 불리언** ⓑ 전기화학 = **구간처럼 보이지만 두 반응모델의 합성** — `E_d`(리튬화 **개시**, hull 첫 상영역 최고 계단) + `E_c`(**액체로의 양이온 용출**, NBS 수용액 표준산화전위 + 활동도 10⁻⁶) ⓒ `G_s-HF`(eV per HF).
    ⚠ `G_s-HF` 는 기호·단위가 #1 과 같지만 **ΔG°(298 K) + 액체 H₂O·희박 HF 기준**이라 값이 최대 2배 다르다(Al₂O₃ 0.76 → 0.380). ⛔ 세대 혼용 금지.
    ⚠ 그리고 **같은 논문 안에서도 정의가 갈린다**: 일반 MOOP 는 **절대 문턱**(`E_d<3`·`−E_c>3.5 V`), `Table 2` 는 **양극 상대 문턱 + ±0.12 V 버퍼** — `Table 2` 의 LiCoO₂ 최적 코팅은 **전원 일반 게이트 탈락**이다.
  · **Xiao 2019** = 진짜 창 (`V_ox ≥ 4.0` & `V_red ≤ 2.7 V`, grand potential) + pseudo-binary `|ΔE_rxt| < 100 meV/atom`.
  · **우리** = grand-potential **개시 전압** (ox **2.256** / red **1.242 V**) + `interface_reactivity` **eV/atom**.
  ⇒ **우리 2.256 V 와 같은 양은 [Xiao19]/[Zhu15] 쪽이고, Aykol 두 편은 *다른 양*이다.**
- **Q2 기준** — 두 편 다 **vs Li/Li⁺**, **DB 는 OQMD**(우리는 MP). ⚠ **"평균 ≤ 개시" 논거는 2014 에만 유효하다** — **2016 의 `E_d` 는 개시 전압**이다(#2 digest §6b).
  🔑 **그래서 판정이 두 갈래로 갈린다**: 🟢 **환원축** — `E_d` 는 우리 `reduction_limit_V`(**1.242 V**)와 **같은 종류의 양**(hull 첫 상영역 리튬화 개시) ⇒ #1 digest 의 판정이 **부분적으로 뒤집힌다**. 🔴 **산화축** — `E_c` 는 **양이온이 액체로 용출**되는 전위라 우리 **2.256 V** 와 **대응물이 없다**(용매가 없는 계) ⇒ #1 판정이 **더 강해진다**. **2.256 V 의 직계는 여전히 [Zhu15]/[Xiao19]**. 절대값 비교는 양축 모두 금지 — **정의 대조까지만**.
- **Q3 액체/고체** — #1·#2 는 **액체 LiPF₆**, 적은 **HF**. 우리 계엔 HF 가 없다. 이식 가능한 것은 **문법 3개**뿐:
  ① 산물이 **상온 안정 고체**여야 보호가 된다 ② 코팅이 **가역 Li 를 먹으면 안 된다** ③ **평형 후에도 기능하나**(2016 Eq 5–6: 완전 반응한 Al₂O₃ 는 더 이상 HF-scavenger 가 아니다).
- **Q4 양극/음극** — #1 은 **양극 코팅**이 맞다(양극 5종의 HF 공격 엔탈피를 하한 게이트로 씀).
- 🔑 **우리 쪽 작업거리 2건**(추가 계산 0): `interface_reactivity` 산물에 **ⓐ 기체·저융점 상 표시 열**, **ⓑ Li 소모 몰수 열**. 근거는 digest §7c.

## Answer — #4 digest 가 답한 것 (2026-09-12) ★ 계보 확정

- **Q1 "안정"의 조작적 정의** — **#4 = 스칼라 위의 불리언 `E_d = 0`**. 전압도 구간도 평균 전환전압도 아니다.
  `C_pb(x)=x·C_cat+(1−x)·C_contact`(1원자/f.u. 정규화) → 선형보간 에너지 → hull 과의 차 → **끝점 준안정성 제거** →
  **`E_d = min_x`**, 단위 **eV/atom**, 음수=반응성. 조건은 **양극 SOC 두 이산 상태 각각**(μ_Li 연속 스캔 아님).
  DB = **Materials Project** (⚠ [Aykol] 두 편의 OQMD 와 다르다). 0 K·PV 무시.
  ⛔ **[Aykol16] 의 `E_d`(단위 V)와 기호만 같고 단위부터 다르다.**
- **Q2 계보 — ★ 여기서 확정된다.** 이 편은 **우리 두 양을 둘 다** 갖고 있다:
  · 🟢 **헤드라인 `E_d` = 우리 `interface_reactivity`** — 식·정규화·부호·DB·**구현**(pymatgen `InterfacialReactivity(use_hull_energy=True)` 의 `get_kinks()` 최솟값)까지 일치.
    ⇒ **귀속이 세 층으로 정리된다: 형식화 [Rich16](Richards 2016, 이미 우리 원장에 등재) → *mutual*(끝점 준안정성 제거) 판 [Zhu16] → 양극 SOC 두 상태 전수 적용 [Nolan19]**. 우리는 `use_hull_energy=True` 를 쓰므로 **[Zhu16]/[Nolan19] 판**이다.
  · 🟡 **SI 의 anodic limit = 우리 2.256 V** — 같은 grand-potential, 같은 기준(vs Li/Li⁺). **그러나 이 논문은 정의를 적지 않고**(SI 참고문헌 3개로 [Zhu15]/[Zhu16] 인용 승계) **값도 XLSX 에 없다**(boxplot **figure-read** 뿐).
    ⇒ **2.256 V 의 직계 원전은 여전히 [Zhu15] → Mo/Ong/Ceder 2012 이고, [Nolan19] 는 그 계보의 *형제 적용*이다.**
  ⇒ **[Aykol] 두 편에 내린 "다른 양" 판정은 뒤집히지 않는다.** 가지에 [Nolan19] 가 **추가**될 뿐이고,
    *"Mo 그룹이니 전압축 본류일 것"* 이라는 사전 가설은 **절반만 맞았다** — Mo 본류는 맞지만 **이 편의 본론은 전압축이 아니라 계면 반응에너지축**이다.
- **Q3 무대** — 액체/고체를 가리지 않는 **접촉 고체 화학** 일반이다(#1·#2 의 HF 축도, #3 의 SSB 축도 아니다).
  ⛔ Ed 데이터셋 236종에 **황화물 0·염화물 0·티오인산염 0**. 염화물은 `Fig. S7`·`S8` boxplot 에만(자매논문 Wang *Angew* 2019 ref 63).
- **Q4 양극/음극** — **양극 코팅 + 고체전해질** 둘 다 대상으로 명시. 같은 그룹의 Li 금속 음극판(ref 27 Zhu 2017 질화물)은 별건.
- 🔑 **계보 카드가 #4–#7 에 물었던 것의 답**: **#4 는 [Aykol14] 의 *산물 물리상태 게이트*를 복원하지 않았다.**
  상평형 문자열에 **`O₂` 가 고체와 같은 자격**으로 빈번히 나온다(`LiNiO₂+B₂O₃ → O₂, Li₃B₇O₁₂, Ni₃BO₅` 등).
- 🔑 **#4 가 새로 지목한 우리 공백 2건**(추가 DFT 0~1):
  ① **우리는 양극 SOC 를 한 점(`LiCoO₂`)만 봤다** — 그들 전 데이터의 결론은 **탈리튬 상태가 병목**(Ed=0 비율 LCO 81 % → MNO 3 %).
  ② **`LiCoO₂` 프록시 caveat 의 방향 확정** — LCO 는 Ni-rich 대비 **반응성을 과소평가**한다(`Fig. S3` 로 LNO ≈ NMC111 ≈ NCA 검증됨).
- 🔑 **교차 관찰(우리 계산 + 그들 데이터)**: 우리 `LPSCl|LiCoO₂` 계면 산물 5종 중 **`Li₃PO₄`·`Li₂SO₄`** 가
  그들 데이터의 **양극 양립성 1·2위**다(`Li₂SO₄` 는 236종 중 **8/8 전 상태 안정 2종 중 하나**, `Li₃PO₄` 는 6/8).
  ⚠ `Li₂S`·`LiCl` 은 그들 축에서 **미평가** — 범위를 박고 쓴다.

## Counter-arguments

- **"계보를 세워 봐야 우리 값은 우리 값이다."** — 맞다. 이 카드는 우리 값을 바꾸지 않는다.
  다만 원고에서 *"우리 onset 은 문헌의 코팅 안정성 기준과 같은 틀"* 이라고 쓰려면 그 문장이 참인지 확인해야 하고,
  그 확인이 이 카드의 용도다. (반박 병기: 확인 결과 **다른 틀**로 나오면 그 문장을 버리는 것이 결론이다.)
- **"리뷰(7·8)는 digest 가치가 낮다."** — 원 논문의 정의가 흩어져 있을 때 리뷰가 **정의를 한곳에 모아 둔다**.
  다만 리뷰의 수치는 2차 인용이라 **우리 db 에 값으로 넣지 않는다** — 정의·용어 확인용이다.

## Gap

- ~~Aykol 2016 본문이 없다~~ → **2026-09-12 수령** (12 p, `10.1038/ncomms13779`). 세트가 8편 중 7편 본문 확보.
- ~~Lu 본문이 없다~~ → **2026-09-12 수령** (zip 으로 왔다 — PDF 직접 업로드는 계속 다른 파일 바이트가 도착했다).
  **세트 9편 전부 본문 확보.** ⚠ 다만 이 편은 축이 다르다(저온 계면 동역학) — 양극 코팅 계산 계보의 **8편과 나란히 놓지 않고** 별 행(#9)으로 둔다.
- 우리 `oxidation_stability.json` 의 반응에너지 정의가 문서 어디에 적혀 있는지 아직 이 카드에 안 옮겼다.
- 8편 중 **4편**의 digest 가 아직 없다(#1·**#2**·**#4** 완료, #3 기존) — 순차 진행 중(#5·#6·#7·#8 남음).
- ~~Aykol 2016 본문이 없다~~ → **#2 digest 완료(2026-09-12)**. 부수 소득: **CSV 2본의 스키마 확정 + 깔때기/랭킹 독립 재현**(우리 스크리닝 대조표에 `HHI_R`·`HHI_P` 열을 추가 계산 0 으로 붙일 수 있다).
- ~~**새로 생긴 물음**: #2 가 #1 의 **산물 물리상태 게이트**를 잃어버렸다. #4–#7(Mo 라인)이 복원하는지 확인할 것.~~
  → **#4 의 답 = 복원하지 않았다**(2026-09-12). `O₂` 가 고체와 같은 자격으로 상평형에 들어간다. **#5·#7 에서 다시 확인할 것.**
- **새로 생긴 물음 (2026-09-12, #4 digest 발)**: ① `Fig. S7`·`S8` 의 anodic/cathodic limit 원자료는 자매논문 **Wang/Bai/Nolan/Liu/Gong/Sun/Mo, *Angew* 2019, 58, 8039** 로 보인다 — **그 편이 Li–Cl/Li–Br 계의 grand-potential 창을 갖고 있어 우리 2.256 V 와 *직접* 비교 가능할 가능성이 높다**(세트 밖이지만 다음 우선순위 후보). ② **#7 리뷰(Nolan/Zhu/He/Bai/Mo *Joule* 2018)가 anodic limit 의 식을 적어 두었을 것** — #4 가 생략한 정의를 거기서 확정한다. ③ 우리 `−0.3227 eV/atom` 이 그들 데이터셋 **최악 구간**(−0.29…−0.53)에 해당하는데 이것이 *황화물이라서*인지 *hull 세대 차이*인지 — **대조 잡 1건**(같은 우리 코드로 `Li₃PO₄+LiCoO₂` 를 돌려 **0 이 나오는지**)으로 즉시 갈린다.

## 출처

- `litdb/inbox/106..113` (2026-09-11 수령, inbox 는 gitignore)
- `litdb/papers/xiao2019_cathode_coating_screening.md` (세트 중 유일한 기존 digest)
- `litdb/papers/zuo2022_chlorination_cathode_interface.md` (기준전극 혼용 사고의 선례)
- `db/properties/constrained_esw_cl_scan.json` · `db/properties/oxidation_stability.json`
