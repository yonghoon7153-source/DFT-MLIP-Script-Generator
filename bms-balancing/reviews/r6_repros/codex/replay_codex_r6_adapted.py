"""Codex R6 probe 를 **닫힌 트리에 맞게 고쳐** 다시 돌린다 — hook 이 빗나간 것을 닫힘으로 읽지 않으려고.

원본 probe 는 우리가 고친 자리에 hook 을 건다 (`Path.read_text` · `compare_states._unit_ok` ·
`load_full_cell(root, state, workbook=None)`). 고친 뒤에는 그 hook 이 **안 걸려서** 실패한다 — 그것은 "발견이 닫혔다" 가
아니라 "이 probe 로는 더 못 잰다" 이다. 그래서 hook 지점만 현행 코드에 맞추고 **판정은 뒤집어** 건다: 원본이 "섞인 것을
소비했다" 를 assert 했다면 여기서는 "섞인 것을 소비하지 않는다" 를 assert 한다. 나머지 fixture·입력·경쟁 순서는 원본 그대로다.

    python3 replay_codex_r6_adapted.py --target <bms-balancing> [--output <json>]

상태: `닫힘` = 고친 판정이 성립 · `열림` = 성립 안 함(발견이 남았다) — 둘 다 세부에 실측치를 남긴다.
"""
from __future__ import annotations
import argparse, contextlib, hashlib, importlib.util, io, json, os, pathlib, subprocess, sys, tempfile, traceback
from unittest.mock import patch

HERE = pathlib.Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _guard(fn):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            detail = fn()
        return "닫힘", detail
    except BaseException:                                        # noqa: BLE001
        tb = traceback.format_exc().strip().splitlines()
        return "열림", {"error": tb[-1][:400], "stdio": buf.getvalue()[-300:]}


# ── R6-01 · 독자가 소비하는 묶음 ────────────────────────────────────────────────────────
def a1_degeneracy_snapshot(ex, target, root, v, pv, reader):
    """원본 `snapshot_metadata_mix` 와 같은 순서 — hook 만 `Path.read_bytes` 로 (현행 독자가 쓰는 읽기)."""
    ex.fixture_repo(target, root)
    art = root / "out/degeneracy_100_Li.json"
    v.atomic_write_json(art, ex.deg("attempt-A", 1.0))
    ex.write_meta(target, root, art, "attempt-A", starts=4)
    assert pv.verify_unit(art)[0] is True
    original, switched = pathlib.Path.read_bytes, []

    def scheduled(p, *a, **k):
        data = original(p, *a, **k)
        if p == art and not switched:                            # A 의 bytes 가 독자 손에 들어간 직후 B/B 가 정상 게시
            switched.append(True)
            v.atomic_write_json(art, ex.deg("attempt-B", 20.0))
            ex.write_meta(target, root, art, "attempt-B", starts=24)
        return data

    with patch.object(pathlib.Path, "read_bytes", scheduled):
        loaded = reader.load_degeneracy(root / "out")
    disk = pv.verify_unit(art)
    assert switched and disk[0] is True, (switched, disk)        # 디스크는 B/B 로 온전하다
    e = loaded.get("100")
    if e is None:                                                # 미완으로 걸러낸 경우도 허용 (섞어 쓰지만 않으면 된다)
        first = {"consumed": None, "disk_unit": disk, "why": "읽은 bytes 와 meta 가 안 맞아 표에서 뺐다"}
    else:
        assert e["j"]["run_id"] == e["meta"]["run_id"], (e["j"]["run_id"], e["meta"]["run_id"])
        first = {"data_run_id": e["j"]["run_id"], "meta_run_id": e["meta"]["run_id"],
                 "value": e["j"]["best_modes_percent"]["LLI"], "disk_unit": disk}

    # ② 검증이 **끝난 뒤** 게시가 끼는 순서 — 묶음 검사는 A/A 로 통과하고, 그 뒤 다시 읽으면 B 를 소비하게 된다.
    #    ①의 순서만으로는 "검증 뒤 재읽기" 를 못 잰다 (검사가 먼저 깨져서 어차피 빠진다).
    root2 = root.parent / (root.name + "-after")
    root2.mkdir()
    ex.fixture_repo(target, root2)
    art2 = root2 / "out/degeneracy_100_Li.json"
    v.atomic_write_json(art2, ex.deg("attempt-A", 1.0))
    ex.write_meta(target, root2, art2, "attempt-A", starts=4)
    meta_path, published = str(art2) + ".meta.json", []
    original_text = pathlib.Path.read_text

    def after_meta(p, *a, **k):
        text = original_text(p, *a, **k)
        if str(p) == meta_path and not published:                # A 의 meta 까지 읽은 직후 B/B 가 정상 게시
            published.append(True)
            v.atomic_write_json(art2, ex.deg("attempt-B", 20.0))
            ex.write_meta(target, root2, art2, "attempt-B", starts=24)
        return text

    with patch.object(pathlib.Path, "read_text", after_meta):
        loaded2 = reader.load_degeneracy(root2 / "out")
    assert published, "meta 를 안 읽었다 — 이 순서를 못 쟀다"
    e2 = loaded2.get("100")
    assert e2 is not None, loaded2                               # A/A 는 온전했으니 표에 있어야 한다
    assert e2["j"]["run_id"] == "attempt-A" and e2["meta"]["run_id"] == "attempt-A", e2["meta"]["run_id"]
    assert e2["j"]["best_modes_percent"]["LLI"] == 1.0, e2["j"]["best_modes_percent"]
    return {"검증_중_게시": first,
            "검증_후_게시": {"data_run_id": e2["j"]["run_id"], "meta_run_id": e2["meta"]["run_id"],
                          "value": e2["j"]["best_modes_percent"]["LLI"], "disk_unit": pv.verify_unit(art2)}}


def a2_matrix_snapshot(ex, target, root, v, pv, reader):
    """원본 `matrix_after_verification` 과 같은 순서 — hook 을 현행 `_read_unit`(검증+읽기 한 자리) 로."""
    ex.fixture_repo(target, root)
    art = root / "out/matrix_100.csv"
    rows_a, rows_b = ex.mx("attempt-A", 1.0), ex.mx("attempt-B", 20.0)
    rows_b[1]["LLI_pct"] = 99.0                                  # B 의 폭을 다르게 (공통 오프셋이 아니라)
    v.atomic_write_csv(art, rows_a, list(rows_a[0]))
    ex.write_meta(target, root, art, "attempt-A")
    original, switched = reader._read_unit, []

    def scheduled(p):
        out = original(p)
        if p == art and not switched:                            # A 를 검증·스냅샷한 직후 B 의 데이터만 먼저 게시
            switched.append(True)
            v.atomic_write_csv(art, rows_b, list(rows_b[0]))
        return out

    with patch.object(reader, "_read_unit", scheduled):
        loaded = reader.load_matrix_axis(root / "out")
    final = pv.verify_unit(art)
    assert switched and final[0] is False, (switched, final)     # 디스크는 B 데이터 + A meta = 미완
    e = loaded.get("100")
    assert e is not None and e["per"]["GITT"]["LLI"] == 3.0, e   # 검증한 A 만 소비 (B 의 79 가 아니다)
    return {"A_verified_span": 3.0, "consumed_span": e["per"]["GITT"]["LLI"],
            "consumed_run_id": e["run_id"], "unit_after_publication": final}


def a3_modern_without_meta(ex, target, root, v, pv, reader, shape):
    """원본 `missing_modern_metadata` 의 fixture 그대로 — 판정만 '받아들인다' → '미완으로 거절한다'."""
    ex.fixture_repo(target, root)
    dfile, mfile = root / "out/degeneracy_100_Li.json", root / "out/matrix_100.csv"
    v.atomic_write_json(dfile, ex.deg("fresh-production-attempt", 7.0))
    rows = ex.mx("fresh-production-attempt", 5.0)
    v.atomic_write_csv(mfile, rows, list(rows[0]))               # write_meta 전에 중단된 첫 게시
    dcheck, mcheck = pv.verify_unit(dfile), pv.verify_unit(mfile)
    assert dcheck[0] is False and mcheck[0] is False, (dcheck, mcheck)
    ds, ms = reader.load_degeneracy(root / "out"), reader.load_matrix_axis(root / "out")
    assert ds == {} and ms == {}, (ds, ms)
    try:
        shape.fitted_pair_info(root / "out", "100", "GITT", "Li")
        raise AssertionError("ne_shape 가 미완 산출을 소비했다")
    except RuntimeError as e:
        refused = str(e)[:160]
    # 대조: run_id 없는 **옛** 산출은 호환 경로로 그대로 읽힌다
    legacy = root / "out/degeneracy_200_Li.json"
    legacy.write_text(json.dumps({"best_modes_percent": {k: 1.0 for k in reader.MODES},
                                  **{f"{k}_percent": {"span": 1.0} for k in reader.MODES}}), encoding="utf-8")
    assert pv.verify_unit(legacy)[0] is None and "200" in reader.load_degeneracy(root / "out")
    return {"modern_json_check": dcheck, "modern_csv_check": mcheck, "readers_excluded": True,
            "ne_shape_refused": refused, "legacy_without_run_id_still_read": True}


def a4_half_cell_late_identity(cl, target):
    """원본 `shape_and_matrix` 의 마지막 절 — 반쪽전지를 늦게 해시하던 자리. matrix 에 meta 를 붙여 (현행 규약) 진행한다."""
    ns = cl.load("r6_adapted_ne_shape", target / "scripts/ne_shape.py")
    with tempfile.TemporaryDirectory(prefix="bms-r6-adapted-shape-") as temp:
        base = pathlib.Path(temp)
        data, blend = cl.shape_inputs(base)
        selected = base / "out/matrix_100.csv"
        cl.matrix(selected, .16)
        _sign(selected)                                          # 현행 규약: run_id 열이 있으면 meta 가 있어야 한다
        half = data / "data/half_cell/GITT/100.xlsx"
        half_A = cl.sha(half)
        real_load = ns.D.load_literature

        def finish_new_half_export(root, source, **kw):           # 문헌 배열을 읽은 뒤 반쪽전지 B 를 재-export
            arrays = real_load(root, source, **kw)
            cl.write_half(half, blend, .45, pe_offset=.02)
            return arrays

        with patch.object(ns.D, "load_literature", side_effect=finish_new_half_export):
            raced, raced_meta = cl.run_shape(ns, base, data)
        normal_B, meta_B = cl.run_shape(ns, base, data)
        rec = raced_meta["consumed_inputs"]["100"]["half_cell"]
        pe_raced, pe_B = float(raced["pe_shape_max_mV"]), float(normal_B["pe_shape_max_mV"])
        assert pe_raced == 0. and pe_B == 20., (pe_raced, pe_B)   # 값은 A 로 계산됐다 (원본과 같은 관측)
        assert rec["sha256"] == half_A != cl.sha(half), (rec["sha256"][:12], half_A[:12])   # 서명도 A 여야 한다
        assert rec != meta_B["consumed_inputs"]["100"]["half_cell"]
        return {"A_value_PE_change_mV": pe_raced, "B_value_PE_change_mV": pe_B,
                "recorded_sha_is_A": True, "A_hash": half_A[:16], "disk_now": cl.sha(half)[:16]}


def a5_full_cell_build_signature(cl, target):
    """원본 `fullcell_build_signature` — mock 이 현행 `identity=` 를 받게만 고치고, 판정을 'A값이면 A서명' 으로."""
    import numpy as np, pandas as pd
    from bms_balancing import verify
    with tempfile.TemporaryDirectory(prefix="bms-r6-adapted-build-") as temp:
        data = pathlib.Path(temp)
        subprocess.run([sys.executable, str(target / "matlab/tests/gen_synth_xlsx.py"), str(data)],
                       check=True, capture_output=True, text=True)
        original = verify.build(data, "GITT", "200", "Li", w_dqdv=1., scale_seed=0)
        workbook = verify.D.full_cell_workbook(data)
        A_hash = cl.sha(workbook)
        real_load = verify.D.load_full_cell

        def finish_new_fullcell_export(root, state, workbook=None, **kw):
            arrays = real_load(root, state, workbook=workbook, **kw)
            frame = pd.read_excel(workbook, header=None)
            col = 2 * verify.D.FULL_COL[state] + 1
            frame.iloc[2:, col] = pd.to_numeric(frame.iloc[2:, col], errors="coerce") + .020
            tmp = workbook.with_name(workbook.stem + ".new.xlsx")
            frame.to_excel(tmp, header=False, index=False)
            os.replace(tmp, workbook)
            return arrays

        with patch.object(verify.D, "load_full_cell", side_effect=finish_new_fullcell_export):
            raced = verify.build(data, "GITT", "200", "Li", w_dqdv=1., scale_seed=0)
        normal_B = verify.build(data, "GITT", "200", "Li", w_dqdv=1., scale_seed=0)
        assert np.array_equal(raced.voltage, original.voltage)                  # 값은 A (원본과 같은 관측)
        assert raced.consumed_inputs["full_cell"]["sha256"] == A_hash != cl.sha(workbook)
        assert raced.inputs_sha == original.inputs_sha != normal_B.inputs_sha   # 서명도 A
        return {"raced_arrays_match_A": True, "recorded_full_cell_is_A": True,
                "A_hash": A_hash[:16], "disk_now": cl.sha(workbook)[:16],
                "inputs_sha_raced": raced.inputs_sha[:16], "inputs_sha_B": normal_B.inputs_sha[:16]}


def a6_inference_closure(target):
    """받은 `inference` 스크립트는 `degeneracy_300_0009_Li_v2.json` 이 **있어야** 돈다 (R6-04 로 archive 로 옮겼다).
    없는 이름은 건너뛰도록 **한 줄만** 고친 사본으로 돌려, §3-4 격자·U14 대조·문턱 표가 정본 이름에서도 그대로인지 본다."""
    src = (HERE / "harness_r6_final_inference_repros.py").read_text(encoding="utf-8")
    old = '    for filename in ("degeneracy_300_0009_Li_v2.json", "degeneracy_300_0009_Li.json"):'
    assert src.count(old) == 1
    new = (old + "\n"
           '        if not (root / "out" / filename).is_file():\n'
           "            continue                                  # 적응: `_vN` 은 out/archive/ 로 갔다 (Codex R6-04)")
    baseline = pathlib.Path(os.environ.get("R6_OLD_OUT", ""))
    with tempfile.TemporaryDirectory(prefix="r6-adapted-inference-") as tmp:
        copy = pathlib.Path(tmp) / "inference_adapted.py"
        copy.write_text(src.replace(old, new), encoding="utf-8")
        cmd = [sys.executable, str(copy), "--target", str(target)]
        if baseline.is_dir():
            cmd += ["--old", str(baseline)]
        else:
            cmd += ["--case", "derived"]                          # --old 없으면 u14/table 은 못 돈다
        r = subprocess.run(cmd, capture_output=True, text=True)
        assert r.returncode == 0, (r.returncode, r.stderr.strip().splitlines()[-3:])
        keys = [l.split(" ", 1)[0] for l in r.stdout.splitlines() if l and not l.startswith(" ")]
        return {"rc": 0, "cases": keys, "baseline_used": baseline.is_dir(),
                "note": "한 줄 적응: 없는 `_vN` 이름은 건너뛴다"}


def _sign(path):
    """현행 규약의 최소 meta 사이드카 (run_id 열이 있는 산출은 meta 가 있어야 소비된다)."""
    import csv as _csv
    rid = next(iter({r.get("run_id") for r in _csv.DictReader(path.open(encoding="utf-8-sig"))} - {None, ""}), None)
    meta = {"run_id": rid, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "artifact": path.name,
            "env": {}, "started_utc": "", "git_commit_at_start": "", "git_state_changed_during_run": False}
    path.with_name(path.name + ".meta.json").write_text(json.dumps(meta), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=pathlib.Path, required=True)
    ap.add_argument("--output", type=pathlib.Path)
    a = ap.parse_args()
    target = a.target.resolve()
    sys.path.insert(0, str(target)); sys.path.insert(0, str(target / "scripts"))
    head = subprocess.check_output(["git", "-C", str(target), "rev-parse", "HEAD"], text=True).strip()
    ex = _load("r6_codex_exec", HERE / "harness_r6_final_execution_repros.py")
    cl = _load("r6_codex_claims", HERE / "harness_r6_final_claims_repros.py")
    from bms_balancing import verify as v                        # noqa: E402
    import provenance as pv                                      # noqa: E402
    reader = ex.load("r6_reader", target / "scripts/compare_states.py")
    shape = ex.load("r6_shape", target / "scripts/ne_shape.py")
    out = {"target_head": head, "probes": {}}
    with tempfile.TemporaryDirectory(prefix="r6-adapted-") as tmp:
        mk = lambda n: (pathlib.Path(tmp) / n, (pathlib.Path(tmp) / n).mkdir())[0]
        for name, fn in (
            ("R6-01a 독자는 자기가 검증한 묶음만 (degeneracy)", lambda: a1_degeneracy_snapshot(ex, target, mk("a1"), v, pv, reader)),
            ("R6-01b 검증 뒤 게시된 B 를 안 읽는다 (matrix)", lambda: a2_matrix_snapshot(ex, target, mk("a2"), v, pv, reader)),
            ("R6-02 현행 산출 + meta 없음 = 미완 거절", lambda: a3_modern_without_meta(ex, target, mk("a3"), v, pv, reader, shape)),
            ("R6-03a 반쪽전지: A값이면 A서명", lambda: a4_half_cell_late_identity(cl, target)),
            ("R6-03b 풀셀 build: A값이면 A서명", lambda: a5_full_cell_build_signature(cl, target)),
            ("R6-04 inference 닫힘 확인(정본 이름으로)", lambda: a6_inference_closure(target)),
        ):
            st, detail = _guard(fn)
            out["probes"][name] = {"상태": st, "세부": detail}
    text = json.dumps(out, ensure_ascii=False, indent=2)
    print(text)
    if a.output:
        a.output.write_text(text + "\n", encoding="utf-8")
    return 0 if all(p["상태"] == "닫힘" for p in out["probes"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
