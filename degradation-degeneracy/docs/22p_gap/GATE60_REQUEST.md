# 60차 게이트 리뷰 요청 — 묶음 9 (실행 전 승인 · 보존 lifecycle)

## 판정 대상 (이 블록이 정본이다)

| 항목 | 값 |
|---|---|
| 브랜치 | `claude/14-gate-code-review-9qkx05` |
| **판정 대상 코드** | **`c4e710040c2631d4f8140ee31c2f3c5004d9bcbb`** (RUN_SCOPE 를 마지막으로 건드린 커밋) |
| `source_digest` (RUN_SCOPE `src/ tools/ configs/ scripts/ run.sh requirements*.txt`) | **`d29650980daf6b9a`** |
| 직전 판정 | 60차 **NO-GO** — P0 13건 · P1 4건 |
| 이번 라운드 | 접수 17건 **전부 코드에서 닫음** + 자체 발견 9건 |

> **fetch 는 브랜치 head 로 해 주기 바란다.** 요청문은 자기가 담길 커밋 SHA 를
> 적을 수 없다. 그래서 둘을 나눈다:
>
> - **판정 대상 코드** = `c4e71004` — `source_digest d29650980daf6b9a` 이것을 가리킨다.
> - **이 문서** = 브랜치 head. `c4e71004` 이후 커밋은 RUN_SCOPE 를 **한 바이트도**
>   안 건드렸다 (아래 재현).
>
> ```
> git fetch origin claude/14-gate-code-review-9qkx05 && git checkout FETCH_HEAD
> cd degradation-degeneracy
> python3 -c "import sys; sys.path.insert(0,'.'); from src.io import source_digest; print(source_digest())"
> # → d29650980daf6b9a 이어야 한다. 아니면 그 자체가 발견이다.
> git log --oneline c4e71004..HEAD -- src tools configs scripts run.sh requirements*.txt
> # → 출력이 비어야 한다.
> ```

**RUN_SCOPE 밖이지만 이번 라운드가 크게 고친 파일 둘** —
`docs/22p_gap/row_projection.py` (producer identity) 와
`docs/22p_gap/mutation_replay.py` (변이 재생·증거층). 둘 다 `source_digest` 에
안 들어가지만 **cohort pin 과 변이 등록부의 정본**이므로 판정에는 브랜치 head
의 그 두 파일을 봐 주기 바란다 (`CLAUDE.md` 하드 룰 3).

**환경 안내.** 60차 판정문이 적은 대로 이 저장소의 전체 회귀는 `pybamm`·`tqdm`
을 요구한다. 없으면 그 두 의존성에 걸리는 시험이 **환경 실패**로 빨개진다
(코드 발견이 아니다). `requirements.txt` 로 설치하고 돌려 주기 바란다. 이번
라운드의 전체 회귀 수가 59차의 1196 → 1585 로 늘어난 것도 대부분 그 두
의존성이 이 기계에 깔렸기 때문이지 시험을 389개 더 쓴 것이 아니다 (이 라운드가
실제로 더한 시험은 60차 파일 9벌과 마감의 몇 건이다).

---

## §0 먼저 — 이번 라운드가 **하지 않은** 것

| 조건 | 상태 |
|---|---|
| **P0-1** producer 결속 — 닫힌 typed manifest 파싱 · 두 payload 압축해제 재해시 · producer 발행 영수증 | **미착수** (49차부터 **열두 라운드째**) |
| trusted launcher 의 source 측정 | **미착수** |
| **P0-4** typed 보존 영수증 **소비** | **부분** |
| 변이 증거의 **독립 replay** | **미착수** — 60차도 증언의 **범위**를 넓혔을 뿐(P1-3·P1-4), checker 가 스스로 재생하지는 않는다 |
| 묶음을 **immutable content-addressed object** 로 먼저 게시 | **미착수** — 60차는 내용 주소를 **기록**했을 뿐이다 (아래 ②) |
| 실행 class 5종 중 3종 미구현 · 등록부 삭제 절차 | **미착수** |
| baseline·sweep1d·wsweep 계획 gate · 실물 object-lock adapter · power-loss 모델 · publisher 전용 OS principal | **미착수** |
| 외적타당도 **#50** (`truth_provenance` 를 기계 계약에) | **미착수** |

### 이번 라운드가 스스로 신고하는 것

**① `staged_root()` 는 `/proc/self/fd/N` 이다 — Linux 의 성질이고 프로세스 지역이다.**

P0-4 를 닫으면서 gate 이후의 모든 쓰기를 판정한 handle 아래로 옮겼다. 그 방법은
handle 을 **경로로 노출**하는 것이다: production 의 writer 는 pandas·yaml 처럼
경로를 받는 라이브러리이고, 그것들을 전부 `openat` 으로 다시 쓰는 것은 이 라운드
범위를 넘으며 **다시 쓰는 동안 한 자리라도 빠지면 그 자리가 그대로 구멍**이다.

이 저장소는 이미 `/proc` 에 의존한다 (`fdinfo`·`mountinfo` 로 mount 좌표를 읽는다)
— 새 전제는 아니다. 그러나 다른 커널에서는 writer 를 `openat` 으로 옮겨야 하고,
이 경로는 이 프로세스 안에서만 뜻이 있다. 그 두 사실을 여기 적는다.

**② 묶음의 "검증 → 봉인" 창은 안 없어졌다 (P0-9).**

`bundle_content_id()` 가 검증이 **무엇을 봤는지**를 값으로 만들어 봉인에 넣는다.
그래서 나중에 바뀐 사실이 **기록 자체에서** 드러난다. 그러나 묶음이 mutable
directory 인 한 검증과 봉인 사이의 창 자체는 남는다. 종결은 판정문이 말한 대로
"묶음을 immutable content-addressed object 로 **먼저 게시**" 이고, 그것은 이
라운드의 범위 밖이다.

**③ 좌표 봉인은 TOFU 다 (59차 자체 발견의 연장).**

봉인 파일은 지역 파일이고 그것을 쓸 수 있는 자는 다시 쓸 수도 있다. 그러므로 이
층이 막는 것은 "봉인 뒤에 대상이 바뀌는 것" 이지 "처음 본 것이 남의 것인 경우" 가
아니다. 첫 봉인 시점에 이미 mount 속임수가 서 있으면 틀린 좌표를 굳힌다.

**④ 이름 공간 고정점은 "흘러든 결속" 만 본다 (P0-10 의 대가).**

첫 판은 "호출자가 값을 주는 이름은 이름 공간이 아님의 증명이 아니다" 로 **매개변수
일반**을 거부했다. 그랬더니 `getattr(df, 'columns')` 같은 정상 속성 읽기가 죽었다
(59차가 일부러 지킨 자리다 — 실측으로 되돌렸다). 그래서 지금 규칙은 **이름 공간이
실제로 흘러든 결속**만 namespace 이름으로 본다: 기본값 · `for` 대상 · `with as`.

**남는 구멍**: 호출자가 module 을 넘기는데 그 자리가 위 세 형태가 아니면
(예: 자료구조에 담아 전달) 고정점이 못 따라간다. 다만 그 경우 **능력을 부르는
자리**가 호출자 결속이 되므로 P0-10 의 둘째 층(호출자가 준 이름을 부르는 것은
거부)이 잡는다. 두 층을 같이 뚫는 형태가 있으면 그것이 이 항목의 반증 조건이다.

**⑤ import 증언은 "실행이 소비한 바이트 전부" 가 아니다 (P1-3·P1-4).**

`-X importtime` 이력으로 startup 이 **올렸다 지운** 것까지 담고, `PYTHONPATH` 는
문자열이 아니라 **그 자리의 최상위 module 바이트**로 담는다. 그래도 더 깊은
package 는 실제로 import 될 때만 이력이 잡고, pytest child 의 완전한 late-import
closure 는 여전히 밖이다. 종결은 §0 표의 독립 replay 다.

**⑥ `renameat2` 가 없는 커널에서는 link+unlink 로 물러선다 (P1-1).**

물러선 경로에서도 정리 실패를 삼키지 않고, 읽는 쪽이 `st_nlink == 1` 을 요구하므로
층은 둘이다. 그러나 "이름을 하나만 만든다" 는 **보장**은 `renameat2` 가 있는
커널에서만 성립한다.

**⑦ P0-11 의 방어는 관측 가능한 고유 효과가 없다 — 축을 `declared` 로 내렸다.**

shadow 를 scope 별로 좁힌 것은 의미가 맞다. 그런데 평평한 shadow 와 결과가
**갈라지는** 형태를 두 벌 지어 실측했더니 둘 다 변이 rc 0 이었다 — 능력을
**부르는** 형태는 P0-10 의 둘째 층이 평평한 shadow 아래서 오히려 더 넓게 물고,
능력을 **이름으로 들고 나오는** 형태는 58차 L9-b(`능력을 값으로 옮긴다`)가
shadow 와 무관하게 문다. 평평한 shadow 는 좁힌 것보다 **더 허용적**인데 더
허용된 자리를 전부 다른 규칙이 막고 있어 관측 가능한 차이가 비어 있다.
없는 자리를 지어내는 대신 `DECLARED_MASKED` 에 적었다 (48차
`idempotent-shares-the-validator` 와 같은 형태). 이것이 틀렸다면 — 두 규칙을
동시에 피하면서 scope 만으로 갈라지는 형태가 있다면 — 그것이 이 항목의 반증
조건이다.

---

## §1 발견별 — 무엇이 틀렸고 무엇을 바꿨나

판정문이 정리한 **네 형태**로 묶는다.

> ① capability 의 **발급·소비 authority 가 안 닫혔다**
> ② handle 검사가 **실제 쓰기가 끝난 뒤**에 온다
> ③ `lstat` 와 객체 snapshot 은 **bind mount** 와 **referent 교체**를 못 막는다
> ④ producer 의 "실행된다가 기본" 에 **평가 표면**이 빠졌다

| ID | 무엇이 틀렸나 | 무엇을 바꿨나 | 증인 (시험) | 변이 축 |
|---|---|---|---|---|
| P0-1 | 정상 `all → report` 가 늦은 manifest 로 identity 를 갈아 치워 **정상 실행이 마지막에 거부**된다 | 굳히는 순간의 manifest 목록·digest 를 `.run_identity.json` 에 봉인하고 이후 독자가 거기서 유도한다. 봉인 값은 봉인 시점의 v3 값과 **같다** — 값을 바꾸는 게 아니라 **얼린다** | `test_temporal_seal_60.py` 4건 | `run-identity-is-sealed-at-commit-g60` |
| P0-2 | raw sink 공개 · mint 가 caller 의 class 를 찍음 · 증인이 caller 와 **같은 객체** | sink 를 비공개로 + **callsite 열거** 구조 회귀 · `cls` 인자 삭제(자리가 정한다) · 권한은 **일련번호만** 들고 정본은 서버 쪽 발행 기록 | `test_issuance_authority_60.py` 4건 | `class-is-decided-by-the-place-g60` |
| P0-3 | 소비·거부 뒤 nonce 가 살아 있고 결속만 사라진다 | `issued → consuming` 원자 전이 · 성공 시 **영구 폐기** · 실패 시 `issued` 로 되돌리되 **결속 유지** | `test_issuance_authority_60.py` 2건 | `a-consumed-capability-is-retired-g60` |
| P0-4 | handle 이 마지막 commit 에만 닿아, 거부 전에 이미 밖에 바이트가 남는다 | gate 가 자리를 **만들고** handle 을 잡는다 · gate 이후 모든 쓰기가 `staged_root()` 아래로 · handle 없음은 **거부** | `test_staged_writes_60.py` 4건 | `the-gate-creates-the-judged-place-g60` · `grid-writes-under-the-handle-g60` |
| P0-5 | 파생 root 의 **부모 symlink** 를 따라 얼린 tree 에 token·claim 을 쓴다 | root 를 이름이 아니라 **대상**으로 연다 — `lstat` alias 거부 · `mkdir`(symlink 자리면 `EEXIST`) · **얼린 좌표를 덮으면 거부** | `test_lifecycle_roots_60.py` 4건 | `lifecycle-root-is-not-an-alias-g60` |
| P0-6 | journal 이 unchecked `write_text` — short write 뒤에도 freeze 성공, head 는 메모리 record | journal·head 를 이 저장소가 이미 세 번 만든 **검사하는 계단**에 올리고, anchor 를 **디스크에서 다시 읽은** journal 에서 유도 | `test_lifecycle_durability_60.py` 3건 | `journal-publish-reads-back-g60` |
| P0-7 | `lstat` 가 bind mount 를 평범한 inode 로 센다 | 구성원이 묶음 뿌리와 **같은 mount 인지** 커널에 묻는다 | `test_bundle_containment_60.py` 2건 | `bundle-members-share-the-root-mount-g60` |
| P0-8 | index 가 묶음 밖이어도 `full_bundle` | index 를 **구성원**으로 강제 + index 와 walk 의 **양방향** 대조 | 같은 파일 2건 | `payload-index-is-a-bundle-member-g60` |
| P0-9 | dict 는 굳히고 **그것이 가리킨 묶음**은 안 굳힌다 | `bundle_content_id()` 를 만들고 `finalize_leg()` 이 봉인에 넣는다 (한계는 §0-②) | 같은 파일 2건 | `finalize-seals-the-bundle-bytes-g60` |
| P0-10 | 매개변수·기본값이 module·resolver provenance 를 지운다 | **이름 공간 고정점**을 기본값·`for`·`with as` 로 넓히고, **호출자가 준 이름을 부르는 것**은 거부 (§0-④) | `test_producer_surface_60.py` 4건 | `a-caller-supplied-callee-is-refused-g60` |
| P0-11 | 중첩 scope 의 결속이 **바깥 scope** 를 면제한다 | shadow 를 **scope 별**로 (`_scoped_shadows()`) — M17 의 완화는 그 scope 안에서 그대로 산다 | 같은 파일 2건 | `shadows-are-scoped-g60` — **declared** (§0-⑦) |
| P0-12 | compound **head** 와 vararg/kwarg **주석**이 import-time 밖 | 둘 다 실행 슬라이스에 넣었다 | 같은 파일 5건 | `compound-heads-are-import-time-g60` (3경우) · `vararg-annotations-are-import-time-g60` (2경우) |
| P0-13 | module docstring 은 버리면서 `__doc__` 접근은 허용 | **버리는 것을 없앤다** — `_module_defs()` 가 module docstring 을 `__doc__` 로 묶는다 (51차 P0-I 가 정한 방향 그대로) | 같은 파일 1건 | `module-docstring-is-bound-g60` |
| P1-1 | hardlink 게시가 temp alias 를 남기고(`nlink=2`) 정리 실패를 삼킨다 | `renameat2(RENAME_NOREPLACE)` 로 **옮긴다** — 물음 자체를 없앤다 · fallback 은 실패를 안 삼킨다 · **읽는 쪽이 `st_nlink==1` 요구** | `test_one_name_publish_60.py` 4건 | `a-record-has-exactly-one-name-g60` |
| P1-2 | phase receipt 도 검사한 것과 봉인한 것이 다르다 | 진입 즉시 정규 바이트로 굳힌다 (M9 와 같은 규칙) | `test_bundle_containment_60.py` 1건 | `phase-receipt-is-snapshotted-g60` |
| P1-3 | startup 뒤 `sys.modules` snapshot 은 **상태**이지 이력이 아니다 | `-X importtime` 으로 **실제 import 이력**을 받아 해시한다 | `test_import_closure_60.py` 3건 | `startup-history-is-measured-g60` |
| P1-4 | full receipt 가 startup 뒤 import 되는 바이트를 안 담는다 | `PYTHONPATH` 를 문자열이 아니라 **그 자리의 바이트**로 담는다 | 같은 파일 2건 | `importable-roots-are-measured-g60` |

---

## §2 증거 — 전부 이 브랜치 head 에서 실행한 출력이다

### 2.1 판정 좌표

```
판정 대상 코드          c4e710040c2631d4f8140ee31c2f3c5004d9bcbb
source_digest          d29650980daf6b9a          (직전 4fe8d27269ca9ca2)
그 뒤 RUN_SCOPE diff    없음
    git log --oneline c4e71004..HEAD -- src tools configs scripts run.sh requirements*.txt
    → 빈 출력
```

### 2.2 회귀

```
python -m pytest tests/ -q      1585 passed, 1 xfailed   (39분 07초)
./scripts/smoke_e2e.sh          pipeline smoke 통과       (clean 커밋에서)
```

둘 다 이 문서 직전 커밋(전수 재생 증거를 담은 커밋)에서 받은 출력이다. smoke 는
이 저장소 규칙대로 **clean 커밋에서만** 돈다.

### 2.3 변이 등록부와 전수 재생

```
MUTANTS 193 · MULTI 30 · EXPECT 214 · DECLARED_MASKED 10 · 60차 축 19

--check-preimages               모든 변이 지점이 정확히 한 번 나타난다
slice 1..12 (한 HEAD 에서 순차)  전부 rc=0
--check-coverage s*.json        등록부 scenario 223 (executable 213 · declared 10)
                                조각 12개에서 관측 223
                                조각 합집합이 등록부 전체를 정확히 덮었다
```

**전수 재생을 네 번 돌렸다.** 앞의 세 번은 재생 자신이 낸 발견 때문에 트리를
고쳐 처음부터 다시 돌렸다 — 조각마다 다른 코드에서 난 coverage 는 합집합의
근거가 못 된다. 무엇을 잡았는지는 §3 에 적는다.

### 2.4 cohort 세대 전환 (g14 → g15)

```
g14_2026_09_08  active → frozen  (journal seq 13)
g15_2026_09_08  새 active · docs/22p_gap/proj_g15

pin  compute            c02b963e5d65bb55 → 3b94bda70dc63869
     row_projection     c9bdaa2b33ad6ed4 → a425da3233253625
     producer_semantic  1c768c143c35e43c → 6518c2fa47f1e8c4
     src_scoring        69e69cb046f4b4ae (변동 없음)
영수증 core_sha256       d15881088e022ce6417b54a4d489094e75c125e9f9db6e5f5f2a47db0bdd93ff
validator                d29650980daf6b9a
행 바이트                 ad598fe77e75afec — **열한 세대째 같다**
```

대상 커밋: `f79840bc34b785a2ba4bd95a116df9604c7d13ed`
— 위 `core_sha256` 은 이 커밋의
`docs/22p_gap/receipts/paired_fixed5_v4.validate.yaml` 을 가리킨다 (세대를
넘긴 커밋이고, 그 뒤로 영수증은 안 바뀌었다). 요청문이 인용한 값은 **그것이
이름한 커밋**에 대고 대조하는 것이 자기완결의 뜻이다 — 다음 라운드에 영수증이
바뀌어도 이 문서는 거짓이 되지 않는다.

`evidence.cohorts` 갱신은 **g15 의 구성원에게만** 해야 한다 — 처음에 전체 다리에
넣었다가 "cohort 선언이 양방향으로 맞지 않는다" 로 lint 가 잡았다.

---

## §3 이 라운드가 스스로 잡은 것 (9건)

**① P0-1 을 고치다 P0-1 과 같은 종류의 가용성 결함을 두 번 만들었다.**
"한 번만 봉인" 이 정상 **재개**를 죽였고, "낡은 봉인은 거부" 가 프로세스를 넘는
정상 **e2e** 를 죽였다. 둘 다 실측이 뒤집었고, 규칙을 "굳히는 순간마다 다시 봉인 ·
낡은 봉인은 무시" 로 고쳤다. 판정문의 첫 문장("가장 먼저 닫아야 할 것은 공격
반례가 아니라 정상 production 순서다")을 고치는 동안 같은 실수를 반복한 것이다.

**② 59차가 "한계" 라고 신고한 것이 사실은 정상 경우였다.**
"gate 시점에 자리가 없으면 handle 이 없다" 는 드문 모서리가 아니라 **언제나**였다
(grid 는 `mkdir` 보다 먼저 gate 를 지난다). 즉 "권한이 판정한 대상을 나른다" 는
59차의 문장은 실제로 아무것도 안 나르고 있었다. **신고한 한계도 측정해야 한다.**

**③ 시험 하나가 처음부터 초록이었다.**
journal anchor 를 고치며 "anchor 가 journal 마지막 줄과 같은가" 를 물었는데, 두
값을 **같은 식이 만들므로** 아무것도 구별하지 못했다. 잘림이 아니라 **변조**(같은
길이·다른 내용)를 주입하는 시험으로 바꿔서야 물었다.

**④ 승격 검사 시험이 자기 축을 안 봤다.** smoke 자리로 쓰면 경로 판정이 먼저
걸린다 — canonical 자리로 고쳤다.

**⑤ 변이 축 둘이 false-green 이었다.** 하나는 겨누는 자리가 시험이 부르는 함수가
아니었고, 다른 하나는 probe 가 **저장소 뿌리를 상수로 박아** sandbox 안에서도 원본을
import 했다. 게다가 그 시험은 `unshare` 가 안 되는 환경에서 통째로 **건너뛰어진다**
— 건너뛴 시험은 방어를 지키지 않는다. 좌표 비교만 겨누는 시험을 하나 더 뒀다.

**⑥ 죽은 변이 축 5건.** 방어를 옮기면 그것을 겨누던 변이의 원상이 파일에서
사라진다. 전부 `--check-preimages` 가 먼저 잡았고 다시 겨눠 무는 것을 확인했다.
그 중 `execution-class-record-is-exclusive-g58` 은 배타 지점이
`O_EXCL` → `link` → `renameat2` 로 **세 번째** 옮겨 간 자리였다.

### 그리고 마감의 전수 재생이 **같은 형태를 네 번** 잡았다

**⑦ 방어를 넓히면 그 방어가 다른 시험의 축을 가린다.** 이번 라운드의 대표
교훈이고, 전수 재생 없이는 넷 다 초록으로 보였다.

| 새 방어가 | 가린 축 | 어떻게 드러났나 | 어떻게 고쳤나 |
|---|---|---|---|
| P0-8 (index 는 구성원이어야 한다) | `bundle-members-are-not-followed-g59` | "빨개졌지만 **선언한 이유가 아니다**" — 증인 문자열이 실패 메시지에 없다 | 그 시험의 fixture 에서 index 를 묶음 안으로 옮김 |
| P0-12 (`If.test` 가 실행 슬라이스 안) | `module-assert-runs-at-import-g59` | 실패 집합이 선언과 다르다 — `if False: raise …` 가 안 빨개짐 | `Try` 로 감싼 module-level `raise` 를 더함 (`Try` 는 head 가 없어 `MODULE_EFFECTS` 로 안 묶인다) |
| P1-3·P1-4 (이력·PYTHONPATH 바이트) | `startup-binds-every-loaded-module-g59` | 변이 rc 0 — `startup_modules` 를 통째로 지워도 안 빨개짐 | 경로로 올려 `sys.modules` 에 심은, **이름으로 못 찾는** module 을 겨누는 시험 |
| P1-4 (`importable_roots`) | P1-3 의 두 시험 | 새 축 `startup-history-is-measured-g60` 이 처음부터 안 물었다 | package 의 **하위** module 을 올렸다 지우는 시험 (최상위만 보는 층은 못 본다) |

세 번째 것이 가장 위험했다 — **필드를 지워도 아무 시험도 안 빨개지면 그 필드는
"있는 척" 이다.** 세 층이 갈라지는 자리를 겨누는 시험을 새로 지어 고유한 증인을
되살렸다.

**⑧ 그래서 이번 라운드 방어 **전부**에 축이 있는지 셌다 — 다섯이 없었다.**
θ 둘(P1-3 `startup_history` · P1-4 `importable_roots`)과 ζ 셋(P0-12 의 두 자리 ·
P0-11). 이 요청문의 초안은 그 자리를 "cohort pin 이 움직인 것이 증거다" 로 두려
했는데, 그것은 증거가 아니라 **부작용**이다. 넷은 심어서 물었고, P0-11 은
관측 가능한 고유 효과가 없어 신고로 내렸다 (§0-⑦).

**⑨ 증인이 못 되는 시험 하나를 도로 뺐다.** P0-11 의 축을 살리려고 지은
시험이 실은 다른 규칙에 걸려 초록이었다. **이름이 주장하는 것을 안 물면 그것은
증거가 아니라 장식이다.**

---

## §4 판정 대상이 아닌 것 (혼동 방지)

이 라운드는 **계산식을 안 건드렸다.** cohort 를 `g14` 에서 `g15` 로 넘겼지만
투영의 행 바이트는 `ad598fe77e75afec` 로 **열한 세대째** 같다. pin 이 움직인 이유는
producer analyzer 의 **평가 표면**이 넓어졌기 때문이고(P0-12·P0-13), `src.scoring`
과 analysis spec 은 안 움직였다. 그래도 **cross-cohort 비교는 금지**다 — 같은
바이트라는 사실은 회귀가 확인하는 것이지 인용의 근거가 아니다.

연구 수치의 정본은 artifact 와 `docs/RESULTS*.md` 이고, 이 문서의 숫자는
**게이트 판정용 좌표**다.
