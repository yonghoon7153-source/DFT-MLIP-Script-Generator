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
inter-chain transfer. The measured electronic conductivity is given in Section X.

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
| `identify the carrier but not its mobility` | 전도도 주장 차단 |

⚠ `Counted over ring atoms only` 는 본문에서 뺐다 — **Figure S4 캡션에 반드시 넣는다.**
빠지면 7월 값과 다른 분할(strict 79.5 · extended 91.6)이 같은 그림에 섞여 읽힌다.

**Figure S3 캡션 (구조)** — *Optimized structures of the oxidized (deprotonated) oligomers: two
repeat units, three repeat units oxidized at a terminal and at the internal ring, and six repeat
units. The sulfonate from which the hydrogen was removed is indicated in each structure. Boxes are
for display only; the calculations were performed on isolated molecules without periodic boundary
conditions.*
⚠ 마지막 문장 필수 — `.vasp`/`.vesta` 에 보기용 상자가 들어 있어 주기 계산으로 오해될 수 있다.

## Supplementary Note 2 (초안)

> **Supplementary Note 2. Oligomer models of the oxidized, deprotonated chain**
>
> *Models.* Oligomers of two, three, and six repeat units were constructed from the repeat unit
> defined in Figure 1, each carrying a sulfonate-terminated side chain. For three repeat units, two
> oxidation sites were treated separately: a terminal ring and the internal ring.
>
> *Oxidized state.* A neutral hydrogen atom — one proton and one electron — was removed from a
> sulfonic acid group. The resulting species is charge-neutral with one unpaired electron (charge 0,
> multiplicity 2). This represents self-doping, in which the proton is taken up by a base and the
> electron by an oxidant, leaving a hole on the chain and a sulfonate counter-anion.
>
> *Calculations.* All structures were optimized with ORCA 6.1.1 at the r²SCAN-3c level, which
> combines the r²SCAN meta-GGA functional with a def2-mTZVPP basis set, D4 dispersion, and a
> geometrical counterpoise correction. Optimizations used the program's default convergence
> thresholds: energy change 5 × 10⁻⁶ Eh, maximum and RMS gradient 3 × 10⁻⁴ and 1 × 10⁻⁴ Eh bohr⁻¹,
> and maximum and RMS displacement 4 × 10⁻³ and 2 × 10⁻³ bohr. No solvent model or symmetry
> constraint was applied. The same protocol was used for every chain length, and the two- and
> three-unit values are from the same campaign.
>
> *Spin partition.* Löwdin populations were taken from the final SCF of each optimized structure.
> For six repeat units the total spin population is 1.000, as expected for a doublet. Two groups are
> quoted in the main text: the sulfonate (SO₃ atoms) and the backbone (ring atoms only). Two
> reference partitions are also available: including the ring hydrogens gives 79.5%, and further
> including the side-chain ether oxygens gives 91.6%, at six repeat units. For six units the
> hydrogen was removed from the sulfonate on ring 3, determined from the optimized structure rather
> than from the run label.
>
> *Limits.* Each structure is a single self-consistent solution; no search over spin isomers or
> side-chain conformers was performed. Spin density is reported as such and is not equated with the
> hole charge density. The models are isolated and gas-phase, without solvent, counterions, or chain
> packing.

**Figure S4 캡션 (필수)** — *Backbone denotes ring atoms only; ring hydrogens and side-chain ether
oxygens are excluded. The same partition is used for every chain length.*
⚠ 본문에서 `Counted over ring atoms only` 를 뺐으므로 이 각주가 그 역할을 대신한다. 빠지면 7월
값과 다른 분할(strict 79.5 · extended 91.6)이 한 표에 섞일 수 있다.

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

1. **Section X** — 순수 SDCP 의 전자전도도. 측정값이 있으면 그 절을 가리키고, 없으면 PEDOT-S
   계열 문헌값을 **소환값으로 명시**해 한 줄 넣는다. 이게 비면 [5]가 "우리는 전도도를 안 다룬다"
   로만 끝나 독자가 이 계산을 읽은 이유를 잃는다.
2. **삽입 위치** — FT-IR 절 **뒤**여야 한다. [1]의 `above` 가 그 전제다 (앞이면 `below` 로).
3. ✅ **n=6 도핑 자리 = ring3** (해결). 선택: 본문에 `(ring 3)` 을 넣어 검증 가능하게 만들지,
   Figure S4 (c) 패널에 자리 표시를 넣을지 — 1저자 결정.
