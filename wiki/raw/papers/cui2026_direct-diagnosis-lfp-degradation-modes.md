---
title: "Cui, Chen, Luo, Zhang, Pei, Lv, Shao, Lin, He, Pan, Liu, Zhao, Wang 2026 — A direct diagnosis method for degradation modes of LiFePO4 batteries based on mechanism analysis (Applied Energy 426, 128689)"
source_url: local-upload/20_direct_diagnosis_degradation_modes_lfp.pdf
ingested: 2026-09-11
sha256: 630121b20a77f00a2329e8f5db28d30f1f0279ea1f02e4d83d5bce3b16f3fa48
---

# 수집 목적

Yanwei Cui, Zheng Chen, Fulin Luo, Ying Zhang, Lei Pei, Xiaoxin Lv, Dan Shao,
Chunjing Lin, Zhigang He, Chaofeng Pan, Liang Liu, Xiuliang Zhao, Limei Wang (교신),
**"A direct diagnosis method for degradation modes of LiFePO4 batteries based on
mechanism analysis"**, *Applied Energy* **426** (2026) 128689 의 **절별 해체분석**.

이 저장소가 이 논문을 흡수하는 이유는 세 가지다.

1. **이 계보에서 처음으로 LLI 와 LAM_NE 둘 다에 재료 수준의 measured 라벨**이 붙었다
   — 코인 반쪽전지 용량(LAM_NE, 4 셀)과 XRD 의 LiC₆/LiC₁₂ 회절 피크 세기(LLI, 4 셀).
   OCV 적합값과의 최대 편차가 각각 **1.35 % / 1.68 %** (`[인쇄]`). 우리가 "손으로
   맞춘 α·β 가 맞는지" 를 검증할 때 필요한 **독립 근거의 두 번째 형태**(첫째는
   [[reference-electrode-halfcell-dma]] 의 기준전극)다 — 단 그 라벨 자체의 대가(교차
   셀 보간, 오차 막대 0)를 §7 에 적었다.
2. **"direct diagnosis"** — 적합 없이 IC 곡선의 봉우리 **면적**으로 LLI(Ah)와 LAM_NE(%)를
   읽는다 (식 21–23). LFP 의 평탄 양극이 full-cell dQ/dV 봉우리를 **음극 상(stage) 용량
   그대로**로 만들어 주기 때문에 가능한 것이고, 그 조건이 NMC·Si/Gr 로 옮겨지는지가
   `bms-balancing/` 요구서의 관심사다.
3. **비유일성을 인쇄하고(식 1 → `X1–X4` 재조합: `[인쇄]` "To obtain unique parameter
   results, the variables in Eq. (1) need to be recombined") 물리 사전믿음(입자 파괴 확률
   균일, 식 9)으로 다시 가른다.** [[halfcell-window-parametrization-lineage]] 의 "여분을
   죽이는 세 가지" 에 **등식의 새 변종(사전믿음 등식)** 이 하나 더 생긴다. 그리고 LFP 의
   평탄 양극이 `(X1, X3)` — 곧 LAM_PE ↔ LLI — 를 구조적으로 못 가른다는 것을 이 논문의
   식 (1)·(5)·(20)과 Fig. 3(a) 가 함께 보여 준다 (§4.4, 이 digest 의 판단).

**표기 규칙** (이 위키 관례 3구분 + 1):
- `[인쇄]` — 논문 본문/식/표에 글자로 있는 것
- `[도표]` — 그림에서 눈으로 읽은 근사값 (**원 데이터가 아니다**)
- `[해석]` — 이 문서를 쓰면서 붙인 판단. **논문의 주장이 아니다**
- `[재현]` — 원문 값을 이 세션에서 산술로 옮긴 것 (계산식을 함께 적는다)

- 원본 파일: 로컬 업로드 PDF `20_direct_diagnosis_degradation_modes_lfp.pdf` (15쪽,
  12,264,369 bytes, PDF sha256
  `5a01e314ac2c881e2d7a1b27c227226c960c18f6e2a6b63f17aa178351aa1842`; 저장소에
  바이너리를 넣지 않는다)
- 크로핑 그림: `raw/figures/cui2026_direct-diagnosis-lfp-degradation-modes/` (fig 17장 +
  tab 6장). **도구가 Fig. 6 과 Fig. 7 을 한 장(`fig_6.png`)으로 잘랐다** — 캡션이 한
  줄에 붙어 있어서다. `figures.json` 에 `f7` 항목이 없으며 불변층이라 덧쓰지 않았다.
  이 digest 를 쓰기 전에 **Fig. 3, 4, 6(+7), 8, 9, 10, 11, 12, 14, 15, 17, 18 의 12장을
  Read 로 직접 봤다.** Fig. 1(시험대 사진), Fig. 2(좌표계 도식), Fig. 5(XRD 패턴),
  Fig. 13(봉우리 세기·면적 통계), Fig. 16(순서도)은 안 봤다. 표 6장은 PDF 텍스트로.
- 페이지 참조는 PDF 페이지 = 저널 페이지 (1–15).
- 같은 제1저자의 다른 논문이 이 위키에 있다:
  `raw/papers/cui2024_electrode-utilization-formation-cycle-life.md` (**다른 Cui**,
  formation/전극 활용도). 혼동 주의 — 이 문서는 **Cui (Jiangsu Univ., L. Wang 그룹)
  2026** 으로 부른다.

---

# 원문에 없어서 확인이 필요한 것 (읽기 전에 먼저 본다)

| # | 공백 | 왜 문제인가 |
|---|---|---|
| G1 | **오차 막대가 하나도 없다.** SOH 당 셀 1개(No. 1–8), 코인셀은 3 사이클 평균이라고만. XRD 세기비의 반복도 없음. | "최대 편차 1.35 % / 1.68 %" 가 잡음 수준 안인지 밖인지 알 수 없다. |
| G2 | **노화 프로토콜의 전류·전압이 없다.** `[인쇄]` "According to the battery technical specification … CC-CV charging and CC discharging" 뿐. | 셀마다 사이클 수·조건이 같은지, "conventional aging" 이 무엇인지 정의되지 않는다. |
| G3 | **모델의 `U_p(·)`, `U_n(·)` 곡선 출처가 없다.** 코인 반쪽전지는 **용량**에만 쓰였다고 적혀 있고 OCP 곡선을 어디서 가져왔는지(fresh 코인셀? 문헌?) 없다. | 형상 불변 전제([[halfcell-ocp-shape-invariance]])를 어느 곡선에 걸었는지 모른다. |
| G4 | **PSO 의 탐색 범위·초기값이 없다.** 개체 100·반복 200·관성 0.7 만. | Fig. 3(a) 의 `X1` 이 8개 SOH 에서 **완전히 같은 값**(`[도표]` ≈22.7 Ah)으로 보인다. 데이터가 정한 것인지 경계/초기값이 정한 것인지 구분 불가 (§4.4). |
| G5 | **`(X1, X3)` 의 식별 가능성을 논하지 않는다.** `identifiab*` 2회는 문헌 소개와 "C/25 연속 데이터가 practical identifiability 에 좋다" 뿐. | LFP 양극 창 하단이 관측 창 밖이라 `X1 − X3` 만 구속된다 (§4.4). 이는 LAM_PE ↔ LLI 축퇴이고 이 카드의 질문 그 자체다. |
| G6 | **li/de 분할은 가정이다** (식 9: 파괴 확률이 리튬화 상태와 무관 → 격리 부분의 리튬화도 = 순환 구간 중점). 시험이 없다. | Birkl 2017 이 "동시 LLI 가 있으면 li/de 는 유일하게 식별되지 않는다" 고 인쇄한 그 자리를 **사전믿음으로 닫은 것**. 결과 `LAM_liNE/LAM_NE ≈ 0.36` 은 구성상 순환 구간 중점(≈0.39)이다 (§11.3). |
| G7 | **XRD-LLI 의 보정에 다른 셀의 LAM_NE 를 쓴다.** `[인쇄, §3.3.2]` "a linear interpolation method based on the NE coin half-cell capacities of No. 5–8 batteries is employed to estimate LAM_NE" — XRD 는 No. 1–4 셀, 코인셀은 No. 5–8. | "독립 라벨" 이 절반만 독립이다. 보정량은 `[도표]` 최대 8 pp (24.97 → ≈16.9 %) 로 LLI 자체의 절반 크기. |
| G8 | **IC 법의 정답 축이 OCV 적합값이다.** Fig. 14 의 비교 대상은 `LLI-OCV`, `LAM-OCV`. 재료 수준 라벨은 OCV 법에만(그것도 4+4 셀) 대조됐다. | "1.79 % / 1.62 %" 는 fitted 라벨 재현 오차다. |
| G9 | **`Q_fresh` 값이 없다** (식 18·23 의 분모). | `[재현]` 3.40 Ah / 17.2 % ≈ 19.8 Ah 로 역산할 수 있을 뿐. |
| G10 | **가상 배터리(Table 5)가 `LAM_deNE = LAM_liNE` (1:1) 로 만들어졌는데**, 같은 논문의 진단 결과(Fig. 3b)는 `[도표]` ≈1.75:1 이다. | "de 와 li 가 Peak C 에서 서로 상쇄한다" 는 결론(§4.1.2)이 **1:1 구성에서만** 성립할 수 있다 (§8.4). |
| G11 | **C-rate 보정 계수(1, 1.19, 1.26, 1.47)가 같은 셀에서 나온 오프라인 교정**이다 — 서론에서 남의 방법을 비판한 그 항목. 온라인 교정(Fig. 16 주황 상자)은 순서도뿐이고 데이터가 없다. | "offline calibration 없이" 라는 기여 (3) 의 범위가 LLI 에는 닿지 않는다. |
| G12 | **Fig. 15(a) 의 LAM_NE 율 의존이 정량되지 않았다.** 본문은 "not affected by the C-rate … some fluctuations" 인데 `[도표]` SOH 79.4 % 에서 C/3 ≈18 % vs C/25 ≈11.7 %. | 결론 (3) "LAM_NE is insensitive to the C-rate" 가 그림과 어긋난다 (§9.1, §12 불일치 1). |
| G13 | **18650 비교의 기준이 각형 셀의 OCV 적합값을 SOH 로 보간한 것**이다. | "다른 셀 종류에서도 맞는다" 가 아니라 "두 셀 종류의 모드–SOH 관계가 같다고 가정하면 1.5 % 안" 이다. |
| G14 | **Fig. 9 와 Fig. 11 의 봉우리 전압이 `[도표]` ≈40 mV 다르다** (B: ≈3.325 vs ≈3.287 V; C: ≈3.365 vs ≈3.328 V). 충/방전 방향이 어느 그림에도 인쇄돼 있지 않다. | 봉우리를 **전압 위치**로 찾는 온라인 구현(Fig. 16 "voltage is used to determine whether Peak B or Peak C has been reached")에 직접 걸린다. |
| G15 | 사소한 불일치: 18650 SOH 가 본문 79.72 %, Fig. 18 범례 79.76 %. 온도 시험 셀 4개 중 그림엔 3개. | 인용 시 주의. |
| G16 | **데이터 비공개.** `[인쇄]` "Data will be made available on request." | — |

---

## 0. 서지사항 (직접 확인)

`[인쇄]` PDF 메타데이터 및 헤더/푸터:

| 항목 | 값 |
|---|---|
| 제목 | A direct diagnosis method for degradation modes of LiFePO4 batteries based on mechanism analysis |
| 저자 | Yanwei Cui ᵃ, Zheng Chen ᵃ, Fulin Luo ᵃ, Ying Zhang ᵃ, Lei Pei ᵃ, Xiaoxin Lv ᵃ, Dan Shao ᵇ, Chunjing Lin ᶜ, Zhigang He ᵃ, Chaofeng Pan ᵃ, Liang Liu ᵃ, Xiuliang Zhao ᵈ, Limei Wang ᵃ (교신, wanglimei@ujs.edu.cn) |
| 소속 | a: Automotive Engineering Research Institute, Jiangsu University · b: Shunde Polytechnic University · c: Chongqing University of Technology · d: School of Automotive and Traffic Engineering, Jiangsu University |
| 저널 | Applied Energy 426 (2026) 128689, doi 10.1016/j.apenergy.2026.128689 |
| 이력 | Received 31 March 2026 · Revised 2 August 2026 · Accepted 12 August 2026 · Available online 18 August 2026 |
| 키워드 | LiFePO4 battery · Degradation modes diagnosis · Mechanistic decoupling · Incremental capacity curve |
| 분량 | 15쪽 (본문 §1–5 + 참고문헌 53편), 그림 18, 표 6, SI 없음 |
| 자금 | NSFC 52477214, 52072155 · Jiangsu BZ2023039 · KYCX25_4191 |
| 데이터 | "available on request" |

---

## 1. 한 문단 요약

`[해석]` 20 Ah 각형 LFP/graphite 셀 10개(8개 노화 SOH 79.4–96.5 %, 2개 기준)에 대해
(i) C/25 방전 의사-OCV 를 4-파라미터 `X1–X4`(양극 가용 용량 · 음극 가용 용량 · 좌표
오프셋 `LAM_liNE − LAM_dePE + LLI` · 방전 종료 음극 리튬화도) 모델로 PSO 적합하고,
"입자 파괴 확률이 리튬화 상태와 무관" 이라는 가정으로 `X1–X3` 를 다섯 모드(LLI,
LAM_li/de × PE/NE)로 되푼다 → LAM_PE ≈ 0, LAM_NE 최대 2.83 Ah, LLI 최대 3.40 Ah.
(ii) 분해한 전극의 코인 반쪽전지 용량(LAM_NE)과 음극 XRD 의 LiC₆/LiC₁₂ 피크 세기(LLI)
로 재료 수준 라벨을 만들어 OCV 적합값과 대조 → 최대 편차 1.35 % / 1.68 %. (iii) OCV
적합값을 기준으로 **가상 배터리**(LLI 0–3.5 Ah, LAM_de = LAM_li 0–1.75 Ah)를 만들어
IC 곡선의 세 봉우리(A·B·C)가 모드마다 어떻게 반응하는지 정리 — **Peak B 면적은 LLI
에 불변·LAM_NE 에 감소, Peak C 면적은 LLI 가 지배**(de·li 의 효과가 상쇄) — 하고,
`LAM_NE = ΔArea_B/Area_B,fresh`, `LLI′ = ΔArea_C/Q_fresh` 라는 **적합 없는 직접
진단식**을 세운다 (OCV 적합값 대비 최대 편차 1.79 % / 1.62 %). (iv) C-rate(C/25–C/3;
LLI 는 율에 따라 최대 6.07 % 낮아져 계수 1/1.19/1.26/1.47 로 보정), 온도(0–55 °C),
셀 형식(18650 1.3 Ah)에 대한 적응성을 보인다. **모드 값의 불확실성·유일성 분석은
없다.**

---

## 2. p.1–2 — Highlights / Abstract / §1 Introduction

### 2.1 Highlights `[인쇄]`

- "Based on the assumption of particle fracture probability the DMs are decoupled."
- "Quantitative association of DMs across material- and cell-level is established."
- "Battery maximum lithium content is quantitative calculated by XRD testing."
- "Direct Online diagnosis of LLI and LAM is achieved by the IC curve."
- "Diagnostic method enables accuracy diagnosis in real-world scenarios."

### 2.2 Abstract 에서 뽑은 명제 `[인쇄]`

- "Existing non-destructive diagnostic methods either rely on specific assumptions or
  require offline-calibrated functions, making the accuracy of the results difficult to
  validate".
- "decoupling and quantitative calculation methods for DMs at both the material- and
  cell-level are proposed, thereby validating the accuracy of the Open-Circuit Voltage
  (OCV)-based method."
- "the effects of different DMs on Incremental Capacity (IC) curve are clarified through
  mechanism analysis, based on which a direct online diagnostic method for DMs is
  proposed."

### 2.3 §1 문헌 지도 — 이 위키와 겹치는 것 `[인쇄]`

- Dubarry et al. [22] ([[dubarry-mechanistic-mode-synthesis]]) 가 모드 ↔ OCV/IC/DV 의
  정량 관계를, Wang et al. [23] 이 "unified coordinate system … coordinate
  transformation among electrode potentials" 을, **Lin et al. [24]**
  ([[np-lip-ocv-reparametrization]]) 가 "re-parametrized the OCV model based on the
  negative-to-positive ratio and lithium-to-positive ratio, and then conducted an
  identifiability study on DMs". Birkl 2017 [9] 는 모드 분류의 근거로만 인용된다.
- 다른 IC/DV 봉우리 추적법에 대한 비판: "their work requires offline calibration of such
  correlations, and the diagnostic results lack direct ground-truth validation."
- 세 물음: "(i) How to provide ground-truth for the diagnostic results of external
  characteristic methods? (ii) How to achieve refined decoupling and quantitative
  characterization of different DMs? (iii) How to enable online quantitative diagnosis
  of DMs in practical scenarios?"

### 2.4 기여 4개 `[인쇄]` (요약)

(1) OCV 진단 모델 + "a normalization-based framework and a probabilistic strategy … for
material- and cell-level DM decoupling"; (2) 재료–셀 수준 정량 연관으로 OCV 법 검증;
(3) POCV·IC 에 대한 모드 효과 규명 → IC 특징 봉우리 기반 직접 정량 진단 ("overcomes
the limitation of conventional IC-based methods that rely on offline calibration");
(4) C-rate·온도·셀 형식 적응성.

---

## 3. p.2–3 — §2 Experimental and testing system

`[인쇄]`:

| 항목 | 값 |
|---|---|
| 셀 | 각형 LiFePO₄ (중국 제조사), **정격 20 Ah**, 3.2 V, 7 mΩ, 485 ± 15 g, 130 × 70 × 27 mm (Table 2) |
| 셀 수 | 10 — **8개 노화**(No. 1–8), 2개 기준(No. 9, 10) |
| 노화 | 25 °C, CC-CV 충전 / CC 방전 "according to the battery technical specification" (G2) |
| SOH 정의 | 가용 방전 용량 / 정격 (GB/T 31486) |
| SOH (Table 3) | No.1 93.47 · No.2 89.12 · No.3 86.77 · No.4 79.41 · No.5 96.54 · No.6 90.61 · No.7 83.63 · No.8 79.76 · No.9 **102.3** · No.10 99.1 |
| 장비 (Table 1) | NBT5V20AC16-T (0–5 V, 0–20 A, ±0.05 % FS) · 챔버 ETE-GDJS-150 L · 코인셀 CT-4008Tn-5V10mA (5 μA–10 mA) · BLC-150 |

`[해석]` 기준 셀이 둘(102.3 %, 99.1 %)이고 어느 것이 모드의 "fresh" 인지가 그림마다
다르다 — Fig. 3(b) 는 99.1 % 에서 0, Fig. 6·8 은 102.3 % 를 포함한다. 두 기준 사이의
3.2 % 용량 차이는 이 논문의 검증 편차(1.35–1.79 %)보다 크다.

---

## 4. p.3–5 — §3.1 셀 수준 OCV 진단 모델

### 4.1 모드 분류와 좌표계 `[인쇄]`

LAM → LAM_PE, LAM_NE → 각각 de-lithiated/lithiated (`LAM_dePE`, `LAM_liPE`, `LAM_deNE`,
`LAM_liNE`) [22,37,38] — [[birkl-ocv-degradation-diagnostic]] 과 같은 5-모드 분류.
좌표계 네 개: `x_PE–y_PE`, `x_APE–y_APE`(Available PE), `x_NE–y_NE`, `x_ANE–y_ANE`.
기준 좌표는 `x_ANE`. 변환은 Ref. [23] (Fig. 2 — 안 봄).

### 4.2 식 (1)–(8) — 원문 이미지로 확인

식 (1):
```
OCV(x_ANE) = U_p(x_APE) − U_n(x_ANE)
           = U_p( 1 − [x_ANE·(C_NE − LAM_liNE − LAM_deNE) + LAM_liNE − LAM_dePE + LLI]
                      / (C_PE − LAM_liPE − LAM_dePE) ) − U_n(x_ANE)
```
`[인쇄]` "**To obtain unique parameter results, the variables in Eq. (1) need to be
recombined.**" →
```
X1 = C_APE = C_PE − LAM_liPE − LAM_dePE                       (2)
X2 = C_ANE = C_NE − LAM_liNE − LAM_deNE                       (3)
X3 = LAM_liNE − LAM_dePE + LLI                               (4)
OCV(x_ANE) = U_p( 1 − (x_ANE·X2 + X3)/X1 ) − U_n(x_ANE)       (5)
POCV = OCV + I·R0   (충전 +, 방전 −)                           (6)
x_ANE = X4 + ΔQ_bat / X2                                     (7)
min RMSE = Σᵢ (POCVᵢ − POCV(x_ANE)ᵢ)²                         (8)
```
- 관측: **C/25 방전** 의사-OCV (`[인쇄]` "POCV is the voltage measured at a low
  discharging rate of C/25"). 이유: 등간격 SOC 휴지 OCV 의 "limited data and long
  relaxation times" 를 피한다 — "It is of great significance for ensuring the practical
  identifiability of model parameters" (이 논문에서 `identifiab*` 가 방법에 대해 쓰인
  유일한 자리).
- `X4` = 방전 컷오프에서의 `x_ANE` ("may not be zero").
- 식 (8) 은 "RMSE" 라 부르지만 인쇄된 식은 제곱합이다 (루트·1/n 없음). `[해석]` 최소화
  대상으로는 동치.

`[해석]` 좌표 대응: `X1 ↔ a_PE·Q`, `X2 ↔ a_NE·Q`, `X3/X1 ↔` 양극 창의 오프셋, `X4 ↔`
음극 창 하단 — 우리 `[a_PE, b_PE, a_NE, b_NE]` 와 같은 4-창 좌표계다. Birkl 이 컷오프
등식 2개로 3개로 줄인 것과 달리 여기서는 4개를 다 열어 두고 `X4 ≈ 0` 은 결과로 얻는다.
**재조합 자체가 축퇴의 인쇄**다: 7개 물리량(`C_PE, C_NE, LAM ×4, LLI`)이 OCV 에서는
3개 결합으로만 보인다는 것을 식 (2)–(4) 가 말한다.

### 4.3 PSO 와 결과 — Fig. 3 (직접 봄)

`[인쇄]` PSO: 개체 100, 반복 200, 관성 가중 0.7 (G4). "the NE capacity exhibits
noticeable decrease, whereas PE capacity shows only slight variation … X3 increases
linearly as SOH decreases. According to the previously derived equations, LLI
constitutes the main component of X3."

Fig. 3(a) `[도표]` (Capacity/Ah vs SOH 79–99 %): `X1` ≈ **22.7 Ah 로 여덟 점이 같은
높이**; `X2` ≈25.5 (99 %) → ≈22.8 (79.4 %); `X3` ≈2.3 (99 %) → ≈6.7 (79.4 %) 단조
증가; `X4` ≈ 0 전 구간.
Fig. 3(b) `[도표]` (모드 Ah vs SOH): LLI 0 → ≈3.4; `LAM_deNE` 0 → ≈1.6–1.8; `LAM_liNE`
0 → ≈0.95–1.05; `LAM_dePE`, `LAM_liPE` ≈0–0.1. SOH ≈79.4/79.8 % 에 두 점(No. 4, 8)이
있고 값이 조금 다르다 (LLI ≈3.2 vs 3.4).
`[인쇄]` "The maximum loss of capacity caused by LLI, LAMNE, are 3.40 Ah, 2.83 Ah,
respectively."

### 4.4 ★ LFP 평탄 양극이 만드는 `(X1, X3)` 축퇴 — 이 digest 의 판단 `[해석]`

식 (5)·(7)에서 양극 리튬화도는 `x_APE = 1 − (ΔQ + X4·X2 + X3)/X1`. `X4 ≈ 0` 이면
- 방전 종료(ΔQ = 0): `x_APE = 1 − X3/X1` ≈ 1 − 2.3/22.7 ≈ **0.90** — 양극은 평탄역
  위에 있다. 식 (20)과 Fig. 10 (`[도표]` 종료 `x_PE ≈ 0.88`) 이 이를 확인한다.
- 충전 종료(ΔQ = Q_EOC): `x_APE → 0` (양극 제한) → **`X1 − X3 = Q_EOC`**.

즉 관측이 구속하는 것은 `X1 − X3` 한 개다. `X1` 과 `X3` 를 같은 양만큼 함께 움직이면
양극 곡선의 **어느 구간이 창에 들어오는가**(`Q_EOC/X1`)만 바뀌는데, LFP 평탄역에서 그
구간의 전압 차이는 수 mV 다. 따라서 데이터는 `X1` 을 (그리고 `X3` 를) 거의 정하지
못하고, 정하는 것은 **PSO 의 경계·초기값**이다 — Fig. 3(a) 에서 `X1` 이 여덟 점 모두
정확히 같은 높이인 것이 그 징후다 (G4).

이것이 무엇을 뜻하는가: `X3 = LAM_liNE − LAM_dePE + LLI` 이므로 `X1` 이 잘못 고정되면
그 오차가 **LLI 로 흘러간다** — 식 (1) 에서 `Q_EOC = C_PE − LAM_liPE − LAM_liNE − LLI`
로 **LLI 와 LAM_liPE 가 같은 부호·같은 크기로 용량에 들어가고**, 둘을 가르는 정보는
평탄역 기울기뿐이다. 즉 **LFP 의 OCV 적합은 LAM_PE 와 LLI 를 원리적으로 거의 못
가른다.** 이 논문에서 그 축퇴가 해를 끼치지 않은 이유는 **재료 수준 측정이 LAM_PE ≈ 0
을 독립으로 확인해 줬기 때문**이다 (Fig. 4a 코인셀, Fig. 5a XRD) — 그래서 `X1` 을
fresh 값에 묶어 둔 것이 우연히 옳았다. LAM_PE 가 실제로 있는 셀(가혹 조건; 저자도
결론 한계 (2) 에서 유보)에서는 같은 절차가 LAM_PE 를 LLI 로 읽는다. 논문은 이 구조를
어디에도 적지 않는다 (G5).

이 판단의 근거는 전부 논문의 식 (1)·(5)·(20)과 Fig. 3(a)·10 이며, 감도의 실제 크기
(평탄역 기울기가 주는 정보량)는 **우리 프레임으로 잴 수 있고 재지 않았다**.
[[marongiu2016_lfp-onboard-capacity-halfcell]] 계열에서 이 위키가 닫힌 형태로 푼 LFP
null 과 같은 자리다.

---

## 5. p.5 — §3.1.2 파괴 확률 가정으로 모드 되풀기 (식 9–12)

`[인쇄]` "Assuming that the probability of active particle fracture is equal under
different lithiation conditions during a single lithiation/delithiation process, the
lithiation ratio of the isolated portion after fracture is expected to be approximately
consistent with the average lithiation ratio of the active material during cycling [39]."

```
x_crk,p(soh) = [min(x_APE) + max(x_APE)]/2 ,  x_crk,n(soh) = [min(x_ANE) + max(x_ANE)]/2   (9)
min(x_ANE) = X4 ;  max(x_ANE) = X4 + Q_aging/X2
min(x_APE) = 1 − (X4·X2 + X3 + Q_aging)/X1 ;  max(x_APE) = 1 − (X4·X2 + X3)/X1            (10)
LAM_li(soh) = LAM_li(soh−Δsoh) + [x_crk(soh) + x_crk(soh−Δsoh)]/2 × [C_A(soh) − C_A(soh−Δsoh)]  (11)
LAM_de(soh) = C_A(fresh) − C_A(soh) − LAM_li(soh)                                            (12)
LLI = X3 − LAM_liNE + LAM_dePE   (식 4 로부터)
```
식 (11) 은 SOH 간격 `Δsoh` 마다 잃은 가용 용량에 그 구간 평균 리튬화도를 곱해 누적한다
(경로 의존; 진단 간격에 따라 값이 달라질 수 있다 — 논문은 언급 없음).

`[해석]` 이것이 Birkl 2017 이 "`LAM_li`/`LAM_de` 는 동시 LLI 가 있으면 유일하게 식별
되지 않는다" 고 인쇄하고 **포기한** 분할을 되살리는 방법이다. 데이터가 아니라 **가정
하나(파괴 확률 균일)** 로 닫는다. 결과 `LAM_liNE/LAM_NE` `[재현]` 1.03/2.83 = **0.36**
— 그런데 음극 순환 구간이 `x_ANE ∈ [0, 20/25.5 ≈ 0.78]` 이므로 그 중점은 **0.39**.
즉 이 비는 측정이 아니라 **구성**이다. 논문의 Highlights 첫 줄이 "Based on the
assumption …" 으로 시작하는 것은 정직하다; 다만 그 가정의 시험은 없다 (G6).
[[halfcell-window-parametrization-lineage]] 의 "여분을 죽이는 방법" 에서 이것은
**등식**의 새 변종 — 컷오프 전압 등식(Birkl)이 아니라 **물리 사전믿음 등식**이다.

---

## 6. p.5–7 — §3.2 재료 수준 진단

### 6.1 §3.2.1 코인 반쪽전지 용량 — Fig. 4 (직접 봄) `[인쇄]`

- No. 1–4 는 **만충 상태**에서, No. 5–8 은 **만방 상태**에서 분해. Li 금속 상대극 코인셀,
  25 °C, **0.2 mA** CC, 3 사이클 평균.
- 만충 분해 음극은 "lithium-carbon compound, which exhibits considerable instability" →
  **음극 용량은 No. 5–8 만** 보고.
- Fig. 4 `[도표]`: (a) PE 코인셀 ≈3.55–3.65 mAh, No. 1–8 거의 평탄; (b) NE 코인셀 No. 5
  ≈2.82 → No. 6 ≈2.68 → No. 7 ≈2.57 → No. 8 ≈2.47 mAh, 직선적 감소.

`[해석]` 코인셀 용량 3.6 mAh / 2.8 mAh 는 전극 조각 면적에 비례하므로 절대값은 의미가
없고 비만 쓰인다 (식 17). 면적 재현성(펀치 지름 편차)이 곧 라벨 잡음인데 인쇄돼 있지
않다.

### 6.2 §3.2.2 XRD 최대 리튬 함량 — Fig. 5 (안 봄), Fig. 6 (직접 봄) `[인쇄]`

- PANalytical X'Pert3 Powder, 2θ 10–80°, step 0.013°, 실온.
- 양극: FePO₄ 피크 거의 불변("LAM in the PE is negligible"), LiFePO₄ 피크 세기 감소
  ("verifies the occurrence of LLI") — 그러나 피크가 분산·중첩 → **음극을 쓴다.**
- 음극: 만충 상태의 LiC₆·LiC₁₂ 피크 세기가 SOH 에 따라 크게 변함; 만방 상태는 탄소상
  (완전 탈리튬) → 만충 피크 = **최대 리튬 함량**.
- 식 (13) `Li_xC = (1/6)·x₁/(x₁+x₂) + (1/12)·x₂/(x₁+x₂)` (`x₁` = LiC₆ 세기, `x₂` = LiC₁₂
  세기), 식 (14) `LLI_XRD = (Li_xC,fresh − Li_xC,aging)/Li_xC,fresh`.
- Fig. 6 `[도표]`: `LLI_XRD` ≈0.3 (102.3 %), ≈9.0 (93.5 %), ≈13.8 (89.1 %), ≈15.7
  (86.8 %), **≈25** (79.4 %). `[인쇄]` "the variation in the maximum lithium content
  reaches 24.97%, exceeding the corresponding SOH degradation … the diagnosed LLI_XRD
  encompasses the LAM_NE" → 식 (15) `Li_xC′ = Li_xC/(1 − LAM_NE)`, 식 (16) `LLI′_XRD`.

`[해석]` 식 (13) 은 두 상의 **세기비**를 몰비로 읽는다 — 흡수·배향·결정성 보정이
없다. 그리고 탄소를 1 로 정규화하므로 잃어버린 탄소(LAM_NE)가 보이지 않는다는 것을
저자가 인정하고 (15) 로 보정한다. 그 보정의 `LAM_NE` 가 **다른 셀**에서 온다 (G7).

---

## 7. p.7–8 — §3.3 연관 분석 (검증의 실체)

### 7.1 §3.3.1 LAM_NE — Table 4, Fig. 7 (직접 봄; `fig_6.png` 오른쪽)

식 (17): `LAM_NE,Cap = (C_NE,Cap,fresh − C_NE,Cap,aging)/C_NE,Cap,fresh`,
`LAM_NE,OCV = LAM_NE,aging / C_NE,OCV,fresh`.

Table 4 `[인쇄]`:

| | No. 5 (96.54 %) | No. 6 (90.61 %) | No. 7 (83.63 %) | No. 8 (79.76 %) |
|---|---:|---:|---:|---:|
| `LAM_NE,Cap` (%) | 0 | 4.55 | 8.91 | 11.54 |
| `LAM_NE,OCV` (%) | 0 | 3.20 | 7.93 | 10.40 |
| 차 (Cap − OCV) `[재현]` | 0 | **1.35** | 0.98 | 1.14 |

`[인쇄]` "strong consistency, with a maximum deviation of only 1.35%."
`[해석]` 세 노화점 모두 **OCV 쪽이 낮다** — 편차가 무작위가 아니라 계통적(≈1.0–1.35 pp).
기준이 No. 5 (96.54 %) 라 fresh 가 아니다. Fig. 7 `[도표]`: 코인셀(2.49 → 2.815 mAh)과
ANE(22.65 → 25.3 Ah)가 SOH 80–96.5 % 에서 거의 직선으로 같이 움직이고, 코인셀 쪽이
상단에서 조금 더 가파르다.

### 7.2 §3.3.2 LLI — Fig. 8 (직접 봄)

식 (18) `LLI_OCV = LLI_aging / Q_fresh` (G9). `[인쇄]` "a linear interpolation method
based on the NE coin half-cell capacities of No. 5–8 batteries is employed to estimate
LAM_NE" (No. 1–4 의 XRD 보정용).

Fig. 8 `[도표]` (LLI % vs SOH):

| SOH | 102.3 | 93.5 | 89.1 | 86.8 | 79.4 |
|---|---:|---:|---:|---:|---:|
| `LLI_OCV` | ≈0.2 | ≈5.6 | ≈9.2 | ≈11.9 | ≈17.2 |
| `LLI′_XRD` | ≈0.2 | ≈7.3 | ≈8.9 | ≈10.7 | ≈16.9 |

`[인쇄]` "maximum deviation of only 1.68%" (`[재현]` 93.5 % 에서 7.3 − 5.6 ≈ 1.7 ✓).
"This result validates the accuracy of the OCV-based method and the feasibility of the
decoupling strategy based on particle fracture probability."

`[해석]` 마지막 문장은 과하다. XRD′ 는 LAM_NE **총량**으로만 보정되므로 (식 15) li/de
**분할**에 대해서는 아무 정보가 없다 — 분할이 틀려도 `LLI′_XRD` 는 같다. 검증된 것은
`LLI` 와 `LAM_NE` 의 총량 둘뿐이고, 그것도 각각 4 셀·오차 막대 없음·기준 셀 상이·보정
LAM_NE 교차 셀 (G1, G7)이다. 그럼에도 **이 계보에서 LLI 에 재료 라벨을 붙인 첫 편**
이라는 사실은 남는다.

---

## 8. p.8–11 — §4 IC 곡선 기반 진단

### 8.1 §4.1 봉우리 정의 — Fig. 9 (직접 봄)

`[도표]` 위: 용량(0–20 Ah) vs 전압(3.16–3.45 V); 아래: dQ/dV (0–250 Ah/V). **Peak A**
≈3.24 V (≈55), **Peak B** ≈3.325 V (≈240), **Peak C** ≈3.365 V (≈230). 충/방전 방향
미인쇄 (G14). `[인쇄]` "three prominent characteristic peaks caused by phase transition
processes … defined as Peak A, Peak B, and Peak C from left to right."

왜 가상 배터리인가 `[인쇄]`: "it is almost impossible to obtain a battery that contains
only a single DM under practical conditions. Therefore, the diagnosed results of the
OCV-based method are employed as references, and a controlled variable approach is
adopted to construct the virtual batteries" — Table 5:

| | S-1 | S-2 | S-3 | S-4 | S-5 | S-6 | S-7 | S-8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LLI (Ah) | 0 | 0.5 | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 |
| LAM_deNE (Ah) | 0 | 0.25 | 0.5 | 0.75 | 1 | 1.25 | 1.5 | 1.75 |
| LAM_liNE (Ah) | 0 | 0.25 | 0.5 | 0.75 | 1 | 1.25 | 1.5 | 1.75 |

식 (19)–(20) (양극 좌표 `x_PE` 로 변환한 POCV 와 그 정의역):
```
POCV(x_PE) = U_p( (x_PE·C_PE − LAM_liPE)/(C_PE − LAM_liPE − LAM_dePE) )
           − U_n( ((1 − x_PE)·C_PE − LAM_liNE − LLI)/(C_NE − LAM_liNE − LAM_deNE) ) + I·R0
x_PE ∈ [ max(LAM_liPE, C_PE − C_NE + LAM_deNE − LLI)/C_PE ,  min(C_PE − LAM_dePE, C_PE − LLI − LAM_liNE)/C_PE ]
```
`[해석]` 정의역 상한 `(C_PE − LLI − LAM_liNE)/C_PE` 가 §4.4 의 "LLI 와 LAM_li 가 같은
자리에 들어간다" 를 논문 자신의 식으로 보여 준다 (양극 쪽 `LAM_liPE` 는 하한에만).

### 8.2 §4.1.1 POCV 에 대한 효과 — Fig. 10 (직접 봄)

`[도표]` (전압 3.6 → 2.4 V vs `x_PE` 0–0.9, 방전): (a) LLI 0 → 3.5 Ah: 컷오프 도달
`x_PE` ≈0.88 → ≈0.73, 음극 상 특징도 왼쪽으로; (b) LAM_deNE 0 → 1.75: 곡선 거의 겹침,
종료 ≈0.88 그대로; (c) LAM_liNE 0 → 1.75: 종료 ≈0.88 → ≈0.81; (d) S-1 → S-8: ≈0.88 →
≈0.65. `[인쇄]` "the lithiation ratio range gradually narrows as LLI and LAM_liNE
increase, whereas LAM_deNE has almost no effect on the lithiation ratio range."

### 8.3 §4.1.2 IC 에 대한 효과 — Fig. 11, Fig. 12 (직접 봄) ★ 부호 구조

전처리 `[인쇄]`: Savitzky–Golay **1차 다항, 창 21** [47].

Fig. 11 `[도표]` (dQ/dV 0–600 Ah/V vs 3.22–3.35 V; Peak B ≈3.287 V, Peak C ≈3.328 V):

| 패널 | 스윕 | Peak B 높이 | Peak C 높이 |
|---|---|---|---|
| (a) LLI 0 → 3.5 Ah | 단독 | ≈390 **불변** | ≈430 → ≈175 **단조 감소** |
| (b) LAM_deNE 0 → 1.75 | 단독 | ≈390 → ≈365 (약간 ↓) | ≈430 → **≈500 (↑)** |
| (c) LAM_liNE 0 → 1.75 | 단독 | ≈390 → ≈365 (약간 ↓) | ≈430 → ≈380 (↓) |
| (d) S-1 → S-8 | 복합 | ≈390 → ≈335 | ≈430 → ≈190 |

봉우리 **위치**는 네 패널 모두 고정. `[인쇄]` "with the increase of LLI, the intensity
of Peak C gradually decreases, while Peak B remains basically stable … as LAM_deNE and
LAM_liNE increase, the intensity of Peak B decreases, whereas the intensity of Peak C
shows increasing and decreasing trends, respectively … Compared to LLI, LAMNE exerts a
relatively minor influence on the IC curve during the early stages."

Fig. 12 `[도표]` (면적 Ah vs S-1…S-8): (a) Peak B — LLI 단독 ≈7.35 평탄(S-8 에서 7.2),
복합 7.35 → 6.3 단조 감소; (b) Peak C — LLI 단독 5.45 → 2.7, 복합 5.45 → 2.6 **겹침**.
`[인쇄]` "the effects of LAM_deNE and LAM_liNE on the high-voltage characteristic peak
can offset each other, resulting in the peak area change of Peak C being predominantly
governed by LLI."

`[해석]` 부호표로 정리하면 (LFP/graphite, 방전, C/25):

| 관측 | LLI | LAM_deNE | LAM_liNE | LAM_PE |
|---|---|---|---|---|
| Peak B 면적 | **0** | − | − | (스윕 없음 — 가정상 0) |
| Peak C 면적 | **−−** (Ah 로 1:1) | + | − | (스윕 없음) |
| 사용 가능 리튬화 범위 | − | 0 | − | — |

물리적 읽기: Peak C 는 최고 전압 봉우리 = 음극의 **최상단 stage** 용량이고, LLI 는
음극 창을 양극 창에 대해 밀어 **그 최상단 stage 를 컷오프가 잘라내므로** Peak C 면적
감소(Ah) = LLI(Ah) — 식 (23) 의 분모를 `Q_fresh` 로 바꾸는 "보정" 이 바로 이 항등식이다.
Peak B 는 중간 stage 용량 = 음극 활물질에 비례 → 상대 감소 = LAM_NE. **LFP 이라서 되는
것**이다: 양극이 평탄해 full-cell dQ/dV 봉우리가 음극 stage 용량 그대로다. NMC 에서는
봉우리가 양극·음극 특징의 합성이라 이 1:1 이 깨진다 (§14 한계).

### 8.4 ★ "상쇄" 결론의 범위 `[해석]` (G10)

Table 5 는 `LAM_deNE = LAM_liNE` 로 만들었다. Fig. 11(b)(c) 의 단독 효과는 1.75 Ah 에
대해 Peak C 높이 ≈+70 / ≈−50 (`[도표]`) 이라 1:1 에서도 완전 상쇄는 아니고, 논문 자신의
Fig. 3(b) 는 de:li ≈ 1.8:1.03 ≈ **1.75:1** 이다. 그 비로는 순효과 ≈ +72 − 29 ≈ **+43
Ah/V** (LLI 1 Ah 당 ≈ −73 Ah/V 에 해당) → Peak C 로 읽은 LLI 가 ≈0.6 Ah(≈3 %p) **과소**
될 수 있다. Fig. 14(c) 의 편차(1.79 %) 안에 묻힐 크기이지만, "Peak C 는 LLI 만 본다" 는
문장은 **1:1 구성의 산물**이다.

### 8.5 §4.2 진단식과 결과 — Fig. 14 (직접 봄)

식 (21) 면적: `LAM_NE = (Area_B,fresh − Area_B,aging)/Area_B,fresh`,
`LLI = (Area_C,fresh − Area_C,aging)/Area_C,fresh`; 식 (22) 세기(같은 꼴); 식 (23)
`LLI′ = (Area_C,fresh − Area_C,aging)/Q_fresh`.

Fig. 14 `[도표]` (Loss % vs SOH):
- (a) 면적, 식 (21): `LLI-IC` 0 → **≈42** vs `LLI-OCV` 0 → ≈17 (크게 과대); `LAM-IC`
  0 → ≈11.5 vs `LAM-OCV` ≈11.
- (b) 세기, 식 (22): `LLI-IC` → ≈44; `LAM-IC` → ≈14 (면적보다 나쁨).
- (c) 보정 식 (23): `LLI′-IC` ≈ `LLI-OCV` (0 → ≈17); `LAM-IC` ≈ `LAM-OCV`.
`[인쇄]` "the deviation associated with peak area is significantly smaller than that
with peak intensity … peak intensity is a local point feature, which is easily affected
by battery polarization, measurement noise" / "the effect of LLI on the POCV curve mainly
manifests as an overall offset, determined by the entire lithiation ratio rather than
changes in local peak intensity or peak area" / 최대 편차 **LLI 1.79 %, LAM_NE 1.62 %**.

`[해석]` (a)→(c) 의 교정은 "Peak C 면적의 **상대** 감소" 가 아니라 "**절대** 감소(Ah)를
셀 용량으로 나눈 것" 이 LLI 라는 뜻이고, 이는 §8.3 의 항등식이다. 비교 대상이 전부
**OCV 적합값**이라는 것(G8)을 잊지 말 것 — 그림 (c) 는 "IC 가 OCV 적합을 재현한다" 를
보이는 것이지 참값을 보이는 것이 아니다.

---

## 9. p.11–13 — §4.3 적응성

### 9.1 C-rate — Fig. 15 (직접 봄), Table 6 `[인쇄]`

- C/25·C/10·C/5·C/3 (더 높으면 "characteristic peaks tend to merge or disappear").
- 식 (24)(25): 율별 fresh 기준으로 같은 꼴.
- `[인쇄]` "the LAM_NE diagnosed results at three C-rates … exhibit a consistent trend
  with those obtained at C/25, which demonstrate that the diagnosed LAM_NE is not
  affected by the C-rate. However, some fluctuations are observed" — Peak B 가 비대칭이라
  중심 평활이 영향을 줄 수 있다고 덧붙임.
- Fig. 15(a) `[도표]` LAM_NE: SOH 79.4 % 에서 C/3 ≈**18**, C/5 ≈18/14, C/10 ≈15/12.5,
  C/25 ≈11.7; 86.8 % 에서 C/5 ≈10.4 vs C/25 ≈5.4. → 편차 최대 **≈6 pp** (G12).
- Fig. 15(b) `[도표]` LLI: 79.4 % 에서 C/25 ≈16.9 > C/10 ≈13.9 > C/5 ≈12.9 > C/3 ≈10.8 —
  율이 높을수록 단조 감소. `[인쇄]` 최대 편차 **3.25 % (C/10), 4.77 % (C/5), 6.07 %
  (C/3)** → "a negative correlation between LLI and C-rate".
- 보정 계수 `[인쇄]` **1, 1.19, 1.26, 1.47** (LLI–용량손실비 관계에서). Table 6 (보정 후
  LLI %):

| SOH (%) | 96.54 | 93.47 | 90.61 | 89.12 | 86.77 | 83.63 | 79.76 | 79.41 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C/25 | 1.08 | 4.10 | 5.05 | 7.83 | 10.99 | 13.46 | 16.43 | 16.89 |
| C/10 | 1.21 | 3.93 | 6.33 | 7.32 | 10.57 | 12.20 | 14.91 | 16.60 |
| C/5 | 1.28 | 4.47 | 5.77 | 7.54 | 10.84 | 11.87 | 14.75 | 16.29 |
| C/3 | 1.49 | 2.77 | 5.39 | 6.84 | 10.96 | 13.11 | 15.26 | 15.95 |

`[재현]` 보정 후 최대 편차 = 16.43 − 14.75 = **1.68** (79.76 %, C/5) ✓ 인쇄값과 일치.
`[해석]` Table 6 이 첫 열부터 그림 순서(SOH 내림차순)가 아니라 셀 번호가 뒤섞인 순서
(96.54, 93.47, …)라 Fig. 15 와 대조할 때 주의.

### 9.2 §4.3.2 순서도 — Fig. 16 (안 봄) `[인쇄]`

전압으로 Peak B/C 도달을 판정 → 식 (24)(25) → 전류로 C-rate 산출 → **오프라인 교정
함수**로 LLI 보정; 조건·셀 편차로 정확도가 떨어지면 "an online calibration strategy …
based on real measured data" — 실차 부분 충전 구간에서 POCV 를 재구성([52])해 율별
진단과 대조하여 보정 함수를 실시간 구성. 데이터 시연 없음 (G11).

### 9.3 온도 — Fig. 17 (직접 봄) `[인쇄]`

추가 셀 4개 (SOH 100.13/97.66/87.07/83.84 %), C/25, 0–55 °C, 5 °C 간격, Ref. [47] 의
온도 보상. 최대 편차 **LAM_NE 1.59 %, LLI 0.60 %**; 97.66 % 셀의 음수 값은 0 으로.
Fig. 17 `[도표]`: (a) LAM_NE — 83.84 %: 8.7 (10 °C) ~ 10.8 (55 °C); 87.07 %: 4.7–6.3;
(b) LLI — 83.84 %: 13.3–13.9; 87.07 %: 10.2–10.6. (100.13 % 셀은 그림에 없다 — 기준으로
쓰인 것으로 보인다.)

### 9.4 셀 형식 — Fig. 18 (직접 봄) `[인쇄]`

18650 LFP 3.2 V **1.3 Ah** 4개 (100.08/96.01/85.96/79.72 %), **C/10**, 10–55 °C. 온도 간
최대 편차 LAM_NE 1.61 %, LLI 1.10 %. 각형 셀의 C/25 결과를 SOH 로 선형 보간해 비교:
LLI 1.51 %, LAM_NE 1.53 %. Fig. 18 `[도표]`: LAM_NE 79.76 %: 10.5–12.0; 85.96 %:
5.3–6.8; LLI 79.76 %: 15.6–16.7; 85.96 %: 12.1–12.3.

`[해석]` 두 셀 형식이 같은 SOH 에서 같은 모드 비율을 가진다는 것은 검증 대상이지
가정으로 쓸 것이 아니다 (G13). 그리고 각형 셀의 참조값 자체가 OCV 적합값이다.

---

## 10. p.13–14 — §5 Conclusion `[인쇄]`

- "(1) … a particle fracture probability method is further proposed to achieve
  quantitative decoupling of different DMs. At the material level, LAM is quantified via
  coin half-cell capacity tests, while LLI is quantified using the intensity of
  lithium-carbon compound diffraction peaks".
- "(2) … LAMPE can be neglected under conventional aging conditions investigated in this
  study. The maximum deviations of LAMNE and LLI are 1.35% and 1.68%".
- "(3) … LAMNE is insensitive to the C-rate, while the maximum deviation of the corrected
  LLI is 1.68%."
- 한계 (저자): "(1) This study mainly focuses on the normal aging stage and has not been
  extended to the accelerated degradation stage after the capacity knee point. (2) Under
  harsh operating conditions … whether LAMPE remains negligible requires further
  exploration. (3) … validated using a limited number of battery samples."

`[해석]` 한계 (1) 은 [[rate-independent-li-plating-signature]] (Wang (Xiong) 2025) 와
정확히 이어진다 — 무릎 이후에는 음극 창이 리튬 창을 밑돌고 새 봉우리가 생겨 이
논문의 봉우리 A/B/C 회계가 깨진다. 두 논문이 같은 화학(LFP/graphite)의 **무릎 앞과
뒤**를 각각 다룬다.

---

## 11. 정의·산술 정리 (이 digest 의 계산)

### 11.1 좌표 대응 `[해석]`

| 이 논문 | 뜻 | 우리 창 좌표 |
|---|---|---|
| `X1 = C_APE` | 양극 가용 용량 (Ah) | `a_PE·Q_full` |
| `X2 = C_ANE` | 음극 가용 용량 (Ah) | `a_NE·Q_full` |
| `X3 = LAM_liNE − LAM_dePE + LLI` | 양극 창 오프셋 (Ah) | `b_PE`-계열 (양극 창 상단 − 음극 창 하단 의 여집합) |
| `X4` | 방전 종료 음극 리튬화도 | `b_NE` |
| `LLI = X3 − LAM_liNE + LAM_dePE` | 식 (4) 역 | Marongiu·Schmitt·Wang 과 동형 |

### 11.2 백분율 재현 `[재현]`

- `LAM_NE,OCV(79.4 %) = 2.83 / 25.5 ≈ 11.1 %` — Fig. 14 `LAM-OCV` ≈11, Table 4 No. 8
  10.40 % 와 정합 (`C_NE,OCV,fresh` 는 Fig. 3a 의 `[도표]` ≈25.5 Ah).
- `LLI_OCV(79.4 %) = 3.40 / Q_fresh` = Fig. 8 의 ≈17.2 % → **`Q_fresh ≈ 19.8 Ah`** (G9).
- 창: `Q_EOC = X1 − X3 ≈ 22.7 − 2.3 = 20.4 Ah` (fresh) — 정격 20 Ah × 99.1 % ≈ 19.8 과
  `[도표]` 오차 안.
- `X2/X1` (fresh) ≈ 25.5/22.7 ≈ **1.12** (가용 N/P).

### 11.3 li/de 분할이 구성인 것 `[재현]`

`x_crk,n = [min + max]/2 = [0 + Q_aging/X2]/2`; fresh 에서 `20/25.5/2 ≈ 0.39`, 79.4 % 에서
`(0.8·20)/22.8/2 ≈ 0.35`. 누적 `LAM_liNE/LAM_NE` ≈ 1.03/2.83 = 0.36 — 구간 중점의 가중
평균과 같다. **분할 비는 데이터가 아니라 식 (9) 가 정했다.**

### 11.4 원문 안의 불일치 목록

1. **결론 (3) "LAM_NE is insensitive to the C-rate" vs Fig. 15(a)**: `[도표]` 79.4 % 에서
   C/3 ≈18 % vs C/25 ≈11.7 % (≈6 pp), 86.8 % 에서 C/5 ≈10.4 vs 5.4. LLI 의 율 편차
   (최대 6.07 %) 와 같은 크기인데 LAM_NE 쪽은 정량하지 않았다.
2. **Fig. 9 vs Fig. 11 봉우리 전압** ≈40 mV 차이, 충/방전 미표기 (G14).
3. **18650 SOH** 본문 79.72 % vs Fig. 18 범례 79.76 %.
4. **기준 셀** — Fig. 3(b) 는 99.1 % 에서 0, Fig. 6·8 은 102.3 % 포함.
5. **"validates … the decoupling strategy based on particle fracture probability"
   (§3.3.2)** — XRD′ 는 LAM_NE 총량으로만 보정되므로 li/de 분할을 검증하지 못한다.
6. 식 (8) 을 RMSE 라 부르지만 인쇄된 것은 제곱합.

---

## 12. 어휘 전수 (이 계보 열여덟 편째)

본문(참고문헌 제외; 줄바꿈 하이픈 결합 후) 문자열 검색:
`identifiab*` **2** (① 문헌 소개 "Lin et al. … conducted an identifiability study",
② "ensuring the practical identifiability of model parameters" — C/25 연속 데이터의
장점 서술; **분석은 0회**) · `uniqu*` **1** ("To obtain unique parameter results, the
variables in Eq. (1) need to be recombined" — **비유일성의 인쇄**) · `observab*` **0** ·
`degenera*`/`redundan*`/`collinear*`/`confound*` **0** · `uncertaint*` **1** ("Battery
aging uncertainties and manufacturing process variations" — 추정 불확실성 아님) ·
`error bar` **0** · `sensitivit*` **0** (본문) · `Fisher`/`CRB`/`Hessian`/`singular`/
`condition number`/`nullspace` **각 0** · `global` **2** (에너지 구조; PSO 의 "global
search") · `local` **3** · `compensat*` **1** (온도 보상) · `offset each other` **1** ·
`ground-truth` **1** (서론, 남의 방법 비판) · `validat*` **11** · `deviation` **13** ·
`assum*` **3** · `correlat*` **6**.

`[해석]` 이 계보에서 **비유일성을 인쇄하고 그 대응(재조합)까지 한 편**은 Birkl(등식
소거)·Lin(재매개화)·이 논문(재조합 `X1–X3`) 셋이다. 이 논문은 거기에 **사전믿음으로
다시 늘리는** 단계를 붙였다 — 줄였다가 늘린다. 그리고 `validat*` 11회의 대상은 총량
둘뿐이다.

---

## 13. 비판 (이 digest 의 판단)

1. **"direct" 는 적합이 없다는 뜻이지 가정이 없다는 뜻이 아니다.** 식 (21)–(23) 은
   (i) 봉우리 A/B/C 가 순수 음극 stage 라는 LFP 가정, (ii) LAM_PE ≈ 0, (iii) Peak C 에서
   de/li 상쇄(1:1 구성), (iv) 무릎 이전, (v) SG 창 21 위에 서 있다. 이 다섯이 깨지는
   순간을 각각 시험하지 않았다.
2. **정답 축의 층위가 섞여 있다.** OCV 법 ← 재료 라벨(4+4 셀, 교차 셀 보정) ; IC 법 ←
   OCV 적합값 ; 18650 ← 각형 OCV 적합값의 SOH 보간. "1.79 % / 1.62 %" 를 인용할 때
   **무엇에 대한 편차인지** 반드시 붙여야 한다.
3. **`(X1, X3)` 축퇴를 재료 측정이 대신 풀어 줬는데 그것을 모른다** (§4.4). 방법의 성공
   조건(LAM_PE ≈ 0)이 방법의 결과로 서술된다. 가혹 조건에서 LAM_PE 가 생기면 같은 절차는
   그것을 LLI 로 읽고, IC 법의 Peak C 도 같은 방향으로 틀린다 (양극 손실도 최상단
   stage 를 잘라내므로).
4. **li/de 분할은 가정으로 닫혔고 검증되지 않았다** (§5, §11.3). Birkl 이 포기한 자리를
   가정 하나로 메우면서 "decoupling strategy validated" 라 적었다.
5. **오차 막대 0, 셀 1개/SOH, 기준 셀 두 개.** 편차 1.35–1.79 % 의 유의성을 판정할 잡음
   척도가 없다.
6. **C-rate 보정이 오프라인 교정**이고 (G11) LAM_NE 의 율 편차는 정량되지 않았다 (G12).
7. 좋은 점: (i) **LLI 에 재료 라벨(XRD)을 붙였다** — 이 계보에서 처음이며, 그 라벨의
   결점(탄소 정규화)을 스스로 찾아 보정했다. (ii) 부호 구조를 **단독 + 복합** 스윕으로
   같이 그려 상쇄를 드러냈다 — [[pvs-sev-degradation-mode-features]] 가 단독 스윕만 한
   것보다 낫다. (iii) 비유일성을 인쇄하고 4개로 줄였다. (iv) 결론 한계 (1)(2) 가
   정직하다.

---

## 14. 이 저장소가 가져갈 것 — 특히 `bms-balancing/` 새 모델 요구서용

> 전부 `[해석]`. 수치는 LFP/graphite 20 Ah 값이며 우리 셀에서 다시 잰다.

| 항목 | 내용 |
|---|---|
| **관측 O1** | C/25 방전 IC 의 봉우리 A/B/C 위치는 모드에 **불변**, 면적만 변한다 (Fig. 11). 위치가 움직이면 이 논문의 회계 밖(온도·율·도금·형상 변화)이다. |
| **관측 O2** | Peak C **절대 면적 감소(Ah) ≈ LLI(Ah)**; Peak B **상대 감소 ≈ LAM_NE** (식 21·23). |
| **관측 O3** | 사용 가능 리튬화 범위가 LLI·LAM_liNE 로만 좁아지고 LAM_deNE 로는 안 좁아진다 (Fig. 10). |
| **관측 O4** | LLI 로 읽은 값이 율에 따라 **단조 감소**(C/3 에서 −6 %); LAM_NE 는 흔들린다 (±6 pp). |
| **후보 원인 (잔차·모드 값이 이상할 때)** | (a) LAM_PE ≠ 0 (LLI 로 오귀속 — 양극 평탄역 축퇴) · (b) 무릎 이후 도금 (새 봉우리, [[rate-independent-li-plating-signature]]) · (c) 율/온도 (봉우리 병합·이동) · (d) li/de 비의 구성 오류 (Peak C 오염, §8.4). |
| **구분 시험 T1 (양극 독립 검사)** | 코인셀 PE 용량 또는 XRD 양극 피크 — **OCV 로는 원리적으로 못 가른다** (§4.4). 오프라인 1회라도 있어야 LLI 라벨이 선다. |
| **구분 시험 T2 (봉우리 개수·위치 불변 검사)** | A/B/C 개수와 전압이 RPT 간 고정인가. 고정 아니면 (b)(c). |
| **구분 시험 T3 (면적 항등식 검사)** | `ΔArea_C(Ah)` 와 OCV 적합의 `ΔLLI(Ah)` 가 1:1 인가. 어긋나면 (a) 또는 (d). |
| **구분 시험 T4 (율 계열)** | C/25·C/10·C/5 에서 LLI 추정이 단조인가, 계수가 1/1.19/1.26 근처인가. 셀 종류가 바뀌면 계수를 다시 잰다. |
| **채택 기준** | LFP 셀에 한해, T1 이 LAM_PE ≈ 0 을 주고 T2·T3 가 통과하면 IC 직접 진단을 **라벨 생성기**로 채택할 수 있다 — 단 li/de 분할은 채택하지 않는다 (가정). |
| **한계 (이식 조건)** | NMC 계열: 양극이 평탄하지 않아 (i) `(X1, X3)` 축퇴가 사라지는 대신 (ii) full-cell dQ/dV 봉우리가 양극·음극 합성이라 **면적 = 음극 stage 용량** 항등식이 깨진다 → O2 를 그대로 옮길 수 없다. Si/Gr: stage 봉우리 자체가 흐려지고 형상 변화([[halfcell-ocp-shape-invariance]])가 위치를 움직여 O1 이 깨진다. 무릎 이후: (b). |

**우리 프레임이 이 논문에 공급할 수 있는 것 (미실행, 값싸다)**:
1. LFP 합성 truth 에서 `(X1, X3)` 방향의 `JᵀJ` 고유값 — §4.4 의 "거의 못 가른다" 를
   수치(조건수)로. 평탄역 기울기 몇 mV 가 주는 정보량이 곧 답이다.
2. 같은 합성에서 LAM_PE 를 0 → 10 % 로 넣고 (i) OCV 적합의 LLI 오귀속량, (ii) Peak C
   면적법의 LLI 오귀속량을 함께 그린다 — 두 방법이 **같은 방향으로** 틀리는지.
3. de:li 를 1:1 / 1.75:1 / 3:1 로 바꾸며 Peak C 면적법의 LLI 편향 — §8.4 의 +0.6 Ah
   추정을 확인.

**위키 컴파일 층에 붙는 것**: 새 개념 [[ic-peak-area-direct-mode-readout-lfp]];
[[halfcell-window-parametrization-lineage]] 에 Cui 2026 행 (4, 재조합으로 7 → 4, 그
뒤 사전믿음 등식으로 다시 7) + "등식의 새 변종" 절; [[mode-identifiability-unmeasured-lineage]]
표에 행 추가 + 다섯 번째 인쇄; [[22p-physics-or-degeneracy]] Evidence For 1건 (LFP
`(X1, X3)` 축퇴를 재료 측정이 풀었고 적합의 `X1` 상수는 tie-break 의 징후) + Status
Log; [[pvs-sev-lli-lampe-separability]] Evidence Against 1건 (LFP 에서 LLI ↔ LAM_liPE
가 IC/OCV 어느 관측에서도 같은 자리에 들어간다 — 논문 식 (1)·(20) 에서 유도) + Gap
(IC 법의 정답 축이 fitted) + Status Log.

---

## 15. 그림 판독 기록 (무엇을 보고 무엇을 안 봤는가)

| 그림 | 봤는가 | 기록한 것 |
|---|---|---|
| Fig. 1 | 아니오 | 시험대 사진 |
| Fig. 2 | 아니오 | 좌표계 도식 — 식 (1)–(5) 텍스트로 충분 |
| Fig. 3 | **예** | §4.3 — `X1` 여덟 점 동일 높이, `X2`·`X3` 궤적, 모드 Ah |
| Fig. 4 | **예** | §6.1 — PE 코인셀 평탄, NE 코인셀 직선 감소 |
| Fig. 5 | 아니오 | XRD 패턴 — 정량은 Fig. 6 으로 |
| Fig. 6 (+ Fig. 7) | **예** (한 크롭) | §6.2, §7.1 — `LLI_XRD` 24.97 %, 코인셀 vs ANE |
| Fig. 8 | **예** | §7.2 — `LLI_OCV` vs `LLI′_XRD` 다섯 점 |
| Fig. 9 | **예** | §8.1 — 봉우리 A/B/C 전압·높이 |
| Fig. 10 | **예** | §8.2 — 정의역 축소 방향 |
| Fig. 11 | **예** | §8.3 — 부호 구조 (높이) |
| Fig. 12 | **예** | §8.3 — 면적: Peak B 는 LLI 불변, Peak C 는 LLI 지배 |
| Fig. 13 | 아니오 | 세기·면적 통계 — Fig. 12 와 중복 |
| Fig. 14 | **예** | §8.5 — (a)(b) 과대 → (c) 보정 후 일치 |
| Fig. 15 | **예** | §9.1 — LAM_NE 율 편차 ≈6 pp (본문과 어긋남), LLI 단조 |
| Fig. 16 | 아니오 | 순서도 — §4.3.2 텍스트로 |
| Fig. 17 | **예** | §9.3 — 온도 편차 |
| Fig. 18 | **예** | §9.4 — 18650 편차 |
| Table 1–6 | 텍스트 | 전부 옮김 |

**본문 서술과 그림이 어긋난 것**: §11.4 의 1 (LAM_NE 율 무관 주장 vs Fig. 15a), 2 (Fig. 9
vs Fig. 11 봉우리 전압), 3 (18650 SOH 표기).
