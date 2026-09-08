"""59차 γ (M2·M7) — **내용 identity 와 phase 결속을 production schema 에서 유도한다.**

리뷰어의 두 반례:

    M2  `_EXEC_ID_MANIFESTS` 는 `curves/fits/manifest.yaml` 인데 production 이
        쓰는 것은 `curves_manifest_start.yaml`·`manifest_start.yaml` 이다.
        `fits_manifest.yaml` 은 **쓰는 곳이 저장소에 없다.** 그래서 시작
        manifest 만 다른 두 실행이 같은 identity 를 갖는다.

    M7  `fit → grid` 역순이면 `phase_done("fit")` 이 선행 receipt 를 못 찾고
        `consumed` 를 **조용히 생략**한다. finalize 는 `consumed` 가 없으면
        `continue` 하므로, 결속 없이 `executed` 로 닫힌다.

`[해석]` 둘은 같은 병이다. 우리가 "닫힌 집합" 이라고 부른 것이 **실제 schema
보다 작았다.** 그러므로 이름을 하나씩 더하지 않는다 (그러면 다음 manifest 가
또 빠진다). schema 를 **선언**하고, 선언 밖의 것이 나타나면 **멈춘다**. 결속도
같다 — "있으면 검사" 가 아니라 **"없으면 오류"** 여야 결속이다.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import tools.preserve as P                                      # noqa: E402

#: run 디렉터리 안의 manifest 를 뜻하는 이름 꼴.
_MANIFEST_RE = re.compile(r"^[a-z0-9_]*manifest[a-z0-9_]*\.yaml$")


# ── M2 ────────────────────────────────────────────────────────────────────
def test_the_start_manifest_takes_part_in_the_content_identity(tmp_path):
    """★ M2 — 시작 manifest 만 다른 두 실행은 **다른 실행**이다.

    production 은 grid 시작에 `curves_manifest_start.yaml` 을, fit 시작에
    `manifest_start.yaml` 을 쓴다 (`src/grid.py` · `src/fitting.py`). 그
    두 파일이 identity 밖이면, 시작 조건이 다른 두 실행이 같은 키를 갖고
    한쪽의 class 가 다른 쪽에 적용된다.
    """
    a = tmp_path / "a"
    b = tmp_path / "b"
    for d, start in ((a, "seed: 1\n"), (b, "seed: 2\n")):
        d.mkdir()
        (d / "curves_manifest.yaml").write_text("curves_sha256: same\n",
                                                encoding="utf-8")
        (d / "curves_manifest_start.yaml").write_text(start, encoding="utf-8")
    assert P.run_content_id(a) != P.run_content_id(b), (
        "시작 manifest 가 내용 identity 밖이다 — 시작 조건이 다른 두 실행이 "
        "같은 키를 갖는다 (M2)")

    c = tmp_path / "c"
    c.mkdir()
    (c / "manifest.yaml").write_text("fits_sha256: same\n", encoding="utf-8")
    (c / "manifest_start.yaml").write_text("seed: 1\n", encoding="utf-8")
    d = tmp_path / "d"
    d.mkdir()
    (d / "manifest.yaml").write_text("fits_sha256: same\n", encoding="utf-8")
    (d / "manifest_start.yaml").write_text("seed: 2\n", encoding="utf-8")
    assert P.run_content_id(c) != P.run_content_id(d), (
        "fit 의 시작 manifest 가 내용 identity 밖이다 (M2)")


def test_the_declared_schema_is_exactly_what_production_writes():
    """★ M2 — 선언한 schema 가 **production 의 실제 이름 집합**이어야 한다.

    이 시험이 이 라운드의 핵심이다. 이름을 하나 더하는 수정은 다음 manifest 를
    또 놓치지만, 이 시험은 **새 이름이 생기는 순간** 빨개진다.

    두 방향을 다 본다:
      · production 에 있는 manifest 이름이 선언에 없으면 → identity 가 모른다
      · 선언에만 있고 production 에 없으면 → 선언이 거짓이다
        (`fits_manifest.yaml` 이 정확히 그랬다 — 쓰는 곳이 0곳)
    """
    declared = set(P.RUN_MANIFEST_SCHEMA)
    seen: dict[str, list[str]] = {}
    for py in sorted([*(REPO / "src").rglob("*.py"),
                      *(REPO / "tools").rglob("*.py")]):
        if py.resolve() == Path(P.__file__).resolve():
            continue                    # 선언 자신은 근거가 아니다
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):   # pragma: no cover
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                    and _MANIFEST_RE.match(node.value):
                seen.setdefault(node.value,
                                []).append(py.relative_to(REPO).as_posix())

    unknown = {n: v for n, v in seen.items() if n not in declared}
    assert not unknown, (
        f"production 이 쓰는 manifest 이름이 schema 선언 밖이다: {unknown} — "
        "내용 identity 가 그 파일을 모르므로 두 실행이 같은 키를 가질 수 있다 "
        "(M2)")

    orphan = sorted(declared - set(seen))
    assert not orphan, (
        f"schema 가 선언한 이름을 production 에서 아무도 안 쓴다: {orphan} — "
        "선언이 실물과 다르면 그것은 schema 가 아니라 소망이다 (M2)")


def test_an_undeclared_manifest_in_a_run_dir_is_refused(tmp_path):
    """★ M2 — 선언 밖의 manifest 를 만나면 **멈춘다** (fail-closed).

    구조 시험(위)은 우리 코드가 만드는 이름을 닫는다. 이 시험은 **런타임에**
    모르는 manifest 를 만났을 때를 닫는다 — 그때 identity 는 이미 불완전하고,
    불완전한 identity 로 class 를 정하면 그 class 는 다른 내용에도 적용된다.
    """
    d = tmp_path / "run"
    d.mkdir()
    (d / "curves_manifest.yaml").write_text("a: 1\n", encoding="utf-8")
    (d / "sidecar_manifest.yaml").write_text("b: 2\n", encoding="utf-8")
    with pytest.raises(P.PreserveError) as ei:
        P.run_content_id(d)
    assert "sidecar_manifest.yaml" in str(ei.value), ei.value


def test_the_content_id_descriptor_declares_its_own_version():
    """identity 형식이 바뀌면 **키가 바뀐다** — 그 사실이 descriptor 에 있어야 한다.

    58차에 v1→v2 로 바뀌면서 기존 레코드의 키가 안 맞았고, 그때 re-key 를
    수동으로 했다 (판단은 다시 하지 않고 승계). 형식 표시가 없으면 그런 이행이
    조용히 일어나고 "등록 없음" 과 "형식이 바뀜" 을 구별할 수 없다.
    """
    d = Path(__file__).parent / "_probe_never_exists"
    assert "run-content-id/v" in P._CONTENT_ID_KIND, P._CONTENT_ID_KIND
    assert not d.exists()


# ── M7 ────────────────────────────────────────────────────────────────────
def _claim(tmp_path):
    """`test_preserve.py` 의 lifecycle fixture 를 그대로 쓴다.

    ★ 58차에 손으로 만든 계획 fixture 가 필드 하나를 빠뜨려 시험이 **틀린
      이유로** 빨갰다. 이미 있는 것을 재사용한다.
    """
    import tests.test_preserve as TP
    from tools.preserve import open_leg_run

    led = TP._lifecycle_ledger(tmp_path)
    return led, open_leg_run("L", TP._RUN_SPEC_L, "0123456789abcdef",
                                  ledger=led)


def test_a_later_phase_can_not_close_before_its_predecessor(tmp_path):
    """★ M7 — `fit → grid` 역순은 **거부**한다.

    58차 L6 은 소비자가 자기가 본 생산자를 적게 했다. 그런데 그 기록은
    `if first is not None:` 아래에 있었다 — 선행 phase 가 아직 없으면 조용히
    생략된다. 그러면 순서를 뒤집는 것만으로 결속을 **없애 버릴 수 있다.**
    """
    from tools.preserve import CLAIM_PHASES, PreserveError

    _led, claim = _claim(tmp_path)
    later = CLAIM_PHASES[1]
    with pytest.raises(PreserveError) as ei:
        claim.phase_done(later, {"x": 1})
    assert CLAIM_PHASES[0] in str(ei.value), (
        f"거부는 했는데 선행 phase 를 지목하지 않는다: {ei.value}")

    # 순서를 지키면 통과하고, 결속이 **반드시** 남는다
    claim.phase_done(CLAIM_PHASES[0], {"curves": "a"})
    claim.phase_done(later, {"x": 1})
    ent = (claim._read().get("phases") or {})[later]
    assert (ent.get("consumed") or {}).get(CLAIM_PHASES[0]), (
        "순서를 지켰는데 결속이 안 남았다 (M7)")


def test_finalize_refuses_a_later_phase_with_no_recorded_predecessor(tmp_path):
    """★ M7 — `consumed` 가 **없으면 오류**다 (없으면 통과가 아니라).

    58차 finalize 는 `if not _want: continue` 였다. 결속이 있으면 검사하고
    없으면 넘어간다 — 그것은 검사가 아니라 **선택 사항**이다. 리뷰어는 역순
    실행으로 `consumed` 없는 durable state 를 만들어 그대로 `executed` 를 받았다.

    이 시험은 그 durable state 를 **직접** 만든다 (역순 실행 경로는 위 시험이
    막았으므로, 이미 디스크에 남아 있는 옛 상태를 재현한다 — 방어가 둘 다
    필요하다는 것이 M7 의 요지다).
    """
    from tools.preserve import CLAIM_PHASES, PreserveError, finalize_leg

    led, claim = _claim(tmp_path)
    claim.phase_done(CLAIM_PHASES[0], {"curves": "a"})
    claim.phase_done(CLAIM_PHASES[1], {"x": 1})

    # 결속만 손으로 지운다 — 58차 이전 코드가 남긴 상태와 같은 모양이다
    import json
    rec = json.loads(claim.path.read_text(encoding="utf-8"))
    rec["phases"][CLAIM_PHASES[1]].pop("consumed", None)
    claim.path.write_text(json.dumps(rec), encoding="utf-8")

    with pytest.raises(PreserveError) as ei:
        finalize_leg("L", ledger=led, token=claim.token,
                     evidence={"leg_source_digest": "0123456789abcdef",
                               "cohorts": ["gA"]})
    msg = str(ei.value)
    assert "consumed" in msg or "결속" in msg, msg
    assert CLAIM_PHASES[1] in msg, msg
