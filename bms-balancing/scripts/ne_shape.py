"""측정된 음극 OCP 가 열화하면서 **모양이 바뀌는가** — γ_Si 를 자유 파라미터로
둘 근거가 있는지 직접 본다.

## 왜 이 질문인가

목적함수는 음극을 **문헌 순수 Si + 순수 Gr 을 γ 로 섞어** 만든다. 그런데 이
셀의 음극은 **실제로 측정돼 있다** (`data/half_cell/<src>/<state>.xlsx` 의
`NE_capacity`/`NE_voltage`). 측정본은 γ 초기값 잡는 데만 쓰인다.

γ 를 자유롭게 두는 정당한 이유는 하나다: 열화하면서 음극 OCP **모양 자체가
바뀌니까** (Si 가 먼저 죽으면 유효 Si 분율이 준다). 파우치 셀은 반쪽전지를
상태마다 따로 쟀으므로 그 전제를 직접 확인할 수 있다.

    측정 곡선이 겹친다   -> γ 를 자유로 둘 근거가 약하다. 측정본을 쓰면
                           '문헌 곡선 선택' 축이 통째로 사라진다
    측정 곡선이 갈린다   -> γ 가 흡수할 실체가 있다. 그러면 적합된 γ 가 그
                           변화를 실제로 따라가는지가 다음 질문

## 무엇을 재나

pristine 대비 각 상태에서
  (a) **측정** E_NE(x) 의 변화량   — 실제로 일어난 일
  (b) **모델** Blend.E(x, γ_적합) 의 변화량 — γ 가 만들어 낸 변화

(b) 가 (a) 보다 훨씬 크면, γ 는 음극 모양 변화를 따라가는 것이 아니라 다른
것을 흡수하고 있다는 뜻이다.

⚠ 둘은 다른 물건이다 (측정본은 실제 음극, 블렌드는 대용품). 그래서 **절대
  값이 아니라 pristine 대비 변화량**을 견준다.

    python3 scripts/ne_shape.py --source GITT --si-source Li
"""
from __future__ import annotations
import argparse, csv, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))  # provenance

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from bms_balancing import data as D                      # noqa: E402
from bms_balancing.model import Blend, HalfCell          # noqa: E402

GRID = np.linspace(0.02, 0.98, 400)     # 양 끝은 외삽이라 뺀다


def fitted_pair(out_dir: pathlib.Path, state: str, src: str,
                si: str) -> tuple[float, float] | None:
    """`matrix_<state>.csv` 의 **한 행에서** (그 상태의 γ, 그 실행의 기준 γ).

    ⚠ 짝을 같은 행에서 꺼내는 것이 중요하다. `matrix` 는 조합마다 pristine 을
      **다시 적합**하므로, 기준 γ 가 파일마다·조합마다 다르다. 다른 행의 기준을
      가져다 쓰면 있지도 않은 변화를 만들어 낸다.
      (그리고 `matrix_pristine.csv` 는 애초에 없다 — pristine 은 상태가 아니라
      매 실행의 기준이다. 첫 판이 그걸 찾다가 전부 nan 을 냈다.)
    """
    for f in sorted(out_dir.glob(f"matrix_{state}*.csv"), reverse=True):
        for r in csv.DictReader(f.open(encoding="utf-8")):
            if (r.get("half_cell") == src and r.get("si") == si
                    and float(r.get("w_dqdv", 1)) == 0):
                if not r.get("ref_gamma_Si"):
                    return None          # 옛 판 산출 — ref_* 열이 없다
                return float(r["gamma_Si"]), float(r["ref_gamma_Si"])
    return None


def raw_ne_capacity(path: pathlib.Path) -> float:
    """정규화 **전** 음극 용량. (a) 의 변화가 모양 탓인지 용량 탓인지 가르려고."""
    import pandas as pd
    df = pd.read_excel(path)
    c = pd.to_numeric(df["NE_capacity"], errors="coerce").dropna().to_numpy()
    return float(c.max()) if c.size else float("nan")


def _write_csv(d: pathlib.Path, a, rows, cap, base_cap, cwhere) -> pathlib.Path:
    """표를 그대로 CSV 로. 옆에 `.meta.json` 을 같이 둔다 (run_states.sh 와 같은 규약).

    `cap_delta_pct` 를 **반드시 같이** 남긴다 — `(a) 측정변화` 는 정규화 뒤
    값이라 용량이 크게 변한 상태에서는 순수한 OCP 모양 변화로 읽으면 안 된다.
    그 한정어가 CSV 에서 떨어지면 숫자만 인용된다.
    """
    import datetime, json
    d.mkdir(parents=True, exist_ok=True)
    art = d / f"ne_shape_{a.source}_{a.si_source}.csv"
    with art.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["state", "cap_delta_pct", "gamma_ref",
                    "measured_shape_mV", "gamma_shape_mV", "ratio_b_over_a",
                    "blend_vs_meas_max_mV", "blend_vs_meas_rms_mV",
                    "max_at_x", "frac_over_50mV"])
        for s_, da, db, ratio, cmax, crms, g in rows:
            c = cwhere.get(s_)
            w.writerow([s_, f"{100*(cap[s_]/base_cap-1):.4f}",
                        f"{g:.6f}" if g is not None else "",
                        f"{da:.6f}", f"{db:.6f}", f"{ratio:.6f}",
                        f"{cmax:.6f}", f"{crms:.6f}",
                        f"{c[1]:.4f}" if c else "", f"{c[2]:.4f}" if c else ""])
    from provenance import git_state          # scripts/ 가 sys.path 에 있다
    sha, dirty = git_state()
    (art.parent / (art.name + ".meta.json")).write_text(json.dumps({
        "artifact": art.name, "half_cell_source": a.source,
        "si_source": a.si_source, "grid_n": int(GRID.size),
        "grid_range": [float(GRID[0]), float(GRID[-1])],
        "gamma_from": f"{a.out_dir}/matrix_<state>.csv 의 ref_gamma_Si",
        "note": "measured_shape_mV 는 정규화 뒤 값 — cap_delta_pct 와 함께 읽을 것",
        "git_commit": sha, "git_dirty": dirty,
        "created_utc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return art


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default=None)
    ap.add_argument("--source", default="GITT", choices=list(D.HALF_FILE))
    ap.add_argument("--si-source", default="Li", choices=D.SI_SOURCES)
    ap.add_argument("--out-dir", default="out")
    # ⚠ 이 스크립트는 오래 **출력만** 했다. 그러면 여기서 나온 수치를
    #   FINDINGS 에 적어도 테스트가 재계산할 수 없고, 그건 이 저장소가
    #   반복해서 당한 드리프트 구조다 (정본은 artifact). 그래서 남긴다.
    ap.add_argument("--write", default="out", metavar="DIR",
                    help="산출 CSV 를 쓸 곳. 빈 문자열이면 안 쓴다")
    a = ap.parse_args()

    root = D.data_root(a.data_root)
    out_dir = pathlib.Path(a.out_dir)
    states = [s for s in D.STATES
              if D.half_cell_path(root, a.source, s).is_file()]
    if "pristine" not in states:
        raise SystemExit(f"`{a.source}` 에 pristine 이 없다 — 기준이 없으면 못 잰다")

    meas = {s: HalfCell(D.half_cell_path(root, a.source, s),
                        window=11, poly_order=3).E_NE(GRID) for s in states}
    cap = {s: raw_ne_capacity(D.half_cell_path(root, a.source, s)) for s in states}
    si_c, si_v, gr_c, gr_v = D.load_literature(root, a.si_source)
    blend = Blend(si_c, si_v, gr_c, gr_v, window=11, poly_order=3)

    print(f"반쪽전지 {a.source} · 문헌 Si {a.si_source} · 상태 {len(states)}개")
    print(f"기준은 pristine. 격자 x={GRID[0]:.2f}~{GRID[-1]:.2f} ({GRID.size}점)\n")

    base_m, base_cap = meas["pristine"], cap["pristine"]
    print(f"{'state':10}{'용량 Δ%':>9}{'γ':>8}"
          f"{'(a) 측정변화':>13}{'(b) γ변화':>11}{'(b)/(a)':>9}"
          f"{'(c) |블렌드−측정|':>19}")
    print(f"{'':10}{'':9}{'':8}{'max mV':>13}{'max mV':>11}{'':9}"
          f"{'max mV':>13}{'rms mV':>6}")
    pr = fitted_pair(out_dir, states[1] if len(states) > 1 else "100",
                     a.source, a.si_source)
    if pr is not None:
        dc = (blend.E(GRID, pr[1]) - base_m) * 1e3
        print(f"{'pristine':10}{0.0:>9.2f}{pr[1]:>8.4f}"
              f"{'—':>13}{'—':>11}{'—':>9}"
              f"{np.max(np.abs(dc)):>13.1f}{np.sqrt(np.mean(dc**2)):>6.1f}")
    rows, flips, cwhere = [], [], []
    for s in states:
        if s == "pristine":
            continue
        da = float(np.max(np.abs(meas[s] - base_m))) * 1e3
        pair = fitted_pair(out_dir, s, a.source, a.si_source)
        if pair is None:
            db, ratio, g, gr = float("nan"), float("nan"), None, None
        else:
            g, gr = pair
            db = float(np.max(np.abs(blend.E(GRID, g) - blend.E(GRID, gr)))) * 1e3
            ratio = db / da if da > 0 else float("inf")
        # (c) **절대 일치** — 모델은 음극 OCP 를 Blend(x, γ) 라고 주장한다.
        #     a_NE·b_NE 는 풀셀 Q 를 전극 x 로 옮길 뿐 **곡선 모양을 못 고친다.**
        #     그러니 이 둘은 그냥 맞아야 한다. 안 맞으면 γ 로도 못 고치고
        #     그 차이는 a_NE·b_NE 로 밀려난다 — 그것이 LAM_NE·LLI 다.
        #   ⚠ **방향 규약**을 먼저 배제한다. `HalfCell` 은 끝점 둘로 방향을
        #     정하고, `Blend` 는 q 를 정렬한다. 둘의 x=0 이 반대 끝을 뜻하면
        #     (c) 가 거대하게 나오고 그것을 "블렌드가 틀렸다" 로 읽게 된다.
        #     그래서 뒤집은 것도 같이 재고 **작은 쪽**을 쓴다.
        if g is not None:
            be = blend.E(GRID, g)
            d_f = (be - meas[s]) * 1e3
            d_r = (be - meas[s][::-1]) * 1e3
            fwd = float(np.max(np.abs(d_f)))
            rev = float(np.max(np.abs(d_r)))
            flipped = rev < fwd
            dc = d_r if flipped else d_f
            cmax, crms = float(np.max(np.abs(dc))), float(np.sqrt(np.mean(dc ** 2)))
            # **어디가** 어긋나는지. max 만 보면 "모양이 아니다" 로 읽히지만,
            # rms 가 훨씬 작으면 어긋남이 **좁은 구간에 몰린** 것이고 그건
            # 전혀 다른 이야기다 (2026-09-10: max 70~147 mV 인데 rms 는
            # 19~24 mV 로 거의 일정했다 — 그걸 놓칠 뻔했다).
            xa = float(GRID[int(np.argmax(np.abs(dc)))])
            over = float(np.mean(np.abs(dc) > 50) * 100)
            cwhere.append((s, xa, over))
            if flipped:
                flips.append((s, fwd, rev))
        else:
            cmax = crms = float("nan")
        rows.append((s, da, db, ratio, cmax, crms, g))
        print(f"{s:10}{100*(cap[s]/base_cap-1):>9.2f}"
              f"{(f'{g:.4f}' if g is not None else '—'):>8}"
              f"{da:>13.2f}{db:>11.2f}{ratio:>9.2f}{cmax:>13.1f}{crms:>6.1f}")

    if a.write:
        art = _write_csv(pathlib.Path(a.write), a, rows, cap, base_cap,
                         {c[0]: c for c in cwhere})
        print(f"\n→ {art}")

    print()
    ok = [r for r in rows if r[3] == r[3]]
    if not ok:
        print("γ 짝을 못 찾았다 — `--out-dir` 에 `ref_gamma_Si` 열이 있는")
        print("matrix_<state>.csv 가 있어야 한다 (v2 이후 산출).")
        return 1
    worst = max(ok, key=lambda r: r[3])
    print(f"측정된 음극 모양 변화 최대 {max(r[1] for r in ok):.2f} mV,")
    print(f"γ 가 만들어 낸 모델 변화 최대 {max(r[2] for r in ok):.2f} mV.")
    if worst[3] > 3:
        print(f"\n→ 모델 변화가 측정 변화의 **{worst[3]:.1f} 배** ({worst[0]}). γ 는 음극")
        print("  모양 변화를 따라가는 것이 아니라 **다른 것을 흡수하고 있다.**")
    elif worst[3] < 0.34:
        print(f"\n→ 모델 변화가 측정 변화의 **{worst[3]:.2f} 배**에 그친다. 실제 음극은")
        print("  γ 가 표현할 수 있는 것보다 **훨씬 크게** 변한다 — 그러면 그 차이는")
        print("  a_NE·b_NE 로 새어 들어가고, 그것이 곧 LAM_NE 다.")
    else:
        print(f"\n→ 두 변화가 같은 규모다 (최대 {worst[3]:.1f} 배). γ 가 측정된 모양")
        print("  변화를 대략 따라간다 — 자유 파라미터로 둘 근거가 있다.")
    if flips:
        print(f"\n⚠ **방향 규약이 반대다.** {len(flips)} 개 상태에서 측정 곡선을")
        print("   뒤집어야 블렌드와 가까워진다:")
        for s, f, r in flips:
            print(f"     {s:10} 그대로 {f:7.1f} mV → 뒤집으면 {r:7.1f} mV")
        print("   아래 (c) 는 뒤집은 값이다. 이건 모델의 잘못이 아니라 x 축")
        print("   해석의 문제이므로, 그 자체로는 발견이 아니다.")

    cs = [r[4] for r in rows if r[4] == r[4]]
    if cs:
        rmss = [r[5] for r in rows if r[5] == r[5]]
        print(f"\n(c) **절대 일치** — `Blend(x, γ_적합)` 이 측정 음극과 얼마나 맞나")
        print(f"    max |Δ| {min(cs):.1f} ~ {max(cs):.1f} mV   "
              f"rms {min(rmss):.1f} ~ {max(rmss):.1f} mV")
        print(f"    {'state':10}{'max 위치 x':>11}{'|Δ|>50mV 인 격자 비율':>22}")
        for st, xa, over in cwhere:
            print(f"    {st:10}{xa:>11.3f}{over:>21.1f} %")
        spread = max(cs) / max(rmss) if max(rmss) > 0 else float("inf")
        worst_over = max(o for _, _, o in cwhere) if cwhere else 0.0
        print()
        if worst_over > 30:
            print("    → 격자의 30 % 넘게 50 mV 이상 벌어진다. **블렌드가 이 음극의")
            print("      모양이 아니다.** γ 를 어떻게 고르든 남고, a_NE·b_NE 가")
            print("      흡수한다 = LAM_NE·LLI 에 계통 편향.")
        elif spread > 3:
            print(f"    → max 가 rms 의 {spread:.1f} 배다. 어긋남이 **좁은 구간에**")
            print("      몰려 있다는 뜻이고, 곡선 대부분은 rms 수준으로 맞는다.")
            print("      'max 가 크다' 만으로 모델을 기각하면 안 된다 — 위 'max 위치'")
            print("      가 어디인지(끝단인지 평탄부인지) 보고 판단할 것.")
        else:
            print("    → 어긋남이 곡선 전체에 고르다. rms 를 대표값으로 쓸 것.")
    print("\n⚠ (a) 는 **정규화 뒤** 변화다. 음극 용량이 줄면(위 '용량 Δ%') 곡선이")
    print("   가로로 늘어나 그것만으로도 모양이 바뀐 것처럼 보인다. 용량 변화가")
    print("   큰 상태에서는 (a) 를 순수한 OCP 모양 변화로 읽으면 안 된다.")
    print("⚠ 이것은 **크기 비교**다. 방향이 같은지는 따로 봐야 한다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
