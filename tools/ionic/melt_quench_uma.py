#!/usr/bin/env python3
"""melt_quench_uma.py — LPSCl@Li₂S **1층**: 비정질 계면상 후보를 UMA NPT melt-quench 로 만들고 판정 지표를 찍는다.

카드: db/properties/lpscl_li2s_interphase_prereg_2026_09_11.json
      §2 ⭐_1층_개정_2026_09_11b (타깃·판정 지표) · §4 ⭐_1층_게이트 G1–G4

후보 (조성은 복합체 x 와 무관 — LPSCl 1 f.u. → Li₃PS₄ + LiCl, Li₂S 는 소모되지 않는다)
  A              Li₄PS₄Cl × n_fu(40) = 400 원자   a-Li₃PS₄·LiCl 균질 (Cl 이 유리망 안에)
  B              Li₃PS₄  × n_fu(50) = 400 원자   a-Li₃PS₄ 단독 (Cl 은 결정 LiCl 로 빠졌다는 가정)
  control_li7ps6 Li₇PS₆  × n_fu(28) = 392 원자   대조잡 — 1저자 원가설. 스스로 Li₃PS₄-like + Li₂S-like 로 갈라지나

절차 (G2 담금질 속도 선언 · G3 시드 ≥ 5 · G4 NPT 0 GPa, 밀도는 결과)
  ① 무작위 셀 — PS₄ 사면체(P–S 2.05 Å)를 **단위로** 무작위 배치(무작위 회전) + 자유 S·Li·Cl 무작위, 서로 다른 원자쌍 최소거리
     2.0 Å, 시작 밀도 1.2 g/cm³ (NPT 가 고친다)
  ② 짧은 FIRE 완화 (fmax 1.0 eV/Å · ≤ 200 스텝) — 겹침만 푼다
  ③ NPT Berendsen 0 GPa: T_melt(1200 K) 유지 --melt_ps → **선형 담금질** T_melt → T_final(300 K), 속도 --quench_rate [K/s]
     (10¹² K/s 면 900 ps) → T_final 유지 --hold_ps
  ④ 최종 FIRE 완화 (fmax 0.05) → final.xyz + final.vasp (VESTA 규율: xyz+POSCAR 쌍) + traj.xyz(--save_ps 간격) + result.json

판정 지표 (문턱은 카드에 있다 — 이 도구는 **값만 찍는다**)
  · PS₄ 보존율 = P 중 S 이웃(≤ 2.6 Å)이 정확히 4개인 비율 · P–S–P 가교 S 수 · P–P(≤ 2.4 Å) 수
  · Cl 환경 = Cl 의 Li 배위수(≤ 3.0 Å) 분포 · 6-배위 분율 · Cl–Cl 최근접 거리 분포와 3.4–3.9 Å 창 분율
  · Li₂S 국소질서 = S 중 Li 이웃(≤ 2.8 Å)이 8개 이상인 비율
  · 밀도 · 부분 g(r) (P–S · S–S · Li–S · Li–Cl · Cl–Cl) → Origin-ready CSV

⛔ 이 도구가 못 하는 것
  · 판정하지 않는다 — 지표를 찍고, 문턱 대조는 카드·사람이 한다.
  · UMA 오차를 모른다 — G1(QE 단일점 대조)은 별도 도구·별도 잡이다.
  · 담금질 속도가 물리적으로 타당한지 보증 못 한다 — 선언하고 기록할 뿐이다 (G2).
  · 결정화 여부를 못 가른다 — g(r)·배위수만 준다. XRD 지문은 tools/xrd/phase_fingerprint.py.
  · 2층(전도)을 하지 않는다 — 최종 구조를 넘길 뿐이다. 시드 하나만 돌리며, 앙상블 통계는 호출자가 모은다 (G3).
  · Berendsen 은 앙상블이 엄밀하지 않다 — 구조 생성용이지 수송 계산용이 아니다.
  · **밀도가 낮게 나온 원인을 스스로 못 가른다** — 배선인지 UMA·구조인지는 --npt_control 대조 잡이 가른다.
    그 대조도 "배로스탯이 ρ_UMA(0K) 를 지키나" 까지만 말한다. UMA 자신의 밀도 오차는 그 판정 밖이다.

  python3 tools/ionic/melt_quench_uma.py --system A --seed 1 --quench_rate 1e12 --out_root /data/work/runs/li2s_layer1
  python3 tools/ionic/melt_quench_uma.py --npt_control db/structures/sei_li2s_mp-1153.vasp --out_root /data/work/runs/li2s_layer1
  python3 tools/ionic/melt_quench_uma.py --selftest
"""
from __future__ import annotations
import argparse, json, math, os, pathlib, sys, time
import numpy as np

MASS = {"Li": 6.94, "P": 30.974, "S": 32.06, "Cl": 35.45}
EV_A3_TO_GPA = 160.21766208
# ⭐ 배로스탯 설정은 여기 한 곳에만 있다 — 대조 잡(--npt_control)이 생산 런과 **같은 설정**을 쓰지 않으면
#    아무것도 증명하지 못한다. 바꾸려면 여기서 바꾸고, 두 경로가 같이 따라간다.
BARO = {"taut_fs": 100.0, "taup_fs": 1000.0, "compressibility_au": 8.0}   # 8.0 Å³/eV ≈ 1/(20 GPa)
SYSTEMS = {                       # 식단위 조성 · 기본 n_fu
    "A":              ({"Li": 4, "P": 1, "S": 4, "Cl": 1}, 40),
    "B":              ({"Li": 3, "P": 1, "S": 4, "Cl": 0}, 50),
    "control_li7ps6": ({"Li": 7, "P": 1, "S": 6, "Cl": 0}, 28),
}
PS_BOND = 2.05          # Å — PS₄ 단위 초기 P–S
MIN_DIST = 2.0          # Å — Li 가 낀 쌍의 최소거리
MIN_DIST_ANION = 3.0    # Å — P·S·Cl 끼리(다른 단위) 최소거리: P 에 제3의 S 가 2.6 Å 안에 못 들어온다 (PS₄ 보존율 정의와 정합)
R_PS, R_PP, R_CLLI, R_SLI = 2.6, 2.4, 3.0, 2.8     # 지표 컷오프 (카드 §2 판정_지표)
CLCL_WIN = (3.4, 3.9)   # LiCl 결정 Cl–Cl 3.63 Å 창

# ───────────────────────── 기하 유틸 (numpy · MIC · 직교/비직교 셀) ─────────────────────────
def mic_dists(A, B, cell):
    """A(n,3) 와 B(m,3) 사이 최소상 거리 행렬 (n,m)."""
    cinv = np.linalg.inv(cell)
    d = A[:, None, :] - B[None, :, :]
    f = d @ cinv
    f -= np.round(f)
    return np.linalg.norm(f @ cell, axis=2)


def counts_within(A, B, cell, rcut, exclude_self=False):
    D = mic_dists(A, B, cell)
    if exclude_self:
        np.fill_diagonal(D, np.inf)
    return (D <= rcut).sum(axis=1), D


# ───────────────────────── ① 무작위 셀 ─────────────────────────
def _tetra_vertices(rng):
    """정사면체 4 꼭짓점(단위벡터)에 무작위 회전."""
    v = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], float) / math.sqrt(3)
    q = rng.normal(size=4); q /= np.linalg.norm(q)            # 무작위 단위 사원수 → 회전행렬
    a, b, c, d = q
    R = np.array([[a*a+b*b-c*c-d*d, 2*(b*c-a*d), 2*(b*d+a*c)],
                  [2*(b*c+a*d), a*a-b*b+c*c-d*d, 2*(c*d-a*b)],
                  [2*(b*d-a*c), 2*(c*d+a*b), a*a-b*b-c*c+d*d]])
    return v @ R.T


def build_random_cell(system, seed, density_g_cm3=1.2, n_fu=None, min_dist=MIN_DIST, max_tries=60000):
    """PS₄ 단위 + 자유 원자를 무작위로 채운 입방 셀. → (symbols list, positions (N,3), cell (3,3))"""
    if system not in SYSTEMS:
        raise SystemExit(f"⛔ 모르는 계 {system!r} — 카드에 있는 것: {sorted(SYSTEMS)}")
    comp, n_default = SYSTEMS[system]
    n_fu = int(n_fu or n_default)
    counts = {k: v * n_fu for k, v in comp.items() if v}
    mass_g = sum(MASS[k] * v for k, v in counts.items()) / 6.02214076e23
    L = (mass_g / density_g_cm3 * 1e24) ** (1.0 / 3.0)                 # Å
    cell = np.eye(3) * L
    rng = np.random.default_rng(seed)
    n_P = counts.get("P", 0)
    n_S_free = counts.get("S", 0) - 4 * n_P
    if n_S_free < 0:
        raise SystemExit(f"⛔ S 가 PS₄ 를 만들기에 모자란다 ({counts})")
    sym, pos = [], []
    def ok(new, new_sym):
        if not pos:
            return True
        D = mic_dists(np.asarray(new), np.asarray(pos), cell)
        heavy_new = np.array([s != "Li" for s in new_sym])[:, None]
        heavy_old = np.array([s != "Li" for s in sym])[None, :]
        need = np.where(heavy_new & heavy_old, MIN_DIST_ANION, min_dist)
        return bool((D >= need).all())
    tries = 0
    for _ in range(n_P):                                                 # PS₄ 단위
        while True:
            tries += 1
            if tries > max_tries:
                raise SystemExit(f"⛔ {system} 밀도 {density_g_cm3} g/cm³ 에 {max_tries}회 안에 못 채웠다 — 밀도를 낮춰라")
            p = rng.uniform(0, L, 3)
            unit = np.vstack([p, p + PS_BOND * _tetra_vertices(rng)])
            if ok(unit, ["P", "S", "S", "S", "S"]):
                sym += ["P", "S", "S", "S", "S"]; pos += unit.tolist(); break
    for el, n in (("S", n_S_free), ("Cl", counts.get("Cl", 0)), ("Li", counts.get("Li", 0))):
        for _ in range(n):
            while True:
                tries += 1
                if tries > max_tries:
                    raise SystemExit(f"⛔ {system} 밀도 {density_g_cm3} g/cm³ 에 {max_tries}회 안에 못 채웠다 — 밀도를 낮춰라")
                p = rng.uniform(0, L, 3)
                if ok([p], [el]):
                    sym.append(el); pos.append(p.tolist()); break
    return sym, np.asarray(pos), cell


# ───────────────────────── 판정 지표 ─────────────────────────
def indicators(sym, pos, cell):
    sym = np.asarray(sym); pos = np.asarray(pos, float); cell = np.asarray(cell, float)
    P = pos[sym == "P"]; S = pos[sym == "S"]; Li = pos[sym == "Li"]; Cl = pos[sym == "Cl"]
    out = {}
    if len(P) and len(S):
        nS, D_PS = counts_within(P, S, cell, R_PS)
        out["PS4_fraction"] = float((nS == 4).mean())
        out["P_S_coord_hist"] = {int(k): int(v) for k, v in zip(*np.unique(nS, return_counts=True))}
        nP_per_S = (D_PS.T <= R_PS).sum(axis=1)
        out["bridging_S_P2S7_like"] = int((nP_per_S >= 2).sum())
        nPP, _ = counts_within(P, P, cell, R_PP, exclude_self=True)
        out["P_P_bonds_P2S6_like"] = int(nPP.sum() // 2)
    if len(Cl):
        nLi, _ = counts_within(Cl, Li, cell, R_CLLI) if len(Li) else (np.zeros(len(Cl), int), None)
        out["Cl_Li_coord_hist"] = {int(k): int(v) for k, v in zip(*np.unique(nLi, return_counts=True))}
        out["Cl_6coord_fraction"] = float((nLi == 6).mean())
        if len(Cl) > 1:
            Dcc = mic_dists(Cl, Cl, cell); np.fill_diagonal(Dcc, np.inf)
            nn = Dcc.min(axis=1)
            out["ClCl_nearest_A"] = {"median": float(np.median(nn)), "min": float(nn.min()),
                                     "in_window_fraction": float(((nn >= CLCL_WIN[0]) & (nn <= CLCL_WIN[1])).mean()),
                                     "window_A": list(CLCL_WIN)}
    if len(S) and len(Li):
        nLiS, _ = counts_within(S, Li, cell, R_SLI)
        out["S_Li8_fraction_Li2S_like"] = float((nLiS >= 8).mean())
        out["S_Li_coord_hist"] = {int(k): int(v) for k, v in zip(*np.unique(nLiS, return_counts=True))}
    vol = abs(np.linalg.det(cell))
    mass_g = sum(MASS[s] for s in sym) / 6.02214076e23
    out["density_g_cm3"] = float(mass_g / (vol * 1e-24))
    out["n_atoms"] = int(len(sym)); out["cell_A"] = cell.tolist()
    return out


def partial_gr(sym, pos, cell, pairs=(("P", "S"), ("S", "S"), ("Li", "S"), ("Li", "Cl"), ("Cl", "Cl")), rmax=8.0, dr=0.05):
    sym = np.asarray(sym); pos = np.asarray(pos, float); vol = abs(np.linalg.det(cell))
    edges = np.arange(0, rmax + dr, dr); rc = 0.5 * (edges[1:] + edges[:-1])
    cols = {"r_A": rc}
    for a, b in pairs:
        A = pos[sym == a]; B = pos[sym == b]
        if not len(A) or not len(B):
            continue
        D = mic_dists(A, B, cell)
        if a == b:
            np.fill_diagonal(D, np.inf)
        h, _ = np.histogram(D[D < rmax], bins=edges)
        shell = 4 * math.pi * rc ** 2 * dr
        cols[f"g_{a}{b}"] = h / (len(A) * len(B) / vol) / shell
    return cols


# ───────────────────────── ③ MD ─────────────────────────
def make_calc(device="cuda", turbo=False):
    """UMA-s-1p1 · omat. turbo=True 면 fairchem 의 MD 용 inference_settings="turbo" 를 시도한다
    (원자 수·조성이 고정된 MD 전용 · 보통 ~2배). 이 fairchem 판에 없으면 **기본으로 내려가고 화면에 적는다** —
    조용히 다른 설정으로 돌지 않는다 (결과 파일 plan.json 에 실제 모드를 남긴다)."""
    from fairchem.core import pretrained_mlip
    from fairchem.core.calculate.ase_calculator import FAIRChemCalculator
    mode = "default"
    if turbo:
        try:
            pu = pretrained_mlip.get_predict_unit("uma-s-1p1", device=device, inference_settings="turbo"); mode = "turbo"
        except Exception as e:
            print(f"⚠ turbo 불가 ({type(e).__name__}: {e}) — 기본 모드로 돈다")
            pu = pretrained_mlip.get_predict_unit("uma-s-1p1", device=device)
    else:
        pu = pretrained_mlip.get_predict_unit("uma-s-1p1", device=device)
    calc = FAIRChemCalculator(pu, task_name="omat"); calc._mq_mode = mode
    return calc


def pressure_GPa(atoms):
    """순간 압력 [GPa] = -tr(σ)/3. 응력을 못 주는 계산기면 NaN (조용히 0 으로 적지 않는다)."""
    try:
        sig = np.asarray(atoms.get_stress(voigt=True), float)
    except Exception:
        return float("nan")
    return float(-(sig[0] + sig[1] + sig[2]) / 3.0 * EV_A3_TO_GPA)


def density_g_cm3(atoms):
    """g/cm³. 카드 밖 원소(대조 잡에 아무 결정이나 넣을 수 있다)는 ASE 질량으로 — MASS 는 4원소뿐이라
    예전 같으면 KeyError 로 죽었다. 생산 런 경로는 MASS 를 그대로 쓰므로 숫자가 안 바뀐다."""
    sy = atoms.get_chemical_symbols()
    m = sum(MASS[x] for x in sy) if all(x in MASS for x in sy) else float(atoms.get_masses().sum())
    return float(m / 6.02214076e23 / (atoms.get_volume() * 1e-24))


def run_npt_control(atoms, calc, out, *, T_K, ps, dt_fs, save_ps=1.0, tol=0.03, log=print):
    """⭐ 배로스탯 **대조 잡** — 알려진 결정을 같은 NPT 배선에 넣어 밀도를 지키는지 본다.

    비정질 밀도가 낮게 나왔을 때 원인이 두 갈래다: (ⓐ 우리 배선·단위가 틀렸다 / ⓑ UMA 또는 구조가 그렇다).
    이 잡이 그 둘을 가른다 — 결정을 **UMA 0 K 가변셀로 먼저 완화**해 ρ_UMA(0K) 를 얻고(= UMA 자신의 답),
    그 구조로 **생산 런과 같은 BARO 설정** NPT 를 돌려 ρ_NPT 를 얻는다.
      · |ρ_NPT/ρ_UMA(0K) − 1| ≤ tol → 배선 정상. 비정질 밀도는 배로스탯 탓이 아니다.
      · 벗어나면 → 배선·단위 문제. 비정질 결과를 해석하기 전에 여기를 고친다.
    ρ_UMA(0K) 와 파일 밀도의 차이는 **UMA 자신의 오차**라 tol 판정에 넣지 않는다 — 따로 찍어서 사람이 본다.
    """
    from ase import units
    from ase.md.nptberendsen import NPTBerendsen
    from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, Stationary
    from ase.optimize import FIRE
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    atoms.calc = calc
    rho_file = density_g_cm3(atoms)
    try:
        from ase.filters import FrechetCellFilter as _CF
    except ImportError:
        from ase.constraints import ExpCellFilter as _CF        # 구버전 ASE
    FIRE(_CF(atoms), logfile=str(out / "cellrelax.log")).run(fmax=0.02, steps=500)
    rho_0K = density_g_cm3(atoms); P_0K = pressure_GPa(atoms)
    log(f"  [대조] ρ(파일) {rho_file:.3f} → ρ_UMA(0K) {rho_0K:.3f} g/cm³ (P {P_0K:+.3f} GPa)")
    MaxwellBoltzmannDistribution(atoms, temperature_K=T_K, rng=np.random.default_rng(0)); Stationary(atoms)
    dt = dt_fs * units.fs
    dyn = NPTBerendsen(atoms, dt, temperature_K=T_K, pressure_au=0.0,
                       taut=BARO["taut_fs"] * units.fs, taup=BARO["taup_fs"] * units.fs,
                       compressibility_au=BARO["compressibility_au"])
    n = int(round(ps * 1000 / dt_fs)); save_int = max(1, int(round(save_ps * 1000 / dt_fs)))
    tlog = open(out / "thermo.csv", "w"); tlog.write("t_ps,T_K,T_set_K,density_g_cm3,volume_A3,E_pot_eV,P_GPa\n")
    rows = []
    for step in range(n + 1):
        if step % save_int == 0:
            r, P = density_g_cm3(atoms), pressure_GPa(atoms)
            rows.append((step * dt_fs / 1000, r, P))
            tlog.write(f"{step*dt_fs/1000:.3f},{atoms.get_temperature():.1f},{T_K:.1f},{r:.4f},"
                       f"{atoms.get_volume():.2f},{atoms.get_potential_energy():.4f},{P:.4f}\n"); tlog.flush()
        if step < n:
            dyn.run(1)
    tlog.close()
    half = [x for x in rows if x[0] >= rows[-1][0] / 2] or rows
    rho_npt = float(np.mean([x[1] for x in half])); P_npt = float(np.mean([x[2] for x in half]))
    drift = rho_npt / rho_0K - 1.0
    res = {"kind": "npt_barostat_control", "T_K": T_K, "ps": ps, "dt_fs": dt_fs, "baro": dict(BARO),
           "n_atoms": len(atoms), "composition": {e: atoms.get_chemical_symbols().count(e) for e in sorted(set(atoms.get_chemical_symbols()))},
           "rho_file_g_cm3": rho_file, "rho_UMA_0K_g_cm3": rho_0K, "P_UMA_0K_GPa": P_0K,
           "rho_NPT_mean_last_half_g_cm3": rho_npt, "P_NPT_mean_last_half_GPa": P_npt,
           "drift_vs_UMA_0K": drift, "tol": tol, "plumbing_ok": bool(abs(drift) <= tol),
           "UMA_vs_file": rho_0K / rho_file - 1.0,
           "⛔": "판정은 배선(배로스탯·단위)에 한정된다. UMA 자신의 밀도 오차(UMA_vs_file)는 이 판정 밖이다."}
    (out / "control.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    return res


def schedule(T_melt, T_final, quench_rate_K_s, dt_fs):
    if quench_rate_K_s is None or quench_rate_K_s <= 0:
        raise SystemExit("⛔ --quench_rate [K/s] 를 주어라 (G2: 담금질 속도는 결과 보기 전에 선언한다). 기본값은 없다.")
    quench_ps = (T_melt - T_final) / quench_rate_K_s * 1e12
    n = int(round(quench_ps * 1000.0 / dt_fs))
    return quench_ps, n


def run_melt_quench(atoms, calc, out, *, seed, T_melt, T_final, melt_ps, quench_rate, hold_ps, dt_fs, save_ps,
                    pre_relax=True, log=print):
    from ase import units
    from ase.io import write
    from ase.md.nptberendsen import NPTBerendsen
    from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, Stationary
    from ase.optimize import FIRE
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    atoms.calc = calc
    if pre_relax:
        FIRE(atoms, logfile=str(out / "prerelax.log")).run(fmax=1.0, steps=200)
    MaxwellBoltzmannDistribution(atoms, temperature_K=T_melt, rng=np.random.default_rng(seed)); Stationary(atoms)
    dt = dt_fs * units.fs
    dyn = NPTBerendsen(atoms, dt, temperature_K=T_melt, pressure_au=0.0,
                       taut=BARO["taut_fs"] * units.fs, taup=BARO["taup_fs"] * units.fs,
                       compressibility_au=BARO["compressibility_au"])
    quench_ps, n_q = schedule(T_melt, T_final, quench_rate, dt_fs)
    n_m = int(round(melt_ps * 1000 / dt_fs)); n_h = int(round(hold_ps * 1000 / dt_fs))
    save_int = max(1, int(round(save_ps * 1000 / dt_fs)))
    trj = out / "traj.xyz"; trj.unlink(missing_ok=True)
    tlog = open(out / "thermo.csv", "w"); tlog.write("t_ps,T_K,T_set_K,density_g_cm3,volume_A3,E_pot_eV,P_GPa\n")
    step = 0; t0 = time.time()
    def record(T_set):
        nonlocal step
        if step % save_int == 0:
            write(str(trj), atoms, format="extxyz", append=True)
            vol = atoms.get_volume(); rho = sum(MASS[s] for s in atoms.get_chemical_symbols()) / 6.02214076e23 / (vol * 1e-24)
            tlog.write(f"{step*dt_fs/1000:.3f},{atoms.get_temperature():.1f},{T_set:.1f},{rho:.4f},{vol:.2f},"
                       f"{atoms.get_potential_energy():.4f},{pressure_GPa(atoms):.4f}\n"); tlog.flush()
    chunk = 50
    for phase, n_steps, Tfun in (("melt", n_m, lambda i: T_melt),
                                 ("quench", n_q, lambda i: T_melt - (T_melt - T_final) * i / max(1, n_q)),
                                 ("hold", n_h, lambda i: T_final)):
        i = 0
        while i < n_steps:
            T_set = Tfun(i); dyn.set_temperature(temperature_K=T_set)
            k = min(chunk, n_steps - i)
            for _ in range(k):
                record(T_set); dyn.run(1); step += 1
            i += k
            if (i // chunk) % 200 == 0:
                log(f"  [{phase}] {i}/{n_steps} T_set={T_set:.0f} K T={atoms.get_temperature():.0f} K "
                    f"ρ={sum(MASS[s] for s in atoms.get_chemical_symbols())/6.02214076e23/(atoms.get_volume()*1e-24):.3f} "
                    f"({(time.time()-t0)/60:.1f} min)")
                sys.stdout.flush()   # ⛔ 로그 리다이렉트 시 블록 버퍼링 — 안 하면 진행 줄이 몇 시간 뒤에 뜬다
    record(T_final); tlog.close()
    FIRE(atoms, logfile=str(out / "final_relax.log")).run(fmax=0.05, steps=2000)
    write(str(out / "final.xyz"), atoms, format="extxyz")
    write(str(out / "final.vasp"), atoms, format="vasp", direct=True, sort=True)
    return {"quench_ps": quench_ps, "n_steps": {"melt": n_m, "quench": n_q, "hold": n_h}, "wall_min": (time.time() - t0) / 60}


def write_gr_csv(cols, path):
    keys = list(cols)
    with open(path, "w") as f:
        f.write(",".join(keys) + "\n")
        for i in range(len(cols["r_A"])):
            f.write(",".join(f"{cols[k][i]:.5f}" for k in keys) + "\n")


# ───────────────────────── selftest ─────────────────────────
def _selftest():
    ok = bad = 0
    def chk(c, m):
        nonlocal ok, bad
        print(("  ⭕ " if c else "  ⛔ ") + m); ok += c; bad += (not c)
    # ① 무작위 셀
    for sysname, n_exp in (("A", 400), ("B", 400), ("control_li7ps6", 392)):
        sym, pos, cell = build_random_cell(sysname, seed=1)
        comp, n_fu = SYSTEMS[sysname]
        cnt = {e: sym.count(e) for e in set(sym)}
        chk(len(sym) == n_exp and all(cnt.get(k, 0) == v * n_fu for k, v in comp.items()), f"{sysname}: 원자 {n_exp} · 조성 정확")
        D = mic_dists(pos, pos, cell); np.fill_diagonal(D, np.inf)
        P = np.where(np.asarray(sym) == "P")[0]
        ps = np.array([sorted(D[i])[:4] for i in P])
        chk(abs(ps - PS_BOND).max() < 1e-6, f"{sysname}: 모든 P 의 최근접 4 S 가 {PS_BOND} Å (PS₄ 단위)")
        # 단위 밖 최소거리
        unit = -np.ones(len(sym), int)
        for u, i in enumerate(P): unit[i:i+5] = u
        mask = (unit[:, None] != unit[None, :]) | (unit[:, None] < 0)
        heavy = np.array([x != "Li" for x in sym])
        hh = heavy[:, None] & heavy[None, :]
        chk(D[mask & hh].min() >= MIN_DIST_ANION - 1e-9 and D[mask & ~hh].min() >= MIN_DIST - 1e-9,
            f"{sysname}: 단위 밖 최소거리 — 음이온·P 끼리 ≥ {MIN_DIST_ANION} Å · Li 쌍 ≥ {MIN_DIST} Å")
    ind = indicators(sym, pos, cell)
    chk(abs(ind["density_g_cm3"] - 1.2) < 0.02, "밀도 지표가 시작 밀도 1.2 를 재현한다")
    try:
        build_random_cell("A", seed=1, density_g_cm3=6.0, max_tries=3000); ok_d = False
    except SystemExit as e:
        ok_d = "밀도" in str(e)
    chk(ok_d, "⛔음성: 6 g/cm³ 는 못 채우고 멈춘다 (조용히 겹치게 두지 않는다)")
    try:
        build_random_cell("Z", seed=1); ok_z = False
    except SystemExit:
        ok_z = True
    chk(ok_z, "⛔음성: 카드에 없는 계 이름은 거부")
    try:
        schedule(1200, 300, None, 2.0); ok_q = False
    except SystemExit as e:
        ok_q = "quench_rate" in str(e)
    chk(ok_q, "⛔음성: 담금질 속도를 안 주면 시작하지 않는다 (G2)")
    qp, nq = schedule(1200, 300, 1e12, 2.0)
    chk(abs(qp - 900.0) < 1e-9 and nq == 450000, "10¹² K/s · 1200→300 K = 900 ps = 450000 스텝 @ 2 fs")
    # ② 지표 — 합성 구조
    symA, posA, cellA = build_random_cell("A", seed=3)
    iA = indicators(symA, posA, cellA)
    chk(iA["PS4_fraction"] == 1.0 and iA["bridging_S_P2S7_like"] == 0, "무작위 PS₄ 단위 셀: PS₄ 보존율 1.0 · 가교 0")
    first_S = next(i for i, x in enumerate(symA) if x == "S")
    symB = [x for i, x in enumerate(symA) if i != first_S]; posB = np.delete(posA, first_S, axis=0)   # S 하나를 없앤다
    chk(abs(indicators(symB, posB, cellA)["PS4_fraction"] - (1 - 1 / 40)) < 1e-9, "⛔음성: S 하나를 없애면 보존율 39/40")
    a = 5.13; n = 3; rs = []; rsym = []                                    # 암염 LiCl
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for base, el in (((0, 0, 0), "Cl"), ((0.5, 0.5, 0), "Cl"), ((0.5, 0, 0.5), "Cl"), ((0, 0.5, 0.5), "Cl"),
                                 ((0.5, 0, 0), "Li"), ((0, 0.5, 0), "Li"), ((0, 0, 0.5), "Li"), ((0.5, 0.5, 0.5), "Li")):
                    rs.append(((np.array(base) + [i, j, k]) * a).tolist()); rsym.append(el)
    iL = indicators(rsym, np.array(rs), np.eye(3) * a * n)
    chk(iL["Cl_6coord_fraction"] == 1.0 and iL["ClCl_nearest_A"]["in_window_fraction"] == 1.0
        and abs(iL["ClCl_nearest_A"]["median"] - a / math.sqrt(2)) < 1e-6, "암염 LiCl: Cl 6-배위 1.0 · Cl–Cl 3.63 Å 창 분율 1.0")
    a2 = 5.71; qs = []; qsym = []                                          # 반형석 Li₂S
    for i in range(2):
        for j in range(2):
            for k in range(2):
                for base in ((0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)):
                    qs.append(((np.array(base) + [i, j, k]) * a2).tolist()); qsym.append("S")
                for base in ((.25, .25, .25), (.75, .75, .75), (.75, .25, .25), (.25, .75, .75),
                             (.25, .75, .25), (.75, .25, .75), (.25, .25, .75), (.75, .75, .25)):
                    qs.append(((np.array(base) + [i, j, k]) * a2).tolist()); qsym.append("Li")
    iQ = indicators(qsym, np.array(qs), np.eye(3) * a2 * 2)
    chk(iQ["S_Li8_fraction_Li2S_like"] == 1.0, "반형석 Li₂S: S 의 Li 8-배위 분율 1.0")
    chk(iA["S_Li8_fraction_Li2S_like"] < 0.2, "무작위 A 셀은 Li₂S 국소질서가 거의 없다 (< 0.2)")
    gr = partial_gr(symA, posA, cellA)
    chk("g_PS" in gr and abs(gr["r_A"][int(np.argmax(gr["g_PS"]))] - PS_BOND) < 0.06, "g_PS 첫 봉우리가 2.05 Å")
    # ③ MD 연기 시험 — fairchem 없이 LJ 로 배선만 (n_fu 2 · 몇 스텝)
    import tempfile
    from ase import Atoms
    from ase.calculators.lj import LennardJones
    symS, posS, cellS = build_random_cell("A", seed=5, n_fu=2, density_g_cm3=0.8)
    at = Atoms(symbols=symS, positions=posS, cell=cellS, pbc=True)
    with tempfile.TemporaryDirectory() as td:
        info = run_melt_quench(at, LennardJones(sigma=2.5, epsilon=0.05, rc=6.0), td, seed=5, T_melt=600, T_final=300,
                               melt_ps=0.02, quench_rate=3e14, hold_ps=0.02, dt_fs=2.0, save_ps=0.004, pre_relax=False, log=lambda *a: None)
        n_frames = open(os.path.join(td, "traj.xyz")).read().count("Lattice=")
        chk(info["n_steps"]["quench"] == 500 and n_frames >= 5, f"LJ 연기: 담금질 500 스텝 · 궤적 {n_frames} 프레임 기록")
        chk(os.path.isfile(os.path.join(td, "final.xyz")) and os.path.isfile(os.path.join(td, "final.vasp"))
            and os.path.isfile(os.path.join(td, "thermo.csv")), "final.xyz + final.vasp + thermo.csv 생성 (xyz·POSCAR 쌍)")
        hdr = open(os.path.join(td, "thermo.csv")).readline().strip().split(",")
        row = open(os.path.join(td, "thermo.csv")).readlines()[1].strip().split(",")
        chk(hdr[-1] == "P_GPa" and len(row) == len(hdr) and row[-1] not in ("", "nan"),
            f"thermo.csv 에 배로스탯 제어변수 P_GPa 가 실제 값으로 기록된다 ({row[-1]} GPa)")
    # ④ 배로스탯 대조 잡 — LJ 결정(fcc)으로 배선만. 같은 BARO 를 쓰는지까지 본다
    from ase.build import bulk
    with tempfile.TemporaryDirectory() as td:
        cr = bulk("Li", "fcc", a=4.3, cubic=True).repeat(2)
        res = run_npt_control(cr, LennardJones(sigma=3.0, epsilon=0.20, rc=8.0), td,
                              T_K=50, ps=0.4, dt_fs=2.0, save_ps=0.02, log=lambda *a: None)
        chk(res["baro"] == BARO, "대조 잡이 생산 런과 **같은** BARO 상수를 쓴다 (다르면 아무것도 증명 못 한다)")
        chk(math.isfinite(res["rho_UMA_0K_g_cm3"]) and math.isfinite(res["P_NPT_mean_last_half_GPa"])
            and os.path.isfile(os.path.join(td, "control.json")),
            f"대조 잡 배선: ρ(0K) {res['rho_UMA_0K_g_cm3']:.3f} · P_NPT {res['P_NPT_mean_last_half_GPa']:+.3f} GPa · control.json")
        chk(abs(res["P_UMA_0K_GPa"]) < 0.5, f"가변셀 완화가 0 GPa 근처로 간다 (P_0K {res['P_UMA_0K_GPa']:+.3f} GPa)")
    # ⛔음성: 압력을 못 주는 계산기는 0 이 아니라 NaN
    class _NoStress(LennardJones):
        implemented_properties = ["energy", "forces"]
        def get_stress(self, atoms=None):
            raise RuntimeError("stress 없음")
    at2 = bulk("Li", "fcc", a=4.3, cubic=True); at2.calc = _NoStress()
    chk(math.isnan(pressure_GPa(at2)), "⛔음성: 응력을 못 주면 NaN — 0 GPa 로 조용히 적지 않는다")
    print(f"selftest: ⭕ {ok} · ⛔ {bad}")
    return 0 if bad == 0 else 1


def main():
    ap = argparse.ArgumentParser(description="LPSCl@Li₂S 1층 melt-quench (UMA NPT)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--system", choices=sorted(SYSTEMS), help="A · B · control_li7ps6 (카드 §2)")
    ap.add_argument("--seed", type=int, help="담금질 시드 (G3: ≥ 5개, 호출마다 하나)")
    ap.add_argument("--n_fu", type=int, help="식단위 수 (기본: A 40 · B 50 · control 28)")
    ap.add_argument("--density", type=float, default=1.2, help="시작 밀도 g/cm³ (NPT 가 고친다; 음이온 3 Å 배제라 1.5 도 못 채운다)")
    ap.add_argument("--T_melt", type=float, default=1200.0)
    ap.add_argument("--T_final", type=float, default=300.0)
    ap.add_argument("--melt_ps", type=float, default=100.0)
    ap.add_argument("--quench_rate", type=float, help="K/s — G2 선언값. 기본값 없음 (예: 1e12 → 900 ps)")
    ap.add_argument("--hold_ps", type=float, default=50.0)
    ap.add_argument("--dt_fs", type=float, default=2.0)
    ap.add_argument("--save_ps", type=float, default=1.0)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--turbo", action="store_true", help="fairchem inference_settings='turbo' 시도 (없으면 기본으로 내려가고 기록)")
    ap.add_argument("--out_root", help="출력 루트 → <out_root>/<system>/seed<seed>/")
    ap.add_argument("--npt_control", metavar="STRUCT",
                    help="⭐배로스탯 대조 잡: 결정 구조 파일(.vasp/.cif/.xyz)을 같은 NPT 배선에 넣어 밀도 유지 확인")
    ap.add_argument("--control_repeat", type=int, default=2, help="--npt_control 셀 반복 (기본 2 → 2×2×2)")
    ap.add_argument("--control_ps", type=float, default=20.0, help="--npt_control NPT 길이 [ps]")
    ap.add_argument("--control_tol", type=float, default=0.03, help="--npt_control 통과 문턱 |Δρ/ρ_UMA(0K)|")
    ap.add_argument("--control_out", help="--npt_control 출력 폴더 (기본 <out_root>/npt_control)")
    ap.add_argument("--dry_run", action="store_true", help="셀만 만들고 계획을 찍는다 (UMA 안 부름)")
    a = ap.parse_args()
    if a.selftest:
        raise SystemExit(_selftest())
    if a.npt_control:
        if not os.path.isfile(a.npt_control):
            raise SystemExit(f"⛔ 구조 파일이 없다: {a.npt_control}")
        from ase.io import read
        at = read(a.npt_control)
        at = at.repeat(a.control_repeat); at.pbc = True
        cout = pathlib.Path(a.control_out or (pathlib.Path(a.out_root or ".") / "npt_control"))
        print(f"[대조 잡] {a.npt_control} ×{a.control_repeat}³ = {len(at)} 원자 · {a.T_final:.0f} K · {a.control_ps:.0f} ps → {cout}", flush=True)
        calc = make_calc(a.device, a.turbo)
        res = run_npt_control(at, calc, cout, T_K=a.T_final, ps=a.control_ps, dt_fs=a.dt_fs, tol=a.control_tol)
        res["uma_inference_mode"] = getattr(calc, "_mq_mode", "default")
        res["structure_file"] = a.npt_control
        (cout / "control.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
        print(json.dumps({k: res[k] for k in ("rho_file_g_cm3", "rho_UMA_0K_g_cm3", "P_UMA_0K_GPa",
                                              "rho_NPT_mean_last_half_g_cm3", "P_NPT_mean_last_half_GPa",
                                              "drift_vs_UMA_0K", "UMA_vs_file", "plumbing_ok")},
                         ensure_ascii=False, indent=1))
        print("⭕ 배선 정상 — 비정질 밀도는 배로스탯 탓이 아니다" if res["plumbing_ok"]
              else "⛔ 배선 이상 — 비정질 결과를 해석하기 전에 배로스탯·단위를 고친다")
        return
    if not (a.system and a.seed is not None and a.out_root):
        ap.error("--system · --seed · --out_root 가 필요하다")
    quench_ps, n_q = schedule(a.T_melt, a.T_final, a.quench_rate, a.dt_fs)
    sym, pos, cell = build_random_cell(a.system, a.seed, a.density, a.n_fu)
    out = pathlib.Path(a.out_root) / a.system / f"seed{a.seed}"; out.mkdir(parents=True, exist_ok=True)
    plan = {"system": a.system, "seed": a.seed, "n_atoms": len(sym), "composition": {e: sym.count(e) for e in sorted(set(sym))},
            "start_density_g_cm3": a.density, "T_melt_K": a.T_melt, "T_final_K": a.T_final, "melt_ps": a.melt_ps,
            "quench_rate_K_s": a.quench_rate, "quench_ps": quench_ps, "hold_ps": a.hold_ps, "dt_fs": a.dt_fs,
            "G2_declared_before_results": True, "card": "db/properties/lpscl_li2s_interphase_prereg_2026_09_11.json"}
    (out / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    from ase import Atoms
    from ase.io import write
    at = Atoms(symbols=sym, positions=pos, cell=cell, pbc=True)
    write(str(out / "initial.xyz"), at, format="extxyz")
    print(f"[{a.system} seed{a.seed}] {len(sym)} 원자 · 셀 {cell[0,0]:.2f} Å · 담금질 {quench_ps:.0f} ps ({n_q} 스텝) → {out}", flush=True)
    if a.dry_run:
        print("dry_run — 여기서 멈춘다"); return
    calc = make_calc(a.device, a.turbo)
    plan["uma_inference_mode"] = getattr(calc, "_mq_mode", "default")
    (out / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(f"UMA inference mode: {plan['uma_inference_mode']}", flush=True)
    info = run_melt_quench(at, calc, out, seed=a.seed, T_melt=a.T_melt, T_final=a.T_final, melt_ps=a.melt_ps,
                           quench_rate=a.quench_rate, hold_ps=a.hold_ps, dt_fs=a.dt_fs, save_ps=a.save_ps)
    ind = indicators(at.get_chemical_symbols(), at.get_positions(), np.asarray(at.get_cell()))
    gr = partial_gr(at.get_chemical_symbols(), at.get_positions(), np.asarray(at.get_cell()))
    write_gr_csv(gr, out / "gr_partials.csv")
    res = {"plan": plan, "run": info, "indicators": ind, "E_final_eV": float(at.get_potential_energy()),
           "files": ["initial.xyz", "traj.xyz", "thermo.csv", "final.xyz", "final.vasp", "gr_partials.csv"],
           "⛔": "지표만 찍었다 — 문턱 대조는 카드 §2 판정_지표. 이 시드 하나로 판정하지 않는다 (G3)."}
    (out / "result.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(json.dumps({"indicators": ind, "wall_min": round(info["wall_min"], 1)}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
