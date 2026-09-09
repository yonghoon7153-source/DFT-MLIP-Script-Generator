#!/usr/bin/env python3
"""survey_coverage.py — 조사가 **실제로 몇 %를 봤나** 를 센다.

    python3 tools/survey_coverage.py <조사폴더>              # 요약표
    python3 tools/survey_coverage.py <조사폴더> --area tools  # 그 영역의 미인용 목록
    python3 tools/survey_coverage.py --selftest

왜 생겼나
  2026-09-08 밤 전수조사(29 에이전트 · 6.7 M 토큰 · 3.2 h)가 552 발견을 냈고 스스로를
  "전수" 라고 불렀다. 그런데 2026-09-09 에 273 캐스케이드가 Stage 04 에서 전멸했고,
  그 원인(`tier_cascade.sh` 가 `run_anneal.py --seed` 를 안 넘김)은 조사가 **한 번도
  열지 않은 파일**에 있었다. 조사 문서 자신이 적어 놓았다 — *"cascade 11개 전부의
  본문", "run_anneal … 본문" 못 봄*. 그리고 `tier_cascade.sh` 를 **"끝난 캠페인"** 으로
  분류해 P0 대상에서 뺐다.
  실측 커버리지는 **34.3 %** 였다 (tools 25.8 % · webapp 86.8 %).
  ⇒ "전수조사 했다" 는 **검증 가능한 주장**이어야 한다. 그걸 재는 게 이 도구다.

⛔ 이 도구가 **못 하는 것** (제일 중요한 절)
  · **"인용됐다 = 제대로 봤다" 가 아니다.** 파일명이 한 번 스쳐도 인용으로 센다.
    그래서 여기 나오는 수는 **상한**이고 실제 정독률은 그보다 낮다.
  · 반대로 **안 봐도 되는 파일**을 못 가른다 — 화석·일회성 복구 스크립트까지 분모에 넣는다.
    분모를 좁히려면 호출자가 `--glob` 으로 범위를 준다.
  · 조사의 **품질**은 안 본다. 잘못된 판정을 걸러내지 못한다.
  · 파일명이 흔한 것(`README.md` · `__init__.py`)은 다른 곳의 언급에 묻어 통과한다.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

#: 세는 확장자. 바이너리·데이터 덤프는 조사 대상이 아니다.
EXTS = (".py", ".sh", ".json", ".md", ".html", ".css", ".js")
#: 영역 — 이 순서로 앞에서 맞는 첫 번째를 쓴다.
AREAS = ("tools/", "kb/", "db/", "webapp/", "litdb/", "docs/", "research_agent/")
_PATH_RE = re.compile(r"[A-Za-z0-9_./-]+\.(?:py|sh|json|md|html|css|js|csv|cif|xyz)")


def _area(rel: str) -> str:
    for a in AREAS:
        if rel.startswith(a):
            return a.rstrip("/")
    return "(root/기타)"


def cited_paths(survey_dir: Path) -> set:
    """조사 문서들이 언급한 경로·파일명 전부."""
    out = set()
    for p in sorted(survey_dir.rglob("*")):
        if not p.is_file() or p.suffix not in (".md", ".json", ".txt"):
            continue
        for m in _PATH_RE.finditer(p.read_text(encoding="utf-8", errors="ignore")):
            out.add(m.group(0).lstrip("./"))
    return out


def tracked_files(root: Path, globs=None) -> list:
    try:
        files = subprocess.check_output(["git", "-C", str(root), "ls-files"],
                                        text=True).split()
    except (OSError, subprocess.CalledProcessError):
        files = [str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()]
    files = [f for f in files if f.endswith(EXTS)]
    if globs:
        import fnmatch
        files = [f for f in files if any(fnmatch.fnmatch(f, g) for g in globs)]
    return sorted(files)


def coverage(survey_dir: Path, root: Path = REPO, globs=None):
    """→ (영역별 {n, miss}, {영역: [미인용 파일…]})"""
    cited = cited_paths(survey_dir)
    cited_base = {c.rsplit("/", 1)[-1] for c in cited}
    stat = collections.defaultdict(lambda: {"n": 0, "miss": 0})
    missing = collections.defaultdict(list)
    for f in tracked_files(root, globs):
        a = _area(f)
        stat[a]["n"] += 1
        if f not in cited and f.rsplit("/", 1)[-1] not in cited_base:
            stat[a]["miss"] += 1
            missing[a].append(f)
    return dict(stat), dict(missing)


def _print(stat, missing, area=None, limit=0):
    if area:
        files = missing.get(area, [])
        print(f"# {area} 미인용 {len(files)}개")
        for f in (files[:limit] if limit else files):
            print(" ", f)
        if limit and len(files) > limit:
            print(f"  … 외 {len(files) - limit}개")
        return
    print(f"{'영역':<14}{'추적':>7}{'미인용':>8}   커버리지")
    tot = miss = 0
    for a in sorted(stat, key=lambda x: -stat[x]["n"]):
        n, m = stat[a]["n"], stat[a]["miss"]
        tot += n
        miss += m
        print(f"{a:<14}{n:>7}{m:>8}   {100 * (1 - m / n):5.1f}%" if n else "")
    if tot:
        print(f"{'합계':<14}{tot:>7}{miss:>8}   {100 * (1 - miss / tot):5.1f}%")
    print("\n⚠ 이 수는 **상한**이다 — 파일명이 한 번 스쳐도 인용으로 센다. 실제 정독률은 더 낮다.")


def selftest() -> int:
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as d:
        t = Path(d)
        (t / "tools").mkdir()
        (t / "webapp").mkdir()
        for rel in ("tools/seen.py", "tools/unseen.py", "webapp/app.py"):
            (t / rel).write_text("x\n")
        sv = t / "survey"
        sv.mkdir()
        # 조사가 seen.py 와 app.py 만 언급했다
        (sv / "a.md").write_text("tools/seen.py 를 봤고 webapp/app.py 도 봤다\n")
        stat, missing = coverage(sv, t)
        # ⛔음성: 안 본 파일을 못 잡으면 실패
        if missing.get("tools") != ["tools/unseen.py"]:
            print("⛔ selftest: 미인용 파일을 못 잡았다:", missing)
            ok = False
        # ⛔음성: 본 파일을 미인용으로 오탐하면 실패
        if "webapp" in missing and missing["webapp"]:
            print("⛔ selftest: 인용된 파일을 미인용으로 오탐했다:", missing["webapp"])
            ok = False
        if stat["tools"]["n"] != 2 or stat["tools"]["miss"] != 1:
            print("⛔ selftest: 집계가 틀렸다:", stat)
            ok = False
        # ⛔음성: 파일명만 같아도 인용으로 세는 **알려진 한계**가 실제로 그런지
        #   (문서에 적은 한계가 사실인지 확인한다 — 한계를 적어 놓고 틀리면 더 나쁘다)
        (sv / "b.md").write_text("어디선가 unseen.py 라고만 적혀 있다\n")
        _, m2 = coverage(sv, t)
        if m2.get("tools"):
            print("⛔ selftest: 파일명만으로 통과하는 한계가 문서와 다르다:", m2)
            ok = False
    print("selftest PASS" if ok else "selftest FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("survey_dir", nargs="?", help="조사 결과 폴더 (예: .v3_survey)")
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--area", help="그 영역의 미인용 목록만")
    ap.add_argument("--glob", nargs="*", help="분모를 좁힌다 (예: 'tools/**')")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--json", help="미인용 목록을 이 경로에 JSON 으로")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.survey_dir:
        ap.error("조사 폴더를 주거나 --selftest 를 써라")
    stat, missing = coverage(Path(a.survey_dir), Path(a.root), a.glob)
    if a.json:
        Path(a.json).write_text(json.dumps(missing, ensure_ascii=False, indent=1),
                                encoding="utf-8")
        print(f"미인용 목록 → {a.json}")
    _print(stat, missing, a.area, a.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
