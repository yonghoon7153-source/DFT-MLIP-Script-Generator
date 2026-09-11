#!/usr/bin/env python3
"""framework_site_census.py — C6 골격 게이트의 판정 근거: **원자별 자리 이탈 census** (개정안 §2).

왜 (회신 BL Q3)
  `--framework` 의 β 는 시간창 안의 곡선 모양이라 유계 운동(진동·회전)도 β≈0.45 를 낸다.
  `--framework_com` 의 골격 평균 MSD 는 소수 원자의 이동을 감춘다 (O 9개만 4 Å 움직여도 0.46 Å²).
  둘 다 "원자가 자리를 떠났나" 의 증거가 못 된다 → 원자 하나하나를 **직접 센다**.

규칙 (db/properties/lpsocl_box331_closure_amendment_2026_09_11.json §2 · 결과 보기 전 고정)
  · P 결합 음이온: frame 0 에서 최근접 P 거리가 O ≤ 2.0 / S ≤ 2.6 Å 인 O·S.
    이탈 = **그 P** 와의 거리(MIC)가 O > 2.5 / S > 3.0 Å 를 **≥ 10 ps 연속** 유지.
    회전·진동은 P 에 붙은 채라 잡히지 않는다. 다른 P 로 옮겨 붙어도 원래 P 에서 멀어지므로 잡힌다.
  · 자유 음이온(P 에 안 붙은 S · Cl)과 P: frame 0 위치 대비 변위(골격 전체 평균 병진 제거, unwrap)가
    > 2.0 Å 를 ≥ 10 ps 연속 유지.
  · 런 판정: 이벤트 ≥ 1 → `framework_mobile`, 0 → `framework_rigid`. 원소별 이벤트·원자·시작 시각을 남긴다.

⛔ 이 도구가 못 하는 것
  · Li 는 보지 않는다 — Li 는 확산하는 것이 정상이다.
  · 왜 움직였는지(회전·재배열·확산)를 가르지 않는다 — 자리를 떠났는가만 센다.
  · β 를 계산하지 않고 β 경보를 지우지도 않는다 — 경보는 결과 파일에 보존된다.
  · 문턱을 정하지 않는다 — `--card` 에서 읽는다. 없으면 기본값을 쓰되 화면에 경고를 찍는다.
  · 셀이 변하는 궤적(NPT)은 unwrap 이 frame-0 셀을 쓰므로 정확하지 않다 — NVT 전용. 셀이 변하면 멈춘다.
  · 이탈 문턱 바로 아래(예: O 2.4 Å 유지)는 잡지 않는다 — 그래서 원자별 **최대 지표**를 같이 찍어 여유를 보인다.

  python3 tools/ionic/framework_site_census.py --traj .../T600/traj.xyz --out .../T600/site_census.json \
      --card db/properties/lpsocl_box331_closure_amendment_2026_09_11.json
  python3 tools/ionic/framework_site_census.py --selftest
"""
from __future__ import annotations
import argparse, json, os, pathlib, sys, tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aimd_jump_stats import read_traj, unwrap      # 같은 extxyz 리더 · 같은 unwrap (규약을 복제하지 않는다)

DEFAULTS = {"o_bond_A": 2.0, "s_bond_A": 2.6, "o_escape_A": 2.5, "s_escape_A": 3.0,
            "disp_escape_A": 2.0, "min_ps": 10.0}


def read_thresholds(card):
    d = json.loads(pathlib.Path(card).read_text(encoding="utf-8"))
    m = d["2_C6_분류기_감사_정의_결과_보기_전_고정"]["문턱_기계값"]
    return {k: float(m[k]) for k in DEFAULTS}


def mic_series(d, cells):
    """(T,3) 또는 (T,n,3) 차분에 프레임별 최소상 규약."""
    cinv = np.linalg.inv(cells)                                   # (T,3,3)
    f = np.einsum("t...i,tij->t...j", d, cinv)
    f -= np.round(f)
    return np.einsum("t...j,tji->t...i", f, cells)


def sustained_runs(mask, min_frames):
    """bool 배열에서 길이 ≥ min_frames 인 True 연속 구간 → [(start, length)]."""
    runs, n, i = [], len(mask), 0
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]:
                j += 1
            if j - i >= min_frames:
                runs.append((i, j - i))
            i = j
        else:
            i += 1
    return runs


def census(sym, pos, cells, dt_ps, th=DEFAULTS):
    sym = np.asarray(sym); pos = np.asarray(pos, float); cells = np.asarray(cells, float)
    T, N, _ = pos.shape
    if np.abs(cells - cells[0]).max() > 1e-6:
        raise SystemExit("⛔ 셀이 프레임마다 다르다 — 이 도구는 NVT(고정 셀) 전용이다. 멈춘다.")
    min_frames = max(1, int(round(th["min_ps"] / dt_ps)))
    fw = np.where(sym != "Li")[0]
    P = np.where(sym == "P")[0]
    events, peak = [], {}
    # ── (1) P 결합 음이온: 자기 P 와의 거리 ───────────────────────────────
    bonded = {}
    for a in np.where((sym == "O") | (sym == "S"))[0]:
        if len(P) == 0:
            break
        d0 = np.linalg.norm(mic_series((pos[0, P] - pos[0, a])[None], cells[:1])[0], axis=1)
        k = int(np.argmin(d0))
        bond = th["o_bond_A"] if sym[a] == "O" else th["s_bond_A"]
        if d0[k] <= bond:
            bonded[int(a)] = int(P[k])
    for a, p in bonded.items():
        d = np.linalg.norm(mic_series(pos[:, p] - pos[:, a], cells), axis=1)
        esc = th["o_escape_A"] if sym[a] == "O" else th["s_escape_A"]
        peak[a] = {"elem": str(sym[a]), "kind": "P-bonded", "P": p, "max_dP_A": float(d.max()), "escape_A": esc}
        for s, L in sustained_runs(d > esc, min_frames):
            events.append({"kind": "P-bonded", "elem": str(sym[a]), "atom": a, "P": p,
                           "start_ps": s * dt_ps, "length_ps": L * dt_ps, "peak_dP_A": float(d[s:s + L].max())})
    # ── (2) 자유 음이온·P: 골격 평균 병진 제거 후 변위 ──────────────────────
    free = [int(i) for i in fw if int(i) not in bonded and sym[i] in ("S", "Cl", "P", "O")]
    uw = unwrap(pos[:, fw], cells[0])                             # (T, n_fw, 3)
    disp = uw - uw[0]
    disp = disp - disp.mean(axis=1, keepdims=True)                # 골격 전체 평균 병진 제거
    idx = {int(i): j for j, i in enumerate(fw)}
    for a in free:
        m = np.linalg.norm(disp[:, idx[a]], axis=1)
        peak[a] = {"elem": str(sym[a]), "kind": "free", "max_disp_A": float(m.max()), "escape_A": th["disp_escape_A"]}
        for s, L in sustained_runs(m > th["disp_escape_A"], min_frames):
            events.append({"kind": "free", "elem": str(sym[a]), "atom": a,
                           "start_ps": s * dt_ps, "length_ps": L * dt_ps, "peak_disp_A": float(m[s:s + L].max())})
    by_elem = {}
    for e in events:
        by_elem.setdefault(e["elem"], {"events": 0, "atoms": set()})
        by_elem[e["elem"]]["events"] += 1; by_elem[e["elem"]]["atoms"].add(e["atom"])
    by_elem = {k: {"events": v["events"], "n_atoms": len(v["atoms"]), "atoms": sorted(v["atoms"])} for k, v in by_elem.items()}
    # 원소별 최대 지표 (이벤트 0 이라도 문턱까지 얼마나 갔나)
    margin = {}
    for a, q in peak.items():
        key = f"{q['elem']}/{q['kind']}"
        val = q.get("max_dP_A", q.get("max_disp_A"))
        if key not in margin or val > margin[key]["max_A"]:
            margin[key] = {"max_A": float(val), "escape_A": q["escape_A"], "atom": a}
    return {
        "n_frames": int(T), "dt_ps": dt_ps, "total_ps": T * dt_ps, "min_frames": min_frames,
        "thresholds": dict(th),
        "n_framework": int(len(fw)), "n_P_bonded_anions": len(bonded), "n_free": len(free),
        "verdict": "framework_mobile" if events else "framework_rigid",
        "n_events": len(events), "by_elem": by_elem, "events": events,
        "margin_max_by_elem_kind": margin,
        "⛔": "이 판정은 '자리를 떠났나' 만 본다. β 경보는 지우지 않는다 — 결과 파일에 병기한다.",
    }


def census_file(traj, dt_ps=None, th=DEFAULTS):
    sym, pos, cells = read_traj(traj)
    if dt_ps is None:
        side = pathlib.Path(traj).parent / "aimd_results.json"
        if side.is_file():
            dt_ps = float(json.loads(side.read_text())["save_fs"]) / 1000.0
        else:
            raise SystemExit("⛔ dt 를 모른다 — aimd_results.json 이 없으면 --dt_ps 를 주어라.")
    return census(sym, pos, cells, dt_ps, th)


# ── selftest: 합성 궤적 ──────────────────────────────────────────────────
def _base(T=600):
    L = 12.0
    sym = np.array(["P", "O", "S", "S", "S", "S", "Cl", "Li", "Li"])
    p0 = np.array([[6, 6, 6], [7.5, 6, 6], [6, 8.05, 6], [6, 6, 8.05], [3.95, 6, 6],   # P, O, 3 bonded S
                   [2, 2, 2], [11.8, 2, 2], [9, 9, 3], [3, 9, 9]], float)               # free S, Cl, Li×2
    pos = np.repeat(p0[None], T, axis=0)
    cells = np.repeat((np.eye(3) * L)[None], T, axis=0)
    return sym, pos, cells


def _write_extxyz(path, sym, pos, cells):
    L = cells[0]
    lat = " ".join(f"{v:.4f}" for v in L.reshape(-1))
    with open(path, "w") as f:
        for t in range(len(pos)):
            f.write(f"{len(sym)}\n")
            f.write(f'Lattice="{lat}" Properties=species:S:1:pos:R:3\n')
            w = pos[t] % np.diag(L)                       # wrapped 좌표로 쓴다 (PBC 경로 검사)
            for s, r in zip(sym, w):
                f.write(f"{s} {r[0]:.5f} {r[1]:.5f} {r[2]:.5f}\n")


def _selftest():
    ok = bad = 0
    def chk(c, m):
        nonlocal ok, bad
        print(("  ⭕ " if c else "  ⛔ ") + m); ok += c; bad += (not c)
    dt = 0.1                                   # ps → min_frames = 100 (10 ps)
    sym, pos, cells = _base()
    t = np.arange(len(pos))
    r0 = census(sym, pos, cells, dt)
    chk(r0["verdict"] == "framework_rigid" and r0["n_P_bonded_anions"] == 4 and r0["n_free"] == 3,
        "정지 궤적: rigid · P 결합 음이온 4(O1+S3) · 자유 3(S, Cl, P)")
    # (i) O 진동 0.8 Å → 최대 2.3 < 2.5
    p = pos.copy(); p[:, 1, 0] = 6 + 1.5 + 0.8 * np.sin(2 * np.pi * t / 5.0)
    r = census(sym, p, cells, dt)
    chk(r["n_events"] == 0 and 2.2 < r["margin_max_by_elem_kind"]["O/P-bonded"]["max_A"] < 2.35,
        "⛔음성: 진폭 0.8 Å 진동은 이벤트 0 (최대 2.3 Å 는 여유 지표에 남는다)")
    # (ii) 5 ps 일시 이탈 → 0 · min_ps 0.5 면 1 (지속 필터가 걸러낸 것임을 증명)
    p = pos.copy(); p[200:250, 1, 0] = 6 + 3.0
    chk(census(sym, p, cells, dt)["n_events"] == 0, "⛔음성: 5 ps 일시 이탈(3.0 Å)은 이벤트 0")
    th2 = dict(DEFAULTS); th2["min_ps"] = 0.5
    chk(census(sym, p, cells, dt, th2)["n_events"] == 1, "지속 문턱을 0.5 ps 로 내리면 같은 궤적이 1 이벤트 — 필터가 작동한다")
    # (iii) O 3.5 Å 이동 후 유지 → 1 이벤트 O, 시작 20 ps
    p = pos.copy(); p[200:, 1, 0] = 6 + 3.5
    r = census(sym, p, cells, dt)
    chk(r["n_events"] == 1 and r["by_elem"] == {"O": {"events": 1, "n_atoms": 1, "atoms": [1]}}
        and abs(r["events"][0]["start_ps"] - 20.0) < 1e-9 and r["verdict"] == "framework_mobile",
        "⭕양성: O 가 P 에서 3.5 Å 로 떠나 유지 → 1 이벤트 (O · 시작 20 ps) · mobile")
    # (viii) 결합 S 2.8 Å 유지 → 0 (S 문턱 3.0) — 원소별 문턱이 갈린다
    p = pos.copy(); p[200:, 2, 1] = 6 + 2.8
    chk(census(sym, p, cells, dt)["n_events"] == 0, "⛔음성: 결합 S 가 2.8 Å 로 늘어나 유지해도 S 문턱 3.0 아래라 0")
    p = pos.copy(); p[200:, 2, 1] = 6 + 3.2
    chk(census(sym, p, cells, dt)["by_elem"].get("S", {}).get("events") == 1, "결합 S 3.2 Å 유지 → S 이벤트 1")
    # (iv) 자유 S 3 Å 병진 후 유지 → free 이벤트 1
    p = pos.copy(); p[100:, 5, 0] += 3.0
    r = census(sym, p, cells, dt)
    chk(r["n_events"] == 1 and r["events"][0]["kind"] == "free" and r["events"][0]["elem"] == "S",
        "⭕양성: 자유 S 가 3 Å 옮겨 유지 → free 이벤트 1")
    # (v) 골격 전체 병진 5 Å (COM drift) → 0
    p = pos.copy(); p[:, :, 0] += 5.0 * t[:, None] / len(t)
    chk(census(sym, p, cells, dt)["n_events"] == 0, "⛔음성: 골격 전체가 5 Å 병진(드리프트)해도 COM 제거로 0")
    # (vi) PBC: Cl 이 x=11.8±0.3 으로 경계를 넘나든다 (wrapped 좌표) → 0
    p = pos.copy(); p[:, 6, 0] = 11.8 + 0.3 * np.sin(2 * np.pi * t / 7.0); p = p % 12.0
    chk(census(sym, p, cells, dt)["n_events"] == 0, "⛔음성: 경계를 넘나드는 wrapped 좌표는 unwrap 으로 0")
    # (vii) extxyz 왕복 + 파일 경로 (CLI 가 타는 함수) → (iii) 재현
    p = pos.copy(); p[200:, 1, 0] = 6 + 3.5
    with tempfile.TemporaryDirectory() as td:
        f = os.path.join(td, "traj.xyz"); _write_extxyz(f, sym, p, cells)
        pathlib.Path(td, "aimd_results.json").write_text(json.dumps({"save_fs": 100.0}))
        r = census_file(f)
        chk(r["n_events"] == 1 and r["by_elem"]["O"]["events"] == 1 and abs(r["dt_ps"] - 0.1) < 1e-12,
            "extxyz 파일 경로 + aimd_results.json 의 save_fs 자동 읽기로 (iii) 재현")
        os.remove(os.path.join(td, "aimd_results.json"))
        try:
            census_file(f); ok_dt = False
        except SystemExit as e:
            ok_dt = "dt" in str(e)
        chk(ok_dt, "⛔음성: dt 를 모르면 멈춘다 (아무 값도 가정하지 않는다)")
    # (ix) 셀이 변하면 멈춘다
    c2 = cells.copy(); c2[300:] *= 1.01
    try:
        census(sym, pos, c2, dt); ok_cell = False
    except SystemExit as e:
        ok_cell = "NVT" in str(e)
    chk(ok_cell, "⛔음성: 셀이 프레임마다 다르면 SystemExit (NVT 전용)")
    # (x) 카드 문턱 읽기 = 기본값과 동일 (카드와 코드가 갈라지면 여기서 잡힌다)
    card = pathlib.Path(__file__).resolve().parents[2] / "db/properties/lpsocl_box331_closure_amendment_2026_09_11.json"
    if card.is_file():
        chk(read_thresholds(card) == DEFAULTS, "카드 §2 문턱_기계값 == 도구 기본값 (갈라지면 개정이 필요하다)")
    print(f"selftest: ⭕ {ok} · ⛔ {bad}")
    return 0 if bad == 0 else 1


def main():
    ap = argparse.ArgumentParser(description="C6 원자별 자리 이탈 census (개정안 §2)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--traj", help="extxyz 궤적 (Lattice 필수)")
    ap.add_argument("--dt_ps", type=float, help="프레임 간격 ps (없으면 옆의 aimd_results.json 의 save_fs)")
    ap.add_argument("--card", help="문턱을 읽을 개정안 카드 (없으면 기본값 + 경고)")
    ap.add_argument("--out", help="결과 JSON")
    a = ap.parse_args()
    if a.selftest:
        raise SystemExit(_selftest())
    if not a.traj:
        ap.error("--traj 가 필요하다 (--selftest 제외)")
    if a.card:
        th = read_thresholds(a.card); print(f"문턱 ← {pathlib.Path(a.card).name}: {th}")
    else:
        th = dict(DEFAULTS); print(f"⚠ 문턱을 카드가 아니라 기본값에서 썼다: {th} — 판정 기록에는 --card 로 다시.")
    r = census_file(a.traj, a.dt_ps, th)
    r["traj"] = str(a.traj); r["card"] = a.card
    print(f"[{a.traj}] frames={r['n_frames']} dt={r['dt_ps']} ps total={r['total_ps']:.1f} ps · 골격 {r['n_framework']} "
          f"(P결합 음이온 {r['n_P_bonded_anions']} · 자유 {r['n_free']})")
    print(f"  ★ 판정: **{r['verdict']}** · 이벤트 {r['n_events']}")
    for k, v in r["by_elem"].items():
        print(f"    {k}: {v['events']} 이벤트 · 원자 {v['n_atoms']}개 {v['atoms'][:10]}")
    for k, v in sorted(r["margin_max_by_elem_kind"].items()):
        print(f"    여유 {k}: 최대 {v['max_A']:.2f} Å / 문턱 {v['escape_A']} Å (원자 {v['atom']})")
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n")
        print(f"-> {a.out}")


if __name__ == "__main__":
    main()
