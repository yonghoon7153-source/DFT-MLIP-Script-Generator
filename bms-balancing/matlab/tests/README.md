# `tests/` — MATLAB 쪽 파일을 **실제로 돌려 본** 검사

    ./run_all.sh            # 전부 (Octave 가 있으면 5종, 없으면 Python 2종)

2026-09-10 이전까지 `dd_eval.m` · `dd_verify.m` · `dd_shims/` 는 **한 번도
실행된 적이 없었다.** 블록 균형만 프로그램으로 셌을 뿐이고, 사용자 기계에서
`dd_verify('check')` 가 돈 것이 유일한 실행 증거였다. 그 상태로 사용자에게
`dd_eval` 을 돌리게 하면 구문 오류 하나에 왕복 한 번이 날아간다.

이 디렉터리는 그 왕복을 여기서 미리 태우기 위한 것이다. `apt-get install
octave` 로 GNU Octave 8.4 를 넣고, 규진팀 함수 자리에 합성 대역품을 끼워
`dd_eval.m` 을 끝까지 돌린다.

## 무엇을 증명하나 / 무엇을 증명 못 하나

**증명한다** (2026-09-10 실측, `run_all.sh` 재현 가능)

| # | 검사 | 결과 |
|---|---|---|
| 1 | 구문 — Octave 파서가 네 파일을 읽는가 | `dd_eval.m` · `dd_verify.m` · shim 둘 전부 통과 |
| 2 | `quantile` shim ≡ Python `matlab_quantile` | 88 케이스, 최대 \|Δ\| **0.000e+00** |
| 2 | `quantile` shim ≡ Octave 내장 `quantile`(method 5) | 최대 \|Δ\| **8.9e-16** |
| 2 | `sgolayfilt` shim ≡ Python `sgolay`(scipy, `mode='interp'`) | 8 케이스, 최대 \|Δ\| **5.9e-13**, 가장자리 **4.4e-15** |
| 3 | `dd_eval.m` 배관 ≡ Python 전사본 | 7 조합, 앵커 10 + 파라미터 8행, 최대 상대차 **2.1e-16** |
| 4 | `--compare` 이분 판정이 갈린 단계를 짚는가 | 앵커 10개를 하나씩 어긋뜨려 전부 올바른 단계 지목 |
| 5 | Python `verify eval` 배관 | 5 상태 × 2 반쪽전지 소스 × 8 Si 소스 전부 적재 |

②의 Octave 내장 `quantile` 일치가 중요하다. Octave 의 method 5 는 MATLAB 의
정의((i−0.5)/n plotting position)와 같으므로, 이건 **제3자 구현에 대한 확인**
이지 우리끼리의 자기일관성이 아니다.

②의 `sgolayfilt` 가장자리 일치는 `model.py` 가 `# ≠MATLAB` 으로 표시해 두고
"완전히 같은 수는 아닐 수 있다" 고 적어 둔 바로 그 자리를 닫는다 — **shim 과
scipy 사이에서는** 닫힌다.

**증명 못 한다 — 이건 계속 열려 있다**

- **MATLAB 이 이 파일들을 돌리는가.** 잰 것은 Octave 8.4 다. Octave 파서가
  통과시키고 MATLAB 이 거부하는 구문이 있을 수 있다 (반대도).
- **MathWorks 의 진짜 `sgolayfilt`·`quantile` 과 같은가.** 이 컨테이너에도
  사용자 기계에도 Signal Processing Toolbox 가 없다. 다만 사용자 기계에서
  `sgolayfilt` 는 **항상 우리 shim** 이므로, 그쪽 MATLAB↔Python 대조는 이
  자리에서만큼은 같은 정의끼리 비교하는 것이 맞다.
- **규진팀 모델이 맞는가.** ③은 그들 함수 자리에 **합성 대역품**을 끼운다
  (`synth/README_SYNTH.md`). 재는 것은 배관(인덱싱·마스크·파라미터 변환·
  RMSE 식)이지 모델이 아니다.
- **MATLAB `pchip`/`interp1` 이 scipy 와 같은 수를 내는가.** ③은 그 자리를
  일부러 우회한다. 이건 사용자 기계의 실제 실행으로만 알 수 있고, 그것이
  `dd_eval` → `verify eval --compare` 절차가 존재하는 이유다.

## 파일

| 파일 | 무엇 |
|---|---|
| `run_all.sh` | 전부 실행. Octave 없으면 4·5만 |
| `gen_shim_cases.py` · `run_shims.m` · `check_shims.py` | ② shim 3자 대조 |
| `gen_synth_data.py` · `synth/` · `oct_stubs/` · `mirror_dd_eval.py` · `check_e2e.py` · `run_e2e.sh` | ③ 배관 e2e |
| `test_compare_bisect.py` | ④ 이분 판정 |
| `gen_synth_xlsx.py` · `test_py_smoke.py` | ⑤ Python 스모크 |

### `oct_stubs/` 와 `dd_shims/` 는 목적이 다르다 — 헷갈리면 안 된다

| | `matlab/dd_shims/` | `matlab/tests/oct_stubs/` |
|---|---|---|
| 어디서 쓰나 | **사용자 기계 (MATLAB)** | **이 컨테이너 (Octave)만** |
| 왜 | 툴박스가 없어서 `sgolayfilt`·`quantile` 이 없다 | Octave 에 `contains`·`readmatrix`·`readtable` 이 없다 |
| 사용자 폴더에 복사? | **한다** (`addpath('dd_shims')`) | **절대 안 한다** — MATLAB 엔 원래 있고, 복사하면 내장함수를 가린다 |

## 알려진 차이 — 1 ULP

③에서 `dq_hi` 가 Octave `4.1435370741482966` vs numpy `4.1435370741482958`
로 갈린다 (상대차 2.1e-16). `linspace` 의 마지막 자리 반올림 차이이고 배관
버그가 아니다. 그래서 `check_e2e.py` 는 바이트가 아니라 **상대오차 1e-12** 로
본다.

이 잡음이 분위수 창 마스크를 흔들 수 있나 — **없다.** `differential` 은
`capacity_uniform2` 를 항상 `linspace(…, 500)` 으로 만들고 `quantile` 은 **그
격자 자신**의 분위수다. p=0.05·0.15·0.85·0.95 에서 `p·500` 이 정수라 경계는
언제나 격자점 **정확히 중간**에 떨어진다 (여유 = 격자간격의 0.5배 ≈ 1e-3
상대). 데이터와 무관한 기하학이고, 1e-16 잡음과는 13자리 차이다.
실측: 모든 e2e 조합에서 `dv_n` = 350 으로 동일.
