#!/usr/bin/env python
"""generate_dft_inputs.py — generate QE pw.in files for Top-N MLIP winners.

UMA-s-1p1 is a general MLIP that has known bias for sulfide systems
(Wang 2025 npj Comp Mater reports PES softening / Li diffusivity over-
estimation). For paper-grade B0 / band gap / Bader / PDOS we need DFT
spot-checks on the top MLIP candidates.

This tool reads the final FINAL_RANKING.json (from combine_rankings.py)
and generates QE input files for the top N structures, using the same
template as our Nd-EOS pipeline (52-atom cell, ecutwfc=52 Ry, K=2×2×1).

Each top winner gets its own directory with:
  relax.in        — QE relax input (cell+positions, BFGS)
  pseudo_list.txt — required pseudopotentials for this structure

Then user scp's the directory to KISTI and runs sbatch.

Usage:
  python3 tools/doping/generate_dft_inputs.py \\
      --ranking runs/tier_.../FINAL_RANKING.json \\
      --top 10 \\
      --out runs/tier_.../dft_inputs/
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

from ase.io import read

sys.path.insert(0, str(Path(__file__).parent))
from _provenance import get_provenance


PSEUDO_DIR_KISTI = '/scratch/x3430a02/kgy/manuscript_support/pseudo'

# Element → mass + pseudopotential filename (matches Nd-EOS prepare script)
PSEUDOS = {
    'Li': ('6.9410',   'li_pbe_v1_4_uspp_F.UPF'),
    'P':  ('30.9740',  'P_pbe-n-rrkjus_psl_1_0_0.UPF'),
    'S':  ('32.0650',  's_pbe_v1_4_uspp_F.UPF'),
    'Cl': ('35.4530',  'cl_pbe_v1_4_uspp_F.UPF'),
    'Br': ('79.9040',  'br_pbe_v1.4.uspp.F.UPF'),
    'I':  ('126.9045', 'I.pbe-n-rrkjus_psl.0.2.UPF'),
    'F':  ('18.9984',  'F.pbe-n-kjpaw_psl.0.1.UPF'),
    'O':  ('15.9994',  'O.pbe-n-kjpaw_psl.0.1.UPF'),
    'N':  ('14.0067',  'N.pbe-n-rrkjus_psl.0.1.UPF'),
    # Cations
    'Nd': ('144.242',  'Nd.paw.z_14.atompaw.wentzcovitch.v1.2.upf'),
    'La': ('138.9055', 'La.paw.z_11.atompaw.wentzcovitch.v1.2.upf'),
    'Sm': ('150.36',   'Sm.paw.z_14.atompaw.wentzcovitch.v1.2.upf'),
    'Y':  ('88.9059',  'Y.pbe-spn-kjpaw_psl.1.0.0.UPF'),
    'Sc': ('44.9559',  'Sc.pbe-spn-kjpaw_psl.0.2.3.UPF'),
    'Al': ('26.9815',  'Al.pbe-n-kjpaw_psl.1.0.0.UPF'),
    'Mg': ('24.3050',  'Mg.pbe-n-kjpaw_psl.0.3.0.UPF'),
    'Zn': ('65.38',    'Zn.pbe-dnl-kjpaw_psl.1.0.0.UPF'),
    'Ca': ('40.0780',  'Ca.pbe-spn-kjpaw_psl.1.0.0.UPF'),
    'Sr': ('87.62',    'Sr.pbe-spn-kjpaw_psl.1.0.0.UPF'),
    'Ba': ('137.327',  'Ba.pbe-spn-kjpaw_psl.1.0.0.UPF'),
    'Cu': ('63.546',   'Cu.pbe-dn-kjpaw_psl.1.0.0.UPF'),
    'Ag': ('107.868',  'Ag.pbe-n-kjpaw_psl.1.0.0.UPF'),
    'Ti': ('47.867',   'Ti.pbe-spn-kjpaw_psl.1.0.0.UPF'),
    'Zr': ('91.224',   'Zr.pbe-spn-kjpaw_psl.1.0.0.UPF'),
    'Hf': ('178.49',   'Hf.pbe-spn-kjpaw_psl.1.0.0.UPF'),
    'Si': ('28.0855',  'Si.pbe-n-kjpaw_psl.1.0.0.UPF'),
    'Ge': ('72.63',    'Ge.pbe-dn-kjpaw_psl.1.0.0.UPF'),
    'Sn': ('118.710',  'Sn.pbe-dn-kjpaw_psl.1.0.0.UPF'),
    'Sb': ('121.76',   'Sb.pbe-n-kjpaw_psl.1.0.0.UPF'),
    'Bi': ('208.98',   'Bi.pbe-dn-kjpaw_psl.1.0.0.UPF'),
    'B':  ('10.811',   'B.pbe-n-kjpaw_psl.1.0.0.UPF'),
    'V':  ('50.9415',  'V.pbe-spnl-kjpaw_psl.1.0.0.UPF'),
    'Nb': ('92.9064',  'Nb.pbe-spn-kjpaw_psl.1.0.0.UPF'),
    'Ta': ('180.9479', 'Ta.pbe-spn-kjpaw_psl.1.0.0.UPF'),
    'W':  ('183.84',   'W.pbe-spn-kjpaw_psl.1.0.0.UPF'),
    'Mo': ('95.95',    'Mo.pbe-spn-kjpaw_psl.1.0.0.UPF'),
    'Cr': ('51.9961',  'Cr.pbe-spn-kjpaw_psl.1.0.0.UPF'),
    'Mn': ('54.9380',  'Mn.pbe-spn-kjpaw_psl.0.3.1.UPF'),
    'Fe': ('55.845',   'Fe.pbe-spn-kjpaw_psl.0.2.1.UPF'),
    'Co': ('58.9332',  'Co.pbe-spn-kjpaw_psl.0.3.1.UPF'),
    'Ni': ('58.6934',  'Ni.pbe-spn-kjpaw_psl.1.0.0.UPF'),
}


def generate_pwin(atoms, prefix: str, ecutwfc=52, ecutrho=520,
                 kpoints='2 2 1', pseudo_dir=None, pp_names=None,
                 calculation='relax', nosym=True, occupations='smearing',
                 conv_thr='1.0d-8', nspin=1, start_mag=None, hubbard=None,
                 tot_magnetization=None) -> str:
    """⚠ 2026-09-08 — `occupations`/gamma k-점을 열었다 (힘 대조 카드 §4).
    금속용 smearing 을 절연체 단일점에 그대로 쓰면 힘에 smearing 항이 섞인다.
    `kpoints='gamma'` 를 주면 `K_POINTS gamma` 를 쓴다 (automatic 1 1 1 과 다르다 —
    gamma 전용 코드경로가 절반의 비용으로 같은 답을 낸다)."""
    # ⛔ pseudo_dir 를 KISTI 로 박아두면 다른 머신에서 pw.x 가 조용히 죽는다
    #   (gabia 는 /data/work/pseudo). 호출부가 줄 수 있게 열어둔다.
    species = sorted(set(atoms.get_chemical_symbols()))
    ntyp = len(species)
    nat = len(atoms)
    cell = atoms.cell.array
    frac = atoms.get_scaled_positions()
    syms = atoms.get_chemical_symbols()

    missing = [s for s in species if s not in PSEUDOS]
    if missing:
        raise ValueError(f"Missing pseudopotentials for {missing}; add to PSEUDOS")

    lines = []
    lines.append("&CONTROL")
    lines.append(f"    calculation = '{calculation}'")
    lines.append(f"    prefix      = '{prefix}'")
    lines.append("    outdir      = './tmp'")
    lines.append(f"    pseudo_dir  = '{pseudo_dir or PSEUDO_DIR_KISTI}'")
    lines.append("    tprnfor     = .true.")
    lines.append("    tstress     = .true.")
    lines.append("    etot_conv_thr = 1.0d-6")
    lines.append("    forc_conv_thr = 1.0d-4")
    lines.append("    nstep        = 200")
    lines.append("/")
    lines.append("&SYSTEM")
    lines.append("    ibrav       = 0")
    lines.append(f"    nat         = {nat}")
    lines.append(f"    ntyp        = {ntyp}")
    lines.append(f"    ecutwfc     = {ecutwfc}")
    lines.append(f"    ecutrho     = {ecutrho}")
    lines.append(f"    occupations = '{occupations}'")
    if occupations == 'smearing':
        lines.append("    smearing    = 'mv'")
        lines.append("    degauss     = 0.01")
    lines.append(f"    nosym       = .{str(bool(nosym)).lower()}.")
    # ── 스핀·U (2026-09-08 · Nd O-모티프 순위 재채점) ─────────────────────────
    #   ⚠ Nd³⁺ = 4f³ 이다. z≈14 PP(4f 원자가)를 쓰면서 nspin=1 로 두면 전자 3개가
    #     7겹 f 다중항에 **분수 점유**로 퍼져 계가 인공적으로 금속이 된다 (2026-08-07 실측:
    #     화학이 다른 세 상의 갭이 −0.021/−0.022/−0.028 eV 로 7 meV 안에 몰렸다).
    #   ⛔ 그리고 **씨앗 자화를 계마다 다르게 주면 총에너지 차가 무의미해진다** —
    #     비교하는 두 구조가 다른 f 점유로 수렴할 수 있다 (SDCP wave1 교훈).
    #     그래서 이 함수는 값을 정하지 않고 호출부가 준 것을 그대로 찍는다.
    if int(nspin) == 2:
        lines.append("    nspin       = 2")
        for el, m in sorted((start_mag or {}).items()):
            i = species.index(el) + 1              # ATOMIC_SPECIES 순서 = 아래 정렬과 같다
            lines.append(f"    starting_magnetization({i}) = {float(m)}")
        if tot_magnetization is not None:
            lines.append(f"    tot_magnetization = {float(tot_magnetization)}")
    lines.append("/")
    lines.append("&ELECTRONS")
    lines.append(f"    conv_thr     = {conv_thr}")
    lines.append("    mixing_beta  = 0.2")
    lines.append("    diagonalization = 'david'")
    lines.append("/")
    if calculation != 'scf':
        lines.append("&IONS")
        lines.append("    ion_dynamics = 'bfgs'")
        lines.append("/")
        lines.append("&CELL")
        lines.append("    cell_dynamics = 'bfgs'")
        lines.append("    press_conv_thr = 0.5")
        lines.append("/")
    lines.append("ATOMIC_SPECIES")
    for s in species:
        mass, ppf = PSEUDOS[s]
        # pp_names 로 실제 머신의 파일명을 덮어쓴다 (같은 pseudo 라도 구두점이 다르다)
        ppf = (pp_names or {}).get(s, ppf)
        lines.append(f"  {s}  {mass}  {ppf}")
    lines.append("CELL_PARAMETERS angstrom")
    for row in cell:
        lines.append(f"  {row[0]:14.10f}  {row[1]:14.10f}  {row[2]:14.10f}")
    lines.append("ATOMIC_POSITIONS crystal")
    for sym, fr in zip(syms, frac):
        lines.append(f"  {sym}  {fr[0]:14.10f}  {fr[1]:14.10f}  {fr[2]:14.10f}")
    if str(kpoints).strip().lower() == 'gamma':
        lines.append("K_POINTS gamma")
    else:
        lines.append("K_POINTS automatic")
        lines.append(f"  {kpoints} 0 0 0")
    # ⛔ 원자가에 없는 껍질에 U 를 걸면 QE 가 죽거나 **조용히 무시**한다 (2026-08-29 실측:
    #   frozen-4f PP 인데 `HUBBARD U Nd-4f 6.0` 을 찍고 있었다). 여기서는 호출부가 준
    #   목록을 그대로 찍되, 판별은 호출부 몫이다 — 이 함수는 PP 의 z_valence 를 모른다.
    #   형식은 tools/sei/build_dft_inputs.py 와 **같아야 한다** (갈라지면 두 트랙이 어긋난다).
    if hubbard:
        lines.append("HUBBARD (ortho-atomic)")
        for man in hubbard:
            lines.append(f"  U {man}")
    return "\n".join(lines) + "\n"


# ══════════════════════════════════════════════════════════════════════════
# 궤적 스냅샷 → DFT 단일점 (2026-09-08 · b2o3 UMA-vs-DFT 힘 대조 카드 §4)
#   카드: db/properties/b2o3_uma_vs_dft_force_prereg_2026_09_08.json (ratified 2판)
#
#   왜 여기에 붙였나 — `generate_pwin()` 이 이미 52/520 USPP 레시피와 `pp_names`
#   머신별 덮어쓰기를 갖고 있다. 새 파일을 만들면 그 레시피가 두 곳으로 갈라진다.
#
#   ⛔ 이 경로가 **못 하는 것**
#     · 표본을 고르지 않는다 — 프레임 번호는 카드의 결정적 규칙(시각→index)이 정한다.
#     · UMA 힘을 계산하지 않는다. 같은 `frame.xyz` 를 쓰라고 내보낼 뿐이다.
#     · pw.x 를 돌리지 않는다. 입력과 대조용 해시만 만든다.
#     · 유사포텐셜이 **물리적으로 맞는지**는 모른다 — 존재와 해시만 본다.
#: 카드 §4 가 못박은 파일명 (kgy /home/kgy/work/pseudo 실물 기준 · 구두점이 PSEUDOS 와 다르다)
PP_USPP_52_520 = {
    'Li': 'li_pbe_v1.4.uspp.F.UPF',
    'P':  'P.pbe-n-rrkjus_psl.1.0.0.UPF',
    'S':  's_pbe_v1.4.uspp.F.UPF',
    'Cl': 'cl_pbe_v1.4.uspp.F.UPF',
    'O':  'O.pbe-n-kjpaw_psl.0.1.UPF',
    'B':  'B.pbe-n-kjpaw_psl.1.0.0.UPF',
}


def frame_index_for_time(t_ps, save_fs):
    """카드의 결정적 규칙: index = round(t[ps] * 1000 / save_fs), 0-기준.

    ⚠ **half-up 반올림을 명시한다.** 파이썬 내장 `round` 는 은행가 반올림이라
      `round(0.5) == 0` 이다 — 표본 index 가 이런 규칙에 걸리면 재현 시 사람이
      다른 답을 낸다. 카드의 시각(10·20·30·40·50 ps)은 정확히 떨어져 이 분기를
      타지 않지만, 규칙은 문서와 코드가 같아야 하므로 여기서 고정한다.
    ⛔ 사람이 프레임을 고르는 경로를 두지 않는다 (§8 무효 조건)."""
    import math as _m
    if save_fs <= 0:
        raise ValueError("save_fs 는 양수여야 한다")
    return int(_m.floor(float(t_ps) * 1000.0 / float(save_fs) + 0.5))


def coord_digest(atoms):
    """좌표·격자의 sha256 — QE 입력과 UMA 입력이 **같은 배치**인지 기계로 대조한다.

    소수 10자리로 고정한다. 그 **아래**(1e-11 이하)는 xyz 왕복에서 살아남지 않으므로
    비교 기준이 못 된다. 1e-10 은 10자리에 그대로 보이므로 다른 배치로 센다."""
    import hashlib as _h
    parts = []
    for row in atoms.cell.array:
        parts.append(" ".join(f"{v:.10f}" for v in row))
    for sym, pos in zip(atoms.get_chemical_symbols(), atoms.get_positions()):
        parts.append(f"{sym} " + " ".join(f"{v:.10f}" for v in pos))
    return _h.sha256("\n".join(parts).encode()).hexdigest()


def preflight_pseudos(species, pseudo_dir, pp_names=None):
    """유사포텐셜 존재·해시. 하나라도 없으면 **거부**한다 (조용히 빠지면 pw.x 가 나중에 죽는다)."""
    import hashlib as _h
    pp = dict(PP_USPP_52_520)
    pp.update(pp_names or {})
    out, missing = {}, []
    for el in sorted(set(species)):
        name = pp.get(el)
        if not name:
            missing.append(f"{el}(파일명 미정)")
            continue
        f = Path(pseudo_dir) / name
        if not f.is_file():
            missing.append(f"{el}:{name}")
            continue
        out[el] = {"file": name,
                   "sha256": _h.sha256(f.read_bytes()).hexdigest()}
    if missing:
        raise FileNotFoundError("유사포텐셜 없음 — " + " · ".join(missing)
                                + f"  (pseudo_dir={pseudo_dir})")
    return out


def snapshots_from_traj(traj, times_ps, save_fs, out_dir, label, seed,
                        pseudo_dir, ecutwfc=52, ecutrho=520, pp_names=None):
    """궤적에서 카드 규칙대로 프레임을 뽑아 frame.xyz + scf.in + 대조 해시를 쓴다."""
    from ase.io import read as _read, write as _write
    out_dir = Path(out_dir)
    idxs = [frame_index_for_time(t, save_fs) for t in times_ps]
    frames = _read(str(traj), index=':')
    n = len(frames)
    bad = [(t, i) for t, i in zip(times_ps, idxs) if i >= n or i < 0]
    if bad:
        raise IndexError(f"궤적 프레임 {n}개인데 필요한 index {bad} 가 범위 밖이다 "
                         "— 창 밖 표본을 조용히 대체하지 않는다 (카드 §8)")
    pseudos = preflight_pseudos(frames[0].get_chemical_symbols(), pseudo_dir, pp_names)
    pp = dict(PP_USPP_52_520); pp.update(pp_names or {})
    recs = []
    for t, i in zip(times_ps, idxs):
        a = frames[i]
        tag = f"{label}_{seed}_t{int(round(float(t)))}ps"
        w = out_dir / tag
        w.mkdir(parents=True, exist_ok=True)
        _write(str(w / "frame.xyz"), a, format="extxyz")
        (w / "scf.in").write_text(generate_pwin(
            a, tag, ecutwfc, ecutrho, kpoints='gamma', pseudo_dir=pseudo_dir,
            pp_names=pp, calculation='scf', nosym=True, occupations='fixed'))
        recs.append({"tag": tag, "time_ps": float(t), "frame_index": i,
                     "n_atoms": len(a), "coord_sha256": coord_digest(a),
                     "cell": [[float(x) for x in r] for r in a.cell.array],
                     "path": str(w)})
    man = {"card": "db/properties/b2o3_uma_vs_dft_force_prereg_2026_09_08.json",
           "label": label, "seed": seed, "traj": str(traj),
           "n_frames_in_traj": n, "save_fs": float(save_fs),
           "규칙": "index = round(t_ps*1000/save_fs), 0-기준 — 사람이 고르지 않는다",
           "dft": {"code": "QE 7.4.1", "calculation": "scf", "kpoints": "gamma",
                   "occupations": "fixed", "ecutwfc": ecutwfc, "ecutrho": ecutrho,
                   "conv_thr": "1.0d-8", "tprnfor": True, "nosym": True},
           "pseudos": pseudos, "snapshots": recs,
           "⛔_이_파일이_보증하지_않는_것": "pw.x 수렴 · UMA 힘 계산 · 유사포텐셜의 물리적 적합성"}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"SNAPSHOTS_{label}_{seed}.json").write_text(
        json.dumps(man, ensure_ascii=False, indent=1))
    return man


# ── 회수: pw.x 출력 → DFT 라벨 붙은 extxyz (2026-09-08) ────────────────────
#   왜 여기인가 — 이 폴더 구조(<label>_<seed>_t<NN>ps/{frame.xyz,scf.in,scf.out})와
#   SNAPSHOTS json 을 만든 것이 이 도구다. 구조를 아는 쪽이 회수도 해야 갈라지지 않는다.
#   힘 **대조** 는 여기서 하지 않는다 — mlip_committee.py bench 가 그 일을 한다.
RY_TO_EV = 13.605693122994
RY_AU_TO_EV_A = RY_TO_EV / 0.529177210903        # Ry/bohr → eV/Å


def parse_pw_out(text):
    """pw.x scf 출력에서 (energy_eV, forces_eV_per_A, flags). 실패는 예외로 낸다.

    ⛔ 못 하는 것: 수렴의 **물리적** 타당성을 보지 않는다. 문자열이 있는지만 본다.
    ⚠ 자체 파서를 쓰는 이유 — ase 의 espresso-out 리더는 버전마다 요구 블록이 달라
      합성 시험을 만들기 어렵다. 우리가 읽는 세 블록은 QE 출력 형식에서 안정적이다.
    """
    import re as _re
    conv = "convergence has been achieved" in text
    done = "JOB DONE" in text
    m = _re.findall(r"^!\s+total energy\s+=\s+([-\d.]+)\s+Ry", text, _re.M)
    if not m:
        raise ValueError("총에너지 줄(`!    total energy`)이 없다 — scf 가 안 끝났다")
    energy = float(m[-1]) * RY_TO_EV
    fb = _re.search(r"Forces acting on atoms.*?\n(.*?)\n\s*\n", text, _re.S)
    if not fb:
        raise ValueError("힘 블록(`Forces acting on atoms`)이 없다 — tprnfor 를 확인하라")
    F = []
    for ln in fb.group(1).splitlines():
        g = _re.match(r"\s*atom\s+(\d+)\s+type\s+\d+\s+force\s*=\s*"
                      r"([-\d.Ee+]+)\s+([-\d.Ee+]+)\s+([-\d.Ee+]+)", ln)
        if g:
            F.append([float(g.group(2)) * RY_AU_TO_EV_A,
                      float(g.group(3)) * RY_AU_TO_EV_A,
                      float(g.group(4)) * RY_AU_TO_EV_A])
    if not F:
        raise ValueError("힘 블록은 있는데 `atom N type M force =` 줄을 하나도 못 읽었다")
    return energy, F, {"converged": conv, "job_done": done}


def parse_pw_in_positions(text):
    """scf.in 의 CELL_PARAMETERS(angstrom) + ATOMIC_POSITIONS(crystal) → (cell, symbols, cart)."""
    import re as _re
    cm = _re.search(r"CELL_PARAMETERS angstrom\n((?:\s*[-\d.Ee+]+\s+[-\d.Ee+]+\s+[-\d.Ee+]+\n){3})", text)
    pm = _re.search(r"ATOMIC_POSITIONS crystal\n((?:.*\n)+?)(?=K_POINTS|\Z)", text)
    if not (cm and pm):
        raise ValueError("scf.in 에서 CELL_PARAMETERS/ATOMIC_POSITIONS 를 못 읽었다")
    cell = [[float(x) for x in ln.split()] for ln in cm.group(1).strip().splitlines()]
    syms, frac = [], []
    for ln in pm.group(1).splitlines():
        t = ln.split()
        if len(t) == 4:
            syms.append(t[0]); frac.append([float(x) for x in t[1:]])
    cart = [[sum(frac[i][k] * cell[k][j] for k in range(3)) for j in range(3)]
            for i in range(len(frac))]
    return cell, syms, cart


def collect_results(out_dir, label, seed, max_dev_A=1e-6):
    """<out_dir> 의 이 (label, seed) 점들을 회수해 DFT 라벨 extxyz + RESULTS json 을 쓴다.

    ⛔ 실패한 점을 **빼고 진행하지 않는다** — 카드 §8 (19점으로 판정하지 않는다).
      실패가 있으면 기록하고 예외를 낸다.
    ⚠ 좌표 대조는 `frame.xyz` ↔ `scf.in` 이다. scf 는 원자를 움직이지 않으므로 이 둘이
      맞으면 두 계산이 같은 배치를 본 것이다. 완전한 비트 동일은 xyz↔분수좌표 왕복에서
      성립하지 않으므로 **문턱(기본 1e-6 Å)** 으로 판정하고 그 값을 기록한다.
    """
    from ase.io import read as _read, write as _write
    import numpy as _np
    out_dir = Path(out_dir)
    man_p = out_dir / f"SNAPSHOTS_{label}_{seed}.json"
    if not man_p.is_file():
        raise FileNotFoundError(f"스냅샷 원장이 없다: {man_p}")
    man = json.loads(man_p.read_text(encoding="utf-8"))
    frames, rows, bad = [], [], []
    for rec in man["snapshots"]:
        w = Path(rec["path"])
        at = _read(str(w / "frame.xyz"))
        try:
            if coord_digest(at) != rec["coord_sha256"]:
                raise ValueError("frame.xyz 가 원장 기록과 다르다 (파일이 바뀌었다)")
            _c, _s, cart = parse_pw_in_positions((w / "scf.in").read_text())
            if _s != at.get_chemical_symbols():
                raise ValueError("scf.in 과 frame.xyz 의 원소 순서가 다르다")
            dev = float(_np.abs(_np.asarray(cart) - at.get_positions()).max())
            if dev > max_dev_A:
                raise ValueError(f"좌표가 어긋난다: 최대 {dev:.3e} Å > {max_dev_A:.0e}")
            e, F, fl = parse_pw_out((w / "scf.out").read_text(errors="ignore"))
            if len(F) != len(at):
                raise ValueError(f"힘 {len(F)}개 · 원자 {len(at)}개")
            if not (fl["converged"] and fl["job_done"]):
                raise ValueError(f"미수렴/미완료 {fl}")
        except Exception as exc:
            bad.append({"tag": rec["tag"], "why": str(exc)}); continue
        at.calc = None
        from ase.calculators.singlepoint import SinglePointCalculator as _SPC
        at.calc = _SPC(at, energy=e, forces=_np.asarray(F))
        frames.append(at)
        rows.append({"tag": rec["tag"], "time_ps": rec["time_ps"],
                     "E_eV": e, "F_max_eVA": float(_np.abs(_np.asarray(F)).max()),
                     "coord_max_dev_A": dev, "coord_sha256": rec["coord_sha256"]})
    res = {"card": man["card"], "label": label, "seed": seed,
           "n_ok": len(rows), "n_expected": len(man["snapshots"]),
           "coord_check": {"기준": "frame.xyz ↔ scf.in 카티전 최대편차",
                           "문턱_A": max_dev_A,
                           "⚠": "비트 동일이 아니라 문턱 판정이다 — 분수좌표 왕복 때문."},
           "pseudos": man["pseudos"], "points": rows, "failed": bad}
    (out_dir / f"RESULTS_{label}_{seed}.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1))
    if bad:
        raise RuntimeError(f"{label}/{seed}: {len(bad)}점 실패 — " +
                           " · ".join(f"{b['tag']}({b['why']})" for b in bad) +
                           "  ⛔ 카드 §8: 빠뜨린 채 판정하지 않는다")
    _write(str(out_dir / f"labeled_{label}_{seed}.xyz"), frames, format="extxyz")
    return res


def _selftest():
    import tempfile, hashlib as _h
    from ase import Atoms
    from ase.io import write as _write
    ok = fail = 0

    def chk(c, m):
        nonlocal ok, fail
        print(("  \u2b55 " if c else "  \u26d4 ") + m)
        ok, fail = ok + bool(c), fail + (not c)

    chk(frame_index_for_time(10, 100) == 100, "t=10 ps · save_fs 100 fs → index 100")
    chk(frame_index_for_time(50, 100) == 500, "t=50 ps → index 500")
    chk(frame_index_for_time(0.05, 100) == 1,
        "half-up 반올림 (0.05 ps → index 1 · 파이썬 기본 round 면 0 이 된다)")
    try:
        frame_index_for_time(10, 0); chk(False, "\u26d4음성: save_fs=0 을 받으면 안 된다")
    except ValueError:
        chk(True, "\u26d4음성: save_fs=0 거부")

    a1 = Atoms("Li2", positions=[[0, 0, 0], [1, 1, 1]], cell=[5, 5, 5], pbc=True)
    a2 = Atoms("Li2", positions=[[0, 0, 0], [1, 1, 1.000000000001]], cell=[5, 5, 5], pbc=True)
    a3 = Atoms("Li2", positions=[[0, 0, 0], [1, 1, 1.001]], cell=[5, 5, 5], pbc=True)
    chk(coord_digest(a1) == coord_digest(a2), "10자리 **아래**(1e-12) 차이는 같은 배치")
    a2b = Atoms("Li2", positions=[[0, 0, 0], [1, 1, 1.0000000001]], cell=[5, 5, 5], pbc=True)
    chk(coord_digest(a1) != coord_digest(a2b), "⛔음성: 1e-10 은 10자리에 보이므로 다른 배치")
    chk(coord_digest(a1) != coord_digest(a3), "\u26d4음성: 0.001 Å 다르면 다른 배치")

    txt = generate_pwin(a1, "t", calculation='scf', kpoints='gamma',
                        occupations='fixed', pseudo_dir='/x',
                        pp_names={'Li': 'li_pbe_v1.4.uspp.F.UPF'})
    chk("K_POINTS gamma" in txt and "automatic" not in txt, "gamma k-점 경로")
    chk("occupations = 'fixed'" in txt and "degauss" not in txt,
        "\u26d4음성: fixed 인데 degauss 가 남으면 안 된다")
    chk("tprnfor     = .true." in txt and "&IONS" not in txt, "scf + 힘 출력 · 이완 절 없음")

    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "pp").mkdir()
        (d / "pp" / "li_pbe_v1.4.uspp.F.UPF").write_bytes(b"x")
        got = preflight_pseudos(["Li"], d / "pp")
        chk(got["Li"]["sha256"] == _h.sha256(b"x").hexdigest(), "유사포텐셜 해시 기록")
        try:
            preflight_pseudos(["Li", "S"], d / "pp")
            chk(False, "\u26d4음성: 없는 유사포텐셜을 통과시키면 안 된다")
        except FileNotFoundError as e:
            chk("S:" in str(e), "\u26d4음성: 빠진 원소를 이름으로 지목")

        tr = d / "traj.xyz"
        _write(str(tr), [a1] * 6, format="extxyz")
        m = snapshots_from_traj(tr, [0.1, 0.2], 100, d / "out", "lbl", "s2", d / "pp")
        chk(len(m["snapshots"]) == 2 and m["snapshots"][1]["frame_index"] == 2,
            "스냅샷 2개 · index 규칙 적용")
        chk((d / "out" / "lbl_s2_t0ps" / "scf.in").is_file(), "scf.in 생성")
        chk(m["snapshots"][0]["coord_sha256"] == coord_digest(a1), "좌표 해시가 frame 과 일치")
        try:
            snapshots_from_traj(tr, [10.0], 100, d / "out2", "lbl", "s2", d / "pp")
            chk(False, "\u26d4음성: 범위 밖 프레임을 조용히 대체하면 안 된다")
        except IndexError as e:
            chk("범위 밖" in str(e), "\u26d4음성: 창 밖 표본 거부")

        # ── 회수 경로 ──────────────────────────────────────────────────
        e, F, fl = parse_pw_out(
            "!    total energy              =     -10.00000000 Ry\n"
            "     convergence has been achieved in  9 iterations\n"
            "     Forces acting on atoms (cartesian axes, Ry/au):\n\n"
            "     atom    1 type  1   force =     0.10000000    0.00000000    0.00000000\n"
            "     atom    2 type  1   force =    -0.10000000    0.00000000    0.00000000\n"
            "\n     JOB DONE.\n")
        chk(abs(e - (-10.0 * RY_TO_EV)) < 1e-9 and fl["converged"] and fl["job_done"],
            "pw.x 에너지·수렴·완료 파싱")
        chk(len(F) == 2 and abs(F[0][0] - 0.1 * RY_AU_TO_EV_A) < 1e-9,
            "힘 단위 변환 Ry/au → eV/Å")
        try:
            parse_pw_out("아무것도 없음"); chk(False, "\u26d4음성: 빈 출력을 통과시키면 안 된다")
        except ValueError:
            chk(True, "\u26d4음성: 총에너지 없는 출력 거부")
        try:
            parse_pw_out("!    total energy              =     -1.0 Ry\n")
            chk(False, "\u26d4음성: 힘 없는 출력을 통과시키면 안 된다")
        except ValueError as _x:
            chk("힘 블록" in str(_x), "\u26d4음성: 힘 블록 없는 출력 거부 (tprnfor 안내)")
        _pin = (d / "out" / "lbl_s2_t0ps" / "scf.in").read_text()
        _c, _s2, _cart = parse_pw_in_positions(_pin)
        import numpy as _np2
        chk(_s2 == ["Li", "Li"] and
            float(_np2.abs(_np2.asarray(_cart) - a1.get_positions()).max()) < 1e-9,
            "scf.in 분수좌표 → 카티전이 frame 과 일치")

    # \u2500\u2500 \uc2a4\ud540\u00b7U \ubc29\ucd9c (2026-09-08 \u00b7 Nd O-\ubaa8\ud2f0\ud504 \uc7ac\ucc44\uc810) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    from ase import Atoms as _At
    _nd = _At('NdOLi', positions=[[0, 0, 0], [2, 0, 0], [0, 2, 0]], cell=[8, 8, 8], pbc=True)
    _pp = {'Nd': 'Nd.paw.z_14.atompaw.wentzcovitch.v1.2.upf'}
    _plain = generate_pwin(_nd, 'x', calculation='scf', pp_names=_pp, pseudo_dir='/p')
    # \u26d4\uc74c\uc131: \uc548 \uc2dc\ud0a4\uba74 \uc548 \ub098\uc628\ub2e4 (\uae30\ubcf8\uc774 \uc870\uc6a9\ud788 \uc2a4\ud540\u00b7U \ub97c \ucf1c\uba74 \uc61b \uacc4\uc0b0\uacfc \ubabb \ube44\uad50\ud55c\ub2e4)
    chk('nspin' not in _plain and 'HUBBARD' not in _plain,
        "\u26d4\uc74c\uc131: nspin/HUBBARD \ub294 **\uc548 \uc8fc\uba74 \uc548 \ucc0d\ud78c\ub2e4**")
    _spin = generate_pwin(_nd, 'x', calculation='scf', pp_names=_pp, pseudo_dir='/p',
                          nspin=2, start_mag={'Nd': 0.3}, hubbard=['Nd-4f 6.0'],
                          tot_magnetization=6)
    _sp = sorted(set(_nd.get_chemical_symbols()))          # ATOMIC_SPECIES \uc21c\uc11c
    chk(f'starting_magnetization({_sp.index("Nd") + 1}) = 0.3' in _spin,
        "starting_magnetization \uc774 **Nd \uc758 \uc885 \ubc88\ud638**\uc5d0 \ubd99\ub294\ub2e4")
    chk('nspin       = 2' in _spin and 'tot_magnetization = 6' in _spin, "nspin\u00b7\ucd1d\uc790\ud654 \ubc29\ucd9c")
    chk('HUBBARD (ortho-atomic)' in _spin and '  U Nd-4f 6.0' in _spin,
        "HUBBARD \uce74\ub4dc \ud615\uc2dd\uc774 tools/sei/build_dft_inputs.py \uc640 \uac19\ub2e4")
    # \u26d4\uc74c\uc131: \uc885 \ubc88\ud638\ub97c 1\ub85c \ubc15\uc544 \ub450\uba74 \uc6d0\uc18c \uc21c\uc11c\uac00 \ubc14\ub014 \ub54c **\uc5c9\ub6b1\ud55c \uc6d0\uc18c\uc5d0 \uc790\ud654\uac00 \uac78\ub9b0\ub2e4**
    _nd2 = _At('LiNdO', positions=[[0, 0, 0], [2, 0, 0], [0, 2, 0]], cell=[8, 8, 8], pbc=True)
    _s2x = generate_pwin(_nd2, 'x', calculation='scf', pp_names=_pp, pseudo_dir='/p',
                         nspin=2, start_mag={'Nd': 0.3})
    chk(f'starting_magnetization({sorted(set(_nd2.get_chemical_symbols())).index("Nd") + 1}) = 0.3'
        in _s2x, "\u26d4\uc74c\uc131: \uc6d0\uc18c \uad6c\uc131\uc774 \ub2ec\ub77c\ub3c4 Nd \uc758 \ubc88\ud638\ub97c \ub2e4\uc2dc \uc13c\ub2e4")

    # \u2500\u2500 \uad6c\uc870\ud30c\uc77c \u2192 scf (--from_xyz) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    with tempfile.TemporaryDirectory() as _td:
        _d = Path(_td)
        (_d / "ps").mkdir()
        for _f in ('li_pbe_v1.4.uspp.F.UPF', 'O.pbe-n-kjpaw_psl.0.1.UPF', 'ND.upf'):
            (_d / "ps" / _f).write_text("x")
        _a = _At('LiLiO', positions=[[0, 0, 0], [2, 0, 0], [0, 2, 0]], cell=[8, 8, 8], pbc=True)
        _p1 = _d / "one_post_relax.xyz"; _a.write(str(_p1))
        _m = scf_from_xyz([_p1], _d / "o", str(_d / "ps"), nspin=2,
                          start_mag={'Li': 0.1}, tot_mag_per={'Li': 2})
        chk((_d / "o" / "one" / "scf.in").is_file(), "--from_xyz: <out>/<name>/scf.in \ubc30\uce58")
        chk(_m['cells'][0]['tot_magnetization'] == 4.0,
            "tot_magnetization \uc744 **\uc140\ubcc4 \uc6d0\uc790 \uc218**\ub85c \uacc4\uc0b0\ud55c\ub2e4 (Li 2\uac1c \u00d7 2)")
        chk((_d / "o" / "one" / "struct.xyz").is_file(), "\uc6d0\ubcf8 \uad6c\uc870\ub97c \uc606\uc5d0 \ub0a8\uae34\ub2e4 (\uc7ac\ud604)")
        chk(bool(json.loads((_d / "o" / "MANIFEST.json").read_text()).get("gate")),
            "MANIFEST \uc5d0 gate(\ube44\uad50 \ub2e8\uc704\u00b7\ubb34\ud6a8 \uc870\uac74)\uac00 \uc2e4\ub9b0\ub2e4")
        # \u26d4\uc74c\uc131: \uc720\uc0ac\ud3ec\ud150\uc15c\uc774 \uc5c6\uc73c\uba74 **\uc785\ub825\uc744 \ub9cc\ub4e4\uc9c0 \uc54a\ub294\ub2e4** (\ub098\uc911\uc5d0 pw.x \uac00 \uc8fd\ub294\ub2e4)
        try:
            scf_from_xyz([_p1], _d / "o2", str(_d / "nope"))
            chk(False, "\u26d4\uc74c\uc131: \uc5c6\ub294 pseudo_dir \ub85c\ub3c4 \uc785\ub825\uc744 \ub9cc\ub4e4\uba74 \uc548 \ub41c\ub2e4")
        except Exception:
            chk(True, "\u26d4\uc74c\uc131: pseudo \uc5c6\uc73c\uba74 \uc785\ub825 \uc0dd\uc131 \uac70\ubd80")

    print(f"  selftest: \u2b55 {ok} \u00b7 \u26d4 {fail}")
    return 0 if fail == 0 else 1


# ══════════════════════════════════════════════════════════════════════════
# 완화된 구조 파일 → scf 단일점 (2026-09-08 · Nd O-모티프 UMA 순위 DFT 재채점)
#
#   왜 여기냐 — `generate_pwin()` 의 52/520 레시피와 `pp_names` 머신별 덮어쓰기를
#   그대로 쓴다. 산출 배치(`<out>/<name>/scf.in`)도 `--from_traj` 와 같게 두어
#   **같은 러너**(run_force_check_scf.sh)가 순차 실행한다.
#
#   ⛔ 이 경로가 **못 하는 것**
#     · 순위를 판정하지 않는다 — 총에너지를 낼 뿐이다. 비교 규칙은 아래 gate 가 적는다.
#     · **다른 조성끼리 비교할 수 있는지 모른다.** n=4(54원자)와 n=5(66원자)는 조성이
#       달라 총에너지도 원자당 에너지도 가로질러 비교하면 안 된다. manifest 에 적어만 둔다.
#     · 스핀 상태가 **의도한 상태로 수렴했는지** 모른다. 그건 회수 단계가 본다.
#     · PP 가 물리적으로 맞는지 모른다 (존재·해시만).
#: 이 비교가 **무엇을 판정하고 무엇을 판정하지 않는가** — 산출물에 항상 실린다.
SCF_COMPARE_GATE = {
    "비교_단위": "같은 조성(같은 n) 안에서만. n=4(54원자)와 n=5(66원자)는 조성이 "
         "달라 총에너지도 원자당 에너지도 가로질러 비교하지 않는다.",
    "상태_선택_정책": ("네 셀 전부 같은 씨앗 자화·같은 U·같은 cutoff/k점. "
               "값을 통일하는 것이 아니라 **정책**을 통일한다."),
    "스핀_구속_선언": ("tot_magnetization 을 Nd 개수×3(4f³, FM 정렬)로 **고정**한다. "
               "이건 자유 바닥상태가 아니라 **선언된 구속**이다 — 두 셀이 서로 "
               "다른 f 점유로 수렴하는 것을 막으려는 것이고, 쌍의 조성이 같으므로 "
               "같은 구속이 걸린다(SDCP wave1 의 '제약된 기준 − 자유로운 복합체' "
               "사고를 피한다). ⚠ 따라서 이 에너지는 **절대값으로 인용 금지**이고 "
               "같은 구속끼리의 차이로만 읽는다. AFM 이 진짜 바닥이어도 Nd 는 이 "
               "비교에서 구경꾼이라 O 모티프 순위는 거의 안 움직인다는 가정 위에 "
               "있다 — 그 가정을 확인하려면 AFM 대조를 따로 돌려야 한다."),
    "무효_조건": ("쌍 안에서 수렴 총자화가 다르면 그 쌍의 ΔE 는 무효다 — "
          "다른 f 점유끼리 뺀 값이 된다 (SDCP wave1 교훈)."),
    "판정하는_것": "같은 n 안의 O 모티프 순위가 UMA 와 같은 부호인가.",
    "판정하지_않는_것": "절대 에너지 · 조성 간 비교 · 형성에너지.",
}


def scf_from_xyz(paths, out_dir, pseudo_dir, ecutwfc=52, ecutrho=520,
                 kpoints='2 2 1', pp_names=None, nspin=1, start_mag=None,
                 hubbard=None, tot_mag_per=None, gate=None):
    """구조 파일 여러 개 → `<out>/<name>/scf.in` + manifest.

    `tot_mag_per` = {원소: 원자당 모멘트} — 셀마다 그 원소 개수 × 값으로 tot_magnetization
    을 계산한다 (셀마다 원자 수가 다르므로 상수로 박으면 틀린다).
    """
    from ase.io import read as _read
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    # ⛔ gate 는 **함수가 항상 싣는다.** CLI 에만 두었더니 함수를 직접 부른 경로에서
    #   조용히 사라졌다 (자체시험이 잡았다) — 선언이 빠진 산출물은 나중에 근거가 없다.
    _g = dict(SCF_COMPARE_GATE); _g.update(gate or {})
    man = {"provenance": get_provenance(), "created": _dt_now(),
           "settings": {"ecutwfc": ecutwfc, "ecutrho": ecutrho, "kpoints": kpoints,
                        "nspin": nspin, "starting_magnetization": start_mag or {},
                        "hubbard": hubbard or [], "tot_mag_per_atom": tot_mag_per or {},
                        "occupations": "smearing(mv,0.01)", "calculation": "scf"},
           "gate": _g, "cells": []}
    species_all = set()
    for pth in paths:
        a = _read(str(pth))
        species_all |= set(a.get_chemical_symbols())
    pp = preflight_pseudos(sorted(species_all), pseudo_dir, pp_names)
    man["pseudos"] = pp
    for pth in paths:
        pth = Path(pth)
        a = _read(str(pth))
        name = pth.stem.replace("_post_relax", "")
        d = out / name; d.mkdir(parents=True, exist_ok=True)
        syms = a.get_chemical_symbols()
        tm = None
        if int(nspin) == 2 and tot_mag_per:
            tm = sum(syms.count(el) * float(m) for el, m in tot_mag_per.items())
        txt = generate_pwin(a, name, ecutwfc=ecutwfc, ecutrho=ecutrho,
                            kpoints=kpoints, pseudo_dir=pseudo_dir,
                            pp_names={el: v["file"] for el, v in pp.items()},
                            calculation='scf', occupations='smearing',
                            nspin=nspin, start_mag=start_mag, hubbard=hubbard,
                            tot_magnetization=tm)
        (d / "scf.in").write_text(txt)
        (d / "struct.xyz").write_text(Path(pth).read_text())
        man["cells"].append({"name": name, "source": str(pth), "n_atoms": len(a),
                             "formula": a.get_chemical_formula(),
                             "tot_magnetization": tm,
                             "coord_sha256": coord_digest(a)})
    (out / "MANIFEST.json").write_text(json.dumps(man, ensure_ascii=False, indent=1) + "\n")
    return man


def _dt_now():
    import datetime as _d
    return _d.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                               formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--ranking',
                  help='FINAL_RANKING.json from combine_rankings.py')
    p.add_argument('--from_traj', help='궤적에서 스냅샷을 뽑아 scf 입력을 만든다 (힘 대조 카드 §4)')
    p.add_argument('--label'); p.add_argument('--seed')
    p.add_argument('--times_ps', nargs='+', type=float, default=[10, 20, 30, 40, 50])
    p.add_argument('--save_fs', type=float, default=100.0)
    p.add_argument('--pseudo_dir', default='/home/kgy/work/pseudo')
    p.add_argument('--selftest', action='store_true')
    p.add_argument('--collect', action='store_true',
                  help='pw.x 출력을 회수해 DFT 라벨 extxyz + RESULTS json (--out --label --seed)')
    p.add_argument('--top', type=int, default=10)
    p.add_argument('--out')          # --selftest 는 out 이 필요 없다
    p.add_argument('--ecutwfc', type=float, default=52)
    p.add_argument('--ecutrho', type=float, default=520)
    p.add_argument('--kpoints', default='2 2 1')
    # ── 구조 파일 → scf 단일점 (Nd O-모티프 재채점) ─────────────────────────
    p.add_argument('--from_xyz', nargs='+',
                  help='완화된 구조 파일들 → <out>/<name>/scf.in (같은 러너로 순차 실행)')
    p.add_argument('--nspin', type=int, default=1, choices=(1, 2))
    p.add_argument('--start_mag', nargs='*', default=[],
                  help='원소=씨앗자화 (예: Nd=0.3). ⚠ 비교하는 셀 전부 **같은 값**이어야 한다')
    p.add_argument('--tot_mag_per', nargs='*', default=[],
                  help='원소=원자당 모멘트 (예: Nd=3) → 셀별 개수×값으로 tot_magnetization')
    p.add_argument('--hubbard', nargs='*', default=[],
                  help='HUBBARD 항목 (예: "Nd-4f 6.0"). ⛔ 원자가에 없는 껍질에 걸지 말 것')
    p.add_argument('--pp', nargs='*', default=[],
                  help='유사포텐셜 파일명 덮어쓰기 (예: Nd=Nd.paw.z_14.atompaw...upf)')
    args = p.parse_args()

    def _kv(items):
        d = {}
        for s in items:
            if '=' not in s:
                p.error(f'--- 형식은 원소=값 이다: {s!r}')
            k, v = s.split('=', 1)
            d[k] = v
        return d

    if args.selftest:
        sys.exit(_selftest())
    if args.collect:
        if not (args.out and args.label and args.seed):
            p.error('--collect 는 --out --label --seed 가 필요하다')
        r = collect_results(args.out, args.label, args.seed)
        print(f"✓ {args.label}/{args.seed}: {r['n_ok']}/{r['n_expected']}점 회수 "
              f"· 좌표 최대편차 {max(x['coord_max_dev_A'] for x in r['points']):.2e} Å")
        return
    if args.from_xyz:
        if not args.out:
            p.error('--from_xyz 는 --out 이 필요하다')
        _sm = {k: float(v) for k, v in _kv(args.start_mag).items()}
        _tm = {k: float(v) for k, v in _kv(args.tot_mag_per).items()}
        if args.nspin == 2 and not _sm:
            p.error('--nspin 2 인데 --start_mag 이 없다 — 씨앗을 안 주면 셀마다 다른 '
                    '상태로 수렴할 수 있고 그러면 총에너지 차가 무의미해진다')
        man = scf_from_xyz(args.from_xyz, args.out, args.pseudo_dir,
                           args.ecutwfc, args.ecutrho, args.kpoints,
                           pp_names=_kv(args.pp), nspin=args.nspin,
                           start_mag=_sm, hubbard=args.hubbard,
                           tot_mag_per=_tm)
        print(f"✓ {len(man['cells'])}셀 → {args.out}  (nspin={args.nspin}"
              f"{' · U=' + ','.join(args.hubbard) if args.hubbard else ''})")
        for c in man['cells']:
            print(f"    {c['name']:36s} {c['formula']:26s} n={c['n_atoms']:3d} "
                  f"tot_mag={c['tot_magnetization']}  {c['coord_sha256'][:12]}")
        print("  ⚠ 비교는 같은 n 안에서만. MANIFEST.json 의 gate 를 읽어라.")
        return
    if args.from_traj:
        if not args.out:
            p.error('--from_traj 는 --out 이 필요하다')
        if not (args.label and args.seed):
            p.error('--from_traj 는 --label 과 --seed 가 필요하다 (산출물 이름·계보)')
        man = snapshots_from_traj(args.from_traj, args.times_ps, args.save_fs,
                                  args.out, args.label, args.seed, args.pseudo_dir,
                                  args.ecutwfc, args.ecutrho)
        print(f"✓ {args.label}/{args.seed}: 스냅샷 {len(man['snapshots'])}개 → {args.out}")
        for r in man['snapshots']:
            print(f"    {r['tag']}  frame {r['frame_index']}  n={r['n_atoms']}  {r['coord_sha256'][:12]}")
        return
    if not (args.ranking and args.out):
        p.error('--ranking(+--out) 또는 --from_traj 또는 --selftest')

    data = json.loads(Path(args.ranking).read_text())
    rows = data.get('rows', [])[:args.top]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # Resume: skip if relax.in already exists
    summary = {'provenance': get_provenance(), 'generated': [], 'skipped': [],
               'failed': []}
    for i, row in enumerate(rows, 1):
        name = row.get('name', f'top{i}')
        work = out / f'rank{i:02d}_{name}'
        relax_in = work / 'relax.in'
        if relax_in.exists():
            summary['skipped'].append(name)
            print(f"  [skip] {name} (relax.in exists)")
            continue
        # We need the xyz to read coordinates — look up from screening
        xyz_candidates = [
            row.get('xyz_input'), row.get('xyz_file'),
            row.get('_anneal', {}).get('post_relax_xyz'),
        ]
        xyz_path = next((Path(x) for x in xyz_candidates
                        if x and Path(x).exists()), None)
        if xyz_path is None:
            summary['failed'].append({'name': name, 'reason': 'no xyz found'})
            print(f"  ⚠ {name}: no xyz available")
            continue
        try:
            atoms = read(str(xyz_path))
            work.mkdir(parents=True, exist_ok=True)
            relax_in.write_text(generate_pwin(atoms, name,
                                              args.ecutwfc, args.ecutrho,
                                              args.kpoints))
            # Copy xyz for traceability
            shutil.copy(str(xyz_path), str(work / 'init.xyz'))
            # List required pseudos
            species = sorted(set(atoms.get_chemical_symbols()))
            (work / 'pseudo_list.txt').write_text(
                '\n'.join(PSEUDOS[s][1] for s in species) + '\n')
            summary['generated'].append({
                'name': name, 'path': str(work),
                'rank': i,
                'composite_score': row.get('score_combined'),
                'B0_GPa_MLIP': row.get('B0_GPa'),
                'E_young_GPa_MLIP': row.get('E_young_GPa'),
            })
            print(f"  ✓ rank{i:02d}_{name} → {work}")
        except Exception as e:
            summary['failed'].append({'name': name, 'reason': str(e)})
            print(f"  ✗ {name}: {e}")

    (out / 'dft_input_summary.json').write_text(
        json.dumps(summary, indent=2, default=str))
    print(f"\n✓ Generated {len(summary['generated'])} DFT inputs "
          f"({len(summary['skipped'])} skipped, "
          f"{len(summary['failed'])} failed)")
    print(f"\nNext: scp -r {out} <KISTI>:/path/  then sbatch <run script>")


if __name__ == '__main__':
    main()
