# 59차 게이트 리뷰 요청 — 묶음 9 (실행 전 승인 · 보존 lifecycle)

## 판정 대상 (이 블록이 정본이다)

| 항목 | 값 |
|---|---|
| 브랜치 | `claude/14-gate-code-review-9qkx05` |
| **판정 대상 코드** | **`7e03cb19`** (RUN_SCOPE 를 마지막으로 건드린 커밋) |
| `source_digest` (RUN_SCOPE `src/ tools/ configs/ scripts/ run.sh requirements*.txt`) | **`4fe8d27269ca9ca2`** |
| 직전 판정 | 58차 **NO-GO** — P0 12건 · P1 4건 · P2 1건 (이 문서에서 M1…M17 로 부른다) |
| 이번 라운드 | 접수 17건 **전부 코드에서 닫음** |

> **fetch 는 브랜치 head 로 해 주기 바란다.** 요청문은 자기가 담길 커밋 SHA 를
> 적을 수 없다. 그래서 둘을 나눈다:
>
> - **판정 대상 코드** = `7e03cb19` — `source_digest 4fe8d27269ca9ca2` 이 이것을
>   가리킨다.
> - **이 문서** = 브랜치 head. `7e03cb19` 이후 커밋은 RUN_SCOPE 를 **한 바이트도**
>   안 건드렸다 (아래 재현).
>
> ```
> git fetch origin claude/14-gate-code-review-9qkx05 && git checkout FETCH_HEAD
> cd degradation-degeneracy
> python3 -c "import sys; sys.path.insert(0,'.'); from src.io import source_digest; print(source_digest())"
> # → 4fe8d27269ca9ca2 이어야 한다. 아니면 그 자체가 발견이다.
> git log --oneline 7e03cb19..HEAD -- src tools configs scripts run.sh requirements*.txt
> # → 출력이 비어야 한다.
> ```

**RUN_SCOPE 밖이지만 이번 라운드가 크게 고친 파일 둘** —
`docs/22p_gap/row_projection.py` (producer identity) 와
`docs/22p_gap/mutation_replay.py` (변이 재생·증거층). 둘 다 `source_digest` 에
안 들어가지만 **cohort pin 과 변이 등록부의 정본**이므로 판정에는 브랜치 head
의 그 두 파일을 봐 주기 바란다 (`CLAUDE.md` 하드 룰 3).

---

## §0 먼저 — 이번 라운드가 **하지 않은** 것

| 조건 | 상태 |
|---|---|
| **P0-1** producer 결속 — 닫힌 typed manifest 파싱 · 두 payload 압축해제 재해시 · producer 발행 영수증 | **미착수** (49차부터 **열한 라운드째**) |
| trusted launcher 의 source 측정 | **미착수** |
| **P0-4** typed 보존 영수증 **소비** | **부분** |
| 변이 증거의 **독립 replay** | **미착수** — 59차는 증언의 **범위**를 넓혔을 뿐(M14·M15), checker 가 스스로 재생하지는 않는다 |
| 실행 class 5종 중 3종 미구현 · 등록부 삭제 절차 | **미착수** |
| baseline·sweep1d·wsweep 계획 gate · 실물 object-lock adapter · power-loss 모델 · publisher 전용 OS principal | **미착수** |
| 외적타당도 **#50** (`truth_provenance` 를 기계 계약에) | **미착수** |

### 이번 라운드가 스스로 신고하는 것 (새로 생긴 한계)

**① `if __name__ == "__main__":` 은 producer identity 밖이다 (M12 의 대가).**

이 라운드는 import-time 실행 슬라이스의 기본값을 뒤집었다 — **실행된다**를
기본으로 두고 실행되지 않음을 **증명할 수 있는 것만** 뺀다. 그 증명이 서는
유일한 module-level 분기가 `if __name__ == "__main__":` 이고 (import 는
`__name__` 에 module 이름을 넣는다), 그래서 제외했다.

**남는 구멍**: 투영을 실제로 만드는 것은 이 파일을 **스크립트로 실행**하는
일이고, 그 실행에서는 그 분기가 돈다. 즉 `main()` 안에 계산을 넣으면 identity
밖에서 돌릴 수 있다.

빼지 않으면 어떻게 되는지도 **쟀다**: `raise SystemExit(main())` 한 줄이
producer 닫힘을 93 → 99 로 늘리고 `main`·`argparse`·`_cohort_dir`·
`_frozen_cohort_dirs`·`seal_frozen_cohorts` 를 끌고 온다 — 44차가 그은 게시 경로
경계를 그대로 넘는다. 두 손해 중 후자를 택했고, 근거는 계산 함수가
`_COMPUTE_NAMES` 로 **선언**돼 있고 `main` 은 그것을 부르는 자리라는 것이다.
더 나은 답이 있으면 그것이 이 항목의 반증 조건이다.

**② 실행 class 권한의 handle 은 gate 시점에 자리가 있을 때만 잡힌다 (M5).**

`issue_execution_class()` 는 판정한 디렉터리를 `O_DIRECTORY|O_NOFOLLOW` 로 열어
`dir_fd` 를 들고 간다. 그런데 gate 는 산출을 만들기 **전에** 도는 것이 정상이고,
그때 자리가 아직 없으면 handle 이 없다 (`dir_fd=None`). 그 경우 굳히는 자리는
이름으로 연다 — 판정과 쓰기 사이의 창이 그만큼 남는다.

없음을 없음으로 나르고 (있다고 말하지 않는다) 그 사실을 여기 적는다. 제대로
닫으려면 gate 가 자리를 **만들고** handle 을 잡아야 하는데, 그러면 "gate 는
거부하기 전에 아무 부작용도 만들지 않는다"(47차 조건 11-c)와 충돌한다. 두 성질을
같이 만족시키는 설계를 이 라운드에 못 찾았다.

**③ 능력 escape 규칙의 정밀도를 올렸다 — 그 자체가 완화다 (M17).**

리뷰어 Q1 의 답은 "그렇다" 였다: 58차 규칙은 능력과 **철자만 같은** 매개변수
(`def f(vars)`)나 남의 객체 속성(`df.vars`)도 거부했다. 판정을 철자에서
**결속**으로 바꿨다 — 호출자가 값을 주는 자리(매개변수·`for`·`with as`·
`except as`·내포)로 묶인 이름은 능력이 아니고, 속성은 뿌리가 import 한 module
일 때만 능력이다.

**평범한 대입(`GET = getattr`)은 여전히 거부한다** — 58차 L9-b 가 닫은 축이고,
값을 모르는 대입까지 열면 그 구멍으로 되돌아간다. 매개변수를 면제해도 되는
근거: 호출자가 진짜 능력을 넘기려면 자기 자리에서 능력을 **부르는 자리 밖**에
써야 하고, 그 호출자도 닫힘 안이면 거기서 걸린다. 닫힘 밖 호출자는 애초에
identity 밖이다. 이 논증이 틀렸다면 그것이 반증 조건이다.

**④ 좌표 봉인은 여전히 기계 지역이다 — 다만 이제 그것을 강제한다 (M6).**

58차가 신고한 대로 `_frozen_coords/` 는 gitignore 된다. 59차가 확인한 것은 그
층이 **이 기계에서조차 거의 없었다**는 사실이다: 얼린 cohort **12개 중 11개**에
봉인이 없었고, 58차에 봉인 코드가 생긴 뒤 얼린 `g12` 하나에만 있었다.

이제 봉인 없는 frozen cohort 가 하나라도 있으면 **게시를 거부**하고
`row_projection.py --seal-frozen` 으로 안내한다. 그것이 clean clone 에서 이 층이
없다는 사실에 대한 정직한 처리다 — 없는 방어를 있는 척하지 않고, 사람이 그
기계에서 한 번 세우게 한다.

**그리고 그 거부가 시험 세션까지 멈춰 세웠다 (마감에서 실측한 자체 발견).**
좌표 봉인의 이름은 좌표이고 좌표에는 그 filesystem 안의 **경로**가 들어간다.
그래서 트리를 복사하면 `_frozen_coords/` 가 **함께 복사돼 있어도** 새 자리에
대해서는 없는 것이다. 변이 재생 1/12 조각의 baseline 이 이 거부로 3건 빨갛게
죽었고(`caller-stage-safe-read`·`sink-validates-itself`·`pending-base-generation`),
같은 이유로 **fresh clone 의 `pytest tests/` 도 빨갛다** — 이 라운드의 증거를
만드는 통로와 리뷰어가 재현하는 통로가 같이 막혀 있었다.

해석: 봉인 파일은 지역 파일이고 그것을 쓸 수 있는 자는 다시 쓸 수도 있다.
그러므로 이 층이 실제로 막는 것은 **"봉인한 뒤에 대상이 바뀌는 것"** 이지 "처음
본 것이 남의 것인 경우" 가 아니다. 사람에게 명령 한 줄을 더 요구해도 그 사실은
안 바뀌고, 바뀌는 것은 새 checkout 의 시험이 빨갛다는 것뿐이다. 그래서
**시험 세션(`tests/conftest.py`)이 자기 자리를 처음 한 번 봉인하고 무엇을
봉인했는지 출력한다** — 조용한 bootstrap 은 없는 층을 있는 척하는 것과 구별되지
않으므로 출력을 뺄 수 없다. **게시 경로의 거부는 그대로다.**

남는 한계를 그대로 적는다: 그러므로 이 층은 TOFU(first-use 신뢰)다. 첫 봉인
시점에 이미 mount 속임수가 서 있으면 틀린 좌표를 굳힌다. 그 창을 닫으려면
봉인이 지역 파일이 아니어야 하고, 그것은 이 라운드의 범위 밖이다.
회귀: `test_a_never_sealed_checkout_can_still_run_its_own_test_suite`.

**⑤ `mv` 는 여전히 봉인을 벗어난다.** 58차에 시험으로 못 박은 한계 그대로다
(`test_the_seal_is_not_invariant_under_rename__a_recorded_limit`).

---

## §1 발견별 — 무엇이 틀렸고 무엇을 바꿨나

리뷰어가 요약한 **세 형태**로 묶는다.

> ① 새 primitive 가 production 의 **산출 commit 에 닿지 않는다** (M1)
> ② 판정은 한 시점의 이름·caller 객체를 보고 **쓰기·봉인은 나중의 것을 다시
>    연다** (M5·M6·M8·M9)
> ③ "닫힌 집합" 이라고 부른 **입력이 실제 schema 보다 작다** (M2·M11·M12·M14·M15)

| ID | 무엇이 틀렸나 | 무엇을 바꿨나 | 증인 (시험) | 변이 축 |
|---|---|---|---|---|
| M1 | 완료 시 class 기록이 production 에 배선 안 됨 (`record_run_outputs` 실호출 0) | gate 가 **권한**을 발행하고 굳히는 함수가 그것을 **요구**한다. raw class 를 받던 함수는 **삭제**. legacy 분류는 명시적 roster 로 | `test_exec_class_capability_59.py` 5건 | `output-commit-requires-a-capability-g59` |
| M2 | content id 가 production start manifest 를 누락 (`fits_manifest.yaml` 은 writer 0곳) | 목록을 **schema 선언**으로 승격 + 구조 시험이 양방향 동일성 강제 + 선언 밖 manifest 거부 (`run-content-id/v3`) | `test_run_schema_binding_59.py` 4건 | `run-content-id-refuses-unknown-manifests-g59` · `run-manifest-schema-is-production-wide-g59` |
| M3 | final `O_EXCL` 파일이 부분 바이트로 공개되고 성공 | temp → write-all → fsync → **바이트 read-back** → `os.link()` no-replace CAS → parent fsync | `a_short_write_never_publishes_a_partial_record` | `exec-class-record-is-read-back-g59` |
| M4 | shared/local class 충돌을 reader 가 canonical 로 숨김 | reader 가 **두 자리를 다 읽고** 어긋나면 두 class 를 이름으로 말하며 거부 | `a_shared_local_class_conflict_is_fail_closed` | (M3 축이 같은 함수를 덮는다) |
| M5 | smoke 판정 직후 bind swap → 실제 쓰기가 밖으로 | 권한이 판정한 디렉터리의 **handle** 을 나르고, 굳히는 자리가 같은 커널 객체인지 확인한 뒤 그 handle 로 manifest 를 읽는다 | `test_handle_carry_59.py` 2건 | `capability-carries-the-judged-handle-g59` |
| M6 | clean clone 에서 marker+ledger 만으로 frozen 못 지킴 | 봉인 없는 frozen cohort 가 있으면 **게시 거부** + `--seal-frozen` 진입점 | `test_frozen_clean_clone_59.py` 3건 | `frozen-publication-needs-a-local-seal-g59` |
| M7 | `fit → grid` 역순이면 consumed 결속 없이 executed | 순서를 강제하고 `consumed` 를 **필수**로 (없으면 오류). 뒤 phase 는 **모든** 선행을 결속 | `test_run_schema_binding_59.py` 2건 | `phase-order-is-enforced-g59` · `finalize-requires-the-consumed-binding-g59` |
| M8 | bundle member symlink 로 repo 밖 바이트 | walk 를 `lstat` 으로 — symlink·비일반 파일 구성원은 **거부** | `a_bundle_member_symlink_can_not_smuggle_bytes_from_outside` | `bundle-members-are-not-followed-g59` |
| M9 | 검증한 evidence 와 봉인한 evidence 가 다르다 | 진입 즉시 **정규 바이트로 굳히고** 그것을 다시 읽어 쓴다 (깊이 무관) | `finalize_seals_the_evidence_it_verified` | `finalize-snapshots-the-evidence-g59` |
| M10 | 공개 `claim_planned_leg(token=…)` 가 disk token 없는 running 생성 | raw 발급을 **비공개**로 + token 이 디스크에 굳어 있는지 확인 | `test_issuance_surface_59.py` 3건 | `issuance-requires-a-durable-token-g59` |
| M11 | capability 의 module target 을 식으로 감싸면 closure 밖 | "module 인가" 대신 **"module 이 아님을 증명할 수 있는가"**. 별칭도 고정점으로 | `wrapping_the_capability_target_does_not_escape` (6 변형) | `capability-target-must-be-provable-g59` |
| M12 | import-time 실행 모델이 `assert`·metaclass·future flag 를 버림 | **실행된다**를 기본으로. `assert`·`raise` 는 슬라이스 안, class base·metaclass 는 데코레이터와 같은 **치환**, `__future__` 는 실행 의미를 바꾸는 지시. `__main__` 분기만 증명으로 제외 (§0-①) | `test_import_time_slice_59.py` 7건 | `module-assert-runs-at-import-g59` · `class-bases-are-substitution-g59` · `future-flag-changes-the-model-g59` |
| M13 | class durability 재시도가 실패한 parent fsync 를 안 고침 | 성공의 출구를 **하나로** — 새 게시든 멱등 재시도든 다시 읽고 다시 굳힌다. 등록부 층도 `_mkdir_durable` | `a_retry_after_a_failed_parent_fsync_redoes_the_durability_step` | `exec-class-retry-reseals-durability-g59` |
| M14 | startup probe 가 `sitecustomize` 의 transitive import 를 안 묶음 | 탐침이 `sys.modules` 를 **스크립트 첫 줄에서** 찍어 startup 에 올라온 module 전부를 잰다 | `the_startup_probe_binds_what_sitecustomize_pulls_in` | `startup-binds-every-loaded-module-g59` |
| M15 | `environment_tag()` 가 full receipt 아니라 `startup` 만 증언 | tag 가 **영수증 전체**를 해시. 영수증 계산을 탐침 본문으로 옮겨 부모와 증언 node 가 같은 문자열을 쓴다 | `test_evidence_layer_59.py` 2건 | `env-tag-covers-the-whole-receipt-g59` |
| M16 | 내 회귀 하나가 이 환경에서 자기 축을 실행 안 함 (`254:0` 하드코딩) | 좌표를 현재 mount table 에서 **유도**하고 후보가 하나 이상임을 **먼저 단언** | `names_for_does_not_swallow_a_refusal` | (기존 축) |
| M17 | 능력 escape 규칙이 무해한 local shadow 도 거부 | 판정을 철자에서 **결속**으로 (§0-③) | `a_local_name_that_merely_shares_a_spelling_is_not_a_capability` · `the_escape_rule_still_refuses_a_real_alias` | 없음 — 완화라 "지우면 빨개진다" 형태가 안 선다 |

---

## §2 증거

### 2-1 전체 회귀 + strict smoke

```
$ python -m pytest tests/ -q                     # 7e03cb19 (판정 대상 코드)
1534 passed, 1 xfailed in 1687.41s (0:28:07)     rc 0

$ ./scripts/smoke_e2e.sh                          # 32f7424e
✅ pipeline smoke 통과                             rc 0
$ git status --short                              # smoke 뒤
(빈 출력)
```

두 커밋 사이의 차이는 `docs/22p_gap/mutation_coverage/` **뿐이다** — RUN_SCOPE
밖이고 변이 증거의 tree digest(`src/ tools/ tests/` + 세 파일) 밖이다. 그래서
회귀를 다시 돌릴 이유가 없었고, 다시 돌리지 않았다는 사실을 여기 적는다.

smoke 뒤 작업 트리가 clean 이다 — 등록부 오염 0건 (`_exec_class` ·
`_frozen_coords` 둘 다). 58차 L14 가 smoke 실행 class 레코드를 gitignore 된
지역 등록부로 가른 결과가 이 라운드에서도 유지된다.

### 2-2 산출물 identity — g13 을 얼리고 g14 로

대상 커밋: `32f7424e78a0c15b59faab5c129c2873b9e1cbf2`

> 이 줄은 장식이 아니라 **자기완결의 조건**이다. 아래에서 영수증 core sha 를
> 인용하므로 그것을 무엇에 대고 대조할지 요청문 안에서 정해야 한다
> (`test_committed_gate_requests_are_self_contained`). 이 커밋의
> `docs/22p_gap/receipts/paired_fixed5_v4.validate.yaml` 이 정본이다.

```
compute_sha256            0d3e1355383dda14 → c02b963e5d65bb55
row_projection_py_sha256  f55f5ddd6fb7bd2f → c9bdaa2b33ad6ed4
producer_semantic_sha256  13def6a32e8d9536 → 1c768c143c35e43c
src_scoring_py_sha256     69e69cb046f4b4ae (변동 없음)
analysis_spec_sha256      43d74dd3…        (변동 없음)
영수증 core sha           c9b41978002d46fb…  (검사 34건 · 산출 2건)
validator source_digest   920cfd31c22ebe06 → 4fe8d27269ca9ca2
투영                      proj_g13 → proj_g14   (freeze journal seq 12)
```

**행 바이트는 안 움직였다 — 열 세대째 같은 값이다.**

```
✅ paired_fixed5_v4: 6138행 · restart 30690행 · proj ad598fe77e75afec
   · 전체 True · by_obj True · fits삼중 True · 봉인일치 True
```

`ad598fe77e75afec` 는 g4 이후 유지돼 온 값이다. 이번 라운드가 고친 것은 실행
class 권한 배선·내용 identity·handle 결속·발급 표면·producer 의 실행 의미·
증언 범위이고 **계산식이 아니다.** `src.scoring` 과 analysis spec 이 안 움직인
것도 같은 사실의 다른 면이다. 그래도 **cross-cohort 비교는 금지**다 — 같은
바이트라는 사실은 회귀가 확인하는 것이지 인용의 근거가 아니다.

### 2-3 변이 등록부 — 12조각 전수, 합집합이 등록부를 정확히 덮는다

```
$ for i in $(seq 1 12); do
    python mutation_replay.py --slice "$i/12" --emit-coverage mutation_coverage/s$i.json
  done
조각 1..12 전부 rc=0

$ python mutation_replay.py --check-coverage mutation_coverage/s{1..12}.json
모든 변이 지점이 정확히 한 번 나타난다
등록부 scenario 204 (executable 195 · declared 9) · 조각 12개에서 관측 204
조각 합집합이 등록부 전체를 정확히 덮었다
```

driver 는 **하나로 순차** 실행했다 (58차 교훈: driver 를 둘 돌리면 같은 coverage
파일을 함께 써서 증거가 오염된다). 조각마다 `binding.tree_digest` 가 같은 트리를
가리키고, checker 가 **지금 트리와 대조**한다 — 실제로 이번 마감에서 그 대조가
낡은 조각 12개를 먼저 거부했다.

새로 심은 축은 18개(`-g59`)이고, 그 중 두 개는 처음에 안 물어서 고쳤다(§3).
이 라운드에 축 **13개가 죽었고** 전부 `--check-preimages` 또는 전수 재생이 먼저
잡았다 — 사람이 알아챈 것은 하나도 없다.

---

## §3 이 라운드가 배운 것 — 죽은 변이 축 13건

여섯 묶음을 고치는 동안 **변이 축 10개가 조용히 죽었다.** 방어를 옮기면 그
방어를 겨누던 변이의 원상이 더 이상 파일에 없고, 그러면 그 변이는 아무것도 안
문다.

지나가지 않은 이유는 **"합집합을 셀 수 없으면 거부한다"** 는 규칙 때문이다.
매 묶음마다 `--check-preimages` 가 먼저 소리를 냈고, 새 원상으로 고친 뒤
**다시 무는 것을 눈으로 보고** 넘어갔다.

| 묶음 | 죽은 축 |
|---|---|
| α | `module-gate-before-side-effects` · `execution-class-record-is-exclusive-g58` |
| γ | `content-id-hashes-every-manifest-g58` |
| β | `lifecycle-owned-evidence-is-refused-g58` |
| δ | `closure-refuses-dynamic-resolution` · `decorators-are-import-time-effects-g58` · `producer-normalizes-the-node` |
| ε | `execution-receipt-binds-the-startup-g58` · `evidence-binds-the-environment` (두 자리) |

그리고 마감의 전수 재생이 **세 개를 더 잡았다** (조각 3·7·10). 셋 다 "변이가
아무것도 안 문다" 였고, 셋 다 다른 이유였다.

| 축 | 왜 안 물었나 | 어떻게 고쳤나 |
|---|---|---|
| `smoke-gate-records-the-execution-class-g58` | **원상이 죽은 코드였다.** M1 이 계약을 옮기면서 `note_smoke_exemption()` 의 호출자가 0곳이 됐다 | 그 함수를 **삭제**하고 축을 지금의 L1 명제(면제 분기가 권한을 발행하는가, 대상 `src/grid.py`)에 다시 겨눴다 → `smoke-gate-issues-the-execution-capability-g59` |
| `frozen-seal-is-consulted-first-g58` | M6 이 `_assert_writable()` 맨 앞에 "얼린 자리를 알기는 하는가" 를 넣어 **첫 층이 먼저 거부**한다 | 두 층을 함께 되돌리는 MULTI(2자리)로 승격 |
| `claim-is-atomic` | M10 이 시험을 raw 발급에서 `open_leg_run()` 으로 옮겼고, 그 진입점이 살아 있는 claim 을 **먼저** 본다 | 세 번째 자리를 더해 MULTI(3자리)로 |

**죽은 축은 죽은 코드를 가리킨다** — 첫 항목이 그것이다. 등록부가 이번에는
"방어가 사라졌다" 가 아니라 "이 방어 표면에 아무도 안 온다" 를 알려 줬고,
그래서 공개 함수 하나를 지웠다. 있는 척하는 표면은 없는 것보다 나쁘다.

그리고 새 축을 심을 때 **두 개가 처음에 안 물었다**. 둘 다 배운 것이 있다.

1. `output-commit-requires-a-capability-g59` — guard 를 지워도 다음 줄이
   `None.nonce` 로 터져 `AttributeError` 가 났고, 시험이 받아들이는 예외 집합에
   그것이 있었다. **crash 는 거부가 아니다** — 어디까지 진행됐는지 말하지 않고
   부분 상태를 남길 수 있다. 시험을 `PreserveError` 하나로 좁혔다.
2. `module-assert-runs-at-import-g59` — 한 자리만 되돌리면 다른 자리가 가렸고,
   다른 자리만 비우면 fail-closed 거부가 나서 "거부도 정답" 인 시험이 통과했다.
   58차 상태를 정확히 복원하려면 **둘을 함께** 되돌려야 한다 (MULTI).

**교훈**: 증거가 낡았다는 것은 사람이 알아채는 것이 아니라 **기계가 거부해야**
하는 것이다. 이 라운드에서 가장 자주 값을 한 규칙이다.

### 세 번째 형태 — 축은 살아 있는데 **무는 층이 바뀐 것** 1건

`token-is-written-before-the-claim` (50차 축). 그때는 변이가 claim 만 남기고
token 을 안 굳혀서 **시험의 assert** 가 "이어받을 수 없는 다리" 를 봤다. 59차
M10 이 발급에 durable-token 확인을 넣은 뒤로는 **claim 을 만들기 전에
production 이 거부한다.** 그래서 node 는 그대로 빨간데 증인 문장이 달라졌고,
전수 재생이 그것을 `선언한 이유가 아니다` 로 거부했다.

축의 물음("token 이 claim 보다 먼저 굳는가")은 안 바뀌었고 답하는 층만 시험의
assert 에서 production 검사로 **올라갔다**. 그래서 축을 지우지 않고 증인을 그
거부문으로 옮기고, 등록부에 사유를 적었다. 이 구별을 기계가 해 주지 않았다면
"통과했으니 됐다" 로 지나갔을 자리다.
