---
title: "Schmitt et al. 2022 — Degradation modes considering aging-induced changes in the Si/graphite half-cell OCP curve (JPS 532, 231296)"
source_url: local-upload/55a6f97e-Determination_of_degradation_modes_of_lithiumion_batteries_considering_aginginduced_changes_in_the_halfcell_opencircuit_potential_curve_of_silicon_graphite.pdf
ingested: 2026-09-10
sha256: 5aad50ce9e6a91323514e4f607bb9264871c4cf25019b0e514beed60f709140c
---

# 수집 목적

Julius Schmitt, Markus Schindler, Andreas Oberbauer, Andreas Jossen,
**"Determination of degradation modes of lithium-ion batteries considering
aging-induced changes in the half-cell open-circuit potential curve of
silicon–graphite"**, *Journal of Power Sources* **532** (2022) 231296
(doi:10.1016/j.jpowsour.2022.231296, CC BY) 의 **페이지·절별 해체분석**.

이 논문은 사용자가 **MATLAB electrode balancing 코드
(5-파라미터 `[a_PE, b_PE, a_NE, b_NE, γ_Si]`)의 α·β 가 실제로 맞는지 검증**
하려는 중에 지목한 문헌이다. 이 논문의 모델이 정확히 그 5-파라미터다:
`(α_cat, β_cat, α_an, β_an)` 4개 + blend 비율 `γ_Si` 1개. 따라서 digest 의
무게중심은 "이 논문이 무엇을 발견했나" 가 아니라 **"우리 코드가 의존하는
전제(pristine half-cell 곡선을 α·β 로만 늘이고 옮긴다)가 어디서 깨지고,
깨졌을 때 모드 수치가 얼마나 움직이는가"** 다.

**표기 규칙** (이 위키 관례 3구분):
- `[인쇄]` — 논문 본문·표·식·캡션·**그림 안에 벡터 텍스트로 찍힌 숫자**
- `[도표]` — 그림에서 눈으로 읽은 근사값 (원 데이터가 아니다)
- `[해석]` — 이 문서를 쓰면서 붙인 판단. **논문의 주장이 아니다**

- 원본 파일: 로컬 업로드 PDF **12쪽** (본문 10쪽 + 부록/참고문헌).
  업로드 시 "21 pages" 로 전달됐으나 실제 PDF 는 12쪽이다. **SI 는 없다.**
- 크로핑 그림: `raw/figures/schmitt2022_sic-ocp-shape-change-degradation-modes/`
  (fig 8장 + tab 1장, `figures.json` 에 캡션 색인).
  **Fig. 1–8 전부를 실제로 Read 했다** (§12 에 무엇을 어떻게 읽었는지 기록).
  `tab_1.png` 만 이미지로 안 봤다 — PDF 텍스트가 정확하다.

---

## 0. 원문에 없어서 확인이 필요한 것 (공백 목록)

이 절을 머리에 두는 이유는, 아래 본문의 어떤 숫자도 이 공백을 메우지 않기
때문이다. 인용할 때 같이 인용해야 한다.

1. **모드 추정치의 불확실성이 전혀 없다.** LAM_an·LAM_cat·LLI 어느 것에도
   오차 막대·신뢰구간·재적합 산포가 없다. Fig. 8 은 aging state 당 **셀 1개,
   점 1개**다.
2. **모드의 독립 ground truth 가 없다.** 해체(post-mortem) 후 half-cell 측정을
   했지만 그것은 **입력**(aged anode OCP)으로 쓰였지 LAM 의 정답으로 쓰이지
   않았다. 즉 "LAM_an = 13.1 % 가 맞다"를 확인해 주는 독립 측정이 없다.
3. **fitting 의 유일성·국소최적 문제를 다루지 않는다.** `lsqnonlin`
   (trust-region-reflective) 의 **초기값·경계·다중 시작점·수렴 판정**이
   전혀 적혀 있지 않다. 5-파라미터(γ_Si 포함) 최적화인데 파라미터 상관·
   Hessian·identifiability 언급이 **한 줄도 없다**.
4. **cathode OCP 의 형상 불변은 선행 논문 [22] 에 위임**돼 있다. 이 논문 안에
   NMC-811 형상 불변을 뒷받침하는 데이터는 없다 (인용만).
5. **각 aging state 가 서로 다른 셀이다.** 같은 셀의 시계열이 아니라 서로 다른
   셀을 서로 다른 시점에 해체한 것이라, Fig. 2(c)·6·7·8 의 "추세"에는
   cell-to-cell variation 이 섞여 있다 (저자도 인정, §4.1).
6. **γ_Si 이외의 형상 변화 원인을 배제하지 않았다.** graphite 자체의 형상
   변화, 전극 불균일(inhomogeneity), SEI 로 인한 kinetic 변화가 blend 비율
   변화로 흡수됐을 가능성을 검정하지 않는다 (Fig. 3(b) stage 2 peak 높이
   감소를 "inhomogeneity 탓" 이라고 하면서도 모델에는 넣지 않는다).
7. **저전류(C/30) 충전 곡선 하나만 쓴다.** 방전 방향·부분 곡선·고전류는
   "further research is necessary" 로 미룬다 (결론).
8. **본문과 그림이 한 군데 어긋난다** (§4.5 의 LAM_an = 15.5 % 문장) — §11.1 에
   따로 적었다.

---

## 1. p.1 — 서지·Highlights·Abstract

`[인쇄]` PDF 1쪽에서 확인:

| 항목 | 값 |
|---|---|
| 저자 | Julius Schmitt (교신, julius.schmitt@tum.de), Markus Schindler, Andreas Oberbauer, Andreas Jossen |
| 소속 | TU München, Chair for Electrical Energy Storage Technology (EES) / Munich School of Engineering |
| 학술지 | *Journal of Power Sources* **532** (2022) 231296 |
| DOI | 10.1016/j.jpowsour.2022.231296 |
| 접수 / 개정 / 게재 | 2022-01-04 / 2022-02-23 / accepted 2022-03-07 (online 2022-03-31) |
| 라이선스 | CC BY (open access) |
| 키워드 | Lithium-ion battery · Cycle aging · **Half-cell open-circuit potential** · **Silicon–graphite** · Degradation modes |
| 자금 | 독일 연방경제에너지부 (BMWi) 03ETE019F |
| 데이터/코드 | **공개 언급 없음** (repository 없음) |

`[인쇄]` Highlights 5줄 — 논문 자신이 요약한 기여:
1. Aging-induced change in SiC OCP curve is analyzed using a blend electrode model.
2. Aged full-cell OCV curves are reconstructed using **measured aged** SiC OCP curves.
3. Full-cell OCV curves are reconstructed using **simulated** SiC OCP curves.
4. Degradation modes are estimated with higher validity **avoiding misinterpretations**.
5. Destruction-free estimation method for component degradation in SiC is presented.

`[인쇄]` Abstract 의 핵심 문장 (그대로):
> "Reconstructing the OCV curve of aged cells by shifting and linearly scaling
> **pristine** half-cell OCP curves is an established diagnostic method…
> **Lower estimates are obtained for the loss of anode active material and
> higher estimates for the loss of both cathode active material and lithium
> inventory**, when aging-induced changes in the shape of the silicon–graphite
> OCP are considered."

`[해석]` 이 한 문장이 사용자 질문 1·2의 답을 이미 담고 있다. 형상 불변 가정이
깨지면 **오차가 무작위로 퍼지는 게 아니라 방향이 정해진 편향**으로 나타난다:
LAM_an 과대, LAM_cat·LLI 과소.

---

## 2. p.1–2 — Introduction: 이 논문이 서 있는 계보

`[인쇄]` 논문이 세우는 사슬:

- 열화 **모드**(degradation mode)는 "cell level 에서 같은 관측 변화를 만드는
  메커니즘들의 묶음" 이다 [7,8].
- Dubarry et al. [8] 이 세운 모델: 세 모드 **LAM_an · LAM_cat · LLI** 로
  full-cell OCV 변화를 기술하고, 두 전극 OCP 곡선을 full-cell OCV 에 **정렬**
  해서 모드를 읽는다. → 이 저장소의 [[dubarry-mechanistic-mode-synthesis]] ·
  [[birkl-ocv-degradation-diagnostic]] 과 같은 계보.
- `[인쇄]` "**The shape of the OCP curve of the individual electrodes is
  generally regarded to be invariant during battery aging** in the models used
  for analyzing degradation modes based on the full-cell OCV. This means that
  the OCP curve of an aged electrode can be obtained by **linear scaling** of
  the OCP curve of a pristine electrode."
  → **이것이 이 논문이 겨냥하는 전제이고, 우리 MATLAB 코드가 깔고 있는 전제다.**
- 예외를 시도한 선행 3편: Lee et al. [21] (NMC OCP 형상을 aging 중 적응),
  Jia et al. [19] (aged 전극 OCP 를 쓰면 재구성 정확도가 올라간다),
  Schindler et al. [16] (**SOC-의존 스케일링**으로 비균일 전극 열화 모델링).
- `[인쇄]` 저자들의 직전 논문 [22] (JPS 506 (2021) 230240) 의 결과:
  **NMC-811 의 OCP 형상은 full-cell 사이클링에서 유의하게 변하지 않는다.
  반면 silicon–graphite 의 OCP 형상은 변한다.** 원인 해석: **Si 가 graphite
  보다 빨리 열화** → 두 성분의 상대적 용량 기여가 바뀜 → blend 곡선 모양이 바뀜.
  Si 우선 열화는 [23–26] 에서도 보고 (원인: Si 의 팽창·수축에 의한 전기적·
  이온적 접촉 손실 [23], 형태학적 변화 [27]).
- 이 논문의 신규성 주장 2개 `[인쇄]`:
  (a) "to our knowledge, **the first study in which silicon–graphite half-cell
  OCP curves measured for cells at a series of aging states are used to
  reconstruct the full-cell OCV curve at the corresponding aging state**";
  (b) pristine 순수 Si·graphite 곡선으로 만든 **합성(synthetic) half-cell 곡선**
  으로 aged full-cell OCV 를 재구성하는 접근은 "not been presented in the
  literature before".

`[해석]` (a) 는 **형상 불변 가정을 실험적으로 직접 반증할 수 있는 유일한 설계**
다 — 같은 셀에서 full-cell OCV 와 그 셀의 aged half-cell OCP 를 둘 다 갖고 있기
때문이다. 이 저장소의 관점에서 이 논문의 최대 가치가 여기 있다.

---

## 3. p.2 — Experimental (측정 설계)

`[인쇄]` 실험 상세는 선행 논문 [22] 에 있고 여기는 요약이다.

**셀**: LG Chem **INR18650-MJ1** (MJ1), 18650, 공칭 최소용량 3.35 Ah.
- 음극: graphite (타원형 flake, 평균 15 μm [29]) + **SiO_x 계 입자**
  (날카로운 shard, 평균 3 μm [29]) 의 blend.
  문헌상 Si 질량비는 **1–5 wt.%** 로 편차가 크다 [26,29–31].
- 양극: **NMC-811** [29,31].
- C-rate 기준 용량 3.35 Ah. **1 EFC = 6.7 Ah** 전하 처리량 (공칭용량의 2배).

**사이클링 프로토콜**: CCCV 충전 **C/2** / CC 방전 **1 C**, **25 °C**,
최대 550 cycles. 셀마다 종료 사이클 수를 다르게 해 열화 정도를 분산.

**OCV 측정 (full-cell)**: 준정상 상태, **CC 구간 C/30**, CV 종료전류 C/1000,
2.5 V–4.2 V. 사이클링 전(pristine)·후(aged) 모두 측정. 그 뒤 3 V 로 CCCV 방전
→ **아르곤 글로브박스에서 개봉** → 양쪽 전극 샘플 채취 → 분석저울로 칭량 →
**리튬 금속 대극 코인셀로 준정상 OCP 측정, 약 C/90**.

**graphite 단독 OCP** (이 논문에서 새로 측정한 것):
상용 천연 graphite 시트 (mass loading **13.0 mg cm⁻²**), 지름 14 mm 펀칭,
한쪽 코팅 제거, Li foil 대극 코인셀. formation 5 cycles
(CCCV lithiation C/10, cut-off 0.01 V, cut-off current C/50 → CC delithiation
C/10, cut-off 1.7 V, 각 단계 사이 1시간 휴지). 이후 CCCV delithiation C/10
(1.7 V, C/100) → 100 s 휴지 → **C/100 lithiation 으로 준정상 OCP 측정**
(0.01 V 까지). 25 °C, ESPEC LU-123, BaSyTec CTS. 코인셀 공칭 5.43 mAh.

**silicon 단독 OCP 는 측정하지 않았다** — `[인쇄]` Li & Dahn [38] 의
**lithiation 곡선을 문헌에서 가져왔다**.

`[해석]` **이것이 blend 모델의 가장 약한 고리다.** γ_Si 는 "우리 셀의 SiO_x"
가 아니라 "Li & Dahn 의 결정질 Si" 곡선을 기준으로 정의된 값이다. 저자는 이
치환의 오차를 정량하지 않는다.

---

## 4. p.3–4 — §3.1 Full-cell OCV 모델과 좌표 규약 ★ (질문 3의 답)

이 절이 사용자 질문 3에 직접 답하는 곳이다. **식 번호는 원문 그대로**다.

### 4.1 기본식과 전극 SOC 정의

`[인쇄]` 식 (1):
```
U_full(x_full) = U_cat(x_cat) − U_an(x_an)
```

`[인쇄]` **좌표 규약 (원문 그대로 옮김)**:
- **anode**: `x_an` = "the amount of lithium inserted into the anode divided by
  the total amount of lithium inserted into the anode during a **lithiation
  from 1.7 V to 0.01 V**". 0 ≤ x_an ≤ 1, **x_an = 1 이 lithiated 상태**.
  → 즉 **x_an = 0 이 delithiated (방전된 음극, 1.7 V)**.
- **cathode**: `x_cat` = "the amount of lithium **extracted** from the cathode
  divided by the total amount extracted during a **delithiation from 3.0 V to
  4.3 V**". 0 ≤ x_cat ≤ 1, **x_cat = 1 이 delithiated (4.3 V)**.
  → 즉 **x_cat = 0 이 lithiated (3.0 V)**.
- 두 전극 모두 **"충전이 진행되는 방향"이 x 증가 방향**이다. 이것이 두 곡선을
  같은 부호의 α 로 다룰 수 있게 하는 규약이다.

`[인쇄]` half-cell 전압 한계를 1.7/0.01 V, 3.0/4.3 V 로 잡은 근거 [31]:
SiC 는 1.7 V 에서 이미 사실상 완전 delithiated [34] 이고 그 이상 lithiation 은
**Li plating 위험**; NMC-811 은 3.0 V 에서 사실상 완전 lithiated [35,36] 이고
4.3 V 이상 delithiation 은 **rock-salt 표면층** 생성으로 열화 [37].

`[해석]` 이 선택은 자의적이지 않다 — α·β 의 **수치 자체가 이 전압창 정의에
묶여 있다**. 우리 MATLAB 코드와 비교할 때 `a_NE`/`a_PE` 의 절대값이 다르다면
먼저 **half-cell 전압창 정의가 같은지** 확인해야 한다. (여기서는 α_an,ini ≈
1.04, α_cat,ini ≈ 1.07 — §9 참조.)

### 4.2 정렬(alignment) 변환 — α·β 의 정확한 의미

`[인쇄]` 식 (2)(3):
```
x_full = α_an · x_an  + β_an
x_full = α_cat · x_cat + β_cat
```
- `α_an` = "the factor by which the anode OCP curve is **scaled** to fit the
  full-cell curve" = **"음극 용량이 full-cell 용량 대비 얼마나 oversize 인가"**.
- `β_an` = "the value by which the anode curve is **shifted towards higher
  full-cell SOC**".
- **★ 스케일링의 원점은 언제나 0 % 전극 SOC 다** `[인쇄]`: "In this model,
  the point of origin for the scaling of the half-cell OCP is **always 0 %
  electrode SOC**, which corresponds to the **delithiated state for the anode**
  and the **lithiated state for the cathode**."
- **★ β_an, β_cat 은 언제나 음수다** `[인쇄]`: "As both electrode curves need
  to have their origin at or below 0 % full-cell SOC, β_an and β_cat are always
  negative, which means that the curves are **left-shifted** in the full-cell
  coordinate system."

`[인쇄]` 역변환 식 (4)(5) 와 최종 모델 식 (6):
```
x_an  = (x_full − β_an ) / α_an
x_cat = (x_full − β_cat) / α_cat
U_full(x_full) = U_cat((x_full − β_cat)/α_cat) − U_an((x_full − β_an)/α_an)
```

`[해석] ★ 우리 코드와의 대조표` — 이름만 다르고 같은 4개다:
| 이 논문 | 우리 MATLAB | 의미 |
|---|---|---|
| `α_cat` | `a_PE` | 양극 용량 / full-cell 용량 |
| `β_cat` | `b_PE` | 양극 곡선의 좌측 이동 (음수) |
| `α_an` | `a_NE` | 음극 용량 / full-cell 용량 |
| `β_an` | `b_NE` | 음극 곡선의 좌측 이동 (음수) |
| `γ_Si` | `γ_Si` | 음극 용량 중 Si 기여 분율 |
다만 **부호 규약과 정규화 기준**이 같은지는 코드에서 직접 확인해야 한다
(이 논문은 x_full 을 0–1 로 정규화하고 β 를 **음수로 강제**한다).

### 4.3 모드 정의식 ★ (질문 3의 답 2)

`[인쇄]` 음극 용량: `C_an = C_full · α_an` (해당 aging state 의 잔존 full-cell
용량에 그 state 의 α_an 을 곱한다).

`[인쇄]` 식 (7):
```
LAM_an = (C_an,ini − C_an) / C_an,ini
```
양극도 동일한 방식(`LAM_cat`).

**★ 여기서 놓치기 쉬운 것** `[해석]`: `C_full` 이 aging state 마다 **다르다**
(Table 1). 따라서 LAM 은 α 만의 함수가 아니라
`LAM_an = 1 − (α_an·C_full)/(α_an,ini·C_full,ini)` 이다. α_an 이 **증가**해도
C_full 이 더 크게 줄면 LAM_an 은 **양수**로 나온다. 실제로 §4.3 에서 이런 일이
일어난다 (α_an ↑ 인데 LAM_an ↑).

`[인쇄]` **lithium inventory** 정의 — 식 (8)–(12):
```
C_lit = C_lit,an(x_full,ref) + C_lit,cat(x_full,ref)                (8)
C_lit,an (x_full,ref) = C_full · (x_full,ref − β_an)                (9)
C_lit,cat(x_full,ref) = C_full · (α_cat − x_full,ref + β_cat)      (10)
C_lit = [(x_full,ref − β_an) + (α_cat − x_full,ref + β_cat)] · C_full  (11)
LLI = (C_lit,ini − C_lit) / C_lit,ini                               (12)
```
`[인쇄]` "available lithium" = **각 전극의 상한 cut-off 전압까지 delithiate
할 수 있는 양**. `[인쇄]` "**x_full,ref cancels out in Eq. (11)**" — 기준 SOC
선택에 무관하다.

`[해석]` 식 (11) 을 정리하면 **닫힌 형태**가 된다:
```
C_lit = (α_cat + β_cat − β_an) · C_full
```
즉 **LLI 는 α_cat, β_cat, β_an 세 개에만 의존하고 α_an 에는 전혀 의존하지
않는다.** 이 구조가 뒤(§11.3)에서 축퇴 방향을 읽는 열쇠가 된다.

### 4.4 fitting 알고리즘 ★ (질문 4 관련)

`[인쇄]`
- 모든 곡선을 **정규화**한다 (full-cell 충전 전하량 / 음극 lithiation 전하량 /
  양극 delithiation 전하량을 각각 그 절차 종료 시점 값으로 나눔).
- 목적함수는 **OCV 차이가 아니라 DV(differential voltage) 차이**다. 식 (13):
  ```
  dU/dQ |_x_full = [U_full(x_full + Δx) − U_full(x_full)] / Δx
  ```
- `x_full` **0–1 사이 2001 개 등간격 보간점**에서 계산. `Δx` = SOC 범위의
  **0.2 %**.
- **MATLAB `lsqnonlin` + trust-region-reflective** 로 DV 차이 제곱합 최소화.
- `[인쇄]` DV 를 쓰는 이유: "to align the **features** of the DV curves that
  represent the phases and phase transitions of the active materials and to
  **minimize the influence of absolute offsets** of the OCV curves."
- `[인쇄]` **양 끝 각 1 % 는 목적함수에서 제외** — "to avoid the optimization
  being dominated by the steep slope of the OCV curves near the edges."
- 측정 OCP 곡선은 여러 샘플 평균 [22] 후 **이동평균 필터로 평활화**한 뒤 fitting.

`[해석] ★ 이것이 우리 코드 검증에 직접 걸린다.` 목적함수가 DV 라는 것은
**절대 전압 오프셋 정보를 의도적으로 버린다**는 뜻이다. 절대 OCV 를 쓰면
제약이 하나 더 걸려 α·β 가 달라질 수 있다. 우리 MATLAB 코드가 OCV-RMSE 를
최소화하고 있다면 이 논문의 α·β 와 **직접 비교할 수 없다** — 같은 데이터라도
목적함수가 다른 추정량이다.

### 4.5 세 가지 음극 곡선 (이 논문의 실험 설계 축)

`[인쇄]` 양극은 **언제나 pristine 곡선** (형상 불변 [22]). 음극만 3종:
1. **pristine** 셀에서 뜯은 음극의 측정 OCP → 기존(형상 불변) 방법
2. **같은 셀의 aged** 음극에서 측정한 OCP → "정답에 가장 가까운" 참조
3. **blend 모델로 계산한 합성 곡선** (γ_Si 를 자유 파라미터로) → 제안 방법

각 aging state × 3종 = 정렬 파라미터 세트가 3벌 나오고, 거기서 모드를 계산한다.
(Fig. 1(b) 흐름도.)

---

## 5. p.4–5 — §3.2 Blend electrode OCP 모델 ★ (질문 2의 답)

`[인쇄]` 모델은 Schmidt et al. [9] 의 일반 blend 전극 모델. 정의:
`Q_Si(U)`, `Q_G(U)` = 각 성분에 전위 `U` 까지 lithiation 될 때 삽입되는
용량 분율.

`[인쇄]` 식 (14):
```
Q_blend(U) = γ_Si · Q_Si(U) + (1 − γ_Si) · Q_G(U)
```
`γ_Si` = **음극 총 용량 중 Si 가 제공하는 분율**.
하한 cut-off `U_min` 에서 `Q_Si = Q_G = Q_blend = 1` (정의상).

`[인쇄]` 식 (15): blend OCP 는 위 관계의 **역함수**로 얻는다:
```
U_OCV,blend(Q_blend) = f⁻¹(Q_blend(U))
```
`[인쇄]` "The blend OCP curve is **similar to that of graphite for small γ_Si**
and **similar to that of silicon for large γ_Si**."

`[인쇄]` 실무 주의: graphite lithiation 곡선의 **< 1 mV 국소 최소점**(측정
아티팩트로 추정)을 **제거해야 역함수를 취할 수 있다**.
Si lithiation 곡선은 Li et al. [38] 에서 가져온다.

**★ 핵심 (질문 2의 답)**: `[인쇄]` "the full-cell OCV curve is reconstructed by
aligning both the synthetic anode OCP and the pristine cathode OCP.
**The silicon capacity fraction γ_Si used to calculate the anode OCP is then
optimized along with the four alignment parameters.**"
→ **γ_Si 를 다섯 번째 자유 파라미터로 추가한다.** 우리 코드의
`[a_PE, b_PE, a_NE, b_NE, γ_Si]` 와 정확히 같은 구조다.

`[인쇄]` 식 (16) — γ_Si 에서 Si **질량** 분율로:
```
m_Si / M_blend = (γ_Si · c_G) / (c_Si − γ_Si · (c_Si − c_G))
```
(`c_Si`, `c_G` = 각 성분의 중량비 용량. 유도는 Appendix, 식 A.1–A.9.)

`[해석]` **이 논문이 형상 변화를 다루는 방식은 "곡선을 다시 재는 것"이 아니라
"곡선을 만드는 1-파라미터 족(family)을 도입하고 그 파라미터를 fitting 에
넘기는 것"** 이다. 대가는 명확하다: 자유도가 4 → 5 로 늘고, γ_Si 방향이
α_an 방향과 얼마나 겹치는지(=새 축퇴가 생기는지)를 저자는 **검사하지 않는다**.

---

## 6. p.5–6 — §4.1 SiC OCP 곡선의 형상 변화 정량 ★ (질문 1의 답)

`[인쇄]` **pristine blend 재구성** (Fig. 2(a)):
- 최적화로 얻은 **γ_Si = 9.52 %**.
- 측정 vs 계산 OCP 의 **RMSE = 6.6 mV**.
- `[인쇄]` "The right-shift of the graphite features in comparison to the pure
  graphite curve can be simulated particularly well with the model."

`[인쇄]` **aging 으로 인한 형상 변화의 서술** (선행 논문 [22] 의 관측을 여기서
모델로 설명):
- `[인쇄]` "The most prominent changes are a **left-shift of both the graphite
  and silicon DV peaks towards a lower electrode SOC**."
- 원인 해석: **Si 가 제공하는 전극 용량 분율의 감소**.
- 488 EFC 셀의 aged SiC 를 모델로 맞춘 결과 (Fig. 2(b)):
  `[인쇄]` 모델이 **0.3 V–0.2 V 사이 삽입 전하 감소**(Si 용량 감소)와
  **graphite stage 4L→2L 전압 기울기의 저 SOC 쪽 이동**을 잡아낸다.
- `[인쇄]` **모든 aging state 에서 RMSE < 6.9 mV**.

`[인쇄]` 두 가지 함의를 저자가 직접 적는다:
1. SiC OCP 변화가 **Si 의 더 빠른 용량 감소** 때문이라는 이론을 지지.
2. blend 모델 fitting 이 **성분별 용량 분율의 진단 도구**가 된다.

`[인쇄]` **γ_Si 의 aging 추세** (Fig. 2(c), half-cell 기준):
- 488 EFC 전극에서 **γ_Si = 5.55 %** — **초기값의 약 58 %**.
- 단일 점의 추세 이탈은 **셀간 편차(intrinsic cell variation)** [1,33] 탓.

`[인쇄]` **질량 분율 환산**: `c_Si = 3579 mAh g⁻¹` [25,38],
`c_G = 372 mAh g⁻¹` [40] 를 식 (16) 에 넣으면 **전기화학적으로 활성인 Si 의
질량 분율 = 1.08 %** (blend 활물질 기준). 바인더·카본블랙이 5 wt.% 라고 가정
하면 **전체 음극 질량의 1.03 %**.

`[해석] ★ 질문 1 에 대한 정량 답의 실체`:
저자는 "형상 불변 가정이 깨진다"를 **곡선 오차(mV)로 재지 않고**
**형상을 지배하는 물리 파라미터 γ_Si 의 변화(9.52 % → 5.55 %, 42 % 상대 감소)로**
잰다. 즉 **깨짐의 크기 = γ_Si 의 이동량**이고, 그 이동이 full-cell 에서 만드는
겉보기 효과 = **음극 feature 의 좌이동**이며, 이것이 α_an 감소(=LAM_an)와
**같은 관측 서명**을 준다. 이것이 논문 전체의 논지다.

---

## 7. p.6 — §4.1 계속: 질량 정합성 점검 (저자의 유일한 외부 정합 검증)

`[인쇄]`
- 음극 샘플 평균 질량 (집전체 포함) **35.9 mg**, 집전체 추정 **15.2 mg** [31]
  → 전극 질량 **20.8 mg**, mass loading **13.5 mg cm⁻²**.
- 가정: 비활성 5 %, 총 Si 3.5 wt.% [29,31] 중 **활성 Si 는 1.03 %**,
  나머지 **91.5 wt.% graphite**.
- 이론 중량비 용량으로 계산한 코인셀 용량 **7.84 mAh** vs
  **측정 평균 7.40 mAh** → **차이 < 6 %**.
- 만약 3.5 wt.% 전체가 활성이면 계산값 **9.55 mAh** 로 측정값을 명백히 초과.
- `[인쇄]` 결론: "**a significant part of the silicon in the anode is
  electrochemically inactive**".
- 문헌 총 Si 함량: ICP-OES 약 **3.5 wt.%** [31], EDS 약 **4.5 wt.%** [26],
  X-ray CT 약 **3–4 wt.%** [29]. 또한 `[인쇄]` 이 셀 타입의 조성은 **연도에
  따라 바뀌었고 최근 셀일수록 Si 함량이 낮다** [32].
- `[인쇄]` 참고: 3–4 wt.% Si 상용 SiC 전극에서 **Si 용량 분율 10 %** 가
  Ansean et al. [28] 에서도 보고됐다.

`[해석]` 이것이 이 논문에서 **모델 밖 물리량과 대조한 유일한 점검**이다.
그러나 이 점검이 확인하는 것은 **γ_Si 의 pristine 값의 타당성**이지,
**LAM/LLI 추정치의 정확성이 아니다**. 질문 4 의 답이 약한 근본 이유가 여기 있다.

---

## 8. p.6–7 — §4.2 Full-cell OCV/DV 의 aging 변화 ★ (관측 서명의 혼동)

Fig. 3 을 근거로 한 서술. `[인쇄]`:
- 전반적으로 **같은 SOC 에서 절대 전압이 상승** — LLI 로 balancing 이 밀려
  같은 full-cell SOC 에서 양극이 더 delithiated 되기 때문 [23].
- DV 의 **peak = lithiation phase**, **minimum = 두 상 공존(상전이) 구간**.
- **양극 기인 변화 2개**:
  - NMC-811 **M-phase** peak (약 50–60 % SOC) 가 좌이동. pristine/경열화
    셀에서는 graphite stage 2 peak 와 겹쳐 잘 안 보이다가 **≥361 EFC 에서
    구별 가능**해진다.
  - NMC-811 **H2-phase** peak (약 80 % SOC) 도 좌이동.
  - 원인: cyclable Li 손실 → 충전 중 양극이 더 delithiated → 양극 곡선이 음극
    대비 좌이동 [16]. (이 셀은 0 % SOC 에서 **항상 음극이 제한**, §4.3.)
- **음극 기인 변화 2개**:
  - graphite **stage 4L–2L** peak (약 20 % SOC) 저 SOC 쪽 이동.
  - **silicon phase** peak (10 % SOC 이하) 도 저 SOC 쪽 이동.
- **graphite stage 2 중앙 peak**: 위치에 뚜렷한 추세 없음, **높이는 감소** —
  `[인쇄]` "probably caused by an **increase in the inhomogeneity of the
  anode**" [42–44].

★ **이 논문의 핵심 문단** `[인쇄]` (그대로 옮긴다):
> "There are two possible explanations for this observation: The traditional
> explanation, neglecting changes in the shape of the electrode OCP, would be
> that there is a **higher relative loss of anode active material**… As the
> anode is limiting at 0 % SOC, compression of the anode OCP curve leads to a
> left-shift of the anode features in the full-cell OCV. But… this shift…
> could **also** be caused by the changes in the shape of the anode half-cell
> OCP curve due to silicon degradation being faster than graphite degradation.
> **As both effects would lead to the same results with regard to the full-cell
> OCV, the left-shift of the anode peaks in the full-cell DV can be
> misinterpreted as resulting solely from an overall anode active material
> loss.**"

`[해석] ★ 이것이 축퇴(degeneracy) 진술 그 자체다.` 저자는 `degeneracy`,
`identifiability`, `non-uniqueness` 라는 단어를 **한 번도 쓰지 않지만**,
문장이 말하는 것은 정확히 **두 파라미터 방향(α_an ↓ vs γ_Si ↓)이 full-cell
관측에 같은 서명을 남긴다**는 것이다. 이 저장소의 [[fitting-degeneracy]] 가
LLI/LAM_PE/LAM_NE 사이에서 묻는 것과 같은 질문을, 저자는 **LAM_an ↔ 음극 내부
조성 변화** 축에서 발견했다.

---

## 9. p.6–8 — §4.3 세 곡선으로 재구성한 결과 ★ (질문 1·4 의 정량 답)

### 9.1 대표 사례 — 486 EFC 셀 (Fig. 4)

`[인쇄]` **그림 안에 벡터 텍스트로 찍힌 숫자** (Fig. 4 를 직접 Read 해 확인):

| 음극 곡선 | α_an | β_cat | α_cat | OCV RMSE | 100 % SOC 에서 |
|---|---|---|---|---|---|
| (a) **pristine** | **1.027** | **−0.190** | **1.216** | **9.9 mV** | "**Anode limiting**" |
| (b) **aged (측정)** | **1.056** | **−0.164** | **1.179** | **9.6 mV** | "Anode **not** limiting" |
| (c) **blend model** (γ_Si = 5.6 %) | **1.057** | **−0.159** | **1.174** | **8.2 mV** | "Anode **not** limiting" |

`[인쇄]` 물리적 해석의 차이:
- (a) pristine 곡선을 쓰면 full-cell DV 의 음극 feature 좌이동을 **곡선 압축**
  으로만 만들 수 있다 → **LAM_an 으로 해석**. 그 결과 100 % SOC 에서 음극 전위가
  이미 stage 2↔1 plateau 를 벗어나 **음극이 충전 종료를 제한**한다고 나온다.
- (b) aged 곡선은 **half-cell 수준에서 이미 좌이동**해 있으므로 **압축이 덜**
  필요하다.
- (c) blend 모델은 좌이동의 일부를 **γ_Si 를 줄여 half-cell 수준에서** 실현한다.
- (b)(c) 에서는 **음극이 충전 종료를 제한하지 않는다** (전위가 아직 plateau 안).

`[해석] ★ 여기가 가장 날카롭다.` **RMSE 차이는 9.9 → 9.6 → 8.2 mV (최대
1.7 mV)** 인데, **"충전 종료를 제한하는 전극이 어느 쪽인가" 라는 정성적 결론이
뒤집힌다.** 데이터 적합도로는 세 모델을 거의 구별할 수 없는데 물리 결론은
반대다 — 교과서적인 축퇴 시연이다.

### 9.2 전 aging state 의 RMSE (Fig. 5)

`[도표]` Fig. 5 를 직접 Read 해 읽은 근사값 (원 데이터가 아니다):

| EFC | pristine | aged | blend |
|---|---|---|---|
| 9 | ≈ 4.9 | ≈ 4.9 | ≈ 4.2 |
| 54 | ≈ 4.05 | ≈ 3.65 | ≈ 2.9 |
| 101 | ≈ 7.6 | ≈ 4.15 | ≈ 3.5 |
| 361 | ≈ 11.85 | ≈ 11.4 | ≈ 7.8 |
| 410 | ≈ 9.8 | ≈ 7.75 | ≈ 6.5 |
| 444 | ≈ 10.5 | ≈ 10.45 | ≈ 7.25 |
| 486 | ≈ 9.95 | ≈ 9.6 | ≈ 8.25 |

`[인쇄]` 저자의 해석: RMSE 는 사이클링과 함께 **증가 추세**(전극 불균일 증가
[43,44] 가 모델에 없기 때문일 수 있다). 그러나 **항상 12 mV 미만**이므로
"**세 종류 음극 곡선 모두, 모든 aging state 에서 좋은 일치**" 이며,
`[인쇄]` "aging-related changes in the full-cell OCV curve **can be accurately
described with the model regardless of whether changes in the anode half-cell
OCP are considered**. **But while having a small impact on fit accuracy**, the
consideration of changes in the half-cell OCP shape **influences the
quantitative results for the alignment parameters** and therefore the
interpretation."

`[해석] ★ 저자가 스스로 적은 이 문장이 우리 프로젝트의 명제와 동일하다`:
**적합도는 모델 선택을 구별하지 못하지만 파라미터(=모드)는 크게 달라진다.**
특히 361 EFC 에서 pristine 11.85 vs aged 11.4 (**Δ = 0.45 mV**) 인데 LAM_an 은
12.7 % vs 10.3 % (**Δ ≈ 2.4 pp**) 다 `[도표]`.

### 9.3 정렬 파라미터 4개의 궤적 (Fig. 6) — ★ 부호가 뒤집히는 곳

`[도표]` Fig. 6 을 직접 Read 해 읽은 근사값:

| 파라미터 | pristine 상태 (≈9 EFC) | 486 EFC · pristine 곡선 | 486 EFC · aged 곡선 | 486 EFC · blend |
|---|---|---|---|---|
| **α_an** | ≈ 1.041 | ≈ **1.027 (감소)** | ≈ **1.056 (증가)** | ≈ **1.057 (증가)** |
| **β_an** | ≈ −4.5×10⁻³ | ≈ −5.5×10⁻³ | ≈ −5.65×10⁻³ | ≈ −5.25×10⁻³ |
| **α_cat** | ≈ 1.066 | ≈ 1.216 | ≈ 1.180 | ≈ 1.174 |
| **β_cat** | ≈ −0.051 | ≈ −0.190 | ≈ −0.164 | ≈ −0.159 |

`[인쇄]` 본문 서술:
- pristine 상태에서 **음극 용량은 full-cell 대비 약 4 % 크다** (α_an ≈ 1.04);
  이 셀 타입의 "거의 완전한 음극 활용"은 문헌 [31] 과도 일치.
- **★ 추세의 방향이 갈린다**: pristine 곡선을 쓰면 α_an 이 **감소**,
  aged/blend 곡선을 쓰면 α_an 이 **증가**한다. 저자의 해석 `[인쇄]`:
  "this does **not** mean that there is an increase in absolute anode capacity.
  Rather, it should be interpreted such that **less of the anode capacity is
  used within the voltage limits of the full-cell due to LLI**."
- **β_an 은 항상 0 에 가깝다 (|β_an| < 0.6 %)** → `[인쇄]` "the anode is always
  limiting the usable full-cell capacity at the **lower** cut-off voltage."
  세 곡선 종류 사이 차이는 **< 0.12 pp** 이고 `[인쇄]` "probably due to the
  fitting and **have no physical significance**".
- pristine 상태에서 **양극 용량은 full-cell 대비 약 7 % 크다** (α_cat ≈ 1.07,
  문헌 [31] 과 일치). α_cat 은 aging 과 함께 **증가** = 양극 용량 중 쓰이는
  비율이 줄어든다 (LLI 탓으로 추정).
  `[인쇄]` **중열화 셀(≥361 EFC) 에서 형상 변화를 고려하면 α_cat 이 2 pp 이상
  작다.**
- β_cat 은 pristine 에서 **약 −5 %** → 양극이 full-cell 하한 전압에서 완전
  lithiated 되지 않는다. aging 과 함께 **더 감소**(좌이동) = LLI 로 balancing
  이 이동 [16]. 형상 변화를 고려하면 **감소폭이 작아진다**.

`[해석] ★ 이 표에서 읽히는 축퇴 방향 (우리 좌표로)`:
486 EFC 에서 pristine → blend 로 바꿀 때 파라미터가 움직인 방향은
```
Δα_an ≈ +0.030,  Δα_cat ≈ −0.042,  Δβ_cat ≈ +0.031,  Δβ_an ≈ +0.25×10⁻³
```
즉 **α_an 을 키우면 α_cat 을 줄이고 β_cat 을 올려서 상쇄**하는 것이 거의 같은
DV 를 준다. 이것이 **4-파라미터 공간의 평평한 골짜기 방향**이며, γ_Si 라는
5번째 축이 그 골짜기 위 어디에 앉을지를 정한다.

---

## 10. p.8 — §4.4 full-cell OCV 만으로 γ_Si 를 추정 (질문 4 의 실제 검증)

`[인쇄]` 두 접근의 역할 분담을 저자가 명시한다:
- **aged half-cell OCP 를 측정해 쓰는 것** = 형상 변화의 영향을 **실험적으로
  분석**하기 위한 것.
- **blend 모델 합성 곡선** = **진단 방법으로 쓰기 위한 것** (실험 부담이 적다.
  aged half-cell 측정이 **불필요**).

`[인쇄]` 절차: pristine 순수 graphite + 순수 Si (문헌 [38]) 곡선으로 blend 음극
OCP 를 만들고, **γ_Si 와 4개 정렬 파라미터를 함께 최적화**해 측정 full-cell OCV
의 DV 와의 차이를 최소화.

`[인쇄]` **결과 (Fig. 7)** — 이 논문의 **유일한 교차 검증**:
- full-cell OCV 로 추정한 γ_Si 와 half-cell OCP 로 추정한 γ_Si 의 차이가
  **모든 aging state 에서 0.8 pp 미만**.
- full-cell 기반 값이 **체계적으로 약간 높다**.
- **pristine 10.3 %**, **486 EFC 5.6 %**.
- 식 (16) 으로 환산한 pristine 음극의 **Si 질량 분율 1.1 %**.

`[도표]` Fig. 7 을 직접 Read 해 읽은 근사값 (γ_Si / %):

| EFC | half-cell 기반 | full-cell 기반 | 차이 |
|---|---|---|---|
| 9 | ≈ 9.55 | ≈ 10.3 | ≈ 0.75 |
| 54 | ≈ 8.45 | ≈ 9.0 | ≈ 0.55 |
| 101 | ≈ 7.8 | ≈ 8.5 | ≈ 0.7 |
| 361 | ≈ 5.85 | ≈ 6.25 | ≈ 0.4 |
| 410 | ≈ 5.95 | ≈ 6.15 | ≈ 0.2 |
| 444 | ≈ 5.2 | ≈ 5.5 | ≈ 0.3 |
| 486 | ≈ 5.55 | ≈ 5.65 | ≈ 0.1 |

`[인쇄]` 방법의 장점 주장: 비파괴, 실행 용이, ICP-OES [31]·EDS [26] 와 달리
**전기화학적으로 활성인 Si 만** 잰다, 총 Si 질량은 aging 중 변하지 않으므로
[26] **Si 의 열화를 볼 수 있는 유일한 축**이다.

`[해석] ★ 질문 4 의 답의 실체`: 이 교차 검증은 **모드(LAM/LLI)를 검증하지
않는다**. 검증되는 것은 **γ_Si 라는 하나의 파라미터**이고, 그것도 양쪽이
**같은 blend 모델과 같은 DV 목적함수**를 공유한다 (다른 것은 입력 곡선이
full-cell 이냐 half-cell 이냐뿐). 즉 **부분적으로 독립적인 교차 확인**이지
ground truth 대조가 아니다. 그리고 full-cell 기반 값이 **모든 점에서 위로**
치우친 것은 무작위 오차가 아니라 **계통 편향**의 서명이다 — 저자는 이 편향의
원인을 논하지 않는다.

---

## 11. p.8–9 — §4.5 열화 모드 결과 ★ (질문 1 의 최종 수치)

### 11.1 LAM_an (Fig. 8(a))

`[인쇄]` 본문 §4.5:
- 형상 변화를 고려하면 **486 EFC 에서 LAM_an = 13.1 %**;
  pristine 곡선을 쓰면 **15.5 %**.
- aged 곡선과 blend 모델의 LAM_an 값은 **서로 매우 유사**.
- `[인쇄]` "the loss of anode material is probably **overestimated by something
  in the order of a few percentage points** if no changes in the shape of the
  silicon–graphite OCP are considered."

`[도표]` Fig. 8(a) 에서 읽은 근사값 (LAM_an / %):

| EFC | pristine | aged | blend |
|---|---|---|---|
| 9 | 0 | 0 | 0 |
| 54 | ≈ 2.1 | ≈ 0.6 | ≈ 1.3 |
| 101 | ≈ 2.6 | ≈ 0.7 | ≈ 1.4 |
| 361 | ≈ 12.7 | ≈ 10.3 | ≈ 10.3 |
| 410 | ≈ 11.0 | ≈ 7.3 | ≈ 7.9 |
| 444 | ≈ 13.3 | ≈ 10.8 | ≈ 11.1 |
| 486 | ≈ 15.6 | ≈ 13.0 | ≈ 13.1 |

**★ 본문 ↔ 그림 불일치 (원문의 오류로 보인다)** `[해석]`:
§4.5 의 LAM_cat 문단에 `[인쇄]` "if the measured aged anode curves are used,
**5.3 % LAM_cat and 15.5 % LAM_an** are estimated for the cell cycled for
486 EFC" 라는 문장이 있다. 그러나
(i) 같은 절 앞부분은 **형상 변화 고려 시 13.1 %**, **pristine 곡선 사용 시
15.5 %** 라고 적었고,
(ii) Fig. 8(a) 에서 486 EFC 의 aged-anode 점은 **≈ 13 %** 이지 15.5 % 가 아니다.
LAM_cat 쪽 5.3 % 는 Fig. 8(b) 의 aged 점과 맞는다.
→ **"15.5 % LAM_an" 은 pristine-곡선 값을 잘못 옮긴 것으로 보인다.**
이 문장만 인용하면 논문의 논지(형상 고려 시 LAM_an 이 **낮아진다**)와
**정반대** 값을 인용하게 된다.

### 11.2 LAM_cat (Fig. 8(b))

`[인쇄]`
- **첫 100 EFC 동안 LAM_cat 이 음수** (= 양극 용량이 약간 증가). pristine 음극
  곡선을 쓰면 그 증가가 **더 두드러진다**.
- 100 EFC 이후 증가.
- **≥361 EFC 에서 pristine 곡선을 쓰면 LAM_cat 이 약 3 pp 낮다** →
  "**양극 용량 감소를 약간 과소평가**".
- 전체적으로 LAM_cat ≪ LAM_an (문헌 [29,43,44] 과 일치).

`[도표]` Fig. 8(b) 근사값 (LAM_cat / %):

| EFC | pristine | aged | blend |
|---|---|---|---|
| 54 | ≈ −2.0 | ≈ −0.2 | ≈ −1.1 |
| 101 | ≈ −2.6 | ≈ −0.5 | ≈ −0.6 |
| 361 | ≈ 0.2 | ≈ 2.8 | ≈ 5.1 |
| 410 | ≈ 0.35 | ≈ 3.1 | ≈ 3.9 |
| 444 | ≈ 0.1 | ≈ 3.2 | ≈ 5.0 |
| 486 | ≈ 2.3 | ≈ 5.3 | ≈ 6.5 |

`[해석]` **음수 LAM_cat 은 물리적으로 불가능하다** (양극 활물질이 늘어날 수
없다). 저자는 "slight increase in cathode capacity" 라고만 적고 **추정 오차의
증거로 읽지 않는다.** 우리 관점에서 이것은 **추정량의 편향·분산이 최소 2–3 pp
규모**라는 직접적 증거다 — 그리고 그 크기는 이 논문이 주장하는 효과 크기
(2.4 pp, 3 pp, 1.1 pp) 와 **같은 자릿수**다.

### 11.3 LLI (Fig. 8(c))

`[인쇄]`
- LLI 는 사이클링과 함께 증가.
- **LLI 추정치가 Table 1 의 상대 용량 손실과 매우 유사**하다.
- 모든 aging state 에서 상한 cut-off 까지 delithiate 가능한 Li 양이 full-cell
  전압창 안에서 쓰이는 양보다 **약간만** 많다 → **aging 내내 유의한 LLI**.
- **형상 변화를 고려하면 LLI 가 최대 1.1 pp 높다.**

`[도표]` Fig. 8(c) 근사값 (LLI / %): 486 EFC 에서 pristine ≈ 13.2,
aged ≈ 14.2, blend ≈ 14.2. (Table 1 의 ΔC = **14.3 %** 와 비교.)

`[해석] ★ 식 (11) 의 닫힌 형태로 이 결과를 재현해 봤다` (검산):
`C_lit = (α_cat + β_cat − β_an)·C_full` 과
`LAM = 1 − (α·C_full)/(α_ini·C_full,ini)` 에 §9.3 의 `[도표]` 값과 Table 1 의
`C_full` (pristine 3.40 Ah, 486 EFC 2.91 Ah) 을 넣으면:

| 양 | pristine 곡선 | blend 곡선 | 논문 값 |
|---|---|---|---|
| LAM_an | 15.6 % | 13.1 % | 15.5 % / 13.1 % ✔ |
| LAM_cat | 2.4 % | 6.5 % | ≈2.3 % / ≈6.5 % ✔ |
| LLI | 13.4 % | 14.3 % | ≈13.2 % / ≈14.2 % ✔ |

→ **§4 에서 옮겨 적은 정의식들이 논문의 그림 수치를 재현한다.** 우리 MATLAB
코드의 후처리(α·β → 모드)를 대조할 때 이 검산 경로를 그대로 쓸 수 있다.
특히 **LLI 가 α_an 에 전혀 의존하지 않는다**는 것과 **LAM 계산에 C_full 이
반드시 들어간다**는 두 가지가 구현 오류가 잘 나는 지점이다.

### 11.4 §4.5 요약 문장

`[인쇄]` "Considering aging-induced changes in the shape of the anode half-cell
curve leads to **lower estimates for LAM_an and higher estimates for LAM_cat
and LLI**, and improves the validity of the estimates."

---

## 12. p.9–10 — Conclusion / Appendix / 부대 정보

`[인쇄]` 결론의 실질 4줄:
1. SiC OCP 형상 변화는 **blend 전극 모델로 기술 가능**하다.
2. half-cell OCP 로부터 **γ_Si: pristine 약 9.5 % → 488 EFC 약 5.5 %** —
   "**The silicon therefore degrades faster than the graphite**".
3. `[인쇄]` "An accurate reconstruction of aged full-cell OCV curves can be
   obtained by shifting and scaling half-cell OCP curves **regardless of**
   whether aging-related changes in the shape of the SiC OCP are considered or
   not. **Still, the validity of the degradation mode estimates… can be
   improved by considering** aging-induced changes."
   → 형상 무시 시 **LAM_an 은 약간 과대, LAM_cat 과 LLI 는 약간 과소**.
4. full-cell 저전류 충전 곡선만으로 **γ_Si 추정 가능** = 비파괴 성분별 열화 진단.

`[인쇄]` 남긴 과제: "how the proposed method performs using only **partial
charging curves** or charging curves obtained at **higher current rates**".

`[인쇄]` **Appendix** (식 A.1–A.9): 식 (16) 의 유도.
`C_Si = γ_Si·C_blend = m_Si·c_Si`, `C_G = m_G·c_G`,
`C_blend = C_Si + C_G`, `M_blend = m_Si + m_G` 를 연립해 정리.

`[인쇄]` **Table 1** (PDF 텍스트에서 읽음, 이미지로 보지 않음):

| Cycles | Q_tot / EFC | C_full / Ah | ΔC / % |
|---|---|---|---|
| 0 | 9 | 3.40 | 0 |
| 50 | 54 | 3.35 | 1.5 |
| 100 | 101 | 3.30 | 2.9 |
| 400 | 361 | 3.01 | 11.6 |
| 450 | 410 | 3.06 | 10.0 |
| 500 | 444 | 2.99 | 11.9 |
| 550 | 486 | 2.91 | 14.3 |

`[해석]` **ΔC 가 사이클 수에 대해 단조가 아니다** (400 cy → 11.6 %,
450 cy → 10.0 %). 각 행이 **다른 셀**이기 때문이다. 이 비단조성이 Fig. 6·8 의
410 EFC 점에서 보이는 "튐" 의 원인이며, 그 크기가 **논문이 주장하는 효과 크기와
비슷하다** — 즉 **셀간 편차가 모델 선택 효과와 뒤섞여 있다**.
또한 half-cell 서술은 **488 EFC**, full-cell 서술은 **486 EFC** 로 같은 셀을
두 숫자로 부른다 (Table 1 은 486).

---

## 13. 실제로 본 그림 (무엇을 어떻게 읽었는지)

크로핑된 9장 (fig 8 + tab 1) 중 **fig_1 ~ fig_8 전부를 Read 로 직접 보았다**.
`tab_1.png` 만 이미지로 보지 않았다 (PDF 텍스트가 정확).

| 파일 | 무엇을 확인했나 | 본문과 어긋남 |
|---|---|---|
| `fig_1.png` | (a) α·β 의 기하학적 의미 — α_cat 은 전체 폭 화살표, β_cat 은 0 % 왼쪽 짧은 화살표, **β_an ≈ 0 라벨**. 음극 곡선이 x_full = 0 에서 ≈1.2 V 로 시작해 감소. (b) 흐름도: 세 종류 음극 OCP → "Fitting of full-cell differential voltage" ← pristine 양극 OCP + 측정 aged full-cell OCV → 정렬 파라미터 → 모드. (c) C_lit 모식도: 양극·음극 막대에 −β, x_full,ref, α_cat 구간 표시 | 없음. 단, (a) 의 양극 곡선 좌측 끝이 ≈3.5 V 에서 시작해 보이는데 β_cat ≈ −5 % 지점의 x_cat = 0 은 정의상 3.0 V 다 — **곡선이 그 근처에서 극도로 가팔라 렌더 범위 밖으로 보이는 것**으로 판단 |
| `fig_2.png` | (a) graphite·Si·SiC 측정 + blend 계산 곡선, x = normalized capacity, "Lithiation" 화살표 = 전위 감소 방향. Si 곡선이 graphite 보다 **높은 전위**에서 용량을 낸다 (0.2–0.3 V 대). (b) pristine vs 488 EFC, "Reduced silicon capacity"(≈0.21 V 부근)·"Graphite stages 4L-2L" 좌향 화살표 2개. (c) γ_Si vs EFC: 9.55 → 5.2 (444 EFC) 최저, 486 에서 5.55 로 반등 | 없음 |
| `fig_3.png` | (a) OCV 2.5–4.25 V, 7개 aging state (9~486 EFC). 곡선들이 **거의 겹친다**. (b) 정규화 DV, y = dU/dQ⁻¹·C_full / V, 라벨 4개(Silicon phases / Graphite 4L-2L / NMC-811 M-phase / Graphite stage 2 / NMC-811 H2-phase) 와 **좌향 화살표** | 없음. (a) 에서 "절대 전압 상승" 은 **육안으로는 매우 작다** — 본문 주장보다 그림이 약하다 |
| `fig_4.png` | **α_an·α_cat·β_cat·RMSE 가 그림 안에 숫자로 인쇄**돼 있다 (§9.1 표). "Anode limiting" ↔ "Anode not limiting" 라벨 대비 | 없음 — 오히려 본문보다 정보가 많다 |
| `fig_5.png` | 3계열 RMSE vs EFC (§9.2 표). blend 가 **모든 점에서 최저** | 없음 |
| `fig_6.png` | 4-panel 정렬 파라미터 (§9.3 표). **β_an 축이 ×10⁻³ 단위**라는 것이 여기서만 확인된다 | 없음 |
| `fig_7.png` | γ_Si: half-cell 기반 vs full-cell 기반 (§10 표). full-cell 값이 **7개 점 전부에서 위** | 없음 |
| `fig_8.png` | LAM_an / LAM_cat / LLI 3-panel + "Lower estimate for LAM_an" 등 주석 화살표 | **있다** — §11.1 의 "15.5 % LAM_an (aged curves)" 문장이 그림과 모순 |

---

## 14. 비판 (이 저장소 기준)

1. **★ ground truth 가 없는데 "validity" 를 주장한다.** 논문은 "improves the
   **validity** of the determined degradation modes" 를 highlight·abstract·
   결론에서 반복한다. 그러나 검증된 것은 (i) OCV 재구성 RMSE 가 **1.7 mV**
   낮아진다, (ii) γ_Si 가 두 경로에서 **0.8 pp 이내로** 일치한다, 두 가지뿐이다.
   **LAM_an = 13.1 % 가 15.5 % 보다 참에 가깝다는 독립 증거는 이 논문에 없다.**
   논지는 "물리적으로 더 그럴듯한 모델이므로 더 타당하다" 는 **모델 선택 논증**
   이지 측정 논증이 아니다.
2. **★ 오차 막대가 하나도 없다.** aging state 당 셀 1개. 그런데 주장하는 효과
   크기는 2.4 pp (LAM_an), 3 pp (LAM_cat), 1.1 pp (LLI) 다. 같은 그림 안에서
   **LAM_cat 이 −2.6 % 까지 음수로 내려간다** (물리적 불가) — 즉 **추정 잡음이
   효과 크기와 같은 자릿수**임을 논문 자신의 데이터가 보여준다.
3. **★ 축퇴를 발견해 놓고 축퇴로 부르지 않는다.** §4.2 의 "both effects would
   lead to the same results with regard to the full-cell OCV" 는 정확히
   비식별성 진술이다. 그런데 identifiability·degeneracy·parameter correlation
   ·confidence region 중 **어느 단어도 논문에 없다**. 해법도 "물리적으로 옳은
   곡선을 넣자" 이지 "얼마나 갈리는지 재자" 가 아니다.
4. **γ_Si 를 5번째 자유 파라미터로 넣으면서 새 축퇴를 검사하지 않았다.**
   γ_Si ↓ 와 α_an ↓ 는 §4.2 에서 저자 스스로 "같은 서명" 이라고 했다. 그렇다면
   둘을 **동시에** 자유롭게 둔 5-파라미터 fitting 은 정의상 **거의 평평한
   방향**을 갖는다. 그런데 Fig. 7 의 γ_Si 는 오차 막대 없이 단일 값으로 제시된다.
   (완화 요인: full-cell 기반 γ_Si 가 독립적으로 얻은 half-cell 기반 γ_Si 와
   0.8 pp 이내로 맞는다 — 이건 실질적인 방어다. 다만 **계통 편향**이 남는다.)
5. **Si OCP 를 남의 논문(결정질 Si, Li & Dahn 2007)에서 가져왔다.** 대상 셀의
   활물질은 SiO_x 다. 이 치환이 γ_Si 절대값에 주는 오차를 정량하지 않는다.
   γ_Si 의 **추세**는 이 오차에 상대적으로 강건하겠지만 **절대값(9.5 %, 1.08
   wt.%)** 은 그렇지 않다.
6. **DV 목적함수의 선택이 결과에 미치는 영향을 검사하지 않았다.** 절대 OCV 를
   쓰면 α·β 가 달라질 수 있다. 한 줄의 민감도 분석도 없다.
7. **초기값·경계·다중 시작점이 보고되지 않았다.** 5-파라미터 비선형 최소제곱
   결과를 재현하려면 필수 정보인데 없다. 코드·데이터 공개도 없다.
8. **`C_full` 정의가 미묘하다** `[인쇄]`: "the charge throughput during
   low-current charging after cycling and prior to cell opening is taken as the
   value of the remaining full-cell capacity". 즉 C/30 **충전** 용량이다.
   모드 계산 전체가 이 값에 비례하므로 (§11.3 검산 참조) 정의가 다르면 모든
   모드 수치가 함께 움직인다.

`[해석]` **그럼에도 이 논문은 실험 설계에서 정직하다.** 같은 셀에서 full-cell
OCV 와 aged half-cell OCP 를 **둘 다** 확보해 "형상 불변 가정이 정말 깨지는가"
를 실험으로 물었고, 깨진다는 것을 보였고, 그 결과 자기 방법의 기존 결론
(LAM_an 크기)이 **틀렸었다고** 적었다. 이 계보에서 흔치 않다.

---

## 15. 우리 프로젝트와의 접점

### 15.1 사용자 질문 4개에 대한 직답

**Q1. 형상 불변 전제가 어디서 깨지고, 저자는 그것을 어떻게 정량했는가.**
- **깨지는 지점**: 음극이 **blend(SiC)** 일 때. Si 가 graphite 보다 빨리
  열화하면 두 성분의 **용량 기여 비율 γ_Si** 가 바뀌고, blend OCP 는 두
  성분 곡선의 **역함수 합성**(식 14–15)이므로 **모양 자체가 바뀐다**.
  α·β 는 곡선을 **아핀 변환**만 하므로 이 변화를 표현할 수 없다.
  (양극 NMC-811 은 형상이 유지된다 — 선행 논문 [22].)
- **정량 지표**: 곡선 오차가 아니라 **γ_Si 의 이동**.
  `γ_Si: 9.52 % → 5.55 %` (488 EFC, half-cell 측정 기준; **초기값의 58 %**).
  blend 모델은 이 변화를 **RMSE < 6.9 mV** 로 재현한다.
- **깨짐이 full-cell 에서 만드는 크기** (486 EFC):
  `ΔLAM_an ≈ −2.4 pp` (15.5 → 13.1), `ΔLAM_cat ≈ +3 pp`,
  `ΔLLI ≈ +1.0~1.1 pp`, `Δα_an ≈ +0.030`, `Δα_cat ≈ −0.042`,
  `Δβ_cat ≈ +0.031`. 그리고 **정성적 결론이 뒤집힌다** — "충전 종료를 제한하는
  전극" 이 음극 → 양극.
- **적합도로는 거의 구별되지 않는다**: OCV RMSE 9.9 → 8.2 mV.

**Q2. 저자가 제안한 보정/대안과 그 대가.**
- **곡선을 상태별로 다시 재는 것**(aged half-cell 측정)은 **분석용**으로만
  쓴다 — 셀을 뜯어야 하므로 진단법이 될 수 없다.
- **제안된 방법은 세 번째 것**: pristine **순수 graphite** + pristine **순수
  Si** OCP 로 **blend 모델(식 14–15)** 을 세우고, **γ_Si 를 다섯 번째 자유
  파라미터로 두어 4개 정렬 파라미터와 동시에 최적화**한다.
  → 즉 **"γ_Si 를 자유 파라미터로 둔다" 가 정답**이다.
- **대가**:
  (a) 자유도 4 → 5, 그리고 §4.2 에서 저자 스스로 인정하듯 γ_Si 와 α_an 은
      full-cell 에 **같은 서명**을 남긴다 → 새 축퇴 위험 (저자는 미검사).
  (b) **성분별 pristine OCP 곡선이 필요**하다 (여기서는 Si 를 문헌에서 차용).
  (c) blend 모델은 두 성분의 **평형·병렬 lithiation** 을 가정한다 (kinetic
      상호작용·히스테리시스 없음).
  (d) 역함수를 취하기 위해 graphite 곡선의 국소 최소점을 **손으로 제거**해야
      한다.
  (e) 이득은 RMSE 1~4 mV 수준으로 작다 — 즉 **데이터가 이 선택을 강하게
      지지하지 않는다**. 선택의 근거는 물리적 타당성이다.

**Q3. 모드 정의식과 좌표 규약.** → §4.1–4.3 에 전부. 요약:
```
x_full = α_an·x_an + β_an          x_an : 0 = delithiated(1.7 V), 1 = lithiated(0.01 V)
x_full = α_cat·x_cat + β_cat        x_cat: 0 = lithiated(3.0 V),  1 = delithiated(4.3 V)
스케일 원점 = 전극 SOC 0 %.  β_an, β_cat < 0 (항상 좌이동).
C_an = α_an·C_full;   LAM_an = (C_an,ini − C_an)/C_an,ini
C_lit = (α_cat + β_cat − β_an)·C_full;   LLI = (C_lit,ini − C_lit)/C_lit,ini
```
목적함수 = **DV 차이 제곱합**, 2001 점, Δx = 0.2 %, 양끝 1 % 제외,
`lsqnonlin` trust-region-reflective.

**Q4. 검증 방법과 오차.**
- **모드에 대한 ground truth 는 없다.** 아래 4개가 저자가 보고한 전부다:
  1. **OCV 재구성 RMSE**: 전 aging state·전 곡선종류에서 **< 12 mV**;
     486 EFC 에서 9.9 / 9.6 / **8.2** mV (pristine / aged / blend).
  2. **half-cell OCP 재구성 RMSE**: pristine **6.6 mV**, 전 aging state **< 6.9 mV**.
  3. **γ_Si 교차 확인**: full-cell 기반 vs half-cell 기반 차이 **< 0.8 pp**
     (단, full-cell 쪽이 **7/7 점 모두 위** = 계통 편향).
  4. **질량 정합성**: 계산 코인셀 용량 7.84 mAh vs 측정 7.40 mAh → **< 6 %**.
- **오차 막대·반복 fitting·감도 분석·식별 가능성 진단: 전부 없음.**

### 15.2 이 저장소가 이 논문에서 가져올 것 / 이 논문에 공급할 수 있는 것

`[해석]`

**가져올 것**:
1. **α·β 만으로는 표현 불가능한 열화 축이 실재한다는 실험 증거.** 우리
   [[fitting-degeneracy]] 판정은 "α·β(=우리 좌표) 안에서" 두 전극이 갈리는가를
   묻는다. 이 논문은 그 **좌표 자체가 불완전**할 수 있음을 보인다 — 모델
   오설정(model misspecification)이 축퇴와 **구별되지 않는 형태**로 편향을
   만든다.
2. **LLI 가 α_an 에 의존하지 않는다는 구조** (식 11 의 닫힌 형태). 우리
   축퇴 방향 해석에 바로 쓸 수 있는 구조적 사실이다.
3. **"적합도는 같은데 결론이 뒤집힌다" 의 실측 사례** — 1.7 mV 차이로
   "limiting electrode" 가 바뀐다. 우리 결과를 발표할 때 인용 가능한 **외부
   독립 사례**다.
4. **음의 LAM_cat** 을 추정기 잡음의 하한 증거로 쓸 수 있다.

**공급할 수 있는 것 (이 논문이 비어 있는 곳)**:
1. **γ_Si 를 5번째 파라미터로 넣었을 때 (α_an, γ_Si) 평면의 축퇴 지도.**
   저자가 §4.2 에서 "같은 서명" 이라고 쓰고도 재지 않은 바로 그것을,
   우리 프레임(합성 truth + 격자 스윕)으로 **재는 것이 가능하다**.
2. **오차 막대**: 같은 DV 목적함수·같은 5-파라미터에 대해 CRB/프로파일 우도로
   `[LAM_an, LAM_cat, LLI, γ_Si]` 의 식별 가능성 경계를 계산해 줄 수 있다.
3. **목적함수 감도**: DV vs 절대 OCV 가 α·β 추정치를 얼마나 옮기는지.

**우리 MATLAB 코드 검증에 직접 쓸 체크리스트** `[해석]`:
- [ ] `b_PE`, `b_NE` 가 **항상 음수**로 나오는가 (이 논문 규약). 부호가 반대면
      좌표 규약이 다른 것이고 모드식도 함께 바뀌어야 한다.
- [ ] `a_NE` 의 pristine 값이 **1.0 근처(≈1.04)**, `a_PE` 가 **≈1.07** 인가.
      크게 다르면 half-cell 전압창 정의(1.7/0.01, 3.0/4.3 V)가 다른 것이다.
- [ ] `|b_NE|` 가 **0.6 % 미만**인가 (음극 제한 셀). 이 논문 값은 4–6×10⁻³ 다.
- [ ] LAM 계산에 **각 aging state 의 `C_full`** 이 들어가는가
      (`LAM = 1 − a·C_full/(a_ini·C_full,ini)`). 빠뜨리면 α 비만 보게 된다.
- [ ] LLI 가 `(a_PE + b_PE − b_NE)·C_full` 로 계산되는가 (α_an 미포함).
- [ ] 목적함수가 **DV** 인가 **OCV** 인가 — 이 논문 수치와 비교하려면 DV 여야 한다.
- [ ] `γ_Si` 를 자유롭게 둘 때 `a_NE` 와의 상관을 **뽑아 보는가** (이 논문은 안 함).

---

## 16. 한 줄 결론

**"pristine half-cell 곡선을 α·β 로 늘이고 옮긴다" 는 전제는 blend 음극에서
성분 비율이 변하면 깨지고, 깨졌을 때 데이터 적합도는 거의 변하지 않는 채
(9.9 → 8.2 mV) 모드 분해가 방향성 있게 편향된다 (LAM_an −2.4 pp,
LAM_cat +3 pp, LLI +1.1 pp) — 심지어 "어느 전극이 충전을 제한하는가" 가
뒤집힌다.** 저자의 해법은 곡선을 다시 재는 것이 아니라 **γ_Si 를 다섯 번째
자유 파라미터로 두는 것**이고, 그 대가로 저자 자신이 "같은 서명을 남긴다" 고
인정한 두 축(α_an, γ_Si)을 동시에 자유롭게 두면서도 **그 축퇴는 재지 않았다**.
우리 프로젝트가 설 자리가 정확히 거기다.
