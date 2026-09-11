# 적대적 리뷰 요청 — 6차 라운드 · α·β 검증 하네스 (`bms-balancing/`)

5차(대상 `0cb7b7a`)는 **NO-GO** (P1 7 · P2 4, `reviews/R5_CODEX.md`). 열한 건 전부 우리 트리에서 재현됐고
(`reviews/r5_repros/replay_ours_0cb7b7a.json` — 11 단계 rc 일치), 반박 성립 없음. 이 판은 그 열한 건의 대응이다
(`reviews/R5_LEDGER.md`). GO 기준은 R3 §5 의 다섯 조건에 대한 R5 §4 의 재판정("부분" 이던 1·3·4)이다.
목표는 같다: **"정본이 우리 새 모델의 설계 근거로 쓸 만한가"**.

**6차는 외부 리뷰 전에 내부 자체 리뷰를 먼저 돌렸다** (Codex 토큰 소진, 2026-09-11): 네 렌즈 37 건 → 적대적 검증 CONFIRMED 30
전부 닫음 (`reviews/R6_LEDGER.md`, §2b). 이 요청문은 그 위에서 시작한다 — 우리가 이미 찾은 것과 신뢰 경계로 남긴 것을 §2b 에 밝혔다.

## 0. 대상

| 항목 | 값 |
|---|---|
| 커밋 | 이 파일이 들어 있는 커밋 (`git log -1`; R5 대응 본체는 직전 커밋) |
| 브랜치 | `claude/bms-alpha-beta-verify` — `bms-balancing/` 소유 |
| 범위 | `bms-balancing/` 만 |
| 정본 | `FINDINGS.md` + `out/` (+ `.meta.json`). 이 요청문의 숫자는 사본 |
| 저장소에 없는 것 | 원본 MATLAB · 원자료 xlsx · 문헌 OCP → `BMS_DATA_ROOT` (전과 같음) |
| 우리 환경에서만 되는 것 | U13 — 새 감사 줄(식별자·eps_rel·equiv)의 `eval` 실측: **완료** (`out/scale_audit_eval_u13.txt`, 18 build 전부 `equiv=1`, eps_rel ≤ 1.7e-15; 루트 이름은 보고 순서 — 다음 판부터 `root=`) |

```bash
git clone -b claude/bms-alpha-beta-verify https://github.com/yonghoon7153-source/Yonghoon-DEM-DFT
cd Yonghoon-DEM-DFT/bms-balancing && git checkout <이 파일이 든 커밋>
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python3 -m pytest tests/ -q                       # 원자료 불필요. 122 passed 기대 (동시 실행 시험은 subprocess·fcntl.flock 사용, Linux/WSL; 합성 xlsx 로 실제 build·degeneracy 도 돈다)
# ⚠ fresh clone 으로 (위 명령). autocrlf 가 켜진 옛 사본을 pull 로 올리면 안 바뀐 `.sh` 가 CRLF 로 남아 run_all.sh 가 죽는다 — `git add --renormalize` 로는 안 고쳐진다 (R6 내부 F6)
# R6 내부 반례 재생: reviews/r6_repros/<렌즈>/repro_*.py 는 대상 1049894 (worktree) 에서 전부 '재현' 이고 이 트리에서는 그 assertion 이 실패해야 한다
bash matlab/tests/run_all.sh                      # Octave 없으면 4·5 단계
# R5 반례 재생 — 대상 SHA 가 0cb7b7a 이어야 돌므로 worktree 로:
git worktree add /tmp/r5 0cb7b7a && python3 reviews/r5_repros/harness_r5_replay.py --target /tmp/r5/bms-balancing --output /tmp/r5.json
# 수정된 트리에서는 반례의 '재현' assertion 이 실패해야 한다 (닫힘):
python3 reviews/r5_repros/harness_r5_port_repros.py --target "$PWD" --case sig2_zero_false_complete      # model_mismatch 에서 AssertionError
python3 reviews/r5_repros/harness_r5_port_repros.py --target "$PWD" --case parameter_header_swap_false_complete   # invalid 에서 AssertionError
python3 reviews/r5_repros/harness_r5_inference_repros.py --target "$PWD" --case exception   # n=50 에서 AssertionError
python3 reviews/r5_repros/harness_r5_inference_repros.py --target "$PWD" --case matrix      # 감사 열 존재에서 AssertionError
python3 reviews/r5_repros/harness_r5_claims_repros.py --target "$PWD"                        # quoted_path_roles 에서 AssertionError
python3 reviews/r5_repros/harness_r5_execution_repros.py --target "$PWD"                     # metadata_race 에서 AssertionError (A rc ≠ 0)
```

## 1. 검증 — 2026-09-11, 이 트리, 작업트리 clean

| 검사 | 결과 |
|---|---|
| `pytest tests/ -q` | 122 passed (R5 신규 11 · R6 내부 신규 35) |
| `matlab/tests/run_all.sh` | 4·5 단계 통과 (Octave 없음) |
| R5 반례 | port 8 건 → model_mismatch/invalid, inference exception·matrix, claims quoted_path, execution metadata_race — 전부 수정 뒤 assertion 실패. 통과로 남는 것과 이유: `epsilon`(감사 dict 새 키에서 멈춤 — 22205 배 차이 자체는 사실, flag 로 표시), `population`(증거 수준을 사본으로 한정한 결과), `scope`(§0-2 의 철회 인용문이 옛 문장을 담음 — 살아 있는 §1-13 은 `test_r5_docs_*` 가 확인), `consumed_untracked_input`(옛 다섯 필드는 의도적으로 같음 — 닫힘은 새 `consumed_inputs`) |
| RED 확인 | 신규 11 이 옛 코드·문서에서 11 실패 — 이유 확인(`%.2g` complete, 중복 선언 complete, 이름 바꾼 p complete, meta A≠CSV B, consumed_inputs 없음, eps flag 없음, matrix 감사 없음, 행마다 다른 id, n=100, 한글 경로 code, 문서) |

## 2. R5 열한 건 — 대응

| R5 | 판정 | 어디서 | 테스트 |
|---|---|---|---|
| 01 `%g` 구간 | 닫힘 (코드) | `token_excess`: 같은 형식으로 실제로 찍어 구간을 정한다 (같은 문자열 = 자리수 안, 아니면 경계까지 이분법); audit 이 토큰을 선언 형식으로 다시 찍어 일치 확인. 전제: Python format = C/MATLAB printf 규칙 (유효자리 반올림·뒤 0 제거·지수 전환) | `test_r5_01_*` (8 경우) |
| 02 선언·앵커 역할 | 닫힘 (코드) | audit: 선언 유효한 하나만 · 알려진 앵커는 숫자 하나만(비유한은 incomplete) · 아니면 `invalid`. 예외: 해석 못 하는 선언은 명시 `--precision` 이 대체 (Q1, README 명시) | `test_r5_02_*` |
| 03 파라미터 열 이름 | 닫힘 (코드) | `header[:5] == PARAM_COLS` 아니면 `invalid` | `test_r5_03_*` |
| 04 결과+meta 묶음 | 닫힘 (코드) | `publish_lock`(`<산출>.lock` flock) — verify.py 게시·shell degeneracy `mv`·`write_meta` 가 같은 잠금; meta 작성자는 잠금 안에서 id 를 필드로 재확인, bytes sha256 을 meta 에; 실패면 meta 안 씀; 게시 뒤 `provenance --verify-unit`. 정책: 동시 실행 허용, "마지막 온전한 묶음" 만 남음 | `test_r5_04_*` (Codex 와 같은 schedule → B/B, A 거부), `test_r4_06_concurrent_*` 갱신 |
| 05 소비 입력 | 닫힘 (코드) | `fitted_pair_info` → meta `consumed_inputs`: matrix 경로·sha256·행, 반쪽전지·문헌 경로·sha256 (tracked 무관) | `test_r5_05_*` |
| 06 동치 조건 | 닫힘 (코드+정정+**실측**) | 감사에 `raw_lower_half_mean`·`scale`·`eps_rel`·`equivalent_within_rel`(유한·예외 없음·eps_rel ≤ 1e-9 — 상대 근사); §1-13·§0-1·§0-2: "16 build 전부 유한 → 영역 안" 을 철회, 동치는 새 감사 줄로만 | `test_r5_06_*` |
| 07 matrix 감사 | 닫힘 (코드) | 행에 `scale_*_target/ref`·`scale_audit_target/ref`·`scale_seed`·`n_scale_samples`; stdout 행 JSON | `test_r5_07_*` |
| 08 run id 계약 | 닫힘 (코드) | `main()` 이 파싱 직후 id 고정; `check_run_id`(CSV 열 전 행 / JSON 필드) | `test_r5_08_*` |
| 09 U12 범위 | 닫힘 (정정) | §1-13: "보고 순서의 16 줄(식별자 없음)", 192 값 중 GITT·Li 96 값만, Kunz·step_005C 96 값 실측 밖; 감사 줄에 식별자 추가 | `test_r5_docs_*`, `test_u12_*` |
| 10 감사 개수 | 닫힘 (코드) | 항별 try, 표본당 한 기록, `n_exception` | `test_r5_10_*` |
| 11 quoted 경로 | 닫힘 (코드) | `git status --porcelain -z` 레코드 (rename 두 경로) | `test_r5_11_*` |

## 2b. R6 내부 자체 리뷰 — 무엇을 찾았고 무엇을 신뢰 경계로 남겼나 (`reviews/R6_LEDGER.md`)

| 렌즈 | 발견 → CONFIRMED | 결론급 | 신뢰 경계로 남긴 것 |
|---|---|---|---|
| validator 우회 | 9 → 8 | 헤더 위치·`--precision` 옵션·헤더 없음·부분 대조 하한으로 1 % 급 차이가 complete/`--allow-partial` 0 (V6-01~04) → 전부 invalid | V6-09 `%f` ±0 경계: rmse 가 sqrt(mean(r²)) 라 도달 불가. R5-01 의 "format = sprintf" 전제는 MATLAB 판 의존 — 미실측 |
| 순서/TOCTOU | 9 → 8 | F01 degeneracy 게시가 producer 의 stdout fd 로 잠금 밖에서 덮임 (R5-04 의 "마지막 온전한 묶음" 이 그 경로에서 거짓) → `--out` 잠금 게시; F07 reader 절 구현 | F08 run_id 는 공개 열 — 복사한 producer 는 못 가린다 (위협 모델 밖; 소유 증명은 주장한 적 없음) |
| 파생 보고서·공정성 | 10 → 8 (+부분 2) | DF-01 §3-4 "두 독립 방법이 수렴" 은 힌트 격자가 제약 최적화의 끝점을 격자점으로 포함한 결과 → 정정; DF-02 HANDOFF·INTRO 의 철회 문장 잔존 | 공정성: seed 0 하나·1e-9 문턱은 verdict 에 무관(여유 5.8e5 배), 예산 차이(30 sqp vs 24 L-BFGS-B)는 밝혀져 있고 like-for-like 를 주장하지 않음 |
| sig-완전성·이식성 | 11 → 8 (+부분 3) | F4 풀셀 워크북 identity 미기록 → `consumed_inputs`·`inputs_sha`; F3 라이브러리 버전 미기록 (scipy 1.11↔1.17 에서 최적점 끝자리) → `env` | F2 루트 차원은 사본으로 검증 불가 (U14 부터 identity 로); F6 autocrlf 사본은 fresh clone |

## 3. 철회·정정 목록 (§0-2 에 추가된 R5 행 + R6 내부 행)

"16 build 전부 유한이므로 그 범위에서는 원본 설명식과 포팅의 scale 이 같고, §1-8 의 192 값과 A축 산출은 그 영역 안" (R5-06 · R5-09: eps 조건 미기록, 96/192, 식별자 없음). §0-1 의 "포팅이 원본과 같다" 에 경험적 일치·비유한/eps 영역 제외 한정어.

## 4. 지금 정본이 말하는 것 — 범위를 붙인 다섯 관측 (R5 Q5 반영)

| 관측 | 붙인 범위 |
|---|---|
| 포팅 일치 | 보존된 네 조합 192 출력값의 경험적 일치(TXT 원시값 재계산, `%g` 실제 구간 규칙으로도 complete). 네 로컬 함수의 식 대조는 사용자 기록. scale 동치는 유한·예외 없음·eps_rel ≤ 1e-9 의 상대 근사이고, U13 실측 18 build(recompare 4 조합 포함)에서 그 조건이 성립 — 모든 입력의 동치는 아님(B축 나머지 조합 미실측) |
| 음수 LAM_NE | 공개 5 행 · 고정 기준의 부호 산술, 행별 임계. 경계 변경 재적합의 인과 미확립 |
| 파우치 폭 순위 | 네 상태 · 소스 · 설정의 탐색 하한 순위 4/4. 식별성·정확도 보장 아님 |
| 원통형/PE 대조 · 재척도화 | 명시한 소스 집합·분모·통계량의 기술값. 원인 배제·공유 가능값 증명 아님 |
| 잔차 · γ 변화 | 상태별 RMSE 증가 · 선택된 쌍의 진폭비 · γ_ref 고정 격자 여유(진폭 증인 — 모양 적합 아님). 원인·보상 경로는 가설 |

## 5. 닫지 않은 것

| # | 무엇 | 상태 |
|---|---|---|
| U2 | pOCV 원자료/재표본 | 원시 timestamp·export 설정 필요 (R4 Q1) |
| U3 | 원통형 차이의 원인 | 미확정 — 구분 시험은 요구서 항목 |
| U4~U10 | 전과 같음 | 그대로 |
| ~~U13~~ | 새 감사 줄 실측 | **닫힘** — 18 build 전부 `equiv=1` (`out/scale_audit_eval_u13.txt`); 실측 밖: 나머지 Si 소스 6 종 · step_005C 의 다른 상태 · `w_dqdv=1` 조합 (B축 `matrix` 재실행의 행별 감사로) |
| S-04 | 증인 반대쪽 도달 여부 · 가족 최대의 상태 독립성 표기 | 개선 후보 |

## 6. 리뷰어에게 — 질문

1. R5-01: 구간을 "같은 형식으로 실제로 찍어서" 정하는 방식의 빈틈 — Python `format` 과 MATLAB `sprintf` 가 갈리는 입력(반올림 타이·`%g` 지수 전환 문턱·음의 0)이 있는가. audit 의 "토큰을 선언 형식으로 다시 찍으면 같아야 한다" 검사가 MATLAB 산출에서 오탐을 낼 수 있는가.
2. R5-04: 잠금(`<산출>.lock` flock) + 잠금 안 필드 재확인 + meta 의 sha256 + `--verify-unit` — 남는 창이 있는가. 동시 실행을 거부하지 않고 "마지막 온전한 묶음" 을 택한 것이 맞는가.
3. R5-06: 동치 flag 의 정의(유한 · 예외 없음 · eps_rel ≤ 1e-9) 와 "상대 근사" 표현이 적절한가. 요구서의 scale 항목에 더 넣을 것.
4. R5-05: `consumed_inputs` 의 범위(matrix 행 · 반쪽전지 · 문헌) — 빠진 입력이 있는가 (예: `D.data_root` 의 풀셀 워크북).
5. §4 의 다섯 관측을 요구서 관측 열로 옮기는 데 남은 문제.
6. R6 내부 (§2b): (a) F08 의 위협 모델 — 게시 파일에서 읽은 id 로 만든 묶음을 가려야 하는가, 그렇다면 producer 의 bytes 해시를 stdout 으로 넘기는 설계면 되는가; (b) DF-01 정정문 — "끝점 재확인" 이 §3-3 의 폭을 믿을 근거로 충분한가, 힌트 없는 격자 재실행이 필요한가; (c) V6-02 의 규칙(선언 없으면 옵션 형식으로 토큰 재출력 검사, 선언 있으면 선언) 에 남는 역전이 있는가.

## 7. 실측 첨부

- `reviews/r5_repros/replay_ours_0cb7b7a.json` — R5 반례 우리 재생 (11 단계).
- `out/scale_audit_eval_u13.txt` — U13 실측 사본 (18 줄, 사용자 기계 a78f0a5). 그 외 `out/` 변경 없음 — 새 스키마(`env`·`inputs_sha`·`--out` 게시) 는 U14 재실행에서 처음 채워진다.
- `reviews/r6_repros/<렌즈>/{REPORT.md,repro_*.py,VERDICT.md,verify_*.py}` — R6 내부 리뷰의 발견·재현·검증 판정 사본.

## 8. 이후

GO 면 새 모델 설계 요구서(`docs/`) 초안 — §4 의 다섯 행을 관측 열로. U13 은 요구서와 무관하게 사용자 기계에서 닫는다.
