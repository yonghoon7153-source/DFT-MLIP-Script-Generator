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
import argparse, csv, json, pathlib, re, sys

VER = re.compile(r"_v(\d+)$")          # `matrix_300_0009_v2.csv` — compare_states._split_version 과 같은 규칙

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


def baseline_for(new_file: pathlib.Path, old: pathlib.Path) -> pathlib.Path | None:
    """`new_file` 에 대응하는 **정본** — 같은 이름이 아니라 가장 높은 판이다 (`_v2` 가 있으면 그것).

    ⚠ U14-02: 전 판은 이름으로만 골라 `degeneracy_300_0009_Li.json`(v1, 힌트 격자 이전)과 댔다. 정본은 `_v2` 고
      (`compare_states._keep_latest` 가 표에 쓰는 것도 그쪽), 그래서 재실행이 v2 를 그대로 재현했는데도
      span 0.0908 → 2.5826 이 "숫자가 움직였다" 로 나왔다.
    """
    stem, suffix = new_file.stem, new_file.suffix
    base = VER.sub("", stem)
    cands = []
    for f in old.glob(f"{base}*{suffix}"):
        if f.name.endswith(".meta.json"):
            continue
        st = VER.sub("", f.stem)
        if st != base:
            continue
        m = VER.search(f.stem)
        cands.append((int(m.group(1)) if m else 1, f))
    return max(cands)[1] if cands else None


def _rows(p: pathlib.Path, key):
    with p.open(encoding="utf-8", newline="") as fh:
        return {key(r): r for r in csv.DictReader(fh)}


def _num_diff(a, b, path="", added=None):
    """같은 모양의 두 값에서 다른 스칼라를 [(경로, 옛, 새)] 로. 숫자는 문자열이어도 float 로 댄다.

    ⚠ U14-02: 정본에 **없던 필드**(스키마 추가분 — `grid_pct`·`attainable_pct` 등)는 `None → [값]` 이 되어 전부
      diff 로 세어졌다 (618 건 중 대부분). 새 필드는 스키마 얘기지 숫자가 움직인 것이 아니다 — `added` 로 뺀다.
    """
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            kp = f"{path}.{k}" if path else k
            if k not in a and added is not None:
                added.append(kp); continue
            out += _num_diff(a.get(k), b.get(k), kp, added)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path, f"길이 {len(a)}", f"길이 {len(b)}"))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                out += _num_diff(x, y, f"{path}[{i}]", added)
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
    missing, diffs, seen, added, paired = [], [], 0, [], []
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
        o = baseline_for(f, old)
        if o is None:
            diffs.append((f.name, "정본에 없음", "새 파일만 있다")); continue
        paired.append((f.name, o.name))
        if f.suffix == ".json":
            a, b = json.loads(o.read_text(encoding="utf-8")), json.loads(f.read_text(encoding="utf-8"))
            for k in JSON_NUM:
                sub = []
                diffs += [(f"{f.name}:{k}{p and '.' + p}", x, y) for p, x, y in _num_diff(a.get(k), b.get(k), added=sub)]
                added += [f"{f.name}:{k}.{x}" for x in sub]
        else:
            key = ((lambda r: (r["half_cell"], r["si"], r["w_dqdv"])) if f.name.startswith("matrix_")
                   else (lambda r: r["gamma_Si"]))
            A, B = _rows(o, key), _rows(f, key)
            for k in sorted(set(A) | set(B)):
                if k not in A or k not in B:
                    diffs.append((f"{f.name}:{k}", "정본에만" if k in A else "새 산출에만", "")); continue
                added += [f"{f.name}:{c}" for c in sorted(set(B[k]) - set(A[k]) - ROW_SKIP)]
                for c in sorted(set(A[k]) & set(B[k]) - ROW_SKIP):
                    diffs += [(f"{f.name}:{k}:{c}", x, y) for _, x, y in _num_diff(A[k][c], B[k][c])]
    return seen, missing, diffs, sorted(set(added)), paired


def renormalize(new: pathlib.Path) -> int:
    """U14-01 뒷수습 — 이미 게시된 CSV 가 CRLF 면 LF 로 고치고 meta 를 **다시 서명**한다.

    재실행 없이 bytes 를 바꾸는 것이므로 조건을 건다: 파싱한 셀이 **완전히 같아야** 한다 (줄끝만 다르다는 증명).
    하나라도 다르면 그 파일은 건드리지 않는다 — 그때는 재실행이 답이다. 무엇을 했는지는 meta 에 적는다.
    """
    import datetime, hashlib
    touched, refused, skipped = [], [], []
    for f in sorted(new.glob("*.csv")):
        raw = f.read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        if lf != raw:                               # 디스크가 CRLF 면 먼저 LF 로 (셀이 같을 때만)
            if list(csv.reader(raw.decode("utf-8").splitlines())) != list(csv.reader(lf.decode("utf-8").splitlines())):
                refused.append(f"{f.name} (줄끝 말고 다른 것이 바뀐다)"); continue
        m = f.with_name(f.name + ".meta.json")
        if not m.is_file():
            skipped.append(f"{f.name} (meta 없음 — 옛 산출)")
            if lf != raw:
                f.write_bytes(lf); touched.append(f"{f.name} (줄끝만, 서명 없음)")
            continue
        meta = json.loads(m.read_text(encoding="utf-8"))
        want = meta.get("sha256")
        if not want:                                # 옛 meta (R5 이전) — 서명이 없으니 다시 서명할 것도 없다
            skipped.append(f"{f.name} (옛 meta — sha256 없음)")
            if lf != raw:
                f.write_bytes(lf); touched.append(f"{f.name} (줄끝만, 서명 없음)")
            continue
        # ⚠ 기록된 해시가 **어느 줄끝**의 것이든, 지금 bytes 의 줄끝 변형 중 하나와 맞으면 "줄끝만 다르다" 가
        #   증명된다 (git 정규화는 CRLF→LF, Windows 체크아웃은 LF→CRLF — 양쪽 다 본다).
        crlf = lf.replace(b"\n", b"\r\n")
        if want not in {hashlib.sha256(x).hexdigest() for x in (raw, lf, crlf)}:
            refused.append(f"{f.name} (meta 의 sha256 이 줄끝 변형 어느 것과도 안 맞는다 — 내용이 다르다)"); continue
        if want == hashlib.sha256(lf).hexdigest() and lf == raw:
            continue                                # 이미 LF 이고 서명도 그것 — 할 일 없음
        f.write_bytes(lf)
        meta["sha256"] = hashlib.sha256(lf).hexdigest()
        meta["bytes_renormalized"] = {
            "what": "CRLF→LF", "why": "U14-01 — writer 가 CRLF 를 썼고 git 은 LF 로 저장한다 (서명이 fresh clone 에서 깨진다)",
            "verified": "기록된 sha256 이 지금 bytes 의 줄끝 변형과 맞는다 (내용은 같고 줄끝만 다르다)",
            "utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        m.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        touched.append(f.name)
    print(f"줄끝 정규화: {len(touched)} 개 처리" + (f" — {', '.join(touched)}" if touched else " (고칠 것이 없다)"))
    if skipped:
        print(f"  meta 없는 옛 산출 {len(skipped)} — 서명이 없어 다시 서명할 것도 없다: {', '.join(skipped[:6])}")
    if refused:
        print(f"! 손대지 않음 {len(refused)}: {', '.join(refused)}")
        print("  내용이 다르다는 뜻이다 — 재실행이 답이다 (bytes 를 손으로 고치면 서명의 뜻이 사라진다).")
    return 1 if refused else 0


def extract_rev(rev: str, dest: pathlib.Path, repo: pathlib.Path) -> int:
    """`<rev>` 의 `out/` 을 `dest` 로 꺼낸다 — 정본을 git 에서 직접 읽는다.

    ⚠ 2026-09-12: `git show <rev> --name-only` 는 그 커밋이 **바꾼** 파일을 주지 트리를 주지 않는다. 그걸로
      정본을 모으면 디렉터리가 비고 전부 "정본에 없음" 으로 나온다. 트리는 `git ls-tree -r` 다.
    """
    import subprocess
    dest.mkdir(parents=True, exist_ok=True)
    try:
        names = subprocess.run(["git", "ls-tree", "-r", "--name-only", rev, "--", "out"],
                               cwd=repo, capture_output=True, text=True, check=True).stdout.split()
    except subprocess.CalledProcessError as e:
        print(f"! `{rev}` 를 읽지 못했다: {e.stderr.strip()}"); return 0
    n = 0
    for name in names:
        rel = pathlib.PurePosixPath(name)
        # `out/` **바로 아래**의 산출만 — `out/bms97/`·`out/recompare/`·`out/cells_*/` 는 다른 축이고,
        # basename 만 떼면 이름이 부딪친다.
        if len(rel.parts) != 2 or rel.suffix not in (".json", ".csv"):
            continue
        # ⚠ `<rev>:<path>` 는 **저장소 루트** 기준이다. cwd 가 하위 디렉터리면 `:./` 를 써야 여기 기준이 된다.
        r = subprocess.run(["git", "show", f"{rev}:./{name}"], cwd=repo, capture_output=True)
        if r.returncode != 0:
            continue
        (dest / rel.name).write_bytes(r.stdout); n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True, help="재실행 산출 디렉터리 (예: out_u14)")
    ap.add_argument("--old", default="out", help="정본 디렉터리 (기본 out)")
    ap.add_argument("--old-rev", default=None, metavar="REV",
                    help="정본을 디렉터리 대신 **git 커밋**에서 읽는다 (예: `HEAD^`) — 재실행이 out/ 을 이미 "
                         "덮었을 때. 손으로 `git show` 를 엮지 않게 한다")
    ap.add_argument("--schema-only", action="store_true", help="숫자 대조 없이 새 스키마만")
    ap.add_argument("--max-show", type=int, default=20)
    ap.add_argument("--renormalize", action="store_true",
                    help="U14-01 뒷수습: CRLF 로 게시된 CSV 를 LF 로 고치고 meta 를 다시 서명한다 "
                         "(파싱한 셀이 완전히 같을 때만 — 아니면 그 파일은 건드리지 않는다)")
    a = ap.parse_args()
    import tempfile
    new = pathlib.Path(a.new)
    if not new.is_dir():
        print(f"! {new} 가 없다"); return 2
    if a.renormalize:
        return renormalize(new)
    old = None if a.schema_only else pathlib.Path(a.old)
    tmp = None
    if a.old_rev and not a.schema_only:
        tmp = tempfile.TemporaryDirectory(); old = pathlib.Path(tmp.name)
        n = extract_rev(a.old_rev, old, pathlib.Path(__file__).resolve().parents[1])
        print(f"정본을 `{a.old_rev}` 에서 읽었다 — 산출 {n} 개")
        if not n:
            print("! 그 커밋의 out/ 이 비었다 — 리비전이 맞나?"); return 2
    seen, missing, diffs, added, paired = check(new, old, a.schema_only)
    print(f"산출 {seen} 개 점검 ({new})")
    for n, o in paired:
        if n != o:
            print(f"  정본 선택: {n} ↔ **{o}** (가장 높은 판 — compare_states 가 표에 쓰는 것과 같은 규칙)")
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
        if added:
            print(f"\n  정본에 없던 필드 {len(added)} — 스키마 추가분이다 (숫자가 움직인 것이 아니다): "
                  + ", ".join(sorted({x.split(":")[-1].split(".")[-1] for x in added})[:12]))
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
