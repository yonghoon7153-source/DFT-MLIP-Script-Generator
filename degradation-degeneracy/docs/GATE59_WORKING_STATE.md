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
| M1 | P0 | 완료 시 class 기록이 production 에 배선 안 됨 (`record_run_outputs` 실호출 0) | `preserve.py:6754` · `grid.py:407` · `fitting.py:888` | 대기 |
| M2 | P0 | content id 가 production start manifest 를 누락 | `preserve.py:4238` | 대기 |
| M3 | P0 | final `O_EXCL` 파일이 부분 바이트로 공개되고 성공 | `preserve.py:4417-4441` | 대기 |
| M4 | P0 | shared/local class 충돌을 reader 가 canonical 로 숨김 | `preserve.py:4458-4473` | 대기 |
| M5 | P0 | smoke 검사 직후 bind swap → 실제 쓰기가 밖으로 (TOCTOU) | `is_inside_namespace()` 소비자 전부 | 대기 |
| M6 | P0 | clean clone 에서 marker+ledger 만으로 frozen 못 지킴 | `row_projection.py:4388-4474` | 대기 |
| M7 | P0 | `fit → grid` 역순이면 consumed 결속 없이 executed | `preserve.py:5033-5114` · `6532-6546` | 대기 |
| M8 | P0 | bundle member symlink/bind 로 repo 밖 바이트 | `preserve.py:6185-6211` · `_verify_declared_bundle` | 대기 |
| M9 | P0 | 검증한 evidence 와 봉인한 evidence 가 다르다 (caller dict TOCTOU) | `preserve.py:6427-6624` | 대기 |
| M10 | P0 | 공개 `claim_planned_leg(token=…)` 가 disk token 없는 running 생성 | `preserve.py:5466-5556` | 대기 |
| M11 | P0 | capability 의 module target 을 식으로 감싸면 closure 밖 | `row_projection.py:1290-1305` · `1454-1461` | 대기 |
| M12 | P0 | import-time 실행 모델이 `assert`·metaclass·future flag 를 버림 | `row_projection.py:627` · `_has_import_time_compute` | 대기 |
| M13 | P1 | class durability 재시도가 실패한 parent fsync 를 안 고침 | `preserve.py` 등록부 | 대기 |
| M14 | P1 | startup probe 가 `sitecustomize` 의 transitive import 를 안 묶음 | `mutation_replay.py` `_ENV_PROBE_BODY` | 대기 |
| M15 | P1 | `environment_tag()` 가 full receipt 아니라 `startup` 만 증언 | `mutation_replay.py:3588-3603` | 대기 |
| M16 | P1 | 내 회귀 하나가 이 환경에서 자기 축을 실행 안 함 (`254:0` 하드코딩) | `test_frozen_coordinate_seal_58.py:192` | **GREEN** |
| M17 | P2 | 능력 escape 규칙이 무해한 local shadow 도 거부 (Q1 의 답: 그렇다) | `_assert_no_dynamic_resolution` | 대기 |

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

## 진행 로그

- 2026-09-08 — 판정 접수. P0-1·P0-2 를 grep 으로 즉시 확인(둘 다 사실).
  M16 을 먼저 닫았다: 좌표를 현재 mount table 에서 유도하고 후보가 하나 이상임을
  **먼저 단언**한다. 전제가 깨지면 그 사실이 보이게.
