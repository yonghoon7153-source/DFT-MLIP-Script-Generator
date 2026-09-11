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
"""
from __future__ import annotations
import subprocess


def git_state(cwd: str | None = None) -> tuple[str, bool | None]:
    """(HEAD sha, 추적 파일이 수정됐는가). git 이 없으면 ("", None)."""
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cwd,
                             capture_output=True, text=True, check=True
                             ).stdout.strip()
        mod = subprocess.run(["git", "status", "--porcelain",
                              "--untracked-files=no"], cwd=cwd,
                             capture_output=True, text=True, check=True
                             ).stdout.strip()
    except Exception:
        return "", None
    return sha, bool(mod)


if __name__ == "__main__":
    import json
    sha, dirty = git_state()
    print(json.dumps({"git_commit": sha, "git_dirty": dirty}))
