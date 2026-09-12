"""증거 러너의 **공용 gate** — 무엇을 실행했는지 봉인하는 부분만 (Codex R10 P2-4 · P2-5).

R7·R9 닫힘 재생기가 같은 계약을 쓴다. 두 벌로 두면 한쪽만 고쳐지므로 여기 한 자리에 둔다.

닫는 것:

- **assert 로 증거를 판정하지 않는다.** `python -O` 는 `assert` 를 통째로 지운다 — 전 판은 delegated pytest 가 usage
  error 인데 runner rc 0 · `closed: true` 를 냈다. 판정은 `EvidenceError` 를 던지는 명시적 분기이고, optimize 모드
  자체를 fail-closed 한다 (`require_assertions`).
- **`git status` 의 rc 를 본다.** `GIT_INDEX_FILE` 이 디렉터리면 status 는 rc 128 인데 전 판은 stdout 이 비었다는
  이유로 `dirty: false` 였다.
- **실행 bytes 를 expected commit 에서 새로 materialize 한다.** working tree 를 그대로 쓰면 `assume-unchanged` 로
  고친 tracked module 도, ignored `__pycache__` 의 위조 bytecode 도 clean 으로 보이면서 실행됐다. sparse detached
  worktree 는 그 commit 의 blob 만 풀고 자기 index 를 쓰므로 둘 다 닿지 않는다.
"""
from __future__ import annotations
import hashlib, os, pathlib, subprocess, sys, tempfile


class EvidenceError(RuntimeError):
    """증거를 만들 수 없는 상태 — 러너는 이것을 잡아 비영 종료한다 (성공으로 넘기지 않는다)."""


def require_assertions() -> None:
    if not __debug__:
        raise EvidenceError(
            "이 러너는 `python -O`(PYTHONOPTIMIZE) 에서 증거를 만들지 않는다 — 보관한 probe 의 반례는 `assert` 로 "
            "쓰여 있고 optimize 모드는 그것을 통째로 지운다. 최적화 없이 다시 부를 것 (Codex R10 P2-4)")


def need(cond, what: str, detail=None) -> None:
    """증거 판정의 **명시적 분기** — `assert` 를 쓰면 `python -O` 에서 통째로 사라진다 (Codex R10 P2-4)."""
    if not cond:
        raise EvidenceError(f"{what}" + (f" — {detail!r}" if detail is not None else ""))


def _git(target, *args, check=True) -> str:
    p = subprocess.run(["git", "-C", str(target), *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise EvidenceError(f"`git {' '.join(args)}` 이 rc {p.returncode} 로 끝났다 — 저장소 상태를 모르는 채로 "
                            f"증거를 만들지 않는다 (Codex R10 P2-5): {p.stderr.strip()[:300]}")
    return p.stdout


def git_head(target) -> str:
    return _git(target, "rev-parse", "HEAD").strip()


def dirty_paths(target) -> list:
    """working tree 의 변경 목록. **rc 를 본다** — 모르는 상태는 clean 이 아니다 (Codex R10 P2-5 반례 A)."""
    out = _git(target, "status", "--porcelain", "--untracked-files=normal", "--", ".")
    return [ln for ln in out.splitlines() if ln.strip()]


def package_digest(pkg: pathlib.Path, sums: pathlib.Path):
    """보관한 패키지 bytes 가 SHA256SUMS 와 같은가 → (전부 ok, {파일: ok|mismatch|missing})."""
    status = {}
    for ln in sums.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        want, name = ln.split(None, 1)
        f = pkg / name.strip()
        status[name.strip()] = ("missing" if not f.is_file()
                                else ("ok" if hashlib.sha256(f.read_bytes()).hexdigest() == want else "mismatch"))
    return bool(status) and all(v == "ok" for v in status.values()), status


def parse_probes(text: str, known):
    """`--probes` → (목록, 문제). 빈 이름·모르는 이름·중복은 전부 거부한다 (Codex R9 P2-1)."""
    want = [p.strip() for p in str(text).split(",")]
    problems = []
    if not str(text).strip() or any(not p for p in want):
        problems.append("빈 probe 이름")
    unknown = [p for p in want if p and p not in known]
    if unknown:
        problems.append(f"모르는 probe {unknown} (아는 것: {list(known)})")
    dup = sorted({p for p in want if p and want.count(p) > 1})
    if dup:
        problems.append(f"중복 probe {dup}")
    return want, problems


def materialize(target, head: str, keep=None):
    """expected commit 의 **격리 snapshot** 을 만든다 → (실행할 target 경로, cleanup 함수).

    sparse detached worktree 라 (i) 그 commit 의 blob 만 풀리고 (ii) 자기 index 를 쓰므로 원본의
    `assume-unchanged`/`skip-worktree` 가 따라오지 않으며 (iii) ignored `__pycache__` 같은 untracked bytes 가
    애초에 없다. `git rev-parse HEAD` 도 expected commit 그대로라 중첩 러너의 계약이 살아 있다.
    """
    target = pathlib.Path(target).resolve()
    prefix = _git(target, "rev-parse", "--show-prefix").strip().strip("/")
    _git(target, "worktree", "prune", check=False)
    dest = pathlib.Path(keep) if keep else pathlib.Path(tempfile.mkdtemp(prefix="evidence-snap-")) / "snap"
    if dest.exists():
        raise EvidenceError(f"snapshot 자리가 이미 있다: {dest}")
    _git(target, "worktree", "add", "--detach", "--no-checkout", str(dest), head)

    def cleanup():
        _git(target, "worktree", "remove", "--force", str(dest), check=False)
        _git(target, "worktree", "prune", check=False)

    try:
        if prefix:
            # `.gitignore` 도 같이 — probe 가 **저장소 루트의 ignore 정책**을 보고 clone 을 만든다 (ignored-pyc case).
            # 없으면 sparse 가 조용히 넘어간다.
            _git(dest, "sparse-checkout", "set", "--no-cone", prefix, "/.gitignore")
        _git(dest, "checkout")
        got = git_head(dest)
        if got != head:
            raise EvidenceError(f"snapshot 의 HEAD 가 다르다: {got} ≠ {head}")
        inner = dest / prefix if prefix else dest
        if not inner.is_dir():
            raise EvidenceError(f"snapshot 에 {prefix} 가 없다")
    except BaseException:
        cleanup()
        raise
    return inner, cleanup


def isolate_bytecode(env: dict | None = None) -> str:
    """이미 놓인 `__pycache__` 를 **읽지 않게** 한다 — 캐시 위치를 임시 prefix 로 돌린다 (Codex R10 P2-5 반례 C).

    트리를 건드리지 않는다 (지우지 않는다). in-process import 와 자식 프로세스 둘 다에 건다.
    """
    prefix = tempfile.mkdtemp(prefix="evidence-pycache-")
    sys.pycache_prefix = prefix
    os.environ["PYTHONPYCACHEPREFIX"] = prefix
    if env is not None:
        env["PYTHONPYCACHEPREFIX"] = prefix
    return prefix


def instrument_sealed(target, rel_paths) -> tuple:
    """**도구 자신**(러너·gate)의 bytes 가 expected commit 의 blob 과 같은가 → (bool, {경로: ok|다름|없음}).

    대상 트리를 격리 snapshot 에서 읽어도 러너가 수정된 채라면 그 증거는 그 커밋의 것이 아니다. index 를 거치지 않는
    `hash-object` ↔ `rev-parse HEAD:<path>` 로 댄다 (Codex R10 P2-5 의 identity 요구를 도구에도 적용).
    """
    detail = {}
    for rel in rel_paths:
        f = pathlib.Path(target) / rel
        if not f.is_file():
            detail[rel] = "없음"; continue
        try:
            have = _git(target, "hash-object", "--", str(f)).strip()
            want = _git(target, "rev-parse", f"HEAD:./{rel}").strip()
        except EvidenceError:
            detail[rel] = "커밋에 없음"; continue
        detail[rel] = "ok" if have == want else "다름"
    return all(v == "ok" for v in detail.values()), detail


def index_skip_flags(target) -> list:
    """`assume-unchanged`/`skip-worktree` 가 걸린 tracked 파일 (소문자 플래그) — 봉인 전에 배제한다."""
    out = _git(target, "ls-files", "-v", "--", ".")
    return [ln[2:] for ln in out.splitlines() if ln[:1].islower()]
