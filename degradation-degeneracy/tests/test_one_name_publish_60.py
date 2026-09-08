"""60차 η (P1-1) — **게시가 이름을 둘 남긴다.**

리뷰어 반례:

    {"crash_child_rc":77,"temp_alias_count":1,
     "nlink_before_retry":2,"nlink_after_successful_retry":2,
     "swallowed_unlink_error":{"registration_returned_success":true,
                               "temp_alias_count":1,"final_nlink":2},
     "final_class_after_writing_through_temp_alias":"smoke"}

`[해석]` `os.link(tmp, final)` 은 **이름을 하나 더 만드는** 연산이다. 그 뒤
`unlink(tmp)` 가 실패하면 지금 코드는 그것을 삼키고 성공을 보고했다 — 남은
temp 이름은 같은 inode 를 가리키는 **쓸 수 있는 두 번째 문**이고, 그리로 쓰면
등록부의 내용이 바뀐다. process death 뿐 아니라 평범한 `OSError` 로도 그 상태가
됐다.

닫는 방법 둘을 같이 쓴다.

  ① **이름을 하나만 만드는 게시** — `renameat2(RENAME_NOREPLACE)` 는 무대체
     보장을 유지하면서 원자적으로 **옮긴다** (link + unlink 가 아니다).
     없는 커널에서는 link + unlink 로 물러서되 **unlink 실패를 안 삼킨다.**
  ② **읽는 쪽이 `st_nlink == 1` 을 요구한다** — 게시 경로가 무엇을 하든,
     이름이 둘인 레코드는 authority 가 아니다. 층이 둘이어야 한 층이 뚫려도
     남는다 (이 저장소가 반복해서 쓰는 형태다).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import tools.preserve as P                                      # noqa: E402


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    led = tmp_path / "authority" / "LEG_PRESERVATION.yaml"
    led.parent.mkdir(parents=True)
    led.write_text("planned: []\nlegs: []\ncohorts: []\n", encoding="utf-8")
    monkeypatch.setattr(P, "canonical_ledger", lambda x=None: led)
    ns = tmp_path / "results" / "_smoke"
    ns.mkdir(parents=True)
    monkeypatch.setattr(P, "SMOKE_NAMESPACE", ns)
    return led


def _commit(tmp_path, ledger, name="run"):
    out = tmp_path / "results" / "_smoke" / name
    out.mkdir(parents=True, exist_ok=True)
    (out / "curves_manifest.yaml").write_text(f"curves_sha256: {name}\n",
                                              encoding="utf-8")
    cap = P.issue_execution_class(out, "L", "grid", ledger=ledger)
    P.commit_run_outputs(cap, [out])
    return out


def _record_path(out: Path, ledger: Path) -> Path:
    cid = P.run_content_id(out)
    for root in (P.exec_class_root_for_ledger(ledger),
                 P.exec_class_root_for_ledger(ledger) / "local"):
        for p in root.glob("*.json") if root.is_dir() else ():
            if cid[:16] in p.read_text(encoding="utf-8"):
                return p
    raise AssertionError("등록 레코드를 못 찾았다")


def test_a_published_record_has_exactly_one_name(tmp_path, ledger):
    """★ P1-1 — 정상 게시가 끝나면 이름은 **하나**다."""
    out = _commit(tmp_path, ledger)
    rec = _record_path(out, ledger)
    assert os.stat(rec).st_nlink == 1, (
        f"게시된 레코드의 이름이 {os.stat(rec).st_nlink}개다 — 두 번째 문으로 "
        "내용을 바꿀 수 있다 (P1-1)")
    leftovers = [p.name for p in rec.parent.iterdir() if p.name.startswith(".")]
    assert not leftovers, f"temp alias 가 남았다: {leftovers} (P1-1)"


def test_the_publish_never_creates_a_second_name_on_this_kernel(tmp_path,
                                                                 ledger):
    """★ P1-1 — 이 커널에서는 **정리할 temp 자체가 안 생긴다.**

    `renameat2(RENAME_NOREPLACE)` 는 무대체 보장을 유지하면서 원자적으로
    **옮긴다.** 그러므로 "정리가 실패하면?" 이라는 물음이 성립하지 않는다 —
    질문을 없애는 것이 검사를 더하는 것보다 강하다.
    """
    assert P._rename_noreplace is not None
    out = _commit(tmp_path, ledger, "moved")
    rec = _record_path(out, ledger)
    assert os.stat(rec).st_nlink == 1
    assert P._RENAMEAT2 not in (None,), "게시가 renameat2 를 안 물어봤다"


def test_the_fallback_path_does_not_swallow_a_cleanup_failure(tmp_path, ledger,
                                                               monkeypatch):
    """★ P1-1 — `renameat2` 가 없는 커널로 물러설 때가 반례의 자리다.

    리뷰어 실측: 평범한 `OSError` 하나로 `registration_returned_success:true ·
    temp_alias_count:1 · final_nlink:2` 였다. process death 가 아니어도 그
    상태가 만들어진다. 물러선 경로에서는 **성공을 보고하지 않는다.**
    """
    monkeypatch.setattr(P, "_rename_noreplace", lambda src, dst: False)
    real_unlink = os.unlink

    def _refuse(path, *a, **k):
        if str(path).rsplit("/", 1)[-1].startswith("."):
            raise OSError(1, "시험이 만든 정리 실패")
        return real_unlink(path, *a, **k)

    monkeypatch.setattr(P.os, "unlink", _refuse)
    with pytest.raises(P.PreserveError) as ei:
        _commit(tmp_path, ledger, "unlink-fails")
    monkeypatch.setattr(P.os, "unlink", real_unlink)
    assert "두 번째 문" in str(ei.value), str(ei.value)


def test_a_record_with_two_names_is_refused_by_the_reader(tmp_path, ledger):
    """★ P1-1 — 층이 둘이다. **읽는 쪽**도 이름이 하나인지 본다.

    게시 경로를 아무리 고쳐도 crash 로 남은 alias 는 있을 수 있다. 그때
    읽는 쪽이 그것을 authority 로 받으면 방어가 없는 것과 같다.
    """
    out = _commit(tmp_path, ledger)
    rec = _record_path(out, ledger)
    os.link(rec, rec.parent / (".sneaked." + rec.name))     # 두 번째 문

    with pytest.raises(P.PreserveError) as ei:
        P.read_execution_class(P.run_content_id(out), ledger=ledger)
    assert "이름" in str(ei.value), str(ei.value)
