"""Codex R6 닫음의 변이 감사 — 각 수정을 되돌리면 그 RED 테스트가 다시 실패해야 한다. bms-balancing/ 에서 `python3 reviews/r6_repros/codex_r6_mutation_audit.py`."""
import pathlib, shutil, subprocess, sys
ROOT = pathlib.Path(".").resolve()
def run(k):
    r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_r6_internal.py", "-q", "--no-header",
                        "-p", "no:cacheprovider", "-k", k], capture_output=True, text=True)
    return r.returncode, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]
def mutate(path, old, new):
    p = ROOT / path; s = p.read_text(encoding="utf-8")
    assert s.count(old) == 1, (path, old[:60], s.count(old)); p.write_text(s.replace(old, new), encoding="utf-8")
M = [
 ("R6-01 read_unit 이 검증 뒤 경로를 다시 읽는다", "c6_01", "scripts/provenance.py",
  "    ok, why = verify_unit_bytes(p.name, data, meta, rid)\n    return ok, why, data, meta",
  "    ok, why = verify_unit_bytes(p.name, data, meta, rid)\n    return ok, why, p.read_bytes(), meta"),
 ("R6-02 현행 산출 + meta 없음 → 옛 산출로", "c6_02", "scripts/provenance.py",
  "    if meta is None:\n        if modern:\n            return False,",
  "    if meta is None:\n        if False:\n            return False,"),
 ("R6-03 build: 파싱 뒤 경로를 다시 열어 해시", "c6_03", "bms_balancing/data.py",
  "    src = read_input(workbook or full_cell_workbook(root))\n    if identity is not None:\n        identity.update(src.identity())\n    df = pd.read_excel(src.stream(), header=None, skiprows=2)",
  "    wbp = workbook or full_cell_workbook(root)\n    src = read_input(wbp)\n    df = pd.read_excel(src.stream(), header=None, skiprows=2)\n    if identity is not None:\n        import hashlib as _h\n        identity.update({\"path\": str(wbp), \"sha256\": _h.sha256(Path(wbp).read_bytes()).hexdigest()})"),
 ("R6-03 ne_shape: 반쪽전지 identity 를 다시 열어 해시", "c6_03", "scripts/ne_shape.py",
  "                    \"half_cell\": hb[s].identity()}",
  "                    \"half_cell\": {\"path\": hb[s].path, \"sha256\": __import__('hashlib').sha256(pathlib.Path(hb[s].path).read_bytes()).hexdigest()}}"),
 ("R6-04 가장 높은 _vN 을 정본으로", "c6_04", "scripts/compare_states.py",
  "        if VER.search(f.stem):\n            print(f\"  ! {f.name}: 판 번호가 붙은 옛 산출 — 정본은 unversioned 이름 하나다; `out/archive/` 로 옮길 것 \"\n                  f\"(Codex R6-04)\", file=sys.stderr)\n            continue\n        yield f",
  "        if VER.search(f.stem):\n            yield f\n            continue\n        if list(d.glob(f\"{f.stem}_v[0-9]*{f.suffix}\")):\n            continue\n        yield f"),
 ("R6-05 -z 경로를 ' -> ' 로 쪼갬", "c6_05", "scripts/provenance.py",
  "        rel = ln[3:]\n", "        rel = ln[3:].split(\" -> \")[-1].strip()\n"),
 ("R6-06 원장이 '적은 시작' 을 산 문장으로", "c6_06", "reviews/R6_LEDGER.md",
  "돈다 — 시작 예산이\n적어서 움직인 것이 **아니다**.", "돈다 — 시작 예산이\n적어서 움직인 것이 **아니다**. 적은 시작 탓이다."),
 ("Q3 §1-8 이 '충돌은 항상 partial' 로", "c6_q3", "FINDINGS.md",
  "**옵션이 선언은 못 흡수하는 차이를 흡수한 셀이 있을 때만**\npartial(3)", "충돌은 R4-02 Q3 대로 partial\n(3)"),
]
rc, last = run("c6_0 or c6_q3")
print("baseline:", rc, last); assert rc == 0
bad = 0
for what, k, path, old, new in M:
    bak = (ROOT / path).read_bytes()
    try:
        mutate(path, old, new)
        rc, last = run(k)
        ok = rc != 0
        print(("CAUGHT " if ok else "MISSED ") + f"| {what} | {k} | {last}")
        bad += (not ok)
    finally:
        (ROOT / path).write_bytes(bak)
rc, last = run("c6_0 or c6_q3")
print("restored:", rc, last)
print("MISSED:", bad)
