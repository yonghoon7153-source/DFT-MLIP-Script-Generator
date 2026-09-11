# 세션 진행 — 2026-09-10 (압축 전 대피소)

> 브랜치 `claude/sdcp-dem-manuscript-si-pqwtv8` · 정본 원장 `docs/reviews/claims.json`
> ⚠ 이 문서는 **오늘의 판정·경위 보존용**이다.  충돌 시 원장과 사전등록이 이긴다.

---

## 1. `probe015` (kgy) — 완주·정상 종료.  멈춘 게 아니다

`~/pa/probe015.sh` 가 **2026-09-09 10:30:03 에 끝났다.**  9/10 09:12 에 확인했으니
22시간 42분째 조용한 것이고, 그것이 정상이다.

| 근거 | 실측 |
|---|---|
| 셸 잡 상태 | `[1]+ Done` — bash 는 **종료코드 0** 일 때만 `Done` 을 찍는다 (죽으면 `Exit N`·`Killed`) |
| 로그 mtime | `2026-09-09 10:30:03.678` 이후 무변화 |
| 프로세스 | `pgrep -af 'step3_sigma\|run_mpm\|phase_a\|probe015'` → 없음 |
| 오류 흔적 | `Traceback`·`Killed`·`MemoryError`·`No space` **0 건** |
| ★ 계획 대비 | `run_receipt.json` 의 **`"arms": 1`** — 1팔이 계획이었고 정확히 1팔(`a0`)이 나왔다 |

⚠ `origins` 에 8개가 적힌 것은 **규약 기록**이지 실행 목록이 아니다.  이 런은 ARMS=1 프로브다.

산출: `~/pa/phaseA_probe015_arm1/p2_VGCF_PTFE_1_1_a0.json` (150.8 MB) · 피크 호스트 RSS 31.2 GB.
규약: `vox 0.15` · `ptfe_stamp centerline` · `sdcp_stamp point` · `sdcp_sphere_d_um 0.0` ·
`bridge_um 0.24` · `fibre_stamp segment` · `periodic_xy false` · `expect_backend gpu`.

**이 팔로 Phase A 판정은 못 한다** — `phase_a_order_verdict.py` 의 fail-closed ① 이
*"설계 격자점이 하나라도 비면 판정하지 않는다"* 인데 지금은 조성 1 × 격자 1 × origin 1 이다.
러너 배너가 스스로 *"이 러너는 팔만 낸다"* 라고 적은 그대로이고, 결함이 아니다.

⚠ 관측 하나는 정체 미상으로 남긴다 — `nvidia-smi` 가 `11039 MiB, 100 %` 를 찍는데
프로세스 조회가 `Process-level GPU information is restricted` 로 막혀 있다.  호스트 RAM 이
5 GB 이고 이 잡은 `Done` 이므로 **이 런은 아니다** (다른 잡이거나 놓지 않은 컨텍스트).

---

## 2. ★ receipt 가 **origin 에 없는 커밋**을 가리키고 있었다 (SELF-17)

`run_receipt.json` 의 `"code_sha": "70b9e37a"` 가 이 리포에서 **풀리지 않았다**
(`fatal: Not a valid object name`).  전 브랜치를 fetch 한 뒤에도 없었다 =
**푸시된 적 없는 커밋**이다 (`+dirty` 가 안 붙었으니 트리는 깨끗했다).

⇒ 그 팔의 코드 정체를 **아무도 되살릴 수 없는 상태**였다.  kgy 가 초기화되면 끝이다
(원장 §19 receipt 계약이 막으려던 바로 그 자리).

### 어디 있었나

| 트리 (kgy) | 브랜치 | 비고 |
|---|---|---|
| `~/Yonghoon-DEM-DFT` | `claude/sdcp-dem-manuscript-si-pqwtv8` | **여기.**  `70b9e37a` 가 HEAD 였다 |
| `~/work/Yonghoon-DEM-DFT` | `claude/friendly-meitner-lldvar` | litdb 정본 트리 — 코드 소관 아님 |

### ⛔ `claude/stoic-knuth-NObVQ` 로는 **보낼 수 없었다**

```
70b9e37a = 머지( d76a93d3 , b449135f )      ← kgy   (stoic-knuth 옛 tip)
4874ad12 = 머지( d76a93d3 , be0ae956 )      ← 이 세션 (stoic-knuth 현 tip)
```

`b449135f` 이후 stoic-knuth 에 **13커밋**이 더 쌓였다 (v3 원장 렌더 · 탄소 앵커 ·
감사 커버리지 정정 · Codex 대응 · 인계 프롬프트).  따라서 `70b9e37a` 를 그 브랜치로
push 하면 **non-fast-forward 로 거부**되고, `--force` 로 밀면 **그 13커밋이 지워진다.**
⇒ 그 길은 막았다.  `--force` 는 이 사안에서 영구히 금지다.

### 그래서 한 것 — 박제용 새 ref 하나

```
git push origin 70b9e37a:refs/heads/claude/phase-a-96arm-kgy
```

kgy 의 **HEAD·추적설정·워크트리를 하나도 건드리지 않는다** (런 트리가 `code_sha` 를
정하는 자리이므로).  이것으로 receipt provenance 가 닫혔다.

### ★ 그리고 그 커밋은 **내용을 하나도 안 들고 있다** (실측)

```
git log --oneline b5db1639..70b9e37a      →  70b9e37a 한 줄뿐
d76a93d3 · b449135f                       →  둘 다 b5db1639 의 조상
git merge-tree --write-tree b5db1639 70b9e37a
  →  105ea5b363d3df38857e9390b867bc4282547033
git rev-parse b5db1639^{tree}
  →  105ea5b363d3df38857e9390b867bc4282547033      ★ 동일
```

### ★★ 그리고 등록부가 **스스로 낡았다** — 설계대로

어제 세션은 이 sha 를 `docs/reviews/doc_refs_sha_exceptions.tsv` 에 사유와 함께 등재해 뒀다:
*"kgy 로컬 머지 커밋 — 원격에 없다 … 이 리포에서 **도달 불가한 것이 정상이다** (CL-88)"*.
오늘 push 로 도달 가능해지자 `check_doc_refs` 가 **즉시 그 등재를 낡았다고 지적**했고
(등록부 머리의 ⓐ 조항), 같은 커밋에서 지웠다.  검사 기계는 흠이 없다.

⛔ 흠은 **사유 쪽**이다 — *"도달 불가한 것이 정상이다"* 가 정상이 아니었다.  한 줄 push 로
닫혔고, 닫고 보니 내용이 0 이었다.  **예외가 최후 수단이 아니라 안착 상태로 쓰인 것**이고
그것이 `SELF-17` 로 열려 있다.

⇒ `70b9e37a` 를 공용 브랜치에 **합쳐도 파일이 한 개도 안 바뀐다.**  같은 머지를 이 세션이
더 새 재료(`be0ae956`)로 이미 해 뒀기 때문이다.  그 커밋의 유일한 가치는 **receipt 가
그 이름을 부른다**는 것 하나고, 그래서 박제만 하면 충분하다.
⚠ 그러므로 *"kgy 작업분이 유실됐다"* 고 읽으면 안 된다 — 유실된 것이 없다.

---

## 3. 이 세션이 커밋한 것 (2026-09-09~10)

기준: `origin/claude/stoic-knuth-NObVQ` = `be0ae956`.  거기서 갈라져 나와
**`claude/sdcp-dem-manuscript-si-pqwtv8` 에만** 올렸다.  기준 브랜치에는 **아무것도 안 올렸다.**

| SHA | 무엇 |
|---|---|
| `4874ad12` | 기준 브랜치 따라잡기 — stoic-knuth 33커밋 반입 (감사 트랙 AUD-01~07 포함) |
| `8345e866` | **AUD-06** 동결 재현기 예외를 경로가 아니라 **내용**(sha256)에 건다 + 거부 **행동** 회귀 |
| `6904d3d9` | 원장 — AUD-06 `claimed_fixed` |
| `986cd84a` | **AUD-05** 면제 근거를 **독자가 실제로 보는 자리**로 좁힌다 (출력 문장 · 보이는 덩어리) |
| `b3e00465` | 원장 — AUD-05 `claimed_fixed` |
| `0dee4f33` | **AUD-07** 감사 원시 finding 에 기계 판독 가능한 판정 상태 (`audit_adjudication_20260909.json`) |
| `b5db1639` | 원장 — AUD-07 `claimed_fixed` |

⚠ **AUD-01·02·03·04 는 손대지 않았다** — 넷 다 물리(dead-AM 문턱)·모델(매트릭스→복합전극
전이)·기록 정책(박제냐 정본이냐)의 **저자 판단**이다.  내가 정하면 그게 곧 지어낸 근거가 된다.

커밋 5회 전부 앞에서 `bash scripts/check_all.sh` 가 초록이었다.

---

## 4. 브랜치 지도 (2026-09-10 현재)

| 브랜치 | tip | 무엇 |
|---|---|---|
| `claude/stoic-knuth-NObVQ` | `be0ae956` | 기준선.  ⛔ 이 세션은 여기 푸시하지 않는다 |
| `claude/sdcp-dem-manuscript-si-pqwtv8` | `b5db1639` | 이 세션 작업분 + kgy 의 옛 sdcp 라인 |
| `claude/phase-a-96arm-kgy` | `70b9e37a` | **박제 전용.**  receipt `code_sha` 앵커 (내용 0) |
| `claude/friendly-meitner-lldvar` | — | litdb 정본 (202장).  코드 금지 |

⚠ kgy 의 `~/Yonghoon-DEM-DFT` 는 아직 로컬 HEAD 가 `70b9e37a` 다 (`ahead 1, behind 20`).
**그대로 두는 것이 맞다** — 그 트리가 다음 런의 `code_sha` 를 정한다.  옮기려면 런이 없는
때에, 옮긴 사실을 여기 적고 옮긴다.

---

## 5. ⬜ 남은 것

1. **AUD-01~04 저자 판단** (§3).
2. **`single` 페이지 회귀 미확인** — 분석된 케이스가 있어야 열려서 컨테이너의 `test_ledger_view`
   27·28 이 그 페이지를 못 봤다 (`SKIP 26b` 로 남는다).  실물 케이스가 있는 기계에서 한 번.
3. **SELF-17** — 커밋된 receipt 의 `code_sha` 가 **origin 에서 풀리는지** 검사하는 자리가 없다
   (`check_cohort_packages.py` 는 `code_sha` 를 보지 않는다).  오늘 건은 손으로 잡았다.
4. `probe015` 다음 수 — Phase A 판정을 하려면 설계 격자점을 **전부** 채워야 한다 (fail-closed ①).

---

## 6. Phase A `h = 0.15` 캠페인 — 착수 · 중단 2회 (원인은 **카드 공유**)

10:14 착수.  런처 `~/pa/phaseA_h015.sh` = `probe015.sh` 에서 `KITS`·`ARMS`·`OUTDIR` 세 줄만
바꾼 것 (재구성하지 않았다 — `phase_a_plan.py` 가 폐기된 이유가 그것이다).

### 봉인 (사전등록 §5 와 한 글자도 안 어긋난다)

```
arms 8 · vox_um 0.15 · bridge_um 0.24 · fibre_stamp segment · ptfe_stamp centerline
sigma_ptfe = 0 (미지정 = exact-zero DOF) · periodic_xy false · LEAN 2 (--no-ion --no-pore)
origins = {0, 0.075}³ 완전 factorial       receipt_digest 9fd74d421c84
code_sha 70b9e37a  ← **`+dirty` 없음** (인용 금지 조항 통과)
```

⚠ 러너가 찍는 *"진단 팔 … 생산 규약 아님 (CDXR2-6)"* 은 **SDCP 캠페인** 기준의 말이다.
Phase A 에서는 그것이 **등록된 규약**이고, probe015 도 같은 배너를 찍었다.

### 진행 (2026-09-10 22:57 기준)

| | |
|---|---|
| 완료 | **11 / 32** (가벼운 3킷 24팔 중 11) |
| 속도 | 팔당 **≈ 1.1 h** (14:05 → 22:53 에 8팔) |
| 중단 | 2회 — `4_1_a0` (dof 50.5 M) · `3_1_a3` (3 wt%) |

### ★ 중단 원인 — 조성이 아니라 **GPU 자리**다 (실측으로 닫음)

```
우리 팔 1개        ≈ 9.9 GB   (14:05 실측: 총 14,625 − 확산 3,916 − 표시 0.8k)
확산 잡 1776487      3.9 GB   (tools/modelc_v3/disorder_ensemble_diffus…, 37 h째, 고정)
conda   2444560     14.3 GB   ★ 14:05 엔 없었고 그 뒤에 떴다 — 이것이 3_1_a3 를 죽였다
표시·기타            0.8 GB
────────────────────────────
                    19.0 GB / 24.6 GB  →  남는 5.5 GB  <  필요 9.9 GB
```

2차 중단이 **3 wt%**(최중량 4 wt% 가 아니다)에서 난 것이 조성 가설을 기각한다.
⇒ 처방은 하나 — **재개 전에 카드에 10 GB 이상 비어 있는지 보고 건다.**

★ **봉인이 제 일을 했다** — `--step3-require-gpu` 가 CPU 폴백을 **거부**했다.  안 그랬으면
그 팔 하나만 다른 backend 로 풀려 캠페인에 조용히 섞였을 것이다.  그리고 `SKIP` 캐시 덕에
손해는 매번 in-flight 팔 **하나**뿐이고, 실제로 3 → 11 로 밀었다.

⚠ **영수증은 나눠 돌려도 안 깨진다** — 봉인 축에 `KITS` 가 없어 `receipt_digest` 가 불변이다.
그래서 가벼운 3킷(24팔)과 4 wt%(8팔)를 갈라 돌려도 같은 캠페인이다.

### ⬜ 재개 조건 · 남은 것

1. 카드에 여유 확보 (아래 2026-09-11 갱신의 문턱).
2. 남은 21팔 = 가벼운 13 + 4 wt% 8.  순수 계산 **≈ 23 h**.
3. 32팔 완주 후 `python3 scripts/phase_a_order_verdict.py --dir ~/pa/phaseA_h015`.
   ⚠ 역전이 나오면 `ORDER-UNRESOLVED` 로 **즉시 중단**하고 0.20·0.25 는 안 돈다.

### ★ 갱신 2026-09-11 — 막고 있는 것이 확정됐다.  **저자 결정 = DFT 우선, 캠페인 대기**

시도를 두 번 더 했고 둘 다 같은 팔(`3_1_a3`)에서 죽었다 (15:15 건 것은 **39분을 태우고** OOM).
진행은 **11 / 32 그대로**다.

**막는 것 = Quantum ESPRESSO `pw.x` GPU SCF 루프.**

```
/home/kgy/apps/qe-7.4.1-gpu/bin/pw.x -nk 1 -in scf.in
cwd  ~/work/runs/force_check_700K_v2/b2o3_2_t30ps
드라이버  python …framework_com…   ← 프레임마다 새 pw.x 를 띄운다
```

⇒ PID 가 계속 바뀐 이유가 이것이다 (`2444560 → 2776880 → 2789251 → 2802111`, 매번 **14.1 GB**).
하나가 오래 도는 잡이 아니라 **루프**라 저절로 끝나지 않는다.

★ 별개로, 37시간 돌던 확산 잡(`tools/modelc_v3/disorder_ensemble_diffus…`)은 09-11 오후에
**완주했다** — 3.9 GB 가 풀렸지만 그것으로는 모자랐다 (여유 5.7 → 9.2 GB).

**산수가 닫힌다 — 둘은 같이 못 돈다:**

```
pw.x            14.1 GB  (고정)
Phase A 팔 1개   9.2 ~ 9.9 GB
표시·기타         0.8 GB
──────────────────────────
               24.1 ~ 24.8 GB   >   24.6 GB 카드
```

오늘 세 번 실측으로 확인됐다 (`4_1_a0` · `3_1_a3` × 2).

**⬜ 재개 문턱 (실측 기반 정정)** — `nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits` 가

| 대상 | 필요 여유 | 근거 |
|---|---:|---|
| 가벼운 조성 (1·2·3 wt%) | **≥ 9,600 MiB** | 여유 **9,211** 에서 `3_1_a3` 이 실패했다 ⇒ 옛 문턱 9,300 은 낮았다 |
| 4 wt% | **≥ 10,400 MiB** | 팔 실측 ≈ 9,929 + 여유 |

⚠ **CPU 폴백은 답이 아니다.**  봉인(사전등록 §5 `backend`) 이전에 **대역폭 산수**로 막힌다 —
5천만 dof 희소 CG 는 메모리 대역폭 싸움이고, 3090 ~900 GB/s 대 CPU 수 GB/s 라 팔당 1시간이
**1~2일**이 된다.  21팔이면 몇 주다.

★ 저자 결정 (2026-09-11): **DFT force check 를 먼저 돌린다.**  Phase A 는 11/32 로 세워 둔다.
DFT 루프가 끝나 여유가 위 문턱을 넘으면 `phaseA_h015_light.sh` 재개 → light 13팔 ≈ 14 h →
`phaseA_h015.sh` (4 킷) 재개 → 4 wt% 8팔 ≈ 9 h.  **SKIP 캐시가 11팔을 그대로 받는다.**
