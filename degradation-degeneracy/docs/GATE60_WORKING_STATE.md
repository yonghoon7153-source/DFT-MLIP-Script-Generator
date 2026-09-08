# 60차 게이트 리뷰 작업 상태 (정본)

판정: **NO-GO** (2026-09-08). P0 13건 · P1 4건.
대상 head `ae4ef19069c0343888ff9761ea45fffcc7d07e1c` · RUN_SCOPE `7e03cb19` ·
`source_digest 4fe8d27269ca9ca2` (실측 일치 확인됨).

리뷰어가 **새 발견으로 세지 않은 것**: 요청문 §0 의 미착수·신고 항목,
환경 결손(`pybamm`·`tqdm` 부재)으로 인한 전체 회귀 실패 2건.
`--check-preimages` 는 통과. 커밋된 coverage 합집합은 **리뷰어 환경의 receipt 가
달라 fail-closed** 했고, 그래서 전수 재생 증거도 통과로 옮겨 적지 않았다.

## 판정이 말하는 공통 형태 넷

1. capability 의 **발급·소비 authority 가 안 닫혔다** — raw sink/mint 공개, 소비한 nonce 생존.
2. handle 검사가 **실제 pathname 출력이 다 끝난 뒤** 온다.
3. `lstat` 와 Python object snapshot 은 각각 **bind mount** 와 **referent 후속 교체**를 못 막는다.
4. producer 의 "실행된다가 기본" 에 **parameter provenance · lexical scope · compound head · vararg annotation · module `__doc__`** 가 빠졌다.

## 발견 원장

| ID | 조건 | 무엇이 틀렸나 | 묶음 | 상태 |
|---|---|---|---|---|
| P0-1 | M2 | 정상 `all → report` 가 `analysis_manifest.yaml` 을 늦게 써서 content id 가 바뀌고 class 가 사라진다 → **정상 실행이 마지막에 거부됨(가용성 결함)** | α | **GREEN** |
| P0-2 | M1 | 공개 `record_execution_class(run_dir, cls,…)` raw sink · `issue_execution_class(…, cls,…)` unrestricted mint · `_ISSUED_EXEC_CAPS` 가 caller 의 **같은 mutable object** 를 증인으로 씀 | β | **GREEN** |
| P0-3 | M1·M5 | commit/거부 뒤 **nonce 가 살아 있고** `dir_fd=None` 이라 두 번째 호출이 미판정 자리를 canonical 로 굳힌다 | β | **GREEN** |
| P0-4 | M5 | capability fd 는 마지막 commit 에만 닿는다 — grid chunk/parquet/manifest 는 pathname 으로 쓰여 bind swap 시 **밖에 이미 바이트가 남는다** | γ | **GREEN** |
| P0-5 | M6·M10 | `_claims`/`_attempts` root 가 pathname 유도라 **부모 symlink** 를 따라 frozen tree 에 token·claim 을 쓴다 | δ | **GREEN** |
| P0-6 | — | lifecycle journal temp 가 unchecked `write_text` — **short write 뒤에도 freeze 성공**, head 는 메모리 record 로 만든다 | δ | **GREEN** |
| P0-7 | M8 | `lstat` walk 가 **bind mount 된 밖의 파일**을 평범한 inode 로 센다 | ε | **GREEN** |
| P0-8 | M8 | `payload_index` 가 bundle member 일 필요가 없다 — repo 안 gitignored 경로여도 `full_bundle` | ε | **GREEN** |
| P0-9 | M9 | dict 는 snapshot 하지만 **그것이 가리킨 bundle** 은 안 한다 — 검증 뒤 ledger commit 전 member 교체 성공 | ε | **GREEN** |
| P0-10 | M11·M17 | parameter/default 가 module·resolver provenance 를 지운다 (`namespace=sc` · caller 가 `sc`·`getattr` 을 전달) | ζ | **GREEN** |
| P0-11 | M17 | `_binding_shadows()` 가 `ast.walk` 로 **중첩 scope 의 parameter** 를 바깥에 적용 + subscript callee 우회 | ζ | **GREEN** |
| P0-12 | M12 | compound **head**(`If.test`·`While.test`·`For.iter`·`With`·`Match.subject`) 와 **vararg/kwarg annotation** 이 import-time 밖 | ζ | **GREEN** |
| P0-13 | M12 | module docstring 은 버리면서 **`__doc__` 접근은 허용** — 문서 문자열로 값이 흐른다 | ζ | **GREEN** |
| P1-1 | M3·M13 | hardlink 게시가 temp alias 를 남기고(`nlink=2`) unlink 실패를 삼킨 채 성공 | η | **GREEN** |
| P1-2 | M9 | `phase_done()` 이 caller dict 를 **lock 밖에서 검사하고 같은 reference 를 나중에 직렬화** | ε | **GREEN** |
| P1-3 | M14 | startup 에서 실행됐다 `sys.modules` 를 떠난 byte 를 probe 가 못 본다 | θ | **GREEN** |
| P1-4 | M15 | full receipt 가 **startup 뒤 import 되는 byte** 를 안 담는다 | θ | **GREEN** |

## 묶음

| 묶음 | 축 | 발견 |
|---|---|---|
| α | 내용 identity 의 **시간** — 어느 시점에 봉인하는가 | P0-1 |
| β | capability 의 발급·소비 authority | P0-2 · P0-3 |
| γ | 산출을 **capability 아래에서** 쓴다 | P0-4 |
| δ | lifecycle root 의 물리 좌표 · journal 의 checked write | P0-5 · P0-6 |
| ε | bundle 의 물리 담김 · immutable 게시 · snapshot 범위 | P0-7 · P0-8 · P0-9 · P1-2 |
| ζ | producer identity 의 평가 표면 | P0-10 · P0-11 · P0-12 · P0-13 |
| η | 한 이름 게시 (hardlink alias) | P1-1 |
| θ | 실행이 실제로 올린 byte 의 closure | P1-3 · P1-4 |

## 규율 (이 라운드에도 적용)

- 발견마다 **RED 를 먼저 눈으로 본다**. 리뷰어 반례는 그대로 회귀로 고정한다.
- 방어를 옮기면 **변이 축이 죽는다**. 묶음마다 `--check-preimages`, 마감에 12조각 전수.
- 새 시험이 처음부터 통과하면 fixture 가 진실을 가린 신호다.


## 진행 기록

### α (P0-1) — 내용 identity 를 **시간에** 결속 · `99e6e695`

`commit_run_outputs()` 가 등록보다 먼저 그 순간의 manifest 목록·digest 를
`.run_identity.json` 에 봉인하고, 이후 독자는 전부 그것에서 유도한다. 봉인 값은
봉인 시점의 v3 값과 **같다** — 봉인은 값을 바꾸지 않고 얼린다.

**두 번 정정했다 (둘 다 실측이 뒤집었다).**
① "한 번만 봉인" → 정상 재개가 죽었다 (run 디렉터리는 여러 phase 가 이어서 쓴다).
   → **굳히는 순간마다 다시 봉인** (read-back 뒤 원자적 대체).
② "낡은 봉인은 거부" → cross-process e2e 가 죽었다 (fit 이 자기 gate 를 지나는
   시점에는 재봉인 기회가 없다). → **낡은 봉인은 무시**하고 지금 manifest 로
   계산한다. 그 값은 등록부에 없으므로 승격은 여전히 거부된다 (= 60차 이전과
   같은 의미). P0-1 을 고치다 같은 종류의 가용성 결함을 두 번 만들었다.

### β (P0-2·P0-3) — 발급·소비 authority · `a3ab13ff`

- raw sink 비공개화 + **callsite 열거** 구조 회귀.
- mint 에서 `cls` 제거 → `_decide_execution_class()` (계획 gate 면제와 같은 함수).
- 권한 객체는 **일련번호만**. 정본은 프로세스 안의 발행 기록 `_IssuedExecCap`.
- 소비는 `issued → consuming` 원자 전이. 성공 시 영구 폐기, 실패 시 `issued` 로
  되돌리되 **결속은 유지** (bound → unbound 상태를 만들지 않는다).
- 죽은 변이 축 2건 재조준.

### γ (P0-4) — 산출을 **판정한 실물 아래**로 · 진행 중

- `_open_judged_dir()` 가 **자리를 만들고** handle 을 잡는다. 59차가 신고한
  "자리가 없으면 handle 이 없다" 는 드문 모서리가 아니라 **production 의 정상
  경우**였다 (grid 는 `mkdir` 보다 먼저 gate 를 지난다). 즉 그 한계 아래에서
  handle 은 언제나 없었고, "권한이 대상을 나른다" 는 말은 아무것도 안 날랐다.
- `staged_root(cap)` = `/proc/self/fd/N`. grid·fit 의 gate 이후 **모든 쓰기**가
  그 아래로 간다. writer(pandas·yaml)를 안 고치고도 전부가 handle 아래로 온다.
  한계: Linux 의 성질이고 이 프로세스 안에서만 뜻이 있다 — 요청문에 적는다.
- **이름은 따로 들고 간다**: 기록(`out`)·다음 phase 가 여는 자리·commit 의
  "이 이름이 아직 판정한 대상인가" 검사는 전부 이름으로 한다.
- handle 없음은 이제 **통과가 아니라 거부**다 (59차의 조용한 통과가 P0-3 둘째
  반례의 마지막 한 걸음이었다).

### δ (P0-5·P0-6) — lifecycle root 의 좌표 · journal 의 checked write

**P0-6.** `_write_all_checked()` + `_publish_bytes_checked()` 를 만들고 journal 과
head 를 **같은 계단**에 올렸다 (write-all → fsync → 정확한 read-back → 대체 →
최종 read-back → 부모 fsync). anchor 는 이제 **디스크에서 다시 읽은 journal** 의
마지막 줄에서 유도한다 — 59차까지는 메모리의 의도 record 를 해시했고, 그러면
anchor 는 "들어갔어야 하는 것" 을 가리킨다 (증거가 아니라 주장).

*시험 하나를 버렸다*: 처음 쓴 "head 가 journal 마지막 줄과 같은가" 는 **처음부터
통과**했다 — 두 값을 같은 식이 만들므로 아무것도 구별 못 한다. 잘림이 아니라
**변조**(같은 길이·다른 내용)를 주입하는 시험으로 바꿨다.

**P0-5.** `_lifecycle_root()` 하나로 합치고 root 자신을 본다: ① `lstat` 로 alias
거부 ② 없으면 `mkdir` (그 자리에 symlink 가 있으면 `EEXIST` → ①이 잡는다) ③
**얼린 좌표를 덮고 있으면 거부** (symlink 가 아닌 길 — bind·이동 — 로도 같은
해악이 서므로 이름이 아니라 대상의 좌표를 묻는다).

죽은 변이 축 1건(`claims-root-comes-from-the-ledger`) 재조준.

### ε (P0-7·P0-8·P0-9·P1-2) — 묶음의 물리적 담김 · `23699f02`

- **P0-7**: 구성원이 묶음 뿌리와 **같은 mount 인지** 커널에 묻는다
  (`_kernel_mount_id`). `lstat` 는 bind mount 를 평범한 inode 로 보고
  `Path.resolve()` 는 namespace 안의 철자만 증명한다. 회귀는 리뷰어와 같은
  방식으로 `unshare -Urnm` 안에서 실제 bind mount 를 건다.
- **P0-8**: index 를 **구성원**으로 강제 + index 가 이름한 집합과 실제로 걸은
  집합의 **양방향** 대조. index 형식이 구성원을 열거하지 않으면 그 대조는
  건너뛴다 (억지 해석으로 틀린 집합을 만드는 것보다 정직하다).
- **P0-9**: `bundle_content_id()` 를 만들고 `finalize_leg()` 이 봉인에 넣는다.
  **한계**: mutable directory 인 한 "검증 → 봉인" 창 자체는 안 없어진다.
- **P1-2**: `phase_done()` 이 진입 즉시 정규 바이트로 굳힌다 (M9 와 같은 규칙).

### ζ (P0-10·P0-11·P0-12·P0-13) — producer identity 의 평가 표면

- **P0-12**: compound **head**(`If.test`·`While.test`·`For.iter`·`With` 의
  context·`Match.subject`)와 **vararg·kwarg 주석**을 실행 슬라이스에 넣었다.
- **P0-11**: shadow 를 **scope 별**로 (`_scoped_shadows()`). 59차는 `ast.walk`
  로 중첩 함수의 매개변수까지 한 set 에 합쳐 바깥 load 에 적용했다.
- **P0-10**: 두 번 고쳐 잡았다.
  - 첫 판은 "shadow 인 대상은 증명 아님" 으로 **통째로 거부**했는데,
    `getattr(df, 'columns')` 같은 정상 속성 읽기가 죽었다 (59차가 일부러 지킨
    자리다). 실측으로 되돌렸다.
  - 대신 **이름 공간 고정점을 넓혔다**: 기본값·`for` 대상·`with as` 로
    **이름 공간이 실제로 흘러든** 결속만 namespace 이름으로 본다.
  - 그리고 **호출자가 준 이름을 부르는 것**(`GET(...)` 에서 `GET` 이 매개변수)
    은 거부한다 — 능력을 매개변수로 넘기면 `caps` 검사가 하나도 안 돌았다.
- **P0-13**: `__doc__` 접근 거부가 첫 판이었는데, **51차 P0-I 가 이미 반대
  방향을 정해 뒀다** ("철자를 막는 것은 종결 조건이 아니다 — 버리는 것을
  없앤다"). 그 수정이 function·class 에만 적용돼 있었을 뿐이다. 그래서
  `_module_defs()` 가 **module docstring 을 `__doc__` 로 묶는다.**

죽은 변이 축 1건(`bundle-uri-must-be-repo-relative-g58`, 원상이 2회가 됐다) —
묶음 뿌리 해석을 `_bundle_root()` 한 자리로 모아 고쳤다.

### 마감에 남은 기계적 항목

- cohort pin drift (row_projection.py 가 바뀌었다) → g14 freeze → g15
- 검증 영수증 core sha 갱신 (`make_receipt.py paired_fixed5_v4`)
- 12조각 전수 재생 · 전체 회귀 + strict smoke · 요청문

### η (P1-1) — 한 이름 게시

`os.link` + `unlink` 는 잠깐이라도 **이름을 둘** 만든다. 정리가 실패하면(평범한
`OSError` 로도 됐다) 같은 inode 를 가리키는 **쓸 수 있는 두 번째 문**이 남고,
그리로 쓴 값이 등록부의 답이 됐다.

- `renameat2(RENAME_NOREPLACE)` 로 **옮긴다** (ctypes, Linux ≥3.15). 무대체
  보장을 유지하면서 이름은 언제나 하나다 — "정리가 실패하면?" 이라는 물음
  자체가 없어진다.
- 없는 커널에서는 link + unlink 로 물러서되 **정리 실패를 안 삼킨다.**
- 그리고 **읽는 쪽이 `st_nlink == 1` 을 요구한다.** crash 로 남은 alias 는
  게시 경로를 아무리 고쳐도 있을 수 있다.

죽은 변이 축 1건(`execution-class-record-is-exclusive-g58`) 재조준 — 배타
지점이 `O_EXCL` → `link` → `renameat2` 로 세 번째 옮겨 갔다.

### θ (P1-3·P1-4) — 실행이 실제로 올린 byte

- **P1-3**: `sys.modules` 는 **상태**이고 이력이 아니다. `-X importtime` 손자
  프로세스로 startup 이 **실제로 import 한** 이름을 전부 받고(그 뒤 지워도 로그에
  남는다) 이름마다 파일을 찾아 해시한다.
- **P1-4**: `PYTHONPATH` 를 **문자열로만** 담던 것을, 그 자리의 **최상위 module
  바이트**로 담는다. 더 깊은 package 는 실제로 import 될 때 위 이력이 잡는다.
- 반대 방향 시험도 뒀다 — 무관한 파일 하나에 영수증이 움직이면 그 층은 경계가
  아니라 잡음이다.

**남는 한계**: 이것도 "실행이 소비한 바이트 전부" 는 아니다. 종결은 독립
replay 이고 이 라운드의 범위 밖이다 — 요청문에 적는다.

## 마감 진행

| 단계 | 상태 |
|---|---|
| 변이 등록부 60차 축 14개 | **완료** — MUTANTS 188 · EXPECT 210, 14축 전부 뭄 (`b37a7aae`) |
| g14 freeze → g15 · 투영 재생성 · 영수증 | **완료** (`f79840bc`) |
| 12조각 전수 재생 | 진행 중 — `30816e10` 에서 **1조각부터 다시** (아래 참조) |
| 전체 회귀 + strict smoke | 대기 |
| 요청문 | 초안 완료 (스크래치패드) — §2 증거만 남음 |
| webapp · 원장 | 대기 |

### 세대 전환 실측

```
g14_2026_09_08  active → frozen  (journal seq 13)
g15_2026_09_08  새 active · docs/22p_gap/proj_g15

pin        compute c02b963e5d65bb55 → 3b94bda70dc63869
           row_projection c9bdaa2b33ad6ed4 → a425da3233253625
           producer_semantic 1c768c143c35e43c → 6518c2fa47f1e8c4
           src_scoring 69e69cb046f4b4ae (변동 없음)
영수증      core c9b41978002d46fb… → d15881088e022ce6…
validator  4fe8d27269ca9ca2 → d29650980daf6b9a
행 바이트    ad598fe77e75afec — **열한 세대째 같다**
```

`evidence.cohorts` 갱신은 **g15 의 구성원에게만** 해야 한다 — 처음에 전체 다리에
넣었다가 "cohort 선언이 양방향으로 맞지 않는다" 로 lint 가 잡았다.

### 변이 축 두 건이 false-green 이었다

- `grid-writes-under-the-handle-g60` — 겨누는 자리가 시험이 부르는 함수가 아니었다.
- `bundle-members-share-the-root-mount-g60` — probe 가 저장소 뿌리를 **상수로 박아**
  sandbox 안에서도 원본을 import 했고, 게다가 `unshare` 가 안 되는 환경에서는
  통째로 **건너뛰어진다**. probe 가 지금 실행 중인 트리를 쓰게 고치고, 좌표 비교
  자체를 겨누는 시험을 하나 더 뒀다. **건너뛴 시험은 방어를 지키지 않는다.**

### 전수 재생이 잡은 것 — 시험 하나가 자기 축을 안 보고 있었다

`bundle-members-are-not-followed-g59` 조각(2/12)이 이렇게 멈췄다:

```
… 빨개졌지만 **선언한 이유**가 아니다 — 증인 '… 저장소 밖을 가리키는 link 가
묶음 구성원으로 통과했다 …' 이 실패 메시지에 없다
("… payload index 가 묶음 안에 없다: index.json … (60차 P0-8)")
```

`test_a_bundle_member_symlink_can_not_smuggle_bytes_from_outside` 의 fixture 가
payload index 를 묶음 **밖**(`repo/index.json`)에 두고 있었다. 60차 P0-8 이
"index 는 구성원이어야 한다" 를 넣은 뒤로 이 시험은 **변이를 심든 안 심든**
같은 이유로 빨개진다 — 즉 symlink 방어를 아무것도 지키지 않는 상태였다.

`test_a_bundle_of_plain_files_still_passes` 에는 P0-8 을 닫으며 같은 이동을
이미 적용했는데, 이 쪽은 빠뜨렸다. **방어를 넓히면 그 방어가 다른 시험의
축을 가릴 수 있다** — 이 저장소가 반복해서 겪는 형태다(58차·59차에도 있었다).
고침: index 를 `bundle/index.json` 으로 옮기고 선언 수치를 맞췄다 (`30816e10`).

측정: `pytest tests/test_handle_carry_59.py -q` → 5 passed ·
`mutation_replay.py -k bundle-members-are-not-followed` → 물었다 · ran 1.

전수 재생은 **트리를 고치면 처음부터** 다시 돌린다 — 조각마다 다른 코드에서
난 coverage 는 합집합의 근거가 못 된다.

### 판정 좌표 (실측)

| 항목 | 값 |
|---|---|
| 판정 대상 코드 | `c4e710040c2631d4f8140ee31c2f3c5004d9bcbb` — RUN_SCOPE 를 마지막으로 건드린 커밋 |
| `source_digest` | `d29650980daf6b9a` |
| 대상 이후 RUN_SCOPE diff | 없음 (`git log --oneline c4e71004..HEAD -- src tools configs scripts run.sh requirements*.txt` 이 빈 출력) |
