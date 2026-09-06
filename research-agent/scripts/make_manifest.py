#!/usr/bin/env python3
"""전달 매니페스트 생성기 — 사람이 세지 않는다.

v0.1.6 과 v0.1.8 에서 같은 실패가 났다: 회신문의 파일 목록과 실제로 도착한 파일이 달랐고,
두 번 다 "1:1 대조했다"고 적혀 있었다. 목록도 사람이 쓰고 대조도 사람이 하면 같은 순간에
두 번 실수해서 안 걸린다.

⇒ 목록을 **실제 파일에서 기계로 뽑는다.** 이 스크립트의 출력을 회신문에 그대로 붙이면,
   받는 쪽이 도착한 파일로 같은 명령을 돌려 해시를 비교할 수 있다. 그러면 유실이
   **어느 구간에서 났든**(보내는 쪽 누락 / 전송 중 유실 / 압축 중 누락) 잡힌다.

    python scripts/make_manifest.py 0.1.10 <코드...> --doc <문서...>
    python scripts/make_manifest.py --verify MANIFEST_0.1.10.md     # 받는 쪽에서

문서(회신문·매니페스트 자신)도 표에 넣되 `kind: doc` 으로 구분한다. 코드만 넣으면
"첨부 10개 중 8개가 목록에 있다" 를 받는 쪽이 매번 손으로 조정해야 하고, 그러면
**개수 대조가 다시 사람 일**이 된다 — 이 스크립트를 만든 이유가 사라진다.
매니페스트 자신은 해시를 계산할 수 없으므로(자기 참조) `—` 로 두고 검증에서 존재만 본다.
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


def build(version: str, code: list[str], docs: list[str]) -> str:
    self_name = f"MANIFEST_{version}.md"
    docs = list(dict.fromkeys([*docs, self_name]))     # 매니페스트 자신도 첨부물이다
    rows, missing = [], []
    for kind, group in (("code", code), ("doc", docs)):
        for rel in sorted(dict.fromkeys(group)):
            if rel == self_name:                        # 자기 참조 — 해시는 못 낸다
                rows.append((rel, kind, None, None, "—"))
                continue
            p = (ROOT / rel) if not Path(rel).is_absolute() else Path(rel)
            if not p.exists():
                missing.append(rel)
                continue
            sha, lines, size = _digest(p)
            rows.append((rel, kind, lines, size, sha))
    n_code = sum(1 for r in rows if r[1] == "code")
    out = [f"# 전달 매니페스트 — v{version}", "",
           f"**첨부 {len(rows)}개** (code {n_code} · doc {len(rows) - n_code}).",
           "이 표의 줄 수와 실제 첨부 개수가 **같아야 한다** — 다르면 그 자체가 유실 신호다.", "",
           "```bash",
           f"python scripts/make_manifest.py --verify {self_name}",
           "```",
           "`MISSING`(파일 없음) / `MISMATCH`(내용 다름) 가 하나라도 나오면",
           "**병합하지 말고 회신해 주십시오.** 매니페스트 자신은 해시가 `—` 라 존재만 확인한다.", "",
           "| 파일 | kind | 줄 | 바이트 | sha256[:16] |", "|---|---|---:|---:|---|"]
    out += [f"| `{r}` | {k} | {l if l is not None else '—'} | {s if s is not None else '—'} | `{h}` |"
            for r, k, l, s, h in rows]
    if missing:
        out += ["", "⛔ **보내는 쪽에서 찾지 못한 파일** (전달 전에 해결할 것):"]
        out += [f"- `{m}`" for m in missing]
    return "\n".join(out) + "\n"


def verify(manifest: Path) -> int:
    text = manifest.read_text(encoding="utf-8")
    rows = re.findall(
        r"^\|\s*`([^`]+)`\s*\|\s*(code|doc)\s*\|\s*([\d—]+)\s*\|\s*([\d—]+)\s*\|\s*`([0-9a-f—]+)`\s*\|$",
        text, re.M)
    if not rows:
        print("매니페스트에서 파일 표를 찾지 못했다 (v0.1.10 이전 형식이면 kind 열이 없다).",
              file=sys.stderr)
        return 2
    bad = 0
    for rel, kind, lines, size, sha in rows:
        p = ROOT / rel
        if not p.exists():
            print(f"MISSING   [{kind}] {rel}")
            bad += 1
            continue
        if sha == "—":                      # 매니페스트 자신 — 존재만 본다
            print(f"ok(self)  [{kind}] {rel}")
            continue
        got_sha, got_lines, _ = _digest(p)
        if got_sha != sha:
            print(f"MISMATCH  [{kind}] {rel}  (기대 {sha} / 실제 {got_sha}, {lines}→{got_lines}줄)")
            bad += 1
        else:
            print(f"ok        [{kind}] {rel}")
    print(f"\n{len(rows) - bad}/{len(rows)} 일치" + ("" if not bad else f"  ⛔ {bad}건 문제 — 병합하지 말 것"))
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--verify":
        return verify(Path(argv[1]))
    version, rest = argv[0], argv[1:]
    code, docs, cur = [], [], None
    for a in rest:
        if a == "--doc":
            cur = docs
            continue
        (docs if cur is docs else code).append(a)
    print(build(version, code, docs), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
