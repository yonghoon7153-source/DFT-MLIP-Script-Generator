"""R6 내부 자체 리뷰 회귀 테스트 (2026-09-11, 대상 1049894 — Codex 토큰 소진으로 `/self-review` 4 렌즈 + 적대적 검증).

원장: `reviews/R6_LEDGER.md`. 렌즈 보고·재현 스크립트 사본: `reviews/r6_repros/`.
ID 규약 — V: validator 우회 · T: 순서/TOCTOU · D: 파생 보고서·공정성 · P: sig 완전성·이식성.

공통 반례(validator 렌즈): MATLAB rmse 가 Python 과 상대차 1e-3 ~ 1e-2 (`MODEL_REL` 의 10⁶ 배 이상) 인데
`%.2g` 로 찍으면 두 값이 같은 문자열 — 형식이 실제보다 거칠다고 **주장**하기만 하면 차이가 사라진다.
"""
from __future__ import annotations
import json, pathlib, shutil, sys
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bms_balancing import verify                                      # noqa: E402
from test_review_findings import _r2_base, _r2_csv, _r2_run          # noqa: E402


def _prov():
    import importlib.util
    spec = importlib.util.spec_from_file_location("provenance", ROOT / "scripts" / "provenance.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _same_cell_but_different(pv, fmt=".2g"):
    """`fmt` 로 찍으면 pv 와 **같은 문자열**이지만 값은 상대차 ≥ 1e-6 (MODEL_REL 의 1000 배 이상) 만큼 다른 값.
    2 유효자리 칸의 마지막 자리 0.45 배만큼 위로 — 칸 안이라 거친 형식 아래서는 차이가 보이지 않는다."""
    import math
    t = format(pv, fmt); base = float(t)
    unit = 10 ** (math.floor(math.log10(abs(base))) - 1)
    mv = base + 0.45 * unit
    assert format(mv, fmt) == t and abs(mv - pv) / abs(pv) > 1e-6, (pv, mv, t)
    return mv


def _mat_rows(rows, fmt=".2g"):
    """파라미터 다섯은 그대로, rmse 값은 `%.2g` 칸 안에서 다른 값 — 'MATLAB 쪽이 다른 모델' 을 흉내낸다."""
    return [r[:5] + [_same_cell_but_different(x, fmt) for x in r[5:]] for r in rows]


def _rewrite(p, lines):
    p.write_text("\n".join(lines) + "\n", encoding="utf-8"); return p


# ── V6-01 · 헤더가 데이터 행 뒤에 오면 행별 검사(R4-04 열 수 · R5-01 재출력)가 한 번도 돌지 않는다 ──────────
def test_i6v_01_header_after_data_rows_is_malformed(tmp_path):
    """[R6 내부 V6-01] audit 의 행별 검사는 `header is not None` 뒤에만 돌고, header 는 스캔 순서로 정해진다.
    헤더가 위면 `%.2g` 선언 + 17 자리 토큰 → invalid 인데, 같은 파일의 헤더를 맨 아래로 옮기면 complete 였다
    (1.5 % 차이가 "적힌 자리수 안"). 어떤 writer 도 그 순서로 안 쓴다 — 그래서 옛 스키마가 아니라 malformed 다."""
    anchors, cols, P, py, rows = _r2_base()
    top = _r2_csv(tmp_path, anchors, cols, _mat_rows(rows), head=("# printed_format,%.2g",), name="top.csv")
    res_top, _ = _r2_run(anchors, P, py, top)
    assert res_top["status"] == "invalid"                                   # 대조군: 헤더 위 → 이미 invalid
    lines = top.read_text(encoding="utf-8").splitlines()
    hdr = next(l for l in lines if l.startswith("a_PE")); lines.remove(hdr); lines.append(hdr)
    bottom = _rewrite(tmp_path / "bottom.csv", lines)
    probs = verify.dd_eval_csv_audit(bottom, spec=verify.parse_precision_spec("%.2g"))
    assert probs and any("헤더" in m for m in probs), probs
    res, txt = _r2_run(anchors, P, py, bottom)
    assert res["status"] == "invalid", (res["status"], txt[-400:])


# ── V6-02 · `--precision` 옵션은 파일의 토큰과 대조되지 않았다 ────────────────────────────────────────
@pytest.mark.parametrize("head", [(), ("# printed_format,%.17e",), ("# printed_format,17",)],
                         ids=["no-declaration", "unparseable-declaration", "numeric-declaration"])
def test_i6v_02_precision_option_must_reproduce_the_tokens(tmp_path, head):
    """[R6 내부 V6-02] 선언이 없거나 해석 불가인 파일의 17 자리 토큰에 `--precision sig:2` 를 주면 complete 였다
    (audit 은 `declared_spec` 만 받고, '옵션이 느슨' 판정은 해석 가능한 선언이 있을 때만). 옵션은 "이 파일은 이
    형식으로 찍혔다" 는 주장이므로 토큰이 그 형식으로 재출력되지 않으면 그 주장이 틀린 것 → invalid."""
    anchors, cols, P, py, rows = _r2_base()
    p = _r2_csv(tmp_path, anchors, cols, _mat_rows(rows), head=head)
    res, txt = _r2_run(anchors, P, py, p, precision="sig:2")
    assert res["status"] == "invalid", (head, res["status"], txt[-400:])
    assert any("sig:2" in m or ".2g" in m for m in res["problems"]), res["problems"]
    # 대조군 (R4-02 Q3 그대로): 선언 `%.17g` 이 있으면 느슨한 옵션은 partial 이고 선언과의 충돌이 기록된다
    ctl = _r2_csv(tmp_path, anchors, cols, _mat_rows(rows), name="ctl.csv")
    res_c, _ = _r2_run(anchors, P, py, ctl, precision="sig:2")
    assert res_c["status"] == "partial" and res_c["precision_override_looser"], res_c["status"]


# ── V6-03 · 헤더 없는 파일: audit 전무 + 앞 두 열을 위치로 rmse 로 본다 — 존재한 적 없는 스키마 ────────────
def test_i6v_03_missing_header_is_malformed_not_old_schema(tmp_path):
    """[R6 내부 V6-03] `dd_eval.m` 은 첫 판(56a35a8:118)부터 헤더를 썼다. 헤더 없는 파일은 옛 산출이 아니라
    malformed 인데, 비교기는 앞 두 열을 rmse 로 보고 partial 을 주었고 `--allow-partial` 이면 0 이었다."""
    anchors, cols, P, py, rows = _r2_base()
    p = _r2_csv(tmp_path, anchors, cols, _mat_rows(rows), head=("# printed_format,%.2g",))
    _rewrite(p, [l for l in p.read_text(encoding="utf-8").splitlines() if not l.startswith("a_PE")])
    res, txt = _r2_run(anchors, P, py, p)
    assert res["status"] == "invalid", (res["status"], txt[-400:])
    assert any("헤더" in m for m in res["problems"]), res["problems"]


# ── V6-04 · `--allow-partial` 의 "스키마 누락" 에 하한이 없었다 ───────────────────────────────────────
def test_i6v_04_partial_needs_the_first_schema_columns(tmp_path):
    """[R6 내부 V6-04] rmse 열이 0 개(헤더 = 파라미터 다섯뿐)여도, 앵커까지 없어도 partial → `--allow-partial` 로 0
    ("앵커 0개와 rmse 0개가 전부 일치", compared=0/0). 첫 판(56a35a8) 도 `rmse_pocv,rmse_dvdq` 두 열은 썼다 —
    그 둘이 없으면 옛 스키마가 아니라 비교할 것이 없는 파일이다."""
    anchors, cols, P, py, rows = _r2_base()
    par = ["a_PE,b_PE,a_NE,b_NE,gamma_Si"] + [",".join(format(x, ".6f") for x in r[:5]) for r in rows]
    anc = ["# printed_format,%.17g"] + [f"# {k},{v:.17g}" for k, v in anchors.items()]
    res0, txt0 = _r2_run(anchors, P, py, _rewrite(tmp_path / "p0.csv", anc + par))       # rmse 열 0
    assert res0["status"] == "invalid", (res0["status"], txt0[-400:])
    res1, txt1 = _r2_run(anchors, P, py, _rewrite(tmp_path / "p1.csv", anc[:1] + par))   # 앵커도 0
    assert res1["status"] == "invalid", (res1["status"], txt1[-400:])
    p2 = _r2_csv(tmp_path, anchors, ["rmse_pocv"], [r[:6] for r in rows], name="p2.csv")  # dvdq 열 없음
    res2, txt2 = _r2_run(anchors, P, py, p2)
    assert res2["status"] == "invalid", (res2["status"], txt2[-400:])
    # 대조군: 진짜 옛 스키마 (rmse 2 열) 는 그대로 partial 이고 그 두 열은 비교된다
    p3 = _r2_csv(tmp_path, anchors, ["rmse_pocv", "rmse_dvdq"], [r[:7] for r in rows], name="p3.csv")
    res3, _ = _r2_run(anchors, P, py, p3)
    assert res3["status"] == "partial" and res3["compared"] == 2 * len(P), res3["status"]


# ── V6-05 · `verify_unit` 은 meta 의 run_id·sha256 만 보고 `artifact` 이름은 안 본다 ─────────────────────
def test_i6v_05_verify_unit_binds_the_meta_to_the_artifact_name(tmp_path):
    """[R6 내부 V6-05] `matrix_100.csv` + meta(`artifact=matrix_100.csv, state=100`) 를 `matrix_200.csv` 이름으로
    복사하면 `--verify-unit matrix_200.csv` 가 0 '일치' 였다. matrix 행에는 state 열이 없어 이름·meta 가
    상태 identity 의 전부다 — meta 의 `artifact` 가 파일 이름과 같아야 한 묶음이다."""
    prov = _prov(); rid = "r6-v05-run"
    art = tmp_path / "matrix_100.csv"; art.write_text(f"a,run_id\n1,{rid}\n", encoding="utf-8")
    meta = {"artifact": "matrix_100.csv", "state": "100", "run_id": rid, "sha256": prov.sha256_file(art)}
    (tmp_path / "matrix_100.csv.meta.json").write_text(json.dumps(meta), encoding="utf-8")
    assert prov.verify_unit(art) == (True, "일치")
    shutil.copy(art, tmp_path / "matrix_200.csv")
    shutil.copy(tmp_path / "matrix_100.csv.meta.json", tmp_path / "matrix_200.csv.meta.json")
    ok, why = prov.verify_unit(tmp_path / "matrix_200.csv")
    assert ok is False and "artifact" in why, (ok, why)


# ── V6-06 · `# printed_format,17` — audit 는 선언으로 세는데 meta 리더는 숫자라 버린다 ─────────────────
def test_i6v_06_numeric_printed_format_declaration_is_unparseable_not_absent(tmp_path):
    """[R6 내부 V6-06] `read_dd_eval_meta` 가 값이 숫자면 버려서 `resolve_precision` 은 '선언 없음(추정)' 으로 갔다
    → auto 에서 invalid(2) 가 아니라 partial/model_mismatch. R5-02 의 "역할은 값 변환 전에 이름으로" 를 meta
    리더에도 적용한다: `printed_format` 은 값이 무엇이든 선언이고, 해석 못 하면 invalid."""
    anchors, cols, P, py, rows = _r2_base()
    p = _r2_csv(tmp_path, anchors, cols, rows, head=("# printed_format,17",))
    assert verify.read_dd_eval_meta(p).get(verify.PRINTED_FORMAT_KEY) == "17"
    assert verify.declared_precision(p) == "invalid"
    pol = verify.resolve_precision(p)
    assert pol["source"] == "invalid" and pol["declared_raw"] == "17", pol
    res, txt = _r2_run(anchors, P, py, p)                   # 값은 전부 같아도 선언 해석 불가 → invalid
    assert res["status"] == "invalid", (res["status"], txt[-300:])


# ── V6-07 · `--compare` 경로가 없으면 traceback 으로 종료 1 = README 의 "1 갈림" ────────────────────────
def test_i6v_07_unreadable_compare_path_is_incomplete_not_a_model_mismatch(tmp_path):
    """[R6 내부 V6-07] `cmd_eval` 은 ValueError 만 잡았다 — 없는 경로·디렉터리는 OSError traceback 으로 rc 1
    (판정 줄 없음). 못 읽은 파일은 '갈림' 이 아니라 대조 미완(2) 이다."""
    anchors, cols, P, py, rows = _r2_base()
    res, txt = _r2_run(anchors, P, py, tmp_path / "does_not_exist.csv")
    assert verify.EXIT_BY_STATUS[res["status"]] == 2, (res["status"], txt[-300:])
    res_d, txt_d = _r2_run(anchors, P, py, tmp_path)         # 디렉터리
    assert verify.EXIT_BY_STATUS[res_d["status"]] == 2, (res_d["status"], txt_d[-300:])


# ── V6-08 · `check_run_id` 의 CSV 분기는 DictReader — `run_id` 열이 둘이면 마지막 열만 본다 ─────────────
def test_i6v_08_duplicate_run_id_column_is_not_a_match(tmp_path):
    """[R6 내부 V6-08] 첫 `run_id` 열이 다른 시도의 id 여도 '전 행 일치'. dd_eval audit 의 '중복 열' 과 비대칭이었다."""
    prov = _prov()
    p = tmp_path / "dup.csv"; p.write_text("run_id,x,run_id\nother-run,1,the-run\n", encoding="utf-8")
    ok, why = prov.check_run_id(p, "the-run")
    assert ok is False and "run_id" in why, (ok, why)
