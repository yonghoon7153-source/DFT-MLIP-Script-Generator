#!/usr/bin/env python3
"""STEP4 각도분해 결손의 **런 전 위험 선별** — 스캐폴드 CSV 만으로, GPU 없이.

    python3 scripts/step4_angular_risk.py --kit kit_ps_7_3
    python3 scripts/step4_angular_risk.py --am <am.csv[.gz]> --se <se.csv[.gz]> --out r.json
    python3 scripts/step4_angular_risk.py --selftest

━━ 왜 이 도구가 있나 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`step4_dyn.py` 는 AM–이온상 **면별** BV 를 실제로 푼다(:1104, :1193).  그런데 그 면전류를
입자 하나의 **총전류로 합친 뒤**(:1447) 그 총량을 **전 구면적 4πR² 에 살포**한다(:1693).
⇒ 버려지는 것은 고체확산의 `l > 0` **각도 모드**다.  실제로는 덮인 patch 로만 들어오므로
국소 flux 가 균일값의 약 `1/c` 이고, 현재 모델은 **국소 표면포화를 늦추는 낙관 편향**이다.

Codex 2026-09-07 (원장 CL-73) 판정:
  · 이 결손은 조성 간에 **상쇄되지 않는다** (공통 i0 도 보장이 아니다).
  · 그러나 조성 차의 **부호는 미결**이다 — 옛 캠페인 실측 coverage 가 VGCF 1 wt% 60.7/62.2 로
    4 wt% 51.7/52.5 보다 **높고** 계열이 비단조다.
⇒ 그래서 **먼저 재야 할 것은 σ 가 아니라 "이 침대가 그 문제에 걸리는 침대인가"** 다.
  진짜 각도 구현(`K = 12/48`)은 방사 상태 수가 4~16배로 늘어 비싸다.  이 도구는 그 전에
  **스캐폴드만으로** 위험을 재는 피검사다.

━━ 무엇을 재나 (Codex 가 지정한 5종) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ① 입자별 coverage `c_i` 의 p05 · 중앙값 · zero fraction
  ② `H_i = |I_i| / (F · 4πR_i² · c_i · √D_i)` 의 p95 / p99
  ③ 전류가중 effective active area
  ④ angular dipole · 유효 활성섹터 수
  ⑤ ①~④ 의 separator / mid / collector z-bin 대조

★ **필요 섹터 수는 사전등록 규칙으로 나온다** — `K · c_p05 ≥ 3`  (Codex 가 런 전에 준 규칙).
  이 도구는 그 규칙에 측정 p05 를 넣어 `K_required = ceil(3 / c_p05)` 를 낸다.
  ⚠ 문턱을 결과 보고 고르지 않는다 — 규칙은 측정 전에 등록됐고 여기선 대입만 한다.

━━ 규약과 한계 (⚠ 읽고 쓸 것) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
· **coverage 정의는 리포 정본과 같다** — `mpm_webapp_payload.geometric_coverage` 의 강체-구
  기하: AM 표면 Fibonacci 표본에서 가장 가까운 **SE 구 표면**까지의 gap 이 밴드 안이면 덮인
  것.  Hertz 0.13 µm / Tabor 0.26 µm 두 밴드를 그대로 쓴다.
  ★ **주 지표는 Hertz** 다 — σ_ionic T1 이 *"Li⁺ 유효 전도면적"* 은 Hertz 쪽이라고 판정했다
  (ρ 0.697 vs 0.476).  Tabor 는 기계적 접촉면이라 vdW 간극이 이온 수송을 방해한다.
· **`I_i` 는 가정이다** (§F1).  런 전이라 STEP4 전류가 없으므로 **균일 활용**을 가정한다:
  `I_i ∝ V_i`.  ⇒ `H_i ∝ R_i / c_i` 이고 **순위는 그 가정에 강건**하다 (전류를 어떻게 정규화해도
  `R_i/c_i` 큰 입자가 위험 상위다).  절대값은 C-rate·용량 규약에 딸리므로 **인용 금지**,
  **분포 모양과 순위만** 쓴다.
· **`D_i` 는 단일값** (`--d-s`, 기본 3e-14 = step4_dyn 기본).  √D 가 공통이면 순위 불변.
  bimodal D 를 쓰면 `--d-s-sc` 로 반경 문턱 아래를 갈라 넣는다.
· ⚠ **이것은 STEP4 를 대신하지 않는다.**  최종 허용 게이트는 Codex 가 등록한
  *"조성 간 `q_frac_at_cutoff` < 1 %p **이고** 동일 SOC 전압차 < 5 mV"* 이고 그건 실제 런이
  필요하다.  이 도구는 **그 런을 할 가치가 있는지**와 **K 를 얼마로 잡을지**만 답한다.
· ⚠ coverage 는 **이온상(SE)** 기준이다.  탄소(VGCF)는 전자망 전용이라 BV 계면이 아니다.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure_provenance import provenance                        # noqa: E402  (CL-75)

F_CONST = 96485.33212                    # C/mol  (step4_dyn 과 같은 값)
CSV_UM = 1000.0                            # 스캐폴드 CSV 1 단위 = 1000 µm (payload 규약)
BAND_HERTZ_UM, BAND_TABOR_UM = 0.13, 0.26  # payload geometric_coverage 와 동일


def _load_csv(path):
    op = gzip.open if str(path).endswith('.gz') else open
    with op(path, 'rt') as fh:
        return np.loadtxt(fh, delimiter=',')


def _fib_dirs(n):
    """단위구 위 Fibonacci 방향 n 개 (거의 등면적).  payload 와 같은 생성식."""
    k = np.arange(n)
    phi = np.pi * (3 - np.sqrt(5))
    z = 1 - 2 * (k + 0.5) / n
    r = np.sqrt(np.clip(1 - z * z, 0, None))
    return np.column_stack([r * np.cos(phi * k), r * np.sin(phi * k), z])


def per_particle_coverage(am, se, n_samp=2000, n_sector=48, bands_um=(BAND_HERTZ_UM, BAND_TABOR_UM)):
    """입자별 coverage + 각도 형상.  반환 dict of arrays (길이 = AM 개수).

    ⚠ gap 정의는 `geometric_coverage` 와 **같아야** 한다 — 다르면 옛 캠페인 수치와 비교 불가.
    """
    from scipy.spatial import cKDTree
    C, R, TY = am[:, 1:4], am[:, 4], am[:, 0].astype(int)
    tree = cKDTree(se[:, 1:4])
    r_se = float(np.median(se[:, 4]))
    b0, b1 = bands_um[0] / CSV_UM, bands_um[1] / CSV_UM
    U = _fib_dirs(n_samp)
    S = _fib_dirs(n_sector)
    #  각 표본 → 가장 가까운 섹터 중심 (Fibonacci 점의 구면 Voronoi ≈ 등면적)
    sec_of = np.argmax(U @ S.T, axis=1)
    n = len(C)
    c_h = np.zeros(n); c_t = np.zeros(n); dip = np.zeros(n); neff = np.zeros(n)
    for i in range(n):
        d, _ = tree.query(C[i] + R[i] * U)
        gap = d - r_se
        mh = gap < b0
        c_h[i] = mh.mean()
        c_t[i] = float((gap < b1).mean())
        if not mh.any():
            dip[i] = np.nan                       # 덮인 곳이 없으면 방향이 정의되지 않는다
            neff[i] = 0.0
            continue
        v = U[mh].mean(axis=0)
        dip[i] = float(np.linalg.norm(v))         # 0 = 등방 · 1 = 한 점에 뭉침
        cnt = np.bincount(sec_of[mh], minlength=n_sector).astype(float)
        p = cnt / cnt.sum()
        neff[i] = float(1.0 / np.sum(p * p))      # 역참여비 = 유효 활성섹터 수
    return {'cov_hertz': c_h, 'cov_tabor': c_t, 'dipole': dip, 'n_eff_sector': neff,
            'R_um': R * CSV_UM, 'z_um': C[:, 2] * CSV_UM, 'type': TY, 'r_se_um': r_se * CSV_UM,
            'n_sector': n_sector, 'n_samp': n_samp}


def risk_metrics(pp, c_rate=1.0, d_s=3e-14, d_s_sc=None, split_um=3.5, cov_key='cov_hertz'):
    """② H_i · ③ 전류가중 유효면적 · ④ 각도 형상 요약.

    `I_i ∝ V_i` (균일 활용, §F1 가정).  전체 전류는 C-rate × (Σ V_i 의 용량) 로 잡되
    **절대값은 인용 금지** — 순위와 분포 모양만 쓴다.
    """
    R = pp['R_um'] * 1e-6                                    # µm → m
    c = np.asarray(pp[cov_key], float)
    V = 4.0 / 3.0 * np.pi * R ** 3
    #  균일 활용: 1 C 는 1 시간에 전부 → I_i = C_rate · (Q_vol · V_i) / 3600.  Q_vol 은
    #  공통 상수라 순위에 무관하다.  NCM 통상값 ~ 550 mAh/cm³ = 1.98e9 C/m³ 를 쓴다.
    Q_VOL = 1.98e9                                           # C/m³ (공통 상수, 순위 무관)
    I = c_rate * Q_VOL * V / 3600.0
    D = np.full(R.shape, float(d_s))
    if d_s_sc is not None:
        D[pp['R_um'] < split_um] = float(d_s_sc)
    with np.errstate(divide='ignore', invalid='ignore'):
        H = np.abs(I) / (F_CONST * 4.0 * np.pi * R ** 2 * c * np.sqrt(D))
    H[~np.isfinite(H)] = np.inf                              # c = 0 → 물리적으로 무한 위험
    A_geo = 4.0 * np.pi * R ** 2
    #  ③ 전류가중 유효 활성면적 = Σ I_i·(c_i A_i) / Σ I_i  vs  Σ I_i·A_i / Σ I_i
    w = I / I.sum()
    return {'H': H, 'I': I, 'A_geo_m2': A_geo,
            'A_eff_iw_m2': float(np.sum(w * c * A_geo)),
            'A_geo_iw_m2': float(np.sum(w * A_geo)),
            'cov_iw': float(np.sum(w * c))}


def _q(a, p):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    return float(np.percentile(a, p)) if a.size else float('nan')


def summarize(pp, rm, cov_key='cov_hertz', n_zbin=3):
    c = np.asarray(pp[cov_key], float)
    H = rm['H']
    p05 = _q(c, 5)
    #  ★ 사전등록 규칙 (Codex 2026-09-07): K · c_p05 ≥ 3
    k_req = int(math.ceil(3.0 / p05)) if p05 > 0 else None
    out = {
        'cov_band': cov_key,
        'n_particles': int(c.size),
        'cov_p05': p05, 'cov_median': float(np.median(c)), 'cov_mean': float(c.mean()),
        'cov_zero_frac': float((c <= 0).mean()),
        'cov_p01': _q(c, 1),
        'H_p95': _q(H, 95), 'H_p99': _q(H, 99),
        'H_n_infinite': int(np.sum(~np.isfinite(H))),
        'A_eff_over_geo_iw': (rm['A_eff_iw_m2'] / rm['A_geo_iw_m2']) if rm['A_geo_iw_m2'] else None,
        'cov_current_weighted': rm['cov_iw'],
        'dipole_median': float(np.nanmedian(pp['dipole'])),
        'dipole_p95': _q(pp['dipole'], 95),
        'n_eff_sector_median': float(np.median(pp['n_eff_sector'])),
        'n_eff_sector_p05': _q(pp['n_eff_sector'], 5),
        'K_required_from_p05': k_req,
        'K_rule': 'K · cov_p05 ≥ 3  (Codex 2026-09-07, 런 전 등록)',
    }
    z = pp['z_um']
    edges = np.quantile(z, np.linspace(0, 1, n_zbin + 1))
    edges[0] -= 1e-9; edges[-1] += 1e-9
    lab = ['collector', 'mid', 'separator'] if n_zbin == 3 else [f'z{i}' for i in range(n_zbin)]
    bins = []
    for i in range(n_zbin):
        m = (z >= edges[i]) & (z < edges[i + 1])
        bins.append({'label': lab[i], 'z_um': [float(edges[i]), float(edges[i + 1])],
                     'n': int(m.sum()),
                     'cov_p05': _q(c[m], 5), 'cov_median': float(np.median(c[m])) if m.any() else None,
                     'cov_zero_frac': float((c[m] <= 0).mean()) if m.any() else None,
                     'H_p95': _q(H[m], 95),
                     'n_eff_sector_median': float(np.median(pp['n_eff_sector'][m])) if m.any() else None})
    out['z_bins'] = bins
    #  ⚠ z-bin 은 **입자 중심 분위수**로 나눈다 (등개수).  물리 두께 3등분이 아니다 —
    #    두께 방향으로 입자 밀도가 다르면 등개수 쪽이 통계가 안정적이다.
    out['z_bin_rule'] = '입자 중심 z 의 등개수 분위수 (물리 3등분 아님)'
    return out


# ═══════════════════════════════════════════════════════════════════════════
def _selftest():
    ok, fail = 0, []

    def chk(n, c):
        nonlocal ok
        (ok := ok + 1) if c else fail.append(n)
        print(('  PASS  ' if c else '  FAIL  ') + n)

    # ① 완전히 둘러싸인 입자 = coverage 1, dipole 0, 유효섹터 = 섹터 수
    R = 0.002
    dirs = _fib_dirs(600)
    am = np.array([[1, 0.0, 0.0, 0.0, R]])
    se_r = 0.0005
    se = np.column_stack([np.ones(600), dirs * (R + se_r), np.full(600, se_r)])
    se = np.column_stack([se[:, 0], se[:, 1:4], np.full(600, se_r)])
    pp = per_particle_coverage(am, se, n_samp=500, n_sector=48)
    chk(f'① 완전 피복 → cov = 1.0 (측정 {pp["cov_hertz"][0]:.3f})', pp['cov_hertz'][0] > 0.99)
    chk(f'① 등방 → dipole ≈ 0 (측정 {pp["dipole"][0]:.3f})', pp['dipole'][0] < 0.05)
    chk(f'① 등방 → 유효섹터 ≈ 48 (측정 {pp["n_eff_sector"][0]:.1f})', pp['n_eff_sector'][0] > 40)

    # ② 한쪽 반구만 덮으면 cov ≈ 0.5 이고 dipole 이 커진다 (한 점 뭉침의 해석값 0.5 근방)
    hemi = dirs[dirs[:, 2] > 0.30]
    se2 = np.column_stack([np.ones(len(hemi)), hemi * (R + se_r), np.full(len(hemi), se_r)])
    pp2 = per_particle_coverage(am, se2, n_samp=500, n_sector=48)
    chk(f'② 극관만 덮임 → cov < 0.5 (측정 {pp2["cov_hertz"][0]:.3f})', 0.0 < pp2['cov_hertz'][0] < 0.5)
    chk(f'② 한쪽 뭉침 → dipole 이 등방보다 크다 ({pp2["dipole"][0]:.3f} > {pp["dipole"][0]:.3f})',
        pp2['dipole'][0] > pp['dipole'][0] + 0.3)
    chk(f'② 뭉치면 유효섹터가 준다 ({pp2["n_eff_sector"][0]:.1f} < {pp["n_eff_sector"][0]:.1f})',
        pp2['n_eff_sector'][0] < pp['n_eff_sector'][0])

    # ③ 아무것도 안 닿으면 cov = 0 · H = inf · dipole = nan (조용한 0 이 아니어야 한다)
    se3 = np.array([[1.0, 10.0, 10.0, 10.0, se_r]])
    pp3 = per_particle_coverage(am, se3, n_samp=200, n_sector=12)
    rm3 = risk_metrics(pp3)
    chk('③ 미접촉 입자 → cov 0 · H 무한 · dipole nan (조용히 통과 금지)',
        pp3['cov_hertz'][0] == 0.0 and not np.isfinite(rm3['H'][0]) and np.isnan(pp3['dipole'][0]))

    # ④ H 의 순위는 R/c 를 따른다 (전류 정규화·D 공통이면 상수배)
    am4 = np.array([[1, 0.0, 0.0, 0.0, 0.006], [2, 0.02, 0.0, 0.0, 0.002]])
    pp4 = {'R_um': np.array([6.0, 2.0]), 'cov_hertz': np.array([0.5, 0.5]),
           'z_um': np.array([0.0, 0.0]), 'dipole': np.array([0.1, 0.1]),
           'n_eff_sector': np.array([20.0, 20.0]), 'type': np.array([1, 2])}
    h4 = risk_metrics(pp4)['H']
    chk(f'④ 같은 coverage 면 큰 입자가 위험 상위 ({h4[0]:.3g} > {h4[1]:.3g})', h4[0] > h4[1])
    pp5 = dict(pp4, cov_hertz=np.array([0.5, 0.1]))
    h5 = risk_metrics(pp5)['H']
    chk('④ coverage 가 낮으면 H 가 1/c 로 커진다',
        abs(h5[1] / risk_metrics(pp4)['H'][1] - 5.0) < 1e-9)

    # ⑤ 사전등록 K 규칙이 그대로 대입된다 (문턱을 만들지 않는다)
    s = summarize({'cov_hertz': np.array([0.10] * 20 + [0.02]), 'z_um': np.zeros(21),
                   'dipole': np.full(21, 0.1), 'n_eff_sector': np.full(21, 10.0),
                   'R_um': np.full(21, 2.0), 'type': np.ones(21, int)},
                  risk_metrics({'R_um': np.full(21, 2.0),
                                'cov_hertz': np.array([0.10] * 20 + [0.02])}))
    chk(f'⑤ K_required = ceil(3 / p05) 그대로 (p05 {s["cov_p05"]:.4f} → K {s["K_required_from_p05"]})',
        s['K_required_from_p05'] == math.ceil(3.0 / s['cov_p05']))

    # ⑥ Hertz ≤ Tabor (밴드가 넓으면 더 많이 덮인다) — 규약 뒤집힘 감지
    chk('⑥ Hertz ≤ Tabor (밴드 순서 규약)', bool((pp2['cov_hertz'] <= pp2['cov_tabor'] + 1e-12).all()))

    print(f'\nstep4_angular_risk selftest: {ok}/{ok + len(fail)} PASS'
          + (f'   FAILED: {fail}' if fail else ''))
    return 1 if fail else 0


def _fmt(s):
    z = s['z_bins']
    L = [
        f"  입자 {s['n_particles']:,} · 밴드 {s['cov_band']}",
        '',
        '  ① coverage  c_i',
        f"     p01 {s['cov_p01']:.4f} · p05 {s['cov_p05']:.4f} · 중앙 {s['cov_median']:.4f} "
        f"· 평균 {s['cov_mean']:.4f} · zero {100 * s['cov_zero_frac']:.2f} %",
        '',
        '  ② H_i = |I| / (F·4πR²·c·√D)     ⚠ 절대값 인용 금지 (I 는 균일활용 가정) — 분포·순위만',
        f"     p95 {s['H_p95']:.4g} · p99 {s['H_p99']:.4g} · 무한(c=0) {s['H_n_infinite']} 개",
        '',
        '  ③ 전류가중 유효 활성면적',
        f"     A_eff/A_geo = {s['A_eff_over_geo_iw']:.4f}   (전류가중 coverage {s['cov_current_weighted']:.4f})",
        '',
        '  ④ 각도 형상',
        f"     dipole 중앙 {s['dipole_median']:.3f} · p95 {s['dipole_p95']:.3f}   (0 = 등방, 1 = 한 점)",
        f"     유효 활성섹터 중앙 {s['n_eff_sector_median']:.1f} · p05 {s['n_eff_sector_p05']:.1f}  (섹터 48 기준)",
        '',
        '  ⑤ z-bin  (입자 중심 등개수 분위수)',
        '     bin          n     cov_p05   cov_med   zero%    H_p95     유효섹터',
    ]
    for b in z:
        L.append(f"     {b['label']:<11} {b['n']:>4}   {b['cov_p05']:7.4f}   "
                 f"{(b['cov_median'] or 0):7.4f}  {100 * (b['cov_zero_frac'] or 0):6.2f}   "
                 f"{b['H_p95']:8.4g}   {(b['n_eff_sector_median'] or 0):6.1f}")
    L += ['',
          f"  ★ 사전등록 규칙 {s['K_rule']}",
          f"    ⇒ **K_required = {s['K_required_from_p05']}**"
          + ('   (p05 = 0 → 규칙 적용 불가: 미접촉 입자가 5 % 를 넘는다)'
             if s['K_required_from_p05'] is None else '')]
    return '\n'.join(L)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='STEP4 각도분해 위험 선별 (런 전, GPU 불요)')
    ap.add_argument('--kit', default='', help='docs/data/kit_ps_scaffolds 의 킷 이름')
    ap.add_argument('--am', default='', help='AM 스캐폴드 CSV(.gz)')
    ap.add_argument('--se', default='', help='SE 스캐폴드 CSV(.gz)')
    ap.add_argument('--band', choices=['hertz', 'tabor'], default='hertz',
                    help='주 지표 밴드 (기본 hertz = Li⁺ 유효 전도면적, σ_ionic T1 판정)')
    ap.add_argument('--n-samp', type=int, default=2000, help='AM 표면 Fibonacci 표본 수')
    ap.add_argument('--n-sector', type=int, default=48, help='유효섹터 계산의 기준 섹터 수')
    ap.add_argument('--c-rate', type=float, default=1.0)
    ap.add_argument('--d-s', type=float, default=3e-14, help='고체확산 D_s [m²/s] (step4_dyn 기본)')
    ap.add_argument('--d-s-sc', type=float, default=None, help='소립(single-crystal) D_s — 쌍 지정')
    ap.add_argument('--split-um', type=float, default=3.5, help='소립/대립 반경 문턱 [µm]')
    ap.add_argument('--label', default='', help='JSON 에 남길 팔 이름')
    ap.add_argument('--out', default='')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        raise SystemExit(_selftest())

    if a.kit:
        d = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         'docs', 'data', 'kit_ps_scaffolds')
        a.am = a.am or os.path.join(d, f'{a.kit}__am_scaffold.csv.gz')
        a.se = a.se or os.path.join(d, f'{a.kit}__se_scaffold.csv.gz')
    if not (a.am and a.se):
        ap.error('--kit 또는 --am/--se 가 필요하다')
    for p in (a.am, a.se):
        if not os.path.exists(p):
            ap.error(f'없는 파일: {p}')

    am, se = _load_csv(a.am), _load_csv(a.se)
    print(f'AM {len(am):,} · SE {len(se):,} · 표본 {a.n_samp} · 섹터 {a.n_sector}')
    pp = per_particle_coverage(am, se, n_samp=a.n_samp, n_sector=a.n_sector)
    key = f'cov_{a.band}'
    rm = risk_metrics(pp, c_rate=a.c_rate, d_s=a.d_s, d_s_sc=a.d_s_sc,
                      split_um=a.split_um, cov_key=key)
    s = summarize(pp, rm, cov_key=key)
    print('\n' + _fmt(s))
    print('\n  ⚠ 이것은 STEP4 를 대신하지 않는다.  최종 허용 게이트는 '
          '"조성 간 q_frac_at_cutoff < 1 %p 이고 동일 SOC 전압차 < 5 mV" 이고 실제 런이 필요하다.')

    if a.out:
        s.update({'label': a.label or (a.kit or os.path.basename(a.am)),
                  'am_csv': a.am, 'se_csv': a.se, 'r_se_um': pp['r_se_um'],
                  'n_samp': a.n_samp, 'n_sector': a.n_sector, 'c_rate': a.c_rate,
                  'd_s': a.d_s, 'd_s_sc': a.d_s_sc, 'split_um': a.split_um,
                  'assumptions': ('I_i ∝ V_i (균일 활용, §F1) — H 절대값 인용 금지, 순위·분포만.  '
                                  'coverage = geometric_coverage 와 같은 강체-구 gap 규약.')})
        #  ★ CL-75 — 측정 JSON 은 그것을 만든 코드 상태를 봉인한다.  스캐폴드 CSV 도 dirty 범위에
        #    넣는다 (그 데이터가 커밋된 것인지까지 봉인해야 재현이 성립한다).
        s.update(provenance(paths=('scripts/', 'docs/data/')))
        with open(a.out, 'w') as fh:
            json.dump(s, fh, ensure_ascii=False, indent=1)
        print(f'\n  → {a.out}')
