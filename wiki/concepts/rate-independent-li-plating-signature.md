---
title: 무율(rate-independent) 리튬 도금 — LAM_NE 유도 도금의 OCV 서명과 모드 회계
description: "음극 활물질이 리튬 재고를 밑돌 때(Q_NE < Q_Li) 0.05 C 에서도 생기는 도금이 full-cell OCV·DV 에 남기는 서명, 그것이 LLI/LAM 어느 칸에도 안 들어간다는 회계, 그리고 아핀 창 매개화가 깨지는 방식 (Wang (Xiong) 2025, LFP/graphite)"
created: 2026-09-11
updated: 2026-09-11
type: concept
tags: [battery, degradation, research]
sources: [raw/papers/wang2025_aging-induced-rate-independent-li-plating.md, raw/papers/dubarry2012_synthesize-degradation-modes.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: mixed
evidenceScope: single-source
---

# 무율(rate-independent) 리튬 도금 — LAM_NE 유도 도금의 OCV 서명과 모드 회계

## 정의

리튬 도금을 원인으로 둘로 가른다 (Wang (Xiong) 2025 §1.1 의 어휘):

| | rate-dependent | **rate-independent** (이 페이지) |
|---|---|---|
| 원인 | 수송·반응 과전위가 국소 음극 전위를 0 V vs Li/Li⁺ 아래로 민다 (저온·급속 충전) | **`Q_NE < Q_Li`** — 음극 활물질 손실로 음극이 리튬 재고를 다 받지 못해 남는 Li 가 표면에 석출 |
| 율 의존 | 있다 — 전류를 낮추면 사라진다 | **없다** — `[인쇄]` "can occur even at very low charging rates"; 0.05 C 의사-OCV 에서 관측 |
| 열화 모드와의 관계 | 독립 부반응 | **`LAM_NE` 의 결과** (그리고 비가역분은 `LLI` 의 원인) |
| 설계 시 방지 | — | N/P > 1 로 막지만, 노화로 음극이 줄면 다시 생긴다 |

이 구분은 [[dubarry-mechanistic-mode-synthesis]] 가 이론으로 갖고 있던 특수 경우
(`LAM_NE` 가 `LLI` 를 앞질러 음극 창이 리튬 창보다 짧아지는 것)를 실셀에서 부른
이름이다. Wang (Xiong) 2025 는 1.1 Ah LFP/graphite 17 셀 중 **10 셀(58.8 %)** 에서
이것을 봤다.

## 관측 서명 (full-cell, 0.05 C 의사-OCV)

원전 raw digest `raw/papers/wang2025_aging-induced-rate-independent-li-plating.md`
§5.3·§6.2 에서 옮김. 전압 수치는 LFP 값이다.

| # | 서명 | 어디에 | 수치 (LFP/graphite) |
|---|---|---|---|
| S1 | 충전 **말단**에 새 전압 평탄역 | 고 SOC | `[도표]` ≈3.46 V; 시작 전압이 노화에 따라 ≈3.468 → ≈3.461 V 로 내려간 뒤 멈춤 |
| S2 | 방전 **시작**에 짝 평탄역 (박리) | 저 DOD (< ≈0.1) | `[도표]` ≈3.40 V, ≈0.05–0.07 Ah |
| S3 | dV/dQ 에 **원래 없던** 봉우리/골 | 충전 고 SOC / 방전 저 DOD | `[도표]` 충전 SOC ≈0.865 높이 ≈1.25 (dV/dSOC); 방전 DOD ≈0.065 깊이 ≈−1.65 |
| S4 | 평탄역 **전압은 고정**, 길이만 변함 — 늘고 → 멈추고 → 줄어든다 (자기 제한) | RPT 간 | 17 셀 중 10 셀에서 같은 진화 |
| S5 | 평탄역 시작에서 **≈2 mV 하강 후 회복** (동역학) | 충전 | `[인쇄]` "around 2 mV"; 저자 해석: 도금이 전하전달 저항의 병렬 가지 |
| S6 | 음극 반쪽전지에서 도금 구간의 전위 | half-cell | `[도표]` ≈−0.02 V 핵생성 골 → ≈−0.015 V 평탄역; 박리 ≈+0.01~0.02 V |
| S7 | 기존 음극 봉우리의 **SOC 이동**이 S3 과 **같은 곡선에 공존** | 충전 dV/dQ | `[도표]` 중간 봉우리 0.67 → 0.52 SOC — 이것은 도금이 아니라 `LAM_NE` 의 서명 |

정량: `[인쇄]` 식 (7) `Q_li-plating = ΔSOC × Q_age` (DV 새 봉우리의 SOC 폭 × 그 시점
용량). 최댓값 31.5–118.5 mAh (공칭의 2.9–10.8 %). 충전측 > 방전측이며 그 차이가
비가역분이다. **불확실성 표기는 없다.**

## 모드 회계 — 도금은 LLI 인가 LAM 인가

`[해석]` 원전 정의(식 3, 6, 7)를 따라 재구성하면 답은 "**둘 다 아니다**":

| 도금의 부분 | 회계 칸 | 관측 |
|---|---|---|
| 원인 | `LAM_NE` | S7 (기존 봉우리 이동) |
| 가역 도금 (박리되는 분) | **모드 3개 밖** — 용량에는 들어가고 (`Cap > Q_NE`) `Q_NE` 에는 안 들어간다 | S1–S4 |
| 비가역 도금 (dead Li) | `LLI` (`Q_Li` 감소) — 원전은 이 수지를 계산하지 않는다 | 충전측 − 방전측 도금량 |
| 4-창 아핀 모델에 강제로 넣으면 | 어깨를 못 맞추고 **충전 말단 국소 잔차**로 남거나 `a_NE` 가 흡수 — 어느 쪽인지 원전에 없음 | Fig. 4(b) |

Fig. 12 `[도표]` 가 이 회계의 그림이다: S1(리튬 제한) 에서 `Cap ≈ Q_Li`, `Q_NE` 가
`Q_Li` 를 가로지른 뒤 `Cap ≈ Q_NE` (약간 위 = 가역 도금분), `Q_Li − Cap` 이 벌어진다.
**`Q_Li` 궤적에는 변곡이 없고 변곡은 `Q_NE`·`Cap` 에 있다.**

## 왜 중요한가

1. **아핀 창 매개화가 깨진다.** [[halfcell-ocp-shape-invariance]] 가 Si/graphite
   blend 에서 본 파괴를 LFP/graphite 에서 **도금 때문에** 본다 (Fig. 4b: 아핀
   시뮬레이션이 어깨를 못 만든다). 원전의 처방은 음극 곡선을 DV 극값 4개로 5 구간으로
   잘라 **구간마다 가로 스케일**을 두는 것 — 자유도 **4 → 8**, GA 적합, 검증 RMSE
   < 10 mV, 유일성 논의 0 ([[halfcell-window-parametrization-lineage]] 의 여섯째 축).
2. **식별 가능성의 국면 전환이 궤적에 보인다.** Fig. 11 `[도표]` 에서 음극의 0 V
   교차점이 SOH 100 → 57.1 % 에 걸쳐 full-cell SOC **1.08 → 0.88** 로, 즉 창 **밖에서
   안으로** 들어온다. 창 밖에 있는 동안 `K_NE` 는 곡선 내부 상전이 간격으로만 정해지고
   (약함), 안에 들어오면 어깨 위치가 고정한다 (강함). Fig. 12 의 `Q_NE` 가 그 경계에서
   `[도표]` 100–300 사이클에 ≈0.1 Ah 계단으로 떨어지는 것은 물리(도금이 LAM_NE 를
   가속)와 **이 국면 전환** 두 독해가 가능하고 원전은 후자를 검토하지 않았다.
   [[data-window-identifiability]] 의 "창 위치가 어느 전극을 보이게 하는지 고른다" 와
   같은 기제 — 여기서는 관측 창이 아니라 **전극 창이 움직여** 들어온다.
3. **LFP 양극이 만드는 구조적 비식별.** 양극 OCP 가 평탄하면 양극 창 상단은 3.6 V
   컷오프에 고정되고 하단은 관측 창 밖이다 → `Q_Li = (1 − S_NE)·Q_Full` 로 `Q_Li` 는
   식별되지만 **`Q_PE` 는 안 된다.** 원전이 `Q_PE` 를 어디에도 인쇄하지 않는 것과
   정합한다. 이 축퇴는 NMC 계열로 옮기면 사라진다 (양극 곡률로 식별).

## 이 위키에서의 적용 — `bms-balancing/` 새 모델 요구서 항목 후보

`[해석]` 전부 후보이며, 수치 문턱은 우리 셀에서 다시 잰다.

- **관측**: 아핀 적합 뒤 충전 말단 국소 잔차 어깨(S1) + 같은 RPT 방전 시작의 짝(S2)
  + dV/dQ 봉우리 **개수 증가**(S3).
- **후보 원인**: (a) 무율 도금 · (b) 음극 OCP 형상 변화(blend) · (c) 양극 상단 창
  절단/저항 ([[reference-electrode-halfcell-dma]]) · (d) 축퇴 — 골짜기의 다른 점
  ([[fitting-degeneracy]]).
- **구분 시험**: T1 짝 검사 (S2 가 있는가 — (a) 만 짝을 만든다) · T2 새 특징 vs 이동
  (봉우리 개수가 늘었는가 — (b)(c)(d) 는 위치/높이만 바꾼다) · T3 전압 고정성 (RPT 간
  수 mV — 저항형 (c) 는 움직인다) · T4 모드 정합 (아핀 적합의 `Q_NE` 가 `Q_Li` 를
  가로질렀거나 직전인가; 아니라면서 S1–S3 이 있으면 적합이 틀린 것) · T5 율 무관성
  (0.05 C 에서도 남는가).
- **채택 기준**: T1 ∧ T2 ∧ T3 ∧ T4. 채택 시 4-창 좌표에 **도금 구간 폭 1개**만
  더하고 8-파라미터 구간 스케일링은 채택하지 않는다 (유일성 근거 없음). 도금량은 식
  (7) 로 **별도 관측량**으로 두고 모드 3개에 섞지 않는다.
- **한계**: LFP 수치. NMC 계열은 양극 기울기 때문에 어깨가 기울어진 단이 되어 T3 이
  약해진다. Si/Gr 은 (a)(b) 가 동시에 있을 수 있어 T2 만으로 못 가른다. 방전측 골
  검출기는 도금 없는 셀에서도 ≈0.014–0.022 Ah 를 낸다 (`[도표]` Fig. 10) — 문턱을
  먼저 잰다.
- **봉우리를 순서로 세는 feature 에 대한 경고**: [[pvs-sev-degradation-mode-features]]
  의 PVS 처럼 "두 번째 봉우리/골" 로 정의된 양은 S3(새 봉우리 출현)에 취약하다 —
  개수 변화 검출을 앞에 둔다.

## 반대 해석 / 데이터 공백

- 원전은 모드의 ground truth 가 없고(분해·SEM 은 도금 유무의 정성 근거), 오차 막대
  0, GA 설정 미인쇄, RPT 주기 미인쇄, SOH 기준 미인쇄, 아핀 4-파라미터 적합의 RMSE
  미인쇄 (digest G1–G13).
- "도금은 LLI·LAM 어느 칸도 아니다" 는 **이 위키의 재구성**이지 원전의 문장이 아니다.
  원전은 회계를 명시하지 않는다.
- 국면 전환 독해(왜 중요한가 2)는 원전 데이터로는 검증할 수 없다 — 우리 합성
  프레임에서 `a_NE` 를 창 밖 → 안으로 움직이며 오차막대의 불연속을 보는 실험이
  필요하다 (미실행).
- 순수 graphite 에서 아핀 불변이 버틴다는 근거(Fig. 2d: SOH 100/70/58 % 겹침)는
  세로 해상도 0–0.5 V 그림 하나뿐이다.

## 관련
- [[halfcell-ocp-shape-invariance]] — 같은 종류의 파괴, 다른 원인 (blend)
- [[halfcell-window-parametrization-lineage]] — 여섯째 축 (구간별 스케일링, +4)
- [[data-window-identifiability]] — 창 위치와 전극 가시성
- [[fitting-degeneracy]] · [[22p-physics-or-degeneracy]]
- [[dubarry-mechanistic-mode-synthesis]] — 이 특수 경우의 이론 원전
- [[pvs-sev-lli-lampe-separability]] — 순서 기반 feature 의 취약성, 2 mV 동역학 하강
