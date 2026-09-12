# 세션 진행 2026-09-11 ~ 09-12 — litdb 계보 5장 완주 · 압력축 판정 · ban-sweep 사각 발견

> 정본 아님.  판정·규약의 정본은 `CLAUDE.md` 와 `docs/reviews/*`.  이 문서는 **오늘의 수치·판정 대피소**다.

## 1. litdb 정본 브랜치(`claude/friendly-meitner-lldvar`)에 5장

| 카드 | 커밋 | 성격 |
|---|---|---|
| `vijay2025_hybrid_cgmd_dl_slurry_microstructure` | `d36bedcad` | 신규 |
| `galvezaranda2024_time_dependent_dl_calendering_microstructure` | `aac1a2bf8` | 신규 |
| `galvezaranda2025_paml_vgg16_dem_slurry_drying` | `a104784b3` | 신규 |
| `ngandjong2021_dem_calendering_digital_twin` | `0f555ccd3` | **2판** (200 → 757줄) |
| `xu2023_realistic_am_shape_cgmd_calendering` | `2270fab36` · `804270465` | 신규 (846줄) |

⚠ 중복 판정은 전부 `git ls-tree FETCH_HEAD litdb/papers/ --name-only` **전수**로 했다.
`ngandjong2021` 은 `INDEX_DEM.md` 에만 있고 `INDEX.md` 에는 **없었다** — CLAUDE.md 가 적어 둔
"인덱스가 하나가 아니다" 함정이 이번에도 실재했다 (xu2023 커밋에서 `INDEX.md` 구멍도 닫았다).

## 2. ★ 압력축 판정 — 이 계보에 우리 300 MPa 로 옮길 압력값은 **0개**다

- `ngandjong2021` 은 계보에서 **유일하게 MPa 축**을 갖는다: 실험 5점 · 시뮬 7점, **P_max = 156 MPa**.
  우리 Heckel knee `P_y = 138 MPa` 바로 위에서 끝나고 생산점 300 MPa 의 **52 %** 다.
  densification 의 63 %가 5.92 MPa, 99 %가 86 MPa 안에서 끝나 **post-knee 구간에 점이 0개**.
- `xu2023` (후속편, 물리 엔진 원점)은 본문·SI 통틀어 **`MPa` 0회**.  공정 축이 두께감소율(CD %)
  하나로 바뀌었다.  ⚠ 압연기(BPN250)·라인속도(0.54 m/min)·롤온도(60 ℃)가 `ngandjong2021` 과
  **동일**한데 그쪽이 쓴 FlexiForce 갭→압력 환산을 **안 했다** ("못 했다"가 아니다).
- ⛔ 두 카드를 이어 붙여 CD 에 MPa 를 붙이면 안 된다 — 같은 96:2:2 인데 압연 전 실측 porosity 가
  **42.15 %(ngandjong, stated) vs ≈47.5 %(xu, digitized) = 5.4 %p 차** ⇒ 다른 침대다.
- ⛔ **Heckel P_y 인용 금지** — `ngandjong2021` 점을 `ln(1/(1−D)) = K·P + A` 로 옮기면 창에 따라
  408 / 740 / 410 / 1,284 MPa 로 **3.1배** 흔들리고, R² 0.99 인 창은 자유도 1 이다.  게다가 그 ε 는
  **springback 후(out-of-die)** 라 in-die 규약인 우리 `P_y = 138` 과 같은 양이 아니다.
- ★ **살아남는 문장 하나**: *"floor 를 깨는 것은 압력이 아니라 기전이다"* — 86 → 156 MPa(1.8배)에
  Δε = **0.1 %p**.  frame[5] DEM↔MPM 분업에 대한, 우리 데이터가 아닌 **외부 실험** 근거다.
  ⚠ `xu2023` 의 20.4 / 25.0 % 는 **바닥이 아니다** (마지막 구간 기울기 dε/dCD ≈ −0.90 / −0.96 %p/%
  로 가파른 채 끝난다) — 강체구 floor 사다리에 넣지 말 것.

## 3. ★★ ban-sweep 사각 — 정본 litdb 브랜치는 스윕이 **원리적으로 못 본다** (SELF-18)

`claims.json` 의 `quotation_ban` 22 패턴으로 정본 `litdb/` 536 파일을 훑으니 **23 히트**,
그 중 **6 파일이 표지 없는 실사용**이다 (나머지는 철회 서사 자체이거나 무관한 우연 일치).
원장 항목 = `docs/reviews/findings.json` **SELF-18**.

## 4. ibb LHS

- 실측 정정: **다중코어 재시작이 빠르다는 증거가 없다** — 4~5코어 r3 들이 191~435 k스텝/일,
  1코어 r2 들이 214~483 k스텝/일로 **구분되지 않는다** (`OverSubscribe=OK` 로 노드가 이미 포화).
  ⇒ 유휴 코어를 쓰는 것 자체는 타당하나 "몰아주면 빨라진다" 는 근거가 없다.
- `lhsx_*_r2` 18개가 **09-12T15:03 동시 만료**(09-07 시작 + 5일 한도) — 그 시점이 실제 배분 결정점.
- 재시작은 `~/dem_test/dem_restart.py --case-list <CASE> --root ~/dem_test/lhs --suffix r3` 를 쓴다
  (⚠ 2026-09-12 에 내가 sed 로 같은 일을 새로 짰다 = 규율 ① "이 리포에 이미 있나" 위반).

## 5. Phase A vox 0.15 — 32/32 완주, 스칼라 회수, **판정은 거부**

- 캠페인이 09-12 10:32 에 **32/32** 로 끝났다 (중단 2회를 `phaseA_autorun.sh` 가 자동 재개).
- ⚠ **러너 산출물과 판정기 입력 스키마가 애초에 안 맞았다** — 러너는 웹앱 payload
  (`p2_*.json`, 팔당 150 MB, σ_e 가 `mpm_metrics.step3.sigma_e_eff_S_cm`)를 내는데
  `phase_a_order_verdict.py` 는 평평한 스키마를 읽는다.  판정기가 러너보다 먼저 쓰여
  (09-09) 그 사이가 비어 있었고, **32팔을 다 돌리고 나서** `키 없음` 으로 드러났다.
  ⇒ 어댑터 `scripts/phase_a_arms_from_payload.py` 신설 (selftest 15/15, 음성대조 10).
- ⚠ 기존 `reduce_arm_payloads.py` 는 못 쓴다 — **SBE/DBE 2역할 16팔 cohort 전용**이라
  4조성 × 8 origin 을 *origin 중복* 으로 보고 진단 모드에서도 거부한다.  **그 거부는 옳다**
  (표지 없는 부분 cohort 가 `p2_*.json` 이름으로 리포에 들어가는 것을 막는 장치).
- ★ 조성 축은 **원자료에 있다**: `mpm_metrics.additives.VGCF.wt_pct`.  파일명은 교차확인 전용.
- 회수한 팔 = `docs/data/phase_a_h015_arms/arms/` (32) + `run_receipt.json` + 어댑터 요약.

### 판정 = **REFUSED** (설계 64칸 공백)
등록 설계는 `{1,2,3,4} wt% × {0.25, 0.20, 0.15} µm × 8 origin = 96팔` 인데 이번 캠페인은
**vox 0.15 한 격자(32팔)** 만 돌았다.  ⇒ 판정기가 *"부분집합으로 판정하면 조용히 초록이
된다 (CL-71)"* 로 거부한다.  **ORDER-ROBUST 를 주장할 수 없다.**

### vox 0.15 단면 **측정** (판정 아님)
| VGCF wt% | n | 평균 σ_e [S/cm] | 팔-폭 | SE |
|---|---|---|---|---|
| 1 | 8 | 0.0021204 | 2.07 % | 0.211 % |
| 2 | 8 | 0.0152413 | 3.20 % | 0.431 % |
| 3 | 8 | 0.0607626 | 2.18 % | 0.281 % |
| 4 | 8 | 0.130968 | 0.84 % | 0.120 % |

인접 조성 쌍대응비 (같은 origin 끼리): **1→2 7.1878 ± 0.0224 · 2→3 3.9869 ± 0.0077 ·
3→4 2.1555 ± 0.0044** (전부 8/8 쌍).  구간이 **완전분리**된다 (다음 조성의 최소가 앞 조성의
최대보다 7.03 / 3.88 / 2.12 배 크다) 이고 **origin 8개 전부에서 단조 증가**다.
⇒ 이 격자에서 조성 순서는 origin 섭동에 흔들리지 않는다.  ⚠ **한 격자의 서술일 뿐**이고,
격자를 바꾸면 SR-01 에서 σ_ion 비의 **부호가 뒤집힌** 전례가 있다.

★ **plate rule 확인 완료 (2026-09-12, 삭제 전 회수)** — `run_receipt.json` 에는 그 칸이
없어서(`periodic_xy: false` 만 있다) payload 매니페스트를 전수로 읽었다:
**32/32 가 `plate_rule = p2-occupied-surface-first`** 이고 `periodic_xy` 도 32/32 가 False 다.
⇒ R5-CX-06 이 인용을 금지하는 것은 **p1** 산물이므로 이 32팔은 **그 축에 걸리지 않는다.**
전수 기록 = `docs/data/phase_a_h015_arms/phaseA_h015_manifests.json` (32팔 매니페스트 전문).
⚠ 다만 이것이 "인용해도 된다" 는 뜻은 아니다 — **판정은 여전히 REFUSED** 이고, 쓸 수 있는
것은 *"vox 0.15 에서 이렇게 측정됐다"* 는 서술뿐이다.
⚠ receipt 에 `plate_rule` 칸이 **없다는 것 자체**가 구멍이다 — 봉인 축을 receipt 만 보고
확인할 수 없었고, payload 를 지웠으면 영영 확인 못 했다.

## 6. kgy 디스크 (95 % · 여유 50 G)

`~/work` 552 G 는 DFT 라 건드리지 않는다.  우리 쪽에서 정리한 것:
- `~/sdcp` 4 디렉터리 **8.0 G** — 디렉터리명에 박힌 `receipt_digest` 가 리포의 커밋된
  축소 패키지와 일치해 중복이 증명된다 (`3137a340344b` · `ddb33647303c` · `d2be19ea80e4`
  · `2f46127f44a8`) — 넷 다 receipt digest 다.
  ⚠ 리포에 든 축소본은 **스칼라 패키지**라 시각화·재솔브 원자료는 아니다.
- `~/pa/phaseA_h015` 4.6 G — 스칼라 회수 후 삭제 가능 (위 §5).
- ⛔ `prereg_v2_vox04_*` · `prereg_v2_vox015` · `prereg_v2_vox015_sph` 는 이름에 digest 가
  없고 리포에 커밋된 대응본이 **없다** = 유일본이므로 지우지 않는다.

## 7. 원고 v6 · SI v6 의 시뮬 절 대조 (2026-09-12)

### ★ 헤드라인이 커밋된 원자료에서 **정확히 재현된다**
`docs/data/w4_ptfe_centerline_20260827` (8팔, vox 0.15, sphere 스탬프, PTFE centerline):
**SBE 53.987 · DBE 70.605 mS/cm · 쌍대응비 1.307820 ± 0.001053** (팔 범위 70.04–71.40).
원고 Table S3 의 `54.0 / 70.6` 과 일치하고 `plate_rule = p2-occupied-surface-first` 라
**R5-CX-06 의 p1 인용금지에 걸리지 않는다.**
⚠ 혼동 주의 — 같은 vox 0.15 의 **다른** 커밋 패키지
`cohorts/prereg_v2_vox015_sph_b048_ptscenterline_sbrg001_lean2_rd2be19ea80e4_reduced` 는
SBE 가 **같고**(53.987) DBE 만 다르다(71.279, 비 1.3203).  `sbrg001` 축이 SDCP 있는 팔에만
걸리기 때문이다.  ⇒ **원고 출처는 `w4_ptfe_centerline_20260827` 이고 cohorts 쪽이 아니다.**

### 지적 3건
1. ⚠⚠ **σ_SDCP 가 표와 런에서 다르다** — Table S2 는 `256.6 S cm⁻¹ (Measured)` 인데
   **런은 250.0** 을 썼다(매니페스트 전수 확인).  값 차이 2.6 % 는 결과를 못 바꾸지만
   (비 감도로 1e-4 수준), 표가 **런이 쓰지 않은 값**을 적어 재현이 어긋난다.  원장 등재 = SELF-20.
   ★ **동시에 좋은 소식**: CL-61 은 σ_SDCP 를 *"문헌 밴드가 없는 저자 지정값"* 으로 두고
   방어를 감도 스윕에 맡겼는데, Figure S5 의 **4점 탐침 실측**(189 nm 필름)이 생겼다
   ⇒ 그 약점이 닫힌다.  저자 확인 후 CL-61 의 방어 문장을 갱신할 것.
2. ⚠ **σ_ion 절대값에 규약 라벨이 없다** — Table S3 의 `0.553 / 0.558 mS cm⁻¹` 은 복셀 FV 값이라
   **협착(Holm) 항이 없다** (CL-81: `CONTACT_FREE` 상한, 코퍼스 실측 4.04×/6.69×).  같은 SI 에
   실험 `Rion`(Table S4)이 나란히 있으므로 *"협착 미포함 = 상한"* 을 병기해야 한다.
   ★ **상대비교는 안전하다** — SBE·DBE 가 같은 골격을 쓰므로 그 결손이 양쪽에 같은 크기로 걸린다.
   다만 그 **근거를 적어야** 한다 (CL-81: 무근거 "공통모드 상쇄" 금지).
3. ⚠ **porosity 규약 미기재** — Table S3 의 `7.86 / 7.37 %` 가 `ε_sphere` 인지 `ε_union` 인지
   안 적혀 있다.  둘은 이 계에서 **1.25 %p** 어긋난다.

### 확인 대기 2건
- Table S2 는 NCM 전자전도도를 한 값(`1.0×10⁻²`)으로 적는데 런의 상별 표에는
  `AM_S 0.01 / AM_P 0.005` 둘이 있다.  침대가 NCM 단일 반경(2.5 µm)이라 `AM_S` 하나만
  쓰였을 가능성이 크고 표의 값도 그것과 같다 — **침대 시딩에서 sid 를 확인**해 닫을 것.
- `SE coverage of AM 86.6 %` 의 정의(밴드·방식)가 안 적혀 있다.  우리 쪽에 Hertz/Tabor
  두 규약이 있고 값이 크게 갈린다.

### 표가 원장과 맞는 것 (확인 완료)
`σ_VGCF 100 → 78.5` 직경보존 재척도 ✓ (CL-47 의 "압축분말" 라벨도 표에 반영돼 있다) ·
`σ_ion(LPSCl) 3.0e-3` ✓ · `σ_ion(SDCP) 1.0e-3` ✓ · `σ_PTFE = 0` ✓ ·
DEM `E 1.35 / ν 0.3`, MPM `E 1.53 / ν 0.49 / σ_y 0.30` ✓ (전부 `Calibrated` 라벨) ·
PTFE centerline 차단 ✓ · 8 origin 반-복셀 factorial ✓.
