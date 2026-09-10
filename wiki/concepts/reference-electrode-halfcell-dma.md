---
title: 기준전극 기반 half-cell 분해 DMA
description: "In-situ reference electrode DMA: LAM from DVA feature spacing, LLI from lateral offset — no optimizer, and what it costs"
created: 2026-09-10
updated: 2026-09-10
type: concept
tags: [battery, degradation, research]
sources: [raw/papers/natterer2026_re-halfcell-anode-potential-aging.md, raw/papers/birkl2017_degradation-diagnostics-ocv.md, raw/papers/marongiu2016_lfp-onboard-capacity-halfcell.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: definition
evidenceScope: multi-source-primary
---

# 기준전극 기반 half-cell 분해 DMA

## 정의

셀 안에 **기준전극(RE)** 을 심어 두 전극의 전위를 따로 기록하고, 그 half-cell
곡선의 **DVA 특징점 위치만으로** 열화 모드를 산술로 계산하는 DMA 절차.
정본 사례는 Natterer et al. 2026 (`raw/papers/natterer2026_re-halfcell-anode-potential-aging.md`,
LTO-RE 를 넣은 NMC-811‖Gr 단층 파우치 1000 사이클).

**세 식이 전부다** (원문 식 1–4):

```
Q_LAM,neg = Q_II − Q_III                        (1)   # 한 전극 안 두 feature 사이 거리
LAM_neg   = 1 − Q_LAM,neg / Q_LAM,neg,init      (2)   # 초기 RPT 기준 상대량
ξ_OCP     = ξ_OCP,init · (1 − LAM) · Q_cycle/Q_ref   (3)   # pristine OCP 를 LAM·SoH_C 로 스케일
Δξ_LLI    = ξ_OCP^feature − ξ_meas^feature      (4)   # 스케일된 곡선 대비 가로 이동량
```

LAM_pos 는 (1)–(2) 를 양극 feature 쌍(NMC C1↔C3)에 그대로 적용한다. LLI 는 두
전극 창의 겹침(LI) 변화로 마무리된다.

**핵심 성질**: 한 전극 **안의** 두 feature 사이 거리는 LLI 가 바꾸지 못한다
(LLI 는 두 전극의 **상대 오프셋**만 움직인다). 따라서 `LAM_neg`·`LAM_pos` 는
서로, 그리고 LLI 와 **구조적으로 분리되어** 측정된다.

## 왜 중요한가

이 위키의 모든 DMA 계보([[birkl-ocv-degradation-diagnostic]],
[[dubarry-mechanistic-mode-synthesis]], [[halfcell-window-parametrization-lineage]])는
**같은 4개 창 좌표**를 쓴다. 차이는 그 좌표를 **무엇으로 못 박는가** 뿐이다:

| 방법 | 여분(null)을 죽이는 수단 | 최적화 |
|---|---|---|
| Dubarry 2012 | 매개변수를 애초에 2개만 만든다 | 정방향 합성 |
| Birkl 2017 | 컷오프 전압 **등식 제약** 2개 | `fmincon` + MultiStart |
| Lin & Khoo 2024 | 좌표 자체를 2 자유도로 재매개화 | — (구조 정리) |
| **이 방법** | **관측 채널을 늘린다** (full-cell 1 → half-cell 2) | **없음 (산술)** |

마지막 줄이 이 개념의 전부다. **최적화가 없으면 [[fitting-degeneracy]] 가 말하는
"평평한 골짜기에서 추정기가 미끄러진다" 는 통로 자체가 사라진다.** 축퇴는
목적함수의 성질인데, 목적함수가 없기 때문이다.

그 대신 **다른 종류의 오차로 갈아탄다** — 아래 "대가" 참조. 축퇴가 사라지는 것이
아니라 **불확실성이 최적화 지형에서 특징점 판독으로 이동**한다.

## 대가 (이 절차가 참이려면 참이어야 하는 것)

1. **feature 화학량론 불변** — DVA 극값이 대응하는 전극 화학량론이 수명 내내
   고정. Birkl 의 가정과 동일하며, 이 절차는 그것을 **더 강하게** 쓴다(위치를
   직접 값으로 읽으므로).
2. **저전류 곡선 ≈ OCP** — Natterer 는 RPT 를 **0.2 C** 로 돌린다(보통의 C/20 보다
   훨씬 빠르다). 원문 Fig. 1a 에서 GITT OCP 와 0.2 C 곡선의 차이가 `[도표]`
   10–25 mV 이고 OCP 에 있는 ≈60 mAh 계단이 측정 곡선에는 없다.
3. **pristine OCP 재사용** — 노화된 전극의 OCP 를 다시 재지 않는다. Ni-rich
   양극의 OCP 형상 변화(Rodrigues 의 blending 문제)를 "이 경우엔 불필요" 로
   판정하는데, 그 판정 근거인 Fig. A.1 의 **DVA 재구성은 양극·full-cell 에서
   실제로 어긋난다** (raw digest §9). 이 가정이 무엇이고 어디서 깨지는지는
   [[halfcell-ocp-shape-invariance]] 가 따로 다룬다 — 그 페이지의 Si/Gr blend
   사례와 달리 Natterer 의 셀에는 **Si 가 없고**(순수 graphite), 형상이 흔들리는
   쪽은 **양극(NMC-811)** 이다.
4. **peak 판독 절차** — 평활·미분·창 정의가 원문에 인쇄되지 않았다.
   [[mode-observability]] Phase 1 이 실측한 "valley 정의 하나로 feature 값이
   −20.0 vs −11.3 으로 갈린다" 와 같은 자유도다.
5. **기준전극 위치** — 같은 셀에서 스택 **밖** LTO-RE 와 스택 **안** 금선 RE 가
   `[도표, 원문 Fig. 4]` 0.75 C 에서 **20 mV 이상** 다른 음극 전위를 준다
   (LTO ≈ +18 mV vs GWRE ≈ −5 mV). 저자는 이를 상수 옴 항 `R_GWRE→LTO-RE = 0.35 Ω`
   로 흡수한다.
   → **단, 모드 계산(식 1–4)은 전위의 세로 절대값을 쓰지 않고 특징점의 가로
   위치만 쓴다.** 그래서 이 오차는 **전위 결론**을 위협하지 가로축 기반
   **모드 결론**을 직접 위협하지는 않는다. 두 결론의 신뢰도를 분리해서 다뤄야 한다.
6. **셀 1개** — 원문은 4셀로 시작해 3셀을 잃었다. 셀 간 재현성이 0.

## 이 위키에서의 적용

- **α·β 검증의 독립 근거 "형태"**: [[degradation-degeneracy]] 는 손으로 맞춘 창
  좌표가 맞는지 확인할 외부 근거를 찾고 있다. 이 절차는 그 근거가 **어떤 모양이어야
  하는지**를 보여 준다 — 전극별 관측 채널 + 최적화 없는 산술. 다만 Natterer 의
  데이터 자체는 `[인쇄]` "Data will be made available on request" 라 즉시 쓸 수 없다.
- **판정 기준 하나**: 어떤 논문이 "half-cell 로 검증했다" 고 할 때 물어야 할 것은
  "**최적화가 있었는가**" 와 "**pristine OCP 를 재사용했는가**" 두 개다. 둘 다
  '예' 면 그 half-cell 은 검증이 아니라 **같은 가정의 반복**이다.
- **반사실 대조군이 비어 있다**: 원문의 가장 강한 주장("RE 가 없었으면 양극 저항
  증가가 음극에 오귀속됐을 것")에 대조 실행이 없다. 같은 PyBaMM 모델에서
  half-cell 항만 뺀 적합을 돌리면 값싸게 채울 수 있고, 그것이 곧
  [[fitting-degeneracy]] 의 정량 측정이 된다.

## 관련
- [[fitting-degeneracy]]
- [[birkl-ocv-degradation-diagnostic]]
- [[halfcell-window-parametrization-lineage]]
- [[np-lip-ocv-reparametrization]]
- [[22p-physics-or-degeneracy]]
