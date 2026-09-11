# 진행 상태 — α·β 검증 하네스

> **이 파일이 "지금 어디까지 왔나" 의 정본이다.** 대화 요약이나 기억이 아니라
> 여기를 본다. 수치의 정본은 여전히 `FINDINGS.md` + `out/` 산출물이다.
>
> 갱신 규칙: 단계가 열리거나 닫히면 **그 커밋에서 같이** 고친다.

최종 순서: **남은 것 끝내기 → Codex 적대 리뷰 → 규진팀에 `FOR_BMS_TEAM.md` 전달**

---

## 지금 할 것 — **Codex 2차 적대 리뷰 요청문**

막고 있던 셀 일반화가 2026-09-11 에 닫혔다 (§1-12). 우리가 더 닫을 수 있는
미결이 없다 — 남은 것은 전부 규진팀이나 계측 쪽에 있다. 그러므로 다음 단계는
`CODEX_REVIEW_REQUEST.md` **2차 판을 새로 쓰는 것**이다 (1차 판은 배너로
인용 금지를 박아 뒀고, 상한 자리마다 `→` 갱신을 달아 뒀다).

2차 요청문에서 제일 세게 맞아야 할 자리 (스스로 신고할 것):

1. **§1-12 의 대조가 충분히 강했나.** 파우치 상태별 반쪽전지가 서로 다른
   파일이라는 것(해시)만 확인했고 **얼마나 다른지는 원장에 없다.**
   `scripts/ne_shape.py` 를 한 번 돌려 mV 로 적으면 닫힌다 — 이게 우리가
   리뷰 전에 할 수 있는 **유일하게 남은 실측**이다.
2. **"셀 차이" 와 "그 셀 자료의 잡음·분해능" 을 못 갈랐다.** 결론 문장이
   셀 쪽으로 읽히게 쓰여 있지 않은지.
3. 원통형 13 행 중 3 행이 `a_NE=ub` 에 눌려 있다.
4. dQ/dV 항의 로컬 함수 둘은 여전히 **전사**다.

그 뒤 순서: Codex 리뷰 → 반영 → 규진팀에 `FOR_BMS_TEAM.md` 전달.

### 재현 명령 (사용자 기계, `~/dd/bms-balancing`)

```bash
source .venv/bin/activate
export BMS_DATA_ROOT='/mnt/d/가형 관련/degradation mode'

# 네 갈래 비교 (§1-12 의 표가 여기서 나온다)
python3 scripts/compare_states.py \
    pouch=out fixedhc=out/cells_pouch_fixedhc \
    c168=out/cells_c168 c171=out/cells_c171

# 대조 루트가 정말 고정본인지 — 해시로. 둘 다 돌려야 판정기가 살아 있다는 증거
python3 scripts/fixed_hc.py check --root ~/dd/cells/pouch_fixedhc --expect fixed
python3 scripts/fixed_hc.py check --root "$BMS_DATA_ROOT"        --expect per-state

# 남은 실측 하나 — 반쪽전지가 상태 사이에 얼마나 다른가 (위 1번)
python3 scripts/ne_shape.py
```

## 닫힌 것

| | 어디 | 한 줄 |
|---|---|---|
| 포팅 forward model | §1-0 · §1-8 | MATLAB↔Python 192 값, 최대 4.04e-12 |
| 툴박스 vs 우리 shim | §1-7 | `rmse_dqdv` 1.78e-12 — `sgolayfilt` 에서 생겨 dQ/dV 가 증폭 |
| 최적화 절차 | §1-9 | 자유 조합 최대 0.17 %p. 갈린 두 점에서 이긴 건 **그들** |
| 97 행 원표 | §2 · §2-1 | `out/bms97/` 커밋. 음수 LAM 이 경계 산물이라는 것을 **산술로** |
| 상태 일반화 | §1-10 | 파우치 네 상태에서 LAM_NE 최광 · LLI 최협 (4/4). **절대 폭으로 말할 때만** |
| **셀 일반화** | **§1-12** | **넘어가지 않는다.** 대조로 반쪽전지 대체를 배제(이동 0.03~0.20 vs 격차 2.23~5.64 %p). 원통형은 순위가 반대 — LAM_PE 로 사이클을 가르고 LAM_NE·LLI 는 겹친다 |
| 문서↔산출 정합 | `cb23dbf` | 여섯 문서 중 넷이 뒤처져 있었다. drift 테스트 둘로 고정 |

## 열려 있는 것 (셀 말고)

- **dQ/dV 항의 로컬 함수 둘은 전사다.** `compute_dqdv_rmse_blend` ·
  `build_peak_weights_local` 은 `electrode_balancing_blend.m` 안에 있어 밖에서
  못 부른다. 그 항만 「우리 전사 ↔ 우리 포팅」 대조다. 규진팀이 눈으로 한 번
  맞춰 주면 닫힌다 (`FOR_BMS_TEAM.md` §8 에 요청문 있음).
- **pOCV 가 원자료인지 필터본인지 모른다.** 한 곡선으로는 원리적으로 못 가른다
  (§`verify noise`). 두 해석을 다 적어 뒀고, 규진팀 export 하나면 닫힌다.
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
