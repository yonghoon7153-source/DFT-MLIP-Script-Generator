# MATLAB 쪽에서 돌릴 것 — 명령어

이 파일들을 **규진팀 프로젝트 루트**(`electrode_balancing_blend.m` 이 있는
폴더)에 복사해 두고 돌린다. 기존 함수를 고치지 않고 그대로 호출하므로,
여기서 나오는 값은 **그들 파이프라인의 값**이다.

```
degradation mode/                ← 여기가 루트 (여기서 실행)
├── electrode_balancing_blend.m
├── electrode_ocv.m
├── build_blend_functions.m
├── differential.m
├── extractMyData.m
├── averageDuplicates.m
├── dd_verify.m                  ← 복사
├── dd_eval.m                    ← 복사
├── dd_shims/                    ← 폴더째 복사 (sgolayfilt.m · quantile.m)
└── data/
    ├── half_cell/{GITT,step_005C}/
    ├── full_cell/large_cell_033C/
    └── literature/{Si_Gr_literature_OCP.xlsx, Si_OCP_sources/*.csv}
```

`main_blend_final.m` 첫머리의 `cd('C:\Users\ga117\...')` 는 **지우거나 주석
처리**해야 한다 (수정 제안 #7). `dd_verify.m`·`dd_eval.m` 은 `cd` 를 안 한다 —
현재 폴더 기준 상대경로만 쓴다.

---

## 먼저: 이 기계에 툴박스가 없다

사용자 기계(R2026a, Windows) `ver` 실측 — **기본 MATLAB 뿐이다.** 그래서 없는 것:

| 없는 것 | 어디서 필요한가 |
|---|---|
| `fmincon` · `MultiStart` · `createOptimProblem` | 적합 — 규진팀 `electrode_balancing_blend.m` 본체 |
| `sgolayfilt` | 평활 — 그들 `differential.m` |
| `quantile` | 창 자르기 — 그들 `electrode_balancing_blend.m` |
| `findpeaks` | dQ/dV 피크 가중 (`w_dqdv ≠ 0` 일 때만) |

**즉 `main_blend_final.m` 자체가 이 기계에서 안 돈다.** 그래서 길을 둘로 나눴다.

- `dd_shims/` — `sgolayfilt` · `quantile` 을 기본 MATLAB 만으로 다시 쓴 것.
  그들 코드를 **한 줄도 안 고치고** 돌리려는 것이다 (MATLAB 이 경로를 먼저
  보므로 그들 `differential.m` 이 이 파일을 부른다).
  ⚠ MathWorks 구현이 아니다. 그래서 조용히 켜지지 않게 `addpath` 로 **명시적
  으로** 올려야 한다.
- `dd_eval.m` — **적합 없이** 주어진 파라미터에서 목적함수만 찍는다.
  포팅 대조에 정말 필요한 건 최적화기가 아니라 **모델**이기 때문이다:
  같은 p 에서 MATLAB 과 Python 이 같은 RMSE 를 내는지가 핵심이고,
  그건 `fmincon` 없이 잴 수 있다.

`findpeaks` 대체품은 아직 없다. `w_dqdv = 0`(그들 기본 설정)에서는 안 쓰이므로
대조는 그 조건에서 한다.

---

## 0. `check` — 몇 초, 제일 먼저

경로·툴박스·데이터·배관을 한 번에 확인한다. **첫 실패에서 멈추지 않고 전부
세서** 요약을 낸다.

```matlab
cd 'D:\가형 관련\degradation mode'
dd_verify('check')
```

> 이건 사용자 기계에서 이미 정상 실행됐다 (2026-09-10).

찍히는 것: 그들 함수 6개가 경로에 있는가 · 툴박스 함수 5종이 있는가 ·
반쪽전지 상태 파일 개수 · 풀셀 워크북의 상태별 `c_cell` 5개 · 문헌 Si 8종 ·
그리고 실제로 한 번 읽어 `E_PE(0.5) − E_NE(0.5, γ=0.25)` 를 계산한 값.

마지막 값이 **2.5~4.5 V 밖이면** 방향 규약(어느 쪽이 lithiation 인가)이
우리 가정과 다른 것이므로 그 자리부터 봐야 한다.

`c_cell` 다섯 개가 이 값과 다르면 워크북이 우리가 본 것과 다른 판이다:

    pristine 74.671 · 100 71.631 · 200 69.571 · 300_0009 63.720 · 300_0147 67.369

---

## 1. 포팅 대조 — **지금 할 것** (툴박스 불필요)

```matlab
cd 'D:\가형 관련\degradation mode'
addpath('dd_shims')          % ← 반드시. 없으면 dd_eval 이 그 자리에서 멈춘다
dd_eval('State','pristine','SiSource','Li','Out','dd_eval_pristine_Li.csv')
```

수십 초 안에 끝난다 (적합을 안 하므로). 나오는 CSV 는 이렇게 생겼다:

```
# dd_eval  state=pristine  halfcell=data/half_cell/GITT/  Si=Li  w_dqdv=0
# c_cell,74.670999999999999
# dv_lo,0.149298597...
  … 앵커 10개 …
a_PE,b_PE,a_NE,b_NE,gamma_Si,rmse_pocv,rmse_dvdq
1.077218,-0.022949,1.001342,0.000309,0.295099,…,…
  … 8행 …
```

앞머리 `#` 열 개가 **이분(bisection) 앵커**다. 갈렸을 때 어느 단계가 범인인지
좁히는 값들이라 화면뿐 아니라 CSV 에도 같이 적는다 — 화면에만 찍으면 CSV 만
보내 왔을 때 이분할 근거가 사라진다.

**그 CSV 파일 하나만 보내면 된다.** 이쪽에서:

```bash
export BMS_DATA_ROOT=/…/electrode_balancing_blend
python -m bms_balancing.verify eval --state pristine --si-source Li \
       --compare dd_eval_pristine_Li.csv
```

앵커 10개 + rmse 16개를 대조하고, **갈린 첫 앵커의 단계 이름**을 말한다
(예: "`E_NE_0p5_0p25` 에서 처음 갈린다 → 범인 단계는 「문헌 적재 +
build_blend_functions」"). 그 앞 앵커가 맞았으면 그 앞 단계는 용의선상에서 빠진다.

조건을 바꿔 몇 개 더 뽑으면 대조가 튼튼해진다:

```matlab
dd_eval('State','300_0009','SiSource','Li',  'Out','dd_eval_300_Li.csv')
dd_eval('State','pristine', 'SiSource','Kunz','Out','dd_eval_pristine_Kunz.csv')
dd_eval('HalfCellDir','data/half_cell/step_005C/','State','pristine', ...
        'SiSource','Li','Out','dd_eval_pristine_Li_005c.csv')
```

임의의 파라미터를 직접 넣어 볼 수도 있다:

```matlab
dd_eval('P', [1.10 -0.05 1.10 -0.01 0.15; 1.10 -0.05 1.10 -0.01 0.30])
```

---

## 2~4. 적합이 필요한 것들 — **툴박스가 생기면**

아래는 `fmincon` + `MultiStart` 가 있어야 돈다. 지금 기계에서는 그 자리에서
에러가 난다 (조용히 다른 답을 내지는 않는다).

### 2. `dump` — Si 소스 8종 전수 재적합

```matlab
dd_verify('dump', 'State','300_0009', 'WDqdv',0, 'Out','dd_dump_gitt_w0.csv')
```

우리 Python 이 같은 조건에서 낸 값 (`out/matrix_300_0009.csv`):

| Si 소스 | LAM_PE % | LAM_NE % | LLI % | 경계 |
|---|---|---|---|---|
| Baggetto | 7.02 | 14.67 | 16.09 | a_NE=lb, gamma=lb |
| Friedrich | 9.32 | 14.67 | 16.50 | a_NE=lb, gamma=lb |
| Jiang | 6.70 | 6.11 | 15.72 | — |
| Kunz | 7.19 | 6.36 | 15.81 | — |
| Li | 6.36 | 7.90 | 15.70 | — |
| Lu | 6.61 | 8.23 | 15.63 | — |
| Sethuraman | 5.66 | 7.84 | 15.47 | — |
| Wetjen | 7.48 | 15.04 | 15.59 | — |

**차이가 1 %p 안쪽이면** 포팅이 맞다고 본다.

### 3. `profile` — γ_Si 프로파일, LAM_NE 의 실질 오차막대

```matlab
dd_verify('profile', 'State','300_0009', 'SiSource','Li', 'WDqdv',0, ...
          'Gammas',0:0.025:0.5, 'Out','dd_profile_Li.csv')
```

우리 Python 이 낸 값 (같은 조건):

| γ_Si | pOCV RMSE | a_NE | LAM_NE | LLI |
|---|---|---|---|---|
| 0.050 | 9.47 mV | 1.209 | **−3.00 %** | 16.33 % |
| 0.150 | **5.59 mV** | 1.146 | 2.33 % | 15.91 % |
| 0.250 | 8.00 mV | 1.073 | 8.58 % | 15.70 % |
| 0.325 | 11.00 mV | 1.021 | **13.00 %** | 15.29 % |

**보아야 할 것**: `a_NE` 가 γ 와 반대로 움직이는가, 그리고 RMSE 12 mV
(원전 Schmitt 2022 가 "좋은 재구성"이라 부른 문턱) 안에서 LAM_NE 가 몇 %p 를
훑는가.

### 4. `scalenoise` — 목적함수의 난수 의존 (수정 제안 #4 를 눈으로)

```matlab
dd_verify('scalenoise', 'State','300_0009', 'Out','dd_scalenoise.csv')
```

`electrode_balancing_blend.m` 은 목적함수 scale 을 `rand` 50개로 잡는데
**seed 가 없다.** 결과가 seed 마다 다르면 "같은 데이터·같은 설정으로 두 번
돌리면 답이 다르다" 가 실물로 확인된다.

> `dd_verify` 는 비교를 위해 매 적합 앞에 `rng(0,'twister')` 를 건다.
> `main_blend_final.m` 은 안 건다 — 그것이 발견 #4 다.

한 번의 적합이 MultiStart 20회 + 사전 적합 10회다. `dump` 는 16회, `profile`
은 21회 적합이므로 각각 십수 분~한 시간을 잡아 두면 된다.

---

## 이 파일들은 어디까지 검사됐나

`tests/` 에서 GNU Octave 8.4 로 실제 실행해 봤다 (`tests/run_all.sh`).
구문·shim 수치·`dd_eval.m` 배관까지는 통과했고, **MATLAB 자체에서 돈다는
증명은 아니다.** 무엇이 닫혔고 무엇이 열려 있는지는 `tests/README.md`.

에러가 나면 그 텍스트를 그대로 주면 된다 — 그게 제일 빠르다.
