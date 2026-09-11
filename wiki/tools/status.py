#!/usr/bin/env python3
"""LLM Wiki status — counts, verification coverage, paper/DOI coverage, recent log.

Usage: python3 wiki/tools/status.py
"""
import glob
import pathlib
import re
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

BASE = pathlib.Path(__file__).resolve().parent.parent
DIRS = ['papers', 'mechanisms', 'protocols', 'experiments', 'comparisons',
        'concepts', 'entities', 'queries', 'guides', 'questions', 'syntheses']


def parse_fm(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            km = re.match(r'^([A-Za-z][A-Za-z0-9_]*):\s*(.*)$', line)
            if km:
                fm[km.group(1)] = km.group(2).strip()
        fm['_raw'] = m.group(1)
    return fm


pages = {}
for d in DIRS:
    for f in sorted(glob.glob(str(BASE / d / '*.md'))):
        p = pathlib.Path(f)
        pages[p.stem] = (d, parse_fm(p.read_text(encoding='utf-8')))

raws = glob.glob(str(BASE / 'raw/**/*.md'), recursive=True)
digests = sorted(glob.glob(str(BASE / 'raw/papers/*.md')))
figdirs = [d for d in (BASE / 'raw' / 'figures').glob('*/') if (d / 'figures.json').is_file()]

print('=== LLM WIKI STATUS — mid-Ni NCA721 formation ===\n')
by_dir = {}
for stem, (d, fm) in pages.items():
    by_dir[d] = by_dir.get(d, 0) + 1
print(f'wiki pages: {len(pages)}  (' +
      ' · '.join(f'{d} {by_dir.get(d, 0)}' for d in DIRS) + ')')
print(f'raw sources: {len(raws)}  (digest {len(digests)} · 그림 폴더 {len(figdirs)})')

# 논문 노트 ↔ digest 커버리지
notes = {s for s, (d, _) in pages.items() if d == 'papers'}
dig = {pathlib.Path(x).stem for x in digests}
if notes or dig:
    print(f'papers: 노트 {len(notes)} · digest {len(dig)} · 노트 없는 digest {len(dig - notes)} · digest 없는 노트 {len(notes - dig)}')
    n_doi = 0
    for s in notes:
        m = re.search(r'^\s+doi:\s*(.+)$', pages[s][1].get('_raw', ''), re.M)
        if m and m.group(1).strip().strip('"\'').lower() not in ('', 'null'):
            n_doi += 1
    print(f'        DOI 있는 노트 {n_doi}/{len(notes)}')


def dist(key):
    out = {}
    for _, (_, fm) in pages.items():
        v = fm.get(key, '?')
        out[v] = out.get(v, 0) + 1
    return ' · '.join(f'{k} {v}' for k, v in sorted(out.items()))


print(f'\nconfidence:         {dist("confidence")}')
print(f'verificationStatus: {dist("verificationStatus")}')
print(f'explored:           {dist("explored")}')

open_q = sorted(s for s, (d, fm) in pages.items()
                if d == 'questions' and fm.get('status', 'open') in ('open', 'active'))
if open_q:
    print(f'\n열린 질문 ({len(open_q)}): ' + ' · '.join(open_q))

unverified = sorted(s for s, (_, fm) in pages.items()
                    if fm.get('verificationStatus') == 'unverified')
if unverified:
    print(f'\nverify 대기 (unverified {len(unverified)}):')
    print('  ' + ' · '.join(unverified))

background = sorted(s for s, (_, fm) in pages.items()
                    if fm.get('evidenceScope') == 'synthesis-only')
if background:
    print(f'\n미검증 배경 페이지 (근거 논문 없음 — ingest 로 채울 자리, {len(background)}):')
    print('  ' + ' · '.join(background))

log = (BASE / 'log.md').read_text(encoding='utf-8')
entries = re.findall(r'^## \[.*$', log, re.M)
print(f'\n최근 log ({len(entries)} entries, last 5):')
for e in entries[-5:]:
    print('  ' + e.lstrip('# '))
