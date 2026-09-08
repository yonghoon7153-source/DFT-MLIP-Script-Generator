"""60차 γ (P0-4) — **handle 검사가 산출을 다 쓴 뒤에 온다.**

리뷰어 반례 (`unshare -Urnm` 로 gate 뒤 pathname 을 밖으로 bind-swap):

    {"handle_was_present_at_gate":true,
     "outside_received_curves_before_commit":true,
     "outside_received_manifest_before_commit":true,
     "commit_result_after_side_effects":"PreserveError: ... 실물이 다르다 ..."}

`[해석]` 59차의 handle 은 **마지막 commit 에만** 닿았다. grid 의 chunk·parquet·
manifest 와 fit 의 결과는 그 사이 내내 **이름으로** 쓰였다. 마지막 거부는 이미
밖에 남은 바이트를 되돌리지 못한다 — "분류 직전 검출은 containment 가 아니다."

그래서 이 라운드는 두 가지를 바꾼다:

  1. gate 가 자리를 **만들고** handle 을 잡는다. 59차는 "자리가 아직 없으면
     handle 이 없다" 를 한계로 신고했는데, 그 한계가 바로 production 의
     정상 경우였다 (grid 는 `mkdir` 전에 gate 를 지난다). 거부는 그 전에
     끝나므로 성공 경로에서만 만드는 것은 47차 조건 11-c 와 충돌하지 않는다.
  2. 모든 writer 가 **그 handle 아래**로 쓴다 (`staged_root()` →
     `/proc/self/fd/N`). 이름이 그 뒤에 무엇을 가리키게 되든, 쓰는 곳은 판정한
     그 커널 객체다.

이 시험은 mount namespace 없이 같은 형태를 만든다: gate 뒤에 판정한 자리를
치우고 **다른 디렉터리를 같은 이름에 놓는다**. 리뷰어의 bind-swap 과 같은
구조이고 (이름 → 다른 실물), 어디서나 재현된다.
"""
from __future__ import annotations

import os
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
    ns = tmp_path / "results" / "_smoke"
    ns.mkdir(parents=True)          # 좌표 판정은 실물을 본다 (58차 L4)
    monkeypatch.setattr(P, "SMOKE_NAMESPACE", ns)
    return led


def test_the_gate_creates_the_place_and_always_carries_a_handle(tmp_path,
                                                                 ledger):
    """★ P0-4 — 59차가 신고한 "자리가 없으면 handle 이 없다" 는 **정상 경우**였다.

    production 의 grid 는 `mkdir` 보다 먼저 gate 를 지난다 (47차 조건 11-c).
    그러므로 그 한계는 드문 모서리가 아니라 **언제나**였다. 발행이 자리를 만들고
    handle 을 잡으면 그 창이 없어진다.
    """
    out = tmp_path / "results" / "새-자리"
    assert not out.exists()
    cap = P.issue_execution_class(out, "L", "grid", ledger=ledger)
    assert out.is_dir(), "gate 가 자리를 안 만들었다"
    assert cap.dir_fd is not None, "gate 가 handle 을 안 들었다 (P0-4)"
    st_fd = os.fstat(cap.dir_fd)
    st = out.stat()
    assert (st_fd.st_dev, st_fd.st_ino) == (st.st_dev, st.st_ino)
    P.discard_execution_capability(cap)


def test_writes_go_to_the_judged_object_not_to_the_name(tmp_path, ledger):
    """★ P0-4 — gate 뒤에 이름을 바꿔치기해도 **바이트는 밖으로 안 나간다.**

    리뷰어 반례의 핵심은 "commit 이 거부했다" 가 아니라 **"거부 전에 이미
    밖에 있었다"** 이다. 그러므로 이 시험이 보는 것은 예외가 아니라
    **밖의 디렉터리가 비어 있는가** 이다.
    """
    out = tmp_path / "results" / "_smoke" / "run"
    cap = P.issue_execution_class(out, "L", "grid", ledger=ledger)
    root = P.staged_root(cap)               # 판정한 실물로 가는 길

    # ── gate 뒤 바꿔치기: 판정한 자리를 치우고 밖의 디렉터리를 그 이름에 놓는다
    judged = tmp_path / "judged-moved-aside"
    outside = tmp_path / "outside"
    outside.mkdir()
    out.rename(judged)
    outside.rename(out)

    # ── 그 뒤에 산출을 쓴다 (production 의 writer 가 하는 그대로)
    (root / "curves.parquet").write_bytes(b"PAR1-fake")
    (root / "curves_manifest.yaml").write_text("curves_sha256: aa\n",
                                               encoding="utf-8")

    assert sorted(p.name for p in out.iterdir()) == [], (
        "판정 뒤 이름이 가리키게 된 **밖의** 디렉터리가 산출을 받았다 — "
        "마지막 검사 전에 이미 바이트가 나갔다 (P0-4)")
    assert (judged / "curves.parquet").read_bytes() == b"PAR1-fake", (
        "판정한 실물이 산출을 못 받았다 — handle 이 대상을 안 가리킨다")
    P.discard_execution_capability(cap)


def test_a_missing_handle_is_refused_not_waved_through(tmp_path, ledger):
    """★ P0-4 — handle 이 없으면 **통과가 아니라 거부**다.

    59차의 `_assert_still_the_judged_dir()` 는 `dir_fd is None` 이면 곧바로
    반환했다. 그 조용한 통과가 P0-3 둘째 반례의 마지막 한 걸음이었다. 이제
    발행이 언제나 handle 을 들므로 `None` 은 정상 상태가 아니고, 정상이 아닌
    것을 만나면 멈춘다.
    """
    out = tmp_path / "results" / "run"
    cap = P.issue_execution_class(out, "L", "grid", ledger=ledger)
    rec = P._ISSUED_EXEC_CAPS[cap.nonce]
    os.close(rec.dir_fd)
    rec.dir_fd = None                       # handle 을 잃은 상태를 만든다

    with pytest.raises(P.PreserveError) as ei:
        P.commit_run_outputs(cap, [out])
    assert "handle" in str(ei.value), str(ei.value)


def test_production_grid_writes_through_the_capability(tmp_path, ledger,
                                                        monkeypatch):
    """★ P0-4 — **production 진입점**이 실제로 handle 아래로 쓴다.

    `write_curves_manifest()` 는 gate 가 준 권한을 이미 받는다. 그 함수가
    이름이 아니라 handle 로 쓰는지가 이 축이다 — 시험이 스스로 경로를
    만들면 그 축을 한 번도 안 본다.
    """
    from src import grid as G

    out = tmp_path / "results" / "_smoke" / "grid_run"
    cfg = {"leg": "smoke-leg", "solver": "fake", "seed": 1}
    claim, cap = G._assert_grid_authorized(cfg, out)
    assert claim is None and cap is not None

    judged = tmp_path / "judged-moved-aside"
    outside = tmp_path / "outside"
    outside.mkdir()
    out.rename(judged)
    outside.rename(out)

    # 굳히는 자리는 이름이 바뀐 것을 보고 거부한다 (59차 M5 가 만든 층).
    with pytest.raises(P.PreserveError):
        G.write_curves_manifest(out, cfg, conditions=[{"c_rate": 1.0}],
                                capability=cap)

    # ★ 이 시험이 보는 것은 그 거부가 **아니다.** 리뷰어의 지적은 "거부 전에
    #   이미 밖에 있었다" 였다. 그러므로 묻는 것은 밖이 비어 있는가이다.
    assert not (out / "curves_manifest.yaml").exists(), (
        "production 이 이름으로 써서 밖의 디렉터리가 manifest 를 받았다 — "
        "마지막 거부는 이미 나간 바이트를 못 되돌린다 (P0-4)")
    assert (judged / "curves_manifest.yaml").exists(), (
        "판정한 실물이 manifest 를 못 받았다 (P0-4)")
