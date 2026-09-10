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
    """needles 를 전부 포함하면서 철회 표지가 없는 줄 = 그 숫자를 주장하는 줄."""
    out = []
    for ln in text.splitlines():
        if all(n in ln for n in needles) and not any(m in ln for m in _RETRACTION):
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
