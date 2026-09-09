"""61차 α (P0-1) — **봉인이 옛 파생 산출을 흡수한다.**

리뷰어 반례 (정상 production 순서다, 공격이 아니다):

    identity_changed_after_report_refresh: true
    class_before_refresh: canonical
    class_after_refresh: null
    promotion_after_refresh: PreserveError: ... 실행 class 가 등록돼 있지 않다

`[해석]` 60차는 identity 를 "지금 있는 것 전부" 에서 **"굳히는 순간 있었던 것
전부"** 로 옮겼다. 그런데 그 "전부" 는 여전히 **우연한 파일 존재**로 정해진다.

    첫 fit commit  → 봉인 {curves_manifest, manifest, …}
    report         → analysis_manifest.yaml 생성        (identity 안 흔들림 ✔)
    resume fit commit → 다시 봉인 — 이번엔 **analysis_manifest 도 흡수**
    report 갱신    → 흡수된 member 의 바이트가 바뀜 → 봉인 stale → 무시
                     → v3 로 새 id → 그 id 에는 class 가 없다 → 승격 거부 ✘

60차 회귀는 "봉인 뒤 report 를 **처음** 더하는" 경우만 봤다. `run.sh:558-565`
의 정상 순서(fit → finalize → score → report)를 **두 번** 도는 경우가 빠졌다.

`[고침]` member 집합을 **선언이 정한다.** `RUN_MANIFEST_SCHEMA` 를 둘로 가른다:

  · `RUN_IDENTITY_MANIFESTS` — 실행이 만든 것. 내용 identity 는 **이것만** 담는다.
  · `RUN_DERIVED_MANIFESTS`  — 실행 **뒤** 파생이 만드는 것 (report 의
    `analysis_manifest.yaml`). 선언돼 있으므로 "선언 밖" 이 아니지만 identity
    밖이고, 봉인은 그것을 **기록만** 한다 (staleness 를 허용한다).

그래서 파생 산출이 몇 번 갱신되든 identity 는 안 움직이고, 실행이 만든 것을
고치면 여전히 걸린다.
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
    d.mkdir(parents=True, exist_ok=True)
    (d / "curves_manifest_start.yaml").write_text("seed: 1\n", encoding="utf-8")
    (d / "curves_manifest.yaml").write_text("curves_sha256: aaaa\n",
                                            encoding="utf-8")


def _fit_outputs(d: Path, tag: str) -> None:
    """fit 이 같은 자리에 쓰는 것 — 재개는 `manifest.yaml` 을 다시 쓴다."""
    (d / "manifest_start.yaml").write_text("bounds: preset\n", encoding="utf-8")
    (d / "manifest.yaml").write_text(f"fits_sha256: {tag}\n", encoding="utf-8")


def _report(d: Path, tag: str) -> None:
    """report 가 쓰는 파생 manifest (`run.sh` 의 마지막 단계)."""
    (d / "analysis_manifest.yaml").write_text(f"objectives: [{tag}]\n",
                                              encoding="utf-8")


def _commit(out: Path, ledger: Path, phase: str) -> None:
    cap = P.issue_execution_class(out, "L", phase, ledger=ledger)
    P.commit_run_outputs(cap, [out])


# ── P0-1 ──────────────────────────────────────────────────────────────────
def test_a_resumed_run_survives_a_report_refresh(tmp_path, ledger):
    """★ P0-1 — `기존 report → resume → report 갱신` 이 승격까지 살아야 한다.

    리뷰어가 실행한 순서 그대로다. 마지막 줄이 production 승격 검사가 하는
    일(`read_execution_class(run_content_id(out))`)이다.
    """
    out = tmp_path / "results" / "run"
    _grid_outputs(out)
    _fit_outputs(out, "first")
    _commit(out, ledger, "fit")                      # 첫 fit commit
    _report(out, "first")                            # report 생성

    _fit_outputs(out, "second")
    _commit(out, ledger, "fit")                      # resume fit commit
    cid_before = P.run_content_id(out)
    rec_before = P.read_execution_class(cid_before, ledger=ledger)
    assert rec_before is not None, "재개 commit 직후에 class 가 없다"

    _report(out, "second")                           # report 갱신 (정상 순서)

    cid_after = P.run_content_id(out)
    assert cid_after == cid_before, (
        "report 갱신이 내용 identity 를 갈아 치웠다 — 재개 commit 이 옛 파생 "
        "산출을 봉인에 흡수했기 때문이다 (61차 P0-1)")
    rec_after = P.read_execution_class(cid_after, ledger=ledger)
    assert rec_after is not None, (
        "정상 실행이 계산을 다 마친 뒤 승격에서 거부된다 — 굳힌 class 가 "
        "사라졌다 (61차 P0-1)")
    assert rec_after["execution_class"] == P.EXEC_CLASS_CANONICAL


def test_the_derived_manifest_never_enters_the_identity(tmp_path, ledger):
    """★ P0-1 — 파생 manifest 는 **어느 순서에서도** identity 밖이다.

    "재개 때만 흡수한다" 를 고치는 것으로는 부족하다. 흡수 여부가 순서에
    달려 있으면 다음 순서가 또 반례가 된다. 그러므로 규칙은 순서가 아니라
    **선언**이어야 한다 — 파생은 언제 있든 identity 밖이다.
    """
    a = tmp_path / "a"
    b = tmp_path / "b"
    for d in (a, b):
        _grid_outputs(d)
        _fit_outputs(d, "same")
    _report(a, "one")                       # a 만 report 를 가진 채로
    _commit(a, ledger, "fit")
    _commit(b, ledger, "fit")               # b 는 report 없이 굳힌다

    assert P.run_content_id(a) == P.run_content_id(b), (
        "굳히는 순간 파생 산출이 있었는지가 identity 를 갈랐다 — 같은 실행이 "
        "두 키를 가진다 (61차 P0-1)")


def test_a_derived_refresh_does_not_disturb_the_seal(tmp_path, ledger):
    """★ P0-1 — 파생을 **몇 번 갱신해도** 봉인은 유효한 채로 남는다.

    stale 봉인은 조용히 무시되므로, "봉인이 살아 있다" 를 직접 묻는다.
    무시된 봉인은 가용성 결함을 조용한 fallback 으로 바꾼다.
    """
    out = tmp_path / "results" / "run"
    _grid_outputs(out)
    _fit_outputs(out, "x")
    _commit(out, ledger, "fit")
    # ★ 파생이 **이미 있는 상태에서** 다시 굳힌다. 이 한 줄이 없으면 봉인에
    #   파생이 애초에 안 들어가서 이 시험은 아무것도 구별하지 않는다 (60차가
    #   시험한 자리가 정확히 그 조각이었다).
    _report(out, "zero")
    _fit_outputs(out, "y")
    _commit(out, ledger, "fit")

    for tag in ("one", "two", "three"):
        _report(out, tag)
        assert P._sealed_manifest_parts(out, None) is not None, (
            f"파생을 {tag} 로 갱신했더니 봉인이 stale 이 됐다 (61차 P0-1)")


# ── 반대 방향 (닫으면서 잃으면 안 되는 것) ────────────────────────────────
def test_editing_an_execution_manifest_is_still_caught(tmp_path, ledger):
    """★ 실행이 만든 member 를 고치면 여전히 봉인이 죽는다 — 무결성은 그대로."""
    out = tmp_path / "results" / "run"
    _grid_outputs(out)
    _fit_outputs(out, "x")
    _commit(out, ledger, "fit")
    assert P._sealed_manifest_parts(out, None) is not None

    (out / "manifest.yaml").write_text("fits_sha256: tampered\n",
                                       encoding="utf-8")
    assert P._sealed_manifest_parts(out, None) is None, (
        "봉인이 담은 실행 manifest 를 고쳤는데 봉인이 살아 있다")


def test_an_undeclared_manifest_is_still_refused(tmp_path, ledger):
    """★ 59차 M2 는 그대로 산다 — 선언 밖 manifest 는 여전히 거부."""
    out = tmp_path / "results" / "run"
    _grid_outputs(out)
    (out / "sneaky_manifest.yaml").write_text("x: 1\n", encoding="utf-8")
    with pytest.raises(P.PreserveError) as ei:
        P.run_content_id(out)
    assert "schema 선언 밖" in str(ei.value), str(ei.value)


def test_the_derived_manifest_is_still_a_declared_name(tmp_path, ledger):
    """★ 파생을 identity 밖으로 뺀 것이 "모르는 파일" 로 만들면 안 된다.

    선언에서 빼면 `_MANIFEST_NAME_RE` 가 그것을 **선언 밖 manifest** 로 보고
    정상 report 를 거부한다 — P0-1 을 고치다 또 정상 순서를 죽이는 형태다.
    """
    assert "analysis_manifest.yaml" in P.RUN_MANIFEST_SCHEMA
    assert "analysis_manifest.yaml" not in P.RUN_IDENTITY_MANIFESTS
    assert "analysis_manifest.yaml" in P.RUN_DERIVED_MANIFESTS
    assert set(P.RUN_MANIFEST_SCHEMA) == (set(P.RUN_IDENTITY_MANIFESTS)
                                          | set(P.RUN_DERIVED_MANIFESTS))
    assert not (set(P.RUN_IDENTITY_MANIFESTS) & set(P.RUN_DERIVED_MANIFESTS))


def test_an_execution_manifest_written_after_the_commit_keeps_the_class(
        tmp_path, ledger):
    """★ 봉인이 **아직도 하는 일** — 61차 α 뒤에 남은 몫.

    60차 P0-1 의 축은 "굳힌 뒤 `analysis_manifest.yaml` 을 더해도 class 가
    안 사라진다" 를 증인으로 썼다. 그런데 61차 α 가 파생 manifest 를 identity
    **선언 밖**으로 뺐으므로, 이제 그 경우는 봉인이 없어도 흔들리지 않는다 —
    즉 그 시험은 더 이상 **봉인의** 증인이 아니다 (마감 전수 재생이 잡았다:
    변이 rc 0).

    봉인이 지금 지키는 것은 다른 자리다: **실행 manifest 가 굳힌 뒤에 하나 더
    생기는** 정상 순서다. `run.sh` 에서 grid 가 굳힌 뒤 fit 이 같은 자리에
    `manifest_start.yaml`·`manifest.yaml` 을 쓴다. 봉인이 없으면 그 순간
    identity 가 갈리고, 갈린 키에는 class 가 없다.
    """
    out = tmp_path / "results" / "run"
    _grid_outputs(out)
    _commit(out, ledger, "grid")                 # grid 가 굳힌다
    cid_before = P.run_content_id(out)
    assert P.read_execution_class(cid_before, ledger=ledger) is not None

    # fit 이 **같은 자리**에 실행 manifest 를 더한다 (아직 안 굳혔다)
    _fit_outputs(out, "first")

    assert P.run_content_id(out) == cid_before, (
        "굳힌 뒤에 생긴 실행 manifest 가 내용 identity 를 갈아 치웠다 — "
        "봉인이 그 순간의 목록을 안 얼렸다 (60차 P0-1)")
    assert P.read_execution_class(P.run_content_id(out),
                                  ledger=ledger) is not None, (
        "grid 가 굳힌 class 가 fit 의 첫 쓰기에 사라졌다 (60차 P0-1)")
