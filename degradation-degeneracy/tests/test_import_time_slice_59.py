"""59차 δ (M11·M12·M17) — producer identity 를 **실행 의미**로.

리뷰어의 세 반례:

    M11  능력의 대상(module)을 **식으로 한 겹 감싸면** 거부가 안 온다.
         `getattr([sc][0], "add_error_columns")` — 대상 검사가 벌거벗은
         `ast.Name` 만 알아본다.
    M12  import 시 실행 모델이 `assert` · metaclass · `from __future__ import
         annotations` 를 버린다. module scope 의 `assert sc.무엇()` 은 import
         때 **실행되는데** `_MODULE_NONBINDING` 이라 통째로 건너뛴다.
    M17  능력 escape 규칙이 무해한 지역 그림자도 거부한다 (Q1 의 답: 그렇다).

`[해석]` 57·58차는 **AST 종류를 하나씩 더해** 이 축을 두 번 닫으려 했고 두 번
거절당했다. 종류를 세는 한 다음 종류가 남는다. 그래서 이 라운드는 물음을
뒤집는다: module initialization 이 **무엇을 실행하는가** 를 기본값으로 두고,
**실행되지 않음을 증명할 수 있는 것만** 뺀다. 증명할 수 없으면 fail-closed.

능력 대상도 같다 — "이것이 module 이다" 를 알아보는 대신 **"이것이 module 이
아님을 증명할 수 있는가"** 를 묻는다.
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
    """닫힘이 요구하는 이름을 다 갖춘 최소 producer 소스 (58차 시험과 같다)."""
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


# ── M11 ───────────────────────────────────────────────────────────────────
#: 능력의 **대상을 한 겹 감싸는** 방법들. 전부 같은 계산(`sc` 의 이름 공간을
#: 연다)이고, 전부 벌거벗은 `Name` 이 아니다.
_WRAPPED_TARGETS = {
    "list_index":   "[sc][0]",
    "tuple_index":  "(sc,)[0]",
    "conditional":  "(sc if True else sc)",
    "dict_value":   "{'m': sc}['m']",
    "identity_call": "(lambda m: m)(sc)",
    "or_chain":     "(None or sc)",
}


@pytest.mark.parametrize("how", sorted(_WRAPPED_TARGETS))
def test_wrapping_the_capability_target_does_not_escape(how):
    """★ M11 — 대상을 식으로 감싸도 **이름 공간을 여는 것은 같다**.

    58차 대상 검사는 `isinstance(first, ast.Name) and first.id in mods` 였다.
    한 겹만 감싸면 그 조건이 거짓이 되고, 능력은 그대로 `sc` 의 이름 공간을
    연다. 종류를 세는 검사의 전형적인 실패다.

    그러므로 묻는 것을 뒤집는다: **이 대상이 module 이 아님을 증명할 수 있는가.**
    못 하면 거부다 — 위 여섯은 전부 증명할 수 없는 형태다.
    """
    rp = _rp()
    inject = ("def score_canonical(df):\n"
              f"    return getattr({_WRAPPED_TARGETS[how]}, "
              "'add_error_columns')(df)\n")
    with pytest.raises(SystemExit) as ei:
        rp._producer_semantic_over(_base(rp) + inject, _scoring())
    assert "이름 공간" in str(ei.value) or "증명" in str(ei.value), ei.value


def test_reading_a_plain_object_attribute_is_still_allowed():
    """★ M11 의 반대 방향 — 평범한 속성 읽기까지 막으면 마비다.

    이 파일의 정규형 함수들이 실제로 `getattr(node, f, None)` 을 쓴다. 경계는
    "이름 공간을 여는가" 이지 "`getattr` 을 쓰는가" 가 아니다.
    """
    rp = _rp()
    inject = ("def score_canonical(df):\n"
              "    return getattr(df, 'columns', None)\n")
    rp._producer_semantic_over(_base(rp) + inject, _scoring())   # 예외 없음


# ── M12 ───────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("inject", [
    # ① module scope 의 `assert` — 조건식이 import 때 **실행된다**.
    #    `_MODULE_NONBINDING` 에 있어 통째로 건너뛰었다.
    "assert sc.add_error_columns is not None\n",
    # ② `assert` 의 메시지도 실행된다 (조건이 거짓일 때만이지만, 그 조건을
    #    정하는 것도 이 문장이다 — 문장 전체가 실행 슬라이스 안이다).
    "assert True, str(sc.add_error_columns)\n",
    # ③ metaclass — 이름 하나여도 class 생성 때 **호출된다**. 데코레이터와
    #    같은 종류의 치환인데 58차는 데코레이터만 무조건 묶었다.
    "class _Meta(type):\n    pass\n"
    "class _WithMeta(metaclass=_Meta):\n    pass\n",
    # ④ base 도 이름 하나면 계산으로 안 셌다 — 그런데 class 생성은 base 의
    #    `__init_subclass__`/`__set_name__` 를 부른다.
    "class _Base:\n    pass\n"
    "class _Derived(_Base):\n    pass\n",
    # ⑤ module scope 의 `raise` 는 실행 흐름을 정한다 (뒤 문장이 안 돈다).
    "if False:\n    raise RuntimeError(str(sc.add_error_columns))\n",
])
def test_the_import_time_slice_contains_everything_that_runs(inject):
    """★ M12 — import 때 도는 문장을 더했는데 digest 가 그대로면 안 된다.

    58차 시험(`test_import_time_execution_is_inside_the_identity__58`)과 같은
    형태이고, 리뷰어가 든 세 축(`assert`·metaclass·future flag)을 더한다.
    거부도 정답이다 — 볼 수 없으면 막는 것이 이 규칙이기 때문이다.
    """
    rp = _rp()
    sc = _scoring()
    base = _base(rp)
    d0 = rp._producer_semantic_over(base, sc)
    try:
        d1 = rp._producer_semantic_over(base + inject, sc)
    except SystemExit:
        return
    assert d0 != d1, (
        "import 때 실행되는 문장을 더했는데 producer digest 가 그대로다 — "
        "그 실행은 봉인 밖이다 (59차 M12)")


def test_a_metaclass_body_change_moves_the_identity():
    """★ M12 — metaclass **구현**이 바뀌면 digest 가 움직여야 한다.

    "노드를 더하면 바뀐다" 만으로는 부족하다 (58차가 데코레이터에서 배운 것과
    같다). metaclass 는 class 객체를 만드는 주체이므로 그 구현이 계산 의미를
    정한다.
    """
    rp = _rp()
    sc = _scoring()
    a = ("class _Meta(type):\n"
         "    def __call__(cls, *a, **k):\n        return 1\n"
         "class _C(metaclass=_Meta):\n    pass\n")
    b = ("class _Meta(type):\n"
         "    def __call__(cls, *a, **k):\n        return 9\n"
         "class _C(metaclass=_Meta):\n    pass\n")
    base = _base(rp)
    assert rp._producer_semantic_over(base + a, sc) \
        != rp._producer_semantic_over(base + b, sc), (
        "metaclass 구현을 바꿨는데 producer digest 가 같다 (59차 M12)")


def test_the_future_annotations_flag_is_part_of_the_model():
    """★ M12 — `from __future__ import annotations` 는 **의미를 바꾼다**.

    그 flag 가 있으면 annotation 은 import 때 평가되지 않고, 없으면 평가된다.
    우리 모델은 "annotation 이 import 때 돈다" 를 전제로 규칙을 세웠으면서
    그 전제를 뒤집는 한 줄을 읽지 않았다.

    어느 쪽으로 처리하든 좋지만 **모델이 그 줄을 알기는 해야** 한다. 여기서는
    가장 값싼 방식으로 확인한다: 그 줄이 있고 없고가 producer identity 를
    바꾼다 (그 줄이 이 module 의 실행 의미를 바꾸기 때문이다).
    """
    rp = _rp()
    sc = _scoring()
    base = _base(rp)
    with_flag = "from __future__ import annotations\n" + base
    assert rp._producer_semantic_over(base, sc) \
        != rp._producer_semantic_over(with_flag, sc), (
        "`from __future__ import annotations` 를 더했는데 producer digest 가 "
        "그대로다 — 모델이 annotation 평가 의미를 바꾸는 줄을 안 본다 (M12)")


# ── M17 ───────────────────────────────────────────────────────────────────
def test_a_local_name_that_merely_shares_a_spelling_is_not_a_capability():
    """★ M17 — 능력 escape 규칙이 **무해한 그림자**까지 거부한다.

    규칙은 "능력이 부르는 자리 밖에 Load 로 나타나면 거부" 인데, 판정을
    **철자**로 한다. 그래서 능력과 철자만 같은 지역 이름(매개변수·지역 변수)
    이나 남의 객체 속성(`obj.vars`)도 걸린다.

    리뷰어의 Q1 이 물은 것이 이것이고 답은 "그렇다" 였다. 방어를 약하게 하지
    않으면서 정밀도를 올린다:

      · **매개변수·루프/with/except 대상**으로 묶인 이름은 능력이 아니다. 그
        값은 호출자가 준다 — 호출자가 진짜 능력을 넘기려면 자기 자리에서
        능력을 부르는 자리 **밖**에 쓰게 되고 거기서 걸린다.
      · **속성 접근**은 뿌리가 import 한 module 일 때만 능력이다
        (`operator.attrgetter`). 남의 객체의 `.vars` 는 그냥 속성이다.

    평범한 대입(`GET = getattr`)은 **여전히 거부한다** — 58차 L9-b 가 닫은
    축이고, 값을 모르는 대입을 열어 주면 그 구멍으로 되돌아간다.

    ★ 이 시험은 닫힘이 **실제로 훑는 함수** 안에 그림자를 둔다. 아무도 안 부르는
      함수에 두면 규칙이 그 노드에 닿지 않아 시험이 초록으로 지나간다 (처음 판이
      그랬다 — 이름이 약속한 축을 실행하지 않는 시험, 59차 M16 과 같은 형태).
    """
    rp = _rp()
    sc = _scoring()
    base = _base(rp)

    # ① 매개변수가 능력과 철자만 같다 (계산 경로 안에서)
    shadow_param = ("def score_canonical(df, vars=None):\n"
                    "    return df if vars is None else df\n")
    # ② 남의 객체 속성이 철자만 같다
    shadow_attr = ("def score_canonical(df):\n"
                   "    return df.vars\n")
    for inject in (shadow_param, shadow_attr):
        rp._producer_semantic_over(base + inject, sc)      # 예외가 없어야 한다


def test_the_escape_rule_still_refuses_a_real_alias():
    """★ M17 — 정밀도를 올리면서 **방어는 그대로**여야 한다.

    58차 L9-b 가 닫은 축(함수 지역 별칭)이 M17 수정 뒤에도 여전히 거부돼야
    한다. 이것이 없으면 "정밀도" 라는 이름으로 방어를 지운 것이다.
    """
    rp = _rp()
    inject = ("def score_canonical(df):\n"
              "    GET = getattr\n"
              "    return GET(sc, 'add_error_columns')(df)\n")
    with pytest.raises(SystemExit):
        rp._producer_semantic_over(_base(rp) + inject, _scoring())
