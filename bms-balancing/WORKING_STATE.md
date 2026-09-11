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

## 지금 상태 — **Codex R5 = NO-GO (P1 7 · P2 4). `reviews/R5_LEDGER.md` 가 작업 원장이다**

2026-09-11 Codex 5차 리뷰(대상 `0cb7b7a`, `reviews/R5_CODEX.md`) 열한 건을 우리 트리에서 **전부 재현**했다
(`reviews/r5_repros/replay_ours_0cb7b7a.json` — 11 단계 rc 가 Codex 와 같다). 반박 성립 없음. 코드 아홉
(R5-01~05 · 07 · 08 · 10 · 11)·문서 둘(R5-06 동치 조건, R5-09 U12 범위)을 RED → 수정 → GREEN 으로 닫았다.
R4 에서 Codex 가 종결로 인정한 것: R4-01·03·S-02, R4-02/04/05/06/07 의 원래 반례.

**U13 실측 완료** (사용자 기계, a78f0a5): 18 build 전부 유한 · 예외 0 · eps_rel ≤ 1.7e-15 · `equiv=1`
(`out/scale_audit_eval_u13.txt`). §1-13 은 recompare 4 조합이 그 조건 안이라고 적었다. 루트 이름은 그 판
줄에 없어 보고 순서 — 다음 판부터 `root=` 가 붙는다.
남은 것: `reviews/R6_REQUEST.md` 를 Codex 에 보낸다 (대상 = 그 파일이 든 커밋). 아래 명령은 실행 기록.

```bash
cd ~/dd/bms-balancing && git pull --rebase origin claude/bms-alpha-beta-verify
source .venv/bin/activate && export BMS_DATA_ROOT='/mnt/d/가형 관련/degradation mode'
python3 -m pytest tests/ -q                       # 107 passed 기대
# U13: 새 감사 줄(식별자·eps_rel·동치 flag 포함) — GITT·Li 16 build + Kunz·step_005C 조합. `# scale_audit` 줄만 붙여 주면 된다
for st in pristine 100 200 300_0009; do python3 -m bms_balancing.verify eval --state $st --si-source Li | grep scale_audit; done
for c in c168 c171 pouch_fixedhc; do for st in pristine 100 200 300_0009; do BMS_DATA_ROOT=~/dd/cells/$c python3 -m bms_balancing.verify eval --state $st --si-source Li | grep scale_audit; done; done
python3 -m bms_balancing.verify eval --state pristine --si-source Kunz | grep scale_audit
python3 -m bms_balancing.verify eval --state pristine --source step_005C --si-source Li | grep scale_audit
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
