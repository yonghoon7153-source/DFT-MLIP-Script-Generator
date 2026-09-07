# Codex R9 판정 — Phase A **RUN HOLD** (2026-09-07)

기준 스냅샷 `9e66c042`.  요청서 = `codex_request_phase_a_rate_20260907.md`.
원장 = `claims.json` **CL-79**.

> **판정: RUN HOLD.**  과학적 설계 이전에 **실행·판정 배선이 깨져 있고**, Q1 의
> *"동일 재하율·공통모드"* 전제도 코드로 반박된다.

| | 판정 |
|---|---|
| **P0-1** 계획 생성기 | 캠페인을 **시작조차 못 한다** (15/15 초록인 채로) |
| **P0-2** exact replay 게이트 | **fail-open** — 음성대조가 한 번도 발화하지 않는다 |
| **Q1** 재하율 | **REFUTED** — 조성마다 Mach 가 다르다 (dilate-z) |
| **Q2** 게이트 충돌 | **REFUTED** — 두 게이트는 다른 축이다 |
| **Q3** 각도 선별 | **REFUTED** — 전이 안 되고, 봉인 자체가 인용 금지다 |
| **Q4** porosity | **NOT IDENTIFIED** — 알려진 항만으로 닫힌다 |

★ 넷 중 셋이 **내 서술의 결함**이고, P0 둘은 **내가 만든 도구의 결함**이다.

---

## P0-2 ⚠⚠ exact replay 가 fail-open 이었다 (가장 아픈 것)

`phase_a_order_verdict.py` 초판은 QC 팔을 **QC 끼리** 묶고 `len(g) < 2` 를 건너뛰었다.
그런데 계획은 셀마다 **primary 1 + QC 1** 을 만든다 ⇒ 모든 묶음이 길이 1 ⇒ `rows` 가 비고
`passes = None` 이 되어 그대로 순서 판정으로 넘어갔다.

```
PYTHONPATH=scripts python3 -c "import phase_a_order_verdict as v;
  a=v._full(.05)+[v._mk('qc_replay',1,.15,o,9.9) for o in range(8)];
  print(v.verdict(a)['order'], v.verdict(a)['replay'])"

→ ORDER-ROBUST ... 'passes': None          ← QC 를 참값의 **1000배**로 넣어도 통과
```

★★ **내가 false-green 을 막으려고 만든 도구가, 오늘 하루 내내 고쳐 온 바로 그 결함을
갖고 있었다.**  `step3_transport_resolution` 의 끝-누수(CL-74)와 **구조가 같다** — 마지막
원소에서 `all(...)`/`len<2` 가 공허하게 참이 되는 자리.

### 고침 (2026-09-07, selftest 17/17)

QC 를 **primary 쌍둥이와 직접** 비교하고, 셋을 fail-closed 로 바꿨다:

| 조건 | 결과 |
|---|---|
| QC 가 하나도 없다 | **HOLD** — 음성대조 없이 판정하지 않는다 |
| 쌍둥이 없는 QC (orphan) | **HOLD** — 무엇과 비교했는지 못 말하면 음성대조가 아니다 |
| 같은 셀에 QC 중복 | **HOLD** — 어느 것이 replay 인지 모호 |
| `d > δ_num` | **HOLD** (기존) |

신설 테스트 `⑤b~⑤e` 가 위 반례를 전부 문다.  ⚠ 옛 테스트 넷(①②⑤⑦)이 새로 실패했는데
**게이트가 옳게 작동한 결과**다 (그 픽스처에 QC 가 없었다) — 게이트를 약화시키지 않고
픽스처를 계약에 맞췄다.

---

## P0-1 계획 생성기가 실행 불가능한 명령을 냈다 — selftest 15/15 인 채로

```
--add-recipe VGCF=1,PTFE=1        → 파서는 VGCF:PTFE=1:1 만 받는다
STEP2   --save-se --save-phase --save-fibre --save-fibre-dia --save-metrics  없음
STEP3   --se --scaffold --phase --fibre --metrics-json  **전부** 없음
        → 빈 scaffold 의 max() 에서 즉시 죽는다
출력명에 .json 없음 · 판정기는 arms/*.json 만 읽는다
payload 는 σ_e 를 mpm_metrics **아래** 에 두는데 판정기는 최상위를 요구
사전등록 STEP2 봉인축 21 중 **17 미명시** · n_grid 288 vs 실물 킷 256
```

★★ **교훈 — 필수 토큰을 세는 것은 필수 입력이 빠졌는지 확인하는 것이 아니다.**
계획을 자료구조로 만들어 검사 가능하게 한 것은 옳았고, **무엇을 검사할지 고른 것이 틀렸다.**

⇒ `phase_a_plan.py` 는 **실행을 거부**하도록 바꿨다 (selftest 는 기록으로 남긴다).
정본 = `mpm_input_from_case.py` → `run_mpm.sh` → `docs/data/phase_a_6mah/kits/`.

---

## Q1 REFUTED — 조성마다 Mach 가 다르다

내가 *"c_P 는 SE 재료상수라 조성 무관 ⇒ 공통모드"* 라고 **철회했던 것을 다시 철회한다.**
`c_P` 가 상수인 것은 맞지만 **`dilate_z` 가 조성마다 다르고**, 그것이 z 에 곱해져 `WALL0` 을
정하며, 기하 규칙은 속도를 **높이에 비례**시킨다.

```
킷 실측 dilate-z    W1 1.0214 · W2 1.0519 · W3 1.0798 · W4 1.1085   (단조 증가)
Codex 재계산 Mach   W1 0.42745 · W2 0.43928 · W3 0.45010 · W4 0.46123
                    ⇒ VGCF 와 함께 **+7.9 % 단조 증가**
```

⇒ 공통모드가 아니라 **조성축에 걸린 수치적 재하율 축**이다.

### ★ 그리고 *"4.8 % 는 δ_num 의 120배"* 는 **범주 오류**였다

원자료의 `0.1616 → 0.1694` 은 **`final_stress_GPa`** 다 — σ_e 가 아니다 (리포에서 확인).
역학 응력 변화를 **전기 판정 deadband** 와 비교했다.  동역학 민감성 경고 자체는 유효하나
그 배수는 무의미하다.

### Codex 권고

| | |
|---|---|
| **최소 정직한 본 판정** | 네 조성 **전부 고정 Mach 0.03**.  결론은 *"Mach 0.03 생산 규약에 조건부인 순서"* 로 제한 |
| rate 일반화 최소 선별 | `{W1, W4} × {0.03, 0.01}` — 4 STEP2 + 32 STEP3 (계획된 0.03 팔 재사용 시 증분 2 STEP2 + 16 STEP3) |
| 전체 rate 강건성 | 4 조성 × 2 속도 = **8 STEP2 + 64 STEP3** |
| ⛔ 금지 | **기하 규칙으로 바꾸는 개정은 허용할 수 없다** |
| 개정 조건 | smoke 는 날짜와 함께 **exploratory/excluded pilot** 로 남길 것 |

⚠ 내 비용 산술도 틀렸다 — 후보 (b) 를 20~38 h 로 적었는데 실제는 **~70~143 h** 다.

---

## Q2 REFUTED — 두 게이트는 반대 답을 낸 것이 아니다

- `d_h/dx` 는 **STEP2 의 평균적 역학** 해상도 휴리스틱이다.
- 내가 든 neck 분석은 **압밀 전 analytic SE 구**의 **이온** 전도도 대상이다.
  Phase A primary 는 **`--no-ion` 전자** 전도도다 ⇒ **SE-neck 통계는 σ_e 해상도 게이트가 아니다.**
- 같은 침대를 **6-face 규칙**으로 재계산하면:
  ```
  참 접촉 누락      h=.15/.20/.25 → 0.060 / 0.246 / 0.863 %
  가짜 face 접촉    참 접촉 대비   18.06 / 20.93 / 23.28 %
  ```
  ⇒ *"97.4 % 가 2셀 미만 ⇒ 대부분 삭제"* 는 **직접 반증**된다.
- 전자축에서 VGCF 는 **항상 1-voxel tube** 다.  실제 Ø 0.15 µm 대비 단면이
  `h=.15/.20/.25` 에서 **1.27× / 2.26× / 3.54×** 로 바뀐다.  AM bridge 반경도 기본 `1.2h`.
  ⇒ **h 를 바꾸면 오차만이 아니라 전도 feature 자체가 바뀐다.**

⇒ 거친 64 팔은 *"SE 접점이 지워져도 순서가 남는다"* 도, grid convergence 도 증명하지 못한다.
유지한다면 **지정된 h-의존 디지털 규약의 stress test** 로만 둔다.
예산을 줄이면 primary 를 `h=0.15` 32 팔로 좁히고 거친 격자는 **secondary 로 강등**.
⚠ `h=0.15` 도 continuum 수렴이 아니라 **지정 규약에서의 결과**다.

---

## Q3 REFUTED — 각도 선별은 전이되지 않고, 봉인이 인용을 금지한다

- 도구는 **무첨가 강체 AM/SE CSV** 만 읽는다 — STEP2 의 `se_dump.npy`/`phase.npy`/`fibre.npy` 를
  읽지 않는다.
- 생산은 **x/y periodic** 인데 선별 KDTree 에 **periodic image 가 없다**.  독립 9-image
  재계산에서 `p05 0.39985 → 0.46700`, `K 8 → 7`.  (이 경우 K=8 이 우연히 보수적이지만
  **규약이 불일치**한다.)
- ★ `angular_risk.json` 자체가 **`code_dirty = true`** 다 — **내 게이트가 "인용 금지" 라고
  적어 둔 파일을 내가 README·사전등록·CL-78 에서 인용했다** (리포에서 확인).

⇒ 네 조성 **모두의 최종 STEP2 상태**에서 **periodic-aware** 선별을 다시 해야 한다.
비교에는 조성별 다른 K 가 아니라

```
K_common = 등록된 ladder 에서  max_j ceil(3 / p05_j)  이상인 최소 K
```

를 **공통 적용**한다.  선별은 실행예산을 정하는 **필요조건**이고 실제 게이트를 대신하지 않는다.

---

## Q4 NOT IDENTIFIED — porosity 차이에 빠른 재하의 몫은 식별되지 않는다

`14.321 → 13.699 %` 는 알려진 항만으로 닫힌다:

```
높이 효과        +1.253 %p
첨가제 체적      −3.142 %p
union/raster 항  +1.268 %p
```

⇒ *"추가 소성 치밀화"* 를 꺼낼 **잔차가 없다**.  DEM 값은 고정 상자의 해석적 구 부피이고
MPM 값은 조성별 dilation·첨가제 체적·union/raster 규약·최종 wall height 를 전부 포함한다.

⚠ 그리고 **README 는 14.321 을 정본이라 하는데 킷의 `mpm_input.json` 은 14.283 을 적는다** —
단일화가 먼저다.

### 정확한 문구 (Codex 제안, 채택)

> 모든 Phase-A 팔은 동일한 봉인 DEM scaffold 에서 출발하지만, 조성별 dilation · 첨가제 삽입 ·
> MPM settling 을 거쳐 서로 다른 post-MPM bed 가 된다.  DEM 과 MPM porosity 는 분자와 높이
> 규약이 달라 직접적인 치밀화 전후 비교가 아니다.

---

## 다음 (순서 고정)

1. ✅ **P0-2 replay fail-open 수정** — 완료 (17/17)
2. ✅ **P0-1 계획 생성기 폐기** — 실행 거부로 전환
3. ⬜ **porosity 정본 단일화** (14.321 vs 14.283)
4. ⬜ **angular_risk 재측정** — 네 조성 post-STEP2 · periodic-aware · 깨끗한 트리에서 봉인
5. ⬜ **사전등록 v2** — 고정 Mach 0.03 조건부 판정으로 갈지, rate × composition 대조까지
   더할지 결정.  smoke 는 **exploratory/excluded pilot** 로 명기
6. ⛔ **그 전까지 W3·W4 STEP2 시작 금지** (재하율 규약 미정)

⚠ 기하 재하율로 96 팔을 시작하면 안 된다.
