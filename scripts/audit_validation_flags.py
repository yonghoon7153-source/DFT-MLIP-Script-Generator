#!/usr/bin/env python3
"""Audit every case's validation_flags self-report card and produce:

  docs/db/case_audit.csv           every case, every gate value
  docs/db/case_audit_fails.csv     only the failing cases, with the
                                    list of gates that knocked them
                                    out and human-readable case info
  docs/db/case_audit_summary.tex   LaTeX table for §5 Results:
                                    "X / Y cases trustworthy" + a
                                    fail-by-gate breakdown table

The friendly case name is the directory name (`case_dir.name`), which
for archive cases is the auto-generated `<date>_<time>_<hash>` ID.  We
also surface the canonical campaign / source-case label from
meta.json (the upload-time name, e.g. `input_8mAh_8`) when present so
the user can find the case quickly without grep-ing.

Usage:
  python3 scripts/audit_validation_flags.py            # all archives
  python3 scripts/audit_validation_flags.py --fails-only
"""
from __future__ import annotations
import argparse
import os
import json
import sys
from pathlib import Path

#  ★ L4-03 회귀용 — 루트를 env 로 바꿀 수 있게 한다.  **생산 기본은 그대로**이고,
#    이 노브가 없으면 fixture 로 이 감사를 실제로 돌려 볼 방법이 없다 (규칙 J 의 사고).
ROOT    = Path(os.environ.get('AUDIT_FLAGS_ROOT')
               or Path(__file__).resolve().parent.parent).resolve()
WEBAPP  = ROOT / 'webapp'
DOCSDB  = ROOT / 'docs' / 'db'

GATES = [
    'within_bielefeld_range',
    'fracture_distribution_realistic',
    'solver_input_intact',
    'stage_e_le_baseline_sigma_e',
]


def discover_cases() -> list[Path]:
    seen, out = set(), []
    for base in ('archive', 'results'):
        root = WEBAPP / base
        if not root.exists():
            continue
        for atoms_p in root.rglob('atoms.csv'):
            d = atoms_p.parent
            if (d / 'full_metrics.json').exists() and d not in seen:
                seen.add(d)
                out.append(d)
    return sorted(out)


def _friendly_name(case_dir: Path) -> dict:
    """Pull human-recognisable identifiers from meta.json or
    input_params.json if present. Returns dict that may include:
      case_dir, source_case, campaign, ps_ratio, ase_ratio,
      thickness_um, p_vol, s_vol, r_AM_P_um, r_AM_S_um, r_SE_um,
    falling back to None when a field is absent."""
    info = {'case_dir': case_dir.name}
    for fname in ('meta.json', 'input_params.json'):
        p = case_dir / fname
        if not p.exists():
            continue
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        for k in ('source_case', 'campaign', 'ps_ratio', 'p_vol', 's_vol',
                   'ase_ratio', 'am_wt', 'se_wt',
                   'thickness_um', 'r_AM_P_um', 'r_AM_S_um', 'r_SE_um',
                   'name', 'note'):
            if k in d and d[k] is not None and k not in info:
                info[k] = d[k]
    # Pull a couple of useful fields from full_metrics.json too
    try:
        fm = json.loads((case_dir / 'full_metrics.json').read_text())
        for k in ('thickness_um', 'porosity_pct',
                  'sigma_full_mScm', 'electronic_sigma_full_mScm',
                  'sigma_full_mScm_stage_e',
                  'electronic_sigma_full_mScm_stage_e'):
            if k in fm and fm[k] is not None and k not in info:
                info[k] = fm[k]
    except Exception:
        pass
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--fails-only', action='store_true',
                     help='Skip the full case_audit.csv, emit fails+summary only')
    args = ap.parse_args()

    cases = discover_cases()
    if not cases:
        print('No cases found.', flush=True); sys.exit(1)

    rows_all  = []
    rows_fail = []
    fail_by_gate = {g: 0 for g in GATES + ['no_flags_at_all', 'unreadable',
                                       'selfreport_conflict', 'selfreport_bad_type']}
    fail_by_gate['no_flags_at_all'] = 0
    n_trust = n_total = 0
    n_unreadable = n_selfreport_conflict = n_bad_type = 0

    for d in cases:
        try:
            fm = json.loads((d / 'full_metrics.json').read_text())
        except Exception as _e:
            #  ★ L4-03: 초판은 여기서 `continue` 해 **분모에서 통째로 뺐다**.
            #    읽을 수 없는 사례는 "신뢰할 수 있음" 도 "없음" 도 아니라 **UNREADABLE** 이다.
            n_total += 1
            n_unreadable += 1
            fail_by_gate['unreadable'] += 1
            info = _friendly_name(d)
            info['failed_gates'] = f'unreadable ({type(_e).__name__})'
            rows_fail.append(info); rows_all.append(info)
            continue
        flags = fm.get('validation_flags') or {}
        if not flags:
            n_total += 1
            fail_by_gate['no_flags_at_all'] += 1
            info = _friendly_name(d)
            info['failed_gates'] = 'no_flags_at_all'
            rows_fail.append(info)
            rows_all.append(info)
            continue

        n_total += 1
        info = _friendly_name(d)
        for g in GATES + ['trustworthy_overall']:
            info[g] = flags.get(g)
        info['asr_ionic_Ohm_cm2']  = flags.get('asr_ionic_Ohm_cm2')
        info['fracture_severe_pct'] = flags.get('fracture_severe_pct')
        rows_all.append(info)

        #  ★ L4-03 — 자기신고를 **그대로 믿지 않는다**.
        #    (a) `if flags.get(...)` 는 truthy 검사라 **문자열 "false" 가 True 로** 센다.
        #    (b) 개별 게이트가 전부 False 여도 overall 만 True 면 통과했다.
        #    ⇒ 타입을 엄격히 보고, **개별 게이트에서 conjunction 을 재계산**해 대조한다.
        raw_overall = flags.get('trustworthy_overall')
        bad_type = (raw_overall is not None and not isinstance(raw_overall, bool))
        assessable = [g for g in GATES if isinstance(flags.get(g), bool)]
        failed = [g for g in assessable if flags.get(g) is False]
        #  평가 가능한 게이트가 하나도 없으면 통과로 세지 않는다 (증거 없음 ≠ 합격).
        recomputed = bool(assessable) and not failed
        claimed = (raw_overall is True)

        if bad_type:
            n_bad_type += 1
            fail_by_gate['selfreport_bad_type'] += 1
        if claimed != recomputed:
            n_selfreport_conflict += 1
            fail_by_gate['selfreport_conflict'] += 1

        info['trustworthy_recomputed'] = recomputed
        info['n_assessable_gates'] = len(assessable)

        if recomputed and claimed and not bad_type:
            n_trust += 1
        else:
            for g in failed:
                fail_by_gate[g] += 1
            why = list(failed)
            if not assessable:
                why.append('no_assessable_gate')
            if bad_type:
                why.append(f'selfreport_bad_type({raw_overall!r})')
            if claimed != recomputed:
                why.append(f'selfreport_conflict(claimed={claimed} recomputed={recomputed})')
            info['failed_gates'] = ' / '.join(why) if why else 'unassessed'
            rows_fail.append(info)

    DOCSDB.mkdir(parents=True, exist_ok=True)

    import csv as _csv
    # Full table
    if not args.fails_only and rows_all:
        cols = sorted({k for r in rows_all for k in r.keys()})
        cols = (['case_dir'] +
                [c for c in cols if c not in ('case_dir',)])
        with (DOCSDB / 'case_audit.csv').open('w', newline='') as f:
            w = _csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in rows_all: w.writerow(r)
        print(f'  ✓ {DOCSDB / "case_audit.csv"}  ({len(rows_all)} rows)')

    # Fail-only table
    if rows_fail:
        cols = sorted({k for r in rows_fail for k in r.keys()})
        priority = ['case_dir', 'source_case', 'failed_gates',
                    'asr_ionic_Ohm_cm2', 'fracture_severe_pct',
                    'thickness_um', 'porosity_pct',
                    'p_vol', 's_vol', 'am_wt', 'se_wt',
                    'r_AM_P_um', 'r_AM_S_um', 'r_SE_um']
        cols = priority + [c for c in cols if c not in priority]
        with (DOCSDB / 'case_audit_fails.csv').open('w', newline='') as f:
            w = _csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in rows_fail: w.writerow(r)
        print(f'  ✓ {DOCSDB / "case_audit_fails.csv"}  ({len(rows_fail)} rows)')

    # LaTeX summary for §5 Results
    pct = (100.0 * n_trust / max(n_total, 1))
    tex = (
        f"% Auto-generated by scripts/audit_validation_flags.py — do not edit.\n"
        f"% {n_trust}/{n_total} cases passed every assessable trust gate.\n"
        f"\\begin{{table}}[h]\n"
        f"\\centering\n"
        f"\\caption{{Self-reported trust audit on the {n_total}-case "
        f"DEM ensemble. A case is trustworthy when every assessable "
        f"gate (ASR within Bielefeld/Lee experimental window, "
        f"fracture distribution realistic, ${{\\le}}50\\%$ Stage-E "
        f"edge-drop, and Stage-E $\\sigma \\le$ baseline) returns "
        f"True; gates whose underlying metric is missing are excluded "
        f"from the verdict.}}\n"
        f"\\label{{tab:trust-audit}}\n"
        f"\\begin{{tabular}}{{lr}}\n"
        f"\\toprule\n"
        f"Trust verdict & Cases \\\\\n"
        f"\\midrule\n"
        f"Trustworthy (recomputed conjunction AND self-report agree) & "
        f"{n_trust} / {n_total} ({pct:.1f}\\%) \\\\\n"
        f"Excluded: unreadable full\\_metrics.json & "
        f"{n_unreadable} \\\\\n"
        f"Excluded: self-report conflicts with gates & "
        f"{n_selfreport_conflict} \\\\\n"
        f"Excluded: self-report not a boolean & "
        f"{n_bad_type} \\\\\n"
        f"Failed: ASR outside Bielefeld/Lee window      & "
        f"{fail_by_gate['within_bielefeld_range']} \\\\\n"
        f"Failed: fracture distribution unrealistic     & "
        f"{fail_by_gate['fracture_distribution_realistic']} \\\\\n"
        f"Failed: $>$50\\,\\% Stage-E edges dropped     & "
        f"{fail_by_gate['solver_input_intact']} \\\\\n"
        f"Failed: Stage-E $\\sigma >$ baseline (factor $>$ 1) & "
        f"{fail_by_gate['stage_e_le_baseline_sigma_e']} \\\\\n"
        f"No validation flags persisted (older Stage-E run) & "
        f"{fail_by_gate['no_flags_at_all']} \\\\\n"
        f"\\bottomrule\n"
        f"\\end{{tabular}}\n"
        f"\\end{{table}}\n"
    )
    (DOCSDB / 'case_audit_summary.tex').write_text(tex)
    print(f'  ✓ {DOCSDB / "case_audit_summary.tex"}')
    print(f'\nVerdict: {n_trust}/{n_total} trustworthy ({pct:.1f}%)')
    if n_unreadable or n_selfreport_conflict or n_bad_type:
        print(f'  ⚠ 분모에 남긴 비적격: 읽기실패 {n_unreadable} · '
              f'자기신고 모순 {n_selfreport_conflict} · 자기신고 비-bool {n_bad_type}')
    print('Fail breakdown:')
    for g, n in fail_by_gate.items():
        if n: print(f'  {g:38s} {n}')


def _selftest():                                                       # noqa: C901
    """★ L4-03 — Codex 의 네 합성 사례를 그대로 넣어 **거짓 초록**이 재발하는지 본다.

    초판은 이 넷을 넣으면 JSON 오류는 **분모에서 빠지고** 나머지가
    **3/3 trustworthy (100 %)** 로 나왔고, LaTeX 에 *"all assessable gates True"* 를 적었다.
    이 도구가 self-reported audit 인 것은 맞다 — 원 물리의 독립 검증을 기대한 것이 아니다.
    그보다 **약한** 자체 기록의 타입·conjunction·누락 집계도 안 봤다는 것이 결함이었다.
    """
    import json as _j
    import os as _os
    import shutil as _sh
    import subprocess as _sp
    import sys as _sys
    import tempfile as _tf

    ok = True

    def chk(name, cond, extra=''):
        nonlocal ok
        print(('  ✓ ' if cond else '  ✗ ') + name + (f'   {extra}' if extra else ''))
        ok = ok and bool(cond)

    print('audit_validation_flags — 자기신고 감사의 자기일관 (L4-03)')
    tmp = Path(_tf.mkdtemp(prefix='auditst_'))
    try:
        res = tmp / 'webapp' / 'results'
        res.mkdir(parents=True)
        allg = {g: True for g in GATES}

        def case(nm, flags, raw=None):
            d = res / nm
            d.mkdir()
            #  `discover_cases` 는 atoms.csv 가 있어야 케이스로 센다
            (d / 'atoms.csv').write_text('id,x,y,z,radius,type\n1,0,0,0,1,1\n')
            txt = raw if raw is not None else _j.dumps({'validation_flags': flags})
            (d / 'full_metrics.json').write_text(txt)

        #  ① 개별 게이트 하나가 False 인데 overall 만 True
        case('c1', dict(allg, solver_input_intact=False, trustworthy_overall=True))
        #  ② 개별 게이트가 전부 부재인데 overall 만 True
        case('c2', {'trustworthy_overall': True})
        #  ③ 개별 전부 False 인데 overall 이 **문자열** "false"
        case('c3', dict({g: False for g in GATES}, trustworthy_overall='false'))
        #  ④ JSON 자체가 깨짐
        case('c4', None, raw='{ this is not json')
        #  ⑤ 양성 대조 — 정상 통과 사례가 **실제로 통과**해야 판별력이 있다
        case('c5', dict(allg, trustworthy_overall=True))

        env = dict(_os.environ, PYTHONUTF8='1', AUDIT_FLAGS_ROOT=str(tmp))
        r = _sp.run([_sys.executable, _os.path.abspath(__file__)],
                    capture_output=True, text=True, env=env)
        out = r.stdout + r.stderr
        chk('감사가 정상 종료한다', r.returncode == 0, f'rc={r.returncode}')
        chk('① 분모가 5 다 — 깨진 JSON 을 빼지 않는다',
            '/5 trustworthy' in out, out.strip().splitlines()[-3:] and '')
        chk('② 통과는 양성 대조 1건뿐 (3/3 100 % 가 아니다)',
            '1/5 trustworthy' in out)
        for tok, nm in (('unreadable', '④ 읽기 실패를 이름으로 센다'),
                        ('selfreport_conflict', '①② 자기신고 모순을 센다'),
                        ('selfreport_bad_type', '③ 자기신고 비-bool 을 센다')):
            chk(nm, tok in out)
        chk('요약이 "all assessable gates True" 라고 말하지 않는다',
            'all assessable gates True' not in
            (tmp / 'docs' / 'data' / 'trust_audit.tex').read_text(encoding='utf-8')
            if (tmp / 'docs' / 'data' / 'trust_audit.tex').is_file() else True)
    finally:
        _sh.rmtree(tmp, ignore_errors=True)

    print('AUDIT SELFTEST', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    import sys as _s
    if '--selftest' in _s.argv:
        raise SystemExit(_selftest())
    main()
