# R6 라운드 원장 — **내부 자체 리뷰** (Codex 토큰 소진) · 대상 `1049894` · 2026-09-11

> **다음 세션은 이 파일부터 읽는다.** 6차는 외부(Codex) 대신 `/self-review` 로 돌렸다: 네 렌즈 subagent 가
> 1049894 에서 발견을 내고(`reviews/r6_repros/<렌즈>/REPORT.md` + `repro_*.py`), 발견마다 격리 worktree 의
> 적대적 검증 subagent 가 반박을 시도해 재현된 것만 CONFIRMED (`reviews/r6_repros/<렌즈>/VERDICT.md`).
> 렌즈 재현 스크립트 넷은 본인이 1049894 트리에서 다시 돌려 전부 재현을 확인했다 (validator 9/9 · toctou 10/10 ·
> derived 8 FINDING · sig_port 11/11). 닫은 뒤 트리에서는 그 스크립트의 '재현' assertion 이 실패해야 한다.

판정: **CONFIRMED 30 · 부분 5 · 제외 2** (37 건). 전부 RED → 수정 → GREEN 으로 닫았다 —
`tests/test_r6_internal.py` (35 개; V 8 · D 10 · T 8 · P 7 · 매개변수 2). 네 커밋: `509a0cc`(V) · `eb95ac1`(D) ·
`601f8a9`(T) · `a121e2d`(P). 수정 뒤 `python -m pytest tests/ -q` → **122 passed**.

## 렌즈별 통합 발견 (심각도 = 검증자의 독립 판정)

### V · validator 우회 (`reviews/r6_repros/validator/`) — 9 → CONFIRMED 8 · 제외 1

공통 반례: MATLAB rmse 가 Python 과 상대차 1e-3~1e-2 (`MODEL_REL` 의 10⁶ 배) 인데 `%.2g` 로는 같은 문자열.

| ID | 무엇 | 심각도 | 상태 | 테스트 |
|---|---|---|---|---|
| V6-01 | 헤더가 데이터 행 **뒤**면 행별 검사(R4-04·R5-01)가 안 돌아 complete·0 | 결론이_바뀜 | 닫힘 (코드) — 헤더 앞의 데이터 행 = malformed | `test_i6v_01` |
| V6-02 | `--precision` 옵션이 토큰과 대조되지 않아 선언 없는/해석 불가 파일이 선언된 파일보다 관대 (sig:2 로 17 자리 토큰 → 0) | 결론이_바뀜 (옵션 시) | 닫힘 (코드) — 선언 없으면 옵션 형식으로 재출력 검사 | `test_i6v_02` ×3 |
| V6-03 | 헤더 없는 파일 = 존재한 적 없는 스키마(56a35a8 부터 헤더) 인데 partial → `--allow-partial` 로 0 | 결론이_바뀜 (플래그 시) | 닫힘 (코드) — 헤더 없음 = malformed | `test_i6v_03` |
| V6-04 | 스키마 누락에 하한 없음 — rmse 열 0·앵커 0 이어도 "전부 일치" 0 | 결론이_바뀜 (플래그 시) | 닫힘 (코드) — `OLD_SCHEMA_MIN_COLS` (rmse_pocv·rmse_dvdq) 없으면 invalid | `test_i6v_04` |
| V6-05 | `verify_unit` 이 meta 의 `artifact` 이름을 안 봐 다른 상태 이름으로 복사해도 '일치' | 숫자가_바뀜 (사후 rename) | 닫힘 (코드) | `test_i6v_05` |
| V6-06 | `# printed_format,17` 이 '선언 없음' 으로 흘러 invalid 가 아니었다 | 서술만_바뀜 | 닫힘 (코드) — 이름으로 역할 (R5-02 를 meta 리더에도) | `test_i6v_06` |
| V6-07 | 못 읽는 `--compare` 경로가 traceback rc 1 = "갈림" | 서술만_바뀜 | 닫힘 (코드) — OSError → invalid(2) | `test_i6v_07` |
| V6-08 | `run_id` 열 중복 시 DictReader 마지막 열만 | 사소 | 닫힘 (코드) | `test_i6v_08` |
| V6-09 | `%f` ±0 토큰이 부호 경계에서 거짓 거절 | 사소 | **제외** — rmse = sqrt(mean(r²)) 라 음수·-0 은 양쪽 다 생산 불가 (도달 불가, fail-closed) | — |

~~검증 못 한 전제~~ → **닫힘 (U15, 2026-09-11 사용자 기계 실측)**: R5-01 의 "Python format = MATLAB sprintf" 에서
우리가 못 재던 두 축이 둘 다 일치했다 — 반올림 타이 `sprintf('%.2f',0.125)` = `'0.12'` (half-to-even, Python 과 같다;
half-away 였다면 멀쩡한 `0.12` 산출을 audit 이 invalid 로 거절했을 것), 지수 자릿수 `sprintf('%.17g',1e-5)` =
`'1.0000000000000001e-05'` (2 자리 — Windows 식 `e-005` 가 아니고, 원래 double 로 되돌아온다). 기준선을
`tests/test_r6_internal.py::test_i6u_15_*` 에 `MATLAB_SPRINTF` 로 고정했다 (`token_format` 을 바꾸거나 지수 자릿수가
갈리면 걸린다). 남는 한계: 두 표본이고 MATLAB 판·플랫폼 하나다 — 다른 기계의 산출을 댈 때는 다시 재는 편이 맞다.

### D · 파생 보고서 · 공정성 (`reviews/r6_repros/derived/`) — 10 → CONFIRMED 8 · 부분 2

| ID | 무엇 | 심각도 | 상태 | 테스트 |
|---|---|---|---|---|
| DF-01 | §3-4 "두 독립 방법이 수렴" — 힌트 격자(pad=폭/2·21 점)의 grid[5]·grid[15] 가 제약 최적화 min·max 그 자체 → LLI '정확히 일치' 는 같은 격자점 | 서술만_바뀜(상) — 폭 1.0832·`is_lower_bound` 불변 | 닫힘 (문서) — §3-4·§7-3 "끝점 재확인, 독립 수렴 아님" | `test_i6d_01` (artifact 로 grid 재구성) |
| DF-02 | HANDOFF §5·INTRO §6-2 에 §0-2 철회 결론 7 곳 잔존 | 결론이_바뀜 (그 문서 독자) | 닫힘 (문서) | `test_i6d_02` |
| DF-03 | "raw 로 5~10 배" — 어느 통계량도 아님 (max/max 10.52 · min/min 9.66 · med 10.04 · 상태별 쌍 5.1~18.3) | 부분 → 서술만_바뀜 | 닫힘 (문서) — "max/max 10.5 배" 로 통일 | `test_i6d_03` |
| DF-04 | "86 passed 기대" 잔존 (Codex R5 §1 이 짚은 종류) | 숫자가_바뀜 | 닫힘 — 수집 수와 같아야 하는 테스트 | `test_i6d_04` |
| DF-05 | U13 을 "192 값의 조건" 에 묶음 — 192 값은 raw rmse 라 scale 을 소비하지 않는다 | 서술만_바뀜 | 닫힘 (문서) — 대상은 목적함수 build; R5-09 의 build 범위 문장은 유지 | `test_i6d_05` |
| DF-06 | §4-0 6·17·"전부 w=1" 은 상대 1e-9 문턱에서만 (부호만 10·22·0) | 서술만_바뀜 | 닫힘 (문서) | `test_i6d_06` |
| DF-07 | §1-10 에 탐색 하한 한정어 없음 | 서술만_바뀜 | 닫힘 (문서) | `test_i6d_07` |
| DF-08 | §4-1 2.11 → 원값 폭 2.1016 | 사소 | 닫힘 (문서) | `test_i6d_08` |
| DF-09 | §3-3 best 행 인용이 v1 (비트 일치는 v2) | 부분 → 사소 | 닫힘 (문서) | `test_i6d_09` |
| DF-10 | INTRO §6-3 "n=1 … 산수다" 는 §7-3 이 철회 | 사소 | 닫힘 (문서) | `test_i6d_10` |

공정성 검사에서 통과한 것: seed 는 U13 18 줄 전부 0 이고 eps_rel 최대 1.7e-15 vs 문턱 1e-9 (여유 5.8e5 배) 라 seed 는
verdict 에 무관; 1e-9 의 근거는 `model.py` 의 "MODEL_REL 과 같은 크기" 뿐 (문서는 seed-독립을 주장하지 않는다);
MATLAB(30 sqp) vs 우리(24 L-BFGS-B) 예산 차이는 §1-4 가 밝히고 §1-9 는 "관측 상한" 만 말한다.

### T · 순서/TOCTOU (`reviews/r6_repros/toctou/`) — 9 → CONFIRMED 8 · 부분 1

| ID | 무엇 | 심각도 | 상태 | 테스트 |
|---|---|---|---|---|
| F01 | degeneracy `.part` 가 고정 이름 + producer 의 stdout fd — 느린 시도가 게시된 inode 를 잠금 밖에서 덮음 (JSON=B, meta=A, 두 wrapper "통과"); R5-04 "마지막 온전한 묶음" 이 이 경로에서 거짓 | **결론이_바뀜** | 닫힘 (코드) — `cmd_degeneracy --out` + `atomic_write_json`(잠금 안 교체), shell 은 matrix 와 같은 형태 | `test_i6t_01` (실제 두 process) |
| F02 | `ne_shape._write_csv` 비원자·잠금·run_id·sha256 없음 → CSV=B·meta=A, 검출 불가 | 서술만_바뀜 | 닫힘 (코드) — 같은 게시 규약, 행 `run_id` | `test_i6t_02` |
| F03 | `fitted_pair_info` 파싱↔해시 두 번 읽기 | 사소 (창 sub-ms) | 닫힘 (코드) — bytes 한 번 | `test_i6t_03` |
| F04 | git 상태가 계산 뒤 한 번 샘플 | 서술만_바뀜 | 닫힘 (코드) — `git_*_at_start`·`started_utc`·`git_state_changed_during_run` | `test_i6t_04` |
| F05a | `--verify-unit` 이 이 시도의 id 를 안 받음 | 사소 | 닫힘 (코드) — `verify_unit(path, rid)` | `test_i6t_05a` |
| F05b | 실패 이유 `>/dev/null` | 사소 | 닫힘 (shell) — `verify_unit_or_say` | `test_i6t_05b` |
| F06 | `.lock`·`.part` 가 ignore 밖 | 사소 | 닫힘 (`.gitignore`) | `test_i6t_06` |
| F07 | reader 가 묶음을 안 봄 (Codex R5-04 reader 절 미구현) | 서술만_바뀜 | 닫힘 (코드) — `compare_states` 경고+제외, `fitted_pair_info` RuntimeError | `test_i6t_07` |
| F08 | run_id 는 공개 열 — 복사한 producer 는 모든 검사 통과 | 부분 → 사소 | **신뢰 경계** — 문서의 위협 모델(각자 uuid 의 "다른 시도") 밖; 소유 증명은 주장한 적 없음. 원할 때: producer 가 자기 bytes 의 sha256 을 stdout 에 내고 write_meta 가 그것과 대조 | — |

### P · sig-완전성 · 이식성 (`reviews/r6_repros/sig_port/`) — 11 → CONFIRMED 8 · 부분 3

| ID | 무엇 | 심각도 | 상태 | 테스트 |
|---|---|---|---|---|
| F1 | `root=` 라벨이 공백·같은 basename·`.` 에서 식별자가 아님 | 사소 | 닫힘 (코드) — URL 인코딩 + `inputs=<digest>` | `test_i6p_01` |
| F2 | `test_u13` 이 네 루트를 증거 못 함 (위조 사본 통과) | 부분 → 사소 | **한계로 기록** — §1-13 은 이미 "루트는 보고 순서" 라 적음; identity 붙은 다음 실측(U14)부터 루트 집합을 센다 | — |
| F3 | 라이브러리 버전 미기록 (scipy 1.11↔1.17: savgol ULP → 최적점 nit 25↔27, a_NE 1.5e-5) | 숫자가_바뀜 (끝자리) | 닫힘 (코드) — `env_signature` 를 meta·JSON·eval 헤더에 | `test_i6p_03` |
| F4 | 풀셀 워크북(이름순 첫 xlsx) identity 미기록 | 서술만_바뀜 (stderr 경고는 있음) | 닫힘 (코드) — `consumed_inputs`·`inputs_sha` 를 산출마다 | `test_i6p_04` |
| F5 | `--profile-scale`·`--samples/--grid` 가 산출에 없음 | 부분 → 사소 | 닫힘 (코드) — 행 `profile_scale`, JSON `n_grid`·`n_samples` ((c) starts 는 meta 에, (d) seed 는 `--seed 0` 과 쌍 — 반증) | `test_i6p_05` |
| F6 | `eol=lf` 비소급 — autocrlf 사본을 pull 로 올리면 안 바뀐 `run_all.sh` 가 CRLF | 서술만_바뀜 | 닫힘 (요청문 §0 "fresh clone"; `add --renormalize` 는 실측 무효) | — |
| F7 | `git_provenance` 가 cwd 기준 | 사소 | 닫힘 (코드) — 기본 base = 스크립트의 저장소 | `test_i6p_07` |
| F8 | `flock` 명령 부재 시 degeneracy 고아·오진 | 사소 | 닫힘 — F01 수정으로 shell 의 `flock` 사용이 사라짐 | (`test_i6t_01`) |
| F9 | 비-UTF-8 기본에서 check_artifact·CLI 크래시 | 부분 → 사소 | 닫힘 (코드) — `encoding="utf-8"`, stdout backslashreplace | `test_i6p_09` |
| F10 | ENOLCK 면 계산 행 소실 | 사소 | 닫힘 (코드) — `.part` 보존 + 경로를 예외에 | `test_i6p_10` |
| F11 | "86 passed"·`.lock` ignore | 사소 | 닫힘 — DF-04·F06 | — |

## 스키마 변경 (다음 실측 U14 에서 처음 채워진다)

- degeneracy: `--out` 로 게시 (stdout 은 로그); JSON 에 `n_grid`·`n_samples`·`env`·`consumed_inputs`·`ref_consumed_inputs`·`inputs_sha`.
- matrix 행 `inputs_sha`; profile 행 `profile_scale`·`inputs_sha`; ne_shape 행 `run_id`, meta `run_id`·`sha256`.
- meta: `env`, `git_commit_at_start`·`git_dirty_at_start`·`git_modified_code_at_start`·`git_state_changed_during_run`·`started_utc`.
- eval 헤더: `# env,…`·`# inputs,sha=… full_cell=<이름>:<sha12> …`; `# scale_audit,root=<URL 인코딩> … inputs=<digest>; …`.
- 기존 `out/` 은 전부 pre-R5 meta 라 새 검사의 대상이 아니다 (reader 는 옛 meta 를 전과 같이 읽는다).

## U14 실행이 드러낸 것 (2026-09-12, 사용자 기계 네 상태 재실행 — `STARTS=24`, 12 산출, 전부 통과)

재실행 자체는 깨끗했다 (배관 확인 3/3 · 본 실행 12/12 · 새 스키마 전부 갖춤). 그 과정이 두 건을 드러냈다.

| ID | 무엇 | 심각도 | 상태 | 테스트 |
|---|---|---|---|---|
| U14-01 | `atomic_write_csv` 가 `csv` 기본 lineterminator 라 **CRLF** 를 쓰는데 `.gitattributes` 가 csv 를 안 덮어 git 이 LF 로 정규화해 저장한다 → 디스크 bytes ≠ 커밋 bytes → **fresh clone 에서 meta 의 sha256 이 안 맞고**, R6 내부 F07 이 넣은 reader 검사가 그 상태를 §1-10 표에서 뺀다. 저장소를 새로 받은 리뷰어에게는 상태가 사라진 표가 간다 | **결론이_바뀜** (fresh clone 한정) | 닫힘 (코드) — writer 는 LF, `.gitattributes` 에 `*.csv`·`*.json text eol=lf`, `verify_unit` 이 "줄끝만 다르다" 를 짚는다. 이미 게시된 것은 `check_u14.py --renormalize` (파싱한 셀이 같을 때만 다시 서명, meta 에 기록) | `test_i6w_01`·`02`·`04` |
| U14-02 | `check_u14.py` 가 정본을 **파일 이름**으로만 골라 `degeneracy_300_0009_Li.json`(v1, 힌트 격자 이전)과 댔다 — 정본은 `_v2` 다. 또 정본에 없던 필드(스키마 추가분)를 `None → [값]` 으로 전부 diff 에 세었다. 둘이 겹쳐 "다른 숫자 618" 이 나왔는데 대부분 거짓 경보다 | 숫자가_바뀜 (도구) | 닫힘 (코드) — `baseline_for` 가 가장 높은 판을 고르고(`compare_states._keep_latest` 와 같은 규칙), 새 필드는 "정본에 없던 필드" 로 따로 센다 | `test_i6w_03` |

곁: `scale_audit_line` docstring 의 `\S` 가 SyntaxWarning 을 냈다 (raw string 으로).

**아직 판정 안 난 것**: U14 재실행의 숫자가 정본과 같은가. 위 두 거짓 경보를 걷어내야 답이 나온다 —
사용자가 `4de17ee` 를 push 하면 고친 `check_u14.py` 로 `git show` 기반 대조를 돌려 닫는다.

## 순서 (진행 기록)

1. ~~탐색 4 렌즈~~ → 2. ~~선별·본인 재현~~ → 3. ~~적대적 검증 4~~ → 4. ~~V·D·T·P 닫기~~ → 5. 원장·§0-2·요청문 (이 커밋) →
6. Codex 토큰 복귀 시 `R6_REQUEST.md` 송부 → 7. U14 (사용자 기계 `run_states.sh` 재실행으로 새 스키마 산출) → 8. 새 모델 요구서.

## 이력 정정 (2026-09-12)

`4762dcb` 의 커밋 메시지는 "옛 blob 둘(`out/matrix_300_0009.csv`·`out/profile_gamma_300_0009_Li.csv`)은 이 커밋에서
건드리지 않는다" 고 적었으나 **실제로는 그 둘의 CRLF→LF 변환이 같이 들어갔다** (그 전에 시험 삼아 돌린
`git add --renormalize .` 가 남긴 스테이징). 되돌리려 했으나 `.gitattributes` 의 `*.csv text eol=lf` 가 켜진 뒤로는
git 이 add 때마다 LF 로 정규화하므로 CRLF blob 으로 되돌릴 수 없다 — 그것이 그 규칙의 목적이다. 그래서 기록을
사실에 맞춘다: **그 두 파일은 `4762dcb` 에서 LF 로 정규화됐다.**

깨진 것은 없다 — 두 파일 모두 파싱한 셀이 완전히 같고(줄끝만 바뀌었다), 서명(`sha256`)이 없는 R5 이전 산출이라
다시 서명할 대상도 아니었다. 다만 **사용자 트리에서 U14 커밋을 rebase 할 때 이 두 파일이 충돌한다** (그쪽 patch 는
CRLF 판을 base 로 만들어졌다). 해결은 U14 판을 그대로 취하는 것이다 — 재실행 산출이 정본이다.

## U14-03 · U14-04 (2026-09-12, 사용자 기계 rebase 중 드러남)

| ID | 무엇 | 심각도 | 상태 | 테스트 |
|---|---|---|---|---|
| U14-03 | R6 내부 F02 가 `ne_shape` 행에 `run_id` 를 붙였는데 소비 helper `_ne_shape_csv` 는 모든 열을 `float()` 로 읽어 세 테스트가 `ValueError: could not convert string to float` 로 깨졌다. **이 트리에서 안 깨진 이유**가 요점이다 — 커밋된 `out/ne_shape_GITT_Li.csv` 가 아직 옛 스키마라 fixture 가 진실을 가렸다 (이 저장소에서 다섯 번째로 실측된 패턴) | 숫자가_바뀜 (테스트가 새 산출을 못 읽는다) | 닫힘 (코드) — `NE_SHAPE_TEXT_COLS` 에 `run_id`; helper 를 경로 인자로 열어 **새 스키마 파일**로 직접 건다 (커밋된 산출이 재생성되기 전에도 회귀가 잡히게) | `test_i6w_07` |
| U14-04 | rebase 충돌이 해결되지 않은 채 `out/matrix_300_0009.csv` 에 `<<<<<<< HEAD` 가 박혔고, 그것이 여덟 개의 `KeyError: 'half_cell'`·`'w_dqdv'`·`'obj_ratio_to_best'` 로 나왔다 — 원인에서 먼 오류라 진단이 늦는다 | 사소 (진단) | 닫힘 (테스트) — 산출을 훑어 충돌 표식을 바로 말한다; 탐지기 자체 증명 포함 | `test_i6w_08` |

**교훈 (스키마를 바꿀 때)**: 산출 스키마에 열을 더하면 그것을 **읽는 쪽**을 같이 고쳐야 하는데, 커밋된 산출이
옛 판이면 테스트가 통과해 버려 그 사실이 안 보인다. R6 내부 F02·F04·F05 가 더한 열(`run_id`·`inputs_sha`·
`profile_scale`)의 소비자를 전수로 확인한 것은 아니다 — U14 산출이 들어오면 전체 테스트가 그 감사다.

## U14 판정 (2026-09-12) — **결론 숫자는 전부 재현됐다. 움직인 것은 γ 프로파일의 개별 행이다**

사용자 기계 네 상태 재실행(`STARTS=24`, 12 산출) 을 커밋 `bfc4623^` 의 정본과 셀 단위로 댔다
(`python3 scripts/check_u14.py --new out --old-rev bfc4623^`; 환경은 python 3.12.3 · numpy 2.5.3 · scipy 1.18.1 ·
pandas 3.0.5 · WSL2 — 정본을 만든 조합은 meta 에 없어 모른다, 그것이 F3 의 요지였다).

| 무엇 | 최대 상대차 | 뜻 |
|---|---|---|
| `matrix_100·200·300_0147.csv` (전 셀) | **0.00e+00** | B축 산출은 비트 단위로 같다 |
| `matrix_300_0009.csv` ↔ 옛 `_v2` | **0.00e+00** | 재실행이 v2 를 그대로 재현 (U14-05 참조) |
| `degeneracy_*` 의 세 mode `span` | **0.00e+00** | §1-10 A축 폭 — 결론 숫자가 그대로다 |
| `profile_gamma_*.csv` 개별 행 | LAM_NE 2.8e-2 · b_NE 3.6e-1 · rmse_pocv 2.1e-2 | 국소 최적점이 갈린 행이 있다 |
| §5-1 문턱 표 (8·10·11·12 mV) | n 6/10/12/13 **동일**, 폭 13.5860 → 13.5859, 최악 비 동일 | 문서 숫자(소수 3자리)는 그대로 |

**읽는 법**: degeneracy·matrix 는 multistart(24 시작) 라 국소 해가 안정적이고, `profile` 은 γ 마다 등식 제약을 걸고
적은 시작으로 푸는 구조라 입력의 ULP 차이가 다른 국소 최적점으로 갈 수 있다 — F3(scipy 판에 따라 `savgol_filter` 가
ULP 로 갈리고 L-BFGS-B 최적점이 달라진다)이 **야생에서 확인된 것**이다. 다만 영향은 갇혀 있다: §5-1 이 세는 n 과
최악 비는 그대로고 폭은 넷째 자리에서만 움직인다. **어떤 결론도 뒤집히지 않았다.**

**남는 한계**: 정본을 만든 라이브러리 조합을 모른다 (그 산출에는 `env` 가 없다). 그래서 "이 차이가 scipy 판 때문" 은
**가설**이고, 닫으려면 같은 기계에서 옛 조합으로 한 번 더 돌려야 한다 (U16 후보). 지금부터의 산출에는 `env` 가 붙는다.

| ID | 무엇 | 심각도 | 상태 | 테스트 |
|---|---|---|---|---|
| U14-05 | U14 재실행이 `out/matrix_300_0009.csv` 를 덮었는데 그 자리에 있던 것이 §4-0 이 "고치기 **전**" 으로 인용하는 v1 이었다 (재실행은 수정된 코드라 `_v2` 를 재현 — 새 파일 ↔ 옛 v1 최대 상대차 4.17e-01). 파이프라인이 덮어쓰는 이름에 역사 자료가 놓여 있었다 | 숫자가_바뀜 (§4-0 의 근거가 사라졌다) | 닫힘 — `out/archive/matrix_300_0009_premultistart.csv` 로 보존(+`out/archive/README.md`), §4-0·§3-3 인용과 테스트 둘을 그쪽으로. archive 는 `out/*.csv` 비재귀 glob 에 안 걸려 소비자와 섞이지 않는다 | `test_i6d_06`·`test_i6d_09` |
