# 58차 게이트 리뷰 요청 — 묶음 9 (실행 전 승인 · 보존 lifecycle)

## 판정 대상 (이 블록이 정본이다)

| 항목 | 값 |
|---|---|
| 브랜치 | `claude/14-gate-code-review-9qkx05` |
| **판정 대상 코드** | **`bbba9aa3`** (RUN_SCOPE 를 마지막으로 건드린 커밋) |
| `source_digest` (RUN_SCOPE `src/ tools/ configs/ scripts/ run.sh requirements*.txt`) | **`920cfd31c22ebe06`** |
| 직전 판정 | 57차 **NO-GO** — P0 9건 · P1 4건 (이 문서에서 L1…L14 로 부른다) |
| 이번 라운드 | 접수 13건 **전부 코드에서 닫음** + 자체 발견 1건(L14) |

> **fetch 는 브랜치 head 로 해 주기 바란다.** 요청문은 자기가 담길 커밋 SHA 를
> 적을 수 없다. 그래서 둘을 나눈다:
>
> - **판정 대상 코드** = `bbba9aa3` — `source_digest 920cfd31c22ebe06` 이 이것을
>   가리킨다.
> - **이 문서** = 브랜치 head. `bbba9aa3` 이후 커밋은 RUN_SCOPE 를 **한 바이트도**
>   안 건드렸다 (아래 재현).
>
> ```
> git fetch origin claude/14-gate-code-review-9qkx05 && git checkout FETCH_HEAD
> cd degradation-degeneracy
> python3 -c "import sys; sys.path.insert(0,'.'); from src.io import source_digest; print(source_digest())"
> # → 920cfd31c22ebe06 이어야 한다. 아니면 그 자체가 발견이다.
> git log --oneline bbba9aa3..HEAD -- src tools configs scripts run.sh requirements*.txt
> # → 출력이 비어야 한다.
> ```

**RUN_SCOPE 밖이지만 이번 라운드가 크게 고친 파일 둘이 있다** —
`docs/22p_gap/row_projection.py` (producer identity) 와
`docs/22p_gap/mutation_replay.py` (변이 재생·증거층). 둘 다 `source_digest` 에
안 들어가지만 **cohort pin 과 변이 등록부의 정본**이므로, 판정에는 브랜치 head
의 그 두 파일을 봐 주기 바란다. 그 사실 자체가 이 저장소의 경계 정의다
(`CLAUDE.md` 하드 룰 3).

---

## §0 먼저 — 이번 라운드가 **하지 않은** 것

| 조건 | 상태 |
|---|---|
| **P0-1** producer 결속 — 닫힌 typed manifest 파싱 · 두 payload 압축해제 재해시 · producer 발행 영수증 | **미착수** (49차부터 **열 라운드째**) |
| trusted launcher 의 source 측정 | **미착수** |
| **P0-4** typed 보존 영수증 **소비** | **부분** |
| 변이 증거의 **독립 replay** | **미착수** — 58차는 증거를 실행 **안**으로 옮겼을 뿐(L11·L12), checker 가 스스로 재생하지는 않는다 |
| 실행 class 5종 중 3종 미구현 · 등록부 삭제 절차 | **미착수** |
| baseline·sweep1d·wsweep 계획 gate · 실물 object-lock adapter · power-loss 모델 · publisher 전용 OS principal | **미착수** |
| 외적타당도 **#50** (`truth_provenance` 를 기계 계약에) | **미착수** |

57차 판정문의 GO 전제 9개 중 **1~8 은 이번 라운드가 닫았고**, 9번(요청문이 이미
신고한 독립 조건들)은 위 표 그대로 열려 있다.

### 이번 라운드가 스스로 신고하는 것

**① 얼린 좌표 봉인(`_frozen_coords/`)은 gitignore 된다 — 기계 지역 사실이다.**
freeze 가 남긴 값은 `(254:0, /home/user/.../proj_g12)` 이고 다른 clone 에서는
장치 번호도 경로도 다르다. 공유하면 죽은 무게이므로 커밋하지 않는다. 대신
clone 에서는 tree 안의 `.FROZEN` marker 와 원장이 그대로 판정하고, 좌표 봉인은
**그 기계에서 일어나는 mount 공격**을 막는 층이다. 층이 기계마다 다르다는
사실을 숨기지 않고 여기 적는다.

**② 좌표 봉인은 `mv` 에 불변이 아니다.** `_fs_identity()` 의 둘째 항은
filesystem 안의 경로이고 경로는 곧 이름이다. 그러므로 이 봉인이 불변인 것은
**같은 대상을 어떤 창(mount·bind·symlink)으로 보는가** 에 대해서이지 **대상을
옮기는 것**에 대해서가 아니다. 실측으로 뒤집혀서 시험으로 못 박아 뒀다
(`test_the_seal_is_not_invariant_under_rename__a_recorded_limit`). 제대로 닫으려면
파일 handle 급 identity 가 필요하고 그것은 이 라운드의 범위 밖이다.

**③ 환경 증언이 재는 면은 좁다.** 실행 파일 바이트 · `site`/`sitecustomize`/
`usercustomize` · `.pth` 뿐이다. `sys.modules` 전체를 재면 `python -c` 와 pytest
child 가 다른 값을 내고, 그러면 **두 증언을 대조할 수 없다** — 그 대조가 L12 를
닫는 방법이다. 시작 뒤 import 되는 코드는 이 면에 없다 (그쪽은 tree digest 와
`inputs` 가 본다).

**④ report 자체를 위조하면 여전히 통과한다.** L12 가 닫은 것은 "report 를 **안
건드리고**" 세탁하는 경로다. 그 한계는 그대로이고, 진짜 해결은 §0 표의 독립
replay 다.

**⑤ 세 변이 축의 EXPECT 는 전체 재생이 아니라 지역 실행으로 쟀다.** 순환이기
때문이다 — `check_coverage()` 는 모든 executable 변이의 EXPECT 를 요구하는데 그
셋의 증인이 바로 그 함수를 부르는 시험이다. 값은 변이를 실제로 적용해 빨개진
node 와 그 assertion 줄 그대로이고, 채운 뒤 전체 재생이 같은 값을 다시 확인한다
(§2-3). 순환을 깬 방식을 숨기지 않는다.

---

## §1 57차 반례 13건 — 전부 재현한 뒤 고쳤다

| # | 57차 반례 | 재현 | 고친 자리 |
|---|---|---|---|
| L1 | production smoke 가 class 를 기록 안 함 + 이동 뒤 legacy migration 이 `canonical` 발급 | ○ | 면제를 말하는 함수 하나(`note_smoke_exemption()`)를 만들고 **조기 return 자리가 반드시 그것을 거치게** — 진입점마다 호출을 더하지 않는다 |
| L2 | `run_content_id()` first-present 충돌 + conflict 삼킴 | ○ | 후보 목록을 늘리지 않고 **적용되는 모든 manifest 를 담은 닫힌 typed descriptor**(`run-content-id/v2`)를 해시 |
| L3 | class 등록부가 CAS 아님 (last-writer-wins) | ○ | 내용당 `flock` + `O_CREAT|O_EXCL` — 배타 지점을 **class 와 무관한 한 자리**로 |
| L4 | bind mount 로 외부 디렉터리가 smoke 면제 | ○ | `is_inside_namespace()` 가 커널 좌표 `(major:minor, fs 안의 경로)` 로 담김을 판정 · 좌표를 못 얻으면 `BoundaryUnknown` 전파 |
| L5 | 가려진 frozen ancestor 가 writable + `_names_for()` 가 `SystemExit` 삼킴 | ○ | **얼릴 때 좌표를 봉인**하고 `_assert_writable()` 이 이름 탐색보다 **먼저** 그것을 조회 · 삼킴은 `BoundaryUnknown` 만 raise 로 |
| L6 | 소비된 phase receipt 를 늦은 writer 가 덮어씀 | ○ | phase receipt write-once (같은 값 재시도만 멱등) + finalize 가 producer-consumer 결속 재검증 |
| L7 | clone 밖 absolute bundle 이 `full_bundle` | ○ | `_repo_relative_or_refuse()` — absolute 하나가 아니라 **담김을 결과로** 확인 (`..` 도 같은 규칙) |
| L8 | directory fsync 실패를 삼키고 issuance 성공 | ○ | `_fsync_dir_strict()` 를 발급 양쪽 자리에 · 실패는 호출자에게 전파 |
| L9 | producer closure — `AnnAssign` RHS · 이름 하나짜리 decorator · 함수 지역 capability alias | ○ | 데코레이터는 **치환**이므로 계산 여부를 안 묻고 무조건 묶음 · AnnAssign/AugAssign 을 module 효과로 · **능력은 부르는 자리에만 나타날 수 있다**(escape 거부) |
| L10 | normal finalize 가 `verifier_origin` 위조 가능 | ○ | `LIFECYCLE_OWNED_EVIDENCE_KEYS` 전체를 caller evidence 에서 거부 |
| L11 | 강제 환경이 transitive code bytes 를 안 묶음 (`sitecustomize.py`) | ○ | 영수증이 **인터프리터를 띄워** 자기가 올린 것(실행 파일·site 계열·`.pth`)의 내용 주소를 받아 온다 |
| L12 | report 안 건드리고 execution evidence 세탁 → 170/170 통과 | ○ | 재생이 sandbox 에 **자기 환경 tag 를 이름에 담은 시험 node** 를 놓고 그 node 가 자기 프로세스에서 환경을 다시 잰다 · checker 는 조각이 주장한 환경에서 tag 를 유도해 report 바이트에서 찾는다 |
| L13 | 회귀 2건이 배선을 안 부름 + 등록부에 신규 방어 anchor 없음 | ○ | top-level `check_coverage()` 를 부르는 회귀 · `_nodes` 가 아니라 **`_run`** 을 태우는 회귀 + 정적 규칙 · 변이 등록부에 **16축**(`-g58`) |
| L14 | (자체 발견) smoke 레코드가 공유 등록부에 쌓여 트리가 더러워진다 | ○ | class 가 자리를 정한다 — smoke 는 gitignore 된 지역 등록부, canonical 은 공유 등록부 |

### 이번 라운드의 형태 — 57차 verdict 가 요구한 "배선을 옮긴다"

57차 판정문은 고칠 자리만이 아니라 **고치는 방식**을 지정했다: "검사를 늘리는 게
아니라 배선을 옮긴다."

| 반례 | 검사를 늘리는 수정 (안 한 것) | 물음을 바꾼 수정 (한 것) |
|---|---|---|
| L1 | 진입점마다 `record_execution_class()` 호출 추가 | 면제를 말하는 **함수 하나**를 두고 조기 return 이 그것을 거치게 |
| L2 | manifest 후보 목록을 늘린다 | 적용되는 **모든** manifest 를 담은 닫힌 typed descriptor |
| L4·L5 | `is_inside_namespace()`·`_names_for()` 에 패턴/후보를 더한다 | 둘 다 **같은 커널 좌표**로 · frozen 은 얼릴 때 좌표를 봉인 |
| L9 | 데코레이터 문법을 하나씩 특례로 | 데코레이터는 조회가 아니라 **치환**이다 (종류가 다르다) |
| L9-b | 별칭 문법을 하나씩 따라간다 | **능력이 어디로 가는지 답할 수 있는가** — 부르는 자리 밖은 거부 |
| L11·L12 | `BOUND_ENV` 를 늘린다 / 필드를 하나 더 검사한다 | 증거를 **실행 안으로** 옮긴다 (실행이 자기 report 에 증언) |

**"방어를 조이면 그것을 증명하던 시험이 무의미해진다."** 이 라운드에서 세 번
겪었고 세 번 다 **실행이** 잡았다: 51차 docstring 시험의 alias 갈래(이제 거부가
정답) · 44차 경계 시험(내 AnnAssign 수정이 class 전체를 묶었다) · 내 L12 시험
하나(변이 감사에서 살아남았다 — report 를 고치면 digest 가 어긋나 **다른 이유로**
거부됐다). 셋 다 통과했다는 사실만으로는 무엇을 증명하는지 알 수 없었고, 변이를
심어야 말해 줬다.

---

## §2 증거

### 2-1 전체 회귀 — **1488 passed · 0 failed · 1 xfailed** (1127.37s, rc 0)

```
$ cd degradation-degeneracy && python -m pytest tests/ -q
........................................................................ [ 96%]
.................................................                        [100%]
1488 passed, 1 xfailed in 1127.37s (0:18:47)
```

등록부 오염 0건 (`_exec_class` · `_frozen_coords` 둘 다). 이 라운드 첫 완전
초록이다 — 그 전까지는 cohort identity 가 낡아 3건이 빨갰고, 그 사실을
`docs/GATE58_WORKING_STATE.md` 에 적어 두고 마감에서 한 번에 닫았다 (트리가
움직이는 동안 증거를 만들지 않는다 — §65 의 교훈).

### 2-2 산출물 identity — g12 를 얼리고 g13 으로

```
compute_sha256            044a87204bfca078 → 0d3e1355383dda14
producer_semantic_sha256  ad36d111337abd39 → 13def6a32e8d9536
row_projection_py_sha256  ad1349257095cbd1 → f55f5ddd6fb7bd2f
src_scoring_py_sha256     69e69cb046f4b4ae (변동 없음)
analysis_spec_sha256      43d74dd3…        (변동 없음)
영수증 core_sha           f24e28e76f309327… → 82f1e6521eda9cf5…
validator source_digest   4a6fd2b664e6902f → 920cfd31c22ebe06
투영                      proj_g12 → proj_g13
```

**행 바이트는 안 움직였다 — 아홉 세대째 같은 값이다.**

```
✅ paired_fixed5_v4: 6138행 · restart 30690행 · proj ad598fe77e75afec
   · 전체 True · by_obj True · fits삼중 True · 봉인일치 True
```

`ad598fe77e75afec` 는 g4 이후 유지돼 온 값이다. 이번 라운드가 고친 것은 실행
class 배선·내용 identity·배타·경계 좌표·영수증 불변성·증거 도메인·durability·
producer 닫힘·증거층이고 **계산식이 아니다.** `src.scoring` 과 analysis spec 이
안 움직인 것도 같은 사실의 다른 면이다. 그래도 **cross-cohort 비교는 금지**다 —
같은 바이트라는 사실은 회귀가 확인하는 것이지 인용의 근거가 아니다.

freeze 는 journal seq 11 로 chain 에 붙었다 (prev `e10102a38f8d1038…`).
`proj_g12/.FROZEN` 이 tree 안에 있고, 이제 좌표까지 봉인된다 (L5).

### 2-3 변이 등록부 — 16축을 심었고, 조각은 **이 HEAD 에서 다시 만드는 중이다**

57차 판정이 지적한 대로 "170/170 exact coverage" 는 **현재 등록부의 완전성**만
말했다. 57·58차가 만든 방어에는 anchor 가 하나도 없었다. 이번에 16축을 심었다
(`-k g58` 로 고를 수 있다):

    L1 실행 class 배선 · L2 내용 identity · L3 배타(MULTI: flock+O_EXCL) ·
    L4 커널 좌표 담김 · L5 얼린 좌표 봉인 · L6 write-once receipt ·
    L7 repo-relative 도메인 · L8 strict fsync(규칙 자신) · L9-a 데코레이터 ·
    L9-b 능력 escape · L10 lifecycle 소유 필드 · L11 startup 증언 ·
    L12 report 환경 증언 · L13-a top-level 배선 · L13-b 재생 환경 ·
    L14 등록부 분리

EXPECT 는 전부 관측값이다 — 13축은 `--emit-expect`, 3축은 지역 실행(§0-⑤).

**지금 커밋돼 있는 `docs/22p_gap/mutation_coverage/s*.json` 12개는 57차 것이고
이 HEAD 에서는 거부된다** (`_assert_trees_are_current` — 이 라운드가
`src/`·`tools/`·`tests/` 를 고쳤으므로 tree digest 가 다르다). 그것이 결속이
살아 있다는 증거이기도 하다. 새 조각 12개는 **이 HEAD 에서** 전수 재생 중이고
뒤따르는 커밋으로 들어간다. 그 커밋 전에는 §4 의 4번 명령이 rc 1 이 정상이다.

조각을 만드는 과정 자체가 두 가지를 잡았다 (커밋 `f983401f`):

| 무엇 | 왜 |
|---|---|
| L5 의 봉인이 57차 변이 `destination-is-compared-in-filesystem-coordinates` 를 **가렸다** | 좌표 비교를 되돌려도 봉인이 먼저 거부한다 → MULTI 에 봉인 조회를 함께 넣었다 |
| 한글 parametrize id 가 **두 철자**를 갖는다 | report 는 `\ucee8…` 로 escape 하고 EXPECT(파이썬 소스)는 그것을 다시 디코드한다 → id 를 ASCII 로 |

둘째는 값이 아니라 **표기 경계**를 건넌 오류다. `--emit-expect` 가 찍어 준 것을
그대로 붙여 넣었는데도 어긋났다.

---

## §3 무엇을 반증해 주기 바라는가

57차가 "170/170 exact coverage" 를 **과대 주장**이라고 지적한 것에 동의한다.
그 문장이 말한 것은 현재 등록부의 완전성뿐이었고 신규 방어의 변이 증거가
아니었다. 이번에 16축을 심었으므로 이제는 다르지만, 그 16축도 **우리가 고른
자리**다. 다음을 특히 겨눠 주기 바란다.

**Q1. 능력 escape 규칙이 producer 자신의 정상 코드를 막지는 않는가.**
"능력은 부르는 자리에만 나타날 수 있다" 는 넓은 규칙이다. 이 트리는 통과하지만
(`test_the_producer_itself_still_hashes`), 정당한 producer 가 쓰고 싶어할 문법을
막고 있다면 그것은 안전이 아니라 고장이다 — 이 라운드에 같은 실수를 한 번 했다
(뿌리 좌표 봉인을 근거 없이 넓게 거부해 54차 회귀를 깼다).

**Q2. 환경 증언 tag 를 재생 없이 만들 수 있는가.** `_write_env_attestation()`
이 심는 시험은 자기 프로세스에서 환경을 다시 재서 baked tag 와 대조한다.
그 node 를 **돌리지 않고** report 에 넣는 경로가 있으면 L12 는 안 닫힌 것이다.
(report 바이트를 직접 쓰는 것은 이미 선언한 한계다 — 그 밖의 경로를 묻는다.)

**Q3. 좌표 봉인의 등록부가 authority 인데 gitignore 된다.** 이 조합이
"등록돼 있다" 의 값을 떨어뜨리는가. 우리 판단은 "그 기계에서만 의미 있는
사실이므로 그 기계에만 둔다" 이고, clone 에서는 `.FROZEN` 과 원장이 판정한다.
이 분리가 틀렸다면 짚어 주기 바란다.

**Q4. write-once phase receipt 의 멱등 예외.** 같은 canonical 바이트의 재시도는
통과시킨다 (crash 복구가 정상 운용이므로). `_canon_json()` 이 같다고 보는데
의미가 다른 두 receipt 가 있는가.

**Q5. 16축 중 L4 두 축은 user+mount namespace 를 요구한다.** 그 환경이 없으면
시험이 skip 되고, skip 은 "관측 안 됨" 이다. 리뷰어 환경에서 그 둘이 어떻게
나오는지 알려 주기 바란다.

---

## §4 검증 명령

```
git fetch origin claude/14-gate-code-review-9qkx05 && git checkout FETCH_HEAD
cd degradation-degeneracy

# 1. 대상 identity
python3 -c "import sys; sys.path.insert(0,'.'); from src.io import source_digest; print(source_digest())"
#   → 920cfd31c22ebe06

# 2. 전체 회귀
python -m pytest tests/ -q

# 3. 변이 등록부가 성립하는가 (지점이 정확히 한 번 나타나는가)
python3 docs/22p_gap/mutation_replay.py --check-preimages

# 4. 조각 합집합이 등록부 전체를 덮는가
python3 docs/22p_gap/mutation_replay.py --check-coverage docs/22p_gap/mutation_coverage/s*.json

# 5. 58차 축만 골라 실제로 무는지 (한 축씩)
python3 docs/22p_gap/mutation_replay.py -k g58 --emit-expect

# 6. strict e2e (clean 커밋에서)
./scripts/smoke_e2e.sh
```

---

## §5 GO 가 나오면 무엇을 하는가

GO 는 **묶음 9 의 본 실행(~10시간)** 에 대한 것이다. 그 전에는 실행하지 않는다.

1. `run.sh` 로 계획 gate 를 지나 leg 를 연다 (`open_leg_run`).
2. 12개 다리를 순서대로 돌린다 — 각 phase 가 receipt 를 남기고, 산출이 굳는
   순간 실행 class 가 기록된다 (L1).
3. finalize → freeze → 새 cohort generation 으로 투영.
4. 결과를 `docs/RESULTS.md` 에 쓰고 다음 게이트를 연다.

GO 전제(§0 표)는 그대로 열려 있다. 그 중 하나라도 본 실행의 **결론에** 영향을
준다고 보면 GO 대신 그 조건을 먼저 요구해 주기 바란다.
