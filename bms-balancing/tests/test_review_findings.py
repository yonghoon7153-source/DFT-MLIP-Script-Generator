"""2026-09-10 적대적 리뷰(NO-GO)의 반례를 회귀 테스트로 고정한다.

리뷰어가 준 반례는 그대로 회귀 테스트로 박는다 (CLAUDE.md 작업규율 2).
각 테스트 이름 뒤 [Rn]/[An]/[Bn] 은 리뷰 문서의 항목 번호다.
"""
from __future__ import annotations
import csv, pathlib, sys
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
    for name in ("README.md", "FINDINGS.md", "FOR_BMS_TEAM.md"):
        txt = (ROOT / name).read_text(encoding="utf-8")
        assert stale not in txt, (
            f"{name} 에 v1 의 옛 폭 {stale} %p 가 남아 있다. 정본(v2)은 {want} %p 다 "
            f"— multistart 수정으로 답이 최대 5.857 %p 움직인 뒤의 값이다.")
    # 문서마다 자리수가 다르다 (FINDINGS 는 10.8774, 나머지는 10.88) — 둘 다 허용
    forms = {f"{span['LAM_NE_pct']:.{d}f}" for d in (2, 3, 4)}
    for name in ("README.md", "FINDINGS.md", "FOR_BMS_TEAM.md"):
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
