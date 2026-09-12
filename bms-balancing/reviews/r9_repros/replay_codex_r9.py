"""R9 패키지 probe 의 **닫힘 재생기** — 보관한 원본 probe(`codex/`) 는 SHA(29ef505) 를 고정해 두어 현재 트리에서는 `main`
이 rc 1 이다. 이 러너는 원본 probe **함수**를 직접 불러(pin 우회) R7 러너와 같은 세 가지를 기록한다:

  · 도달   — 대상 검증·fixture 를 지나 실제 반례 case 에 닿았는가 (probe 별 반례 assertion 줄로 판정)
  · 상태   — `재현`(반례가 아직 있다) · `반례 소멸`(자기 반례 assertion 에서 멈췄다 / positive closure 가 섰다) · `오류`
  · 멈춘_곳 — 실패한 소스 줄 (있으면)

원본 probe 가 **옛 게시 위치**(partial 이 canonical 을 덮던 시절)나 **옛 러너 출력**(거부 대신 빈 JSON)을 전제해 반례
assertion 앞에서 죽는 것(R9-04 · P2-1 · P2-5)은 hook 만 현행 계약(`<write>/partial/`, 거부 rc 2)으로 옮긴 **적응** probe 로
positive closure 를 잰다 (`적응` 필드 True). 원본 파일은 건드리지 않는다. P2-4·P2-5 는 패키지에 probe 가 없어 회귀
테스트(`tests/test_r9_codex.py::test_d9_10`·`::test_d9_11`)에 위임하고 그 결과를 기록한다.

Codex R9 P2-1·2 의 계약을 그대로 적용한다: `--expected-head` 필수(불일치면 돌지 않는다), dirty 트리는 기본 거부
(`--allow-dirty` 는 목록을 기록), 패키지 bytes 는 `HARNESS_R9_29EF5058_SHA256SUMS.txt` 와 대조, `--probes` 는 빈/오타/
중복을 거부하고 출력 key == 요청 집합. 종료 코드는 재현·오류·mismatch·digest 불일치 중 하나라도 있으면 0 이 아니다.

    python3 reviews/r9_repros/replay_codex_r9.py --target <bms-balancing> --expected-head <sha> [--probes R9-01,…] [--output x.json]
"""
from __future__ import annotations
import argparse, contextlib, csv, hashlib, importlib.util, io, json, os, pathlib, shutil, subprocess, sys, tempfile, traceback

HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE / "codex"
PINNED = "29ef5058e68c0c64dba840ecc5a7495644cb092e"
SUMS = PKG / "HARNESS_R9_29EF5058_SHA256SUMS.txt"
KNOWN_PROBES = ("R9-01", "R9-02", "R9-03", "R9-04", "R9-05", "R9-06", "R9-07", "P2-1", "P2-2", "P2-3", "P2-4", "P2-5")

# 원본 probe 의 "반례 assertion" 조각 — 이 줄에서 멈추면 case 에 **도달**한 것이다
COUNTEREXAMPLE_LINES = {
    "R9-01": ("assert missing_first.returncode == 0",),
    "R9-03": ('assert checked.returncode == 0 and "전부 갖췄다" in checked.stdout',),
    "R9-06": ('assert rc2 == 3 and meta2["pairing"]["missing"] == ["200"]',),
}


def parse_probes(text: str):
    want = [p.strip() for p in str(text).split(",")]
    problems = []
    if not str(text).strip() or any(not p for p in want):
        problems.append("빈 probe 이름")
    unknown = [p for p in want if p and p not in KNOWN_PROBES]
    if unknown:
        problems.append(f"모르는 probe {unknown} (아는 것: {list(KNOWN_PROBES)})")
    dup = sorted({p for p in want if p and want.count(p) > 1})
    if dup:
        problems.append(f"중복 probe {dup}")
    return want, problems


def package_digest():
    status = {}
    for ln in SUMS.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        want, name = ln.split(None, 1)
        p = PKG / name.strip()
        status[name.strip()] = ("missing" if not p.is_file()
                                else ("ok" if hashlib.sha256(p.read_bytes()).hexdigest() == want else "mismatch"))
    return bool(status) and all(v == "ok" for v in status.values()), status


def dirty_paths(target: pathlib.Path) -> list:
    r = subprocess.run(["git", "-C", str(target), "status", "--porcelain", "--untracked-files=normal", "--", "."],
                       capture_output=True, text=True)
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _run_probe(pid, fn):
    """원본 probe: 자기 반례 assertion 에서 멈추면 반례 소멸, 끝까지 가면 재현, 다른 곳에서 죽으면 오류."""
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
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc().strip().splitlines()
        return {"도달": False, "상태": "오류", "멈춘_곳": tb[-1][:300], "세부": "도달 전에 예외"}


def _run_adapted(fn):
    """적응 probe: positive-closure assert 가 **서면** 반례 소멸, 깨지면 재현, 그 밖의 예외는 오류."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            d = fn()
        return {"도달": True, "상태": "반례 소멸", "멈춘_곳": d.pop("closure_assert", None), "세부": d}
    except AssertionError as e:
        return {"도달": True, "상태": "재현", "멈춘_곳": "positive-closure assert 가 깨졌다", "세부": str(e)[:600]}
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc().strip().splitlines()
        return {"도달": False, "상태": "오류", "멈춘_곳": tb[-1][:300], "세부": "도달 전에 예외"}


def _workspace(target: pathlib.Path) -> pathlib.Path:
    """aggregation·provenance 스크립트는 `<ws>/work/harness-r9-target-wsl/bms-balancing` 을 하드코딩한다 — symlink 로 맞춘다."""
    ws = pathlib.Path(tempfile.mkdtemp(prefix="r9-closure-ws-"))
    (ws / "work" / "harness-r9-target-wsl").mkdir(parents=True)
    (ws / "work" / "harness-r9-target-wsl" / "bms-balancing").symlink_to(target)
    (ws / "outputs").mkdir()
    for name in ("r9_aggregation_repros.py", "r9_provenance_repro.py"):
        shutil.copy(PKG / name, ws / "outputs" / name)
    return ws


# ── 적응 probe (hook 만 현행 계약으로) ──────────────────────────────────────────────────────
def _shape_partial_run(ns, mp, matrix, out):
    old_argv = sys.argv
    buf = io.StringIO()
    try:
        mp.setattr(sys, "argv", ["ne_shape.py", "--out-dir", str(matrix), "--write", str(out)])
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = ns.main()
    finally:
        sys.argv = old_argv
    canon = out / "ne_shape_GITT_Li.csv"
    art = canon if canon.is_file() else out / "partial" / "ne_shape_GITT_Li.csv"
    meta = json.loads(art.with_name(art.name + ".meta.json").read_text(encoding="utf-8")) if art.is_file() else None
    return rc, buf.getvalue(), canon, art, meta


def r9_04_adapted(_shape_harness, _pair):
    """R9-04: 원본은 canonical CSV 를 읽다 죽는다(partial 은 이제 `<write>/partial/`). 같은 fixture 로 requested/missing_input 을 본다."""
    import pytest
    with tempfile.TemporaryDirectory(prefix="r9-adapt-roster-") as td:
        base = pathlib.Path(td); matrix = base / "matrix"; out = base / "shape"; matrix.mkdir()
        mp = pytest.MonkeyPatch()
        try:
            ns = _shape_harness(mp, base, {"pristine": 0.0, "100": 0.01, "200": 0.10})
            class P:
                def __init__(self, state): self.state = state
                def is_file(self): return self.state != "200"
            mp.setattr(ns.D, "half_cell_path", lambda root, src, state: P(state))
            mp.setattr(ns.D, "HALF_FILE", {"GITT": {"pristine": "p", "100": "a", "200": "b"}})
            _pair(matrix, "100")
            rc, text, canon, art, meta = _shape_partial_run(ns, mp, matrix, out)
            pr = (meta or {}).get("pairing", {})
            closure = 'assert rc == 3 and not canon.exists() and pr["requested"] == ["100","200"] and pr["missing_input"] == ["200"] and pr["paired"] == ["100"]'
            assert rc == 3 and not canon.exists() and pr.get("requested") == ["100", "200"] \
                and pr.get("missing_input") == ["200"] and pr.get("paired") == ["100"], (rc, canon.exists(), pr)
            return {"rc": rc, "status": meta.get("status"), "pairing": {k: pr.get(k) for k in ("requested", "available", "missing_input", "paired", "missing")},
                    "artifact": str(art.relative_to(base)), "closure_assert": closure}
        finally:
            mp.undo()


def r9_05_adapted(agg, _shape_harness, _pair):
    """R9-05: 원본 `run_shape` 는 `ns.main()` 이 예외를 올리면 그대로 전파한다 — 중복 key 두 순서 모두 RuntimeError(중복) 여야 한다."""
    results = {}
    for order in ("forward", "reversed"):
        with tempfile.TemporaryDirectory(prefix="r9-adapt-dup-") as td:
            base = pathlib.Path(td); matrix = base / "matrix"; matrix.mkdir()
            rows = [agg.matrix_row("shape-dup", gamma="0.10"), agg.matrix_row("shape-dup", gamma="0.40")]
            if order == "reversed":
                rows = list(reversed(rows))
            agg.write_csv_unit(matrix / "matrix_100.csv", agg.MATRIX_FIELDS, rows, "shape-dup")
            ns = agg.load_ne_shape()
            try:
                agg.run_shape(ns, base, ["pristine", "100"], {"pristine", "100"}, matrix, base / "out")
                results[order] = "소비했다 (예외 없음)"
            except RuntimeError as e:
                results[order] = f"RuntimeError: {str(e)[:120]}"
    closure = 'assert all("중복" in v for v in results.values())'
    assert all("중복" in v for v in results.values()), results
    return {"orders": results, "closure_assert": closure}


def p2_5_adapted(_shape_harness):
    """P2-5: 짝 0 은 rc 1 + typed status none, `<write>/partial/` 에만 (canonical 없음)."""
    import pytest
    with tempfile.TemporaryDirectory(prefix="r9-adapt-none-") as td:
        base = pathlib.Path(td); matrix = base / "matrix"; out = base / "shape"; matrix.mkdir()
        mp = pytest.MonkeyPatch()
        try:
            ns = _shape_harness(mp, base, {"pristine": 0.0, "100": 0.01})
            rc, text, canon, art, meta = _shape_partial_run(ns, mp, matrix, out)
            closure = 'assert rc == 1 and not canon.exists() and meta["status"] == "none" and meta["pairing"]["paired"] == []'
            assert rc == 1 and not canon.exists() and (meta or {}).get("status") == "none" and meta["pairing"]["paired"] == [], (rc, meta)
            return {"rc": rc, "status": meta["status"], "closure_assert": closure}
        finally:
            mp.undo()


def p2_1_adapted(target, head):
    """P2-1: `--probes DOES_NOT_EXIST` / 빈 / 중복 / valid+unknown 은 거부 rc 2, JSON 을 내지 않는다."""
    runner = target / "reviews" / "r7_repros" / "replay_codex_r7.py"
    out = {}
    for bad in ("DOES_NOT_EXIST", "", "R7-01,R7-01", "R7-01,NOPE"):
        p = subprocess.run([sys.executable, str(runner), "--target", str(target), "--probes", bad, "--expected-head", head,
                            "--allow-dirty"], cwd=target, capture_output=True, text=True, timeout=180)
        out[bad or "<빈>"] = {"rc": p.returncode, "stdout_json": p.stdout.strip().startswith("{"), "stderr": p.stderr.strip()[-160:]}
    closure = 'assert all(v["rc"] != 0 and not v["stdout_json"] for v in out.values())'
    assert all(v["rc"] != 0 and not v["stdout_json"] for v in out.values()), out
    return {"cases": out, "closure_assert": closure}


def p2_2_adapted(target, head):
    """P2-2: expected-head 없음 / 불일치 / dirty(허용 없이) 는 돌지 않는다; 패키지 digest 를 결과에 적는다."""
    runner = target / "reviews" / "r7_repros" / "replay_codex_r7.py"
    def run(*extra):
        p = subprocess.run([sys.executable, str(runner), "--target", str(target), "--probes", "R7-06", *extra],
                           cwd=target, capture_output=True, text=True, timeout=180)
        return p.returncode, (p.stdout + p.stderr)
    no_head = run()
    wrong = run("--expected-head", "0" * 40)
    out = {"no_expected_head": {"rc": no_head[0], "msg": no_head[1].strip()[-140:]},
           "wrong_head": {"rc": wrong[0], "msg": wrong[1].strip()[-160:]}}
    if dirty_paths(target):
        strict = run("--expected-head", head)
        out["dirty_without_allow"] = {"rc": strict[0], "msg": strict[1].strip()[:160], "names_dirty": "dirty" in strict[1]}
    src = (target / "reviews" / "r7_repros" / "replay_codex_r7.py").read_text(encoding="utf-8")
    out["records_package_digest"] = "package_digest_ok" in src and "SHA256SUMS" in src
    closure = 'assert no_head rc != 0 and "expected-head" in msg; wrong rc != 0 and "mismatch" in msg; dirty rc != 0 (if dirty); digest recorded'
    assert out["no_expected_head"]["rc"] != 0 and "expected-head" in no_head[1], out
    assert out["wrong_head"]["rc"] != 0 and "mismatch" in wrong[1], out
    assert all(v["rc"] != 0 and v["names_dirty"] for k, v in out.items() if k == "dirty_without_allow"), out
    assert out["records_package_digest"], out
    return {**out, "closure_assert": closure}


def p2_3_adapted(target):
    """P2-3: 같은 `1 failed` summary 에 rc 2·3·4·5 는 오류, rc 1 만 CAUGHT."""
    audit = _load("r9_closure_audit", target / "reviews" / "r6_repros" / "codex_r6_mutation_audit.py")
    s = "1 failed, 51 deselected in 1.4s"
    got = {rc: audit.classify(rc, s) for rc in (1, 2, 3, 4, 5)}
    got["0 passed-summary"] = audit.classify(0, "1 passed, 51 deselected in 1.4s")
    closure = 'assert got == {1: "CAUGHT", 2: "오류", 3: "오류", 4: "오류", 5: "오류", "0 passed-summary": "MISSED"}'
    assert got == {1: "CAUGHT", 2: "오류", 3: "오류", 4: "오류", 5: "오류", "0 passed-summary": "MISSED"}, got
    return {"classify": {str(k): v for k, v in got.items()}, "closure_assert": closure}


def delegated(target, node):
    """패키지에 probe 가 없는 항목 — 회귀 테스트 노드에 위임하고 결과를 그대로 기록한다."""
    p = subprocess.run([sys.executable, "-m", "pytest", node, "-q", "--no-header", "-p", "no:cacheprovider"],
                       cwd=target, capture_output=True, text=True, timeout=600)
    last = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr[-200:]
    closure = f"pytest {node} → rc 0 · '1 passed'"
    assert p.returncode == 0 and "1 passed" in last, (p.returncode, last)
    return {"node": node, "summary": last, "closure_assert": closure}


def r9_02_03_agg(agg, target):
    """aggregation 패키지의 U18 case 를 helper 그대로 다시 만든다 — 이제 전부 rc ≠ 0 이어야 한다."""
    u14 = str(target / "scripts" / "check_u14.py")
    cases = {}
    root = pathlib.Path(tempfile.mkdtemp(prefix="r9-adapt-u18-"))
    old, new = root / "roster" / "old", root / "roster" / "new"
    agg.write_json_unit(old / "degeneracy_100_Li.json", "old-100", "100")
    agg.write_json_unit(old / "degeneracy_200_Li.json", "old-200", "200")
    agg.write_json_unit(new / "degeneracy_100_Li.json", "new-100", "100")
    r = agg.run_cli(u14, "--new", str(new), "--old", str(old)); cases["u14_missing_new_artifact"] = (r["rc"], "명부(roster)" in r["stdout"] and "degeneracy_200_Li.json" in r["stdout"])
    old, new = root / "drop" / "old", root / "drop" / "new"
    old_row, new_row = agg.matrix_row("old-drop"), agg.matrix_row("new-drop")
    agg.write_csv_unit(old / "matrix_100.csv", agg.MATRIX_FIELDS, [old_row], "old-drop")
    new_row.pop("LLI_pct")
    agg.write_csv_unit(new / "matrix_100.csv", [x for x in agg.MATRIX_FIELDS if x != "LLI_pct"], [new_row], "new-drop")
    r = agg.run_cli(u14, "--new", str(new), "--old", str(old), "--max-show", "200")     # 패키지 행은 열 부분집합이라 누락 목록이 길다
    cases["u14_dropped_numeric_column"] = (r["rc"], "LLI_pct" in r["stdout"])
    old, new = root / "blank" / "old", root / "blank" / "new"
    for d, rid in ((old, "old-blank"), (new, "new-blank")):
        row = agg.matrix_row(rid, provenance=""); row["ref_inputs_sha"] = ""
        agg.write_csv_unit(d / "matrix_100.csv", agg.MATRIX_FIELDS, [row], rid)
    r = agg.run_cli(u14, "--new", str(new), "--old", str(old)); cases["u14_blank_provenance"] = (r["rc"], "비어 있다" in r["stdout"])
    old, new = root / "dup" / "old", root / "dup" / "new"
    agg.write_csv_unit(old / "matrix_100.csv", agg.MATRIX_FIELDS, [agg.matrix_row("old-dup")], "old-dup")
    agg.write_csv_unit(new / "matrix_100.csv", agg.MATRIX_FIELDS,
                       [agg.matrix_row("new-dup", gamma="0.10", lli="1.0"), agg.matrix_row("new-dup", gamma="0.40", lli="8.0")], "new-dup")
    r = agg.run_cli(u14, "--new", str(new), "--schema-only"); cases["u14_duplicate_schema_only"] = (r["rc"], "중복" in r["stdout"])
    shutil.rmtree(root, ignore_errors=True)
    closure = "assert all(rc != 0 and msg for rc, msg in cases.values())"
    assert all(rc != 0 and msg for rc, msg in cases.values()), cases
    return {"cases": {k: {"rc": v[0], "names_the_defect": v[1]} for k, v in cases.items()}, "closure_assert": closure}


def r9_07_prov(provm):
    """R9-07: 패키지의 race 함수 그대로 — 이제 경로를 한 번 읽고 A 로 판정(invalid)해야 한다."""
    d = provm.eval_verified_bytes_race()
    closure = 'assert d["read_count"] == 1 and d["raced_status"] == "invalid" and d["control_same_malformed_bytes"] == "invalid"'
    assert d["read_count"] == 1 and d["raced_status"] == "invalid" and d["control_same_malformed_bytes"] == "invalid", d
    return {**{k: v for k, v in d.items() if k != "read_sha256"}, "closure_assert": closure}


def u18_prov(provm):
    """R9-02·03 (provenance 패키지의 U18 gate): 1/12 · 빈 receipt · 조건 변경이 전부 rc ≠ 0 이어야 한다."""
    d = provm.u18_roster_and_receipt()
    got = {k: d[k]["returncode"] for k in ("one_of_twelve", "blank_receipts", "config_mismatch") if k in d}
    closure = 'assert all(rc != 0 for rc in got.values())'
    assert got and all(rc != 0 for rc in got.values()), got
    return {"rc": got, "current_out_schema_rc": d.get("current_out_schema", {}).get("returncode"), "closure_assert": closure}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=pathlib.Path, required=True)
    ap.add_argument("--probes", default=",".join(KNOWN_PROBES))
    ap.add_argument("--expected-head", required=True, metavar="SHA")
    ap.add_argument("--allow-dirty", action="store_true")
    ap.add_argument("--output", type=pathlib.Path)
    a = ap.parse_args()
    target = a.target.resolve()
    want, problems = parse_probes(a.probes)
    if problems:
        print("! --probes 거부: " + "; ".join(problems) + " — 아무것도 돌리지 않았다 (Codex R9 P2-1)", file=sys.stderr)
        return 2
    head = subprocess.check_output(["git", "-C", str(target), "rev-parse", "HEAD"], text=True).strip()
    exp = a.expected_head.strip().lower()
    if len(exp) < 7 or not head.startswith(exp):
        print(f"! HEAD mismatch — expected {a.expected_head}, 실제 {head} (다르다) — 돌리지 않았다 (Codex R9 P2-2)", file=sys.stderr)
        return 2
    dirty = dirty_paths(target)
    if dirty and not a.allow_dirty:
        print(f"! working tree 가 dirty 다 ({len(dirty)} 경로) — `--allow-dirty` 없이는 돌리지 않는다:\n  " + "\n  ".join(dirty[:20]),
              file=sys.stderr)
        return 2
    digest_ok, digest = package_digest()
    out = {"target_head": head, "expected_head": a.expected_head, "head_ok": True,
           "dirty": bool(dirty), "dirty_allowed": bool(a.allow_dirty), "dirty_paths": dirty[:50],
           "package_digest_ok": digest_ok, "package_digest": digest, "pinned_sha": PINNED, "pin_bypassed": True,
           "설명": "원본 probe 함수를 직접 불러 SHA pin 을 우회한다 — 도달·상태·멈춘_곳을 따로 적는다; 옛 게시 위치/옛 러너 출력을 전제한 "
                 "probe 는 hook 만 현행 계약으로 옮긴 적응판(적응 True)", "requested": want, "probes": {}}
    if not digest_ok:
        out["오류"] = "패키지 bytes 가 SHA256SUMS 와 다르다 — probe 를 돌리지 않았다"
        print(json.dumps(out, ensure_ascii=False, indent=2)); return 2
    os.environ["PATH"] = str(pathlib.Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", "")
    root = _load("r9c_root", PKG / "r9_root_repros.py")
    target, verify, _prov, _deg, _sign, _full_matrix_rows, _shape_harness, _pair = root.boot(target)
    ws = _workspace(target)
    agg = _load("r9c_agg", ws / "outputs" / "r9_aggregation_repros.py")
    provm = _load("r9c_prov", ws / "outputs" / "r9_provenance_repro.py")
    R = out["probes"]
    for pid in want:
        if pid == "R9-01":
            R[pid] = {"probe": "root_alias", "적응": False, **_run_probe(pid, lambda: root.root_alias(target, verify, _deg, _sign))}
        elif pid == "R9-02":
            R[pid] = {"probe": "u18_roster_and_receipt + aggregation u14 cases (적응: 패키지 helper 그대로, 판정만 뒤집음)", "적응": True,
                      **_run_adapted(lambda: {"provenance": u18_prov(provm), "aggregation": r9_02_03_agg(agg, target),
                                              "closure_assert": "u18 gate 3 case rc≠0 ∧ aggregation 4 case rc≠0 이고 결함 이름을 찍는다"})}
        elif pid == "R9-03":
            R[pid] = {"probe": "blank_provenance", "적응": False, **_run_probe(pid, lambda: root.blank_provenance(target, verify, _prov, _sign, _full_matrix_rows))}
        elif pid == "R9-04":
            R[pid] = {"probe": "shape_missing_halfcell(적응: partial 위치)", "적응": True, **_run_adapted(lambda: r9_04_adapted(_shape_harness, _pair))}
        elif pid == "R9-05":
            R[pid] = {"probe": "shape_duplicate_matrix_rows(+reversed)(적응: 예외를 닫힘으로)", "적응": True, **_run_adapted(lambda: r9_05_adapted(agg, _shape_harness, _pair))}
        elif pid == "R9-06":
            R[pid] = {"probe": "shape_partial_overwrites_complete", "적응": False, **_run_probe(pid, lambda: root.shape_partial_overwrites_complete(target, _prov, _shape_harness, _pair))}
        elif pid == "R9-07":
            R[pid] = {"probe": "eval_verified_bytes_race(적응: 패키지 함수 그대로, 판정만 뒤집음)", "적응": True, **_run_adapted(lambda: r9_07_prov(provm))}
        elif pid == "P2-1":
            R[pid] = {"probe": "replay_vacuity(적응: 거부 rc·JSON 없음)", "적응": True, **_run_adapted(lambda: p2_1_adapted(target, head))}
        elif pid == "P2-2":
            R[pid] = {"probe": "runner identity(적응)", "적응": True, **_run_adapted(lambda: p2_2_adapted(target, head))}
        elif pid == "P2-3":
            R[pid] = {"probe": "r9_evidence_classify_probe(적응: 판정만 뒤집음)", "적응": True, **_run_adapted(lambda: p2_3_adapted(target))}
        elif pid == "P2-4":
            R[pid] = {"probe": "delegated → tests/test_r9_codex.py::test_d9_10", "적응": True,
                      **_run_adapted(lambda: delegated(target, "tests/test_r9_codex.py::test_d9_10_matrix_sidecar_seals_the_exact_roster_and_argv"))}
        elif pid == "P2-5":
            R[pid] = {"probe": "zero-pair typed none(적응) + test_d9_11", "적응": True,
                      **_run_adapted(lambda: {"none": p2_5_adapted(_shape_harness),
                                              "test": delegated(target, "tests/test_r9_codex.py::test_d9_11_zero_pair_and_partial_are_distinct_typed_states"),
                                              "closure_assert": "짝 0 → rc 1 · status none · canonical 없음 ∧ test_d9_11 passed"})}
    shutil.rmtree(ws, ignore_errors=True)
    statuses = {pid: r["상태"] for pid, r in R.items()}
    out["closed"] = list(R) == want and all(s == "반례 소멸" for s in statuses.values())
    out["rc_reason"] = ("모든 요청 probe 가 자기 반례 assertion 에서 멈췄다 / positive closure 가 섰다" if out["closed"]
                        else f"닫히지 않음: { {p: s for p, s in statuses.items() if s != '반례 소멸'} }")
    text = json.dumps(out, ensure_ascii=False, indent=2, default=str)
    print(text)
    if a.output:
        a.output.write_text(text + "\n", encoding="utf-8")
    return 0 if out["closed"] else 1


if __name__ == "__main__":
    sys.exit(main())
