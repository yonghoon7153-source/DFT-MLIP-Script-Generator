# 61차 게이트 리뷰 요청 — 묶음 5 (실행 전 승인 · 보존 lifecycle)

## 판정 대상 (이 블록이 정본이다)

| 항목 | 값 |
|---|---|
| 브랜치 | `claude/14-gate-code-review-9qkx05` |
| **판정 대상 코드** | **`3a08f5894e94ef246f43dfbc04c1df2cbf2e086a`** (RUN_SCOPE 를 마지막으로 건드린 커밋) |
| `source_digest` (RUN_SCOPE `src/ tools/ configs/ scripts/ run.sh requirements*.txt`) | **`4227b40871fa0c10`** (직전 `d29650980daf6b9a`) |
| 직전 판정 | 61차 **NO-GO** — P0 2건 · P1 4건 · P2 1건 |
| 이번 라운드 | 접수 7건 **전부 코드에서 닫음** + 자체 발견 6건 |

> **fetch 는 브랜치 head 로 해 주기 바란다.** 요청문은 자기가 담길 커밋 SHA 를
> 적을 수 없다. 그래서 둘을 나눈다:
>
> - **판정 대상 코드** = `3a08f589` — `source_digest 4227b40871fa0c10` 이것을 가리킨다.
> - **이 문서** = 브랜치 head. `3a08f589` 이후 커밋은 RUN_SCOPE 를 **한 바이트도**
>   안 건드렸다 (아래 재현).
>
> ```
> git fetch origin claude/14-gate-code-review-9qkx05 && git checkout FETCH_HEAD
> cd degradation-degeneracy
> python3 -c "import sys; sys.path.insert(0,'.'); from src.io import source_digest; print(source_digest())"
> # → 4227b40871fa0c10 이어야 한다. 아니면 그 자체가 발견이다.
> git log --oneline 3a08f589..HEAD -- src tools configs scripts run.sh requirements*.txt
> # → 출력이 비어야 한다.
> ```

**RUN_SCOPE 밖이지만 이번 라운드가 크게 고친 파일 둘** —
`docs/22p_gap/row_projection.py` (producer identity · δ 가 고쳤다) 와
`docs/22p_gap/mutation_replay.py` (변이 재생·증거층 · γ 가 고쳤다). 둘 다
`source_digest` 에 안 들어가지만 **cohort pin 과 변이 등록부의 정본**이므로
판정에는 브랜치 head 의 그 두 파일을 봐 주기 바란다 (`CLAUDE.md` 하드 룰 3).

**환경 안내.** 이 저장소의 전체 회귀는 `pybamm`·`tqdm` 을 요구한다. 없으면 그 두
의존성에 걸리는 시험이 **환경 실패**로 빨개진다 (코드 발견이 아니다).
`requirements.txt` 로 설치하고 돌려 주기 바란다.

---

## §0 먼저 — 이번 라운드가 **하지 않은** 것

| 조건 | 상태 |
|---|---|
| **P0-1** producer 결속 — 닫힌 typed manifest 파싱 · 두 payload 압축해제 재해시 · producer 발행 영수증 | **미착수** (49차부터 **열세 라운드째**) |
| trusted launcher 의 source 측정 | **미착수** |
| **P0-4** typed 보존 영수증 **소비** | **부분** |
| 변이 증거의 **독립 replay** | **미착수** — 61차 γ 도 증언의 **실패 전파**를 고쳤을 뿐, checker 가 스스로 재생하지는 않는다 |
| 묶음을 **immutable content-addressed object** 로 먼저 게시 | **미착수** — 60차는 내용 주소를 **기록**했을 뿐이다 |
| 실행 class 5종 중 3종 미구현 · 등록부 삭제 절차 | **미착수** |
| baseline·sweep1d·wsweep 계획 gate · 실물 object-lock adapter · power-loss 모델 · publisher 전용 OS principal | **미착수** |
| 외적타당도 **#50** (`truth_provenance` 를 기계 계약에) | **미착수** |

### 이번 라운드가 스스로 신고하는 것

**① `staged_root()` 는 여전히 `/proc/self/fd/N` 이다 — 그러나 이제 기록에는 안 들어간다.**

60차가 gate 이후의 모든 쓰기를 handle 아래로 옮기면서 그 경로가 **기록에도**
들어갔고, 그것이 이번 P0-2 였다. β 는 논리 경로와 쓰기 뿌리를 갈라서 기록을
논리 이름으로 되돌렸다. 남는 전제는 60차와 같다 — `/proc` 의존, 프로세스 지역,
다른 커널에서는 writer 를 `openat` 으로 옮겨야 한다.

**② 파생 manifest 는 identity 밖이고, 그것이 **선언**이다 (P0-1 의 대가).**

`analysis_manifest.yaml` 은 이제 내용 identity 에 안 들어간다. 그래서 **report 를
아무리 갈아 치워도 실행의 identity 는 안 바뀐다** — 그것이 P0-1 이 요구한 것이지만
동시에 "report 산출은 identity 로 보호되지 않는다" 는 뜻이기도 하다. 봉인은 그
바이트를 `derived` 로 **기록만** 한다. report 산출의 무결성이 필요하면 그것은
identity 가 아니라 **별도 층**이어야 한다 — 이 라운드의 범위 밖이고, 반증 조건은
"파생 산출의 변조가 아무 층에도 안 걸리는 경로" 다.

**③ `run-content-id` 가 v3 → v4 로 갔고, 등록부는 re-key 했다.**

58차 L2 전례대로 **새 키에 승계 레코드**를 쓰고 `evidence` 에 승계를 적었다 —
판단을 새로 하지 않았다. v3 레코드는 지우지 않는다 (감사 대상).

**④ 증언은 여전히 "실행이 소비한 바이트 전부" 가 아니다 (γ 의 한계).**

γ 는 측정 **실패가 성공 모양을 갖는 것**을 고쳤다. 못 잰 것을 못 쟀다고 적게
됐을 뿐, 측정 범위 자체는 안 넓혔다. 종결은 §0 표의 독립 replay 다.

**⑤ 시험이 공유 실행 class 등록부에 레코드를 남긴다 (이번 라운드 자체 발견, 미수정).**

실측 (전체 회귀가 도는 중, 2026-09-09):

```
git ls-files docs/22p_gap/_exec_class | wc -l      16     (추적)
ls docs/22p_gap/_exec_class/*.json    | wc -l     104     (디스크)
mtime                                             88건이 이번 실행 창 안
docs/22p_gap/_exec_class/local/                  6471     (gitignored — 58차 L14)
```

`.gitignore:52` 는 `canonical`·legacy 분류를 **감사 대상이라 커밋한다**고
선언한다. 그런데 시험이 만든 레코드가 그 자리에 섞인다. **어느 시험이 쓰는지는
아직 못 좁혔다** — 원장을 monkeypatch 하지 않는 넷이 후보다
(`tests/test_compare.py` · `test_exec_class_capability_59.py` ·
`test_fitting.py` · `test_handle_carry_59.py`).

고치지 않은 이유는 하나다: 고치면 RUN_SCOPE 가 움직여 영수증·g16·12조각 전수
재생을 전부 다시 만들어야 한다 (~28분 + 재생). 산출물 identity 와
`source_digest` 에는 영향이 없다 (`docs/` 는 RUN_SCOPE 밖). 다음 라운드에서
좁혀서 닫는다.

**⑥ grid 의 **콘솔 요약**은 아직 staged 경로를 적는다 (β 를 닫은 뒤 이번 마감의
strict smoke 출력에서 우리가 봤다, 미수정).**

```
$ ./scripts/smoke_e2e.sh   ── 1. PyBaMM 합성 격자 (producer artifact) ──
{
  "n_ok": 6,
  ...
  "out_dir": "/proc/self/fd/3"      ← 여기
}
```

`src/grid.py:806` 의 `summary` 다. β 는 리뷰어가 짚은 **durable** 기록
(manifest·phase receipt·다음 phase 가 여는 자리)을 논리 이름으로 되돌렸고,
grid 의 durable 기록은 이미 `named_out` 을 쓴다 (`:837` `"out": str(named_out)`
· `write_curves_manifest(named_out, …)`). 남은 것은 `print(json.dumps(summary))`
한 줄뿐이다 — **provenance 가 아니라 운용자에게 보이는 문장**이고, 파일로
안 남는다. 그래서 P0-2 의 "존재하지 않는 경로가 provenance 가 된다" 에는
해당하지 않지만, **운용자가 다음 명령에 복사해 넣을 경로**를 거짓으로 말한다.

고치지 않은 이유: 한 줄이지만 RUN_SCOPE 라서 `source_digest` 가 움직이고,
그러면 이 라운드의 증거 사슬(영수증 재생성 ~28분 · 전체 회귀 44분 · strict
smoke)을 통째로 다시 만들어야 한다. 그 재검증은 **판정 뒤에** 한 번에 하는
편이 싸다. 다음 라운드 첫 항목으로 적어 둔다 (`docs/GATE61_WORKING_STATE.md`).
이것이 발견으로 세어져야 한다면 그렇게 세어 주기 바란다 — 우리가 먼저 봤다는
사실이 등급을 낮추지는 않는다.

---

## §1 발견별 — 무엇이 틀렸고 무엇을 바꿨나

판정문이 정리한 **세 형태**로 묶는다.

> ① 경계의 **구성원을 우연이 정한다** (있는 파일 · basename)
> ② **논리와 물리를 같은 값으로 쓴다** (사라질 값이 durable 기록에)
> ③ **못 잰 것을 잰 것처럼 말한다** (실패가 성공 dict 로)

| ID | 무엇이 틀렸나 | 무엇을 바꿨나 | 증인 (시험) | 변이 축 |
|---|---|---|---|---|
| P0-1 | resume commit 이 **옛 report 를 봉인에 흡수**하고, 이어지는 정상 report 갱신이 그 봉인을 stale 로 만들어 승격이 거부된다 | member 집합을 **선언**이 정한다 — `RUN_IDENTITY_MANIFESTS`(실행이 만든 것, identity) 와 `RUN_DERIVED_MANIFESTS`(파생, 기록만) 로 가른다. `RUN_MANIFEST_SCHEMA` 는 둘의 합집합으로 남겨 59차 M2 를 안 깬다 | `test_temporal_seal_61.py` 7건 | `derived-manifests-are-outside-the-identity-g61` |
| P0-2 | fit 이 `/proc/self/fd/N` 을 manifest·summary·phase receipt 에 적는다 — 성공하면 **없는 경로가 provenance** | 논리 경로(`logical_in`/`logical_out`)와 쓰기 뿌리(`write_root`)를 나눠서 들고 간다. writer 는 뿌리 아래로, 기록은 전부 논리 이름으로 | `test_logical_paths_61.py` 8건 | `records-keep-the-logical-input-g61` · `records-keep-the-logical-output-g61` |
| P1-1 | capability 를 **마지막 사용자보다 먼저** 닫고, lock 삭제가 `OSError` 를 삼킨다 | `commit_run_outputs()` 를 lock 해제 **뒤로** 옮겼다 (부수 효과: 봉인이 논리 이름을 받아 `_assert_still_the_judged_dir()` 가 **실제로 검사**한다 — 전에는 조기 반환) · `release_run_lock()` 이 오류를 안 삼킨다 | 같은 파일 | `the-run-lock-is-released-g61` · `lock-release-failure-is-not-swallowed-g61` |
| P1-2 | 복수 root 의 동명 module 이 basename 키 하나로 접힌다 — 게다가 **뒤** root 로 덮는다 (Python 은 앞을 고른다) | 키에 **검색 순서**를 담는다 (`"<i>/<name>"`). 회귀는 "뒤집으면 값이 바뀐다" 가 아니라 **"첫 자리가 앞 root 의 바이트인가"** 를 묻는다 — 앞의 물음은 접는 구현도 통과한다 | `test_evidence_receipt_61.py` 10건 | (58차 축 재조준) |
| P1-3 | startup-history 측정 실패가 `{"<unmeasured>": "1"}` 로 성공이 된다 | 측정을 **typed** 로 (`status: measured\|failed`). rc·timeout·해석 실패·예외가 전부 `failed` 로 흐르고, builtin/frozen 은 `unfiled` 로 센다. 읽는 쪽이 **불완전한 영수증을 거부**한다. `packages` 도 같은 결함이라 같이 고쳤다 | 같은 파일 | `execution-receipt-binds-the-startup-g58` (완전성 거부로 재조준) |
| P1-4 | comprehension 결속을 **부모 scope** 에 적용한다 | comprehension 을 **자식 scope** 로 내려보내고 target 은 그 안에서만 묶는다. 최외곽 iterable 은 바깥에서 평가 | `test_scope_model_61.py` 5건 | `comprehensions-are-their-own-scope-g61` (MULTI 2자리) |
| P2 | 계약이 "AST 정규형에서 docstring 이 사라진다" 고 적는데 코드는 **보존**한다 | 문구를 정정하고 **언제 왜 뒤집혔는지**(51차 P0-I · 60차 P0-13)를 같이 적었다. `src/fitting.py` 인용 줄번호 둘도 갱신 (β 가 함수를 옮겼다) | `test_stage3_contract_cites_live_code_facts` | — (문서) |

---

## §2 증거 — 전부 이 브랜치 head 에서 실행한 출력이다

### 2.1 판정 좌표

```
판정 대상 코드          3a08f5894e94ef246f43dfbc04c1df2cbf2e086a
source_digest          4227b40871fa0c10          (직전 d29650980daf6b9a)
그 뒤 RUN_SCOPE diff    없음
    git log --oneline 3a08f589..HEAD -- src tools configs scripts run.sh requirements*.txt
    → 빈 출력
```

### 2.2 회귀

```
python -m pytest tests/ -q      1615 passed, 1 xfailed   (44분 26초, exit 0)
./scripts/smoke_e2e.sh          pipeline smoke 통과 (✅ 52건, exit 0)
                                — RUN_SCOPE clean 인 상태에서 돌렸다
```

둘 다 이 문서 직전 커밋(전수 재생 증거를 담은 `54b7be67`)의 트리에서 순차로
받은 출력이다. 그 뒤 커밋은 `webapp/`·`docs/` 만 건드렸다 — RUN_SCOPE 의
dirty 판정은 `src/ tools/ configs/ scripts/ run.sh requirements*.txt` 만 보므로
smoke 의 전제는 그대로다 (`src/io.py:git_info` 의 `scope` 인자).

### 2.3 변이 등록부와 전수 재생

```
MUTANTS 201 · MULTI 31 · EXPECT 223 · DECLARED_MASKED 10 · 61차 축 6

--check-preimages               모든 변이 지점이 정확히 한 번 나타난다
slice 1..12 (한 HEAD 에서 순차)  전부 rc=0
--check-coverage s*.json        등록부 scenario 232 (executable 222 · declared 10)
                                조각 12개에서 관측 232
                                조각 합집합이 등록부 전체를 정확히 덮었다
```

**전수 재생을 세 번 돌렸다.** 앞의 두 번은 재생 자신이 낸 발견 때문에 트리를
고쳐 처음부터 다시 돌렸다 — 조각마다 다른 코드에서 난 coverage 는 합집합의
근거가 못 된다. 무엇을 잡았는지는 §3 에 적는다.

### 2.4 cohort 세대 전환 (g15 → g16)

```
g15_2026_09_08  active → frozen  (journal seq 14)
g16_2026_09_09  새 active · docs/22p_gap/proj_g16

pin  compute            3b94bda70dc63869 → fa5b9324c01ab7f0
     row_projection     a425da3233253625 → 0e22767966646d49
     producer_semantic  6518c2fa47f1e8c4 → 2e2ddce417ecf0db
     src_scoring        69e69cb046f4b4ae (변동 없음)
영수증 core_sha256       fc1cf9c0ef22490f05b2f5291afeb6fa3b2546637463a92a036f7a0d43817009
validator                4227b40871fa0c10
행 바이트                 ad598fe77e75afec — **열두 세대째 같다**
```

대상 커밋: `e37bff8047a624884744de5a8ca13f7849df4347`
— 위 `core_sha256` 은 이 커밋의
`docs/22p_gap/receipts/paired_fixed5_v4.validate.yaml` 을 가리킨다 (세대를 넘긴
커밋이고, 그 뒤로 영수증은 안 바뀌었다). 요청문이 인용한 값은 **그것이 이름한
커밋**에 대고 대조하는 것이 자기완결의 뜻이다.

pin 을 움직인 것은 δ 하나다 — analyzer 가 comprehension 을 자식 scope 로 다루게
됐다. `src_scoring` 이 그대로이고 행 바이트가 안 움직인 것이 "이번 라운드는
증거·경계층만 건드렸고 계산식은 안 건드렸다" 를 실물로 말한다.

전환 중에 이 저장소가 앞선 라운드에 세운 층 셋이 물었다: 얼린 cohort 를
복사하면서 `frozen_reason` 이 딸려 오자 **"status 만 active 로 되돌린 해동이다"**
로 거부 · `evidence.cohorts` 양방향 대조가 g16 누락을 잡음 · 원장의
`validator_identity.source_digest` 가 새 영수증과 어긋난다고 잡음.

---

## §3 이 라운드가 스스로 잡은 것 (6건)

**① 축은 "지운 검사" 가 아니라 고치기 전 코드를 되돌려야 한다.**
δ 의 축을 처음엔 `if _is_comprehension(sub):` → `if False:` 로 뒀는데 **안 물었다**.
검사를 지우면 분석기가 comprehension 안으로 들어가기만 하고 결속은 여전히 안 해서
**고치기 전의 틀린 동작이 복원되지 않는다**. 61차 이전 문장
(`if isinstance(sub, ast.comprehension): out |= …`)을 되살리자 리뷰어의 반례가
그대로 증인이 됐다. 이 저장소의 축 규율에 한 줄이 늘었다.

**② α 가 60차 P0-1 의 축을 가렸다.**
파생 manifest 를 선언 밖으로 빼자 "굳힌 뒤 `analysis_manifest.yaml` 을 더해도
class 가 안 사라진다" 는 증인이 **봉인이 없어도** 통과하게 됐다 (변이 rc 0). 즉
그 시험은 더 이상 봉인의 증인이 아니었다. 봉인이 지금 실제로 지키는 자리 —
**grid 가 굳힌 뒤 fit 이 같은 자리에 실행 manifest 를 더하는 정상 순서** — 로
증인을 옮겼다.

**③ 새 축 하나가 58차 축과 preimage 를 공유했다.**
`startup-facts-are-in-the-receipt-g61` 이 `execution-receipt-binds-the-startup-g58`
과 같은 자리를 겨눴다. `--check-preimages` 가 아니라 **전수 재생**이 잡았다
(같은 원상을 둘이 나눠 가지면 한쪽의 관측이 다른 쪽 것이 된다). 새 축을 떼고
58차 증인을 **완전성 거부**로 재조준했다.

**④ 증인은 접두 대조다 — 꼬리 공백 한 칸이 5조각을 멈춰 세웠다.**
③ 을 고치며 증인에 박혀 있던 content id 를 잘라 냈는데, 자르면서 남긴 **공백
한 칸**(`"… 내용 "` vs 실제 `"… 내용"`) 때문에 12조각 중 5조각이
"baseline 이 이미 빨갛다" 로 멈췄다. 그 실패 문구는 변이 쪽을 먼저 보게 만들어
원인을 늦게 찾게 한다.

**⑤ γ 가 리뷰어가 안 짚은 두 번째 자리를 같이 고쳤다.**
`packages` 도 실패를 `{"<unavailable>": ""}` 라는 정상 dict 로 바꾸고 있었다.
규칙이 한 자리에 있지 않으면 **남은 중복이 곧 다음 반례**다.

**⑥ 미수정 둘 — 시험이 공유 등록부에 레코드를 남긴다(§0-⑤) · grid 의 콘솔
요약이 staged 경로를 적는다(§0-⑥).** 둘 다 이번 마감에서 우리가 봤고, 둘 다
RUN_SCOPE 나 재검증 사슬을 건드려야 해서 판정 뒤로 미뤘다. 이유는 각 항목에
적었다. 특히 ⑥ 은 이번 라운드가 스스로 세운 규칙("규칙이 한 자리에 있지
않으면 남은 중복이 곧 다음 반례")의 **반대 사례**다 — γ 에서는 두 번째 자리를
같이 고쳤고, 여기서는 비용 때문에 안 고쳤다. 그 차이가 무엇 때문인지를 여기
적어 두는 것이 최소한의 정직성이라고 본다: γ 의 둘째 자리는 같은 파일의 같은
함수족이었고, ⑥ 은 증거 사슬 전체의 재생성을 요구한다.

---

## §4 판정 대상이 아닌 것 (혼동 방지)

이 라운드는 **계산식을 안 건드렸다.** cohort 를 `g15` 에서 `g16` 으로 넘겼지만
투영의 행 바이트는 `ad598fe77e75afec` 로 **열두 세대째** 같다. pin 이 움직인
이유는 producer analyzer 의 scope 모델이 Python 과 맞춰졌기 때문이고(P1-4),
`src.scoring` 과 analysis spec 은 안 움직였다. 그래도 **cross-cohort 비교는
금지**다 — 같은 바이트라는 사실은 회귀가 확인하는 것이지 인용의 근거가 아니다.

연구 수치의 정본은 artifact 와 `docs/RESULTS*.md` 이고, 이 문서의 숫자는
**게이트 판정용 좌표**다.
