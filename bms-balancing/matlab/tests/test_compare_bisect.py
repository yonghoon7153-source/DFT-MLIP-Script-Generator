"""`verify.py --compare` 의 **이분 판정**이 실제로 갈린 단계를 짚는지 본다.

이 테스트가 필요한 이유: 대조기가 언제나 "일치" 라고만 말하면 없는 것만
못하다. 그래서 **일부러 어긋뜨린 CSV** 를 먹여서 (a) 갈렸음을 알아채는지,
(b) 갈린 단계 이름을 맞게 부르는지를 확인한다.
"""
from __future__ import annotations
import io, pathlib, sys, contextlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from bms_balancing.verify import (ANCHOR_STAGE, DD_EVAL_P, _compare_dd_eval,   # noqa: E402
                                  read_dd_eval_csv)

BASE = {"c_cell": 74.671, "dv_lo": 0.1492985972, "dv_hi": 0.8507014028,
        "dv_n": 350.0, "dq_lo": 3.1064629259, "dq_hi": 4.1435370741,
        "E_PE_0p5": 3.5584147098, "E_NE_0p5_0p25": 0.381225,
        "dv_PE_0p5": -0.6573737739, "dv_NE_0p5_0p25": 0.0695302306}
ROWS = [list(q) + [0.78 + 0.001 * i, 0.20 + 0.0001 * i]
        for i, q in enumerate(DD_EVAL_P)]


def write_csv(path, anchors, rows):
    out = ["# dd_eval  state=pristine  halfcell=data/half_cell/GITT/  Si=Li  w_dqdv=0"]
    out += [f"# {k},{v:.17g}" for k, v in anchors.items()]
    out.append("a_PE,b_PE,a_NE,b_NE,gamma_Si,rmse_pocv,rmse_dvdq")
    out += [",".join([f"{x:.6f}" for x in r[:5]] + [f"{r[5]:.10f}", f"{r[6]:.10f}"])
            for r in rows]
    pathlib.Path(path).write_text("\n".join(out) + "\n")


def run(tmp, anchors_m, rows_m):
    write_csv(tmp, anchors_m, rows_m)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _compare_dd_eval(dict(BASE), [list(r) for r in ROWS], tmp)
    return buf.getvalue()


def main():
    tmp = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/ddc.csv")
    fails = []

    def expect(name, text, must_have, must_not=()):
        bad = [m for m in must_have if m not in text] + [m for m in must_not if m in text]
        print(f"  {'OK  ' if not bad else 'FAIL'} {name}")
        if bad:
            fails.append((name, bad, text))

    # 0) 같은 값 → 일치 판정
    expect("동일 입력 → 일치", run(tmp, BASE, ROWS),
           ["전부 일치"], ["처음 갈린다"])

    # 1) 각 앵커를 하나씩 어긋뜨리면 그 앵커의 단계를 불러야 한다
    for k, stage in ANCHOR_STAGE:
        a = dict(BASE)
        a[k] = a[k] + (1.0 if k == "dv_n" else max(abs(a[k]), 1.0) * 1e-3)
        txt = run(tmp, a, ROWS)
        expect(f"{k} 어긋남 → 「{stage[:24]}…」", txt,
               [f"**{k}** 에서 처음 갈린다" if k != "dv_n" else "dv_n", stage],
               ["전부 일치"])

    # 2) 앵커는 맞고 rmse 만 갈리면 '목적함수 산술' 로 판정해야 한다
    r2 = [list(r) for r in ROWS]
    r2[3][5] *= 1.02
    expect("rmse 만 어긋남 → 목적함수 산술", run(tmp, BASE, r2),
           ["앵커는 전부 맞는데 rmse 가 갈린다", "목적함수 산술"], ["전부 일치"])

    # 3) 파라미터 격자가 어긋나면 알아채야 한다
    r3 = [list(r) for r in ROWS]
    r3[2][0] += 0.05
    expect("p 격자 어긋남 감지", run(tmp, BASE, r3), ["격자가 어긋났다"])

    # 4) 앞머리 없는 옛 산출도 죽지 않아야 한다
    old = pathlib.Path(str(tmp) + ".old")
    old.write_text("a_PE,b_PE,a_NE,b_NE,gamma_Si,rmse_pocv,rmse_dvdq\n" +
                   "\n".join(",".join([f"{x:.6f}" for x in r[:5]] +
                                      [f"{r[5]:.10f}", f"{r[6]:.10f}"]) for r in ROWS) + "\n")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _compare_dd_eval(dict(BASE), [list(r) for r in ROWS], old)
    expect("앵커 없는 옛 CSV 도 처리", buf.getvalue(), ["(없음)"])

    # 5) BOM 붙은 CSV (MATLAB 이 UTF-8 BOM 을 붙이는 경우)
    bom = pathlib.Path(str(tmp) + ".bom")
    write_csv(bom, BASE, ROWS)
    bom.write_bytes(b"\xef\xbb\xbf" + bom.read_bytes())
    an, rw = read_dd_eval_csv(bom)
    ok = len(an) == 10 and len(rw) == 8
    print(f"  {'OK  ' if ok else 'FAIL'} BOM 붙은 CSV 파싱 (앵커 {len(an)}, 행 {len(rw)})")
    if not ok:
        fails.append(("BOM", ["앵커 10 / 행 8 이어야 한다"], ""))

    print(f"\n{'PASS' if not fails else 'FAIL'} — {len(fails)} 개 실패")
    for n, b, t in fails:
        print(f"\n--- {n}: 빠졌거나 잘못 나온 것 {b}\n{t}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
