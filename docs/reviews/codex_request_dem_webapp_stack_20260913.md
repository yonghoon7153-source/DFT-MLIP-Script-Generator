# Codex 리뷰 요청 — **DEM 웹앱 계산 스택 전체** (층별 게이트 리뷰)

> 작성 2026-09-13 · 브랜치 `claude/sdcp-dem-manuscript-si-pqwtv8` · 기준 스냅샷 **`be79f0827`**
> 저자 지시: *"이참에 DEM 웹앱에서 하는 모든 코드를 리뷰받고 싶다 — 지금 MPM 쪽에 하는 것처럼.
> 잘못되었으면 처음부터 코드 갱신하자.  예를 들어 **DEM 의 한계 때문에 했던 coverage 등의
> 계산, 거기에서의 conductivity**."*
>
> ⚠ **총 30,235 줄이다.**  한 번에 보라는 요청이 아니라 **층별 게이트**다 — 아래 L1 이
> 무너지면 L2 이상은 볼 필요가 없다.  **L1 판정만 먼저 줘도 된다.**

---

## 0. 왜 지금, 왜 이 순서인가

리포의 전체 사슬은 **강체구 DEM 이 소성을 못 한다**는 한 가지 한계 위에 세워진 보정탑이다:

```
강체구 DEM (입자 모양 불변)
  └ E_eff 18배 연화          ← 누락 기전(재배열·GB슬라이딩·미세파괴) lumping
      └ 겹침 δ                ← "밀려난 재료가 융기로 재출현" = ε_sphere 규약
          └ Stage-E 접촉면적 보정 (Tabor + 부피)   ← ★ 저자가 지목한 자리
              └ coverage (Hertz / Tabor / B3)
                  └ Holm 협착 R = 1/(2σa) → Kirchhoff σ 삼중항
                      └ 스케일링법칙 (σ_ion T1 · σ_e 22.5 · σ_th T1)
                          └ grade_engine · ASR · ML 코퍼스
```

⇒ **아래가 틀리면 위는 전부 틀린다.**  그래서 순서가 곧 게이트다.

그리고 지금 이것을 묻는 실무 이유가 있다: `lhs00` **130 배치**를 ML 학습 코퍼스로 만들려는데,
그 설계 CSV 가 선언한 타깃 7개(`phi_se`·`phi_am`·`coverage_AM_{P,S,total}_hertz_pct`·
`tortuosity_dijkstra_SE`·`porosity_sphere_pct_RECORD_ONLY`)를 **이 스택이 계산한다**.
검증 없이 126 런을 통과시키면 코퍼스가 통째로 오염된다.

## 1. 리뷰 대상과 순서 (층별 게이트)

| 층 | 무엇 | 파일 | 줄 |
|---|---|---|---|
| **L1** | 접촉 기하 · **coverage** · porosity 규약 | `analyze_contacts.py` · `coverage_physics_vs_hertzian.py` | 813 + 556 |
| **L2** | 접촉망 수송 (Holm 협착 · Kirchhoff · Stage-E) | `network_conductivity.py` · `run_network_full_corrections.py` | 1,609 + 1,223 |
| **L3** | 스케일링법칙 (σ_ion T1 · σ_e 22.5 · σ_th T1) | `generate_comparison_plots.py` | 7,525 |
| **L4** | 파생·등급·검증플래그 | `grade_engine.py` · `audit_validation_flags.py` · `extract_se_network_diagnostics.py` · `eis_fit.py` · `se_material.py` | 1,859 + 211 + 467 + 269 + 320 |
| **L5** | ML 층 | `ml_design_structure.py` · `predictor_engine.py` · `structure_predictor.py` | 1,462 + 1,567 + 399 |
| **배선** | 오케스트레이션·프로비넌스 | `webapp/app.py` · `pipeline_service.py` | 10,815 + 950 |

**★ L1 → L2 → (L3 ∥ L4) → L5** 순.  각 층에서 *"라벨 ↔ 코드가 실제 계산하는 양"* 이
어긋나는 곳에 `파일:줄` 을 붙여 주면 된다.

---

## L1 — 접촉 기하와 coverage (**저자가 지목한 자리**)

`network_conductivity.py:240-264` 의 **5-regime 분해**가 핵심이다:
```
A_physics = max( lower[A_hertz = πR*δ, A_ligg],
                 min( caps[A_tabor = F/H, A_volume = V/h_min, A_geom = 2πR_min²] ) )
```

**(L1-1)** 이 `max(lower, min(caps))` 가 **의도한 물리**인가?  `A_tabor = F/H` 는 소성
평균압이 경도 `H` 에 도달한다는 가정이고 `A_volume = V/h_min` 은 밀려난 부피의 재분배다.
둘을 **cap 으로 묶고** Hertz 를 **floor 로 두는** 구성이 어떤 조건에서 비물리적 결과를 내나?
특히 **깊은 겹침**(ε_sphere 가 음수로 가는 조밀 pure-SE)에서.

**(L1-2)** 화면의 두 열 — **Hertzian(DEM native)** vs **Physics(Tabor+volume)** — 이
접촉면적에서 Δ **+281.6 % · +299.4 %**, coverage 에서 **+270.3 %** 로 뜬다.
이 Δ 가 **정의 차이**인가 **단위·정규화 불일치**인가?
⚠ 이 리포는 정확히 이 축에서 데였다: `cov_Hertz ↔ cov_physics` 혼용이 **91건 전부
1.4배 과대예측**을 만들고 헛 revert 를 유발했다 (σ_ionic T1 "FALSE-REVERT").

**(L1-3)** `ε_sphere` ↔ `ε_union` 이 이 계에서 **1.251 %p** 어긋난다 (MPM 쪽 실측).
DEM 경로에서 어느 쪽이 어디에 쓰이나?  `porosity_sphere_pct_RECORD_ONLY` 의
`RECORD_ONLY` 접미사는 **학습 타깃 금지**를 뜻하나?

**(L1-4)** `ps_frac = 0 또는 1` 인 **mono 30/130** 행에서 죽은 상의 크기 열이 **0 센티넬**로
채워지는가?  08-18 설계는 **빈 칸(NaN)** 으로 두기로 했는데, 수확 단계에서 0 이 되살아나면
291 코퍼스가 이미 겪은 **40/291 (14 %)** 오염이 재현된다.

**(L1-5)** B3 표면거칠기 coverage 보정이 어디서 걸리고, Hertz/Tabor 와 **중복 계상**되지 않나?

---

## L2 — 접촉망 수송

**(L2-1)** Holm 협착 `R = 1/(2σa)` 가 접촉마다 직렬로 들어가는데, 그것을 **뺀** 가지를
코드가 스스로 `CONTACT_FREE — upper bound, ideal contact limit` 이라 부른다.
`case_master.csv` 의 `R_brug_over_full` 이 **n=157 중앙값 4.04×(Hertz) · 6.69×(소성면적),
범위 2.3~13.6×** 다.  ⇒ **어느 가지가 기본으로 보고되는가?**  화면·CSV·ML 코퍼스가
서로 다른 가지를 쓰고 있지 않나?

**(L2-2)** `f_intact` / fracture-aware 축소가 σ 에 들어가는 경로.  파괴 접촉이 σ 에서
**두 번 빠지지** 않나 (접촉 소실 + `β_F·log f_intact` 항)?

**(L2-3)** ⚠⚠ **알려진 미해결 결함**: `run_decomposition` 이 `build_network` 에 `mode=` 를
**전달하지 않아** 기본 `'ionic'` 으로 돌았고, 그래서 `network_conductivity.py:311` 의
`if mode == 'thermal' and se_type_set:` 분기가 **프로덕션에서 한 번도 실행되지 않았다**
→ 모든 간선 `k_weight = 1.0`.  원장 **CL-12**, 커밋 `27258c77`.
⇒ **지금 코드에서 이것이 실제로 고쳐졌는지**, 그리고 **캐시된 σ_thermal 타깃이 여전히
가중 없는 망의 값인지** 확인해 달라.  (CLAUDE.md 는 재실행 전까지 그 인과 서술을 인용 금지로
묶어 뒀다.)

**(L2-4)** 퍼콜 판정이 **두 군데**서 다르게 정의돼 있지 않나 — AM 접촉 그래프
(`lhs_perc_extract.py`, 확장분 1차 관측량) vs 복셀/솔버 기반.  LHS 사전등록은 *"둘은 동치가
아니다 — primary 는 그래프뿐"* 이라고 못 박았는데 웹앱 경로는 어느 쪽인가?

---

## L3 — 스케일링법칙 (7,525줄)

**(L3-1)** LOCKED 지수 5개(`φ_AM⁴` · `√A` Holm · NCM β=1.5 · logpoly2 · 대칭 bimodal)가
**코드에서 실제로 잠겨 있는가**, 아니면 live 로 재적합되는 경로가 남아 있나?

**(L3-2)** EXCL 목록(σ_e 25건, σ_th 가 공유)이 **적합에만** 적용되고 **보고·플롯**에는 안
적용되는 곳이 있나?

**(L3-3)** ⚠ `φ_AM < 0.3` 외삽 금지가 **코드로 강제되는가** 아니면 문서 경고뿐인가?
(130 배치는 그 아래를 겨냥한 lhsx 확장과 이어진다.)

**(L3-4)** σ_ionic T1 의 **"FALSE-REVERT" 재발 방지** — `_cov_frac`·`_sat_baselog` 를 부르는
**모든 callsite**(최소 4곳)가 같은 coverage 규약을 쓰는가?

---

## L4 — 파생·등급·검증플래그

**(L4-1)** `grade_engine` 의 ~30 파생량 중 **정의상 서로 종속**인 것.
**(L4-2)** `validation_flags` 가 **fail-open** 인 곳 (플래그가 안 뜨는 것이 통과로 읽히는 자리).
**(L4-3)** ASR 계산의 두께·면적 규약이 화면·CSV·등급에서 일관한가.

---

## L5 — ML 층

**(L5-1)** ⚠ **이미 아는 결함 — 다시 보고하지 말고 "고쳐졌는가" 만 봐 달라**:
`predictor_engine` 의 GPR 경로가 ⓐ 커널 6개 중 **최댓값을 전체 데이터로 골라** 보고하고
(max-of-6 낙관) ⓑ `scaler_X/y` 를 **폴드 나누기 전에** 적합한다 (표준화 누수).
CLAUDE.md 가 *"nested 와 나란히 크기 비교 금지"* 로 묶어 뒀다.

**(L5-2)** `ml_design_structure.py` 의 13 특징 중 **7개가 나머지 6개의 대수적 함수**라
`free_products=True` 로 곱항을 자유노브 6개로 제한했다 (nested 0.466 → 0.587, 편향
0.178 → 0.032).  그 제한이 **모든 경로에서** 걸리나, 아니면 우회 경로가 있나?

**(L5-3)** `use_porosity_pct` 는 **REJECT 열**(닫힘 잔차 sd 가 ε sd 의 78 %)인데
코퍼스 생성기가 여전히 그 열을 **쓰거나 노출**하나?

**(L5-4)** `design_performance_corpus.csv`(291행) 생성 경로에서 `d_am` 규약
(max(dP,dS) ↔ ps 가중 산술평균, 중앙 **1.41배**·최대 **6.09배**)이 **한 가지로 고정**돼 있나?

---

## 2. 저자 결정 — 틀렸으면 갱신한다

> *"잘못되었으면 다시 처음부터 코드 갱신화 하자."*

⇒ **재작성이 선택지에 있다.**  그러니 *"고칠 수 있다"* 와 *"이 구성으로는 못 고친다"* 를
갈라 적어 달라.  후자라면 무엇으로 대체해야 하는지도.
⚠ 다만 **σ 스케일링법칙의 계수·문턱은 등록된 것**이다 (LOCKED 지수 · EXCL · φc 동결).
그것을 바꾸라는 권고는 **별도 사전등록 사안**으로 표시해 달라.

## 3. 내가 확인한 것 / 확인 못 한 것

**확인**: 위 체인을 grep 으로 추적 (`webapp/app.py:2878` → `network_conductivity.py` →
`*_hertzian/_physics/_dual.json` → `full_metrics.json` → `run_network_full_corrections.py`).
설계 CSV 전수 130행 · 39열.  `design_performance_corpus.csv` 291행에 **lhs 행 0개**.

**확인 못 함**: 이 스택을 **실행해 본 적 없다** (이 컨테이너에 케이스 데이터가 없다).
화면 Δ% 값은 **사용자 스크린샷**에서 읽은 것이고 재계산하지 않았다.
`generate_comparison_plots.py` 7,525줄은 **전체를 읽지 않았다**.

## 4. 진행 중인 별건 (겹치지 않게)

`docs/reviews/codex_request_phase_a_adapter_20260912.md` = **MPM/STEP3 쪽** Phase A 어댑터
(판정 `PA12-01~09`, P1 8건).  그쪽은 MPM 경로이고 이 요청은 **DEM 경로**다.
다만 `Q7`(로그에서 회수한 batch-level 잔차를 쓸 수 있는가)은 아직 답 대기다.
