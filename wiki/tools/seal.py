#!/usr/bin/env python3
"""seal.py — raw 파일의 sha256 봉인 (wiki/SCHEMA.md Raw Frontmatter).

해시 = frontmatter 뒤 본문(앞 빈 줄 제거)의 sha256. 이 도구는 **아직 봉인되지 않은** raw 파일
(`sha256: PENDING` 또는 sha256 줄 없음)에만 해시를 써 넣는다. 이미 봉인된 파일은 건드리지 않는다
(raw 는 불변층 — 원문이 바뀌었다면 새 -v2 파일을 만든다).

Usage:
  python3 wiki/tools/seal.py wiki/raw/papers/<slug>.md      # 봉인
  python3 wiki/tools/seal.py --check wiki/raw/papers/<slug>.md   # 검증만 (exit 1 이면 불일치)
"""
import hashlib
import pathlib
import re
import sys

FM = re.compile(r'^---\n(.*?)\n---\n(.*)$', re.S)


def body_hash(text: str) -> str:
    m = FM.match(text)
    if not m:
        raise SystemExit('frontmatter 가 없다 (--- 로 시작해야 한다)')
    return hashlib.sha256(m.group(2).lstrip('\n').encode()).hexdigest()


def main(argv):
    check = '--check' in argv
    paths = [a for a in argv if not a.startswith('--')]
    if not paths:
        raise SystemExit(__doc__)
    rc = 0
    for p in paths:
        path = pathlib.Path(p)
        text = path.read_text(encoding='utf-8')
        h = body_hash(text)
        m = FM.match(text)
        fm = m.group(1)
        cur = re.search(r'^sha256:\s*(\S*)\s*$', fm, re.M)
        declared = cur.group(1) if cur else ''
        if check:
            ok = declared == h
            print(f'{path}: {"OK" if ok else "MISMATCH"} (declared {declared[:12]}… actual {h[:12]}…)')
            rc |= 0 if ok else 1
            continue
        if declared and declared.upper() != 'PENDING':
            if declared == h:
                print(f'{path}: 이미 봉인됨 (일치)')
            else:
                print(f'{path}: 이미 봉인된 raw 와 본문이 다르다 — raw 는 불변. 새 -v2 파일을 만들어라', file=sys.stderr)
                rc |= 1
            continue
        if cur:
            new_fm = fm[:cur.start()] + f'sha256: {h}' + fm[cur.end():]
        else:
            new_fm = fm + f'\nsha256: {h}'
        path.write_text('---\n' + new_fm + '\n---\n' + m.group(2), encoding='utf-8')
        print(f'{path}: sealed {h[:12]}…')
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
