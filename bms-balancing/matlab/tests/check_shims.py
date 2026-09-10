"""dd_shims 3자 대조 — 우리 shim · Octave 내장 · Python 포팅.

무엇을 증명하나:
  · `quantile` shim ≡ Octave 내장 `quantile`(method 5). Octave 의 method 5 는
    MATLAB 의 정의((i-0.5)/n plotting position)와 같으므로, 이 일치는 우리
    shim 이 **MATLAB 정의를 구현했다**는 제3자 확인이다.
  · `quantile` shim ≡ Python `matlab_quantile`.
  · `sgolayfilt` shim ≡ Python `sgolay`(scipy savgol_filter, mode='interp').
    특히 **가장자리** 구간 — model.py 가 "완전히 같은 수는 아닐 수 있다" 고
    적어 둔 바로 그 자리다.

무엇을 증명 못 하나:
  MathWorks 의 진짜 `sgolayfilt`. 이 컨테이너에도 사용자 기계에도 Signal
  Processing Toolbox 가 없다. 사용자 기계에서도 `sgolayfilt` 는 **항상 이
  shim** 이므로, 그쪽 MATLAB↔Python 대조는 이 자리에서만큼은 같은 정의끼리
  비교하는 것이 맞다.
"""
import sys, csv, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from bms_balancing.model import matlab_quantile, sgolay

D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".") / "cases"
P = np.loadtxt(D/"pvals.csv")
names = ['n1','n2','n4_int','n5_unsort','n7_dup','n50_rand','n101_ramp','n500_ocv']
vec = {n: np.atleast_1d(np.loadtxt(D/f"vec_{n}.csv")) for n in names}

def load(fn):
    out = {}
    with open(fn) as fh:
        for r in csv.DictReader(fh):
            key = (r["kind"], r["vec"], r["arg1"], r["arg2"], int(r["idx"]))
            out[key] = float(r["value"])
    return out

BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
oct_native, oct_shim = load(BASE/"res_oct_native.csv"), load(BASE/"res_oct_shim.csv")

def rpt(title, pairs):
    if not pairs:
        print(f"  {title}: (없음)"); return 0.0
    d = np.array([abs(a-b) for a,b in pairs])
    rel = np.array([abs(a-b)/max(abs(b),1e-12) for a,b in pairs])
    print(f"  {title}: n={len(pairs)}  max|Δ|={d.max():.3e}  max rel={rel.max():.3e}")
    return d.max()

print("=== 1. quantile ===")
py_q, sh_q, nv_q = [], [], []
for n in names:
    for p in P:
        k = ("quantile", n, f"{p:.17g}", "", 1)
        pyv = matlab_quantile(vec[n], p)
        py_q.append((pyv, oct_shim[k])); sh_q.append((oct_shim[k], oct_native[k]))
worst_a = rpt("shim(MATLAB용) vs Python matlab_quantile", py_q)
worst_b = rpt("shim vs Octave core quantile(method 5)", sh_q)

print("=== 2. sgolayfilt ===")
maxes = {}
with open(D/"sgcases.csv") as fh:
    for r in csv.DictReader(fh):
        n, od, fl = r["vec"], int(r["order"]), int(r["framelen"])
        x = vec[n]
        pyy = sgolay(x, od, fl)
        shy = np.array([oct_shim[("sgolay", n, str(od), str(fl), k+1)] for k in range(len(x))])
        d = np.abs(pyy - shy)
        maxes[(n,od,fl)] = d.max()
        # 가장자리와 내부를 나눠서 본다 — 다르면 가장자리에서 갈린다
        m = (fl-1)//2
        edge = max(d[:m].max() if m else 0.0, d[-m:].max() if m else 0.0)
        core = d[m:len(x)-m].max()
        print(f"  {n:11s} order={od} f={fl:2d}: max|Δ|={d.max():.3e}  (가장자리 {edge:.3e} / 내부 {core:.3e})")
worst_c = max(maxes.values())
print()
print(f"WORST quantile shim-vs-python : {worst_a:.3e}")
print(f"WORST quantile shim-vs-octave : {worst_b:.3e}")
print(f"WORST sgolay  shim-vs-python  : {worst_c:.3e}")
ok = worst_a < 1e-12 and worst_b < 1e-12 and worst_c < 1e-9
print("RESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
