# bms-balancing — α·β 검증 하네스

규진팀 MATLAB electrode balancing (Si/Gr 블렌드, 5-파라미터
`[a_PE, b_PE, a_NE, b_NE, γ_Si]`) 이 내는 답이 **데이터로 정해지는 값인지**를
재기 위한 도구. 2026-09-10 에 받은 코드·데이터·결과를 대상으로 만들었다.

## 이 디렉터리가 하는 일과 안 하는 일

- **한다**: 그들 forward model 을 **고치지 않고** Python 으로 옮기고
  (`model.py`), 그 위에서 경계·축퇴·모델 선택 감도·비결정성을 잰다
  (`verify.py`).
- **안 한다**: 모델을 개선하지 않는다. 고쳐서 옮기면 "그들의 답"이 아니라
  "우리 답"을 재게 된다. 고칠 자리는 재고 나서 따로 제안한다.

## 경계 (중요)

- **RUN_SCOPE 밖이다.** `degradation-degeneracy` 의 `source_digest` 는
  `src/ tools/ configs/ scripts/ run.sh requirements*.txt` 만 본다. 이
  디렉터리는 그 밖이므로 게이트 리뷰 대상 코드 identity 를 안 건드린다.
- **원자료는 저장소에 넣지 않는다.** 반쪽전지·풀셀 xlsx, 문헌 OCP 는 규진팀
  것이다. 경로를 밖에서 받는다:

  ```bash
  export BMS_DATA_ROOT=/…/electrode_balancing_blend
  python -m bms_balancing.verify port --state pristine --si-source Li
  ```

## MATLAB 쪽

`matlab/` 에 사용자 기계에서 돌릴 것이 있다. 그 기계에는 **툴박스가 하나도
없어서**(기본 MATLAB 뿐) 규진팀 `main_blend_final.m` 이 그대로는 안 돈다 —
우회로와 절차는 `matlab/README.md`.

`matlab/tests/` 는 그 MATLAB 파일들을 GNU Octave 8.4 로 **실제 실행해 본**
검사다 (`matlab/tests/run_all.sh`). 무엇이 닫혔고 무엇이 아직 열려 있는지는
`matlab/tests/README.md` 에 표로 적혀 있다.

## 명령

| 명령 | 무엇을 묻나 |
|---|---|
| `port` | **포팅이 그들 모델인가** — 보고된 파라미터가 우리 목적함수의 최적점 근처인가 |
| `eval` | 같은 질문의 **툴박스 없는 길** — 적합 없이 주어진 p 에서 rmse 만. `--compare` 로 `matlab/dd_eval.m` 산출과 대조하고 갈린 단계를 짚는다 |
| `degeneracy` | 최적 목적함수의 (1+ε) 안에 드는 답들이 만드는 LAM/LLI 폭 |
| `matrix` | 문헌 Si 소스 8 × 반쪽전지 소스 2 × dQ/dV 포함 2 — **모델 선택**이 답을 얼마나 움직이나 |
| `profile` | γ_Si 를 고정하고 나머지 넷을 재적합 — γ ↔ a_NE 축퇴 |
| `scale-noise` | 목적함수 scale 의 난수 seed 가 답을 얼마나 흔드나 |

## 측정된 것 (2026-09-10, 요지)

정본은 `FINDINGS.md` 와 `out/` 의 실행 산출이다. 여기 적은 것은 사본이다.

1. **포팅 충실도 확인됨** — pristine·GITT·Si=Li 에서 그들 보고값과 우리 독립
   재적합이 파라미터 소수 셋째 자리, 목적함수 다섯째 자리까지 일치.
2. **모델을 고정하면 답은 좁다** — 최적의 1 % 안에서 LAM_NE 폭 0.87 %p.
3. **모델 선택이 답을 정한다** — 문헌 Si 소스만 8 가지로 바꾸면 LAM_NE 폭
   8.93 %p, LLI 폭 1.02 %p.
4. **γ_Si 가 LAM_NE 를 정한다** — 원전(Schmitt 2022)이 "좋은 재구성" 이라 부른
   pOCV RMSE 12 mV 문턱 안에서 LAM_NE 는 −4.38 % ~ +13.00 % (17.4 %p),
   같은 조건에서 LLI 는 1.14 %p.
