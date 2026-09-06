#!/usr/bin/env python3
"""nseries_n6.py — n-시리즈(스핀 분포)를 n=6 으로 잇는다. **seed 개입 없음.**

7월 n=1·2·3 을 낸 방법 그대로다:
  ① H-제거 doped 구조를 만든다 (charge 0, doublet)
  ② ORCA r2SCAN-3c 로 **그냥 돌린다** (fresh SCF — MORead·Rotate·NoIter 전부 없음)
  ③ `LOEWDIN ATOMIC CHARGES AND SPIN POPULATIONS` 를 그룹별로 합산

왜 이걸 따로 쓰나
  폴라론 pilot(S0)은 *"각 고리에 강제로 앉혀 보고 어느 게 안정한가"* 를 물었고
  그 개입이 막혔다(`kb/questions/polaron_seed_localized_basis_cannot_express_ring_pi.md`).
  이 스크립트는 그 센 질문을 **안 한다.** 7월과 같은 약한 질문 —
  *"그냥 수렴시키면 스핀이 어디 사는가"* — 만 하고, 그건 막힌 적이 없다.

  7월 실측:  n=1 백본 π ~35 % · n=2 32.6 % · n=3(mid) **50.1 %**  (크로스오버)
  이 스크립트가 채우는 칸: **n=6**

⛔ 이 도구가 **못 하는 것 · 안 하는 것**
  · **자가도핑이 일어나는지 판정하지 않는다.** 산화된 상태를 **주고** 그 안에서
    스핀이 어디 사는지 볼 뿐이다. 자가도핑의 자발성은 열역학
    (`db/properties/sdcp_v7c_li_binding.csv` 의 DPE·PA 분석)과 FT-IR 몫이다.
  · **폴라론을 원하는 자리에 놓지 못한다.** 그게 pilot 이고 막혀 있다.
  · SCF 가 여러 해를 가질 때 **어느 해로 갔는지 보증하지 않는다.** fresh start 한 번이다.
    (7월도 같은 한계였다 — n-시리즈끼리는 비교 가능하지만 "전역 최소" 가 아니다.)
  · 기하를 이완할지는 **사람이 정한다**(`--opt`). SP 는 중성 기하 위의 값이라
    폴라론의 격자 완화를 놓친다 — 7월은 Opt 였다. 섞어 인용하지 말 것.

사용:
  python3 tools/sdcp/nseries_n6.py --pilot /data/work/runs/sdcp_polaron_S0_v3 --out n6 --opt
  python3 tools/sdcp/nseries_n6.py --analyze n6        # 돌고 난 뒤
  python3 tools/sdcp/nseries_n6.py --selftest
"""
import argparse
import json
import os
import re
import sys

#: 7월 값 — 비교 기준. 출처: kb/results/sdcp_master_summary_2026_07_16.md §3
JULY = {1: {"so3": 65.0, "bb": 35.0}, 2: {"so3": 62.3, "bb": 32.6},
        "3end": {"so3": 54.6, "bb": 39.8}, "3mid": {"so3": 42.3, "bb": 50.1}}

#: ⛔ 2026-09-06 실물 — 여기 `%%` 를 쓰면 **입력에 그대로 `%%` 가 들어간다.**
#:   `%%` escape 는 %-포맷용이고 이 템플릿은 `.format()` 이다. ORCA 가
#:   `expected an identifier after '%'` 로 즉사했다(잡 하나 날림).
#:   selftest 가 생성물에 `%%` 가 없는지 본다 — 눈으로 안 보이는 종류라 기계가 봐야 한다.
INP = """! UKS r2SCAN-3c {run} TightSCF
%output
  Print[P_Loewdin] 1
end
%maxcore {maxcore}
%pal nprocs {nprocs} end
* xyzfile {charge} {mult} {xyz}
"""



def _ring_atoms(rings):
    """manifest 의 rings → 고리 원자 인덱스 집합 (H·에테르 O 제외).

    ⚠ 형식이 dict({이름: [idx...]} 또는 {이름: {"ring": [...]}}) 일 수도, list 일 수도 있다.
      **모르는 형식이면 빈 집합을 준다** — 조용히 일부만 세지 않는다.
    """
    out = set()
    it = rings.values() if isinstance(rings, dict) else (rings or [])
    for v in it:
        if isinstance(v, dict):
            v = v.get("ring") or v.get("atoms") or []
        if isinstance(v, (list, tuple)):
            out |= {int(x) for x in v if isinstance(x, (int, float))}
    return out


def build(pilot, out, opt, nprocs, maxcore):
    """pilot 산출물에서 기하·그룹을 가져와 n=6 잡을 만든다. **새로 만들지 않는다** —
    pilot 이 이미 봉인한 것을 쓴다(같은 구조를 두 번 정의하면 갈라진다)."""
    man = json.load(open(os.path.join(pilot, "MANIFEST_PILOT.json"), encoding="utf-8"))
    amf = man.get("atom_manifest") or {}
    if "D" not in amf:
        sys.exit("⛔ MANIFEST_PILOT.json 에 atom_manifest.D 가 없다 — 구판 번들이다")
    os.makedirs(out, exist_ok=True)
    # D• 기하: probe 가 쓴 것과 **같은 파일**을 가져온다 (다시 만들지 않는다)
    src = None
    for r, _d, fs in os.walk(os.path.join(pilot, "S0P")):
        for f in fs:
            if f.endswith(".xyz") and "Dradical" in r:
                src = os.path.join(r, f)
                break
        if src:
            break
    if not src:
        sys.exit("⛔ S0P/…/Dradical 밑에서 .xyz 를 못 찾았다 — pilot 경로를 확인하세요")
    xyz = "n6_doped.xyz"
    open(os.path.join(out, xyz), "w").write(open(src, encoding="utf-8").read())
    run = "Opt" if opt else "SP"
    open(os.path.join(out, "n6_doped.inp"), "w").write(
        INP.format(run=run, charge=0, mult=2, xyz=xyz,
                   nprocs=nprocs, maxcore=maxcore))
    # 그룹: manifest 의 D 프레임을 그대로 옮긴다 (0-based → 그대로 쓴다)
    D = amf["D"]
    # ⛔⛔ 7월(n=1·2·3)의 backbone 정의는 **티오펜 고리 원자만**이다
    #   (`build_v7c_dimer.py`: ring = [rS] + alphas + betas — 고리 H 도, 에테르 O 도 없다).
    #   pilot 의 `backbone_strict` 는 거기에 **고리 H 를 더한다**(bb_core = ring_atoms | ring_H).
    #   두 정의를 한 표에 올리면 이 세션에서 반복된 그 실수다. 7월과 **글자 그대로 같은**
    #   분할을 따로 만들어서, n=1→6 을 같은 자로 잰다.
    rings = D.get("rings") or {}
    july = sorted(_ring_atoms(rings))
    groups = {"backbone_july": july,                       # ← n-시리즈 비교는 이걸로
              "backbone_strict": D["derived"]["backbone_strict"],
              "backbone_extended": D["derived"]["backbone_extended"],
              "sulfonate": sorted(D["components"].get("sulfonate", [])),
              "rings": rings}
    if not july:
        sys.exit("⛔ manifest 의 rings 에서 고리 원자를 못 뽑았다 — 7월 정의를 재현할 수 없다. "
                 "구조를 확인하기 전에는 n-시리즈에 값을 얹지 않는다")
    json.dump({"groups": groups, "n_atoms": D["n_atoms"],
               "source_manifest": os.path.abspath(os.path.join(pilot, "MANIFEST_PILOT.json")),
               "source_xyz": os.path.abspath(src),
               "run": run,
               "⚠": ("7월 n=1·2·3 은 **Opt** 였다. SP 로 돌린 값과 섞어 인용하지 말 것 — "
                     "폴라론은 격자 완화와 얽혀 있어 SP 는 국재화를 과소평가한다.")},
              open(os.path.join(out, "groups.json"), "w"), ensure_ascii=False, indent=1)
    print(f"→ {out}/  n6_doped.inp ({run}) · n6_doped.xyz ({D['n_atoms']}원자) · groups.json")
    print(f"   기하 출처: {src}")
    print(f"   backbone_strict {len(groups['backbone_strict'])} · "
          f"extended {len(groups['backbone_extended'])} · sulfonate {len(groups['sulfonate'])}")
    print(f"   실행:  cd {out} && $ORCA n6_doped.inp > n6_doped.out")
    if not opt:
        print("   ⚠ SP 다 — 7월(Opt)과 섞어 인용하지 말 것. Opt 는 --opt")


def parse_loewdin(txt):
    """마지막 `LOEWDIN ATOMIC CHARGES AND SPIN POPULATIONS` 블록 → {idx: spin}.

    ⛔ 못 하는 것: 블록이 없으면 None 을 준다 — 0 이 아니다. 미완료를 완료로 읽지 않는다.
    """
    hdr = "LOEWDIN ATOMIC CHARGES AND SPIN POPULATIONS"
    if hdr not in txt:
        return None
    seg = txt.split(hdr)[-1]
    out = {}
    for ln in seg.splitlines()[1:]:
        m = re.match(r"\s*(\d+)\s+\w+\s*:\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)", ln)
        if m:
            out[int(m.group(1))] = float(m.group(3))
        elif out:
            break
    return out or None


def analyze(d):
    g = json.load(open(os.path.join(d, "groups.json"), encoding="utf-8"))
    p = os.path.join(d, "n6_doped.out")
    if not os.path.isfile(p):
        sys.exit(f"⛔ {p} 가 없다 — 아직 안 돌았다")
    txt = open(p, encoding="utf-8", errors="ignore").read()
    if "ORCA TERMINATED NORMALLY" not in txt:
        print("⚠ ORCA 정상종료 표시가 없다 — 아래 값은 중간값일 수 있다")
    sp = parse_loewdin(txt)
    if sp is None:
        sys.exit("⛔ Loewdin 스핀 블록이 없다 — 계산이 거기까지 안 갔다")
    tot = sum(sp.values())
    print(f"총 스핀 = {tot:.3f}  (더블렛이면 ~1.0)")
    if abs(tot - 1.0) > 0.15:
        print("  ⚠ 1.0 에서 멀다 — 스핀 오염이나 다른 해로 갔을 수 있다")
    gr = g["groups"]
    res = {}
    for name in ("sulfonate", "backbone_july", "backbone_strict", "backbone_extended"):
        idx = gr.get(name) or []
        res[name] = 100.0 * sum(sp.get(i, 0.0) for i in idx) / tot if tot else 0.0
        print(f"  {name:20s} {res[name]:6.1f} %  ({len(idx)}원자)")
    rings = gr.get("rings") or {}
    if isinstance(rings, dict) and rings:
        print("  고리별:")
        for k in sorted(rings):
            idx = rings[k] if isinstance(rings[k], list) else []
            if idx:
                print(f"    {k:12s} {100.0*sum(sp.get(i,0.0) for i in idx)/tot:6.1f} %")
    print()
    print("  n-시리즈 (7월, Opt · kb/results/sdcp_master_summary_2026_07_16.md §3):")
    print(f"    n=1        SO3 {JULY[1]['so3']:.1f} / 백본 {JULY[1]['bb']:.1f}")
    print(f"    n=2        SO3 {JULY[2]['so3']:.1f} / 백본 {JULY[2]['bb']:.1f}")
    print(f"    n=3 end    SO3 {JULY['3end']['so3']:.1f} / 백본 {JULY['3end']['bb']:.1f}")
    print(f"    n=3 mid    SO3 {JULY['3mid']['so3']:.1f} / 백본 {JULY['3mid']['bb']:.1f}  ← 크로스오버")
    print(f"    n=6        SO3 {res['sulfonate']:.1f} / 백본 {res['backbone_july']:.1f}"
          f"   ← 이번 (7월과 같은 분할: 고리 원자만)")
    print(f"      참고    같은 계를 다른 분할로: strict(+고리H) {res['backbone_strict']:.1f} · "
          f"extended(+에테르O) {res['backbone_extended']:.1f}")
    print("      ⛔ 위 표에 올리는 것은 **backbone_july 뿐이다** — 다른 분할을 7월 값 옆에 놓지 않는다")
    print()
    print(f"  ⚠ 이번 실행은 **{g['run']}** 이다. {g['⚠']}")
    print("  ⛔ 이 값은 '자가도핑이 일어난다' 의 증거가 아니다 — 산화된 상태를 **주고**")
    print("     그 안에서 스핀이 어디 사는지 본 것이다. 자발성은 열역학·FT-IR 몫이다.")


def selftest():
    ok = bad = 0

    def chk(c, m):
        nonlocal ok, bad
        print(("  ⭕ " if c else "  ⛔ ") + m)
        ok, bad = (ok + 1, bad) if c else (ok, bad + 1)

    good = ("LOEWDIN ATOMIC CHARGES AND SPIN POPULATIONS\n"
            "-----\n"
            "   0 C :   -0.123456    0.400000\n"
            "   1 O :    0.111111    0.600000\n"
            "\nTimings\n")
    sp = parse_loewdin(good)
    chk(sp == {0: 0.4, 1: 0.6}, "판독: 인덱스와 **스핀 열**(3번째 수)을 읽는다")
    chk(parse_loewdin("아무것도 없음") is None,
        "⛔음성: 블록이 없으면 None — 0 이 **아니다**(미완료를 완료로 안 읽는다)")
    chk(parse_loewdin(good.replace("0.400000", "x")) == {1: 0.6},
        "⛔음성: 깨진 줄은 건너뛰고 조용히 0 으로 채우지 않는다")
    two = good + "LOEWDIN ATOMIC CHARGES AND SPIN POPULATIONS\n-----\n   0 C :  0.0  0.900000\n\nTimings\n"
    chk(parse_loewdin(two) == {0: 0.9},
        "블록이 여럿이면 **마지막**을 쓴다 (Opt 중간 블록을 안 읽는다)")
    # 전하 열을 스핀으로 잘못 읽으면 안 된다 — 음수 전하가 그대로 나오면 실패
    chk(all(v >= 0 for v in (parse_loewdin(good) or {}).values()),
        "⛔음성: 2번째 열(전하)을 스핀으로 읽지 않는다")
    # ── 입력 생성 (2026-09-06 실물 버그: `%%` 가 그대로 남아 ORCA 즉사) ──
    txt = INP.format(run="Opt", charge=0, mult=2, xyz="x.xyz", nprocs=8, maxcore=2500)
    chk("%%" not in txt, "⛔음성: 생성된 입력에 `%%` 가 남지 않는다 (ORCA 가 즉사한다)")
    chk(txt.count("%pal") == 1 and txt.count("%maxcore") == 1 and txt.count("%output") == 1,
        "블록 셋이 각각 한 번씩 들어간다")
    chk("nprocs 8" in txt and "%maxcore 2500" in txt and "0 2 x.xyz" in txt,
        "인자가 실제로 꽂힌다 (전하 0 · 다중도 2 = doublet)")
    chk("{" not in txt and "}" not in txt, "⛔음성: 안 채워진 자리표시자가 남지 않는다")
    print(f"  selftest: ⭕ {ok} · ⛔ {bad}")
    return 0 if bad == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", help="폴라론 pilot 디렉터리 (MANIFEST_PILOT.json 이 있는 곳)")
    ap.add_argument("--out", default="n6")
    ap.add_argument("--opt", action="store_true", help="기하 이완 (7월과 같은 조건)")
    ap.add_argument("--nprocs", type=int, default=8)
    ap.add_argument("--maxcore", type=int, default=2500)
    ap.add_argument("--analyze", help="돌고 난 디렉터리")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.analyze:
        return analyze(a.analyze)
    if not a.pilot:
        ap.error("--pilot 또는 --analyze 또는 --selftest")
    return build(a.pilot, a.out, a.opt, a.nprocs, a.maxcore)


if __name__ == "__main__":
    sys.exit(main() or 0)
