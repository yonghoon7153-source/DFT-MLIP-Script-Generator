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
    cap = {s: raw_ne_capacity(D.half_cell_path(root, a.source, s)) for s in states}
    si_c, si_v, gr_c, gr_v = D.load_literature(root, a.si_source)
    blend = Blend(si_c, si_v, gr_c, gr_v, window=11, poly_order=3)

    print(f"반쪽전지 {a.source} · 문헌 Si {a.si_source} · 상태 {len(states)}개")
    print(f"기준은 pristine. 격자 x={GRID[0]:.2f}~{GRID[-1]:.2f} ({GRID.size}점)\n")

    base_m, base_cap = meas["pristine"], cap["pristine"]
    print(f"{'state':10}{'NE 용량':>12}{'용량 Δ%':>9}"
          f"{'γ':>8}{'γ(기준)':>9}{'(a) 측정':>10}{'(b) 모델':>10}{'(b)/(a)':>9}")
    print(f"{'':10}{'(원단위)':>12}{'':9}{'':8}{'':9}{'max mV':>10}{'max mV':>10}")
    print(f"{'pristine':10}{base_cap:>12.6g}{0.0:>9.2f}")
    rows = []
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
        rows.append((s, da, db, ratio))
        print(f"{s:10}{cap[s]:>12.6g}{100*(cap[s]/base_cap-1):>9.2f}"
              f"{(f'{g:.4f}' if g is not None else '—'):>8}"
              f"{(f'{gr:.4f}' if gr is not None else '—'):>9}"
              f"{da:>10.2f}{db:>10.2f}{ratio:>9.2f}")

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
    print("\n⚠ (a) 는 **정규화 뒤** 변화다. 음극 용량이 줄면(위 '용량 Δ%') 곡선이")
    print("   가로로 늘어나 그것만으로도 모양이 바뀐 것처럼 보인다. 용량 변화가")
    print("   큰 상태에서는 (a) 를 순수한 OCP 모양 변화로 읽으면 안 된다.")
    print("⚠ 이것은 **크기 비교**다. 방향이 같은지는 따로 봐야 한다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
