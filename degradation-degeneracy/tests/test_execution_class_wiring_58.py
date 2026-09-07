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

    ★ 58차 — `root / P.SMOKE_NAMESPACE` 로 쓰면 **`root` 가 버려진다.**
      `SMOKE_NAMESPACE` 는 저장소 루트에서 유도한 **절대경로**이고, pathlib 은
      우변이 absolute 면 좌변을 버린다. 그래서 이 시험들은 `tmp_path` 를 받아
      놓고 실제로는 **저장소의 `results/_smoke/`** 에 썼다 — 격리된 척했지만
      아니었다 (`results/` 가 gitignored 라 트리는 안 더러워져 안 보였다).
      L7 이 `bundle_uri` 에서 잡은 것과 **같은 흡수**다. 시험도 예외가 아니다.

      그래서 namespace 자체를 tmp 로 옮기고 그 아래를 쓴다. 호출자는
      `monkeypatch` 로 `P.SMOKE_NAMESPACE` 를 함께 바꿔야 한다.
    """
    d = Path(root) / "results" / "_smoke" / name
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
    monkeypatch.setattr(P, "SMOKE_NAMESPACE",
                        tmp_path / "results" / "_smoke")
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
    monkeypatch.setattr(P, "SMOKE_NAMESPACE",
                        tmp_path / "results" / "_smoke")
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
    monkeypatch.setattr(P, "SMOKE_NAMESPACE",
                        tmp_path / "results" / "_smoke")
    out = _smoke_out(tmp_path, "conflict-leg")
    P.record_execution_class(out, EXEC_CLASS_CANONICAL,
                            evidence="먼저 정본으로 등록", ledger=ledger)

    with pytest.raises(P.PreserveError):
        P.assert_run_is_authorized("conflict-leg", "grid", [out],
                                   {"x": 1}, "deadbeef", ledger=ledger)


# ── L3 ────────────────────────────────────────────────────────────────────
def _register(args):
    """다른 process 에서 등록한다.

    barrier 는 **임계 구역 안**, 등록부를 읽은 직후에 건다
    (`_read_exec_class_at()`).

    두 번 틀렸고 그 이력을 남긴다:
      1. `read_execution_class()` 에 걸었다 → CAS 로 고치니 이긴 writer 가 그
         함수를 안 불러 barrier 가 안 풀렸다 (무한 대기).
      2. `_exec_class_path()` 로 옮겼다 → 등록부를 class 별로 가른 뒤
         **lock 을 지워도 시험이 통과했다** (변이 D 가 살아남았다). 그 자리는
         임계 구역 **바깥**이라, barrier 를 지난 뒤의 read/write 순서가 순전히
         타이밍에 달렸기 때문이다. 시험이 우연에 기대고 있었다.

    배타를 묻는 시험의 barrier 는 **"둘 다 읽었지만 아직 아무도 안 썼다" 상태**를
    강제해야 한다. 그것이 lock 이 막아야 하는 바로 그 상태다.
    """
    run_dir, cls, ledger_path, mark = args
    import tools.preserve as _P
    _P.canonical_ledger = lambda x=None: Path(ledger_path)
    orig = _P._read_exec_class_at
    seen = []

    def _at_barrier(path, cid):
        got = orig(path, cid)
        if not seen:                              # 임계 구역의 첫 read 뒤 한 번만
            seen.append(1)
            Path(mark).touch()                    # 나는 읽었다 (아직 안 썼다)
            deadline = time.monotonic() + 3
            while (len(list(Path(mark).parent.glob("at-*"))) < 2
                   and time.monotonic() < deadline):
                time.sleep(0.005)
        return got

    _P._read_exec_class_at = _at_barrier
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
