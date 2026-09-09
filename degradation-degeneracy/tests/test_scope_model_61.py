"""61차 δ (P1-4) — **comprehension 결속을 부모 scope 에 적용한다.**

리뷰어 반례 (평범한 Python 코드만 쓴다):

    python_return_value: GLOBAL
    analyzer_marks_global_return_as_shadowed: true
    analyzer_shadow_set_at_return: ["value", "xs"]

`[해석]` Python 3 에서 comprehension 의 target 은 **별도 scope** 다. 바깥에
안 샌다. 그런데 `_own_shadows()` 는 `ast.comprehension` 의 target 을 그 자리를
감싸는 함수의 shadow 집합에 합치고, `_scoped_shadows()` 가 그 집합을 함수
**전체**의 load 에 적용한다. 그러면 분석기가 실제 Python 과 반대를 말한다.

60차 P0-11 은 "shadow 는 scope 별" 을 세웠는데, **scope 의 목록**이 Python 의
것보다 작았다 — 함수·lambda·class 는 넣고 comprehension 은 빼먹었다.
59차 M12(문법보다 작은 실행 슬라이스)와 같은 형태다.

`[고침]` comprehension 넷(`ListComp`·`SetComp`·`DictComp`·`GeneratorExp`)을
**자식 scope 로 다룬다.** 다만 Python 은 **가장 바깥 iterable 만** 바깥 scope
에서 평가하므로 그 자리는 바깥 집합으로 남긴다 — 규칙을 통째로 옮기면 그
자리가 반대로 틀린다.
"""
from __future__ import annotations

import ast
import sys
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO / "docs" / "22p_gap") not in sys.path:
    sys.path.insert(0, str(REPO / "docs" / "22p_gap"))


def _rp():
    import row_projection as rp

    return rp


def _shadow_map(node):
    return {id(n): sh for n, sh in _rp()._scoped_shadows(node)}


_LEAK = textwrap.dedent('''
    value = "GLOBAL"

    def f():
        xs = [value for value in ("A", "B")]
        return value
''')


def test_python_really_does_not_leak_the_comprehension_target():
    """★ P1-4 — 먼저 **Python 이 실제로 무엇을 하는지** 고정한다.

    분석기를 고치기 전에 진실을 박아 둔다. 이 시험이 깨지면 그때는 Python 이
    바뀐 것이고, 규칙을 다시 읽어야 한다.
    """
    ns: dict = {}
    exec(compile(_LEAK, "<leak>", "exec"), ns)          # noqa: S102
    assert ns["f"]() == "GLOBAL", (
        "comprehension target 이 바깥으로 샜다 — 이 시험의 전제가 틀렸다")


def test_the_analyzer_does_not_shadow_the_enclosing_scope(monkeypatch):
    """★ P1-4 — 분석기의 shadow 집합이 Python 과 같아야 한다.

    리뷰어 실측: `analyzer_shadow_set_at_return: ["value", "xs"]`.
    `value` 는 comprehension 안에서만 묶이므로 `return value` 자리에는 없어야
    한다 (`xs` 는 평범한 대입이라 애초에 shadow 가 아니다).
    """
    tree = ast.parse(_LEAK)
    fn = tree.body[1]
    ret = fn.body[1].value                      # `return value` 의 Name
    got = _shadow_map(fn)[id(ret)]
    assert "value" not in got, (
        f"바깥 scope 의 load 가 comprehension target 으로 가려졌다: "
        f"{sorted(got)} — 분석기가 Python 과 반대를 말한다 (61차 P1-4)")


def test_the_target_is_still_shadowed_inside_the_comprehension():
    """★ 반대 방향 — comprehension **안에서는** 그대로 가린다.

    거부가 넓어지는 것만큼 면제가 사라지는 것도 결함이다. 60차 M17 의 완화가
    comprehension 안에서 죽으면 정상 코드가 막힌다.
    """
    tree = ast.parse(_LEAK)
    fn = tree.body[1]
    comp = fn.body[0].value                     # ListComp
    elt = comp.elt                              # 그 안의 `value`
    got = _shadow_map(fn)[id(elt)]
    assert "value" in got, (
        f"comprehension 안의 target 이 안 가려진다: {sorted(got)}")


def test_the_outermost_iterable_is_evaluated_in_the_enclosing_scope():
    """★ P1-4 의 정확한 경계 — **가장 바깥 iterable 은 바깥에서 평가된다.**

    규칙을 통째로 "comprehension 은 자식 scope" 로 옮기면 이 자리가 반대로
    틀린다. Python 은 첫 generator 의 `iter` 만 바깥 scope 에서 계산한다.
    """
    src = textwrap.dedent('''
        def f(items):
            return [items for items in items]
    ''')
    tree = ast.parse(src)
    fn = tree.body[0]
    comp = fn.body[0].value
    outer_iter = comp.generators[0].iter        # 바깥에서 평가되는 `items`
    elt = comp.elt                              # 안에서 평가되는 `items`
    m = _shadow_map(fn)
    assert "items" in m[id(outer_iter)], (
        "가장 바깥 iterable 은 함수 매개변수 `items` 를 본다 — 그 자리의 "
        "shadow 에 매개변수가 있어야 한다")
    assert "items" in m[id(elt)], "comprehension 안은 target 이 가린다"


def test_a_comprehension_target_does_not_exempt_an_outer_capability():
    """★ P1-4 의 보안 결과 — 이것이 이 결함이 위험한 이유다.

    comprehension target 하나로 바깥의 능력 호출이 면제되면, 59차 M17 의
    완화가 다시 우회로가 된다. 실제 producer 승인 경로에서 확인한다.
    """
    import pytest

    rp = _rp()
    base = (
        "import src.scoring as sc\n"
        "def _cell(x):\n    return x\n"
        "def _restart_list(x):\n    return x\n"
        "def _restart_facts(x):\n    return x\n"
        "def _add_multistart_blocks(x):\n    return x\n"
        "def _analyzer_provenance(x):\n    return x\n"
        "def build(x):\n    return x\n"
    ) + "".join(f"def {n}(*a, **k):\n    return None\n"
                for n in rp._PRODUCER_CUT)
    inject = ("def score_canonical(df):\n"
              "    _ = [getattr for getattr in ()]\n"
              "    return getattr(sc, 'add_error_columns')(df)\n")
    scoring = (REPO / "src" / "scoring.py").read_text(encoding="utf-8")
    with pytest.raises(SystemExit) as ei:
        rp._producer_semantic_over(base + inject, scoring)
    assert "능력" in str(ei.value) or "이름 공간" in str(ei.value), ei.value
