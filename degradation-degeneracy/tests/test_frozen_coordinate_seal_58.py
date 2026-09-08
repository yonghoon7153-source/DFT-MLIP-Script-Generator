"""58차 L5 — frozen tree 의 좌표를 **freeze 시점에 봉인**한다.

리뷰어 반례를 실물 mount 로 재현했다:

    가린 이름 수                     1
    guard                            PASSED        ← 통과하면 안 된다
    덮개 걷은 뒤 frozen child 안에?  true

`_assert_writable()` 의 마지막 층은 "이 좌표를 보여 주는 **이름**을 찾아 그
안의 marker 를 읽는다" 이다. 그런데 frozen root 를 가리키는 이름을 무해한
bind 로 덮으면 **후보가 진짜로 없어진다** — 예외가 나는 게 아니다. 그래서
`_names_for()` 의 예외 삼킴(`except (OSError, SystemExit): continue`)을 고쳐도
이 반례는 안 막힌다. 그 수정은 별개로 필요하지만 충분하지 않다.

`[해석]` **물음이 틀렸다.** "지금 이 좌표를 볼 수 있는 이름이 있는가" 는
공격자가 mount 로 바꿀 수 있는 질문이다. 바꿀 수 없는 질문은 **"우리가 얼릴
때 적어 둔 좌표 아래인가"** 다. 얼리는 순간의 `(major:minor, filesystem 안의
경로)` 를 원장 옆에 봉인해 두면, 그 뒤로 이름이 몇 겹으로 덮이든 판정이
안 바뀐다 — 조회에 이름이 안 들어가기 때문이다.

L4 에서 커널 좌표 helper 를 `tools/preserve.py` 로 옮긴 것이 여기서 값을 한다:
smoke containment 와 frozen guard 가 **같은 좌표 함수**를 쓴다.
"""
from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

import tools.preserve as P

REPO = Path(__file__).resolve().parent.parent


def _can_bind_mount() -> bool:
    try:
        return subprocess.run(["unshare", "-Urnm", "true"],
                              capture_output=True, timeout=20).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def test_a_sealed_coordinate_covers_descendants(tmp_path):
    """★ 봉인은 자손까지 덮는다 — `frozen/child` 도 못 쓴다.

    28차 P1-5 가 exact equality 만 보다 놓친 축이다. 좌표 봉인에서도 같은
    성질이 성립해야 한다.
    """
    led = tmp_path / "authority" / "LEG_PRESERVATION.yaml"
    led.parent.mkdir(parents=True)
    led.write_text("planned: []\nlegs: []\n", encoding="utf-8")

    frozen = tmp_path / "gA"
    (frozen / "child" / "deep").mkdir(parents=True)
    P.record_frozen_coordinate(frozen, "gA", ledger=led)

    assert P.frozen_coordinate_covering(frozen, ledger=led) == "gA"
    assert P.frozen_coordinate_covering(frozen / "child", ledger=led) == "gA"
    assert P.frozen_coordinate_covering(frozen / "child" / "deep",
                                        ledger=led) == "gA"


def test_the_seal_is_not_invariant_under_rename__a_recorded_limit(tmp_path):
    """★ **한계를 시험으로 못 박는다** — 좌표 봉인은 `mv` 에 불변이 **아니다**.

    처음에 이 파일은 "이름을 바꿔도 답이 같다" 를 단언했다. **틀렸다.**
    실측으로 뒤집혔다:

        rename 전  ('254:0', .../gA)
        rename 후  ('254:0', .../gA-renamed)

    `_fs_identity()` 의 둘째 항은 **그 filesystem 안의 경로**이고, 경로는 곧
    이름이다. 그러므로 이 좌표가 불변인 것은 **같은 대상을 어떤 창(mount·bind·
    symlink)으로 보는가** 에 대해서이지, **대상을 옮기는 것**에 대해서가 아니다.
    L5 가 막는 것은 전자다.

    남는 구멍: frozen 디렉터리 자체를 `mv` 하면 좌표 봉인이 그 자손을 더는
    안 덮는다 (`.FROZEN` marker 는 tree 안에 남지만 `_assert_writable()` 의
    첫 층은 목적지 **자신**만 본다). 이 시험은 그 사실을 **고정**해 둔다 —
    나중에 누가 "좌표 봉인이 rename 도 막는다" 고 믿지 않도록.

    제대로 닫으려면 좌표가 아니라 **파일 handle 급 identity**(예: 재부팅에도
    살아남는 fsid + inode 계보)가 필요하고, 그것은 이 라운드의 범위 밖이다.
    요청문에 남은 한계로 적는다.
    """
    led = tmp_path / "authority" / "LEG_PRESERVATION.yaml"
    led.parent.mkdir(parents=True)
    led.write_text("planned: []\nlegs: []\n", encoding="utf-8")

    frozen = tmp_path / "gA"
    (frozen / "child").mkdir(parents=True)
    P.record_frozen_coordinate(frozen, "gA", ledger=led)
    assert P.frozen_coordinate_covering(frozen / "child", ledger=led) == "gA"

    renamed = tmp_path / "gA-renamed"
    frozen.rename(renamed)
    assert P.frozen_coordinate_covering(renamed / "child", ledger=led) is None, (
        "좌표 봉인이 rename 을 견뎠다 — 그렇다면 이 시험의 전제(좌표 = "
        "filesystem 안의 경로)가 바뀐 것이므로 위 서술을 다시 써야 한다")


def test_an_unrelated_directory_is_not_covered(tmp_path):
    """봉인이 **넓게** 걸리면 안 된다 — 무관한 자리는 여전히 쓸 수 있어야 한다."""
    led = tmp_path / "authority" / "LEG_PRESERVATION.yaml"
    led.parent.mkdir(parents=True)
    led.write_text("planned: []\nlegs: []\n", encoding="utf-8")

    frozen = tmp_path / "gA"
    frozen.mkdir()
    other = tmp_path / "gB"
    other.mkdir()
    P.record_frozen_coordinate(frozen, "gA", ledger=led)

    assert P.frozen_coordinate_covering(other, ledger=led) is None


_PROBE = r'''
import json, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1])
sys.path.insert(0, str(Path(sys.argv[1]) / "docs" / "22p_gap"))
import tools.preserve as P
import row_projection as R

tmp = Path(tempfile.mkdtemp(prefix="l5-"))
led = tmp / "authority" / "LEG_PRESERVATION.yaml"
led.parent.mkdir(parents=True)
led.write_text("planned: []\nlegs: []\n", encoding="utf-8")
P.canonical_ledger = lambda x=None: led

frozen = tmp / "frozen"; child = frozen / "child"; child.mkdir(parents=True)
R._write_frozen_marker(frozen, "gFROZEN", "tip0")     # ← 여기서 좌표가 봉인된다

alias = tmp / "active-alias"; alias.mkdir()
subprocess.run(["mount", "--bind", str(child), str(alias)], check=True)

# frozen root 를 가리키는 **모든 이름**을 무해한 bind 로 덮는다
dev, fs = P._fs_identity(frozen)
cover = tmp / "benign"; cover.mkdir()
hidden = []
for n in P._names_for(dev, fs, P._mount_table()):
    try:
        subprocess.run(["mount", "--bind", str(cover), str(n)], check=True)
        hidden.append(str(n))
    except subprocess.CalledProcessError:
        pass

guard = "PASSED"
try:
    R._assert_writable(alias)
except BaseException as exc:
    guard = "REFUSED"
print(json.dumps({"hidden": len(hidden), "guard": guard}))
'''


@pytest.mark.skipif(not _can_bind_mount(),
                    reason="user+mount namespace 를 못 만든다 — mount 축 미검증")
def test_hiding_every_name_of_a_frozen_ancestor_does_not_make_it_writable():
    """★ L5 — frozen 조상의 이름을 **전부 덮어도** 자식은 쓸 수 없다."""
    r = subprocess.run(["unshare", "-Urnm", sys.executable, "-c",
                        textwrap.dedent(_PROBE), str(REPO)],
                       capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, f"재현기가 죽었다:\n{r.stdout}\n{r.stderr}"
    got = json.loads(r.stdout.strip().splitlines()[-1])
    assert got["hidden"] >= 1, "이름을 하나도 못 덮었다 — 시험 전제가 깨졌다"
    assert got["guard"] == "REFUSED", (
        "frozen 조상의 이름을 덮었더니 guard 가 통과했다 — 판정이 "
        "'지금 볼 수 있는 이름' 에 의존한다 (L5)")


def test_names_for_does_not_swallow_a_refusal():
    """★ L5 의 둘째 절반 — "답할 수 없다" 를 "후보 없음" 으로 바꾸지 않는다.

    `_names_for()` 는 `except (OSError, SystemExit): continue` 였다. 그 둘은
    좌표를 **못 밝히겠다** 는 fail-closed 신호인데, 그것을 후보 부재로 번역하면
    호출자는 "안전하다" 로 읽는다. 정확히 반대다.

    ★ 59차 P1-4 — 이 시험은 처음에 `dev` 를 `"254:0"` 으로 **하드코딩**했다.
      이 기계에는 그 장치가 있어서 후보가 하나 잡혔지만, 리뷰어 기계에는 없어서
      후보 loop 가 한 번도 안 돌았다. 그러면 monkeypatch 한 `_kernel_mount_id`
      가 **0회 호출**되고 기대한 `BoundaryUnknown` 이 안 난다 (리뷰어 실측:
      `1 failed`). 이름이 약속한 축을 실행하지 않는 시험 — L13 이 지적한 바로
      그 형태를 내 새 시험이 되풀이했다.

      그래서 좌표를 **현재 mount table 에서 유도**하고, 후보가 실제로 하나
      이상임을 **먼저 단언**한다. 전제가 깨지면 그 사실이 보인다.
    """
    table = P._mount_table()
    dev, fs = P._fs_identity(Path("/tmp"))
    candidates = P._names_for(dev, fs, table)
    assert candidates, (
        f"이 기계에서 /tmp 의 좌표 {dev}:{fs} 에 이름 후보가 없다 — "
        "시험 전제가 깨졌다 (그러면 아래 단언은 아무것도 증명하지 않는다)")

    def _boom(*a, **k):
        raise P.BoundaryUnknown("boundary", "좌표를 못 밝힌다")

    orig = P._kernel_mount_id
    P._kernel_mount_id = _boom
    try:
        with pytest.raises(P.BoundaryUnknown):
            P._names_for(dev, fs, table)
    finally:
        P._kernel_mount_id = orig
