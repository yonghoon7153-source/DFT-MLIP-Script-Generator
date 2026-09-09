#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""감사 원시 finding 에 **기계 판독 가능한 판정 상태**를 붙인다 (원장 AUD-07).

⚠⚠ **왜 이 파일이 생겼나** (2026-09-09, Codex 리뷰 Q2-3)

`docs/data/audit_20260909/residual_buckets.json` 의 finding 135 건 중 `status` 나
`verification_status` 를 가진 것이 **0 건**이다.  그런데 같은 파일이 `findings` 배열과
`surviving_p0p1` 배열로 **후보와 적대검증 생존을 갈라 놓고**, 그 사이의 관계는 산문에만
있다.  ⇒ 후속 집계자가 `severity == 'P1'` 만 골라 읽으면 **후보와 확정이 합쳐진다.**

이 도구가 고치는 방식은 원본을 건드리는 것이 **아니다** — 원본은 감사 출력의 박제라
한 바이트도 바꾸지 않는다 (`source.sha256` 으로 못박고, 바뀌면 재-판정을 요구한다).
대신 **별도 판정 원장**에 안정 ID 와 상태·근거·주체를 붙인다.

  · 안정 ID = `AUDR-<sha1(bucket|file|kind|claim)[:8]>` — 내용 주소라 **재정렬·추가에
    흔들리지 않는다** (일련번호는 항목이 하나 늘면 전부 밀린다).
  · 상태 = candidate / self_confirmed / independently_verified / rejected / incomplete.
  · ⚠ **검증을 지어내지 않는다.**  초기 판정은 원본이 실제로 말하는 것만 옮긴다 —
    `surviving_p0p1` 에 있는 3 건은 *그 감사 자신의 적대 패스*를 통과한 것이므로
    `self_confirmed` 이고, **독립 검증자가 본 것이 아니다**.  나머지는 전부 `candidate`.

  python3 scripts/check_audit_adjudication.py            # 검증 (기본)
  python3 scripts/check_audit_adjudication.py --report   # 상태 x 심각도 표
  python3 scripts/check_audit_adjudication.py --init     # 원장 초기 생성
  python3 scripts/check_audit_adjudication.py --selftest
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SOURCE = os.path.join('docs', 'data', 'audit_20260909', 'residual_buckets.json')
LEDGER = os.path.join('docs', 'reviews', 'audit_adjudication_20260909.json')
FINDINGS = os.path.join('docs', 'reviews', 'findings.json')

#: 판정 상태.  ⚠ `candidate` 는 *아직 아무도 확인 안 했다* 는 뜻이고, 그것이 기본값이다.
STATUSES = ('candidate', 'self_confirmed', 'independently_verified',
            'rejected', 'incomplete')
#: 이 감사를 돌린 주체.  `independently_verified` 는 **이 주체가 아닌** 누군가여야 한다.
OWNER = 'claude'
#: 상태별로 **반드시 있어야 하는** 필드.  없으면 그 상태를 주장할 수 없다.
REQUIRED = {
    'candidate': (),
    'self_confirmed': ('verification_note', 'verified_in'),
    'independently_verified': ('verification_note', 'verified_by'),
    'rejected': ('verification_note',),
    'incomplete': ('verification_note',),
}


def row_id(bucket, path, kind, claim):
    """내용 주소 안정 ID.  재정렬·항목 추가에 흔들리지 않는다."""
    raw = '|'.join(str(x) for x in (bucket, path, kind, claim))
    return 'AUDR-' + hashlib.sha1(raw.encode('utf-8')).hexdigest()[:8]


def _sha256(path):
    with open(path, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def raw_findings(root=ROOT, source=None):
    """원시 감사 출력 → 판정 대상 목록 (원본은 읽기만 한다)."""
    src = source or os.path.join(root, SOURCE)
    with open(src, encoding='utf-8') as fh:
        buckets = json.load(fh)
    surviving = set()
    out, seen = [], {}
    for b in buckets:
        for f in (b.get('surviving_p0p1') or []):
            surviving.add(row_id(b.get('bucket'), f.get('file'), f.get('kind'),
                                 f.get('claim')))
    for b in buckets:
        for f in (b.get('findings') or []):
            rid = row_id(b.get('bucket'), f.get('file'), f.get('kind'), f.get('claim'))
            if rid in seen:
                #  같은 (bucket, file, kind, claim) 이 두 번이면 ID 가 안 갈린다.
                #  조용히 합치면 한 건이 사라지므로 **드러낸다**.
                seen[rid] += 1
                continue
            seen[rid] = 1
            out.append({'id': rid, 'bucket': b.get('bucket'), 'file': f.get('file'),
                        'kind': f.get('kind'), 'severity': f.get('severity'),
                        'surviving_p0p1': rid in surviving})
    dupes = sorted(k for k, v in seen.items() if v > 1)
    return out, dupes


def load_ledger(root=ROOT, path=None):
    with open(path or os.path.join(root, LEDGER), encoding='utf-8') as fh:
        return json.load(fh)


def build_ledger(root=ROOT):
    """원본이 **실제로 말하는 것만** 옮겨 초기 원장을 만든다."""
    rows, dupes = raw_findings(root)
    if dupes:
        raise SystemExit(f'원본에 ID 가 겹치는 항목이 있다: {dupes}')
    out = []
    for r in rows:
        row = collections.OrderedDict(
            (('id', r['id']), ('bucket', r['bucket']), ('file', r['file']),
             ('kind', r['kind']), ('severity', r['severity'])))
        if r['surviving_p0p1']:
            row['status'] = 'self_confirmed'
            row['verified_in'] = SOURCE + '#surviving_p0p1'
            row['verification_note'] = (
                '그 감사 자신의 적대 패스를 통과했다 (`surviving_p0p1`).  '
                '⚠ **독립 검증자가 본 것이 아니다** — 승격하려면 다른 주체의 재현이 필요하다.')
        else:
            row['status'] = 'candidate'
        row['promoted_to'] = None
        out.append(row)
    return collections.OrderedDict((
        ('note', '감사 원시 finding 의 **판정 원장** (AUD-07).  원본은 감사 출력의 박제라 '
                 '고치지 않는다 — 여기에만 상태를 붙인다.  `severity` 만 보고 집계하면 '
                 '후보와 확정이 합쳐지므로 **반드시 `status` 와 함께** 읽을 것.'),
        ('source', collections.OrderedDict((
            ('path', SOURCE), ('sha256', _sha256(os.path.join(root, SOURCE))),
            ('note', '이 해시가 어긋나면 원본이 바뀐 것이다 — 판정을 다시 해야 한다.')))),
        ('statuses', list(STATUSES)),
        ('owner', OWNER),
        ('rows', out)))


def validate(ledger, root=ROOT, raw=None, finding_ids=None):
    """→ 문제 목록 (빈 목록 = 통과)."""
    probs = []
    src_rel = ((ledger.get('source') or {}).get('path')) or SOURCE
    src_abs = os.path.join(root, src_rel)
    if not os.path.exists(src_abs):
        return [f'원본이 없다: {src_rel}']
    want = (ledger.get('source') or {}).get('sha256')
    got = _sha256(src_abs)
    if want != got:
        probs.append(f'원본 sha256 불일치 — 원본이 바뀌었다 (원장 {want} vs 실물 {got}).  '
                     f'판정을 다시 하고 해시를 갱신할 것')
    if raw is None:
        raw, dupes = raw_findings(root, source=src_abs)
        for d in dupes:
            probs.append(f'원본에 ID 가 겹치는 항목이 있다 ({d}) — 한 건이 조용히 사라진다')
    by_raw = {r['id']: r for r in raw}
    rows = ledger.get('rows') or []
    by_row = {}
    for r in rows:
        rid = r.get('id')
        if rid in by_row:
            probs.append(f'{rid}: 원장에 두 번 있다')
        by_row[rid] = r
    missing = sorted(set(by_raw) - set(by_row))
    orphan = sorted(set(by_row) - set(by_raw))
    if missing:
        probs.append(f'원본에 있는데 판정이 없다 {len(missing)} 건: {missing[:5]}')
    if orphan:
        probs.append(f'원본에 없는 판정 행 {len(orphan)} 건: {orphan[:5]}')
    owner = (ledger.get('owner') or OWNER).strip().casefold()
    for rid, r in sorted(by_row.items()):
        st = r.get('status')
        if st not in STATUSES:
            probs.append(f'{rid}: status={st!r} 가 등록된 값이 아니다 {STATUSES}')
            continue
        for key in REQUIRED.get(st, ()):
            if not r.get(key):
                probs.append(f'{rid}: status={st} 인데 {key} 가 없다 — '
                             f'근거 없이 상태를 주장할 수 없다')
        if st == 'candidate' and (r.get('verified_by') or r.get('verified_in')):
            probs.append(f'{rid}: candidate 인데 검증 필드를 들고 있다 — '
                         f'후보는 아직 아무도 확인하지 않은 것이다')
        if st == 'independently_verified':
            who = (r.get('verified_by') or '').strip().casefold()
            if who and who == owner:
                probs.append(f'{rid}: independently_verified 인데 verified_by 가 '
                             f'감사 주체({r.get("verified_by")}) 자신이다')
        #  원본과 어긋나면 판정이 다른 항목을 가리키게 된다.
        base = by_raw.get(rid)
        if base:
            for key in ('file', 'kind', 'severity', 'bucket'):
                if r.get(key) is not None and r.get(key) != base.get(key):
                    probs.append(f'{rid}: {key} 가 원본과 다르다 '
                                 f'({r.get(key)!r} vs {base.get(key)!r})')
        pro = r.get('promoted_to')
        if pro:
            if finding_ids is None:
                finding_ids = _finding_ids(root)
            if pro not in finding_ids:
                probs.append(f'{rid}: promoted_to={pro} 가 findings.json 에 없다')
    return probs


def _finding_ids(root=ROOT):
    try:
        with open(os.path.join(root, FINDINGS), encoding='utf-8') as fh:
            d = json.load(fh)
    except OSError:
        return set()
    items = d.get('findings') if isinstance(d, dict) else d
    return {f.get('id') for f in (items or [])}


def report(ledger):
    """상태 x 심각도.  **이 표가 AUD-07 의 요점이다** — `severity` 만 보면 안 된다."""
    grid = collections.Counter()
    for r in (ledger.get('rows') or []):
        grid[(r.get('severity'), r.get('status'))] += 1
    sevs = sorted({s for s, _ in grid}, key=lambda x: str(x))
    lines = ['판정 상태 x 심각도 (후보와 확정을 **합치지 않는다**)', '']
    head = f'{"severity":<10}' + ''.join(f'{s:>24}' for s in STATUSES) + f'{"합":>7}'
    lines += [head, '-' * len(head)]
    for s in sevs:
        row = [grid[(s, st)] for st in STATUSES]
        lines.append(f'{str(s):<10}' + ''.join(f'{v:>24}' for v in row) + f'{sum(row):>7}')
    tot = [sum(grid[(s, st)] for s in sevs) for st in STATUSES]
    lines.append(f'{"합":<10}' + ''.join(f'{v:>24}' for v in tot) + f'{sum(tot):>7}')
    return '\n'.join(lines)


# ─────────────────────────── selftest ────────────────────────────────
def _selftest():
    import copy
    import tempfile
    n = [0, 0]

    def ok(name, cond):
        n[1] += 1
        n[0] += bool(cond)
        print(f'  {"PASS" if cond else "FAIL"}  {name}')

    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, os.path.dirname(SOURCE)), exist_ok=True)
        os.makedirs(os.path.join(td, os.path.dirname(LEDGER)), exist_ok=True)
        src = os.path.join(td, SOURCE)
        buckets = [{'bucket': 'b#1',
                    'findings': [{'file': 'a.csv', 'kind': 'contradiction',
                                  'severity': 'P1', 'claim': 'c1'},
                                 {'file': 'b.csv', 'kind': 'stale',
                                  'severity': 'P2', 'claim': 'c2'}],
                    'surviving_p0p1': [{'file': 'a.csv', 'kind': 'contradiction',
                                        'severity': 'P1', 'claim': 'c1'}]}]
        with open(src, 'w', encoding='utf-8') as fh:
            json.dump(buckets, fh, ensure_ascii=False)
        with open(os.path.join(td, FINDINGS), 'w', encoding='utf-8') as fh:
            json.dump({'findings': [{'id': 'AUD-99'}]}, fh)

        led = build_ledger(td)
        ok('1) 원장을 만들면 원본의 모든 항목을 덮는다',
           len(led['rows']) == 2 and not validate(led, td))
        _sv = [r for r in led['rows'] if r['status'] == 'self_confirmed']
        ok('2) ★ `surviving_p0p1` 만 self_confirmed 이고 나머지는 candidate '
           '(검증을 지어내지 않는다)',
           len(_sv) == 1 and _sv[0]['file'] == 'a.csv'
           and all(r['status'] == 'candidate' for r in led['rows'] if r not in _sv))
        ok('3) ★ 그 한 건도 **independently_verified 가 아니다** '
           '(같은 감사의 적대 패스는 독립 검증이 아니다)',
           all(r['status'] != 'independently_verified' for r in led['rows']))
        ok('4) ID 가 내용 주소다 — 순서를 바꿔도 같은 ID',
           row_id('b#1', 'a.csv', 'contradiction', 'c1')
           == _sv[0]['id'])

        #  ── 음성 대조 — 통과만 하는 검사는 없는 것과 같다 ──────────
        bad = copy.deepcopy(led)
        bad['source']['sha256'] = '0' * 64
        ok('5) 음성 — 원본 해시가 어긋나면 잡는다 (박제가 바뀌면 재-판정)',
           any('sha256' in p for p in validate(bad, td)))

        bad = copy.deepcopy(led)
        bad['rows'].pop()
        ok('6) 음성 — 판정이 빠진 원시 항목을 잡는다',
           any('판정이 없다' in p for p in validate(bad, td)))

        bad = copy.deepcopy(led)
        bad['rows'].append(dict(bad['rows'][0], id='AUDR-deadbeef'))
        ok('7) 음성 — 원본에 없는 유령 판정 행을 잡는다',
           any('원본에 없는' in p for p in validate(bad, td)))

        bad = copy.deepcopy(led)
        bad['rows'][0]['status'] = 'probably_fine'
        ok('8) 음성 — 등록 안 된 상태값을 잡는다',
           any('등록된 값이 아니다' in p for p in validate(bad, td)))

        bad = copy.deepcopy(led)
        for r in bad['rows']:
            if r['status'] == 'candidate':
                r['verified_by'] = 'codex'
        ok('9) ★★ 음성 — candidate 가 검증 필드를 들고 있으면 잡는다 '
           '(후보와 확정이 합쳐지는 바로 그 자리)',
           any('후보는 아직' in p for p in validate(bad, td)))

        bad = copy.deepcopy(led)
        for r in bad['rows']:
            if r['status'] == 'self_confirmed':
                r['status'] = 'independently_verified'
                r['verified_by'] = OWNER
        ok('10) ★ 음성 — 감사 주체 자신이 독립 검증자가 될 수 없다',
           any('자신이다' in p for p in validate(bad, td)))

        bad = copy.deepcopy(led)
        for r in bad['rows']:
            if r['status'] == 'self_confirmed':
                r['verification_note'] = ''
        ok('11) 음성 — 근거 없는 상태 주장을 잡는다',
           any('없다 — 근거 없이' in p for p in validate(bad, td)))

        bad = copy.deepcopy(led)
        bad['rows'][0]['promoted_to'] = 'AUD-없는것'
        ok('12) 음성 — 존재하지 않는 finding 으로의 승격을 잡는다',
           any('findings.json 에 없다' in p for p in validate(bad, td)))

        bad = copy.deepcopy(led)
        bad['rows'][0]['severity'] = 'P0'
        ok('13) 음성 — 판정 행이 원본과 다른 심각도를 적으면 잡는다',
           any('원본과 다르다' in p for p in validate(bad, td)))

        ok('14) 상태 x 심각도 표가 상태를 **가른다**',
           'candidate' in report(led) and 'self_confirmed' in report(led))

    #  ── 리포 실물 ────────────────────────────────────────────────
    #    ⚠ 원장이 없으면 15) 가 **조용히 사라진다** = false-green.  드러내 놓는다
    #    (인자 없는 실행은 원장이 없으면 그 자체로 실패한다).
    if os.path.exists(os.path.join(ROOT, LEDGER)):
        ok('15) ★ 리포의 판정 원장이 지금 자기일관이다',
           not validate(load_ledger(ROOT), ROOT))
    else:
        print(f'  SKIP  15) 리포에 {LEDGER} 이 아직 없다 — `--init` 로 만들 것 '
              '(인자 없는 실행은 이 상태에서 실패한다)')
    print(f'\ncheck_audit_adjudication selftest: {n[0]}/{n[1]} PASS')
    return 0 if n[0] == n[1] else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--init', action='store_true', help='원장을 원본에서 새로 만든다')
    ap.add_argument('--force', action='store_true', help='--init 로 기존 원장을 덮는다')
    ap.add_argument('--report', action='store_true', help='상태 x 심각도 표')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)

    if a.selftest:
        return _selftest()

    path = os.path.join(ROOT, LEDGER)
    if a.init:
        if os.path.exists(path) and not a.force:
            raise SystemExit(f'{LEDGER} 이 이미 있다 — 덮으려면 --force '
                             f'(사람이 적은 판정이 날아간다)')
        led = build_ledger(ROOT)
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(led, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
        print(f'{LEDGER} — 판정 행 {len(led["rows"])} 건 (전부 원본이 말하는 것만)')
        return 0

    if not os.path.exists(path):
        raise SystemExit(f'{LEDGER} 이 없다 — `--init` 로 먼저 만들 것')
    led = load_ledger(ROOT)
    probs = validate(led, ROOT)
    if a.report:
        print(report(led))
        print()
    for p in probs:
        print(f'  ⛔ {p}')
    if probs:
        print(f'\n✗ 판정 원장에 문제 {len(probs)} 건')
        return 1
    counts = collections.Counter(r.get('status') for r in led['rows'])
    print(f'판정 원장 자기일관 ✓  ({len(led["rows"])} 건 — '
          + ' · '.join(f'{k} {counts[k]}' for k in STATUSES if counts[k]) + ')')
    print('⚠ candidate 는 **아직 아무도 확인하지 않은 것**이다 — severity 만 보고 '
          '집계하지 말 것 (AUD-07 이 열린 이유).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
