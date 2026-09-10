"""두 전사본(Octave dd_eval.m · Python mirror)의 산출을 **수치 허용오차로** 대조.

바이트 대조는 너무 빡빡하다: `linspace` 의 마지막 자리 반올림이 Octave 와
numpy 에서 1 ULP 다르다. 그건 배관 버그가 아니라 부동소수점 차이다. 그래서
여기서는 (a) 상대오차 상한과 (b) **정수인 `dv_n` 은 정확히 일치** 를 본다.
`dv_n` 이 갈리면 분위수 창 경계가 격자점을 하나 먹거나 뱉었다는 뜻이고,
그건 진짜 발견이다.
"""
from __future__ import annotations
import sys, pathlib

TOL_REL = 1e-12          # 부동소수점 잡음 상한 (1 ULP ≈ 2e-16)


def parse(p: pathlib.Path):
    anchors, rows = {}, []
    for line in p.read_text().splitlines():
        if line.startswith("# ") and "," in line:
            k, _, v = line[2:].partition(",")
            try:
                anchors[k] = float(v)
            except ValueError:
                pass
        elif line and not line.startswith("#") and not line.startswith("a_PE"):
            rows.append([float(x) for x in line.split(",")])
    return anchors, rows


def compare(fa: pathlib.Path, fb: pathlib.Path):
    A, RA = parse(fa)
    B, RB = parse(fb)
    problems, worst = [], 0.0
    if set(A) != set(B):
        problems.append(f"앵커 이름이 다르다: {sorted(set(A) ^ set(B))}")
    for k in sorted(set(A) & set(B)):
        a, b = A[k], B[k]
        if k == "dv_n":
            if a != b:
                problems.append(f"dv_n 이 다르다: {a:g} vs {b:g} — 분위수 창이 격자점을 먹었다")
            continue
        rel = abs(a - b) / max(abs(b), 1e-30)
        worst = max(worst, rel)
        if rel > TOL_REL:
            problems.append(f"앵커 {k}: {a!r} vs {b!r}  (rel {rel:.3e})")
    if len(RA) != len(RB):
        problems.append(f"행 수가 다르다: {len(RA)} vs {len(RB)}")
    else:
        for i, (ra, rb) in enumerate(zip(RA, RB)):
            for j, (a, b) in enumerate(zip(ra, rb)):
                rel = abs(a - b) / max(abs(b), 1e-30)
                worst = max(worst, rel)
                if rel > TOL_REL:
                    problems.append(f"행 {i} 열 {j}: {a!r} vs {b!r}  (rel {rel:.3e})")
    return problems, worst


if __name__ == "__main__":
    probs, worst = compare(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]))
    print(f"max rel dev = {worst:.3e}   (허용 {TOL_REL:.0e})")
    for p in probs:
        print("  !", p)
    sys.exit(1 if probs else 0)
