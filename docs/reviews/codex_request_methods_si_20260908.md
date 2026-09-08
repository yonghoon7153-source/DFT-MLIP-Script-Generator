# Codex 리뷰 요청 — Methods (DEM–MPM–voxel) 확정본과 Table S2

> 작성 2026-09-08 · 브랜치 `claude/stoic-knuth-NObVQ` · 기준 스냅샷 **`569caa513`**
> 리포 정본 = `docs/manuscript/methods_simulation_v7_draft.md` (2026-09-02) ·
> 빌더 = `scripts/build_methods_docx.py` (2026-09-08 에 md 로 포팅) ·
> 원장 = `docs/reviews/claims.json`
>
> ⚠ **이것은 투고 직전 원고 문안 검토다.**  설계 판정이 아니라 **문장이 리포 실물과 어긋나는가**가
> 쟁점이다.  아래 §1 이 검토 대상 전문이고, §2 가 내가 이미 잡은 것, §3 이 **저자가 의도적으로
> 뺀 것**(내 제안을 기각한 항목 — 다시 넣으라고 하지 말고, 뺀 상태로 성립하는지 봐 달라).

---

## 0. 검토가 필요한 이유 — 나는 이 축에서 두 번 틀렸다

이 원고를 쓰는 동안 내가 **낡은 판을 정본으로 착각해** 공저자에게 두 번 건넸다.

1. `build_methods_docx.py`(2026-08-30)의 *"the powder-scale value was adopted and rescaled"* 와
   *"two conventions reported as equivalent sensitivity points"* 를 현행으로 인용했다.
   실제 정본 md 는 **09-02 에 둘 다 뒤집었다** — 100 S cm⁻¹ 은 *"frozen, uncalibrated legacy
   coefficient"* 이고 분말값에서 유도된 것이 **아니며**, PTFE 는 centerline 이 **공칭 규약**이고
   omitted 는 Table S3c 민감도다.  (커밋 `a16328ce0` 에서 빌더를 md 로 포팅해 해소.)
2. md·빌더가 **영국식 철자**로 쓰여 있었는데(fibre · voxelisation · idealised, 각 27건) CLAUDE.md
   상시 규약은 미국식이다.  그것을 그대로 인용했다.  (커밋 `b1beb98d5` 에서 변환 + **규칙 O**
   신설로 재발 차단.)

⇒ **같은 부류가 §1 본문에 더 남아 있는지**가 이 요청의 1차 질문이다.

---

## 1. 검토 대상 — Methods 확정본 (저자 최종)

> DEM–MPM–voxel transport simulations: Three-dimensional composite cathode microstructures were
> constructed to evaluate how the partial substitution of PTFE with SDCP alters the electronic and
> ionic transport networks. The microstructures were generated in two stages, using DEM to build
> the rigid-sphere packing of NCM811 and LPSCl particles in LIGGGHTS[51] and MPM to resolve the
> subsequent plastic densification of the electrolyte on the fixed DEM skeleton. The packing
> comprised 1,271 NCM811 spheres (radius, r = 2.5 μm) and 146,420 LPSCl spheres (r = 0.5 μm),
> sized after the experimental powders and computed with a Hookean contact model with hysteretic
> unloading. The two populations were mixed at 70:27 by weight in a 50 × 50 μm² cross-section and
> compacted to a final electrode thickness of 72.53 μm.
>
> Rigid-sphere contacts reproduce particle rearrangement, but not the plastic flattening, fracture
> and grain-boundary deformation that also densify sulfide powders. The contact modulus of LPSCl
> was therefore selected against a densification target for sulfide cold pressing (~10 % porosity
> at 300 MPa) rather than taken from the dense material.[9] The resulting value is an effective
> parameter that lumps those unresolved mechanisms (Table S2).[52]
>
> Plastic deformation of the electrolyte was then resolved on the fixed DEM skeleton by MPM
> (Table S2), with the active material held fixed as a rigid obstacle so that only the electrolyte
> densifies. VGCF fibers, PTFE fibrils and SDCP particles were present in the material-point cloud
> during compaction at the experimental weight fractions.
>
> Effective conductivities were obtained by rasterizing each microstructure onto a cubic grid with
> a voxel edge of 0.15 μm (334 × 334 × 484 voxels, ≈ 5.4 × 10⁷). Adjacent conducting voxels were
> coupled through harmonic-mean conductances and the potential field was obtained from
>
> ∇ ⋅ (σ∇φ) = 0  (2)
>
> where σ and φ are the local conductivity of each voxel and the electric potential, respectively.
>
> A potential difference of 1 V was applied between the separator (φ = 0) and current collector
> (φ = 1 V) faces with the remaining boundaries insulating, and the effective conductivity was
> taken from the total current. NCM811, VGCF and SDCP carried the electronic network and LPSCl and
> SDCP the ionic network; voxels lying on the centerline of a PTFE fibril were excluded from both
> grids, so that PTFE was treated as a blocking phase.
>
> Because a cylindrical VGCF fiber of diameter d is rendered as a one-voxel-thick tube of edge h,
> the conductivity assigned to the VGCF phase was rescaled as σ_eff = σ·πd²/(4h²) to preserve the
> conductance of the fiber. Each electrode was solved at eight half-voxel grid-origin shifts
> (2 × 2 × 2), the SBE and DBE sharing the same origins.
>
> Shifting the grid origin resamples the same packing rather than generating a new one, so the
> eight solutions were not treated as independent replicates; ratios are reported as the mean over
> the eight origin-matched SBE/DBE pairs. Across the eight origin shifts the effective
> conductivities varied by 0.5–0.6 % and the SBE/DBE ratio by 0.2 % (1.302–1.310), so the reported
> ratio is insensitive to grid placement. The ohmic loss carried by each phase was evaluated as
>
> P = Σ g_k (Δφ_k)²  (3)
>
> where g_k and Δφ_k are the conductance of and the potential difference across the k-th
> voxel-to-voxel connection, summed over the connections belonging to that phase.

### Table S2 (SI 현행, 저자 소관 — 아래 각주 ①만 내가 이의 제기)

`Simulation domain` 50 × 50 µm² · voxel 0.15 µm | `NCM811` r 2.5 / E 140 / σ_e 1.0 × 10⁻² |
`LPSCl` r 0.5 / E(DEM contact) 1.35 `Calibrated` / ν(DEM) 0.3 `Assumed` / E(MPM) 1.53
`Calibrated` / ν(MPM) 0.49 `Calibrated` / σ_y 0.30 `Calibrated` / σ_ion 3.0 × 10⁻³ |
`VGCF` d 0.15 / E 10 / σ_e(compressed powder) 1.0 × 10² `Assumed` / σ_e(voxel,
diameter-preserving) 78.5 `Calculated` | `PTFE` E 1.8 / σ 0 | `SDCP` d 0.30 / E 9.0 /
σ_e 250 `Measured` / σ_ion 1.0 × 10⁻³

> ※ ① Parameters marked "Calibrated" were adjusted so that the compacted packing reproduces the
> porosity and contact overlap measured for cold-pressed LPSCl.[S]
> ※ ② PTFE was seeded as drawn fibrils: each fibril conserves its own volume V while being drawn
> to a lognormally distributed length L, so that its diameter follows d ∝ √(V/L)

---

## 2. 내가 이미 잡아 저자에게 전달한 것 (재확인만)

| # | 항목 | 근거 |
|---|---|---|
| A | 복셀 수 `333 × 333 × 483` → **`334 × 334 × 484`** | `step3_sigma.py:299` 가 `ceil`; 50/0.15 = 333.3 → 334, 72.534/0.15 = 483.6 → 484.  총합 5.4 × 10⁷ 은 불변 |
| B | *"cannot reproduce … particle rearrangement"* → **DEM 은 재배열을 한다** | md Stage 1 |
| C | origin 산포 **0.08 %** 는 sd/√8 = **표준오차** | 8 origin = 한 침대의 완전 2×2×2 factorial, 복제 자유도 0.  실측 sd: 비 0.21 %(범위 1.302–1.310) · 절대 SBE 0.52 % · DBE 0.61 % |
| D | 시딩이 MPM **뒤**로 읽힘 → **압밀 전**, material-point cloud 안 | 매니페스트 `additive_E_GPa {VGCF 10, PTFE 1.8, SDCP 9.0}` |
| E | *"rendered as a cubic voxel"* → **one-voxel-thick tube** | 식이 단면(πd²/4 vs h²)을 맞춘다 |
| F | Table S2 각주 ① 의 **11–12 % overlap "measured"** | 우리 pure-SE 시뮬 consistency 결과.  md: *"a simulation consistency result rather than a measured calibration target"* |
| G | Table S2 각주 ① 이 **E(MPM) 1.53 · ν(MPM) 0.49 에 대해 거짓** | 그 둘은 공극률에 맞춰 조정한 값이 아니다 (md 라벨: `Model choice`).  네 행이 다 `Calibrated` 라 각주가 그 둘을 잘못 덮는다 |

**A–E 는 §1 확정본에 반영됨.  F·G 는 미반영** (Table S2 는 공저자 소관이라 저자가 그쪽에 전달 예정).

---

## 3. ⛔ 저자가 **의도적으로 뺀 것** — 다시 넣으라고 하지 말 것

내가 제안했다가 저자가 **명시적으로 기각**했다.  판단은 저자 소관이고, 요청하는 것은
*"이 상태로 원고가 성립하는가 / 어디가 위험한가"* 뿐이다.

| 뺀 것 | md 원문 | 저자 판단 |
|---|---|---|
| PTFE 두 규약 민감도 (54.0/70.6 → 1.308 **vs** 72.3/81.3 → 1.124) 와 Table S3c 포인터 | Stage 3 끝 + Values 절 | *"안 넣는다"* |
| *"matching the pure-SE densification target does not by itself validate the SBE/DBE beds"* | Stage 1 | Limitations 로 옮기거나 생략 |
| `J2 (von Mises)` · `GPU-accelerated` | Stage 2 | 표에 σ_y 가 있으므로 불필요 |
| 전도 복셀 수 (≈ 2.7 × 10⁷) | — | 불필요 |

⚠ 그리고 §1 에는 md Limitations 절의 네 한정이 **전부 없다**: 과압축·비검증 · 준정적 위반
(platen 0.27 c_P vs 한계 0.01) · 절대값 면책(접촉저항 0, CL-81) · 격자 미수렴.
저자는 **Limitations 를 Methods 밖에 따로 둔다**는 전제다.  ⇒ 그 전제가 유지되는지는
Results/SI 를 봐야 알 수 있고, 이 요청서에는 그 부분이 없다.

---

## Q1 ⚠⚠ §1 에 §0 과 **같은 부류의 낡은-판 인용**이 더 있는가

내가 두 번 틀린 축(빌더 08-30 ↔ md 09-02)을 §1 전문에 대해 전수 대조해 달라.
특히 **철회된 프레이밍이 문장 안에 남아 있는가**:

- σ_VGCF 100 을 *"powder value"* 로 읽히게 하는 표현 (§1 은 그 낱말을 안 쓰지만
  Table S2 는 `compressed powder` 라 적는다 — **본문과 표가 서로 다른 프레임인가**)
- PTFE centerline 을 *"the method"* 로 단정해 사후 primary 지정이 되는가 (R10 Q2)
- `Calibrated` 를 한 라벨로 뭉쳐 세 역할(경험적 접촉법칙 입력 / 모델 선택 / 치밀화 표적)을
  가리는가

## Q2 §1 의 **사실 진술**을 리포 실물과 대조

각 문장이 코드·매니페스트와 맞는지.  내가 대조한 것: 1,271 / 146,420 / r 2.5·0.5 / 70:27 /
50 × 50 / 72.53 µm · Hookean-hysteretic · `ceil` 격자 · harmonic mean · 1 V ·
collector = 바닥 φ = 1 · separator = 상단 φ = 0 · `periodic_xy False`(측면 절연) ·
PTFE centerline zero-dof (161,407 셀) · SDCP 양쪽 망 · origin {0, h/2}³ 8개 공유 ·
`P = Σ g Δφ²`.  **내가 못 대조한 것: [9] · [51] · [52] 의 실제 문헌** (리포에 없다).

⚠ 특히 §1 셋째 문단 *"only the electrolyte densifies"* — CL-85 실측은 네 침대 전부
`thickness = 씨앗 × λ` 를 **±0.015 %** 로 재현한다 = **압밀이 기하학적으로 no-op** 이다.
*"densifies"* 가 이 사실과 양립하는가, 아니면 문장이 과대 주장인가.

## Q3 §3 의 누락이 **원고를 오도하는가**

Methods 만 읽은 독자가 얻는 인상과 리포가 아는 것 사이의 격차를 매겨 달라.
가장 날카롭게 물으면: **§1 만 읽고 이 결과를 재현하려는 독자가 어디서 다른 값을 얻게 되는가.**
(예: 코드 기본값은 PTFE `omitted` 라 1.124 가 나온다 — 원고는 1.308 을 보고한다.)

## Q4 origin 통계 문장이 관행에 맞는가

> Across the eight origin shifts the effective conductivities varied by 0.5–0.6 % and the SBE/DBE
> ratio by 0.2 % (1.302–1.310), so the reported ratio is insensitive to grid placement.

8 origin 은 **한 침대의 완전 factorial** 이라 복제가 아니다 (표준오차·신뢰구간 금지).
이 문장이 ⓐ 그 성격을 오도하지 않는가 ⓑ 복셀/FFT 균질화 문헌의 격자-민감도 보고 관행에
부합하는가.

---

## 부록 — 이 요청 이후 리포에서 확정된 것 (배경, 검토 대상 아님)

| 원장 | 무엇 |
|---|---|
| **CL-81** | 복셀 σ 는 접촉망의 `CONTACT_FREE` 가지 = 협착 저항 항이 **정확히 0**.  크기 실측 중앙값 **4.04×**(Hertz) · **6.69×**(소성면적), n=157.  ⇒ 절대 σ 를 실험과 나란히 적을 때 상한 표지 필요 |
| **CL-83 · CL-85** | Phase A 네 침대 완주.  `씨앗 × λ` 항등식 ±0.015 % · 도달 압력 조성 무관 (0.443~0.476) |
| **규칙 N · O** | 킷 러너의 재하율 라벨이 실물인가 · 원고 산문이 미국식인가 (`check_method_discipline.py`) |
