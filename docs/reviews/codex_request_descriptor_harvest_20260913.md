# Codex 리뷰 요청 — 웹앱 디스크립터 추출 경로가 **정말 그 값을 내는가**

> 작성 2026-09-13 · 브랜치 `claude/sdcp-dem-manuscript-si-pqwtv8` · 기준 스냅샷 **`be79f0827`**
> 목적 = **lhs00 130 배치를 ML 학습 코퍼스로 만들기 전에** 추출 경로를 검증한다.
> 설계 정본 = `docs/lhs_design_dataset_20260818.md` (특히 §O) ·
> 원장 = `docs/reviews/claims.json` · 결함 원장 = `docs/reviews/findings.json`
>
> ⚠ **설계 재심이 아니다.**  130 배치의 설계·고정인자·플래그 규약은 08-18 에 등록돼 있고
> 그대로 간다.  쟁점은 **그 설계가 선언한 타깃 7개를 코드가 실제로 그 정의대로 내는가** 하나다.

---

## 0. 왜 지금 이걸 묻나

lhs00 130 배치는 처음부터 **"AI 학습용 DEM 데이터셋"** 으로 설계됐고, 설계 CSV
(`docs/data/lhs_design_20260818.csv`, 39열)가 **타깃 열을 스스로 선언**해 두었다:

```
phi_se · phi_am
coverage_AM_P_hertz_pct · coverage_AM_S_hertz_pct · coverage_AM_total_hertz_pct
tortuosity_dijkstra_SE
porosity_sphere_pct_RECORD_ONLY
```

그런데 **덤프 → 이 7개를 내는 수확기가 리포에 없다** (`scripts/lhs_*` 는 설계기와 확장분
퍼콜 추출기뿐이고, 08-18 문서 §P 는 **제출까지만** 닫았다).  ⇒ 291 코퍼스가 거친 것과 같은
경로를 130 덤프에 돌려야 하는데, **그 경로가 라벨대로 계산하는지**를 확인하지 않고 126 런을
통과시키면 코퍼스가 통째로 오염된다.

★ 그리고 이 리포는 **바로 그 부류로 다섯 번 데였다** (08-18 문서 §O-2 표):

| 사고 | 크기 |
|---|---|
| `cov_Hertz` ↔ `cov_physics` 혼용 | **91건 전부 1.4배 과대예측** + 헛 revert |
| `d_am` = max(dP,dS) ↔ ps 가중 산술평균 | 중앙 **1.41배** · 최대 **6.09배** |
| `ps=0` 행의 `d_am = 0` 센티넬 | 코퍼스 **40/291 (14 %)** 오염 |
| `ε_sphere` ↔ `ε_union` | **1.251 %p** 오프셋 |
| `use_porosity_pct` (porosity 만 MPM, φ 는 DEM) | 닫힘 잔차 sd 가 ε sd 의 **78 %** |

## 1. 검토 대상 코드 경로 (내가 추적한 것)

```
webapp/app.py:2878  →  scripts/network_conductivity.py          (1,609줄)
        → network_conductivity{,_hertzian,_physics,_dual}.json
        → full_metrics.json 병합
        → scripts/run_network_full_corrections.py               (1,223줄, _compute_validation_flags)
        → scripts/coverage_physics_vs_hertzian.py               (556줄)
        → scripts/grade_engine.py                               (1,859줄)
```

⚠ 이 체인은 **내가 grep 으로 추적한 것**이고 실행으로 확인하지 않았다.  누락된 단계가 있으면
그것부터 지적해 달라.

## 2. 묻는 것

**(Q1) 타깃 7개가 라벨대로 계산되는가.**  각각에 대해 *"코드가 실제로 계산하는 양"* 을
정의 수준에서 적어 달라 — 특히:
- `coverage_*_hertz_pct` — Hertz 접촉면적 기준이 맞나?  화면에는 **Hertzian(DEM native)** 과
  **Physics(Tabor+volume)** 두 열이 나란히 나오고 Δ 가 **+281.6 % · +299.4 % · +270.3 %** 인
  행들이 있다.  그 Δ 가 **정의 차이**인가 아니면 **단위·정규화 불일치**인가?
- `tortuosity_dijkstra_SE` — Dijkstra 경로 기반이 맞나?  같은 화면에 `τ_Laplace`·
  `constriction overhead` 가 따로 있고 Δ **+156.4 %** 로 뜬다.  ML 타깃으로 쓸 때 둘 중
  어느 것이 설계가 말한 그 양인가?
- `porosity_sphere_pct_RECORD_ONLY` — 이름에 `RECORD_ONLY` 가 붙어 있다.  **학습 타깃으로
  쓰면 안 되는 양인가?**  (설계 문서는 디스크립터로 열거했는데 열 이름은 반대로 읽힌다.)
- `phi_se`·`phi_am` — 설계 CSV 에 **추정값(`phi_*_est`)과 실측 열이 둘 다** 있다.
  수확기는 어느 쪽을 채워야 하나?

**(Q2) 규약 오염이 이 경로에 남아 있는가.**  위 다섯 사고 중 지금도 발화 가능한 것.
특히 `ps_frac = 0/1` 행(**mono 30/130**)에서 죽은 상의 크기 열이 **0 센티넬**로 채워지는가?
08-18 설계는 그것을 **빈 칸(NaN)** 으로 두기로 했는데, 수확 단계에서 0 으로 되살아나면
291 이 겪은 14 % 오염이 재현된다.

**(Q3) 타깃끼리 대수적으로 종속인가.**  `ml_design_structure.py` 는 이미 같은 부류로 한 번
데였다 — 13 특징 중 **7개가 나머지 6개의 대수적 함수**라 유도량끼리 곱항을 만들면 과적합
연료가 됐고, 자유노브 6개로 제한해 `mpm_plastic_gain` nested 0.466 → **0.587**, 편향
0.178 → **0.032** 로 개선됐다.  ⇒ 타깃 7개 중 **닫힘 관계**(예: `ε = C − φ_SE − φ_AM`)나
정의상 종속이 있는 쌍을 지적해 달라.  학습을 어느 부분집합으로 해야 하는가?

**(Q4) 이 경로를 130 배치에 그대로 돌려도 되는가.**  291 코퍼스는 첨가제·MPM 단계를 거친
케이스가 섞여 있는데 130 은 **첨가제 없음 · DEM 전용**이다.  경로가 그 부재를 **0 으로 채우는지
빈 칸으로 두는지**가 코퍼스 규약을 가른다.

**(Q5) 아직 안 도는 4런·미실행 8건의 처리.**  ibb 에 lhs00 **4개가 아직 압축 중**(압력
0.225~0.266 / 목표 0.30)이고, 로컬 30점 중 **8개가 미실행**인데 그 중 **5개는 설계 게이트
(`se_percolation = BELOW_phic`)라 안 돌리는 것이 맞다**고 이미 판정돼 있다
(`docs/reviews/lhs_local_gap_verdict_20260903.md`).  ⇒ 126행으로 먼저 학습하고 나중에 얹는
것이 통계적으로 안전한가, 아니면 **결측 구조가 조성에 의존**하므로 전수를 기다려야 하는가?
⚠ `se_percolation = BELOW_phic` 는 설계 CSV 기준 **44/130 (34 %)** 이고,
`finite_size_flag` 가 깨끗한 행은 **62/130** 뿐이다.  08-18 §3b 는 그 플래그를
*"거부가 아니라 라벨 — 학습에 공변량으로 남기면 모델이 흡수한다"* 로 정했다.  그 처리가
**44 %가 축퇴(σ_ion = 0)인 상황에서도** 타당한가?

## 3. 내가 확인한 것 / 확인 못 한 것

**확인**: 설계 CSV 전수(130행 · 39열) — 블록 bimodal 100 / mono_AM_S 15 / mono_AM_P 15,
`se_percolation` OK 86 · BELOW_phic 44, `finite_size_flag` 깨끗 62.
`design_performance_corpus.csv`(291행)에 **lhs 행이 0개**임을 이름 대조로 확인.

**확인 못 함**: 위 코드 체인을 **실행**해 본 적 없다.  130 덤프는 ibb·로컬 두 기계에 있고
이 컨테이너에 없다.  화면의 Δ% 값들은 **사용자가 보낸 스크린샷**에서 읽은 것이고 내가
재계산하지 않았다.

## 4. 부탁하는 형태

각 타깃에 대해 **`라벨 ↔ 코드가 계산하는 실제 양`** 대응표를 주고, 어긋나는 것에
`파일:줄` 을 붙여 달라.  그리고 **ML 타깃으로 쓰면 안 되는 것**이 있으면 그 이유를
(정의 종속 · RECORD_ONLY · 축퇴) 갈라 적어 달라.
