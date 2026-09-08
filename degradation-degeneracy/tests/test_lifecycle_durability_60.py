"""60차 δ (P0-6) — **성공한 short write 뒤에도 freeze 가 성공한다.**

리뷰어 반례 (전원 손실 모델이 아니다 — `write_text()` 가 **성공 반환**한다):

    {"fault_hit":true,"freeze_returned_record":true,
     "frozen_marker_exists":true,"head_exists":true,"journal_bytes":"{",
     "ledger_status_after_success":"frozen",
     "subsequent_reader":"SystemExit: ... journal 0번째 줄이 JSON 이 아니다 ..."}

`[해석]` `_append_lifecycle_locked()` 는 journal temp 를 `Path.write_text()` 로
쓰고 **돌아온 길이를 안 보고 다시 읽지도 않았다.** 그리고 head 는 디스크의
journal 이 아니라 **메모리의 의도 record** 로 만들었다. 그래서 손상된 temp 가
publish 되고, head 는 있지도 않은 줄을 가리키며, ledger 는 `frozen` 이 된다 —
성공을 보고하면서 원장을 못 읽는 상태로 만든 것이다.

이 저장소는 같은 계단을 이미 세 번 만들었다 (claim·token·실행 class 레코드):
**write-all → fsync → 정확한 read-back → 대체 → 최종 read-back → 부모 fsync.**
journal 과 head 만 그 계단 밖에 있었다.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(REPO / "docs" / "22p_gap") not in sys.path:
    sys.path.insert(0, str(REPO / "docs" / "22p_gap"))

import row_projection as R                                      # noqa: E402


@pytest.fixture
def lifecycle(tmp_path, monkeypatch):
    """journal·head·잠금을 tmp 로 옮긴 lifecycle 한 벌."""
    root = tmp_path / "22p_gap"
    root.mkdir(parents=True)
    monkeypatch.setattr(R, "_lifecycle_path",
                        lambda: root / "COHORT_LIFECYCLE.jsonl")
    monkeypatch.setattr(R, "_lifecycle_head_path",
                        lambda: root / "COHORT_LIFECYCLE.head")
    monkeypatch.setattr(R, "_cohort_dir_key", lambda cid: f"proj_{cid}")
    return root


def test_a_short_journal_write_never_becomes_a_published_transition(lifecycle,
                                                                     monkeypatch):
    """★ P0-6 — 한 바이트만 쓰이면 그 전이는 **게시되지 않는다.**

    반례 그대로: temp 에 `{` 한 글자만 쓰고 성공 반환하게 만든다. 그러면
    전이는 실패해야 하고, journal 도 head 도 그 손상을 안 받아야 한다.
    """
    R._append_lifecycle("g1", None, "active", "첫 줄")
    before = lifecycle.joinpath("COHORT_LIFECYCLE.jsonl").read_bytes()
    head_before = lifecycle.joinpath("COHORT_LIFECYCLE.head").read_bytes()

    real = R._write_all_checked

    def _short(fd, data, where):
        if where == "cohort-lifecycle-journal":
            return real(fd, data[:1], where)     # 한 바이트만 (성공 반환)
        return real(fd, data, where)

    monkeypatch.setattr(R, "_write_all_checked", _short)
    with pytest.raises(SystemExit) as ei:
        R._append_lifecycle("g1", "active", "frozen", "얼린다")
    monkeypatch.setattr(R, "_write_all_checked", real)

    assert "read-back" in str(ei.value) or "다시 읽" in str(ei.value), str(ei.value)
    assert lifecycle.joinpath("COHORT_LIFECYCLE.jsonl").read_bytes() == before, (
        "손상된 temp 가 journal 로 게시됐다 (P0-6)")
    assert lifecycle.joinpath("COHORT_LIFECYCLE.head").read_bytes() == head_before, (
        "journal 이 안 굳었는데 head 가 움직였다 (P0-6)")
    # 그리고 그 뒤에도 읽힌다 — 실패가 원장을 못 읽는 상태로 만들지 않았다
    assert R.cohort_lifecycle_state("g1", R.read_lifecycle()) == "active"


def test_bytes_that_differ_from_what_we_meant_to_write_are_refused(lifecycle,
                                                                    monkeypatch):
    """★ P0-6 — 디스크에 들어간 것이 **쓰려던 것과 다르면** 게시하지 않는다.

    처음에 쓴 판은 "head 가 journal 의 마지막 줄과 같은가" 를 물었다. 그것은
    **처음부터 통과했다** — head 를 메모리 record 에서 만들고 journal 도 같은
    record 로 만들므로 두 값은 쓰기가 성공하든 실패하든 같은 식이 만든다.
    즉 그 시험은 아무것도 구별하지 못하는 시험이었고, 이 저장소가 반복해서
    배운 신호(처음부터 초록이면 fixture 가 진실을 가린다)가 정확히 그것이다.

    구별하는 물음은 **"쓴 것을 다시 읽어 대조하는가"** 다. 그래서 잘림이 아니라
    **변조**를 주입한다: 길이는 같고 내용이 다른 바이트를 쓴다.
    """
    R._append_lifecycle("g1", None, "active", "첫 줄")
    before = lifecycle.joinpath("COHORT_LIFECYCLE.jsonl").read_bytes()
    real = R._write_all_checked

    def _garbled(fd, data, where):
        if where == "cohort-lifecycle-journal":
            return real(fd, b"x" * len(data), where)     # 같은 길이, 다른 내용
        return real(fd, data, where)

    monkeypatch.setattr(R, "_write_all_checked", _garbled)
    with pytest.raises(SystemExit):
        R._append_lifecycle("g1", "active", "frozen", "얼린다")
    monkeypatch.setattr(R, "_write_all_checked", real)

    assert lifecycle.joinpath("COHORT_LIFECYCLE.jsonl").read_bytes() == before
    assert R.cohort_lifecycle_state("g1", R.read_lifecycle()) == "active"


def test_a_short_head_write_is_refused_too(lifecycle, monkeypatch):
    """★ P0-6 — head 도 같은 계단을 쓴다.

    journal 만 고치고 head 를 unchecked 로 두면 같은 반례가 한 칸 옆에서
    다시 선다. 이 저장소가 반복해서 배운 형태다.
    """
    R._append_lifecycle("g1", None, "active", "첫 줄")
    real = R._write_all_checked

    def _short(fd, data, where):
        if where == "cohort-lifecycle-head":
            return real(fd, data[:1], where)
        return real(fd, data, where)

    monkeypatch.setattr(R, "_write_all_checked", _short)
    with pytest.raises(SystemExit):
        R._append_lifecycle("g1", "active", "frozen", "얼린다")
    monkeypatch.setattr(R, "_write_all_checked", real)
