"""59차 β (M6) — clean clone 에는 좌표 봉인이 **없다**. 그러면 무엇을 지키는가.

58차 L5 는 얼릴 때의 `(major:minor, filesystem 안의 경로)` 를 봉인해 두고
`_assert_writable()` 의 **첫 층**으로 삼았다. 그 봉인은 기계 지역이고
gitignore 된다 (`_frozen_coords/`) — 다른 기계의 좌표는 여기서 뜻이 없기
때문이다.

리뷰어의 지적: 그렇다면 **fresh clone 에서는 그 층이 통째로 없다.** 남는 것은
원장이 적은 이름과 tree 안 marker 를 "지금 보이는 이름" 으로 찾는 층들인데,
그것들은 58차 반례가 이미 무력화한 층이다. 즉 이 방어는 **이 기계에서만**
살아 있다.

`[해석]` 봉인을 clone 에 담을 수는 없다 (좌표는 기계의 사실이다). 그러면
답은 하나뿐이다 — **봉인이 없으면 게시하지 않는다.** 없는 방어를 있는 척하지
않고, 사람이 이 기계에서 한 번 봉인하게 만든다. fail-closed 는 "모른다" 를
"안전하다" 로 바꾸지 않는 것이고, 여기서 우리는 정확히 모른다.
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

import tools.preserve as P                                      # noqa: E402
import row_projection as R                                      # noqa: E402


@pytest.fixture
def clean_clone(tmp_path, monkeypatch):
    """원장은 `gA` 를 frozen 이라 적었고, 좌표 봉인은 **하나도 없다**."""
    led = tmp_path / "authority" / "LEG_PRESERVATION.yaml"
    led.parent.mkdir(parents=True)
    led.write_text("planned: []\nlegs: []\ncohorts: []\n", encoding="utf-8")
    monkeypatch.setattr(P, "canonical_ledger", lambda x=None: led)

    frozen = tmp_path / "gA"
    (frozen / "child").mkdir(parents=True)
    monkeypatch.setattr(R, "_frozen_cohort_dirs", lambda: {"gA": frozen})
    assert P.sealed_frozen_coordinates(led) == [], "이 시험은 봉인 0건에서 시작한다"
    return led, frozen


def test_publication_is_refused_while_a_frozen_cohort_has_no_local_seal(
        clean_clone, tmp_path):
    """★ M6 — 봉인 없는 frozen cohort 가 있으면 **아무 데도 못 쓴다**.

    "그 cohort 자리만 막는다" 로는 부족하다 — 막을 자리를 아는 층이 바로 지금
    없는 층이기 때문이다. 모르는 동안은 게시 자체를 멈춘다.
    """
    dest = tmp_path / "새-세대"
    dest.mkdir()
    with pytest.raises(SystemExit) as ei:
        R._assert_writable(dest)
    msg = str(ei.value)
    assert "gA" in msg, msg
    assert "봉인" in msg, msg
    assert "--seal-frozen" in msg, (
        f"거부만 하고 빠져나갈 길을 안 알려준다: {msg}")


def test_after_sealing_on_this_machine_publication_proceeds(clean_clone,
                                                            tmp_path):
    """★ M6 의 반대 방향 — 봉인한 뒤에는 정상 자리에 쓸 수 있다.

    거부가 영구하면 그것은 경계가 아니라 마비다 (49차에 smoke 승격 검사에서
    같은 실수를 했고 실패 11건으로 배웠다).
    """
    led, frozen = clean_clone
    P.record_frozen_coordinate(frozen, "gA", ledger=led)

    dest = tmp_path / "새-세대"
    dest.mkdir()
    R._assert_writable(dest)             # 예외가 없어야 한다

    # 그리고 얼린 자리 **안**은 여전히 못 쓴다 (봉인이 제 일을 한다)
    with pytest.raises(SystemExit):
        R._assert_writable(frozen / "child")


def test_the_seal_entry_point_seals_every_declared_frozen_cohort(clean_clone,
                                                                 tmp_path):
    """★ M6 — 사람이 한 번 부르는 자리가 **선언된 전부**를 봉인해야 한다.

    하나씩 봉인하게 하면 빠뜨린 하나가 조용한 구멍이 된다. 거부 메시지가
    가리키는 명령은 원장이 frozen 이라고 말한 것을 모두 덮어야 한다.
    """
    led, frozen = clean_clone
    sealed = R.seal_frozen_cohorts()
    assert sealed == ["gA"], sealed
    assert P.frozen_coordinate_covering(frozen / "child", ledger=led) == "gA"

    # 멱등이다 — 두 번 불러도 같은 상태고 오류가 아니다
    assert R.seal_frozen_cohorts() == []
