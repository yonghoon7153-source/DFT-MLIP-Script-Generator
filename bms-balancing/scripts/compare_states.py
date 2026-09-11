"""상태·셀을 가로질러 축퇴 폭을 견준다 — §1-10 의 표를 만드는 명령.

왜 스크립트인가: 이 비교를 손으로 하면 그 숫자가 **문서에만 있는 주장**이 된다.
§2 에서 이미 한 번 그렇게 됐고(97 행 원표가 없어 재현이 안 됐다) 그것을
`audit97.py` 로 닫았다. 같은 규율을 여기에도 적용한다.

    python3 scripts/compare_states.py out
    python3 scripts/compare_states.py pouch=out c168=~/dd/cells/c168/out \\
                                      c171=~/dd/cells/c171/out

읽는 것
  `degeneracy_<state>_<si>.json` — 근최적 집합 위의 LAM/LLI 폭 (모델 고정 축)
  `matrix_<state>.csv`           — 모델 선택(Si 8 종)이 만드는 폭 (다른 축)

⚠ 두 축은 **다른 것을 잰다.** 같은 표에 나란히 놓되 합치지 않는다.
⚠ `.meta.json` 이 있으면 설정을 같이 찍는다. 설정이 다른 행끼리는 비교 금지다.
"""
from __future__ import annotations
import csv, json, pathlib, re, sys

MODES = ("LAM_PE", "LAM_NE", "LLI")


#: 산출 이름 뒤에 `_v2` 같은 판 번호가 붙는다. **최신 판만** 쓴다.
#: 2026-09-10 에 이 저장소에서 옛 판을 읽고 쓴 실수가 세 번 있었다
#: (README 의 8.93 %p, matlab/README 의 dump 표, 그리고 이 스크립트 첫 판).
VER = re.compile(r"_v(\d+)$")


def _split_version(stem: str) -> tuple[str, int]:
    m = VER.search(stem)
    return (stem[:m.start()], int(m.group(1))) if m else (stem, 1)


def _keep_latest(cands: dict) -> dict:
    """{(키, 판): 값} → 키마다 가장 높은 판만."""
    best = {}
    for (key, ver), val in cands.items():
        if key not in best or ver > best[key][0]:
            best[key] = (ver, val)
    return {k: v for k, (_, v) in best.items()}


def _unit_ok(f: pathlib.Path):
    """R6 내부 F07 (Codex R5-04 의 reader 절): 산출물과 meta 가 한 시도의 묶음이 아니면 표에 넣지 않는다.
    meta 가 없거나 옛 meta(run_id/sha256 없음)면 None — 전과 같이 읽는다."""
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from provenance import verify_unit
    ok, why = verify_unit(f)
    if ok is False:
        print(f"  ! {f.name}: 묶음 불일치 ({why}) — 표에서 뺀다 (R6 내부 F07)", file=sys.stderr)
    return ok


def load_degeneracy(d: pathlib.Path) -> dict:
    cands = {}
    for f in sorted(d.glob("degeneracy_*.json")):
        stem, ver = _split_version(f.stem)
        m = re.match(r"degeneracy_(.+)_([A-Za-z]+)$", stem)
        if not m:
            continue
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  ! {f.name} 이 JSON 이 아니다 — 중간에 죽은 산출인가?",
                  file=sys.stderr)
            continue
        if _unit_ok(f) is False:
            continue
        meta = pathlib.Path(str(f) + ".meta.json")
        cands[(m.group(1), ver)] = {
            "si": m.group(2), "j": j, "version": ver, "file": f.name,
            "meta": json.loads(meta.read_text(encoding="utf-8"))
                    if meta.is_file() else None}
    return _keep_latest(cands)


def load_matrix_axis(d: pathlib.Path) -> dict:
    """`matrix_<state>.csv` 에서 **한 축만** 꺼낸다: 반쪽전지 하나 · dQ/dV 끔 · Si 8 종."""
    cands = {}
    for f in sorted(d.glob("matrix_*.csv")):
        stem, ver = _split_version(f.stem)
        st = stem[len("matrix_"):]
        if _unit_ok(f) is False:
            continue
        rows = [r for r in csv.DictReader(f.open(encoding="utf-8"))
                if r.get("w_dqdv") and float(r["w_dqdv"]) == 0]
        if not rows:
            continue
        by_src = {}
        for r in rows:
            by_src.setdefault(r["half_cell"], []).append(r)
        per = {}
        for src, rs in by_src.items():
            free = [r for r in rs if not (r.get("bounds") or "").strip("-")
                    and not (r.get("ref_bounds") or "").strip("-")]
            per[src] = {
                "n": len(rs), "n_free": len(free),
                **{k: (max(float(r[f"{k}_pct"]) for r in rs)
                       - min(float(r[f"{k}_pct"]) for r in rs)) for k in MODES},
                **{f"{k}_free": (max(float(r[f"{k}_pct"]) for r in free)
                                 - min(float(r[f"{k}_pct"]) for r in free))
                   if len(free) > 1 else None for k in MODES}}
        cands[(st, ver)] = {"per": per, "version": ver, "file": f.name}
    return _keep_latest(cands)


def main() -> int:
    args = sys.argv[1:] or ["out"]
    roots = {}
    for a in args:
        label, _, path = a.partition("=")
        roots[label if path else "out"] = pathlib.Path(path or label).expanduser()

    print("=" * 78)
    print("A. 근최적 집합 위의 폭 — **모델을 고정**했을 때 데이터가 못 가르는 만큼")
    print("=" * 78)
    ok_llI_narrowest = True
    for label, d in roots.items():
        deg = load_degeneracy(d)
        if not deg:
            print(f"\n[{label}] {d} — degeneracy 산출 없음"); continue
        print(f"\n[{label}] {d}")
        srcs = set()
        # ⚠ 2026-09-11 Codex R2-04: `best ± span/2` 는 best 를 중점처럼 보이게 한다.
        #   best 는 경계해에서 구간의 끝점이라 (c168 300_0009 LAM_NE: [2.30, 11.00] 을
        #   2.30±4.35 로 찍어 [−2.05, 6.65] 로 읽혔다) 산출의 min/max 를 그대로 찍는다.
        print(f"  {'state':12}{'src':10}{'LAM_PE best [min,max]':>25}{'LAM_NE':>25}{'LLI':>25}"
              f"  {'최광':7} 파일")
        for st, e in deg.items():
            j = e["j"]
            spans = {k: j[f"{k}_percent"]["span"] for k in MODES}
            best = j["best_modes_percent"]
            widest = max(spans, key=spans.get)
            narrow = min(spans, key=spans.get)
            if narrow != "LLI":
                ok_llI_narrowest = False
            src = j.get("half_cell", "?")
            srcs.add(src)
            cells = "".join(f"{best[k]:8.2f} [{j[f'{k}_percent']['min']:.2f}, "
                            f"{j[f'{k}_percent']['max']:.2f}]".rjust(25) for k in MODES)
            print(f"  {st:12}{src:10}{cells}  {widest:7} {e['file']}")
            b = j.get("best_active_bounds") or []
            rb = j.get("ref_active_bounds") or []
            if b or rb:
                print(f"  {'':12}⚠ 경계 — 대상 {b or '—'} · 기준 {rb or '—'}")
            if e["meta"] and e["meta"].get("starts", 24) < 24:
                print(f"  {'':12}⚠ starts={e['meta']['starts']} — 시험 산출이다")
        if len(srcs) > 1:
            print(f"  ⚠ **반쪽전지 소스가 섞였다** ({', '.join(sorted(srcs))}) — 이 표의")
            print(f"    상태들을 서로 비교하지 마라. 소스가 바뀌면 `E_PE` 가 바뀌고")
            print(f"    그러면 LAM_PE 가 다른 것을 재게 된다 (`prepare_cell.py` 머리말 2번).")
            print(f"    같은 소스끼리만 묶어서 읽을 것.")

    print("\n" + "=" * 78)
    print("B. 모델 선택(Si 8 종)이 만드는 폭 — **다른 축**이다. 위와 합치지 말 것")
    print("=" * 78)
    for label, d in roots.items():
        mx = load_matrix_axis(d)
        if not mx:
            print(f"\n[{label}] matrix 산출 없음"); continue
        print(f"\n[{label}]")
        print(f"  {'state':12}{'source':11}{'n':>3}{'자유':>5}"
              f"{'LAM_PE':>9}{'LAM_NE':>9}{'LLI':>9}{'LLI(자유)':>11}   파일")
        for st, e in mx.items():
            for src, v in e["per"].items():
                fr = v["LLI_free"]
                print(f"  {st:12}{src:11}{v['n']:>3}{v['n_free']:>5}"
                      f"{v['LAM_PE']:>9.3f}{v['LAM_NE']:>9.3f}{v['LLI']:>9.3f}"
                      f"{(f'{fr:.3f}' if fr is not None else '—'):>11}"
                      f"   {e['file']}")

    print("\n" + "=" * 78)
    print("판정")
    print("=" * 78)
    print(f"  A 축에서 LLI 가 **항상 가장 좁은가**: "
          f"{'예' if ok_llI_narrowest else '**아니오** — 상태에 따라 뒤집힌다'}")
    print("  ⚠ 상대 불확실성(폭/최적값)은 열화가 쌓이면 분모가 커져 작아진다.")
    print("     상태를 가로질러 말할 때는 **절대 폭(%p)** 으로 말할 것.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
