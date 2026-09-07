"""58차 L1·L2·L3 — 실행 class 를 **production 배선**에서 검증한다.

57차의 `tests/test_execution_class_p0_8.py` 7건은 전부 `record_execution_class()`
나 `assert_run_is_authorized()` 를 **직접** 불렀다. 그래서 authority 함수의 규칙은
확인했지만 **production 진입점이 그 함수에 닿는지는 한 번도 안 물었다.**
58차 리뷰어가 그 구멍(L1)과, 그것을 못 잡은 이유(L13)를 같이 지적했다.

그러므로 이 파일의 규칙은 하나다 — **top-level consumer 를 부른다.**
`src/grid.py`·`src/fitting.py` 의 계획 gate 를 실제로 통과시키고, 그 뒤에
등록부가 무엇을 알고 있는지 묻는다. helper 를 직접 부르면 이 파일의 존재 이유가
사라진다.

`[재현]` 세 시험 모두 고치기 전에 빨갛다:
  L1 — production smoke gate 를 지나도 class 가 `None`
  L2 — curves 가 같고 fits 가 다른 두 산출이 같은 content id
  L3 — 두 writer 가 동시에 등록하면 둘 다 성공하고 마지막이 이긴다
"""
from __future__ import annotations

import json
import multiprocessing as mp
import os
import time
from pathlib import Path

import pytest

import tools.preserve as P
from tools.preserve import EXEC_CLASS_CANONICAL, EXEC_CLASS_SMOKE


@pytest.fixture
def ledger(tmp_path) -> Path:
    led = tmp_path / "authority" / "LEG_PRESERVATION.yaml"
    led.parent.mkdir(parents=True)
    led.write_text("planned: []\nlegs: []\n", encoding="utf-8")
    return led


def _smoke_out(root: Path, name: str) -> Path:
    """smoke namespace 안의 산출 자리. manifest 까지 굳혀 둔다.

    class 는 manifest 가 있어야 정해진다 (`run_content_id()`). 실행 직전에는
    identity 가 없으므로, 이 시험은 **산출이 굳은 뒤** 상태를 본다 — 그것이
    production 에서 등록이 일어나야 하는 시점이다.
    """
    d = root / P.SMOKE_NAMESPACE / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "curves_manifest.yaml").write_text(
        f"leg: {name}\nsource_digest: abc\n", encoding="utf-8")
    return d


# ── L1 ────────────────────────────────────────────────────────────────────
def test_production_smoke_gate_records_the_execution_class(
        tmp_path, ledger, monkeypatch):
    """★ L1 — production 진입점이 authority 에 **닿아야** 한다.

    `src/grid.py:_assert_grid_authorized()` 는 smoke namespace 면
    `assert_run_is_authorized()` 를 부르기 전에 return 한다. 그래서 등록부에
    아무것도 안 굳는다. 그러면 §64 가 근거로 든 "양쪽 분기가 모두 적는다" 가
    production 에서 성립하지 않고, "등록 없음 = 모른다" 도 무너진다.

    이 시험은 **`_assert_grid_authorized()` 를 부른다** — 등록 함수가 아니라.
    """
    from src import grid as G

    monkeypatch.setattr(P, "canonical_ledger", lambda x=None: ledger)
    out = _smoke_out(tmp_path, "smoke-leg")

    # production 계획 gate. smoke 라 계획을 요구하지 않고 통과해야 한다.
    claim = G._assert_grid_authorized({"leg": "smoke-leg"}, out)
    assert claim is None, "smoke 는 계획 gate 를 면제받는다 (계약 §13.3.3)"

    # 그 면제가 **기록으로 남아야** 한다.
    rec = P.read_execution_class(P.run_content_id(out), ledger=ledger)
    assert rec is not None, (
        "production smoke gate 를 지났는데 등록부에 아무것도 없다 — "
        "면제를 정한 authority 에 진입점이 닿지 않았다 (L1)")
    assert rec["execution_class"] == EXEC_CLASS_SMOKE


def test_a_smoke_artifact_moved_outside_is_not_migrated_into_canonical(
        tmp_path, ledger, monkeypatch):
    """★ L1 의 두 번째 절반 — 이동 뒤 legacy migration 이 정본을 발급하면 안 된다.

    L1 로 class 가 안 굳은 산출을 namespace 밖으로 옮기면,
    `classify_legacy_run()` 이 **지금 경로만 보고** `canonical` 을 발급한다.
    P0-8 이 없애려던 경로 의존이 migration 창으로 되살아난다.
    """
    from src import grid as G

    monkeypatch.setattr(P, "canonical_ledger", lambda x=None: ledger)
    out = _smoke_out(tmp_path, "smoke-leg")
    G._assert_grid_authorized({"leg": "smoke-leg"}, out)

    moved = tmp_path / "canonical-looking"
    moved.mkdir()
    (moved / "curves_manifest.yaml").write_bytes(
        (out / "curves_manifest.yaml").read_bytes())

    # `classify_legacy_run()` 은 이미 분류된 내용에 대해 **기존 레코드를 돌려주는**
    # 멱등 동작이다 (예외가 아니다). 그러므로 지켜야 할 성질은 "예외가 난다" 가
    # 아니라 **"경로를 보고 정본을 새로 발급하지 않는다"** 이다.
    rec = P.classify_legacy_run(moved, ledger=ledger)
    assert rec["execution_class"] == EXEC_CLASS_SMOKE, (
        f"namespace 밖으로 옮겼더니 {rec['execution_class']!r} 가 발급됐다 — "
        "migration 이 지금 경로를 보고 정본을 정했다 (L1)")

    # 그리고 승격 sink 가 실제로 막아야 한다 — 등록부를 읽는 쪽까지 확인한다.
    with pytest.raises(P.PreserveError):
        P.assert_not_smoke_provenance([moved], "보고서",
                                      dest=tmp_path / "OUT.md")


# ── L2 ────────────────────────────────────────────────────────────────────
def test_two_fits_sharing_curves_do_not_share_a_content_id(tmp_path):
    """★ L2 — `run_content_id()` 가 **첫 manifest 하나**만 해시한다.

    `_EXEC_ID_MANIFESTS` 는 `curves → fits → manifest` 순이므로, 같은 곡선에서
    갈라진 두 fit 실행이 같은 identity 를 갖는다. 해시 충돌이 아니라 **투영이
    손실적**인 것이다. 그러면 한쪽의 class 가 다른 쪽에 적용된다.
    """
    same_curves = b"curves: shared\n"
    a, b = tmp_path / "fit-a", tmp_path / "fit-b"
    for d, fits in ((a, b"fit: A\n"), (b, b"fit: B\n")):
        d.mkdir()
        (d / "curves_manifest.yaml").write_bytes(same_curves)
        (d / "fits_manifest.yaml").write_bytes(fits)

    assert P.run_content_id(a) != P.run_content_id(b), (
        "곡선이 같고 적합이 다른 두 실행이 같은 내용 identity 를 가졌다 — "
        "identity 가 적용되는 manifest 전부를 담지 않는다 (L2)")


def test_a_class_conflict_is_not_swallowed_by_the_gate(
        tmp_path, ledger, monkeypatch):
    """★ L2 의 두 번째 절반 — gate 가 `PreserveError` 를 통째로 삼킨다.

    `assert_run_is_authorized()` 의 smoke 분기는 `except PreserveError: pass`
    다. 주석은 "manifest 가 아직 없는 시점" 만 뜻했지만, 실제로는 **class 충돌**
    (이미 canonical 로 등록된 내용을 smoke 로 적으려는 것)도 같이 삼킨다.
    삼키면 등록부가 authority 이기를 그만둔다.
    """
    monkeypatch.setattr(P, "canonical_ledger", lambda x=None: ledger)
    out = _smoke_out(tmp_path, "conflict-leg")
    P.record_execution_class(out, EXEC_CLASS_CANONICAL,
                            evidence="먼저 정본으로 등록", ledger=ledger)

    with pytest.raises(P.PreserveError):
        P.assert_run_is_authorized("conflict-leg", "grid", [out],
                                   {"x": 1}, "deadbeef", ledger=ledger)


# ── L3 ────────────────────────────────────────────────────────────────────
def _register(args):
    """다른 process 에서 등록한다.

    barrier 는 `_exec_class_path()` 에 건다 — **고치기 전 코드와 고친 뒤 코드가
    둘 다 지나는 유일한 자리**다. 앞선 판은 `read_execution_class()` 에 걸었는데,
    CAS 로 고치면 이긴 writer 는 그 함수를 아예 안 부르므로 barrier 가 영원히
    안 풀렸다 (실제로 걸려서 이 주석이 있다). seam 은 수정 전후 **공통**이어야
    한다 — 아니면 시험이 구현을 따라다니게 된다.
    """
    run_dir, cls, ledger_path, mark = args
    import tools.preserve as _P
    _P.canonical_ledger = lambda x=None: Path(ledger_path)
    orig = _P._exec_class_path

    def _at_barrier(cid, ledger=None):
        path = orig(cid, ledger=ledger)
        path.parent.mkdir(parents=True, exist_ok=True)
        Path(mark).touch()                       # 나는 자리를 정했다
        deadline = time.monotonic() + 20
        while (len(list(Path(mark).parent.glob("at-*"))) < 2
               and time.monotonic() < deadline):
            time.sleep(0.005)                    # 둘 다 도착할 때까지
        return path

    _P._exec_class_path = _at_barrier
    try:
        _P.record_execution_class(Path(run_dir), cls, evidence="경쟁",
                                  ledger=Path(ledger_path))
        return f"ok:{cls}"
    except _P.PreserveError:
        return f"refused:{cls}"


def test_only_one_writer_can_create_an_execution_class(tmp_path, ledger):
    """★ L3 — 등록이 read → check → `os.replace` 라 CAS 가 아니다.

    `os.replace` 는 torn write 를 막을 뿐 lost update 를 막지 않는다. 두
    writer 가 "없음" 을 함께 관측하면 **둘 다 성공**하고 마지막 replace 가
    authority 를 정한다. 그러면 "한 내용은 한 class" 라는 불변식이 경쟁 아래
    깨진다.
    """
    d = tmp_path / "raced"
    d.mkdir()
    (d / "curves_manifest.yaml").write_bytes(b"same\n")
    gate = tmp_path / "gate"
    gate.mkdir()

    with mp.Pool(2) as pool:
        got = pool.map(_register, [
            (str(d), EXEC_CLASS_CANONICAL, str(ledger), str(gate / "at-a")),
            (str(d), EXEC_CLASS_SMOKE, str(ledger), str(gate / "at-b")),
        ])

    assert sorted(got) == sorted([f"ok:{EXEC_CLASS_CANONICAL}",
                                  f"refused:{EXEC_CLASS_SMOKE}"]) or \
           sorted(got) == sorted([f"ok:{EXEC_CLASS_SMOKE}",
                                  f"refused:{EXEC_CLASS_CANONICAL}"]), (
        f"경쟁하는 두 등록이 둘 다 성공했다 ({got}) — "
        "read/check/replace 는 CAS 가 아니다 (L3)")
