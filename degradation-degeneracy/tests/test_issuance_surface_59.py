"""59차 ζ (M10) — 발급의 **공개 표면**은 하나여야 한다.

리뷰어 반례: 공개 raw 발급 함수에 `token="아무거나"` 를 주면 계획이 `running`
으로 옮겨지고 claim 파일이 생긴다. 그런데 그 token 은 **디스크에 없다.** 그러면
그 다리는

  · 재개할 수 없고 (`attach_leg_run()` 이 읽을 token 파일이 없다)
  · 되돌릴 수도 없고 (`release_leg_run()` 도 소유 증명을 요구한다)
  · 닫을 수도 없다

— 53차가 "메모리에만 있는 소유 증명" 을 없애며 지운 바로 그 상태다. 54차 P0-6
은 `token=None` 을 막았지만 **아무 문자열이나** 주는 길은 열어 두었다.

`[해석]` 방어는 "token 이 비어 있지 않은가" 가 아니라 **"그 token 이 디스크에
굳어 있는가"** 여야 한다. 그리고 그 불변식을 세우는 자리는 하나뿐이다
(`open_leg_run()` — token 을 먼저 굳히고 그 값으로 claim 을 만든다). 그러므로
공개 표면에서 raw 발급을 **내린다** (M1 이 `record_run_outputs()` 에 한 것과
같은 판정이다: 우회로가 공개 API 로 남아 있으면 "그 길은 없다" 가 거짓이다).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import tools.preserve as P                                      # noqa: E402

#: 공개 표면에 있으면 안 되는 이름. 문자열로 적는다 — 이 파일이 그 이름을
#: import 하면 시험 자신이 표면을 되살리는 셈이다.
_RAW_ISSUER = "claim" "_planned_leg"


def test_there_is_no_public_raw_issuance():
    """★ M10 — raw 발급 함수가 **공개돼 있으면 안 된다**."""
    assert not hasattr(P, _RAW_ISSUER), (
        f"raw 발급(`{_RAW_ISSUER}`)이 아직 공개 API 다 — 디스크에 없는 소유 "
        "증명으로 계획을 `running` 으로 옮길 수 있다 (M10)")
    assert callable(getattr(P, "open_leg_run", None)), (
        "발급의 정상 경로(`open_leg_run`)가 없다")


def test_issuing_with_a_token_that_is_not_on_disk_is_refused(tmp_path):
    """★ M10 — 이름을 숨기는 것으로 끝내지 않는다. **불변식을 세운다.**

    내부 함수라도 디스크에 없는 소유 증명을 받으면 같은 상태가 만들어진다.
    그러므로 발급은 그 token 이 이 다리의 자리에 **이미 굳어 있는지** 확인한다.
    """
    import tests.test_preserve as TP

    led = TP._lifecycle_ledger(tmp_path)
    issue = getattr(P, "_" + _RAW_ISSUER)
    with pytest.raises(P.PreserveError) as ei:
        issue("L", TP._RUN_SPEC_L, "0123456789abcdef",
              ledger=led, token=TP._tok())
    msg = str(ei.value)
    assert "디스크" in msg or "open_leg_run" in msg, msg

    # 그리고 **아무 상태도 안 남았다** — 거부하면서 계획을 옮기면 그것이 곧
    # 리뷰어가 지목한 갇힌 다리다.
    idx = P.planned_index(ledger=led)
    assert idx["L"]["status"] == "planned", (
        f"거부했는데 계획이 {idx['L']['status']!r} 로 옮겨졌다 (M10)")


def test_the_normal_path_still_issues_and_leaves_a_durable_token(tmp_path):
    """★ M10 의 반대 방향 — 정상 발급은 그대로여야 한다.

    `open_leg_run()` 은 token 을 먼저 굳히고 그 값으로 claim 을 만든다. 발급
    뒤에는 claim 과 소유 증명이 **둘 다** 디스크에 있어야 한다.
    """
    import tests.test_preserve as TP

    led = TP._lifecycle_ledger(tmp_path)
    claim = P.open_leg_run("L", TP._RUN_SPEC_L, "0123456789abcdef", ledger=led)
    assert claim.token, "발급이 소유 증명을 안 돌려준다"
    tok = P.attempt_path_for("L", ledger=led)
    assert tok.is_file(), "소유 증명이 디스크에 없다 — 재개도 되돌림도 못 한다"
    assert P.read_token_file(tok, "L") == claim.token
    assert P.planned_index(ledger=led)["L"]["status"] == "running"
