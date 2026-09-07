"""58차 L9 — producer 의미 닫힘이 **아직 실행 가능한 코드**를 놓친다.

57차 P0-6/P0-7 이 닫았다고 한 바로 그 자리의 반례다. 리뷰어 실측:

    MODULE_EFFECTS_ANNASSIGN:      digest_equal=true, result 1 -> 9
    MODULE_EFFECTS_NAME_DECORATOR: digest_equal=true, result 1 -> 9
    {"accepted":true, "capability_discovered":false,
     "digest_equal":true, "result_a":1, "result_b":9}

세 축이 같은 실패형이다 — **import 시 도는 계산과 이름 공간을 여는 능력이
닫힘 밖에 있다.** 그러면 "이 코드가 이 값을 만들었다" 는 주장이 그만큼 거짓이
된다.

`[해석]` 두 물음을 바꾼다.

1. **머리** — 57차는 "머리에 계산이 있는가" 를 물었다 (`Call`·`Attribute` 등).
   데코레이터는 이름 하나여도 **정의된 객체를 바꾼다** — 조회가 아니라 치환이다.
   그래서 데코레이터는 계산 여부를 묻지 않고 **무조건** 묶는다. annotation·기본
   인자·base 는 조회일 수 있으므로 계산 규칙을 그대로 둔다 (57차가 그 구별을
   실측으로 정했다: 넓게 잡으면 게시 경로가 producer 안으로 끌려온다).

2. **능력** — 57차는 "이 이름이 능력인가" 를 module scope 에서만 따라갔다.
   별칭은 함수 안에서도, 튜플 풀기로도, 컨테이너·partial·factory 로도 만들 수
   있고 그 목록은 안 끝난다. 그래서 방향을 뒤집는다: **능력은 부르는 자리에만
   나타날 수 있다.** 다른 자리에 나타나면 어디로 가는지 정적으로 답할 수
   없으므로 거부한다 (fail-closed).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
if str(REPO / "docs" / "22p_gap") not in sys.path:
    sys.path.insert(0, str(REPO / "docs" / "22p_gap"))


def _rp():
    import row_projection as rp

    return rp


def _scoring() -> str:
    return (REPO / "src" / "scoring.py").read_text(encoding="utf-8")


def _base(rp) -> str:
    """닫힘이 요구하는 이름을 다 갖춘 최소 producer 소스."""
    return (
        "import src.scoring as sc\n"
        "def _cell(x):\n    return x\n"
        "def _restart_list(x):\n    return x\n"
        "def _restart_facts(x):\n    return x\n"
        "def _add_multistart_blocks(x):\n    return x\n"
        "def _analyzer_provenance(x):\n    return x\n"
        "def score_canonical(df):\n    return df\n"
        "def build(x):\n    return x\n"
    ) + "".join(f"def {n}(*a, **k):\n    return None\n"
                for n in rp._PRODUCER_CUT)


# ─────────────────────────────────────────────────────────────────────────────
# L9-a — import 시 도는데 닫힘에 안 들어오는 문법
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("inject", [
    # ① AnnAssign 의 우변 — 리뷰어 반례 그대로. `Assign` 은 57차가 닫았지만
    #    `AnnAssign` 은 target 만 묶고 우변을 안 봤다.
    "_SIDE: object = sc.add_error_columns\n",
    # ② AnnAssign 의 annotation — 미룸 없는 module scope 에서는 이것도 돈다
    "_ANN: sc.add_error_columns = 1\n",
    # ③ AugAssign — 기존 이름의 **상태를 바꾼다**. 아무도 그 이름을 안 읽으면
    #    54차가 `Expr` 에서 닫은 것과 같은 구멍이 된다.
    "_ACC = 0\n_ACC += 1\n",
    # ④ 이름 하나짜리 데코레이터 — 리뷰어 반례. 계산 노드가 안 남지만 정의
    #    시점에 **반드시** 실행되고 정의된 객체를 바꾼다.
    "def _decorate(f):\n    return f\n"
    "@_decorate\ndef _decorated():\n    return None\n",
])
def test_import_time_execution_is_inside_the_identity__58(inject):
    """★ L9-a — import 시 도는 노드를 더했는데 digest 가 그대로면 안 된다."""
    rp = _rp()
    sc = _scoring()
    base = _base(rp)

    d0 = rp._producer_semantic_over(base, sc)
    try:
        d1 = rp._producer_semantic_over(base + inject, sc)
    except SystemExit:
        return          # 거부도 정답이다 — 볼 수 없으면 막는 것이 이 규칙이다
    assert d0 != d1, (
        "import 시 실행되는 노드를 더했는데 producer digest 가 그대로다 — "
        "그 계산은 봉인 밖에서 돈다 (58차 L9-a)")


def test_a_name_only_decorator_changes_the_identity_when_its_body_changes():
    """★ L9-a — 데코레이터 **본문**이 바뀌면 digest 가 움직여야 한다.

    "노드를 더하면 digest 가 바뀐다" 만으로는 부족하다. 데코레이터는 정의된
    객체를 치환하므로 그 **구현**이 계산 의미를 정한다. 리뷰어가 결과를
    1 → 9 로 바꾼 자리가 바로 여기다.
    """
    rp = _rp()
    sc = _scoring()
    dec_a = ("def _decorate(f):\n    return f\n"
             "@_decorate\ndef _decorated():\n    return 1\n")
    dec_b = ("def _decorate(f):\n    return lambda *a, **k: 9\n"
             "@_decorate\ndef _decorated():\n    return 1\n")

    base = _base(rp)
    da = rp._producer_semantic_over(base + dec_a, sc)
    db = rp._producer_semantic_over(base + dec_b, sc)
    assert da != db, (
        "데코레이터 구현을 바꿔 결과가 1 → 9 로 달라지는데 producer digest 가 "
        "같다 — 데코레이터 적용이 identity 밖에서 돈다 (58차 L9-a)")


# ─────────────────────────────────────────────────────────────────────────────
# L9-b — 능력이 함수 scope·컨테이너·factory 로 새 나간다
# ─────────────────────────────────────────────────────────────────────────────

_ESCAPES = {
    # 리뷰어 반례 그대로 — 함수 지역 별칭
    "함수 지역 별칭":
        "def score_canonical(df):\n"
        "    GET = getattr\n"
        "    return GET(sc, 'add_error_columns')(df)\n",
    # 튜플 풀기 — 별칭을 만드는 다른 문법
    "튜플 풀기":
        "def score_canonical(df):\n"
        "    GET, _Z = getattr, 1\n"
        "    return GET(sc, 'add_error_columns')(df)\n",
    # 컨테이너 경유 — 이름이 아니라 값이 능력을 나른다
    "컨테이너":
        "def score_canonical(df):\n"
        "    _T = (getattr,)\n"
        "    return _T[0](sc, 'add_error_columns')(df)\n",
    # partial — 능력을 인자로 넘겨 한 겹 미룬다
    "partial":
        "import functools\n"
        "def score_canonical(df):\n"
        "    return functools.partial(getattr, sc)('add_error_columns')(df)\n",
    # factory — 능력을 **돌려주는** 함수
    "factory":
        "def _mk():\n    return getattr\n"
        "def score_canonical(df):\n"
        "    return _mk()(sc, 'add_error_columns')(df)\n",
}


@pytest.mark.parametrize("label", sorted(_ESCAPES))
def test_a_capability_that_leaves_the_call_site_is_refused(label):
    """★ L9-b — 능력이 **부르는 자리 밖**에 나타나면 거부한다.

    57차의 고정점은 module scope 의 `x = getattr` 만 따라갔다. 리뷰어는 그
    별칭을 함수 안으로 한 줄 옮겨 그대로 통과시켰다 — `src.scoring.external`
    을 1 → 9 로 바꿔도 digest 가 같았다.

    별칭을 만드는 문법을 하나씩 더 따라가는 것은 끝나지 않는다 (53차에
    blacklist 로 이미 배운 것과 같은 형태다). 그래서 묻는 것을 바꾼다:
    **이 능력이 어디로 가는지 정적으로 답할 수 있는가.** 호출식의 대상으로
    쓰이는 것 말고는 답할 수 없으므로 거부한다.
    """
    rp = _rp()
    sc = _scoring()
    body = _ESCAPES[label]
    src = (
        "import src.scoring as sc\n"
        "def _cell(x):\n    return x\n"
        "def _restart_list(x):\n    return x\n"
        "def _restart_facts(x):\n    return x\n"
        "def _add_multistart_blocks(x):\n    return x\n"
        "def _analyzer_provenance(x):\n    return x\n"
        + body +
        "def build(x):\n    return x\n"
    ) + "".join(f"def {n}(*a, **k):\n    return None\n"
                for n in rp._PRODUCER_CUT)

    with pytest.raises(SystemExit) as ei:
        rp._producer_semantic_over(src, sc)
    msg = str(ei.value)
    assert "능력" in msg or "동적" in msg, msg


def test_the_capability_set_follows_function_scope_and_destructuring():
    """★ L9-b 앞단 — 능력 유도가 **함수 안의 대입**도 본다.

    57차 유도 함수는 `tree.body` 만 훑었다. "정적으로 안 보인다" 고 적어 뒀지만
    함수 안의 대입은 정적으로 보인다 — 우리가 안 본 것뿐이다.

    escape 규칙(위)이 이미 같은 반례를 잡지만 이 층을 따로 못 박는다: 두 층은
    서로 다른 물음이고, 한쪽을 좁힐 때 다른 쪽이 조용히 사라지면 안 된다.
    """
    rp = _rp()
    caps = rp._namespace_capabilities(
        "def f():\n"
        "    GET = getattr\n"
        "    return GET\n"
        "def g():\n"
        "    G2, _Z = GET, 1\n"
        "    return G2\n"
        "def h():\n"
        "    SAFE = len\n"
        "    return SAFE\n")
    for want in ("GET", "G2"):
        assert want in caps, f"{want} 가 능력 집합에 없다: {sorted(caps)}"
    assert "SAFE" not in caps, "무해한 별칭까지 능력으로 셌다"
    assert "_Z" not in caps, "튜플 짝을 안 맞추고 통째로 물들였다"


def test_the_producer_itself_still_hashes():
    """★ 규칙을 넓혔으므로 **이 트리 자신이 그 규칙을 통과하는지** 본다.

    fail-closed 를 넓히는 수정은 producer 자신의 정상 코드를 먼저 잡을 수
    있다 — 54차·57차가 실측으로 겪었다. 근거 없이 넓은 거부는 안전이 아니라
    고장이다.
    """
    rp = _rp()
    assert len(rp._producer_semantic_sha256()) == 16
    assert len(rp._compute_sha256()) == 16
