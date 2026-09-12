# Codex 적대 리뷰 판정 — LHS 130 DEM 디스크립터 추출 경로 (2026-09-13)

> 요청서 = `docs/reviews/codex_request_descriptor_harvest_20260913.md`
> 기준 스냅샷 = `be79f0827ea253ffb027b584e37067b60b03aa7c` · 대상 브랜치
> `claude/sdcp-dem-manuscript-si-pqwtv8`.
>
> ⚠ **아래는 받은 판정문 전문이다.**  요약·재서술하지 않는다 (규율 ③: 한정어가 값이다).
> 링크의 `C:/Users/...` 경로는 Codex 검토 workspace 의 사본이고, 우리 리포의 대응 파일은
> 같은 상대경로(`scripts/…`, `webapp/…`, `docs/…`)에 있다.
>
> ★ **독립 재현 = 완료** (이 리포에서, 아래 §부록).  세 P1 전부 우리 트리에서 재현됐다.

---

# LHS 130 DEM 디스크립터 추출 경로 — 독립 리뷰

검토일: 2026-09-13  
고정 스냅샷: `be79f0827ea253ffb027b584e37067b60b03aa7c`  
브랜치: `claude/sdcp-dem-manuscript-si-pqwtv8`

## 결론

**현재 웹앱 출력물을 그대로 일곱 열에 매핑해 학습 코퍼스로 확정하는 것은 HOLD.** 설계 좌표·고정 인자를 재심한 것이 아니다. 추출 계측기에 새 P1 3건을 재현했다.

1. **P1-DESC-01:** 경로 계산이 실패하면, 기하만으로 계산 가능한 `phi_se`·`phi_am`도 저장되지 않는다.
2. **P1-DESC-02:** SE 관통률 0인 그래프에 유한 `τ=1`을 부여한다. 반대로 관통 경로가 존재해도 샘플링 때문에 τ가 결측될 수 있다.
3. **P1-DESC-03:** Physics 피복률의 5 nm 두께와 확대 DEM 길이를 혼용한다. “큰 Δ는 정의 차이뿐이며 단위 문제는 없다”는 주장은 반증된다. **이 오류가 Hertz 전용 타깃까지 바꾼다는 뜻은 아니다.**

현재 설계 CSV의 130×39, 세 블록 100/15/15, BELOW 44, finite flag 빈 행 62는 재계산했다. **일곱 측정 열은 모두 130행 전부 빈칸**이다. 덤프 130개·현재 작업 로그·스크린샷 원자료는 제공되지 않았다. 따라서 실제 배치의 결함 발생 건수, 현재 완주 수, 화면 Δ% 원인을 확인했다고 주장하지 않는다.

문서는 등록 의도를 판독하는 데만 사용했다. 계산의 타당성은 소스·합성 입력의 실제 함수/CLI 실행·저장 CSV의 독립 재계산으로 검사했다. 원본 소스·CSV·두 원장은 수정하지 않았다.

## 1. 먼저 호출 경로를 정정한다

요청서의 시작점 `app.py:2878 → network_conductivity` 앞에 **타깃의 주 생산자**가 빠져 있다.

1. [app.py:3240](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/webapp/app.py:3240): atom/contact/mesh/input → **parse_liggghts.py** → atoms.csv, contacts.csv, mesh_info.json, input_params.json.
2. [app.py:3271](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/webapp/app.py:3271): **analyze_contacts_bimodal.py → analyze_contacts.py → dem_analysis_core.run_full_analysis**. Standard 분기도 같은 core를 사용한다. 여기서 구 공극률·상별 피복률·SE 그래프·Dijkstra τ를 계산하고 `full_metrics.json`을 만든다.
3. [app.py:3292](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/webapp/app.py:3292): **coverage_physics_vs_hertzian.py**가 별도 Physics/rough 피복률과 `coverage_per_am.csv`를 만든다.
4. [app.py:3304](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/webapp/app.py:3304): network baseline 두 mode → `full_metrics`에 σ 투영 → Stage E full corrections. **Hertz 디스크립터의 주 생산 단계가 아니다.**
5. [app.py:3309](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/webapp/app.py:3309): **recompute_porosity_dual.py**. 기존 sphere 공극률은 보존하고 union 계열 값을 보충한다.
6. grade_engine·화면 변환은 이미 계산한 값/파생량의 소비자다. 등급용 “effective” 필드나 화면 표를 일곱 등록 타깃의 정본으로 삼으면 안 된다.

검증 범위: parser→contact analyzer는 합성 dump로 CLI 실행했다. coverage·graph·network·ML loader는 실제 함수를 호출했다. **웹앱의 전체 UI/Stage E 경로를 실제 130 dump로 종단 실행한 것은 아니다.**

## 2. Q1 — 일곱 라벨과 실제 계산량

기호: (V_B=L_xL_yH), (V_i=4πr_i^3/3). 길이·반지름·벽은 **같은 프레임, 같은 DEM 단위**여야 한다. 아래 φ는 전극 전체 부피 분율이며 고체 내부 조성분율이나 질량분율이 아니다.

| 등록 라벨 | 현행 실제 계산/필드 | 판정과 수확 규약 |
|---|---|---|
| `phi_se` | (Σ_{i∈SE}V_i/V_B). [core:934](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/dem_analysis_core.py:934), [저장:430](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/analyze_contacts.py:430) | **정의는 맞지만 항상 생산된다는 주장은 REFUTED.** τ 없으면 필드도 없다. dump에서 독립 계산해야 한다. |
| `phi_am` | 현행은 (1-φ_{SE}-ε_{sphere}/100). [저장:434](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/analyze_contacts.py:434) | AM+SE만 존재하고 같은 상자일 때 (Σ_{AM}V_i/V_B)와 같다. φ_SE와 함께 누락된다. 다른 상이 있으면 “나머지 전부=AM”이므로 일반화 불가. |
| `coverage_AM_P_hertz_pct` | `coverage_AM_P_mean`: 아래 (c_i^H)의 **P 입자별 산술평균**. [core:172](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/dem_analysis_core.py:172) | **정의 조건부 CONFIRMED.** DEM contact_area 기반, AM–AM 차감 분모, 100% cap, shape factor OFF. 단순 전체 구 표면 피복률로 쓰면 틀림. P가 없으면 N/A. |
| `coverage_AM_S_hertz_pct` | `coverage_AM_S_mean`: 동일 계산의 S 입자별 평균. [저장:393](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/analyze_contacts.py:393) | P와 동일. 없는 S=0이 아니다. 존재하지만 SE 접촉이 없으면 유효 0이다. |
| `coverage_AM_total_hertz_pct` | 전체 AM 입자별 평균 ( (N_PC_P+N_SC_S)/(N_P+N_S) ) | **기존 bimodal JSON에 대응 키가 항상 있다는 주장은 REFUTED.** core는 상 라벨별만 반환하고, 후속 비교기는 전체 **Physics** 키만 별도 추가한다. [core:208](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/dem_analysis_core.py:208), [비교기:362](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/coverage_physics_vs_hertzian.py:362). 실측 입자수와 상별 값으로 유도하거나 per-particle 원자료를 재집계. |
| `tortuosity_dijkstra_SE` | SE contact graph, x/y 최소상 거리 가중 최단경로의 중심거리 합 / **경로 양 끝점 z 거리**. 최대 200 후보쌍, (1≤τ<20)만 집계. mean·median·recommended 세 키. [core:473](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/dem_analysis_core.py:473) | **Dijkstra 계열은 CONFIRMED, “동일한 관통 경로량 한 가지”는 REFUTED.** 비관통 fallback·샘플 누락·통계량 전환이 있다. 등록 이름만으로 mean/median이 정해지지 않는다. |
| `porosity_sphere_pct_RECORD_ONLY` | (100(1-Σ_iV_i/V_B)), `porosity`/sphere-sum. 구 겹침을 빼지 않는다. [core:64](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/dem_analysis_core.py:64) | **기록용 CONFIRMED.** 현재 등록에서는 독립 회귀 타깃이 아니다. closure로 유도·검산한다. union/MPM 값을 대신 넣지 않는다. |

### Hertz에서 “접촉면적 기준”의 정확한 뜻

```text
F_i = 4πr_i² − Σ(AM–AM의 LIGGGHTS 접촉면적)
c_i = min(100, 100 × Σ(AM–SE 접촉면적) / F_i)   [F_i > 0]
c_i = 0                                       [F_i ≤ 0: 현행의 문제 처리]
```

실제 분자는 파서가 받은 **LIGGGHTS `contact_area`**다. 이 분석기가 (πR^*δ)를 독립 재계산한 것이 아니다. 어떤 DEM contact-area 출력 규약을 썼는지도 보존해야 한다.

반례: 전체 구 표면의 25%가 AM–AM 접촉, 25%가 AM–SE 접촉이면 출력은 **25%가 아니라 33.3333%**. 두 항 모두 면적이라 현재 scale=1000에서 단위 상쇄는 성립한다. 그러나 분모 정의가 다르다.

전체 평균 반례: P 1개·10%, S 3개·각90%이면 **전체 70%**다. 상 평균의 평균은 50%, 총면적비는 30%, ps 질량가중은 18%다. 네 개는 서로 다른 양이다.

### Physics와 Δ — 정의 차이와 단위 결함이 함께 있다

Raw Hertz/Physics는 [비교기:282](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/coverage_physics_vs_hertzian.py:282)의 **동일 free-surface 분모**를 쓴다. Physics만 분자가 Tabor/volume/geometry 연산자 결과로 바뀐다. rough는 표면 shape factor까지 적용한 제3의 값이다.

[비교기:326](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/coverage_physics_vs_hertzian.py:326)의 Δ는 ((C_P/C_H-1)×100). 따라서 +281.6/+299.4/+270.3%는 각각 **3.816/3.994/3.703배**다. 이 비율만으로 단위 오류 유무를 판정할 수 없다.

**P1-DESC-03: 실제 단위 반례.**

- [coverage:206](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/coverage_physics_vs_hertzian.py:206): 확대 DEM δ·r를 helper에 그대로 전달.
- [plastic_coverage:50](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/plastic_coverage.py:50): 두께 `H_FILM_MIN=5e-9` m.
- [plastic_coverage:284](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/plastic_coverage.py:284): 확대된 길이의 세제곱 (V_{overlap})을 미확대 5 nm로 나눈다.

같은 물리 접촉(AM/SE 반경 0.5 μm, δ/R*=0.05)을 실제 함수에 넣은 결과:

| 조건 | Hertz % | Physics % | Δ % |
|---|---:|---:|---:|
| 현행 scale=1000 | 0.312500 | 0.782064561 | +150.260660 |
| 같은 입력, 두께만 동일 DEM 단위 5e-6 m로 환산한 대조 | 0.312500 | 0.384114583 | +22.916667 |

두 번째는 **메모리 안 대조만** 했고 소스는 수정하지 않았다. 물리 SI 좌표로 직접 호출해도 두 번째와 일치한다. cap 선택은 Tabor→volume, Physics 면적 차이는 **2.036019배**다.

무너지는 결론은 **“Physics 비교의 Δ가 의도한 정의 차이만 나타낸다”**이다. Hertz 등록 타깃을 Physics로 대체하지 않는다면 이 특정 오류는 Hertz 타깃에 전이되지 않는다. **스크린샷 세 수치의 원인이 이 오류라고는 단정하지 않는다.**

### Dijkstra와 Laplace는 대체할 수 없다

현행 Laplace 계열은 (τ_{eff}=√(φ_{SE}σ_{grain}/σ_{full})), bulk-only는 σ_full을 σ_bulk로 바꾼 값이다. 이는 기하 최단경로가 아니라 전도도에서 역산한 양이다. 같은 그래프에서 접촉저항만 바꾸면 **Dijkstra=1 그대로, τ_Laplace,eff=1.00499→3.17805**가 된다.

또 “constriction overhead”도 두 소비자가 다르다.

- [app.py:2503](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/webapp/app.py:2503): (τ_{eff}/τ_{Dijkstra}).
- [grade_engine.py:893](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/grade_engine.py:893): (τ_{eff}/τ_{bulk}). numerator에는 Stage-E Physics 우선 선택도 있다.

앞의 비는 무접촉저항 입력에서도 **2**가 될 수 있다. 뒤의 비는 동일 모델·동일 조건이면 (√(R_{full}/R_{bulk}))이지 저항 배율 자체가 아니다. **둘 다 등록 Dijkstra 열에 넣지 않는다.** +156.4%는 원자료가 없어 미검증이다.

### 추정 φ와 실측 φ

[generator:237](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/lhs_design_dataset.py:237)은 밀도·질량 조성에 고정 `EPS_TYPICAL=0.183`을 넣어 `phi_*_est`를 만든다. 수확기는 이를 복사하지 말고 **최종 dump의 실제 상별 구 부피 / 실제 상자·벽 부피**를 `phi_*`에 채워야 한다. 추정과 실측 열을 둘 다 보관하고 차이를 진단한다.

## 3. 새 직접 반례와 추가 수확 게이트

### P1-DESC-01 — τ 때문에 φ 두 개가 사라짐

[core:941](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/dem_analysis_core.py:941)의 τ 가드가 `effective_conductivity=None`을 반환하면, [analyze_contacts:430](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/analyze_contacts.py:430)은 φ_SE·φ_AM까지 쓰지 않는다.

합성 atom/contact/mesh → parser → analyzer 실행 결과:

- 두 실행 모두 **rc=0**.
- 원 구 부피에서 계산한 φ_SE=φ_AM=**0.0001675516082**.
- sphere 공극률 **99.9664896784%**는 정상 저장.
- `tortuosity_mean=null`, `percolation_pct=0`.
- **phi_se, phi_am은 키 자체가 없다.**
- [NET_MERGE_KEYS:83](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/webapp/pipeline_service.py:83)에 φ가 없으므로 후속 network merge도 이를 복구하지 않는다.

이는 극소 합성 입력의 계측기 단위시험이다. 실제 130개에서 이 공극률/누락 수를 관측했다는 뜻은 아니다. 반증의 핵심은 **기하량이 경로 계산 성공 여부에 종속됨**이다. 완전행 삭제를 하면 연결성이 약한 배치의 구조 타깃이 함께 탈락할 수 있다.

### P1-DESC-02 — 비관통 τ와 샘플링 실패를 혼합

[core:503](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/dem_analysis_core.py:503)은 관통 bottom source가 없으면 위판 연결 성분의 최저 z를 새 source로 만든다.

실제 graph 함수의 반례:

- 아래판 접촉 3개는 고립, 위쪽 직선 기둥 3개는 아래판에 연결되지 않음.
- **percolation_pct=0인데 τmean=τrecommended=1, 유효 표본 3**.
- 동일 graph의 resistor network는 σ를 계산하지 못함.

반대 방향도 있다. [core:517](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/dem_analysis_core.py:517)은 서로 다른 연결성분의 무경로 쌍까지 200개 예산에 포함한다. **직선 관통 성분 200개, 모든 유효 τ=1인 그래프도 샘플 0개→τ=None**이 된다.

따라서 유한 τ≠관통 보장이고, τ=None≠미퍼콜 보장이다. 원자료의 관통 판정과 `NO_VALID_SAMPLED_PAIR`/계산 실패를 별도 보존해야 한다.

### P2 — 같은 이름 안의 통계량·경계·절단

- [core:545](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/dem_analysis_core.py:545): 경로 [1,1,10] → mean **4**, recommended **1**. 새 수확기가 임의로 recommended를 고르면 기존 mean과 다른 target이 된다.
- [core:533](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/dem_analysis_core.py:533): [1,20.024984] → 긴 경로 삭제 후 mean **1**. 무절단 평균 10.512492와 다름.
- [core:404](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/dem_analysis_core.py:404): own-radius×2 → 벽높이 15/85% → 관측 SE z범위 15/85%로 경계를 바꿈. 실제 양판 접촉 0인 구조도 마지막 fallback에서 관통 100%, τ=1을 낸다.

기존 결과를 어떤 통계량/경계로 부를지 명시하고, legacy 값과 새로 교정한 값을 같은 컬럼에 섞지 않아야 한다. **설계를 다시 뽑으라는 요구가 아니다.**

### P2 — 0, N/A, invalid를 분리해야 함

- 존재 P·SE 접촉 없음 → P coverage **0**. 없는 S → 키 없음: 이것은 **N/A**.
- [core:215](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/dem_analysis_core.py:215): AM–AM 면적합으로 free surface≤0이 되어도 coverage **0**을 돌려준다. 실제 무접촉과 분모 붕괴가 섞인다. cap 횟수·free≤0 횟수를 함께 검사해야 한다.
- [analyze_contacts:162](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/analyze_contacts.py:162): mono 입력에 없는 type을 고정 bimodal map으로 남기면 `np.min(empty)`에서 **rc=1**. 상 존재를 확인한 map이 필요하다.
- CSV-only/일반 AM에서 P/S를 직경으로 추정하는 UI fallback을 정본으로 쓰지 말고, 봉인 설계의 block·실제 type/radius/count를 대조한다. **130 설계의 현재 직경 범위가 radius>0.004 heuristic을 실제로 넘나든다는 결함을 주장하는 것은 아니다.**

### P2 — 덤프를 읽었다고 같은 최종 프레임인 것은 아님

[parse_liggghts.py:243](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/parse_liggghts.py:243)의 파일 선택은 atom/contact/mesh 각 종류의 최신 파일을 독립 선택한다. 합성 `atom_100 + contact_200 + mesh_100`을 **rc=0**으로 받았다. 다중 프레임 파일은 행을 이어 붙이고, atom loader는 ID 사전으로 마지막 값을 쓰는 반면 contact는 중복될 수 있다.

[core:110](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/dem_analysis_core.py:110)은 mesh가 없으면 최고 입자 중심으로 벽을 추정한다. 합성 실제 벽 .020, 최고 중심 .019이면 부피 분율은 **5.263% 상대차**가 생긴다.

130 배치가 이런 입력을 가진다고 단정하지 않는다. 새 수확 계약은 **같은 최종 timestep, 상자/벽 실물, type map, 완료 압력, 원파일 해시**를 검사해야 한다. 기본값·추정값으로 조용히 메우면 안 된다.

## 4. Q2·Q4 — 291 코퍼스와 그대로 합치면 안 됨

현재 130 설계 자체는 mono의 없는 상 직경을 빈칸으로 유지하고, `d_am_max_um`은 존재상 max와 130/130 일치했다. 그러나 **수확기가 아직 없으므로 NaN을 끝까지 보존한다는 보증은 없다.**

기존 [291 corpus](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/docs/data/design_performance_corpus.csv)의 실제 저장값을 다시 읽고, [ML loader:540](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/ml_design_structure.py:540)를 호출했다.

- `d_am=0` **40개 모두 학습 입력에 수용**된다. ps=0은 36개, ps=1은 2개, ps=.7은 2개다. “ps=0만 고치기”는 충분하지 않다.
- 추가 **18행**은 `d_am=12`인데 기록된 존재상은 AM_S 반경2 μm뿐이다. CSV 2행이 최소 예: `ps=0, fm_n_AM_P 빈칸, fm_n_AM_S=1555, fm_r_AM_S=2`. **존재상 메타자료와 특징의 불일치**는 확정. 원 dump를 확인한 실측 지름이라고 확대하지 않는다.
- [predictor_engine:231](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/webapp/predictor_engine.py:231)의 입력 반경 max 경로는 존재하지 않는 상의 입력 반경까지 포함할 수 있다. 신규 존재상 max와 동일 정의인지 재구축해야 한다.
- `phi_se+phi_am+porosity/100−1`: 291행 최대 절댓값 **2.22e−16**.
- 같은 식에 `use_porosity_pct`를 넣은 235행: 최대 **10.816%p**, 잔차 SD **2.975%p**. ε SD **3.823%p**의 **77.82%**다. MPM/DEM 상태 혼합이 저장 파일에 남아 있다.

이들은 기존 사고의 **현행 재발/잔존 확인**이지 모두 이번에 새로 발견한 설계 결함은 아니다. `use_porosity_pct`, Physics coverage, generic d_am을 그대로 append 키로 쓰면 §O의 오염을 다시 만든다.

**DEM-only 130에는 MPM·첨가제 단계가 필요 없다.** φ/구 공극률/DEM 접촉 피복률/SE graph를 원 dump에서 산출할 수 있다. 다만 291 혼합 코퍼스의 “대표값 선택” 규칙을 복사하지 말 것:

- 실제 첨가제 없음: 수량/질량 등 해당 변수는 **확인된 0**.
- MPM을 안 함: MPM 결과는 **NOT_RUN/N/A**이지 0% porosity가 아님.
- 없는 AM 하위상: 직경·해당 coverage **N/A**, 상 개수는 **0**.
- 물리적 미퍼콜, 샘플 실패, 입력 누락, 추출 예외는 다른 상태.
- 한 타깃이 미정의라고 φ·coverage 등 나머지 타깃이 있는 행 전체를 삭제하지 않는다.

## 5. Q3 — 일곱 열 보관과 일곱 독립 회귀는 다르다

**정의 종속 1:**

```text
ε_{sphere}(%)=100(1-φ_{SE}-φ_{AM})
```

AM+SE만, 동일 프레임/상자일 때의 관계다. corpus DEM 열에서 부동소수 오차 수준으로 재현했다. 새 학습에서 φ 둘과 ε를 세 독립 응답처럼 세지 않는다.

**정의 종속 2:**

```text
C_{total}=(N_PC_P+N_SC_S)/(N_P+N_S)
```

입자수까지 주어지면 전체 피복률에는 추가 정보가 없다. 행마다 가중치가 달라지므로 **세 coverage 열의 고정계수 행렬 rank가 항상 2라는 뜻은 아니다.**

권고 기본 출력은 **φ_SE·φ_AM, 존재상별 Hertz C_P·C_S, 검증된 관통 graph의 Dijkstra τ**다. 전체 coverage와 ε는 파생/QC 값으로 보관한다.

주의: 예측 시점에 **실현 입자수 N_P/N_S를 모르는 모델**이라면 관측 N을 몰래 넣어 total을 예측했다고 하면 안 된다. 그 경우 total을 직접 학습하는 별도 예측 목표는 가능하지만, 세 coverage 모델을 독립된 세 증거로 해석해서는 안 된다. 설계 추정 N과 dump 실측 N도 구분한다.

### “학습 타깃으로 쓰면 안 된다”의 세 가지 다른 이유

| 부류 | 이 배치에서의 처리 |
|---|---|
| **RECORD_ONLY** | ε_sphere는 현재 등록이 독립 회귀에서 제외한다. 수치가 무의미해서가 아니라 φ와 항등식이며 명시적으로 기록만 하기로 했기 때문이다. |
| **정의 종속** | total coverage와 P/S+실측 N, ε와 두 φ. QC·표에 보관해도 되지만 중복 독립 성능으로 세지 않는다. |
| **물리적 미정의/축퇴** | 미퍼콜 graph의 관통 τ는 유한 회귀값이 아니다. 0이나 임의 큰 값으로 치환 금지. 연결 여부·사유를 보존하고 유한 τ는 조건부 목표로 학습한다. |
| **없는 상** | mono의 없는 P/S 크기·coverage는 N/A. 존재상의 피복0과 다르다. |
| **계산 실패** | NO_VALID_SAMPLED_PAIR/invalid free surface/입력 누락은 물리적 미퍼콜과도 다르다. |

Dijkstra와 Laplace 사이에는 일반적인 정확 대수 변환이 없다. 같은 graph의 저항 변경 반례가 이를 직접 보여 준다.

## 6. Q5 — 126 선학습과 결측

### 먼저, 요청에 인용된 “5개 제외”는 이미 철회돼 있다

[local gap verdict:68](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/docs/reviews/lhs_local_gap_verdict_20260903.md:68)에 **“8개 전부 돌린다. 게이트를 걸지 않는다.”**라는 저자 정정이 있다. 앞부분 제외 권고를 현재 판정으로 다시 사용하면 안 된다. 이는 새 설계 재심이 아니라 같은 문서의 유효 판정을 따른 것이다.

44/130은 **33.846%의 사전 추정 BELOW flag**다. “44%가 실측 σ_ion=0”이라는 자료가 아니다. 설계 타깃 7열은 모두 빈칸이고, 그중 σ_ion 열도 없다.

과거 문서의 미실행 8개 ID를 봉인 설계에 join하면:

- 모두 mono_AM_S.
- mono_AM_S×d_SE=2 μm 다섯 점 **105·108·109·110·111이 전부 결측 목록**이다.
- 남은 mono_AM_S에는 그 수준이 0개다.
- 로컬 30 전체 BELOW는 11개(누락5+나머지6). “정확히5 전부 미실행”은 mono_AM_S에 한정할 때만 맞는다.

따라서 이 누락이 지금도 지속된다면 단순 무작위 결측이 아니다. 공변량/가중치만으로 **한 수준의 관측이 전혀 없는 구간**을 되살릴 수 없다.

### 답: 탐색 학습은 가능, 최종 130-domain 검증은 아직 안 됨

- 추출기를 교정한 뒤 완료분으로 파싱·전처리·모델 탐색을 시작할 수 있다. 단 현재 관측 도메인의 잠정 결과로 표시한다.
- 목표 압력에 못 미친 진행 프레임을 최종 300 MPa 목표값으로 넣지 않는다.
- 130-domain 최종 성능·순위·해석은 미완료/미실행분의 처리와 수확 게이트가 닫힌 뒤 재검증한다.
- `126+4`와 `로컬22+8`은 현행 ID별 원장 없이는 동시에 받아들일 수 없다. 4개와 8개가 같은 130 안의 서로 다른 미완료 집합이면 완료는 118이지126이다. **현재 작업 상태는 이번 리뷰로 확인하지 않았다.**
- 전처리·변수 선택은 훈련 fold 안에서 수행하고, 추가 데이터를 보며 모델을 선택한 뒤 같은 검증 점수를 독립 성능처럼 재사용하지 않는다. [scikit-learn 공식 누설 방지 지침](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).

finite_size_flag를 **진단 라벨로 남기는 것은 타당**하지만 “공변량으로 넣으면 유한크기 효과를 알아서 제거한다”는 보장은 아니다. 이 flag는 설계 변수의 결정론적 함수다. 관측 없는 구간을 채우거나 고정 RVE 설계에서 크기/유한크기 효과를 독립 인과효과로 식별하지 못한다. 이 범위에서는 **고정 finite-box 규약 안의 예측**으로 해석해야 한다.

## 7. 수확 전 필요한 최소 계약

설계를 재추첨할 필요는 없다. 다음을 수확 도구에 고정하고 대표 mono_P/mono_S/bimodal·관통/비관통·무경로 샘플 실패 반례로 검증해야 한다.

1. 일곱 별칭→원필드/계산식/단위/mean 통계량을 정확히 매핑. 전체 Hertz는 실측 입자수로 집계.
2. φ는 전도도·τ 성공과 무관하게 기하에서 계산. ε와 같은 frame/상자·상 census 사용.
3. τ의 관통성·경계·추출 표본·긴 경로 처리와 N/A/실패 사유를 명시. 불량 geometry를 유효0으로 채우지 않음.
4. 표준 scale에서의 Hertz 보존과 Physics helper의 단위 일관성을 검증. Physics/rough/Laplace/Stage E 필드 대체 금지.
5. frozen130 ID에 최종 pressure/timestep·raw hashes·phase map·상 개수·target별 상태를 연결.
6. 우선 130 단독 corpus. 291 합치는 작업은 기존 d_am 및 MPM/DEM 규약 정리 후 별도 판단.

## 8. 재현 자료

이 리뷰는 대규모 자기 selftest 개수를 근거로 하지 않았다. 아래 독립 재현기 네 개를 실제 실행했고 모두 **rc=0**이었다. 원본 checkout의 `git status --short`는 빈 출력이다.

- [probe_descriptor_pipeline.py](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_evidence_20260913/probe_descriptor_pipeline.py) — parser→analyzer, φ 누락, mono map, wall fallback, timestep 혼합.
- [probe_coverage.py](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_evidence_20260913/probe_coverage.py) — 원 함수의 집계·분모·0/N/A·Physics 단위 대조.
- [probe_tortuosity.py](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_evidence_20260913/probe_tortuosity.py) — 비관통 유한τ, 관통 결측, 절단·평균/중앙값, Laplace 분리.
- [probe_design_corpus.py](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_evidence_20260913/probe_design_corpus.py) — 130/291 재계산, 실제 ML loader, closure, 누락 ID join.

실행 위치는 검토 workspace. numpy/pandas/scipy/networkx가 설치된 Python에서:

```powershell
python ./lhs_descriptor_evidence_20260913/probe_descriptor_pipeline.py
python ./lhs_descriptor_evidence_20260913/probe_coverage.py
python ./lhs_descriptor_evidence_20260913/probe_tortuosity.py
python ./lhs_descriptor_evidence_20260913/probe_design_corpus.py --repo ./lhs_descriptor_review_20260913
```

저장된 실행 결과: [pipeline](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_evidence_20260913/result_descriptor_pipeline.txt), [coverage](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_evidence_20260913/result_coverage.txt), [tortuosity](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_evidence_20260913/result_tortuosity.txt), [design/corpus](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_evidence_20260913/result_design_corpus.txt).

로컬에서는 기존 검토 의존성과 새 networkx를 사용했으며, 설치 계정에서 실행했다. 라이브러리 권한이나 원본 리포 파일을 변경하지 않았다. 생성된 임시 합성 dump는 각 검사 종료 후 정리되며 실제 실험 데이터는 삭제하지 않았다.

현재 출력물을 그대로 ML 코퍼스로 확정하면 안 됩니다. 새 P1 세 건을 재현했습니다.
[전체 리뷰문 — 정의 대응표·반례·재현 명령](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_evidence_20260913/codex_review_lhs_descriptors_20260913.md)
가장 중요한 반례
1. 경로 계산이 안 되면 φ 두 개도 사라집니다.
   합성 dump를 정상 처리하고 공극률까지 저장했지만, τ가 없다는 이유로 phi_se·phi_am은 누락됐습니다. 완전행만 학습하면 연결성이 약한 구조가 함께 탈락할 수 있습니다. [저장 가드:430 (line 430)](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/analyze_contacts.py:430)
2. SE 관통률 0인데 τ=1을 냅니다.
   아래판에 연결되지 않은 위쪽 성분을 새 출발점으로 삼기 때문입니다. 반대로 직선 관통 성분 200개가 있어도 샘플링 때문에 τ가 결측되는 반례도 나왔습니다. [fallback:503 (line 503)](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/dem_analysis_core.py:503)
3. Physics 피복률에 실제 단위 혼용이 있습니다.
   확대 DEM 길이와 미확대 5 nm 두께를 함께 씁니다. 같은 물리 접촉에서 단위를 일치시키자 Physics 피복률이 **0.782065% → 0.384115%**로 달라졌습니다. Hertz는 0.3125%로 불변입니다. 따라서 큰 Δ를 전부 정의 차이로 설명할 수 없습니다. [두께 사용:284 (line 284)](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/scripts/plastic_coverage.py:284)
일곱 타깃의 실제 뜻
등록 타깃	코드가 계산하는 양·주의점
phi_se	실제 SE 구 부피합 / 전극 부피. 추정 열 복사 금지, τ와 독립적으로 추출해야 함
phi_am	현재는 1−phi_se−ε/100. AM+SE만 있고 같은 부피 규약일 때 AM 분율
coverage_AM_P_hertz_pct	P 입자별 **SE 접촉면적 / (구 표면적−AM–AM 접촉면적)**의 산술평균, 100% 상한
coverage_AM_S_hertz_pct	S에 같은 계산. 없는 상=N/A, 존재하지만 무접촉=0
coverage_AM_total_hertz_pct	실측 입자수 가중 P/S 평균. 질량분율 가중이나 상 평균의 단순평균이 아님. 기존 JSON에 전체 Hertz 키가 항상 있지도 않음
tortuosity_dijkstra_SE	SE 최단경로 중심거리 / 끝점 z 거리. mean·median·recommended 중 무엇인지 추가 동결 필요. Laplace로 대체 금지
porosity_sphere_pct_RECORD_ONLY	겹침을 빼지 않은 구 부피합 공극률. 현재 등록에서는 기록·검산용, 독립 회귀에서 제외


피복률 주 생산자는 전도도 솔버가 아니라 **앞단의 dem_analysis_core → analyze_contacts**입니다.
학습·결측에 대한 답
- 일곱 열은 보관하되 일곱 독립 타깃으로 세지 마세요. ε는 두 φ에서, 전체 피복률은 상별 피복률과 실측 입자수에서 유도됩니다.
- 기존 291건에는 d_am=0 40건이 실제 ML 입력으로 계속 들어가며, DEM φ와 MPM 공극률의 닫힘 불일치도 남아 있습니다. 신규 130과 바로 합치면 안 됩니다.
- 44/130은 33.85%의 사전 플래그입니다. “44%가 실측 σ_ion=0”이라는 증거가 아닙니다.
- 인용하신 결측 판정문은 후반부에서 “5개 제외”를 철회하고 “8개 전부 실행”으로 정정했습니다. [정정:68 (line 68)](C:/Users/Administrator/Documents/Codex/2026-08-24/claude-stoic-knuth-nobvq-x20/lhs_descriptor_review_20260913/docs/reviews/lhs_local_gap_verdict_20260903.md:68)
- 교정된 완료분으로 탐색 학습은 가능하지만, 특정 조성·입경 수준이 통째로 빠진 상태를 130-domain 최종 성능으로 보고하면 안 됩니다. 전처리·변수 선택도 훈련 fold 안에 둬야 합니다. 공식 검증 지침
독립 재현기 네 개를 실행했습니다. 원본 코드·CSV는 수정하지 않았으며, 실제 130개 dump와 스크린샷 원자료가 없어 배치 내 발생 건수와 화면 Δ의 원인은 미확정입니다.

---

## 부록 — 이 리포에서의 독립 재현 (2026-09-13, claude)

판정문을 받은 자리에서 **우리 트리의 같은 파일**로 세 P1 을 직접 확인했다.  Codex 의 검토 사본이
아니라 `HEAD` 의 소스다.

### P1-DESC-01 — τ 가드가 기하량 두 개를 함께 삼킨다 ✅ 재현

- `scripts/dem_analysis_core.py:931-943` — `φ_SE = v_se / v_electrode` 를 **먼저** 계산해 놓고
  (`:938`), 그 아래 `tau` 가 없거나 `≤ 0` 이면 `return None` 한다 (`:941-943`).
  ⇒ 이미 손에 든 기하량을 **버린다**.
- `scripts/analyze_contacts.py:430-434` — `if eff_cond:` 안에서만 `phi_se` 와
  `phi_am = 1 − phi_se − porosity/100` 을 쓴다.  τ 실패 = 두 φ 키 **부재**.
- `webapp/pipeline_service.py` `NET_MERGE_KEYS` 에 `phi` 를 포함하는 키가 **하나도 없다**
  (전수 확인: `'phi' in <블록>` → `False`) ⇒ 후속 network merge 도 복구하지 않는다.

### P1-DESC-02 — 비관통 fallback source ✅ 코드 확인

- `scripts/dem_analysis_core.py:502-509` — `src_candidates` 가 비면 **위판에 닿는 성분마다
  최저 z 를 새 source 로 승격**한다.  바닥판 접촉 여부와 무관하므로 `percolation_pct = 0`
  에서도 유한 τ 가 나온다.
- 같은 함수 `:517-522` — `pairs` 를 `src_candidates × reach_top` 전수로 만든 뒤
  **shuffle 하고 앞 200 개만** 남긴다.  성분이 갈려 경로가 없는 쌍도 그 예산을 먹는다
  ⇒ 관통 성분이 많아도 `n_samples = 0` 이 될 수 있다.
- ⇒ **유한 τ ≠ 관통 보장**, **τ = None ≠ 미퍼콜 보장**.  두 상태를 같은 결측으로 접으면 안 된다.

### P1-DESC-03 — 단위 혼용 ✅ **수치까지 재현**

`scripts/coverage_physics_vs_hertzian.py:205-207` 이 `delta_sim`·`r` 를 **sim 단위 그대로**
`film_area_from_overlap` 에 넘기는데, `scripts/plastic_coverage.py:50` 의 `H_FILM_MIN = 5.0e-9`
은 **SI 미터**다.  `:284` 의 `A_volume = V_overlap / H_FILM_MIN` 에서 분자는 길이³(스케일 1e9),
분모는 미스케일 ⇒ **부피 cap 이 1000배 부풀어 사실상 절대 안 걸린다**.

Codex 의 반례(AM/SE 반지름 0.5 µm, δ/R\* = 0.05)를 실제 함수로 재실행한 결과:

| 입력 단위 | binding cap | A_physics / A_hertz |
|---|---|---|
| 현행 sim (scale = 1000, 길이 단위 = mm) | `tabor` | **2.502607** |
| 같은 접촉, 길이를 SI 미터로 통일 | `volume` | **1.229167** |

비의 비 = **2.036019** — Codex 가 보고한 값과 일치한다.  요청서의 Hertz 0.312500 % 를 곱하면
**0.782065 % → 0.384115 %** 로, 판정문의 두 수치가 그대로 나온다.
⇒ **cap 선택 자체가 뒤집힌다** (Tabor ↔ volume).  "Δ 는 정의 차이뿐" 이라는 내 주장은 반증됐다.
⚠ 단 **Hertz 는 두 경우 모두 불변**이므로, 등록 타깃이 Hertz 전용인 한 이 오류는 그 일곱 열로
**전이되지 않는다** — 판정문이 그어 놓은 경계를 넘겨 읽지 말 것.

### 내 요청서의 오류 — 판정문이 고친 것

1. **호출 경로를 잘못 시작했다.**  요청서는 `app.py:2878 → network_conductivity` 로 썼으나
   피복률·φ·τ 의 **주 생산자는 `app.py:3271 → analyze_contacts_bimodal.py → analyze_contacts.py
   → dem_analysis_core.run_full_analysis`** 다.  전도도 솔버는 소비자다.
2. **"5개 제외" 를 현재 권고처럼 인용했다.**  `docs/reviews/lhs_local_gap_verdict_20260903.md:68`
   에 저자 정정 *"8개 전부 돌린다.  게이트를 걸지 않는다"* 가 **이미 있었다** — 같은 문서의
   뒷부분이다.  (이유도 그 자리에 적혀 있다: `se_percolation` 은 `phi_se_est` 파생 = 런 **전**
   추정이라 그것으로 실행을 거르는 것이 "자기 신고를 읽지 마라" 규칙 위반.)
   ⇒ 이 리포에서 직접 확인했다.  **인용을 철회한다.**
3. **`phi_se`·`phi_am` 이 항상 생산된다** · **전체 Hertz 피복률 키가 기존 JSON 에 항상 있다** ·
   **"큰 Δ 는 정의 차이뿐"** — 셋 다 REFUTED.
