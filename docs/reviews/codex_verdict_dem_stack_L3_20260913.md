# Codex 적대 리뷰 판정 — DEM 웹앱 스택 **L3** (2026-09-13)

> 기준 스냅샷 = `f28d7a53ce25ffb2d91af3993fbe08262c98e441`.
> 선행 = `codex_verdict_dem_stack_L1_20260913.md` · `..._L2_20260913.md` (둘 다 HOLD).
>
> ⚠ **아래는 받은 판정문 전문이다.**  요약·재서술하지 않는다 (규율 ③).
> `G:행` = `scripts/generate_comparison_plots.py` 의 행 번호.
>
> ★ **독립 재현 = 완료** (§부록).  `L3-02`·`L3-11` 과 상수 셋(EXCL 25 · 특징 14 · α 0.05)을
> 소스에서 직접 확인했고, 설명 세대가 **셋**(18/16/14)이라는 것을 추가로 찾았다.

---

# Codex 판정 — DEM 웹앱 스택 L3: HOLD

검토일: 2026-09-13
최종 기준: claude/sdcp-dem-manuscript-si-pqwtv8 @ **f28d7a53ce25ffb2d91af3993fbe08262c98e441**
범위: **L3-0·L3-a·L3-b·L3-c**, 그리고 원요청 L3의 도메인·표시·LOCKED 배선. **L4/L5 전체, LHS 수확기, Phase A Q7은 이번 판정에 포함하지 않는다.**

## 0. 결론

**새 P1 세 건이다.** L1/L2를 고쳐도 L3가 값을 다시 바꾸는 소비자 결함, 같은 T1이라는 이름 아래 다른 feature를 쓰는 호출부 결함, Hertz 입력이 Physics로 바뀌는 규약 혼합이 남는다.

1. **L3-01 / P1:** 정상 Stage-E 0을 raw 양수로 대체한다. 이온·전자·열 세 타깃 입구에서 재현했다. fallback 행도 이온·열에는 그대로, 전자에는 선택하지 않은 반대 채널의 source에 따라 들어간다.
2. **L3-02 / P1:** 이온 parity·전역 예측·per-config·outlier는 AM 크기를 전달하지 않아 조성 sigmoid를 쓴다. 요인분해는 AM 크기 power gate를 쓴다. 같은 T1의 계수/요인분해가 아니다.
3. **L3-03 / P1, 결손/0 조건부:** cov_Hertz가 없거나 0이면 cov_Physics로 대체된다. 양수 Hertz가 있을 때의 우선순위 수정은 살아 있지만, "모든 T1 입력이 Hertz"라는 계약은 없다.

반대로 **전자 8 LIVE + 2 LOCKED·4drop, 열 14특징·Ridge α=0.05, 전자/열 생산 EXCL 공유·실제 제외는 CONFIRMED**다. 현재 선언 집합은 **25개**이며 23개라는 설명이 낡았다. "14열 배열이 있으니 전자 14 LIVE" 또는 "EXCL이 그림에 남으니 적합에도 들어간다"는 비판은 하지 않는다.

**실코퍼스 계수/R²/LOOCV의 오염량은 미측정이다.** 아래 합성 반례의 배수·점수는 원고 수치의 오차 추정이 아니다. 이번 회신으로 등록식 재적합을 시작하거나 φc·LOCKED·EXCL을 변경하지 않았다.

### 검토 증거와 스냅샷

실행 당시 source는 570d040391f610f43876a609716821bbfba218cc였다. 이후 원격에 올라온 f28d7a53은 L2 판정 등 **문서 4개만** 변경했다. 전체 Git diff와 검토 source 11개의 SHA256을 대조해 실행 결과를 최종 스냅샷에 연결했다. 원래 실행 metadata를 나중 커밋에서 실행한 것처럼 바꾸지 않았다.

검사는 실제 함수 호출 또는 원본 AST 함수 본문의 실행, 합성 입력, 독립 행렬 계산을 사용했다. 출력 기록을 위해 일부 plotting/file-writing만 대체했다. 열 한 건은 **실제 CLI subprocess**까지 실행했다. 브라우저 렌더링·전체 check_all·원코퍼스 재학습은 이번에 수행하지 않았다.

## 1. L3-0 — 실제로 선택되는 y

아래 P/H는 각각 Physics/Hertz-명명 열이다. 이름이 접촉면적의 물리적 타당성을 증명한다는 뜻은 아니다.

| 생산 채널 | 실제 우선순위 | 정상 0 + 다음 양수 | source=fallback 처리 | EXCL이 이 문제를 막는가 |
|---|---|---|---|---|
| 이온 T1 | Stage-E P → raw P → Stage-E H → raw H, **첫 양수** | 0 → **0.7** | source를 읽지 않는다. **0.825도 fit 배열에 포함** | 이온 생산 배열에는 보조 검증기의 두 이름 EXCL도 없다 |
| 전자 22.5 | raw H>0 선행조건; Stage-E H → raw H → Stage-E P → raw P, 양수·상한 검사 | 0 → **20** | **H와 P가 모두** fallback일 때만 거부. H fallback/P solver인 **4는 strict fit에 포함** | 25개 이름과 별개다. 반례는 미등재 이름이며 포함 |
| 열 T1 | Stage-E P → raw P → Stage-E H → raw H, **첫 양수** | 0 → **0.7** | source를 읽지 않는다. **0.825도 fit에 포함** | 전자와 같은 25개 이름만으로 새 fallback을 판별하지 못한다 |

근거: 이온 target `G:4222–4232`, 전자 target `G:5816–5827`, 열 우선순위 `G:6716–6720`, 열 선택 `G:6783–6788`.

### [P1-L3-01] "하나의 Stage-E solver 타깃"이라는 해석은 REFUTED

**이온:** 동일 레코드의 Stage-E Physics=0, raw Physics=0.7에 실제 grade getter는 0, 생산 getter는 0.7을 반환했다. 생산 배열은 log(0.7)을 보존한다. 대체 양수가 없는 정상 0은 fit 배열에서 빠진다. 따라서 "모든 0이 무조건 양수로 된다"가 아니라 **다른 열에 양수가 있으면 다른 해로 승격, 없으면 제외**다.

**전자:** Stage-E Hertz=0/raw Hertz=20을 넣으면 strict fitting의 sig_act=20이다. 실제 plot 함수도 빨간 **σ_e Stage E target** 계열과 Stage-E CSV 열에 20을 전달한다. 원본 0은 그 라벨과 함께 남지 않는다.

별도 반례: selected Hertz의 source=fallback_weighted_factor, selected value=4, raw Hertz=20, 반대 Physics source=solver. target=4, phantom=False, strict 배열/fit/plot에 모두 남았다. 거부 조건이 두 source의 AND이므로 **선택하지 않은 분기가 선택한 값의 신뢰성을 대신 보증**한다.

양성 대조도 했다. **양쪽 모두 fallback인 전자 행은 strict fit에서 빠진다.** allow_no_sigma=True에서 그 행이 sig=NaN으로 남는 것은 prediction-only이고, 그 사실을 fit 오염으로 세지 않았다.

**열:** 정상 0→raw P 0.7, 두 source fallback인 0.825 모두 실제 열 fit에 들어간다. validation_flags.bruggeman_fallback_fired_any가 14개 특징 중 하나인 것은 사실이다(`G:6740`). 그러나 fallback 여부를 설명변수로 넣는다고 대체 추정치가 Kirchhoff 해로 바뀌지는 않는다.

**무너지는 결론:** 하나의 target 정의에 대한 계수·CV·Stage-E 표시라는 주장. L2에서 0을 보존하도록 고쳐도 이 소비자가 다시 양수로 바꾸므로, L2 수정만으로 닫히지 않는다. log fit에 0을 넣을 수 없다는 것은 **다른 모델의 양수를 같은 정답 열에 넣을 근거가 아니다.**

최소 처방은 값만 반환하지 않고 **value/status/target_key/source_kind/reason**을 함께 선택하는 것이다. 정상 0과 미실행을 분리하고, **선택된 열 자신의 source**를 검사한다. 양수 조건부 모델과 전체 퍼콜레이션 모델의 경계·결측 시 raw 대체 허용 여부는 명시적으로 등록해야 한다.

### 호출부별 소비 경로

| 소비자 | 실제 y/필터 |
|---|---|
| 이온 parity | `G:4575` 의 _stage_e_sigma. 정상 0/source 계약은 위와 같다 |
| 이온 전역 fit → 예측·불확실성 | `G:4687` 의 _stage_e_base_arrays → `G:4739` 전역 fit, `G:4762` bootstrap |
| 이온 per-config | `G:4858` 의 같은 getter; 전역 계수 호출도 별도로 존재 |
| 이온 outlier | `G:5176` 의 같은 getter |
| 이온 요인분해 | `G:2331` 의 같은 getter. **y getter는 같지만 X가 다름**(§2) |
| 전자 전역/parity/outlier/요인분해 | 공통 _electronic_form_arrays; 각각 `G:2671` · `G:6214` · `G:6343` · `G:6564` 에서 EXCL mask로 fit |
| 전자 상세 표·ASR | `webapp/app.py:1189` 및 `:1467` 는 **분기별 source**로 숨김. 생산 plot과 다름 |
| 전자 group plots | `webapp/app.py:6214` 에서 저장 full_metrics 파일 경로 수집 → `:6272` 의 별도 plot CLI. 상세 표의 메모리상 숨김은 저장 파일을 바꾸지 않음 |
| 전자 tradeoff 등 | `G:2448` 의 _load_electronic_sigma가 strict getter 거부 후 raw fallback. tradeoff `G:3188`·`G:3208` 에는 주 전자 plot의 추가 phantom mask가 없음; normalized/absolute도 `G:3234`·`G:3280` 에서 같은 loader |
| 열 final parity/outlier/요인분해 | `G:6864` · `G:6919` · `G:6999` 가 공통 배열/fit 사용 |
| fitting report | `scripts/generate_fitting_report.py:362` 전자, `:426` 열은 공통 fit 호출. **표시 문구는 별도 drift**(§6) |

따라서 "모든 UI가 source를 무시한다"도 틀리다. 일부 상세 UI는 막고, 저장 파일을 다시 읽는 plot/fit 소비자는 더 느슨하게 해석한다. 전체 grade 판정과 모든 route의 보증은 L4에서 따로 다룬다.

함수별 source 호출 인벤토리는 이온 결과의 callsite_inventory와 전자 결과의 caller_inventory(관련 scripts 호출 52곳)에 저장했다. 이 개수는 52개 모두를 end-to-end로 실행했다는 뜻이 아니다.

## 2. L3-a — 등록식의 구조와 호출부가 일치하는가

### 2-1. [P1-L3-02] 이온 T1의 power gate는 주 생산 호출에 전달되지 않는다

`G:4341` 의 _sat_g_smooth는 AM 두 크기가 모두 None이면 **옛 조성 sigmoid**로 돌아간다. 실제 AM 크기를 읽는 helper가 있어도, 주요 _sat_baselog 호출은 **여섯 인수만** 넘긴다. 여섯째는 r_SE이지 r_AM이 아니다.

| 실제 호출 | AM 크기 전달 | 실행된 gate |
|---|---|---|
| parity `G:4585` | 없음 | 조성 sigmoid |
| 전역 배열 `G:4694` | 없음 | 조성 sigmoid |
| per-config `G:4868` | 없음 | 조성 sigmoid |
| outlier `G:5185` | 없음 | 조성 sigmoid |
| 요인분해 `G:2314` | r_S·r_P 전달 | min(3.5/r_eff,1)² |

추가로 P2 extras `G:4719–4724` 는 AM 크기 인수를 받지도 않고, g_010을 직접 다시 계산한다. 반면 요인분해 `G:2325` 는 power gate로 P2를 만든다. **base만 고쳐도 P2에 옛 규약이 남는다.**

합성 16행으로 실제 네 plot 함수를 호출해 gate 인수를 기록했다. parity 16회, per-config 32회, outlier 16회 모두 **크기 전달 0회**였다. 요인분해는 16/16회 크기를 전달했다. 저장·그리기만 억제했고, gate/fit 계산은 실제 함수를 썼다.

독립 반례: p=.5, φ_SE=.21, r_SE=1, 나머지 descriptor 동일. AM 반경만 (r_S,r_P)=(2,4)에서 (4,10) μm로 바꾼다.

| 양 | 작은 AM | 큰 AM |
|---|---:|---:|
| 주 생산 base_log | −0.707892914583 | −0.707892914583 |
| 주 생산 P2 | 0.00005625 | 0.00005625 |
| 크기로 계산한 g | 1 | 0.25 |
| 같은 frozen 상수의 size-aware base_log | −0.410863556762 | −0.932442161037 |
| size-aware P2 | 0.0001125 | 0.000028125 |

주 생산 base는 **비트 단위로 불변**이다. 크기 규약으로 독립 재계산한 base 배수는 **1.684685**다. 이 배수는 AM gate 효과를 격리한 고정계수 base 비교이며, 실제 전극 σ의 오차나 재적합 후 배수가 아니다.

**무너지는 결론:** parity·예측·요인분해가 같은 T1을 표현하고, 현재 생산식에 size-based gate가 배선돼 있다는 것. 어느 규약을 정본으로 택하든 지금 두 호출군이 다르다는 반례는 남는다.

### 2-2. Cronau도 생산/검증 구현이 같지 않다

생산 `G:4319` 는 piecewise다. 보조 `scripts/nested_cv_sat.py:211` 의 기본은 smooth sigmoid 합이다. 실제 함수를 같은 r_SE에 호출했다.

| r_SE, μm | 생산 factor | 검증 기본 factor |
|---:|---:|---:|
| 0.1 | 0.650000 | 0.490011 |
| 0.3 | 0.900000 | 0.774990 |
| 0.5 | 1.000000 | 0.949989 |

검증의 smooth=False와 생산은 일치한다. 즉 라이브러리 반올림이 아니라 **다른 함수 선택**이다. 이 차이와 AM gate 차이를 묶어 L3-02의 "같은 T1이 아님"으로 계상하며 별도 P1을 중복 추가하지 않는다.

현재 실제 코퍼스가 해당 반경을 얼마나 포함하는지, 계수/LOOCV가 얼마나 변하는지는 미측정이다. 등록 설명 내부에도 옛 C_blend/게이트 세대가 공존한다. 문서 문구 하나를 근거로 어느 쪽을 즉시 재적합하도록 정하지 않는다. 먼저 등록 의도와 실행 함수·target·cohort를 하나의 식 ID로 고정해야 한다.

### 2-3. [P1-L3-03] Hertz 우선은 맞지만 Hertz 전용은 아니다

_cov_frac는 대상 열 중 **양수만** 평균해 %를 fraction으로 바꾼다(`G:4235`). 정상 Hertz=0도 None처럼 사라진다. 생산 호출들은 모두 **native or Physics**다 — 요인분해 `G:2287` · parity `G:4578` · 전역 배열 `G:4689` · per-config `G:4862` · outlier `G:5179`·`G:5209`.

실제 입력의 native fraction=.12, Physics=.36:

| native 상태 | 실제 채택 cov | base_log |
|---|---:|---:|
| .12 존재 | .12 | −0.707892914583 |
| 없음 | .36 | −0.158586770249 |
| 모든 native 열이 0 | .36 | −0.158586770249 |

같은 고정식의 base가 **√3=1.732051배**로 바뀐다. 이는 합성 입력의 정의 교환 효과이지, 과거 91건의 1.4배를 재측정한 것이 아니다.

**무너지는 결론:** cov_Hertz^0.5에 적합·예측한 단일 규약. L1 단위 수정으로 Physics가 움직이면, Hertz가 없는 행은 이온 "Hertz T1"에서도 움직일 수 있다. 따라서 "이온은 Hertz라 Physics 수정의 영향을 절대로 안 받는다"는 주장은 현재 코드에서는 안 된다.

별도 진단 함수는 φc scan `G:4500`, formtest `G:4985`, refit `G:5063` 에서 Physics를 우선한다. 이들을 현행 primary 호출과 동일시하지 않았다. 진단 코드를 발견했다는 이유만으로 생산이 매번 φc를 재선택한다고 판정하지도 않는다.

### 2-4. 실제 계산 구조 — CONFIRMED 부분

| 생산식 | 실제 구조 | 한정 |
|---|---|---|
| 이온 T1 | `G:4458` 의 OLS: **1, lnτ, (lnτ)², P2, ln f_intact = 5 LIVE** | φc_P=.200, φc_S=.195, δ=.040, CN², cov^.5 상수는 존재. 그러나 gate/P2/cov 계약은 위와 같이 불일치 |
| 전자 22.5 | **8 LIVE + 2 LOCKED**. 14열 중 0/1 고정, 3/7/12/13은 정확히 0 | NCM mix + 4lnφ_AM + .5lnA는 고정 offset. live thin/bimodal 항도 φ에 의존하므로 **전체 탄력성이 언제나 4라는 뜻은 아님** |
| 열 T1 | **14특징 + 절편**, Ridge **α=.05**, 절편 벌점 0 | 실제 세 final plot이 같은 14/.05를 호출. 단일 올바른 y/물리법칙의 검증은 아님 |

전자 근거: version/drop 상수 `G:5796`, 고정 offset `G:6045`, 14열 `G:6104`, lock/drop 후 실제 적합 `G:6165`. 합성 fit에서 LOCKED endpoints=10/5, dropped 네 계수=정확히 0. φ만 1.1배→offset 배수 1.4641, A만 4배→2.
8 LIVE는 β_T, τ의 절편/1차/2차, thin×lnφ, thin×lncoverage, p(1−p)lnφ, ln f_intact다. NCM은 `G:6045–6046` 에서 1/[1+(r/2)^1.5]로 계산되며 β=1.5는 LIVE 열이 아니다. 대칭 bimodal 구조 p(1−p)도 고정이다. 원래 원요청의 "LOCKED 지수 5개"를 모두 별도의 회귀 계수 5개라는 뜻으로 읽으면 안 된다.

열 근거: 활성 특징 목록 `G:6729`, Ridge fit `G:6823`. 독립 정상방정식과 계수 최대차 0. 실제 14특징은 porosity, lnCN, τ_std, lnGBdensity, lnASR, AM vulnerability, CN_std, lnactive_fraction, ln(R_brug/full)_physics, fallback flag, SE–SE Physics area, AM–SE Physics area, τ_median, lnE_SE다. **열은 L1/L2의 Physics 면적·파생량에 직접 의존**한다. 명칭의 낡음과 실제 배열을 구분해야 한다.

전자 도메인 가드도 실제 작동한다. `G:5959` 는 strict와 allow_no_sigma 모두 **φ_AM>.30**을 요구한다. .20/.299999/.30 제외, .300001 포함을 실행했다. 다른 옛 screening 모델이 저φ 값을 내는 것은 22.5 가드 우회와 동일하지 않으며, 앱 전체의 모든 모델 금지를 보증한 것은 아니다.

## 3. L3-b — 상수와 EXCL은 한 곳인가

**부분적으로만 그렇다.**

| 항목 | 실제 공유/중복 |
|---|---|
| 생산전자 ↔ 열 EXCL | 같은 G 모듈의 **25명 집합**을 열 `G:6807` 가 직접 읽음 |
| 생산전자 적합·플롯 | fit mask로 실제 제외; 표시용 배열/예측에는 X로 남길 수 있음 |
| 보조 electronic_nested_cv | 자체 **6명**. 생산과 차집합 19명 |
| 이온 φc/δ | `G:4259` 에 상수, 보조 nested에도 별도 구현. P2의 .195/g_010은 `G:4719` 에 다시 하드코딩 |
| 이온 EXCL | nested loader는 두 이름 제외; G의 전역 loader/배열은 같은 제외를 하지 않음 |
| 버전/설명 | 활성 코드와 그림 제목·CSV·report 문자열은 여러 곳에 중복 |

생산전자의 EXCL 효과를 실제로 검증했다. 합성 32행 중 EXCL 2행 → n_fit=30. EXCL 행들의 log target에만 +100을 줘도 fit 계수 변화는 **0**이었다. 열도 25개 이름을 각각 붙여 **25/25 제외**를 재현했다. **이름 25개라는 집합 크기는 현재 코퍼스에서 실제로 탈락한 행 수와 다르다.** 사유의 정당성·현재 교집합 수는 재승인하지 않는다.

### [P2-L3-04] 검증 스크립트의 이름/점수가 현행 생산식을 식별하지 않는다

이온 `scripts/nested_cv_sat.py:61`·`:103` 는 input_1mAh_9와 input_particulate_12_S3를 제외한다. G 전역 loader `G:7129` 및 배열 `G:4686` 에는 같은 필터가 없다. 같은 임시 JSON 두 개(제외 이름 하나와 대조군)를 읽히면 **보조 1행 / 생산 2행**, y=.05가 생산에 남는다.

전자 `scripts/electronic_nested_cv.py:278` 는 고정 base의 plain LOO, `:359` 는 같은 LOO를 보는 지수 screen이다. 실제 base는 `:254` 의 **50·φ_AM^1.5·CN²·cov^.5·f_p³**로, 현행 22.5와 다르다. outer 선택 평가 루프가 없으며 EXCL도 6명이다.

**무너지는 결론:** 이 보조 파일이나 그 점수를 곧 현행 T1/22.5·현행 코호트의 nested 검증으로 인용하는 것. 이는 생산 EXCL이 작동하지 않는다는 뜻도, 고정형식 plain LOO 자체가 무조건 부적절하다는 뜻도 아니다. 검증 아티팩트에는 적어도 target 규약·feature 함수·EXCL/코호트·선택 절차 ID가 필요하다. 코드가 다른 상태에서 점수만 전사하면 안 된다.

## 4. L3-c — LOO·nested·GPR

### 4-1. 고정된 X/y의 coefficient LOO 계산은 맞다

합성 24행, 원함수와 독립 n−1 재적합/열 hat-matrix 계산:

| 모델 | 원함수 LOO R² | 독립 계산 |
|---|---:|---:|
| 이온 | .8415429927828078 | .8415429927828078 |
| 전자 | .9738432342928135 | .9738432342928133 |
| 열 | .9975949629298785 | .9975949629298785 |

근거: `G:4480` · `G:6190` · `G:6841`. **고정 feature·target·cohort·형식 조건부 CONFIRMED**다. upstream 결함이나 과거 항/문턱/EXCL 선택까지 이 실험으로 검증한 것은 아니다.

모델/하이퍼파라미터 선택까지 포함하는 성능은 그 선택을 inner fold에서 수행하고 별도 outer에서 평가해야 한다. 고정식 coefficient LOO와 그 전체 선택 절차의 성능은 다른 추정 대상이다.

### 4-2. 알려진 GPR 누설 — 미수정, 신규 P1 중복 계상 안 함

실제 predictor train_models를 합성 12행·한 타깃에 실행했다. 실제 sklearn estimator와 기본 optimizer를 유지했다.

- `webapp/predictor_engine.py:415` 의 X scaler, `:449`·`:496` 의 y scaler: **세 fit 모두 12행 전체**.
- 그 뒤 6커널×5fold=30회, RF 5fold가 실행된다.
- `:528` 에서 같은 CV로 커널 선택. 별도 outer 없음.
- 첫 fold의 학습 X가 train-only 표준화와 최대 .350076 차이였다.

단, `webapp/templates/predictor.html:693` 에는 **실제 화면 toast 경고**가 있다. "경고가 주석뿐이다"는 판정은 틀리다. nested 구조 패널도 별도 표시한다. 그러나 `webapp/app.py:10637` 의 학습 API는 numeric cv_scores를 그대로 반환한다. 현행은 **경고·표시 분리이지 기계적 비교 차단 계약은 아니다**.

전처리 추정량은 각 학습 fold에서만 적합해야 한다. 이 원칙은 scaler뿐 아니라 결측 대체에도 적용된다.

### 4-3. 새 P2 세 건 — 검증 숫자의 의미가 달라지는 반례

**[P2-L3-05] SAT nested의 결측 반경 대체가 보류점을 읽는다.**
`scripts/nested_cv_sat.py:346` 는 제공된 전체 배열의 AM 반경 중앙값을 쓴다. outer `:489` 와 inner `:461` 는 전체 base를 만든 뒤 train을 자른다.

학습행 하나의 r_S=NaN, 보류행 하나의 r_S만 1→20. 다른 학습 입력/y는 그대로인데 전체 median 4→5, **학습행 base −.0566580738→−.0724783898**. train-only 계산은 불변이었다. **결측 조건부의 누설**이며 실제 코퍼스 발생률/점수 변화는 미측정이다. 보조 size-gate 검증기의 결함이지, 주 생산 label-gate와 같은 경로라고 섞지 않는다.

**[P2-L3-06] 열 LOO 실패 fold가 오차 0으로 사라진다.**
`G:6845` 의 except:pass. 전체 fit은 정상으로 두고 첫 LOO solve만 LinAlgError를 내게 하면 **.997594962930→.997619905607**로 점수가 좋아지고 실패 상태가 없다. 실제 수치 실패 발생을 관측한 것은 아니며, 실패 시의 검증 계약 반례다. 실패 fold를 제외해 좋은 점수를 반환하지 말고 **CV_FAILED/불완전**을 내야 한다.

**[P2-L3-07] 반환 CV는 배포 blend의 CV가 아니다.**
`webapp/predictor_engine.py:583` 는 GPR/RF 점수의 max를 보고하지만, 배포 예측 `:712` 은 가중 blend다. 실제 합성 실행에서 GPR=.854192822, RF=−1.062218172, 보고=.854. 저장된 가중치 .895199379/.104800621로 같은 OOF 예측을 합치면 **.826989101**이다. 마지막 값도 global selection을 쓴 **차이 진단**이지 unbiased nested 점수가 아니다. 보고값을 단일 선택모델의 non-nested CV라고 명명하거나 전체 blend 선택 절차를 outer 평가해야 한다.

## 5. L3에서 추가 재현한 운영/입력 경계

| ID | 반례와 위치 | 무너지는 결론 / 범위 |
|---|---|---|
| **P2-L3-08** | EXCL 전 최소 8행 `G:6027`, 이후 `G:6155` 에 mask 후 최소수/랭크 검사 없음. 8행 모두 EXCL → **n_fit=0인데 유한 예측·R²=LOO=0** 반환 | "적합 성공한 모델"이라는 해석. 현재 전 코퍼스가 0행이라는 주장은 아님 |
| **P2-L3-09** | `G:6004` 가 frac_intact_force_pct=0을 1.0으로 바꿈. 실제 LIVE ln f_intact 열은 **0%=100%=결측=0**, 0.01%/5%는 −2.995732 | 확정 전파괴와 전건전이 같은 feature. 실제 incidence/효과량 미측정 |
| **P2-L3-10** | 열 registry `G:6911`·`G:6986`·`G:7063` 는 desc, main `G:7350` 은 description 요구. 실제 thermal_fit_final CLI에서 **PNG 생성 후 KeyError, rc=1**, 최종 metadata 없음 | "계산 성공→게시 완료"가 성립하지 않음. fit 자체는 실행됐고 Flask/브라우저 전체는 미실행 |
| **P2-L3-12, 동일 프로세스 한정** | 이온 bootstrap key `G:4771` 는 n/B/seed/첫·끝 y/sum(base)뿐. 중간 y 하나×10 → 이전 객체 재사용. stale residual SE=.04488437, cache clear 후 .56962704 | 현재 입력의 불확실성이라는 해석. 보통 새 subprocess인 웹 요청 간 누적 오염을 주장하는 것은 아님 |

합성 fit의 계수나 SE를 원고 오차막대로 사용하면 안 된다.

## 6. [P2-L3-11] Methods/그림으로 전사하면 모델 세대가 달라진다

이는 문법 취향이 아니라 **어느 수식을 계산했다고 보고하는가**의 결함이다.

- 전자 실제 plot 제목 `G:2854` 에는 drop한 네 항이 남는다. 계산은 8 LIVE인데 설명식을 그대로 옮기면 더 큰 모델이 된다.
- CSV 예측 열 `G:2876` 은 **Stage_15_form**, 값은 현재 22.5 예측이다.
- `scripts/generate_fitting_report.py:370` 이후 보고서는 Stage22/12 LIVE로 설명하지만 앞에서 현행 fit을 호출한다.
- 열 실제 decomposition 제목 `G:7039` 는 **α=.1**, 호출 연산은 **.05**다.
- 열 registry `G:6911` 는 16특징/.1, fitting report `scripts/generate_fitting_report.py:436` 등은 16특징/23 EXCL이다. 실제는 **14/.05/25명 집합**.

전자 plot의 렌더러 인수와 열 실제 제목을 기록했다. fitting report 전체 생성은 하지 않았으며 해당 문자열/호출을 추적한 범위다. 설명을 상수·활성열에서 생성하게 만드는 것은 계수/지수 선택 변경이 아니다.

전자 bootstrap의 12-LIVE residual/8-LIVE resample 혼합도 `G:2548`·`G:2565` 에서 정적으로 보인다. **이번에는 PI 영향의 독립 실행 재현을 완료하지 않아 위 신규 finding 숫자에 넣지 않았다.** 점예측 구조의 CONFIRMED를 PI 보증으로 넓히지 않는다.

## 7. 고칠 수 있는 것과 분석을 다시 정해야 하는 것

### 기존 구조에서 고칠 수 있는 구현

1. **단일 target selector:** 정상 0/미실행/fallback/raw를 분리하고 선택한 값의 source를 따라간다. UI·fit·CSV가 같은 선택 결과를 받게 한다.
2. **단일 feature builder:** AM gate/P2/Cronau/coverage family를 한 번 계산해 parity·예측·요인분해·CV에 전달한다. 같은 데이터의 X/base/y/cohort가 소비자별로 동일한지 회귀시험한다.
3. **검증 계약:** fold 내 imputation, failed-fold fail-closed, EXCL 후 유효행/랭크 검사, 배포 estimator와 CV estimator 명칭 일치.
4. **출력 계약:** 실제 모델 버전·활성항·α·EXCL 및 선택 source를 결과에 기록하고 설명/CSV/캐시 식별자도 여기서 생성한다.

현재 OLS/Ridge 전체를 버려야 한다는 반례는 아니다. **분산된 getter/feature/설명 생성부는 교체·통합이 필요하지만 선형대수 엔진 자체의 전면 재작성 근거는 없다.**

### 지금 구조의 "첫 양수 fallback"으로는 해결할 수 없는 것

정상 미퍼콜 0을 대상으로 하면서 log-positive 단일 회귀에 모든 관측량을 조용히 넣는 문제는 getter 수정만으로 끝나지 않는다. **퍼콜레이션 관측량과 양수 조건부 σ를 분리할지**, 다른 모델을 쓸지, raw/fallback을 별도의 결과 계열로 둘지 분석 범위를 명시해야 한다. 값이 다른 계산을 같은 y라 부르는 방식은 유지할 수 없다.

L1/L2에서 면적·접촉저항/Stage-E 값을 고친 뒤 L3의 어떤 입력과 y가 달라지는지 **원자료로 census**해야 한다. 기존 정본의 수치를 새 함수로 덮어쓰는 것은 금지다. 이온도 Hertz fallback 때문에 영향 0을 보장할 수 없고, 열은 Physics 면적 특징을 직접 쓴다.

**재적합·새 CV 성과 보고는 별도 사전등록 사안이다.** 이번에는 φc=.200/.195/δ=.040, LOCKED 지수, EXCL 이름·이유, α 또는 실제 코퍼스 계수를 바꾸지 않았다. 구현 정합성 수정과 과학적 모델 선택을 한 커밋/한 성과 숫자로 섞지 않는 것이 해제 조건이다.

### L3 해제에 필요한 증거

- 정상 zero·결손·selected fallback·반대 채널 solver를 포함한 target 계약 회귀.
- 한 원자료 레코드의 모든 소비자에서 **같은 base/X/y/key/source** 확인. AM 반경 두 반례 및 native=0 포함.
- 생산/CV의 모델·feature·cohort·EXCL fingerprint 일치 또는 별도 진단이라는 기계 판별.
- 실패/결측/EXCL 후 부족/캐시 변경을 검증기가 성공 숫자로 숨기지 않는 회귀.
- 원코퍼스 **영향 census 먼저**, 변경된 타깃/규약과 기존 분석 구분, 새 성능 수치가 필요하면 등록 후 실행.

## 8. 재현 명령과 산출물

네 probe(`probe_l3_ionic.py` · `probe_l3_electronic.py` · `probe_l3_thermal.py` ·
`probe_l3_cv.py`)를 **실제 실행해 rc=0을 얻었다**. T 내부 CLI rc=1은 L3-10의 기대된 실패
증거다. 원본 source·실코퍼스를 고치지 않고 합성/임시 자료만 사용한다.

CV 검증용 scikit-learn **1.9.1** 및 의존성은 증거 폴더에만 설치했다. 실제 배포 서버 버전과
동일하다고 가정하지 않는다. probe의 원 실행 대상은 570d 스냅샷이며, 최종 f28d와 source가
동일한 연결 증거를 앞에 붙였다.

하위 검토문의 ID는 담당별 임시 ID다. **이번 회신의 finding ID 정본은 본문 L3-01~L3-12**이며, 리포 findings.json에 자동 등재하지 않았다.

## 9. 아직 답하지 않은 범위

**L4 전체, L5의 ml_design_structure 중첩 선택/free_products/use_porosity/7개 구조 타깃, LHS130 수확기, Phase A Q7은 미판정**이다. GPR 일부를 L3-c 비교 문제로 읽었다는 이유로 L5 전체 검토 완료라 하지 않는다. 이번 L3 HOLD는 L1/L2의 미해결 물리 문제를 해제하지도 않는다.

---

## 부록 — 이 리포에서의 독립 재현 (2026-09-13, claude)

### P1-L3-02 — **생산 4곳은 AM 반경을 안 넘기고 요인분해만 넘긴다** ✅ 소스로 확정

`_sat_baselog` 호출을 전수로 훑어 인자 개수를 셌다:

```
 4585  인자 6개  AM반경전달=아니오   parity
 4694  인자 6개  AM반경전달=아니오   전역 배열
 4868  인자 6개  AM반경전달=아니오   per-config
 5185  인자 6개  AM반경전달=아니오   outlier
```
반면 요인분해는 **`G:2314`** 에서
```python
g_p = _sat_g_smooth(p_amp[i], r_AM_S[i], r_AM_P[i])      # ← AM 반경 전달
```
⇒ 판정문 그대로다.  **같은 T1 이라는 이름 아래 두 gate 가 동시에 돈다.**

### P2-L3-11 — **설명 세대가 셋이다** (판정문은 둘까지 봤다)

| 상수 | 실제 | 파일 안의 설명 |
|---|---|---|
| `_EXCLUDED_NAMES_EL` (`G:5661` frozenset 전수) | **25** | 문서·report **23** |
| `_THERMAL_T1_FEATURES` | **14** | `G:6703` 주석 **18** · `G:6911` registry **16** · `G:7039` 제목 |
| 열 Ridge α (`_thermal_fit` 기본값, 호출 3곳 전부 기본값) | **0.05** | `G:6911` **0.1** · `G:7039` 제목 **0.1** · `G:6694` 주석 **0.1** |

★ `G:6703` 의 *"18 features"* 는 판정문도 안 짚은 **세 번째 세대**다.
전자 제목에도 드롭된 네 항이 살아 있다:
```
2855:  × exp[β_AC·φ·logCN + β_v·v_AM]  ←network
2858:  × exp[g_thin·(β_φth·logφ + β_covth·log cov_AM,P + β_fpth·log f_p)]  ←thin film
2877:  ['σ_e_Stage_E(mS/cm)', 'σ_e_Stage_15_form(mS/cm)']
```
⇒ 계산은 **8 LIVE** 인데 제목을 그대로 옮기면 **12 항 모델**이 되고, CSV 열은
**Stage_15** 라 적힌 채 **22.5 예측값**을 담는다.

### ⚠ 내 검증이 한 번 틀렸다

처음에 정규식으로 `_EXCLUDED_NAMES_EL` 을 세어 **0개**, `_THERMAL_T1_FEATURES` 를 **16개**로
읽고 *"판정문의 25·14 가 아니다"* 라고 쓸 뻔했다.  전자는 `frozenset([` 형태라 내 패턴이
안 걸린 것이고, 후자는 내가 **다른 상수**를 잡은 것이었다.  괄호 균형으로 다시 세니
**25 · 14** 로 판정문과 정확히 같다.
⇒ 교훈: **엉성한 grep 으로 판정문을 반박하지 않는다.**  ID `SELF-25`.

### 우리 정본 정정 (규율 ④, 같은 커밋)

`CLAUDE.md:1979` 의 *"EXCL list = σ_e `_EXCLUDED_NAMES_EL` (23 cases, shared)"* 를
**25개**로 고쳤다 (`L3-06`).  ⚠ **이름 25개 ≠ 현재 코퍼스에서 실제 탈락한 행 수**.

### 아직 재현하지 않은 것

`L3-01`(정상 0 → raw 양수, 세 채널) · `L3-03`(cov 결손 시 Physics 대체, √3배) ·
`L3-04`(보조 검증기 불일치) · `L3-05`(nested imputation 누설) · `L3-07~10` · `L3-12`(bootstrap
캐시) 는 합성 레코드와 실제 plot 함수 호출이 필요해 이 자리에서 돌리지 않았다.
소스 위치는 전부 실재를 확인했다.
