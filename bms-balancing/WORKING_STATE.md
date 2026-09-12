# 진행 상태 — α·β 검증 하네스

> **이 파일이 "지금 어디까지 왔나" 의 정본이다.** 수치의 정본은 `FINDINGS.md` + `out/`.
> 갱신 규칙: 단계가 열리거나 닫히면 **그 커밋에서 같이** 고친다.

**목표가 바뀌었다 (2026-09-11, 사용자 결정).** 코드를 준 분이 은퇴하며 사용자가
**전권**을 받았다. 규진팀에 회신하지 않고 **우리 독자 모델로 발전**시킨다.
그러므로:
- `FOR_BMS_TEAM.md` 는 더 이상 산출물이 아니다 — **보관**(배너로 표시, 갱신 안 함).
- 검증 하네스의 발견은 "남의 코드 감사" 에서 **"우리가 물려받은 코드의 감사 +
  새 모델의 설계 요구서"** 로 역할이 바뀐다. 새 모델의 출발점은 리뷰가 남긴 **관측**이다
  — PE 기준 처리가 답을 %p 단위로 바꿈 · 원통형의 적합 잔차가 사이클과 함께 커짐 ·
  선택된 γ 쌍의 진폭비 3~16 % · 블렌드 vs 측정 음극 rms 19~24 mV. "모델 부적합"
  은 그 관측들을 함께 설명할 **후보 가설**이지 확인된 원인이 아니다 (Codex R3-01·02:
  정확한 모델 + 상태별 잡음, 정확히 표현 가능한 곡선이 같은 표·같은 비를 낸다).
  새 모델의 요구서는 `관측 → 후보 원인 → 구분 시험 → 채택 기준 → 남는 한계` 로 쓴다.
- 규진팀에 물어봐야 닫히던 U1(전사 함수 2 개)·U2(pOCV 원자료 여부)는 이제 **우리가
  원본 코드·원자료를 직접 열어** 닫을 수 있다.
- 원자료는 여전히 public 저장소에 넣지 않는다 (전권 ≠ 공개). 바꾸려면 사용자 결정.
- 게이트(`degradation-degeneracy/`)는 본체 브랜치 일이다 — 이 브랜치는 R2 원장을
  끝까지 닫고 R3 를 받는다.

최종 순서(갱신): R2 원장 닫기 → R3 리뷰(GO 까지) → 새 모델 설계 요구서

---

## 지금 상태 — **Codex 6차 NO-GO (P1 3 · P2 3) 여섯 건 전부 닫음 · 7차 요청문 준비됨**

2026-09-12 Codex 6차 리뷰(대상 `d431404`, `reviews/R6_CODEX.md`)는 출처 결속 세 조건을 P1 으로 짚었다 — 독자가
검증한 snapshot 이 아니라 경로를 다시 읽는다(R6-01), 현행 산출에 meta 가 없으면 옛 산출로 흘러 들어간다(R6-02),
입력을 파싱한 뒤 경로를 다시 열어 해시한다(R6-03). P2 셋은 정본 선택 규칙이 옛 `_v2` 를 골랐다(R6-04), `-z`
경로를 " -> " 로 쪼갰다(R6-05), U14 판정문의 "적은 시작" 오기(R6-06 — 실제 γ당 25 회). 여섯 건 전부 우리 트리에서
RED 로 재현한 뒤 닫았다 (`tests/test_r6_internal.py` C 절 `test_c6_01`~`06` + Q3 pin). 원장은 `reviews/R6_LEDGER.md`
"Codex R6" 절, 요청문은 `reviews/R7_REQUEST.md`.

규약이 바뀐 것: 독자는 `provenance.read_unit` 이 돌려준 (data, meta) snapshot 만 소비한다 · `run_id` 가 있는
산출은 meta 없이는 미완(False) · 입력은 `data.read_input` 의 bytes 로 파싱과 해시를 같이 한다 · 정본은 unversioned
이름 하나이고 `_vN` 은 `out/archive/` 의 역사 자료다.

## 직전 상태 — R6 내부 리뷰 30 건 닫음 · U13·U14·U15 실측 완료 (닫힘)

Codex 토큰 소진으로 6차는 `/self-review` 로 돌렸다 (네 렌즈 37 건 → 적대적 검증 CONFIRMED 30, 전부 RED → 수정 →
GREEN). 그 뒤 사용자 기계 실측 셋이 붙었다 — U13(scale 동치 18 build), U15(MATLAB `sprintf` 기준선), U14(네 상태
재실행). 원장은 `reviews/R6_LEDGER.md`, 요청문은 `reviews/R6_REQUEST.md`.

**U14 판정: 결론 숫자는 전부 재현됐다.** matrix 세 상태와 degeneracy 세 mode 폭이 **0.00e+00**, §5-1 문턱 표의
n 과 최악 비도 동일. 움직인 것은 γ 프로파일의 개별 행(LAM_NE 최대 2.8e-2)뿐이고 §5-1 폭은 넷째 자리에서만
바뀐다 — F3(라이브러리 판)이 야생에서 확인됐으나 **어떤 결론도 뒤집히지 않았다**. 정본을 만든 라이브러리
조합은 모른다(그 산출에 `env` 가 없다) — "scipy 판 때문" 은 가설이고 U16(옛 조합 재실행)이 닫는다.

U14 가 드러낸 다섯 건(U14-01 줄끝로 서명이 fresh clone 에서 깨짐 · 02 도구의 정본 선택 · 03 새 열을 소비 helper 가
못 읽음 · 04 충돌 표식 · 05 재실행이 §4-0 의 역사 자료를 덮음)은 전부 닫았다.

남은 것: Codex 6차 요청문 송부 (토큰 복귀) → 새 모델 설계 요구서 (문헌 입력은 `docs/LIT_19_20_FOR_NEW_MODEL.md`).
아래 명령은 실행 기록.

```bash
# ── 0. 받기 · 확인 (몇 분) ────────────────────────────────────────────────────────────────────────
cd ~/dd/bms-balancing && git pull --rebase origin claude/bms-alpha-beta-verify
source .venv/bin/activate && export BMS_DATA_ROOT='/mnt/d/가형 관련/degradation mode'
python3 -m pytest tests/ -q                       # 139 passed 기대 (원자료 불필요)

# ── 1. 배관 확인 — 새 스키마가 붙는지만 (몇 분, STARTS=6 이라 수치는 못 쓴다) ─────────────────────
STARTS=6 STATES=100 OUT=out_u14_smoke ./scripts/run_states.sh
python3 scripts/check_u14.py --new out_u14_smoke --schema-only     # 0 이어야 한다
# ↑ 0 이 아니면 여기서 멈추고 출력을 그대로 붙여 줘. 2 = 스키마 누락(옛 코드로 돈 것).
rm -rf out_u14_smoke

# ── 2. 본 실행 — 정본을 덮지 않고 **다른 디렉터리로** 받는다 (몇 시간) ────────────────────────────
#    정본(out/)을 먼저 덮으면 "숫자가 움직였나" 를 댈 대상이 사라진다. 네 상태 × 세 명령 = 12 회.
OUT=out_u14 STATES='100 200 300_0009 300_0147' ./scripts/run_states.sh 2>&1 | tee out_u14.log

# ── 3. 대조 — 새 스키마 + 정본과 같은 숫자인가 ───────────────────────────────────────────────────
python3 scripts/check_u14.py --new out_u14        # 0 = 스키마 갖췄고 숫자 동일 · 1 = 숫자가 다름 · 2 = 스키마 누락
#    out/ 을 이미 덮었으면 정본을 git 에서 읽는다 (손으로 `git show` 를 엮지 말 것 — `--name-only` 는 트리가 아니다):
#      python3 scripts/check_u14.py --new out --old-rev <재실행 커밋>^
#    ★ 1 이면 그것이 발견이다. 계산 경로는 안 고쳤으니 같아야 한다. 출력과 함께 이것도 붙여 줘:
python3 -c "import json;print(json.load(open('out_u14/matrix_100.csv.meta.json'))['env'])"

# ── 3b. U14-01 뒷수습 (2026-09-12 실행에서 드러남) — 줄끝 때문에 서명이 깨진 산출을 다시 서명 ──────
#    writer 가 CRLF 를 썼고 git 은 LF 로 저장한다 → fresh clone 에서 meta 의 sha256 이 안 맞고, reader(F07)가
#    그 상태를 표에서 뺀다. 지금 코드는 LF 로 쓰지만 **이미 게시된 것**은 이 명령으로. 기록된 해시가 지금
#    bytes 의 줄끝 변형과 맞을 때만 다시 서명하고(=내용이 같다는 증명), 아니면 손대지 않는다.
python3 scripts/check_u14.py --new out --renormalize

# ── 4. 0 이었을 때만 정본 교체 ───────────────────────────────────────────────────────────────────
for f in out_u14/*; do mv "$f" out/; done && rmdir out_u14
python3 scripts/ne_shape.py                       # 소비 입력이 바뀌었으니 (d) 표도 다시 (초 단위)
python3 scripts/compare_states.py out             # §1-10 표 재생 — '묶음 불일치' 경고가 없어야 한다
git add out/ && git commit -m "U14 — 새 게시·서명 스키마로 네 상태 재실행 (숫자 동일)" && git push

# ── 5. ~~MATLAB 한 줄씩~~ → **닫힘 (U15, 2026-09-11)**: 둘 다 Python 과 일치 ────────────────────
#      sprintf('%.2f', 0.125)  → '0.12'                    (half-to-even, Python 과 같다)
#      sprintf('%.17g', 1e-5)  → '1.0000000000000001e-05'  (2 자리 지수, 원래 double 로 복원)
#    기준선은 tests/test_r6_internal.py 의 MATLAB_SPRINTF 에 고정. 다른 MATLAB 판·플랫폼의 산출을 댈 때는 다시 잰다.
```
줄마다 `equiv=1` 이면 그 build 에서 scale 이 원본 설명식과 상대 1e-9 안에서 같다 (유한 · 예외 없음 · eps_rel ≤ 1e-9).
`degeneracy`/`profile`/`matrix` 를 다시 돌릴 때는 `run_states.sh` 가 이제 id 를 **필드로** 확인하고 meta 를 잠금
안에서 재확인해 bytes 해시와 함께 쓴다 (R5-04 · R5-08). matrix 행에 target/ref scale·감사가 실린다 (R5-07).

## 직전 상태 — Codex R4 (닫힘, `reviews/R4_LEDGER.md`)

2026-09-11 Codex 4차 리뷰(대상 `39a5fe0`) 일곱 건을 전부 재현·닫았다. U12 실측(사용자 기계, 274f1f8):
4 루트 × 4 상태 16 build 전부 Inf 0 · NaN 0 (`out/scale_audit_eval.txt`) — 그 증거 수준은 R5-09 로 "보고 순서의
16 줄(식별자 없음)" 로 한정했고, 동치 조건에 eps_rel 이 빠져 있던 것은 R5-06 으로 정정했다.

## 직전 상태 — Codex R3 (닫힘, `reviews/R3_LEDGER.md`)

2026-09-11 Codex 3차 리뷰(대상 `a432d23`) 아홉 건을 전부 재현·닫았다. 사용자 기계 실측(`ne_shape.py`
재실행, fb62342)으로 §5-2 (d) 표를 채웠다 — 100·200 은 (a) 진폭을 내는 합법 γ 가 있고(줄이는 쪽),
300_0009 는 합법 최대 86.01 mV < 119.34 mV 로 없다 (정규화·모양 한정어). 그 meta 의 `git_dirty: true`
로 자체 발견 S-01(산출물 재작성이 플래그를 켬)을 잡아 닫았다.

## 직전 상태 — Codex R2 (닫힘, `reviews/R2_LEDGER.md`)

2026-09-11 Codex 2차 리뷰(P1 9 · P2 1)와 내부 리뷰 L2·L5 를 합친 20 항목이
`reviews/R2_LEDGER.md` 에 있고, **닫는 순서**가 거기 적혀 있다. 여기서는 되풀이하지
않는다 — 그 파일의 "닫는 순서" 1~7 을 위에서부터 진행하고, 끝난 항목은 그 표의
"상태" 열을 갱신한다.

가장 아픈 셋: (C1) 대조 실험이 LAM_PE 쪽에서는 원통형 패턴을 **재현**한다 — "대체는
원인이 아니다" 는 LLI 에만 성립 · (C2) 측정 음극은 목적함수가 **소비하지 않는다** —
"35.77 mV 를 지웠는데도" 강도 논증 무효 · (C3·C4) MATLAB 대조기가 비교 안 한 값도
"전부 일치" 로 찍는다 — 192 값 대조를 고친 비교기로 **다시 돌려야** 한다.

Codex 반례 재생: `python3 reviews/r2_repros/harness_r2_replay.py --target $(pwd) --output /tmp/r.json`.

**2026-09-11 저녁 기준 — 원장 20 항목 중 코드·문서 쪽은 닫혔다 (a8084ec, 이 커밋).**
남은 것은 사용자 기계에서 몇 분이면 되는 실측 셋과, 그 뒤 R3 요청문이다:

```bash
cd ~/dd/bms-balancing && git pull --rebase origin claude/bms-alpha-beta-verify
source .venv/bin/activate && export BMS_DATA_ROOT='/mnt/d/가형 관련/degradation mode'
# ① PE 축 개입 강도 (§1-12 조건 7) — 초 단위
python3 scripts/ne_shape.py
# ② interp 가드가 실데이터에서 켜지는가 (L0-7) — 각 수 초. 에러가 나면 그 자체가 발견이다
python3 -m bms_balancing.verify eval --state 100 --si-source Li
BMS_DATA_ROOT=~/dd/cells/c168 python3 -m bms_balancing.verify eval --state 100 --si-source Li
BMS_DATA_ROOT=~/dd/cells/c171 python3 -m bms_balancing.verify eval --state 100 --si-source Li
BMS_DATA_ROOT=~/dd/cells/pouch_fixedhc python3 -m bms_balancing.verify eval --state 100 --si-source Li
git add out/ne_shape_GITT_Li.csv* && git commit -m "ne_shape 재실행 — PE 축 변화량 추가" && git push
```
그 결과로 §1-12 조건 7 을 채우고(PE 강도), 가드가 켜졌으면 원통형 산출을 재검토한다.

## 닫힌 것

| | 어디 | 한 줄 |
|---|---|---|
| 포팅 forward model | §1-0 · §1-8 | MATLAB↔Python 192 값, 최대 4.04e-12 |
| 툴박스 vs 우리 shim | §1-7 | `rmse_dqdv` 1.78e-12 — `sgolayfilt` 에서 생겨 dQ/dV 가 증폭 |
| 최적화 절차 | §1-9 | 자유 조합 최대 0.17 %p. 갈린 두 점에서 이긴 건 **그들** |
| 97 행 원표 | §2 · §2-1 | `out/bms97/` 커밋. 음수 LAM 이 경계 산물이라는 것을 **산술로** |
| 상태 일반화 | §1-10 | 파우치 네 상태에서 LAM_NE 최광 · LLI 최협 (4/4). **절대 폭으로 말할 때만** |
| **셀 일반화** | **§1-12** | **넘어가지 않는다** — 기술적 결과만. 원통형 LLI 하한 폭이 raw 로 max/max 10.5 배; 파우치 PE 고정 실험은 그 폭을 만들지 않았으나 LAM_PE 에서는 원통형 패턴을 재현 (R2 정정). 외곽 범위는 원통형에서 LAM_PE 분리·LAM_NE·LLI 겹침 (공유 가능값 미확정). 잔차 증가는 관측, 원인 미확정 (R3-01) |
| 문서↔산출 정합 | `cb23dbf` | 여섯 문서 중 넷이 뒤처져 있었다. drift 테스트 둘로 고정 |

## 열려 있는 것 (셀 말고)

- ~~dQ/dV 항의 로컬 함수 둘은 전사다 … 규진팀이 눈으로 맞춰 주면 닫힌다~~ → **닫힘**
  (U1, §1-13): 사용자가 원본을 직접 열어 네 로컬 함수 전부를 줄 단위로 댔다 — 일치
  (lower_half_mean 은 빈-표본 가드만 다름).
- **pOCV 가 원자료인지 필터본인지 모른다** (U2). 한 곡선으로는 원리적으로 못 가른다
  (§`verify noise`). 두 해석을 다 적어 뒀다. 이제 원자료를 우리가 갖고 있으므로 워크북의
  간격 균일성 검사로 닫을 수 있다 (사용자 기계, 선택).
- **γ 직접 적합(표현력)·공유 가능값 증인** (U9) — 미구현. 새 모델 요구서의 구분 시험 항목.
- **held-out 예측 없음.** 다른 셀의 **독립** 반쪽전지가 있어야 한다.
- **`CODEX_REVIEW_REQUEST.md` 2차 판을 아직 안 썼다.** 1차 판은 배너로
  인용 금지를 박아 뒀고 상한 자리마다 `→` 갱신을 달았다. 셀 축이 닫히면 새로 쓴다.

## 기계 쪽 사실 (잊기 쉬운 것)

- 작업본은 **`~/dd/bms-balancing`** (브랜치 `claude/bms-alpha-beta-verify`).
  `~/bms/bms-balancing` 은 본체 브랜치 체크아웃이니 **건드리지 않는다.**
- `BMS_DATA_ROOT='/mnt/d/가형 관련/degradation mode'` — 원자료는 저장소에 안 넣는다.
- MATLAB 은 `cd 'D:\가형 관련\degradation mode'` → `addpath('dd_shims','-end')`
  → `dd_verify('check')`. `-end` 없으면 진짜 툴박스 함수까지 가린다.
- 툴박스는 2026-09-10 에 전부 깔렸다. "없어서 못 한다" 는 더 이상 사유가 아니다.
- ⚠ **그 기계의 clone 루트는 `~/dd` 다.** 그래서 `~/dd/cells/` 가 **저장소 안**에
  있고, 그 안에는 규진팀 원자료 xlsx 사본이 들어간다. 저장소는 public 이다.
  `.git/info/exclude` 에 `cells/` 를 넣어 막아 뒀지만 그건 그 clone 에만
  적용된다. 루트 `.gitignore` 는 본체 소유라 못 고쳤고 `HANDOFF_TO_GATE.md`
  §2b 에 신고했다. **루트에서 `git add -A` 를 치지 않는다.**
