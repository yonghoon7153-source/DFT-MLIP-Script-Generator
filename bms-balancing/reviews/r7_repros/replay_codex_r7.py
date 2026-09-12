"""R7 패키지 probe 의 **닫힘 재생기** (Codex R8-07) — 보관한 원본 probe 는 SHA(521be85) 를 고정해 두어 현재 트리에서는
첫 assertion 에서 rc 1 이다. 그것은 옳지만 "수정 뒤 각 probe 가 자기 반례 assertion 에서 실패한다" 를 재생할 명령이
없었다. 이 러너는 원본 probe 함수를 **직접** 불러(pin 우회) 세 가지를 따로 기록한다:

  · 도달   — 대상 검증·fixture 를 지나 실제 반례 case 에 닿았는가 (probe 별 반례 assertion 줄 목록으로 판정)
  · 상태   — `재현`(반례가 아직 있다) · `반례 소멸`(자기 반례 assertion 에서 멈췄다) · `오류`(도달 전에 죽었다)
  · 멈춘_곳 — 실패한 소스 줄 (있으면)

R7-05·06 은 원본 probe 가 옛 내부 이름(`M`, baseline 기본값)에 묶여 있어 현행 API 로 **적응**한 positive-closure
검사를 같이 둔다 (`적응` 필드가 True 인 항목). 원본 파일은 건드리지 않는다.

    python3 reviews/r7_repros/replay_codex_r7.py --target <bms-balancing> [--probes R7-01,R7-06] [--output x.json]
"""
from __future__ import annotations
import argparse, contextlib, importlib.util, io, json, os, pathlib, subprocess, sys, tempfile, traceback

HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE / "codex"
PINNED = "521be85e74acef80feec45bd147dd339e25b8d0a"

# probe 별 "반례 assertion" 의 소스 조각 — 이 줄에서 멈추면 case 에 **도달**한 것이다
COUNTEREXAMPLE_LINES = {
    "R7-01": ('assert partial["rc"] == 0', 'assert empty_run["rc"] == 0'),
    "R7-02": ('assert A["sigma_at_k1_V"]!=mixed["sigma_at_k1_V"]',),
    "R7-03": ('assert not any("ref" in k', 'assert A["inputs_sha"]==B["inputs_sha"]'),
    "R7-04": ('assert p.returncode == 0',),
}


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _run_adapted(fn):
    """적응 probe: positive-closure assert 가 **서면** 반례 소멸, 깨지면 반례 재현, 그 밖의 예외는 오류."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            d = fn()
        return {"도달": True, "상태": "반례 소멸", "멈춘_곳": d.get("closure_assert"), "세부": {k: v for k, v in d.items() if k != "closure_assert"}}
    except AssertionError as e:
        return {"도달": True, "상태": "재현", "멈춘_곳": "positive-closure assert 가 깨졌다", "세부": str(e)[:400]}
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc().strip().splitlines()
        return {"도달": False, "상태": "오류", "멈춘_곳": tb[-1][:300], "세부": "도달 전에 예외"}


def _run_probe(pid, fn):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            detail = fn()
        return {"도달": True, "상태": "재현", "멈춘_곳": None, "세부": str(detail)[:400]}
    except AssertionError:
        tb = traceback.extract_tb(sys.exc_info()[2])
        frames = [f for f in tb if str(PKG) in (f.filename or "")]
        line = (frames[-1].line or "").strip() if frames else ""
        reached = any(sn in line for sn in COUNTEREXAMPLE_LINES.get(pid, ()))
        return {"도달": reached, "상태": "반례 소멸" if reached else "오류",
                "멈춘_곳": f"{pathlib.Path(frames[-1].filename).name}:{frames[-1].lineno}: {line}" if frames else "?",
                "세부": ("자기 반례 assertion 에서 멈췄다" if reached else "반례 case 전에 assertion 이 깨졌다 — 원본 probe 의 전제가 현행 트리와 다르다")}
    except BaseException as e:                                          # noqa: BLE001
        tb = traceback.format_exc().strip().splitlines()
        return {"도달": False, "상태": "오류", "멈춘_곳": tb[-1][:300], "세부": "도달 전에 예외"}


def r7_05_adapted(target):
    """R7-05 (baseline 기본값): 원본은 `default_environment` rc 1 을 assert 한다 — 현행은 R6_OLD_OUT 없이 `mode: 부분` rc 0."""
    prog = target / "reviews/r6_repros/codex/replay_codex_r6_adapted.py"
    env = dict(os.environ); env.pop("R6_OLD_OUT", None)
    r = subprocess.run([sys.executable, str(prog), "--target", str(target)], capture_output=True, text=True, env=env, cwd=target)
    rep = json.loads(r.stdout) if r.stdout.strip().startswith("{") else {}
    mode = rep.get("mode", "")
    closure = 'assert r.returncode == 0 and mode.startswith("부분")'                # positive closure
    assert r.returncode == 0 and mode.startswith("부분"), (r.returncode, mode)
    return {"rc": r.returncode, "mode": mode, "baseline": rep.get("baseline"), "closure_assert": closure}


def r7_06_adapted(target):
    """R7-06 (MISSED 에 rc 0): 원본은 옛 내부 이름 `M` 을 잘라 넣는다 — 현행 `MUTATIONS` 로 같은 대조를 한다."""
    prog = target / "reviews/r6_repros/codex_r6_mutation_audit.py"
    code = ("import importlib.util,sys\n"
            f"p={str(prog)!r}\n"
            "s=importlib.util.spec_from_file_location('audit_ctl',p)\n"
            "m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\n"
            "old='MODES = (\"LAM_PE\", \"LAM_NE\", \"LLI\")'\n"
            "m.MUTATIONS=[('semantic no-op','c6_04','scripts/compare_states.py',old,old+'  # no-op')]\n"
            "sys.exit(m.main())\n")
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=target)
    closure = 'assert "MISSED: 1" in r.stdout and r.returncode != 0'                 # positive closure
    assert "MISSED: 1" in r.stdout and r.returncode != 0, (r.returncode, r.stdout[-300:])
    return {"rc": r.returncode, "tail": r.stdout.strip().splitlines()[-2:], "closure_assert": closure}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=pathlib.Path, required=True)
    ap.add_argument("--probes", default="R7-01,R7-02,R7-03,R7-04,R7-05,R7-06")
    ap.add_argument("--output", type=pathlib.Path)
    a = ap.parse_args()
    target = a.target.resolve()
    sys.path.insert(0, str(target)); sys.path.insert(0, str(target / "scripts"))
    os.environ["PATH"] = str(pathlib.Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", "")
    head = subprocess.check_output(["git", "-C", str(target), "rev-parse", "HEAD"], text=True).strip()
    want = [p.strip() for p in a.probes.split(",") if p.strip()]
    out = {"target_head": head, "pinned_sha": PINNED, "pin_bypassed": True,
           "설명": "원본 probe 함수를 직접 불러 SHA pin 을 우회한다 — 도달·상태·멈춘_곳을 따로 적는다 (Codex R8-07)",
           "probes": {}}
    ex = _load("r7c_exec", PKG / "harness_r7_execution_repros.py")
    cl = _load("r7c_claims", PKG / "harness_r7_claims_repros.py")
    inf = _load("r7c_inf", PKG / "harness_r7_inference_repros.py")
    from bms_balancing import verify as v                                # noqa: E402
    import provenance as pv                                              # noqa: E402
    with tempfile.TemporaryDirectory(prefix="r7-closure-") as tmp:
        root = pathlib.Path(tmp) / "agg"; root.mkdir()
        probes = {
            "R7-01": ("aggregate_completeness", lambda: ex.aggregate_completeness(target, root, v, pv)),
            "R7-02": ("noise_reopen", lambda: cl.noise_reopen(target)),
            "R7-03": ("matrix_reference_omission", lambda: cl.matrix_reference_omission(target)),
            "R7-04": ("r7_baseline_policy_split", lambda: inf.r7_baseline_policy_split(target)),
        }
        for pid in want:
            if pid in probes:
                name, fn = probes[pid]
                out["probes"][pid] = {"probe": name, "적응": False, **_run_probe(pid, fn)}
            elif pid == "R7-05":
                out["probes"][pid] = {"probe": "adapted_runs(적응)", "적응": True, **_run_adapted(lambda: r7_05_adapted(target))}
            elif pid == "R7-06":
                out["probes"][pid] = {"probe": "missed_exit_control(적응)", "적응": True, **_run_adapted(lambda: r7_06_adapted(target))}
    text = json.dumps(out, ensure_ascii=False, indent=2)
    print(text)
    if a.output:
        a.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
