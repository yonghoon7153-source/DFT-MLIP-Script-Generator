---
title: "Natterer et al. 2026 — Modeling and half-cell-resolved measurement of the influence of cell degradation on the anode potential of high-energy lithium-ion cells (JPS 678, 240036)"
source_url: local-upload/08e897b2-Modeling_and_halfcellresolved_measurement_of_the_influence_of_cell_degradation_on_the_anode_potential_of_highenergy_lithiumion_cells.pdf
ingested: 2026-09-10
sha256: 6a1ae22e0eb1b8930ca0fd4210ce7d2f51f85b5776cec53ded70d6ade8cc1e6d
---

# 수집 목적

J. Natterer, F.F. Oehler, S. O'Kane, M. Marinescu, G.J. Offer, A. Jossen,
**"Modeling and half-cell-resolved measurement of the influence of cell
degradation on the anode potential of high-energy lithium-ion cells"**,
*Journal of Power Sources* **678** (2026) 240036 의 **절별 해체분석**.

이 저장소가 이 논문을 흡수하는 이유는 저자들의 연구 질문(노화가 anode potential 을
어떻게 움직이는가 → 리튬 도금 회피)이 아니라, **그 질문에 답하기 위해 저자들이
만든 도구** 때문이다. 네 가지가 우리 축에 정면으로 걸린다:

1. **기준전극(LTO-RE)으로 1000 사이클 동안 half-cell 전위를 in-situ 로 측정**했다.
   즉 전극별 열화를 **full-cell 곡선 fitting 없이** 읽는다 — 우리가 "손으로 맞춘
   α·β 가 맞는지" 를 검증할 때 필요한 **독립 근거의 형태**가 여기 있다.
2. **DMA 에서 수치 최적화를 아예 뺐다.** `[인쇄, §3.1]` "This approach **eliminates
   numerical fitting procedures** by directly utilizing in-situ half-cell data".
   LLI·LAM_neg·LAM_pos 가 **peak tracking 산술 4식**으로만 나온다. 최적화가 없으면
   [[fitting-degeneracy]] 의 "골짜기에서 미끄러지는" 통로 자체가 없다.
3. 그런데 **그 결과값 세 개가 서로 거의 같다** (500 EFC 에서 LAM_neg ≈ 8.2 %,
   LAM_pos ≈ 8.1 %, LLI ≈ 9.3 % — `[도표, Fig. 6a–c]`). 이것은
   [[np-lip-ocv-reparametrization]] 이 닫힌 형태로 지목한 **full-cell OCV 의 null
   방향** 바로 위다. 즉 **full-cell 곡선만으로는 원리적으로 거의 안 보이는 상태를
   기준전극이 실제로 분해해 낸 사례**다.
4. 모델이 **PyBaMM 24.1 + DFN + O'Kane 열화 파라미터 세트**다 — 우리 파이프라인과
   같은 계보의 코드이고, 공저자에 O'Kane 본인이 있다.

**표기 규칙** (이 위키 관례 3구분 + 1):
- `[인쇄]` — 논문 본문/식/표에 글자로 있는 것
- `[도표]` — 그림에서 눈으로 읽은 근사값 (**원 데이터가 아니다**)
- `[해석]` — 이 문서를 쓰면서 붙인 판단. **논문의 주장이 아니다**
- `[재현]` — 원문 값을 이 세션에서 산술로 옮긴 것 (계산식을 함께 적는다)

- 원본 파일: 로컬 업로드 PDF (저장소에 바이너리를 넣지 않는다)
- 크로핑 그림: `raw/figures/natterer2026_re-halfcell-anode-potential-aging/`
  (fig 8장 + tab 1장을 도구가 뽑았고, **부록 Fig. A.1 / A.2 는 도구의 캡션 정규식이
  `Fig. A.1.` 형태를 못 잡아 이 세션에서 따로 잘랐다** → `fig_A1.png`, `fig_A2.png`.
  `figures.json` 은 도구가 만든 원본 그대로이며 A1/A2 항목이 없다 — 불변층이라
  덧쓰지 않았다.)
- 페이지 참조는 **PDF 페이지**(1–16). 저널 조판 페이지는 PDF 페이지와 같다(1–14 + 표지).

---

# 원문에 없어서 확인이 필요한 것 (읽기 전에 먼저 본다)

이 절이 이 digest 의 가장 중요한 산출물이다. 아래는 **논문이 답을 주지 않는 것**이고,
이 중 여러 개가 우리 프로젝트가 채울 수 있는 자리다.

| # | 공백 | 왜 문제인가 |
|---|---|---|
| G1 | **열화 모드 3개에 오차 막대가 없다.** Fig. 6a–c 의 "Meas." 점에 불확실성 표기가 전혀 없다. | peak tracking 은 DVA 극값 위치를 읽는 절차이고 그 위치는 평활화·샘플링·C-rate 에 민감하다. 크기를 아무도 모른다. |
| G2 | **peak 위치 추출 절차가 인쇄되지 않았다.** 평활 필터·미분 방식·창 정의·보간 어느 것도 없다. | 우리가 [[mode-observability]] Phase 1 에서 실측한 "valley 정의 하나로 feature 값이 −20.0 vs −11.3 으로 갈린다" 와 정확히 같은 자유도다. 재현 불가. |
| G3 | **모델 쪽 LAM/LLI 를 어떻게 뽑았는지 없다.** Fig. 6 은 "Sim." 과 "Meas." 를 겹쳐 그리는데, 시뮬레이션 값이 식 (19)(`ε_s` 비)·식 (20)(`n_Li`)에서 나온 것인지, 아니면 **시뮬레이션 곡선에 같은 peak tracking 을 돌린 것**인지 적혀 있지 않다. | 전자면 **정의가 다른 두 양을 겹쳐 놓고 "일치" 라고 부르는 것**이다. 이 구분이 Fig. 6 의 의미 전부를 정한다. |
| G4 | **"LI = 두 balancing bar 의 overlap" 이라는 정의가 LLI 를 LAM 으로 오염시킬 수 있다.** `[인쇄, §3.1.2]` "the available capacity, which is **synonymous with the lithium inventory (LI)** and defined as the **overlap** of the illustrated cell balancing bars". | overlap 은 두 전극 창의 교집합이므로 LAM 이 창을 줄이면 LLI 를 안 잃어도 줄어든다. 식 (3)–(4) 로 LAM 을 먼저 소거했다고 해도 그 소거가 완전한지는 인쇄된 식만으로 판정되지 않는다. 이 잠재적 이중계산이 Fig. 6c 에서 LLI 가 두 LAM 보다 항상 큰 이유일 수 있다. |
| G5 | **fitting 절차가 "iterative fitting over a multitude of simulations"** 한 줄뿐이다 (§4.1). 목적함수·가중치·초기값·수렴 기준·해의 유일성 아무것도 없다. | 6개 파라미터가 `f`(fitted) 로 표시돼 있다 (Table A.1). 그 6개가 5개 관측 곡선군에 어떻게 배분됐는지 알 수 없다. |
| G6 | **저자 스스로 식별 가능성 분석이 없다고 적는다** — 그리고 문헌에도 없다고 적는다. `[인쇄, §3.3.2]` "as of today, **no such parametric analyses exist for the presented model or comparable ones in the literature**". | 이것은 공백이자 **인용 가능한 진술**이다. 우리 프로젝트의 존재 이유를 이 계보의 저자들이 직접 확인해 준 문장이다. |
| G7 | **셀이 1개다.** `[인쇄, §2.5]` 4개로 시작해 2개 조기 고장, 1개는 LTO-RE 불안정 → 모델 검증은 사실상 **1셀**. | 셀 간 재현성이 0. Fig. 6 의 8~9 % 삼중항이 이 셀의 것인지 이 화학의 것인지 구분 불가. |
| G8 | **LTO-RE 와 GWRE 가 서로 다른 anode 전위를 준다** (Fig. 4). 그 차이가 이 논문이 분해하려는 효과보다 크다. 논문은 이 차이를 **물리가 아니라 전해질 저항 오프셋**으로 보고 상수 `R_GWRE→LTO-RE = 0.35 Ω` 로 흡수한다. | 그 오프셋이 **노화 중에도 상수인지** 검증이 없다. 전해질·다공도가 변하면 안 상수다 (논문 자신의 식 (17) 이 다공도 감소를 모델링한다). |
| G9 | **DVA 재구성이 어긋나는데 "good agreement" 라고 적는다** (Fig. A.1e/f). 전위 곡선 `U(Q)` 는 잘 맞지만 그 미분은 안 맞는다. | §3.1 의 전제("features remain constant over lifetime")를 시험하는 유일한 그림이 그 전제와 부합하지 않는 쪽으로 보인다. 아래 §9 참조. |
| G10 | **half-cell OCP 는 pristine GITT 한 번뿐이다.** 노화된 전극의 OCP 를 다시 재지 않았다. | Rodrigues 의 blending 이 "필요 없었다" 는 판정 근거가 **재구성 품질**뿐이고 독립 측정이 아니다. |
| G11 | **데이터 비공개.** `[인쇄]` "Data will be made available on request." | 우리가 이 half-cell 궤적을 α·β 검증에 직접 쓰려면 저자 접촉이 필요하다. |
| G12 | **anode 전위 측정과 모델 비교가 "500 사이클까지" 다** (Table 1). 실험은 1000 사이클인데 시뮬레이션은 계산시간 때문에 500 에서 끊었다 (§4.1). | 후반 500 사이클(비선형 구간이 시작되는 곳 — Fig. 6d 에서 550 EFC 부터 기울기가 꺾인다)은 모델이 한 번도 시험받지 않았다. |

---

## 0. 서지사항 (직접 확인)

`[인쇄]` PDF 메타데이터 및 헤더/푸터:

| 항목 | 값 |
|---|---|
| 제목 | Modeling and half-cell-resolved measurement of the influence of cell degradation on the anode potential of high-energy lithium-ion cells |
| 저자 | J. Natterer ᵃᐟᵇ (교신, †), F.F. Oehler ᵃᐟᵇ (†), S. O'Kane ᶜᐟᵈ, M. Marinescu ᶜᐟᵈ, G.J. Offer ᶜᐟᵈ, A. Jossen ᵃ († equal contribution) |
| 소속 | a: TUM EES (Institute for Electrical Energy Storage Technology, München) · b: Infineon Technologies AG · c: Imperial College London, Mech. Eng. · d: The Faraday Institution |
| 학술지 | Journal of Power Sources **678** (2026) 240036 |
| DOI | 10.1016/j.jpowsour.2026.240036 |
| 접수/개정/게재 | Received 25 June 2025 · Revised 31 March 2026 · Accepted 1 April 2026 · Online 17 April 2026 |
| 저작권 | © 2026 The Authors, Elsevier — **CC BY-NC-ND 4.0 (open access)** |
| 키워드 | Degradation modeling · Reference electrode · Doyle-Fuller-Newman model · Fast charging · **PyBaMM** |
| 지원 | BMWi/BMWK ProMoBiS [03ETE046A] |
| 이해충돌 | Natterer = Infineon 재직, Oehler = Infineon 전 재직 (본인들이 명시) |
| 생성형 AI 고지 | `[인쇄]` "the authors used Claude Sonnet 3.7 and DeepL for grammatical and syntactical enhancement" — 문법 교정 용도로 한정 명시 |

`[해석]` **공저자 구성이 이 논문의 좌표를 설명한다**: TUM Jossen 그룹(half-cell
OCP fitting DMA 의 Schmitt 계보) + Imperial O'Kane/Marinescu/Offer(PyBaMM 열화
submodel 의 저자들). 즉 **실험 쪽 DMA 전통과 PyBaMM 열화 모델링이 한 논문에서
만난다**. 우리 파이프라인은 정확히 그 교집합 위에 서 있다.

---

## 1. 한 문단 요약

`[해석]` 저자들은 기준전극이 박힌 단층 파우치셀(NMC-811‖graphite, 100 mAh)을
25 °C 에서 0.5 C/0.5 C 로 **1000 사이클, 약 1년** 돌리면서 50 사이클마다 RPT 를
찍었다. LTO 기준전극이 두 전극의 전위를 따로 주기 때문에, **full-cell OCV 를
half-cell OCP 로 fitting 하는 통상 절차를 쓰지 않고** 각 전극의 DVA 특징점 사이
거리로 LAM 을 직접 재고, 스케일한 pristine OCP 와 측정 곡선 사이의 **가로 이동량**
으로 LLI 를 잰다. 그 세 궤적 + 충전용량 궤적을 목표로 PyBaMM DFN + 열화 submodel
(nSEI·pSEI·입자균열·2차SEI·LAM)을 맞춘 뒤, submodel 을 하나씩 꺼 보는 OAAT 로
**anode 표면 전위에 무엇이 중요한가**를 묻는다. 답: **LAM 이 중요하고(빼면 anode
전위를 최대 ~7 mV 과대평가) 입자균열은 무시 가능하며, SEI 는 anode 가 아니라
cathode 쪽(pSEI)에서 지배적**이다. 부수적이지만 논문이 가장 강조하는 결과는
**저항 증가의 거의 전부가 양극에서 온다**는 것이고, 이것은 기준전극이 없었으면
음극에 잘못 귀속됐을 것이라고 적는다.

---

## 2. p.1–2 — Abstract / Highlights / Introduction

### 2.1 Highlights `[인쇄]`
- "Single-layer pouch cells with **reference electrodes** underwent over **1000 cycles**."
- "A physicochemical aging model is **validated**, revealing critical aging parameters."
- "The validated aging-sensitive model is then analyzed for the anode potential."
- "Key degradation mechanisms are identified and discussed for the anode potential."

### 2.2 Abstract 에서 뽑은 명제 `[인쇄]`
- 데이터: "a **one-year, 1000-cycle** aging study using **multi-reference electrode
  single-layer pouch cells with NMC-811/graphite**".
- 모델: "a physics-based degradation model based on the **Doyle-Fuller-Newman**
  framework, leveraging **half-cell-resolved measurement data in a pre-plating regime**".
- 결론 1: "**Loss of active material is identified as a key mechanism which, if not
  considered, results in overestimation of the anode potential.**"
- 결론 2: "a significant **resistance increase in the cathode material** … was
  identified and **empirically captured** in the model."
- 결론 3 (★ 우리 축): "**Without reference electrodes, this resistance increase could
  not be accurately detected and, as suggested in the literature, would likely have
  been misattributed to the anode in the aging model.**"

`[해석]` 결론 3 은 **관측이 부족할 때 열화가 엉뚱한 전극에 배정된다**는 진술이며,
이 저장소의 [[fitting-degeneracy]] 가 열역학 축에서 말하는 것을 **동역학(저항) 축**
에서 말한 것이다. 다만 논문은 이것을 degeneracy 라고 부르지 않고, 정량화도 하지
않는다 (기준전극 없이 맞춰 본 대조 모델이 없다 — 아래 §11 비판 1).

### 2.3 Introduction 의 문제 설정 `[인쇄]`
- 규제 배경: EURO 7 / UNECE GTR 의 SoH 추정 허용오차 밴드.
- 열화 모델 분류: **interface passivation** (도금·SEI) vs **mechanical fatigue**
  (LAM·입자균열).
- 기존 half-cell 접근의 문제: 전극을 **뜯어내(harvesting)** 코인셀로 재는 방식은
  전해질이 달라지고, 심하게 열화된 셀에서는 기계적 취약성 때문에 쓸 만한 코인셀을
  얻기 어렵다 [6–9].
- 대안: **기준전극(RE)을 셀 안에 넣는다** [10–12]. 그런데 "the utilization of
  in-situ half-cell data collected over extended cycling for the detailed validation
  of aging models **remains rare in literature**".
- 현행 관행에 대한 진술 (★): "semi-empirical half-cell models are often used to
  derive degradation modes via fitting mostly with half-cell curves of **pristine
  material**" [8,13–15].
- ★★ 이 논문 전체에서 우리 질문에 가장 가까운 문장 (p.2 말미):
  > "existing aging models have not been thoroughly investigated and validated using
  > half-cell-resolved data from extensive cycling, which fundamentally improves
  > confidence in model predictions, as it substantially **reduces the ambiguity
  > inherent in fitting models to full-cell data alone, where multiple parameter
  > combinations and effects can produce similar terminal responses, while yielding
  > vastly different internal states**."

  `[해석]` 이것은 **비식별성(degeneracy)의 정의를 그대로 쓴 문장**이다 — "여러
  파라미터 조합이 같은 단자 응답을 내면서 내부 상태는 완전히 다르다". 저자들은
  이 문제를 **관측을 늘려서**(half-cell 채널 2개 추가) 푼다. 우리 카드
  [[pvs-sev-lli-lampe-separability]] 가 "관측을 늘리면 갈리는가" 를 묻는데,
  이 논문은 **"곡선 안에서 늘리는" 것이 아니라 "채널 자체를 하나 더 다는"**
  경로의 실물 사례다. 그리고 그 채널은 [[np-lip-ocv-reparametrization]] 의 2 자유도
  상한이 적용되지 않는 유일한 종류다 (full-cell 곡선의 함수가 아니므로).
- 목표 3개 (i) RE 안정성 + half-cell 고유 열화 분석, (ii) 열화 모델을 **half-cell
  분해 데이터로** 파라미터화, (iii) **OAAT 영향 분석**으로 anode 전위에 중요한
  메커니즘 선별.
- 범위 한정 `[인쇄]`: "rather than aiming for a broadly generalizable and
  statistically robust model, the focus of this study is on identifying the **most
  relevant aging mechanisms to achieve practical accuracy**."

---

## 3. p.2–3 — §2 Experimental (셀·장비·프로토콜)

### 3.1 셀 `[인쇄]`
| 항목 | 값 |
|---|---|
| 형식 | 자체 제작 **SLP** (Single-Layer Pouch) |
| 공칭 용량 | **100 mAh** |
| 전극 면적 | **25 cm²** |
| 음극 | graphite, 로딩 **4.4 mAh cm⁻²**, 캘린더링 후 공극률 **36.9 %**, 두께 ≈ **83 μm** |
| 양극 | **NMC-811**, 로딩 **4.0 mAh cm⁻²**, 공극률 **32.5 %**, 두께 ≈ **70 μm** |
| 전해질 | **1.0 M LiPF₆ + 0.2 M LiFSI** in EC:DMC:EMC (1:1:1 wt), 주입량 **1750 μl** |
| 기준전극 | 스택 **밖**에 **LTO-RE**(Li₄Ti₅O₁₂) 1개 + 스택 **안** 유리섬유 분리막 사이에 **금선 기준전극(GWRE) 4개** 균등 배치 |

`[해석]` **N/P 비 = 4.4/4.0 = 1.10** (로딩 기준). 우리 파이프라인의 α·β 좌표에서
`r_N/P` 에 해당하는 초기값이며, Table A.1 의 화학량론 창(§10)과 교차 확인된다.
Si 가 없는 **순수 graphite** 다 — 사용자 질문 4의 "Si/Gr" 축은 이 논문에 없다.

### 3.2 장비·프로토콜 `[인쇄]`
- 온도: Vötsch VTS 7018-5 챔버, **25 °C** 고정. 압력·온도 균일성은 전용 강철 고정구.
- 계측: Keithley 2460 소스미터 + Keithley 2000 멀티미터(멀티플렉서)로 **LTO-RE 전위
  샘플링 ≈ 0.7 Hz**. 멀티미터 입력 임피던스 **> 100 GΩ**.
- **사이클링**: 0.5 C CC 충전 → 4.2 V 도달 시 CV → **C/50** 차단; 0.5 C CC 방전 →
  2.8 V. 전압창 **2.8–4.2 V**. C-rate 는 formation + 3 사이클 후 방전용량 기준으로
  정하고 **시험 내내 바꾸지 않았다**.
- **RPT (50 사이클마다)**: 0.2 C 완전 충방전 **2회** → 0.75 C **1회** → SoC 50 %
  (용량 기준) 설정 → **1.0 C, 10 s DC 펄스 저항** 충·방전 양방향.
- **기준선**: formation 직후가 아니라 **50 사이클 후의 첫 RPT** 를 initial 로 삼는다.
- 방전을 CC 로 한 이유: Geslin et al. [36] — CC 방전이 **worst case** 라서.

`[해석]` **RPT 가 0.2 C 다.** 저자들이 스스로 "notably higher than the C-rate chosen
by other researchers" 라고 적는다(§3.1). 즉 이 논문의 "half-cell OCP 곡선" 은
평형 곡선이 아니라 **0.2 C 충전 곡선**이고, 과전압이 섞여 있다. 아래 §11 비판 3.

### 3.3 §2.4 LTO-RE 안정성 검증 (우리 질문 1의 핵심)
`[인쇄]` 논리 사슬:
1. 선행 연구 [35](Oehler et al., 같은 저자 그룹)가 GWRE·LTO-RE 모두 **10개월 이상**
   안정적이었다고 보였다. 타 문헌: Costard [37] LTO/Al mesh **최소 70일**;
   Epding [38] 은 **재충전이 필요**했다고 보고 → "the previously investigated time
   spans are **insufficient** for the presented aging study, which lasted for about
   a year."
2. 가정: 0.2 C 에서 graphite 음극 과전압은 **10⁻² V 규모** [39] 이므로 무시 가능
   수준이고, RE 가 표류하면 **비정상적인 전위 강하/표류**로 검출될 것이다.
3. 검사 지점: **SoC ≈ 8 % (≈ 6.5 mAh)** 의 DVA 특징 — 1000 사이클 동안 안정.
4. 판정 `[인쇄]`: 그 지점에서 초기(50 사이클) 대비 **"maximum difference of less than
   4 mV"** → "the RE is considered stable".
5. **저자 자신의 반론** `[인쇄]`: "the low deviation could be due to **mutually
   canceling mechanisms**" — 부반응 과전압은 음극 전위를 낮추고, 측정기에 의한
   탈리튬화는 LTO-RE 전위를 올린다. 후자는 >100 GΩ 입력임피던스로 "unlikely" 라고
   본다.

`[도표, Fig. 1c]` 그 4 mV 는 **무작위 잡음이 아니라 단조 감소**다: 50→550 사이클에서
0 → 약 **−3.3 mV** 로 매끈하게 내려가고, 550–1000 사이클은 **−3.3 ~ −3.6 mV 평탄**.
`[해석]` 크기는 작지만 **모양이 표류의 모양**이다. 저자의 "상쇄" 반론은 이 단조성과
정합적이며(두 단조 효과의 차), 논문은 그 가능성을 배제하지 않고 열어 둔 채 넘어간다.
**우리 목적(ground truth)에는 이 4 mV 가 상한 오차로 기록되어야 한다** — 그리고
이것은 논문이 제시한 **유일한 정량 불확실성**이다.

### 3.4 §2.5 한계 (저자가 직접 적음) `[인쇄]`
- 4셀로 시작 → **2셀 조기 고장 + 1셀 LTO-RE 불안정** → "the model validation
  **primarily relied on data from one cell**".
- "the limited sample size restricts the statistical power and unconditional
  generalizability".
- 보상 논리: "The restricted nature of the dataset is, to some extent, offset by the
  **considerable depth of observability** enabled by the RE".

`[해석]` **표본 1, 관측 깊이 최대**. 이 교환비가 이 논문의 성격 전부를 정한다.
우리 쪽에 주는 의미: 이 데이터는 **모집단 통계**로 쓸 수 없고 **단일 사례의 좌표
검증용**으로만 쓸 수 있다.

---

## 4. p.3–5 — §3.1 Degradation Mode Analysis (★ 우리 질문 1·2의 본체)

### 4.1 왜 OCV fitting 을 버렸는가 `[인쇄]`
> "The availability of half-cell measurements allowed for a **re-evaluation of the
> common practice of fitting pristine half-cell OCP curves to degraded full-cell OCV
> curves** for Degradation Mode Analysis (DMA)."
> "we opted **not to use** the well-established OCV-fitting concept presented by,
> e.g., Schmitt et al. [7,8], in favor of a broader approach enabled by the LTO-RE.
> This approach **eliminates numerical fitting procedures** by directly utilizing
> in-situ half-cell data for **straightforward interpretation** of electrode-specific
> degradation."

`[해석]` **이 저장소가 이 논문에서 가져갈 첫째 물건이 이 문단이다.** 우리가 판정
대상으로 삼는 절차([[birkl-ocv-degradation-diagnostic]], Schmitt 계보)를 이 논문은
**같은 실험실 전통 안에서 스스로 대체**한다. 대체의 대가는 기준전극을 심어야 한다는
것이고, 얻는 것은 **최적화가 사라진다**는 것이다.

### 4.2 계보 정리 (논문이 스스로 그리는 지도) `[인쇄]`
- **Christensen & Newman [13]**: 전극별 불균등 용량 손실 — LLI 와 용량 감쇠를
  "cycle path slope 변화 → lithiation window 이동" 으로 구분. **balancing 곡선의
  scaling & shifting** 개념의 시조.
- **Birkl et al. [15]**: 두 전극 OCP 의 고유 feature 가 **수명 내내 불변**이라 가정하고,
  느린 충방전 곡선으로 LLI·LAM_neg·LAM_pos 를 **최적화**로 구한다.
  (= 우리 [[birkl-ocv-degradation-diagnostic]])
- **ICA/DVA peak tracking 계열 [41–44]**: 최적화 없이 특징 peak 의 이동을 추적.
- **Dubarry et al. [45]**: 상전이/DVA peak 의 이동을 **열화-둔감 feature 기준으로
  상대화**해 LAM·LLI 를 추적. (= 우리 [[dubarry-mechanistic-mode-synthesis]])
- **이 논문의 위치** `[인쇄]`: "the idea of analytical peak tracking in readily
  available DVA curves is pursued in the present study, **but in close relation to
  the often chosen OCV fitting approach**."

`[해석]` 즉 **좌표계는 Birkl/Dubarry 것을 그대로 쓰되, 관측을 full-cell 에서
half-cell 로 갈아 끼운 것**이다. 이것이 우리 비교 페이지
[[halfcell-window-parametrization-lineage]] 에 붙는 새 항목이다: **매개변수 수를
줄이거나 제약을 더하는 대신, 관측 채널을 늘려 여분을 없앤다.**

### 4.3 §3.1.1 LAM — 식과 좌표 규약 (★ 사용자 질문 3)

`[인쇄]` graphite 상(phase) 명명은 **Gantenbein et al. [49–51]** 를 따르고, NMC 는
**Schmitt et al. [7]** 의 C1/C3 명명을 따른다.

```
Q_LAM,neg = Q_II − Q_III                                     (1)
LAM_neg   = 1 − Q_LAM,neg / Q_LAM,neg,init                   (2)
```

- `Q_II` = graphite 상전이 **I/II 및 II/III** 를 대표하는 stage II feature 의 위치
- `Q_III` = 상전이 **II/III → III/IV** 에 해당하는 stage III feature 의 위치 (기준점)
- 노화가 진행되면 **stage II 가 stage III 기준 feature 대비 왼쪽으로 이동**한다
  `[인쇄]`.
- LAM_pos 는 **C1 ↔ C3** 사이에 같은 절차 `[인쇄]`.

`[해석]` **이 정의의 좌표 규약을 정확히 읽어야 한다.** 두 feature 는 각각 그 전극의
**고정된 화학량론 값**에 대응한다고 가정된다. 그 사이의 **full-cell 용량 축 거리**는
곧 "그 전극이 두 화학량론 사이를 지나는 데 필요한 전하량" = **전극 용량에 비례**한다.
따라서 식 (1)–(2) 는 **한 전극의 용량 비**를 재는 것이고, 이것은 우리 파이프라인의
`C_p`, `C_n` (또는 α·β 창 폭)에 **직접 대응**한다. 중요한 것은:
- **LLI 와 섞이지 않는다.** LLI 는 두 전극의 상대 오프셋을 바꾸지만 한 전극 **안의**
  두 feature 사이 거리는 바꾸지 않는다.
- 따라서 **LAM_neg 와 LAM_pos 는 서로 독립적으로, 그리고 LLI 와 독립적으로 측정된다.**
  full-cell OCV fitting 에서 세 모드가 하나의 곡선을 공유하며 얽히는 구조가 **여기서는
  구조적으로 없다.**
- 전제 조건 두 개: (a) feature 의 화학량론 위치가 노화에도 불변 (Birkl 의 가정과 동일),
  (b) 0.2 C 과전압이 feature 위치를 이동시키지 않는다.

`[도표, Fig. 2a]` 음극: stage III feature ≈ **16 mAh**, stage II feature ≈ **55 mAh**
(50 사이클, 파랑) → **≈ 52 mAh** (녹색). 즉 `Q_LAM,neg` ≈ 39 → 36 mAh.
`[재현]` 1 − 36/39 = **7.7 %** — Fig. 6a 의 최종 LAM_neg ≈ 8.2 % 와 정합 (판독 오차 내).
`[도표, Fig. 2b]` 양극: C3 ≈ **5 mAh**, C1 ≈ **70.5 mAh**(파랑) → **≈ 65 mAh**(녹색).
`Q_LAM,pos` ≈ 65.5 → 60 mAh. `[재현]` 1 − 60/65.5 = **8.4 %** ↔ Fig. 6b ≈ 8.1 %.

### 4.4 §3.1.2 LLI — 식과 좌표 규약

```
ξ_OCP = ξ_OCP,init · (1 − LAM) · (Q_cycle / Q_ref)           (3)
Δξ_LLI,neg = ξ^II_OCP − ξ^II_meas                            (4)
```

`[인쇄]` 절차:
1. LLI 는 "**a shift of the OCP along the SoC**" 로 이해된다 [15].
2. pristine OCP 를 **LAM 과 SoH_C 로 스케일**해 `ξ_OCP` 를 만든다 (식 3). `ξ_OCP` 는
   "the scaled, half-cell potential curve of the respective electrode **over the
   full-cell capacity**".
3. 같은 상전이 feature 의 위치를 **스케일된 OCP 곡선**(식 3)과 **측정 곡선**에서 각각
   읽어 그 차이를 `Δξ` 로 둔다 (식 4). 측정 곡선은 "inherently includes LLI, LAM_neg,
   and LAM_pos".
4. 양극에도 같은 계산 → **두 전극의 lithiation window 가 모두 추적**된다.
5. `[인쇄]` "Fig. 3e indicates that the **available capacity**, which is synonymous
   with the **lithium inventory (LI)** and defined as the **overlap of the illustrated
   cell balancing bars**, undergoes a progressive decrease. **Relating the change in
   LI to the first value gives LLI.**"
6. **bow tie 마커** = LAM 스케일링의 **고정 기준점** [55].

`[해석]` **좌표 규약 요약** (우리 α·β 와의 사전):
| 논문 | 우리 쪽 대응 | 성격 |
|---|---|---|
| `Q_LAM,neg/pos` (식 1) | 전극 용량 `C_n`, `C_p` | **직접 측정**, fitting 없음 |
| `LAM_neg/pos` (식 2) | `1 − C/C_init` | 초기 RPT 기준 **상대량** |
| `Δξ_LLI,·` (식 4) | 두 전극 창의 **상대 오프셋** | 측정 − 스케일된 pristine OCP |
| `LI` (Fig. 3e overlap) | 사용 가능 용량 | **overlap 정의 — G4 의 위험** |
| `LAM` 스케일의 bow tie | 창의 고정 끝점 | 어느 끝을 고정하는지가 규약 |

**우리 질문 3("모델 식과 좌표 규약")의 답**: 저자의 좌표는 **Birkl/Dubarry 의 창
좌표와 같지만 추정 경로가 다르다**. Birkl 은 4개 창 좌표를 3개 모드로 매개화하고
**최적화**로 찾는다. 이 논문은 창의 **폭**(LAM)을 DVA 거리로 **직접** 재고, 창의
**위치**(LLI)를 "직접 잰 폭으로 스케일한 pristine 곡선" 대비 **가로 이동량**으로 잰다.
즉 **4개 창 좌표를 3개 관측으로 순차적으로 못 박는 구조**이며, 여분(null 방향)이
남을 자리가 없다. 대가는 (i) 기준전극, (ii) feature 불변 가정, (iii) peak 판독 잡음.

`[도표, Fig. 3b]` `Δξ_LLI,neg` ≈ **0.04 SoC** (점선 측정 ≈ 0.62 ↔ 파선 스케일 OCP ≈ 0.66).
`[도표, Fig. 3d]` `Δξ_LLI,pos` ≈ **0.035 SoC** (파선 ≈ 0.765 ↔ 점선 ≈ 0.80).
`[도표, Fig. 3e]` 축 눈금은 −18.7 … 112.3 mAh. 양극 막대의 오른쪽 끝이 노화와 함께
왼쪽으로, 음극 막대의 왼쪽 끝이 오른쪽으로 이동한다 (양쪽 확대 삽입도). **막대가
두꺼워 색이 겹치므로 이 그림에서 신뢰할 수치를 뽑지 못했다** — 겹침 폭의 변화를
읽으면 10 %대가 나오는데 Fig. 6c 의 9.3 % 와 맞추기 어려워, **수치는 적지 않는다**
(판독 실패를 기록해 둔다).

### 4.5 §3.1 말미 — 방법 자체의 자체 검증 `[인쇄]`
- RPT 가 0.2 C 라 저항 증가를 보정해야 한다 → **Fly et al. [48]** 의 방식: CC 충전
  시작의 IR drop 과 CV 종료의 IR drop 을 **선형 보간**해 곡선을 보정.
- **Rodrigues et al. [56]** 가 Ni-rich 산화물의 노화가 양극 OCP **자체를 바꾼다**고
  보고하고 **aged/pristine half-cell 곡선의 blending** 을 제안했다 (대상:
  LiNi₀.₉Mn₀.₀₅Co₀.₀₅O₂).
  → `[인쇄]` "However, **this was not necessary in the presented case** to obtain
  reasonable results with NMC-811."
- 근거는 **Fig. A.1**: 500 사이클 시점의 곡선을 초기 곡선에서 LAM·LLI 스케일·이동 +
  IR 보정으로 재구성 → "The curves show **good agreement**, confirming the chosen
  approach."

`[해석]` **사용자 질문 4("half-cell 곡선 자체가 변하는 문제를 어떻게 다뤘나")의
답이 이 세 줄이다**: 문제를 인지하고, 문헌의 해법(blending)을 인용하고, **자기
데이터에는 불필요했다고 판정**한다. 판정 근거는 **재구성 품질 하나**이며 독립
측정이 아니다 (G10). 그리고 **그 근거 그림이 부분적으로 저자의 판정과 어긋난다**
— 아래 §9.

---

## 5. p.5–7 — §3.2 Simulation and model

### 5.1 프레임 `[인쇄]`
- **PyBaMM 24.1** [57], **DFN** [58,59] 을 pristine 상태의 기반으로 두고 열화 모델을 결합.
- **등온 25 °C** 가정 (대형 강철 고정구 + 큰 접촉면적 + 능동 챔버).
- 다루는 열화: **passivation layer 성장, 입자 균열, LAM**, 그리고 그것들과 음극 전위의 관계.
- `[인쇄]` **리튬 도금은 모델에 없다** — "the experimental study was limited to C-rates
  that are expected to refrain the negative half-cell potential from reaching critical
  levels."

### 5.2 §3.2.1 SEI (nSEI / pSEI)
```
j_nSEI = −(D_nSEI·c_Li,0·F / L_nSEI) · exp(−F/(RT)·(φ_s,neg − φ_l))     (5)
dL_nSEI/dt = Ω_nSEI · j_nSEI / (F·z_nSEI),   z_nSEI = 2                  (6)
```
`[인쇄]` **nSEI 는 "리튬 이온 interstitial 확산 律속 + 전위 의존"** 모델 [18,66,67].
용매확산 律속 단독 모델은 "does not align with the observed capacity fade" 라 SoC
의존을 넣어야 한다는 논리.

```
N_pSEI = D_pSEI·c_sol,0 / L_pSEI                                          (7)
dL_pSEI/dt = N_pSEI·Ω_pSEI / z_pSEI,          z_pSEI = 2                  (8)
```
`[인쇄]` **pSEI 는 명시적으로 "physically supported but empirically interpreted"** 다.
양극의 진짜 기전(산소 방출에 따른 입자 상변화 [68,69]; Ghosh [70]·Zhuo [71] 의
전용 passivation phase 모델)은 "numerically expensive and require hitherto unclear
model calibration" 이라 **채택하지 않았다**. 대신 **용매확산 律속 SEI 식을 양극에
빌려 쓴다**.

`[해석]` **이 논문에서 가장 중요한 단일 모델 결정이다.** 양극의 저항 증가는
**측정된 현상**이지만 그 모델 표현은 **물리가 아니라 곡선 맞춤용 대리 변수**다.
따라서 "pSEI 가 지배적" 이라는 §4.2.2 의 결론은 **"양극 쪽 저항 성장 항이
지배적"** 이라고 읽어야 하고, 그것이 실제로 계면 피막인지 상변화인지 입자 접촉
손실인지는 이 논문이 구분하지 않는다 (저자도 그렇게 적는다).

### 5.3 §3.2.2 입자 역학
```
σ_r = 2EΩ_l/(3(1−ν)) · [ (1/R_p³)∫₀^{R_p} c̄ r² dr − (1/r³)∫₀^r c̄ r² dr ]   (9)
σ_t =  EΩ_l/(3(1−ν)) · [ (2/R_p³)∫₀^{R_p} c̄ r² dr + (1/r³)∫₀^r c̄ r² dr − c̄ ] (10)
σ_h = (σ_r + 2σ_t)/3                                                        (11)
```
(식 (10) 의 부호는 PDF 텍스트 추출에서 모호했다 — `[해석]` 표준형(Zhang/Ai)을
따르면 위와 같다. **원문 조판을 다시 확인할 것**.)

- **응력 유발 확산** [26]:
  ```
  θ_M = (Ω_s/RT)·(2Ω_s E)/(9(1−ν))                                        (12)
  D_s = (1 + θ_M·c_s)·D_s,0                                               (13)
  ```
  `[인쇄]` O'Kane [72] 을 따라 기준 농도 0 → "mechanical stress directly follows
  the lithiation level".
- **균열 전파 (Paris 법칙)** [25,72]:
  ```
  dl_cr/dN = (k_cr/t₀)·( σ_t · b_cr · √(π l_cr) )^{m_cr}                  (14)
  ```
  단일 대표 균열, 합체·분기 없음.
- `[인쇄]` **양극의 균열은 고려하지 않는다** — NMC 류의 부피 변화가 균형 잡힌
  리튬화/탈리튬화에서 **≈ 2 %** 라서 [76,77].

### 5.4 §3.2.3 2차 SEI (균열면 SEI)
`[인쇄]` Karger et al. [24] 의 3분류 — (i) SEI 균열, (ii) SEI 박리, (iii) **입자 균열에
의한 SEI 생성** — 중 (iii) 만 지배적이라 가정.
```
∂L_nSEI/∂t = Ω_SEI·j_nSEI/(F·z) + (∂l_cr/∂t)·ΔL_nSEI,cr/l_cr              (15)
Δn_nSEI,cr = (2·a·ρ_cr·w_cr/Ω_nSEI)·( l_cr·L_nSEI − L_nSEI,0·l_cr,0 )      (16)
Δε = a·( ΔL_nSEI + L_nSEI,cr·2·l_cr·w_cr·ρ_cr )                            (17)
```
식 (16) = **균열면 SEI 가 소비하는 cyclable Li** (= LLI 경로), 식 (17) = **다공도
감소**(선형화, 곡률 무시 — PyBaMM 소스와 동일하다고 명시).

### 5.5 §3.2.4 LAM 모델 (★)
```
∂ε_s/∂t = ζ_LAM · ( (σ_h,max − σ_h,min) / σ_crit )^{γ_LAM},   σ_h,min > 0  (18)
LAM = 1 − C_el/C_el,init = 1 − ε_s,avg/ε_s,avg,init                        (19)
∂n_Li/∂t = A_act·L·(∂ε_s,avg/∂t)·c_s,avg                                   (20)
```
`[인쇄]` 식 (18) 은 **Reniers et al. [3]** 의 경험식(Laresgoiti [21] 기반), `ζ_LAM`
과 `γ_LAM` 은 **fitting 파라미터**. 식 (20) 은 **Sulzer et al. [83]** 을 따라
"**LAM may imply LLI** since it is likely that lithiated material becomes
unaccessible" 를 반영한다.

`[해석]` ★ **식 (20) 이 우리 축에 직접 걸린다.** 모델 안에서 **LAM 이 LLI 를
생성한다** — 즉 두 모드가 **인과적으로 결합**되어 있다. 그러면 Fig. 6 에서
LLI(9.3 %)와 LAM(8.1–8.2 %)이 비슷하게 나오는 것은 **독립적인 세 물리량이 우연히
같은 것**이 아니라 **모델 구조가 강제한 상관의 일부**일 수 있다. 실측 쪽 LLI 도
비슷하게 나오므로 실측이 모델을 지지하는 것으로 보이지만, **"세 모드가 왜 같이
가는가" 라는 질문에 이 논문은 물리적 답(식 20)을 하나 제시하고 있는 셈**이다.
우리 [[22p-physics-or-degeneracy]] 카드가 "PE ≈ NE ≈ LLI 는 축퇴의 산물인가" 를
묻는데, **이 논문은 "그럴 수도 있지만 물리적으로 그렇게 될 통로도 있다"** 는 쪽의
근거를 준다 (반대 방향 증거).

### 5.6 §3.2.5 모델의 물리적 성격에 대한 저자의 유보 `[인쇄]`
"the aging model's accuracy can be **directly influenced by the validity of the
underlying assumptions**" — DFN 의 기하 단순화, 차원 축소된 입자역학, 등온 가정.
그리고 §3.2.5 는 pSEI 를 "empirically interpreted" 로 다시 못 박는다.

---

## 6. p.7–8 — §3.3 Parameterization (★ 우리 질문 3·G5·G6)

### 6.1 파라미터 정책 `[인쇄]`
- "parameters are typically estimated by **iterative fitting** of observable
  performance metrics. However, this approach risks **suboptimal parameter
  identification**." — Laue et al. [84] 가 표준 DFN 만으로도 **과적합 위험과
  파라미터 민감도 분산**을 지적.
- 대응: **O'Kane et al. [72] 의 열화 파라미터 세트를 baseline 으로 채택**하고 소수만 조정.
- ★ `[인쇄]` "the LTO-RE provides enhanced insights into cell behavior, enabling
  **distinct separation of aging effects and polarization changes for both
  electrodes**. This represents **progress towards more identifiable degradation
  parameter fitting** without risks associated with electrode harvesting."

`[해석]` **"more identifiable" 이라는 단어가 이 논문에서 이렇게 한 번 나온다.**
주장은 정성적이고 정량 증거는 없다 (조건수·상관·CRB 없음). 하지만 **주장의 방향은
우리 결론과 같다**: 관측 채널을 늘리면 식별 가능성이 올라간다.

### 6.2 Table 1 — 검증 데이터 `[인쇄]`
전위 곡선은 항상 full-cell 기준 **2.8–4.2 V** 구간, 용량·모드는 **50 사이클마다의 RPT**.

| 검증 데이터 | C-rate | 사이클 수 |
|---|---|---|
| 음극 half-cell 전위 / V | 0.2, 0.5, 0.75 | 500 |
| 양극 half-cell 전위 / V | 0.2, 0.5, 0.75 | 500 |
| Full-cell 전위 / V | 0.2, 0.5, 0.75 | 500 |
| 충전용량 CC / mAh | 0.2 | 500 |
| 충전용량 CCCV / mAh | 0.2 | 500 |
| LAM_neg / % | 0.2 | 500 |
| LAM_pos / % | 0.2 | 500 |
| LLI / % | 0.2 | 500 |

`[해석]` **관측 벡터가 8종**이다. 우리 파이프라인이 쓰는 것은 사실상 첫 줄의 full-cell
전위 하나이며, 이 논문은 거기에 **전극별 전위 2개 + 전극별 모드 3개**를 더한다.
이것이 §2.3 에서 인용한 "reduces the ambiguity" 의 구체적 내용이다.

### 6.3 §3.3.1 무엇을 손으로 돌렸는가 `[인쇄]`
- `D_nSEI`, `D_pSEI` — **fitted** (문헌값이 모호하고 LLI·용량손실·과전압에 직접 영향).
- `R_SEI` — Borodin [85]/Safari [16] 의 **2·10⁵ Ω·m 에서 30 % 감소** (→ 1.4·10⁵).
  근거: 이 셀의 전해질에 **LiFSI** 가 들어 있어 Asheim [86] 기준 SEI 이온전도가 더 좋다.
- `k_cr` — Purewal [25] 의 **3.9·10⁻²⁰ 를 3.9·10⁻²¹ 로** (10배 낮춤). 근거: 이 연구의
  C-rate 가 Purewal 보다 온건하다. 배경 논쟁: Takahashi [87] 는 25 °C 에서 graphite
  균열이 "rather unlikely" 라고 보고하나, 초기 결함을 고려하지 않았다고 반박.
- `ρ_cr` — 직접 측정값이 없어 Purewal 의 **3.18·10¹⁵ m⁻¹** 을 그대로 사용
  (Table A.1 에는 단위가 **m⁻²** 로 적혀 있다 — **본문과 표의 단위가 불일치**).
- `ζ_LAM` — **fitted**, `γ_LAM` 은 O'Kane [72] 값(=2) 고정.

### 6.4 §3.3.2 민감도·식별 가능성 (★★ 인용 가치 최상)
`[인쇄]` 전문에 가까운 인용:
> "a parametric sensitivity analysis may be helpful in identifying **compensating
> parameters** and further clarifying degradation pathways within electrodes.
> Unfortunately, **as of today, no such parametric analyses exist for the presented
> model or comparable ones in the literature**, which might be primarily due to the
> methodological and computational complexity … This complexity can be attributed to
> the DFN model's nonlinear nature and inherent parameter interactions, which make
> sensitivity assessment with isolated parameter variation around a nominal value
> difficult [89–91], **even without considering aging effects**. While the current
> study cannot address this challenge due to scope limitations and methodological
> ambiguities, the authors are **currently developing strategies for global parametric
> sensitivity analysis** of an aging-sensitive DFN model. … **sensitivity results
> inform but do not fully resolve identifiability**, which is a limitation explicitly
> acknowledged in the present work."

`[해석]` 세 가지가 한꺼번에 들어 있다:
1. **"compensating parameters"** — 저자들이 축퇴를 정확히 그 이름으로 부르지는
   않지만 개념은 갖고 있다.
2. **분야 전체에 이 분석이 없다는 전수 주장** — 우리가
   [[pvs-sev-lli-lampe-separability]]·[[22p-physics-or-degeneracy]] 에서 "이 공백은
   한 논문의 누락이 아니라 계보의 구조적 공백" 이라고 적어 온 것에 대한 **저자 측
   확인**이다. 2026년 4월 게재 논문의 진술이므로 시점도 최신이다.
3. **감도 ≠ 식별 가능성** 을 저자가 명시적으로 구분한다 — 이 계보에서 드문 정확성.

---

## 7. p.8 §3.3.3 — pristine 모델과 기준전극 위치 문제 (★ 우리 질문 1의 함정)

`[인쇄]`
- 선행 연구 [35](Oehler)의 **SLP ①** (같은 종류, GWRE 4개 + LTO-RE 1개)와 비교.
- **LTO-RE 는 스택 밖**에 있어 GWRE 와 전위가 "**differs significantly … due to the
  spatial allocation**".
- 원래 GWRE 전위를 재현하도록 만든 모델은 **LTO-RE 전위와 맞지 않는다**.
- 해결: **옴 항 하나를 더한다.**
  ```
  U = φ_s − φ_l + I · R_GWRE→LTO-RE,     R_GWRE→LTO-RE = 0.35 Ω           (21)
  ```
  "aiming to map the **electrolyte resistance between the position of the GWREs and
  the LTO-RE**". 전해질 특성이 노화 내내 **불변**이라고 가정한 이 모델이 이후 전부 사용된다.

`[도표, Fig. 4]` (pristine, SLP ①)
| C-rate | LTO-RE − GWRE 전위차 (충전 중반) | 충전 후반 최저점 |
|---|---|---|
| 0.2 C | ≈ **+10 mV** | LTO ≈ 0.062 V / GWRE ≈ 0.052 V (@ ~88 mAh) |
| 0.5 C | ≈ **+15 mV** | LTO ≈ 0.038 V / GWRE ≈ 0.021 V (@ ~78 mAh) |
| 0.75 C | ≈ **+20~25 mV** | LTO ≈ **+0.018 V** / **GWRE 1 ≈ −0.005 V** (@ ~72 mAh) |

`[해석]` ★★ **이것이 이 논문에서 가장 무거운 단서이자 가장 큰 위험이다.**
0.75 C 에서 **스택 안 기준전극(GWRE)은 음극 전위가 0 V 아래로 내려갔다고 말하고,
스택 밖 기준전극(LTO-RE)은 +18 mV 라고 말한다.** 같은 셀, 같은 시점이다. 즉
"half-cell-resolved measurement" 는 **하나의 값이 아니라 기준전극 위치에 따라
20 mV 이상 달라지는 값**이다. 그리고 이 논문이 anode 전위에 대해 분해하려는
효과(LAM 을 빼면 ~7 mV, §8.3)는 **그 차이보다 작다**.

논문은 이 문제를 **인지하고 처리한다** — 옴 오프셋 (21) 로 흡수하고, 이후 OAAT
분석(Fig. 7·8)에서는 아예 **anode–separator 계면의 국소 전위**로 평가 지점을 옮긴다
(`[인쇄, §4.2]` "since this region is expected to exhibit the **lowest local
potentials** and thus has the highest risk of lithium plating"). 그러나
- 그 오프셋이 **노화 중 상수**라는 검증이 없고 (G8),
- 실험 데이터와의 비교(Fig. 5)는 여전히 **LTO 프레임**에서 이뤄지며,
- 도금 여유 판정(20 mV 문턱)은 **모델 내부 좌표**에서만 이뤄진다.

**우리 질문 1의 답에 이 제약이 붙는다**: 이 논문의 half-cell 데이터는 **모드 분해
(LLI/LAM)의 ground truth 로는 쓸 수 있지만**(그 계산은 DVA 특징의 **가로 위치**만
쓰고 전위의 **세로 절대값**을 쓰지 않는다), **전위 절대값의 ground truth 로는 위험**
하다. 다행히 우리가 원하는 것은 전자다.

---

## 8. p.8–12 — §4 Results

### 8.1 §4.1 Validation (Fig. 5, Fig. 6)
`[인쇄]`
- "By **iterative fitting over a multitude of simulations**, the parameters listed in
  Table A.1 were obtained" — 절차 서술은 이 한 줄이 전부 (G5).
- 시뮬레이션 종료는 **500 사이클** (계산 시간 제약).
- "The simulated **positive** half-cell potentials show significant overpotential
  increases, yet **deviate more from the measurements than the negative** half-cell
  potentials." 이유: NMC-811 의 복잡한 열화를 submodel 이 다 담지 못해서.
- ★ "the resistance increase at the positive electrode **only becomes identifiable,
  specifiable in the accompanying model, and ultimately parametrizable through the
  experimental setup with a RE** presented in this work."
- "degradation modes are important metrics for **reducing overfitting risks** in
  physics-based aging models" (Li et al. [92]) — Fig. 6 의 존재 이유.
- 충전용량은 "deviating only approximately **1.5 mAh**".
- 자기 유보 `[인쇄]`: "it remains possible that the chosen parameters and aging
  submodels **may not fully account for the underlying, physically entangled
  mechanisms, which are difficult to uniquely discern**."

`[도표, Fig. 5]` 오차(점선, `Δ/mV`, 눈금 20 mV):
| 대상 | 0.2 C | 0.5 C | 0.75 C |
|---|---|---|---|
| 음극 half-cell | 대부분 **< 5 mV**, 충전 초기 스파이크 ≈ 20 mV | 대부분 < 5 mV | 후반 ≈ **10 mV** 까지 |
| 양극 half-cell | 중반 **10–20 mV** | **10–20 mV** | **20–25 mV** |
| Full-cell | **10–20 mV** | 10–20 mV | ≈ 20 mV |

`[해석]` **모델–측정 불일치의 크기 (우리 질문 3)**: **음극 ≲ 5–10 mV, 양극 10–25 mV,
full-cell 10–20 mV**. 즉 이 모델은 **음극을 잘 맞추고 양극을 못 맞춘다**. 그리고
논문의 주 결론(LAM 효과 ~7 mV)은 **음극 오차와 같은 규모**다. 결론이 틀렸다는 뜻은
아니지만, **"LAM 을 빼면 anode 전위를 7 mV 과대평가한다" 는 진술의 신호 대 잡음비가
1 근처**라는 것은 논문에 적혀 있지 않다.

`[도표, Fig. 6]` (마지막 점 ≈ 505 EFC)
| 양 | Meas. | Sim. |
|---|---|---|
| LAM_neg | ≈ **8.2 %** | ≈ **8.2 %** |
| LAM_pos | ≈ **8.1 %** | ≈ **8.0 %** |
| LLI | ≈ **9.3 %** | ≈ **8.4 %** |

- 세 패널 모두 **x축(EFC) 눈금 라벨이 없다** — 위치는 (d) 의 축과 공유된다고 가정.
- **LLI 는 전 구간에서 Meas. > Sim.** (≈ 0.5–1 %p). LAM_pos 는 거의 완전 일치,
  LAM_neg 는 중반에 Meas. 가 약간 위.
- (d) 용량: `Q_CCCV,Meas` ≈ 91.8 → 85.2 mAh (@505 EFC), 이후 650 EFC 에서 82.3.
  `Q_CC,Meas` ≈ 88.6 → 79.2. 시뮬레이션은 505 에서 멈춘다.
  **550 EFC 부터 측정 곡선의 기울기가 꺾인다** (비선형 가속 시작) — 모델은 그
  구간을 보지 않았다 (G12).
- (e) 차이: `ΔQ_CCCV` **0.8 → 1.7 mAh**, `ΔQ_CC` **≈ 0.25 → 1.45 mAh**, **둘 다 단조
  증가**.

`[해석]` 두 가지를 기록한다.
1. **차이가 단조 증가한다** = 잔차가 백색이 아니라 **구조적 편향**이다. 모델이
   용량 감쇠를 **체계적으로 과소평가**한다. 논문은 "≈1.5 mAh" 라는 절대값만 적고
   이 추세를 논하지 않는다.
2. **기준점(50 EFC)에서 이미 0.8 mAh 어긋나 있다** — 열화 이전의 정합 오차다.

### 8.2 ★★ 세 모드의 삼중항과 full-cell 곡선의 null 방향 `[재현]`

`[도표]` 실측 삼중항 `(LLI, LAM_pos, LAM_neg) ≈ (9.3, 8.1, 8.2) %` 를
[[np-lip-ocv-reparametrization]] 의 식 (16) 좌표로 옮기면:

```
r_N/P / r_ini = (1 − LAM_NE)/(1 − LAM_PE) = (1 − 0.082)/(1 − 0.081) = 0.9989
z₀⁺  / z₀,ini = (1 − LLI)   /(1 − LAM_PE) = (1 − 0.093)/(1 − 0.081) = 0.9869
```

`[해석]` **500 사이클, 약 8 % 의 용량 손실 동안 SOC 정규화 full-cell OCV 의 형상은
한 좌표에서 0.11 %, 다른 좌표에서 1.31 % 밖에 움직이지 않았다.** 다시 말해 이 셀의
1년치 열화는 **full-cell OCV 형상이 거의 보지 못하는 방향**을 따라 진행됐다 —
Lin & Khoo 의 닫힌 형태 null 방향(`LLI = LAM_PE = LAM_NE`) 바로 옆이다.

그런데 기준전극은 그 셋을 **8.2 / 8.1 / 9.3 으로 갈라서** 보고한다. 즉:

> **이 논문은 "full-cell 곡선으로는 거의 볼 수 없는 상태를 half-cell 채널이
> 분해해 낸" 사례의 실물이다.** 우리 [[fitting-degeneracy]] 가 말하는 축퇴 방향
> 위에 실제 셀이 앉아 있었고, 관측 채널을 늘린 쪽은 답을 냈다.

**단, 이 문장을 과대 인용하지 않기 위한 한정 3개**:
(a) 논문은 **full-cell 만으로 같은 분해를 시도한 대조군을 만들지 않았다.** 따라서
"full-cell 로는 못 했을 것" 은 우리 `[해석]` 이고 논문의 실측이 아니다.
(b) 세 값의 **불확실성이 없다**(G1). 8.2 vs 8.1 의 차이(0.1 %p)가 판독 잡음보다
크다는 근거가 없다. **"세 값이 서로 다르다" 는 주장은 이 데이터로 지지되지 않고,
"세 값이 8~9 % 대에 모여 있다" 만 지지된다.**
(c) 삼중항이 null 방향 근처라는 것은 **이 셀·이 프로토콜**의 사실이다. 일반 법칙이
아니다 (셀 1개, G7).

### 8.3 §4.2 OAAT — anode 전위 (Fig. 7) (★ 사용자 질문 2)

`[인쇄]` 평가 지점을 **anode–separator 계면**으로 옮긴다 (국소 최저 전위).
500 사이클 노화 후 0.2 / 0.5 / 0.75 C 충전을 시뮬레이션하고 submodel 을 하나씩 끈다.

| 끈 submodel | 결과 `[인쇄]` | 크기 `[도표, Fig. 7b/d/f]` |
|---|---|---|
| **입자 균열 전파** | "nearly indistinguishable" → "unlikely to be the determining mechanism" | Δ ≈ **0 mV** 전 구간, 세 C-rate 모두 |
| **SEI 성장** (n+p) | 양극 분극이 작아져 4.2 V 도달이 **늦어짐** → 음극이 **더 오래 리튬화** → 전위가 **더 내려감**. 수직 이동은 작다 → "the overpotential caused by the nSEI is **small**" | SoC ≈ 0.75–0.9 에서 Δ ≈ **−10 ~ −13 mV** (0.5 C·0.75 C), 나머지 구간 ≈ 0 |
| **LAM** | 끄면 전위가 **올라간다**(과대평가). `ε_s` ↓ → 비표면적 `a` ↓ → 전류밀도 ↑ → 과전압 ↑ 이 사라지므로 | Δ ≈ **+2 mV**(0.2 C), **+4 mV**(0.5 C), **+5~7 mV**(0.75 C). 본문은 0.75 C 에서 "approximately **7 mV**" |

`[인쇄]` 결론: "if LAM is not considered, the surface potential may be
**overestimated**, which could lead to higher charging currents and increased lithium
plating risk in virtual sensing applications."

`[도표]` 세 C-rate 모두 SoC ≈ 0 에서 초기 스파이크 Δ ≈ **+12 mV**(LAM·SEI 둘 다).
`[도표]` 0.75 C 전체 모델의 음극 전위 최저값 ≈ **0.030 V** (SoC ≈ 0.75), 20 mV 문턱 위.
SEI 를 끈 경우 최저 ≈ **0.020 V** 로 문턱에 닿는다.

`[해석]` ★ **사용자 질문 2("LLI/LAM 이 anode 전위에 남기는 구별 가능한 서명이
있는가")의 답은 "부분적으로, 그리고 부호가 반대 방향이라 유망하다"** 이다.

| 모드 | anode 전위에 대한 부호 | 기전 (논문) | 형태 |
|---|---|---|---|
| **LAM** (주로 NE) | **↓ 낮춘다** (모델에서 빼면 올라간다) | `ε_s`↓ → `a`↓ → 국소 전류밀도↑ → 전하전달·SEI 과전압↑ | **수직 이동**, C-rate 에 비례해 커짐 |
| **LLI/SEI (nSEI)** | 직접 효과 ≈ **0** | 전위 의존 nSEI 성장이 느려 과전압 기여 미미 | — |
| **pSEI (양극 저항)** | **↑ 올린다 (간접)** | 양극 분극↑ → 4.2 V 조기 도달 → 리튬화 **단축** | **가로(종료점) 이동** |

`[해석]` **두 서명의 형태가 다르다**: LAM 은 곡선을 **아래로 평행이동**시키고,
양극 저항은 **충전 종료 시점을 앞당겨** 곡선을 **짧게 자른다**. 형태가 다르면
원리적으로 분리 가능하다 — 이것은 [[pvs-sev-lli-lampe-separability]] 가 찾는
"부호가 아니라 **모양이 다른** 관측" 의 후보다. **단, C-rate 의존이라 열역학 관측이
아니고 동역학 관측이며, 크기가 10 mV 급이라 §7 의 기준전극 위치 오차(20 mV)에
묻힐 수 있다.**

### 8.4 §4.2.2 저항 배분의 실측 (Fig. A.2) — 논문이 강조하는 결과
`[인쇄]` Stiaszny et al. [61] 이 해체·재조립 방식으로 "양극 임피던스 증가가 음극을
지배" 를 보고했으나 "disassembly and reconstruction … may have disturbed the SEI"
라는 공정 오염 가능성이 있다. 이 연구는 **in-situ 로 같은 결론을 확인**한다:
"it appears that the predominant increase in resistance in the SLP cell may originate
from the **positive half-cell**. … The DC resistance of the negative half-cell
**remains relatively constant**."

`[도표, Fig. A.2]` 1 C, 10 s 충전 방향 DC 펄스 저항 (50 → 505 EFC):
| 대상 | 시작 | 끝 | 변화 |
|---|---|---|---|
| 음극 | ≈ **0.27 Ω** | ≈ **0.20 Ω** | **−0.07 Ω (−26 %)** |
| 양극 | ≈ **0.95 Ω** | ≈ **1.44 Ω** | **+0.49 Ω (+52 %)** |
| Full-cell | ≈ **1.21 Ω** | ≈ **1.64 Ω** | **+0.43 Ω (+36 %)** |

`[해석]` **본문 서술과 그림이 어긋난다.** 본문은 음극이 "relatively constant" 라고
적지만, 그림은 **단조 감소**(−26 %)를 보인다. 그리고 full-cell 증가분(+0.43)이
양극 증가분(+0.49)보다 **작은** 것은 음극의 감소가 상쇄했기 때문이다 — 즉
**full-cell 저항만 봤다면 양극의 실제 증가폭을 과소평가했을 것**이다.
`[재현]` 합이 맞는지부터 확인한다: `ΔR_pos + ΔR_neg = (+0.49) + (−0.07) =
**+0.42 Ω**` ≈ 측정 `ΔR_full = +0.43 Ω` — 판독 오차 내에서 정합한다.
따라서 full-cell 만 관측했다면 양극 증가폭을 `0.43/0.49 = 0.88`, 즉
**약 12 % 낮게** 봤을 것이고, 더 중요하게는 **음극이 −26 % 로 내려갔다는 사실을
전혀 볼 수 없었을 것**이다. **이것이 논문의 abstract 결론 3
("RE 없이는 이 저항 증가를 정확히 검출할 수 없고 음극에 오귀속됐을 것")의 정량
근거이며, 논문 본문은 이 산술을 적지 않는다.**

`[인쇄]` 저자 자신의 반론도 있다: 음극 활물질의 **부피 변화로 표면적이 증가**해
전하전달 저항이 내려가고 nSEI 두께 증가와 **상쇄**될 수 있다 — "this theoretically
possible effect is **not included in any of the DFN-based aging models in the
literature** and is considered **a gap in the modeling efforts of the research
community**, which also **cannot be remedied in this study**."

`[해석]` 이 유보가 정확히 위 그림의 −26 % 를 설명하는 후보다. 저자들은 그것을
적어 두고 모델에는 넣지 않았다. **동역학 축(SEV 류)을 모드 관측으로 쓰려는 설계에
대한 경고**이기도 하다 — [[pvs-sev-lli-lampe-separability]] Gap 절의 "임피던스 유래
feature 의 부호가 셀 간에 뒤집힌다"(Su 2024) 와 같은 계열의 위협이며, 여기서는
**한 셀 안에서 두 전극의 부호가 반대**다.

### 8.5 §4.3 모델 기반 급속충전 (Fig. 8)
`[인쇄]` **MCC** 프로토콜: 1.5 C 로 시작, anode 표면 전위가 **20 mV** 에 접근하면
전류를 **1 %씩 재귀적으로 감소** → CAP(Constant Anode Potential) 충전 모사.
500 사이클 노화 **후**에 적용 (노화 자체는 실험이 뒷받침하는 0.5 C 로 진행).

`[도표, Fig. 8]`
- (a) C-rate: SoC ≈ 0.37 까지 1.5 C 유지 → 이후 감소. **No-LAM(녹색)이 전 구간에서
  더 높은 전류**를 허용(최대 ≈ +0.1 C).
- (b) 음극 전위: No-LAM 이 SoC 0.30–0.45 에서 ≈ **+5 mV** 높다 ("Overestimation" 주석).
  전체 모델은 20 mV 선에 붙어 평탄하게 제어된다.
- (c)(d) No-SEI(주황)는 양극 전위·full-cell 전압이 **≈ 100–150 mV 낮아** 4.2 V 도달이
  늦고, 그래서 SoC ≈ 0.79 까지 충전이 이어진다 (전체 모델은 ≈ 0.71).
- `[인쇄]` 중요한 유보: LAM 을 무시했을 때의 전위 차이가 **0 mV 에 도달하지는 않는다**
  ("this potential difference does not approach 0 mV … remains below 20 mV"), 다만
  "this safety margin could **decrease** in applications with greater thermal and
  utilization inhomogeneities".

---

## 9. p.13 부록 — Fig. A.1 (★ 사용자 질문 4의 실물 증거)

`[인쇄, 캡션]` "Validation of the peak tracking approach by fitting the aged negative
half-cell (left), positive half-cell (right), and full-cell (middle) charging curves
over 500 cycles to the respective, initial charging curves after 50 cycles (a)–(c).
The accompanying fitted and measured DVA curves (d)–(f)."

`[도표, Fig. A.1]` **직접 봤다.**
- (a)(b)(c) **전위 곡선 `U(Q)` 는 세 경우 모두 육안으로 거의 완전 일치**한다.
- (d) **음극 DVA**: 잘 맞는다. 15–20 mAh 의 봉우리 위치·높이 모두 일치, 50 mAh 부근의
  작은 혹만 측정 쪽이 약간 높다.
- (e) **full-cell DVA**: **어긋난다.** 측정(진한 점선)은 ≈ 42 mAh 에서 봉우리 ≈ 11,
  적합(연한 실선)은 그 자리에서 ≈ 10 이고 **위상이 밀려 있다**. 55–60 mAh 에서
  측정은 ≈ 8.7 로 완만한데 적합은 ≈ 9.5 에서 다른 모양의 골을 만든다. 70–80 mAh
  구간에서는 **곡선이 갈라진다** (측정 ≈ 5 → 4.8, 적합 ≈ 8 → 13.5).
- (f) **양극 DVA**: **가장 크게 어긋난다.** 40 mAh 부근에서 측정 ≈ **10.2**, 적합 ≈
  **8.3**. 55–62 mAh 에서 측정이 ≈ **5** 로 내려가는데 적합은 ≈ **8.5** 로 남는다.
  70 mAh 이후에도 두 곡선이 서로 다른 방향으로 벌어진다.

`[해석]` ★ **논문의 판정("this was not necessary in the presented case", "good
agreement, confirming the chosen approach")은 (a)–(c) 에 대해서만 성립하고
(e)–(f) 에 대해서는 성립하지 않는다.** 그리고 판정하려는 대상(= 노화된 NMC-811 의
OCP 형상이 변했는가)은 정확히 **미분 곡선에서만 보이는 성질**이다. 전위 곡선의
일치는 형상 불변의 증거로 약하다 — 적분이 미분의 차이를 평활하기 때문이다.

이 관측은 **Fig. 2b 와 정합적**이다: `[도표, Fig. 2b]` 양극 half-cell DVA 의 **형상
자체가** 노화와 함께 크게 변한다 (25–60 mAh 구간에서 파랑(50 사이클)과 주황(1000
사이클)의 봉우리 구조가 다른 모양이다). 반면 `[도표, Fig. 2a]` 음극 DVA 의 형상은
거의 불변이고 **위치만** 이동한다.

**따라서 사용자 질문 4의 답**:
- 저자는 문제를 알고 있었고(Rodrigues 인용), **blending 을 쓰지 않기로 판정**했으며,
  그 판정 근거는 **재구성 품질** 하나다.
- 그 근거 그림은 **전위 축에서는 판정을 지지하고 미분 축에서는 지지하지 않는다.**
- **양극 쪽 형상 변화가 실재하는 것으로 보이며**, 그것이 (i) 진짜 OCP 변화인지
  (ii) 성장한 양극 저항이 0.2 C 곡선을 왜곡한 것인지 이 논문은 구분하지 않는다.
  후자라면 IR 보정(Fly 방식, 선형 보간)이 불충분했다는 뜻이 된다.
- **Si/Gr 축은 이 논문에 없다** (순수 graphite). Si 팽창으로 인한 음극 OCP 변화 문제는
  다루지 않는다.

`[해석]` **그러나 이 결함이 LAM 측정을 즉시 무효화하지는 않는다.** 식 (1)–(2) 는
DVA 봉우리의 **위치 차이**만 쓰고 **높이·모양**을 쓰지 않는다. 형상이 변해도 C1·C3
극값의 **위치**가 화학량론적으로 고정돼 있으면 LAM_pos 는 유효하다. 위험한 것은
형상 변화가 **극값 위치를 이동시키는** 경우이며, 그 크기는 이 논문에 없다 (G2).

---

## 10. p.14 Table A.1 — 모델 파라미터 (`f` = fitted, **굵게** = 이 논문에서 변경)

`[인쇄]` 기하·수송·열역학·동역학·전해질은 Oehler [27] + [96] 에서 그대로 가져왔다.

**기하**
| 항목 | Gr | Separator | NMC-811 |
|---|---|---|---|
| 두께 `L` / μm | ≈ 82.25 | ≈ 388 | ≈ 68.95 |
| 입자 반경 `R_p` / μm | 10 | — | 14 |
| 공극률 `ε_l` / % | 36.9 | 86.37 | 32.5 |
| 활물질 분율 `ε_s` / % | 58.7 | — | 60.6 |
| 비활성 분율 `ε_s,na` / % | 4.4 | — | 6.9 |
| Bruggeman `β` | ≈ 1.89 | ≈ 1.5 | ≈ 2.82 |

**열역학 (★ 우리 α·β 대응물)**
| 항목 | Gr | NMC-811 |
|---|---|---|
| 최대 고상 농도 `c_s,max` / mol m⁻³ | **35,632** | **50,060** |
| **화학량론 (0 %–100 % SoC)** | **≈ 1.03 – 80.93 %** | **≈ 80.71 – 14.94 %** |
| 평형전위 `E_eq` | [27] Fig. 2 | [27] Fig. 2 |

`[재현]` 이 표만으로 전극 용량을 재계산해 §3.1 의 로딩값과 대조했다
(`q = ε_s · L · c_s,max · F`, 면적당):
- Gr: 0.587 × 82.25 μm × 35,632 mol m⁻³ × F = **4.61 mAh cm⁻²** (이론), 사용 창
  폭 80.93 − 1.03 = **79.90 %p** → 사용분 **3.68 mAh cm⁻²**
- NMC: 0.606 × 68.95 μm × 50,060 mol m⁻³ × F = **5.61 mAh cm⁻²** (이론), 사용 창
  폭 80.71 − 14.94 = **65.77 %p** → 사용분 **3.69 mAh cm⁻²**

`[해석]` 두 사용분이 **3.68 ↔ 3.69 로 일치**한다 — 표가 자기정합적이라는 확인이며
(같은 전하가 두 전극을 지나므로 당연히 성립해야 한다), 동시에 §3.1 의 로딩 표기
(음극 4.4 / 양극 4.0 mAh cm⁻², N/P = **1.10**)가 **이론 용량이 아니라 실용 용량 기준**
임을 알려 준다. 우리 파이프라인의 `α·β`(창의 시작·끝)에 대응하는 **인쇄된 좌표 한
벌**이 여기 있다: 음극 `[0.0103, 0.8093]`, 양극 `[0.8071, 0.1494]`(방향이 반대).
전극 이론 용량비 `C_n/C_p = 4.61/5.61 = **0.822**` 이고, 창 폭 비
79.90/65.77 = 1.215 가 그것을 정확히 상쇄한다.

**기계**
| 항목 | Gr | NMC-811 | 출처 |
|---|---|---|---|
| 임계응력 `σ_crit` / MPa | 60 | 375 | [72] |
| 초기 균열 길이 `l_cr` / nm | 20 | — | [72] |
| 초기 균열 폭 `w_cr` / nm | 15 | — | [72] |
| **균열률 `k_cr`** | **3.9·10⁻²¹ (f)** | — | [25,72] |
| 부분몰부피 `Ω_active` / m³ mol⁻¹ | 3.1·10⁻⁶ | 1.25·10⁻⁵ | [26,72] |
| Young `E` / GPa | 15 | 375 | [26,72] |
| Poisson `ν` | 0.3 | 0.2 | [26,72] |
| Paris `b_cr` / `m_cr` | 1.12 / 2.2 | — | [25,72] |
| 균열 밀도 `ρ_cr` / m⁻² | 3.18·10¹⁵ | — | [25,72] |
| **LAM 선형상수 `ζ_LAM`** | **6.5·10⁻⁸ (f)** | **5.5·10⁻⁵ (f)** | [72] |
| LAM 지수 `γ_LAM` | 2 | 2 | [72] |

**Passivation**
| 항목 | Gr(n) | NMC(p) | 출처 |
|---|---|---|---|
| 초기 SEI 두께 / nm | 5 | 5 (가정) | [72] |
| Li interstitial 농도 `c_Li,0` | 15 | — | [72] |
| 용매 벌크 농도 `c_sol,0` / mol m⁻³ | — | 2636 | [72] |
| SEI 부분몰부피 `Ω_SEI` / m³ mol⁻¹ | 9.585·10⁻⁵ | 9.585·10⁻⁵ | [16,72] |
| **SEI 저항률 `R_SEI` / Ω m** | **1.4·10⁵ (f)** | **1.4·10⁵ (f)** | [16,72,86] |
| **SEI 확산계수 `D_SEI` / m² s⁻¹** | **1·10⁻²⁰ (f)** | **4.6·10⁻²¹ (f)** | [72] |

`[해석]` ★ **`ζ_LAM,pos / ζ_LAM,neg = 5.5·10⁻⁵ / 6.5·10⁻⁸ ≈ 846**. 두 전극의 LAM
속도상수가 **약 850배** 차이나도록 각각 따로 맞춰졌다. 그런데 결과(Fig. 6a·b)는
LAM_neg ≈ LAM_pos ≈ 8 % 로 거의 같다. 즉 **"두 전극이 비슷하게 열화했다" 는 것은
모델의 예측이 아니라 두 자유 파라미터가 각각 그렇게 맞춰진 결과**다 (응력 진폭이
전극마다 다르므로 상수도 달라야 하는 것은 맞지만, 그 크기는 데이터가 정했다).
**우리 [[22p-physics-or-degeneracy]] 카드에 이것은 중립 정보다** — 실측 쪽 LAM 두
개는 모델과 독립적으로(DVA 로) 측정됐으므로, 모델의 자유도가 실측의 대칭성을
만들어 낸 것은 아니다. 다만 **모델은 그 대칭성을 설명하지 못하고 흡수만 한다.**

`[인쇄]` 전해질 물성(염 확산계수·이온전도도·활동도·전이수)은 농도·온도의 다항/지수
피팅식으로 표에 전부 인쇄돼 있다 (기준 농도 1.2 mol L⁻¹).

---

## 11. 비판 (이 digest 의 판단)

1. **"RE 가 없었으면 음극에 오귀속됐을 것" 은 반사실(counterfactual)인데 대조군이 없다.**
   저자들은 full-cell 데이터만으로 같은 모델을 맞춰 보는 실험을 하지 않았다. 그 대조
   실행은 **PyBaMM 으로 값싸게 가능**하다 (같은 모델, 목적함수에서 half-cell 항만 제거).
   이 논문의 가장 강한 주장이 **가장 검증되지 않은 주장**이다. — 우리가 공급할 수 있다.
2. **fitted 라벨과 measured 라벨의 구분이 이 논문에서는 옳게 되어 있다.** 이 계보에서
   드문 미덕이다: LAM·LLI 가 최적화 산물이 아니라 산술 산물이다. 다만
   **"측정" 이라는 말이 "가정 없는" 을 뜻하지는 않는다** — feature 화학량론 불변,
   0.2 C 과전압 무시, pristine OCP 사용 세 가정 위에 서 있다.
3. **0.2 C 를 OCP 대용으로 쓴다.** Fig. 1a 에서 GITT OCP(파선)와 0.2 C 측정 곡선의
   차이가 육안으로 **10–25 mV** 이고, OCP 에는 있는 ≈ 60 mAh 의 계단이 측정 곡선에는
   **없다**. 즉 0.2 C 곡선은 이미 형상이 다르다. LLI 계산(식 3–4)이 **pristine OCP
   와 0.2 C 측정 곡선의 feature 위치를 직접 비교**하므로, 두 곡선의 형상 차이가
   `Δξ` 에 그대로 편향으로 들어간다. 논문은 IR 보정으로 이를 다룬다고 하지만
   보정은 **곡선 재구성**(Fig. A.1)에만 언급되고 **식 (4) 의 `Δξ` 추출**에 적용됐는지
   불분명하다.
4. **기준전극 위치가 20 mV 를 흔든다** (§7). 논문의 핵심 정량 결론(LAM ~7 mV)보다 크다.
   전위 절대값에 의존하는 모든 결론은 이 오차 안에 있다.
5. **잔차의 구조를 보고하지 않는다.** Fig. 6e 의 단조 증가, Fig. 5 의 양극 편향,
   Fig. A.2 의 음극 저항 감소 — 셋 다 "평균 오차 1.5 mAh" 류의 스칼라로 덮인다.
6. **6개 fitted 파라미터에 대한 유일성 논의가 없다** (G5). 저자들이 §3.3.2 에서
   이 한계를 명시적으로 인정하는 것은 정직하지만, 인정이 해결은 아니다.
7. **셀 1개** (G7). 논문이 스스로 크게 강조하므로 감점 요소라기보다 **이 데이터의
   사용 범위를 정하는 사실**이다.
8. **본문–그림 불일치 2건**: (a) Fig. A.2 의 음극 저항이 "relatively constant" 가
   아니라 −26 %, (b) Fig. A.1 의 "good agreement" 가 DVA(e·f)에서 성립하지 않는다.

---

## 12. 이 저장소가 가져갈 것 (요약)

| # | 물건 | 어디에 |
|---|---|---|
| A | **fitting 없는 전극별 DMA 절차** (식 1–4) — α·β 검증의 독립 근거 **형태** | [[reference-electrode-halfcell-dma]] |
| B | **`(9.3, 8.1, 8.2) %` 삼중항이 null 방향 옆에 있다는 실측** + Lin 좌표 환산 | [[22p-physics-or-degeneracy]] Evidence |
| C | **"이 계보에 파라미터 민감도·식별 가능성 분석이 존재하지 않는다" 는 저자 진술** (§3.3.2) | 두 questions 카드 Gap |
| D | **LAM 과 양극 저항이 anode 전위에 남기는 서명의 *모양*이 다르다** (수직 이동 vs 종료점 이동) | [[pvs-sev-lli-lampe-separability]] |
| E | **기준전극 위치가 20 mV 를 흔든다** — 동역학 축 관측의 실측 상한 | [[pvs-sev-lli-lampe-separability]] Gap |
| F | **한 셀 안에서 두 전극의 저항 변화 부호가 반대**(양극 +52 %, 음극 −26 %) | [[thermo-kinetic-loss-partition]] 계열 |
| G | **인쇄된 화학량론 창 좌표 한 벌** (Gr 1.03–80.93 %, NMC 80.71–14.94 %) | 파라미터 대조용 |
| H | **반사실 대조군(full-cell only 적합)이 비어 있다** — 우리가 값싸게 채울 수 있는 실험 | 후속 제안 |

---

## 13. 그림 판독 기록 (무엇을 보고 무엇을 안 봤는가)

크로핑된 그림 **9장**(fig 8 + tab 1) + 이 세션에서 따로 자른 **부록 2장** = 총 10장의
그림. **그림 10장을 전부 직접 Read 했다.** 표(tab_1)는 이미지로 읽지 않고 PDF 텍스트로
읽었다 (도구 권고).

| 그림 | 봤나 | 이 digest 에서 쓴 곳 | 판독 실패/유보 |
|---|---|---|---|
| Fig. 1 | ✔ | §3.3 (RE 안정성, −3.5 mV 단조), §11-3 (OCP vs 0.2 C 차이) | — |
| Fig. 2 | ✔ | §4.3 (LAM 판독 7.7 %/8.4 %), §9 (양극 DVA 형상 변화) | 색-사이클 대응이 연속이라 "녹색"이 정확히 몇 사이클인지 확정 못 함 |
| Fig. 3 | ✔ | §4.4 (`Δξ` 0.04/0.035) | **(e) balancing bar 에서 수치 추출 실패** — 막대 두께·색 겹침 |
| Fig. 4 | ✔ | §7 (LTO vs GWRE 20 mV) | — |
| Fig. 5 | ✔ | §8.1 (오차 크기표) | 오차 패널의 y 상한이 잘려 최대값이 20 mV 인지 그 이상인지 불확실 |
| Fig. 6 | ✔ | §8.1·8.2 (삼중항, ΔQ 단조 증가) | (a)–(c) 의 **x 눈금 라벨이 없다** — EFC 위치는 (d) 와 공유 가정 |
| Fig. 7 | ✔ | §8.3 (OAAT 크기표) | — |
| Fig. 8 | ✔ | §8.5 (MCC) | — |
| Fig. A.1 | ✔ (직접 크롭) | §9 (★ 본문과 어긋나는 DVA) | — |
| Fig. A.2 | ✔ (직접 크롭) | §8.4 (저항 배분) | — |
| Table 1 | 텍스트로 | §6.2 | — |
| Table A.1 | 텍스트로 | §10 | 전해질 물성 식은 PDF 추출이 조판을 흐트려 **부분적으로만 신뢰**. `ρ_cr` 단위가 본문(m⁻¹)과 표(m⁻²)에서 다르다 |

**본문 서술과 그림이 어긋난 것 2건** (§11-8): Fig. A.2 음극 저항, Fig. A.1 의 DVA.
