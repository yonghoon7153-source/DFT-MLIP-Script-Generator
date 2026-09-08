# 59차 게이트 작업 상태 — **정본**

58차 요청에 대한 판정: **NO-GO**. P0 최소 반증 조건 **12건** · P1 4건 · P2 1건.

리뷰어가 판정한 좌표: production RUN_SCOPE `bbba9aa3` · branch head `fa31b6a0`.
그 뒤 우리가 올린 커밋(`0916c8cf`·`3a0b1512`·`9bd85223`·`527f91e8`)은 RUN_SCOPE 를
안 건드렸고 `row_projection.py` 도 안 건드렸다 — **P0 발견은 전부 현행 트리에
그대로 적용된다.** (`mutation_replay.py` 만 변이 등록부 쪽이 바뀌었다.)

## 판정을 받아들이는 이유 — 두 건은 즉시 확인했다

| 발견 | 확인 방법 | 결과 |
|---|---|---|
| P0-1 | `record_run_outputs(` 호출 grep | **정의·주석·docstring 뿐. 실호출 0곳** |
| P0-2 | `_EXEC_ID_MANIFESTS` vs production writer | 등록부는 `curves/fits/manifest.yaml`, production 은 `curves_manifest_start.yaml` 을 쓴다 (`src/grid.py:645`) |

P0-1 은 우리 docstring 이 스스로 자백하고 있었다 — "호출자는 이 목록을 무시해도
된다" 와 "산출이 굳는 순간 기록한다" 는 **동시에 참일 수 없다**. 요청문 §1 의
L1 줄("조기 return 자리가 반드시 그것을 거치게")은 gate 시점만 말하고 **완료
시점을 말하지 않았다**. 그 문장이 과대 주장이었다.

## 이번 판정의 세 형태 (리뷰어 요약을 그대로 옮긴다)

1. 새 primitive 가 production 의 **산출 commit 에 닿지 않는다** (L1).
2. 판정은 한 시점의 pathname·caller object 를 보고, **쓰기/봉인은 나중의 것을
   다시 연다** (L4·L5·L7·L10).
3. "닫힌 descriptor/closure" 라고 부른 **입력 집합이 실제 schema 보다 작다**
   (L2·L9·L11·L12).

우리가 58차에 "물음을 바꿨다" 고 적은 수정들이, 이 셋 중 하나로 다시 열렸다.

## 발견 원장 (17건)

상태: `대기` → `RED` (재현 테스트가 빨감) → `GREEN` → `변이` (등록부 anchor)

| ID | 등급 | 한 줄 | 자리 | 상태 |
|---|---|---|---|---|
| M1 | P0 | 완료 시 class 기록이 production 에 배선 안 됨 (`record_run_outputs` 실호출 0) | `preserve.py:6754` · `grid.py:407` · `fitting.py:888` | **GREEN** |
| M2 | P0 | content id 가 production start manifest 를 누락 | `preserve.py:4238` | **GREEN** |
| M3 | P0 | final `O_EXCL` 파일이 부분 바이트로 공개되고 성공 | `preserve.py:4417-4441` | **GREEN** |
| M4 | P0 | shared/local class 충돌을 reader 가 canonical 로 숨김 | `preserve.py:4458-4473` | **GREEN** |
| M5 | P0 | smoke 검사 직후 bind swap → 실제 쓰기가 밖으로 (TOCTOU) | `is_inside_namespace()` 소비자 전부 | **GREEN** |
| M6 | P0 | clean clone 에서 marker+ledger 만으로 frozen 못 지킴 | `row_projection.py:4388-4474` | **GREEN** |
| M7 | P0 | `fit → grid` 역순이면 consumed 결속 없이 executed | `preserve.py:5033-5114` · `6532-6546` | **GREEN** |
| M8 | P0 | bundle member symlink/bind 로 repo 밖 바이트 | `preserve.py:6185-6211` · `_verify_declared_bundle` | **GREEN** |
| M9 | P0 | 검증한 evidence 와 봉인한 evidence 가 다르다 (caller dict TOCTOU) | `preserve.py:6427-6624` | **GREEN** |
| M10 | P0 | 공개 `claim_planned_leg(token=…)` 가 disk token 없는 running 생성 | `preserve.py:5466-5556` | **GREEN** |
| M11 | P0 | capability 의 module target 을 식으로 감싸면 closure 밖 | `row_projection.py:1290-1305` · `1454-1461` | **GREEN** |
| M12 | P0 | import-time 실행 모델이 `assert`·metaclass·future flag 를 버림 | `row_projection.py:627` · `_has_import_time_compute` | **GREEN** |
| M13 | P1 | class durability 재시도가 실패한 parent fsync 를 안 고침 | `preserve.py` 등록부 | **GREEN** |
| M14 | P1 | startup probe 가 `sitecustomize` 의 transitive import 를 안 묶음 | `mutation_replay.py` `_ENV_PROBE_BODY` | **GREEN** |
| M15 | P1 | `environment_tag()` 가 full receipt 아니라 `startup` 만 증언 | `mutation_replay.py:3588-3603` | **GREEN** |
| M16 | P1 | 내 회귀 하나가 이 환경에서 자기 축을 실행 안 함 (`254:0` 하드코딩) | `test_frozen_coordinate_seal_58.py:192` | **GREEN** |
| M17 | P2 | 능력 escape 규칙이 무해한 local shadow 도 거부 (Q1 의 답: 그렇다) | `_assert_no_dynamic_resolution` | **GREEN** |

## 묶음 (같이 고쳐야 값이 나오는 것)

- **α — capability 를 산출 commit 까지**: M1 · M3 · M4 · M13.
  gate 가 raw pending 이 아니라 **sealed capability** 를 주고, 모든 output commit 이
  그것을 소비하게. 등록부 게시는 temp→read-back→CAS→parent fsync.
- **β — handle 을 끝까지 들고 간다**: M5 · M6 · M8 · M9.
  네 건이 **같은 병**이다: 판정은 이름/객체를 한 번 보고, 쓰기는 나중에 다시 연다.
  `openat`/dirfd identity 를 authorization 부터 commit 까지 carry 하고, caller
  evidence 는 진입 즉시 canonical bytes 로 deep snapshot.
- **γ — schema 를 하나로**: M2 · M7.
  content id 와 phase 결속이 **production artifact schema** 에서 유도돼야 한다.
- **δ — producer identity 를 실행 의미로**: M11 · M12 · M17.
  AST 종류를 더하는 대신 module initialization **execution slice** 를 모델링.
  못 답하면 fail-closed. M17 은 그 규칙의 정밀도 문제라 같이 본다.
- **ε — 증거층**: M14 · M15.
  child 가 full canonical receipt 를 증언하거나 hermetic runner.
- **ζ — 공개 API 표면**: M10. (작다. 단독)

## 순서 (정한 것)

1. **M16** — 내 회귀의 이식성 결함. 가장 싸고, 리뷰어 재실행을 초록으로 만든다. ✅
2. **α** (M1·M3·M4·M13) — 판정의 머리. "배선이 없다" 는 가장 큰 거짓이었다.
3. **γ** (M2·M7) — schema 유도. α 와 같은 파일을 만진다.
4. **β** (M5·M6·M8·M9) — 네 건을 한 벌로. 가장 크다.
5. **δ** (M11·M12·M17)
6. **ε** (M14·M15) · **ζ** (M10)
7. 마감: 등록부 새 축 → cohort 전환 → 12조각 → 회귀+smoke → 요청문

## 하지 말 것

- **완료 함수가 caller 에게 raw `cls` 를 다시 받게 하지 않는다** (M1 의 최소 조건이
  명시). 그러면 같은 우회가 남는다.
- **AST 종류를 하나씩 더해서 M12 를 닫지 않는다.** 57·58차가 두 번 거절당한 방식이다.
- **경로 검사에 패턴을 더해서 M5·M8 을 닫지 않는다.** handle 을 들고 가는 것이 답이다.
- 조각·요청문은 **코드가 다 끝난 뒤** 한 번에 (§65).

## 마감까지 미뤄 둔 것 (지금 빨간 것의 전부)

| 무엇 | 왜 지금 안 고치나 | 언제 |
|---|---|---|
| `test_docs_lint.py::test_full_bundle_claims_are_backed_by_a_real_bundle` — `paired_fixed5_v4` 영수증이 `920cfd31c22ebe06` 을 가리키는데 현행 core sha 는 계속 움직인다 (α 뒤 `47afc7e4`, γ 뒤 `a594d426`) | RUN_SCOPE(`tools/preserve.py`·`src/`)를 고칠 때마다 `source_digest` 가 바뀌는 것이 **정상**이다. β·δ·ε·ζ 가 같은 파일을 더 만지므로 지금 만들면 또 낡는다 | 마감 (§65: 조각·영수증·요청문은 코드가 다 끝난 뒤 한 번에) |
| 활성 cohort `g13` 의 pin 이 현행 트리에서 벗어났다 (`compute_sha256`·`row_projection_py_sha256`) — `test_exactly_one_cohort_is_active_…` · `test_projection_analyzer_digests_recompute_…` | β(M6)가 `row_projection.py` 를 고쳤고 **δ(M11·M12·M17)가 같은 파일을 더 고친다**. 지금 전환하면 또 벗어난다 | 마감 (g13 freeze → g14) |
| 변이 등록부에 **γ·β 의 새 축이 아직 없다** (M2 schema 거부 · M7 순서/`consumed` 필수 · M5 handle 결속 · M6 봉인 없으면 거부 · M8 lstat walk · M9 deep snapshot) | EXPECT 측정에 재생이 필요하고, 그 사이 코드가 또 바뀌면 다시 측정해야 한다 | 마감 (등록부 새 축을 한 번에) |

그 밖에는 **전부 초록이다** (β 뒤 전체 회귀 실측: **1508 passed · 3 failed** — 위 표의 세 건).

## 진행 로그

- 2026-09-08 — 판정 접수. P0-1·P0-2 를 grep 으로 즉시 확인(둘 다 사실).
  M16 을 먼저 닫았다: 좌표를 현재 mount table 에서 유도하고 후보가 하나 이상임을
  **먼저 단언**한다. 전제가 깨지면 그 사실이 보이게.

- 2026-09-08 — **α 닫힘** (M1·M3·M4·M13). 새 시험 9건
  (`tests/test_exec_class_capability_59.py`), 전부 고치기 전에 빨갰다.

  - **M1** — gate 가 목록이 아니라 **권한**(`ExecutionClassCapability`, frozen
    dataclass + 모듈 비공개 nonce 등록부)을 발행하고, `commit_run_outputs()` 가
    그것을 **요구**한다. class 는 권한이 나르므로 raw `cls` 를 받는 완료 함수는
    없다 — `record_run_outputs()` 를 **삭제**했다 (최소 조건이 명시한 우회로).
    배선: `src/grid.py` gate → `write_curves_manifest(capability=…)`,
    `src/fitting.py` gate → `_run_fit_locked(exec_capability=…)` → fit manifest
    가 굳는 자리. legacy 분류는 `LEGACY_EXEC_CLASS_ROSTER` 네 자리로 닫았다.
  - **M3** — 등록 게시를 temp → write-all → fsync → **바이트 read-back** →
    `os.link()`(no-replace CAS) → parent fsync 로 뒤집었다. `O_EXCL` 은 이름
    배타일 뿐 내용 완전성이 아니다. (리뷰어 반례의 한 바이트 short write 는
    `_write_all()` 의 loop 가 이미 이어 쓴다 — 실측. 그래서 시험은 loop 를
    우회해 **read-back 층**을 겨눈다. 그 층이 진짜 구멍이었다.)
  - **M4** — `read_execution_class()` 가 공유·국소 **양쪽을 다 읽고**, 어긋나면
    두 class 를 이름으로 말하며 거부한다.
  - **M13** — 성공의 출구를 `_seal_exec_class_record()` **하나**로 모았다.
    새 게시든 같은 class 멱등 재시도든 똑같이 레코드를 다시 읽고 parent 를
    다시 굳힌다 (32차 P0-3 이 `_mkdir_durable()` 에서 내린 결론과 같다:
    "durable 한지 구별할 수 없으면 항상 굳힌다"). 등록부 층 자체도
    `_mkdir_durable()` 로 만든다.

  **다른 시험 5건이 이 계약 변화로 빨개졌고, 전부 계약을 따라 고쳤다** (약화가
  아니라 이동이다 — 근거는 각 시험의 docstring):
  `test_execution_class_wiring_58.py` 2건(gate 가 쓰던 것 → gate 가 발행하고
  commit 이 쓴다), `test_preserve.py` 1건(면제 분기가 이제 다리 이름을 검사하므로
  sentinel `__계획에없는다리__` 를 형식에 맞는 `unplanned-leg` 로 — 옛 이름이면
  두 절반이 **모두** 형식 오류로 죽어 명제를 한 번도 안 본다),
  `test_execution_class_p0_8.py` 1건(roster 를 실제로 태운다),
  `test_fitting.py` fixture 1건(권한을 발행한 뒤 manifest 를 굳힌다).

  **변이 등록부 두 축이 죽어 있었다** (`check_coverage()` 가 거부해서 발견):
  `module-gate-before-side-effects` 의 원상이 gate 반환 쌍으로 바뀌었고,
  `execution-class-record-is-exclusive-g58` site 1 의 배타 지점이 `O_EXCL` 에서
  `os.link()` 로 옮겨졌다. 둘 다 새 원상으로 고쳐 **다시 문다** (실측: 각각
  `물었다 … node 1`). 이것이 이 저장소가 반복해 배운 문장이다 — 방어를 옮기면
  그것을 증명하던 변이가 조용히 무해해진다.

- 2026-09-08 — **γ 닫힘** (M2·M7). 새 시험 6건
  (`tests/test_run_schema_binding_59.py`), 전부 고치기 전에 빨갰다.

  - **M2** — `_EXEC_ID_MANIFESTS` 를 `RUN_MANIFEST_SCHEMA` 로 승격했다. 옛
    목록은 production 과 **두 방향으로** 어긋나 있었다: 빠진 것
    (`curves_manifest_start.yaml`·`manifest_start.yaml`·`analysis_manifest.yaml`·
    `manifest_grid.yaml`)과 **없는 것**(`fits_manifest.yaml` — 쓰는 곳이 0곳).
    이름을 더하는 대신 세 층으로 닫았다:
      (a) 선언을 authority 로 두고,
      (b) 구조 시험이 `src/`·`tools/` 의 manifest 이름 리터럴 집합과 **양방향**
          동일함을 강제하며 (새 이름이 생기는 순간 빨개진다),
      (c) 런타임에 선언 밖 manifest 를 만나면 **거부**한다 (불완전한 identity 로
          정한 class 는 다른 내용에도 적용되므로).
    descriptor 형식 표시를 상수 `_CONTENT_ID_KIND = "run-content-id/v3"` 로 뺐다.
  - **M7** — 결속을 **선택 사항에서 필수로** 바꿨다. `phase_done()` 은 뒤 phase 를
    선행 phase 가 전부 닫히기 **전에는 거부**하고, 닫을 때 `consumed` 에 **모든**
    선행 phase 를 담는다. `finalize_leg()` 은 `if not _want: continue` 를 버리고
    빠진 결속을 **오류**로 만든다. 58차판은 "있으면 검사, 없으면 통과" 였고,
    리뷰어는 역순 실행으로 결속 없는 durable state 를 만들어 `executed` 를 받았다.

  **등록부 re-key (v2 → v3)**. 내용 identity 형식이 바뀌어 기존 tracked 레코드
  4건의 키가 안 맞는다. 58차의 v1→v2 와 **같은 규칙**으로 처리했다 — 경로를 다시
  보고 정하지 않고 (그건 M1 이 없앤 세탁 경로다) v2 레코드의 class 를 승계하고
  어느 키에서 왔는지를 `evidence` 에 적었다. 등록부는 tracked 4(v1) + 4(v2) +
  4(v3) = 12건.

  | 산출 | v2 키 | v3 키 |
  |---|---|---|
  | `results/grid_curves_v4` | `dbf46c587d…` | `d0d7eacedb…` |
  | `results/grid_fit_v4` | `fc8a5c90a5…` | `465748dc8d…` |
  | `results/halfcell_fit_v4` | `7fc65fbd51…` | `68829b5d3f…` |
  | `results/paired_fixed5_v4` | `0656f29383…` | `f37e21c8a4…` |

  **낡은 시험 하나가 없는 파일로 명제를 증명하고 있었다.** 58차 L2 회귀
  (`test_two_fits_sharing_curves_do_not_share_a_content_id`)가 fit manifest 로
  `fits_manifest.yaml` 을 썼는데 그 이름은 저장소 어디서도 쓰이지 않는다.
  production 이 실제로 쓰는 `manifest.yaml` 로 바꿨다 — 명제는 그대로다.

  **변이 축 하나가 또 죽어 있었다**: `content-id-hashes-every-manifest-g58` 의
  원상이 descriptor 리터럴이었는데 형식 표시가 이름으로 바뀌었다. 새 원상으로
  고쳐 다시 문다 (실측: `물었다 … node 1`).

- 2026-09-08 — **β 닫힘** (M5·M6·M8·M9). 새 시험 8건
  (`tests/test_handle_carry_59.py` 5 · `tests/test_frozen_clean_clone_59.py` 3),
  M8 의 "정상 묶음은 통과한다" 하나를 빼고 전부 고치기 전에 빨갰다.

  네 건은 같은 병이었다 — **판정은 이름/객체를 한 번 보고, 쓰기·봉인은 나중의
  것을 다시 연다.** 그래서 넷을 한 벌로 고쳤다.

  - **M5** — 권한이 class 만이 아니라 **gate 가 판정한 대상**도 나른다.
    발행 시점에 그 디렉터리를 `O_DIRECTORY|O_NOFOLLOW` 로 열어 `dir_fd` 를 들고
    가고, 굳히는 자리는 (a) 그 handle 로 manifest 를 읽어 identity 를 만들고
    (b) 지금 그 이름이 **같은 커널 객체**인지 확인한다. 이름 아래가 바뀌었으면
    (bind·rename) 거부한다. 한계 하나를 남긴다: gate 시점에 자리가 아직 없으면
    들고 갈 handle 이 없고, 그때는 이름으로 연다 — 요청문에 적는다.
  - **M6** — **이 발견은 실물로 확인됐다.** 이 기계의 frozen cohort **12개 중
    11개에 좌표 봉인이 없었다** (`g12` 하나만 있었다 — 58차에 봉인 코드가
    생긴 뒤 얼린 것이라서). 58차가 만든 첫 층이 실제로는 cohort 하나에만 살아
    있었다는 뜻이고, 리뷰어 지적이 정확했다. 좌표는 기계의 사실이라 clone 에
    담을 수 없으므로 답은 하나뿐이다 — **봉인 없는 frozen cohort 가 하나라도
    있으면 게시하지 않는다.** 빠져나갈 길은
    `row_projection.py --seal-frozen` 이고 선언된 것을 **전부** 덮는다
    (하나씩 봉인하게 하면 빠뜨린 하나가 조용한 구멍이 된다).
    이 기계는 그 명령으로 11건을 봉인했다.
  - **M8** — 묶음 구성원 walk 를 `is_file()`(이름을 따라간다)에서 `lstat` 으로
    바꾸고, symlink·비일반 파일 구성원을 **거부**한다. 58차 L7 이 `bundle_uri`
    자신에 대해 고친 것과 같은 흡수인데 그때 뿌리만 고치고 구성원은 안 고쳤다.
  - **M9** — `finalize_leg()` 이 진입에서 evidence 를 **정규 바이트로 굳히고**
    그것을 다시 읽어 쓴다. 58차는 얕은 복사였고 그마저 lock 을 잡고 원장을
    읽은 한참 뒤였다 — 중첩 값은 계속 공유됐다. 깊이에 상관없이 끊어지므로
    "어느 층까지 복사할까" 를 안 물어도 된다.

  **48차 회귀 하나의 일정이 불법이 됐다.** `test_two_phase_records_do_not_
  overwrite_each_other` 는 grid·fit 을 아무 순서로나 동시에 닫았는데, M7 이
  순서를 강제하면서 그 일정 자체가 불법이 됐다. 그대로 두면 순서 거부로 빨갈
  뿐 원래 명제(경쟁 아래 lost update)를 한 번도 안 본다. **명제는 유지하고
  일정만 합법으로** 바꿨다 — 두 스레드가 같은 claim record 를 동시에 두드리되
  fit 은 grid 가 닫힐 때까지 재시도한다 (실제 coordinator 가 하는 일이다).
  결속이 실제로 닫힌 grid 를 가리키는지도 같이 단언한다.

  **변이 축 하나가 또 죽었다**: `lifecycle-owned-evidence-is-refused-g58` 의
  원상이 `_assert_evidence_domain(evidence)\n    import yaml` 두 줄이었는데
  그 사이에 M9 의 deep snapshot 이 들어왔다. 도메인 검사 한 줄만 원상으로
  좁혀 다시 문다 (실측: `물었다 … node 6`).

  **이번 라운드 네 번째 죽은 변이다** (α 2 · γ 1 · β 1). 방어를 옮기면 그것을
  증명하던 변이가 조용히 무해해진다 — 매 묶음마다 `--check-preimages` 를
  돌리는 것이 이 라운드의 규율이 됐다.

- 2026-09-08 — **δ·ζ·ε 닫힘. 17건이 전부 GREEN 이다.** 새 시험 24건
  (`test_import_time_slice_59.py` 16 · `test_issuance_surface_59.py` 3 ·
  `test_evidence_layer_59.py` 3, 그리고 M17 의 반대 방향 2건).

  ### δ (M11·M12·M17) — 물음을 뒤집었다

  57·58차는 **AST 종류를 하나씩 더해** 이 축을 두 번 닫으려 했고 두 번
  거절당했다. 종류를 세는 한 다음 종류가 남는다. 그래서 기본값을 바꾼다:
  **실행된다** 를 기본으로 두고, **실행되지 않음을 증명할 수 있는 것만** 뺀다.

  - **M11** — 능력의 대상을 "module 인가" 로 알아보는 대신 **"module 이 아님을
    증명할 수 있는가"** 로 묻는다. 증명 가능한 형태는 둘뿐이다 (이름 공간 이름이
    아닌 벌거벗은 이름 · 뿌리가 그런 이름인 속성 사슬). 여섯 가지 감싸기
    (`[sc][0]` · `(sc,)[0]` · `(sc if True else sc)` · `{'m': sc}['m']` ·
    `(lambda m: m)(sc)` · `(None or sc)`)가 전부 거부된다. `M = sc` 같은 별칭도
    고정점으로 잡는다 (`_namespace_targets()`).
  - **M12** — module scope 의 `assert`·`raise` 가 실행 슬라이스에 들어온다
    (`_MODULE_NONBINDING` 의 뜻을 "이름을 안 묶는다" 에서 **"아무것도 실행하지
    않는다"** 로 바꿨다). class 의 base·keyword 를 데코레이터와 **같은 종류**로
    다룬다 — class 문은 metaclass 를 호출해 class 객체를 만들고 base 의
    `__init_subclass__` 를 부르므로 조회가 아니라 치환이다.
    `from __future__ import …` 는 실행 의미를 바꾸는 컴파일러 지시이므로 묶는다.

    **반대로 `if __name__ == "__main__":` 은 뺐다** — import 때 안 돈다는 것을
    언어가 보장하므로 이 라운드 규칙("증명할 수 있는 것만 뺀다")이 서는 유일한
    분기다. 안 빼면 `raise SystemExit(main())` 한 줄이 CLI 전체를 producer
    identity 로 끌고 온다 (실측: 닫힘 93 → 99, `main`·`argparse`·`_cohort_dir`·
    `seal_frozen_cohorts` 가 들어왔다 — 44차 경계를 그대로 넘는다).
    **남는 한계**: 투영을 실제로 만드는 것은 스크립트 실행이고 거기서는 그
    분기가 돈다. 계산 함수는 `_COMPUTE_NAMES` 로 선언돼 있고 `main` 은 그것을
    부르는 자리라는 근거로 경계를 유지했다. 요청문에 적는다.
  - **M17** — 판정을 **철자에서 결속으로**. 호출자가 값을 주는 자리(매개변수·
    `for`·`with as`·`except as`·내포)로 묶인 이름은 능력이 아니고, 속성은
    뿌리가 import 한 module 일 때만 능력이다. 평범한 대입(`GET = getattr`)은
    **여전히 거부**한다 — 58차 L9-b 가 닫은 축이고, 값을 모르는 대입까지 열면
    그 구멍으로 되돌아간다.

  **닫힘 측정** (분석기 변경만의 효과, 같은 소스 기준): 93 → 90. 좁아졌다.
  게시 경로 계열은 `_ledger_roster` 하나로 그대로다.

  ### ζ (M10) — 발급의 공개 표면

  raw 발급을 비공개로 내리고(`_claim_planned_leg`), **이름을 숨기는 것으로
  끝내지 않았다**: token 이 이 다리의 자리에 **이미 굳어 있는지** 확인한다.
  시험 22곳을 production 경로(`open_leg_run`)로 옮겼고, raw 발급을 일부러
  부르던 53·54차 회귀 2건은 비공개 이름으로 되돌리되 **전제를 맞춘 뒤**
  겨누는 층만 부수게 고쳤다 (새 검사가 먼저 걸리면 그 시험은 자기 축을 한 번도
  안 본다 — M16 과 같은 형태다).

  ### ε (M14·M15) — 증언의 범위

  - **M14** — 탐침이 `sys.modules` 를 **스크립트 첫 줄에서** 찍어 startup 에
    올라온 module 전부의 바이트를 잰다. 이름 세 개(`site`·`sitecustomize`·
    `usercustomize`) 목록으로는 겹수만큼 구멍이 남았다.
  - **M15** — `environment_tag()` 가 `startup` 하나가 아니라 **영수증 전체**를
    해시한다. 그러려면 자식도 같은 범위를 재야 하므로, 영수증 계산 전체를
    탐침 본문(`_receipt_facts()`)으로 옮기고 부모와 심어 놓은 증언 node 가
    **같은 문자열**을 쓴다. node 는 in-process 로 재지 않고 **탐침을 띄운다** —
    pytest 가 이미 온갖 것을 올린 프로세스에서는 startup 집합을 잴 수 없다.

  ### 변이 축이 또 죽었다 — 이번 라운드 누적 **10건**

  δ 에서 3건(`closure-refuses-dynamic-resolution` ·
  `decorators-are-import-time-effects-g58` · `producer-normalizes-the-node`),
  ε 에서 3건(`execution-receipt-binds-the-startup-g58` ·
  `evidence-binds-the-environment` 두 자리). 전부 `--check-preimages` 가 먼저
  잡았고, 새 원상으로 고쳐 **다시 무는 것을 확인**했다.

  이것이 이 라운드에서 가장 자주 값을 한 규칙이다: **증거가 낡았다는 것은
  사람이 알아채는 것이 아니라 기계가 거부해야 하는 것이다.**

  ### webapp

  `/trust` 를 59차로 갱신했다 — §3 에 재정정("목록은 버릴 수 있지만 권한은
  버릴 수 없다"), §4 에 죽은 변이 축 10건 이야기, §6 에 현재 판정과 남은 마감.
  세 페이지 렌더링을 확인했다 (`/` `/trust` `/gate` 전부 200).
