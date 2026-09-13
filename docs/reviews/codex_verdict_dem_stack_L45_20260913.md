# Codex 적대 리뷰 판정 — DEM 웹앱 스택 **L4 · L5** + 별건 둘 (2026-09-13)

> 기준 스냅샷 = `e68d2b23a1f578327db443ab1360318446d064b3`.
> 선행 = L1 · L2 · L3 판정 (전부 HOLD).
>
> ⚠ **아래는 받은 판정문 전문이다.**  요약·재서술하지 않는다 (규율 ③).
>
> ★ **`P1-HARV-01` 은 내가 쓴 코드의 결함이고 같은 날 재현·수정했다** (§부록).

---

# Codex 판정 — DEM 웹앱 L4·L5 통합 리뷰

기준: **e68d2b23a1f578327db443ab1360318446d064b3**
브랜치: claude/sdcp-dem-manuscript-si-pqwtv8
범위: L4 등급·검증 소비자·SE 진단·EIS/재료 상수, L5 구조 ML의 데이터·검증·배포. 별건 LHS 수확기와 Phase A Q7도 아래에서 별도로 답한다.

## 0. 결론

**L4 HOLD · L5 end-to-end HOLD. 기본 구조 ML의 nested_cv 자체는 CONFIRMED.**

새 P1은 본체에서 **6건**이다: L4-01/02/03, L5-01/02/03. 기존 L1/L2/L3의 물리·GPR 결함을 이 숫자에 다시 넣지 않았다. 별건 수확기에는 추가 P1-HARV-01이 있다.

- 이온 전도도 0을 등급의 직접 σ 축은 D로 읽지만, 파생 ASR 합산에서는 이온 저항이 사라져 **총 ASR·C-rate proxy·분극이 A**가 된다.
- fallback/source와 실패 flag는 등급의 권위 있는 게이트가 아니다. audit도 자기신고의 모순을 통과시켜 **실패 flag가 있는 합성 사례들을 3/3 trustworthy**로 출력했다.
- 구조 ML은 σ를 y로 삼지 않지만, 데이터 생성기가 먼저 **σ<0.01 행을 버린다**. coverage의 정상 0도 0.20으로 바꾼다.
- 금지한 use_porosity_pct는 학습되고, 일반 예측·표면에서는 숨겨져도 **다음 배치 추천에는 사용된다**.
- nested 핵심을 폐기할 근거는 없다. 다만 닫힘 ε의 부착된 검증/띠에는 별도 누출과 모델 설정 불일치가 있다.

**이는 실제 코퍼스의 영향 건수/원고 변화량을 계산한 판정이 아니다.** 실제 291/130 데이터를 재적합하지 않았다. 원본 함수를 결정론적 합성 자료에 실행했고, 소스·정본·계수는 변경하지 않았다. 기존 check_all/selftest의 초록을 근거로 삼지 않았다.

### 증거의 강도와 한계

- 등급, audit의 실제 main, SE 진단, 구조 데이터 생성기, nested/학습/배포 함수, 수확기의 τ 함수: **실제 함수 실행**.
- 앱의 상세화면 suppression: 원본 AST의 해당 문장 그대로 실행. 전체 Flask 요청/브라우저 화면을 띄운 검증은 아니다.
- 구조 UI: 원본 JavaScript 두 함수를 Node의 합성 DOM에서 실행. 서버 함수와 수치 대조.
- eis_fit의 회로 선택/입력: CustomCircuit recorder로 데이터 흐름을 관찰. **실제 impedance 최적화 수렴 검증은 하지 않았다.** 별도 physics_eis 스펙트럼과 se_material 수식은 실제 실행했다.
- 원고 숫자·실험 적합도·실침대 영향량·원 로그 완전성은 이 합성 검증으로 보증하지 않는다.

## 1. 질문별 답

| 질문 | 판정 | 핵심 |
|---|---|---|
| L4-0 수치/source/정상 zero | **REFUTED** | 직접 σ는 0을 유지하지만 파생 저항에서 소실. source를 바꿔도 등급 동일. 상세 경로의 Physics suffix 정리도 불완전 |
| L4-a τ 라벨/동일성 | **부분 CONFIRMED / 동일량 주장은 REFUTED** | grade는 Laplace eff/bulk, 앱 overhead는 eff/Dijkstra. grade의 3.0 고정 때문에 온도 스케일 불변성도 깨짐 |
| L4-b validation이 보증하는 것 | **제한적 자체 진단만** | 네 개의 평가 가능한 sanity flag. 관통·물리 타당성·solver 출처 증명 아님. audit conjunction 재검증도 없음 |
| L4-c 파생 축의 독립성 | **REFUTED** | 54축 중 36개가 파생 키. 다수는 동일 σ·조성·porosity의 재표현 |
| L4-d EIS가 STEP3/4에서 유도되는가 | **eis_fit에 대해서 REFUTED** | 실험 f,Z를 별도 회로에 역적합. physics_eis는 별도 순방향 근사. se_material 내부 단위/온도식은 대조 통과, 전역 중앙화는 미완료 |
| L5-a nested 항/λ/기저족/표준화 | **핵심 CONFIRMED** | outer train 안에서 재선택·표준화. 단 bundle에 붙이는 closure 검증까지 CONFIRMED는 아님 |
| L5-b free_products 제한 | **기본 후보 생성 CONFIRMED / 대조 전용 봉인은 REFUTED** | 기본 6노브 곱만. --derived-products 산물이 일반 USABLE 배포 모델로 수용됨 |
| L5-c use_porosity 학습·노출 제외 | **REFUTED** | 학습됨. status/predict/surface는 차단, suggest는 미차단 |
| L5-d σ는 y가 아닌가 / 구조 독립인가 | **전자는 CONFIRMED, 후자는 REFUTED** | 12 y에 σ 없음. 그러나 upstream σ 기준으로 구조 행을 제외하고, 입력 target 값도 변환 |
| L5-e 학습/배포 변환 일치 | **동일 6노브·정상 수치에서는 CONFIRMED / UI·비유한 경계는 REFUTED** | 동일 모델의 scaler/값/구간은 일치. UI가 다른 d_am을 전달하고 NaN이 정상 표지로 반환됨 |

## 2. L4 반례

### P1-L4-01 — 정상 미전도/결측이 총 저항에서는 0 Ω처럼 취급된다

위치: `scripts/grade_engine.py:934` · `:997` · `:1023` · `:1526`.

실제 계산: σ_ion≤0 → ASR_ionic=None → (asr_i or 0)+(asr_e or 0). 따라서 비전도와 저항 0이 합산 단계에서 같은 효과를 낸다.

합성 입력은 두께 100 µm, σ_e=5 mS/cm이며 다른 항은 고정했다.

| 입력 | 직접 σ_ion 등급 | ASR_ion | ASR_total | 1/ASR_total | 분극 | 종합 |
|---|---|---:|---:|---:|---:|---|
| σ_ion=0.1 mS/cm | B− | 100 | 102 (B) | 0.009804 (B) | 33.66 mV (A) | B+ / 86.2 |
| **σ_ion=0** | **D** | **없음** | **2 (A)** | **0.5 (A)** | **0.66 mV (A)** | B / 82.4 |
| 이온 값 전부 결측 | — | 없음 | **2 (A)** | **0.5 (A)** | **0.66 mV (A)** | B+ / 89.5 |

여기서 **종합이 A라는 뜻은 아니다**. 잘못 좋아지는 것은 파생 축이며, 결측은 종합의 분모에서도 빠진다(21→18→17개 채점). 이를 정상적인 비퍼콜 전극의 수송 성능 순위로 쓸 수 없다.

직접 등급 축은 `scripts/grade_engine.py:1288` 의 None 검사라 정상 0을 raw 양수로 승격하지 않는다. L3의 생산 target getter와 값이 다른 문제는 그대로이고, **이번 신규 결함은 그 0이 저항·등급으로 번역될 때 생긴다.**

정상 0은 유효 비전도 상태/무한 저항으로, 미확인은 UNKNOWN으로 구분해야 한다. 이를 숫자 None 하나에 합친 뒤 산술 기본값 0을 넣는 구조로는 해결되지 않는다.

### P1-L4-02 — source/실패 flag가 등급을 막지 않으며 상세화면 정리도 한 조합에서 샌다

위치: `scripts/grade_engine.py:715` · `:741` · `:1118` · `:1239` · `webapp/app.py:5803` · `:5836`.

반례 1: 동일 σ=0.825에 source만 solver↔fallback_weighted_factor로 바꾸면 **전체 grade 결과가 동일**했다. solver_input_intact=False, trustworthy_overall=False도 다른 축을 중단시키지 않는다. 신뢰 축은 낮은 가중치의 점수일 뿐이다. Stage E 보정 적용 축은 수치 키의 존재만으로 A를 준다.

반례 2: 상세화면에 Hertz 전자 source=solver, Physics 전자 source=fallback을 준다. 원본 suppression을 실행하면:

- raw Physics 값은 None이 된다.
- 잘못된 이름 electronic_sigma_full_mScm_physics_stage_e 등을 새로 None 처리한다.
- **정식 키 electronic_sigma_full_mScm_stage_e_physics=5는 남아 A등급**이 된다.

원인: raw key 뒤에 suffix를 붙이는 5813–5814의 조립 순서. Hertz와 Physics가 **모두** fallback이면 Hertz 반복이 정식 Physics 키도 지울 수 있으므로, "모든 fallback이 샌다"고 넓혀 말하지 않는다. 혼합 source가 결정적 반례다. 열 κ에도 같은 이름 조립 구조가 있다(실행 반례는 전자).

고치는 방향은 소비자별 문자열 조립이 아니라 canonical 필드명+상태 계약의 공통 조회다. 등급은 source 적격성을 가중 평균으로 상쇄하면 안 된다.

### P1-L4-03 — audit가 개별 실패와 요약의 모순을 통과시킨다

위치: `scripts/audit_validation_flags.py:117` · `:140` · `:180`.

합성 디렉터리 네 개를 실제 main에 넣었다: ① solver_input_intact=False, trustworthy_overall=True. ② 모든 개별 게이트 부재, trustworthy_overall=True. ③ 개별 게이트 전부 False, trustworthy_overall은 문자열 "false". ④ JSON 자체가 깨진 파일.

결과: 발견 4건 중 JSON 오류는 분모에서 빠지고, 나머지는 **3/3 trustworthy (100%)**, fail 파일 미생성. LaTeX는 "all assessable gates True"라고 기록한다. **코드가 읽은 flag들과 그 요약이 모순**이다.

이 도구가 명시적으로 self-reported audit인 것은 맞다. 그래서 원 물리의 독립 검증을 기대한 것이 아니다. 그보다 약한 **자체 기록의 bool 타입·conjunction·누락 집계**도 검증하지 않는다는 반례다.

### P2-L4-04 — τ의 분모·온도·라벨이 소비자마다 다르다

위치: `scripts/grade_engine.py:893` · `:913` · `webapp/app.py:2503` · `:6705`.

| 소비량 | 코드가 계산하는 양 |
|---|---|
| grade τ_eff | √(φ_SE × **3.0** / 선택된 Stage-E Physics 우선 σ) |
| grade τ_bulk | √(φ_SE × **3.0** / σ_bulk_net) |
| grade overhead | τ_eff/τ_bulk = √(σ_bulk_net/σ_selected) |
| 앱 τ_eff | baseline Hertz/Physics σ와 **그 baseline 온도에 맞춘** σ_grain |
| 앱 overhead | τ_eff/**τ_Dijkstra** |

동일 구조에서 모든 이온 σ와 대응 grain을 ×4 했다. 앱 τ_eff는 **3.464101615 그대로**지만 grade는 **3.464101615→1.732050808**, 등급 B−→A. grade τ_bulk도 1.73205→0.86603으로 바뀐다. 이 ×4는 온도식의 실측 계수가 아니라 **공통 스케일 불변성 검사**다.

같은 합성 자료에서도 grade overhead=2, 앱 eff/Dijkstra=2.309401이다. 둘은 서로의 대체 열이 아니며 등록 Dijkstra target도 아니다. grade overhead는 **저항비의 제곱근**이므로 저항비 자체라고 설명하면 틀린다.

또 `scripts/grade_engine.py:340` 의 Bruggeman overestimation은 앞 L2가 밝힌 CONTACT_FREE/FULL 모델 내부 비교를 소비한다. 실험 오차로 재명명할 수 없다. `:921` 의 constriction fraction도 L2-08의 잘못된 원 저항 분율을 1−f로 옮길 뿐, 소산 분율을 새로 측정하지 않는다. 이 두 기존 L2 결함은 신규 P1로 재계상하지 않는다.

### P2-L4-05 — 가장 좁은 0면적 edge가 bottleneck 집계에서 사라진다

위치: `scripts/viewer3d_data.py:547` · `:650` · `scripts/grade_engine.py:817`.

5 SE 노드의 4-edge chain 중 1개 면적만 0. 위상은 4개 edge를 모두 써 5개 입자를 관통 성분으로 본다. 그런데 bottleneck 집계는 area≤0을 제외해 **n_perc_edges=3, below-threshold=0, grade burden=0**을 내놓는다.

위상 접촉을 0면적에서도 유지하는 규약 자체를 부정하는 것이 아니다. **그 망의 "좁은 접점 비율"을 재면서 최소 면적 edge를 분자·분모에서 지우는 것**이 문제다.

### P2-L4-06 — 진단 코퍼스 중복제거가 바이트 수만 본다

위치: `scripts/extract_se_network_diagnostics.py:82` · `:92`.

서로 다른 atoms 내용/SHA를 가진 두 사례의 파일 크기를 각각 atoms=97 B, contacts=85 B로 맞추면 **case_a만 남는다**. 동일 크기는 동일 자료의 증거가 아니다. grade의 corpus-percentile 기준에도 이 선택이 전파될 수 있다.

### P2-L4-07 — input_params가 존재하면 meta의 명시적 상 지도를 무시한다

위치: `scripts/extract_se_network_diagnostics.py:107` · `:133`.

input_params에는 scale만, meta에는 1:AM_P,2:SE가 있고 실제 입자가 type2인 합성 자료. 첫 JSON을 읽자마자 break하므로 meta의 type_map을 보지 않고 3-type 기본 지도를 쓴다. **실제 SE 5개 → 추론 SE 0개**.

모든 mono가 잘못된다고 일반화하지 않는다. 이 정상적으로 표현 가능한 메타데이터 배치에서 상이 사라진다는 반례다.

### P2-L4-08 — cycle-stable은 교집합 측정이 아니고 파괴 결측은 0으로 읽힌다

위치: `scripts/grade_engine.py:833` · `:1045`.

이온 활성 50%, 전자 활성 50%, 심한 파괴 0%이면 코드의 cycle-stable은 **25%**. 하지만 두 활성 집합이 일치하면 실제 교집합은 50%, 서로 겹치지 않으면 0%이다. 같은 주변 비율만으로 둘을 식별할 수 없다. 여기에 파괴 입력 전부 부재도 심한 파괴 0%/A가 된다.

이 값은 독립성을 가정한 marginal-product proxy로 라벨링하거나, 입자별 전자·이온 활성과 손상 마스크의 **실제 교집합**으로 대체해야 한다. 숫자 버그 하나를 고쳐 실제 cycle life 측정으로 만드는 것은 불가능하다.

### P3-L4-09 — Q_gravimetric의 표시식이 실제 175를 190으로 설명한다

위치: `scripts/grade_engine.py:356` · `:969`.

85:15 입력의 실제 Q는 **148.75 mAh/g=0.85×175**. 반환 formula/meaning은 190 계열을 설명하여 161.5를 뜻한다. 175를 190으로 바꾸라는 권고가 아니다. **선택한 175를 설명까지 동일하게 써야 한다.**

### L4-d: eis_fit과 physics_eis의 관계 — 범주 정정

`scripts/eis_fit.py:114` 는 실험 f,Z와 HF 절편을 받아 R0를 고정하고 나머지를 적합한다. 대칭셀은 R0-p(R1,CPE1), full-cell은 여기에 Wo1. **STEP3/STEP4 상태나 미분 연산자로부터 회로를 유도하지 않는다.**

`scripts/eis_drt_ica.py:53` 는 별도의 순방향 근사다. 앱은 `webapp/app.py:4218` 에서 i0/D_s 등을 별도 입력으로 받고, STEP3에서 주로 σ·두께·porosity를 가져온다. 실험 앵커 사용 옵션(`:4258`)은 C_dl/R_w를 공급하므로 같은 실험에 대한 독립 예측 검증으로 부를 수 없다.

CPE를 유효 C 한 개로 환산해도 스펙트럼 항등식이 아니다. R=100, Q=1e−4, α=.7 합성 예에서 peak의 −ImZ는 CPE **30.6400**, 환산한 이상 C는 **50.0000**이다.

적절한 문구: **"실험 EIS는 독립 등가회로로 적합하였다. 별도 순방향 회로는 시뮬레이션 수송계수와 명시된 계면·확산 가정을 입력으로 사용하였다."** 이를 STEP4의 충실한 선형응답이라고 주장하려면 실제 운전점의 선형화/주파수 응답과 회로를 대조하는 별도 작업이 필요하다.

### P2-L4-10 — EIS의 HF/DC 표지가 자기 스펙트럼 극한과 불일치한다

위치: `scripts/eis_drt_ica.py:83` · `:124` · `:129` · `:388`.

원함수에 σ_e=2 S/cm, σ_ion=2e−4 S/cm, L=72 µm, R_int=50, a_spec=20, R_w=30을 넣었다.

- 표지 R0_hf=**0.0036**, 실제 고주파 ReZ→**12.0036 Ω·cm²**. 상수 직렬 항으로 R_ion/3을 추가했기 때문이다.
- 표지 R_dc_total=**98.426745**, 실제 저주파 ReZ→**78.426745**. Wo의 전개는 R_w/(jωτ)+R_w/3+…이므로 +R_w를 유한 DC 저항처럼 더한 표지와 다르다.
- Wo의 허수부는 ω→0에서 발산한다. 엄밀한 복소 DC 임피던스 자체가 유한 98.4가 아니다.

**R0_hf라는 부분 파라미터와 실제 곡선 절편**, **소자 계수 합과 DC 응답**을 구분해야 한다. 이 R_dc 정의는 cycle-N helper/내보내기에도 쓰여 단순 사문서 문제가 아니다.

### P2-L4-11 — % 입력을 값 크기로 추측해 1%에서 EIS가 불연속이다

위치: `scripts/eis_drt_ica.py:92` · `webapp/app.py:4220` · `webapp/templates/eis.html:107`.

화면은 porosity(%)이고 API도 0.1–60을 허용한다. 함수는 값이 1 초과면 %, 아니면 fraction으로 해석한다.

- porosity=**1**: a_spec=1e−6, R_ct=**1.284628956×10⁸**.
- porosity=**1.000001**: a_spec=26.72999973, R_ct=**4.805944516**.
- 명시적 1%의 계산값은 R_ct=**4.805944467**이어야 한다.

API 단위 계약을 명시적으로 전달해야 한다. "값이 작으면 fraction"은 단위 식별 규칙이 아니다.

### se_material 내부 대조 — CONFIRMED 범위

`scripts/se_material.py:81` · `:117` 의 σ·T Arrhenius 식과 S/cm↔mS/cm 함수는 독립 식과 일치했다. None/25°C 기본은 각각 0.003/3.0과 bitwise 일치. Ea=.29/.41/.46, 30/45/60°C에서 대조했고, 25→60°C/Ea=.41의 계수는 **4.785100625**다.

문헌 앵커의 정당성을 새로 검증한 것은 아니다. "모듈 내부 일관성"과 "모든 소비자가 같은 규약을 쓴다"는 다르다. 후자는 grade의 bare 3.0 반례(L4-04)로 REFUTED다.

## 3. L4-c — 등급 의존성 지도

실제 AXES를 읽어 센 값은 **총 54축, __로 시작하는 파생 키 36개**다. "54개의 독립 증거"가 아니다.

| 파생 키 그룹 | 수 | 실제 상위 입력 | L1/L2 전파·해석 |
|---|---:|---|---|
| tau_lap_eff, tau_lap_bulk, constriction_overhead | 3 | φ_SE, 선택 σ, bulk σ, grain 상수 | L2 수송/면적/경계 및 L4 온도 정합. Dijkstra 아님 |
| asr_ionic, asr_electronic, asr_thermal, ASR_total, c_rate_capability, polarization, ASR_per_capacity | 7 | 두께, σ_i/σ_e/κ, 면용량 | σ 삼중항의 역수·합·정규화. L1/L2와 L4-01/02가 직접 전파 |
| constriction_R_fraction_pct, sigma_e_fracture_loss_pct | 2 | bulk resistance fraction, Stage-E 전후 전자 σ | L2-08의 분율, L1 면적/손상→L2 보정 |
| cut_fraction, bn_below_frac, bn_median_norm | 3 | viewer SE graph/접점 면적 | L2와 공유하는 경계·접촉 의미. 이번 L4-05/06/07 |
| vulnerable_pct, am_percolation_pct, electronic_active_pct | 3 | DEM/전자망 연결·활성 비율 | graph/endpoint 정의에 조건부 |
| frac_severe_force_pct, sigma_vm_cv_pct, cycle_stable_AM_pct | 3 | 파괴/응력, 두 활성 marginal | L1 손상 경로 및 L4-08 |
| wt_am_pct, commercial_composition, Q_gravimetric, Q_volumetric, Q_areal, Q_target_match | 6 | AM:SE 질량비, 밀도·175, porosity, 두께/목표 이름 | σ solver 직접 의존은 없음. porosity 세대·측정 정의 오염은 전파 |
| compaction_efficiency, volume_change_buffer | 2 | 같은 porosity | 독립 측정 두 개가 아니라 같은 수에 다른 점수 기준 |
| r_SE_um, lambda_eff, ps_ratio_band, bimodal_design | 4 | 입력 크기·비율·종류 | L1/L2 σ 직접 의존 없음 |
| am_am_short_risk_cn | 1 | AM–AM CN | CN의 재노출 |
| stage_e_available, validation_pass_pct | 2 | 키 존재, 자체 flag들 | 물리 관측량 아님 |

**validation flags의 실제 범위:** `scripts/run_network_full_corrections.py:539`–625는 ASR window, 심한 파괴 비율/최소 diversity, 전자 edge-drop≤.5, Stage-E 전자 σ≤1.05×baseline의 평가 가능한 값들을 묶는다. assessable이 하나도 없으면 overall은 False다. 그러나 이온/열의 ≤baseline flag와 fallback_fired는 기록되어도 이 네 개 conjunction에는 들어가지 않는다. τ의 관통, SI 면적, solver 수렴, 원자료 출처를 독립 검증하지도 않는다.

따라서 "정상 비퍼콜인데 trustworthy=True"는 물리 모순의 증명이 아니라 **trustworthy라는 이름이 그 성질을 보증하지 않음**을 뜻한다.

## 4. L5 반례와 통과한 부분

### P1-L5-01 — σ를 y에서 빼도 σ로 구조 코호트를 선별한다

위치: `scripts/design_performance_dataset.py:112` · `webapp/predictor_engine.py:269`.

build는 predictor_engine.load_training_data를 재사용한다. 거기서 raw sigma_full_mScm<0.01이면 **행 전체를 제외**한다. τ≤0/τ>8과 porosity>30도 전체 행 제외 조건이다. 구조 y의 개별 품질 판정이 아니다.

동일한 φ_SE=.3, φ_AM=.55, τ=1.5, 두께·CN·설계인자에 raw σ만 각각 결측/0/.009를 주면 세 행 모두 사라졌다. 양수 σ 사례는 남는다. 실제 build를 호출해도 같은 4/7행만 남았다.

무너지는 결론: "y가 구조량이므로 L2 수송 경로와 무관하게 코퍼스를 만들 수 있다." 정확한 표현은 **y 목록에는 σ가 없지만 selection은 σ에 조건부**다. 원고의 전체 DEM 설계영역/저퍼콜 영역 성능으로 일반화할 수 없다.

신규 LHS 수확기는 이 loader를 우회할 수 있지만, 기존 build에 그대로 합치면 다시 선별된다.

### P1-L5-02 — 구조 target의 0과 결측을 양수/관측 0으로 만든다

위치: `webapp/predictor_engine.py:314`, 특히 `:326`.

| 원 측정값 | ML coverage |
|---|---:|
| P=0%, S=0% | **0.20** |
| P=0%, S=40% | **0.40** |
| 둘 다 결측 | **0.20** |

양수 상 평균만 골라 평균내고, 비면 0.20을 넣는다. 정상 zero가 소실되고 존재 상의 가중도 달라진다. CN/AM-CN/percolation의 결측은 실제 0으로 채워졌다.

이는 앞 DESC의 "평균 정의를 고정하라"와 별개로 **그후 ML loader가 관측값을 실제로 변조하는 실행 경로**다.

### P1-L5-03 — 금지 target을 학습하고 추천에 쓴다

위치: `scripts/ml_design_structure.py:63` · `:847` · `webapp/structure_predictor.py:152` · `:252`.

합성 60행으로 use_porosity_pct만 충분히 예측 가능하게 만들었다. 실제 train 결과는 **USABLE, nested R²=.999998319**.

- status/predict 결과에서는 이 target을 숨겼다.
- surface는 명시적으로 거부했다.
- **suggest_batch(target=use_porosity_pct)는 error=None, 추천 2개**를 내놓았다.

높은 R²가 혼합상태 porosity를 정당화한다는 뜻이 아니다. 금지는 모든 소비자에서 동일해야 하며, 학습에서 제외했다는 주장도 현재 사실과 다르다.

### L5-a — 핵심 nested_cv는 CONFIRMED

위치: `scripts/ml_design_structure.py:258`, 기본 호출 `:838`.

합성 96행/4fold에서: 표준화 mu/sd는 outer train 72행으로 계산 · linear/quadratic/full family 재선택 12회 전부 train 72행만 · 항과 λ를 매 fold 재선택(λ .1/.1/.001/1.0) · 독립 outer loop 예측과 최대 차 **1.78e−15** · heldout y를 크게 바꿔도 자기 fold 예측/선택 차이 **0** · 고정 Φ의 hat-matrix LOO와 oracle 잔차 차 **2.00e−15**.

**median imputation은 이 경로에 없다.** L3 SAT의 전체 median 누출과 같은 결함으로 묶으면 틀린다.

단 inner hat LOO와 fit의 pi90_coverage는 선택된 특징/스케일을 조건으로 한 값이다. 이를 별도 nested된 구간 coverage라고 부를 수는 없다.

### P2-L5-04 — 닫힘 ε의 "폴드 밖 오차띠"는 누출되고 다른 학습기를 채점한다

위치: `scripts/ml_design_structure.py:783` · `:889` · `webapp/structure_predictor.py:169`.

(a) 두 φ는 OOF지만 C=mean(φ_SE+φ_AM+ε/100)은 **heldout ε까지 포함**한다. 합성 64행/4fold에서 heldout 16행의 ε만 +.8%p 바꾸면 두 φ 예측은 그대로인데 **그 heldout 유도 ε 예측이 +.2%p** 변한다. train-only C면 변화는 0.

(b) closure_test는 nested_cv 기본값 **full/False**를 쓰고 생산 train은 **auto/True**를 쓴다. 같은 C·fold를 고정한 대조에서도 유도 OOF 차이 최대 **.5208118964%p**, 잔차 SD는 **.7359459938 대 .7504307628%p**다.

두 값이 bundle에 부착되어 배포 φ 예측의 띠/"nested" 표지로 사용된다. **기본 nested 함수가 맞다는 사실이 이 파생 검증을 구제하지 못한다.**

### L5-b — 자유노브 곱 후보 제한 자체는 CONFIRMED

실제 `scripts/ml_design_structure.py:95` 호출에서 13 특징의 후보 총수는 **105→35**, 곱/제곱항은 **91→21**로 줄었다. free_products=True이면 두 인덱스가 모두 처음 6개 자유노브 범위다. **13개 선형항을 모두 남기는 것**은 이 계약 위반이 아니다.

### P2-L5-05 — 대조용 derived-products 산물이 일반 배포 모델로 들어간다

위치: `scripts/ml_design_structure.py:1356` · `:1431` · `webapp/structure_predictor.py:94`.

실제 main --derived-products --out을 합성 96행에 실행했다. 선택항 [[],[6,12]], free_products=False, nested R²=.9896169693, PI90 coverage=.8854166667, **USABLE**. 실제 load_bundle→predict_structure가 **ready=True**, "ML (ridge, nested-CV 검증)"으로 출력.

유도량 곱 모델의 높은 합성 성능이 잘못된 것은 아니다. **"대조 전용"이 출력 목적/생산 계약에 강제되지 않는 것**이 결함이다.

### P2-L5-06 — 모델은 같은데 UI가 다른 d_am을 보낸다

위치: `webapp/predictor_engine.py:300` · `webapp/templates/predictor.html:704` · `:1330` · `:1421`.

학습과 기존 getParams는 d_am=max(d_am_p,d_am_s). 구조 패널의 _structDesign은 **d_am_p만** 쓴다. P=3, S=8을 실제 JS에 주면 학습/기존 경로 d_am=8, 구조 패널 d_am=3, 동일 합성 φ 모델의 예측은 **.309999362 대 .210001029**.

**통과한 범위:** 동일한 6개 유한 노브에서는 P.derive_features와 M.derive_features의 13개 값이 모두 동일하고, 고정 모델의 직접 M.predict와 배포 S.predict 값/원 PI는 bitwise 동일했다. scaler 직렬화를 원인으로 지목하면 틀린다.

### P2-L5-07 — 비유한 입력이 정상 배포 표지로 반환된다

위치: `scripts/ml_design_structure.py:525` · `:540` · `:312` · `webapp/structure_predictor.py:145`.

합성 모델의 실제 predict_structure에 am_pct=NaN을 주면 ready=True, USABLE, any_extrapolation=False, value_out_of_bounds=False인데 **value와 leverage는 비유한**이다. NaN의 비교가 False여서 범위/외삽 가드를 통과한다.

load_corpus에서도 설계 결측 1행은 빠지지만, y 문자열 "nan"은 float 변환을 통과해 target 배열에 남았다(60행 중 X 59, y 58에 nonfinite 1).

## 5. L5-d — 실제 y와 오염 경로

목록은 `scripts/ml_design_structure.py:63` 의 실제 12개다. σ_ion/σ_el/σ_th 열을 합성 CSV에 같이 넣어도 load_corpus의 y에는 들어가지 않았다. 이 부분은 CONFIRMED다.

| y | 이 build에서 들어오는 실제 값 | 직접/간접 의존성 |
|---|---|---|
| φ_SE, φ_AM | full_metrics의 해당 값, 결측 기본 0 | DEM 기하량. L2 σ 자체로 계산하지 않지만 **σ/τ 전역 행 필터**를 거침 |
| se_of_solid_pct | 100φ_SE/(φ_SE+φ_AM) | 두 φ의 대수 함수. 독립 관측 아님 |
| cn, am_cn, f_perc | se_se_cn, am_am_cn, percolation_pct; 결측 기본 0 | 접촉/위상 정의, 경계 및 위 필터. 정상0과 미측정 구분 소실 |
| coverage | bare coverage_AM_P/S/AM_mean 중 양수만 평균, 비면 .20 | legacy DEM contact-area 채널. **Physics suffix/Stage-E coverage를 직접 읽지는 않는다.** 그러나 L5-02 재정의/0 변조 |
| tau | tortuosity_mean, 키 없을 때 tortuosity_recommended | legacy Dijkstra 계열. Laplace getter가 아님 |
| thickness | thickness_um | 기하·벽 위치 정의. σ 필터로 행이 사라짐 |
| use_porosity_pct | DEM/MPM 판정 혼합 또는 curated 값 | 기존 DESC-08 + 이번 L5-03 |
| mpm_plastic_gain_AM_P_tabor_pp | MPM plastic coverage−rigid coverage | 별도 MPM 경로. LHS DEM-only 7타깃이 아님 |
| mpm_dg_mean | mpm_metrics의 dg_mean | 별도 MPM 경로. 미실행은 미측정이지 관측0 아님 |

중요한 구분: **L1 Physics cap의 SI 버그를 고치면 이 legacy coverage target이 무조건 직접 바뀐다고 말할 수 없다.** 소비 키가 다르다. 또 L3 스케일링 예측 σ가 이 12 y로 직접 들어가는 경로를 확인한 것은 아니다. 대신 L2 raw σ를 쓰는 **행 선택**은 실행으로 확인했다.

### LHS 130과 병렬 진행할 수 있는 범위

**원 dump의 독립 수확·정의 검사·탐색은 웹앱 수정과 병렬로 진행할 수 있다. 현행 build로 291에 append해 최종 학습하는 것은 안 된다.**

필요한 최소 분리:

1. legacy σ/τ row filter를 재사용하지 않는, frozen ID 전수의 상태 원장.
2. 등록 7열→새 모델 target을 옮기는 명시적 adapter. 실제로 7개 등록 이름을 현행 load_corpus에 줬더니 **φ 두 개만 y로 읽었다**. 나머지는 자동 alias가 없다.
3. 전체-AM coverage는 입자수/원 per-particle 집계 규약으로 옮긴다.
4. ε_sphere RECORD_ONLY는 닫힘 확인용이다. 별도의 독립 회귀 y로 늘리지 않는다.
5. no-percolation에서 정의되지 않은 τ는 0/유한값으로 채우지 않는다.
6. 다음 §6의 주기 τ 결함부터 고친 뒤 그 열을 사용한다. 실제 130 dump 중 표본 end-to-end 대조는 아직 필요하다.
7. train/test 선정, 누락·미완주 처리, 전처리 및 새 성능 보고는 결과를 보고 선택하지 않도록 고정한다.

## 6. 별건 1 — LHS 수확기 제한 리뷰

### P1-HARV-01 — 주기 접촉과 비주기 경로 길이를 섞어 τ가 좌표 원점에 의존한다

위치: `scripts/lhs_descriptor_harvest.py:325` · `:358`, 최소영상 접촉 계산 `scripts/lhs_perc_extract.py:217`.

합성 상자 Lx=Ly=10. SE 5개, r=.55, z=1…5, x=.1/9.9 교대, y=5. 인접 네 쌍은 xy minimum-image 거리 √(1²+.2²)로 접촉한다.

| 같은 주기 침대의 표현 | 함수 τ | 상태 |
|---|---:|---|
| x=.1/9.9 교대 | **9.850888285** | OK |
| 모두 x+5, mod 10 | **1.019803903** | OK |
| minimum-image 독립 계산 | **1.019803903** | 참조 |

**평행이동만으로 9.6596배** 바뀐다. _pairs_within은 주기 경계를 쓰는데 graph weight와 최종 path sum은 raw 좌표 차를 쓰기 때문이다. area/물성/수렴/랜덤 샘플 문제가 아니다. 두 단계 모두 같은 minimum-image edge length를 써야 한다.

실제 수확기의 함수 자체를 실행했으며, 130 dump를 본 것은 아니다. 따라서 현재 τ 열의 학습 사용은 HOLD다.

### fallback·슬래브·area_channel 답

- **CONFIRMED:** source/slab가 없을 때 임의 노드를 source로 승격하는 경로는 없고, 후보 쌍을 같은 연결성분에서만 만든다(`:332`). 이전 무리한 유한 τ 발급과 방향은 다르다.
- **단, known-wall 판정과 동치는 아니다:** τ 함수는 입자 외연의 z 범위와 r_SE,max를 사용하고, harvest가 요구한 plate_z를 **τ 함수에 넘기지 않는다**(`:409`). 벽과 떨어진 고체 덩어리도 자체 점유 영역에서의 τ를 가질 수 있다. "점유 고체 영역의 경로 descriptor"라는 등록은 방어 가능하지만 "두 실제 전극 벽 사이 관통"의 증서는 아니다.
- **area_channel은 필요한 정정이다:** c_cpl22에서 읽은 geometric area이며 Hertz 탄성 면적이 아니라는 설명은 코드와 맞는다. 기존 *_hertz_pct 열은 호환 별칭임을 소비자에도 강제해야 한다. 문자열을 옮겼다는 사실만으로 구판 학습기와의 의미 일치가 확보되지는 않는다.
- 면적 합산은 AM 표면에서 AM–AM 접촉 면적을 뺀 분모, SE 접촉 면적의 분자, 100% cap을 사용한다. invalid 분모 제외/상 absent 상태까지 계약에 남겨야 한다. **실제 덤프 c_cpl22의 출처/값 검증은 별도 미완료**다.

이는 수확기 전체 GO가 아니라 질문한 두 경로에 대한 제한 리뷰다.

## 7. 별건 2 — Phase A Q7

**현재 제출된 TSV만으로는 수렴 증서 GO가 아니다. 다만 "팔별 정확한 잔차를 못 복구하면 무조건 32팔 재실행"이라는 강한 결론도 아직 정당하지 않다.**

실제 보존 TSV에서 다시 센 값: 32행, n_dof 32개 유일, 잔차 표기 9.8e−9…1.0e−8, wall 합 **81,463 s=22.628611 h**. 표 SHA256은 **3094994100aef98eb0d88c47ec032db562d84ec4f5800a101da92a23c095c2e8**. 이는 **TSV의 해시**이지 원 로그의 해시/완전성 증명이 아니다.

`scripts/mpm_webapp_payload.py:1875` 는 resid를 .1e로 출력한다. 보수적으로 가장 큰 표시 1.0e−8의 상단을 **1.05e−8**로 잡아도 `scripts/run_contract.py:29` 의 실제 한계 **1e−6**보다 충분히 작다. 다른 flag가 0/False로 적격하다는 조건에서 conv_ok(0,False,1.05e−8)는 통과한다. 따라서 **수치 반올림은 이번 blocker가 아니다.**

남은 것은 집합 증명이다:

> 로그 줄 ↔ 필수 32팔의 **bijection(누락·중복 없는 일대일 대응)이 이미 증명**된다면, 모든 줄의 상한이 같으므로 어느 permutation에서도 잔차 게이트는 같다.

이 조건부 논증은 맞다. 그러나 32줄/32 unique dof만으로 bijection은 성립하지 않는다. 반례로 팔0…30의 로그 + 팔0의 재시도 로그 1개도 32줄이다. 재시도에서 입력/조건이 달라지면 dof도 달라질 수 있다. 팔31의 인증은 빠진다. **그 일이 실제 있었다는 주장이 아니라 현재 표가 그 가능성을 배제하지 못한다는 뜻**이다.

권고 순서:

1. 원 로그 전수·receipt·restart/SKIP 내역·job 기록 등으로 대상 코호트, 검증한 코드/입력, 성공한 solves와 최종 팔의 **완전한 대응**을 복구한다. 팔별 정확한 잔차 숫자까지 알아야 할 필요는 없다.
2. 이 대응과 cg_info=0/unconverged=False 등 나머지 conjunction을 입증하면, 별도 batch certificate에 residual_upper_bound·출처·수집 규칙·적용 32 ID를 담는 것은 가능하다. **per-arm cg_resid에 관측한 척 수치를 복사하지 않는다.** 현행 conv_ok는 scalar 계약이므로 typed batch certificate를 받아들이는 변경/동등성 시험은 별도 필요하다.
3. 대응을 끝내 입증하지 못한 팔은 UNKNOWN이다. 미인증 부분을 재실행하고, 어느 팔인지도 구분할 수 없다면 그때 32팔 전체가 재실행 대상이 된다.
4. --show-results는 **이미 가려져 기록된 과거 로그 문자열을 복원하지 못한다**. 새로 실행해 값을 보이는 것은 과거 로그 귀속의 복구가 아니다.

원격 kgy의 원 로그·운영 기록은 이번에 접근하지 않았으므로, 위 1의 복구 가능성은 미판정이다.

## 8. 처방 경계 — 고칠 수 있는 것 / 다른 측정이 필요한 것

**기존 구성 안에서 고칠 수 있다:** canonical 상태/키 조회, 정상0·미측정 분리, source/검증 gate 공통화, audit 타입·conjunction·분모, 진단 dedup/metadata, UI feature 공통화, 금지 target의 모든 소비자 차단, nested closure fold-local화, periodic edge 길이.

**숫자 버그 패치만으로 주장할 수 없는 것:**

- marginal-product를 실제 cycle-stable 입자율로 부르기 → 입자별 교집합 관측 또는 명시적 독립성 proxy가 필요.
- 등가회로 역적합을 STEP4 선형응답 유도로 부르기 → 별도 선형응답/주파수 모델 검증이 필요.
- 36 파생축을 36 독립 물리 증거로 부르기 → 의존성을 드러내고 점수의 해석 범위를 정해야 함.
- 선택된 legacy 코호트의 성능을 모든 130 설계점 성능으로 부르기 → 대상 모집단·결측/비퍼콜 처리·검증 계획이 필요.

L1/L2의 면적/저항 모델 결정은 여전히 선행된다. 이번에 코드 소비자들을 고친다고 기존 물리와 등록 스케일링법칙이 검증되는 것은 아니다. **새 target 값/코호트/검증을 사용한 재적합과 원고 숫자 갱신은 별도 사전등록·승인 사안**이다.

검토 원본은 detached e68d2b23a…이며 최종 git status에 변경이 없었다. **L4·L5는 모두 이번 회신으로 판정했고, 별건 둘은 위에 명시한 제한까지 답했다.**

---

## 부록 — 이 리포에서의 독립 재현 · 그리고 즉시 수정 (2026-09-13, claude)

### P1-HARV-01 — **내 코드였다.  재현하고 같은 날 고쳤다.**

판정문의 fixture 를 그대로 `lhs_descriptor_harvest.tortuosity_se` 에 넣었다:

```
x = .1/9.9 교대        τ_mean = 9.850888284819803   status=OK
모두 x+5 (mod 10)      τ_mean = 1.0198039027185568  status=OK
minimum-image 독립계산  τ      = 1.019803903         (판정문과 일치)
```
⇒ **평행이동만으로 9.6596배**.  원인도 판정문 그대로다 — `_pairs_within` 은 xy 주기
minimum-image 로 이웃을 찾는데 내가 **간선 가중치와 경로 길이를 raw 좌표차**로 계산했다.

**수정** (규율 ②: 회귀를 먼저 넣고 고쳤다):
- `_mi_dist(p, q, lx, ly)` 신설 — xy 최소영상 · z 개방.
- 간선 `distance` 와 경로 길이 합을 **둘 다** 그것으로 교체.
- docstring §τ 규약에 *"간선 가중치와 경로 길이는 xy 최소영상 — 쌍 찾기와 같은 규약"* 명시.
- selftest **⑬a** 신설: 평행이동 불변 + minimum-image 해석값(1.019803903) 일치.
  수정 전이면 9.85 ≠ 1.02 로 **반드시 깨진다**.

selftest 31/31.

### 받아들인 한정 — 내 수확기에 대해

- ★ *"fallback source 승격 없음 · 같은 성분 안에서만 쌍"* 은 **CONFIRMED**.
- ⚠ **그러나 known-wall 판정과 동치가 아니다**: τ 함수가 `plate_z` 를 **안 받는다**.
  ⇒ 벽과 떨어진 고체 덩어리도 자기 점유 영역의 τ 를 갖는다.  **"점유 고체 영역의 경로
  descriptor" 로는 방어 가능하지만 "두 실제 전극 벽 사이 관통" 의 증서가 아니다.**
  ⬜ 미수정 — 이름/경계를 그렇게 보존하거나 `plate_z` 를 넘기도록 고쳐야 한다.
- ⚠ `area_channel` 은 *"필요한 정정"* 이지만 **소비자에게도 강제**해야 하고, 문자열을 옮긴
  것만으로 구판 학습기와 의미가 일치하지는 않는다.

### ★★ L5-d 의 답 — 내 질문에 대한 정면 답

내가 물은 *"LHS 130 을 webapp 수정과 병렬로 갈 수 있나"* 의 답:

> **원 dump 의 독립 수확·정의 검사·탐색은 병렬 가능.
> 현행 build 로 291 에 append 해 최종 학습하는 것은 안 된다.**

★ σ 가 y 에 없다는 내 이해는 **CONFIRMED** 다 (12 y 에 σ 열이 없다).
⛔ 그러나 `design_performance_dataset.py:112` → `predictor_engine.py:269` 가
**raw `sigma_full_mScm < 0.01` 이면 행 전체를 버린다** (τ≤0/τ>8, porosity>30 도 동일).
⇒ **y 목록에는 σ 가 없지만 selection 은 σ 에 조건부**다.  내 수확기는 그 loader 를
우회하지만, 기존 build 에 합치면 **다시 선별된다**.

⚠ 그리고 **등록 7열을 현행 `load_corpus` 에 주면 φ 둘만 y 로 읽힌다** — 나머지는 자동
alias 가 없다.  adapter 가 필요하다.

### 아직 재현하지 않은 것

`L4-01`~`L4-11` · `L5-01`~`L5-07` 은 합성 레코드와 실제 grade/audit/train 호출이 필요해
이 자리에서 돌리지 않았다.  소스 위치는 전부 실재를 확인했다.
