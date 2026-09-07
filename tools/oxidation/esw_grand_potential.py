#!/usr/bin/env python3
"""esw_grand_potential.py — REAL electrochemical stability window (ESW)
via the grand-potential phase-diagram method (Ong 2008; Mo/Ong/Ceder 2012,
Chem. Mater. 24, 15; Zhu/He/Mo 2015, JMCA).

This is the genuine ESW — NOT the qualitative "competing-phase energy span"
hint from tools/doping/esw_check.py. The Li reservoir is opened (grand
canonical) and the composition's Li-grand-potential decomposition is tracked
as the applied potential (= μ_Li) is scanned, using pymatgen's standard
`PhaseDiagram.get_element_profile`.

Why get_element_profile (and not "place compound at hull energy + scan")
-----------------------------------------------------------------------
For these argyrodite electrolytes the ordered phase is itself slightly
metastable (~tens of meV/atom above hull) and, more importantly, a
non-stoichiometric composition (modelc Li5.4PS4.4Cl1.6) has NO MP entry and
no MP-scale total energy of its own. get_element_profile needs only the
*composition* and the MP convex hull: it returns, as the Li chemical
potential is swept, the sequence of equilibrium decomposition reactions and
the critical μ_Li at which they switch. That makes comp1 (in MP) and modelc
(not in MP) directly comparable on the same footing.

Voltage convention
------------------
V (vs Li/Li+) = μ_Li(metal) − μ_Li ,  with e = 1, energies in eV.
V = 0  → μ_Li = Li-metal reference (most reducing).
High V → low μ_Li (most oxidizing).

  • Reduction (cathodic) limit = lowest V above which NO further Li is taken
    up (below it the composition is reduced — Li3P / Li2S / Li metal form).
  • Oxidation (anodic) limit  = highest V below which NO Li is released
    (above it the composition is oxidized — S / P2S5 / Cl2 form).
  • ESW width = anodic − cathodic.

Usage (run where MP_API_KEY is set, e.g. gabia/kserver116-27):
    python3 esw_grand_potential.py \
        --target "Li6PS5Cl:comp1" "Li5.4P1S4.4Cl1.6:modelc" \
        --out esw_lpscl_results.json
"""
import argparse
import json
import os
from pathlib import Path


def get_chemsys_entries(elements):
    """MP2020-corrected entries for the chemsys, pinned to the classic
    GGA/GGA+U mixed hull (avoids R2SCAN mixing noise; matches the Mo/Ong
    literature numbers)."""
    key = os.environ.get("MP_API_KEY") or os.environ.get("PMG_MAPI_KEY")
    chemsys = "-".join(sorted(elements))
    from mp_api.client import MPRester
    with MPRester(key) as mpr:
        entries = mpr.get_entries_in_chemsys(
            elements,
            additional_criteria={"thermo_types": ["GGA_GGA+U"]})
    print(f"[mp_api] {len(entries)} entries in {chemsys} (GGA_GGA+U hull)")
    return entries


def rxn_to_str(reaction):
    try:
        return str(reaction)
    except Exception:
        return repr(reaction)


# ── 열린 원소별 해석 (2026-09-07 추가) ───────────────────────────────────────
#: `evolution` 은 저장소와 **주고받은 몰수**다. 부호의 물리적 뜻이 **원소마다 다르다** —
#: 이걸 헷갈리면 산화를 환원이라 부르게 된다.
#:   Li 를 열면:  받아들임(+) = **환원**   · 내보냄(−) = **산화**
#:   O  를 열면:  받아들임(+) = **산화**   · 내보냄(−) = 환원(탈산소)
#: 그래서 결과 키를 `reduction/oxidation` 으로 박지 않고 **uptake/release** 로 중립화하고,
#: 원소별 해석 문자열을 결과에 같이 실어 보낸다.
OPEN_ELEMENT_MEANING = {
    "Li": {"uptake": "환원 (cathodic) — Li 를 받아들인다",
           "release": "산화 (anodic) — Li 를 내놓는다",
           "axis": "V_vs_Li"},
    "O":  {"uptake": "**산화** — 저장소(O₂)에서 O 를 받아들인다",
           "release": "환원/탈산소 — O 를 내놓는다",
           "axis": "dmu_O_eV"},
    "S":  {"uptake": "황화 (sulfidation)", "release": "탈황", "axis": "dmu_S_eV"},
}

#: ⛔⛔ O 를 열 때 반드시 같이 나가야 하는 경고. 데이터에 붙여 보낸다 — 화면에만 찍으면
#:   JSON 만 받은 사람이 μ_O 축을 절대값으로 읽는다.
O2_REFERENCE_CAVEAT = (
    "⛔ μ_O 축의 절대값을 믿지 말 것. (1) PBE 는 O₂ 분자를 ~1 eV 과결합하고, "
    "MP 는 anion correction 으로 보정한다 — 그래서 이 축은 **MP 보정 기준계**의 것이다. "
    "(2) UMA 등 다른 방법의 에너지와 **섞으면 축이 통째로 밀린다**. "
    "(3) pO₂·온도 환산은 이 도구가 하지 않는다 — 환산은 기준 선택이 결과를 지배하는 자리라 "
    "고체 기준반응(예: Li₂O 생성)에 앵커한 뒤 별도로 한다. "
    "여기서 인용 가능한 것은 **Δμ_O 축 위의 순서와 분해산물 정체**다."
)


def steps_from_profile(profile, open_symbol, mu_ref, rxn=rxn_to_str):
    """profile(dict 리스트) → steps. **순수 함수** — pymatgen·MP 없이 시험할 수 있다.

    ⚠ `V_vs_Li` 는 **Li 를 열었을 때만** 낸다. 'V vs Li/Li⁺' 는 Li 저장소에서만 뜻이 있고,
      O 를 연 프로파일에 전압 칸을 붙이면 읽는 사람이 산소압을 전압으로 읽는다.
    """
    steps = []
    for p in profile:
        mu = float(p["chempot"])
        s = {
            f"mu_{open_symbol}_eV": round(mu, 4),
            f"dmu_{open_symbol}_eV": round(mu - mu_ref, 4),
            f"evolution_{open_symbol}": round(float(p["evolution"]), 4),
            "reaction": rxn(p["reaction"]),
        }
        if open_symbol == "Li":
            s["V_vs_Li"] = round(mu_ref - mu, 3)
        if p.get("energy") is not None:
            s["energy_per_atom"] = round(float(p["energy"]), 5)
        steps.append(s)
    return steps


def limits_from_steps(steps, open_symbol):
    """교환 경계를 μ 축에서 찾는다. **원소에 무관한 한 가지 규칙**을 쓴다.

      받아들이기(uptake)는 μ 가 **높을수록** 일어난다 ⇒ 개시점 = `min(μ | evolution>0)`
      내보내기(release)는 μ 가 **낮을수록** 일어난다 ⇒ 개시점 = `max(μ | evolution<0)`

    Li 로 환산하면 V = μ_ref − μ 라 부호가 뒤집혀, 종전의
    `reduction_limit = max(V over pos)` · `oxidation_limit = min(V over neg)` 와 **같은 값**이다.
    (그래서 Li 경로는 동작이 안 바뀐다 — selftest 가 이걸 본다.)
    """
    mk = f"mu_{open_symbol}_eV"
    ek = f"evolution_{open_symbol}"
    pos = [s for s in steps if s[ek] > 1e-6]
    neg = [s for s in steps if s[ek] < -1e-6]
    neu = [s for s in steps if abs(s[ek]) <= 1e-6]
    return {
        "uptake_onset_mu_eV": min((s[mk] for s in pos), default=None),
        "release_onset_mu_eV": max((s[mk] for s in neg), default=None),
        # 중립(자기분해) 지점은 μ 가 제일 높은 쪽을 택한다 — Li 경로의 min(V) 와 같다
        "neutral_mu_eV": max((s[mk] for s in neu), default=None),
    }


def analyze(pd, comp, mu_ref, label, comp_str, open_symbol="Li"):
    """Run get_element_profile for the opened element and extract the limits."""
    from pymatgen.core import Element
    X = Element(open_symbol)

    # evolution profile of the OPEN element for this composition.
    # {'chempot','evolution','reaction','energy'}, sorted by DECREASING chempot.
    profile = pd.get_element_profile(X, comp)
    n_nominal = comp[X] if X in comp else 0.0

    steps = steps_from_profile(profile, open_symbol, mu_ref)
    lim = limits_from_steps(steps, open_symbol)
    mean = OPEN_ELEMENT_MEANING.get(
        open_symbol, {"uptake": f"{open_symbol} 를 받아들인다",
                      "release": f"{open_symbol} 를 내놓는다",
                      "axis": f"dmu_{open_symbol}_eV"})
    mk = f"mu_{open_symbol}_eV"
    ek = f"evolution_{open_symbol}"

    def reaction_at(mu):
        if mu is None:
            return None
        return min(steps, key=lambda s: abs(s[mk] - mu))["reaction"]

    def fmt(mu):
        if mu is None:
            return "—"
        if open_symbol == "Li":
            return f"{mu_ref - mu:+.2f} V"
        return f"Δμ {mu - mu_ref:+.3f} eV"

    print(f"\n=== {label}  {comp_str}  (열린 원소: {open_symbol}) ===")
    print(f"  nominal n_{open_symbol} = {float(n_nominal):.3f}"
          f"   ·  μ_ref({open_symbol}) = {mu_ref:.4f} eV/atom")
    print(f"  중립(자기분해)     @ {fmt(lim['neutral_mu_eV'])} → {reaction_at(lim['neutral_mu_eV'])}")
    print(f"  받아들임 개시      @ {fmt(lim['uptake_onset_mu_eV'])}  [{mean['uptake']}]")
    print(f"                     → {reaction_at(lim['uptake_onset_mu_eV'])}")
    print(f"  내보냄 개시        @ {fmt(lim['release_onset_mu_eV'])}  [{mean['release']}]")
    print(f"                     → {reaction_at(lim['release_onset_mu_eV'])}")
    print(f"  전체 프로파일 ({len(steps)} 분기점):")
    for s in steps:
        print(f"    {fmt(s[mk]):>14}  n={s[ek]:>7.3f}  {s['reaction']}")

    out = {
        "composition": comp_str,
        "label": label,
        "open_element": open_symbol,
        f"n_{open_symbol}_nominal": float(n_nominal),
        f"mu_{open_symbol}_ref_eV": round(mu_ref, 4),
        "meaning": mean,
        "uptake_onset_rxn": reaction_at(lim["uptake_onset_mu_eV"]),
        "release_onset_rxn": reaction_at(lim["release_onset_mu_eV"]),
        "neutral_rxn": reaction_at(lim["neutral_mu_eV"]),
        "profile": steps,
        **lim,
    }
    if open_symbol == "Li":
        # 종전 키 유지 — 이 이름으로 인용된 기존 결과(b2o3_esw.json 등)가 있다
        V = lambda mu: (None if mu is None else round(mu_ref - mu, 3))
        out.update({
            "n_Li_nominal": float(n_nominal),
            "mu_Li_ref_eV": round(mu_ref, 4),
            "reduction_limit_V": V(lim["uptake_onset_mu_eV"]),
            "oxidation_limit_V": V(lim["release_onset_mu_eV"]),
            "ocv_self_decomposition_V": V(lim["neutral_mu_eV"]),
            "ocv_self_decomposition_rxn": reaction_at(lim["neutral_mu_eV"]),
            "oxidation_onset_rxn": reaction_at(lim["release_onset_mu_eV"]),
        })
    if open_symbol == "O":
        out["⛔_caveat"] = O2_REFERENCE_CAVEAT
    return out


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", nargs="+", required=True,
                    help='comp:label, e.g. "Li6PS5Cl:comp1" '
                         '"Li5.4P1S4.4Cl1.6:modelc"')
    ap.add_argument("--elements", nargs="+", default=["Li", "P", "S", "Cl"])
    ap.add_argument("--open_element", default="Li",
                    help="저장소를 여는 원소. 기본 Li(전기화학 ESW). **O 를 주면 산소 노출** "
                         "(LPSCl + O₂) 의 μ_O staircase 가 나온다. ⚠ 부호의 뜻이 원소마다 "
                         "다르다 — O 는 받아들임(+)이 **산화**다.")
    ap.add_argument("--out", default="esw_grand_potential_results.json")
    ap.add_argument("--exclude_phases", nargs="*", default=[],
                    help="Phases to drop from the hull, by reduced FORMULA or MP-id "
                         "(Gil-González 2022 set: LiS4 SCl3 Li5PS4Cl2). Formula match "
                         "is robust to MP re-ids.")
    ap.add_argument("--selftest", action="store_true",
                    help="MP·pymatgen 없이 판정 논리만 시험 (음성 경로 포함)")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    # ⛔ 열 원소가 chemsys 에 없으면 hull 에 그 원소가 아예 없다 — 조용히 빈 프로파일이
    #   나오지 않게 여기서 멈춘다 (fail-closed).
    if args.open_element not in args.elements:
        raise SystemExit(
            f"⛔ --open_element {args.open_element} 가 --elements {args.elements} 에 없다. "
            f"O 를 열려면 --elements Li P S Cl O 처럼 chemsys 에 넣어야 한다.")

    from pymatgen.core import Element, Composition
    from pymatgen.analysis.phase_diagram import PhaseDiagram

    entries = get_chemsys_entries(args.elements)
    if args.exclude_phases:
        ex = set(args.exclude_phases)
        def _ids(e):
            # match by entry_id OR material_id OR reduced formula (MP re-ids phases,
            # so formula match is the robust one, e.g. --exclude_phases LiS4 SCl3 Li5PS4Cl2)
            return (str(getattr(e, "entry_id", "")) + "|"
                    + str((getattr(e, "data", {}) or {}).get("material_id", "")) + "|"
                    + e.composition.reduced_formula)
        dropped = [_ids(e) for e in entries if any(x in _ids(e) for x in ex)]
        entries = [e for e in entries if not any(x in _ids(e) for x in ex)]
        print(f"[exclude] dropped {len(dropped)} entries {sorted(ex)}: {dropped}")
    pd = PhaseDiagram(entries)
    X = Element(args.open_element)
    mu_ref = pd.el_refs[X].energy_per_atom
    print(f"μ_{args.open_element}(element reference) = {mu_ref:.4f} eV/atom")
    if args.open_element == "O":
        print(f"  {O2_REFERENCE_CAVEAT}")

    results = {}
    for spec in args.target:
        comp_str, _, label = spec.partition(":")
        label = label or comp_str
        comp = Composition(comp_str)
        try:
            results[label] = analyze(pd, comp, mu_ref, label, comp_str,
                                     open_symbol=args.open_element)
        except Exception as e:
            print(f"  [error] {label}: {type(e).__name__}: {e}")
            results[label] = {"composition": comp_str, "error": str(e)}

    payload = {
        "method": "grand-potential element profile via PhaseDiagram.get_element_profile "
                  f"(Mo/Ong/Ceder 2012); MP GGA_GGA+U corrected hull; **{args.open_element} opened**.",
        "open_element": args.open_element,
        "elements": args.elements,
        "excluded_phases": args.exclude_phases,
        f"mu_{args.open_element}_ref_eV": round(mu_ref, 4),
        "axis_convention": (
            "V = mu_Li(metal) - mu_Li; 0 V = Li metal" if args.open_element == "Li"
            else f"dmu_{args.open_element} = mu - mu_ref(element); 0 = 원소 기준상태. "
                 f"⚠ 전압(V vs Li/Li+)이 **아니다.**"),
        "results": results,
    }
    if args.open_element == "Li":
        payload["mu_Li_ref_eV"] = round(mu_ref, 4)     # 종전 키 유지
    if args.open_element == "O":
        payload["⛔_caveat"] = O2_REFERENCE_CAVEAT
    Path(args.out).write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"\n→ {args.out}")


# ── selftest ────────────────────────────────────────────────────────────────
def selftest():
    """판정 논리만 시험한다 (MP·pymatgen 불필요).

    ⛔ 여기서 **보증하지 못하는 것**: MP 엔트리 회수, hull 구성, `get_element_profile`
       자체의 정확도. 이 시험이 보는 것은 **프로파일을 받은 뒤 우리가 하는 해석**뿐이다.
    """
    ok = bad = 0
    def chk(c, m):
        nonlocal ok, bad
        print(("  ⭕ " if c else "  ⛔ ") + m); ok += bool(c); bad += (not c)

    # μ 가 감소하는 순서 (pymatgen 관례). Li: μ 높음 = 저전압.
    prof = [{"chempot": -1.0, "evolution":  2.0, "reaction": "R_uptake_hi"},
            {"chempot": -2.0, "evolution":  1.0, "reaction": "R_uptake_lo"},
            {"chempot": -3.0, "evolution":  0.0, "reaction": "R_neutral"},
            {"chempot": -4.0, "evolution": -1.5, "reaction": "R_release"}]

    s_li = steps_from_profile(prof, "Li", mu_ref=-1.0)
    chk("V_vs_Li" in s_li[0], "Li 를 열면 전압축을 낸다")
    chk(s_li[3]["V_vs_Li"] == 3.0, f"V = μ_ref − μ (기대 3.0, 실제 {s_li[3]['V_vs_Li']})")
    L = limits_from_steps(s_li, "Li")
    chk(L["uptake_onset_mu_eV"] == -2.0, "받아들임 개시 = min(μ | evolution>0)")
    chk(L["release_onset_mu_eV"] == -4.0, "내보냄 개시 = max(μ | evolution<0)")
    # 종전 Li 공식과 같은 값인가 — 리팩터가 값을 바꾸지 않았다는 증거
    chk(round(-1.0 - L["uptake_onset_mu_eV"], 3) == 1.0,
        "⛔음성: 종전 `reduction_limit = max(V over pos)` 와 **같은 값**이 나온다")
    chk(round(-1.0 - L["release_onset_mu_eV"], 3) == 3.0,
        "⛔음성: 종전 `oxidation_limit = min(V over neg)` 와 **같은 값**이 나온다")

    s_o = steps_from_profile(prof, "O", mu_ref=-4.5)
    chk("V_vs_Li" not in s_o[0],
        "⛔음성: **O 를 열면 전압축을 안 낸다** (산소압을 전압으로 읽게 만들면 안 된다)")
    chk("dmu_O_eV" in s_o[0] and s_o[0]["dmu_O_eV"] == 3.5, "Δμ_O = μ − μ_ref")
    chk("evolution_O" in s_o[0] and "evolution_Li" not in s_o[0], "키가 열린 원소를 따라간다")
    O = limits_from_steps(s_o, "O")
    chk(O["uptake_onset_mu_eV"] == -2.0 and O["release_onset_mu_eV"] == -4.0,
        "경계 공식은 원소에 무관하다 (같은 프로파일 → 같은 μ)")
    chk("산화" in OPEN_ELEMENT_MEANING["O"]["uptake"]
        and "환원" in OPEN_ELEMENT_MEANING["Li"]["uptake"],
        "⛔음성: **O 의 받아들임은 산화, Li 의 받아들임은 환원** — 뜻이 뒤집혀 있다")

    # 경계: 교환이 한 방향뿐이면 반대쪽은 None (0 이 아니다)
    one = steps_from_profile([{"chempot": -1.0, "evolution": 1.0, "reaction": "r"}], "O", -1.0)
    chk(limits_from_steps(one, "O")["release_onset_mu_eV"] is None,
        "⛔음성: 없는 경계를 **0 으로 지어내지 않는다** (None)")
    chk(limits_from_steps([], "O")["uptake_onset_mu_eV"] is None, "빈 프로파일도 안 죽는다")
    chk("μ_O" in O2_REFERENCE_CAVEAT and "pO₂" in O2_REFERENCE_CAVEAT,
        "O₂ 기준 경고문이 데이터에 실려 나간다")

    print(f"  selftest: ⭕ {ok} · ⛔ {bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    main()
