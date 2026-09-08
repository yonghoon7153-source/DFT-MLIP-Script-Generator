"""60차 ε (P0-7·P0-8·P0-9·P1-2) — **묶음이 담고 있다는 것을 무엇이 보증하나.**

리뷰어 반례 셋:

    P0-7  bind mount 로 밖의 파일을 묶음 안에 보이게 하면 `lstat` 는 그것을
          평범한 inode 로 센다 → `verifier_errors:[] · full_bundle`
    P0-8  `payload_index` 가 묶음 **밖**의 gitignored 경로여도 통과한다
          → clone 이나 묶음 전달본에는 그 index 가 아예 없다
    P0-9  검증 **직후**·ledger commit **전**에 member 하나를 같은 길이의 다른
          바이트로 갈아 끼우면 그대로 `full_bundle` 로 굳는다

그리고 P1-2: `phase_done()` 은 caller dict 를 lock **밖**에서 검사하고 **같은
reference** 를 나중에 직렬화한다 — 59차 M9 가 finalize 의 evidence 에 대해 고친
것과 같은 병이 phase receipt 에 그대로 남아 있었다.

`[해석]` 셋은 같은 물음의 세 얼굴이다: **"검사한 것"과 "봉인한 것"이 같은
대상인가.** 이름(`lstat`)·경로(`payload_index`)·객체 reference 는 전부 그 물음에
답하지 않는다. 답하는 것은 **좌표**(어느 mount 의 어느 자리인가)와 **바이트**
(무엇이 들어 있었나)뿐이다.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import tools.preserve as P                                      # noqa: E402


def _bundle(root: Path, *, index_inside=True):
    """`full_bundle` 을 주장할 수 있는 최소 묶음 한 벌."""
    d = root / "bundle"
    d.mkdir(parents=True)
    (d / "a.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (d / "b.csv").write_text("c,d\n3,4\n", encoding="utf-8")
    idx_dir = d if index_inside else (root / "results")
    idx_dir.mkdir(parents=True, exist_ok=True)
    idx = idx_dir / "payload_index.json"
    members = sorted(x for x in ("a.csv", "b.csv"))
    idx.write_text(json.dumps({"members": members}, sort_keys=True) + "\n",
                   encoding="utf-8")
    files = [x for x in sorted(d.rglob("*")) if x.is_file()]
    return d, idx, {
        "bundle_uri": d.relative_to(root).as_posix(),
        "bundle_files": len(files),
        "payload_bytes": sum(x.stat().st_size for x in files),
        "payload_index": idx.relative_to(root).as_posix(),
        "payload_index_sha256": hashlib.sha256(idx.read_bytes()).hexdigest(),
    }


# ── P0-8 ──────────────────────────────────────────────────────────────────
def test_the_payload_index_must_be_a_member_of_the_bundle(tmp_path):
    """★ P0-8 — index 가 묶음 밖이면 그 묶음은 **자기를 설명하지 못한다.**

    `full_bundle` 의 뜻은 "clone 한 사람이 이 결과를 검증할 수 있는 묶음이
    실재한다"(계약 §8)이다. 그런데 index 가 묶음 밖이면 묶음만 받은 사람에게는
    그것을 인증한다는 목록이 **아예 없다.**
    """
    d, idx, ev = _bundle(tmp_path, index_inside=False)
    bad = P._verify_declared_bundle(ev, repo_root=tmp_path)
    assert bad, "묶음 밖 index 가 통과했다 (P0-8)"
    assert any("index" in b for b in bad), bad


def test_the_index_and_the_walk_must_agree_both_ways(tmp_path):
    """★ P0-8 — index 가 이름한 것과 **실제로 걸은 것**이 같아야 한다.

    한쪽만 보면 "index 에 있는데 없는 파일" 이나 "묶음에 있는데 index 가 모르는
    파일" 이 통과한다. 그 둘이 곧 "완전 묶음" 이라는 말이 무너지는 두 방향이다.
    """
    d, idx, ev = _bundle(tmp_path)
    (d / "c.csv").write_text("e,f\n5,6\n", encoding="utf-8")     # index 밖 구성원
    files = [x for x in sorted(d.rglob("*")) if x.is_file()]
    ev["bundle_files"] = len(files)
    ev["payload_bytes"] = sum(x.stat().st_size for x in files)
    bad = P._verify_declared_bundle(ev, repo_root=tmp_path)
    assert bad, "index 가 모르는 구성원이 통과했다 (P0-8)"


# ── P0-9 ──────────────────────────────────────────────────────────────────
def test_the_verified_bundle_is_sealed_by_its_bytes(tmp_path):
    """★ P0-9 — 검증한 것과 봉인한 것이 **같은 바이트**임을 기록이 말해야 한다.

    59차 M9 는 caller 의 dict 를 진입 시점에 정규 바이트로 굳혔다. 그런데 그
    dict 가 **가리키는 묶음**은 안 굳혔다. 그래서 검증 뒤 ledger commit 전에
    같은 길이의 다른 바이트로 갈아 끼우면 그대로 `full_bundle` 이 된다.

    닫는 방법은 검증이 **내용 주소**를 만들고 그것을 봉인에 넣는 것이다. 그러면
    나중에 바뀐 사실이 기록 자체에서 드러난다 (mutable directory 를 유지하는
    한 창 자체는 남고, 그 한계는 요청문에 적는다).
    """
    d, idx, ev = _bundle(tmp_path)
    cid = P.bundle_content_id(ev, repo_root=tmp_path)
    assert len(cid) == 64

    (d / "a.csv").write_text("a,b\n9,9\n", encoding="utf-8")     # 같은 길이
    assert P.bundle_content_id(ev, repo_root=tmp_path) != cid, (
        "member 를 갈아 끼웠는데 내용 주소가 그대로다 (P0-9)")


# ── P0-7 ──────────────────────────────────────────────────────────────────
_BIND_PROBE = textwrap.dedent('''
    import json, os, subprocess, sys, hashlib
    sys.path.insert(0, {repo!r})
    import tools.preserve as P
    root = {root!r}
    d = os.path.join(root, "bundle")
    outside = os.path.join(root, "outside")
    # 묶음 안의 한 자리를 **밖의 디렉터리**로 bind 한다
    subprocess.run(["mount", "--bind", outside, os.path.join(d, "sub")],
                   check=True)
    ev = json.load(open(os.path.join(root, "ev.json")))
    files = []
    for dirpath, _dn, fn in os.walk(d):
        for f in fn:
            files.append(os.path.join(dirpath, f))
    ev["bundle_files"] = len(files)
    ev["payload_bytes"] = sum(os.stat(f).st_size for f in files)
    bad = P._verify_declared_bundle(ev, repo_root=root)
    print(json.dumps({{"errors": bad}}, ensure_ascii=False))
''')


def _have_unshare() -> bool:
    try:
        r = subprocess.run(["unshare", "-Urnm", "true"], capture_output=True,
                           timeout=30)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):        # pragma: no cover
        return False


@pytest.mark.skipif(not _have_unshare(),
                    reason="이 환경에서는 mount namespace 를 만들 수 없다")
def test_a_bind_mounted_outside_directory_is_not_a_bundle_member(tmp_path):
    """★ P0-7 — `lstat` 는 bind mount 를 평범한 inode 로 본다.

    `Path.resolve()` 도 못 잡는다 — 그것은 namespace 안의 **철자**만 증명한다.
    잡는 것은 좌표다: 구성원이 묶음 뿌리와 **같은 mount** 에 있는가.
    """
    d, idx, ev = _bundle(tmp_path)
    (d / "sub").mkdir()
    out = tmp_path / "outside"
    out.mkdir()
    (out / "outside-only.csv").write_text("x\n" * 8, encoding="utf-8")
    (tmp_path / "ev.json").write_text(json.dumps(ev), encoding="utf-8")

    src = _BIND_PROBE.format(repo=str(REPO), root=str(tmp_path))
    r = subprocess.run(["unshare", "-Urnm", sys.executable, "-c", src],
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr[-2000:]
    got = json.loads(r.stdout.strip().splitlines()[-1])
    assert got["errors"], (
        "bind mount 된 밖의 파일이 묶음 구성원으로 통과했다 — clone 에는 그 "
        "바이트가 없다 (P0-7)")


# ── P1-2 ──────────────────────────────────────────────────────────────────
def test_the_phase_receipt_is_snapshotted_at_entry(tmp_path, monkeypatch):
    """★ P1-2 — 검사한 receipt 와 봉인한 receipt 가 같아야 한다.

    리뷰어 실측: `phase_done()` 이 lock 밖에서 caller dict 를 검사하고 **같은
    reference** 를 entry 에 넣어 나중에 직렬화했다. 그래서 검사 뒤에 dict 를
    고치면 다른 값이 굳었다. 59차 M9 가 finalize 에서 고친 것과 같은 병이다.
    """
    from tests.test_preserve import _lifecycle_ledger, _RUN_SPEC_L

    led = _lifecycle_ledger(tmp_path)
    claim = P.open_leg_run("L", _RUN_SPEC_L, "0123456789abcdef", ledger=led)
    receipt = {"v": "검사 시점의 값"}

    real_lock = P._ledger_lock

    def _mutating_lock(path):
        receipt["v"] = "검사 뒤에 바꾼 값"      # 검사와 봉인 사이에 고친다
        return real_lock(path)

    monkeypatch.setattr(P, "_ledger_lock", _mutating_lock)
    claim.phase_done("grid", receipt)
    monkeypatch.setattr(P, "_ledger_lock", real_lock)

    sealed = claim.phase_receipt("grid")
    assert sealed["v"] == "검사 시점의 값", (
        f"검사한 값이 아니라 나중 값이 굳었다: {sealed!r} (P1-2)")


def test_finalize_seals_the_bundle_content_id(tmp_path, monkeypatch):
    """★ P0-9 — 봉인된 기록이 **검증한 바이트**를 말해야 한다.

    값을 만드는 함수가 있는 것만으로는 부족하다 (그것은 59차가 배운
    "있는 것과 배선된 것은 다르다"). `finalize_leg()` 이 실제로 그 값을
    원장에 남기는지가 이 축이다.
    """
    from tests.test_preserve import _lifecycle_ledger, _RUN_SPEC_L
    import yaml

    _real_verify = P._verify_declared_bundle
    _real_cid = P.bundle_content_id
    led = _lifecycle_ledger(tmp_path)
    root = led.parent
    d, idx, ev = _bundle(root)
    claim = P.open_leg_run("L", _RUN_SPEC_L, "0123456789abcdef", ledger=led)
    claim.phase_done("grid", {"g": 1})
    claim.phase_done("fit", {"f": 1})

    ev["leg_source_digest"] = "0123456789abcdef"
    # 검증기는 저장소 뿌리를 모듈 상수에서 얻는다 — 시험 tree 로 옮긴다
    monkeypatch.setattr(P, "REPO_ROOT", root, raising=False)
    monkeypatch.setattr(P, "_verify_declared_bundle",
                        lambda ev_, repo_root=None: _real_verify(ev_, root))
    monkeypatch.setattr(P, "bundle_content_id",
                        lambda ev_, repo_root=None: _real_cid(ev_, root))
    P.finalize_leg("L", ev, ledger=led, token=claim.token)

    rec = yaml.safe_load(led.read_text(encoding="utf-8"))
    leg = [x for x in rec["legs"] if x["leg_id"] == "L"][0]
    got = leg["evidence"].get("bundle_content_id")
    assert got == _real_cid(ev, repo_root=root), (
        f"봉인이 검증한 바이트를 말하지 않는다: {got!r} (P0-9)")
