"""60차 α (P0-1) — **내용 identity 는 언제 정해지는가.**

리뷰어 반례 (공격이 아니라 **정상 production 순서**다):

    grid/fit 이 실행 class 를 등록한다 → 그 뒤 report 가
    `analysis_manifest.yaml` 을 쓴다 (`tools/compare_objectives.py`) →
    `run_content_id()` 가 바뀐다 → 새 ID 로는 class 가 없다 →
    마지막 승격 검사(`tools/make_results.py`)가 **정상 `all → report` 를
    거부한다.** 계산을 다 마친 뒤 막히는 가용성 결함이다.

`[해석]` 59차는 "identity 가 담는 이름 집합" 을 schema 로 승격했다. 그런데
빠진 것은 집합이 아니라 **시간**이었다: 이름 집합 시험은 writer 들의 **순서**를
증명하지 않는다. 파생 산출이 뒤에 더 써도 identity 가 안 흔들리려면, identity 는
"지금 디렉터리에 무엇이 있는가" 가 아니라 **"굳히는 순간 무엇이 있었는가"** 로
정해져야 한다.

그래서 굳히는 자리(`commit_run_outputs()`)가 **봉인**을 남기고, 이후의 모든
독자는 그 봉인에서 identity 를 유도한다. 봉인은 담은 member 의 digest 를 함께
적으므로,

  - 뒤에 **다른** manifest 가 추가돼도 identity 는 그대로고 (가용성),
  - 봉인이 담은 member 의 **바이트가 바뀌면** 검증이 실패하며 (무결성),
  - 봉인만 복사해 가도 그 바이트가 없으면 검증에서 떨어진다 (위조 불가).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import tools.preserve as P                                      # noqa: E402


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    led = tmp_path / "authority" / "LEG_PRESERVATION.yaml"
    led.parent.mkdir(parents=True)
    led.write_text("planned: []\nlegs: []\ncohorts: []\n", encoding="utf-8")
    monkeypatch.setattr(P, "canonical_ledger", lambda x=None: led)
    return led


def _grid_outputs(d: Path) -> None:
    """grid 가 굳기 전에 남기는 것 — 시작 manifest 와 본 manifest."""
    d.mkdir(parents=True, exist_ok=True)
    (d / "curves_manifest_start.yaml").write_text("seed: 1\n", encoding="utf-8")
    (d / "curves_manifest.yaml").write_text("curves_sha256: aaaa\n",
                                            encoding="utf-8")


def test_a_later_sanctioned_manifest_does_not_erase_the_registered_class(
        tmp_path, ledger):
    """★ P0-1 — 정상 `all → report` 가 마지막에 거부되면 안 된다.

    리뷰어 반례를 그대로 고정한다: class 를 굳힌 뒤 production report 가 쓰는
    `analysis_manifest.yaml` 을 더하고, 그 뒤에 **승격 검사가 하는 그대로**
    `read_execution_class(run_content_id(out))` 를 부른다.
    """
    out = tmp_path / "results" / "run"
    _grid_outputs(out)

    cap = P.issue_execution_class(out, "L", "grid", P.EXEC_CLASS_CANONICAL,
                                  ledger=ledger)
    P.commit_run_outputs(cap, [out])

    cid_before = P.run_content_id(out)
    assert P.read_execution_class(cid_before, ledger=ledger) is not None

    # ── report 가 뒤에 쓴다 (production 의 정상 순서다)
    (out / "analysis_manifest.yaml").write_text("objectives: [a, b]\n",
                                                encoding="utf-8")

    cid_after = P.run_content_id(out)
    assert cid_after == cid_before, (
        "파생 manifest 하나가 내용 identity 를 갈아 치웠다 — 정상 실행이 계산을 "
        "다 마친 뒤 승격에서 거부된다 (P0-1)")
    rec = P.read_execution_class(cid_after, ledger=ledger)
    assert rec is not None and rec["execution_class"] == P.EXEC_CLASS_CANONICAL, (
        "굳힌 class 가 사라졌다 — 봉인이 시간에 결속돼 있지 않다 (P0-1)")


def test_the_seal_still_notices_when_a_sealed_member_is_edited(tmp_path, ledger):
    """★ P0-1 의 반대 방향 — 봉인이 **가용성만** 주고 무결성을 버리면 안 된다.

    봉인이 담은 member 의 바이트를 고치면 identity 를 만들 수 없어야 한다.
    "뒤에 더해도 안 바뀐다" 와 "봉인한 것을 고치면 걸린다" 는 같이 성립해야
    하고, 그 둘이 같이 성립하는 것이 이 수정의 요점이다.
    """
    out = tmp_path / "results" / "run"
    _grid_outputs(out)
    cap = P.issue_execution_class(out, "L", "grid", P.EXEC_CLASS_CANONICAL,
                                  ledger=ledger)
    P.commit_run_outputs(cap, [out])

    (out / "curves_manifest.yaml").write_text("curves_sha256: bbbb\n",
                                              encoding="utf-8")
    with pytest.raises(P.PreserveError) as ei:
        P.run_content_id(out)
    assert "봉인" in str(ei.value), str(ei.value)


def test_a_stolen_seal_does_not_carry_the_class_to_other_bytes(tmp_path,
                                                                ledger):
    """★ P0-1 — 봉인 파일만 훔쳐 가도 class 는 따라가지 않는다.

    봉인은 member 의 digest 를 담고 독자가 그것을 **다시 계산**하므로, 같은
    identity 를 받으려면 같은 바이트여야 한다. 그것은 곧 같은 내용이다.
    """
    out = tmp_path / "results" / "run"
    _grid_outputs(out)
    cap = P.issue_execution_class(out, "L", "grid", P.EXEC_CLASS_CANONICAL,
                                  ledger=ledger)
    P.commit_run_outputs(cap, [out])

    thief = tmp_path / "results" / "thief"
    thief.mkdir(parents=True)
    (thief / "curves_manifest_start.yaml").write_text("seed: 999\n",
                                                      encoding="utf-8")
    (thief / "curves_manifest.yaml").write_text("curves_sha256: zzzz\n",
                                                encoding="utf-8")
    (thief / P.RUN_SEAL_NAME).write_bytes((out / P.RUN_SEAL_NAME).read_bytes())

    with pytest.raises(P.PreserveError):
        P.run_content_id(thief)


def test_the_promotion_guard_still_passes_a_canonical_run_after_report(
        tmp_path, ledger, monkeypatch):
    """★ P0-1 — **마지막 승격 검사**가 정상 실행을 통과시켜야 한다.

    반례가 실제로 막힌 자리는 `run_content_id()` 가 아니라 그것을 읽는
    `assert_not_smoke_provenance()` 였다 (`tools/make_results.py` 가 부른다).
    class 가 사라지면 그 검사는 "등록돼 있지 않다" 로 **정상 canonical 실행을
    거부**한다 — 계산을 다 마친 뒤에.

    smoke 자리로 쓰면 경로 판정(①)이 먼저 걸려서 이 축을 한 번도 안 본다.
    그래서 canonical 자리로 쓰고, **아무 예외도 없어야** 한다.
    """
    monkeypatch.setattr(P, "SMOKE_NAMESPACE", tmp_path / "results" / "_smoke")
    out = tmp_path / "results" / "canonical_run"
    _grid_outputs(out)

    cap = P.issue_execution_class(out, "L", "grid", P.EXEC_CLASS_CANONICAL,
                                  ledger=ledger)
    P.commit_run_outputs(cap, [out])

    # ── report 가 뒤에 쓴다 (production 의 정상 순서다)
    (out / "analysis_manifest.yaml").write_text("objectives: [a]\n",
                                                encoding="utf-8")

    P.assert_not_smoke_provenance([str(out)], "보고서",
                                  dest=str(tmp_path / "docs" / "R.md"))
