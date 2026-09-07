"""58차 L14 (자체 발견) — smoke 면제 레코드는 **커밋 대상이 아니다**.

L1 을 고쳐 production smoke 가 등록부에 적기 시작하자 두 가지가 깨졌다:

1. smoke 를 돌릴 때마다 등록부가 **자란다.** 실측으로 확인했다 — 연속 두 번
   돌리니 8 → 9 → 10 이고 매번 **다른** content id 였다. smoke manifest 에
   실행마다 달라지는 것이 들어 있어 멱등이 아니다.
2. 그래서 **smoke 를 돌리면 트리가 더러워진다.** 이 저장소의 규율은 "smoke 는
   clean 커밋에서 돈다" 인데, 내 수정이 그 규율과 충돌하는 상태를 만들었다.

`[해석]` 결정적 사실은 **smoke 가 종료 시 자기 산출을 지운다**는 것이다.
그러면 등록된 내용이 어디에도 없는데 레코드만 남는다 — 죽은 무게다. 정본
authority(canonical·legacy 분류)는 감사 대상이고 수가 적고 오래 살지만,
smoke 면제는 ephemeral 산출에 대응하는 **국소 운용 상태**다.

**방어를 잃지 않는다**: 등록이 없으면 승격은 **거부**된다(fail-closed). 그러므로
smoke 레코드를 공유하지 않아도 다른 머신에서는 여전히 거부다 — 오히려 더 엄격하다.
"""
from __future__ import annotations

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


def _run(root: Path, name: str, body: bytes) -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "curves_manifest.yaml").write_bytes(body)
    return d


def test_smoke_records_do_not_land_in_the_shared_registry(tmp_path, ledger):
    """★ L14 — smoke 레코드가 **공유(tracked) 등록부**에 쌓이면 안 된다.

    smoke 실행마다 새 content id 가 나오므로, 공유 자리에 적으면 등록부가
    무한히 자라고 그 저장소는 영원히 dirty 다.
    """
    shared = P.exec_class_root_for_ledger(ledger)
    local = P.local_exec_class_root_for_ledger(ledger)

    for i in range(3):                       # smoke 를 세 번 돌린 셈
        P.record_execution_class(_run(tmp_path, f"s{i}", f"run {i}\n".encode()),
                                 EXEC_CLASS_SMOKE, evidence="면제", ledger=ledger)

    n_shared = len(list(shared.glob("*.json"))) if shared.is_dir() else 0
    n_local = len(list(local.glob("*.json"))) if local.is_dir() else 0
    assert n_shared == 0, (
        f"smoke 레코드 {n_shared}건이 공유 등록부에 쌓였다 — smoke 를 돌릴 때마다 "
        "저장소가 더러워지고 등록부가 무한히 자란다 (L14)")
    assert n_local == 3, f"국소 등록부에 3건이 있어야 하는데 {n_local}건이다"


def test_canonical_records_still_land_in_the_shared_registry(tmp_path, ledger):
    """정본 분류는 **여전히 공유**된다 — 감사 대상이고 리뷰어가 인용한다."""
    P.record_execution_class(_run(tmp_path, "c", b"canonical\n"),
                             EXEC_CLASS_CANONICAL, evidence="계획 gate 통과",
                             ledger=ledger)
    shared = P.exec_class_root_for_ledger(ledger)
    assert len(list(shared.glob("*.json"))) == 1


def test_a_smoke_record_still_blocks_promotion(tmp_path, ledger, monkeypatch):
    """★ 자리를 옮겨도 **방어는 그대로**여야 한다.

    이 시험이 없으면 L14 의 수정이 곧 P0-8 의 후퇴가 된다. 국소로 옮긴 뒤에도
    승격 sink 가 smoke 를 알아보고 막는지 묻는다.
    """
    monkeypatch.setattr(P, "canonical_ledger", lambda x=None: ledger)
    d = _run(tmp_path, "moved", b"smoke bytes\n")
    P.record_execution_class(d, EXEC_CLASS_SMOKE, evidence="면제", ledger=ledger)

    with pytest.raises(P.PreserveError):
        P.assert_not_smoke_provenance([d], "보고서", dest=tmp_path / "OUT.md")


def test_one_content_still_cannot_hold_two_classes_across_the_split(
        tmp_path, ledger):
    """★ 갈라 놓은 두 자리가 **한 불변식**을 유지해야 한다.

    자리를 나누면 "한 내용은 한 class" 가 자리마다 따로 성립하는 사고가 나기
    쉽다. 그러면 같은 내용을 한쪽엔 smoke, 다른 쪽엔 canonical 로 적을 수 있고
    읽는 쪽이 무엇을 믿을지 정할 수 없다.
    """
    d = _run(tmp_path, "both", b"same bytes\n")
    P.record_execution_class(d, EXEC_CLASS_SMOKE, evidence="먼저 smoke",
                             ledger=ledger)
    with pytest.raises(P.PreserveError):
        P.record_execution_class(d, EXEC_CLASS_CANONICAL, evidence="뒤집기",
                                 ledger=ledger)


def test_the_local_registry_is_ignored_by_git():
    """★ 국소 등록부가 실제로 **git 이 안 보는 자리**여야 한다.

    코드가 어디에 쓰든, `.gitignore` 가 그 자리를 덮지 않으면 트리는 여전히
    더러워진다. 실물 저장소에 대고 `git check-ignore` 로 묻는다 — 규칙을
    문자열로 읽어 해석하지 않는다.
    """
    import subprocess

    repo = Path(__file__).resolve().parent.parent
    target = P.local_exec_class_root_for_ledger(
        repo / "docs" / "22p_gap" / "LEG_PRESERVATION.yaml") / "probe.json"
    r = subprocess.run(["git", "check-ignore", "-q", str(target)],
                       cwd=repo, capture_output=True)
    assert r.returncode == 0, (
        f"{target} 가 gitignore 되지 않는다 — smoke 를 돌리면 트리가 더러워진다")
