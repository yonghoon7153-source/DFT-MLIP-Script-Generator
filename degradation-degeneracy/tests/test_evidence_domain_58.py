"""58차 L7·L10 — caller 가 준 evidence 를 lifecycle 이 그대로 믿는다.

두 발견은 같은 축이다. `finalize_leg()` 는 caller evidence 를 `dict(evidence)`
로 복사한 뒤 몇 개만 덮어쓴다. 나머지는 **caller 가 정한 대로 원장에 봉인된다.**

  L7  `bundle_uri` 가 absolute 이면 `root / uri` 가 `root` 를 **버린다** (pathlib).
      그래서 clone 밖 디렉터리가 개수·바이트·index 해시만 맞으면
      `full_bundle` 로 기록된다 — clean clone 에서는 회수할 수 없는 증거다.

  L10 `verifier_origin` 은 **일부러 약한** 한 번짜리 migration 경로를 표시하는
      값이다 (§57 P0-5). 그런데 normal finalize 가 그 값을 그대로 적을 수 있어,
      정상 기록과 migration 기록이 **유일한 provenance 표시로 구분되지 않는다.**

`[해석]` 둘 다 "무엇을 받아들일지" 의 도메인이 열려 있는 것이다. 검사를
늘리는 대신 **도메인을 닫는다** — 경로는 저장소 안 상대경로만, evidence 는
lifecycle 소유 키를 caller 가 못 쓰게.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import tools.preserve as P


@pytest.fixture
def ledger(tmp_path) -> Path:
    from tests.test_preserve import _lifecycle_ledger
    return _lifecycle_ledger(tmp_path)


def _finish(ledger: Path):
    """두 phase 를 정상으로 닫은 claim 을 만든다."""
    from tests.test_preserve import _RUN_SPEC_L
    claim = P.open_leg_run("L", _RUN_SPEC_L, "0123456789abcdef", ledger=ledger)
    claim.phase_done("grid", {"g": 1})
    claim.phase_done("fit", {"f": 1})
    return claim


# ── L7 ────────────────────────────────────────────────────────────────────
def test_an_absolute_bundle_uri_is_refused(tmp_path, ledger):
    """★ L7 — clone **밖** 묶음이 `full_bundle` 로 기록되면 안 된다.

    `root / "/tmp/…"` 는 pathlib 에서 `root` 를 버리고 `/tmp/…` 가 된다.
    그래서 저장소 밖 디렉터리가 개수·바이트·index 해시만 맞으면 통과했다.
    clean clone 에서 회수할 수 없는 증거를 "clone 으로 검증 가능한 묶음" 이라고
    기록하는 것이므로 거짓 양성이다.
    """
    outside = tmp_path / "outside-clone"
    outside.mkdir()
    (outside / "payload.bin").write_bytes(b"x" * 10)
    idx = outside / "index.json"
    idx.write_text('{"files": ["payload.bin"]}', encoding="utf-8")

    import hashlib
    files = sorted(x for x in outside.rglob("*") if x.is_file())
    claim = _finish(ledger)
    with pytest.raises(P.PreserveError):
        P.finalize_leg(
            "L", ledger=ledger, token=claim.token,
            evidence={
                "leg_source_digest": "0123456789abcdef",
                "cohorts": ["gA"],
                "preservation_status": "full_bundle",
                "bundle_uri": str(outside),                 # ← absolute
                "payload_index": str(idx),
                "bundle_files": len(files),
                "payload_bytes": sum(x.stat().st_size for x in files),
                "payload_index_sha256":
                    hashlib.sha256(idx.read_bytes()).hexdigest(),
            })


@pytest.mark.parametrize("uri", ["../escape", "docs/../../escape", ""])
def test_a_bundle_uri_that_escapes_the_repository_is_refused(uri, ledger):
    """★ L7 — absolute 만이 아니라 **탈출하는 모든 철자**를 막는다.

    absolute 하나만 막으면 `..` 로 같은 자리에 도달한다. 도메인을 닫는다는 것은
    "저장소 안에 담긴 정규 상대경로" 만 받는다는 뜻이다.
    """
    claim = _finish(ledger)
    with pytest.raises(P.PreserveError):
        P.finalize_leg(
            "L", ledger=ledger, token=claim.token,
            evidence={"leg_source_digest": "0123456789abcdef",
                      "cohorts": ["gA"],
                      "preservation_status": "full_bundle",
                      "bundle_uri": uri,
                      "payload_index": "idx.json",
                      "bundle_files": 1, "payload_bytes": 1,
                      "payload_index_sha256": "0" * 64})


# ── L10 ───────────────────────────────────────────────────────────────────
def test_normal_finalize_cannot_forge_the_migration_provenance(ledger):
    """★ L10 — `verifier_origin` 은 **lifecycle 소유**다.

    이 값은 "인증 근거가 원장 봉인보다 약한 경로로 넘어왔다" 를 표시한다
    (57차 P0-5). caller 가 쓸 수 있으면 정상 기록과 migration 기록이 구분되지
    않고, 그 표시를 근거로 한 감사가 무의미해진다.
    """
    claim = _finish(ledger)
    with pytest.raises(P.PreserveError):
        P.finalize_leg("L", ledger=ledger, token=claim.token,
                       evidence={"leg_source_digest": "0123456789abcdef",
                                 "cohorts": ["gA"],
                                 "verifier_origin": "legacy_migration_57"})


@pytest.mark.parametrize("key", ["phases", "attempt_id", "run_spec_digest",
                                 "attempt_verifier", "verifier_origin"])
def test_lifecycle_owned_evidence_keys_are_refused_from_callers(key, ledger):
    """★ L10 — 예약 키 **전부**를 닫는다.

    `verifier_origin` 하나만 막으면 나머지 넷은 열려 있다. 그 중 셋은 지금
    lifecycle 이 나중에 덮어쓰므로 무해해 보이지만, "덮어쓰니 괜찮다" 는
    **순서에 기댄 안전**이다 — 순서가 바뀌면 조용히 뚫린다. 도메인에서 거절한다.
    """
    claim = _finish(ledger)
    with pytest.raises(P.PreserveError):
        P.finalize_leg("L", ledger=ledger, token=claim.token,
                       evidence={"leg_source_digest": "0123456789abcdef",
                                 "cohorts": ["gA"], key: "무엇이든"})


def test_a_normal_finalize_still_records_its_own_origin(ledger):
    """정상 경로도 origin 을 **남긴다** — 없애는 게 아니라 lifecycle 이 정한다."""
    claim = _finish(ledger)
    P.finalize_leg("L", ledger=ledger, token=claim.token,
                   evidence={"leg_source_digest": "0123456789abcdef",
                             "cohorts": ["gA"]})
    doc = json.loads(json.dumps(P._load_ledger(ledger)))   # 순수 읽기
    leg = next(e for e in doc["legs"] if e["leg_id"] == "L")
    assert (leg["evidence"] or {}).get("verifier_origin") == "normal_finalize", (
        "정상 finalize 가 자기 origin 을 안 남긴다 — 그러면 '표시 없음' 이 "
        "정상인지 옛 기록인지 구분되지 않는다")
