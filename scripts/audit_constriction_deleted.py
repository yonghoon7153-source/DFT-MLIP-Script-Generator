#!/usr/bin/env python3
"""S0 — **협착 항이 삭제된 접촉이 몇 개인가** (면적 계약 §4, 계산 불변).

정본 계약 = `docs/area_contract_20260913.md`.  원장 = `SELF-28`.

★ 왜 이 도구가 필요한가
`network_conductivity.py` 의 Physics 가지는 면적을 **평면 원판**으로 읽는다
(`:323` `a = sqrt(A/pi)`).  그런데 `A_physics` 는 **구 표면** 공간에서 만들어진 양이라
(`A_geom = 2*pi*R_min**2` = 반구), 원판으로 환산하면 `a > R_min` 이 나온다.  그러면
`:395` 가 `a_eff = min(a, R_min)` 으로 자르고, 그 순간

    psi = (1 - a_eff/R_min)**1.5 = (1 - 1)**1.5 = 0

이 되어 `:399-401` 의 `psi <= 1e-4` 분기가 **R_constriction = 0** 을 준다.
= 그 간선의 협착 항이 근사되는 것이 아니라 **삭제**된다 (국소적으로 CONTACT_FREE).

★ 이미 아는 것은 **하한뿐**이다
`case_master.csv` 의 `A_binding_share_*_pct.geom` 은 **`geom` cap 이 결속한** 접촉만 센다
(163/163 케이스에서 > 0, 접촉 가중 전체 3.966 % · AM-SE 13.843 %).  그러나 실측 사다리가
보여주듯 **`tabor` 가 먼저 문턱을 넘는다** — r_SE 0.5 <-> r_AM 6.0 에서 psi->0 은
delta = 0.10234 um (binding=tabor) 부터이고 `geom` 결속은 delta = 0.16292 um 부터다.
⇒ geom 결속률은 삭제율의 **하한**이고, 진짜 값은 **아직 아무도 재지 않았다**.

★ 이 도구가 재는 것 (판정 문턱은 하나다)

    삭제 <=> a >= s_star * R_min,  s_star = 1 - (1e-4)**(2/3) = 0.99784556531
          <=> A_final >= (s_star**2) * pi * R_min**2   (= 0.99570 * pi * R_min**2)

어느 cap 이 결속했는지와 **무관**하다.  결속 라벨은 진단용으로 같이 센다.

⚠ **계산을 바꾸지 않는다** — 읽기 전용 후처리다.  솔버도 코퍼스도 건드리지 않는다.
⚠ **Physics 가지 전용**이다.  Hertz-명명 가지에는 이 clamp 자체가 없다
   (`contact_mode == 'physics'` 안에만 있다) -> `--mode hertzian` 은 대조용이다.
⚠ 이 컨테이너에는 `contacts.csv` 가 없다 (webapp/results 에 reports 만).
   **코퍼스가 있는 머신에서** 돌린다.

사용:
  python3 scripts/audit_constriction_deleted.py                 # 전 케이스
  python3 scripts/audit_constriction_deleted.py --limit 5
  python3 scripts/audit_constriction_deleted.py --out-csv docs/data/constriction_deleted.csv
  python3 scripts/audit_constriction_deleted.py --selftest
"""
from __future__ import annotations
import argparse
import csv
import importlib.util
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / 'scripts'


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


#  규율 (1): 케이스 탐색·로딩은 **이 리포에 이미 있다** — 다시 짜지 않는다.
#  `extract_se_network_diagnostics` 의 로더는 2026-09-13 에 L4-06(내용 지문 중복제거)·
#  L4-07(메타 병합)로 고쳐졌으므로 그 수정을 그대로 물려받는다.
_SED = _load('_sed_loader', SCRIPTS / 'extract_se_network_diagnostics.py')
_PC = _load('_pc_area', SCRIPTS / 'plastic_coverage.py')

#  psi <= 1e-4 분기가 켜지는 지점 (network_conductivity.py:397 의 리터럴과 한 출처)
PSI_FLOOR = 1e-4
S_STAR = 1.0 - PSI_FLOOR ** (2.0 / 3.0)          # 0.99784556531
AREA_FRAC = S_STAR ** 2                           # 0.99570...  (A / (pi R_min^2))


def constriction_deleted(A_final: float, r_min: float) -> bool:
    """이 접촉의 협착 항이 삭제되는가 (원판 환산 후 psi <= 1e-4).

    `network_conductivity.py:323`·`:395-397` 과 **같은 산술**이다:
        a = sqrt(A/pi);  a_eff = min(a, r_min);  psi = (1 - a_eff/r_min)**1.5
    """
    if r_min <= 0 or A_final <= 0:
        return False
    a = math.sqrt(A_final / math.pi)
    a_eff = min(a, r_min)
    psi = max(1.0 - a_eff / r_min, 0.0) ** 1.5
    return psi <= PSI_FLOOR


def _pair_kind(t1: str, t2: str) -> str:
    am = {'AM_P', 'AM_S', 'AM'}
    a1, a2 = t1 in am, t2 in am
    if a1 and a2:
        return 'AM_AM'
    if a1 != a2:
        return 'AM_SE'
    return 'SE_SE'


def audit_case(case_dir: Path, mode: str = 'physics') -> dict | None:
    """한 케이스의 접촉을 전수로 훑어 삭제율을 낸다."""
    try:
        atoms, type_map, scale, _meta = _SED.load_case(case_dir)
        contacts = _SED.load_contacts(case_dir)
    except Exception as e:
        print(f'  [{case_dir.name}] SKIP — {type(e).__name__}: {e}')
        return None
    if not contacts:
        return None

    n_by_kind = Counter()
    del_by_kind = Counter()
    bind_by_kind = defaultdict(Counter)
    del_bind = Counter()
    n_no_delta = 0

    for c in contacts:
        a1 = atoms.get(c['id1'])
        a2 = atoms.get(c['id2'])
        if a1 is None or a2 is None:
            continue
        r1, r2 = a1['radius'], a2['radius']
        delta = c['delta']
        if not (r1 > 0 and r2 > 0):
            continue
        kind = _pair_kind(type_map.get(a1['type'], '?'), type_map.get(a2['type'], '?'))
        n_by_kind[kind] += 1
        if delta <= 0:
            n_no_delta += 1
            continue
        R_star = (r1 * r2) / (r1 + r2)
        R_min = min(r1, r2)
        try:
            A, _regime, comp = _PC.film_area_from_overlap(
                delta, R_star, R_min=R_min, ligg_area=c['contact_area'],
                mode=mode, return_components=True)
        except Exception:
            continue
        b = (comp or {}).get('binding') or 'none'
        bind_by_kind[kind][b] += 1
        if constriction_deleted(A, R_min):
            del_by_kind[kind] += 1
            del_bind[b] += 1

    tot_n = sum(n_by_kind.values())
    tot_d = sum(del_by_kind.values())
    row = {
        'case': case_dir.name,
        'mode': mode,
        'n_contacts': tot_n,
        'n_no_delta': n_no_delta,
        'n_deleted': tot_d,
        'deleted_pct': round(100.0 * tot_d / tot_n, 4) if tot_n else 0.0,
    }
    for k in ('AM_AM', 'AM_SE', 'SE_SE'):
        n, dd = n_by_kind[k], del_by_kind[k]
        row[f'n_{k}'] = n
        row[f'deleted_{k}'] = dd
        row[f'deleted_{k}_pct'] = round(100.0 * dd / n, 4) if n else 0.0
    #  삭제된 접촉이 **어느 cap 으로** 거기 갔는가 — geom 만이 아니라는 것이 요점
    for b in ('tabor', 'volume', 'geom', 'liggghts', 'hertzian', 'elastic'):
        row[f'deleted_via_{b}'] = del_bind[b]
    return row


def main() -> int:
    ap = argparse.ArgumentParser(
        description='협착 항이 삭제된 접촉 비율 (면적 계약 S0)')
    ap.add_argument('--mode', default='physics',
                    choices=['physics', 'hertzian', 'liggghts', 'capped'],
                    help='면적 모드.  기본 physics = 생산 Physics 가지.')
    ap.add_argument('--limit', type=int, default=0, help='앞에서 N 케이스만')
    ap.add_argument('--out-csv', default='')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()

    if a.selftest:
        return _selftest()

    cases = _SED.discover_cases()
    if a.limit:
        cases = cases[:a.limit]
    print(f'케이스 {len(cases)}개 · mode={a.mode}')
    print(f'판정 문턱: A >= {AREA_FRAC:.8f} * pi * R_min^2   '
          f'(<=> a/R_min >= {S_STAR:.11f})')
    if not cases:
        print('\n⚠ 접촉 자료를 못 찾았다 — 이 도구는 `contacts.csv` 가 있는 머신에서 돌린다.')
        return 1

    rows = []
    for i, d in enumerate(cases):
        r = audit_case(d, mode=a.mode)
        if r is None:
            continue
        rows.append(r)
        print(f'  [{i+1:>3}/{len(cases)}] {r["case"][:34]:34s} '
              f'n={r["n_contacts"]:>8,d}  삭제 {r["deleted_pct"]:>6.2f} %  '
              f'(AM-SE {r["deleted_AM_SE_pct"]:>6.2f} %)')

    if not rows:
        print('집계할 행이 없다.')
        return 1

    tn = sum(r['n_contacts'] for r in rows)
    td = sum(r['n_deleted'] for r in rows)
    print('\n═══ 접촉 가중 집계 ═══')
    print(f'  케이스 {len(rows)} · 접촉 {tn:,d}')
    print(f'  협착 삭제 = {td:,d} / {tn:,d} = {100.0*td/tn:.3f} %')
    for k in ('AM_AM', 'AM_SE', 'SE_SE'):
        n = sum(r[f'n_{k}'] for r in rows)
        dd = sum(r[f'deleted_{k}'] for r in rows)
        if n:
            print(f'    {k:6s} {dd:>10,d} / {n:>10,d} = {100.0*dd/n:6.3f} %')
    print('  삭제된 접촉이 거쳐간 cap:')
    for b in ('tabor', 'volume', 'geom', 'liggghts', 'hertzian', 'elastic'):
        v = sum(r[f'deleted_via_{b}'] for r in rows)
        if v:
            print(f'    via {b:9s} {v:>10,d}  ({100.0*v/max(td,1):5.2f} % of deleted)')
    print('\n⚠ `geom` 만 세면 하한이다 — 위 표의 `via tabor` 가 그 차이다 (SELF-28).')
    print('⚠ 계산을 바꾸지 않았다.  이 값은 면적 계약 §4 의 S0 이고, S2 전환의 **사전** 기록이다.')

    if a.out_csv:
        p = Path(a.out_csv)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f'\n→ {p}')
    return 0


def _selftest() -> int:
    """★ 판정식이 **솔버와 같은 산술**인가 + 대조.

    ⚠ 대조가 요점이다 — `constriction_deleted` 를 `return True` 로 만들어도 (1)(2) 는
    통과한다.  그래서 (3) 이 *'얕은 접촉은 삭제되지 않는다'* 를 잡는다.
    """
    ok = True

    def chk(name, cond, extra=''):
        nonlocal ok
        print(('  ✓ ' if cond else '  ✗ ') + name + (f'   {extra}' if extra else ''))
        ok = ok and bool(cond)

    print('협착 삭제 판정 (면적 계약 S0)')

    # ── (1) 문턱 상수가 솔버 리터럴에서 유도되는가 ─────────────────────────
    chk('① s* = 1 − (1e-4)^(2/3) = 0.99784556531 (판정문 값과 일치)',
        abs(S_STAR - 0.99784556531) < 1e-11, f'{S_STAR:.11f}')
    chk('① 면적 문턱 = s*² · πR² = 0.99570 · πR²',
        abs(AREA_FRAC - 0.9957) < 1e-4, f'{AREA_FRAC:.8f}')
    src = (SCRIPTS / 'network_conductivity.py').read_text(encoding='utf-8')
    chk('① 솔버가 아직 같은 분기를 쓴다 (`psi > 1e-4`)',
        'psi > 1e-4' in src)
    chk('① 솔버가 아직 원판으로 읽는다 (`sqrt(A_contact / np.pi)`)',
        'np.sqrt(A_contact / np.pi)' in src)

    # ── (2) geom cap 이 결속하면 **반드시** 삭제 (반지름 무관) ─────────────
    for r in (0.1, 0.5, 1.5, 6.0):
        A_geom = 2.0 * math.pi * r * r
        if not constriction_deleted(A_geom, r):
            chk(f'② geom cap (r={r}) 이 삭제로 판정되지 않았다', False)
            break
    else:
        chk('② geom cap = 2πR² 는 **모든 반지름에서** 삭제로 판정된다', True)
    chk('② 대조: 원판 상한 πR² 의 **절반**은 삭제가 아니다',
        not constriction_deleted(0.5 * math.pi * 0.25, 0.5))

    # ── (3) 대조: tabor 가 먼저 문턱을 넘는다 (geom 만 세면 하한) ──────────
    r_se, r_am = 0.5, 6.0
    R_star = (r_se * r_am) / (r_se + r_am)
    got = {}
    for delta in (0.05, 0.12, 0.20):
        A, _reg, comp = _PC.film_area_from_overlap(
            delta * 1e-6, R_star * 1e-6, R_min=r_se * 1e-6, ligg_area=0.0,
            mode='physics', return_components=True)
        got[delta] = (comp['binding'], constriction_deleted(A * 1e12, r_se))
    chk('③ δ=0.05 은 삭제 아님 (얕은 접촉 — "항상 True" 가 아니다)',
        got[0.05] == ('tabor', False), str(got[0.05]))
    chk('③ ★ δ=0.12 은 **binding=tabor 인데 삭제** (geom 만 세면 놓친다)',
        got[0.12] == ('tabor', True), str(got[0.12]))
    chk('③ δ=0.20 은 binding=geom 이고 삭제', got[0.20] == ('geom', True),
        str(got[0.20]))

    # ── (4) 경계가 예리한가 ────────────────────────────────────────────────
    r = 0.5
    A_on = AREA_FRAC * math.pi * r * r
    chk('④ 문턱 바로 위는 삭제', constriction_deleted(A_on * (1 + 1e-9), r))
    chk('④ 문턱 바로 아래는 삭제 아님', not constriction_deleted(A_on * (1 - 1e-6), r))

    # ── (5) 계약 문서가 실재하고 이 도구를 가리키는가 ─────────────────────
    doc = ROOT / 'docs' / 'area_contract_20260913.md'
    chk('⑤ 면적 계약 문서가 있다', doc.exists())
    chk('⑤ 계약이 이 도구를 S0 으로 지목한다',
        doc.exists() and 'audit_constriction_deleted.py' in doc.read_text(encoding='utf-8'))

    print('협착 삭제 판정 SELFTEST', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
