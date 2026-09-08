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

## 본문 (미국식 영어 · 짧은 문장)

**[1]** Density functional theory was used to identify what carries the charge in this oxidized,
deprotonated state. The state was imposed, not predicted. A hydrogen atom was removed from the
sulfonic acid group of gas-phase oligomers of two, three, and six repeat units. The resulting
doublet was optimized at the r²SCAN-3c level, and the spin density was partitioned by Löwdin
population analysis (Supplementary Note 2, Figure Sx, Table Sx). These calculations show where the
unpaired spin resides in an already-oxidized chain. Whether that oxidation occurs is established by
the infrared spectra above, not here.

**[2]** The unpaired spin moves from the sulfonate onto the conjugated backbone as the chain
lengthens. Counted over ring atoms only, the backbone share rises from one-third in the dimer to
79.7% at six repeat units. The sulfonate share falls monotonically across the same series, reaching
7.7%. The crossover occurs once the oxidation site has conjugated neighbors on both sides.
Per-oligomer values are given in Table Sx.

**[3]** At six repeat units the spin is not confined to one ring. It is spread over three adjacent
rings, which carry 15.9%, 23.3%, and 20.0% — 59.2% in total. No single ring carries more than a
quarter. The remainder lies on the side-chain ether oxygens (12.1%) and on ring and linker hydrogens
(0.5%). The four groups sum to 100.0%.

**[4]** These numbers describe a polaron delocalized over several repeat units of the backbone. The
deprotonated sulfonate acts as a fixed counter-anion, not as the site of the unpaired electron. This
is the molecular content of self-doping in this polymer. The chain supplies both the carrier and the
charge that compensates it, and the carrier is not trapped on the anchoring group. The backbone
share is still rising at six repeat units, so the delocalization in the polymer is expected to be at
least this extensive.

**[5]** These are isolated gas-phase oligomers of up to six repeat units. Each was obtained as a
single self-consistent solution, without a search over spin isomers. The spin density is reported as
such, and is not equated with the hole charge density. The calculations establish the identity and
location of the carrier, not its mobility. An electronic conductivity also requires a carrier
concentration set by the doping level, and transfer between chains. Neither is accessible from a
single-chain gas-phase model. The measured electronic conductivity of the polymer is given in
Section X.

## 각 문장이 지키는 것 (심사 방어선)

| 문장 | 방어하는 것 |
|---|---|
| [1] "imposed, not predicted" | DFT 로 **자발성**을 주장하지 않는다. H 를 손으로 뗀 계산이다 |
| [1] 마지막 | 역할 분담 — 자발성은 FT-IR 몫. 전도도를 안 다루는 것이 회피가 아니라 설계로 읽힌다 |
| [2] "Counted over ring atoms only" | 7월 n=1–3 과 **같은 분할**. strict(+고리H)·extended(+에테르O)를 섞지 않는다 |
| [2] "sulfonate … monotonically" | 단조는 **SO₃ 에만** 참이다 (백본은 n=1→2 에서 내려간다) |
| [3] "no single ring … a quarter" | ring4 23.3 을 "국재" 로 읽는 것을 막는다. 그리고 **도핑 자리는 아직 미확인**이라 자리 언급 없음 |
| [3] "sum to 100.0%" | "87.4 밖에 안 되는데?" 를 사전에 닫는다 |
| [4] "molecular content of self-doping" | *일어난다* 가 아니라 *일어났을 때의 모습* |
| [4] "at least this extensive" | 외삽 한계 — "폴리머에서 100%" 는 못 쓴다 |
| [5] 세 한계 | 기체상 · fresh SCF 한 번(스핀 이성질체 탐색 없음) · 스핀밀도 ≠ 홀 전하밀도 |

## SI 연결

- **Table Sx** = `db/properties/sdcp_nseries_spin_2026_09_08.csv` (Origin-ready · 열 이름 명시).
  n=6 고리별은 `db/properties/sdcp_n6_ring_profile_fig.csv` (두 정의 열: 고리 원자만 / +고리 H).
- **Figure Sx** = `docs/figures/sdcp_nseries_spin/sdcp_nseries_spin_partition.png` (3패널).
  영문 캡션 `docs/figures/sdcp_nseries_spin/caption.md`.
- 정본 값·허용/금지 서술 = `db/properties/sdcp_nseries_spin_2026_09_08.json`.

## ⏳ 남은 것

1. **Section X** — 순수 SDCP 의 전자전도도. 측정값이 있으면 그 절을 가리키고, 없으면 PEDOT-S
   계열 문헌값을 **소환값으로 명시**해 한 줄 넣는다. 이게 비면 [5]가 "우리는 전도도를 안 다룬다"
   로만 끝나 독자가 이 계산을 읽은 이유를 잃는다.
2. **삽입 위치** — FT-IR 절 **뒤**여야 한다. [1]의 `above` 가 그 전제다 (앞이면 `below` 로).
3. **n=6 도핑 자리** — `groups.json` source_manifest 확인 전에는 "자리 근방" 서술 금지.
