#!/usr/bin/env python3
"""arrhenius_compat.py — C3 **아레니우스 양립** 판정: ΔEa 를 공동 재표본으로 직접 잰다.

왜 별도 도구인가 (사다리 ②③ 를 밟고 왔다)
  `build_final_conductivity.py` 는 b2o3/modelc D 값이 **하드코딩**된 일회용이고
  C3 의 공동 재표본 절차가 없다. `msd_diffusive_check.py` 는 런 하나의 plateau 를
  보는 도구지 온도 3점을 잇지 않는다. 기존 도구에 플래그로 붙일 자리가 없다.

⛔ 이 도구가 재는 것 (lpsocl_box331_closure_conditions_2026_09_07.json C3)
  초판(*"시드 bootstrap 1σ 구간이 겹치면 양립"*)은 **회신 BG Q4 가 기각**했다:
    ① 두 구간 Ea 는 **800 K 값을 공유**하므로 독립 CI 가 아니다
    ② CI 겹침 자체가 두 값의 차이나 동등성을 판정하지 않는다
  그래서:
    ① **공동 재표본** — 각 표본에서 세 온도를 **함께** 뽑는다. 시드 하나는 세 온도를
       모두 돈 **한 런 묶음**이므로, 시드를 복원추출하면 800 K 공유 상관이 살아난다.
    ② ΔEa = Ea(600–800) − Ea(800–1000) 를 **직접** 계산한다.
    ③ CI(ΔEa) **전체**가 [−δ, +δ] 안 → compatible
    ④ CI 가 허용영역 **밖** → incompatible (곡률 주장 가능)
    ⑤ 경계와 겹침 → inconclusive / **HOLD**

  ⭐ 시드가 3개면 복원추출의 **정확한** 분포가 3³ = 27 표본이다 — 난수를 쓰지 않고
     전수 열거한다. 재현 가능하고 꼬리가 RNG 에 의존하지 않는다.
     CI 는 그 27점의 **95 % 백분위 구간**이다 (이 정의를 결과 보기 전에 박는다).

⛔ 이 도구가 **못 하는 것**
  · D 를 계산하지 않는다 — `msd_diffusive_check.py --mto` 의 값을 받는다.
    MSD 규약(창 2–50 ps · MTO · 자유절편)을 여기서 다시 구현하지 않는다
    (convention_check.py 가 감시하는 복제를 늘리지 않으려고).
  · plateau·홉·골격(C2·C2b·C6)을 판정하지 않는다 — 그건 앞 게이트다.
  · δEa 를 **정하지 않는다.** 카드에서 읽는다 (`--card`). 하드코딩 금지.
  · n=3 의 bootstrap 꼬리가 거칠다는 사실을 고치지 못한다 — 그래서 민감도 둘을 같이 찍는다.
  · 어느 온도를 뺄지 결정하지 않는다. 빠진 칸이 있으면 **시작하지 않는다**.

  python3 tools/ionic/arrhenius_compat.py --d d.json \
      --card db/properties/lpsocl_box331_closure_conditions_2026_09_07.json
  python3 tools/ionic/arrhenius_compat.py --selftest
"""
from __future__ import annotations
import argparse, itertools, json, math, pathlib, statistics, sys

KB = 8.617333262e-5          # eV/K


def ea_two_point(T1, D1, T2, D2):
    """두 온도 사이의 아레니우스 기울기 Ea [eV]. T1 < T2 를 가정하지 않는다."""
    if D1 <= 0 or D2 <= 0:
        raise ValueError("D 는 양수여야 한다")
    return KB * math.log(D2 / D1) / (1.0 / T1 - 1.0 / T2)


def delta_ea(D_by_T, temps):
    """ΔEa = Ea(T0–T1) − Ea(T1–T2). temps 는 오름차순 3개."""
    t0, t1, t2 = temps
    return (ea_two_point(t0, D_by_T[t0], t1, D_by_T[t1])
            - ea_two_point(t1, D_by_T[t1], t2, D_by_T[t2]))


def joint_resamples(table, temps, seeds):
    """⭐ **공동** 재표본 — 시드를 복원추출하고, 뽑힌 시드 묶음으로 세 온도를 **함께** 만든다.

    이것이 C3 의 핵심이다. 온도마다 따로 뽑으면 800 K 공유 상관이 깨진다.
    n 개 시드의 정확한 bootstrap 분포는 n**n 개 순서표본이다 — 전수 열거한다.
    """
    out = []
    for draw in itertools.product(range(len(seeds)), repeat=len(seeds)):
        picked = [seeds[i] for i in draw]
        D = {T: statistics.fmean(table[T][s] for s in picked) for T in temps}
        out.append(delta_ea(D, temps))
    return out


def independent_resamples(table, temps, seeds):
    """⛔ **대조용** — 온도마다 시드를 따로 고른다. C3 가 금지한 절차다.

    판정에 쓰지 않는다. 공동 재표본이 실제로 상관을 살리고 있는지 보는 **대조**다:
    시드 수준 상관이 있으면 공동 쪽 산포가 **더 좁아야** 한다.
    """
    out = []
    for combo in itertools.product(seeds, repeat=len(temps)):
        D = {T: table[T][s] for T, s in zip(temps, combo)}
        out.append(delta_ea(D, temps))
    return out


def percentile(vals, q):
    """백분위 (선형 보간). numpy 없이 — 이 도구는 stdlib 만 쓴다."""
    v = sorted(vals)
    if len(v) == 1:
        return v[0]
    k = (len(v) - 1) * q
    lo = math.floor(k); hi = math.ceil(k)
    return v[lo] if lo == hi else v[lo] + (v[hi] - v[lo]) * (k - lo)


def verdict(ci_lo, ci_hi, delta):
    """C3 ③④⑤ 를 그대로 옮긴다. 문턱은 호출부가 카드에서 읽어 넘긴다."""
    if ci_lo >= -delta and ci_hi <= delta:
        return "compatible", "CI 전체가 허용영역 [−δ, +δ] 안"
    if ci_lo > delta or ci_hi < -delta:
        return "incompatible", "CI 전체가 허용영역 밖 — 곡률 주장 가능"
    return "inconclusive", "CI 가 허용영역 경계와 겹친다 → HOLD (판정하지 않는다)"


def read_delta_from_card(path):
    """⛔ δEa 를 카드에서 **읽는다**. 도구가 정하지 않는다."""
    d = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    c3 = d["2_닫힘_조건"]["C3_아레니우스_양립_재설계_2026_09_07"]
    return float(c3["봉인_허용차_δEa_eV"]), c3.get("✅_비준", "")


def analyse(table, temps, seeds, delta):
    joint = joint_resamples(table, temps, seeds)
    lo, hi = percentile(joint, 0.025), percentile(joint, 0.975)
    v, why = verdict(lo, hi, delta)
    point = delta_ea({T: statistics.fmean(table[T][s] for s in seeds) for T in temps}, temps)
    loo = {}
    for drop in seeds:
        keep = [s for s in seeds if s != drop]
        loo[f"−{drop}"] = delta_ea(
            {T: statistics.fmean(table[T][s] for s in keep) for T in temps}, temps)
    indep = independent_resamples(table, temps, seeds)
    return {
        "temps": list(temps), "seeds": list(seeds),
        "delta_eV": delta,
        "dEa_point_eV": point,
        "joint_bootstrap": {"n": len(joint), "방식": "시드 복원추출 전수 열거 (n**n)",
                            "CI95": [lo, hi], "min": min(joint), "max": max(joint),
                            "median": statistics.median(joint)},
        "verdict": v, "why": why,
        "민감도_불확도_아님": {
            "leave_one_seed_out_dEa": loo,
            "independent_resample_spread": {
                "n": len(indep), "min": min(indep), "max": max(indep),
                "⛔": "C3 가 금지한 절차다. 공동 재표본이 상관을 살리는지 보는 대조일 뿐 판정에 쓰지 않는다"},
            "⛔": "이 둘은 **불확도가 아니라 민감도 진단**이다. 독립 반복으로 읽지 않는다"},
    }


def _selftest():
    ok = bad = 0
    def chk(c, m):
        nonlocal ok, bad
        print(("  ⭕ " if c else "  ⛔ ") + m); ok += c; bad += (not c)

    T = (600, 800, 1000)
    # ── 완전한 아레니우스(곡률 0)에서는 ΔEa = 0 ──────────────────────────
    Ea, D0 = 0.30, 1e-3
    D = {t: D0 * math.exp(-Ea / (KB * t)) for t in T}
    chk(abs(delta_ea(D, T)) < 1e-9, "직선 아레니우스면 ΔEa = 0")
    chk(abs(ea_two_point(600, D[600], 800, D[800]) - Ea) < 1e-9, "두점 Ea 가 참값을 준다")

    # ── 곡률을 넣으면 부호가 맞게 나온다 ─────────────────────────────────
    Dc = dict(D); Dc[800] = D[800] * 1.30          # 800 이 높다 = 저온구간 기울기가 커진다
    chk(delta_ea(Dc, T) > 0, "800 K 가 높으면 ΔEa > 0 (저온구간 Ea 가 크다)")
    Dc2 = dict(D); Dc2[800] = D[800] * 0.70
    chk(delta_ea(Dc2, T) < 0, "800 K 가 낮으면 ΔEa < 0")

    # ── ⭐ 공동 vs 독립 — 상관이 있으면 공동 쪽이 **좁아야** 한다 ─────────
    #    이것이 이 도구의 핵심 음성시험이다. 공동 재표본을 잘못 짜서 온도마다 따로
    #    뽑으면 둘이 같아지고, 그러면 C3 의 ① 요구를 안 지킨 것이다.
    seeds = ["s2", "s3", "s4"]
    bias = {"s2": 0.85, "s3": 1.00, "s4": 1.18}     # 시드 수준 공통 배수 = 완전 상관
    tab = {t: {s: D[t] * b for s, b in bias.items()} for t in T}
    j = joint_resamples(tab, T, seeds); i = independent_resamples(tab, T, seeds)
    jw, iw = max(j) - min(j), max(i) - min(i)
    chk(jw < 1e-9, "⭕양성: 시드 배수가 온도무관이면 공동 재표본 ΔEa 산포 = 0 (배수가 상쇄된다)")
    chk(iw > 10 * max(jw, 1e-12),
        "⛔음성: 독립 재표본은 같은 자료에서 **넓다** — 공동/독립이 같으면 상관을 안 살린 것이다")

    # ── 판정 경계 ────────────────────────────────────────────────────────
    chk(verdict(-0.01, 0.02, 0.05)[0] == "compatible", "CI 가 허용영역 안 → compatible")
    chk(verdict(0.08, 0.12, 0.05)[0] == "incompatible", "CI 가 허용영역 밖 → incompatible")
    chk(verdict(-0.02, 0.09, 0.05)[0] == "inconclusive", "⛔음성: 경계와 겹치면 HOLD — 판정하지 않는다")
    chk(verdict(-0.05, 0.05, 0.05)[0] == "compatible", "경계에 정확히 닿으면 포함(≤)으로 읽는다")

    # ── 빠진 칸은 시작하지 않는다 ────────────────────────────────────────
    try:
        delta_ea({600: 1e-5, 800: 2e-5}, T); ok_missing = False
    except KeyError:
        ok_missing = True
    chk(ok_missing, "⛔음성: 온도 칸이 비면 KeyError — 조용히 2점으로 맞추지 않는다")
    try:
        ea_two_point(600, 0.0, 800, 1e-5); ok_zero = False
    except ValueError:
        ok_zero = True
    chk(ok_zero, "⛔음성: D ≤ 0 을 거부한다 (log 가 조용히 -inf 가 되지 않는다)")

    print(f"selftest: ⭕ {ok} · ⛔ {bad}")
    return 0 if bad == 0 else 1


def main():
    ap = argparse.ArgumentParser(description="C3 아레니우스 양립 — ΔEa 공동 재표본")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--d", help='D 표 JSON: {"600":{"s2":1.2e-5,...},"800":{...},"1000":{...}} [cm^2/s]')
    ap.add_argument("--card", help="δEa 를 읽을 닫힘조건 카드 (하드코딩 금지)")
    ap.add_argument("--delta", type=float, help="⚠ 카드가 없을 때만. 쓰면 화면에 경고를 찍는다")
    ap.add_argument("--out", help="결과 JSON 경로")
    a = ap.parse_args()
    if a.selftest:
        raise SystemExit(_selftest())
    if not a.d:
        ap.error("--d 가 필요하다 (--selftest 제외)")

    raw = json.loads(pathlib.Path(a.d).read_text(encoding="utf-8"))
    table = {int(k): {s: float(v) for s, v in vv.items()} for k, vv in raw.items()}
    temps = tuple(sorted(table))
    if len(temps) != 3:
        raise SystemExit(f"⛔ 온도가 3점이어야 한다 — 받은 것: {temps}. "
                         "2점이면 C3(두 구간 비교)가 성립하지 않는다 → no_value 다.")
    seeds = sorted(set().union(*(set(v) for v in table.values())))
    missing = [(T, s) for T in temps for s in seeds if s not in table[T]]
    if missing:
        raise SystemExit(f"⛔ 빈 칸이 있다: {missing} — 시작하지 않는다. "
                         "어느 시드를 뺄지는 이 도구가 정하지 않는다(카드/1저자 결정).")

    if a.card:
        delta, ratified = read_delta_from_card(a.card)
        print(f"δEa = {delta} eV  ← 카드에서 읽음 ({pathlib.Path(a.card).name})")
        if ratified:
            print(f"  비준: {ratified[:80]}")
    elif a.delta is not None:
        delta = a.delta
        print(f"⚠ δEa = {delta} eV — **카드가 아니라 명령줄에서** 받았다. 판정 기록에 쓰지 말 것.")
    else:
        raise SystemExit("⛔ --card 또는 --delta 가 필요하다. δEa 를 도구가 정하지 않는다.")

    r = analyse(table, temps, seeds, delta)
    jb = r["joint_bootstrap"]
    print(f"\n온도 {temps} · 시드 {seeds}")
    print(f"  ΔEa (점추정)      = {r['dEa_point_eV']:+.4f} eV")
    print(f"  공동 재표본 {jb['n']}개 · CI95 = [{jb['CI95'][0]:+.4f}, {jb['CI95'][1]:+.4f}] eV"
          f"  (범위 [{jb['min']:+.4f}, {jb['max']:+.4f}])")
    print(f"  허용영역          = [{-delta:+.4f}, {+delta:+.4f}] eV")
    print(f"\n  ★ 판정: **{r['verdict']}**  — {r['why']}")
    if r["verdict"] == "inconclusive":
        print("     ⇒ C3 불충족 → **HOLD**. 값은 있으나 정밀도가 모자란 것이지 값이 없는 게 아니다.")
    print("\n  민감도 (⛔ 불확도가 아니다 — 독립 반복으로 읽지 말 것)")
    for k, v in r["민감도_불확도_아님"]["leave_one_seed_out_dEa"].items():
        print(f"    leave-one-out {k}: ΔEa = {v:+.4f} eV")
    ind = r["민감도_불확도_아님"]["independent_resample_spread"]
    print(f"    독립 재표본 대조 {ind['n']}개: [{ind['min']:+.4f}, {ind['max']:+.4f}] eV "
          f"(폭이 공동보다 넓어야 정상 — C3 가 금지한 절차다)")
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n")
        print(f"\n-> {a.out}")


if __name__ == "__main__":
    main()
