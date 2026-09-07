# GATE58 작업 상태 — 58차 판정 대응 (진행 중)

이 문서가 **진행 중 상태의 정본**이다. 세션이 끊기면 여기부터 읽는다.
발견의 서사와 판정 이력은 `docs/08_REVIEW_RESPONSE.md` §66.

- **직전 판정**: 58차 **NO-GO** (대상 `cf10f345` · `source_digest 2f1e10779368987f`)
- **범위**: 묶음 9 lifecycle 게이트만. 6 mAh STEP3/STEP4 과학 게이트(`06a9aed9`,
  `scripts/mpm*`·`step3_sigma.py`·`step4_dyn.py`)는 **다른 브랜치 소유** — 손대지 않는다.
- **작업 브랜치**: 루트 `CLAUDE.md` 하드룰 1 이 지정한 것.

## 절차 (라운드 내내 지킨다)

1. 발견마다 **RED 테스트 먼저**. 실패를 눈으로 본 뒤 고친다 (`/finding`).
2. 새 테스트가 **처음부터 통과하면** fixture 가 진실을 가린 신호다 — 이 저장소에서
   5회 이상 실측된 패턴. 이번 라운드의 L1 이 정확히 그 사례다.
3. **테스트는 top-level consumer 를 불러야 한다.** L13 이 지적한 실패형 —
   helper 를 직접 부르면 이름이 약속한 성질을 단언이 안 건드린다.
4. 변이 증거 재생성 중에는 **저장소를 얼린다** (§65).
5. RUN_SCOPE(`src/ tools/ configs/ scripts/ run.sh requirements*.txt`)를 고치면
   `source_digest` 가 움직인다. 이번 라운드는 거의 전부 RUN_SCOPE 다 — 끝난 뒤
   `paired_fixed5_v4` 검증 영수증과 원장 identity 를 다시 만들어야 한다.

## 발견 원장 (13건)

상태: `대기` → `RED` (재현 테스트가 빨감) → `GREEN` (고침) → `변이` (등록부 anchor 심음)

| ID | 등급 | 한 줄 | 자리 | 상태 |
|---|---|---|---|---|
| L1 | P0 | production smoke 가 class 를 기록 안 함 + 이동 후 legacy migration 이 canonical 발급 | `src/grid.py:403` · `src/fitting.py:884` · `preserve.py:3747` | **GREEN** |
| L2 | P0 | `run_content_id()` first-present 충돌 + conflict 삼킴 | `preserve.py:3946` · `3763` | **GREEN** |
| L3 | P0 | class 등록부가 CAS 아님 (last-writer-wins) | `preserve.py:3979-3993` | **GREEN** |
| L4 | P0 | bind mount 외부 디렉터리가 smoke 면제 | `preserve.py:3853-3900` | 대기 |
| L5 | P0 | 가려진 frozen ancestor 가 writable + `_names_for()` 가 `SystemExit` 삼킴 | `row_projection.py:4327-4353` · `4388-4397` | 대기 |
| L6 | P0 | 소비된 phase receipt 를 늦은 writer 가 덮어씀 | `preserve.py:4606-4610` · `5934` | 대기 |
| L7 | P0 | clone 밖 absolute bundle 이 `full_bundle` | `preserve.py:5661` · `5670` | 대기 |
| L8 | P0 | directory fsync 실패를 삼키고 issuance 성공 | `preserve.py:5029` · `5226` | **GREEN** |
| L9 | P0 | producer closure — AnnAssign RHS · name-only decorator · 함수 지역 alias | `row_projection.py:681-722` · `772-808` · `1016-1067` | 대기 |
| L10 | P1 | normal finalize 가 `verifier_origin` 위조 가능 | `preserve.py:5681` · `5993` | 대기 |
| L11 | P1 | 강제 환경이 transitive code bytes 를 안 묶음 (`sitecustomize.py`) | `mutation_replay.py:3135-3214` | 대기 |
| L12 | P1 | report 안 건드리고 execution evidence 세탁 → 170/170 통과 | `mutation_replay.py:3432-3498` | 대기 |
| L13 | P1 | 회귀 2건이 배선을 안 부름 + 등록부에 신규 방어 anchor 없음 | `tests/test_docs_lint.py:11799-11908` · `mutation_replay.py` MUTANTS | 대기 |

## 묶음 (같이 고쳐야 값이 나오는 것)

- **묶음 α — 실행 class 를 진짜 authority 로**: L1 · L2 · L3.
  배선(L1) 없이 키(L2)만 고치면 여전히 아무것도 안 굳는다. 셋을 한 벌로.
- **묶음 β — 경계 판정을 kernel 좌표 하나로**: L4 · L5.
  smoke containment 와 frozen guard 가 **같은 함수**를 써야 한다. 지금은 lexical /
  kernel 두 판정이 갈려 있고, 갈리면 어느 쪽이 경계인지 정할 수 없다.
- **묶음 γ — 영수증 불변성**: L6 · L7 · L10.
  전부 "caller 가 준 것을 lifecycle 이 그대로 믿는다" 축.
- **묶음 δ — durability**: L8 (단독, 작다).
- **묶음 ε — producer closure**: L9 (단독, 깊다).
- **묶음 ζ — 증거층**: L11 · L12 · L13. **마지막에 한다** — 앞의 수정이 끝나야
  등록부에 심을 anchor 가 정해진다.

## 순서 (정한 것)

1. **α** (L1·L2·L3) — 58차 판정의 머리. §64 가 거짓이 된 지점이라 여기부터.
2. **δ** (L8) — 작고 독립적. α 도는 동안 끼워 넣기 좋다.
3. **γ** (L6·L7·L10)
4. **β** (L4·L5) — bind mount 재현이 필요해 환경 확인이 먼저.
5. **ε** (L9)
6. **ζ** (L11·L12·L13) + 변이 등록부에 새 축 심고 12조각 재생성

## 하지 말 것 (56차가 거절한 수정 방식)

- 진입점마다 호출을 추가하는 방식으로 L1 을 닫지 않는다 → 새 진입점이 또 빠진다.
- manifest 후보 목록을 늘리는 방식으로 L2 를 닫지 않는다 → 투영이 여전히 손실적.
- `is_inside_namespace()` 에 금지 패턴을 추가하는 방식으로 L4 를 닫지 않는다.
- `_names_for()` 가 후보를 더 찾게 하는 방식으로 L5 를 닫지 않는다.

**공통 원리**: 검사를 정교하게 만드는 대신 **물음 자체를 바꾼다.**

## 진행 로그

- 2026-09-07 — 판정 접수. 6건(L1·L2·L3·L6·L7·L8)을 정적으로 직접 확인, 전부 사실.
  원장 §66 기록. 이 문서 생성.

- 2026-09-07 (이어서) — **묶음 α(L1·L2·L3) + δ(L8) 닫음.**

  | 발견 | 고친 방식 | 시험 |
  |---|---|---|
  | L1 | 진입점마다 호출 추가 **안 함**. 면제를 말하는 함수 `note_smoke_exemption()` 하나를 두고 두 gate 가 같은 문장을 쓰게 함. 주석만 있고 없던 `record_run_outputs()` 를 실제로 만듦 | `test_execution_class_wiring_58.py` 2건 |
  | L2 | 후보 목록을 늘리지 **않음**. 적용되는 모든 manifest 를 이름과 함께 닫힌 descriptor(`run-content-id/v2`)로 해시. gate 의 `except PreserveError: pass` 를 "manifest 아직 없음" 으로만 좁힘 (`_MISSING_MANIFEST_MARK` 상수로 결속) | 같은 파일 2건 |
  | L3 | read→check→`os.replace` 를 `O_CREAT\|O_EXCL` 로. 진 writer 는 읽어서 같은 class 면 멱등 성공, 다르면 거부 | 같은 파일 1건 |
  | L8 | 발급 두 자리를 `_fsync_dir_strict()` 로 (`claim-publish` · `attempt-token-publish`) | `test_issuance_durability_58.py` 1건 |

  **fixture 감사**: 변이 2건(L1 배선 제거 · L2 를 first-present 로 되돌림)을 심어
  각각 해당 시험이 빨개지는 것을 확인했다. 시험이 배선에 결속돼 있다.

  **등록부 re-key**: content id 가 v1→v2 로 바뀌어 기존 4건의 키가 안 맞는다.
  **경로를 다시 보고 정하지 않았다** — 그건 L1 의 두 번째 절반을 되풀이하는 것이다.
  v1 레코드의 class 와 근거를 승계하는 re-key 로 처리했고 `evidence` 에 v1 키를
  적었다. 등록부는 tracked 4(v1) + new 4(v2) = 8건.

  ### 이 라운드에 저지른 절차 실수 셋 (기록해 둔다)

  1. **회귀가 도는 도중에 `tools/preserve.py` 를 고쳤다** (L8). §65 에서 배운 것과
     같은 실수다 — 그 실행 결과는 못 쓴다. 죽이고 다시 돌렸다.
     **규칙을 넓힌다**: 변이 증거뿐 아니라 **전체 회귀 중에도 RUN_SCOPE 를 얼린다.**
  2. **시험이 틀린 이유로 빨갰다.** L8 의 계획 fixture 를 손으로 만들다 필드
     하나(`authorization_kind`)를 빠뜨려 durability 에 닿기 전에 죽었다.
     이미 있는 `_lifecycle_ledger()` 를 재사용해 고쳤다. RED 를 봤다고 다 같은
     RED 가 아니다 — **실패 사유를 읽어야 한다.**
  3. 죽인 pytest 가 conftest teardown 을 못 돌려 등록부에 fixture 68건이 남았다.
     수동으로 걷어냈다. guard 는 정상 종료에만 작동한다는 뜻이다.

- 2026-09-07 (α·δ 커밋 `334f4c20` 뒤) — **내 수정이 새 결함을 만들었다: L14 (자체 발견).**

  strict smoke 는 통과했다 (`rc 0` · `✅ pipeline smoke 통과`). 그런데 **등록부에
  항목이 하나 늘었다.** L1 배선이 실제로 도는 증거이지만 동시에 문제다.

  `[재현]` smoke 를 연속 두 번 돌렸다:

  | 회차 | 등록부 | 새 content id |
  |---|---:|---|
  | 1 | 8 → 9 | `8cd4a2ec…` (class `smoke`, 근거 `results/_smoke/curves`) |
  | 2 | 9 → 10 | `f6176b28…` |

  **멱등이 아니다.** 나는 "smoke 산출이 결정적이면 같은 content id 라 두 번째는
  멱등 성공한다" 고 가정했는데 **틀렸다** — 실측으로 뒤집혔다. smoke manifest 에
  실행마다 달라지는 것이 들어 있다.

  그래서 두 가지가 깨진다:
  1. **등록부가 smoke 실행마다 무한히 자란다.**
  2. **smoke 를 돌리면 트리가 더러워진다.** 그런데 이 저장소의 규율은
     "smoke 는 clean 커밋에서 돈다" 다. 고치기 전에는 smoke 가 아무것도 안
     적었으므로(그게 L1 이었다) 이 충돌이 없었다. **내 수정이 만든 것이다.**

  ### 결정적 사실 — smoke 는 자기 산출을 지운다

  smoke 종료 뒤 `results/_smoke/curves` 는 없다. 그러면 **등록된 내용이 어디에도
  없는데 레코드만 남는다.** 죽은 무게다.

  `[해석]` 그러므로 smoke 면제 레코드는 **커밋 대상이 아니다.** 정본 authority
  (canonical·legacy 분류)는 감사 대상이고 수가 적고 오래 산다. smoke 면제는
  ephemeral 산출에 대응하는 **국소 운용 상태**다.

  **지우는 것이 안전한 이유**: 등록이 없으면 승격이 **거부**된다 (fail-closed).
  레코드를 지우면 시스템이 더 관대해지는 게 아니라 **더 엄격해진다.** 다른
  머신으로 바이트를 옮겨도 거기엔 레코드가 없으니 역시 거부다. 그래서
  "smoke 레코드를 공유하지 않는다" 로 잃는 방어가 없다.

  ### 다음에 할 것 (묶음 α')

  `_exec_class/` 를 둘로 가른다 — tracked (canonical·legacy) / gitignored
  (smoke). 읽기는 양쪽을 보고, 쓰기는 class 로 자리를 정한다. 회귀는
  "smoke 를 두 번 돌려도 tracked 쪽이 안 늘어난다" 를 단언한다.

  지금은 stray 2건을 지워 트리를 clean 으로 되돌렸다 (위 근거로 안전).

  **이번에도 가정을 실측이 뒤집었다.** 이 라운드에서 두 번째다 (첫 번째는
  "e2e 실패는 커널 탓" — 아니었다). 가정은 적되 **재기 전에는 주장하지 않는다.**
