#!/usr/bin/env python3
"""U14 재실행 점검 — 새 산출이 (a) 새 스키마를 담고 (b) 정본과 **같은 숫자**인가.

R6 내부 리뷰가 게시·서명 경로를 고쳤다 (`reviews/R6_LEDGER.md`). 계산 경로는 안 건드렸으므로 재실행의 숫자는
정본과 **비트 단위로 같아야 한다**. 다르면 그것이 발견이다 — 먼저 볼 축은 F3(라이브러리 버전)이고, 새 meta 의
`env` 가 그때 처음 근거를 준다. 그래서 재실행은 `OUT=out_u14` 처럼 **다른 디렉터리로** 받고 이 스크립트로 댄 뒤에만
정본을 교체한다 (정본을 먼저 덮으면 비교 대상이 사라진다).

    python3 scripts/check_u14.py --new out_u14            # 정본 out/ 과 대조
    python3 scripts/check_u14.py --new out_u14 --old out --schema-only   # 스키마만

종료 코드: 0 = 스키마 갖췄고 숫자 동일 · 1 = 숫자가 다름 · 2 = 스키마 누락·파일 없음.
"""
from __future__ import annotations
import argparse, csv, json, pathlib, sys

# 산출 종류별 **새 스키마** 필수 필드 (R6 내부 F3·F4·F5 · R5-04·R5-07·R5-08)
JSON_KEYS = ("run_id", "n_grid", "n_samples", "env", "consumed_inputs", "inputs_sha")
MATRIX_COLS = ("run_id", "inputs_sha", "scale_seed", "n_scale_samples")
PROFILE_COLS = ("run_id", "inputs_sha", "profile_scale")
META_KEYS = ("run_id", "sha256", "artifact", "env", "started_utc",
             "git_commit_at_start", "git_state_changed_during_run")

# 대조할 **수치** 필드 (스키마·provenance 필드는 당연히 다르다 — 숫자만 본다)
JSON_NUM = ("n_accepted", "best_obj", "best_p", "ref_p", "best_modes_percent",
            "LAM_PE_percent", "LAM_NE_percent", "LLI_percent",
            "LAM_PE_percent_observed_cloud", "LAM_NE_percent_observed_cloud",
            "LLI_percent_observed_cloud")
ROW_SKIP = {"run_id", "inputs_sha", "scale_audit_target", "scale_audit_ref"}


def _rows(p: pathlib.Path, key):
    with p.open(encoding="utf-8", newline="") as fh:
        return {key(r): r for r in csv.DictReader(fh)}


def _num_diff(a, b, path=""):
    """같은 모양의 두 값에서 다른 스칼라를 [(경로, 옛, 새)] 로. 숫자는 문자열이어도 float 로 댄다."""
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            out += _num_diff(a.get(k), b.get(k), f"{path}.{k}" if path else k)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path, f"길이 {len(a)}", f"길이 {len(b)}"))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                out += _num_diff(x, y, f"{path}[{i}]")
    else:
        try:
            if float(a) == float(b):
                return out
        except (TypeError, ValueError):
            if a == b:
                return out
        out.append((path, a, b))
    return out


def check(new: pathlib.Path, old: pathlib.Path | None, schema_only=False):
    missing, diffs, seen = [], [], 0
    # ⚠ `.meta.json` 은 산출이 아니다 — `degeneracy_*.json` glob 이 `degeneracy_100_Li.json.meta.json` 까지
    #   먹어서 meta 를 산출로 점검했다 (TOCTOU 렌즈 N02 가 소비자 glob 에서 확인한 것과 같은 종류).
    arts = [f for f in sorted(new.glob("degeneracy_*.json")) + sorted(new.glob("matrix_*.csv"))
            + sorted(new.glob("profile_gamma_*.csv")) if not f.name.endswith(".meta.json")]
    for f in arts:
        seen += 1
        if f.suffix == ".json":
            j = json.loads(f.read_text(encoding="utf-8"))
            missing += [f"{f.name}: {k}" for k in JSON_KEYS if j.get(k) in (None, "")]
        else:
            need = MATRIX_COLS if f.name.startswith("matrix_") else PROFILE_COLS
            with f.open(encoding="utf-8", newline="") as fh:
                hdr = next(csv.reader(fh), [])
            missing += [f"{f.name}: {c}" for c in need if c not in hdr]
        m = f.with_name(f.name + ".meta.json")
        if not m.is_file():
            missing.append(f"{f.name}: .meta.json 없음")
        else:
            meta = json.loads(m.read_text(encoding="utf-8"))
            missing += [f"{f.name}.meta: {k}" for k in META_KEYS if meta.get(k) is None]
        if schema_only or old is None:
            continue
        o = old / f.name
        if not o.is_file():
            diffs.append((f.name, "정본에 없음", "새 파일만 있다")); continue
        if f.suffix == ".json":
            a, b = json.loads(o.read_text(encoding="utf-8")), json.loads(f.read_text(encoding="utf-8"))
            for k in JSON_NUM:
                diffs += [(f"{f.name}:{k}{p and '.' + p}", x, y) for p, x, y in _num_diff(a.get(k), b.get(k))]
        else:
            key = ((lambda r: (r["half_cell"], r["si"], r["w_dqdv"])) if f.name.startswith("matrix_")
                   else (lambda r: r["gamma_Si"]))
            A, B = _rows(o, key), _rows(f, key)
            for k in sorted(set(A) | set(B)):
                if k not in A or k not in B:
                    diffs.append((f"{f.name}:{k}", "정본에만" if k in A else "새 산출에만", "")); continue
                for c in sorted(set(A[k]) & set(B[k]) - ROW_SKIP):
                    diffs += [(f"{f.name}:{k}:{c}", x, y) for _, x, y in _num_diff(A[k][c], B[k][c])]
    return seen, missing, diffs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True, help="재실행 산출 디렉터리 (예: out_u14)")
    ap.add_argument("--old", default="out", help="정본 디렉터리 (기본 out)")
    ap.add_argument("--schema-only", action="store_true", help="숫자 대조 없이 새 스키마만")
    ap.add_argument("--max-show", type=int, default=20)
    a = ap.parse_args()
    new, old = pathlib.Path(a.new), (None if a.schema_only else pathlib.Path(a.old))
    if not new.is_dir():
        print(f"! {new} 가 없다"); return 2
    seen, missing, diffs = check(new, old, a.schema_only)
    print(f"산출 {seen} 개 점검 ({new})")
    if not seen:
        print("! 점검할 산출이 없다 — 경로가 맞나?"); return 2
    if missing:
        print(f"\n■ 새 스키마 누락 {len(missing)} — 옛 코드로 만든 산출이다 (재실행이 이 트리에서 돌았는지 확인)")
        for m in missing[:a.max_show]:
            print(f"  - {m}")
        if len(missing) > a.max_show:
            print(f"  … 외 {len(missing) - a.max_show}")
    else:
        print("  새 스키마: 전부 갖췄다 (run_id·sha256·env·inputs_sha·시작 시점 git·인자 필드)")
    if old is not None:
        if diffs:
            print(f"\n■ 정본과 **다른 숫자** {len(diffs)} — 계산 경로는 안 고쳤으므로 같아야 한다.")
            print("   먼저 볼 축: meta 의 `env`(python·numpy·scipy) 가 정본을 만든 기계와 같은가 (R6 내부 F3:")
            print("   scipy 1.11↔1.17 에서 savgol 이 ULP 로 갈리고 L-BFGS-B 최적점이 달라진다).")
            for p, x, y in diffs[:a.max_show]:
                print(f"  - {p}: 정본 {x} → 새 {y}")
            if len(diffs) > a.max_show:
                print(f"  … 외 {len(diffs) - a.max_show}")
        else:
            print(f"  숫자: 정본({old})과 전부 같다 — 게시·서명만 바뀌었다")
    return 2 if missing else (1 if diffs else 0)


if __name__ == "__main__":
    sys.exit(main())
