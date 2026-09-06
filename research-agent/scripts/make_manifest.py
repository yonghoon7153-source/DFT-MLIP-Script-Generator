#!/usr/bin/env python3
"""전달 매니페스트 생성기 — 사람이 세지 않는다.

v0.1.6 과 v0.1.8 에서 같은 실패가 났다: 회신문의 파일 목록과 실제로 도착한 파일이 달랐고,
두 번 다 "1:1 대조했다"고 적혀 있었다. 목록도 사람이 쓰고 대조도 사람이 하면 같은 순간에
두 번 실수해서 안 걸린다.

⇒ 목록을 **실제 파일에서 기계로 뽑는다.** 이 스크립트의 출력을 회신문에 그대로 붙이면,
   받는 쪽이 도착한 파일로 같은 명령을 돌려 해시를 비교할 수 있다. 그러면 유실이
   **어느 구간에서 났든**(보내는 쪽 누락 / 전송 중 유실 / 압축 중 누락) 잡힌다.

    python scripts/make_manifest.py 0.1.9 research_agent/cli.py tests/test_feedback.py ...
    python scripts/make_manifest.py --verify MANIFEST_0.1.9.md      # 받는 쪽에서
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _digest(p: Path) -> tuple[str, int, int]:
    data = p.read_bytes()
    lines = data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)
    return hashlib.sha256(data).hexdigest()[:16], lines, len(data)


def build(version: str, paths: list[str]) -> str:
    rows, missing = [], []
    for rel in sorted(dict.fromkeys(paths)):
        p = (ROOT / rel) if not Path(rel).is_absolute() else Path(rel)
        if not p.exists():
            missing.append(rel)
            continue
        sha, lines, size = _digest(p)
        rows.append((rel, lines, size, sha))
    out = [f"# 전달 매니페스트 — v{version}", "",
           f"**{len(rows)}개.** 받는 쪽에서 확인:",
           "```bash",
           f"python scripts/make_manifest.py --verify MANIFEST_{version}.md",
           "```",
           "해시가 다르거나 파일이 없으면 그 줄이 `MISMATCH`/`MISSING` 으로 찍힌다.",
           "**하나라도 걸리면 병합하지 말고 회신해 주십시오.**", "",
           "| 파일 | 줄 | 바이트 | sha256[:16] |", "|---|---:|---:|---|"]
    out += [f"| `{r}` | {l} | {s} | `{h}` |" for r, l, s, h in rows]
    if missing:
        out += ["", "⛔ **보내는 쪽에서 찾지 못한 파일** (전달 전에 해결할 것):"]
        out += [f"- `{m}`" for m in missing]
    return "\n".join(out) + "\n"


def verify(manifest: Path) -> int:
    text = manifest.read_text(encoding="utf-8")
    rows = re.findall(r"^\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*`([0-9a-f]+)`\s*\|$",
                      text, re.M)
    if not rows:
        print("매니페스트에서 파일 표를 찾지 못했다.", file=sys.stderr)
        return 2
    bad = 0
    for rel, lines, size, sha in rows:
        p = ROOT / rel
        if not p.exists():
            print(f"MISSING   {rel}")
            bad += 1
            continue
        got_sha, got_lines, got_size = _digest(p)
        if got_sha != sha:
            print(f"MISMATCH  {rel}  (기대 {sha} / 실제 {got_sha}, {lines}→{got_lines}줄)")
            bad += 1
        else:
            print(f"ok        {rel}")
    print(f"\n{len(rows) - bad}/{len(rows)} 일치" + ("" if not bad else f"  ⛔ {bad}건 문제 — 병합하지 말 것"))
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--verify":
        return verify(Path(argv[1]))
    print(build(argv[0], argv[1:]), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
