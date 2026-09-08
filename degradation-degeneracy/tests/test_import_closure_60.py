"""60차 θ (P1-3·P1-4) — **증언이 재는 것은 상태이지 이력이 아니다.**

리뷰어 반례 둘.

    P1-3  고정된 `sitecustomize.py` 가 payload 를 import 해 builtins 에 값을
          남긴 뒤 `sys.modules` 에서 payload 만 지운다. payload 바이트를
          `ALPHA → OMEGA` 로 바꿔도:
          `payload_in_startup_modules:false · receipt_equal:true ·
           environment_tag_equal:true` 인데 `runtime ALPHA → OMEGA`

    P1-4  같은 `PYTHONPATH` 자리의 평범한 module 바이트를 `FIRST → OTHER` 로
          바꾸고 **probe 뒤에** import 한다. 역시 receipt 도 tag 도 그대로다.

`[해석]` 59차 M14 는 "이름 세 개를 세는 대신 `sys.modules` 를 통째로 잰다" 로
갔다. 그런데 `sys.modules` 는 **그 순간의 상태**이고, 실행이 무엇을 올렸다
지웠는지의 **이력**이 아니다. 그리고 그 순간 이후에 올라오는 것도 안 담는다.

그러므로 재는 것을 둘 더한다.

  ① **import 이력** — `-X importtime` 은 인터프리터가 startup 에 실제로 import
     한 module 을 전부 찍는다 (그 뒤 `sys.modules` 에서 지워도 로그에는 남는다).
  ② **import 가능한 뿌리의 바이트** — `PYTHONPATH` 가 가리키는 자리의 module
     내용을 봉인한다. "그 문자열 아래 무엇이 있는가" 를 문자열이 아니라
     바이트로 답한다.

**남는 한계**는 그대로 적는다: 이것도 "실행이 실제로 소비한 바이트 전부" 는
아니다. 그 종결은 독립 replay 이고 이 라운드의 범위 밖이다.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
if str(REPO / "docs" / "22p_gap") not in sys.path:
    sys.path.insert(0, str(REPO / "docs" / "22p_gap"))


def _mr():
    import mutation_replay as mr

    return mr


def _receipt_in(root: Path, extra_env: dict) -> dict:
    """`root` 를 cwd 로, 주어진 환경에서 영수증을 한 번 잰다."""
    mr = _mr()
    src = mr._ENV_PROBE_BODY + (
        "\nimport json\n"
        "print(json.dumps(_receipt_facts([], [], %r), sort_keys=True, "
        "ensure_ascii=False))\n" % str(root))
    env = dict(os.environ)
    env.update(extra_env)
    r = subprocess.run([sys.executable, "-c", src], cwd=root, env=env,
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr[-2000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


@pytest.fixture
def sandbox(tmp_path):
    """`sitecustomize` 가 payload 를 올렸다 지우는 startup 한 벌."""
    site = tmp_path / "site"
    site.mkdir()
    (site / "sitecustomize.py").write_text(textwrap.dedent('''
        import sys
        import _payload
        import builtins
        builtins._LEFT_BEHIND = _payload.VALUE
        del sys.modules["_payload"]          # 흔적을 지운다
    '''), encoding="utf-8")
    return tmp_path, site


def _write_payload(site: Path, value: str) -> None:
    (site / "_payload.py").write_text(f"VALUE = {value!r}\n", encoding="utf-8")


# ── P1-3 ──────────────────────────────────────────────────────────────────
def test_a_module_that_startup_loaded_and_dropped_is_still_measured(sandbox):
    """★ P1-3 — 올렸다 **지운** module 의 바이트가 증언에 들어가야 한다.

    `sys.modules` snapshot 은 그 순간의 상태다. `sitecustomize` 가 값을
    builtins 에 남기고 자기 흔적을 지우면, 그 payload 는 상태에 없지만
    **실행에는 있었다.**
    """
    root, site = sandbox
    env = {"PYTHONPATH": str(site)}

    _write_payload(site, "ALPHA")
    a = _receipt_in(root, env)
    _write_payload(site, "OMEGA")
    b = _receipt_in(root, env)

    assert a != b, (
        "startup 이 올렸다 지운 module 의 바이트를 바꿨는데 영수증이 그대로다 "
        "— 증언이 상태만 보고 이력을 안 본다 (P1-3)")


def test_the_environment_tag_moves_with_that_history(sandbox):
    """★ P1-3 — tag 도 같이 움직인다 (영수증 전체를 해시하므로)."""
    mr = _mr()
    root, site = sandbox
    env = {"PYTHONPATH": str(site)}

    _write_payload(site, "ALPHA")
    ta = mr.environment_tag(_receipt_in(root, env))
    _write_payload(site, "OMEGA")
    tb = mr.environment_tag(_receipt_in(root, env))
    assert ta != tb, "영수증은 움직였는데 tag 가 그대로다 (P1-3)"


def test_a_dropped_submodule_is_measured_by_the_history(tmp_path):
    """★ P1-3 — **이력만이** 잡는 자리.

    위 두 시험은 payload 를 `PYTHONPATH` 의 **최상위** module 로 두는데, 그
    자리는 P1-4 의 `importable_roots` 도 본다. 그래서 이력 층을 통째로 지워도
    두 시험은 안 빨개진다 — 층이 둘인 것은 좋지만, 그러면 이력 층은 **자기
    증인이 없다.** 이 저장소는 그 상태를 이번 라운드에만 세 번 실측했다.

    세 층이 갈라지는 자리를 겨눈다: package 의 **하위** module 을 startup 에서
    올린 뒤 `sys.modules` 에서 지운다.

      · `importable_roots` — `PYTHONPATH` 자리의 **최상위**만 해시한다
        (`pkg/__init__.py` 는 담지만 `pkg/sub.py` 는 안 담는다) → 못 본다.
      · `startup_modules` — 지워졌다 → 못 본다.
      · `startup_history` — importtime 이 `pkg.sub` 를 찍고 `find_spec` 이
        그 이름을 푼다 → **이것만 본다.**
    """
    root = tmp_path / "root"
    root.mkdir()
    site = tmp_path / "site"
    pkg = site / "pkg"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (site / "sitecustomize.py").write_text(textwrap.dedent('''
        import sys
        import pkg.sub
        import builtins
        builtins._LEFT_BEHIND = pkg.sub.VALUE
        del sys.modules["pkg.sub"]           # 흔적을 지운다
    '''), encoding="utf-8")
    env = {"PYTHONPATH": str(site)}

    (pkg / "sub.py").write_text("VALUE = 'ALPHA'\n", encoding="utf-8")
    a = _receipt_in(root, env)
    (pkg / "sub.py").write_text("VALUE = 'OMEGA'\n", encoding="utf-8")
    b = _receipt_in(root, env)

    assert a != b, (
        "startup 이 올렸다 지운 **하위** module 의 바이트를 바꿨는데 영수증이 "
        "그대로다 — 최상위만 보는 층도 상태만 보는 층도 이것을 못 본다. "
        "이력을 재는 층만이 잡는 자리다 (P1-3)")


# ── P1-4 ──────────────────────────────────────────────────────────────────
def test_a_module_imported_after_startup_is_inside_the_receipt(tmp_path):
    """★ P1-4 — startup **뒤에** import 되는 바이트도 담아야 한다.

    59차 영수증은 `PYTHONPATH` 를 **문자열로** 담았다. 같은 문자열 아래 파일
    내용을 바꾸면 실행은 달라지는데 영수증은 그대로다 (리뷰어 실측:
    `FIRST → OTHER`).

    담는 방법: 그 자리의 module 바이트를 봉인한다 — "그 문자열 아래 무엇이
    있는가" 를 문자열이 아니라 바이트로 답한다.
    """
    root = tmp_path / "root"
    root.mkdir()
    lib = tmp_path / "lib"
    lib.mkdir()
    env = {"PYTHONPATH": str(lib)}

    (lib / "_late.py").write_text("VALUE = 'FIRST'\n", encoding="utf-8")
    a = _receipt_in(root, env)
    (lib / "_late.py").write_text("VALUE = 'OTHER'\n", encoding="utf-8")
    b = _receipt_in(root, env)

    assert a != b, (
        "PYTHONPATH 자리의 module 바이트를 바꿨는데 영수증이 그대로다 — "
        "문자열만 담고 그것이 가리키는 바이트를 안 담았다 (P1-4)")


def test_an_unrelated_change_does_not_move_the_receipt(tmp_path):
    """★ 반대 방향 — 무관한 변화까지 담으면 증언이 쓸모없어진다.

    영수증이 아무 때나 움직이면 "환경이 같다" 는 말을 할 수 없게 되고, 그러면
    이 층은 경계가 아니라 잡음이다.
    """
    root = tmp_path / "root"
    root.mkdir()
    lib = tmp_path / "lib"
    lib.mkdir()
    env = {"PYTHONPATH": str(lib)}
    (lib / "_late.py").write_text("VALUE = 'FIRST'\n", encoding="utf-8")

    a = _receipt_in(root, env)
    (root / "무관한파일.txt").write_text("아무거나\n", encoding="utf-8")
    b = _receipt_in(root, env)
    assert a == b, "무관한 파일 하나에 영수증이 움직였다"
