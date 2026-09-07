# 사전등록 — 6 mAh VGCF+PTFE 조성 순서 (Phase A, STEP3)

> 작성 2026-09-07 · 브랜치 `claude/stoic-knuth-NObVQ` · **런 시작 전 커밋 필수**
> 선행 판정 = `codex_verdict_6mah_20260907.md` (Q1 REFUTED · RUN HOLD) — 이 문서가 그 지적을
> 반영한 **재작성판**이다.  옛 초안(요청서 §2)은 폐기.
> 선택된 설계 = **(A) primary 96 팔** (사용자 결정 2026-09-07).

⚠⚠ **결과를 보고 이 문서의 문턱·창·판정 규칙을 바꾸지 않는다.**  바꾸면 사전등록이 무효다.

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

### 실행 순서 — `0.15` 를 **먼저**

```
① h = 0.15   32 팔     ← 원 질문의 완전한 답이 여기 하나에 다 있다
② h = 0.20   32 팔
③ h = 0.25   32 팔
```

★ **역전이 나오면 즉시 `ORDER-UNRESOLVED` 로 중단**한다 (남은 팔을 돌리지 않는다).
`ORDER-ROBUST` 를 주장하려면 96 을 다 완주해야 한다.

⚠⚠ **0.20·0.25 의 해석은 미리 좁혀 둔다.**  오늘 실측(CL-72)에서 SE neck 지름 중앙값이
0.2751 µm 이고 **`h=0.20` 에서 neck 의 85.6 %, `h=0.25` 에서 97.4 % 가 2 셀 미만**이다.
⇒ 그 두 격자는 *"조금 거친 같은 침대"* 가 아니라 **SE 접점 기하가 대부분 사라진 침대**다.
거기서 순서가 유지돼도 쓸 수 있는 문장은 *"격자에 강건"* 이 아니라
**"SE 접점이 지워져도 순서가 남는다"** 뿐이다.

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
| **Primary (순서)** | `0.03` + `--allow-fast-platen` | 상대 순서용 조건부 규약.  위반이 결과 JSON 에 기록된다 |
| **Secondary (Lee 절대)** | `0.01` | 절대 대조에는 준정적 경로가 필요하다.  런타임 3~5× |

⚠ Primary 와 Secondary 는 **재하율이 다르다** ⇒ 두 결과를 나란히 놓을 때 반드시 명시한다.

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

⚠ **6 mAh 스캐폴드가 아직 리포에 없다** — DEM dump 에서 추출해 **커밋한 뒤** 런을 시작한다.

---

## 6. Secondary (Lee) 의 알려진 한계 — 런 전 명시

⚠ **`--add-recipe` 는 AM:SE 입력을 무시하고 실제 scaffold 비를 쓴다** (help 문자열 자신이
*"the AM:SE in the recipe is IGNORED"* 라고 적는다).
⇒ *"Lee 와 같은 조성"* 을 recipe 로 **지정할 수 없다**.  우리 침대의 AM:SE 는 스캐폴드가 정한다
(SE/solid 33.23 vol%).

⇒ 쓸 수 있는 문장은 *"같은 조성"* 이 아니라
**"첨가제 wt% 를 Lee 에 맞추고, AM:SE 는 우리 스캐폴드 값(33.23 vol%)으로 고정한 대조"** 다.
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
```

원장 등재 = 완주 시 새 `CL-` 번호.  ⚠ 판정이 `ORDER-UNRESOLVED` 여도 **똑같이 등재**한다.

---

## 9. 체크리스트 (런 시작 전 전부 ✅ 여야 한다)

- [x] **`d_h/dx ≥ 3.5` 게이트** — ✅ **통과** (아래 §9-1).  라벨 불필요
- [x] **첨가제 객체 수 확정** — ✅ (아래 §9-2).  옛 캠페인 4행을 0.58 % 로 재현
- [ ] 6 mAh 스캐폴드 추출 · **커밋** · SHA 기록  ← **유일한 블로커**
- [ ] 각도 선별 두 endpoint (스캐폴드 오면 수 분, GPU 불요)
- [ ] `--add-rng-per-phase` 켠 STEP2 4 런 (+ Lee 1 런)
- [ ] STEP3 규약 전 항목 봉인 확인 (`run_contract`)
- [ ] exact replay 8 팔 → `d ≤ δ_num` 확인 (**넘으면 전체 HOLD**)
- [ ] 이 문서 커밋 (**런 시작 전**)

### 9-1. `d_h/dx` 게이트 — 통과 (CL-78)

`scripts/phase_a_precompute.py` (selftest 9/9, GPU·스캐폴드 파일 불요).
정본 공식 `fit_dh_collapse.d_h_at_phi` 를 그대로 부른다.

```
총량   V_AM 159,978 µm³ · S_AM 125,965 µm² · V_SE 80,401 · φ_SE_local 0.6574
d_h    0.9710 µm   (잔여공극만 0.3327)

 n_grid   192    256   [288]   320    384    448    512
 d_h/dx  3.73   4.97   5.59   6.21   7.46   8.70   9.94      전부 ✅
 ★ 최소 통과 n_grid = 181
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
| VGCF 1 + PTFE 1 | **26,813** | 2,194 | 1.971 | 1.792 | 81.03 | 16.97 |
| VGCF 2 + PTFE 1 | **54,179** | 2,216 | 3.983 | 1.810 | 80.20 | 16.80 |
| VGCF 3 + PTFE 1 | **82,115** | 2,239 | 6.037 | 1.829 | 79.38 | 16.62 |
| VGCF 4 + PTFE 1 | **110,639** | 2,263 | 8.134 | 1.849 | 78.55 | 16.45 |

검증 — 옛 캠페인 실측 `n_objects` (VGCF 만) 대조, 최대 |Δ| **0.58 %**:

```
0.5 wt%  13,204 vs 13,281 (−0.58)      1 wt%  26,542 vs 26,696 (−0.58)
2   wt%  53,626 vs 53,529 (+0.18)      4 wt% 109,487 vs 110,120 (−0.57)
```

잔차 0.58 % 는 `V_solid` 닫힘 오차 0.65 % 와 **같은 크기** = 공식이 아니라 기하 입력 몫이다.

⚠ **PTFE 는 1 wt% 고정인데 개수가 2,194 → 2,263 으로 3.1 % 는다.**  버그가 아니라 규약이다 —
wt% 는 **AM+SE+첨가제 전체**의 몫이라 VGCF 가 늘면 총질량이 늘고 PTFE 질량도 함께 는다.
⇒ *"PTFE 를 고정했다"* 는 **wt% 고정**이지 **개수 고정이 아니다**.  결과 표에 병기할 것.
