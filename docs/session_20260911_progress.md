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
