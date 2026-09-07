"""58차 L4 — smoke containment 를 **커널 좌표**로 묻는다.

`is_inside_namespace()` 는 어휘(`..`)와 symlink 만 본다. bind mount 는 symlink 가
아니므로 그 검사를 통과한다. 리뷰어가 실물 mount 로 재현했고 우리도 재현했다:

    is_inside_namespace   true          ← smoke 안이라고 판정
    계획 gate             통과(면제)
    쓴 것이 밖에 떨어졌나 true
    같은 디렉터리인가      true

`[해석]` 47차가 어휘 gate 를 실물 gate 로 바꾼 것과 **같은 종류의 수정**이
한 번 더 필요하다. 그때는 symlink 를 봤고, 이번엔 mount 를 본다. 금지 목록을
늘리는 대신 **물음을 바꾼다** — publisher guard 가 이미 쓰는 커널 좌표
(`(major:minor, filesystem 안의 경로)`)로 담김을 판정한다. 그 좌표는 bind·겹침·
이름 변경에 불변이므로 "어떤 이름으로 왔는가" 를 더 물을 필요가 없다.

이 시험은 **실제 `mount --bind`** 를 쓴다. mount 를 만들 수 없는 환경에서는
skip 한다 — 그 경우 이 축은 검증되지 않았다는 뜻이고, 조용히 통과시키지 않는다.
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


def _can_bind_mount() -> bool:
    try:
        r = subprocess.run(["unshare", "-Urnm", "true"],
                           capture_output=True, timeout=20)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


pytestmark = pytest.mark.skipif(
    not _can_bind_mount(),
    reason="이 환경에서는 user+mount namespace 를 못 만든다 — mount 축 미검증")


_PROBE = r'''
import json, os, sys, tempfile, subprocess
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import tools.preserve as P

tmp = Path(tempfile.mkdtemp(prefix="l4-"))
# SMOKE_NAMESPACE 는 저장소 루트에서 유도한 절대경로다. `tmp / 그것` 은 tmp 를
# 버린다(pathlib 흡수) — 그러면 재현기가 실제 저장소에 쓴다. tmp 로 옮긴다.
P.SMOKE_NAMESPACE = tmp / "results" / "_smoke"
alias = P.SMOKE_NAMESPACE / "alias"
outside = tmp / "canonical-outside"
alias.mkdir(parents=True); outside.mkdir()
subprocess.run(["mount", "--bind", str(outside), str(alias)], check=True)

target = alias / "unplanned-run"
os.chdir(tmp)
led = tmp / "LEG_PRESERVATION.yaml"
led.write_text("planned: []\nlegs: []\n", encoding="utf-8")

inside = P.is_inside_namespace(target, P.SMOKE_NAMESPACE)
try:
    P.assert_run_is_authorized("unplanned", "grid", [target], {"x": 1},
                               "deadbeef", ledger=led)
    gate = "exempted"
except P.PreserveError:
    gate = "refused"
except SystemExit as exc:
    gate = "refused-fail-closed:" + str(exc)[:40]
print(json.dumps({"inside": inside, "gate": gate}))
'''


def _run_in_namespace() -> dict:
    r = subprocess.run(["unshare", "-Urnm", sys.executable, "-c",
                        textwrap.dedent(_PROBE), str(REPO)],
                       capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, f"재현기가 죽었다:\n{r.stdout}\n{r.stderr}"
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_a_bind_mounted_outside_directory_is_not_inside_the_smoke_namespace():
    """★ L4 — bind mount 로 들여온 외부 디렉터리는 smoke 안이 아니다."""
    got = _run_in_namespace()
    assert got["inside"] is False, (
        "bind mount 한 외부 디렉터리를 smoke namespace 안이라고 판정했다 — "
        "어휘·symlink 만 보고 mount 를 안 본다 (L4)")


def test_an_unplanned_leg_under_a_bind_alias_is_not_exempted():
    """★ L4 — 그러므로 계획에 없는 다리가 **면제받지 못한다**.

    판정 함수만 고치고 gate 가 여전히 통과하면 아무것도 안 고친 것이다.
    top-level consumer 를 부른다.
    """
    got = _run_in_namespace()
    assert got["gate"].startswith("refused"), (
        f"계획에 없는 다리가 bind alias 아래에서 면제받았다 ({got['gate']}) — "
        "smoke 면제가 실물 경계를 안 본다 (L4)")
