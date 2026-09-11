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
        # ⚠ Codex R5-11: 기본 `--porcelain` 은 비ASCII 경로를 따옴표·8진수로 찍는다 ("out/\354\270\241…").
        #   `-z` 레코드는 경로를 그대로 준다; rename/copy 는 새 경로 뒤에 원 경로가 한 레코드 더 온다.
        raw = _git(top, "status", "--porcelain", "-z", "--untracked-files=no")
    except Exception:
        return {"git_commit": "", "git_dirty": None, "git_modified_outputs": None, "git_modified_code": None}
    lines, parts, i = [], raw.split("\0"), 0
    while i < len(parts):
        rec = parts[i]; i += 1
        if not rec:
            continue
        xy, path_ = rec[:2], rec[3:]
        if "R" in xy or "C" in xy:
            i += 1                                 # 원 경로 레코드는 건너뛴다 (새 경로가 수정된 파일)
        lines.append(f"{xy} {path_}")
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


def sha256_file(path) -> str:
    import hashlib, pathlib
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def check_run_id(path, rid: str):
    """산출물이 **필드로** 이 시도의 id 를 담고 있는가 (Codex R5-08: 파일 어디든 문자열이 있으면 통과하던 grep 대신).

    CSV → 모든 행의 `run_id` 열이 rid; JSON → 최상위 `run_id` 가 rid. → (ok, 설명)"""
    import csv, json, pathlib
    p = pathlib.Path(path)
    if not p.is_file():
        return False, "파일 없음"
    if not rid:
        return False, "run id 없음"
    try:
        if p.suffix.lower() == ".csv":
            with p.open(encoding="utf-8", newline="") as fh:
                header = next(csv.reader(fh), [])
                n_col = header.count("run_id")
                if n_col != 1:                       # R6 내부 V6-08: DictReader 는 같은 이름의 마지막 열만 본다
                    return False, ("run_id 열 없음" if n_col == 0 else f"run_id 열이 {n_col} 개")
                fh.seek(0)
                rows = list(csv.DictReader(fh))
            if not rows:
                return False, "행 없음"
            bad = [r.get("run_id") for r in rows if r.get("run_id") != rid]
            return (not bad), ("전 행 일치" if not bad else f"다른 run_id 행 {len(bad)}/{len(rows)}: {bad[:2]}")
        data = json.loads(p.read_text(encoding="utf-8"))
        ok = isinstance(data, dict) and data.get("run_id") == rid
        return ok, ("일치" if ok else f"JSON run_id={data.get('run_id') if isinstance(data, dict) else None!r}")
    except Exception as e:                           # noqa: BLE001
        return False, f"읽기 실패: {e}"


def verify_unit(path):
    """산출물과 그 `.meta.json` 이 **같은 시도의 한 묶음**인가 (Codex R5-04): meta 의 run_id 가 산출물의
    필드와 같고 meta 의 sha256 이 지금 bytes 와 같아야 한다. → (ok, 설명). meta 가 없으면 (None, …)."""
    import json, pathlib
    p = pathlib.Path(path); meta = p.with_name(p.name + ".meta.json")
    if not meta.is_file():
        return None, "meta 없음"
    try:
        m = json.loads(meta.read_text(encoding="utf-8"))
    except Exception as e:                           # noqa: BLE001
        return False, f"meta 읽기 실패: {e}"
    rid, digest = m.get("run_id"), m.get("sha256")
    if not rid or not digest:
        return None, "옛 meta (run_id/sha256 없음)"
    if m.get("artifact") and m["artifact"] != p.name:  # R6 내부 V6-05: 묶음이 맞는 이름 아래 있는가
        return False, f"meta 의 artifact({m['artifact']!r}) 가 파일 이름({p.name!r}) 과 다르다"
    ok_id, why = check_run_id(p, rid)
    if not ok_id:
        return False, f"meta 의 run_id 가 산출물과 다르다: {why}"
    if sha256_file(p) != digest:
        return False, "meta 의 sha256 이 지금 bytes 와 다르다"
    return True, "일치"


def git_state(cwd: str | None = None, exclude=()) -> tuple[str, bool | None]:
    """(HEAD sha, **코드**가 수정됐는가). git 이 없으면 ("", None). `exclude[0]` 은 지금 쓰는 산출물."""
    pv = git_provenance(cwd, artifact=(list(exclude) or [None])[0])
    return pv["git_commit"], pv["git_dirty"]


if __name__ == "__main__":
    import json, sys
    if len(sys.argv) >= 4 and sys.argv[1] == "--check-run-id":     # run_states.sh 가 쓴다 (R5-08)
        ok, why = check_run_id(sys.argv[2], sys.argv[3]); print(why); sys.exit(0 if ok else 1)
    if len(sys.argv) >= 3 and sys.argv[1] == "--verify-unit":      # run_states.sh 가 쓴다 (R5-04)
        ok, why = verify_unit(sys.argv[2]); print(why); sys.exit(0 if ok else 1)
    print(json.dumps(git_provenance(artifact=sys.argv[1] if len(sys.argv) > 1 else None)))
