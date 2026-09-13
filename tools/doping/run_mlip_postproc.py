#!/usr/bin/env python
"""run_mlip_postproc.py — full MLIP post-processing per structure.

For each input xyz, runs in order:
  1. Light anneal (300 K, 20 ps, optional). NOTE: 300K @ 20ps is mostly
     finite-T noise injection rather than true Li-sublattice annealing
     (Arrhenius rate × 20ps ≈ 0.01 hop/Li at 300K). Use temperature=500
     and time_ps=50 for actual Pipeline-Step-3 anneal (kT=0.043 eV
     vs Li hop Eₐ=0.2 eV barrier).
  2. EOS volume sweep (94-106% in 7 steps: 0.94/0.96/0.98/1.00/1.02/
     1.04/1.06), Birch-Murnaghan 3rd-order fit
     → V0, B0, B0', R² (returns None for B0/V0 if r²<0.95 — A-3 fix)
  3. Elastic constants via finite strain (6 Voigt strains, ε = ±0.005),
     Voigt-Reuss-Hill average → B, G, E (Young), ν (Poisson), G/B (Pugh).
     Sign convention: ASE atoms.get_stress() returns positive stress
     for compression (= negative of dE/dV/V), so dσ/dε > 0 → C_ii > 0.

All UMA, no extra DFT. Output: per-structure JSON + global summary.

Usage:
  python3 tools/doping/run_mlip_postproc.py \\
      --winners runs/.../winners.json \\
      --out runs/.../mlip_postproc/ \\
      --device cuda

  # Skip steps (per-step toggle)
  python3 ... --no_anneal --no_elastic   # only EOS

  # Specific xyz instead of winners JSON
  python3 ... --xyz path/a.xyz path/b.xyz --out ...
"""
import argparse
import json
import sys
import time
from pathlib import Path
import numpy as np
from ase.io import read, write
from ase.optimize import FIRE
from ase.md.langevin import Langevin
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase import units

try:
    from ase.filters import FrechetCellFilter as CellFilter
except ImportError:
    try:
        from ase.constraints import ExpCellFilter as CellFilter
    except ImportError:
        from ase.constraints import UnitCellFilter as CellFilter

sys.path.insert(0, str(Path(__file__).parent))
from _provenance import get_provenance


def load_uma(device='cuda', task='omat'):
    from fairchem.core import pretrained_mlip, FAIRChemCalculator
    predictor = pretrained_mlip.get_predict_unit('uma-s-1p1', device=device)
    return FAIRChemCalculator(predictor, task_name=task)


def light_anneal(atoms, T=300, time_ps=20, dt_fs=2.0, relax_steps=500,
                fmax=0.05):
    """Brief Langevin NVT then cell+positions relax. Returns relaxed atoms +
    log dict."""
    MaxwellBoltzmannDistribution(atoms, temperature_K=T)
    n_steps = int(time_ps * 1000 / dt_fs)
    dyn = Langevin(atoms, dt_fs * units.fs, temperature_K=T, friction=0.01,
                  logfile=None)
    t0 = time.time()
    dyn.run(n_steps)
    t_md = time.time() - t0
    opt = FIRE(CellFilter(atoms), logfile=None)
    t1 = time.time()
    opt.run(fmax=fmax, steps=relax_steps)
    t_relax = time.time() - t1
    return atoms, {'T_K': T, 'time_ps': time_ps,
                   'n_relax_steps': opt.get_number_of_steps(),
                   'converged': opt.get_number_of_steps() < relax_steps,
                   't_md_s': t_md, 't_relax_s': t_relax,
                   'E_post_atom': atoms.get_potential_energy() / len(atoms)}


def eos_sweep(atoms_ref, calc, fractions=(0.94, 0.96, 0.98, 1.00, 1.02, 1.04, 1.06),
             fmax=0.05, relax_steps=500):
    """Volume sweep + Birch-Murnaghan 3rd-order fit. atoms_ref is the
    relaxed reference at V0; we scale its lattice by f^(1/3) per point."""
    V = []
    E = []
    n = len(atoms_ref)
    for f in fractions:
        atoms = atoms_ref.copy()
        new_cell = atoms.cell.array * f ** (1/3)
        atoms.set_cell(new_cell, scale_atoms=True)
        atoms.calc = calc
        # Atoms-only relax (cell fixed for EOS)
        opt = FIRE(atoms, logfile=None)
        opt.run(fmax=fmax, steps=relax_steps)
        V.append(atoms.get_volume())
        E.append(atoms.get_potential_energy())
    V = np.array(V)
    E = np.array(E)
    # 3rd-order Birch-Murnaghan fit
    try:
        from scipy.optimize import curve_fit
        def bm3(V, E0, V0, B0, Bp):
            eta = (V0 / V) ** (2/3)
            return (E0 + (9 * V0 * B0 / 16) *
                    ((eta - 1) ** 3 * Bp + (eta - 1) ** 2 * (6 - 4 * eta)))
        p0 = [E.min(), V[E.argmin()], 0.1, 4.0]  # B0 in eV/Å³ ≈ 0.1 = 16 GPa
        popt, _ = curve_fit(bm3, V, E, p0=p0, maxfev=10000)
        E0, V0, B0, Bp = popt
        # B0 in GPa: 1 eV/Å³ = 160.218 GPa
        B0_GPa = B0 * 160.21766208
        # R²
        E_pred = bm3(V, *popt)
        ss_res = np.sum((E - E_pred) ** 2)
        ss_tot = np.sum((E - E.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        # A-3 fix: r² gate. Diverged BM3 fits (r²<0.95) shouldn't poison
        # downstream rankings; flag B0_GPa as None and set fit_quality_ok=False
        # so combine_rankings can drop them.
        # N-? fix: also gate on a physical B0' (0<Bp<15). A BM3 fit can have high
        # r² yet diverge to garbage (e.g. B0=2.2 GPa, Bp=-306) — those slip past
        # the r² gate but are unphysical; require a sane B0' so B0_GPa→None.
        # ⛔ 2026-09-13 — `bool(...)` 로 감싼다. numpy 비교는 `np.bool_` 을 내고,
        #   기록을 쓰는 `json.dumps(..., default=str)` 이 그걸 **문자열 "False"** 로
        #   직렬화한다. 하류가 `if rec['fit_quality_ok']:` 로 읽으면 **"False" 가 참**이다.
        #   (실측: eos_diag per_seed 가 "False"/"True" 문자열로 나왔다)
        fit_ok = bool(r2 >= 0.95 and 0 < V0 < 5 * V[len(V)//2]
                      and 0.0 < Bp < 15.0)
        return {'V_points': V.tolist(), 'E_points': E.tolist(),
                'fractions': list(fractions),
                'V0': float(V0) if fit_ok else None,
                'V0_per_atom': float(V0) / n if fit_ok else None,
                'E0': float(E0) if fit_ok else None,
                'B0_eV_per_A3': float(B0) if fit_ok else None,
                'B0_GPa': float(B0_GPa) if fit_ok else None,
                'Bp': float(Bp) if fit_ok else None,
                'r2': float(r2),
                'fit_quality_ok': fit_ok,
                'fit_quality_reason': ('OK' if fit_ok
                                      else f"r2={r2:.4f} / V0 / B0'={Bp:.2f} "
                                           f"unphysical (need r2>=0.95, 0<B0'<15)")}
    except Exception as e:
        return {'V_points': V.tolist(), 'E_points': E.tolist(),
                'fractions': list(fractions),
                'fit_error': str(e)}


def eos_ensemble(atoms_ref, calc, n_seeds=5, perturb=0.1,
                 fractions=(0.94, 0.96, 0.98, 1.00, 1.02, 1.04, 1.06),
                 fmax=0.05, relax_steps=500):
    """Run eos_sweep on N rattled copies of atoms_ref and keep the BEST BM3 fit.

    MLIP single-curve EOS is basin-sensitive: a stray Li/ion rearrangement at one
    volume kinks the curve and gives an unphysical B0' (e.g. the Nd-doped case had
    B0' from -64 to +16 across seeds while the clean fits clustered at ~6). The
    best-of-N curve avoids that. Returns the selected curve's dict (SAME schema as
    eos_sweep, so downstream is unchanged) plus an 'ensemble' summary (per-seed +
    mean/std). Selection: highest r² among physical fits (fit_ok and 0<B0'<15);
    fall back to highest r² with a B0; else the first result.
    """
    results = []
    for s in range(n_seeds):
        a = atoms_ref.copy()
        if s > 0:
            a.rattle(stdev=perturb, seed=s)
        results.append(eos_sweep(a, calc, fractions=fractions, fmax=fmax,
                                 relax_steps=relax_steps))
    physical = [r for r in results
                if r.get('fit_quality_ok') and r.get('B0_GPa') is not None
                and r.get('Bp') is not None and 0.0 < r['Bp'] < 15.0]
    pool = physical or [r for r in results if r.get('B0_GPa') is not None] or results
    best = dict(max(pool, key=lambda r: r.get('r2', -1.0)))
    b0s = [r['B0_GPa'] for r in results if r.get('B0_GPa') is not None]
    _nfit = int(sum(1 for r in results if r.get('fit_quality_ok')))
    # ⛔⛔ 2026-09-13 — `std` 가 **거짓 정밀도**를 낸다. 살아남은 값이 하나면
    #   `np.std([x]) == 0.0` 이고, 화면에는 *"시드 간 완벽 일치"* 로 읽힌다.
    #   실측(P2_Al2S3_B, 시드 3): r² 0.79 / 0.998 / 0.90 → **2개 실패**, 통과 1개.
    #   그런데 std 는 0.0 이었다. 정반대의 뜻으로 읽히는 숫자다.
    #   ⇒ 표본이 2 미만이면 **None**. 그리고 몇 개로 잰 값인지(`n_B0`)를 같이 낸다.
    _std = float(np.std(b0s)) if len(b0s) >= 2 else None
    best['ensemble'] = {
        'n_seeds': int(n_seeds), 'perturb': float(perturb),
        'n_fit_ok': _nfit,
        'n_physical_Bp': len(physical),
        'n_B0': len(b0s),
        'B0_GPa_mean': float(np.mean(b0s)) if b0s else None,
        'B0_GPa_std': _std,
        '⚠_std_가_None_인_이유': (None if _std is not None else
                                f'B0 를 낸 시드가 {len(b0s)}개뿐이라 산포를 잴 수 없다. '
                                f'0.0 이 아니다 — 0.0 은 일치를 뜻하는데 그게 아니다'),
        'B0_GPa_median': float(np.median(b0s)) if b0s else None,
        'selection': ('max_r2_physical_Bp' if physical
                      else ('max_r2_any' if b0s else 'all_failed')),
        '⛔_선택_경고': (None if _nfit == int(n_seeds) else
                     f'시드 {n_seeds}개 중 **{int(n_seeds)-_nfit}개가 적합 실패**했고 '
                     f'아래 값은 살아남은 것 중 r² 최대를 **고른 것**이다. '
                     f'결과를 보고 고르는 선택이므로 **산포의 근거가 아니다** — '
                     f'적합이 시드에 민감하면 골짜기 이동(basin hopping)을 의심해라'),
        'per_seed': [{'B0_GPa': r.get('B0_GPa'), 'V0_per_atom': r.get('V0_per_atom'),
                      'Bp': r.get('Bp'), 'r2': r.get('r2'),
                      'fit_quality_ok': r.get('fit_quality_ok')} for r in results],
    }
    return best


# ══════════════════════════════════════════════════════════════════════════
# 셀 정책 (2026-09-13 · 회신 BP Q4③ 지적 → 실물 확인 → 이행)
#
# ⛔⛔ **GAP-3 실측**: `eos_sweep` 은 점마다 `atoms_ref.copy()` 로만 작업해
#   **atoms_ref 를 바꾸지 않는다**. 그래서 `process_one` 이 V₀ 를 record 에
#   기록만 하고, 이어지는 `elastic_finite_strain(atoms, ...)` 에는 여전히
#   **2단계 post-anneal 구조**가 들어갔다 — 즉 **탄성이 보고된 V₀ 가 아닌
#   부피에서 계산됐다.** 두 양이 같은 구조를 가리킨다고 읽으면 틀린다.
#
# ⚠ 기본 동작은 **바꾸지 않는다** (과거 명령의 재현성). 대신
#   ① `--apply_eos_v0` 로 명시하면 V₀ 를 실제로 적용하고
#   ② 적용하든 안 하든 `record['cell_policy']` 에 **무엇을 했는지 남긴다**.
#   적용 안 한 경우에도 경고 문자열이 출력에 박히므로 조용히 지나가지 않는다.
#
# 형상 정책의 정확한 표현 (회신 BP):
#   "셀 각도와 길이비를 고정하고 등방 E(V) 경로에서 부피를 최적화한다.
#    **목표** 평균압은 0 GPa 이며, **실제 잔류 평균압과 편차응력을 별도로 보고**한다."
#   ⛔ '전체 응력 0' · '자유 영응력 평형' 과 다르다.
# ══════════════════════════════════════════════════════════════════════════
EV_A3_TO_GPA = 160.21766208


def stress_report(atoms):
    """실제 잔류 응력 — 평균압과 편차성분을 **따로** 낸다 (회신 BP Q4③).

    ⛔ 이 함수가 하지 않는 것: '영응력이다' 판정. 숫자만 낸다.
    """
    import numpy as _np
    v = _np.asarray(atoms.get_stress(voigt=True), dtype=float) * EV_A3_TO_GPA
    sig = _np.array([[v[0], v[5], v[4]], [v[5], v[1], v[3]], [v[4], v[3], v[2]]])
    p = float(_np.trace(sig) / 3.0)
    dev = sig - p * _np.eye(3)
    return {'sigma_GPa': sig.tolist(), 'P_mean_GPa': p,
            'deviatoric_max_abs_GPa': float(_np.abs(dev).max()),
            '⚠': '목표 평균압 0 과 별개로 **실제** 값이다. 영응력 판정 아님'}


def apply_v0_fixed_shape(atoms_ref, V0, calc, fmax=0.05, relax_steps=500):
    """**셀 각도·길이비를 고정한 채** 부피만 V₀ 로 맞추고 원자만 완화한다.

    등방 스케일이므로 각도와 길이비는 구조적으로 보존된다 — 그것이 이 정책이
    'argyrodite 골격 보존' 을 뜻하는 방식이다.

    ⛔ 이 함수가 **못 하는 것**
      · 셀 형상을 최적화하지 않는다 (그것이 금지된 vc-relax 다).
      · 편차응력을 없애지 않는다 — 없애려면 형상을 풀어야 한다. 남은 값을 **보고**한다.
      · V₀ 가 None 이면 아무것도 하지 않고 그대로 돌려준다 (BM 적합 실패 시).
    """
    if V0 is None:
        return atoms_ref, {'applied': False, 'reason': 'V0 is None (BM 적합 실패)'}
    a = atoms_ref.copy()
    f = float(V0) / a.get_volume()
    a.set_cell(a.cell.array * f ** (1.0 / 3.0), scale_atoms=True)
    a.calc = calc
    opt = FIRE(a, logfile=None)                 # ← 고정셀: CellFilter 를 쓰지 않는다
    opt.run(fmax=fmax, steps=relax_steps)
    rep = {'applied': True, 'V0_target_A3': float(V0),
           'V_before_A3': float(atoms_ref.get_volume()),
           'V_after_A3': float(a.get_volume()),
           'scale_factor': f,
           'n_relax_steps': opt.get_number_of_steps(),
           'converged': opt.get_number_of_steps() < relax_steps}
    try:
        rep['residual_stress'] = stress_report(a)
    except Exception as e:                       # 계산기가 응력을 못 내는 경우
        rep['residual_stress'] = {'error': str(e)}
    return a, rep


def maybe_apply_eos_v0(atoms, record, args, calc):
    """EOS V₀ 를 적용할지 말지의 **갈림길 자체**. selftest 가 이 함수를 친다.

    반환 (atoms, policy_dict). 적용 안 한 경우에도 policy_dict 에 **경고가 박힌다** —
    조용히 지나가지 않게 하는 것이 이 함수의 목적이다.

    ⛔ 이 함수가 **못 하는 것**: 어느 쪽이 옳은지 판정하지 않는다. 무엇을 했는지 적을 뿐이다.
    """
    pol = {
        'step0_relax': ('FIRE(atoms) — 고정셀(각도·길이비 보존)'
                        if getattr(args, 'fixed_shape_relax', False)
                        else 'CellFilter(atoms) — 형상 무제한'),
        'eos_v0_applied': False,
        '표현': ('셀 각도와 길이비를 고정하고 등방 E(V) 경로에서 부피를 최적화한다. '
                 '목표 평균압은 0 GPa 이며, 실제 잔류 평균압과 편차응력을 별도로 보고한다'),
    }
    no_eos = bool(getattr(args, 'no_eos', False))
    if getattr(args, 'apply_eos_v0', False) and not no_eos:
        v0 = (record.get('eos') or {}).get('V0')
        atoms, rep = apply_v0_fixed_shape(atoms, v0, calc,
                                          fmax=getattr(args, 'eos_fmax', 0.05),
                                          relax_steps=getattr(args, 'relax_steps', 500))
        pol['eos_v0_applied'] = bool(rep.get('applied'))
        pol['apply_report'] = rep
        if not rep.get('applied'):
            pol['⛔경고'] = ('V₀ 적용을 요청했으나 적용하지 못했다 (%s). 아래 elastic 은 '
                             'V₀ 가 아닌 부피에서 계산된 값이다.' % rep.get('reason', '?'))
    elif not no_eos and not bool(getattr(args, 'no_elastic', False)):
        pol['⛔경고'] = (
            'EOS 가 낸 V₀ 를 **적용하지 않았다**. 아래 elastic 은 V₀ 가 아니라 '
            'post-anneal 부피에서 계산된 값이다 (GAP-3, cell_policy_gap_2026_09_13.json). '
            '두 양이 같은 구조를 가리킨다고 읽으면 틀린다. 적용하려면 --apply_eos_v0')
    return atoms, pol


def elastic_finite_strain(atoms_ref, calc, eps=0.005, fmax=0.05,
                          relax_steps=300):
    """6 independent Voigt strains × ±eps. Compute stress → Cij.
    Voigt-Reuss-Hill avg → B, G, E, ν, G/B.
    """
    # Strain matrices for ε₁..ε₆ (Voigt convention)
    voigt = [
        np.array([[1, 0, 0], [0, 0, 0], [0, 0, 0]]),  # ε₁ = εxx
        np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]]),  # ε₂ = εyy
        np.array([[0, 0, 0], [0, 0, 0], [0, 0, 1]]),  # ε₃ = εzz
        np.array([[0, 0, 0], [0, 0, 0.5], [0, 0.5, 0]]),  # ε₄ = εyz
        np.array([[0, 0, 0.5], [0, 0, 0], [0.5, 0, 0]]),  # ε₅ = εxz
        np.array([[0, 0.5, 0], [0.5, 0, 0], [0, 0, 0]]),  # ε₆ = εxy
    ]

    cell0 = atoms_ref.cell.array.copy()
    n = len(atoms_ref)
    Cij = np.zeros((6, 6))
    for i, strain in enumerate(voigt):
        stresses_pos_neg = []
        for sign in (+1, -1):
            atoms = atoms_ref.copy()
            F = np.eye(3) + sign * eps * strain
            atoms.set_cell(cell0 @ F, scale_atoms=True)
            atoms.calc = calc
            opt = FIRE(atoms, logfile=None)
            opt.run(fmax=fmax, steps=relax_steps)
            # Stress in Voigt order: [σxx, σyy, σzz, σyz, σxz, σxy] (ASE convention)
            stresses_pos_neg.append(atoms.get_stress(voigt=True))
        sigma_pos, sigma_neg = stresses_pos_neg
        # Central difference: ∂σ/∂ε
        dsigma_de = (sigma_pos - sigma_neg) / (2 * eps)
        Cij[:, i] = dsigma_de  # column i = ∂σⱼ/∂εᵢ

    # Symmetrize
    Cij = 0.5 * (Cij + Cij.T)
    # ASE stress is in eV/Å³; convert to GPa
    Cij_GPa = Cij * 160.21766208

    # Voigt-Reuss-Hill
    C = Cij_GPa
    Bv = (C[0, 0] + C[1, 1] + C[2, 2] + 2 * (C[0, 1] + C[0, 2] + C[1, 2])) / 9
    Gv = ((C[0, 0] + C[1, 1] + C[2, 2]) - (C[0, 1] + C[0, 2] + C[1, 2])
          + 3 * (C[3, 3] + C[4, 4] + C[5, 5])) / 15
    try:
        S = np.linalg.inv(C)
        Br = 1 / (S[0, 0] + S[1, 1] + S[2, 2] + 2 * (S[0, 1] + S[0, 2] + S[1, 2]))
        Gr = 15 / (4 * (S[0, 0] + S[1, 1] + S[2, 2])
                  - 4 * (S[0, 1] + S[0, 2] + S[1, 2])
                  + 3 * (S[3, 3] + S[4, 4] + S[5, 5]))
    except np.linalg.LinAlgError:
        Br = Gr = None

    Bh = (Bv + Br) / 2 if Br is not None else Bv
    Gh = (Gv + Gr) / 2 if Gr is not None else Gv
    if Bh and Gh:
        E_young = 9 * Bh * Gh / (3 * Bh + Gh)
        nu = (3 * Bh - 2 * Gh) / (2 * (3 * Bh + Gh))
        pugh = Gh / Bh
    else:
        E_young = nu = pugh = None

    return {
        'eps': eps,
        'Cij_GPa': Cij_GPa.tolist(),
        'B_voigt_GPa': float(Bv), 'B_reuss_GPa': float(Br) if Br else None,
        'B_hill_GPa': float(Bh),
        'G_voigt_GPa': float(Gv), 'G_reuss_GPa': float(Gr) if Gr else None,
        'G_hill_GPa': float(Gh),
        'E_young_GPa': float(E_young) if E_young else None,
        'poisson_nu': float(nu) if nu else None,
        'pugh_ratio_GoverB': float(pugh) if pugh else None,
    }


def winner_name(xyz_path):
    """NEW-D fix (v4.5.17): cascade outputs like
    04_anneal/{winner}/post_relax.xyz all share stem='post_relax',
    causing dict-key collision in collect_dataset. Use parent dir
    name in that case."""
    from pathlib import Path
    p = Path(xyz_path)
    if p.stem in ('post_relax', 'post_md'):
        return p.parent.name
    return p.stem


def process_one(xyz_path, calc, out_dir, args):
    name = winner_name(xyz_path)
    work = out_dir / name
    work.mkdir(parents=True, exist_ok=True)

    atoms = read(str(xyz_path))
    atoms.calc = calc
    record = {'name': name, 'xyz_input': str(xyz_path),
              'n_atoms': len(atoms),
              'composition': {el: int(c) for el, c in
                              zip(*np.unique(atoms.get_chemical_symbols(),
                                            return_counts=True))}}

    # 0. Refresh relax to ensure starting at minimum
    #    ⚠ 기본은 형상 무제한 CellFilter — **DFT 쪽 고정셀 규율이 여기 걸려 있지 않다**
    #      (GAP-1·2). --fixed_shape_relax 로 고정셀 경로를 고를 수 있다.
    _target = atoms if getattr(args, 'fixed_shape_relax', False) else CellFilter(atoms)
    opt = FIRE(_target, logfile=None)
    opt.run(fmax=0.05, steps=500)
    record['E_pre_anneal_per_atom'] = atoms.get_potential_energy() / len(atoms)

    # 1. Anneal (optional)
    if not args.no_anneal:
        atoms, log = light_anneal(atoms, T=args.anneal_T,
                                 time_ps=args.anneal_ps,
                                 relax_steps=args.relax_steps)
        record['anneal'] = log
    record['E_post_anneal_per_atom'] = atoms.get_potential_energy() / len(atoms)
    write(work / 'post_anneal.xyz', atoms)

    # 2. EOS (optionally an ensemble of N rattled seeds, best BM3 fit kept)
    if not args.no_eos:
        t0 = time.time()
        if args.n_eos_seeds > 1:
            record['eos'] = eos_ensemble(atoms, calc,
                                         n_seeds=args.n_eos_seeds,
                                         perturb=args.eos_perturb,
                                         fractions=tuple(args.eos_fractions),
                                         fmax=args.eos_fmax,
                                         relax_steps=args.relax_steps)
        else:
            record['eos'] = eos_sweep(atoms, calc,
                                      fractions=tuple(args.eos_fractions),
                                      fmax=args.eos_fmax,
                                      relax_steps=args.relax_steps)
        record['eos']['t_s'] = time.time() - t0

    # 2b. EOS V₀ 를 **실제로** 적용한다 (GAP-3). 기본은 과거 동작 유지.
    atoms, record['cell_policy'] = maybe_apply_eos_v0(atoms, record, args, calc)

    # 3. Elastic
    if not args.no_elastic:
        t0 = time.time()
        try:
            record['cell_policy']['stress_at_elastic_ref'] = stress_report(atoms)
        except Exception as _e:
            record['cell_policy']['stress_at_elastic_ref'] = {'error': str(_e)}
        record['elastic'] = elastic_finite_strain(atoms, calc,
                                                  eps=args.elastic_eps,
                                                  fmax=args.elastic_fmax,
                                                  relax_steps=args.relax_steps)
        record['elastic']['t_s'] = time.time() - t0

    (work / 'postproc.json').write_text(json.dumps(record, indent=2, default=str))
    return record


def _selftest():
    """셀 정책 로직 검사 — UMA 없이 ASE EMT 로. **음성 경로 포함** (카드 v4 §4b).

    이 selftest 가 보는 것은 '갈림길이 제대로 갈리는가' 뿐이다.
    ⛔ 물리를 검증하지 않는다. EMT 는 Cu 용 장난감 퍼텐셜이다.
    """
    import numpy as _np
    from ase.build import bulk
    from ase.calculators.emt import EMT

    ok = fail = 0
    def chk(cond, label):
        nonlocal ok, fail
        if cond: ok += 1
        else: fail += 1; print(f"  ⛔ {label}")

    class A:                      # 가짜 args
        def __init__(self, **kw):
            self.apply_eos_v0 = False; self.fixed_shape_relax = False
            self.no_eos = False; self.no_elastic = False
            self.eos_fmax = 0.05; self.relax_steps = 50
            self.__dict__.update(kw)

    at = bulk('Cu', 'fcc', a=3.6, cubic=True) * (2, 2, 2)
    at.calc = EMT()
    V_post = at.get_volume()
    V0 = V_post * 1.08                      # post-anneal 과 **다른** V₀

    # ① 적용: 부피가 V₀ 가 되고 각도·길이비가 보존된다
    a2, rep = apply_v0_fixed_shape(at, V0, EMT(), fmax=0.05, relax_steps=50)
    chk(rep['applied'] and abs(a2.get_volume() - V0) / V0 < 1e-9,
        "V₀ 적용 후 부피 = V₀")
    ang0, ang2 = at.cell.angles(), a2.cell.angles()
    l0, l2 = at.cell.lengths(), a2.cell.lengths()
    chk(_np.allclose(ang0, ang2, atol=1e-9), "각도 보존")
    chk(_np.allclose(l0 / l0[0], l2 / l2[0], atol=1e-9), "길이비 보존 (등방 스케일)")

    # ② ⛔음성: V₀ 가 None 이면 적용하지 않고 구조를 그대로 돌려준다
    a3, rep3 = apply_v0_fixed_shape(at, None, EMT())
    chk((not rep3['applied']) and abs(a3.get_volume() - V_post) < 1e-12,
        "⛔음성: V₀=None → 미적용 + 구조 불변")

    # ③ ★ 갈림길 — 같은 record 로 두 갈래가 **다른 부피**를 탄성에 넘긴다
    rec = {'eos': {'V0': V0}}
    at_on = bulk('Cu', 'fcc', a=3.6, cubic=True) * (2, 2, 2); at_on.calc = EMT()
    a_on, pol_on = maybe_apply_eos_v0(at_on, rec, A(apply_eos_v0=True), EMT())
    at_off = bulk('Cu', 'fcc', a=3.6, cubic=True) * (2, 2, 2); at_off.calc = EMT()
    a_off, pol_off = maybe_apply_eos_v0(at_off, rec, A(apply_eos_v0=False), EMT())
    chk(pol_on['eos_v0_applied'] and abs(a_on.get_volume() - V0) / V0 < 1e-9,
        "갈림길 ON: 탄성이 V₀ 를 받는다")
    chk((not pol_off['eos_v0_applied']) and abs(a_off.get_volume() - V_post) < 1e-9,
        "⛔음성: 갈림길 OFF → 탄성이 **post-anneal 부피**를 받는다 (= GAP-3 의 실제 모습)")
    chk(abs(a_on.get_volume() - a_off.get_volume()) > 1e-6,
        "⛔음성: 두 갈래가 실제로 **다른 구조**를 넘긴다 (같으면 이 시험은 아무것도 안 본 것이다)")

    # ④ 적용 안 했으면 **경고가 박힌다** — 조용히 지나가지 않는가
    chk('⛔경고' in pol_off and 'GAP-3' in pol_off['⛔경고'],
        "⛔음성: 미적용 시 record 에 경고 문자열")
    chk('⛔경고' not in pol_on, "적용했으면 경고 없음")

    # ⑤ no_eos 면 경고도 안 단다 (EOS 를 안 돌렸으니 V₀ 자체가 없다)
    _, pol_noeos = maybe_apply_eos_v0(at, {}, A(no_eos=True), EMT())
    chk('⛔경고' not in pol_noeos, "no_eos → 경고 없음 (V₀ 가 애초에 없다)")

    # ⑥ 응력 보고: 평균압과 편차가 **따로** 나오고 산술이 맞는다
    sr = stress_report(at)
    sig = _np.array(sr['sigma_GPa'])
    chk(abs(sr['P_mean_GPa'] - _np.trace(sig) / 3) < 1e-9, "P_mean = trace/3")
    dev = sig - sr['P_mean_GPa'] * _np.eye(3)
    chk(abs(sr['deviatoric_max_abs_GPa'] - _np.abs(dev).max()) < 1e-9, "편차 최대성분")
    chk('영응력 판정 아님' in sr['⚠'], "응력 보고에 '영응력 판정 아님' 이 박혀 있다")

    # ⑦ ⛔음성: step0 정책이 기록에 남는가 (두 값이 달라야 한다)
    chk(maybe_apply_eos_v0(at, {}, A(no_eos=True), EMT())[1]['step0_relax'] !=
        maybe_apply_eos_v0(at, {}, A(no_eos=True, fixed_shape_relax=True), EMT())[1]['step0_relax'],
        "⛔음성: step0 정책 두 갈래가 기록에서 구분된다")

    # ⑧ ensemble 요약이 **선택을 숨기지 않는가** (2026-09-13 실측 사고)
    #   P2_Al2S3_B 시드 3개에서 r² 0.79/0.998/0.90 → 2개 실패, 그런데 std 가 0.0 이었다.
    #   0.0 은 "시드 간 완벽 일치" 로 읽힌다 — 정반대 뜻이다.
    def _fake_ens(rs):
        """eos_ensemble 의 요약 계산만 떼어 검증한다 (UMA 없이)."""
        physical = [r for r in rs if r.get('fit_quality_ok') and r.get('B0_GPa') is not None
                    and r.get('Bp') is not None and 0.0 < r['Bp'] < 15.0]
        b0s = [r['B0_GPa'] for r in rs if r.get('B0_GPa') is not None]
        _nfit = int(sum(1 for r in rs if r.get('fit_quality_ok')))
        _std = float(_np.std(b0s)) if len(b0s) >= 2 else None
        return {'n_B0': len(b0s), 'B0_GPa_std': _std, 'n_fit_ok': _nfit,
                '⚠_std_가_None_인_이유': (None if _std is not None else 'x'),
                '⛔_선택_경고': (None if _nfit == len(rs) else 'y')}

    _one = _fake_ens([{'fit_quality_ok': True, 'B0_GPa': 19.0, 'Bp': 1.3},
                      {'fit_quality_ok': False}, {'fit_quality_ok': False}])
    chk(_one['B0_GPa_std'] is None and _one['n_B0'] == 1,
        "⛔음성: B0 가 1개뿐이면 std 는 **None** 이다 (0.0 이 아니다 — 0.0 은 일치를 뜻한다)")
    chk(_one['⚠_std_가_None_인_이유'] is not None,
        "⛔음성: std 가 None 인 **이유**가 기록에 남는다 (빈칸으로 두지 않는다)")
    chk(_one['⛔_선택_경고'] is not None,
        "⛔음성: 시드가 하나라도 실패하면 '골라낸 값' 경고가 뜬다")

    _all = _fake_ens([{'fit_quality_ok': True, 'B0_GPa': 19.0, 'Bp': 4.0},
                      {'fit_quality_ok': True, 'B0_GPa': 20.0, 'Bp': 4.1},
                      {'fit_quality_ok': True, 'B0_GPa': 21.0, 'Bp': 3.9}])
    chk(_all['B0_GPa_std'] is not None and _all['B0_GPa_std'] > 0,
        "양성: 시드 3개가 다 통과하면 std 가 **실제 산포**를 낸다")
    chk(_all['⛔_선택_경고'] is None and _all['⚠_std_가_None_인_이유'] is None,
        "양성: 전원 통과면 경고가 **안 뜬다** (무조건 경고하는 게 아니다)")

    # ⑨ ⛔음성: fit_quality_ok 가 JSON 에서 **진짜 불리언**이어야 한다
    #   `json.dumps(..., default=str)` 이 np.bool_ 을 "False" 문자열로 만들면
    #   하류의 `if rec['fit_quality_ok']:` 가 **거짓을 참으로** 읽는다.
    _r2, _V0, _Bp = _np.float64(0.5), _np.float64(100.0), _np.float64(-3.0)
    _fit_ok = bool(_r2 >= 0.95 and 0 < _V0 < 500 and 0.0 < _Bp < 15.0)
    chk(type(_fit_ok) is bool, "⛔음성: fit_ok 가 np.bool_ 이 아니라 파이썬 bool 이다")
    _round = json.loads(json.dumps({'fit_quality_ok': _fit_ok}, default=str))
    chk(_round['fit_quality_ok'] is False,
        "⛔음성: JSON 왕복 뒤에도 False 다 (문자열 \"False\" 가 되면 하류가 참으로 읽는다)")

    print(f"  selftest: ⭕ {ok} · ⛔ {fail}")
    return 0 if fail == 0 else 1


def main():
    p = argparse.ArgumentParser(description=__doc__,
                               formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--winners', help='winners.json from select_winners.py')
    p.add_argument('--xyz', nargs='+', help='specific xyz files')
    p.add_argument('--out')          # ⚠ --selftest 는 out 이 필요 없다 (아래에서 검사)
    p.add_argument('--device', default='cuda')
    p.add_argument('--task', default='omat')
    # Step toggles
    p.add_argument('--no_anneal', action='store_true')
    p.add_argument('--no_eos', action='store_true')
    p.add_argument('--no_elastic', action='store_true')
    # Anneal params
    p.add_argument('--anneal_T', type=float, default=300,
                  help='Light anneal T (default 300K)')
    p.add_argument('--anneal_ps', type=float, default=20,
                  help='Light anneal time (default 20 ps)')
    # EOS params
    p.add_argument('--eos_fractions', nargs='+', type=float,
                  default=[0.94, 0.96, 0.98, 1.00, 1.02, 1.04, 1.06])
    p.add_argument('--eos_fmax', type=float, default=0.05)
    p.add_argument('--n_eos_seeds', type=int, default=1,
                   help='EOS ensemble size: N rattled seeds, best BM3 fit kept '
                        '(1 = single curve, current behaviour)')
    p.add_argument('--eos_perturb', type=float, default=0.1,
                   help='rattle stdev (Å) applied to EOS seeds > 0')
    # Elastic params
    p.add_argument('--elastic_eps', type=float, default=0.005,
                  help='Voigt strain magnitude')
    p.add_argument('--elastic_fmax', type=float, default=0.05)
    # General
    p.add_argument('--relax_steps', type=int, default=500)
    # ── 셀 정책 (2026-09-13, 회신 BP §4b) — 기본값은 과거 동작 그대로 ──
    p.add_argument('--apply_eos_v0', action='store_true',
                   help='EOS 가 낸 V0 를 **실제로 적용**해 고정셀 원자완화 후 탄성으로 넘긴다 '
                        '(기본 미적용 = GAP-3 그대로, 단 record 에 경고가 박힌다)')
    p.add_argument('--fixed_shape_relax', action='store_true',
                   help='0단계 relax 를 CellFilter 없이 고정셀로 한다 (각도·길이비 보존)')
    p.add_argument('--selftest', action='store_true',
                   help='셀 정책 로직만 검사 (UMA 없이 ASE EMT 로 — 음성 경로 포함)')
    p.add_argument('--limit', type=int, default=None,
                  help='Limit to first N structures (debug)')
    args = p.parse_args()
    if args.selftest:
        sys.exit(_selftest())
    if not args.out:
        p.error('--out 이 필요하다 (--selftest 제외)')


    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.winners:
        winners = json.loads(Path(args.winners).read_text())['winners']
        xyz_paths = [Path(w['xyz_file']) for w in winners
                    if Path(w.get('xyz_file', '')).exists()]
    elif args.xyz:
        xyz_paths = [Path(p) for p in args.xyz]
    else:
        p.error("Provide --winners or --xyz")

    if args.limit:
        xyz_paths = xyz_paths[:args.limit]

    # Resume
    summary_path = out / 'postproc_summary.json'
    done = {}
    if summary_path.exists():
        existing = json.loads(summary_path.read_text())
        done = {r['name']: r for r in existing.get('records', [])}
        print(f"Resume: {len(done)} already done")
    # NEW-D: use winner_name for resume check
    todo = [p for p in xyz_paths if winner_name(p) not in done]
    print(f"To process: {len(todo)}/{len(xyz_paths)}")

    print(f"Loading UMA-s-1p1 ({args.device})...")
    calc = load_uma(args.device, args.task)

    records = list(done.values())
    t_start = time.time()
    for i, xpath in enumerate(todo):
        wname = winner_name(xpath)
        print(f"\n[{i+1}/{len(todo)}] {wname}")
        try:
            rec = process_one(xpath, calc, out, args)
            records.append(rec)
            ann = rec.get('anneal', {})
            eos = rec.get('eos', {})
            ela = rec.get('elastic', {})
            # dict.get(k, default) only fires when key is ABSENT — None values
            # (e.g. eos.B0_GPa when Bp-gate rejected the fit) slip through and
            # crash :.1f format. Coerce None→NaN explicitly.
            _nz = lambda x: float('nan') if x is None else x
            print(f"  E={_nz(rec.get('E_post_anneal_per_atom')):.4f} "
                  f"B0={_nz(eos.get('B0_GPa')):.1f} GPa "
                  f"E_young={_nz(ela.get('E_young_GPa')):.1f} GPa "
                  f"Pugh={_nz(ela.get('pugh_ratio_GoverB')):.2f}")
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            records.append({'name': winner_name(xpath), 'error': str(e)})
        # Periodic save
        if (i + 1) % 3 == 0 or (i + 1) == len(todo):
            summary_path.write_text(json.dumps({
                'provenance': get_provenance(),
                'cli_args': vars(args),
                'n_done': len(records),
                'records': records,
            }, indent=2, default=str))

    print(f"\n{'='*60}")
    print(f"✓ Post-proc done: {len(records)} structures, "
          f"{time.time()-t_start:.0f}s")
    print(f"✓ Summary: {summary_path}")


if __name__ == '__main__':
    main()
