---
title: "Wang, Xiong, Shen, Sun 2025 — Aging-induced, rate-independent Lithium plating: A complete mechanism analysis throughout the battery lifecycle (Applied Energy 393, 126094)"
source_url: local-upload/19_aging_induced_rate_independent_lithium_plating.pdf
ingested: 2026-09-11
sha256: 0d152b1746f4600868769014d81c2ef9e61a5ebf1a326263db11c7a03197151e
---

# 수집 목적

Peng Wang, Rui Xiong (교신), Weixiang Shen, Fengchun Sun,
**"Aging-induced, rate-independent Lithium plating: A complete mechanism analysis
throughout the battery lifecycle"**, *Applied Energy* **393** (2025) 126094 의
**절별 해체분석**.

이 저장소가 이 논문을 흡수하는 이유는 세 가지다.

1. **열화 모드 3개(LLI·LAM_PE·LAM_NE) 바깥의 네 번째 현상**이 full-cell OCV 에
   어떤 서명을 남기는지를 실셀로 보여 준다 — 음극 활물질이 리튬 재고보다 작아져
   (`Q_NE < Q_Li`) 0.05 C 에서도 생기는 **무율(rate-independent) 리튬 도금**.
   `bms-balancing/` 의 새 독자 모델 요구서(관측 → 후보 원인 → 구분 시험 → 채택
   기준 → 한계)가 "α·β 아핀 변환으로 안 맞는 잔차가 나오면 무엇을 의심할 것인가"
   에 답하려면 이 서명이 필요하다.
2. **아핀 창 매개화(`K_NE, K_PE, S_NE, S_PE`)가 실제로 깨지는 장면**이 인쇄돼 있다
   (Fig. 4b). [[halfcell-ocp-shape-invariance]] 가 Si/graphite blend 에서 본 것과
   같은 종류의 파괴를 **LFP/graphite 에서, 도금 때문에** 본다. 저자들의 처방은
   음극 곡선을 DV 극값으로 5 구간으로 잘라 **구간별 스케일링**하는 것 — 자유
   파라미터가 4 → 8 로 늘고, 식별 가능성은 묻지 않는다.
3. 모드 추정 궤적(Fig. 12)에 **음극 상단 가장자리가 관측 창 안으로 들어오는 순간**
   `Q_NE` 가 계단처럼 꺾이는 장면이 있다 — [[data-window-identifiability]] 가 말하는
   "창의 위치가 어느 전극을 보이게 하는지 고른다" 의 야생 실측 후보다.

**표기 규칙** (이 위키 관례 3구분 + 1):
- `[인쇄]` — 논문 본문/식/표에 글자로 있는 것
- `[도표]` — 그림에서 눈으로 읽은 근사값 (**원 데이터가 아니다**)
- `[해석]` — 이 문서를 쓰면서 붙인 판단. **논문의 주장이 아니다**
- `[재현]` — 원문 값을 이 세션에서 산술로 옮긴 것 (계산식을 함께 적는다)

- 원본 파일: 로컬 업로드 PDF `19_aging_induced_rate_independent_lithium_plating.pdf`
  (12쪽, 8,724,674 bytes, PDF sha256
  `37d51e5a41c66d79226c97a88d96a210159a92a90540e185782523bf65c7c67e`; 저장소에
  바이너리를 넣지 않는다)
- 크로핑 그림: `raw/figures/wang2025_aging-induced-rate-independent-li-plating/`
  (fig 12장 + tab 3장, `figures.json` 포함). 이 digest 를 쓰기 전에 **Fig. 2, 4, 5,
  6, 7, 9, 10, 11, 12 의 9장을 Read 로 직접 봤다.** Fig. 1(시험 절차 도식),
  Fig. 3(방법 개요 순서도), Fig. 8(SEM 사진) 은 안 봤다. 표 3장은 PDF 텍스트로 옮겼다.
- 페이지 참조는 PDF 페이지 = 저널 페이지 (1–12).
- 같은 성의 다른 논문과 혼동 주의: 이 위키의
  `raw/papers/wang2025_interpretable-ml-battery-prognosis.md` 는 **다른 Wang** (Adv.
  Energy Mater. 리뷰) 이다. 이 문서는 **Wang (Xiong 그룹, BIT) 2025** 로 부른다.

---

# 원문에 없어서 확인이 필요한 것 (읽기 전에 먼저 본다)

| # | 공백 | 왜 문제인가 |
|---|---|---|
| G1 | **모드 값에 오차 막대가 없다.** Table 3 의 `Q_NE`, `Q_Li` 네 점, Fig. 12 의 궤적 모두 불확실성 표기 0. | 8-파라미터 GA 적합의 결과를 점 하나로 인쇄한다. 다른 초기값에서 같은 값이 나오는지 아무 정보가 없다. |
| G2 | **GA 의 설정이 한 문장이다.** `[인쇄, §3.2]` "A genetic algorithm is used to identify these model parameters." — 탐색 범위·개체수·세대·초기값·수렴 기준·반복 횟수 전부 없음. | 재현 불가. 그리고 [[fitting-degeneracy]] 의 "평평한 골짜기" 위에서 GA 가 어디에 멈추는지는 설정에 달린다. |
| G3 | **식 (6) 의 조건이 인쇄된 대로는 뜻이 안 통한다.** `K_NE = max(SOC′(SOC′ ≥ 0))` — 조건이 전위가 아니라 `SOC′` 자신에 걸려 있다. | `[해석]` 가장 그럴듯한 독해는 "전위 ≥ 0 V 인 구간(구간 ①–④)의 `SOC′` 최댓값", 즉 **도금 구간 ⑤ 를 `Q_NE` 에서 제외**한다는 뜻. Fig. 12 에서 S3 구간의 `Q_NE` 가 `Cap` 보다 **작게** 그려지는 것이 이 독해와 맞는다 (도금된 Li 가 용량에는 들어가고 `Q_NE` 에는 안 들어간다). 그러나 확정은 못 한다. |
| G4 | **`Q_PE` 를 어디에도 인쇄하지 않는다.** Table 3 은 `Q_NE`, `Q_Li`, RMSE 만. 본문은 "cathode … degrades more slowly … left for future investigation" (§4.3). | LFP 양극의 평탄 OCP 는 창 하단 가장자리를 관측 창 밖에 둔다 → `K_PE` 는 원리적으로 약하게 식별된다. 인쇄하지 않은 것이 신중함인지 값이 이상했기 때문인지 알 수 없다 (§9.3 참조). |
| G5 | **SOH 의 기준이 없다.** 공칭 1.1 Ah 인지 초기 실측 용량(Fig. 12 `[도표]` ≈1.17–1.20 Ah)인지. | Table 3 의 SOH 와 `Q_NE`/`Q_Li` 를 용량과 대조하려면 필요하다 (§9.2 의 재현 산술이 이 가정에 걸린다). |
| G6 | **RPT 주기가 없다.** "Capacity calibration and OCV tests were performed regularly". | Fig. 10 점 간격이 `[도표]` ≈100 사이클로 보이지만 인쇄된 값이 아니다. |
| G7 | **재구성에 쓴 반쪽전지 곡선이 어느 SOH 의 것인지 없다.** 과방전 시험 곡선(도금 구간 포함)이 템플릿인 것은 §3.1 (3) 으로 알 수 있으나, fresh 전극인지 aged 전극인지 없다. | Fig. 2(d) 로 "OCP–SOC 관계는 노화해도 불변" 이라 주장하지만 그 그림의 세로 해상도(0–0.5 V) 로는 수 mV 차이를 못 본다. |
| G8 | **아핀 4-파라미터 적합의 RMSE 가 없다.** Fig. 4(b) 는 "안 맞는다" 를 그림으로만 보이고 수치가 없다. 제안법의 RMSE 2.7–9.1 mV (Table 3) 와 비교할 기준선이 없다. | "구간별 스케일링이 필요하다" 는 주장의 정량 근거가 빠져 있다. |
| G9 | **셀 형식·제조사·전극 조성이 없다.** "a lithium iron phosphate battery with a capacity of 1.1 Ah" 뿐. 음극이 순수 graphite 인지도 명시 없음 (반쪽전지 전압 범위 0/1.5 V 와 "graphite" 표기로 추정). | 다른 화학(NMC·Si/Gr)으로의 이식 범위를 정할 수 없다. |
| G10 | **Table 1 의 조건 표기 형식이 정의돼 있지 않다.** "1.5 A-3.5 V-2.2 A-2.0 V". | `[해석]` 충전전류–충전 상한–방전전류–방전 하한으로 읽힌다 (Table 2 도 같은 형식). |
| G11 | **비가역 도금 → LLI 수지가 없다.** 충전측 도금량 > 방전측 박리량이라는 차이(Fig. 10)를 "부분 비가역" 이라 말하지만, 그 차이를 `Q_Li` 감소와 대조하지 않는다. | "도금이 LLI 로 잡히는가" 에 이 논문이 직접 답하지 않는다 — §9.4 에 이 위키가 재구성한 회계를 둔다. |
| G12 | **방전측 박리량이 도금 검출 전부터 0 이 아니다.** Fig. 10(a)(b)(c)(f) 에서 충전측이 0 인 구간에도 방전측이 `[도표]` ≈0.014–0.022 Ah. | 방전 DV 골(valley) 정의가 도금 없는 셀에서도 값을 내는 것인지, 실제 박리인지 구분이 없다 (§6.2). |
| G13 | **데이터 비공개.** `[인쇄]` "Data will be made available on request." | 궤적을 우리 프레임에 얹으려면 저자 접촉 필요. |

---

## 0. 서지사항 (직접 확인)

`[인쇄]` PDF 메타데이터 및 헤더/푸터:

| 항목 | 값 |
|---|---|
| 제목 | Aging-induced, rate-independent Lithium plating: A complete mechanism analysis throughout the battery lifecycle |
| 저자 | Peng Wang ᵃ, Rui Xiong ᵃ (교신, rxiong@bit.edu.cn), Weixiang Shen ᵇ, Fengchun Sun ᵃ |
| 소속 | a: National Engineering Research Center of Electric Vehicles, School of Mechanical Engineering, Beijing Institute of Technology · b: School of Engineering, Swinburne University of Technology |
| 저널 | Applied Energy 393 (2025) 126094, doi 10.1016/j.apenergy.2025.126094 |
| 이력 | Received 12 March 2025 · Revised 23 April 2025 · Accepted 8 May 2025 · Available online 17 May 2025 |
| 키워드 | Lithium-ion battery · Lithium plating · Aging modes · Aging trajectory |
| 분량 | 12쪽 (본문 §1–5 + 참고문헌 30편), 그림 12, 표 3, SI 없음 |
| 자금 | National Key R&D Program of China 2024YFB2505003 |
| 데이터 | "available on request" |

---

## 1. 한 문단 요약

`[해석]` 1.1 Ah LFP/graphite 셀 17개를 6개 조건으로 사이클하면서 정기적으로
0.05 C 의사-OCV 를 찍었더니 **10개(58.8 %)** 에서 노화 후반에 충전 말단 고 SOC 에
새 전압 평탄역(LFP 에서 `[도표]` ≈3.46 V)이 생기고, 그 다음 방전 시작에 박리
평탄역(`[도표]` ≈3.40 V)이 짝으로 나타난다. 분해한 음극 반쪽전지를 0 V 아래로
과방전시켜 얻은 곡선(Fig. 2)이 이 평탄역의 정체 — 음극 전위가 `[도표]` ≈−0.015 V
에 머무는 **도금 구간** — 를 준다. 저자들은 이것을 **율 무관(rate-independent)
도금**이라 부른다: 원인이 과전위가 아니라 `Q_NE < Q_Li` (음극 활물질 손실이
리튬 재고를 밑돌아, 남는 Li 가 갈 곳이 없음) 이기 때문이다. 종래의 아핀
창 적합(스케일 2 + 이동 2)은 이 평탄역을 못 맞추므로(Fig. 4b), 음극 곡선을 DV
극값 4개로 5 구간으로 나누어 **구간마다 다른 스케일**을 두는 8-파라미터 적합을
GA 로 돌린다 (RMSE 2.7–9.1 mV, Table 3). 도금량은 DV 새 봉우리의 SOC 폭 × 용량으로
잰다 (식 7; 최대 31.5–118.5 mAh, Table 2). 모드 궤적(Fig. 12)에서는 `Q_NE` 가
`Q_Li` 를 가로지르는 순간이 용량 감소의 변곡점과 겹친다 — 저자들은 이를 "도금은
가속 열화의 결과이자 원인" 이라 결론 짓는다. **모드 값의 불확실성·유일성은 어디에도
없다.**

---

## 2. p.1–3 — Highlights / Abstract / §1 Introduction

### 2.1 Highlights `[인쇄]`

- "Electrode-level analysis unveils rate-independent lithium plating mechanisms via
  SEM imaging and multi-rate half-cell tests."
- "Lithium plating quantified during charge/discharge using DV analysis, highlighting
  its reversibility and role in capacity fade."
- "A phase-based method incorporates rate-independent lithium plating into aging
  analysis, achieving accurate OCV matching and early degradation detection."

### 2.2 Abstract 에서 뽑은 명제 `[인쇄]`

- "some reactions, such as aging-induced lithium plating, occur independently of
  C-rate and play a major role in battery aging."
- "aging is accompanied by the formation of a distinct open circuit voltage (OCV)
  plateau, which contracts over time as lithium deposition on the anode initially
  increases and then stabilizes."
- "an innovative phase-based scaling technique to segment and scale the anode's
  over-discharge potential curve … achieving a root mean square error below 10 mV
  under both plating and non-plating conditions."
- "a strong correlation was identified between lithium plating and capacity
  degradation inflection point."

### 2.3 §1.1 문헌 정리 — 논문이 스스로 그리는 지도 `[인쇄]`

- 열화 부반응 → 세 모드 `LAM_PE`, `LAM_NE`, `LLI` [7,8]. "the growth of the SEI layer
  and irreversible lithium plating contribute to LLI, while the structural disarray,
  particle cracking, and dissolution of transition metal ions cause varying degrees of
  LAM in both cathode and anode."
- 도금의 두 분류 (이 논문의 핵심 어휘):
  - **rate-dependent**: "excessive transport or reaction overpotentials cause the local
    electrode potential to drop below the Li/Li+ threshold, as seen during
    low-temperature or fast charging [15,16]."
  - **rate-independent**: "arises when the lithium inventory exceeds the capacity of
    anode during charging, leading to excess lithium deposition. … as the anode degrades
    over time, significant loss of active material can still lead to rate-independent
    lithium plating, even in batteries originally designed with excess anode capacity."
    "This type of lithium plating can occur even at very low charging rates [13,14]."
- 선행: Dubarry et al. [14,17,18] 이 `LAM_NE` 에서 오는 무율 도금을 **이론적으로**
  (가역/비가역 비율까지) 다뤘고, Beck et al. [19] 가 OCV–Q 를 두 전극 OCP–Q 로
  분해했다. `[인쇄]` "once the anode capacity falls below the cathode's, a critical
  inflection point is reached, leading to rapid performance degradation."
- 남는 공백 `[인쇄]`: "the effects of lithium plating induced by significant anode
  material loss on battery performance remain unclear, and the changes in anode
  potential during rate-independent lithium plating are not well understood."
- 진단 방법 분류: advanced characterization (in-situ TEM/XAS/AFM, ex-situ SEM/EDX) vs
  external characteristic analysis (IC/DV). DV 로 도금 검출하는 근거:
  "when lithium plating occurs, a new high-voltage plateau emerges during subsequent
  discharge, corresponding to the oxidation or stripping of reversible plated lithium
  [30]. Since the stripping potential of lithium is lower than its deintercalation
  potential, this high-voltage plateau is often detected first."

`[해석]` 이 지도에서 이 위키가 이미 가진 것: Dubarry 2012 계보
([[dubarry-mechanistic-mode-synthesis]]) 가 무율 도금을 "LAM_NE 가 LLI 를 앞지르는
특수 경우" 로 식 안에 갖고 있었다. 이 논문은 그 특수 경우를 **실셀 17개 중 10개**
에서 봤다는 것이 새롭다.

### 2.4 §1.2 기여 3개 `[인쇄]`

1. "Mechanistic analysis at electrode level" — 분해·SEM·다율 반쪽전지·0 V 이하 방전.
2. "Quantitative detection and analysis of lithium plating" — "A distinct high-voltage
   plateau observed during low-rate cycling (0.05C) indicates lithium plating. Through
   DV analysis, we quantify lithium plating during both charging and discharging".
3. "Enhanced aging mode analysis through incorporating rate-independent lithium
   plating" — "By segmenting and scaling the over-discharge potential curve of the
   graphite half-cell in each phase, we accurately reconstruct the anode potential curve
   across battery lifespan."

---

## 3. p.3–5 — §2 Experimental setup

### 3.1 §2.1 셀·프로토콜 `[인쇄]`

| 항목 | 값 |
|---|---|
| 셀 | LFP (LiFePO₄) / (graphite), **1.1 Ah** — 형식·제조사 없음 (G9) |
| 셀 수·조건 | 17개, 6개 운전 조건 (Table 1) |
| 온도 | 25 °C (RPT) |
| 용량 교정 | 0.5 C CC → 3.6 V, CV → 0.05 C; 30 min 휴지; 0.5 C CC → 2.0 V |
| OCV 시험 | **0.05 C CC 충전 → 3.6 V, 곧바로 0.05 C 방전 → 2.0 V** (휴지 없음; 의사-OCV) |
| RPT 주기 | "regularly" (G6) |

### 3.2 §2.2 전극 OCP — 반쪽전지와 과방전 시험 `[인쇄]`

- "Batteries with different states of health (SOHs) were disassembled in an argon-filled
  glove box … positive and negative electrode sheets were removed and reassembled into
  half-cells."
- 용량 교정: ≈0.1 C (fresh 반쪽전지 기준), 전압 범위 **2.5/4.2 V (LFP vs Li)**,
  **0/1.5 V (graphite vs Li)**.
- OCP 곡선: 0.05 C, 교정된 실제 용량 기준.
- Fig. 1 ①: graphite 반쪽전지 표준 전압 범위 시험. ②: **과방전 시험** — "discharging at
  a constant current of 0.05C for **6 h** after the voltage of the graphite half-cell
  reaches 0 V. The extended discharge duration ensures the formation of a stable lithium
  metal layer on the surface of the graphite electrode."

### 3.3 Fig. 2 — graphite 전위 곡선 4장 (★ 이 논문의 물리적 근거; 직접 봄)

`[인쇄]` 캡션: "(a) Induced lithium plating potential curve, (b) Potential curves
with/without lithium-plating, (c) Potential curves under different rates, (d) Potential
curves at different aging levels."

**(a) 과방전 시간 곡선** — 세로 NE potential 0–1 V, 가로 시간 0–3.5×10⁵ s.
`[도표]` 리튬화 중 세 평탄역(≈0.2, ≈0.11, ≈0.08 V)을 지나 0 V 아래로 내려가며,
삽입 확대(1.4–1.8×10⁵ s, −0.02~+0.03 V)에 `T₁`·`T₂`·`T₃` 세 상자: `T₁` 에서 전위가
**≈−0.02 V 까지 내려가는 핵생성 골**, `T₂` 에서 **≈−0.015 V 평탄역**(도금), 전류 반전
후 `T₃` 에서 **≈+0.01~+0.02 V 평탄역**(박리) 뒤 탈리튬 곡선으로 복귀. 0 V 이하는
음영. 큰 스파이크 2개(≈0.7·2.55×10⁵ s)는 탈리튬 종료(1.5 V 상한).

`[인쇄]` 세 단계 서술: "In phase one, when the anode potential first drops below 0 V,
both lithium plating and lithium intercalation occur simultaneously. In phase two, the
lithium intercalation process ends, and uniform lithium plating begins to form … with
the potential gradually stabilizing. In phase three, the oxidation stripping of metallic
lithium occurs first since the lithium stripping potential is lower than the lithium
deintercalation potential."

**(b) 도금 유/무 비교** — 가로 half-cell SOC 0–1.4. `[도표]` 초록 실선(without)과
빨강 파선(with)이 0 V 위에서 **완전히 겹치고**, SOC ≈1.0 에서 with 만 0 V 아래로
내려가 ≈−0.02 V 골 뒤 ≈−0.015 V 로 평탄. 삽입 확대(SOC 0.5–1.3, −0.05~0.1 V)가
이를 확대한다. `[인쇄]` "The potential curves within the normal voltage range, above
0 V, are closely aligned with minimal variation."

**(c) fresh 전극의 율 의존** — 0.04·0.045·0.05·0.06·0.07·0.08 C 여섯 곡선,
SOH = 100 %. `[도표]` 주곡선은 겹쳐 보이고, 삽입 확대(SOC 0.28–0.55, 0.09–0.115 V)
에서 곡선 간 간격이 **≈5 mV 이내**로 율 순서대로 내려간다; 두 번째 삽입(SOC 1.0–1.4,
−0.03~−0.01 V)의 도금 평탄역도 ≈−0.01~−0.02 V 안. `[인쇄]` "When the discharge
rate increases from 0.04C and 0.08C, the potential curves of the graphite anode shift
slightly downward while their overall shape remains almost unchanged."
왜 0.08 C 까지인가 `[인쇄]`: OCV 시험 전류가 fresh 공칭 기준 0.05 C 인데 SOH 60 % 셀
에서는 실효 0.08 C 가 되기 때문.

**(d) 노화 수준·율** — SOH 100 %/70 %/58 % @0.05 C, 70 %/58 % @0.1 C. `[도표]`
0.05 C 세 곡선(빨강·주황·갈색)이 SOC 0–1 에서 **거의 겹치고**, 0.1 C 두 곡선(초록·보라)
은 그 아래로 ≈5–10 mV 평행 이동. 삽입 확대(SOC 1.0–1.2, −0.03~0 V): 도금 골 최저가
0.05 C 에서 ≈−0.018 V, 0.1 C 에서 ≈−0.023 V (SOC ≈1.07–1.10), 그 뒤 각각 ≈−0.010 /
≈−0.018 V 로 회복. `[인쇄]` "as the battery ages, the relationship between the
electrode's OCP and SOC remains unchanged, providing a crucial foundation for analyzing
aging patterns based on electrode OCP and battery OCV."

`[해석]` (d) 는 **아핀 불변 전제(pristine 곡선 재사용)를 이 화학에서 지지하는 실측**
이다 — 단 세로 해상도가 0–0.5 V 라 수 mV 의 형상 변화는 못 본다 (G7). Si/graphite 에서
[[halfcell-ocp-shape-invariance]] 가 깨지는 것과 대조되는, "순수 graphite 에서는 버틴다"
쪽 근거로 쓸 수 있다. 이 위키에 필요한 것은 바로 이런 **화학별 경계**다.

---

## 4. p.5 — §3 Method

### 4.1 §3.1 개요 (Fig. 3 — 안 봄) `[인쇄]`

네 단계: (1) 전 수명 OCV 시험, (2) fresh·aged graphite 반쪽전지 다조건 OCV 시험,
(3) "The electrode potential is then segmented into different stages based on the peaks
in the DV curves and the corresponding phase transition points", (4) 분할된 음극 곡선을
full-cell OCV 에 정렬해 "under both non-lithium plating and lithium plating conditions"
모드 결정.

### 4.2 §3.2 기준 방법 — 아핀 창 매개화 (식 1–3) `[인쇄]` (원문 이미지로 확인)

식 (1):
```
SOC_NE,FC = K_NE·SOC_NE + S_NE = K_NE·f_NE⁻¹(OCP_NE) + S_NE
SOC_PE,FC = K_PE·SOC_PE + S_PE = K_PE·f_PE⁻¹(OCP_PE) + S_PE
```
`K` = scaling, `S` = shift. 식 (2): `argmin_θn RMSE = sqrt( (1/N) Σᵢ (OCVᵢ −
(OCP_PE,i − OCP_NE,i))² )`, `θn = [K_NE, K_PE, S_NE, S_PE]`. 식 (3):
```
Q_PE = K_PE·Q_Full
Q_NE = K_NE·Q_Full
Q_Li = K_PE·Q_Full − (S_NE − S_PE)·Q_Full
```
"A genetic algorithm is used to identify these model parameters." (G2)

`[해석]` 좌표 규약 확인: `S` 는 **full-cell SOC 단위**의 이동량(용량 아님), `K` 는
전극 용량/full-cell 용량 비. 우리 `[a_PE, b_PE, a_NE, b_NE]` 와 같은 4-창 좌표계이며
제약 0 — [[halfcell-window-parametrization-lineage]] 의 Navidi/우리 행과 같은 부류.
`Q_Li` 는 "양극 창 상단 − 음극 창 하단" 이다: `Q_Li/Q_Full = (K_PE + S_PE) − S_NE`.

### 4.3 ★ 아핀 매개화가 깨지는 장면 — Fig. 4 (직접 봄)

`[인쇄]` "In the early stage of battery aging, without lithium plating, electrode
potential curves align well with the measured OCV curve. However, once lithium plating
occurs and alters the shape of the OCV-SOC curve, this alignment deteriorates, as shown
in Fig. 4. In Fig. 4(b), the anode potential curve no longer aligns with the battery OCV
shape, increasing voltage matching errors and preventing accurate identification of
aging modes."

**(a) 도금 없음** — 왼쪽 축 Voltage/PE potential 2.6–3.8 V, 오른쪽 축 NE potential
−0.2~1.2 V, 가로 Battery SOC. `[도표]` PE(파랑) 창 ≈−0.15 → ≈1.02, NE(빨강) 창 0 →
≈1.28, 화살표 `Q_Li` 0 → ≈1.02, `Q_NE` 0 → ≈1.28, `Q_Full` 0 → 1, `Q_PE` ≈−0.15 → ≈1.02.
Experiment(검정)와 Simulation(초록 파선)이 겹친다. `[재현]` 이 그림 기준
`Q_NE/Q_Li ≈ 1.28/1.02 ≈ 1.25`, `Q_NE/Q_PE ≈ 1.28/1.17 ≈ 1.09` — Table 3 의 SOH 100 %
값(`Q_NE/Q_Li = 1.063`)과 다르므로 **다른 셀 또는 다른 상태**로 보인다.

**(b) 도금 있음** — 세로 3.2–3.55 V 확대, 가로 −0.2~1. `[도표]` 실험 곡선이 SOC
≈0.85–0.92 에서 **≈3.45–3.46 V 의 작은 평탄역(어깨)** 을 만들고(회색 음영 0.85–1.0),
아핀 시뮬레이션은 그 구간에서 실험 아래로 처지며 어깨를 못 만든다; SOC 0.1–0.25 에서도
어긋난다. NE 곡선(오른쪽 축 0–0.4 V)이 SOC ≈0.95 에서 0 V 에 닿는다.

`[해석]` 이 그림이 이 논문에서 우리 축에 가장 직접 걸리는 장면이다. **아핀 4-파라미터
모델의 잔차가 "무작위" 가 아니라 충전 말단에 국소화된 어깨** 로 나타난다. 그러나 (G8)
그 RMSE 가 인쇄되지 않아, "잔차가 얼마나 커야 모델을 바꿔야 하는가" 의 문턱을 이
논문에서는 못 얻는다.

### 4.4 제안 방법 5 단계와 식 (4)–(6) `[인쇄]` (원문 이미지로 확인)

1) 음극 과방전 시험 → 도금 전위 곡선. 2) 그 곡선의 DV 분석 — "Each peak in the DV
curve signifies a phase transition, enabling precise segmentation, as shown in Fig. 5."
3) DV 봉우리 위치로 곡선 분할. 4) "Each segmented portion of the potential curve was
scaled individually … The scaled segments were then reassembled". 5) OCV 정합 → 모드.

식 (4): `[V_t:t+N, SOC′_t:t+N] = [V_t:t+N, K_NEi × (SOC_t:t+N − SOC_t) + SOC′_t]` —
구간 `i` 의 전위 열은 그대로 두고 SOC 열만 구간 시작점 기준으로 `K_NEi` 배 늘린 뒤
앞 구간 끝 `SOC′_t` 에 이어 붙인다.
식 (5): `θn = [K_NE1, K_NE2, K_NE3, K_NE4, K_NE5, K_PE, S_NE, S_PE]` — **8 개**.
식 (6): `K_NE = max(SOC′(SOC′ ≥ 0))`, `Q_NE = K_NE·Q_Full` — "where SOC′ refers to the
terminal value of the SOC sequence after scaling the previous segment." (G3)

`[해석]` 구조적으로 이것은 음극 곡선을 **구간별 아핀(piecewise-affine)** 으로 만드는
것이다. 각 구간의 **전위 값은 고정**이고 **가로 폭만** 자유다. 즉 저자들은 "형상이
바뀐다" 를 "각 상전이 평탄역의 길이가 따로 바뀐다" 로 모형화했다. 이는
[[halfcell-ocp-shape-invariance]] 의 Schmitt 처방(`γ_Si` 를 다섯째 파라미터로)과 같은
방향 — **여분을 죽이지 않고 늘린다** — 이며, 이번엔 +4. 식별 가능성 논의는 0회
(§10). 구간 ⑤(0 V 이하)의 폭 `K_NE5` 가 곧 도금 평탄역의 길이이고 그것만이 새
관측(어깨)에 직접 묶인다; 나머지 `K_NE1–4` 는 종래 `K_NE` 하나가 하던 일을 넷이
나눠 갖는 것이라 **서로 보상할 수 있다** (구간 폭의 합만 구속).

### 4.5 Fig. 5 — 분할 도식 (직접 봄)

`[도표]` NE potential(검정, 0–0.4 V) 과 DV(빨강, 0–2) vs half-cell SOC 0–1.3. DV
봉우리(파란 점) 4개: SOC ≈0.14 (≈0.7), ≈0.21 (≈0.45), ≈0.55 (≈0.33), ≈0.99 (≈1.1).
그 위치에 NE 곡선의 상전이점(별). 구간: ① 0–0.14, ② 0.14–0.21, ③ 0.21–0.55,
④ 0.55–0.99, ⑤ 0.99–1.3 (0 V 이하, 음영). `[해석]` ⑤ 의 하한이 DV 의 가장 큰
봉우리(SOC ≈0.99, 0 V 교차)라는 점이 중요하다 — 도금 구간의 시작이 곧 `Q_NE` 의
끝이며, 식 (6) 은 그 점을 `K_NE` 로 읽는다는 뜻으로 보인다.

---

## 5. p.5–7 — §4.1 무율 도금 (prevalence · 전압 · 형태)

### 5.1 §4 도입 `[인쇄]`

"The lithium plating discussed in this study occurs at a low current charging rate of
0.05C under 25 °C. A distinct lithium plating voltage plateau is observed during the
charging process, with significant reversible lithium plating detected during the
subsequent low current discharge … The primary cause of this lithium plating is the
excessive loss of active material in the anode during aging process."

### 5.2 §4.1.1 분포 — Fig. 6 + Table 1 (직접 봄)

`[인쇄]` "10 out of 17 batteries (58.8 %) exhibited clear evidence of lithium plating
induced by aging". "Statistical analysis of the test data identifies cutoff voltage,
charging current, and aging-induced stress as the key factors contributing to this
rate-independent lithium plating." (그 통계 분석 자체는 인쇄돼 있지 않다.)

Table 1 `[인쇄]`:

| No. | 조건 (G10 형식) | 시험 셀 | 도금 셀 |
|---|---|---:|---:|
| 1 | 1.5 A-3.5 V-2.2 A-2.0 V | 2 | 2 |
| 2 | 3.3 A-3.6 V-3.3 A-2.1 V | 3 | 3 |
| 3 | 5.5 A-3.7 V-1.1 A-1.9 V | 3 | 0 |
| 4 | 1.5 A-3.6 V-3.3 A-1.9 V | 3 | 0 |
| 5 | 3.3 A-3.7 V-1.1 A-2.0 V | 3 | 2 |
| 6 | 5.5 A-3.5 V-2.2 A-2.1 V | 3 | 3 |

Fig. 6 `[도표]` 막대: group 1 2/2, 2 3/3, 3 0/3, 4 0/3, 5 2/3, 6 3/3; 파이 58.8 % / 41.2 %.
`[해석]` 표만 보면 도금 0 인 두 조건(3, 4)의 공통점은 **방전 하한 1.9 V** 이고 도금
조건은 2.0/2.1 V 다. 충전 상한(3.5–3.7 V)·전류(1.5–5.5 A)는 양쪽에 섞여 있다.
n = 2–3 이라 통계라 부를 수 없다.

### 5.3 §4.1.2 전압 특성 — Fig. 7 (★ 서명의 원전; 직접 봄)

`[인쇄]` 캡션: "(a)-(b) charging voltage curve (c)-(d) discharging voltage curve (e)
charging DV curve (f) discharging DV curve." 색: aged(파랑) → fresh(빨강).

**(a)** `[도표]` 충전 전압(2.8–3.6 V) vs Q(0–1.2 Ah). 용량이 fresh ≈1.18 Ah 에서 aged
≈0.72 Ah 로 줄고, aged 곡선에 충전 말단 **≈3.46 V 평탄역**이 생긴다(회색 상자 0.65–1.2
Ah, 3.44–3.5 V).
**(b)** `[도표]` 확대(3.455–3.49 V, 0.65–1.2 Ah): fresh 곡선은 1.1–1.18 Ah 에서 곧장
치솟고, aged 곡선은 **≈3.461–3.463 V 에서 평탄**하다가 치솟는다. 평탄역 시작 전압이
노화에 따라 ≈3.468 → ≈3.461 V 로 **내려간 뒤 멈춘다**. 평탄역 길이는 처음엔 늘고
가장 노화된 곡선(짙은 파랑)에서 다시 짧아진다.
`[인쇄]` 세 특성: "(1) the lithium plating voltage plateau initially extends as it first
emerges, then stabilizes before gradually shrinking … (2) The voltage at which the
lithium plating plateau first appears progressively decreases and then stabilizes. (3)
During the mid-to-late stages of aging, a slight voltage drop of **around 2 mV** is
observed when the voltage reaches the onset of lithium plating during charging cycles,
followed by a rapid recovery after lithium plating ceases."
`[인쇄]` 해석 (저자): "Increased lithium plating reduces the charge transfer resistance
at the electrode surface, effectively adding a parallel branch to the equivalent surface
resistance, leading to a drop in polarization voltage." / "The decrease in the onset
voltage of lithium plating may be attributed to the loss of active material in the anode
… the anode potential drops more rapidly during charging". / "lithium plating is a
self-accelerating process … However, as the SEI layer thickens and dead lithium forms,
the plating process becomes inhibited."

**(c)** `[도표]` 방전 전압(2.8–3.6 V) vs Q: aged 곡선의 방전 **시작**에 ≈3.4 V 어깨
(회색 상자 0–0.13 Ah, 3.3–3.5 V).
**(d)** `[도표]` 확대(3.30–3.50 V, 0–0.15 Ah): aged(파랑) 곡선이 **≈3.40 V 평탄역**을
≈0.05–0.07 Ah 까지 끌고 가다 3.33 V 로 떨어진다; fresh(빨강)는 곧장 떨어진다. 화살표
두 개(빨강 →, 파랑 ←)가 "늘었다가 줄어듦" 을 표시. `[인쇄]` "the lithium stripping
voltage plateau gradually extends, stabilizes, and eventually shrinks."

**(e)** `[도표]` 충전 dV/dQ (0–4 V/Ah): aged 곡선에 **≈0.6–1.0 Ah 에서 새 봉우리(높이
≈1.5–2.5 V/Ah)** 가 생기고 노화와 함께 왼쪽으로 이동(파란 화살표). fresh 는 1.05–1.15
Ah 의 충전 종료 급상승과 0.1·0.2·0.4 Ah 근처의 작은 봉우리뿐.
**(f)** `[도표]` 방전 −dV/dQ: **≈0.03–0.07 Ah 에 새 봉우리(≈1.5–2)**, 삽입 확대
(0.02–0.1 Ah, 0–2.5)에서 봉우리가 노화 초기에 오른쪽으로 갔다가 다시 왼쪽으로 온다.
`[인쇄]` "a new peak corresponding to lithium plating emerges in the high SOC region,
and its magnitude can be utilized to quantify lithium plating."

`[해석]` 서명을 정리하면 (§12 의 요구서 항목의 원천):
- **위치**: 충전 **말단**(고 SOC) 평탄역 + 방전 **시작**(저 DOD) 평탄역 — 둘 다
  **고 SOC 끝**에 붙어 있고, 두 평탄역의 **전압이 다르다**(≈3.46 vs ≈3.40 V,
  `[도표]`) — 도금 전위 < 박리 전위가 아니라, full-cell 로 보면 충전 시 `U_PE −
  U_NE(<0)` 가 방전 시 `U_PE − U_NE(>0, 박리)` 보다 높다.
- **전압 고정성**: 평탄역 전압이 `[도표]` 수 mV 안에서 고정이고 위치(Q)만 이동한다
  — LAM/LLI 의 특징점 이동(전압 고정·Q 이동)과 같은 성질이라 **전압만으로는 못
  가른다**. 가르는 것은 (i) **새 특징의 출현**(원래 없던 봉우리), (ii) **충·방전
  비대칭 짝**, (iii) 저자가 든 2 mV 동역학 하강.
- **진화**: 커졌다 → 멈췄다 → 줄어든다 (자기 제한).

### 5.4 §4.1.3 전극 형태 — Fig. 8 (안 봄) `[인쇄]`

fresh 와 EOL 이하 aged(DV 도금 봉우리 확인) 셀을 글러브박스에서 분해, DMC 세척.
"the surface of the anode sheet from an aged battery with lithium plating exhibits both
uniform and non-uniform white patches. These aged anodes exhibit a strong reaction with
water, producing numerous bubbles". SEM: fresh 입자는 매끈·경계 뚜렷(8b); 도금 전극은
피막으로 덮여 울퉁불퉁(8d); 더 심한 것은 느슨한 물질이 입자 경계를 가림(8f). 캡션의
SOH: (a)/(b) 100 %, (c)/(d) 57.1 %, (e)/(f) 58 %. "This covering material is
hypothesized to be an additional passivation film formed by the reaction of plated
lithium with the electrolyte, as well as oxides formed when exposed to air".

---

## 6. p.8–9 — §4.2 Effects: 용량 손실 정량과 모드 분석

### 6.1 §4.2 도입 `[인쇄]`

"For LFP batteries, rate-independent lithium plating introduces a new voltage plateau in
the OCV curve, further complicating battery state estimation. This alteration in the OCV
curve reflects changes in electrode potential, which implies that traditional methods for
acquiring aging modes may no longer provide accurate results."

### 6.2 §4.2.1 도금량 정량 — 식 (7), Fig. 9, Fig. 10, Table 2 (직접 봄)

식 (7) `[인쇄]`: `Q_li-plating,n = ΔSOC_n × Q_age,n` — `n` 은 충전/방전, `Q_age,n` 은
그 시점의 충전/방전 용량, "ΔSOC refers to the extent of the lithium plating peak
observed in the DV curve."

Fig. 9 `[도표]`: **(a)** 충전 dV/dSOC(0–2) vs SOC. without(검정): 봉우리 ≈0.17, 0.23,
0.67 SOC 와 ≈0.97 의 종료 상승. with(빨강): ≈0.17, 0.22, **0.52**, 그리고 **SOC ≈0.865
에 높이 ≈1.25 의 새 봉우리**, `ΔSOC` 화살표가 그 봉우리(점선)에서 ≈0.98 까지. **(b)**
방전 dV/dSOC(−3~0) vs DOD: with(빨강)에 **DOD ≈0.065 에 깊이 ≈−1.65 의 새 골**,
`ΔSOC` 화살표 ≈0.01 → ≈0.065; without(검정)은 DOD 0.01 의 −2.4 에서 0.05 까지 곧장
0 으로 올라온다.
`[해석]` (a) 에서 놓치기 쉬운 것: with 곡선의 **중간 봉우리가 0.67 → 0.52 로 옮겨
갔다**. 이것은 도금이 아니라 **`LAM_NE`** 의 서명(음극 상전이가 full-cell SOC 의 더
낮은 곳에서 일어남)이다 — 새 봉우리(도금)와 기존 봉우리 이동(LAM_NE)이 **같은 곡선에
같이** 있다. 요구서의 "구분 시험" 은 이 둘을 따로 세어야 한다.
`[해석]` `ΔSOC` 의 정의가 그림에서 "봉우리 정점부터 종료까지" 인지 "봉우리 폭" 인지
분명치 않다 — 식 (7) 의 재현에는 이 정의가 필요하다 (G 목록에 넣지 않았으나 같은
급의 공백).

Fig. 10 `[도표]` (여섯 셀, 가로 cycle, 세로 capacity/Ah, 빨강 charge · 검정 discharge):

| 패널 | cycle 범위 | charge 궤적 | discharge 궤적 |
|---|---|---|---|
| (a) | 1170–3300 | 0 (–1400) → 0.03 → 0.064 (3000) → **0.098** (3200) → 0.09 | 0.017 → 0.035 평탄 |
| (b) | 2400–4300 | 0 (–2650) → 0.024 | 0.017 → 0.032 |
| (c) | 1200–3550 | 0 (–1350) → 0.068 (3250) → 0.06 | 0.014 → 0.042 → 0.04 |
| (d) | 1650–2450 | 0.032 → 0.077 (2350) → 0.066 | 0.02 → 0.03 |
| (e) | 1900–7000 | 0.025 → **0.118** (5700) → 0.095 | 0.022 → 0.064 (5700) → 0.047 |
| (f) | 4700–7700 | 0 (–4900) → 0.043 | 0.019 → 0.041 |

Table 2 `[인쇄]`:

| No. | 조건 | SOH_start | SOH_end | Max Q_li-plating (mAh) | 그림 |
|---|---|---:|---:|---:|---|
| 1 | 3.3 A-3.7 V-1.1 A-2.0 V | 0.933 | 0.552 | 98.2 | Fig. 10(a) |
| 2 | 1.5 A-3.5 V-2.2 A-2.0 V | 0.960 | 0.928 | 31.5 | Fig. 10(b) |
| 3 | 3.3 A-3.6 V-3.3 A-2.1 V | 0.960 | 0.579 | 67.6 | Fig. 10(c) |
| 4 | 3.3 A-3.6 V-3.3 A-2.1 V | 0.704 | 0.535 | 76.9 | Fig. 10(d) |
| 5 | 5.5 A-3.5 V-2.2 A-2.1 V | 0.955 | 0.571 | 118.5 | Fig. 10(e) |
| 6 | 5.5 A-3.5 V-2.2 A-2.1 V | 0.950 | 0.905 | 43.1 | Fig. 10(f) |

`[재현]` Table 2 의 최댓값과 Fig. 10 의 charge 최댓값이 일치한다 (98.2 ↔ ≈0.098,
67.6 ↔ ≈0.068, 76.9 ↔ ≈0.077, 118.5 ↔ ≈0.118). 단 No. 2 (31.5) 와 No. 6 (43.1) 은
**discharge** 최댓값(≈0.032, ≈0.041)과 맞는다 — 그 두 셀은 charge 가 discharge 보다
작으므로 Table 2 의 "Max" 는 **충·방전 중 큰 쪽**으로 읽힌다.
`[인쇄]` "more lithium typically plating during charging than discharging. This
discrepancy is primarily due to the partial irreversibility of lithium plating".
"the discharging process exhibits higher sensitivity in detecting lithium plating,
allowing for earlier detection." / 세 단계: "(1) a gradual increase with battery aging;
(2) stabilization at a relatively constant level during mid-aging; (3) a peak followed
by a gradual decline with further aging."
`[해석]` (G12) discharge 궤적이 charge 검출 **이전부터** 0.014–0.022 Ah 로 0 이 아닌
것은 "방전이 더 민감" 의 근거일 수도, 방전 DV 골 정의가 도금 없는 곡선에서도 값을
내는 **기저 오프셋**일 수도 있다. Fig. 9(b) 의 without 곡선도 DOD 0.01–0.05 에 급한
경사가 있어서 골 검출기가 무엇을 잡는지에 따라 값이 생길 수 있다. 논문은 이 둘을
가르지 않는다. 도금량 최댓값 31.5–118.5 mAh 는 공칭 1.1 Ah 의 **2.9–10.8 %** 다.

### 6.3 §4.2.2 모드 분석 — Fig. 11, Table 3 (직접 봄)

`[인쇄]` "Fig. 11 and Table 3 demonstrate that the proposed method maintains an OCV
matching for LIBs throughout its entire lifecycle with the root mean square error (RMSE)
below 10 mV."

Table 3 `[인쇄]`:

| No. | SOH | Q_NE (Ah) | Q_Li (Ah) | Voltage RMSE |
|---|---:|---:|---:|---:|
| 1 | 100 % | 1.2722 | 1.1968 | 2.7 mV |
| 2 | 91 % | 1.0232 | 1.1099 | 4.5 mV |
| 3 | 82.5 % | 0.9405 | 1.0427 | 7.2 mV |
| 4 | 57.1 % | 0.6364 | 0.7417 | 9.1 mV |

Fig. 11 `[도표]` (네 패널, 왼쪽 축 3.2–3.6 V, 오른쪽 축 NE 0–0.4 V, 가로 SOC of
battery; 검정 실험, 초록 파선 시뮬레이션, 빨강 NE, 파랑 PE):
- (a) SOH 100 %: NE 가 0 V 에 닿는 위치 ≈**1.08** (창 밖), NE 곡선은 ≈1.3 까지
  그려짐(도금 구간 포함). PE 창 ≈−0.12 → 1.0. 실험·시뮬 겹침.
- (b) 91 %: NE 0 V 교차 ≈**1.0** (창 끝). PE 창 ≈−0.12 → 1.0.
- (c) 82.5 %: NE 0 V 교차 ≈**0.93**; 실험 곡선에 SOC 0.9–0.95, ≈3.46 V 의 어깨; 시뮬이
  어깨를 대체로 따라가나 0.9 부근에서 약간 벗어남.
- (d) 57.1 %: NE 0 V 교차 ≈**0.88**; 어깨 0.85–0.98 (≈3.46 V); 시뮬이 어깨 아래를 약간
  밑돈다(RMSE 9.1 mV 의 출처로 보임).
- 세로축이 3.2 V 부터라 실험 곡선의 SOC 0–0.05 구간(2.0–3.2 V)은 그려지지 않는다.

`[해석]` (a)→(d) 로 갈수록 **NE 의 0 V 교차점이 창 밖(1.08)에서 창 안(0.88)으로 들어
온다.** 이것이 "무율 도금" 의 기하학적 정의다: 음극 상단 가장자리가 full-cell 창 안에
들어오면 그 너머의 Li 는 도금될 수밖에 없다. 그리고 그 가장자리가 창 밖에 있는 동안
(a)(b) 은 `K_NE` 가 **관측되지 않는 가장자리**로 정해져야 하므로 약하게만 식별된다 —
§9.3 참조.

---

## 7. p.10 — §4.3 Further discussions: Fig. 12 세 단계 (직접 봄)

`[인쇄]` "Our findings indicate a strong correlation between rate-independent lithium
plating and the ratio of theoretical lithium inventory to anode capacity. … Since the
cathode in LFP batteries generally degrades more slowly, especially relative to the
anode, this study focuses on anode capacity dynamics, with cathode changes left for
future investigation." / "This is evidenced by a decreasing ratio of lithium
inventory-to-anode capacity" (→ §9.5 불일치 1). / 세 단계: "In stage one, a battery
undergoes a relatively stable, linear degradation driven mainly by the formation and
thickening of SEI layer … In stage two, degradation accelerates, marked by a noticeable
inflection point in capacity loss. This inflection correlates with the onset of lithium
plating, which intensifies active anode material loss … In stage three, a battery enters
rapid degradation, where the depletion of both lithium inventory and anode capacity brings
the battery close to its designed end-of-life threshold."

Fig. 12 `[도표]` (네 셀, 세로 Capacity 0.6–1.4 Ah, `Q_NE` 빨강 원, `Q_Li` 파랑 사각,
`Cap` 점(S1 파랑·S2 초록·S3 살구)):

| 패널 | cycle | `Q_NE` | `Q_Li` | `Cap` | S1→S2 (≈ `Q_NE` 가 `Q_Li` 를 가로지르는 곳) | S2→S3 |
|---|---|---|---|---|---|---|
| (a) | 0–3900 | 1.26 → 1.18 (≈1400) → **≈1.08 (≈1500)** → 0.65 | 1.17 → 0.72 거의 직선 | 1.16 → 0.66 | ≈1400 | ≈2050 |
| (b) | 0–3300 | 1.28 → 1.18 (≈1200) → **≈1.08 (≈1300)** → 0.60 | 1.17 → 0.68 | 1.17 → 0.63 | ≈1200 | ≈2100 |
| (c) | 0–7000 | 1.28 → 1.13 (≈2500) → **≈1.02 (≈2800)** → 0.63 | 1.21 → 0.74 | 1.20 → 0.68 | ≈2300 | ≈3400 |
| (d) | 0–2450 | 1.29 → 1.14 (≈950) → 0.88 (≈1500) → 0.58 | 1.19 → 0.65 | 1.19 → 0.63 | ≈1400 | ≈1750 |

관찰 `[도표]`:
1. S1 에서 `Cap ≈ Q_Li` (약간 아래), `Q_NE > Q_Li` — 리튬 제한.
2. `Q_NE` 가 `Q_Li` 를 가로지른 뒤 `Cap ≈ Q_NE` (약간 **위**) — 음극 제한 + 가역 도금분.
3. S3 에서 `Q_Li − Cap` 간격 ≈0.05–0.08 Ah 로 벌어진다.
4. **`Q_Li` 궤적에는 변곡이 거의 없다.** 변곡은 `Q_NE` 와 `Cap` 에 있다.
5. (a)(b)(c) 에서 `Q_NE` 가 S1/S2 경계 부근 **100–300 사이클 안에 ≈0.1 Ah 계단**처럼
   떨어진다. S1 기울기(≈0.08 Ah / 1400 cycle)의 열 배가 넘는다.

`[해석]` 관찰 5 는 두 가지로 읽힌다. (i) 물리: 도금 개시가 `LAM_NE` 를 급가속시킨다
(저자의 "self-reinforcing loop"). (ii) **식별 가능성의 국면 전환**: S1 에서는 음극
상단 가장자리(구간 ④ 끝·⑤)가 관측 창 밖에 있어 `K_NE` 가 곡선 **내부** 상전이 간격
으로만 정해지는데(약함), 가장자리가 창 안에 들어오는 순간 어깨 위치가 `K_NE` 를
강하게 고정한다 — 그 순간 추정값이 "약한 추정 → 강한 추정" 으로 **점프**한다. (i) 과
(ii) 를 가르려면 S1 구간에서 `K_NE` 의 불확실성(또는 다른 초기값에서의 산포)이
필요한데 논문에 없다 (G1, G2). 이 위키는 (ii) 를 **배제 못 한 채** 기록한다. 이것이
[[data-window-identifiability]] 의 "창의 위치가 어느 전극을 보이게 하는지 고른다" 와
같은 기제이고, 여기서는 창이 아니라 **전극 창이 노화로 움직여 관측 창 안에 들어온**
경우다.

`[인쇄]` 한계 (저자): "the laboratory conditions under which this study was conducted may
not fully capture the full spectrum of real-world operational stresses."

---

## 8. p.10–11 — §5 Conclusions `[인쇄]`

- "such lithium plating can occur even at very low current levels."
- "this high-voltage plateau initially emerges, expands, and stabilizes before eventually
  contracting, reflecting a self-limiting process where initial acceleration of lithium
  plating subsequently inhibits further plating."
- "we observe a polarization voltage reduction on the graphite anode surface due to
  lithium plating, leading to a slight voltage drop."
- "We also address the limitations of traditional OCV curve analysis methods for aging,
  which assume simple translation and scaling."
- "rate-independent lithium plating typically begins near the inflection point of
  capacity degradation … lithium plating is both a result and a driver of accelerated
  degradation".

---

## 9. 정의·좌표·산술 정리 (이 digest 의 계산)

### 9.1 이 논문의 모드 정의와 우리 좌표의 대응 `[해석]`

| 이 논문 | 뜻 | 우리 `[a, b]` 창 좌표 |
|---|---|---|
| `K_PE`, `K_NE` | 전극 용량 / full-cell 용량 | `a_PE`, `a_NE` (스케일) |
| `S_PE`, `S_NE` | 전극 SOC 0 의 full-cell SOC 위치 | `b_PE`, `b_NE` (이동) |
| `Q_Li = (K_PE + S_PE − S_NE)·Q_Full` | 양극 창 상단 − 음극 창 하단 | 같은 정의 (Marongiu·Schmitt 와 동형) |
| `K_NE1..5` | 음극 곡선 5 구간의 개별 가로 스케일 | **대응 없음** — 우리 좌표 밖 |
| `Q_li-plating` (식 7) | DV 새 봉우리 폭 × 용량 | **대응 없음** — 모드 3개 밖의 네 번째 양 |

### 9.2 Table 3 에서 뽑은 비와 손실 `[재현]`

| SOH | `Q_NE/Q_Li` | `LAM_NE = 1 − Q_NE/Q_NE(100 %)` | `LLI = 1 − Q_Li/Q_Li(100 %)` |
|---:|---:|---:|---:|
| 100 % | 1.2722/1.1968 = **1.063** | 0 | 0 |
| 91 % | 1.0232/1.1099 = **0.922** | 1 − 1.0232/1.2722 = **19.6 %** | 1 − 1.1099/1.1968 = **7.3 %** |
| 82.5 % | 0.9405/1.0427 = **0.902** | **26.1 %** | **12.9 %** |
| 57.1 % | 0.6364/0.7417 = **0.858** | **50.0 %** | **38.0 %** |

- 기준점을 Table 3 의 SOH 100 % 로 잡았다 (논문은 LAM/LLI 백분율을 인쇄하지 않는다).
- SOH 91 % 에서 이미 `Q_NE < Q_Li` — 이 셀은 **SOH 91 % 이전 어딘가에서 음극 제한으로
  넘어갔다.** 용량 9 % 감소 사이에 `LAM_NE` 19.6 % — 음극이 여유(6.3 %)를 다 쓰고도
  더 줄었다는 뜻이며, Fig. 12 의 계단(관찰 5)과 정합한다.
- SOH 의 기준(G5)에 따라 `Cap` 절대값이 달라지므로 `Cap − Q_NE`(가역 도금분) 은 여기서
  계산하지 않는다.

### 9.3 ★ LFP 양극이 만드는 구조적 비식별 `[해석]`

LFP 양극 OCP 는 평탄하고, full-cell 의 충전 종료(3.6 V)는 양극 상단 가장자리의 급상승이
정한다. 따라서:
- 양극 창 **상단**은 항상 full-cell SOC = 1 에 **고정**된다 (`K_PE + S_PE ≈ 1`).
- 양극 창 **하단**(`S_PE`)은 방전 종료가 음극 상승으로 정해지는 한 **관측 창 밖**이다.
  Fig. 11 네 패널에서 PE 창이 전부 ≈−0.12 → 1.0 으로 **같아 보이는** 것(`[도표]`)이
  이것이다 — 데이터가 `K_PE` 를 정하지 못하면 GA 는 초기값/경계 근처에 남는다.
- 그래서 `Q_Li = (1 − S_NE)·Q_Full` 로 **`Q_Li` 는 식별되지만 `Q_PE` 는 안 된다.**
  Table 3 가 `Q_PE` 를 안 싣는 것(G4)과 정합한다. 이것은 논문이 말하지 않은, 그러나
  그림과 표가 함께 가리키는 구조다.
- 이 구조는 [[marongiu2016_lfp-onboard-capacity-halfcell]] 계열(LFP 창 매개화)과
  같은 자리에서 나오는 축퇴이며, **NMC 계열로 옮기면 사라진다**(양극 OCP 에 기울기가
  있어 하단 가장자리 없이도 `K_PE` 가 곡률로 식별된다). 우리 22p 셀(NMC 계열이면)의
  축퇴와 **종류가 다르다** — 이식할 때 이 경계를 적어야 한다.

### 9.4 "도금이 LLI 로 잡히는가 LAM 으로 잡히는가" — 이 논문 회계의 재구성 `[해석]`

| 도금의 부분 | 어디로 가나 (이 논문의 정의) | 관측 |
|---|---|---|
| **원인** | `LAM_NE` (`Q_NE < Q_Li` 가 되도록 음극이 줄어듦) | 기존 DV 봉우리의 SOC 이동 (Fig. 9a 0.67 → 0.52) |
| **가역 도금** (박리되는 부분) | **모드 3개 어디도 아님** — 용량에 들어가고(`Cap > Q_NE`) `Q_NE`(식 6, G3 독해)에는 안 들어간다 | 충전 말단 평탄역 + 방전 시작 평탄역, DV 새 봉우리/골 |
| **비가역 도금** (dead Li) | **LLI** (`Q_Li` 감소) — 단 논문은 이 수지를 계산하지 않는다 (G11) | 충전측 도금량 − 방전측 박리량 (Fig. 10 의 두 곡선 간격) |
| **아핀 4-파라미터 적합에 강제로 넣으면** | 어깨를 못 맞추고 잔차로 남는다 (Fig. 4b). 어느 파라미터가 흡수하는지는 인쇄 없음 (G8) | 충전 말단 국소 잔차 |

결론: **이 논문의 회계에서 도금은 LAM 도 LLI 도 아닌 별도 항목**이고, 그 원인만
LAM_NE, 그 비가역분만 LLI 다. 우리 4-파라미터 모델은 이 항목이 없으므로, 도금 셀에서는
(a) 잔차 어깨가 남거나 (b) `a_NE` 가 커지는 쪽으로 오염되거나 둘 중 하나다 — 어느
쪽인지는 **우리 프레임에서 합성 실험으로 잴 수 있다** (§12).

### 9.5 원문 안의 불일치 목록 (인용 전 확인)

1. **"decreasing ratio of lithium inventory-to-anode capacity" (§4.3) vs Table 3.**
   `[재현]` `Q_Li/Q_NE` = 0.941 (100 %) → 1.085 (91 %) → 1.109 (82.5 %) → 1.165 (57.1 %)
   로 **증가**한다. 물리적으로도 도금 조건은 이 비가 1 을 **넘어서는** 것이다. 문장은
   "anode capacity-to-lithium inventory" 의 오기로 보인다. 인용하려면 Table 3 의 비를
   쓰고 문장은 쓰지 않는다.
2. **Fig. 4(a) 와 Table 3 의 SOH 100 % 창이 다르다.** `[도표]` Fig. 4(a) `Q_NE/Q_Li ≈
   1.25` vs `[인쇄]` Table 3 `1.063`. 어느 셀인지 캡션에 없다.
3. **Table 2 의 "Max Q_li-plating" 이 어느 과정(충/방전)의 최댓값인지** 행마다 다르다
   (§6.2 재현).
4. **식 (6) 조건** — G3.

---

## 10. 어휘 전수 (이 계보 열일곱 편째)

본문(참고문헌 제외; 줄바꿈 하이픈 결합 후) 문자열 검색:
`identifiab*` **0** · `observab*` **0** · `unidentifiab*`/`unobservab*` **0** ·
`uniqu*` **0** · `degenera*` **0** · `redundan*` **0** · `collinear*` **0** ·
`confound*` **0** · `uncertaint*` **0** · `error bar` **0** · `Fisher`/`CRB`/`Hessian`/
`singular`/`condition number`/`nullspace` **각 0** · `global`/`local minim*` **0** ·
`ill-posed`/`ambigu*`/`non-unique`/`compensat*` **0** · `sensitivit*` **1** (§4.2.1 "the
discharging process exhibits higher sensitivity in detecting lithium plating" — 파라미터
감도가 아니다) · `correlat*` **5** (전부 도금 ↔ 변곡점 상관) · `genetic` **1** ·
`initial*` **8** (전부 "initially/initial stage"; 초기값 아님) · `Cramer` **1**
(참고문헌 [6] 제목에서만).

`[해석]` **8-파라미터 GA 적합을 하면서 비유일성·불확실성 어휘가 완전한 0** 이다. 이
계보에서 자유도를 늘린 두 편(Schmitt 2022 +1, 이 논문 +4)이 모두 그 대가를 재지
않았다는 점이 [[mode-identifiability-unmeasured-lineage]] 의 논지에 그대로 붙는다.

---

## 11. 비판 (이 digest 의 판단)

1. **자유도 4 → 8 을 늘리면서 유일성을 안 묻는다.** `K_NE1–4` 는 종래 `K_NE` 하나의
   역할을 넷이 나눠 갖는다. 관측(full-cell OCV 한 곡선)이 구간 폭 넷을 각각 구속한다는
   근거는 "DV 봉우리 위치" 인데, 그 봉우리들이 full-cell 곡선에서 얼마나 선명한지
   (LFP 는 양극이 평탄해 음극 특징이 그대로 보이므로 유리한 편)는 논의 없음.
   검증은 **RMSE < 10 mV 뿐**이고 [[halfcell-ocp-shape-invariance]] 가 보인 것처럼
   RMSE 는 모드 값이 크게 바뀌어도 거의 안 움직인다.
2. **모드의 ground truth 가 없다.** 분해·SEM 은 "도금이 있었다" 의 정성 근거이고
   `Q_NE`·`Q_Li` 의 참값은 어디에도 없다. 반쪽전지 용량(§2.2 에서 쟀다고 함)을 `Q_NE`
   추정과 대조했다면 유일한 독립 검증이 됐을 텐데 **인쇄돼 있지 않다.**
3. **17 → 6 → 4 → 1.** 17 셀 분포(Fig. 6), 6 셀 도금량(Fig. 10), 4 셀 궤적(Fig. 12),
   4 상태 표(Table 3; 한 셀로 보이나 명시 없음). 셀 간 재현성 진술이 없다.
4. **Fig. 12 계단**(§7 관찰 5)을 물리로만 읽는다. 식별 가능성 국면 전환이라는 대안
   독해를 검토하지 않는다.
5. **양극을 뺀다**는 선택이 결과(§9.3)이자 전제다. `Q_PE` 미인쇄가 "천천히 열화" 의
   근거가 될 수는 없다.
6. **방전측 도금량의 기저 오프셋**(G12)을 다루지 않는다. "방전이 더 민감" 은 그
   오프셋이 실제 박리라는 전제 위에서만 성립한다.
7. 좋은 점도 적는다: (i) 과방전 반쪽전지로 **도금 구간의 전위 값**(≈−0.015 V)을
   직접 쟀고 그것으로 full-cell 어깨의 정체를 **전극 수준에서** 확정했다 — 우리가
   "잔차의 원인" 을 물을 때 필요한 형태의 근거다. (ii) 율 0.04–0.08 C 와 SOH 100/70/58 %
   에서 graphite 곡선의 아핀 불변을 **같은 그림에서** 시험했다 (Fig. 2c,d). (iii) 도금
   서명의 **시간 진화**(늘고 → 멈추고 → 줄고)를 17 셀 중 10 셀에서 봤다 — 단발 관측이
   아니다.

---

## 12. 이 저장소가 가져갈 것 (요약) — 특히 `bms-balancing/` 새 모델 요구서용

> 아래는 전부 `[해석]` 이다. 논문의 관측을 요구서 항목(관측 → 후보 원인 → 구분 시험 →
> 채택 기준 → 한계)의 형식으로 옮긴 것이며, 채택 기준의 수치는 이 논문 값(LFP)을
> 자리표시자로 쓴 것이라 우리 셀에서 다시 재야 한다.

| 항목 | 내용 |
|---|---|
| **관측 O1** | 아핀(α·β) 적합 뒤 **충전 말단 고 SOC 에 국소 잔차 어깨** (실험 > 모델), 폭 수 % SOC. Fig. 4(b). |
| **관측 O2** | 같은 RPT 의 **방전 시작**(DOD < ≈0.1)에 짝 평탄역(박리). Fig. 7(d), Fig. 9(b) 골 DOD ≈0.065. |
| **관측 O3** | 충전 dV/dQ 에 **원래 없던 새 봉우리**(고 SOC), 방전 −dV/dQ 에 새 골(저 DOD). 기존 봉우리의 이동(LAM_NE)과 **공존**. Fig. 7(e)(f), Fig. 9. |
| **관측 O4** | 어깨의 **전압이 RPT 마다 거의 같고**(LFP ≈3.46 V 충전 / ≈3.40 V 방전, `[도표]`) 위치(Q)와 길이만 변한다; 길이는 늘고 → 멈추고 → 준다. |
| **관측 O5** | 어깨 시작점에서 ≈2 mV 의 **동역학 하강 후 회복** (저자: 도금이 전하전달 저항의 병렬 가지). |
| **후보 원인** | (a) 무율 도금 (`Q_NE < Q_Li`); (b) 음극 OCP 형상 변화 (blend, [[halfcell-ocp-shape-invariance]]); (c) 양극 상단 가장자리 이동/저항 증가 ([[reference-electrode-halfcell-dma]] 의 창 절단형); (d) 단순 축퇴 — 파라미터가 골짜기 다른 점에 앉음 ([[fitting-degeneracy]]). |
| **구분 시험 T1 (짝 검사)** | O1 이 있으면 O2 가 **같은 RPT 의 방전 시작**에 있는가. (a) 만 짝을 만든다. (b)(c)(d) 는 방전 시작에 새 평탄역을 만들지 않는다. |
| **구분 시험 T2 (새 특징 vs 이동)** | dV/dQ 봉우리 **개수**가 늘었는가(O3). (a) 는 늘리고, (b)(c)(d) 는 위치/높이만 바꾼다. 봉우리를 **순서로** 세는 feature(예: "두 번째 봉우리")는 이 시험에 취약하다 — 개수 변화 검출을 앞에 둔다. |
| **구분 시험 T3 (전압 고정성)** | 어깨 전압이 RPT 간 수 mV 안에서 고정인가(O4). (a) 는 고정(도금 전위가 화학 상수). (c) 저항형은 전류·SOH 에 따라 움직인다. |
| **구분 시험 T4 (모드 정합)** | 아핀 적합이 낸 `Q_NE` 와 `Q_Li` 가 **교차했는가/교차 직전인가**. (a) 는 `Q_NE ≤ Q_Li` 일 때만 가능. 아핀 적합이 `Q_NE ≫ Q_Li` 라고 하는데 O1–O3 이 있으면 **적합이 틀린 것**(축퇴 (d) 또는 오염)으로 본다. |
| **구분 시험 T5 (율 무관성)** | 0.05 C 의사-OCV 에서도 남는가. 남으면 (a); 율을 낮추면 사라지면 동역학 도금(다른 원인). |
| **채택 기준 (a)** | T1 ∧ T2 ∧ T3 ∧ T4 모두 참. 하나라도 거짓이면 (a) 를 채택하지 않고 (b)–(d) 로 넘긴다. |
| **채택 후 처리** | 4-파라미터 좌표에 **도금 항목을 추가**하되(예: 도금 구간 폭 1개), 8-파라미터 구간 스케일링은 채택하지 않는다 — 유일성 근거가 없다. 도금량은 식 (7) 로 **별도 관측량**으로 기록하고 모드 3개에 섞지 않는다. |
| **한계** | LFP 값이다. NMC 계열은 양극 OCP 에 기울기가 있어 어깨가 **평탄역이 아니라 기울어진 단**으로 나타나고 전압 고정성(T3)이 약해진다. Si/Gr 음극은 (a) 와 (b) 가 **동시에** 있을 수 있어 T2 만으로 못 가른다. 방전측 골 검출기의 기저 오프셋(G12) 때문에 O2 의 문턱을 도금 없는 셀에서 먼저 재야 한다. |

**우리 프레임이 이 논문에 공급할 수 있는 것 (값싼 미실행 후속)**:
1. PyBaMM 합성 truth 에 **음극 창이 `Q_Li` 를 밑도는 상태**를 넣고(도금 물리 없이
   단순히 `a_NE` 를 작게), 4-파라미터 적합이 잔차를 어디에 남기고 어느 파라미터가
   흡수하는지 → §9.4 표의 마지막 행을 수치로 채운다.
2. 같은 합성에서 `K_NE1–5` 8-파라미터 적합의 `JᵀJ` 조건수·null 방향 — 저자가 재지 않은
   유일성을 우리 도구([[fitting-degeneracy]], [[nullspace-coefficient-interpretation]])로
   잰다.
3. §7 관찰 5 의 두 독해를 가르는 실험: `a_NE` 를 창 밖 → 창 안으로 서서히 움직이며
   4-파라미터 적합의 `a_NE` 오차막대(부트스트랩)가 **불연속으로 줄어드는 지점**이
   있는지.

**위키 컴파일 층에 붙는 것**: 새 개념 [[rate-independent-li-plating-signature]];
[[halfcell-window-parametrization-lineage]] 에 Wang (Xiong) 2025 행 (자유도 8, 제약 0,
여분 처리 "구간별 스케일링으로 늘림"); [[mode-identifiability-unmeasured-lineage]] 표에
행 추가; [[22p-physics-or-degeneracy]] 에 Evidence For 1건(창 밖 가장자리의 약한
식별과 계단) + Status Log; [[pvs-sev-lli-lampe-separability]] 에 Gap 1건(새 봉우리
출현이 순서 기반 feature 를 깨고, 2 mV 동역학 하강이 SEV 축에 걸린다).

---

## 13. 그림 판독 기록 (무엇을 보고 무엇을 안 봤는가)

| 그림 | 봤는가 | 기록한 것 |
|---|---|---|
| Fig. 1 | 아니오 | 시험 절차 도식 — 본문 §2.2 로 충분 |
| Fig. 2 | **예** | §3.3 — 도금 전위 ≈−0.015 V, 율 0.04–0.08 C 간격 ≈5 mV, SOH 100/70/58 % 겹침 |
| Fig. 3 | 아니오 | 방법 개요 순서도 — §3.1 텍스트로 충분 |
| Fig. 4 | **예** | §4.3 — 창 좌표(`Q_NE/Q_Li ≈ 1.25`), 도금 시 어깨 0.85–0.92 SOC, 아핀 시뮬 불일치 |
| Fig. 5 | **예** | §4.5 — DV 봉우리 4개 위치와 5 구간 |
| Fig. 6 | **예** | §5.2 — 6 조건별 도금 셀 수, 58.8 % |
| Fig. 7 | **예** | §5.3 — 충전 평탄역 ≈3.46 V·시작전압 하강, 방전 평탄역 ≈3.40 V, DV 새 봉우리 위치 |
| Fig. 8 | 아니오 | SEM/사진 — 정량 없음, 캡션 SOH 만 옮김 |
| Fig. 9 | **예** | §6.2 — 새 봉우리 SOC ≈0.865 (높이 ≈1.25), 골 DOD ≈0.065 (≈−1.65), 중간 봉우리 0.67 → 0.52 이동 |
| Fig. 10 | **예** | §6.2 — 6 셀 도금량 궤적, Table 2 최댓값과 대조, 방전측 기저 오프셋 |
| Fig. 11 | **예** | §6.3 — NE 0 V 교차점 1.08 → 1.0 → 0.93 → 0.88, PE 창 네 패널 동일 |
| Fig. 12 | **예** | §7 — 세 단계 경계, `Q_NE` 계단, `Q_Li` 무변곡 |
| Table 1–3 | 텍스트 | 전부 옮김 (§5.2, §6.2, §6.3) |

**본문 서술과 그림이 어긋난 것**: §9.5 의 1 (비의 증감 방향 — 표 vs 문장), 2 (Fig. 4a
vs Table 3 의 창). 그림끼리의 어긋남은 없었다.
