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
    "inputs_sha", "ref_inputs_sha", "consumed_inputs", "ref_consumed_inputs",
    #: ⚠ Codex R10 P1-3: 실패한 γ 는 행에서 빠지므로 **행만 보면 모집단을 알 수 없다**. 요청·성공·누락을 행마다
    #:   봉인한다 — 사라지는 stdout 요약이 아니라 검증되는 묶음이 스스로 말한다 (R8-04 와 같은 축).
    "gamma_roster")
DEGENERACY_KEYS = (
    "state", "si_source", "half_cell", "w_dqdv", "tol_percent_of_best", "n_starts", "seed", "n_grid", "n_samples",
    "run_id", "env", "consumed_inputs", "ref_consumed_inputs", "inputs_sha",
    "n_accepted", "best_obj", "best_p", "ref_p", "best_modes_percent",
    "LAM_PE_percent", "LAM_NE_percent", "LLI_percent")
#: 재실행이 "같은 실행" 이려면 같아야 하는 조건 (수치가 아니라 **조건** — 다르면 승격 대상이 아니다)
DEGENERACY_CONTROLS = ("state", "si_source", "half_cell", "w_dqdv", "tol_percent_of_best", "n_starts", "seed", "n_grid", "n_samples")
#: 값이 **비어 있으면 안 되는** 열 — 존재만으로는 provenance 가 아니다 (R9-03 B)
PROVENANCE_COLS = ("ref_inputs_sha", "consumed_inputs", "ref_consumed_inputs")
#: receipt 가 반드시 담아야 하는 **역할** — `build()` 가 소비하는 입력 전부 (Codex R10 P1-6). 역할이 빠지거나 모르는
#: 역할이 끼면 그것은 다른 계산이다; decoy 하나로 provenance 를 참칭할 수 없다.
REQUIRED_ROLES = ("full_cell", "half_cell", "literature.gr", "literature.si")
#: 승격 판정에서 **같아야 하는** 환경 축 (R6 내부 F3: scipy 1.11↔1.17 에서 최적점이 갈린다)
ENV_KEYS = ("python", "numpy", "scipy", "platform")
#: sidecar 가 반드시 담아야 하는 실행 조건 — **양쪽에 있어야** 비교가 성립한다 (Codex R10 P1-7: 지우면 검사가 잠들었다)
META_CONTROLS = ("state", "half_cell_source", "si_source", "starts", "seed")
#: success 행에는 없어야 하는 열 — 있으면 그 행은 error 행이고 묶음은 승격 대상이 아니다 (Codex R10 P1-5)
ERROR_COL = "error"
#: 산출 version — digest 규칙이 바뀌면 올린다 (옛 digest 와 새 digest 가 섞여 보이지 않게)
RECEIPT_SCHEMA_VERSION = "r10.1"
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


def receipt_leaves(consumed) -> list:
    """receipt → `[(역할, leaf dict)]`. 중첩 한 단계까지 `literature.gr` 처럼 점으로 이어 붙인 **역할 이름**이 key 다."""
    out = []
    if not isinstance(consumed, dict):
        return out
    for role, v in consumed.items():
        if isinstance(v, dict) and "sha256" in v:
            out.append((str(role), v))
        elif isinstance(v, dict):
            out += [(f"{role}.{k}", w) for k, w in v.items() if isinstance(w, dict)]
        else:
            out.append((str(role), v))
    return out


def inputs_digest(consumed: dict) -> str:
    """소비한 입력의 **역할별** identity 를 묶은 digest 앞 12 자리.

    ⚠ Codex R10 P1-6: 전 판은 sha256 **값만** 정렬해 이어 붙였다 — half_cell 과 full_cell 을 바꿔치기해도 같은 값
      (`76be1dcab00e`) 이었고, 어떤 역할이 있어야 하는지도 묶이지 않아 `{"decoy": …}` 하나가 provenance 로 통과했다.
      이제 `(역할, sha256)` 쌍을 역할 이름으로 정렬해 버전 태그와 함께 해시한다.
    ⚠ **경로는 일부러 digest 에 넣지 않는다.** R6 내부 F4 는 "같은 bytes 면 같은 실행" 을 고정했고
      (`test_i6p_04`: 이름만 다른 사본은 같은 digest), 경로를 넣으면 byte 가 같은 재-export 가 다른 실행으로 읽힌다.
      경로는 receipt 안에 그대로 남고 `validate_receipt` 가 비어 있지 않은지 본다 — identity 는 bytes 다 (R6 내부 F1).
    """
    items = sorted((role, str(leaf.get("sha256", "")) if isinstance(leaf, dict) else "")
                   for role, leaf in receipt_leaves(consumed))
    payload = RECEIPT_SCHEMA_VERSION + "\n" + "\n".join(f"{role}={sha}" for role, sha in items)
    return hashlib.sha256(payload.encode()).hexdigest()[:12]


def env_problems(old: dict | None, new: dict | None, where: str = "env") -> list:
    """두 실행의 환경이 **같은가** (Codex R10 P1-7: 전 판은 존재만 봤다). 축마다 값을 대 본다."""
    p = []
    if not isinstance(old, dict) or not isinstance(new, dict):
        return [f"{where}: 환경 서명이 없다 (정본 {type(old).__name__} · 새 산출 {type(new).__name__})"]
    for k in ENV_KEYS:
        a, b = old.get(k), new.get(k)
        if a in (None, "") or b in (None, ""):
            p.append(f"{where}.{k}: 환경 축이 비어 있다 (정본 {a!r} · 새 산출 {b!r})")
        elif a != b:
            p.append(f"{where}.{k}: 환경이 다르다 — 정본 {a!r} → 새 {b!r}")
    return p


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


def validate_receipt(text, digest, where="", roles=REQUIRED_ROLES) -> list:
    """`consumed_inputs` (JSON 문자열 또는 dict) + 그 digest → 문제 목록.

    비어 있으면 안 되고, **역할 집합이 정확히** `roles` 와 같아야 하며 (빠진 역할·모르는 역할 둘 다 문제),
    역할마다 path 와 64-hex sha256 이 있어야 하고, digest 는 그 (역할, sha256) 에서 **다시 계산한 값**과 같아야 한다
    (R9-03 B · Codex R10 P1-6).
    """
    p = []
    if text in (None, ""):
        return [f"{where}: 출처(receipt)가 비어 있다"]
    try:
        d = json.loads(text) if isinstance(text, str) else text
    except (TypeError, ValueError) as e:
        return [f"{where}: receipt 가 JSON 이 아니다 ({e})"]
    if not isinstance(d, dict) or not d:
        return [f"{where}: receipt 가 빈 dict 이거나 dict 가 아니다"]
    leaves = receipt_leaves(d)
    got = {role for role, _ in leaves}
    if roles:
        missing = [r for r in roles if r not in got]
        unknown = sorted(got - set(roles))
        if missing:
            p.append(f"{where}: 필수 입력 역할이 없다 — {missing} (있는 역할: {sorted(got)})")
        if unknown:
            p.append(f"{where}: 모르는 역할이 끼어 있다 — {unknown} (요구 역할: {list(roles)})")
    for role, leaf in leaves:
        if not isinstance(leaf, dict):
            p.append(f"{where}: 역할 {role!r} 이 dict 가 아니다"); continue
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
    """CSV 산출 한 파일의 exact schema 검사 → 문제 목록.

    **success / error 는 exact tagged union 이다** (Codex R10 P1-5). 전 판은 truthy `error` 한 칸이 그 행의 필수 셀·
    숫자·receipt 검사를 전부 `continue` 로 건너뛰게 했고, 열이 하나 늘어난 것은 "정보성" 으로 셌다 — 정상 수치 행에
    `error=skip` 을 붙이고 receipt 네 칸을 비우면 U18 gate 가 "전부 갖췄다 · 전부 같다 · rc 0" 이었다. 이제:

    - success 행에는 `error` 가 **없어야** 한다. 있으면 그 행은 error 행이고,
    - error 행이 하나라도 있으면 그 묶음은 success 가 아니다 → 승격 대상이 아니라고 **말한다** (문제로 센다),
    - 요구 열도 모르는 열도 아닌 것은 없어야 한다 (열이 조용히 늘면 그것이 다음 우회로다).
    """
    need = required_columns(kind)
    p = [f"열 없음: {c}" for c in need if c not in header]
    unknown = [c for c in header if c not in need and c != ERROR_COL]
    if unknown:
        p.append(f"모르는 열 {unknown} — producer 스키마에 없는 열이다 (`bms_balancing/schema.py` 가 정본)")
    numeric = MATRIX_NUMERIC if kind == "matrix" else PROFILE_NUMERIC
    n_error = 0
    for i, r in enumerate(rows):
        if str(r.get(ERROR_COL) or "").strip():
            n_error += 1
            continue                                                       # 실패한 조합의 행 — 아래 union 규칙이 센다
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
    if n_error:
        p.append(f"`{ERROR_COL}` 행 {n_error}/{len(rows)} — 이 묶음은 success 가 아니다 (부분/실패이고 승격 대상이 "
                 f"아니다; success 행에 `{ERROR_COL}` 칸이 있으면 그것도 error 행이다, Codex R10 P1-5)")
    _, dup, _ = unique_rows([r for r in rows if not str(r.get(ERROR_COL) or "").strip()],
                            matrix_key if kind == "matrix" else profile_key)
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
