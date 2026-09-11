#!/usr/bin/env python3
"""산출물 옆에 붙는 `.meta.json` 의 git 부분 — **한 곳**에서.

## 왜 따로 있나

`run_states.sh` 와 `ne_shape.py` 가 각자 `git status --porcelain` 으로
`git_dirty` 를 계산했다. 그 명령은 **untracked 파일도 센다.** 산출물은 쓰이는
순간 untracked 이고 `cells/` 도 오래 untracked 였으므로, 이 저장소의 meta 는
2026-09-11 확인 시점에 **전부** `git_dirty: true` 였다 — 플래그에 정보가 없었다.
그 위에 §1-12 조건 6 이 "커밋 안 된 변경이 있는 트리에서 돌았다" 고 적었다.
과장이었다.

플래그가 답해야 할 물음은 "**돌린 코드가 `git_commit` 과 같았나**" 다. 그건
추적 파일의 수정 여부이고, untracked 산출물과 무관하다. 그래서
`--untracked-files=no`.

    from provenance import git_state
    sha, dirty = git_state()          # dirty: 추적 파일이 수정됐는가
    sha, dirty = git_state(exclude=[art, art + ".meta.json"])   # 산출물 자신은 뺀다

## 산출물 자신은 뺀다 (2026-09-11, fb62342)

추적된 산출물(`out/*.csv`, `out/*.json`)을 **다시 쓰는 것 자체**가 "추적 파일 수정" 으로
잡혀서, 재생성 meta 는 늘 `git_dirty: true` 였다 — fb62342 의 커밋에는 CSV 와 meta 만
있었는데도. 플래그의 물음은 코드에 대한 것이므로 지금 쓰는 산출물(과 그 meta)은
`exclude` 로 뺀다. 코드 파일이 고쳐져 있으면 여전히 true 다.
"""
from __future__ import annotations
import subprocess


# ── 코드 dirty 와 수정된 산출물을 **분리**한다 (Codex R4-07) ────────────────────────────────
# 산출물 하나만 빼면, 앞 단계에서 다시 쓴 **다른** 산출물이 코드 변경으로 읽혀 두 번째 meta 가
# 다시 dirty 였다. 그렇다고 `out/` 을 통째로 숨기면 계산 **입력**으로 쓰는 artifact(`matrix_*.csv`
# 등)의 변경까지 숨는다. 그래서 둘을 따로 적는다:
#   git_dirty            — 산출 디렉터리 밖의 추적 파일이 수정됐는가 (= 코드가 commit 과 같았나)
#   git_modified_outputs — 산출 디렉터리 안에서 수정된 추적 파일 목록 (지금 쓰는 산출물·meta 제외)


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def git_provenance(cwd: str | None = None, artifact=None, output_roots=("out",)) -> dict:
    """{git_commit, git_dirty(코드), git_modified_outputs[...], git_modified_code[...]}. git 이 없으면 None 들."""
    import pathlib
    base = pathlib.Path(cwd or ".").resolve()
    try:
        sha = _git(cwd, "rev-parse", "HEAD").strip()
        top = pathlib.Path(_git(cwd, "rev-parse", "--show-toplevel").strip()).resolve()
        lines = _git(top, "status", "--porcelain", "--untracked-files=no").splitlines()
    except Exception:
        return {"git_commit": "", "git_dirty": None, "git_modified_outputs": None, "git_modified_code": None}
    skip = set()
    if artifact:
        a = pathlib.Path(artifact)
        a = (a if a.is_absolute() else base / a).resolve()
        skip = {a, a.with_name(a.name + ".meta.json")}
    roots = [(pathlib.Path(r) if pathlib.Path(r).is_absolute() else base / r).resolve()
             for r in output_roots if r]                       # 빈 문자열(미설정 $OUT)은 루트가 아니다
    outputs, code = [], []
    for ln in lines:
        rel = ln[3:].split(" -> ")[-1].strip()
        path = (top / rel).resolve()
        if path in skip:
            continue
        if any(root == path or root in path.parents for root in roots):
            outputs.append(str(path.relative_to(base)) if base in path.parents else rel)
        else:
            code.append(rel)
    return {"git_commit": sha, "git_dirty": bool(code),
            "git_modified_outputs": sorted(outputs), "git_modified_code": sorted(code)}


def git_state(cwd: str | None = None, exclude=()) -> tuple[str, bool | None]:
    """(HEAD sha, **코드**가 수정됐는가). git 이 없으면 ("", None). `exclude[0]` 은 지금 쓰는 산출물."""
    pv = git_provenance(cwd, artifact=(list(exclude) or [None])[0])
    return pv["git_commit"], pv["git_dirty"]


if __name__ == "__main__":
    import json, sys
    print(json.dumps(git_provenance(artifact=sys.argv[1] if len(sys.argv) > 1 else None)))
