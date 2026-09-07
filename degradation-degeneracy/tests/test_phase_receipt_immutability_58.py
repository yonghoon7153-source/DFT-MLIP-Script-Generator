"""58차 L6 — 닫힌 phase 는 **불변**이어야 한다.

`LegClaim.phase_done()` 은 claim lock 안에 있다. 그래서 lost update 는 없다.
그런데 lock 이 막는 것은 **동시 쓰기**이지 **덮어쓰기**가 아니다 — 술어가
없으면 lock 은 "무조건 대입" 을 순서대로 해 줄 뿐이다 (`preserve.py:4756`).

리뷰어가 준 반례는 공개 API 만 쓰는 정상 일정이다:

  1. grid 가 receipt A 를 닫는다
  2. fit 이 `assert_phase_input_binding()` 으로 A 를 검증하고 자기 receipt 를 닫는다
  3. **같은 claim 을 쥔 늦은 writer** 가 grid 를 receipt B 로 다시 닫는다
  4. finalize 가 성공한다 — phase 키의 **존재만** 보기 때문이다 (`:6103`)

결과: 원장에 봉인된 grid receipt 는 B 인데, fit 은 A 를 보고 계산했다.
**생산자-소비자 결속이 끊긴 채 `executed` 로 닫힌다.**

이 파일의 규칙 둘:
  · **top-level consumer 를 부른다** — `open_leg_run()`·`finalize_leg()`.
  · 순서를 묻는 시험의 barrier 는 **임계 구역 안**에 잡는다 (α' 에서 배웠다).
    바깥에 잡으면 통과가 구현이 아니라 스케줄러를 증명한다.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import tools.preserve as P


@pytest.fixture
def ledger(tmp_path) -> Path:
    """계획에 실행권이 있는 다리 하나. 원장 fixture 는 **재사용**한다.

    α 라운드에서 계획 fixture 를 손으로 만들다 필드 하나(`authorization_kind`)를
    빠뜨려 시험이 엉뚱한 이유로 빨갰다. 있는 것을 쓴다.
    """
    from tests.test_preserve import _lifecycle_ledger
    return _lifecycle_ledger(tmp_path)


def _open(ledger: Path):
    from tests.test_preserve import _RUN_SPEC_L
    return P.open_leg_run("L", _RUN_SPEC_L, "0123456789abcdef", ledger=ledger)


def test_a_closed_phase_cannot_be_rewritten_with_a_different_receipt(ledger):
    """★ L6 — 이미 닫힌 phase 를 **다른 receipt** 로 덮으면 거부해야 한다.

    같은 receipt 의 재시도는 멱등으로 통과한다 — 재시도는 정상 운용이다.
    다른 값이면 거부다: 그 시점에 그 receipt 를 읽고 계산한 소비자가 이미
    있을 수 있고, 덮으면 그 소비자의 근거가 소리 없이 바뀐다.
    """
    claim = _open(ledger)
    claim.phase_done("grid", {"used_generation": "A"})

    # 같은 값의 재시도는 통과 (멱등)
    claim.phase_done("grid", {"used_generation": "A"})

    with pytest.raises(P.PreserveError):
        claim.phase_done("grid", {"used_generation": "B-late-writer"})


def test_finalize_refuses_when_the_sealed_grid_receipt_is_not_the_one_fit_used(
        ledger):
    """★ L6 의 두 번째 절반 — finalize 가 **결속을 다시 확인**해야 한다.

    phase 불변성만으로는 부족하다. 불변성이 없던 시절에 이미 어긋난 claim 이
    남아 있을 수 있고, finalize 는 원장에 봉인하는 **마지막 문**이다. 존재만
    보지 말고 fit 이 무엇을 썼는지와 대조해야 한다.

    이 시험은 `phase_done()` 을 우회해 어긋난 상태를 직접 만든 뒤
    **`finalize_leg()` 를 부른다** — 술어가 두 자리에 다 있어야 한다.
    """
    import json

    claim = _open(ledger)
    claim.phase_done("grid", {"used_generation": "A"})
    claim.phase_done("fit", {"consumed_grid": "A"})

    # 불변성 이전에 만들어진 어긋난 durable state 를 재현한다 (파일 직접 수정).
    rec = json.loads(claim.path.read_text(encoding="utf-8"))
    rec["phases"]["grid"]["receipt"] = {"used_generation": "B-late-writer"}
    claim.path.write_text(json.dumps(rec, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")) + "\n",
                          encoding="utf-8")

    with pytest.raises(P.PreserveError):
        P.finalize_leg("L", ledger=ledger, token=claim.token,
                       evidence={"leg_source_digest": "0123456789abcdef",
                                 "cohorts": ["gA"]})
