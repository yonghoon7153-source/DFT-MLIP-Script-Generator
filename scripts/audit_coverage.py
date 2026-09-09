#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""감사 커버리지를 **재현 가능하게** 센다 — 산문에 박힌 일회용 스니펫을 대체한다.

⚠⚠ **왜 이 파일이 생겼나 (2026-09-09, Codex 리뷰 Q2-1)**

`docs/reviews/fable_selfreview_request_20260909.md` 에 공개했던 재현 스니펫에 결함이 둘
있었고, 둘 다 **커버리지를 부풀리는 방향**이었다:

  ① **디렉터리 항목을 `현재` 파일 집합으로 펼쳤다.**  1차 감사는 `docs/reviews/` 를 한 줄로
     적었는데, 그 뒤에 그 폴더에 새 파일이 생기면 **감사가 존재하지도 않던 파일을 읽었다고**
     세어진다.  실측: 오늘 만든 `fable_selfreview_request_20260909.md` ·
     `codex_request_v3_audit_20260909.md` 두 개가 1차 감사 커버리지에 편입돼
     디렉터리 전개가 291 → 293 으로 늘었다.  **감사 시점 스냅샷에 고정해야 한다.**
  ② **`.lstrip('./')` 는 접두사 제거가 아니라 문자 제거다.**  `.claude/settings.json` 이
     `claude/settings.json` 으로 망가져 매칭에 실패했다 (dotfile 9 개).

⇒ 이 도구는 ① 을 **스냅샷 고정**으로, ② 를 정확한 접두사 제거로 고친다.

★★ **그리고 이 숫자가 무엇이 아닌지**:
   경로를 돌려받았다는 것은 **누락이 없다**는 뜻이지 **읽었다**는 뜻이 아니다.  배정 목록을
   그대로 반납하는 프로그램도 이 계약을 만족한다 (Codex Q2-2).  그래서 지표 이름이
   `inventory_returned` 이고 `read`·`reviewed` 가 아니다.

  python3 scripts/audit_coverage.py                 # 현재 HEAD 기준
  python3 scripts/audit_coverage.py --snapshot SHA  # 감사 시점 트리에 고정 (권장)
  python3 scripts/audit_coverage.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
AUDIT_DIR = os.path.join('docs', 'data', 'audit_20260909')
REPO_PREFIX = ROOT.rstrip('/') + '/'


def _norm(path):
    """절대경로를 리포 상대경로로.  ⚠ `lstrip` 을 쓰지 않는다 — 문자 제거라 dotfile 이 깨진다."""
    p = (path or '').strip()
    if p.startswith(REPO_PREFIX):
        p = p[len(REPO_PREFIX):]
    while p.startswith('./'):
        p = p[2:]
    return p


def tracked_at(snapshot=None):
    """대상 스냅샷의 추적 파일 집합.  `None` 이면 작업 트리."""
    if snapshot:
        out = subprocess.run(['git', 'ls-tree', '-r', '-z', '--name-only', snapshot],
                             cwd=ROOT, capture_output=True)
    else:
        out = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True)
    return {p for p in out.stdout.decode('utf-8', 'replace').split('\0') if p}


def _expand_dirs(entries, tracked):
    """디렉터리 항목 → 그 아래 파일들.  **대상 스냅샷의 집합만** 쓴다 (①)."""
    got = set()
    for d in entries:
        pre = d.rstrip('/') + '/'
        got |= {t for t in tracked if t.startswith(pre)}
    return got


def measure(snapshot=None):
    tracked = tracked_at(snapshot)
    d = os.path.join(ROOT, AUDIT_DIR)

    def _load(name):
        with open(os.path.join(d, name), encoding='utf-8') as f:
            return json.load(f)

    explicit, dir_entries = set(), set()
    for s in _load('audit1_scopes.json'):
        for i in (s.get('inventory') or []):
            p = _norm(i.get('path'))
            if not p:
                continue
            if p in tracked:
                explicit.add(p)
            elif os.path.isdir(os.path.join(ROOT, p)):
                dir_entries.add(p)
    a1_dirs = _expand_dirs(dir_entries, tracked)

    a2 = {p for p in (_norm(i.get('path'))
                      for b in _load('gap_partial_buckets.json')
                      for i in (b.get('inventory') or [])) if p in tracked}
    a3 = {p for p in (_norm(x) for x in _load('residual_inventoried.json')) if p in tracked}

    strict = explicit | a2 | a3
    lenient = strict | a1_dirs
    return {
        'snapshot': snapshot or 'working-tree',
        'tracked_files': len(tracked),
        'audit1_explicit': len(explicit),
        'audit1_directory_entries': len(dir_entries),
        'audit1_via_directory_expansion': len(a1_dirs),
        'audit2_gap_partial': len(a2),
        'audit3_residual': len(a3),
        #  ★ 이름이 `inventory_returned` 인 이유는 파일 머리 주석 참조 (읽음 ≠ 반납).
        'inventory_returned_strict': len(strict),
        'inventory_returned_strict_pct': round(100 * len(strict) / len(tracked), 1),
        'inventory_returned_with_dir_expansion': len(lenient),
        'inventory_returned_with_dir_expansion_pct': round(100 * len(lenient) / len(tracked), 1),
        'not_returned': sorted(tracked - lenient),
    }


def _selftest():
    ok, fail = 0, []

    def chk(name, cond):
        nonlocal ok
        (globals().__setitem__('_', None))
        if cond:
            ok += 1
            print(f'  PASS  {name}')
        else:
            fail.append(name)
            print(f'  FAIL  {name}')

    #  ① dotfile 이 안 깨진다 (옛 `lstrip('./')` 반례)
    chk('1) ★ dotfile 경로가 보존된다 (.lstrip 반례)',
        _norm('.claude/settings.json') == '.claude/settings.json'
        and _norm('.github/workflows/discipline.yml') == '.github/workflows/discipline.yml')
    chk('2) 절대경로 접두사는 제거된다',
        _norm(REPO_PREFIX + 'docs/x.md') == 'docs/x.md')
    chk('3) `./` 접두사만 제거하고 그 뒤 점은 남긴다',
        _norm('./.github/x.yml') == '.github/x.yml')

    #  ② 디렉터리 전개가 **대상 스냅샷**에만 의존한다 (미래 파일 편입 반례)
    got = _expand_dirs({'docs/reviews'}, {'docs/reviews/a.md', 'docs/reviews/b.md'})
    chk('4) ★ 디렉터리 전개가 주어진 파일 집합만 본다 (미래 파일 편입 불가)',
        got == {'docs/reviews/a.md', 'docs/reviews/b.md'})

    #  ③ 스냅샷을 고정하면 나중 커밋의 파일이 안 들어온다
    try:
        old = tracked_at('e05a7741')
        new = tracked_at(None)
        chk('5) ★ 옛 스냅샷에는 그 뒤에 만든 파일이 없다',
            'docs/reviews/codex_request_v3_audit_20260909.md' in new
            and 'docs/reviews/codex_request_v3_audit_20260909.md' not in old)
    except Exception as e:                                     # noqa: BLE001
        chk(f'5) (git 을 못 써 건너뜀 — 거짓 실패를 만들지 않는다: {e})', True)

    print(f'\naudit_coverage selftest: {ok}/{ok + len(fail)} PASS')
    return 0 if not fail else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--snapshot', help='감사 시점 커밋/트리에 고정 (권장)')
    ap.add_argument('--json', action='store_true', help='JSON 으로 출력')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    m = measure(a.snapshot)
    if a.json:
        print(json.dumps(m, ensure_ascii=False, indent=1))
        return 0
    print(f"스냅샷            {m['snapshot']}")
    print(f"추적 파일          {m['tracked_files']}")
    print(f"1차 명시 반납      {m['audit1_explicit']}")
    print(f"1차 디렉터리 항목   {m['audit1_directory_entries']} → 전개 {m['audit1_via_directory_expansion']}")
    print(f"2차 갭(부분)       {m['audit2_gap_partial']}")
    print(f"3차 잔여           {m['audit3_residual']}")
    print(f"\n★ 명시 경로 반납만  {m['inventory_returned_strict']} = {m['inventory_returned_strict_pct']} %")
    print(f"  디렉터리 전개 포함 {m['inventory_returned_with_dir_expansion']} = "
          f"{m['inventory_returned_with_dir_expansion_pct']} %")
    print(f"  안 돌아온 것       {len(m['not_returned'])}")
    print("\n⚠ 이것은 **경로 반납률**이지 열람률·검토율이 아니다 (파일 머리 주석 참조).")
    return 0


if __name__ == '__main__':
    sys.exit(main())
