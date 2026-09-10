# MATLAB 쪽에서 돌릴 것 — 명령어

`dd_verify.m` 을 **규진팀 프로젝트 루트**(`electrode_balancing_blend.m` 이 있는
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
├── dd_verify.m                  ← 이 파일을 여기에 복사
└── data/
    ├── half_cell/{GITT,step_005C}/
    ├── full_cell/large_cell_033C/
    └── literature/{Si_Gr_literature_OCP.xlsx, Si_OCP_sources/*.csv}
```

`main_blend_final.m` 첫머리의 `cd('C:\Users\ga117\...')` 는 **지우거나 주석
처리**해야 한다 (수정 제안 #7). `dd_verify.m` 은 `cd` 를 안 한다 — 현재
폴더 기준으로 상대경로만 쓴다.

## 필요한 툴박스

`fmincon` · `MultiStart` (Optimization Toolbox + Global Optimization Toolbox),
`sgolayfilt` · `findpeaks` (Signal Processing Toolbox). 없으면 그 자리에서
에러가 난다 — 조용히 다른 답을 내지 않는다.

## 1. 포팅 대조 (가장 먼저, 제일 중요)

우리 Python 포팅이 **그들 모델을 옮긴 게 맞는지**를 MATLAB 에서 다시 찍는다.
이게 틀리면 우리가 낸 축퇴 숫자가 전부 무의미하다.

```matlab
dd_verify('dump', 'State','300_0009', 'WDqdv',0, 'Out','dd_dump_gitt_w0.csv')
```

또는 셸에서 (headless):

```bash
# Linux / macOS
matlab -batch "dd_verify('dump','State','300_0009','WDqdv',0,'Out','dd_dump_gitt_w0.csv')"
```

```powershell
# Windows PowerShell
matlab -batch "dd_verify('dump','State','300_0009','WDqdv',0,'Out','dd_dump_gitt_w0.csv')"
```

문헌 Si 소스 8개를 돌면서 한 줄씩 찍는다 (약 8×2회 적합).
**대조표** — 우리 Python 이 같은 조건에서 낸 값 (`bms-balancing/out/matrix_300_0009.csv`):

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

**차이가 1 %p 안쪽이면** 포팅이 맞다고 본다. 그보다 크게 갈리는 소스가 있으면
그 자리가 발견이다 (특히 `sgolayfilt` 가장자리 처리와 `quantile` 정의가
다를 수 있는 자리).

## 2. γ_Si 프로파일 — LAM_NE 의 실질 오차막대

γ 를 고정하고 나머지 넷을 다시 적합한다. 이게 **원전(Schmitt 2022)이
"같은 서명을 남긴다"고 적어 놓고 재지 않은** 그 자리다.

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
(원전이 "좋은 재구성"이라 부른 문턱) 안에서 LAM_NE 가 몇 %p 를 훑는가.

## 3. 목적함수의 난수 의존 (수정 제안 #4 를 눈으로)

```matlab
dd_verify('scalenoise', 'State','300_0009', 'Out','dd_scalenoise.csv')
```

seed 만 바꿔 같은 적합을 5번 한다. `electrode_balancing_blend.m` 은 목적함수
scale 을 `rand` 50개로 잡는데 **seed 가 없다.** 결과가 seed 마다 다르면
"같은 데이터·같은 설정으로 두 번 돌리면 답이 다르다" 가 실물로 확인된다.

> 주의: `dd_verify` 는 비교를 위해 매 적합 앞에 `rng(0,'twister')` 를 건다.
> `main_blend_final.m` 은 안 건다 — 그것이 발견 #4 다.

## 4. 반쪽전지 소스를 바꿔서

```matlab
dd_verify('dump', 'HalfCellDir','data/half_cell/step_005C/', ...
          'State','300_0009', 'WDqdv',0, 'Out','dd_dump_005c_w0.csv')
dd_verify('dump', 'State','300_0009', 'WDqdv',1, 'Out','dd_dump_gitt_w1.csv')
```

## 5. 결과를 보내는 법

위 CSV 들을 그대로 넘겨주면 우리 Python 표와 자동으로 대조한다. 파일 4개면
충분하다: `dd_dump_gitt_w0.csv` · `dd_dump_gitt_w1.csv` ·
`dd_dump_005c_w0.csv` · `dd_profile_Li.csv`.

## 참고 — 소요 시간

한 번의 적합이 MultiStart 20회 + 사전 적합 10회다. 이 데이터에서 조합당 수십
초~수 분 걸린다. `dump` 는 16회 적합, `profile` 은 21회 적합이므로 각각
십수 분~한 시간을 잡아 두면 된다.
