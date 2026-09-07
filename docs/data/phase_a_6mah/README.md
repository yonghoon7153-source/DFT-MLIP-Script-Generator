# Phase A 침대 — 6 mAh · P:S 7:3 (2026-09-07 봉인)

사전등록 `docs/reviews/phase_a_6mah_order_prereg_20260907.md` 의 **정본 침대**.
원장 = `claims.json` CL-78 (갱신판).

## 출처 — 사용자 제공 DEM 산출물 (2026-09-07)

```
atom_2850000.liggghts   sha256 a202b19f6ca9eb80c66434554dc7bb1ac7f3fbfaec6181f5fef103e9c8c10104
in.real_4.liggghts      sha256 900ae9c8f1fde02e83ac86dcee7cca55a10df9ac73e59f15a1ae1516903bfda7
mesh_2850000.stl        sha256 989c3e6426c6a06766aef193f4bd081e1c8c22ce15d3154da0ae513015d2ada9
```

덱(`in.real_4.liggghts`)만 여기 커밋했다.  덤프(21 MB)와 메시는 리포에 넣지 않았다 —
**SHA 로 봉인**하고 스캐폴드만 커밋한다.

## ⚠ 이것은 옛 캠페인 침대가 **아니다** — 같은 설계점의 새 realization 이다

옛 `input_6mAh_real_4` (case `260421_215212_f0b6df`) 의 `atoms.csv` 는 **2026-08-25 윈도우
재설치로 소실**됐다 (`webapp/results/…` 에 요약과 `full_metrics.json` 만 남았고 원자 좌표는
기계 전체에 0 개).  그래서 **잃은 침대를 쫓지 않고 이 침대를 정본으로 삼는다** — 덤프·덱·메시가
다 있어 **봉인이 성립하는** 유일한 침대이기 때문이다.

★ 그런데 **조성은 사실상 같다**.  실측 총량으로 옛 캠페인의 첨가제 객체 수를 다시 계산하면:

```
VGCF 0.5 wt%   계산 13,280  vs 실측 13,281   −0.01 %
VGCF 1.0       계산 26,695  vs 실측 26,696   −0.00 %
VGCF 2.0       계산 53,934  vs 실측 53,529   +0.76 %
VGCF 4.0       계산 110,116 vs 실측 110,120  −0.00 %
```

⇒ 넷 중 셋이 **네 자리까지 일치**한다.  (⚠ 옛 `case_master.csv` 요약치 — SE 121,332 ·
SE/solid 33.23 vol% — 로 계산하면 **0.58 % 계통 편차**가 났다.  즉 그 요약치 쪽이 부정확했고,
이 실측 침대가 옛 캠페인을 **더 잘** 재현한다.)

## 실측 침대 상수 (덤프에서 직접 — 가정 없음)

```
AM_P     126 개   R = 6.0 µm        ← 덱 `variable r_AM_P equal 6.0e-3`
AM_S   1,372 개   R = 2.0 µm
SE   158,688 개   R = 0.5 µm        (킷 생성기 산출 = run_mpm.sh 가 먹는 그것)
상자   50 × 50 × 113.419 µm         (plate = mesh STL 의 z)
V_AM 159,978 µm³ · S_AM 125,965 µm² · V_SE 83,069 µm³
porosity 14.321 %                   ← 옛 기록 14.28 % 와 일치
SE/solid 34.18 vol%   ·   p_frac 71.26 %
```

⚠ **단위 규약**: CSV 1 단위 = 1000 µm (덱의 `Scale: r×1000`).  스캐폴드 열은
`type,x,y,z,r` 이고 `type` 은 1=AM_P · 2=AM_S · 3=SE (덱 §3 과 같다).

⚠ **정본은 킷 생성기 산출이다** (`mpm_input_from_case.py`) — `run_mpm.sh` 가 먹는 바로 그
파일이라 여기서 갈라지면 런과 지표가 어긋난다.  초판에서 내가 따로 필터한 158,651 판은
폐기했다 (z 가 상자 밖인 37 개를 뺀 것; 좌표는 같고 쓰기 정밀도만 0.87 nm 달랐다).
두 판의 지표 차이는 무시할 만하다: p05 0.4003→0.3999 · d_h 0.9810→0.9821 · K_required 8 불변.

## 산출물

| 파일 | 내용 |
|---|---|
| `am_scaffold.csv.gz` | AM 1,498 (126 + 1,372) |
| `kits/<recipe>/` | **킷 5개** — `run_mpm.sh` · `mpm_input.json` · `harvest.sh`.  스캐폴드는 공유(위 두 `.gz`)라 킷마다 안 넣었다 |
| `se_scaffold.csv.gz` | SE 158,688 — gzip (6.2 → 1.5 MB).  각도·사전계산 도구는 `.gz` 를 그대로 읽는다 |
| `in.real_4.liggghts` | DEM 덱 (봉인) |
| `precompute.json` | `d_h/dx` 게이트 + 첨가제 객체 수 (실측 경로) |
| `angular_risk.json` | STEP4 각도 위험 5종 |

## 킷 쓰는 법 — ⚠ **부모 폴더에 `scripts/` 가 있어야 한다**

`run_mpm.sh` 는 `$KIT/scripts` 또는 **`$KIT/../scripts`** 에서만 레포를 찾는다 (스크립트 §경로 자립).
아무 데나 풀면 `ABORT — scripts/ 를 못 찾음` 으로 **멈춘다** (실제로 걸렸다, 2026-09-07).

```bash
mkdir -p ~/pa/kits && ln -sfn ~/Yonghoon-DEM-DFT/scripts ~/pa/kits/scripts
#   그 다음 킷들을 ~/pa/kits/<recipe>/ 로 풀고 스캐폴드 두 개를 각 킷에 gunzip
source ~/dem-venv/bin/activate          # ⚠ kgy 는 이것 — 아래 참조
cd ~/pa/kits/VGCF_PTFE_1_1 && bash run_mpm.sh
```

### ⚠⚠ kgy 환경 — `~/dem-venv` 를 **명시적으로** 켜야 한다 (2026-09-07 실측)

킷의 venv 자동탐지는 `$SCR/../venv` 를 먼저 잡는데 그건 **kgy 에서 안 돈다**:

```
kgy glibc                          2.31
~/Yonghoon-DEM-DFT/venv (py 3.13)  taichi 휠이 GLIBC_2.32 요구 → ImportError
~/dem-venv              (py 3.8)   taichi 1.7.0  ✓ ← 이것이 작동 환경
GPU                                RTX 3090 · 24 GB
```

⇒ `source ~/dem-venv/bin/activate` 를 **먼저** 하면 `VIRTUAL_ENV` 가 설정돼 자동탐지가
건너뛴다.  ⚠ **`dem-venv` 에 pip install 금지** (CLAUDE.md).

### ⚠ `--gpu-mem` — 기본 28 은 24 GB 카드에서 실패한다

생성기가 `--gpu-mem 28` 을 **하드코딩**하고 있었다 (V100 32 GB 가정).  2026-09-07 에
`--gpu-mem` 플래그로 빼고 이 킷들은 **20** 으로 구웠다 (3090 24 GB 기준, 4 GB 여유).
다른 카드로 옮기면 재생성할 것: `mpm_input_from_case.py --gpu-mem <GB>`.

⚠ 심링크로 걸면 bash 가 `$SCR/..` 를 **논리 경로**로 읽어 `.git` 을 못 본다 →
스크립트가 `git pull --ff-only` 를 건너뛴다 (*"⚠ git pull 스킵"*).  **무해하다** — 다만
scripts 최신화가 자동으로 안 되니 런 전에 레포를 직접 pull 할 것.

★ `run_mpm.sh` 는 **스스로 detach** 한다 (SSH 끊겨도 산다).  실행하면 `RUN_DIR` 과
`tail -f …/mpm_run.log` 명령을 찍고 즉시 빠져나온다.  완료 마커 = `latest_run/mpm_done.marker`.

## 판정 요약

**① `d_h/dx` 게이트 = 통과** (실측): `d_h = 0.9821 µm` · φ_SE_local 0.6716 ·
**최소 통과 n_grid = 179** ⇒ 킷 격자 256 에서 **5.02**.  STEP2 결과에 하한 라벨 불필요.
⚠⚠ 이것은 **MPM SE 응력** 게이트다 — STEP3 σ 격자와 다른 질문이고, 거기선 SE neck 이
`h = 0.20 · 0.25` 에서 85.6 % · 97.4 % 미해상이다 (CL-72).  **두 게이트가 반대 방향이다.**

**② 첨가제 객체 수** (VGCF w + PTFE 1 wt%):

| 레시피 | VGCF n | PTFE n | VGCF vol% | AM wt% | SE wt% |
|---|---|---|---|---|---|
| VGCF 1 + PTFE 1 | 26,968 | 2,206 | 1.961 | 80.57 | 17.43 |
| VGCF 2 + PTFE 1 | 54,490 | 2,229 | 3.962 | 79.75 | 17.25 |
| VGCF 3 + PTFE 1 | 82,587 | 2,252 | 6.005 | 78.92 | 17.08 |
| VGCF 4 + PTFE 1 | 111,279 | 2,276 | 8.090 | 78.10 | 16.90 |

⚠ PTFE 는 1 wt% 고정인데 개수가 3.2 % 는다 — wt% 는 **AM+SE+첨가제 전체**의 몫이라 VGCF 가
늘면 총질량도 늘기 때문이다.  *"PTFE 고정"* 은 **wt% 고정이지 개수 고정이 아니다.**

**③ 각도 위험 = 낮다** (CL-73 의 STEP4 HOLD 에 대한 선별):

```
cov  p01 0.3254 · p05 0.3999 · 중앙 0.5770 · zero fraction 0.00 %
H    p95 112.5 · p99 141.4 · 무한(c=0) 0 개
A_eff/A_geo (전류가중) 0.5544
dipole 중앙 0.095 · 유효 활성섹터 중앙 41.3 (48 기준)

z-bin   collector 0.5915  →  mid 0.5720  →  separator 0.5700
★ K_required = 8      (사전등록 규칙 K · cov_p05 ≥ 3)
```

- **미접촉 입자 0 개** ⇒ 최악 실패 모드는 실현되지 않는다.
- **`K = 8`** ⇒ Codex 사다리 `{1, 12, 48}` 의 **최저단 12 로 이미 충분**하다.
- ★★ **z 기울기가 없다** (0.5915 → 0.5700).  113 µm 두꺼운 침대인데도 평평하다 ⇒
  *"두꺼울수록 각도 오차가 커진다"* 는 가설이 **또 반증**됐다 (CL-73 · CL-76 에 이어 세 번째).
  ⚠ 참고로 real14(28.8 µm)는 기울기가 강했다 (0.576 → 0.336) — **얇은 쪽이 나빴다.**

⛔ **이 선별은 STEP4 를 대신하지 않는다.**  최종 허용 게이트는 *"조성 간
`q_frac_at_cutoff` < 1 %p **이고** 동일 SOC 전압차 < 5 mV"* 이고 실제 런이 필요하다.
`H` 절대값은 `I_i ∝ V_i` (§F1 가정) 산물이라 **인용 금지** — 순위·분포만 강건하다.
