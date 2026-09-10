"""dd_shims 대조용 결정론적 테스트 벡터.

세 구현(Octave 내장 · 우리 shim · Python 포팅)이 **같은 수**를 읽어야 하므로
난수를 그 자리에서 만들지 않고 파일로 고정한다 (seed 20260910).

사용: python3 gen_shim_cases.py <작업디렉터리>   → <작업디렉터리>/cases/ 에 쓴다
"""
import sys
import pathlib
import numpy as np

base = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).parent
d = base / "cases"
d.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(20260910)

vecs = {
    "n1":        np.array([3.5]),                       # 최소 길이
    "n2":        np.array([1.0, 2.0]),
    "n4_int":    np.array([1.0, 2.0, 3.0, 4.0]),
    "n5_unsort": np.array([5.0, 1.0, 4.0, 2.0, 3.0]),   # 정렬 안 된 입력
    "n7_dup":    np.array([2.0, 2.0, 2.0, 5.0, 9.0, 9.0, 1.0]),   # 중복값
    "n50_rand":  rng.normal(3.7, 1.3, 50),
    "n101_ramp": np.linspace(-2.0, 6.0, 101),
    # 실제 pOCV 를 닮은 모양 — 평활 가장자리 처리가 드러나게
    "n500_ocv":  4.2 - 1.2 * np.linspace(0, 1, 500) ** 1.7
                 + 0.01 * np.sin(np.linspace(0, 40, 500)),
}
for k, v in vecs.items():
    np.savetxt(d / f"vec_{k}.csv", v, fmt="%.17g")

# 규진팀 코드가 실제로 쓰는 분위수(0.05·0.15·0.85·0.95)와 양 끝 경계
np.savetxt(d / "pvals.csv",
           np.array([0.0, 0.001, 0.05, 0.15, 0.25, 0.5, 0.75, 0.85, 0.95, 0.999, 1.0]),
           fmt="%.17g")

# sgolayfilt 케이스: (벡터, order, framelen). 규진팀 설정은 order=3, framelen=11.
sg = [("n50_rand", 3, 11), ("n101_ramp", 3, 11), ("n500_ocv", 3, 11),
      ("n500_ocv", 1, 9), ("n500_ocv", 3, 31), ("n50_rand", 1, 5),
      ("n101_ramp", 2, 7), ("n500_ocv", 4, 21)]
with open(d / "sgcases.csv", "w") as fh:
    fh.write("vec,order,framelen\n")
    for a, b, c in sg:
        fh.write(f"{a},{b},{c}\n")

print(f"wrote {len(vecs)} vectors + {len(sg)} sgolay cases -> {d}")
