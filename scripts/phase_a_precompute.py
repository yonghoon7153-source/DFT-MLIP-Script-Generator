#!/usr/bin/env python3
"""Phase A (6 mAh VGCF+PTFE) **런 전 사전계산** — GPU 불요, 스캐폴드 파일 불요.

    python3 scripts/phase_a_precompute.py --out docs/data/phase_a_6mah/precompute.json
    python3 scripts/phase_a_precompute.py --selftest

━━ 왜 스캐폴드 파일 없이 되나 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`d_h` 와 첨가제 객체 수는 **총량**만 필요하다 (V_AM · S_AM · V_SE · 상자).  입자 **위치**가
필요한 것은 각도 선별(`step4_angular_risk.py`)뿐이고 그건 스캐폴드 CSV 를 기다린다.

침대 상수는 `docs/session_20260906_progress.md` §8-2 에서 온다 (옛 6 mAh 캠페인 case_master):
AM_P 126 · AM_S 1,372 · p_frac 0.7 · SE/solid 33.23 vol% · 상자 50.01 × 50.01 × 112.87 µm.

★ **반경은 가정이 아니라 교차검증된다** — 12:4:1 규약의 R_P=6 · R_S=2 를 넣으면
`V_P/(V_P+V_S) = 0.713` 이 기록된 `p_frac 0.70` 과 맞고(±2 %), `V_AM + V_SE` 가 기록된
`V_solid 241,953 µm³` 와 **0.65 %** 안에서 닫힌다.  둘 다 어긋나면 이 스크립트는 **거부한다**
(조용히 진행하지 않는다).

━━ 무엇을 내나 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
① **`d_h/dx` 게이트** (STEP2 MPM) — `d_h = V_free/S_AM`, 규칙 `d_h/dx ≳ 3.5`.
   ⚠⚠ 이 게이트는 **MPM 의 SE 응력**에 대한 것이다.  STEP3 의 σ 격자와 **다른 질문**이고,
   통과한다고 STEP3 가 안전하다는 뜻이 **전혀 아니다** — STEP3 쪽은 SE neck 해상도가 따로
   있고 `h = 0.20 · 0.25` 에서 neck 의 85.6 % · 97.4 % 가 2 셀 미만이다 (CL-72).
② **첨가제 객체 수** — 프로덕션 경로 `additives.recipe_counts_real` 을 그대로 부른다
   (실물 scaffold 질량 기준; `--add-recipe` 가 AM:SE 를 무시하는 것과 같은 규약).
   ⚠ 옛 손계산(세션 §8-4)은 3.7 % 어긋났다.  이 경로는 옛 캠페인 4행을 **0.58 %** 로 재현한다.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#  ── 침대 상수 (세션 §8-2, 옛 6 mAh 캠페인 case_master) ─────────────────────────
BED = {
    'case': 'input_6mAh_real_4',
    'n_am_p': 126, 'n_am_s': 1372,
    'r_am_p_um': 6.0, 'r_am_s_um': 2.0,       # 12:4:1 규약 — 아래에서 p_frac 으로 교차검증
    'p_frac': 0.70,                            # 기록값 (AM_P 부피 몫)
    'se_frac_of_solid': 0.3323,
    'v_solid_um3': 241953.0,
    'lateral_um': 50.01, 'thickness_um': 112.87,
    'porosity_dem': 0.1428,
}
DH_GATE = 3.5                                  # CLAUDE.md 실용 규칙 (MPM SE 응력)
TOL_PFRAC, TOL_CLOSE = 0.02, 0.02              # 교차검증 허용오차


def bed_totals(bed=BED):
    """총량 + **교차검증**.  어긋나면 예외 — 조용히 진행하지 않는다."""
    nP, nS = bed['n_am_p'], bed['n_am_s']
    RP, RS = bed['r_am_p_um'], bed['r_am_s_um']
    V_P = nP * 4.0 / 3.0 * np.pi * RP ** 3
    V_S = nS * 4.0 / 3.0 * np.pi * RS ** 3
    V_AM = V_P + V_S
    S_AM = nP * 4.0 * np.pi * RP ** 2 + nS * 4.0 * np.pi * RS ** 2
    V_SE = bed['v_solid_um3'] * bed['se_frac_of_solid']
    p_meas = V_P / V_AM
    if abs(p_meas - bed['p_frac']) > TOL_PFRAC:
        raise SystemExit(f'⛔ p_frac 불일치: 계산 {p_meas:.4f} vs 기록 {bed["p_frac"]} '
                         f'⇒ 반경 가정 (R_P {RP}, R_S {RS}) 이 이 침대의 것이 아니다')
    close = (V_AM + V_SE) / bed['v_solid_um3'] - 1.0
    if abs(close) > TOL_CLOSE:
        raise SystemExit(f'⛔ V_solid 닫힘 실패: V_AM+V_SE 가 기록값과 {100 * close:+.2f} % 어긋난다')
    Ah = bed['lateral_um'] ** 2 * bed['thickness_um']
    return {'V_AM_um3': V_AM, 'S_AM_um2': S_AM, 'V_SE_um3': V_SE, 'Ah_um3': Ah,
            'phi_se_local': V_SE / (Ah - V_AM),
            'check_p_frac': p_meas, 'check_v_solid_rel': close}


def dh_gate(tot, lateral_um=BED['lateral_um'], n_grids=(192, 256, 288, 320, 384, 448, 512)):
    """① `d_h/dx` — dx = lateral_box / n_grid (real14 @384 → dx 0.141 µm 로 검증된 규약)."""
    from fit_dh_collapse import d_h_at_phi                       # 정본 공식을 그대로 쓴다
    dh = d_h_at_phi(tot['V_SE_um3'], tot['S_AM_um2'], tot['phi_se_local'], include_se=True)
    dh_void = d_h_at_phi(tot['V_SE_um3'], tot['S_AM_um2'], tot['phi_se_local'], include_se=False)
    rows = [{'n_grid': int(n), 'dx_um': lateral_um / n,
             'dh_over_dx': dh / (lateral_um / n),
             'pass': bool(dh / (lateral_um / n) >= DH_GATE)} for n in n_grids]
    return {'d_h_um': dh, 'd_h_void_only_um': dh_void, 'gate': DH_GATE,
            'n_grid_min_pass': int(math.ceil(DH_GATE * lateral_um / dh)), 'rows': rows,
            'scope': ('이 게이트는 **MPM 의 SE 응력** 해상도다.  STEP3 σ 격자와 다른 질문이고, '
                      '통과가 STEP3 안전을 뜻하지 **않는다** (STEP3 쪽은 SE neck — CL-72).')}


def additive_counts(tot, vgcf_wts=(1.0, 2.0, 3.0, 4.0), ptfe_wt=1.0):
    """② 프로덕션 경로를 그대로 부른다 (손계산 금지 — 옛 손계산은 3.7 % 틀렸다)."""
    from additives import recipe_counts_real
    out = []
    for v in vgcf_wts:
        r = recipe_counts_real({'VGCF': float(v), 'PTFE': float(ptfe_wt)},
                               tot['V_AM_um3'], tot['V_SE_um3'])
        out.append({'vgcf_wt_pct': float(v), 'ptfe_wt_pct': float(ptfe_wt),
                    'n_vgcf': r['VGCF']['n'], 'n_ptfe': r['PTFE']['n'],
                    'vgcf_vol_pct_of_solid': r['VGCF']['vol_pct_of_solid'],
                    'ptfe_vol_pct_of_solid': r['PTFE']['vol_pct_of_solid'],
                    'am_wt_pct': r['am_wt_pct'], 'se_wt_pct': r['se_wt_pct']})
    return out


def validate_against_campaign(tot, measured=((0.5, 13281), (1.0, 26696), (2.0, 53529), (4.0, 110120))):
    """옛 캠페인 실측 n_objects 와 대조 — 이 경로가 그 침대를 재현하는지 (VGCF 만, PTFE 없음)."""
    from additives import recipe_counts_real
    rows = []
    for wt, meas in measured:
        n = recipe_counts_real({'VGCF': float(wt)}, tot['V_AM_um3'], tot['V_SE_um3'])['VGCF']['n']
        rows.append({'vgcf_wt_pct': wt, 'n_computed': int(n), 'n_measured': int(meas),
                     'rel_pct': 100.0 * (n / meas - 1.0)})
    return {'rows': rows, 'max_abs_rel_pct': max(abs(r['rel_pct']) for r in rows)}


def _selftest():
    ok, fail = 0, []

    def chk(n, c):
        nonlocal ok
        (ok := ok + 1) if c else fail.append(n)
        print(('  PASS  ' if c else '  FAIL  ') + n)

    tot = bed_totals()
    chk(f'① p_frac 교차검증 {tot["check_p_frac"]:.4f} ≈ 0.70', abs(tot['check_p_frac'] - 0.70) < TOL_PFRAC)
    chk(f'① V_solid 닫힘 {100 * tot["check_v_solid_rel"]:+.2f} %', abs(tot['check_v_solid_rel']) < TOL_CLOSE)
    # ② 반경이 틀리면 **거부**해야 한다 (조용한 통과 금지)
    bad = dict(BED, r_am_p_um=3.0)
    try:
        bed_totals(bad); raised = False
    except SystemExit:
        raised = True
    chk('② 반경이 틀리면 p_frac 검증이 거부한다 (조용히 통과 금지)', raised)
    g = dh_gate(tot)
    chk(f'③ d_h = {g["d_h_um"]:.4f} µm — 킷/real14 밴드(0.5~1.5 µm) 안', 0.4 < g['d_h_um'] < 1.6)
    chk(f'③ 최소 통과 n_grid = {g["n_grid_min_pass"]} · 288 통과', g['rows'][2]['pass'])
    chk('③ d_h/dx 는 n_grid 에 단조 증가', all(a['dh_over_dx'] < b['dh_over_dx']
                                                for a, b in zip(g['rows'], g['rows'][1:])))
    v = validate_against_campaign(tot)
    chk(f'④ 옛 캠페인 4행 재현 (최대 |Δ| {v["max_abs_rel_pct"]:.2f} % < 1 %)', v['max_abs_rel_pct'] < 1.0)
    c = additive_counts(tot)
    chk('⑤ VGCF 개수가 wt% 에 단조 증가', all(a['n_vgcf'] < b['n_vgcf'] for a, b in zip(c, c[1:])))
    chk('⑤ PTFE 는 1 wt% 고정인데 개수가 조금 는다 (총질량이 늘기 때문 — 규약 확인)',
        c[0]['n_ptfe'] < c[-1]['n_ptfe'] and (c[-1]['n_ptfe'] / c[0]['n_ptfe'] - 1) < 0.10)
    print(f'\nphase_a_precompute selftest: {ok}/{ok + len(fail)} PASS'
          + (f'   FAILED: {fail}' if fail else ''))
    return 1 if fail else 0


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Phase A 런 전 사전계산 (GPU·스캐폴드 파일 불요)')
    ap.add_argument('--out', default='')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        raise SystemExit(_selftest())

    tot = bed_totals()
    g = dh_gate(tot)
    cts = additive_counts(tot)
    val = validate_against_campaign(tot)

    print(f"침대 {BED['case']}  ·  AM_P {BED['n_am_p']} (R {BED['r_am_p_um']} µm) · "
          f"AM_S {BED['n_am_s']} (R {BED['r_am_s_um']}) · 상자 "
          f"{BED['lateral_um']}² × {BED['thickness_um']} µm")
    print(f"  교차검증  p_frac {tot['check_p_frac']:.4f} (기록 {BED['p_frac']}) · "
          f"V_solid 닫힘 {100 * tot['check_v_solid_rel']:+.2f} %\n")
    print(f"① d_h = {g['d_h_um']:.4f} µm (잔여공극만 {g['d_h_void_only_um']:.4f}) · "
          f"φ_SE_local {tot['phi_se_local']:.4f}")
    print(f"   게이트 d_h/dx ≥ {DH_GATE}   ★ 최소 통과 n_grid = {g['n_grid_min_pass']}")
    print('   n_grid    dx(µm)   d_h/dx   판정')
    for r in g['rows']:
        print(f"     {r['n_grid']:4}   {r['dx_um']:.4f}   {r['dh_over_dx']:6.2f}   "
              f"{'✅' if r['pass'] else '⚠ 미달 → 하한 라벨'}")
    print(f"   ⚠ {g['scope']}\n")
    print('② 첨가제 객체 수 (프로덕션 경로 recipe_counts_real)')
    print('   레시피             VGCF n     PTFE n   VGCF vol%  PTFE vol%   AM wt%  SE wt%')
    for c in cts:
        print(f"   VGCF {c['vgcf_wt_pct']:.0f} + PTFE 1  {c['n_vgcf']:8,}  {c['n_ptfe']:7,}   "
              f"{c['vgcf_vol_pct_of_solid']:7.3f}   {c['ptfe_vol_pct_of_solid']:7.3f}   "
              f"{c['am_wt_pct']:6.2f}  {c['se_wt_pct']:6.2f}")
    print(f"\n③ 옛 캠페인 대조 (VGCF 만) — 최대 |Δ| {val['max_abs_rel_pct']:.2f} %")
    for r in val['rows']:
        print(f"   VGCF {r['vgcf_wt_pct']:<4} 계산 {r['n_computed']:7,}  실측 {r['n_measured']:7,}  "
              f"Δ {r['rel_pct']:+6.2f} %")
    print('\n⛔ 아직 못 하는 것: 각도 선별 (입자 **위치**가 필요) — 스캐폴드 CSV 대기')

    if a.out:
        from measure_provenance import provenance
        os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
        d = {'bed': BED, 'totals': tot, 'dh_gate': g, 'additive_counts': cts,
             'campaign_validation': val,
             'not_computed': ('각도 선별 (step4_angular_risk) — 입자 위치가 필요해 스캐폴드 CSV 대기'),
             **provenance()}
        json.dump(d, open(a.out, 'w'), ensure_ascii=False, indent=1, default=float)
        print(f'\n  → {a.out}')
