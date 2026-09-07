"""58차 L8 — 발급이 directory fsync 실패를 **삼키지 않아야** 한다.

`_fsync_dir()` 의 docstring 은 "실패를 삼키지 않는다" 라고 적혀 있고,
`_fsync_dir_strict()` 도 있다. 그런데 claim 과 소유 증명을 굳히는 **발급 두
자리**는 비-strict 판본을 부르고 반환값을 버렸다. 그래서 세 번의 directory
flush 가 전부 실패해도 `open_leg_run()` 이 claim 을 돌려주고 계획을 `running`
으로 옮겼다.

`[해석]` 이건 "power-loss 모델이 없다" 는 인프라 한계와 **다르다.** 코드가 검사를
실제로 실행했고, 명시적 실패를 관측했고, 그런데도 성공을 보고했다. 그리고 실패한
그 directory entry 가 하필 **token-before-claim 순서를 증명하는 바로 그것**이다.
파일 데이터가 굳어도 이름이 안 굳으면 복구 불변식이 성립하지 않는다.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import tools.preserve as P


def test_issuance_fails_closed_when_a_directory_cannot_be_flushed(
        tmp_path, monkeypatch):
    """★ L8 — directory fsync 가 실패하면 발급이 멈춰야 한다.

    실패를 주입하는 자리는 `_fsync_dir` 자체다 — 파일 write·read-back·lock 은
    전부 그대로 두고, **커널이 directory 이름을 못 굳혔다** 는 한 가지 사실만
    바꾼다. 그 상태에서 `open_leg_run()` 이 성공하면 안 된다.
    """
    # 계획 원장은 **이미 있는 fixture 를 쓴다.** 손으로 다시 만들면 필드 하나가
    # 빠져 시험이 durability 에 닿기도 전에 다른 이유로 빨개진다 (실제로 그랬다 —
    # `authorization_kind` 가 없어서 계약 enum 검사에 먼저 걸렸다).
    from tests.test_preserve import _lifecycle_ledger, _RUN_SPEC_L
    ledger = _lifecycle_ledger(tmp_path)

    seen: list[str] = []

    def _always_fails(d):
        seen.append(str(d))
        return False

    monkeypatch.setattr(P, "_fsync_dir", _always_fails)

    with pytest.raises(P.PreserveError) as exc:
        P.open_leg_run("L", _RUN_SPEC_L, "0123456789abcdef", ledger=ledger)

    assert seen, "directory fsync 를 아예 시도하지 않았다"
    assert "durable" in str(exc.value) or "굳" in str(exc.value), (
        f"멈추기는 했는데 사유가 durability 가 아니다: {exc.value}")
