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
                 conv_thr='1.0d-8') -> str:
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

    print(f"  selftest: \u2b55 {ok} \u00b7 \u26d4 {fail}")
    return 0 if fail == 0 else 1


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
    p.add_argument('--top', type=int, default=10)
    p.add_argument('--out')          # --selftest 는 out 이 필요 없다
    p.add_argument('--ecutwfc', type=float, default=52)
    p.add_argument('--ecutrho', type=float, default=520)
    p.add_argument('--kpoints', default='2 2 1')
    args = p.parse_args()

    if args.selftest:
        sys.exit(_selftest())
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
