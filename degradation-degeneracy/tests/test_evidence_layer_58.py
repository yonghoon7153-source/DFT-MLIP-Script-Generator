"""58차 ζ (L11·L12·L13) — 증거층. **무엇이 실제로 돌았는가** 를 다시 묻는다.

세 발견이 한 축이다: 우리가 "이 실행에서 나왔다" 고 적은 값들이 실행과
**결속돼 있지 않다.**

    L11  같은 PYTHONPATH 문자열 아래 `sitecustomize.py` 만 바꿔도
         child 결과가 ALPHA → BETA-LONG 으로 달라지는데 영수증 digest 는 동일
    L12  report 는 안 건드리고 `binding.execution`/`execution_digest` 만
         현재 값으로 갈아 끼우자 pytest 실행 0회로 170/170 통과
    L13  이름이 강한 회귀 2건이 실제 배선을 안 부른다 (helper 를 직접 부르거나
         `_nodes` 만 stub 한다)

`[해석]` L11·L12 는 같은 물음의 앞뒤다. **환경 증거가 실행 밖에 있다.** 조각
옆에 적힌 필드는 누구나 다시 쓸 수 있고, 그 필드가 가리키는 "환경" 은 문자열
목록일 뿐이라 목록 밖 바이트(`sitecustomize.py`·interpreter)가 바뀌어도 안
움직인다. 그래서 증거를 **실행 안으로** 옮긴다: 재생이 자기 report 안에
자기가 본 환경을 적고, checker 는 그 바이트에서 다시 유도한다.

이것이 §0 에 신고한 **독립 replay** 를 대체하지는 않는다. report 자체를
위조하면 여전히 통과한다 — 그 한계는 그대로 남고 요청문에 적혀 있다. 닫는
것은 "report 를 **안 건드리고**" 세탁하는 경로다.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
if str(REPO / "docs" / "22p_gap") not in sys.path:
    sys.path.insert(0, str(REPO / "docs" / "22p_gap"))


def _mr():
    import mutation_replay as mr

    return mr


def _good_slice(mr, tmp_path: Path) -> Path:
    """등록부 전체를 덮는 정상 조각 하나 (기존 회귀들과 같은 형태)."""
    reg = mr._registry()
    items, multi, _e, declared = mr._select("")
    out = tmp_path / "s1.json"

    def _report(name, phase):
        fails = (mr.EXPECT.get(name) or {}).get("fail") or []
        wit = (mr.EXPECT.get(name) or {}).get("witness") or {}
        mid = mr._marker_id(name)
        tests = [{"nodeid": f,
                  "call": {"outcome": "failed" if phase == "after" else "passed",
                           "longrepr": f"E       {wit.get(f, '')}"}}
                 for f in fails]
        tests.append({"nodeid": f"tests/test_mutation_marker_{mid}.py"
                                f"::test_mutant_{mid}",
                      "call": {"outcome": "passed", "longrepr": ""}})
        tests += mr.attestation_nodes()
        return json.dumps({"tests": tests}).encode("utf-8")

    receipts = {n: {"kexpr": "", "before": _report(n, "before"),
                    "after": _report(n, "after")} for n in reg}
    mr._write_coverage(out, "", items, multi, declared,
                       {n: True for n in reg}, receipts)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# L11 — 강제 환경이 transitive code bytes 를 안 묶는다
# ─────────────────────────────────────────────────────────────────────────────

def test_the_execution_receipt_binds_what_the_interpreter_actually_loads(
        tmp_path, monkeypatch):
    """★ L11 — 같은 `PYTHONPATH` **문자열** 아래 바이트만 바꿔도 잡혀야 한다.

    리뷰어 실측: `sitecustomize.py` 만 바꾸자 child 결과가 ALPHA → BETA-LONG
    으로 달라졌는데 `receipt_digest_equal=true` 였다. 57차 P1-2 는 재생이 보는
    환경을 **선언한 변수만** 남기도록 정화했지만, 그 변수들의 **값이 가리키는
    바이트**는 여전히 목록 밖이다. `PYTHONPATH` 는 경로 문자열이고, 그 경로
    안의 파일은 얼마든지 달라질 수 있다.

    `[해석]` 목록을 늘리는 길은 여기서도 끝나지 않는다 (`usercustomize`,
    `.pth`, interpreter 자신, 그 다음 것). 그러므로 **환경이 무엇인지 우리가
    적는 대신, 시작한 인터프리터에게 자기가 실제로 무엇을 올렸는지 묻는다.**
    """
    mr = _mr()
    site = tmp_path / "site"
    site.mkdir()
    monkeypatch.setenv("PYTHONPATH", str(site))

    (site / "sitecustomize.py").write_text("MARK = 'ALPHA'\n", encoding="utf-8")
    a = mr._execution_receipt_digest()

    (site / "sitecustomize.py").write_text(
        "MARK = 'BETA-LONG'\n", encoding="utf-8")
    b = mr._execution_receipt_digest()

    assert a != b, (
        "같은 PYTHONPATH 문자열 아래 sitecustomize.py 를 바꿨는데 실행 영수증 "
        "digest 가 그대로다 — 재생이 실제로 올리는 코드가 증거 밖에 있다 (L11)")


def test_the_execution_receipt_binds_the_interpreter_itself(monkeypatch):
    """★ L11 둘째 절반 — 같은 `PATH` 문자열 아래 **도구 바이트**가 바뀌는 경우.

    영수증은 인터프리터를 `"%d.%d.%d"` 로만 적었다. 같은 버전의 다른 바이트는
    구별되지 않는다. 실행이 스스로 보고한 자기 실행 파일의 내용 주소가 영수증
    안에 있어야 한다.

    재는 면을 `site`·`sitecustomize`·`usercustomize`·`.pth`·실행 파일로 좁힌
    것은 **어느 프로세스에서 재도 같은 면**이어야 하기 때문이다. `sys.modules`
    전체를 재면 `python -c` 와 pytest child 가 다른 값을 내고, 그러면 두 증언을
    대조할 수 없다 — 그 대조가 L12 의 핵심이다. 좁힌 대가는 요청문에 한계로
    적는다: 시작 뒤에 import 되는 코드는 이 면에 없다 (그쪽은 tree digest 와
    `inputs` 가 본다).
    """
    mr = _mr()
    rec = mr._execution_receipt()
    startup = rec.get("startup") or {}
    assert startup.get("executable_sha256"), (
        "영수증이 인터프리터 바이트를 안 담는다 — 같은 버전의 다른 실행 파일이 "
        "같은 증거를 만든다 (L11)")
    cust = startup.get("customization")
    assert isinstance(cust, dict) and set(cust) == {
        "site", "sitecustomize", "usercustomize"}, (
        f"영수증이 시작 시 사용자 확장 지점을 안 담는다: {cust!r} (L11)")
    assert "pth" in startup, (
        "영수증이 `.pth` 를 안 담는다 — `.pth` 는 import 를 심을 수 있다 (L11)")


# ─────────────────────────────────────────────────────────────────────────────
# L12 — report 를 안 건드리고 실행 증거만 세탁
# ─────────────────────────────────────────────────────────────────────────────

def test_execution_evidence_can_not_be_laundered_without_the_reports(
        tmp_path, monkeypatch):
    """★ L12 — 조각의 실행 필드만 현재 값으로 갈아 끼우면 통과했다.

    리뷰어 실측::

        original_environment_check_rc=1
        reports_unchanged=true
        pytest_runs=0
        laundered_coverage_rc=0

    조각 옆에 적힌 두 필드는 **누구나 다시 계산해서 쓸 수 있다** —
    `_execution_receipt()` 는 공개 함수다. 그러므로 그 필드가 "이 실행에서
    나왔다" 를 증명할 수는 없다. 증명할 수 있는 것은 실행이 **자기 report 안에
    남긴 것**뿐이다.

    이 시험은 pytest 를 한 번도 안 돌리고 세탁을 재현한다 — 그것이 정확히
    반례의 형태다.
    """
    mr = _mr()
    good = _good_slice(mr, tmp_path)
    assert mr.check_coverage([str(good)]) == 0, "정상 조각이 거부됐다"

    # 환경을 바꾼다 — 조각은 이제 낡았고, checker 는 그것을 거부해야 한다
    monkeypatch.setenv("DD_SMOOTH_CACHE", "laundry")
    assert mr.check_coverage([str(good)]) == 1, (
        "환경이 달라진 조각이 통과했다 — 시험 전제가 깨졌다")

    # 세탁: report 는 그대로 두고 실행 필드만 현재 값으로
    rec = json.loads(good.read_text(encoding="utf-8"))
    rec["binding"]["execution"] = dict(mr._execution_receipt())
    rec["binding"]["execution_digest"] = mr._execution_receipt_digest()
    good.write_text(json.dumps(rec, ensure_ascii=False, indent=2,
                               sort_keys=True), encoding="utf-8")

    assert mr.check_coverage([str(good)]) == 1, (
        "report 를 안 건드리고 실행 증거만 갈아 끼웠는데 통과했다 — 실행 증거가 "
        "실행 밖에 있다 (L12)")


def test_a_report_that_attests_another_environment_is_refused(tmp_path):
    """★ L12 의 반대 방향 — report 안의 증언과 조각의 주장이 어긋나면 거부.

    세탁을 막는 것이 "report 안에 무언가 있다" 가 되면 안 된다. 있는 값이
    **지금 환경과 같은가**를 봐야 한다.

    ★ 이 시험은 처음에 **선언한 이유로 물지 않았다.** 변이 감사에서 드러났다:
      증언 조회를 통째로 꺼도 통과했다. report 바이트를 고치면 `report_sha256`
      이 어긋나 checker 가 **다른 이유로** 거부했기 때문이다. 물긴 하지만
      선언한 이유로 물지 않는 증인은 증거가 아니다 (53차에 같은 형태를 겪었다).

      그래서 공격자가 할 수 있는 것을 그대로 한다: report 를 고친 뒤
      `report_sha256` 과 `transcript_digest` 를 **다시 계산해서 맞춘다**
      (둘 다 공개 함수다). 그러면 남는 불일치는 증언 하나뿐이고, 그것을 잡는
      것은 증언 조회밖에 없다.
    """
    mr = _mr()
    good = _good_slice(mr, tmp_path)
    assert mr.check_coverage([str(good)]) == 0, "정상 조각이 거부됐다"

    # 증언은 **환경 tag** 로 적힌다 (영수증 digest 가 아니다 — 영수증에는
    #   설치 package 목록처럼 자식이 다시 잴 수 없는 것도 들어 있다).
    tag = mr.environment_tag()
    rep_dir = tmp_path / "reports" / good.stem
    hit = 0
    for f in sorted(rep_dir.glob("*.json")):
        raw = f.read_text(encoding="utf-8")
        if tag in raw:
            f.write_text(raw.replace(tag, "0" * 16), encoding="utf-8")
            hit += 1
    assert hit, "report 안에 실행 증언이 없다 — 시험 전제가 깨졌다 (L12)"

    # 공격자가 하듯 digest 를 다시 맞춘다 — 그래야 이 시험이 **증언 조회**를
    #   증명한다.
    rec = json.loads(good.read_text(encoding="utf-8"))
    for name, v in rec["scenarios"].items():
        if not v.get("report_sha256"):
            continue
        blob = {ph: (rep_dir / f"{name}.{ph}.json").read_bytes()
                for ph in ("before", "after")}
        v["report_sha256"] = mr._receipt_digest(name, blob["before"],
                                                blob["after"])
    rec["binding"]["transcript_digest"] = mr._transcript_digest(rec["scenarios"])
    good.write_text(json.dumps(rec, ensure_ascii=False, indent=2,
                               sort_keys=True), encoding="utf-8")

    assert mr.check_coverage([str(good)]) == 1, (
        "다른 환경을 증언하는 report 를 담은 조각이 통과했다 (L12)")


# ─────────────────────────────────────────────────────────────────────────────
# L13 — 이름이 강한 회귀가 실제 배선을 안 부른다
# ─────────────────────────────────────────────────────────────────────────────

def test_the_top_level_checker_consumes_the_execution_receipt(tmp_path):
    """★ L13-a — 57차 회귀는 `_assert_execution_is_current()` 를 **직접** 불렀다.

    그래서 `check_coverage()` 에서 그 배선을 통째로 지워도 통과했다 (리뷰어
    실측). 이름이 "checker 가 실제로 소비한다" 인데 정작 checker 를 안 부른
    것이다 — 이 저장소가 반복해 온 실패형이다.

    이 시험은 **처음부터 초록이다.** 배선이 지금 있기 때문이다. 그러므로 이
    시험의 값은 통과 자체가 아니라 **변이 감사**에 있다: `check_coverage()`
    에서 그 한 줄을 지우면 이 시험이 죽어야 한다 (지운 뒤 실측했다).
    """
    mr = _mr()
    good = _good_slice(mr, tmp_path)
    assert mr.check_coverage([str(good)]) == 0, "정상 조각이 거부됐다"

    for drop in ("execution", "execution_digest"):
        rec = json.loads(good.read_text(encoding="utf-8"))
        rec["binding"].pop(drop, None)
        good.write_text(json.dumps(rec, ensure_ascii=False, indent=2,
                                   sort_keys=True), encoding="utf-8")
        assert mr.check_coverage([str(good)]) == 1, (
            f"`binding.{drop}` 가 없는 조각을 top-level checker 가 통과시켰다")


def test_every_replay_subprocess_declares_its_environment():
    """★ L13-b — 재생이 띄우는 **모든** 프로세스가 환경을 선언한다 (정적).

    57차 회귀는 `_nodes()` 만 stub 했다. 그래서 `_run()` 의 `env=replay_env()`
    를 `env=None` 으로 바꿔도 통과했다 — 정작 변이를 재생하는 쪽이 그쪽인데.

    호출을 하나씩 시험으로 덮는 대신 **규칙**으로 적는다: 이 모듈에서 파이썬을
    띄우는 `subprocess.run` 은 전부 `env=` 를 준다. 새 재생 경로가 생겨도 여기서
    걸린다. (`git` 조회는 재생이 아니므로 대상이 아니다 — 그것은 이 저장소를
    읽는 것이지 시험을 돌리는 것이 아니다.)
    """
    src = (REPO / "docs" / "22p_gap" / "mutation_replay.py").read_text(
        encoding="utf-8")
    missing = []
    for node in ast.walk(ast.parse(src)):
        if not (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "run"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess"):
            continue
        if not node.args:
            continue
        argv = ast.unparse(node.args[0])
        if "sys.executable" not in argv:
            continue                      # git 등 — 재생 프로세스가 아니다
        if not any(k.arg == "env" for k in node.keywords):
            missing.append(node.lineno)
    assert not missing, (
        f"재생 프로세스를 `env=` 없이 띄우는 자리가 있다 ({missing}행) — 운영자의 "
        "부모 환경이 그대로 새어 들고, 그것이 결과를 바꿔도 증거는 안 움직인다")


def test_the_runner_plants_the_attestation_and_selects_it(monkeypatch, tmp_path):
    """★ L12 의 생산자 쪽 — **재생이 증언을 실제로 남기는가.**

    checker 가 증언을 요구해도 재생이 그것을 안 남기면 정상 조각이 거부되거나,
    더 나쁘게는 증언 요구를 나중에 조용히 껐을 때 아무도 모른다. 조각을 합성한
    시험만으로는 이 축이 안 덮인다 — 합성 fixture 는 증언을 **손으로** 넣기
    때문이다. 그래서 sandbox 에 파일이 놓이는지와 `-k` 가 그 node 를 고르는지를
    직접 본다.
    """
    mr = _mr()
    (tmp_path / "tests").mkdir()
    name = sorted(mr._registry())[0]
    mid = mr._write_marker(tmp_path, name)
    tag = mr.environment_tag()

    planted = tmp_path / "tests" / f"test_mutation_env_{tag}.py"
    assert planted.is_file(), (
        f"재생이 sandbox 에 환경 증언 node 를 안 놓는다 ({planted.name})")
    assert f"def test_env_{tag}(" in planted.read_text(encoding="utf-8")

    seen: dict = {}

    class _Done:
        returncode = 1
        stdout = ""
        stderr = ""

    def _fake(cmd, **kw):
        seen["cmd"] = list(cmd)
        for tok in cmd:
            if str(tok).startswith("--json-report-file="):
                Path(str(tok).split("=", 1)[1]).write_text(
                    json.dumps({"exitcode": 1, "summary": {},
                                "tests": [], "collectors": []}),
                    encoding="utf-8")
        return _Done()

    monkeypatch.setattr(mr.subprocess, "run", _fake)
    mr._run("test_x", marker=mid, env_tag=tag)
    kexpr = seen["cmd"][seen["cmd"].index("-k") + 1]
    assert f"test_env_{tag}" in kexpr, (
        f"재생이 증언 node 를 고르지 않는다 — sandbox 에 파일만 있고 report 에는 "
        f"안 나타난다: {kexpr!r}")


def test_the_replayed_run_itself_sees_only_a_declared_environment(monkeypatch,
                                                                  tmp_path):
    """★ L13-b 동적 — `_nodes()` 가 아니라 **`_run()`** 을 태운다.

    변이를 실제로 재생하는 것은 `_run()` 이다. 그쪽을 안 태우면 "재생이 선언한
    환경만 본다" 는 이름이 지키는 것이 없다.
    """
    mr = _mr()
    outside = ("CANONICAL_RUN", "LEG", "SMOKE_DIRTY")
    assert not (set(outside) & set(mr.BOUND_ENV)), (
        f"시험 전제가 깨졌다 — 이미 선언 안에 있다: {mr.BOUND_ENV}")
    for name in outside:
        monkeypatch.setenv(name, "leaked")

    seen: dict = {}

    class _Done:
        returncode = 1
        stdout = ""
        stderr = ""

    def _fake(cmd, **kw):
        seen.update(kw)
        for tok in cmd:
            if str(tok).startswith("--json-report-file="):
                Path(str(tok).split("=", 1)[1]).write_text(
                    json.dumps({"exitcode": 1, "summary": {},
                                "tests": [], "collectors": []}),
                    encoding="utf-8")
        return _Done()

    monkeypatch.setattr(mr.subprocess, "run", _fake)
    mr._run("test_x", marker="")

    assert seen.get("env") is not None, (
        "재생(`_run`)이 pytest 에 환경을 지정하지 않는다")
    leaked = sorted(n for n in outside if n in seen["env"])
    assert not leaked, (
        f"선언하지 않은 환경변수가 재생에 그대로 들어간다: {leaked}")
