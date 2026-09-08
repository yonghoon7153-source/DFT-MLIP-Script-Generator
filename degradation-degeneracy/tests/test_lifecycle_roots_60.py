"""60차 δ (P0-5) — **파생 root 의 부모를 따라 얼린 tree 에 쓴다.**

리뷰어 반례: 유효한 원장 옆의 `_claims`·`_attempts` 를 기존 `.FROZEN` tree 로
향한 **디렉터리 symlink** 로 만들고 공개 `open_leg_run()` 을 부른다.

    {"open_leg_run_returned":true,"plan_status":"running",
     "token_written_inside_frozen_tree":true,
     "claim_written_inside_frozen_tree":true,
     "marker_still_present":true}

`[해석]` 57차는 token 의 **마지막 성분**이 symlink 인 경우를 막았다. 그런데
root 자체가 `canonical_ledger(...).parent / "_claims"` 라는 **이름**으로만
유도되고, `mkdir`·temp·`os.replace` 는 그 부모를 따라간다. 마지막 성분 검사로는
부모 alias 가 안 막힌다 — 경로는 성분의 열이고, 검사한 성분만 검사된 것이다.

그러므로 이 라운드는 root 를 **이름이 아니라 대상**으로 연다: `O_NOFOLLOW` 로
열어 alias 면 그 자리에서 거부하고, 그 handle 아래에서만 만들고 쓴다.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import tools.preserve as P                                      # noqa: E402


@pytest.fixture
def aliased(tmp_path, monkeypatch):
    """원장 옆의 두 파생 root 가 **얼린 tree 로 향한 symlink** 인 상태."""
    led = tmp_path / "authority" / "LEG_PRESERVATION.yaml"
    led.parent.mkdir(parents=True)
    led.write_text(
        "planned:\n"
        "  - leg: L\n"
        "    status: planned\n"
        "legs: []\ncohorts: []\n", encoding="utf-8")
    monkeypatch.setattr(P, "canonical_ledger", lambda x=None: led)

    frozen = tmp_path / "proj_gA"
    frozen.mkdir()
    (frozen / ".FROZEN").write_text("frozen\n", encoding="utf-8")
    for name in ("_claims", "_attempts"):
        (led.parent / name).symlink_to(frozen, target_is_directory=True)
    return led, frozen


def test_a_symlinked_claims_root_is_refused(aliased):
    """★ P0-5 — root 가 alias 면 **거기에 아무것도 안 만든다.**"""
    led, frozen = aliased
    before = sorted(p.name for p in frozen.iterdir())
    with pytest.raises(P.PreserveError) as ei:
        P.claims_root_for_ledger(led)
    assert "alias" in str(ei.value) or "symlink" in str(ei.value), str(ei.value)
    assert sorted(p.name for p in frozen.iterdir()) == before, (
        "거부하면서 얼린 tree 안에 무언가를 만들었다 (P0-5)")


def test_a_symlinked_attempts_root_is_refused(aliased):
    """★ P0-5 — token 쪽 root 도 같다 (둘 다 같은 유도 규칙을 쓴다)."""
    led, frozen = aliased
    with pytest.raises(P.PreserveError):
        P.attempts_root_for_ledger(led)


def test_the_public_issuer_writes_nothing_into_the_frozen_tree(aliased):
    """★ P0-5 — 반례가 부른 **공개 진입점**이 얼린 tree 를 안 건드린다.

    함수 하나를 막는 것으로는 부족하다 — 반례는 `open_leg_run()` 을 불렀다.
    그 경로 전체가 멈춰야 하고, 멈춘 뒤 얼린 tree 는 처음 그대로여야 한다.
    """
    led, frozen = aliased
    before = sorted(p.name for p in frozen.rglob("*"))
    with pytest.raises((P.PreserveError, SystemExit)):
        P.open_leg_run("L", {"phase": "grid"}, "0" * 16, ledger=led)
    assert sorted(p.name for p in frozen.rglob("*")) == before, (
        "얼린 tree 안에 token·claim 이 생겼다 (P0-5)")
    assert (frozen / ".FROZEN").is_file()


def test_a_normal_root_still_works(tmp_path, monkeypatch):
    """★ 거부가 영구하면 그것은 경계가 아니라 마비다 (49차의 교훈).

    alias 가 아닌 정상 자리에서는 root 가 그대로 만들어져야 한다.
    """
    led = tmp_path / "authority" / "LEG_PRESERVATION.yaml"
    led.parent.mkdir(parents=True)
    led.write_text("planned: []\nlegs: []\ncohorts: []\n", encoding="utf-8")
    monkeypatch.setattr(P, "canonical_ledger", lambda x=None: led)

    root = P.claims_root_for_ledger(led)
    assert root.is_dir() and not root.is_symlink()
    assert P.attempts_root_for_ledger(led).is_dir()
