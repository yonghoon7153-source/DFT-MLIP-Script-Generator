"""60차 ζ (P0-10·P0-11·P0-12·P0-13) — **producer identity 의 평가 표면.**

리뷰어 반례 넷. 전부 `digest_equal: true` 이면서 결과가 달라진다 — 즉
identity 밖에서 계산이 일어난다.

    P0-10  `def score_canonical(df, namespace=sc): getattr(namespace, "external")(df)`
           → 매개변수가 module provenance 를 지운다 (2 → 8)
           그리고 caller 가 `sc` 와 `getattr` 을 **전달만** 해도 같다 (1 → 9)

    P0-11  중첩 함수의 매개변수가 **바깥 scope** 의 능력을 면제한다 (3 → 7)
           `def innocent(getattr, GET): ...` 안쪽에 있는데 바깥 `GET` 이 풀린다

    P0-12  `if sc.activate():` 의 **head** 와 `def f(*args: sc.activate())` 의
           vararg 주석이 import-time 표면 밖 (5 → 9 · 4 → 6)

    P0-13  module docstring 은 버리면서 `__doc__` 접근은 허용한다 (ALPHA → OMEGA)

`[해석]` 59차 δ 는 "실행된다를 기본으로" 를 세웠지만 **어디가 실행되는지의
목록**이 아직 문법보다 작았다 (P0-12·P0-13). 그리고 M17 의 완화는 능력의
**철자**에 대한 것이었는데, 그것이 대상의 **출처**까지 면제해 버렸다
(P0-10·P0-11). 두 물음은 다른 물음이다:

  · "이 이름이 능력인가" — 호출자가 값을 주는 자리면 아닐 수 있다 (M17)
  · "이 대상이 이름 공간이 **아님을 증명할 수 있는가**" — 호출자가 값을 주는
    자리면 **증명할 수 없다** (P0-10)

같은 `shadows` 집합이 한쪽에서는 면제, 다른 쪽에서는 거부의 근거다.
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


# ── P0-10 ─────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("inject", [
    # ① 기본값으로 module 을 받는 매개변수
    ("def score_canonical(df, namespace=sc):\n"
     "    return getattr(namespace, 'add_error_columns')(df)\n"),
    # ② 호출자가 **전달만** 하는 경우 — 능력도 매개변수다
    ("def score_canonical(df, namespace=None, GET=None):\n"
     "    return GET(namespace, 'add_error_columns')(df)\n"),
    # ③ `for` 로 묶인 이름도 호출자(반복 대상)가 값을 준다
    ("def score_canonical(df):\n"
     "    for m in [sc]:\n"
     "        return getattr(m, 'add_error_columns')(df)\n"),
])
def test_a_caller_supplied_binding_is_not_a_proof_of_non_namespace(inject):
    """★ P0-10 — 매개변수는 "이름 공간이 아님" 의 **증명이 아니다.**

    59차 M11 은 "벌거벗은 이름이면 증명됐다" 로 뒀다. 그런데 매개변수도
    벌거벗은 이름이고, 그 값은 **이 module 이 정하지 않는다.** 그러므로
    증명이 성립하지 않는다 — 증명할 수 없으면 거부다.
    """
    rp = _rp()
    with pytest.raises(SystemExit) as ei:
        rp._producer_semantic_over(_base(rp) + inject, _scoring())
    msg = str(ei.value)
    assert "이름 공간" in msg or "증명" in msg or "능력" in msg, msg


def test_reading_a_plain_parameter_attribute_is_still_allowed():
    """★ P0-10 의 반대 방향 — 매개변수의 평범한 속성 읽기는 그대로 둔다.

    거부가 넓어지면 producer 자신의 정규형 코드가 먼저 걸린다 (54차에 겪었다).
    막는 것은 **이름을 동적으로 푸는** 자리뿐이다.
    """
    rp = _rp()
    inject = ("def score_canonical(df):\n"
              "    return df.columns\n")
    rp._producer_semantic_over(_base(rp) + inject, _scoring())


# ── P0-11 ─────────────────────────────────────────────────────────────────
def test_a_nested_scope_binding_does_not_exempt_the_outer_scope():
    """★ P0-11 — 중첩 함수의 매개변수는 **그 함수 안에서만** 가린다.

    `_binding_shadows()` 가 `ast.walk` 로 전부 한 set 에 합쳤다. 그래서 안쪽
    함수가 `getattr`·`GET` 을 매개변수로 받기만 하면 바깥 scope 의 같은 이름이
    통째로 면제됐다. Python 의 scope 는 그렇게 동작하지 않는다.
    """
    rp = _rp()
    inject = ("def score_canonical(df):\n"
              "    def innocent(getattr, GET):\n"
              "        return None\n"
              "    GET = getattr\n"
              "    return [GET][0](sc, 'add_error_columns')(df)\n")
    with pytest.raises(SystemExit) as ei:
        rp._producer_semantic_over(_base(rp) + inject, _scoring())
    assert "능력" in str(ei.value) or "이름 공간" in str(ei.value), ei.value


def test_a_binding_still_shadows_inside_its_own_scope():
    """★ P0-11 의 반대 방향 — 59차 M17 의 완화는 **그 scope 안에서** 살아 있다.

    능력과 철자만 같은 매개변수는 여전히 능력이 아니다. scope 를 좁힌 것이
    M17 을 되돌리는 것이면 안 된다.
    """
    rp = _rp()
    inject = ("def _helper(vars):\n"
              "    return vars\n"
              "def score_canonical(df):\n"
              "    return _helper(df)\n")
    rp._producer_semantic_over(_base(rp) + inject, _scoring())


# ── P0-12 ─────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("inject", [
    "if sc.add_error_columns:\n    pass\n",
    "while sc.add_error_columns is None:\n    break\n",
    "for _x in [sc.add_error_columns]:\n    pass\n",
    "def _Trigger(*args: sc.add_error_columns):\n    pass\n",
    "def _Trigger2(**kw: sc.add_error_columns):\n    pass\n",
])
def test_compound_heads_and_vararg_annotations_are_import_time(inject):
    """★ P0-12 — import 때 **평가되는 식**은 전부 실행 슬라이스 안이다.

    `_MODULE_COMPOUND` 는 body 와 target 결속만 기록하고 head(`If.test` ·
    `While.test` · `For.iter` · `With` · `Match.subject`)를 `MODULE_EFFECTS` 에
    안 넣었다. `_import_time_heads()` 는 ordinary/pos-only/kw-only 주석만 보고
    vararg·kwarg 주석을 빠뜨렸다. 둘 다 **실제 import 때 평가된다.**
    """
    rp = _rp()
    base = _base(rp)
    d0 = rp._producer_semantic_over(base, _scoring())
    d1 = rp._producer_semantic_over(base + inject, _scoring())
    assert d0 != d1, (
        "import 때 평가되는 식을 더했는데 producer identity 가 그대로다 (P0-12)")


# ── P0-13 ─────────────────────────────────────────────────────────────────
def test_the_module_docstring_is_inside_the_identity(rp=None):
    """★ P0-13 — module docstring 을 바꾸면 producer identity 가 움직인다.

    처음 쓴 판은 `__doc__` **접근을 거부**하는 쪽이었다. 그런데 이 저장소는
    51차 P0-I 에서 이미 반대 방향을 정해 뒀다 — "철자를 막는 것은 종결 조건이
    아니다 (alias 의 alias 로 이어진다). **버리는 것을 없애면** 그 축 자체가
    사라진다." 그리고 그 결정을 지키는 시험이 있다
    (`test_a_docstring_the_computation_reads_is_inside_the_identity`).

    60차가 찾은 것은 그 수정이 **function·class 에만** 적용됐다는 사실이다:
    module 의 첫 문자열은 여전히 버려졌다. 그래서 고칠 자리는 dunder 목록이
    아니라 `_module_defs()` 이고, 거기서 module docstring 을 `__doc__` 라는
    이름으로 묶는다.
    """
    rp = _rp()
    inject = ("def score_canonical(df):\n"
              "    return __doc__\n")
    a = rp._producer_semantic_over('"""ALPHA"""\n' + _base(rp) + inject,
                                   _scoring())
    b = rp._producer_semantic_over('"""OMEGA"""\n' + _base(rp) + inject,
                                   _scoring())
    assert a != b, (
        "module 문서 문자열만 바꿨는데 producer identity 가 그대로다 — "
        "계산이 그것을 읽는데도 identity 밖이다 (P0-13)")
