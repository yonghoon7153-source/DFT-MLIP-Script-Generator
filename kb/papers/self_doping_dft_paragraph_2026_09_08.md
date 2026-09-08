---
title: "원고 자가도핑 DFT 문단 — 스핀 하나로 좁힌 5문단 (2·3·6 계열)"
date: 2026-09-08
updated: 2026-09-08
tags: [manuscript, dft, sdcp, self-doping, spin, polaron]
status: 1저자 승인 — 삽입 위치 대기
kind: manuscript-draft
system: sdcp
confidence: high
verificationStatus: verified
verifiedAt: 2026-09-08
verifiedBy: self
explored: false
authoredBy: agent
claimType: descriptive
evidenceScope: multi-source-primary
---

# 원고 자가도핑 DFT 문단

## 무엇이 바뀌었나

**종전 초안의 Second·Third 를 뺐다** (1저자 결정 2026-09-08 — 문헌과 개념이 안 맞음).

- ⛔ 뺀 것 ②: 산화가 Li 자리 지형을 평탄화한다 (중성 1.27 eV → 산화 0.43 eV)
- ⛔ 뺀 것 ③: DPE 14.17 eV / LCA −6.76 eV → 사슬은 –SO₃Li 로 작동한다

남은 하나(**산화 상태에서 스핀이 어디 있나**)를 FT-IR 과 전도도 사이의 **다리**로 세운다:

> FT-IR (상태가 존재하는가) → **DFT (그 상태의 캐리어가 무엇·어디인가)** → 전도도 측정 (수송)

세 계열 **n = 2·3·6 을 모두 싣는다** (1저자 확정 2026-09-08). n=6 만으로도 핵심 주장은 서지만,
기체상 올리고머로 폴리머를 말하려면 **사슬 길이 의존성**이 유일한 논거이고, 교차(SO₃ 우세 →
백본 우세)가 있어야 "공액 길이가 만드는 폴라론" 이라는 메커니즘이 선다.
⚠ n=1(모노머)은 **싣지 않는다** — 에테르 산소가 없어 분모가 다르고, 35.0 → 32.6 으로 내려가
백본 단조 서술이 깨진다.

## 본문 (미국식 영어 · 2문단)

Density functional theory was used to identify what carries the charge in the oxidized,
deprotonated chain. A hydrogen atom was removed from the sulfonic acid group of gas-phase oligomers
of two, three, and six repeat units (Figure S3). The resulting doublets were optimized at the r²SCAN-3c level
(Supplementary Note 2). The oxidized state is imposed by this construction; that it is realized in
the material follows from the infrared spectra above. Löwdin spin populations show the unpaired spin
migrating from the sulfonate onto the conjugated backbone as the chain grows. The backbone share
rises from one-third in the dimer to 79.7% at six repeat units, while the sulfonate share falls to
7.7% (Figure S4). At six units the spin is distributed over three adjacent rings (15.9%, 23.3%, and
20.0%) rather than localized at the oxidation site.

The carrier is therefore a backbone polaron delocalized over several repeat units, with the
deprotonated sulfonate as its fixed counter-anion. This is the molecular signature of self-doping:
the chain supplies both the carrier and the charge that compensates it. Because the backbone share
has not saturated at six units, the polymer is expected to be at least this delocalized. These
gas-phase models identify the carrier but not its mobility, which also requires the doping level and
inter-chain transfer. That transport was measured directly: the polymer shows a four-point-probe
electronic conductivity of 250 mS cm⁻¹ (Section X).

### 개정 이력 (2026-09-08)

- **5문단 → 2문단.** 1저자 지적: *"논문스럽게 써야지 하나하나 다 넣으려고 하지 마."*
  방어 문구를 문장마다 박으니 논문이 아니라 체크리스트가 됐다. 한계는 한 문장으로 접고
  나머지는 Methods/SI 로 내린다.
- **SI·Methods 로 내린 것 4:** 네 그룹 합 100.0% · "어느 고리도 1/4 미만" · 스핀 이성질체
  탐색 없음 · 스핀밀도 ≠ 홀 전하밀도. 앞의 둘은 표가 보여주고 뒤의 둘은 Methods 한 줄이면 된다.
- **본문에 남긴 방어 3:** `imposed by this construction`(자발성 주장 차단) ·
  `rather than localized at the oxidation site`(ring4 국재 오독 차단) ·
  마지막 두 문장(전도도 주장 차단).
- **"Density functional theory" 를 되살렸다.** 압축 판에서 빠져 `r²SCAN-3c` 만 남았는데,
  앞이 FT-IR 절이면 방법이 바뀌는 지점이라 명시해야 한다.
- **문장 길이 9–24 단어로 균질화.** 한 문장에 몰아넣지 않는다.

## 본문에 남긴 방어선

| 구절 | 막는 것 |
|---|---|
| `The oxidized state is imposed by this construction` | DFT 로 **자발성**을 주장한다는 오독. H 를 손으로 뗀 계산이다 |
| `follows from the infrared spectra above` | 자발성은 FT-IR 몫 — 역할 분담을 한 절로 |
| `Counted over ring atoms only` → **Figure S4 캡션으로** | 7월 n=1–3 과 같은 분할. strict/extended 를 섞지 않는다 |
| `rather than localized at the oxidation site` | ring4 23.3 을 "국재" 로 읽는 것. **자리는 ring3 확정**(2026-09-08) — 최대(ring4)와 다른 고리라 이 구절이 데이터로 받쳐진다 |
| `expected to be at least this delocalized` | 외삽 한계 — "폴리머에서 100%" 는 못 쓴다 |
| `identify the carrier but not its mobility` | 전도도를 계산으로 주장하는 것 차단 |
| `That transport was measured directly` | 계산이 못 하는 것을 **측정이 답한다** — 회피가 아니라 역할 분담임을 보인다 |

⚠ `Counted over ring atoms only` 는 본문에서 뺐다 — **Figure S4 캡션에 반드시 넣는다.**
빠지면 7월 값과 다른 분할(strict 79.5 · extended 91.6)이 같은 그림에 섞여 읽힌다.

## 캡션·SI 확정 (2026-09-08 · 공저자 형식 지적 반영)

> **지적:** 다른 캡션은 다 compact 하다. S3·S4 캡션을 한두 줄로 줄이고 나머지는 Note 2 로 몰아라.
> Note 1 이 소제목 없는 산문 한 덩어리이므로 Note 2 도 그 형식에 맞춘다.

**Figure S3** — *Optimized structures of the oxidized (deprotonated) oligomers of two, three
(oxidized at a terminal and at the internal ring), and six repeat units. The sulfonate from which
the hydrogen was removed is indicated.*

**Figure S4** — *Löwdin spin populations of the oxidized oligomers: (a) partition into sulfonate,
aryl rings, ether oxygens, and hydrogens against chain length; (b) spin on each thiophene ring at
six repeat units.*

캡션 → Note 2 로 옮긴 것 4: **분할 정의(ring atoms only)** · 참고 분할 79.5/91.6 · ring3 도핑
자리 · 기체상·단일 SCF·스핀밀도 한계. 캡션에는 "무엇을 보여주는 그림인가" 만 남는다.

⚠ 그림이 지켜야 할 것 둘 (캡션이 설명하지 않으므로):
1. **상자를 끈다** (VESTA `Objects → Unit cell` 해제) — 캡션에 상자 설명이 없다.
2. **산화 자리를 실제로 표시한다** — S3 캡션 두 번째 문장이 그걸 약속한다.
   n=2 A-ring · n=3 말단/내부 · **n=6 ring3** (탈양성자 SO₃ 는 O–H 가 없는 유일한 sulfonate).

## Supplementary Note 2 (확정 · Note 1 형식 = 소제목 없는 한 문단)

> **Supplementary Note 2. Oligomer models of the oxidized, deprotonated chain**
>
> Oligomers of two, three, and six repeat units were constructed, each repeat unit being a
> 3,4-ethylenedioxythiophene (EDOT) ring bearing a −CH₂O(CH₂)₄SO₃H side chain (Supplementary Note 1),
> with oxidation at a terminal ring and at the internal ring treated separately for three repeat
> units. The oxidized, deprotonated state was generated by removing a neutral hydrogen atom — one
> proton and one electron — from a sulfonic acid group, giving a charge-neutral species with one
> unpaired electron (charge 0, multiplicity 2), which represents self-doping in which the proton is
> taken up by a base and the electron by an oxidant, leaving a hole on the chain and a sulfonate
> counter-anion; for six repeat units the hydrogen was removed from the sulfonate on ring 3,
> determined from the optimized structure rather than from the run label. All structures were
> optimized with ORCA 6.1.1 at the r²SCAN-3c level, which combines the r²SCAN meta-GGA functional
> with a def2-mTZVPP basis set, D4 dispersion, and a geometrical counterpoise correction, using the
> program's default convergence thresholds and applying no solvent model or symmetry constraint, with
> the same protocol used for every chain length. Löwdin populations were taken from the final SCF of
> each optimized structure, and for six repeat units the total spin population is 1.000, as expected
> for a doublet; the backbone denotes ring atoms only, giving 79.7% at six repeat units, whereas
> including the ring hydrogens gives 79.5% and further including the side-chain ether oxygens gives
> 91.6%, with the main text quoting the ring-atoms-only value throughout. Each structure is a single
> self-consistent solution obtained without a search over spin isomers or side-chain conformers, the
> spin density is reported as such and is not equated with the hole charge density, and the models
> are isolated and gas-phase, without solvent, counterions, or chain packing.

문장 순서 = 모델 → 산화 상태 → 계산 → 스핀 분할 → 한계 (다섯 문장).

### 이 노트에서 고친 오류 2건

1. **`Figure 1` 참조 삭제.** 초안이 "the repeat unit defined in Figure 1" 로 가리켰는데, 원고
   Figure 1 이 그 구조를 정의하는지 확인하지 않고 쓴 것이었다 — 없는 참조는 편집에서 걸린다.
   화학식으로 직접 적고 Note 1(합성)을 가리켜 자체 완결로 만들었다. 부수 효과로 본문의
   "side-chain ether oxygen" 이 EDOT 고리의 에틸렌디옥시 산소가 **아니라** 곁사슬의 그 산소라는
   것이 화학식으로 구분된다.
2. **"raises the backbone share from 79.7% to 79.5%" 는 방향이 틀렸다.** 79.5 < 79.7 이므로
   고리 H 를 넣으면 **내려간다** (π 라디칼 옆 H 의 음의 스핀 분극 −0.2). 방향어를 쓰지 않고
   정의별 값을 나열하는 방식으로 바꿔 같은 오류가 다시 생길 여지를 없앴다.

⏳ 곁사슬 `−CH₂O(CH₂)₄SO₃H` 는 Note 1 의 합성 경로에서 읽은 것(hydroxymethyl-EDOT + 2,4-butane
sultone). 실제 구조가 다르면 이 화학식만 교체한다.

### 채운 값 · 남은 빈칸

- ✅ ORCA **6.1.1** · 수렴 기준은 **프로그램 기본값**(NormalOpt): TolE 5e-6 Eh · TolMAXG 3e-4 ·
  TolRMSG 1e-4 Eh/bohr · TolMAXD 4e-3 · TolRMSD 2e-3 bohr (`n6_doped.out` 실측 2026-09-08).
  ⚠ `Strict Convergence = False` 이므로 "tight" 라고 쓰지 않는다.
- ⏳ **반복단위의 화학 표기** — 지금은 "the repeat unit defined in Figure 1" 로 가리킨다.
  Figure 1 이 그 구조를 실제로 정의하지 않으면 여기서 한 번 풀어 써야 한다.
- ✅ **n=6 도핑 자리 = ring3** (2026-09-08). 라벨이 아니라 구조에서 찾았다 — 탈양성자
  sulfonate(S=72)에서 곁사슬을 따라가 원자 43(C)이 ring3 에 속한다 (`nseries_n6.py doping_site`).
  스핀 최대는 ring4(23.3)라 **자리에서 한 칸 밀려 있다** — 본문의 `rather than localized at the
  oxidation site` 가 데이터로 받쳐진다.

## SI 연결

- **Figure S3** = 구조 (n=2 · n=3 end/mid · n=6) — `db/structures/si_figure_S3/` (xyz+vasp+vesta).
- **Figure S4** = 스핀 분포 3패널 — `docs/figures/sdcp_nseries_spin/sdcp_nseries_spin_partition.png`,
  영문 캡션 `docs/figures/sdcp_nseries_spin/caption.md`. **표는 쓰지 않는다** (1저자 결정 —
  그림에 숫자가 다 찍혀 있다).
- 수치 원본(Origin-ready) = `db/properties/sdcp_nseries_spin_2026_09_08.csv` ·
  `db/properties/sdcp_n6_ring_profile_fig.csv`.
- 정본 값·허용/금지 서술 = `db/properties/sdcp_nseries_spin_2026_09_08.json`.

## ⏳ 남은 것

1. ✅ **Section X 해결** — 4-probe 실측 **250 mS cm⁻¹** (1저자 2026-09-08). 문헌 소환값이
   아니라 우리 측정이라 `measured directly` 로 쓴다. 단위는 mS cm⁻¹ 로 뒀다 — 이 논문의
   황화물 전해질 이온전도도와 같은 축에서 읽히게 (0.25 S cm⁻¹ 로 바꾸려면 원고 전체 통일 필요).
   ⏳ 시료 형태만 미확인: **박막이면 four-point-probe**, 펠릿이면 `four-terminal`/`van der Pauw`
   로 한 단어 교체.
2. **삽입 위치** — FT-IR 절 **뒤**여야 한다. [1]의 `above` 가 그 전제다 (앞이면 `below` 로).
3. ✅ **n=6 도핑 자리 = ring3** (해결). 선택: 본문에 `(ring 3)` 을 넣어 검증 가능하게 만들지,
   Figure S4 (c) 패널에 자리 표시를 넣을지 — 1저자 결정.
