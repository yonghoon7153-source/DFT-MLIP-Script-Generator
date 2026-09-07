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
| L4 | P0 | bind mount 외부 디렉터리가 smoke 면제 | `preserve.py:3853-3900` | **GREEN** |
| L5 | P0 | 가려진 frozen ancestor 가 writable + `_names_for()` 가 `SystemExit` 삼킴 | `row_projection.py:4327-4353` · `4388-4397` | **GREEN** (`bbba9aa3`) |
| L6 | P0 | 소비된 phase receipt 를 늦은 writer 가 덮어씀 | `preserve.py:4606-4610` · `5934` | **GREEN** |
| L7 | P0 | clone 밖 absolute bundle 이 `full_bundle` | `preserve.py:5661` · `5670` | **GREEN** |
| L8 | P0 | directory fsync 실패를 삼키고 issuance 성공 | `preserve.py:5029` · `5226` | **GREEN** |
| L14 | P0 | (자체 발견) smoke 레코드가 공유 등록부에 쌓여 트리가 더러워진다 | `preserve.py` 등록부 root | **GREEN** |
| L9 | P0 | producer closure — AnnAssign RHS · name-only decorator · 함수 지역 alias | `row_projection.py:681-722` · `772-808` · `1016-1067` | 대기 |
| L10 | P1 | normal finalize 가 `verifier_origin` 위조 가능 | `preserve.py:5681` · `5993` | **GREEN** |
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

- 2026-09-07 (이어서) — **묶음 α' (L14) 닫음. 그리고 내 시험의 결함 하나를 더 찾았다.**

  `_exec_class/` 를 갈랐다 — tracked(canonical·legacy) / gitignored(`local/`, smoke).
  읽기는 `read_execution_class()` 가 양쪽을 보고, 쓰기는 class 가 자리를 정한다.

  **자리를 가르자 L3 의 보장이 깨졌다.** 두 class 가 서로 다른 파일에 쓰므로
  `O_EXCL` 이 충돌하지 않는다. 반대쪽을 읽는 교차 검사를 붙였지만 그것은
  read-then-write 라 경쟁에 무력하다 — **57차가 정확히 이 형태로 틀렸던 것을
  내가 반복했다.** 배타 지점을 **class 와 무관한 내용별 lock**(`<cid>.classlock`,
  국소 자리)으로 되돌리고 그 안에서 양쪽을 읽고 쓴다.

  ### ★ 변이 감사가 내 시험의 결함을 잡았다 (이 라운드에서 가장 값진 것)

  | 변이 | 1차 | 조치 |
  |---|---|---|
  | C: smoke 를 공유 등록부로 되돌림 | 잡힘 | — |
  | D: 내용별 lock 제거 | **살아남음** | 시험을 고침 |

  D 가 살아남았을 때 **변이가 실제로 적용됐는지부터 확인했다** — 안 그러면
  "살아남았다" 는 판정 자체가 거짓일 수 있다. 적용은 됐고, 원인은 **barrier 가
  임계 구역 바깥**(`_exec_class_path()`)에 있던 것이었다. 자리를 가르기 전에는
  read→replace 창이 넓어 우연히 잡혔지만, 지금은 순전히 타이밍 의존 —
  **시험이 우연에 기대고 있었다.**

  barrier 를 `_read_exec_class_at()` 로 옮겨 **"둘 다 읽었지만 아직 아무도 안
  썼다"** 상태를 강제했다. 그것이 lock 이 막아야 하는 바로 그 상태다. 변이 D 를
  다시 심으니 잡힌다.

  > **규칙**: 배타·순서를 묻는 시험의 barrier 는 **임계 구역 안**에 잡는다.
  > 바깥에 잡으면 통과가 구현이 아니라 스케줄러를 증명한다.
  > 남은 L6(phase receipt 덮어쓰기)에 그대로 적용된다.

  이 시험의 barrier 는 **세 번 옮겼고** 그 이력을 파일 주석에 남겼다.

  ### 실측

  | 무엇 | 값 |
  |---|---|
  | 전체 회귀 | 1447 passed · 1 failed (영수증 낡음) · 1 xfailed (697.24s) |
  | 영수증 재생성 뒤 | docs lint 전체 + P0-8 계열 **374 passed** (268.77s) |
  | 공유 등록부 | **8건 그대로** — 시험 96건은 전부 국소로 갔다 |
  | 등록부 오염 | **0건** (`git status` 에 `_exec_class` 없음) |
  | `source_digest` | `758e3c2fce0ed344` → `65b3a61be4f01eed` |
  | 영수증 | core_sha `0be402e932ed682b` · 원장 갱신 |

  `[해석]` **자리 분리가 설계대로 작동한다는 증거가 이 표의 셋째·넷째 줄이다** —
  시험이 96건을 만들었는데 공유 등록부는 8건 그대로이고 트리는 깨끗하다.

- 2026-09-07 (이어서) — **묶음 γ (L6·L7·L10) 코드 완료. 그리고 내 수정이 기존
  회귀 하나를 vacuous 하게 만들었다 — 실측으로 잡았다.**

  | 발견 | 고친 방식 |
  |---|---|
  | L6 | `phase_done()` 에 불변성 술어 (같은 값은 멱등, 다른 값은 거부). 그리고 소비자가 **자기가 본 생산자의 정규형 해시**를 남기고 `finalize_leg()` 가 봉인 직전 재대조 |
  | L7 | `root / uri` 의 absolute 흡수. absolute 만 막지 않고 **담김을 결과로 확인** (`..` 경로까지) |
  | L10 | `verifier_origin` 하나가 아니라 **lifecycle 소유 키 5개 전부** 거절 + 정상 finalize 도 자기 origin 을 남긴다 |

  변이 E(불변성 제거)·F(finalize 재대조 제거) 각각 해당 시험만 잡았다.

  ### ★ 미결 — 54차 P0-2 가 증명자를 잃었다

  전체 회귀에서 `test_the_finalize_recovery_branch_holds_the_claim_lock` 이
  `RuntimeError: cannot join thread before it is started` 로 깨졌다. 그 시험은
  **닫힌 grid 를 다른 receipt 로 다시 닫는 것**을 seam 으로 써서
  `_atomic_write_json` 직전에 복구 스레드를 끼워 넣는데, L6 이 그 쓰기에
  도달하기 전에 거부하므로 스레드가 시작조차 안 된다.

  seam 을 `_canon_json`(불변성 비교에서만 불린다)으로 옮겨 통과시켰다. 그런데
  **변이 G 로 재 보니 살아남았다** — finalize 복구 분기의 `_lifecycle_locks` 를
  통째로 제거해도 통과한다 (2.83s → 0.43s, 복구가 안 기다렸다는 뜻).

  `[해석]` L6 이 부활 경로를 **구조적으로** 없앴으므로 그 시험은 lock 유무를
  구별할 수 없다. 더 강한 보장이지만 **대가로 54차 P0-2 의 증명자가 사라졌다.**
  지금은 그 시험이 실제로 지키는 명제(늦은 writer 가 거부된다)를 명시 단언으로
  못 박아 두었다.

  > **미결**: "복구 분기가 claim lock 을 쥔다" 를 증명할 **새 증명자**가 필요하다.
  > `phase_done` 은 더 이상 그 일을 못 한다 (구조적으로 못 쓰므로). 후보는 동시
  > `finalize_leg` 둘, 또는 `resume_claim`/`release` 와의 경쟁이다. ζ 에서 변이
  > 등록부에 새 축을 심을 때 같이 만든다.

  `[교훈]` **방어를 강화하면 그 방어를 증명하던 시험이 vacuous 해질 수 있다.**
  이 저장소가 아는 "fixture 가 진실을 가린다" 의 변종인데, 가리는 것이 fixture 가
  아니라 **더 강해진 제품**이다. 강화할 때마다 기존 anchor 가 여전히 무는지를
  변이로 다시 물어야 한다.

- 2026-09-07 (이어서) — **묶음 β 닫음 (L4·L5).** 둘 다 **실물 `mount --bind`** 로
  먼저 재현했다.

  ### L4 — smoke 경계

  | 관측 | 고치기 전 |
  |---|---|
  | `is_inside_namespace` | true (smoke 안이라고 판정) |
  | 계획 gate | **통과(면제)** |
  | 쓴 것이 namespace 밖에? | **true** |

  커널 좌표 helper 넷을 `row_projection.py`(RUN_SCOPE 밖) → `tools/preserve.py`
  (안)로 옮기고 `is_inside_namespace()` 가 그 좌표로 담김을 묻게 했다.
  **왜 안으로 옮기나**: (a) 한 경계, 한 함수 — smoke containment 와 frozen guard 가
  갈려 있었고 L4 가 그 틈이었다. (b) 봉인 범위 — `row_projection.py` 는 RUN_SCOPE
  밖이라 거기 있던 경계 판정을 `source_digest` 가 안 덮었다.
  **되돌릴 수 있다. 다만 그때도 한 자리여야 한다.** 요청문에 적는다.

  **고치는 도중 진짜 원인이 하나 더 나왔다.** 좌표 검사를 붙였는데도 통과했다 —
  loop 의 `except FileNotFoundError: return True` 가 그 검사에 **닿기 전에**
  돌아가고 있었다. bind alias 아래의 새 디렉터리가 정확히 그 모양이다.

  ### L5 — 가려진 frozen ancestor

  | 관측 | 고치기 전 |
  |---|---|
  | 가린 이름 수 | 1 |
  | guard | **PASSED** |
  | 덮개 걷은 뒤 frozen child 안에? | **true** |

  **`_names_for()` 의 예외 삼킴을 고쳐도 이 반례는 안 막힌다** — 이름을 덮으면
  예외가 나는 게 아니라 후보가 진짜로 없어진다. 그 수정은 따로 했지만
  충분하지 않다.

  물음을 바꿨다. `_write_frozen_marker()` 가 얼리는 **그 순간의 좌표**를 원장 옆
  `_frozen_coords/` 에 봉인하고, guard 는 **이름을 한 번도 안 보고** 좌표만
  비교한다. L4 에서 helper 를 옮긴 것이 여기서 값을 했다 — 두 guard 가 같은
  좌표 함수를 쓴다.

  ### ★ 또 내 시험이 거짓을 단언했다 (이 라운드 네 번째)

  처음에 "이름을 바꿔도 봉인이 따라온다" 를 단언했다. **틀렸다.** 실측:

      rename 전  ('254:0', .../gA)
      rename 후  ('254:0', .../gA-renamed)

  `_fs_identity()` 의 둘째 항은 filesystem **안의 경로**이고 경로는 곧 이름이다.
  이 좌표가 불변인 것은 **같은 대상을 어떤 창으로 보는가** 에 대해서이지
  **대상을 옮기는 것**에 대해서가 아니다.

  그래서 그 시험을 **한계를 고정하는 시험**으로 바꿨다
  (`test_the_seal_is_not_invariant_under_rename__a_recorded_limit`). frozen
  디렉터리를 `mv` 하면 좌표 봉인이 자손을 더는 안 덮는다는 사실을 명시로
  못 박아, 나중에 누가 "rename 도 막는다" 고 믿지 않게 했다.

  > **남은 한계 (요청문에 적는다)**: 제대로 닫으려면 좌표가 아니라 **파일
  > handle 급 identity**(재부팅에도 사는 fsid + inode 계보)가 필요하다.
  > 이 라운드 범위 밖이다.

  변이 감사: J(guard 의 봉인 조회 제거) · K(freeze 시점 봉인 안 함) 둘 다 잡힘.
  L4 쪽은 H(좌표 검사 제거) · I(경로 담김 제거) 둘 다 잡힘.

  ### 이 라운드에서 내 시험이 문제였던 것 — 네 번

  1. α' barrier 가 임계 구역 바깥 → 스케줄러를 증명
  2. γ  내 수정이 54차 회귀를 vacuous 하게 만듦
  3. β  격리된 척했지만 저장소에 씀 (`SMOKE_NAMESPACE` 절대경로 흡수)
  4. β  참이 아닌 성질을 단언 (rename 불변성)

  `[해석]` 네 번 다 **변이 감사나 재현 시도**가 잡았다. 초록만 보고 넘어갔으면
  넷 다 놓쳤다.

## ★ 라운드 마감 작업 (미룬 것 — 잊으면 안 된다)

L5 뒤 전체 회귀가 **1465 passed · 3 failed** 였다. 셋 다 **산출물 identity 가
낡은 것**이고 논리 실패가 아니다:

| 실패 | 원인 |
|---|---|
| `test_full_bundle_claims_are_backed_by_a_real_bundle` | `source_digest` 이동 → 검증 영수증 낡음 |
| `test_projection_analyzer_digests_recompute_from_the_current_tree` | `row_projection.py` 수정 → `compute_sha256`·`row_projection_py_sha256` 이동 |
| `test_exactly_one_cohort_is_active_and_it_tracks_the_current_tree` | 같은 이유 — 활성 cohort **g12 가 현행 트리를 안 따라간다** |

57차의 g11→g12 와 같은 **cohort 세대 전환**(g12 freeze → g13 생성 → 투영
재생성 → 영수증 갱신)이 필요하다.

### 왜 지금 안 하는가

**남은 ε(L9)이 같은 파일을 또 고친다.** 리뷰어가 지목한 자리가
`row_projection.py` 의 `_import_time_heads`(681) · `_namespace_capabilities`(1016)
이다. 지금 전환하면 ε 뒤에 **또** 해야 하고, 그건 §65 가 가르친 것과 같은
낭비다 — 트리가 계속 움직이는 동안 증거를 만들지 않는다.

### 마감 순서 (한 번에, 저장소를 얼린 채)

1. ε(L9) · ζ(L11·L12·L13) 코드 수정 완료
2. **저장소 동결** (RUN_SCOPE·`docs/22p_gap/` 커밋 금지)
3. g12 freeze → g13 생성 → 투영 재생성
4. `paired_fixed5_v4` 검증 영수증 재생성 + 원장 identity 갱신
5. 변이 등록부에 새 축 심기 (P0-8 · `_import_time_heads` ·
   `_namespace_capabilities` · receipt 배선 · `_run` 환경 ·
   **54차 lock 명제의 새 증명자**)
6. 12조각 전수 재생성 — **한 HEAD 에서** (§65)
7. 전체 회귀 + strict smoke (clean 커밋에서)
8. 요청문 갱신 → 게이트 재요청

**그때까지 이 셋은 빨간 채로 둔다.** 숨기지 않고 여기 적어 둔 이유다 —
"초록이어야 커밋한다" 를 지키려고 지금 세대 전환을 하면 두 번 하게 된다.

- 2026-09-07 (β 마감 직전) — **내 안전 수정이 너무 넓어서 회귀가 잡았다.**

  `_frozen_coords` 에 시험 fixture 19건이 쌓였고 그중 하나가 `fs: "/"` 였다.
  "그 봉인은 모든 경로를 frozen 으로 만든다" 고 보고 **뿌리 봉인을 무조건
  거부**하게 고쳤다. 전체 회귀가 그것을 잡았다:

      FAILED test_a_bind_from_a_separate_filesystem_is_resolved_by_the_mount_graph
      PreserveError: filesystem 뿌리는 얼린 좌표로 봉인할 수 없다 (… → 0:39:/)

  `[해석]` **내 판단이 틀렸다.** `(dev, /)` 는 "모든 경로" 가 아니라 **그 장치의
  경로** 다. 별도 파일시스템을 bind 한 정당한 경우에는 그 fs 의 mount root 가
  `/` 이고, 그 봉인은 정확히 그 장치만 덮는 **좁은** 봉인이다.

  진짜 위험은 "뿌리" 가 아니라 **봉인이 authority 자신을 삼키는 것**이었다.
  원장이 사는 자리를 덮는 봉인이 들어오면 그 뒤로 원장에 아무것도 못 쓴다 —
  fail-closed 가 자기 발을 문다. 거부를 거기로 좁혔다.

  > **교훈**: fail-closed 를 늘리는 방향은 대체로 안전하지만 **근거 없이 넓은
  > 거부**는 안전이 아니라 고장이다. 무엇이 위험한지를 정확히 짚어야 한다.
  > 그리고 이번에도 그것을 잡은 것은 내 추론이 아니라 **전체 회귀**였다.

  이 라운드에서 내 수정이 만든 결함은 이제 넷이다 (L14 · L3 재파손 ·
  `_frozen_coords` 오염 · 과잉 거부). 전부 자체 발견이고 전부 **실행이** 잡았다.
