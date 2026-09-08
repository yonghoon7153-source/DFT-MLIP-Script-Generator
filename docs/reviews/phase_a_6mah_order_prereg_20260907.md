# 사전등록 — 6 mAh VGCF+PTFE 조성 순서 (Phase A, STEP3)

> 작성 2026-09-07 · 브랜치 `claude/stoic-knuth-NObVQ` · **런 시작 전 커밋 필수**
> 선행 판정 = `codex_verdict_6mah_20260907.md` (Q1 REFUTED · RUN HOLD) — 이 문서가 그 지적을
> 반영한 **재작성판**이다.  옛 초안(요청서 §2)은 폐기.
> 선택된 설계 = **(A) primary 96 팔** (사용자 결정 2026-09-07).
>
> ## ⚠⚠ v2 개정 (2026-09-07, Codex R9 = RUN HOLD)
> 판정 정본 = `codex_r9_verdict_phase_a_20260907.md` · 원장 `CL-79`.
>
> | 무엇 | 초판 | **v2** |
> |---|---|---|
> | 재하율 | 킷의 기하 규칙 (Mach 0.4275~0.4612, **조성 의존**) | **`--platen-mach 0.03` 고정** · `--frames 2500` |
> | 결론 범위 | *"격자에 강건한 순서"* | **"Mach 0.03 생산 규약에 조건부인 순서"** |
> | exact replay | QC 끼리 비교 → **fail-open** | QC ↔ **primary 쌍둥이** · 부재·orphan·중복 전부 HOLD |
> | 계획 생성기 | `phase_a_plan.py` | **폐기** (실행 거부) — 정본은 킷 `run_mpm.sh` |
> | 각도 선별 | K=8 (무첨가 스캐폴드) | ⛔ **무효** — post-STEP2 · periodic-aware 로 재측정 |
> | 거친 두 격자 | primary 96 의 2/3 | **secondary 로 강등 검토** (§1 참조) |
>
> ⚠ **W1·W2 스모크(2026-09-07)는 exploratory pilot 이고 본 판정에서 제외한다** —
> 기하 규칙으로 돌아 등록 규약이 아니다.  ⛔ **기하 규칙으로 되돌리는 개정은 허용되지 않는다.**

⚠⚠ **결과를 보고 이 문서의 문턱·창·판정 규칙을 바꾸지 않는다.**  바꾸면 사전등록이 무효다.

> ## ⛔⛔ W1 단계 결과 = **STOP** (2026-09-08, 원장 CL-80)
>
> W1 을 **두 재하율로** 돌린 결과, **두 런 다 목표 압력에 도달하지 못했다.**
>
> ```
> 목표 target_GPa = 0.30
>                     기하 규칙       Mach 0.03 (등록 규약)
> final_stress_GPa    0.0139         0.1336        ← 9.6배 차
> 목표 대비            4.6 %          44.5 %        (settled_over_target 0.4434)
> stop_mode           legacy_moving  legacy_moving ← 움직이는 중에 끝남
> frames 사용/예산     40 / 150       90 / 2500     ← 예산이 아니라 다른 이유로 정지
> am_jam              off            off
> porosity_settled    13.699 %       13.848 %      ← **압력 9.6배 차인데 0.15 %p**
> 소요                 ~1.5 h         **52 분**
> ```
>
> · 원인 = **플래튼 운동학적 정지 결함** (`docs/mpm_platen_kinematic_stop_defect.md` 정본).
>   새 발견이 아니라 **알려진 결함이 Phase A 에서 발현**된 것이다.
> · ⇒ 이대로 네 조성을 돌리면 *"300 MPa 전극의 σ_e 순서"* 가 아니라
>   **"각자 다른 압력에 눌린 침대들의 순서"** 가 된다.
> · ★ **예산 걱정은 사라졌다** (52 분).  내 추정 20~35 h 가 **약 30배** 빗나갔다.
>   ⚠ 그러나 싼 이유가 곧 문제다 — 플래튼이 일찍 멈춰서다.
> · ★★ **압력이 9.6배 다른데 porosity 는 0.15 %p** — scaffold 런에서 porosity 가 독립 정보를
>   담지 않는다는 CLAUDE.md 의 경고가 직접 확인됐다 (`solid_vol` 고정 + `wall_z` 만 출력).
>   ⇒ **porosity 를 압축 성공의 증거로 읽지 말 것.**
>
> ⛔ **W2·W3·W4 를 시작하지 않는다.**  먼저 둘 중 하나를 정한다:
> **(a)** 목표 압력에 실제로 도달시키는 경로 (`fam_platen_prereg_20260812.md` — 단 그 문서가
> *"정지만 고치면 더 나빠진다 (ε_sphere 1.13 % vs 실험 15.6 %)"* 라고 적어 둔 상태다)
> **(b)** 도달 압력을 **규약으로 고정** — 네 조성이 같은 압력에 서도록 만들고 등록.
>
> ⚠ Codex 에 다시 물을 값어치가 있다: *"목표 미달 침대로 조성 순서를 재도 되는가."*

---

## 0. 무엇을 묻나 (estimand 를 먼저 못 박는다)

**Primary** — *"centerline PTFE 규약에서, VGCF 함량 1 → 2 → 3 → 4 wt% (PTFE 1 wt% 고정) 의
σ_e 순서가 시험한 세 격자(0.25 · 0.20 · 0.15 µm)와 8 origin 전부에서 유지되는가?"*

**Secondary** — Lee 2025 조성(80:17:3:0.5)과의 절대값 대조.
**QC** — exact replay · 봉인 검증.

⛔ **세 estimand 를 섞지 않는다.**  Secondary 와 QC 는 `ORDER-*` 판정에 **관여하지 못한다**.

### 이 문서가 답하지 **않는** 것 (런 전 명시)

- 참 σ_e 값 · 격자 수렴 (0.15 가 이 침대의 천장이다 — CL-72)
- `h < 0.15` 의 방향 · 연속체 오차의 부호 ⇒ **하한 서술 금지**
- PTFE 규약 선택 (centerline 하나만 잰다)
- rate 성능 · 전기화학 (STEP4 는 각도 파일럿 전까지 HOLD — CL-73)

---

## 1. 팔 배분 — 96 primary + 16 secondary + 8 QC = **120**

```
Primary   4 조성 × 3 격자 × 8 origin              = 96
Secondary Lee 조성 × 1 격자(0.15) × 8 origin      =  8
          생산 조성 × 1 격자(0.15) × 8 origin      =  8   (Lee 와 짝지을 우리 쪽)
QC        exact replay × 8 origin @0.15           =  8
                                                    ───
                                                    120
```

⚠ 옛 초안의 72 팔은 0.20·0.25 에서 **생산 조성 하나만** 재서 나머지 세 조성의 순위가
**정의되지 않았다** (CL-71).  96 은 그 판정 행렬을 실제로 관측한다.

### ★ v2 실행 단계 — **W1 하나로 예산을 먼저 잰다** (2026-09-07, 결과 보기 **전에** 등록)

Mach 를 0.4275 → 0.03 으로 낮추면 프레임이 14배 필요해 STEP2 가 4 런 **140~270 h** 로 간다.
⚠ 그 추정은 내 것이고 **오늘 두 번 빗나갔다** (후보 (b) 를 20~38 h 로 적었으나 실제 70~143 h).
⇒ **W1 한 런으로 실측한 뒤** W2·W3·W4 를 정한다.

**W1 이 답해야 할 것과, 그에 따른 사전 결정** (결과를 보고 이 표를 고치지 않는다):

| W1 관측 | 판단 | 다음 |
|---|---|---|
| 2500 프레임 **안에** 목표 응력 도달 · 완주 | 예산 추정 유효 | **W2·W3·W4 진행** |
| `not_converged_frame_budget` | 프레임 부족 — **숫자가 안 나온다** | frames 를 실측 소요 × 1.3 으로 올려 **W1 재실행** |
| 완주하되 소요가 추정 상한(67 h)의 **1.5배 초과** | 예산이 실측으로 깨짐 | ⛔ 넷 다 돌리지 않는다 — **{W1, W4} 양 끝만** (§아래) |
| 완주하되 `porosity` 가 기하-규칙 런(13.699 %)에서 **3 %p 이상** 이동 | 재하율이 침대를 크게 바꾼다 | 그 사실을 CL 에 등재하고 **결론 범위를 다시 좁힌다** |

★ **양 끝 우선 규칙** — 예산이 부족하면 `{W1, W4}` 를 먼저 채운다.  양 끝이 안 갈리면
중간 둘이 갈릴 리 없다.  ⚠ 다만 `ORDER-ROBUST` 는 **넷을 다 완주해야** 주장할 수 있다
(§1 의 중단 규칙과 같은 논리).

⚠ 이 런의 STEP3 는 킷 기본 `vox 0.4` 다 — **σ 값은 판정 대상이 아니다.**  재는 것은
**STEP2 예산과 완주 가능성**뿐이다.

### 실행 순서 — `0.15` 를 **먼저**

```
① h = 0.15   32 팔     ← 원 질문의 완전한 답이 여기 하나에 다 있다
② h = 0.20   32 팔
③ h = 0.25   32 팔
```

★ **역전이 나오면 즉시 `ORDER-UNRESOLVED` 로 중단**한다 (남은 팔을 돌리지 않는다).
`ORDER-ROBUST` 를 주장하려면 96 을 다 완주해야 한다.

⚠⚠ **v2 정정 (Codex R9 Q2)** — 위 neck 논거는 **철회**한다.  그 분석은 **압밀 전 해석 구의
이온** 축이고 Phase A primary 는 **`--no-ion` 전자** 축이다 ⇒ SE-neck 통계는 σ_e 해상도
게이트가 **아니다**.  6-face 로 재계산하면 참 접촉 누락은 `h=.15/.20/.25` 에서
0.060/0.246/0.863 % 뿐이고, 오히려 **가짜 face 접촉이 참 접촉 대비 18.06/20.93/23.28 %** 다.

★ **전자축에서 h 가 바꾸는 것은 오차가 아니라 feature 자체다** — VGCF 는 항상 1-voxel tube 라
실제 Ø 0.15 µm 대비 단면이 `h=.15/.20/.25` 에서 **1.27× / 2.26× / 3.54×** 로 바뀐다
(AM bridge 반경도 기본 `1.2h`).
⇒ 거친 64 팔은 grid convergence 도, *"접점이 지워져도 순서가 남는다"* 도 **증명하지 못한다.**
유지한다면 **지정된 h-의존 디지털 규약의 stress test** 로만 둔다.
⚠ 예산을 줄이면 **primary 를 `h=0.15` 32 팔로 좁히고 거친 격자는 secondary 로 강등**하는 것이
맞다.  `h=0.15` 도 continuum 수렴이 아니라 **지정 규약에서의 결과**다.

---

## 2. 판정 규칙 (런 전 고정)

인접 조성쌍 `k → k+1`, 격자 `h`, origin `o` 에 대해

```
d(h, o, k) = log σ_e(w_{k+1}, h, o) − log σ_e(w_k, h, o)
```

| 판정 | 조건 |
|---|---|
| **ORDER-ROBUST** | **모든** (h, o, k) 에서 `d > δ_num` |
| **ORDER-UNRESOLVED** | 하나라도 `d ≤ δ_num` |

**`δ_num = 0.04 %`** (= `d` 로는 4.0e-4).

- 8 origins 는 무작위 표본이 아니라 **완전 nuisance 집합**이다 ⇒ 산포를 통계로 다루지 않고
  **최악 팔을 직접 판정**한다.
- 평균 · SD · 범위는 **기술 보고 전용**.  별도 HOLD 게이트로 쓰지 않는다.
- ⛔ **임의의 "origin 산포 문턱" 을 두지 않는다** (옛 초안의 오류).

### 판정기 = `scripts/phase_a_order_verdict.py` (selftest **17/17**, v2)

이 규칙을 **코드로** 박았다.  `δ_num` 은 상수이고 **CLI 로 바꿀 수 없다** — 판정 후 문턱을
움직이는 가장 흔한 사고를 코드가 막는다 (진단용 `--what-if` 는 **판정 없이** 민감도만 찍는다).

fail-closed 조항 (오늘 잡은 결함들의 예방접종):

| # | 조항 | 왜 |
|---|---|---|
| ① | 설계 격자점이 하나라도 비면 **판정하지 않는다** | 부분집합을 훑으면 조용히 초록이 된다 — 72팔 초안이 정확히 그렇게 무너졌다 (CL-71) |
| ② | 미수렴·`cg_info ≠ 0` 이 하나라도 있으면 **거부** | CL-30 계열 |
| ③ | exact replay 가 δ_num 을 넘으면 **전체 HOLD** | 문턱 사후 확대 금지 |
| ④ | Secondary(Lee)·QC 는 `ORDER-*` 에 **관여 못 함** | estimand 분리 |
| ⑤ | 빈 디렉터리·키 결손 → **거부** | 빈 glob 가 초록이 되던 사고 (오늘만 두 번) |
| ⑥ | **QC 가 없으면 거부** · orphan · 중복도 거부 | ⚠ v1 의 ③ 이 **fail-open** 이었다 — QC 끼리 묶고 `len<2` 를 건너뛰어 **음성대조가 한 번도 발화하지 않았다** (QC 를 참값의 1000배로 넣어도 `ORDER-ROBUST`).  v2 는 QC 를 **primary 쌍둥이**와 직접 비교한다 (Codex R9 P0-2) |

★ selftest ② 가 핵심이다 — **96팔 중 하나만 역전시켜도 `ORDER-UNRESOLVED`** 가 나오는지
확인한다.  "최악 팔이 판정을 정한다" 를 코드가 실제로 지키는지의 시험이다.

### δ_num 의 근거와 그 게이트

`0.04 %` 는 합성 solver-method 차이 최대 `0.014 %/solve` 의 양 endpoint 최악합을 올림한
**사전값**이다.

★ **replay 실측은 이미 이 값을 통과했다** (CL-75): 같은 명령 3회가 평균과 8 origin 값 전부
**바이트 동일** ⇒ 재실행 성분 **0.000 %**.

⛔ **그럼에도 이 캠페인의 QC replay 가 0.04 % 를 넘으면, 문턱을 사후 확대하지 말고 전체 HOLD** 한다.

---

## 3. 음성대조 — `exact replay` (seed 변경이 **아니다**)

| 역할 | 무엇 |
|---|---|
| **음성대조** | **exact replay** — 동일 materialized STEP2 배열 · 동일 규약을 **다른 출력 경로**에서 재계산.  `d ≤ δ_num` 이어야 한다 |
| morphology replicate | 다른 seed (= seed sensitivity).  **음성대조 아님** |
| raster phase | 8 origins.  ⚠ **morphology seed 산포를 대신하지 않는다** |

### 왜 seed 가 음성대조가 아닌가 (CL-71)

seed 는 섬유 위치·길이·방향·굴곡을 **실제로** 바꾼다.  게다가 `mpm3d_compaction.py` 의 `ADD`
dict 는 VGCF 를 PTFE **앞**에 두고 **같은 `rng` 객체**를 상마다 순서대로 넘긴다 ⇒
**VGCF 개수만 바꿔도 뒤따르는 PTFE 형상이 달라진다** (동일 seed·VGCF 1→2 에서 PTFE SHA
`c838818136da8291 → e8cdebe8738da083`).

### ⇒ 이 캠페인은 `--add-rng-per-phase` 를 **켜고 돈다** (필수)

2026-09-07 신설.  상마다 `[seed, phase_code]` 로 독립 스트림을 판다 = **common random
numbers**: VGCF 함량이 변해도 PTFE 형상은 **바이트 동일**하게 유지된다.
⇒ 조성 축이 morphology 교란과 **분리**된다.

⚠ 켜면 씨딩이 달라져 **기존 침대와 바이트 비교가 깨진다** — 이 캠페인은 전부 새로 만든다.
⚠ 매니페스트 `add_rng_per_phase` 로 봉인된다 (규칙 M).
⚠ 그래도 남는 한계: 조성이 다르면 **VGCF 자신의** 형상은 당연히 다르다.  없앤 것은
**다른 상으로 새는** 교란이지 조성 효과 자체가 아니다.

---

## 4. STEP2 규약 — 측정 대상을 먼저 선언한다

⚠ STEP2 는 VGCF 함량에 따라 `dilate-z` · `stiff` · `buckle` · `align` 이 **함께** 움직인다.

> **이 캠페인이 재는 것 = "생산 파이프라인 total effect"** 다.
> 함량만의 효과가 아니다.  자동 조정되는 축들을 **끄지 않는다** — 실제 전극에서 VGCF 를 더
> 넣으면 그 축들도 같이 움직이기 때문이다.
> ⇒ 결론 문장은 *"VGCF 함량을 올리면 (생산 규약 하에서) σ_e 순서가 …"* 로 쓴다.

### 봉인할 STEP2 축

```
--add-rng-per-phase (ON)  --seed  --mixing  --add-l-cv  --ptfe-fibril  --ptfe-am-bind
--fibre-align  --fibre-buckle  --buckle-strain  --dilate-z  --platen-mach  --sub  --frames
--e-se  --nu-se  --yield-se  --target-gpa  --n-grid  --lateral-box  --nz  --periodic
```

### `--platen-mach`

| | 값 | 비고 |
|---|---|---|
| **Primary (순서)** | `--platen-mach 0.03 --allow-fast-platen` · `--frames 2500` | ⚠ 0.03 도 한계 0.01 을 넘으므로 **승인 플래그가 여전히 필요**하다 (없으면 시작 즉시 거부).  위반이 결과 JSON 에 기록된다 |
| **Secondary (Lee 절대)** | `0.01` | 절대 대조에는 준정적 경로가 필요.  ⚠ 0.01 에는 **frames ≈ 7500** 이 필요하다 |

⚠ Primary 와 Secondary 는 **재하율이 다르다** ⇒ 두 결과를 나란히 놓을 때 반드시 명시한다.

### ⚠⚠ `--frames` 는 하드 캡이다

`for frame in range(args.frames)` — 초과하면 `not_converged_frame_budget` 으로 죽고
**숫자가 하나도 안 나온다**.  Mach 를 낮추면 프레임당 하강폭이 그만큼 줄므로 **같은 배수로**
늘려야 한다.  생성기가 짝이 안 맞으면 **거부**한다 (`mpm_input_from_case.py --platen-mach`).

```
기하 규칙 150 프레임 · Mach ≤ 0.50   ⇒  Mach 0.03 에는 최소 2500
                                        Mach 0.01 에는 최소 7500
```

⛔ **`MPM_QUASISTATIC=1` 을 쓰지 말 것** — 그 분기는 `--platen-mach 0.01 --frames 1500` 이라
프레임 예산에서 죽는다.

---

## 5. STEP3 규약 — 봉인 최소 집합

```
fibre_stamp = segment          ptfe_stamp = centerline       sigma_ptfe = 0
bridge = 0                     plate rule                    physical area
conductivity tables            backend / rtol / maxiter      LEAN = 2 의 전체 확장
--no-ion --no-pore (σ_e 전용)
```

정본 축 = `scripts/run_contract.py`.
★ **모든 산출 JSON 은 `measure_provenance.provenance()` 로 `code_sha` 를 봉인한다** (CL-75).
`code_dirty = true` 인 산출물은 **인용 금지**다.

### 런 전 봉인할 입력 SHA

```
DEM dump  ·  AM scaffold CSV  ·  SE scaffold CSV  ·  materialized phase 배열  ·  fibre 배열
```

✅ **확보됨** — `docs/data/phase_a_6mah/` (§9-0 에 SHA).  덤프(21 MB)·메시는 리포에 넣지 않고
**SHA 로 봉인**했다; 스캐폴드 CSV 와 덱만 커밋했다.

---

## 6. Secondary (Lee) 의 알려진 한계 — 런 전 명시

⚠ **`--add-recipe` 는 AM:SE 입력을 무시하고 실제 scaffold 비를 쓴다** (help 문자열 자신이
*"the AM:SE in the recipe is IGNORED"* 라고 적는다).
⇒ *"Lee 와 같은 조성"* 을 recipe 로 **지정할 수 없다**.  우리 침대의 AM:SE 는 스캐폴드가 정한다
(실측 SE/solid **34.18 vol%**).

⇒ 쓸 수 있는 문장은 *"같은 조성"* 이 아니라
**"첨가제 wt% 를 Lee 에 맞추고, AM:SE 는 우리 스캐폴드 값(실측 34.18 vol%)으로 고정한 대조"** 다.
이 차이를 결과 표에 **반드시 병기**한다.

---

## 7. 예산 (실측 앵커 기반, 벽시계)

| 앵커 | 실측 |
|---|---|
| STEP3 | CL-70 스윕 = **144 솔브 / 경과 69 h** → 28.8 min/solve (SDCP 50×50×72.53 @0.15, LEAN=2, 26.4 M dof) |
| STEP2 | `kit_ps_7_3` @288 mach 0.03 = **6,685 s = 1.86 h** (V100).  ★ 킷 상자 50×50×113.9 ≈ 6 mAh 상자 50.01×50.01×112.87 |

`dof` (세션 §8-3): 0.25 → 10.3 M · 0.20 → 20.2 M · **0.15 → 47.9 M (21.8 GB, LEAN=2 필수)**

| 항목 | 팔 | 시간 (낙관 ~ 보수) |
|---|---|---|
| STEP3 `0.25` | 32 | 6 h |
| STEP3 `0.20` | 32 | 12 ~ 14 h |
| STEP3 `0.15` | 32 | **28 ~ 43 h** |
| STEP3 Lee 대조 | 16 | 14 ~ 22 h |
| STEP3 exact replay | 8 | 7 ~ 11 h |
| STEP2 primary | 4 런 | 10 ~ 19 h |
| STEP2 Lee (mach 0.01) | 1 런 | 7 ~ 17 h |
| **합** | | **82 ~ 130 h = 3.4 ~ 5.4 일** (단일 GPU 직렬) |

병렬: 2대 → 1.7 ~ 2.7 일 · 3대 → 1.1 ~ 1.8 일 · 4대 → 0.9 ~ 1.4 일

### 추정의 가정 (틀리면 어디가 틀렸는지 알 수 있게)

1. **CG 시간 ∝ dof** (낙관) vs **∝ dof × 해방향 셀 수** (보수).  6 mAh 는 앵커보다 **1.56배
   두꺼워** 이 축이 폭의 대부분이다.
2. **첨가제 점 수** ×1.3 ~ 2.5 (VGCF 1 wt% 26.7k 객체 ↔ 4 wt% 110k).
3. **mach 배수** Lee 만 ×3 ~ 5.
4. CL-70 의 69 h 는 **경과**라 대기·큐가 섞였을 수 있다 (있다면 실제는 더 빠르다).

★ **이 추정은 검증 대상이다.**  완주 후 실제 벽시계를 여기 적고 어느 가정이 빗나갔는지 남긴다.

---

## 8. 산출물

```
docs/data/phase_a_6mah/
  step2_<comp>_<sha>.json          첨가제 매니페스트 + add_rng_per_phase
  step3_<comp>_<vox>_<origin>.json σ_e raw + provenance
  verdict.json                     d(h,o,k) 전수 + ORDER-* 판정
                                   (= phase_a_order_verdict.py --dir <arms> --out verdict.json)
```

원장 등재 = 완주 시 새 `CL-` 번호.  ⚠ 판정이 `ORDER-UNRESOLVED` 여도 **똑같이 등재**한다.

---

## 8-1. 실행 도구 (2026-09-07 신설 — 셋 다 selftest 통과)

| 도구 | 하는 일 | 검증 |
|---|---|---|
| `scripts/phase_a_plan.py` | 이 문서의 축을 **실제 명령으로** 펼친다.  아무것도 실행 안 함 | 15/15 |
| `scripts/phase_a_precompute.py` | `d_h/dx` 게이트 + 첨가제 객체 수 (실측 경로) | 9/9 |
| `scripts/phase_a_order_verdict.py` | §2 판정 규칙 — `δ_num` 은 **상수, CLI 로 못 바꿈** | 12/12 |

```bash
python3 scripts/phase_a_plan.py --emit sh > run_phase_a.sh     # 계획 → 스크립트
bash run_phase_a.sh                                            # kgy 에서
python3 scripts/phase_a_order_verdict.py --dir docs/data/phase_a_6mah/arms --out verdict.json
```

★ **계획을 셸이 아니라 파이썬으로 만든 이유** — 리포가 아홉 번 잡은 결함이
*"규약 축이 봉인 문서엔 있는데 **실제 명령엔 없다**"* 이고, 그건 셸로는 시험이 안 된다.
계획을 자료구조로 만들면 selftest 가 그것을 **센다**:

- `--add-rng-per-phase` 가 STEP2 **전부**에 (조성 교락 차단, CL-71/77)
- STEP3 봉인 6항목이 **120 팔 전부**에 · `LEAN=2` 전부에
- primary = mach 0.03 + 승인 플래그 / Lee = 0.01 **승인 없이**
- origin 이 격자마다 `{0, vox/2}³` **전수 8개**
- ★ **QC 는 쌍둥이와 출력 경로만 다르다** = exact replay 의 정의 (§3)
- 출력 경로 120개가 **전부 다르다** (덮어쓰면 팔이 조용히 사라진다)
- 생성된 **셸 문자열**에도 그 축들이 정확한 횟수만큼 있다

⚠ `run_phase_a.sh` 를 **손으로 고치지 말 것** — 고치면 사전등록과 어긋나고 selftest 가 그것을
못 잡는다.  바꿔야 하면 `phase_a_plan.py` 를 고치고 `--selftest` 를 통과시킨 뒤 재생성한다.

---

## 9. 체크리스트 (런 시작 전 전부 ✅ 여야 한다)

- [x] **`d_h/dx ≥ 3.5` 게이트** — ✅ **통과** (아래 §9-1).  라벨 불필요
- [x] **첨가제 객체 수 확정** — ✅ (아래 §9-2).  실측 총량으로 옛 캠페인 4행을 **네 자리까지** 재현
- [x] **6 mAh 스캐폴드 확보 · 커밋 · SHA 봉인** — ✅ `docs/data/phase_a_6mah/`
      ⚠ 옛 침대는 **소실**됐다 (2026-08-25 WSL 유실).  같은 설계점의 **새 DEM 산출물**을
      정본으로 삼았다 — 덤프·덱·메시 SHA 봉인.  자세한 것은 그 폴더의 `README.md`.
- [x] **각도 선별** — ✅ `K_required = 8` · 미접촉 0 개 · z 기울기 없음 (아래 §9-3)
- [ ] `--add-rng-per-phase` 켠 STEP2 4 런 (+ Lee 1 런)
- [ ] STEP3 규약 전 항목 봉인 확인 (`run_contract`)
- [ ] exact replay 8 팔 → `d ≤ δ_num` 확인 (**넘으면 전체 HOLD**)
- [ ] 이 문서 커밋 (**런 시작 전**)

### 9-0. 정본 침대 (2026-09-07 확보)

```
docs/data/phase_a_6mah/{am_scaffold.csv.gz, se_scaffold.csv.gz, in.real_4.liggghts}
atom_2850000.liggghts  sha256 a202b19f6ca9eb80c66434554dc7bb1ac7f3fbfaec6181f5fef103e9c8c10104
in.real_4.liggghts     sha256 900ae9c8f1fde02e83ac86dcee7cca55a10df9ac73e59f15a1ae1516903bfda7
mesh_2850000.stl       sha256 989c3e6426c6a06766aef193f4bd081e1c8c22ce15d3154da0ae513015d2ada9

AM_P 126 (R 6.0 µm) · AM_S 1,372 (R 2.0) · SE 158,651 (R 0.5)
상자 50 × 50 × 113.419 µm · porosity 14.283 % · SE/solid 34.18 vol%
```

⚠ **옛 침대가 아니다** — `input_6mAh_real_4` 의 `atoms.csv` 는 2026-08-25 WSL 유실로 없어졌다.
같은 설계점의 새 realization 이고, **조성은 사실상 같다**: 실측 총량으로 옛 캠페인 객체 수를
계산하면 −0.01 / −0.00 / +0.76 / −0.00 % 로 네 자리까지 맞는다.
⚠ 옛 침대에 기대던 서술(CL-73 의 coverage 반례 등)은 **이 침대에서 다시 재야 한다**.

### 9-3. 각도 선별 — 위험 낮음 (CL-78)

```
cov  p01 0.3254 · p05 0.4003 · 중앙 0.5767 · zero fraction 0.00 %
H    p95 112.5 · p99 141.4 · 무한(c=0) 0 개   ·   A_eff/A_geo 0.5544
dipole 중앙 0.095 · 유효 활성섹터 중앙 41.3 (48 기준)
z-bin  collector 0.5915 → mid 0.5720 → separator 0.5700     ← 기울기 없음
★ K_required = 8    (사전등록 규칙 K · cov_p05 ≥ 3)
```

· **미접촉 입자 0 개** ⇒ 최악 실패 모드는 실현되지 않는다.
· **`K = 8`** ⇒ Codex 사다리 `{1, 12, 48}` 의 **최저단 12 로 이미 충분**.
· ★★ **두께 가설 세 번째 반증** — 113 µm 인데 z 기울기가 없다.  얇은 real14(28.8 µm)가 오히려
  강했다 (0.576 → 0.336).
⛔ 이 선별이 STEP4 HOLD 를 **자동 해제하지 않는다** — 최종 게이트는 여전히
*"조성 간 `q_frac_at_cutoff` < 1 %p 이고 동일 SOC 전압차 < 5 mV"* 이고 실제 런이 필요하다.

### 9-1. `d_h/dx` 게이트 — 통과 (CL-78)

`scripts/phase_a_precompute.py` (selftest 9/9, GPU·스캐폴드 파일 불요).
정본 공식 `fit_dh_collapse.d_h_at_phi` 를 그대로 부른다.

```
총량   V_AM 159,978 µm³ · S_AM 125,965 µm² · V_SE 83,069 · φ_SE_local 0.6723   (실측)
d_h    0.9810 µm   (잔여공극만 0.3215)

 n_grid   192    256   [288]   320    384    448    512
 d_h/dx  3.77   5.02   5.65   6.28   7.53   8.79  10.05      전부 ✅
 ★ 최소 통과 n_grid = 179
```

★ **반경은 가정이 아니라 교차검증됐다** — 12:4:1 규약의 `R_P=6 · R_S=2` 를 넣으면
`p_frac 0.7126` (기록 0.70) 과 `V_AM+V_SE` 가 `V_solid` 와 **−0.65 %** 로 닫힌다.
틀린 반경을 넣으면 스크립트가 **거부**한다 (selftest ②).

⚠⚠ **이것을 STEP3 안전으로 읽지 말 것.**  `d_h/dx` 는 **MPM 의 SE 응력** 게이트다.
STEP3 의 σ 격자는 **다른 질문**이고 거기선 SE neck 이 지배하는데 `h = 0.20 · 0.25` 에서
neck 의 **85.6 % · 97.4 %** 가 2 셀 미만이다 (CL-72).
⇒ **두 게이트의 결론이 반대 방향**이다: STEP2 는 안전, STEP3 의 거친 두 격자는 위험.

### 9-2. 첨가제 객체 수 — 확정 (CL-78)

프로덕션 경로 `additives.recipe_counts_real` (실물 scaffold 질량 기준).
⚠ 세션 §8-4 의 옛 **손계산은 3.7 % 어긋났다** — 이 표가 정본이다.

| 레시피 | VGCF n | PTFE n | VGCF vol% | PTFE vol% | AM wt% | SE wt% |
|---|---|---|---|---|---|---|
| VGCF 1 + PTFE 1 | **26,967** | 2,206 | 1.961 | 1.782 | 80.57 | 17.43 |
| VGCF 2 + PTFE 1 | **54,490** | 2,229 | 3.962 | 1.801 | 79.75 | 17.25 |
| VGCF 3 + PTFE 1 | **82,587** | 2,252 | 6.005 | 1.820 | 78.92 | 17.08 |
| VGCF 4 + PTFE 1 | **111,275** | 2,276 | 8.091 | 1.839 | 78.10 | 16.90 |

검증 — 옛 캠페인 실측 `n_objects` (VGCF 만) 대조, **네 자리까지 일치**:

```
0.5 wt%  13,280 vs 13,281 (−0.01)      1 wt%  26,695 vs 26,696 (−0.00)
2   wt%  53,934 vs 53,529 (+0.76)      4 wt% 110,116 vs 110,120 (−0.00)
```

★ 옛 `case_master` 요약치(SE/solid 33.23 vol%)로 계산하면 **0.58 % 계통 편차**가 났다.
실측 총량으로는 그것이 사라진다 ⇒ **그 요약치가 부정확했고, 이 침대가 옛 캠페인을 더 잘
재현한다.**  (⚠ 그래도 **같은 침대는 아니다** — 다른 realization 이다.)

⚠ **PTFE 는 1 wt% 고정인데 개수가 2,194 → 2,263 으로 3.1 % 는다.**  버그가 아니라 규약이다 —
wt% 는 **AM+SE+첨가제 전체**의 몫이라 VGCF 가 늘면 총질량이 늘고 PTFE 질량도 함께 는다.
⇒ *"PTFE 를 고정했다"* 는 **wt% 고정**이지 **개수 고정이 아니다**.  결과 표에 병기할 것.
