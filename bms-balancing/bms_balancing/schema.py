"""산출물 스키마의 **한 정본** (Codex R9-03) — producer 가 쓰는 열/키와 checker·reader 가 요구하는 열/키는 여기서만 나온다.

전 판은 `check_u14.MATRIX_COLS` 가 producer 와 따로 살아서 (i) 과학 열(`LLI_pct`)이 사라져도 (ii) 출처 열 값이 비어도
(iii) 실행 조건이 바뀌어도 "전부 갖췄다 · 게시·서명만 바뀌었다" 였고, `ne_shape` 는 중복 key 의 첫 행을 과학 결과로 썼다
(R9-05). producer·checker·reader 가 같은 함수를 부른다.
"""
from __future__ import annotations
import hashlib, json, re

# ── 행/키 스키마 (producer 의 dict 키 순서 그대로) ─────────────────────────────────────────────
MATRIX_ROW = (
    "half_cell", "si", "w_dqdv", "run_id", "inputs_sha", "ref_inputs_sha", "consumed_inputs", "ref_consumed_inputs",
    "scale_seed", "n_scale_samples", "scale_pocv_target", "scale_dvdq_target", "scale_dqdv_target",
    "scale_pocv_ref", "scale_dvdq_ref", "scale_dqdv_ref", "scale_audit_target", "scale_audit_ref",
    "obj", "rmse_pocv", "a_PE", "b_PE", "a_NE", "b_NE", "gamma_Si", "c_cell", "bounds",
    "ref_a_PE", "ref_b_PE", "ref_a_NE", "ref_b_NE", "ref_gamma_Si", "ref_obj", "ref_rmse_pocv", "ref_c_cell", "ref_bounds",
    "LAM_PE_pct", "LAM_NE_pct", "LLI_pct")
PROFILE_ROW = (
    "gamma_Si", "obj", "obj_ratio_to_best", "rmse_pocv", "a_PE", "b_PE", "a_NE", "b_NE", "bounds",
    "LAM_PE_pct", "LAM_NE_pct", "LLI_pct", "n_ok", "n_tried", "run_id", "profile_scale",
    "inputs_sha", "ref_inputs_sha", "consumed_inputs", "ref_consumed_inputs")
DEGENERACY_KEYS = (
    "state", "si_source", "half_cell", "w_dqdv", "tol_percent_of_best", "n_starts", "seed", "n_grid", "n_samples",
    "run_id", "env", "consumed_inputs", "ref_consumed_inputs", "inputs_sha",
    "n_accepted", "best_obj", "best_p", "ref_p", "best_modes_percent",
    "LAM_PE_percent", "LAM_NE_percent", "LLI_percent")
#: 재실행이 "같은 실행" 이려면 같아야 하는 조건 (수치가 아니라 **조건** — 다르면 승격 대상이 아니다)
DEGENERACY_CONTROLS = ("state", "si_source", "half_cell", "w_dqdv", "tol_percent_of_best", "n_starts", "seed", "n_grid", "n_samples")
#: 값이 **비어 있으면 안 되는** 열 — 존재만으로는 provenance 가 아니다 (R9-03 B)
PROVENANCE_COLS = ("ref_inputs_sha", "consumed_inputs", "ref_consumed_inputs")
#: 비어 있어도 되는 열 — producer 가 감사 dict 가 없으면 "" 를 쓴다 (`cmd_matrix` 의 scale_audit_*)
MAY_BE_EMPTY = frozenset({"scale_audit_target", "scale_audit_ref"})
#: 숫자로 파싱돼야 하는 과학 열
MATRIX_NUMERIC = ("obj", "rmse_pocv", "a_PE", "b_PE", "a_NE", "b_NE", "gamma_Si", "c_cell", "LAM_PE_pct", "LAM_NE_pct", "LLI_pct")
PROFILE_NUMERIC = ("gamma_Si", "obj", "obj_ratio_to_best", "rmse_pocv", "LAM_PE_pct", "LAM_NE_pct", "LLI_pct")
#: 숫자 대조에서 뺄 열 (출처·감사 문자열 — 숫자가 아니다)
ROW_SKIP = frozenset({"run_id", "inputs_sha", "ref_inputs_sha", "consumed_inputs", "ref_consumed_inputs",
                      "scale_audit_target", "scale_audit_ref"})

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_HEX12 = re.compile(r"^[0-9a-f]{12}$")


def inputs_digest(consumed: dict) -> str:
    """소비한 입력 파일들의 sha256 을 정렬해 이어 붙인 것의 sha256 앞 12 자리 (R6 내부 F1·F4: 라벨이 아니라 identity)."""
    shas = []
    for v in consumed.values():
        if isinstance(v, dict) and "sha256" in v:
            shas.append(v["sha256"])
        elif isinstance(v, dict):
            shas.extend(w["sha256"] for w in v.values() if isinstance(w, dict) and "sha256" in w)
    return hashlib.sha256("".join(sorted(shas)).encode()).hexdigest()[:12]


def required_columns(kind: str) -> tuple:
    return {"matrix": MATRIX_ROW, "profile": PROFILE_ROW}[kind]


def matrix_key(row: dict) -> tuple:
    """정규화한 identity — `w_dqdv` 는 숫자다 ("0" 과 "0.0" 은 같은 행이다, R9-05)."""
    return (row.get("half_cell"), row.get("si"), float(row.get("w_dqdv") if row.get("w_dqdv") not in (None, "") else "nan"))


def profile_key(row: dict) -> float:
    return float(row.get("gamma_Si") if row.get("gamma_Si") not in (None, "") else "nan")


def unique_rows(rows, key):
    """(key → 행, 중복 key 목록, 행 수). 중복은 **조용히 합치지 않는다** — checker(R8-05)·reader(R9-05)가 같은 함수를 쓴다."""
    seen, dup, out = {}, [], {}
    for r in rows:
        k = key(r)
        seen[k] = seen.get(k, 0) + 1
        if seen[k] > 1 and k not in dup:
            dup.append(k)
        out.setdefault(k, r)
    return out, dup, len(rows)


def validate_receipt(text, digest, where="") -> list:
    """`consumed_inputs` JSON 문자열(또는 dict) + 그 aggregate digest → 문제 목록. 비어 있으면 안 되고, 역할마다 path 와
    64-hex sha256 이 있어야 하며, digest 는 그 sha256 들에서 **다시 계산한 값**과 같아야 한다 (R9-03 B)."""
    p = []
    if text in (None, ""):
        return [f"{where}: 출처(receipt)가 비어 있다"]
    try:
        d = json.loads(text) if isinstance(text, str) else text
    except (TypeError, ValueError) as e:
        return [f"{where}: receipt 가 JSON 이 아니다 ({e})"]
    if not isinstance(d, dict) or not d:
        return [f"{where}: receipt 가 빈 dict 이거나 dict 가 아니다"]
    leaves = []
    for role, v in d.items():
        if isinstance(v, dict) and "sha256" in v:
            leaves.append((role, v))
        elif isinstance(v, dict):
            leaves += [(f"{role}.{k}", w) for k, w in v.items() if isinstance(w, dict)]
        else:
            p.append(f"{where}: 역할 {role!r} 이 dict 가 아니다")
    if not leaves:
        p.append(f"{where}: receipt 에 (path, sha256) 항목이 없다")
    for role, leaf in leaves:
        if not str(leaf.get("path") or "").strip():
            p.append(f"{where}: {role} 의 path 가 비어 있다")
        if not _HEX64.match(str(leaf.get("sha256") or "")):
            p.append(f"{where}: {role} 의 sha256 이 64-hex 가 아니다")
    if digest in (None, "") or not _HEX12.match(str(digest)):
        p.append(f"{where}: aggregate digest 가 12-hex 가 아니다 ({digest!r})")
    elif not p and inputs_digest(d) != digest:
        p.append(f"{where}: aggregate digest 불일치 — 재계산 {inputs_digest(d)} ≠ 기록 {digest}")
    return p


def check_rows(kind: str, rows: list, header: list) -> list:
    """CSV 산출 한 파일의 exact schema 검사 → 문제 목록 (열 존재 · 필수 셀 nonempty · 숫자 파싱 · receipt · 중복 key)."""
    need = required_columns(kind)
    p = [f"열 없음: {c}" for c in need if c not in header]
    numeric = MATRIX_NUMERIC if kind == "matrix" else PROFILE_NUMERIC
    for i, r in enumerate(rows):
        if kind == "matrix" and r.get("error"):
            continue                                                       # 실패한 조합의 행 — 과학 열이 비어 있는 것이 맞다
        for c in need:
            if c in header and c not in MAY_BE_EMPTY and (r.get(c) is None or str(r.get(c)) == ""):
                p.append(f"행 {i}: 필수 셀 {c} 이 비어 있다")
        for c in numeric:
            if c in header and str(r.get(c) or "") != "":
                try:
                    float(r[c])
                except ValueError:
                    p.append(f"행 {i}: {c} 가 숫자가 아니다 ({r[c]!r})")
        if all(c in header for c in ("consumed_inputs", "inputs_sha")):
            p += validate_receipt(r.get("consumed_inputs"), r.get("inputs_sha"), f"행 {i} consumed_inputs")
        if all(c in header for c in ("ref_consumed_inputs", "ref_inputs_sha")):
            p += validate_receipt(r.get("ref_consumed_inputs"), r.get("ref_inputs_sha"), f"행 {i} ref_consumed_inputs")
    _, dup, _ = unique_rows(rows, matrix_key if kind == "matrix" else profile_key)
    p += [f"중복 key {k}" for k in dup]
    return p


def check_degeneracy(j: dict) -> list:
    p = [f"키 없음: {k}" for k in DEGENERACY_KEYS if j.get(k) in (None, "")]
    if "consumed_inputs" in j:
        p += validate_receipt(j.get("consumed_inputs"), j.get("inputs_sha"), "consumed_inputs")
    if "ref_consumed_inputs" in j and j.get("ref_consumed_inputs"):
        ref = j["ref_consumed_inputs"]
        if isinstance(ref, dict):
            p += [x for x in validate_receipt(ref, inputs_digest(ref), "ref_consumed_inputs") if "digest" not in x]
    return p
