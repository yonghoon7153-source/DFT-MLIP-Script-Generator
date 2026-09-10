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

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from bms_balancing import data as D                      # noqa: E402
from bms_balancing.model import Blend, HalfCell          # noqa: E402

GRID = np.linspace(0.02, 0.98, 400)     # 양 끝은 외삽이라 뺀다


def fitted_gamma(root: pathlib.Path, out_dir: pathlib.Path, state: str,
                 src: str, si: str) -> float | None:
    """`matrix_<state>.csv` 에서 그 조합의 자유-γ 적합값."""
    for f in sorted(out_dir.glob(f"matrix_{state}*.csv"), reverse=True):
        for r in csv.DictReader(f.open(encoding="utf-8")):
            if (r.get("half_cell") == src and r.get("si") == si
                    and float(r.get("w_dqdv", 1)) == 0):
                return float(r["gamma_Si"])
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default=None)
    ap.add_argument("--source", default="GITT", choices=list(D.HALF_FILE))
    ap.add_argument("--si-source", default="Li", choices=D.SI_SOURCES)
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args()

    root = D.data_root(a.data_root)
    out_dir = pathlib.Path(a.out_dir)
    states = [s for s in D.STATES
              if D.half_cell_path(root, a.source, s).is_file()]
    if "pristine" not in states:
        raise SystemExit(f"`{a.source}` 에 pristine 이 없다 — 기준이 없으면 못 잰다")

    meas = {s: HalfCell(D.half_cell_path(root, a.source, s),
                        window=11, poly_order=3).E_NE(GRID) for s in states}
    si_c, si_v, gr_c, gr_v = D.load_literature(root, a.si_source)
    blend = Blend(si_c, si_v, gr_c, gr_v, window=11, poly_order=3)
    gam = {s: fitted_gamma(root, out_dir, s, a.source, a.si_source) for s in states}

    print(f"반쪽전지 {a.source} · 문헌 Si {a.si_source} · 상태 {len(states)}개")
    print(f"기준은 pristine. 격자 x={GRID[0]:.2f}~{GRID[-1]:.2f} ({GRID.size}점)\n")

    base_m = meas["pristine"]
    g0 = gam.get("pristine")
    base_b = blend.E(GRID, g0) if g0 is not None else None

    print(f"{'state':10}{'γ 적합':>9}{'(a) 측정 ΔE_NE':>18}{'(b) 모델 ΔE_NE':>18}"
          f"{'(b)/(a)':>10}")
    print(f"{'':10}{'':9}{'max |mV|':>18}{'max |mV|':>18}")
    rows = []
    for s in states:
        if s == "pristine":
            continue
        da = float(np.max(np.abs(meas[s] - base_m))) * 1e3
        db = (float(np.max(np.abs(blend.E(GRID, gam[s]) - base_b))) * 1e3
              if (base_b is not None and gam.get(s) is not None) else float("nan"))
        ratio = db / da if da > 0 else float("inf")
        rows.append((s, da, db, ratio))
        print(f"{s:10}{(f'{gam[s]:.4f}' if gam.get(s) is not None else '—'):>9}"
              f"{da:>18.2f}{db:>18.2f}{ratio:>10.2f}")

    print()
    ok = [r for r in rows if r[3] == r[3]]
    if not ok:
        print("γ 적합값을 못 찾았다 — `--out-dir` 에 matrix_<state>.csv 가 있어야 한다")
        return 1
    worst = max(ok, key=lambda r: r[3])
    print(f"측정된 음극 모양 변화는 최대 {max(r[1] for r in ok):.2f} mV,")
    print(f"γ 가 만들어 낸 모델 변화는 최대 {max(r[2] for r in ok):.2f} mV 다.")
    if worst[3] > 3:
        print(f"\n→ 모델 변화가 측정 변화의 **{worst[3]:.1f} 배** ({worst[0]}). γ 는 음극")
        print("  모양 변화를 따라가는 것이 아니라 **다른 것을 흡수하고 있다.**")
    elif worst[3] < 0.5:
        print(f"\n→ 모델 변화가 측정 변화보다 작다 ({worst[3]:.2f} 배). γ 가 실제")
        print("  모양 변화를 **덜** 표현하고 있다 — 그것대로 따로 볼 문제다.")
    else:
        print(f"\n→ 두 변화가 같은 규모다 (최대 {worst[3]:.1f} 배). γ 가 측정된 모양")
        print("  변화를 대략 따라간다 — 자유 파라미터로 둘 근거가 있다.")
    print("\n⚠ 이것은 **크기 비교**다. 모양이 같은 방향으로 바뀌는지는 따로 봐야 한다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
