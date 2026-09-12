"""Codex R6 닫음의 변이 감사 — 각 수정을 되돌리면 그 RED 테스트가 다시 실패해야 한다.

    bms-balancing/ 에서 `python3 reviews/r6_repros/codex_r6_mutation_audit.py`

⚠ Codex R7-06: 놓친 변이가 있거나 복구 뒤 회귀가 실패하면 **비영 종료**한다 (전 판은 `MISSED: 1` 을 찍고도 rc 0 —
  자동화가 그 실패를 못 봤다). import 만으로는 아무것도 돌지 않는다 (전 판은 모듈을 불러오면 감사가 통째로 돌았다).
"""
import pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]


def run(k):
    r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_r6_internal.py", "-q", "--no-header",
                        "-p", "no:cacheprovider", "-k", k], capture_output=True, text=True)
    return r.returncode, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]


def mutate(path, old, new):
    p = ROOT / path; s = p.read_text(encoding="utf-8")
    assert s.count(old) == 1, (path, old[:60], s.count(old)); p.write_text(s.replace(old, new), encoding="utf-8")
MUTATIONS = [
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
 # ⚠ Codex R7 §4: 전 판의 이 변이는 `_vN` 파일명 때문에 state 가 **사라져** KeyError 로 잡혔다 — "옛 값을 실제로
 # 소비했다" 는 반례가 아니었다. 그래서 옛 `_keep_latest` 규칙을 그대로 되살린다 (판 번호를 떼고 최고판을 고른다).
 ("R6-04 옛 규칙: 가장 높은 _vN 을 정본으로 (이름은 unversioned 로 환원)", "c6_04", "scripts/compare_states.py",
  "    for f in sorted(d.glob(pattern)):\n        if f.name.endswith(\".meta.json\"):\n            continue",
  "    best = {}\n    for f in sorted(d.glob(pattern)):\n        if f.name.endswith(\".meta.json\"):\n            continue\n        m = VER.search(f.stem)\n        key = VER.sub(\"\", f.stem)\n        n = int(m.group(1)) if m else 1\n        if n >= best.get(key, (0, None))[0]:\n            best[key] = (n, f)\n    for key, (n, f) in sorted(best.items()):\n        if n > 1:\n            f = f.rename(f.with_name(key + f.suffix)) if False else f\n        yield f\n    return\n    for f in sorted(d.glob(pattern)):\n        if f.name.endswith(\".meta.json\"):\n            continue"),
 ("R6-05 -z 경로를 ' -> ' 로 쪼갬", "c6_05", "scripts/provenance.py",
  "        rel = ln[3:]\n", "        rel = ln[3:].split(\" -> \")[-1].strip()\n"),
 ("R6-06 원장이 '적은 시작' 을 산 문장으로", "c6_06", "reviews/R6_LEDGER.md",
  "돈다. ~~적은 시작으로 푸는 구조라~~ 는", "돈다. 적은 시작으로 푸는 구조라 움직였다. ~~적은 시작으로 푸는 구조라~~ 는"),
 ("Q3 §1-8 이 '충돌은 항상 partial' 로", "c6_q3", "FINDINGS.md",
  "**옵션이 선언은 못 흡수하는 차이를 흡수한 셀이 있을 때만**\npartial(3)", "충돌은 R4-02 Q3 대로 partial\n(3)"),
]


def main() -> int:
    rc, last = run("c6_0 or c6_q3")
    print("baseline:", rc, last)
    assert rc == 0, last
    bad = 0
    for what, k, path, old, new in MUTATIONS:
        bak = (ROOT / path).read_bytes()
        try:
            mutate(path, old, new)
            rc_m, last_m = run(k)
            ok = rc_m != 0
            print(("CAUGHT " if ok else "MISSED ") + f"| {what} | {k} | {last_m}")
            bad += (not ok)
        finally:
            (ROOT / path).write_bytes(bak)
    rc, last = run("c6_0 or c6_q3")
    print("restored:", rc, last)
    print("MISSED:", bad)
    if rc != 0:
        print("! 복구 뒤 회귀가 실패했다 — 트리가 원상태가 아니다")
    return 1 if (bad or rc != 0) else 0


if __name__ == "__main__":
    sys.exit(main())
