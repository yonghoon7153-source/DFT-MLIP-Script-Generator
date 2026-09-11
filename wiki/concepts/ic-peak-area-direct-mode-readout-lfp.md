---
title: IC 봉우리 면적으로 읽는 직접 모드 진단 (LFP/graphite) — Peak C 면적 = LLI, Peak B 면적 = LAM_NE
description: "적합 없이 C/25 IC 곡선의 봉우리 면적으로 LLI(Ah)·LAM_NE(%)를 읽는 Cui 2026 의 직접 진단: 왜 LFP 에서만 항등식이 성립하는가, 부호 구조, 검증의 층위(재료 라벨 vs 적합 라벨), 평탄 양극이 만드는 (X1, X3) 축퇴와 사전믿음으로 닫은 li/de 분할, 그리고 NMC·Si/Gr 로의 이식 조건"
created: 2026-09-11
updated: 2026-09-11
type: concept
tags: [battery, degradation, research]
sources: [raw/papers/cui2026_direct-diagnosis-lfp-degradation-modes.md, raw/papers/birkl2017_degradation-diagnostics-ocv.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: mixed
evidenceScope: single-source
---

# IC 봉우리 면적으로 읽는 직접 모드 진단 (LFP/graphite)

## 정의

Cui et al. 2026 (Applied Energy 426, 128689; raw digest
`raw/papers/cui2026_direct-diagnosis-lfp-degradation-modes.md`) 의 "direct diagnosis":
C/25 방전 의사-OCV 의 IC(dQ/dV) 곡선에서 세 봉우리 **A·B·C**(왼쪽부터; `[도표]` ≈3.24 /
≈3.29–3.33 / ≈3.33–3.37 V — 그림마다 ≈40 mV 차이, 충/방전 미표기)를 잡고, **적합 없이**

```
LAM_NE = (Area_B,fresh − Area_B,aging) / Area_B,fresh          (원문 식 21)
LLI′   = (Area_C,fresh − Area_C,aging) / Q_fresh               (원문 식 23)
```

로 읽는다. 원문 결과: OCV 적합값 대비 최대 편차 **LLI 1.79 %, LAM_NE 1.62 %** (`[인쇄]`);
율 보정(계수 1 / 1.19 / 1.26 / 1.47 for C/25 / C/10 / C/5 / C/3) 후 LLI 최대 편차 1.68 %;
온도 0–55 °C 에서 LAM_NE 1.59 %, LLI 0.60 %; 18650 1.3 Ah 에서 1.61 % / 1.10 %.

## 왜 되는가 — LFP 에서만 성립하는 항등식 `[해석]`

- LFP 양극 OCP 가 평탄하므로 full-cell dQ/dV 의 봉우리는 **음극 stage 용량 그대로**다.
- Peak C(최고 전압) = 음극 **최상단 stage**. LLI 는 음극 창을 양극 창에 대해 밀어 그
  최상단 stage 를 컷오프가 잘라내므로 **Peak C 면적 감소(Ah) = LLI(Ah)**. 원문이 식 (21)
  의 상대 감소(Fig. 14a, 42 % 로 과대)에서 식 (23) 의 **절대 감소 / 셀 용량**으로 "보정"
  한 것이 바로 이 항등식이다.
- Peak B = 중간 stage 용량 ∝ 음극 활물질 → 상대 감소 = LAM_NE.
- 원문의 근거는 실셀이 아니라 OCV 적합값을 참조로 만든 **가상 배터리**(LLI 0–3.5 Ah,
  `LAM_deNE = LAM_liNE` 0–1.75 Ah) 의 단독·복합 스윕이다.

## 부호 구조 (Fig. 11·12, `[도표]`; 봉우리 **위치**는 전 스윕 불변)

| 관측 | LLI | LAM_deNE | LAM_liNE | LAM_PE |
|---|---|---|---|---|
| Peak B 면적/높이 | **0** | − (작음) | − (작음) | 스윕 없음 (가정상 0) |
| Peak C 면적/높이 | **−−** (Ah 로 1:1) | **+** | − | 스윕 없음 |
| 사용 가능 리튬화 범위 (Fig. 10) | − | 0 | − | — |

원문: "the effects of LAM_deNE and LAM_liNE on the high-voltage characteristic peak can
offset each other" — **단, 이 상쇄는 de:li = 1:1 구성의 산물**이다. 같은 논문의 진단
결과(Fig. 3b)는 de:li ≈ 1.75:1 이고, 그 비로는 Peak C 에 순 +효과가 남아 LLI 를 ≈0.6 Ah
(≈3 %p) 과소 읽을 수 있다 (digest §8.4, 편차 1.79 % 안에 묻히는 크기).

## 검증의 층위 — 무엇이 measured 이고 무엇이 fitted 인가

| 대상 | 정답 축 | 셀 수 | 결과 |
|---|---|---|---|
| OCV 적합 LAM_NE | **코인 반쪽전지 용량** (만방 분해 No. 5–8) | 4 | 최대 편차 1.35 % — 세 노화점 모두 OCV 쪽이 낮은 **계통 편차** |
| OCV 적합 LLI | **XRD LiC₆/LiC₁₂ 세기비** (만충 분해 No. 1–4), LAM_NE 보정은 **다른 셀(No. 5–8)의 코인셀을 선형 보간** | 4 | 최대 편차 1.68 %; 보정량 최대 ≈8 pp |
| IC 직접 진단 LLI·LAM_NE | **OCV 적합값** | 8 | 1.79 % / 1.62 % |
| 18650 | 각형 셀 OCV 적합값의 SOH 보간 | 4 | 1.51 % / 1.53 % |

이 계보에서 **LLI 에 재료 라벨을 붙인 첫 편**이다 — 그러나 오차 막대 0, SOH 당 1 셀,
기준 셀 둘(99.1 / 102.3 %), 노화 프로토콜 미인쇄. "1.79 %" 를 인용할 때는 반드시
"OCV 적합값 대비" 를 붙인다.

## 평탄 양극이 만드는 (X1, X3) 축퇴 — 재료 측정이 대신 풀었다 `[해석]`

OCV 모델(식 5) `OCV = U_p(1 − (x_ANE·X2 + X3)/X1) − U_n(x_ANE)` 에서 양극은 방전
종료에 `x_APE ≈ 0.90` (평탄역 위), 충전 종료에 `x_APE → 0` (양극 제한) → 관측이 구속하는
것은 **`X1 − X3 = Q_EOC` 하나**다. `X1`(양극 가용 용량)과 `X3`(⊃ LLI)를 함께 움직이면
평탄역의 어느 구간이 창에 들어오는지만 바뀌고 그 전압 차는 수 mV. 즉 **LFP OCV 적합은
LAM_PE 와 LLI 를 거의 못 가른다** (`Q_EOC = C_PE − LAM_liPE − LAM_liNE − LLI`, 원문
식 1·20 에서 유도). Fig. 3(a) 의 `X1` 이 8개 SOH 에서 **정확히 같은 높이**인 것은
데이터가 아니라 PSO 의 경계/초기값이 정한 징후다 (탐색 범위·초기값 미인쇄).

이 논문에서 그것이 해를 끼치지 않은 이유: **코인셀 PE 용량(평탄)과 XRD FePO₄ 피크
(불변)가 LAM_PE ≈ 0 을 독립으로 확인**해 줬다. 방법의 성공 조건이 방법의 결과처럼
서술돼 있다. LAM_PE 가 실제로 있는 셀(가혹 조건; 저자도 결론 한계 (2) 에서 유보)에서는
OCV 적합도 Peak C 면적법도 **같은 방향으로**(LAM_PE → LLI) 틀린다.

## li/de 분할 — 사전믿음 등식으로 닫았다

원문 식 (9): 입자 파괴 확률이 리튬화 상태와 무관 → 격리된 부분의 리튬화도 = 순환
구간 중점 `x_crk = [min(x) + max(x)]/2`. 그 결과 `LAM_liNE/LAM_NE ≈ 0.36` 은 측정이
아니라 구성이다 (`[재현]` 순환 구간 `[0, 0.78]` 의 중점 0.39). [[birkl-ocv-degradation-diagnostic]]
이 "동시 LLI 가 있으면 li/de 는 유일하게 식별되지 않는다" 고 인쇄하고 포기한 분할을
**가정 하나로** 되살린 것이며, XRD′ 검증은 LAM_NE 총량으로만 보정되므로 이 분할을
검증하지 못한다. [[halfcell-window-parametrization-lineage]] 의 "여분을 죽이는 방법"
에서 **등식의 새 변종(사전믿음 등식)**.

## 이식 조건 (요구서용 한계)

- **NMC 계열**: 양극이 평탄하지 않다 → (i) `(X1, X3)` 축퇴는 사라지지만 (ii) full-cell
  dQ/dV 봉우리가 양극·음극 특징의 합성이라 "면적 = 음극 stage 용량" 항등식이 깨진다.
  Peak C 면적법을 그대로 옮길 수 없다.
- **Si/Gr 음극**: stage 봉우리가 흐려지고 형상 변화([[halfcell-ocp-shape-invariance]])가
  위치를 움직인다 → "위치 불변" 전제가 깨진다.
- **무릎 이후**: 음극 창이 리튬 창을 밑돌면 새 봉우리(도금)가 생긴다 —
  [[rate-independent-li-plating-signature]] (Wang (Xiong) 2025) 가 같은 화학의 무릎
  **뒤**를 다룬다. 원문 스스로 한계 (1) 로 인정.
- **율·온도**: C/3 이상에서 봉우리 병합; LLI 는 율에 단조 감소(−6 % at C/3); LAM_NE 는
  `[도표]` 최대 ≈6 pp 흔들리는데 원문은 "insensitive" 라 적었다 (본문–그림 어긋남).

## 이 위키에서의 적용 — `bms-balancing/` 새 모델 요구서 항목 후보 `[해석]`

- **관측**: 봉우리 A/B/C 의 개수·위치 불변 + Peak C 절대 면적 감소(Ah) + Peak B 상대
  감소.
- **구분 시험**: T1 양극 독립 검사 (코인셀 PE 용량 또는 XRD — **OCV 로는 원리적으로 못
  가른다**) · T2 개수·위치 불변 검사 · T3 면적 항등식 검사 (`ΔArea_C(Ah)` vs 적합의
  `ΔLLI(Ah)` 1:1) · T4 율 계열 단조성.
- **채택 기준**: LFP 셀에 한해 T1 이 LAM_PE ≈ 0 을 주고 T2·T3 통과 → IC 직접 진단을
  **라벨 생성기**로 채택 가능. li/de 분할은 채택하지 않는다.
- **우리가 공급할 수 있는 것 (미실행)**: LFP 합성 truth 에서 `(X1, X3)` 방향의 `JᵀJ`
  조건수; LAM_PE 0 → 10 % 에서 OCV 적합과 Peak C 면적법의 LLI 오귀속량 동시 계산; de:li
  비를 바꾼 Peak C 편향 ([[fitting-degeneracy]], [[nullspace-coefficient-interpretation]]).

## 반대 해석 / 데이터 공백

- 위 "(X1, X3) 축퇴" 는 원문의 식과 그림에서 이 위키가 유도한 것이며 원문은 언급하지
  않는다. 평탄역 기울기가 주는 정보량(감도)은 재지 않았다 — 0 이 아니라 "작다" 다.
- "면적 = stage 용량" 항등식은 SG 평활(1차, 창 21)과 봉우리 경계 정의에 걸린다; 원문은
  경계 정의를 인쇄하지 않았다.
- 원문의 강점도 적는다: 단독 + 복합 스윕을 같이 그려 상쇄를 드러냈고, 비유일성을
  인쇄한 뒤 4개로 줄였으며, 한계(무릎·가혹 조건·표본 수)를 명시했다.

## 관련
- [[rate-independent-li-plating-signature]] — 같은 화학의 무릎 **뒤**
- [[halfcell-window-parametrization-lineage]] — 등식의 새 변종 (사전믿음 등식)
- [[birkl-ocv-degradation-diagnostic]] — li/de 비식별의 원전
- [[np-lip-ocv-reparametrization]] — 원문이 인용하는 유일한 식별 가능성 연구
- [[pvs-sev-degradation-mode-features]] — 우리 쪽 ICA 유래 feature 와 부호표 대조
- [[22p-physics-or-degeneracy]] · [[pvs-sev-lli-lampe-separability]]
