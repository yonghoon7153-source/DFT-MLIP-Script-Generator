# 진행 상태 — α·β 검증 하네스

> **이 파일이 "지금 어디까지 왔나" 의 정본이다.** 대화 요약이나 기억이 아니라
> 여기를 본다. 수치의 정본은 여전히 `FINDINGS.md` + `out/` 산출물이다.
>
> 갱신 규칙: 단계가 열리거나 닫히면 **그 커밋에서 같이** 고친다.

최종 순서: **남은 것 끝내기 → Codex 적대 리뷰 → 규진팀에 `FOR_BMS_TEAM.md` 전달**

---

## 지금 막혀 있는 것 — 하나뿐이다

**셀 일반화 (§1-12).** 원통형 셀 둘(#168 · #171)의 띠가 파우치보다 넓게
나왔는데, 그 셀들은 반쪽전지를 한 번만 재서 `scripts/prepare_cell.py` 가
같은 파일을 네 상태에 복사했다. `c_lit = (a_PE + b_PE − b_NE)·c` 라 그
대체가 **LAM_PE 와 LLI 양쪽에** 들어간다 (LAM_NE 만 절연 —
`tests/test_review_findings.py::test_half_cell_substitution_reaches_lli_not_just_lam_pe`).

그래서 **셀 차이인지 우리 대체 탓인지 아직 못 가른다.**

가르는 대조 실험: 파우치를 pristine 반쪽전지 하나로 고정해 재실행
(`~/dd/cells/pouch_fixedhc`, 2026-09-11 새벽 완주, 산출 9개).
파우치 원본 대비 띠가 원통형만큼 벌어지면 원인은 **대체**이고, 안 벌어지면
**셀 차이**가 남는다.

### 다음에 칠 명령 (사용자 기계, `~/dd/bms-balancing`)

```bash
cd ~/dd/bms-balancing
git pull --rebase origin claude/bms-alpha-beta-verify
git push  -u origin claude/bms-alpha-beta-verify     # ← 1d671ce(원통형 산출)가 아직 원격에 없다
source .venv/bin/activate
export BMS_DATA_ROOT='/mnt/d/가형 관련/degradation mode'

# ① 대조가 정말 대조였는지 — 해시로. 둘 다 돌려야 판정기가 살아 있다는 증거가 된다
python3 scripts/fixed_hc.py check --root ~/dd/cells/pouch_fixedhc --expect fixed
python3 scripts/fixed_hc.py check --root "$BMS_DATA_ROOT"        --expect per-state

# ② 네 갈래 비교
python3 scripts/compare_states.py \
    pouch=out fixedhc=~/dd/cells/pouch_fixedhc/out \
    c168=~/dd/cells/c168/out c171=~/dd/cells/c171/out
```

①이 기대와 다르면 **어젯밤 실행은 대조가 아니다** — `fixed_hc.py make` 로
다시 만들어 `run_states.sh` 를 다시 돌려야 한다.

---

## 닫힌 것

| | 어디 | 한 줄 |
|---|---|---|
| 포팅 forward model | §1-0 · §1-8 | MATLAB↔Python 192 값, 최대 4.04e-12 |
| 툴박스 vs 우리 shim | §1-7 | `rmse_dqdv` 1.78e-12 — `sgolayfilt` 에서 생겨 dQ/dV 가 증폭 |
| 최적화 절차 | §1-9 | 자유 조합 최대 0.17 %p. 갈린 두 점에서 이긴 건 **그들** |
| 97 행 원표 | §2 · §2-1 | `out/bms97/` 커밋. 음수 LAM 이 경계 산물이라는 것을 **산술로** |
| 상태 일반화 | §1-10 | 파우치 네 상태에서 LAM_NE 최광 · LLI 최협 (4/4). **절대 폭으로 말할 때만** |
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
