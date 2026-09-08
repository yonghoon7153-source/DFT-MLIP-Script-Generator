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
| P0-1 | M2 | 정상 `all → report` 가 `analysis_manifest.yaml` 을 늦게 써서 content id 가 바뀌고 class 가 사라진다 → **정상 실행이 마지막에 거부됨(가용성 결함)** | α | 미착수 |
| P0-2 | M1 | 공개 `record_execution_class(run_dir, cls,…)` raw sink · `issue_execution_class(…, cls,…)` unrestricted mint · `_ISSUED_EXEC_CAPS` 가 caller 의 **같은 mutable object** 를 증인으로 씀 | β | 미착수 |
| P0-3 | M1·M5 | commit/거부 뒤 **nonce 가 살아 있고** `dir_fd=None` 이라 두 번째 호출이 미판정 자리를 canonical 로 굳힌다 | β | 미착수 |
| P0-4 | M5 | capability fd 는 마지막 commit 에만 닿는다 — grid chunk/parquet/manifest 는 pathname 으로 쓰여 bind swap 시 **밖에 이미 바이트가 남는다** | γ | 미착수 |
| P0-5 | M6·M10 | `_claims`/`_attempts` root 가 pathname 유도라 **부모 symlink** 를 따라 frozen tree 에 token·claim 을 쓴다 | δ | 미착수 |
| P0-6 | — | lifecycle journal temp 가 unchecked `write_text` — **short write 뒤에도 freeze 성공**, head 는 메모리 record 로 만든다 | δ | 미착수 |
| P0-7 | M8 | `lstat` walk 가 **bind mount 된 밖의 파일**을 평범한 inode 로 센다 | ε | 미착수 |
| P0-8 | M8 | `payload_index` 가 bundle member 일 필요가 없다 — repo 안 gitignored 경로여도 `full_bundle` | ε | 미착수 |
| P0-9 | M9 | dict 는 snapshot 하지만 **그것이 가리킨 bundle** 은 안 한다 — 검증 뒤 ledger commit 전 member 교체 성공 | ε | 미착수 |
| P0-10 | M11·M17 | parameter/default 가 module·resolver provenance 를 지운다 (`namespace=sc` · caller 가 `sc`·`getattr` 을 전달) | ζ | 미착수 |
| P0-11 | M17 | `_binding_shadows()` 가 `ast.walk` 로 **중첩 scope 의 parameter** 를 바깥에 적용 + subscript callee 우회 | ζ | 미착수 |
| P0-12 | M12 | compound **head**(`If.test`·`While.test`·`For.iter`·`With`·`Match.subject`) 와 **vararg/kwarg annotation** 이 import-time 밖 | ζ | 미착수 |
| P0-13 | M12 | module docstring 은 버리면서 **`__doc__` 접근은 허용** — 문서 문자열로 값이 흐른다 | ζ | 미착수 |
| P1-1 | M3·M13 | hardlink 게시가 temp alias 를 남기고(`nlink=2`) unlink 실패를 삼킨 채 성공 | η | 미착수 |
| P1-2 | M9 | `phase_done()` 이 caller dict 를 **lock 밖에서 검사하고 같은 reference 를 나중에 직렬화** | ε | 미착수 |
| P1-3 | M14 | startup 에서 실행됐다 `sys.modules` 를 떠난 byte 를 probe 가 못 본다 | θ | 미착수 |
| P1-4 | M15 | full receipt 가 **startup 뒤 import 되는 byte** 를 안 담는다 | θ | 미착수 |

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
