# 57차 게이트 리뷰 요청 — 묶음 9 (실행 전 승인 · 보존 lifecycle)

## 판정 대상 (2026-09-07 갱신 — 이 블록이 정본이다)

| 항목 | 값 |
|---|---|
| 브랜치 | `claude/14-gate-code-review-9qkx05` |
| **판정 대상 코드** | **`cf10f345`** |
| `source_digest` (RUN_SCOPE `src/ tools/ configs/ scripts/ run.sh requirements*.txt`) | **`2f1e10779368987f`** |
| 작업 트리 | clean (`git_dirty = False` · `git_dirty_out_of_scope = []`) |
| 직전 판정 | 56차 **NO-GO** — P0 7건 · P1 4건 |

> **fetch 는 브랜치 head 로 해 주기 바란다 — 이 문서 자체는 `cf10f345` 보다
> 뒤에 있다.** 요청문은 자기가 담길 커밋 SHA 를 적을 수 없다 (적는 순간 SHA 가
> 바뀐다). 그래서 두 가지를 나눈다:
>
> - **판정 대상 코드** = `cf10f345` — `source_digest 2f1e10779368987f` 가 이것을
>   가리킨다. 아래 §"RUN_SCOPE 는 한 바이트도 안 바뀌었다" 가 근거다.
> - **이 문서** = 브랜치 head. `cf10f345` 이후 커밋은 **이 파일과 원장(`docs/`)
>   뿐**이므로 head 에서도 `source_digest` 는 같은 값이다.
>
> `[재현]` 리뷰어가 직접 확인하는 방법:
>
> ```
> git fetch origin claude/14-gate-code-review-9qkx05 && git checkout FETCH_HEAD
> python3 -c "import sys; sys.path.insert(0,'.'); from src.io import source_digest; print(source_digest())"
> # → 2f1e10779368987f 이어야 한다. 아니면 그 자체가 발견이다.
> git diff --name-only cf10f345 HEAD | grep -Ev '^degradation-degeneracy/docs/'
> # → 출력이 비어야 한다.
> ```

**이 요청문은 여러 번 커밋 줄을 고쳤다. 그 이력을 남긴다** — 리뷰어가 이전 판을
봤을 수 있고, 우리가 한 번 **거짓 문장을 적었기** 때문이다.

| 시점 | 적었던 것 | 실제 |
|---|---|---|
| 최초 | 대상 `47a2763e` · `source_digest` = `ea35ff4f39b97489` | 맞았다 |
| 2026-09-04 오전 | *"HEAD 가 `6ca8abd0` 로 옮겼지만 `source_digest` 는 그대로"* | **거짓** — 같은 날 P0-8 이 `tools/preserve.py` 를 고쳐 `2f1e1077…` 로 움직였다 |
| 2026-09-04 오후 | 대상 `6ca8abd0` · `2f1e10779368987f` | 맞았다 |
| **2026-09-07 (지금)** | 대상 **`cf10f345`** · `2f1e10779368987f` | 아래 표로 재측정 |

### `6ca8abd0 → cf10f345` 사이에 RUN_SCOPE 는 **한 바이트도 안 바뀌었다**

```
$ git log --oneline 6ca8abd0..cf10f345
cf10f345 fix(webapp): /trust 도해의 글자 7개가 왼쪽 정렬로 떨어져 있었다
aa9eb60b fix(webapp): 고쳐도 화면이 안 바뀌던 이유 — 템플릿이 프로세스에 캐시돼 있었다
5bce6e95 fix(webapp): /trust 의 두 그림을 하나의 격자로 다시 그렸다
8c0e317c fix(webapp): /trust 가 깨져 있었다 — 클래스를 두 번 잘못 썼다
7b479bcc webapp: 앞문을 둘로 — 새 화면이 nav 에만 있어서 아무도 못 찾는 상태였다
b6f43aea docs(gate): 요청문의 거짓 source_digest 문장 정정 + §65 절차 기록

$ git diff --name-only 6ca8abd0 cf10f345 \
    | grep -E 'degradation-degeneracy/(src/|tools/|configs/|scripts/|run\.sh|requirements)'
(출력 없음)
```

`[재현]` 트리에서 직접 계산한 값도 같다:

```
$ python3 -c "import sys; sys.path.insert(0,'.'); from src.io import source_digest; print(source_digest())"
2f1e10779368987f
```

그러므로 **`6ca8abd0` 에 붙은 모든 증거가 `cf10f345` 에서도 그대로 유효하다.**
바뀐 것은 `webapp/`(5커밋) 과 `docs/`(1커밋) 뿐이고 둘 다 RUN_SCOPE 밖이다.

**봉인된 산출물 g12 는 재생성하지 않았고 유효하다** — validator 의 `코드_재계산`
검사는 같은 commit·clean 일 때만 돌고, 다르면 `_참고_코드재계산불가` 로 사실만
남긴다 (`src/io.py`). 10시간짜리 격자를 다시 돌릴 필요는 없다.

**§63·§64·§65 를 먼저 읽어 주기 바란다** (`docs/08_REVIEW_RESPONSE.md`) — 요청문
작성 **뒤에** 나온 자체 발견 셋이다. §63 은 e2e 가 낡은 경로 리터럴로 빨갰고 그것이
**난입 3경우가 구성되지 않고 있었다는 것**과 **변이 하나가 살아남았다는 것**을
가리고 있었다는 기록, §64 는 P0-8 을 닫은 방법, §65 는 증거 재생성 중 커밋이
증거를 무효로 만든 절차 사고다.


### §0.1 P0-8 을 어떻게 닫았나 — **두 갈래를 다 버렸다** (2026-09-04)

이 절은 원래 "**설계 갈림을 리뷰어에게 묻는다**" 였다. 묻기 전에 셋째 길을 찾아
그것으로 닫았으므로, 무엇을 묻으려 했고 왜 버렸는지를 남긴다.

**묻으려던 두 갈래** — 둘 다 "봉인 산출물에 새 필드를 요구하는데 g12 에는 없다" 는
전제 위에 있었다:

- **fail-closed** → 예전 산출이 sink 에서 거부되고 **g12 를 다시 만들어야** 한다.
- **버전화 fallback** → 예전 산출은 **경로 기반**으로 판정된다. 그러면 P0-8 이
  없애려던 그 의존이 **migration 창 동안 살아 있다.**

`[해석]` **전제가 틀렸다.** marker 를 *산출물 안의 필드*로 놓았기 때문에 둘 중
하나를 골라야 했다. marker 를 **원장 옆 등록부**에 두고 키를 **내용 해시**로 잡으면
산출물을 건드리지 않는다 — g12 는 한 바이트도 안 바뀐다.

그리고 migration 은 **기간이 아니라 산출별 1회 행위**가 된다. 경로를 아예 안 보는
것이 아니라 **딱 한 번 보고 영수증에 적는다**(`classify_legacy_run()`). 창이 열려
있는 동안 조용히 경로를 믿는 것과 달리, **언제 무엇을 보고 정했는지가 남고** 그
뒤로는 다시 보지 않는다. 실물 4건을 그렇게 분류했고 영수증은
`docs/22p_gap/_exec_class/` 에 있다.

**리뷰어께 묻는 것이 하나 남는다**: 조건 원문의 class 는 다섯이었는데
(`primary·compare·nested·archive-external·전이 report source`) 우리는 둘만
구현했다(`canonical`·`smoke`). 값만 늘리면 되는 구조이나 **그 넷의 승격 정책이
무엇인지는 우리가 정할 일이 아니라고 판단했다.**

**우리가 재 둔 사실** (`[재현]`):

| 무엇 | 값 |
|---|---|
| `is_inside_namespace()` 호출처 | **12곳** (`src/grid.py` 1 · `src/fitting.py` 3 · `tools/preserve.py` 5 · `tools/make_results.py` 1 · `tools/archive_bundle.py` 1, 나머지는 정의·주석) |
| g12 곡선 manifest 의 `source_digest` | `d50295f980ccaa81` (2026-08-13 생성) |
| 현재 트리 `source_digest` | `2f1e10779368987f` — **이미 다르다** (53~57차 + 이번 P0-8 이 RUN_SCOPE 를 고친 뒤라서) |
| 그런데 g12 가 유효한 이유 | validator 의 `코드_재계산` 검사는 **같은 commit·clean 일 때만** 돈다. 다르면 `_참고_코드재계산불가` 로 사실만 남긴다 (`src/io.py`) |

`[해석]` 그러므로 **RUN_SCOPE 를 고쳐도 봉인된 g12 자체는 무효가 되지 않는다.**
비용은 "새 실행을 하려면 baseline 캐시(`.cache/discharged_state`)가
`source_digest` 로 묶여 있어 재생성해야 한다" 쪽이다 (~28분).

**⚠ 이 문단은 원래 *"묻는 것은 하나다 — 새 필드를 fail-closed 로 요구할까,
버전화 fallback 을 둘까"* 로 끝났다. 그 물음은 철회한다** — 위에서 적었듯 두
갈래를 다 버리고 등록부로 닫았기 때문이다. 지금 남은 물음은 §3 의 Q1~Q4 다.

---

## §0 먼저 — 이번 라운드가 **하지 않은** 것

| 조건 | 상태 |
|---|---|
| **P0-1** producer 결속 — 닫힌 typed manifest 파싱 · 두 payload 압축해제 재해시 · producer 발행 영수증 | **미착수** (49차부터 **아홉 라운드째**) |
| **P0-8** 경로 무관 typed·sealed 실행 class marker | **2026-09-04 닫음** — 판정을 경로에서 **내용**으로 옮겼다. 상세·실측은 `docs/08_REVIEW_RESPONSE.md` §64, 남은 것(class 4종 미구현 · 등록부 삭제 절차)도 거기 적었다 |
| trusted launcher 의 source 측정 | **미착수** |
| **P0-4** typed 보존 영수증 **소비** | **부분** |
| 변이 증거의 **독립 replay** | **미착수** — 57차는 checker 가 영수증을 소비하게 했을 뿐(P1-1), 스스로 재생하지는 않는다 |
| baseline·sweep1d·wsweep 계획 gate · 실물 object-lock adapter · power-loss 모델 · publisher 전용 OS principal | **미착수** |
| 외적타당도 **#48**(단일 C-rate) · **#49**(셀 간 산포) | **2026-09-04 닫음** — `docs/RESULTS.md` §"이 결론이 말하지 않는 것" 에 한계로 승격했다. 격자 전체가 `c_rate 0.05`·`charge_first`·컷오프 4.2/2.5 **한 점**이고 `parameter_set: Chen2020_composite` **하나**라 3069 조건에 **셀 간 산포가 0** 이다 |
| 외적타당도 **#50** (`truth_provenance` 를 기계 계약에) | **미착수** — 아래 §0.1 |

55·56차 판정문의 마지막 문단에 동의한다 — 위 항목들은 반례와 **별개의 독립 GO
전제**로 그대로 남는다.

### 이번 라운드가 스스로 신고하는 것 셋

**① 57차 리뷰어 원문이 이 저장소에 없다.** `docs/22p_gap/` 에는
`GATE56_REQUEST.md` 까지만 있다. 판정의 개수(P0 7 · P1 4)와 P0-1·P0-2/3/4·
P0-5·P0-6/7·P1-1 의 내용은 커밋 시점에 원문을 보고 적었지만, **P1-2 와 P1-3
은 56차 요청문의 §3-6 과 §3-3 에서 재구성한 것**이다. 두 반례는 실제로
재현했고 그 출력을 아래 §1 에 적었다. 다만 **리뷰어가 P1-2 / P1-3 으로 적은
것과 같은 발견인지는 원문 대조가 필요하다.** 다르면 그 둘은 아직 열려 있는
것으로 취급해 주기 바란다.

**② 전체 회귀가 초록이 아니다** — `tests/test_lifecycle_e2e.py` 2건이 빨갛다.
원인은 이 라운드의 수정이 아니라 **컨테이너 커널 교체**다 (§2-1).

**③ 남아 있는 표면** (56차 신고분 + 이번에 확인한 것):

- 원장·journal·anchor·`.FROZEN` 전부에 쓸 수 있는 주체는 역사를 다시 쓸 수 있다.
  이것은 계약 §13.3.4 로 **명문화**했다 (B) — 없앤 것이 아니라 적은 것이다.
- 소유 증명 token(0600)은 같은 uid 의 다른 process 가 읽는다.
- 변이 증거의 **pytest report 자체를 손으로 위조**하면 checker 를 통과한다.
- lock 은 여전히 같은 파일시스템의 `flock` 이다.
- mount 판정은 이제 커널에 묻지만, `/proc/self/fdinfo` 와 `/proc/self/mountinfo`
  를 읽을 수 있는 Linux 를 전제한다. 못 읽으면 거부한다(fail-closed).
- `migrate_legacy_finalized_leg()` 가 인증에 쓰는 근거는 **원장 봉인보다 약하다**
  (디스크의 소유 증명 파일). 그래서 `evidence.verifier_origin` 을 남긴다 — 숨기지
  않지만 약한 것은 사실이다.

---

## §1 56차 반례 11건 — 전부 재현한 뒤 고쳤다

| # | 56차 반례 | 재현 | 고친 자리 |
|---|---|---|---|
| B | lifecycle 경로의 신뢰 경계가 **어디에도 적혀 있지 않다** (자체 발견) | — | `preserve.py` `_TRUST_BOUNDARY` · 계약 §13.3.4 — 무엇을 전제로 빼고 무엇을 결함으로 남기는지 표로 |
| P1-1 | 실행 영수증을 **쓰기만 하고 안 읽는다** — 12조각에서 `binding.execution`·`execution_digest` 를 전부 지워도 rc 0 | ○ | `mutation_replay.py` `_assert_execution_is_current()` 를 `check_coverage()` 가 부른다 (있는가 · 본문이 그 digest 로 해시되는가 · 지금 환경과 같은가) |
| P0-1 | caller 가 지정한 attempt 경로가 authority 를 덮는 sink | ○ | **경로 인자를 없앴다** — `attempts_root_for_ledger()` · `attempt_path_for()` 가 자리를 유도하고, 공개 API 5개에서 `token_file` 을 제거 |
| P0-2 | 겹쳐 쌓인 mount 에서 **아래** 것이 뽑힌다 (`DID NOT RAISE SystemExit`) | ○ | `_deepest_mount_for()` 를 **지웠다** · `_kernel_mount_id()` 가 `/proc/self/fdinfo/<fd>` 의 `mnt_id` 를 읽는다 |
| P0-3 | 같은 모델의 다른 얼굴 — 이름을 되돌리는 설계 | ○ | `_through_bind_mounts()` 를 **지웠다** · `_fs_identity()` 가 `(major:minor, filesystem 안의 경로)` 좌표로 비교 |
| P0-4 | 같은 모델의 세 번째 얼굴 — 목적지가 아직 없을 때 | ○ | 존재하는 가장 깊은 조상을 커널에 묻고 없는 꼬리를 좌표 뒤에 잇는다 (없는 이름 위에는 아무것도 mount 되어 있지 않다) |
| P0-5 | 56차 이전 durable state 에 `attempt_verifier` 가 없어 **닫을 수도 되돌릴 수도 없는 다리**가 된다 | ○ | `_already_finalized()` 가 그 모양을 알아보고 **말한다** · `migrate_legacy_finalized_leg()` 를 사람이 한 번 명시적으로 부른다 (인증은 면제하지 않는다) |
| P0-6 | `MODULE_EFFECTS` 가 import 시 **실행되는** 노드 5종을 안 덮는다 (대입 우변·데코레이터·기본 인자·class base·class body) — 전부 digest 를 안 움직였다 | ○ | 그 노드들을 `MODULE_EFFECTS` 에 묶고 class body 는 `_visit` 로 훑는다 (`_import_time_heads()`) |
| P0-7 | namespace guard 가 호출 대상의 **철자**를 본다 — 우회 4종이 전부 통과 (`GET = getattr` · 별칭의 별칭 · `operator.attrgetter` · `sys.modules[__name__]`) | ○ | `_namespace_capabilities()` — module-level 별칭을 **고정점까지** 따라간다 · `attrgetter` 는 닫힘 안에서 거부 · `sys.modules[...]` 는 Subscript 규칙 |
| P1-2 | 재생이 pytest 에 환경을 지정하지 않아 **부모 환경이 통째로** 샌다 (재구성 — §0-①) | ○ | `replay_env()` — 필요한 것과 선언한 것만 남기고 지운다 · `PYTHONHASHSEED=0` · 영수증의 `env` 가 "중요한 목록" 에서 "**전부였다**" 는 사실로 |
| P1-3 | 멱등성 물음이 임계 구역 **밖**이라 동시 finalize 하나가 `FileNotFoundError` 로 떨어진다 (재구성 — §0-①) | ○ | `_already_finalized()`·`resume_claim()` 을 `_lifecycle_locks()` **안**으로. 락 앞의 중복 분기는 없앴다 |
| P1-4 | 그 좌표를 보여 주는 이름 중 **하나를 골랐다** | ○ | `_names_for()` — 모든 이름을 돌려주고 각 후보를 커널에 되물어 확인한다 (가려진 이름은 거기서 떨어진다) |

### 이번 라운드의 형태 하나 — 56차 verdict 가 못 박은 **종결이 아닌 수정 3종**

56차 판정은 고칠 자리만이 아니라 **고치는 방식**을 거절했다:

1. authority 경로 blacklist 를 더 늘리는 수정은 새 sink 하나를 남기므로 종결이 아니다.
2. 문자열 철자 blacklist 증설은 불충분하다.
3. mountinfo 행 순서와 pathname depth 로 stacked top 을 추측하면 안 된다.

셋 다 **검사를 정교하게 만드는 대신 물음 자체를 바꿔서** 닫았다.

| 반례 | 51~56차가 하던 것 | 57차가 한 것 |
|---|---|---|
| P0-1 | 금지할 경로를 하나씩 추가 (원장·claim·남의 token·symlink·hardlink) | **caller 의 pathname 이 sink 에 닿지 않게** — 인자를 없앴다 |
| P0-6/7 | 금지할 이름을 하나씩 추가 (`getattr`·`__import__`·…) | 이름이 아니라 **capability 를 따라간다** (별칭의 고정점) |
| P0-2/3/4 | 행 순서 → 깊이 → root 좌표계, 세 라운드에 세 번 | **커널에게 묻는다** (`mnt_id`) — 겹침·전파·순서는 커널이 이미 푼 문제다 |
| P1-2 | `BOUND_ENV` 목록을 늘린다 | 환경을 **강제**한다 — 목록 밖 변수는 증거를 안 움직이는 게 아니라 run 에 **닿지 못한다** |
| P1-3 | (해당 없음 — 새 발견) | 술어와 행위를 같은 임계 구역에 (`_lifecycle_locks()` 자신의 규칙을 멱등성 물음에도) |

**"수정이 도달 불가 코드를 만들면 그 코드를 지운다."** P0-1 이 경로 인자를
없애자 `token-path-is-disjoint-from-authority` 와 `attempt-path-is-exclusive`
두 검사가 preimage 0회가 됐다 — 막던 것이 존재할 수 없게 됐기 때문이다.
남겨 두면 "전수 재생 성공" 이 거짓이 되므로 은퇴시켰다 (§2-3).

---

## §2 증거

### 2-1 전체 회귀 — **1437 passed · 0 failed · 1 xfailed** (854.57s, rc 0)

`cf10f345` · clean 트리에서 2026-09-07 06:21–06:35 UTC 에 실행:

```
$ python -m pytest tests/ -q
1437 passed, 1 xfailed in 854.57s (0:14:14)
PYTEST_RC=0
```

**⚠ 이 절은 한 번 틀린 진단을 담고 있었다 — 정정한다.** 원래 여기 *"1427 passed ·
2 failed. 빨간 2건은 `tests/test_lifecycle_e2e.py` 이고 원인은 실행 컨테이너의
커널이 `fc-v22` → `fc-v24` 로 바뀐 것이다"* 라고 적었다. **커널과 무관했다.**

실제 원인은 **시험이 57차 이전의 경로 리터럴을 붙들고 있던 것**이다. 57차 P0-1 이
attempt 자리를 `attempts_root_for_ledger()` 로 원장에서 유도하게 바꿨는데, 시험만
`results/_attempts/` 를 보고 있었다 (실제 발급 자리는 `docs/22p_gap/_attempts/`).
제품은 rc 0 으로 정상 동작했고 시험이 낡았던 것이다. 전말은 §63.

**그 리터럴이 두 가지를 가리고 있었다** — 리뷰어가 여기를 겨눠 주기 바란다:

| 가려져 있던 것 | 무엇 |
|---|---|
| ① 난입 3경우가 **구성되지 않고 있었다** | `--attempt-file` 이 사라진 뒤 ②-a 는 정상 실행이 되고 ②-b·②-c 는 없는 인자를 넘기고 있었다. credential 경로 위에서 다시 구성했고 셋 다 rc 1 로 거부됨을 실측 |
| ② **변이 A 가 살아남았다** | `resume_claim()` 의 위조 검사를 꺼도 시험이 통과했다. 두 방어층이 메시지 접두어 `소유 증명이 맞지 않는다` 를 공유해서 단언이 층을 구분 못 했다. 앞단 전용 꼬리로 조인 뒤 다시 심어 **빨간 것을 눈으로 확인** |

라운드 진행 중 실패 추이 (전부 실측): 9 → 7 → 5 → 3 → 2 → 1 → **0**.

### 2-2 strict smoke — **rc 0 · `✅ pipeline smoke 통과`**

같은 트리에서 06:35–06:38 UTC:

```
$ ./scripts/smoke_e2e.sh
   ✅ 계획 index 일관 · 계획 밖 다리는 거부 (46차 P0-11)
   ✅ run.sh 에 실행 전 gate 가 배선돼 있다 (46차 P0-11)
   ✅ smoke namespace 밖 · 계획에 없는 다리는 실행 전에 거부된다 (46차 P0-11)
✅ pipeline smoke 통과
SMOKE_RC=0
```

**strict 였음을 같이 실측했다** — `SMOKE_DIRTY` 가 서지 않아 `clean_worktree` 와
`코드_identity` 를 건너뛰지 **않았다**:

```
$ python3 -c "from src.io import git_info; g=git_info('.'); print(g['git_dirty'], g['git_dirty_out_of_scope'], g['git_commit'][:12])"
False [] cf10f3459861
```

이번에는 범위 밖 dirty 도 **0건**이다 (이전 판에서는 `mode-observability/` README 둘).

### 2-2b 시험이 등록부를 오염시키지 않는다 — 이번 실행으로 확인

P0-8 의 실행 class 등록부(`docs/22p_gap/_exec_class/`)에는 실물 4건만 커밋되어야
한다. 그런데 시험 fixture 가 `record_execution_class()` 를 부르므로 회귀를 돌리면
항목이 늘어난다. 실제로 이번 회귀 **도중**에 74개까지 늘어난 것을 관측했다
(커밋된 4 + fixture 70). `tests/conftest.py` 의 세션 autouse guard
`_exec_class_registry_is_not_polluted_by_tests` 가 시작 시점 이름을 스냅샷하고
teardown 에서 새 것을 지운다. 종료 후:

```
커밋된:  4
디스크:  4
untracked: 0        # git status --porcelain 전체가 비었다
```

`[해석]` 이 guard 는 사후 대책이다 — 앞선 라운드에서 `git add -A` 가 fixture
93건을 **커밋된 등록부에 밀어 넣었고** 그것을 걷어내야 했다. 등록부가 authority 인
이상 시험이 거기 쓰는 것 자체가 설계 냄새다. **리뷰어가 더 나은 격리(예: 시험
전용 등록부 root)를 요구하면 그 방향이 맞다고 본다.**

### 2-3 변이 전수 — 등록부 **170 scenario** (executable 161 · declared 9)

176 → 170. 이 라운드가 코드를 옮기면서 **끊긴 anchor 14개**를 `--check-preimages`
가 먼저 잡았고, 재결속 8 · 은퇴 6 으로 처리했다.

| 처리 | 예 | 사유 |
|---|---|---|
| 재결속 | `mount-root-is-filesystem-relative` | 자리가 `_fs_identity()` 의 `fs = Path(m["root"]) / rel` 로 옮겨갔을 뿐 규칙은 살아 있다 |
| 개명 | `deepest-mount-is-chosen` → `mount-identity-comes-from-the-kernel` | 지킬 규칙이 "깊이" 에서 "커널에게 묻는다" 로 **바뀌었다** |
| MULTI 승격 | `destination-is-compared-in-filesystem-coordinates` (2-site) | `_assert_writable()` 이 두 자리에서 묻는 심층 방어라 한 자리만 꺼도 다른 쪽이 잡는다 |
| 은퇴 | `token-path-is-disjoint-from-authority` · `attempt-path-is-exclusive` | P0-1 이 **구조적으로 지운** 검사 — 막던 것이 존재할 수 없다 |
| 은퇴 | `finalize-requires-the-credential` | anchor 를 잘못 잡았다 (그 자리의 guard 시험은 항상 `token=` 을 명시로 넘겨 안 문다). 회귀는 `resume-compares-the-verifier` 의 selector 로 옮겼다 |

12조각을 **HEAD 를 고정한 채** 끝까지 돌렸고 조각별 문제는 0건이다.

**⚠ 조각이 기록한 HEAD 는 대상 커밋과 다르다 — 먼저 설명한다.** 12조각 전부
`binding.head = 775a9630` 이고 대상 커밋은 `cf10f345` 다. 리뷰어가 이 불일치를
먼저 볼 것이므로 근거를 붙인다:

```
$ git diff --name-only 775a9630 cf10f345 | grep -v mutation_coverage/
degradation-degeneracy/docs/08_REVIEW_RESPONSE.md
degradation-degeneracy/docs/22p_gap/GATE57_REQUEST.md
webapp/app.py
webapp/static/css/style.css
webapp/templates/index.html
webapp/templates/pipeline.html
webapp/templates/trust.html

$ git diff --name-only 775a9630 cf10f345 \
    | grep -E 'degradation-degeneracy/(src/|tools/|configs/|scripts/|run\.sh|requirements|docs/22p_gap/mutation_replay\.py)'
(출력 없음)
```

**변이 대상 코드(RUN_SCOPE)와 등록부(`mutation_replay.py`) 둘 다 그 사이에 안
바뀌었다.** 그래서 합집합 증명이 지금도 통과한다 — 2026-09-07 재실행:

```
$ python3 docs/22p_gap/mutation_replay.py --check-coverage docs/22p_gap/mutation_coverage/s*.json
모든 변이 지점이 정확히 한 번 나타난다
등록부 scenario 170 (executable 161 · declared 9) · 조각 12개에서 관측 170
조각 합집합이 등록부 전체를 정확히 덮었다
COVERAGE_RC=0
```

`[해석]` 검사는 **조각들이 서로 같은 HEAD 인가** 와 **그 HEAD 가 이 저장소에
실재하는가** 를 묻지, 현재 HEAD 와 같은지는 묻지 않는다. 우리는 그 선택이 옳다고
보지만 — 문서·webapp 커밋으로 증거를 무효화하지 않기 위해 — **리뷰어가 "현재
HEAD 와 같아야 한다" 를 요구하면 그것도 방어 가능한 입장이다.** 그러면 RUN_SCOPE
밖 커밋마다 12조각(약 60분)을 다시 돌려야 하므로 우리는 안 골랐다. 이 판단이
틀렸다고 보면 지적해 달라.

`[관련]` §65 — 첫 재생성은 **실패했다.** 12조각이 도는 동안 webapp 커밋을 해서
조각들이 두 HEAD (`2989298f`·`775a9630`) 에 걸쳤고 체커가 그것을 잡았다. 저장소를
얼리고 다시 돌려 한 HEAD 로 맞춘 것이 위 결과다.

```
모든 변이 지점이 정확히 한 번 나타난다
등록부 scenario 170 (executable 161 · declared 9) · 조각 12개에서 관측 170
조각 합집합이 등록부 전체를 정확히 덮었다
```

**정본은 커밋된 증거 파일이다** — `docs/22p_gap/mutation_coverage/s1..s12.json`
과 그 옆의 `reports/`.

### 2-4 증거 층이 잡은 것 넷

**① 새 시험이 처음부터 초록이면 fixture 가 진실을 가린 것이다.**
`mountinfo-octal-escape-is-decoded` 변이가 안 물길래 손으로 적용해 보니
`1 passed`. 원인은 코드가 아니라 **시험**이었다 — 거부 메시지에 `"frozen"` 이
들어 있는지를 부분문자열로 봤는데, pytest 의 `tmp_path` 이름이 시험 함수
이름에서 나오므로(`…/test_a_frozen_alias_whose_path_ha0/…`) 경로가 오류
문자열에 실리기만 하면 **어떤 이유로 거부해도** 통과했다.
`_assert_refused_as_frozen()` 을 두고 거부의 **이유**를 묻게 바꿨다.

**② 시험이 vacuous 해진 것을 변이가 알려 줬다.** `token-path-alias-is-refused`
가 안 물었다. P0-1 이 caller 경로를 없앤 뒤 그 시험은 아무도 안 보는 symlink
하나를 심어 놓고 `assert before == after` 를 하고 있었다 — 통과해도 아무 뜻이
없다. `attempt_path_for("L")` **자리에** symlink 를 심도록 다시 썼고, 증인은
`OSError: [Errno 40] Too many levels of symbolic links` 가 됐다.

**③ 등록부를 스크립트로 고치면 옆칸이 다친다.** 은퇴 처리 스크립트가 인접
항목(`release-cleanup-holds-the-attempt-path`)의 kexpr 꼬리를 잘라 먹었다.
커밋 전에 MUTANTS/MULTI/EXPECT 전체를 HEAD 와 diff 해서 잡았고
`git show HEAD:` 로 복구했다. **등록부 편집은 diff 로 검산한다**가 이 라운드의
교훈이다.

**④ P1-2 의 환경 결속이 실제로 문다 — 이 요청문을 쓰다가 실측했다.**
위키 열람기 폰트를 만들려고 `pip install brotli` 를 했더니 곧바로:

```
✗ …/s1.json: 증거가 가리키는 실행 환경이 지금과 다르다
   (다른 항목: ['packages']) — 그 환경에서 다시 재생해야 한다
```

`pip uninstall brotli` 로 되돌리자 합집합 증명이 다시 통과했다. 손으로 적은
목록이었으면 이 설치는 **증거를 전혀 움직이지 않았을 것**이다.

### 2-5 산출물 — g11 을 얼리고 g12 로

계약 §13.3.2 는 pin 을 cohort lifetime 동안 고정으로 둔다. 이 라운드가
`preserve.py`·`row_projection.py` 를 고쳐 identity 가 움직였으므로 g10 → g11
과 같은 형태다.

| 값 | 56차 (g11) | 57차 (g12) |
|---|---|---|
| `compute_sha256` | `872ca5b9046ca703` | `044a87204bfca078` |
| `producer_semantic_sha256` | `eb4555abd9490dd0` | `ad36d111337abd39` |
| `row_projection_py_sha256` | `b9d895261c7a9df1` | `ad1349257095cbd1` |
| `src_scoring_py_sha256` | `69e69cb046f4b4ae` | 같음 |
| 영수증 core_sha | `79ed20cd3fd34034…` | `8609f0074ac43197…` |
| validator identity | `9c7e5e71cbef8f05` | `ea35ff4f39b97489` |
| 투영 | `proj_g11` | `proj_g12` |

**행 바이트는 안 움직였다** — 재생성 출력이 `proj ad598fe77e75afec` 로
g4~g11 과 동일하다. 이 라운드의 변경은 신뢰 경계 선언 · 경로 유도 · capability
닫힘 · mount 좌표 · 환경 정화 · 임계 구역이고 **계산식이 아니다.** 움직인 것은
identity 의 **정의**다. cross-cohort 비교는 여전히 금지다 — 같은 바이트라는
사실은 회귀가 확인하는 것이지 인용의 근거가 아니다.

---

## §3 무엇을 반증해 주기 바라는가

우선순위 순. **§0 에 신고한 것을 다시 적는 것은 이미 아는 사실의 재확인이다.**

1. **커널 mount ID 를 믿는 것의 남은 축.** `_kernel_mount_id()` 는
   `O_PATH` 로 연 fd 의 `mnt_id` 를 읽는다 — 그 값이 우리가 묻는 질문에
   **답이 아닌** 구성이 있는가. mount namespace 가 분리된 자식, `/proc` 이
   다른 namespace 의 것으로 mount 된 경우, `mnt_id` 재사용(unmount 후 같은
   ID 재할당), `fdinfo` 에 `mnt_id` 가 없는 커널. 그리고 `_fs_identity()` 가
   목적지가 없을 때 **꼬리를 잇는** 자리 — 그 사이에 mount 가 생기는 TOCTOU.
2. **`_names_for()` 가 이름을 다 못 찾는 구성.** 좌표를 보여 주는 창이
   mountinfo 에 안 나타나는 경우(다른 namespace, `--rbind` 하위, overlayfs 의
   lower/upper). 못 찾으면 marker 순회가 조용히 짧아지는가, 거부하는가.
3. **경로를 없앤 뒤 남은 alias.** caller 는 이제 `leg_id` 만 준다.
   `check_id()` 의 도메인 안에서 두 leg 가 **같은 파일**로 유도되는 입력이
   있는가 (유니코드 정규화, 대소문자 무시 파일시스템, 길이 절단).
   `attempts_root_for_ledger()` 자체를 bind mount 로 덮으면?
4. **capability 고정점의 남은 계보.** `_namespace_capabilities()` 는
   module-level 별칭을 따라간다 — 함수 안 지역 별칭, class attribute,
   dict/list 에 담아 꺼내기, `functools.partial`, decorator 가 돌려주는 것.
   반대로 **너무 넓어** producer 자신의 정상 코드를 막는 자리.
5. **`migrate_legacy_finalized_leg()`.** 사람이 부르는 한 번의 창.
   그 검사(계획 executed · 실행 기록 있음 · claim 없음 · verifier 없음)를
   만족시키면서 **남의 다리**를 넘길 수 있는가. `verifier_origin` 이 붙은
   기록이 나중에 정상 기록과 구분되지 않는 경로.
6. **임계 구역 안으로 옮긴 뒤의 순서.** `_already_finalized()` 가 lock 안에
   있다 — `LOCK_ORDER = (attempt_path, claim, ledger)` 를 지키면서 deadlock
   이나 lock 승격이 생기는 조합. `resume_claim()` 이 lock 을 안 잡는 순수
   읽기라는 주장이 틀리는 자리.
7. **강제한 환경의 구멍.** `replay_env()` 가 지우지 못하는 것 — 상속되는
   fd, cwd, umask, resource limit, locale 을 결정하는 다른 경로, `PATH` 로
   들어오는 실행 파일의 내용. 목록이 "전부였다" 는 주장이 어디서 깨지는가.
8. **증거를 소비한다는 주장.** `_assert_execution_is_current()` 가 셋을
   본다 — 두 필드가 있는가 · 본문이 그 digest 로 해시되는가 · 지금 환경과
   같은가. 셋을 다 만족시키면서 **다른 실행**의 증거를 제출할 수 있는가.
9. **내용 키의 도메인** (P0-8, §64). `run_content_id()` 는 세 manifest
   (`curves_manifest.yaml`·`fits_manifest.yaml`·`manifest.yaml`) 중 있는 것의
   sha256 이다. **서로 다른 실행이 같은 `content_id` 를 갖는 입력**이 있는가 —
   manifest 가 담지 않는 축(예: 같은 계획·같은 입력인데 실행권이 다른 두 leg).
   반대로 정상 산출이 manifest 를 정당하게 갱신해 **키가 바뀌면** 등록이 사라진
   것처럼 보이는가 (`등록 없음 = 거부` 이므로 fail-closed 쪽으로 틀리긴 한다).
10. **`classify_legacy_run()` 의 1회 창.** 경로를 **딱 한 번 보고 영수증에
   적는** 설계다. 그 한 번을 **공격자가 고른 시점에** 일으킬 수 있는가 —
   아직 분류되지 않은 legacy 산출을 smoke namespace 밖으로 옮겨 두고 분류를
   유도하면 `canonical` 영수증이 발급되는가. 발급된 영수증이 나중에 정상
   등록과 구분되는가 (`evidence` 문자열 말고 구조로).

### 우리가 **묻는** 것 (판정이 갈릴 수 있고, 되돌릴 수 있다)

| # | 선택 | 우리가 고른 쪽 | 되돌리면 |
|---|---|---|---|
| Q1 | 실행 class 를 몇 종 둘 것인가 | **2종** (`canonical`·`smoke`). 조건 원문의 `compare`·`nested`·`archive-external`·`전이 report source` 는 미착수 — 값만 늘리면 되는 구조이나 **그 넷의 승격 정책은 우리가 정할 일이 아니라고 판단** | 정책을 주면 이번 라운드에 넣는다 |
| Q2 | 변이 증거를 **현재 HEAD** 에 묶을 것인가 | **아니오** — "조각들이 한 HEAD 를 공유하고 그것이 실재하는가" 만 본다 (§2-3) | 묶으면 RUN_SCOPE 밖 커밋마다 12조각 ~60분 재생 |
| Q3 | 등록부에 **삭제·만료**를 둘 것인가 | **아니오** — 덮어쓰기를 허용하면 등록부가 authority 가 아니라 마지막 쓴 사람의 의견이 된다. 잘못 분류하면 사람이 파일을 지운다 (운용 절차로 남음) | 서명된 철회 레코드를 넣는 쪽이 대안 |
| Q4 | 시험이 **실물 등록부**에 쓰는 것 | 지금은 conftest guard 로 사후 청소 (§2-2b) | 시험 전용 등록부 root 로 격리하는 편이 낫다고 본다 |

### §63 이 남긴, 우리가 못 닫은 물음 둘

1. **§62 의 실측표(`1391 passed · 0 failed`)가 어느 트리를 가리키는지 재구성
   못 했다.** 그 사이 시험이 늘고 P0-1 이 자리를 옮겼다. **기록된 증거와 트리가
   어긋나는 자리**이고, 우리가 스스로 못 메운 구멍이다.
2. **변이 등록부에 "앞단 verifier 무력화"(A형)가 들어 있는가.** 자체 변이로는
   **살아남았는데** 12조각 전수는 문제 0건이었다. 등록부가 이 지점을 안 덮고
   있다면 덮어야 한다 — 리뷰어가 확인해 주기 바란다.

---

## §4 검증 명령

```
python -m pytest tests/ -q
./scripts/smoke_e2e.sh
python3 docs/22p_gap/mutation_replay.py --check-preimages
python3 docs/22p_gap/mutation_replay.py --slice I/12 --emit-coverage docs/22p_gap/mutation_coverage/sI.json
python3 docs/22p_gap/mutation_replay.py --check-coverage docs/22p_gap/mutation_coverage/s*.json
python -m pytest tests/test_lifecycle_e2e.py -q
```

원자료(`results/`)는 gitignored 이므로 clean checkout 에서는 artifact 대조가
계산 불가로 실패할 수 있다. 지원 인터프리터가 하나뿐이면 정규형 회귀 2건이
`len(seen) >= 2` 로 실패한다. mount 회귀 다섯은 bind mount 를 만들 수 없는
환경에서 skip 한다. lifecycle E2E 는 `tqdm` 이 필요하다
(`pip install -r requirements.txt` 를 먼저 부탁한다).

**`--check-coverage` 는 이제 실행 환경까지 본다** (P1-2). 검토 환경의 설치
패키지가 다르면 조각을 그 환경에서 다시 재생해야 한다 — 그것이 결함이 아니라
이번에 고친 것이다. `[실측]` 이 요청문을 쓰다가 `pip install brotli` 하나로
곧바로 `✗ 증거가 가리키는 실행 환경이 지금과 다르다 (다른 항목: ['packages'])`
가 떴고, `pip uninstall` 로 되돌리자 통과했다.

---

## §5 GO 가 나오면 무엇을 하는가

리뷰어가 판정 근거로 삼도록, GO 이후 순서를 미리 적는다. **GO 없이는 아무것도
시작하지 않는다.**

| 순 | 명령 / 행위 | 산출 | 시간 |
|---|---|---|---|
| 1 | baseline 캐시 재생성 — `source_digest` 가 `2f1e1077…` 로 움직였으므로 `.cache/discharged_state` 가 무효다 | 새 캐시 + 계획의 `discharged_cache_sha256` 갱신 | ~28분 |
| 2 | `LEG_PRESERVATION.yaml` 의 `planned:` 에 본 실행 leg 를 적는다 (계획 gate 는 계획에 없는 다리를 거부한다) | 계획 원장 커밋 | — |
| 3 | `./run.sh` 본 격자 — 실행 전 gate 가 계획·실행권 claim 을 확인한 뒤 시작 | `results/grid_*` | **~10시간** |
| 4 | `tools/make_results.py` → `docs/RESULTS*.md` 갱신 | 정본 수치 | — |
| 5 | 산출물 봉인 · 투영 재생성 · 검증 영수증 | g13 cohort | — |

**보존할 증거** (이 라운드 판정의 근거가 되는 것들 — 실행 전후로 건드리지 않는다):

| 무엇 | 자리 |
|---|---|
| 변이 12조각 + 재생 report | `docs/22p_gap/mutation_coverage/s1..s12.json` · `.../reports/` |
| 실행 class 등록부 (실물 4건) | `docs/22p_gap/_exec_class/` |
| 발견 원장 (§1~§65) | `docs/08_REVIEW_RESPONSE.md` |
| 이 요청문과 이전 라운드 요청문 | `docs/22p_gap/GATE*_REQUEST.md` |
| g12 cohort 와 그 영수증 | 원장 + 투영 `proj_g12` |

**한 가지 절차 규칙** (§65 에서 배운 것): 변이 증거를 재생성하는 동안에는
저장소를 얼린다. 각 조각이 실행 시점 HEAD 를 기록하므로, 재생성 중 커밋 한 번이
진행 중인 증거를 무효로 만든다.
