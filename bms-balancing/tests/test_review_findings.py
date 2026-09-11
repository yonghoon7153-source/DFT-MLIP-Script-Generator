"""2026-09-10 적대적 리뷰(NO-GO)의 반례를 회귀 테스트로 고정한다.

리뷰어가 준 반례는 그대로 회귀 테스트로 박는다 (CLAUDE.md 작업규율 2).
각 테스트 이름 뒤 [Rn]/[An]/[Bn] 은 리뷰 문서의 항목 번호다.
"""
from __future__ import annotations
import csv, json, pathlib, re, sys
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bms_balancing import verify                                      # noqa: E402
from bms_balancing.model import LB5, UB5                              # noqa: E402


# ── A3 [P1] 실패한 optimizer 결과를 성공한 fit 으로 채택하면 안 된다 ────

def test_multistart_rejects_failed_optimizer(monkeypatch):
    """success=False 인 optimizer 결과는 후보에서 빠져야 한다."""
    def failed(_obj, start, **_kw):
        return SimpleNamespace(fun=0.0, x=np.asarray(start, float).copy(),
                               success=False, status=2, message="synthetic failure")
    monkeypatch.setattr(verify, "minimize", failed)
    best, val, sols = verify.multistart(lambda _p: 0.0, n_starts=3, seed=0)
    assert sols == [], "success=False 결과가 all_sols 에 들어갔다"
    assert best is None and not np.isfinite(val), \
        "전부 실패했는데 best 가 잡혔다 — 실패를 최적으로 채택한다"


def test_multistart_keeps_successful_results(monkeypatch):
    """성공한 결과는 그대로 채택돼야 한다 (위 수정이 과교정이 아님을 본다)."""
    def ok(_obj, start, **_kw):
        x = np.asarray(start, float).copy()
        return SimpleNamespace(fun=float(np.sum(x ** 2)), x=x,
                               success=True, status=0, message="ok")
    monkeypatch.setattr(verify, "minimize", ok)
    best, val, sols = verify.multistart(lambda p: float(np.sum(p ** 2)),
                                        n_starts=3, seed=0)
    assert best is not None and len(sols) == 3 and np.isfinite(val)


# ── B1 [P0] 근최적 집합의 **폭** 은 무작위 구름의 관측 폭이 아니다 ──────

class _Ridge:
    """γ 를 따라 평평한 굽은 골짜기. a_PE = 1 + 0.8·γ 위에서 목적함수가 일정.

    `eps` 가 골짜기의 **두께**다. eps → 0 이면 근최적 집합이 측도 0 이 되고,
    그때는 어떤 경사법도 골짜기를 끝까지 못 따라간다 (골짜기 위에서 제약의
    기울기가 0 이 되어 LICQ 가 깨진다). 실제 목적함수의 1 % 집합은 부피가
    있으므로 eps 가 큰 쪽이 현실에 가깝다.
    """
    c_cell = 1.0

    def __init__(self, eps=1e-2):
        self.eps = eps

    def __call__(self, p):
        p = np.asarray(p, float)
        return 1.0 + ((p[0] - (1.0 + 0.8 * p[4])) / self.eps) ** 2


def _ridge_args(**kw):
    base = dict(data_root=".", source="GITT", state="300_0009", si_source="Li",
                w_dqdv=0.0, seed=0, starts=1, samples=400, tol=0.01, out=None,
                grid=21)
    base.update(kw)
    return SimpleNamespace(**base)


def _run_ridge(monkeypatch, capsys, eps):
    """참 폭 40 %p (a_PE ∈ [1.0, 1.4]) 인 골짜기에서 cmd_degeneracy 를 돌린다."""
    ridge = _Ridge(eps)
    best = np.array([1.2, -0.25, 1.2, -0.2, 0.25])
    monkeypatch.setattr(verify.D, "data_root", lambda _p=None: pathlib.Path("."))
    monkeypatch.setattr(verify, "build", lambda *_a, **_k: ridge)
    monkeypatch.setattr(verify, "multistart", lambda *_a, **_k: (best.copy(), 1.0, []))
    monkeypatch.setattr(verify, "degradation_modes",
                        lambda _rp, _rc, p, _c: {"LAM_PE": float(np.asarray(p)[0] - 1.0),
                                                 "LAM_NE": 0.0, "LLI": 0.0})
    verify.cmd_degeneracy(_ridge_args())
    import json
    return json.loads(capsys.readouterr().out)


def test_degeneracy_recovers_ridge_with_volume(monkeypatch, capsys):
    """부피가 있는 골짜기(실제 목적함수급)에서는 참 폭을 되찾아야 한다."""
    out = _run_ridge(monkeypatch, capsys, eps=1e-2)
    span = out["LAM_PE_percent"]["span"]
    cloud = out["LAM_PE_percent_observed_cloud"]["span"]
    assert span > 35.0, f"참 40 %p 골짜기에서 {span:.2f} %p 만 되찾았다"
    assert cloud < 5.0, "이 반례의 요점은 무작위 구름이 골짜기를 놓친다는 것이다"


def test_degeneracy_beats_random_cloud_on_measure_zero_ridge(monkeypatch, capsys):
    """측도 0 골짜기(리뷰어 원본 eps=1e-8)에서도 구름보다 훨씬 넓어야 한다.

    여기서 참 40 %p 를 다 되찾지는 못한다 (실측 24.09 %p). 골짜기 위에서
    제약의 기울기가 사라져 경사법이 미끄러지지 못하기 때문이고, 이건 방법의
    결함이 아니라 측도 0 집합의 성질이다. 그래도 전 판의 **0.00 %p** 와는
    질적으로 다르다.
    """
    out = _run_ridge(monkeypatch, capsys, eps=1e-8)
    span = out["LAM_PE_percent"]["span"]
    cloud = out["LAM_PE_percent_observed_cloud"]["span"]
    assert cloud < 1.0, f"구름이 {cloud:.2f} %p 를 봤다 — 반례가 약해졌다"
    assert span > 15.0, (
        f"측도 0 골짜기에서 {span:.2f} %p — 무작위 구름({cloud:.2f} %p)보다 "
        "충분히 넓지 않다")
    assert out["LAM_PE_percent"]["is_lower_bound"] is True, \
        "이 값은 하한이라는 표시가 결과에 남아 있어야 한다"


#: 철회·정정을 적은 줄은 그 숫자를 **주장하는** 줄이 아니다. 문서가 옛 주장을
#: 인용해 취소하는 것은 올바른 행동이므로 검사에서 빼야 한다 (첫 판이 여기서
#: 오탐을 냈다 — 정정문 자체를 위반으로 셌다).
_RETRACTION = ("철회", "정정", "거짓", "약화", "전 판", "**신규**", "리뷰",
               "보다 넓다", "문서가 적은")


def _asserting_lines(text: str, *needles: str) -> list[str]:
    """needles 를 전부 포함하면서 그 숫자를 **주장하는** 줄만 골라낸다.

    주장이 아닌 두 경우를 뺀다:
      · 철회·정정을 적은 줄 (`_RETRACTION`)
      · **비교표 행** — 철회값과 새 정본값을 나란히 놓은 마크다운 표 줄.
        우리 표 규약상 정본값은 `**…**` 로 굵게 적으므로, `|` 로 시작하면서
        굵은 값이 같이 있는 줄은 비교이지 주장이 아니다.
        (2026-09-10: §3-3 의 "철회한 값 vs 새 값" 표가 여기서 오탐을 냈다.)
    """
    out = []
    for ln in text.splitlines():
        if not all(n in ln for n in needles):
            continue
        if any(m in ln for m in _RETRACTION):
            continue
        if ln.lstrip().startswith("|") and "**" in ln:
            continue                      # 비교표 행
        out.append(ln)
    return out


# ── B1 [P0] 문서 숫자가 커밋된 산출과 어긋나면 안 된다 ─────────────────

def _profile_rows():
    p = ROOT / "out" / "profile_gamma_300_0009_Li.csv"
    return list(csv.DictReader(p.open(encoding="utf-8")))


def test_committed_profile_contradicts_no_documented_span():
    """커밋된 프로파일의 1 % 안 두 점이 이미 문서 숫자보다 넓으면 안 된다."""
    ins = [r for r in _profile_rows() if float(r["obj_ratio_to_best"]) <= 1.01]
    lam = [float(r["LAM_NE_pct"]) for r in ins]
    witness = max(lam) - min(lam)
    docs = (ROOT / "FINDINGS.md").read_text(encoding="utf-8") + \
           (ROOT / "README.md").read_text(encoding="utf-8")
    bad = _asserting_lines(docs, "0.87 %p")   # "0.875" 같은 부분일치 배제
    assert not bad, (
        f"문서가 1 % 안 LAM_NE 폭을 0.87 %p 라고 **주장**하는데, 커밋된 "
        f"프로파일의 1 % 안 두 점만으로 이미 {witness:.4f} %p 다. 문제 줄: {bad}")


# ── B4 [P1] matrix 요약은 사후선택 분모를 제목에 적어야 한다 ───────────

def _matrix_rows():
    p = ROOT / "out" / "matrix_300_0009.csv"
    rows = list(csv.DictReader(p.open(encoding="utf-8")))
    for r in rows:
        for k in ("w_dqdv", "LLI_pct", "LAM_NE_pct", "LAM_PE_pct"):
            r[k] = float(r[k])
    return rows


def test_lli_robustness_number_is_the_full_literature_axis():
    """'문헌 곡선 선택에 강건 0.53 %p' 는 GITT 8종 축의 값이 아니다."""
    rows = _matrix_rows()
    gitt_off = [r for r in rows if r["half_cell"] == "GITT" and r["w_dqdv"] == 0.0]
    full_axis = max(r["LLI_pct"] for r in gitt_off) - min(r["LLI_pct"] for r in gitt_off)
    assert len(gitt_off) == 8
    docs = (ROOT / "FINDINGS.md").read_text(encoding="utf-8")
    # ⚠ 문자열을 정확히 적지 않으면 테스트가 **통과한 척** 한다 (첫 판이 그랬다).
    #   마크다운 강조 기호가 섞이므로 '강건' 과 '0.53' 의 동시 등장으로 본다.
    robust_line = _asserting_lines(docs, "강건", "0.53")
    assert not robust_line, (
        f"0.53 %p 는 두 반쪽전지를 섞은 interior 6/16 행이고, Si 소스는 4종뿐이다. "
        f"'문헌 곡선 선택' 축의 정직한 값은 GITT 8종 {full_axis:.4f} %p 다. "
        f"문제 줄: {robust_line}")


def test_dqdv_shift_is_reported_from_matched_pairs():
    """dQ/dV 이동은 완전 대응쌍으로만 말해야 한다 (전체 16쌍은 부호가 섞인다)."""
    rows = _matrix_rows()
    by = {(r["half_cell"], r["si"], r["w_dqdv"]): r for r in rows}
    paired, matched = [], []
    for hc in sorted({r["half_cell"] for r in rows}):
        for si in sorted({r["si"] for r in rows}):
            a, b = by.get((hc, si, 0.0)), by.get((hc, si, 1.0))
            if a is None or b is None:
                continue
            d = b["LLI_pct"] - a["LLI_pct"]
            paired.append(d)
            if all(r["bounds"] == "-" and r["ref_bounds"] == "-" for r in (a, b)):
                matched.append(d)
    assert len(matched) == 3 and len(paired) == 16
    assert min(paired) < 0 < max(paired), "전체 16쌍은 부호가 섞여 있어야 한다"
    docs = (ROOT / "FINDINGS.md").read_text(encoding="utf-8")
    assert not _asserting_lines(docs, "약 +2 %p 의 이동"), (
        f"완전 대응쌍은 3개뿐이고 이동은 +{min(matched):.2f}~+{max(matched):.2f} %p 다. "
        f"전체 16쌍은 중앙값 {float(np.median(paired)):+.2f} %p, 음수 "
        f"{sum(d < 0 for d in paired)}개다")


# ── A2 [P0] 포팅 대조는 보고값을 시작점에서 빼는 길이 있어야 한다 ──────

def test_port_offers_blind_mode():
    """보고값을 x0 로 넣지 않는 blind 재적합 경로가 있어야 한다."""
    import inspect
    src = inspect.getsource(verify.cmd_port)
    assert "args.blind" in src or "blind" in src, (
        "cmd_port 가 보고값을 항상 첫 시작점으로 넣는다 — 그건 독립 재적합이 아니다")


# ── 대조기가 **파일 정밀도보다 빡빡하게** 재면 안 된다 (2026-09-10 실측) ──

def test_compare_does_not_cry_wolf_on_printed_precision():
    """`%.10f` 로 적힌 CSV 를 1e-9 상대문턱으로 재면 없는 불일치를 보고한다.

    실측: MATLAB dd_eval 과 Python 이 rmse_pocv=0.0117453809 에서 상대차
    2.49e-09 로 나왔다. 그런데 `%.10f` 의 절대 양자화 ±0.5e-10 은 그 값에서
    **상대 4.26e-09** 다. 즉 관측된 차이는 두 구현의 차이가 아니라 **출력
    자리수**이고, 그 파일로는 그보다 정밀하게 비교할 수 없다.
    """
    import io, contextlib, tempfile
    from bms_balancing.verify import _compare_dd_eval, DD_EVAL_P

    BASE = {"c_cell": 74.671, "dv_lo": 0.1492985972, "dv_hi": 0.8507014028,
            "dv_n": 350.0, "dq_lo": 2.7926653307, "dq_hi": 4.1273346693,
            "E_PE_0p5": 3.8756842582, "E_NE_0p5_0p25": 0.1133989996,
            "dv_PE_0p5": 1.1237428984, "dv_NE_0p5_0p25": -0.0738972448}
    tmp = pathlib.Path(tempfile.mkdtemp()) / "_wolf.csv"
    py_P = [list(q) for q in DD_EVAL_P[:1]]
    py_vals = {"rmse_pocv": [0.0117453809 + 4.0e-11],
               "rmse_dvdq": [0.1182321473 + 2.0e-11]}
    lines = ["# dd_eval  state=pristine  halfcell=data/half_cell/GITT/  Si=Li  w_dqdv=0"]
    lines += [f"# {k},{v:.17g}" for k, v in BASE.items()]
    lines.append("a_PE,b_PE,a_NE,b_NE,gamma_Si,rmse_pocv,rmse_dvdq")
    lines.append(",".join([f"{x:.6f}" for x in DD_EVAL_P[0]]
                          + ["0.0117453809", "0.1182321473"]))
    tmp.write_text("\n".join(lines) + "\n")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _compare_dd_eval(dict(BASE), py_P, py_vals, tmp)
    txt = buf.getvalue()
    tmp.unlink(missing_ok=True)
    assert "전부 일치" in txt, (
        "적힌 자리수 안에서 같은 값인데 불일치로 보고했다 — 문턱이 파일 "
        f"정밀도보다 빡빡하다.\n{txt}")


# ── B4-4 [P1] matrix 는 기준(pristine)의 전체 적합을 같이 남겨야 한다 ──────

def test_matrix_row_carries_reference_fit():
    """`LAM = 1 − state/ref` 는 기준이 움직여도, 대상이 움직여도 같은 값이다.

    그래서 CSV 에 **기준의 전체 파라미터·목적함수**가 없으면 LAM/LLI 변화의
    원인을 분리할 수 없다. 커밋된 산출에는 `ref_bounds` 만 있다 (리뷰 B4).
    """
    import inspect
    src = inspect.getsource(verify.cmd_matrix)
    need = ["ref_a_PE", "ref_b_PE", "ref_a_NE", "ref_b_NE",
            "ref_gamma_Si", "ref_obj", "ref_c_cell", "c_cell"]
    missing = [k for k in need if f'"{k}"' not in src]
    assert not missing, (
        f"matrix 행이 기준 적합을 안 남긴다 — 빠진 것: {missing}. "
        "기준이 움직인 것인지 대상이 움직인 것인지 분리할 수 없다")


def test_matrix_summary_reports_matched_pairs():
    """dQ/dV on/off 는 **같은 조합의 대응쌍**으로만 보고해야 한다 (리뷰 B4)."""
    import inspect
    src = inspect.getsource(verify.cmd_matrix)
    assert "matched" in src or "대응쌍" in src, (
        "요약이 off/on 을 대응쌍으로 묶지 않는다 — 비대응 비교는 부호가 섞인다 "
        "(실측: 전체 16쌍 중 음수 5개, 범위 −21.03~+2.74 %p)")


# ── 문서에 적힌 폭이 **artifact 와 같은가** (2026-09-10) ──────────────────

def test_quoted_spreads_match_artifact():
    """정본은 `out/` 의 산출이고 문서 숫자는 사본이다 — 사본이 늙지 않게 잰다.

    실측 계기: `README.md` 가 LAM_NE 폭을 **8.93 %p** 로 적고 있었는데 그건
    `matrix_300_0009.csv`(v1, multistart 수정 **전**) 값이었다. 정본인 v2 는
    **10.8774 %p** 이고 `FINDINGS.md` §4-1 · `FOR_BMS_TEAM.md` §5-1 은 그쪽을
    적고 있었다. 즉 한 저장소 안에서 같은 조건의 같은 양이 두 값으로 돌아다녔다.
    """
    import csv
    art = ROOT / "out" / "matrix_300_0009_v2.csv"
    if not art.exists():                      # 산출이 없는 체크아웃에서는 건너뛴다
        return
    rows = [r for r in csv.DictReader(art.open())
            if "GITT" in r["half_cell"] and float(r["w_dqdv"]) == 0]
    assert len(rows) == 8, f"GITT · dQ/dV off 조합이 8개가 아니다: {len(rows)}"
    span = {k: max(float(r[k]) for r in rows) - min(float(r[k]) for r in rows)
            for k in ("LAM_NE_pct", "LAM_PE_pct", "LLI_pct")}

    # 문서가 이 조건으로 인용하는 값 — 소수 둘째 자리까지
    want = f"{span['LAM_NE_pct']:.2f}"        # 10.88
    stale = f"{8.9251:.2f}"                   # v1 값 — 어디에도 남아 있으면 안 된다
    for name in ("README.md", "FINDINGS.md", "FOR_BMS_TEAM.md", "INTRO.md"):
        txt = (ROOT / name).read_text(encoding="utf-8")
        assert stale not in txt, (
            f"{name} 에 v1 의 옛 폭 {stale} %p 가 남아 있다. 정본(v2)은 {want} %p 다 "
            f"— multistart 수정으로 답이 최대 5.857 %p 움직인 뒤의 값이다.")
    # 문서마다 자리수가 다르다 (FINDINGS 는 10.8774, 나머지는 10.88) — 둘 다 허용
    forms = {f"{span['LAM_NE_pct']:.{d}f}" for d in (2, 3, 4)}
    for name in ("README.md", "FINDINGS.md", "FOR_BMS_TEAM.md", "INTRO.md"):
        txt = (ROOT / name).read_text(encoding="utf-8")
        assert any(f in txt for f in forms), (
            f"{name} 이 정본 폭 {want} %p 를 어떤 자리수로도 안 적고 있다 "
            f"(허용: {sorted(forms)})")


def test_dump_table_in_matlab_readme_matches_artifact():
    """`matlab/README.md` 의 대조표는 사용자가 MATLAB 결과를 **맞대 볼 표**다.

    실측 계기: 그 표가 v1(`matrix_300_0009.csv`) 값에 멈춰 있었다 —
    Wetjen LAM_NE 15.04(v1) vs **16.67**(v2), Jiang 6.11 vs **5.79**.
    그 상태로 `dd_verify('dump')` 결과를 대면 **없는 불일치가 1.6 %p 나온다.**
    앞의 `test_quoted_spreads_match_artifact` 는 폭만 봐서 이걸 못 잡았다.
    """
    import csv, re
    art = ROOT / "out" / "matrix_300_0009_v2.csv"
    if not art.exists():
        return
    want = {r["si"]: r for r in csv.DictReader(art.open())
            if "GITT" in r["half_cell"] and float(r["w_dqdv"]) == 0}
    txt = (ROOT / "matlab" / "README.md").read_text(encoding="utf-8")

    seen = 0
    for si, r in want.items():
        m = re.search(rf"^\|\s*{si}\s*\|(.+)$", txt, re.M)
        assert m, f"matlab/README.md 대조표에 {si} 행이 없다"
        cells = [c.strip() for c in m.group(1).split("|")]
        for j, key in enumerate(("LAM_PE_pct", "LAM_NE_pct", "LLI_pct")):
            assert cells[j] == f"{float(r[key]):.2f}", (
                f"matlab/README.md {si} 행의 {key} 가 정본과 다르다: "
                f"적힌 값 {cells[j]} vs 정본 {float(r[key]):.2f} "
                f"(v1 표가 남아 있으면 MATLAB 대조에서 없는 불일치가 나온다)")
        seen += 1
    assert seen == 8, f"대조표에서 확인한 행이 8개가 아니다: {seen}"


# ── 대조기가 **파일이 더 정밀해도** 옛 기본값에 갇히면 안 된다 (2026-09-10) ──

def _write_dd_eval_csv(path, anchors, rows, cols, fmt):
    lines = ["# dd_eval  state=pristine  halfcell=data/half_cell/GITT/  Si=Li  w_dqdv=0"]
    lines += [f"# {k},{v:.17g}" for k, v in anchors.items()]
    lines.append("a_PE,b_PE,a_NE,b_NE,gamma_Si," + ",".join(cols))
    for r in rows:
        lines.append(",".join([f"{x:.6f}" for x in r[:5]]
                              + [format(v, fmt) for v in r[5:]]))
    pathlib.Path(path).write_text("\n".join(lines) + "\n")


_BASE16 = {"c_cell": 74.671, "dv_lo": 0.1492985972, "dv_hi": 0.8507014028,
           "dv_n": 350.0, "dq_lo": 2.7926653307, "dq_hi": 4.1273346693,
           "dq_n": 450.0, "n_peaks": 4.0, "w_peak_sum": 1220.5209098395,
           "w_peak_max": 7.0014383087, "dq_nuniq_p1": 500.0, "dq_nin_p1": 450.0,
           "E_PE_0p5": 3.8756842582, "E_NE_0p5_0p25": 0.1133989996,
           "dv_PE_0p5": 1.1237428984, "dv_NE_0p5_0p25": -0.0738972448}


def test_compare_uses_full_precision_when_file_has_it():
    """`%.17g` 로 적힌 파일을 `%.10f` 시절 기본값(1e-10)으로 재면 안 된다.

    실측 계기: 2026-09-10 192값 대조에서 판정문이 "남은 차이는 전부 CSV 출력
    반올림(**1e-10**) 안이다" 라고 찍혔다. 그런데 그 CSV 는 `%.17g` 였다.
    `printed_abs_tol` 이 `d = default_decimals` 로 시작해 `min()` 으로만
    깎여서, 파일이 **더 정밀해도** 10 자리 위로 못 올라갔다.

    결과는 **너무 관대한** 판정이다 — 실제로 남아 있던 상대 1e-12 수준의
    구현 차이를 "출력 반올림" 이라고 설명해 버렸다. 없는 불일치를 만드는
    반대쪽 실수(`test_compare_does_not_cry_wolf...`)만 막고 이쪽은 안 막혀
    있었다.
    """
    import io, contextlib, tempfile
    from bms_balancing.verify import _compare_dd_eval, printed_abs_tol, DD_EVAL_P

    cols = ["rmse_pocv", "rmse_dvdq", "rmse_dqdv", "rmse_dqdv_w"]
    m_vals = [0.0116757840981582, 0.118232147254087, 0.155185004941108, 0.224458095596453]
    tmp = pathlib.Path(tempfile.mkdtemp()) / "_prec.csv"
    _write_dd_eval_csv(tmp, _BASE16, [list(DD_EVAL_P[0]) + m_vals], cols, ".17g")

    # ① 파일이 17자리를 담고 있으면 한계도 그만큼 내려가야 한다
    tol = printed_abs_tol(tmp)
    assert tol < 1e-14, (
        f"`%.17g` 파일인데 한계가 {tol:.0e} 다 — 옛 기본값에 갇혀 있다")

    # ② 상대 3e-12 어긋난 Python 값을 "출력 반올림" 으로 설명하면 안 된다
    py_vals = {c: [v * (1 + 3e-12 if c == "rmse_dqdv" else 1)]
               for c, v in zip(cols, m_vals)}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _compare_dd_eval(dict(_BASE16), [list(DD_EVAL_P[0])], py_vals, tmp)
    txt = buf.getvalue()
    tmp.unlink(missing_ok=True)
    assert "남은 차이는 전부 CSV 출력 반올림" not in txt, (
        "적힌 자리수보다 큰 차이를 출력 반올림이라고 설명했다.\n" + txt)
    assert "실제 수치 차이" in txt, (
        "적힌 자리수보다 큰 실제 차이가 남았는데 그렇게 말하지 않았다.\n" + txt)

    # ③ 그런데도 **모델 차이라고 과장하면** 안 된다 — 3e-12 는 1e-9 아래다
    assert "목적함수 산술" not in txt, (
        "수치 잡음 수준(3e-12)을 모델 차이로 보고했다.\n" + txt)


# ── §2 의 숫자는 커밋된 원표에서 나와야 한다 (2026-09-10) ─────────────────

def _audit97():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "audit97", ROOT / "scripts" / "audit97.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    rows = list(m.load_rows())
    res = [(r, m.audit(r)) for r in rows]
    return m, rows, res


def test_findings_section2_numbers_come_from_the_committed_table():
    """§2 는 오랫동안 **원표 없이** 32/97 · 16/97 을 적어 왔다.

    2026-09-10 에 원표를 `out/bms97/` 에 넣었으므로, 이제 그 숫자는 주장이
    아니라 계산이어야 한다. 이 테스트는 표와 문서가 갈리면 깨진다 — 한쪽만
    고치는 것을 막는 것이 목적이다.
    """
    if not (ROOT / "out" / "bms97").is_dir():
        return
    m, rows, res = _audit97()
    assert len(rows) == 97, f"원표가 97 행이 아니다: {len(rows)}"

    got = {
        "bound": sum(1 for _, a in res if a["bounds"]),
        "ne": sum(1 for _, a in res if "LAM_NE_pct" in a["neg"]),
        "pe": sum(1 for _, a in res if "LAM_PE_pct" in a["neg"]),
        "lli": sum(1 for _, a in res if "LLI_pct" in a["neg"]),
    }
    want = {"bound": 32, "ne": 16, "pe": 2, "lli": 2}
    assert got == want, f"감사 수치가 달라졌다: {got} vs {want}"

    txt = (ROOT / "FINDINGS.md").read_text(encoding="utf-8")
    for label, n in (("경계", 32), ("LAM_NE", 16)):
        assert f"{n} / 97" in txt, f"§2 에 {label} {n}/97 이 안 적혀 있다"

    lam_ne = [float(r["LAM_NE_pct"]) for r in rows
              if r["state"] == "300_0009" and r.get("LAM_NE_pct")]
    span = max(lam_ne) - min(lam_ne)
    assert f"{span:.2f}" in txt, (
        f"§2 의 LAM_NE 폭이 원표와 다르다: 표 {span:.2f} %p")


def test_negative_lam_ne_is_arithmetic_not_correlation():
    """§2-1 의 인과 주장이 원표에서 실제로 성립하는지.

    (a) 보고된 LAM_NE 가 정의식으로 재계산되고,
    (b) 강한 음수(< −10 %)는 전부 「대상만 상한, 기준은 자유」이며,
    (c) 그 행들에서 음수가 되는 데 필요한 a_NE 문턱이 상자 상한 1.4 보다 낮다
        — 즉 상한을 낮췄으면 그 값이 나올 수 없었다.
    """
    if not (ROOT / "out" / "bms97").is_dir():
        return
    m, rows, _ = _audit97()
    ar = m.mode_arithmetic(rows)
    assert ar["worst"] < 1e-9, (
        f"LAM_NE 가 정의식으로 재계산되지 않는다 (최대 |Δ| {ar['worst']:.2e} %p) "
        "— 표가 자기일관적이지 않다는 뜻이므로 §2-1 의 논증이 성립하지 않는다")

    strong = [d for d in ar["neg"] if d["LAM_NE"] < -10]
    assert len(strong) == 5, f"강한 음수 행이 5 가 아니다: {len(strong)}"
    bad = [d for d in strong if not (d["target_at_ub"] and not d["ref_at_ub"])]
    assert not bad, f"「대상만 상한」이 아닌 강한 음수 행이 있다: {bad}"

    need = max(d["need"] * d["a_NE_ref"] for d in strong)
    assert need < 1.4, (
        f"음수가 되는 데 필요한 a_NE 문턱 {need:.3f} 이 상자 상한 1.4 이상이다 "
        "— 그러면 '상한이 그 값을 만들었다' 고 말할 수 없다")


# ── 잡음 추정기가 아는 σ 를 되찾는가 (2026-09-10) ─────────────────────────

def test_rice_sigma_recovers_known_noise():
    """`verify noise` 의 결론은 σ 추정치 위에 서 있다. 그 추정기를 먼저 잰다.

    반복측정이 없어도 σ 를 잴 수 있다는 것이 이 명령의 전제다. 2 차 차분
    추정기는 참 곡선이 매끄럽고 이웃 잡음이 독립일 때 그것을 준다 — 여기서는
    **σ 를 알고 있는 합성 곡선**에 걸어서 되찾는지 본다.
    """
    import numpy as np
    from bms_balancing.verify import rice_sigma

    rng = np.random.default_rng(20260910)
    q = np.linspace(0, 1, 1200)
    v = 3.05 + 1.15 * q ** 0.8 - 0.06 / (1 + np.exp(-(q - 0.30) / 0.035))
    for s_true in (0.05e-3, 0.2e-3, 0.5e-3, 1.0e-3, 2.0e-3):
        est = rice_sigma(v + rng.normal(0, s_true, q.size))
        assert 0.9 < est / s_true < 1.1, (
            f"σ={s_true*1e3:.2f} mV 를 {est*1e3:.3f} mV 로 추정했다 (비율 "
            f"{est/s_true:.3f}) — 10 % 밖이면 이 추정기 위의 결론을 못 쓴다")


def test_rice_sigma_collapses_on_presmoothed_signal_and_is_detectable():
    """**이미 평활된 신호에 쓰면 σ 가 무너진다.** 그것을 감지할 수 있어야 한다.

    이 함정이 실재한다: 재표본·평활된 곡선에 2 차 차분을 걸면 잡음이 상관되어
    추정치가 몇 배로 작아지고, 그러면 "부적합/잡음" 비율이 **거짓으로 커진다.**
    감지 장치는 1 차 차분의 lag-1 자기상관 — 독립 잡음이면 음수, 평활됐으면 양수.
    """
    import numpy as np
    from scipy.signal import savgol_filter
    from bms_balancing.verify import rice_sigma

    rng = np.random.default_rng(7)
    q = np.linspace(0, 1, 1200)
    v = 3.05 + 1.15 * q ** 0.8 - 0.06 / (1 + np.exp(-(q - 0.30) / 0.035))
    y = v + rng.normal(0, 0.5e-3, q.size)

    def ac1(z):
        d = np.diff(z)
        return float(np.corrcoef(d[:-1], d[1:])[0, 1])

    assert ac1(y) < 0, "원신호인데 lag-1 자기상관이 음수가 아니다"
    ys = savgol_filter(y, 11, 3)
    assert ac1(ys) > 0, "평활된 신호인데 감지가 안 된다 — 경고 장치가 무효다"
    assert rice_sigma(ys) < 0.5 * rice_sigma(y), (
        "평활 뒤 σ 가 안 무너졌다 — 그러면 이 테스트가 지키는 함정이 없는 것이다")


# ── 원통형 셀 변환기 (2026-09-10) ────────────────────────────────────────

def _make_cyl_source(root: pathlib.Path, caps=(0.379049, 0.377735, 0.363715, 0.345661)):
    """`prepare_cell.py` 가 기대하는 배치의 합성 소스."""
    import numpy as np, pandas as pd
    (root / "experiment/cylindrical").mkdir(parents=True, exist_ok=True)
    (root / "half cell ocv").mkdir(parents=True, exist_ok=True)

    def stage(x, x0, w):
        return 1 / (1 + np.exp(-(x - x0) / w))

    cols, n = {}, 800
    for k, ce in enumerate(caps):
        c = np.linspace(1e-5, ce, n)
        x = c / ce
        cols[f"{k}_capacity"] = c
        cols[f"{k}_voltage"] = (2.90 + 1.30 * x ** 0.8
                                - 0.06 * stage(x, 0.30, 0.035)
                                - 0.055 * stage(x, 0.62, 0.040))
    pd.DataFrame(cols).to_excel(
        root / "experiment/cylindrical/pOCV_#168.xlsx", index=True)

    m = 600
    pc = np.linspace(5.8e-8, 3.0e-4, m)
    nc = np.linspace(5.8e-8, 3.0e-4, m)
    u = nc / nc[-1]
    pd.DataFrame({
        "PE_capacity": pc, "PE_voltage": 4.4726 - 0.85 * (pc / pc[-1]) ** 1.3,
        "NE_capacity": nc,
        "NE_voltage": (1.11 * np.exp(-u / 0.012) + 0.24 * np.exp(-u / 0.9)
                       - 0.10 * stage(u, 0.30, 0.05)
                       - 0.05 * stage(u, 0.62, 0.05) + 0.005),
    }).to_excel(root / "half cell ocv/320mAh_cylindrical_cell_half_cell_ocv.xlsx",
                index=False)


def test_prepare_cell_builds_a_tree_data_py_can_read():
    """변환기가 만든 트리를 **실제로 적재해** 본다.

    `data.py` 를 고치지 않고 자료 쪽을 옮기는 것이 이 스크립트의 존재 이유다.
    그러므로 검사도 "파일이 생겼나" 가 아니라 **"검증 대상 적재기가 읽나"** 여야
    한다. 여기서 깨지면 새 셀 숫자를 하나도 못 믿는다.
    """
    import subprocess, tempfile, importlib.util
    import numpy as np

    tmp = pathlib.Path(tempfile.mkdtemp())
    src, out = tmp / "src", tmp / "out"
    # 문헌 곡선은 합성 xlsx 생성기에서 빌린다 (셀과 무관한 자료)
    subprocess.run([sys.executable, str(ROOT / "matlab/tests/gen_synth_xlsx.py"),
                    str(src)], check=True, capture_output=True)
    _make_cyl_source(src)

    r = subprocess.run([sys.executable, str(ROOT / "scripts/prepare_cell.py"),
                        "--src", str(src), "--cell", "#168", "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"변환기가 죽었다:\n{r.stdout}\n{r.stderr}"

    from bms_balancing import data as D
    caps = (0.379049, 0.377735, 0.363715, 0.345661)
    for state, want in zip(("pristine", "100", "200", "300_0009"), caps):
        c, v = D.load_full_cell(out, state)
        assert abs(c[-1] - want) < 1e-9, f"{state} 의 c_cell 이 원본과 다르다"
        assert v[0] < v[-1], f"{state} 전압이 오름차순이 아니다"

    # ⚠ 상태 **이름**이 맞게 붙었나. 위치 왕복만 보면 STATE_OF_COL 을 뒤집어도
    #   통과한다 (2026-09-10 변이 시험). 이름을 붙드는 것은 물리 제약뿐이다:
    #   열화하면 용량이 준다.
    got = [D.load_full_cell(out, s)[0][-1]
           for s in ("pristine", "100", "200", "300_0009")]
    assert all(x > y for x, y in zip(got, got[1:])), (
        f"상태 이름과 용량이 안 맞는다: {got} — 열화하면 c_cell 이 줄어야 한다")

    # 반쪽전지가 상태마다 **같은 측정**인가 (머리말 2번의 가정)
    import hashlib
    h = {s: hashlib.sha256(D.half_cell_path(out, "GITT", s).read_bytes()).hexdigest()
         for s in ("pristine", "100", "200", "300_0009")}
    assert len(set(h.values())) == 1, (
        "상태별 반쪽전지 파일이 서로 다르다 — 이 셀은 한 번만 쟀으므로 같아야 한다")

    # `300_0147` 은 **없어야** 한다. 조용히 다른 상태를 읽으면 안 된다.
    try:
        c, _ = D.load_full_cell(out, "300_0147")
        assert c.size == 0, "300_0147 이 없어야 하는데 자료가 나왔다"
    except (IndexError, KeyError):
        pass


# ── `interp1` 은 내림차순 x 를 받는다. `np.interp` 는 못 받는다 (2026-09-10) ──

def test_interp_handles_descending_x_like_matlab():
    """MATLAB `interp1` 은 **단조 감소** x 도 받는다. `np.interp` 는 못 받는다.

    실측 계기: 원통형 셀(#168) 을 붙였더니 `E_PE(0.5)` 가 **29.96 V** 로
    나왔다 (양극 OCP 가 30 V 일 수 없다). 그 셀의 양극 반쪽전지는 파우치와
    **반대 방향으로 측정**돼서, `HalfCell` 의 방향 정규화
    (`pe_c = 1 - pe_c/pe_c[-1]`)를 지나면 x 가 내림차순이 된다.

    파우치 자료는 오름차순이라 이 자리가 여태 안 드러났다. `np.interp` 는
    오름차순을 **가정만 하고 검사하지 않으므로** 조용히 틀린 값을 낸다 —
    범위 안 점까지 전부.
    """
    import numpy as np
    from bms_balancing.model import _interp_lin_extrap

    xs = np.linspace(0.0, 1.0, 11)
    ys = 4.4726 - 0.85 * xs ** 1.3
    for q in (0.0, 0.25, 0.5, 0.75, 1.0, 1.2, -0.2):
        up = float(_interp_lin_extrap(xs, ys, q)[0])
        dn = float(_interp_lin_extrap(xs[::-1], ys[::-1], q)[0])
        assert abs(up - dn) < 1e-12, (
            f"x={q}: 같은 곡선을 뒤집었더니 {up:.6f} vs {dn:.6f} 로 갈린다 — "
            "MATLAB interp1 은 두 방향 모두 같은 값을 낸다")


def test_interp_ascending_path_is_untouched():
    """내림차순을 고치면서 **오름차순 경로를 건드리면** 안 된다.

    파우치 셀의 모든 숫자가 오름차순 경로를 지나고, 그 값들은 MATLAB 과
    1e-13 수준에서 맞춰 놓은 것이다 (§1-0 · §1-8). 이 경로가 한 자리라도
    움직이면 그 대조가 전부 무효가 된다.
    """
    import numpy as np
    from bms_balancing.model import _interp_lin_extrap

    rng = np.random.default_rng(11)
    xs = np.sort(rng.random(200))
    ys = rng.normal(size=200)
    xq = np.concatenate([rng.random(50) * 1.4 - 0.2, xs[:5], xs[-5:]])
    got = _interp_lin_extrap(xs, ys, xq)

    # 손대기 전의 정의를 여기 그대로 다시 적어 대조한다
    want = np.interp(xq, xs, ys)
    lo, hi = xq < xs[0], xq > xs[-1]
    want[lo] = ys[0] + (ys[1] - ys[0]) / (xs[1] - xs[0]) * (xq[lo] - xs[0])
    want[hi] = ys[-1] + (ys[-1] - ys[-2]) / (xs[-1] - xs[-2]) * (xq[hi] - xs[-1])
    assert np.array_equal(got, want), "오름차순 경로가 바뀌었다 — 기존 대조가 무효가 된다"


# ── 판 번호가 붙은 산출은 **최신 판**을 읽어야 한다 (2026-09-10) ──────────

def test_compare_states_reads_the_latest_version():
    """`_v2` 가 있으면 그걸 읽어야 한다.

    이 저장소에서 옛 판을 읽고 쓴 실수가 하루에 **세 번** 있었다:
      · `README.md` 의 LAM_NE 폭 8.93 %p (v1) — 정본은 10.88 (v2)
      · `matlab/README.md` 의 dump 대조표 8 행 전부 v1
      · `compare_states.py` 첫 판이 `degeneracy_..._Li_v2.json` 을 못 잡고
        v1 을 읽었다 (정규식이 `_v2` 접미사를 안 봤다)
    도구가 조용히 옛 값을 읽으면 그 위의 모든 판단이 옛 값이 된다.
    """
    import importlib.util, json, tempfile
    spec = importlib.util.spec_from_file_location(
        "compare_states", ROOT / "scripts" / "compare_states.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    d = pathlib.Path(tempfile.mkdtemp())

    def deg(span):
        return {"best_modes_percent": {k: 1.0 for k in m.MODES},
                **{f"{k}_percent": {"span": span} for k in m.MODES}}

    (d / "degeneracy_S_Li.json").write_text(json.dumps(deg(111.0)))
    (d / "degeneracy_S_Li_v2.json").write_text(json.dumps(deg(222.0)))
    got = m.load_degeneracy(d)
    assert set(got) == {"S"}, f"상태가 하나여야 하는데 {sorted(got)} — 판을 상태로 셌다"
    assert got["S"]["j"]["LLI_percent"]["span"] == 222.0, (
        f"v1 을 읽었다 ({got['S']['file']}) — 최신 판을 읽어야 한다")
    assert got["S"]["file"].endswith("_v2.json")

    hdr = ("half_cell,si,w_dqdv,LAM_PE_pct,LAM_NE_pct,LLI_pct,bounds,ref_bounds\n")
    for name, lo in (("matrix_S.csv", 0.0), ("matrix_S_v2.csv", 50.0)):
        (d / name).write_text(hdr + "".join(
            f"GITT,Si{i},0,{lo+i},{lo+i},{lo+i},-,-\n" for i in range(3)))
    mx = m.load_matrix_axis(d)
    assert set(mx) == {"S"}, f"상태가 하나여야 하는데 {sorted(mx)}"
    assert mx["S"]["file"].endswith("_v2.csv"), f"v1 을 읽었다: {mx['S']['file']}"


# ── §1-10 의 순위 주장은 산출에서 나와야 한다 (2026-09-10) ────────────────

def test_section_1_10_ranking_comes_from_artifacts():
    """§1-10 의 핵심은 "LAM_NE 최광 · LLI 최협이 네 상태에서 그대로" 다.

    §2 에서 원표 없이 숫자를 적었다가 닫은 적이 있고, `compare_states.py` 가
    옛 판을 읽던 것도 잡았다. 같은 규율을 이 절에도 건다 — 순위가 산출에서
    실제로 나오는지, 그리고 100 사이클의 LLI/LAM_PE 가 사실상 동률이라는
    단서가 문서에 남아 있는지.
    """
    import json
    want = {"100": "out/degeneracy_100_Li.json",
            "200": "out/degeneracy_200_Li.json",
            "300_0009": "out/degeneracy_300_0009_Li_v2.json",
            "300_0147": "out/degeneracy_300_0147_Li.json"}
    got = {}
    for st, rel in want.items():
        f = ROOT / rel
        if not f.is_file():
            return                      # 산출이 없는 체크아웃에서는 건너뛴다
        d = json.loads(f.read_text(encoding="utf-8"))
        got[st] = {k: d[f"{k}_percent"]["span"] for k in ("LAM_PE", "LAM_NE", "LLI")}

    for st, sp in got.items():
        assert max(sp, key=sp.get) == "LAM_NE", (
            f"{st}: 가장 넓은 것이 LAM_NE 가 아니다 — {sp}")
        assert min(sp, key=sp.get) == "LLI", (
            f"{st}: 가장 좁은 것이 LLI 가 아니다 — {sp}")

    # 100 사이클의 LLI 와 LAM_PE 는 0.01 %p 안 — "사실상 동률" 이라는 단서가
    # 문서에 있어야 한다. 없으면 "LLI 가 가장 좁다" 가 과대 진술이 된다.
    gap = got["100"]["LAM_PE"] - got["100"]["LLI"]
    assert 0 < gap < 0.01, f"100 의 LAM_PE−LLI 가 {gap:.4f} %p — 가정이 바뀌었다"
    txt = (ROOT / "FINDINGS.md").read_text(encoding="utf-8")
    assert "동률" in txt, "§1-10 에 100 사이클이 사실상 동률이라는 단서가 없다"

    # 100 사이클의 LAM_NE 구간은 0 을 포함해야 한다 (부호도 못 정한다)
    d = json.loads((ROOT / want["100"]).read_text(encoding="utf-8"))["LAM_NE_percent"]
    assert d["min"] < 0 < d["max"], (
        f"100 의 LAM_NE 구간이 0 을 안 품는다: [{d['min']}, {d['max']}]")


# ── 문서가 산출물보다 뒤처지는 것을 기계가 잡는다 (2026-09-10) ────────────

#: 이 브랜치가 소유한 사람용 문서 전부. 새 문서를 만들면 여기 추가한다.
SCOPE_DOCS = ("FINDINGS.md", "README.md", "INTRO.md", "WORKING_STATE.md",
              "FOR_BMS_TEAM.md", "HANDOFF_TO_GATE.md", "CODEX_REVIEW_REQUEST.md")

#: `~~취소선~~` 은 "철회했다" 는 표시, `"..."` 는 남의(옛) 말을 옮긴 것.
#: 둘 다 **지금 하는 주장이 아니므로** 검사에서 뺀다.
NOT_A_CLAIM = re.compile(r"~~.*?~~|\u201c.*?\u201d|\".*?\"", re.S)

#: 상한 주장의 모양은 **범위를 셀과 상태로 같이 못 박는** 것이다.
#: 상했던 네 줄이 전부 이 모양이었다:
#:   "서브 결과는 한 셀 · 한 상태(`300_0009`) · 한 설정에 한정된다"
#:   "위 측정은 한 셀 · 주로 `300_0009` 한 상태 · 이 설정에 한정됩니다"
#:   "⑥ 한 상태·한 셀이다. `300_0009` 하나."
#: 반대로 "한 상태(`300_0009`)에서 LAM_NE 폭" 은 **측정의 범위**를 적은
#: 정당한 문장이라 잡으면 안 된다 — 그래서 `한 셀` 을 같이 요구한다.
CELL_SCOPE = "한 셀"
NARROWING = ("한 상태", "한정", "하나")


def _load_script(name: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_docs_do_not_claim_a_narrower_state_scope_than_out():
    """`out/` 에 상태가 여럿인데 문서가 "`300_0009` 한 상태" 라고 하면 실패.

    §1-10 이 상태 범위를 넷으로 넓힌 직후, 여섯 문서 중 **넷**이 여전히
    "한 셀·한 상태(`300_0009`)" 를 들고 있었다. 같은 유형(옛 판을 읽고 쓰기)이
    2026-09-10 하루에만 세 번 더 났다 (`scripts/compare_states.py` 머리말).
    사람이 여섯 군데를 손으로 맞추는 방식은 이미 실패했으므로 기계가 잡는다.

    철회(`~~취소선~~`)와 인용(`"..."`)은 지금 하는 주장이 아니라 검사에서
    빠진다. **셀 축은 못 잡는다** — 다른 셀 산출물은 이 저장소 밖에 있어서
    `out/` 만 봐서는 셀이 몇 개인지 알 수 없다. 셀 일반화가 닫히면
    "한 셀" 도 상하므로 그때 이 테스트를 같이 넓혀야 한다.
    """
    if not (ROOT / "out").is_dir():
        pytest.skip("out/ 이 없다 — 산출물 없이는 범위를 알 수 없다")
    states = _load_script("compare_states").load_degeneracy(ROOT / "out")
    if len(states) < 2:
        pytest.skip(f"out/ 의 상태가 {len(states)} 개 — 넓힌 적이 없다")

    bad = []
    for name in SCOPE_DOCS:
        p = ROOT / name
        if not p.is_file():
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            clean = NOT_A_CLAIM.sub("", line)
            if (CELL_SCOPE in clean and "300_0009" in clean
                    and any(t in clean for t in NARROWING)):
                bad.append(f"  {name}:{i}: {line.strip()}")
    assert not bad, (
        f"out/ 에는 상태가 {len(states)} 개({', '.join(sorted(states))})인데 "
        f"문서가 아직 한 상태라고 말한다:\n" + "\n".join(bad))


def test_review_request_clones_the_branch_that_owns_bms_balancing():
    """리뷰 요청문의 clone 명령이 **이 디렉터리를 소유한 브랜치**를 가리켜야.

    루트 `CLAUDE.md` 의 브랜치 표가 정본이다 (그 파일이 그렇게 못 박는다).
    2026-08-20 에 이 저장소에서 여덟 곳이 대체된 브랜치 이름을 붙들고 있었고,
    `wiki/` 쪽은 `wiki/tools/lint.py` 가 막는다. 여기가 그 짝이다 —
    리뷰어가 옛 브랜치를 clone 하면 `bms-balancing/` 의 뒤처진 사본을 본다.
    """
    claude_md = ROOT.parent / "CLAUDE.md"
    if not claude_md.is_file():
        pytest.skip("루트 CLAUDE.md 가 없다 — 정본을 읽을 수 없다")

    owner = None
    for line in claude_md.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*\|\s*`(claude/[^`]+)`\s*\|([^|]*)\|", line)
        if m and "bms-balancing/" in m.group(2):
            owner = m.group(1)
            break
    assert owner, "CLAUDE.md 브랜치 표에서 bms-balancing/ 소유 브랜치를 못 찾았다"

    req = (ROOT / "CODEX_REVIEW_REQUEST.md")
    if not req.is_file():
        pytest.skip("요청문이 없다")
    txt = req.read_text(encoding="utf-8")
    clones = re.findall(r"git clone -b (\S+)", txt)
    assert clones, "요청문에 clone 명령이 없다"
    assert all(c == owner for c in clones), (
        f"요청문이 `{clones}` 를 clone 하라고 한다. "
        f"`bms-balancing/` 소유는 `{owner}` 다 (CLAUDE.md 브랜치 표)")


# ── 반쪽전지 대체가 어디까지 번지는가 — 산술로 고정한다 (2026-09-11) ──────

def test_half_cell_substitution_reaches_lli_not_just_lam_pe():
    """`a_PE`·`b_PE` 를 흔들면 **LLI 도 움직인다.** LAM_NE 만 절연돼 있다.

    2026-09-10 에 사용자에게 "반쪽전지를 대체해도 LAM_NE·LLI 는 영향이 적다"
    고 말했는데 **틀렸다.** 정의가
        c_lit = (a_PE + b_PE − b_NE)·c,  LLI = (c_lit_i − c_lit)/c_lit_i
    이므로 LLI 는 `a_PE`·`b_PE` 를 **직접** 쓴다. 원통형 셀은 반쪽전지를 한
    번만 재서 같은 파일을 여러 상태에 복사했으므로, 그 대체가 LLI 폭에
    그대로 들어간다 — 그것이 셀 일반화를 아직 못 쓰는 이유다.

    말로 고치면 또 상하므로 산술로 박는다.
    """
    from bms_balancing.model import degradation_modes

    p_ref = [1.10, -0.02, 1.00, 0.00, 0.30]
    p     = [1.05, -0.03, 0.95, 0.01, 0.30]
    base = degradation_modes(p_ref, 74.671, p, 63.720)

    def bumped(i, d=1e-3):
        q = list(p); q[i] += d
        return degradation_modes(p_ref, 74.671, q, 63.720)

    for idx, name in ((0, "a_PE"), (1, "b_PE")):
        m = bumped(idx)
        assert abs(m["LAM_NE"] - base["LAM_NE"]) < 1e-15, (
            f"{name} 를 흔들었더니 LAM_NE 가 움직였다 — 절연이 깨졌다")
        assert abs(m["LLI"] - base["LLI"]) > 1e-6, (
            f"{name} 를 흔들었는데 LLI 가 그대로다. 정의상 LLI 는 {name} 를 "
            f"직접 쓴다 — 이 테스트나 정의 중 하나가 틀렸다")

    # a_PE 만은 LAM_PE 로도 간다 (b_PE 는 안 간다 — 둘을 섞어 말하지 않게)
    assert abs(bumped(0)["LAM_PE"] - base["LAM_PE"]) > 1e-6
    assert abs(bumped(1)["LAM_PE"] - base["LAM_PE"]) < 1e-15


def test_prepare_cell_does_not_repeat_the_retracted_lli_claim():
    """`prepare_cell.py` 머리말이 철회된 문장을 들고 있으면 실패.

    이 셀 자료를 만든 변환기라 그 머리말이 셀 결과를 읽는 사람의 첫 안내다.
    """
    txt = (ROOT / "scripts" / "prepare_cell.py").read_text(encoding="utf-8")
    RETRACTED = "LAM_NE\u00b7LLI 는 영향이 적다"
    # 정정문이 옛 문장을 **인용**하는 것은 허용한다 — 그때는 따옴표를 친다.
    # (`NOT_A_CLAIM` 을 그대로 쓰면 안 된다. 저건 마크다운용이라 Python 의
    #  `\"\"\"` 독스트링 구분자와 짝이 어긋나 엉뚱한 구간을 지운다 — 2026-09-11 실측.)
    bad = [f"  {i}: {ln.strip()}"
           for i, ln in enumerate(txt.splitlines(), 1)
           if RETRACTED in ln and '"' not in ln]
    assert not bad, (
        "철회된 문장이 인용 표시 없이 남아 있다 — LLI 는 a_PE·b_PE 를 직접 쓴다 "
        "(test_half_cell_substitution_reaches_lli_not_just_lam_pe):\n"
        + "\n".join(bad))


# ── 대조 실험(반쪽전지 고정)이 정말 고정본인지 기계가 말한다 (2026-09-11) ──

def _fixed_hc():
    return _load_script("fixed_hc")


def _fake_root(base, per_state=True):
    """xlsx 자리에 아무 바이트나 둔다 — `check` 는 **해시만** 보므로 충분하다."""
    hc = base / "data" / "half_cell" / "GITT"
    hc.mkdir(parents=True, exist_ok=True)
    for i, st in enumerate(("pristine", "100", "200", "300_0009")):
        (hc / f"{st}.xlsx").write_bytes(b"HC" + (bytes([i]) if per_state else b"\x00"))
    for rel in ("data/full_cell", "data/literature"):
        d = base / rel
        d.mkdir(parents=True, exist_ok=True)
        (d / "x.bin").write_bytes(b"same")
    return base


def test_fixed_hc_check_tells_fixed_from_per_state(tmp_path, capsys):
    """`check` 가 고정본과 상태별을 **해시로** 가른다.

    실행 로그의 "반쪽전지 소스: 100=GITT 200=GITT ..." 는 소스 *종류*만
    찍으므로 고정 여부를 못 알려준다. 대조 실험의 결론이 그 구분에 통째로
    걸려 있으므로 파일로 증명할 수 있어야 한다.
    """
    m = _fixed_hc()
    ns = SimpleNamespace

    per = _fake_root(tmp_path / "per", per_state=True)
    assert m.cmd_check(ns(root=str(per), expect="per-state")) == 0
    assert m.cmd_check(ns(root=str(per), expect="fixed")) == 2, \
        "상태마다 다른 루트를 '고정됨' 으로 통과시켰다"

    fix = _fake_root(tmp_path / "fix", per_state=False)
    assert m.cmd_check(ns(root=str(fix), expect="fixed")) == 0
    assert m.cmd_check(ns(root=str(fix), expect="per-state")) == 2

    out = capsys.readouterr().out
    assert "고정됨" in out and "상태마다 다름" in out


def test_fixed_hc_make_pins_every_state_to_one_file(tmp_path, capsys):
    """`make` 가 만든 루트는 반쪽전지가 전부 같은 파일이고, 나머지는 원본 그대로."""
    m = _fixed_hc()
    src = _fake_root(tmp_path / "src", per_state=True)
    out = tmp_path / "out"
    assert m.cmd_make(SimpleNamespace(src=str(src), out=str(out),
                                      pin="pristine")) == 0

    hc = sorted((out / "data" / "half_cell" / "GITT").glob("*.xlsx"))
    assert len(hc) == 4, f"상태 4 개가 아니다: {[p.name for p in hc]}"
    digests = {m.sha(p) for p in hc}
    assert len(digests) == 1, "고정했는데 파일이 서로 다르다"
    assert digests == {m.sha(src / "data" / "half_cell" / "GITT" / "pristine.xlsx")}, \
        "pristine 이 아닌 것으로 고정했다"

    # 반쪽전지 **말고는** 아무것도 안 바뀌어야 한다 — 축이 하나여야 대조가 성립한다
    for rel in ("data/full_cell/x.bin", "data/literature/x.bin"):
        assert m.sha(out / rel) == m.sha(src / rel), f"{rel} 이 달라졌다"


def test_fixed_hc_scan_parses_state_names_in_both_sources(tmp_path):
    """`scan` 이 두 소스의 이름 규칙에서 **같은 상태 이름**을 뽑아야 한다.

    `GITT/{state}.xlsx` 와 `step_005C/{state}_005C.xlsx` 다. 꼬리표를 자르는
    자리가 2026-09-11 에 실제로 틀렸었다 (`st[:-0]` → 빈 문자열). 상태 이름이
    뭉개지면 `check` 는 에러가 아니라 **"판정불가"** 를 내므로 조용히 지나간다.
    """
    m = _fixed_hc()
    want = ["100", "200", "300_0009", "pristine"]
    for src, name in (("GITT", "{}.xlsx"), ("step_005C", "{}_005C.xlsx")):
        d = tmp_path / "data" / "half_cell" / src
        d.mkdir(parents=True, exist_ok=True)
        for st in want:
            (d / name.format(st)).write_bytes(b"x")

    got = m.scan(tmp_path)
    assert set(got) == {"GITT", "step_005C"}, f"소스를 못 찾았다: {sorted(got)}"
    for src in got:
        assert sorted(got[src]) == want, f"[{src}] 상태 이름이 다르다: {sorted(got[src])}"


# ── §1-12 의 숫자는 산출물에서 나와야 한다 (2026-09-11) ────────────────────

def _section(txt: str, head: str) -> str:
    """`head` 로 시작하는 절의 본문만. 다음 `##` 제목 전까지."""
    i = txt.index(head)
    rest = txt[i + len(head):]
    for mark in ("\n## ", "\n### "):
        j = rest.find(mark)
        if j != -1:
            rest = rest[:j]
    return rest


def _table_rows(sec: str, states, header_has: str = "") -> dict:
    """`| 100 | 0.29 | **0.49** | ... |` 형태의 행을 {상태: [칸,...]} 로.

    ⚠ 한 절에 같은 첫 칸을 쓰는 표가 **여럿** 있을 수 있다 (§1-12 는 상태
    이름으로 시작하는 표가 둘이다). 그래서 `header_has` 로 표를 특정한다 —
    안 하면 나중 표가 앞 표를 덮어쓰고 엉뚱한 칸을 읽는다 (2026-09-11 실측).
    """
    rows, in_table = {}, not header_has
    for ln in sec.splitlines():
        t = ln.strip()
        if not t.startswith("|"):
            in_table = not header_has          # 표 밖 — 다음 헤더를 기다린다
            continue
        cells = [c.strip().replace("**", "").replace("+", "")
                 for c in t.strip("|").split("|")]
        if header_has and header_has in t:
            in_table = True
            continue
        if in_table and cells and cells[0] in states:
            rows[cells[0]] = cells[1:]
    return rows


DEG_ROOTS = {"pouch": "out", "fixedhc": "out/cells_pouch_fixedhc",
             "c168": "out/cells_c168", "c171": "out/cells_c171"}
MODES = ("LAM_PE", "LAM_NE", "LLI")


def _bands(sub: str):
    """{상태: {양: (최적, 반폭, 최소, 최대)}}.

    ⚠ 판 선택은 **`compare_states.load_degeneracy` 를 재사용**한다. 직접
    글롭하면 `degeneracy_300_0009_Li_v2.json` 을 건너뛰고 **옛 판**을 읽는다
    — 이 저장소가 2026-09-10 에 세 번 당한 실패이고, 이 테스트 첫 판도
    똑같이 당했다 (2026-09-11).
    """
    deg = _load_script("compare_states").load_degeneracy(ROOT / sub)
    return {st: {k: (e["j"]["best_modes_percent"][k],
                     e["j"][f"{k}_percent"]["span"] / 2,
                     e["j"][f"{k}_percent"]["min"],
                     e["j"][f"{k}_percent"]["max"]) for k in MODES}
            for st, e in deg.items()}


def test_section_1_12_pouch_pe_fixing_did_not_reproduce_the_wide_lli_band():
    """§1-12 (R2 정정판): 파우치의 PE 고정은 원통형 크기의 LLI 띠를 만들지 않았다 —
    **그리고 LAM_PE 에서는 원통형 패턴을 재현했다.** 두 방향을 같이 고정한다 (L5-F1).
    초판 이름 `..._control_rules_out_...` 은 철회된 주장("대체는 원인이 아니다")이었다.
    """
    have = {k: (ROOT / v).is_dir() for k, v in DEG_ROOTS.items()}
    if not all(have.values()):
        pytest.skip(f"산출이 없다: {[k for k, v in have.items() if not v]}")

    B = {k: _bands(v) for k, v in DEG_ROOTS.items()}
    txt = (ROOT / "FINDINGS.md").read_text(encoding="utf-8")

    for st in ("100", "200", "300_0009"):
        p = B["pouch"][st]["LLI"][1]
        f = B["fixedhc"][st]["LLI"][1]
        moved = f - p
        assert 0 <= moved <= 0.25, (
            f"{st}: 반쪽전지 고정이 LLI 반폭을 {moved:+.2f} %p 움직였다. "
            f"§1-12 는 0.03~0.20 이라고 적었다")
        for cell in ("c168", "c171"):
            gap = B[cell][st]["LLI"][1] - p
            assert gap > 2.0, f"{st} {cell}: 격차가 {gap:.2f} %p 뿐이다"
            share = 100 * moved / gap
            assert share < 10, (
                f"{st} {cell}: LLI 이동이 격차의 {share:.1f} % — §1-12 의 '두 수의 비' 범위 밖")
        # 반대 부호 — LAM_PE 에서는 같은 개입이 원통형 패턴을 재현한다 (100·200 에서 몫 > 50 %)
        if st in ("100", "200"):
            p_pe = B["pouch"][st]["LAM_PE"][1]; f_pe = B["fixedhc"][st]["LAM_PE"][1]
            for cell in ("c168", "c171"):
                gap_pe = B[cell][st]["LAM_PE"][1] - p_pe
                assert gap_pe > 0 and 100 * (f_pe - p_pe) / gap_pe > 50, (
                    f"{st} {cell}: LAM_PE 대체 몫이 50 % 아래 — §1-12 의 'LAM_PE 는 반대다' 가 무너진다")
    # 문서의 표를 **칸별로** 대조한다.
    # ⚠ `f"{v:.2f}" in txt` 로 하면 안 된다 — 그 숫자가 문서 어딘가에만 있으면
    #   통과해서, 표를 틀리게 고쳐도 안 잡힌다 (2026-09-11 변이 시험에서 실측).
    sec = _section(txt, "### 1-12")
    tbl = _table_rows(sec, ("100", "200", "300_0009"), header_has="fixedhc")
    assert len(tbl) == 3, f"§1-12 의 대조 표를 못 찾았다: {sorted(tbl)}"
    for st, cells in tbl.items():
        want = [B["pouch"][st]["LLI"][1], B["fixedhc"][st]["LLI"][1],
                B["fixedhc"][st]["LLI"][1] - B["pouch"][st]["LLI"][1],
                B["c168"][st]["LLI"][1], B["c171"][st]["LLI"][1]]
        got = [float(c) for c in cells[:5]]
        for i, (g, w) in enumerate(zip(got, want)):
            assert abs(g - w) < 0.005, (
                f"§1-12 표 {st} 행 {i+1}번째 칸: 문서 {g} vs 산출 {w:.2f}")


def test_section_1_12_ranking_and_overlap_come_from_artifacts():
    """§1-12 의 두 불변식과 '겹침/분리' 표가 산출물에서 그대로 나오는가."""
    if not all((ROOT / v).is_dir() for v in DEG_ROOTS.values()):
        pytest.skip("산출이 없다")
    B = {k: _bands(v) for k, v in DEG_ROOTS.items()}

    rows = [(lab, st, r) for lab, R in B.items() for st, r in R.items()]
    assert len(rows) == 13, f"13 행이어야 한다: {len(rows)}"

    narrowest = [min(MODES, key=lambda k: r[k][1]) for _, _, r in rows]
    widest = [max(MODES, key=lambda k: r[k][1]) for _, _, r in rows]
    assert "LAM_NE" not in narrowest, "LAM_NE 가 최협인 행이 생겼다 — §1-12 의 0/13"
    assert "LAM_PE" not in widest, "LAM_PE 가 최광인 행이 생겼다 — §1-12 의 0/13"

    # 겹침/분리가 셀 종류에 따라 **반대**인가
    def overlaps(r1, r2, k):
        return min(r1[k][3], r2[k][3]) - max(r1[k][2], r2[k][2]) > 0

    # 배율 표 — §1-12 의 헤드라인이다 ("LLI 만 한 자릿수로 무너진다")
    sec = _section((ROOT / "FINDINGS.md").read_text(encoding="utf-8"), "### 1-12")
    rng = _table_rows(sec, MODES, header_has="반폭 범위")   # 정규화 표와 행 키가 같다
    assert len(rng) == 3, f"§1-12 의 배율 표를 못 찾았다: {sorted(rng)}"
    pouch_rows = [r for lab, _, r in rows if lab in ("pouch", "fixedhc")]
    cyl_rows = [r for lab, _, r in rows if lab in ("c168", "c171")]
    for k, cells in rng.items():
        for i, group in enumerate((pouch_rows, cyl_rows)):
            v = sorted(r[k][1] for r in group)
            lo, hi = (float(x) for x in cells[i].split("~"))
            assert abs(v[0] - lo) < 0.005 and abs(v[-1] - hi) < 0.005, (
                f"§1-12 배율 표 {k} {'파우치' if i == 0 else '원통형'}: "
                f"문서 {lo}~{hi} vs 산출 {v[0]:.2f}~{v[-1]:.2f}")
        mult = max(r[k][1] for r in cyl_rows) / max(r[k][1] for r in pouch_rows)
        assert abs(float(cells[2].rstrip("x")) - mult) < 0.05, (
            f"§1-12 배율 표 {k} 배율: 문서 {cells[2]} vs 산출 {mult:.1f}x")

    for lab in DEG_ROOTS:
        R = B[lab]
        pouch_like = lab in ("pouch", "fixedhc")
        for a, b in (("100", "200"), ("200", "300_0009")):
            if a not in R or b not in R:
                continue
            lli = overlaps(R[a], R[b], "LLI")
            pe = overlaps(R[a], R[b], "LAM_PE")
            if pouch_like:
                assert not lli, f"{lab} {a}→{b}: LLI 가 겹친다 — 파우치는 갈랐었다"
            else:
                assert lli, f"{lab} {a}→{b}: LLI 가 갈렸다 — 원통형은 겹쳤었다"
                assert not pe, f"{lab} {a}→{b}: LAM_PE 가 겹친다 — 원통형은 갈랐었다"


def test_fixed_hc_check_catches_a_partially_fixed_root(tmp_path, capsys):
    """소스 하나만 고정된 루트를 `check` 가 잡아야 한다.

    2026-09-11 에 실제로 났다 — `pouch_fixedhc` 는 GITT 만 눌리고
    `step_005C` 는 원본 그대로였다. A축은 GITT 로 돌아 유효했지만 B축
    (`matrix`)은 두 소스를 다 쓰므로 대조가 아니었다. 로그는 소스 *종류*만
    찍으므로 이걸 못 알려준다.
    """
    m = _fixed_hc()
    base = tmp_path / "partial"
    g = base / "data" / "half_cell" / "GITT"
    s = base / "data" / "half_cell" / "step_005C"
    g.mkdir(parents=True); s.mkdir(parents=True)
    for i, st in enumerate(("pristine", "100", "200")):
        (g / f"{st}.xlsx").write_bytes(b"pinned")          # 전부 같은 파일
        (s / f"{st}_005C.xlsx").write_bytes(b"x" + bytes([i]))  # 상태마다 다름

    assert m.cmd_check(SimpleNamespace(root=str(base), expect="fixed")) == 2, \
        "GITT 만 고정된 루트를 '전부 고정' 으로 통과시켰다"
    out = capsys.readouterr().out + capsys.readouterr().err
    assert "step_005C" in out, "어느 소스가 안 눌렸는지 안 알려준다"


# ── ne_shape 가 산출물을 남긴다 (2026-09-11) ───────────────────────────────

def test_ne_shape_writes_an_artifact_carrying_the_capacity_caveat(tmp_path):
    """`ne_shape` 의 수치를 원장에 적으려면 **재계산 가능한 산출물**이 있어야 한다.

    이 스크립트는 오래 출력만 했다. 그러면 FINDINGS 에 적힌 mV 값이 사본이
    되고, 그 사본이 상하는 것을 아무도 못 잡는다 — 이 저장소가 반복해서 당한
    구조다.

    그리고 `measured_shape_mV` 는 **정규화 뒤** 값이라 용량이 크게 변한
    상태에서는 순수한 OCP 모양 변화가 아니다. CSV 가 `cap_delta_pct` 를
    같이 들고 있어야 그 한정어가 숫자에서 안 떨어진다.
    """
    m = _load_script("ne_shape")
    rows = [("100", 23.94, 0.64, 0.027, 136.0, 24.1, 0.2935, 0.2953),
            ("300_0009", 119.34, 18.17, 0.152, 70.5, 21.7, 0.2397, 0.2953)]
    cap = {"pristine": 1.0, "100": 0.9247, "300_0009": 0.7271}
    a = SimpleNamespace(source="GITT", si_source="Li", out_dir="out")
    art = m._write_csv(tmp_path, a, rows, cap, cap["pristine"],
                       {"100": ("100", 0.020, 4.0), "300_0009": ("300_0009", 0.063, 4.2)})

    got = list(csv.DictReader(art.open(encoding="utf-8")))
    assert [r["state"] for r in got] == ["100", "300_0009"]
    assert "cap_delta_pct" in got[0], "용량 변화 칸이 없다 — 한정어가 떨어진다"
    assert abs(float(got[1]["cap_delta_pct"]) - (-27.29)) < 0.01
    assert abs(float(got[1]["measured_shape_mV"]) - 119.34) < 0.01
    assert abs(float(got[0]["gamma_target"]) - 0.2935) < 1e-6, \
        "γ 칸이 비어 있다 — rows 에서 안 넘어온다"
    assert abs(float(got[0]["max_at_x"]) - 0.020) < 1e-6

    meta = json.loads((art.parent / (art.name + ".meta.json")).read_text(encoding="utf-8"))
    assert meta["half_cell_source"] == "GITT" and meta["si_source"] == "Li"
    assert "정규화" in meta["note"], "meta 에 정규화 한정어가 없다"


# ── provenance: git_dirty 는 추적 파일의 수정만 봐야 한다 (2026-09-11) ─────

def test_git_state_ignores_untracked_artifacts(tmp_path):
    """산출물이 untracked 라는 이유로 `git_dirty` 가 켜지면 안 된다.

    2026-09-11 확인: 이 저장소의 meta 는 전부 `git_dirty: true` 였다 —
    산출물 자신이 untracked 여서. 플래그에 정보가 없었고, 그 위에 §1-12
    조건 6 이 "커밋 안 된 변경이 있는 트리" 라고 적었다.
    """
    import subprocess
    m = _load_script("provenance")
    def git(*a):
        return subprocess.run(["git", *a], cwd=tmp_path, check=True,
                              capture_output=True, text=True)
    git("init", "-q"); git("config", "user.email", "t@t"); git("config", "user.name", "t")
    (tmp_path / "code.py").write_text("x = 1\n"); git("add", "code.py"); git("commit", "-qm", "c0")
    sha0 = git("rev-parse", "HEAD").stdout.strip()

    (tmp_path / "artifact.csv").write_text("a,b\n")            # 방금 쓴 산출물 (untracked)
    sha, dirty = m.git_state(cwd=str(tmp_path))
    assert sha == sha0 and dirty is False, \
        f"untracked 산출물만 있는데 dirty={dirty} — 플래그에 정보가 없다"

    (tmp_path / "code.py").write_text("x = 2\n")                # 추적 코드를 고침
    assert m.git_state(cwd=str(tmp_path))[1] is True, "추적 파일 수정을 못 봤다"


def test_ne_shape_artifact_uses_lf_and_provenance_helper(tmp_path):
    m = _load_script("ne_shape")
    rows = [("100", 1.0, 0.5, 0.5, 10.0, 2.0, 0.3, 0.29)]
    a = SimpleNamespace(source="GITT", si_source="Li", out_dir="out")
    art = m._write_csv(tmp_path, a, rows, {"pristine": 1.0, "100": 0.9}, 1.0, {})
    assert b"\r" not in art.read_bytes(), "CSV 가 CRLF 다 — 저장소 산출은 LF"


# ── §1-12 · §5-2 의 ne_shape 표는 CSV 와 칸별로 같아야 한다 (2026-09-11) ──

def _ne_shape_csv():
    f = ROOT / "out" / "ne_shape_GITT_Li.csv"
    if not f.is_file():
        pytest.skip("out/ne_shape_GITT_Li.csv 가 없다")
    return {r["state"]: {k: float(v) for k, v in r.items() if k != "state"}
            for r in csv.DictReader(f.open(encoding="utf-8"))}


def _num(cell: str) -> float:
    return float(cell.replace("−", "-").replace(" mV", "").replace("%", "").strip())


def test_section_1_12_and_5_2_ne_shape_tables_match_the_csv():
    R = _ne_shape_csv()
    txt = (ROOT / "FINDINGS.md").read_text(encoding="utf-8")
    states = ("100", "200", "300_0009")

    # §1-12: | 상태 | 용량 Δ% | 측정된 음극 모양 변화 (max) |
    t = _table_rows(_section(txt, "### 1-12"), states, header_has="측정된 음극 모양 변화")
    assert len(t) == 3, f"§1-12 의 모양 변화 표를 못 찾았다: {sorted(t)}"
    for st, c in t.items():
        assert abs(_num(c[0]) - R[st]["cap_delta_pct"]) < 0.005, (st, "용량 Δ%", c[0])
        assert abs(_num(c[1]) - R[st]["measured_shape_mV"]) < 0.005, (st, "모양 변화", c[1])

    # §5-2: | 상태 | 용량 Δ% | γ | (a) | (b) | (b)/(a) |
    sec = _section(txt, "### 5-2")
    t = _table_rows(sec, states, header_has="γ 가 만든 변화")
    assert len(t) == 3, f"§5-2 의 표를 못 찾았다: {sorted(t)}"
    for st, c in t.items():
        want = [R[st]["cap_delta_pct"], R[st].get("gamma_target", R[st]["gamma_ref"]),
                R[st]["measured_shape_mV"],
                R[st]["gamma_shape_mV"], R[st]["ratio_b_over_a"]]
        tol = [0.005, 0.00005, 0.005, 0.005, 0.005]
        for i, (cell, w, e) in enumerate(zip(c, want, tol)):
            assert abs(_num(cell) - w) < e, f"§5-2 표 {st} 행 {i+1}번째 칸: 문서 {cell} vs CSV {w}"

    # §5-2 (c) — 범위 문자열. 도구가 찍는 서식 그대로 만들어 절 안에서 찾는다.
    mx = [R[s]["blend_vs_meas_max_mV"] for s in states]
    rm = [R[s]["blend_vs_meas_rms_mV"] for s in states]
    fr = [R[s]["frac_over_50mV"] for s in states]
    xs = [R[s]["max_at_x"] for s in states]
    spread = max(mx) / max(rm)                      # ne_shape.py 의 정의 그대로
    for want in (f"{min(mx):.1f} ~ {max(mx):.1f} mV", f"{min(rm):.1f} ~ {max(rm):.1f} mV",
                 f"{min(fr):.1f} ~ {max(fr):.1f} %", " · ".join(f"{x:.3f}" for x in xs),
                 f"**{spread:.1f}**"):
        assert want in sec, f"§5-2 (c) 에 '{want}' 가 없다 — CSV 와 다르다"


def test_section_1_12_obj_normalized_table_comes_from_artifacts():
    """자체 리뷰(2026-09-11) 발견 ①: 1 % 띠는 best_obj 에 비례한다.

    원통형의 best_obj 가 파우치의 ~1.5 배라 "10.5 배" 헤드라인은 그 교란을
    안은 값이다. §1-12 가 반폭/best_obj 표를 같이 들고 있어야 하고, 그 표가
    산출물에서 그대로 나와야 한다.
    """
    if not all((ROOT / v).is_dir() for v in DEG_ROOTS.values()):
        pytest.skip("산출이 없다")
    import json
    cs = _load_script("compare_states")
    def rows(sub):
        return [(e["j"]["best_obj"], {k: e["j"][f"{k}_percent"]["span"] / 2 for k in MODES})
                for e in cs.load_degeneracy(ROOT / sub).values()]
    P = rows("out") + rows("out/cells_pouch_fixedhc")
    C = rows("out/cells_c168") + rows("out/cells_c171")
    assert len(P) == 7 and len(C) == 6

    sec = _section((ROOT / "FINDINGS.md").read_text(encoding="utf-8"), "### 1-12")
    t = _table_rows(sec, MODES, header_has="반폭 / best_obj")
    assert len(t) == 3, f"§1-12 의 정규화 표를 못 찾았다: {sorted(t)}"
    for k, cells in t.items():
        pn = sorted(hw[k] / b for b, hw in P); cn = sorted(hw[k] / b for b, hw in C)
        for i, v in enumerate((pn, cn)):
            lo, hi = (float(x) for x in cells[i].split("~"))
            assert abs(lo - v[0]) < 0.005 and abs(hi - v[-1]) < 0.005, \
                f"정규화 표 {k} {'파우치' if i == 0 else '원통형'}: 문서 {lo}~{hi} vs 산출 {v[0]:.2f}~{v[-1]:.2f}"
        assert abs(float(cells[2].rstrip("x")) - cn[-1] / pn[-1]) < 0.05, \
            f"정규화 표 {k} 배율: 문서 {cells[2]} vs 산출 {cn[-1]/pn[-1]:.1f}x"
    # 교란이 "격차의 일부만" 설명한다는 문장의 근거 — 정규화해도 LLI 는 3 배 이상
    pn = sorted(hw["LLI"] / b for b, hw in P); cn = sorted(hw["LLI"] / b for b, hw in C)
    assert cn[-1] / pn[-1] > 3, "정규화하면 LLI 격차가 사라진다 — §1-12 의 결론이 뒤집힌다"


def test_degeneracy_json_records_its_settings():
    """자체 리뷰 발견 ②의 재발 방지: 새 산출은 starts·seed 를 JSON 안에 들고 있어야."""
    import inspect
    src = inspect.getsource(verify.cmd_degeneracy)
    assert '"n_starts": args.starts' in src and '"seed": args.seed' in src, \
        "cmd_degeneracy 가 starts/seed 를 산출에 안 남긴다"


# ═══ R2 (Codex 2차, NO-GO) 반례 — reviews/R2_LEDGER.md 의 C3·C4·C5·C10·C12·C18 ═══

def _r2_csv(tmp, anchors, cols, rows, fmt=".17g"):
    lines = [f"# {k},{v:.17g}" for k, v in anchors.items()]
    lines.append("a_PE,b_PE,a_NE,b_NE,gamma_Si," + ",".join(cols))
    lines.extend(",".join(format(x, fmt) for x in r) for r in rows)
    p = pathlib.Path(tmp) / "r2.csv"; p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def _r2_base():
    from bms_balancing.verify import ANCHOR_STAGE, DD_EVAL_P
    anchors = {k: 1.0 for k, _ in ANCHOR_STAGE}; anchors["dv_n"] = 350.0
    cols = ["rmse_pocv", "rmse_dvdq", "rmse_dqdv", "rmse_dqdv_w"]
    P = [list(p) for p in DD_EVAL_P]
    py = {c: [0.0123456789012345 * (j + 1) + 0.001 * i for i in range(len(P))]
          for j, c in enumerate(cols)}
    rows = [p + [py[c][i] for c in cols] for i, p in enumerate(P)]
    return anchors, cols, P, py, rows


def _r2_run(anchors, P, py, path):
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        res = verify._compare_dd_eval(anchors, P, py, path)
    return res, buf.getvalue()


def test_r2_01_comparator_does_not_certify_uncompared_cells(tmp_path):
    """[Codex R2-01] 행 누락·격자 불일치·NaN 을 "전부 일치" 로 인증하면 안 된다.

    재현 원본: reviews/r2_repros/harness_r2_port_repros.py::comparator_probes.
    abfed8b 에서 세 경우 모두 "… 전부 일치" 가 찍혔다 (rmse 28개 / 32개 / 32개).
    """
    anchors, cols, P, py, rows = _r2_base()
    ok_res, ok_txt = _r2_run(anchors, P, py, _r2_csv(tmp_path, anchors, cols, rows))
    assert "전부 일치" in ok_txt and ok_res["status"] == "complete", ok_txt

    cases = {}
    r = [x.copy() for x in rows]; r.pop(); cases["missing_last_row"] = r
    r = [x.copy() for x in rows]; r[3][0] += 0.05; r[3][5:] = [9.0] * 4; cases["wrong_parameter_row"] = r
    r = [x.copy() for x in rows]; r[3][5:] = [float("nan")] * 4; cases["nan_rmse_row"] = r
    for name, r in cases.items():
        res, txt = _r2_run(anchors, P, py, _r2_csv(tmp_path, anchors, cols, r))
        assert "전부 일치" not in txt, f"{name}: 비교 안 한 값을 일치로 인증했다\n{txt}"
        assert res["status"] != "complete" and res["compared"] < res["expected"], (name, res)
        assert "성공 아님" in txt or "미완" in txt, (name, txt)


def test_r2_02_short_exact_token_does_not_relax_file_tolerance(tmp_path):
    """[Codex R2-02] `%.17g` 파일의 정확한 `1.5` 하나가 파일 전체 atol 을 0.1 로 만들면 안 된다.

    abfed8b: printed_abs_tol → 0.1, 다른 행 pOCV 163 % 차이가 "전부 일치".
    """
    anchors, cols, P, py, rows = _r2_base()
    rows[0][7] = 1.5; py["rmse_dqdv"][0] = 1.5           # 정확한 짧은 토큰
    rows[3][5] += 0.025                                    # 다른 행, 상대 163 %
    path = _r2_csv(tmp_path, anchors, cols, rows)
    tol = verify.printed_abs_tol(path)
    assert tol < 1e-14, f"짧은 토큰이 파일 한계를 {tol:.0e} 로 끌어올렸다"
    res, txt = _r2_run(anchors, P, py, path)
    assert "전부 일치" not in txt, "163 % 차이를 자리수 안이라고 덮었다\n" + txt
    assert "모델 차이" in txt or "목적함수 산술" in txt, txt


def test_r2_03_profile_does_not_store_failed_optimizer_rows(tmp_path, monkeypatch):
    """[Codex R2-03] `cmd_profile` 은 multistart 와 달리 success 를 안 봤다 — A3 미종결 경로.

    abfed8b: 4 회 전부 실패한 γ 두 점이 완료 적합처럼 저장됐다 (LAM_NE −16.67 %).
    """
    import csv as _csv
    center = np.array([1.2, -0.25, 1.2, -0.15, 0.25])

    class Obj:
        c_cell = 1.0; scales = {"pocv": 1.0, "dvdq": 1.0, "dqdv": 1.0}; n_scale_samples = 1
        def __call__(self, p): return float(1.0 + 1e-4 * np.square(np.asarray(p) - center).sum())
        def rmse_pocv(self, p): return float(self(p))
        def _auto_scales(self, *a, **k): return dict(self.scales)
    failed = []
    def nonconverged(fun, start, **kw):
        x = np.array([1.2, -0.25, 1.4, -0.15]); v = float(fun(x)); failed.append(v)
        return SimpleNamespace(x=x, fun=v, success=False, status=1, message="ITERATIONS LIMIT")
    monkeypatch.setattr(verify.D, "data_root", lambda *a, **k: tmp_path)
    monkeypatch.setattr(verify, "build", lambda *a, **k: Obj())
    monkeypatch.setattr(verify, "multistart", lambda *a, **k: (center.copy(), 1.0, []))
    monkeypatch.setattr(verify, "minimize", nonconverged)
    out = tmp_path / "p.csv"
    args = SimpleNamespace(data_root=str(tmp_path), source="GITT", state="200", si_source="Li",
                           w_dqdv=0.0, seed=0, starts=1, grid=2, tol=0.01,
                           profile_scale="global", out=str(out))
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        verify.cmd_profile(args)
    assert len(failed) == 4
    rows = list(_csv.DictReader(out.open(encoding="utf-8"))) if out.is_file() else []
    assert not rows, f"전부 실패한 γ 가 완료 적합처럼 저장됐다: {rows}"
    assert "실패" in buf.getvalue() or "not_success" in buf.getvalue() or "skipped" in buf.getvalue()


def test_r2_04_compare_states_prints_min_max_not_plus_minus():
    """[Codex R2-04] `best ± span/2` 는 best 를 중점처럼 보이게 한다 — best 는 경계해에서 끝점이다.

    c168 300_0009 LAM_NE: 산출 [2.30, 11.00], 표시 `2.30±4.35` → 암시 [−2.05, 6.65].
    """
    if not (ROOT / "out" / "cells_c168").is_dir():
        pytest.skip("산출 없음")
    import io, contextlib, subprocess, sys as _s
    r = subprocess.run([_s.executable, str(ROOT / "scripts" / "compare_states.py"),
                        f"c168={ROOT / 'out' / 'cells_c168'}"], capture_output=True, text=True)
    a_axis = r.stdout.split("B. 모델 선택")[0]
    assert "±" not in a_axis, "A축 표가 아직 ± 로 찍힌다"
    assert "2.30 [2.30, 11.00]" in a_axis, a_axis


def test_r2_10_ne_shape_csv_carries_both_gammas(tmp_path):
    """[Codex R2-10] `gamma_ref` 열에 대상 γ 를 썼다. 두 역할을 따로 저장해야 한다."""
    m = _load_script("ne_shape")
    rows = [("100", 23.94, 0.64, 0.027, 136.0, 24.1, 0.2935, 0.2953)]
    a = SimpleNamespace(source="GITT", si_source="Li", out_dir="out")
    art = m._write_csv(tmp_path, a, rows, {"pristine": 1.0, "100": 0.9}, 1.0, {})
    got = next(csv.DictReader(art.open(encoding="utf-8")))
    assert abs(float(got["gamma_target"]) - 0.2935) < 1e-9 and abs(float(got["gamma_ref"]) - 0.2953) < 1e-9
    committed = ROOT / "out" / "ne_shape_GITT_Li.csv"
    if committed.is_file():
        hdr = committed.open(encoding="utf-8").readline()
        assert "gamma_target" in hdr, (
            "커밋된 ne_shape CSV 가 구판 스키마다 (gamma_ref 에 대상 γ) — "
            "사용자 기계에서 `python3 scripts/ne_shape.py` 를 다시 돌려 커밋해야 한다 (C18)")


def test_r2_09_audit97_reports_per_row_thresholds_not_a_single_cutoff():
    """[Codex R2-09] "1.20 아래로 잡았으면 음수 불가" 는 틀렸다 — 행별 임계 1.177~1.196, 고정-기준 조건."""
    if not (ROOT / "out" / "bms97").is_dir():
        pytest.skip("원표 없음")
    import subprocess, sys as _s
    r = subprocess.run([_s.executable, str(ROOT / "scripts" / "audit97.py")],
                       capture_output=True, text=True)
    assert "나올 수 없었다" not in r.stdout, r.stdout[-600:]
    assert "1.177" in r.stdout and "1.196" in r.stdout, r.stdout[-800:]
    assert "기준" in r.stdout and "고정" in r.stdout


# ── §1-8 의 192 값은 이제 저장소 안 산출물 위에 선다 (2026-09-11, C21) ─────

def test_section_1_8_192_values_are_backed_by_committed_recompare_artifacts():
    """R2 재대조에서 §1-8 의 CSV 가 미보존이라는 것이 드러났다 (C21). 툴박스 `dd_eval` 을
    네 조합에 다시 돌려 `out/recompare/` 에 CSV 와 고친 비교기의 판정을 넣었다.
    이 테스트는 그 산출물이 §1-8 의 문장(앵커 16 · rmse 32 · 최대 상대차 4.04e-12,
    "실제 수치 차이" 띠)을 실제로 받치는지 본다. 판정 텍스트에 미완/부분이 있으면 실패.
    """
    import re
    d = ROOT / "out" / "recompare"
    files = sorted(d.glob("dd_eval_*_r2.csv"))
    if not files:
        pytest.skip("out/recompare 없음")
    assert len(files) == 4, [f.name for f in files]
    worst = 0.0
    for f in files:
        anchors, rows, hdr = verify.read_dd_eval_csv(f)
        assert len(anchors) == 16 and len(rows) == 8, (f.name, len(anchors), len(rows))
        assert hdr[5:] == ["rmse_pocv", "rmse_dvdq", "rmse_dqdv", "rmse_dqdv_w"], hdr
        t = f.with_suffix(".txt").read_text(encoding="utf-8")
        assert "앵커 16개가 전부 맞고" in t and "rmse 32개" in t, f.name
        for bad in ("미완", "부분", "처음 갈린다", "목적함수 산술"):
            assert bad not in t, (f.name, bad)
        m = re.search(r"최대 상대차 ([0-9.]+e-[0-9]+)", t); assert m, f.name
        v = float(m.group(1)); assert 0 < v < 1e-9, (f.name, v)
        worst = max(worst, v)
    assert abs(worst - 4.04e-12) < 0.01e-12, f"§1-8 의 최대 4.04e-12 와 다르다: {worst:.2e}"
    txt = (ROOT / "FINDINGS.md").read_text(encoding="utf-8")
    assert "4.04e-12" in _section(txt, "### 1-8"), "§1-8 에 최대 상대차가 없다"


# ── §1-12 R2 정정판의 새 표 네 개 — 산출물에서 칸별로 (2026-09-11) ─────────

def _r2_tables_ctx():
    if not all((ROOT / v).is_dir() for v in DEG_ROOTS.values()):
        pytest.skip("산출이 없다")
    import statistics as S
    B = {k: _bands(v) for k, v in DEG_ROOTS.items()}
    cs = _load_script("compare_states")
    objs = {k: {st: e["j"]["best_obj"] for st, e in cs.load_degeneracy(ROOT / v).items()}
            for k, v in DEG_ROOTS.items()}
    def rmse(lab, st):
        f = sorted((ROOT / DEG_ROOTS[lab]).glob(f"matrix_{st}*.csv"))[-1]
        r = [x for x in csv.DictReader(f.open(encoding="utf-8"))
             if x.get("si") == "Li" and x.get("half_cell", "GITT") == "GITT" and float(x.get("w_dqdv", 0)) == 0][0]
        return float(r["rmse_pocv"]) * 1e3, float(r["ref_rmse_pocv"]) * 1e3
    sec = _section((ROOT / "FINDINGS.md").read_text(encoding="utf-8"), "### 1-12")
    return B, objs, rmse, sec, S


def test_section_1_12_three_mode_share_table_matches_artifacts():
    B, objs, rmse, sec, S = _r2_tables_ctx()
    rows = [ln for ln in sec.splitlines() if ln.startswith("| LAM_") or ln.startswith("| LLI |")]
    got = {}
    for ln in rows:
        c = [x.strip() for x in ln.strip("|").split("|")]
        if len(c) == 7 and c[1] in ("100", "200", "300_0009"):
            got[(c[0], c[1])] = c
    assert len(got) == 9, f"세 mode 몫 표 9 행을 못 찾았다: {len(got)}"
    for (k, st), c in got.items():
        p = B["pouch"][st][k][1]; f = B["fixedhc"][st][k][1]
        assert abs(float(c[2]) - p) < 5e-4 and abs(float(c[3]) - f) < 5e-4, (k, st, c)
        assert abs(float(c[4].replace("+", "")) - (f - p)) < 5e-4, (k, st, c)
        for i, cell in ((5, "c168"), (6, "c171")):
            want = 100 * (f - p) / (B[cell][st][k][1] - p)
            assert abs(float(c[i].rstrip("%").strip()) - want) < 0.06, (k, st, cell, c[i], want)


def test_section_1_12_physical_normalization_and_misfit_tables_match_artifacts():
    B, objs, rmse, sec, S = _r2_tables_ctx()
    P = [("pouch", st) for st in ("100", "200", "300_0009")] + [("fixedhc", st) for st in ("100", "200", "300_0009")]
    C = [(c, st) for c in ("c168", "c171") for st in ("100", "200", "300_0009")]
    R = {x: rmse(*x) for x in P + C}
    fns = {"raw": lambda x: B[x[0]][x[1]]["LLI"][1],
           "/best_obj": lambda x: B[x[0]][x[1]]["LLI"][1] / objs[x[0]][x[1]],
           "/rmse_pocv": lambda x: B[x[0]][x[1]]["LLI"][1] / R[x][0],
           "/√rmse_pocv": lambda x: B[x[0]][x[1]]["LLI"][1] / R[x][0] ** 0.5}
    t = _table_rows(sec, tuple(fns), header_has="LLI 반폭 정규화")
    assert len(t) == 4, sorted(t)
    for name, fn in fns.items():
        pv = sorted(map(fn, P)); cv = sorted(map(fn, C)); c = t[name]
        lo, hi = (float(x) for x in c[0].split("~")); assert abs(lo - pv[0]) < 6e-5 and abs(hi - pv[-1]) < 6e-5, (name, c)
        lo, hi = (float(x) for x in c[1].split("~")); assert abs(lo - cv[0]) < 6e-5 and abs(hi - cv[-1]) < 6e-5, (name, c)
        for i, want in ((2, cv[-1] / pv[-1]), (3, cv[0] / pv[0]), (4, S.median(cv) / S.median(pv))):
            assert abs(float(c[i].rstrip("x")) - want) < 0.006, (name, i, c[i], want)
        assert c[5] == ("예" if cv[0] < pv[-1] else "아니오"), (name, c)
    # /rmse 에서는 겹친다 — §1-12 의 문장
    assert t["/rmse_pocv"][5] == "예"
    m = _table_rows(sec, tuple(DEG_ROOTS), header_has="pristine 기준 적합")
    assert len(m) == 4, sorted(m)
    for lab, c in m.items():
        v = [R[(lab, st)] for st in ("100", "200", "300_0009")]
        assert abs(float(c[0]) - v[0][1]) < 0.006
        for i in range(3):
            assert abs(float(c[1 + i]) - v[i][0]) < 0.006, (lab, i, c)
        assert abs(float(c[4]) - v[2][0] / v[0][0]) < 0.006, (lab, c)
    # 원통형 부적합은 사이클과 함께 커지고 파우치는 줄어든다 — 문장의 근거
    assert float(m["c168"][4]) > 1.4 and float(m["c171"][4]) > 1.4 and float(m["pouch"][4]) < 1.0


def test_section_1_10_table_prints_best_min_max_and_width():
    """[Codex R2-04] §1-10 A축 표를 `best [min, max]` 와 폭(max−min)으로 바꿨다 — 칸별 대조."""
    B, objs, rmse, sec, S = _r2_tables_ctx()
    txt = (ROOT / "FINDINGS.md").read_text(encoding="utf-8")
    t = _table_rows(_section(txt, "### 1-10"), ("100", "200", "300_0009", "300_0147"), header_has="best [min, max]")
    assert len(t) == 4, sorted(t)
    import re as _re
    for st, c in t.items():
        b = B["pouch"][st]
        for i, k in enumerate(MODES):
            m = _re.match(r"([−-]?[0-9.]+) \[([−-]?[0-9.]+), ([−-]?[0-9.]+)\]", c[1 + i].replace("−", "-"))
            assert m, (st, c[1 + i])
            best, lo, hi = (float(x) for x in m.groups())
            assert abs(best - b[k][0]) < 5e-4 and abs(lo - b[k][2]) < 5e-4 and abs(hi - b[k][3]) < 5e-4, (st, k, c[1 + i])
        assert "±" not in "".join(c)


# ═══ R2 후속 — C20 사각지대와 우리가 직접 닫는 실측 셋 (2026-09-11) ═══

def test_interp_refuses_duplicate_or_nonmonotone_x_like_matlab():
    """MATLAB `interp1` 은 x 가 단조가 아니면 에러다. 우리 `_interp_lin_extrap` 은 조용히
    값을 냈다 (L0-7). 원통형 워크북은 우리가 썼으므로 중복 용량점이 들어올 수 있고,
    그러면 조용한 쓰레기가 '넓은 띠' 로 보일 수 있다. 실패로 닫는다 (fail-closed)."""
    from bms_balancing.model import _interp_lin_extrap as f
    for name, xs in (("중복 x", [0, 1, 1, 2]), ("비단조 x", [0, 2, 1, 3])):
        with pytest.raises(ValueError, match="interp1"):
            f(np.array(xs, float), np.array([0, 1, 2, 3], float), np.array([0.5, 1.5]))
    # 단조 증가·감소는 그대로
    assert np.allclose(f(np.array([0, 1, 2.]), np.array([0, 1, 4.]), np.array([-1, 3.])), [-1, 7])
    assert np.allclose(f(np.array([2, 1, 0.]), np.array([4, 1, 0.]), np.array([-1, 3.])), [-1, 7])


def test_fixed_hc_sha_sees_bytes_after_the_first_chunk(tmp_path):
    """L0-4: `sha()` 가 첫 1 MB 청크만 해시해도 기존 테스트는 통과했다 (파일이 작아서)."""
    m = _fixed_hc()
    base = bytes(1_200_000)
    a = tmp_path / "a.bin"; b = tmp_path / "b.bin"
    a.write_bytes(base); b.write_bytes(base[:1_100_000] + b"\x01" + base[1_100_001:])
    assert m.sha(a) != m.sha(b), "1 MB 뒤의 차이를 해시가 못 본다"


def test_mode_profile_keeps_the_attainable_grid_for_connectivity():
    """[Codex R2-05] 외곽 범위 [min,max] 만 저장하면 가능집합이 비연결인지 알 수 없다.
    도달한 격자점 목록을 같이 저장해야 나중에 '공유 가능값' 을 물을 수 있다."""
    from bms_balancing.verify import mode_profile_extrema
    class Quad:
        c_cell = 1.0
        def __call__(self, p):
            p = np.asarray(p, float); return float(1.0 + 4.0 * np.sum((p[:4] - [1.2, -0.25, 1.2, -0.15]) ** 2))
    best = np.array([1.2, -0.25, 1.2, -0.15, 0.25]); ref = best.copy()
    out = mode_profile_extrema(Quad(), ref, 1.0, 1.0, best, Quad()(best), 0.01, n_grid=5, n_starts=1, seed=0)
    for k in ("LAM_PE", "LAM_NE", "LLI"):
        assert "attainable_pct" in out[k] and "grid_pct" in out[k], k
        assert len(out[k]["attainable_pct"]) == out[k]["n_grid_attainable"]
        assert len(out[k]["grid_pct"]) == out[k]["n_grid"]
        assert min(out[k]["attainable_pct"]) == out[k]["min"] and max(out[k]["attainable_pct"]) == out[k]["max"]


def test_ne_shape_measures_the_consumed_pe_axis_too(tmp_path, monkeypatch):
    """[Codex R2-07 · L5-F2] 대조 실험이 실제로 흔든 축은 PE 곡선이다. `ne_shape` 가
    `E_PE(state) − E_PE(pristine)` 를 같이 재고 CSV 에 남겨야 §1-12 조건 7 이 닫힌다."""
    import io, contextlib, csv as _csv, sys as _s
    m = _load_script("ne_shape")
    u = np.linspace(0, 1, 301); arrays = ((1 - u) ** 2, 0.1 + 0.7 * u, 1 - u, 0.1 + 0.7 * u)
    from bms_balancing.model import Blend
    blend = Blend(*arrays, window=11, poly_order=3)
    class P:
        def __init__(self, st): self.state = st
        def is_file(self): return True
    class HC:
        def __init__(self, path, **kw): self.st = path.state
        def E_NE(self, x): return blend.E(x, 0.25)
        def E_PE(self, x): return 3.8 + 0.02 * (self.st != "pristine") + 0.0 * np.asarray(x)
    monkeypatch.setattr(m.D, "STATES", ["pristine", "100"])
    monkeypatch.setattr(m.D, "data_root", lambda *a, **k: tmp_path)
    monkeypatch.setattr(m.D, "half_cell_path", lambda r, s, st: P(st))
    monkeypatch.setattr(m.D, "load_literature", lambda *a, **k: arrays)
    monkeypatch.setattr(m, "HalfCell", HC)
    monkeypatch.setattr(m, "raw_ne_capacity", lambda p: 1.0)
    monkeypatch.setattr(m, "fitted_pair", lambda *a, **k: (0.26, 0.25))
    monkeypatch.setattr(_s, "argv", ["ne_shape.py", "--write", str(tmp_path)])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = m.main()
    assert rc == 0, buf.getvalue()
    row = next(_csv.DictReader((tmp_path / "ne_shape_GITT_Li.csv").open(encoding="utf-8")))
    assert abs(float(row["pe_shape_max_mV"]) - 20.0) < 1e-6 and abs(float(row["pe_shape_rms_mV"]) - 20.0) < 1e-6, row
    assert "PE" in buf.getvalue()


def test_section_1_12_pe_axis_strength_table_matches_the_csv():
    """§1-12 조건 7: 대조 실험이 실제로 흔든 PE 축의 변화량이 CSV 와 칸별로 같아야 한다."""
    R = _ne_shape_csv()
    if "pe_shape_max_mV" not in next(iter(R.values())):
        pytest.skip("구판 CSV — PE 축 없음")
    sec = _section((ROOT / "FINDINGS.md").read_text(encoding="utf-8"), "### 1-12")
    t = _table_rows(sec, ("100", "200", "300_0009"), header_has="E_PE 변화 max")
    assert len(t) == 3, sorted(t)
    for st, c in t.items():
        assert abs(_num(c[0]) - R[st]["pe_shape_max_mV"]) < 0.005, (st, c)
        assert abs(_num(c[1]) - R[st]["pe_shape_rms_mV"]) < 0.005, (st, c)
    # 100 에서만 강한 개입 — 문장의 근거
    assert R["100"]["pe_shape_rms_mV"] > 5 * max(R["200"]["pe_shape_rms_mV"], R["300_0009"]["pe_shape_rms_mV"])
