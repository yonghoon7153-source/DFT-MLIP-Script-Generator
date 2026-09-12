#!/usr/bin/env python3
"""U14/U18 재실행 점검 — 새 산출이 (a) producer 스키마를 **내용까지** 담고 (b) 정본과 같은 명부·같은 실행 조건이며
(c) **같은 숫자**인가.

R6 내부 리뷰가 게시·서명 경로를 고쳤다 (`reviews/R6_LEDGER.md`). 계산 경로는 안 건드렸으므로 재실행의 숫자는
정본과 **비트 단위로 같아야 한다**. 다르면 그것이 발견이다 — 먼저 볼 축은 F3(라이브러리 버전)이고, 새 meta 의
`env` 가 그때 처음 근거를 준다. 그래서 재실행은 `OUT=out_u14` 처럼 **다른 디렉터리로** 받고 이 스크립트로 댄 뒤에만
정본을 교체한다 (정본을 먼저 덮으면 비교 대상이 사라진다).

    python3 scripts/check_u14.py --new out_u14            # 정본 out/ 과 대조
    python3 scripts/check_u14.py --new out_u14 --old out --schema-only   # 스키마만 (구조 검사는 전부 한다)
    python3 scripts/check_u14.py --new out_part --subset  # 명시적 부분 재실행 — 범위(k/N)를 찍고, 승격 근거가 아니다

⚠ Codex R9-02: 전 판은 **new 에 있는 파일만** 순회했다 — 정본 12 개 중 1 개만 재실행해도 "산출 1 개 · 전부 같다 · rc 0".
  명부(roster)는 정본과 새 산출의 canonical 이름 **합집합**이고, 정본에 있는데 새 산출에 없는 것은 실패다. 부분
  재실행은 `--subset` 으로 계약을 명시해야 하고, 그때도 범위(k/N)를 찍으며 승격 대상이 아니다.
⚠ Codex R9-03: 전 판은 열 **이름**만 봤다 — 과학 열(`LLI_pct`)이 사라져도, 출처 열 값이 전부 비어도, 실행 조건(n_starts·
  seed·n_grid·n_samples·tol)이 바뀌어도 "전부 갖췄다 · 게시·서명만 바뀌었다". 스키마의 정본은 `bms_balancing/schema.py`
  하나이고 (producer 가 같은 것을 assert 한다) 검사는 필수 셀 nonempty · 숫자 파싱 · receipt(역할·path·64-hex·재계산
  digest) · 중복 key · 실행 조건 대조까지다 — `--schema-only` 도 구조 검사는 전부 한다.

종료 코드: 0 = 명부·스키마·조건 갖췄고 숫자 동일 · 1 = 숫자가 다름 · 2 = 명부/스키마/내용/조건 불일치 · 묶음 미완 · 파일 없음.
"""
from __future__ import annotations
import argparse, csv, io, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from bms_balancing import schema as S          # noqa: E402  — producer·checker·reader 의 한 정본 (Codex R9-03)

VER = re.compile(r"_v(\d+)$")          # `matrix_300_0009_v2.csv` — 옛 리비전의 out/ 에만 있는 판 번호 (현행 정본은 unversioned, Codex R6-04)

# 산출 종류별 필수 필드 — **schema.py 가 정본**이고 여기는 이름만 빌린다 (Codex R8-02 · R9-03)
JSON_KEYS = S.DEGENERACY_KEYS
PROVENANCE_COLS = S.PROVENANCE_COLS
MATRIX_COLS = S.MATRIX_ROW
PROFILE_COLS = S.PROFILE_ROW
META_KEYS = ("run_id", "sha256", "artifact", "env", "started_utc",
             "git_commit_at_start", "git_state_changed_during_run")
#: meta 에서 "같은 실행" 이려면 같아야 하는 조건 (Codex R9-03 C)
META_CONTROLS = ("state", "half_cell_source", "si_source", "starts", "seed")

# 대조할 **수치** 필드 (스키마·provenance 필드는 당연히 다르다 — 숫자만 본다)
JSON_NUM = ("n_accepted", "best_obj", "best_p", "ref_p", "best_modes_percent",
            "LAM_PE_percent", "LAM_NE_percent", "LLI_percent",
            "LAM_PE_percent_observed_cloud", "LAM_NE_percent_observed_cloud",
            "LLI_percent_observed_cloud")
ROW_SKIP = S.ROW_SKIP                  # 출처 문자열은 숫자가 아니다


#: 정본 선택 정책 — 두 규칙은 **호출 모드로** 갈린다 (Codex R7-04). docstring 으로만 갈라 두면 현행 디렉터리에도
#: 역사 규칙이 걸린다: 현행 독자는 `_v2` 를 경고·제외하고 A 를 쓰는데 이 도구는 `_v2`(B) 를 골라 "전부 같다" rc 0 을
#: 냈다 (`_v2` 를 지우면 같은 대조가 차이 2 건 rc 1). `--old-rev` 로 **명시한 역사 리비전**에서만 최고판을 쓴다.
POLICY = {"current": "현행 디렉터리 — 정본은 unversioned 이름 하나, 판 번호가 붙은 형제는 쓰지 않는다 (Codex R6-04·R7-04)",
          "historical": "역사 리비전 — 그 커밋 당시의 정본, 즉 가장 높은 판 (`--old-rev` 로 명시했을 때만)"}


def baseline_for(new_file: pathlib.Path, old: pathlib.Path, policy: str = "current",
                 stale: list | None = None) -> pathlib.Path | None:
    """`new_file` 에 대응하는 옛 정본. `policy`:

    - `current`   : 같은(unversioned) 이름 하나. `_vN` 형제는 **쓰지 않고** `stale` 에 적어 보고한다.
    - `historical`: 그 리비전 당시의 정본 = 가장 높은 판 (`_v2` 가 있으면 그것).

    ⚠ U14-02: 전 판은 이름으로만 골라 `degeneracy_300_0009_Li.json`(v1, 힌트 격자 이전)과 댔다. 그 리비전의 정본은
      `_v2` 였고, 그래서 재실행이 v2 를 그대로 재현했는데도 span 0.0908 → 2.5826 이 "숫자가 움직였다" 로 나왔다.
    ⚠ Codex R7-04: 그 규칙이 현행 디렉터리에도 걸려 있었다 — 그래서 정책을 **인자로** 받는다 (주석이 아니라).
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
        if m and policy == "current":
            if stale is not None:
                stale.append(f.name)
            continue
        cands.append((int(m.group(1)) if m else 1, f))
    return max(cands)[1] if cands else None


def _kind(f: pathlib.Path) -> str:
    return "degeneracy" if f.suffix == ".json" else ("matrix" if f.name.startswith("matrix_") else "profile")


def canonical_names(d: pathlib.Path, policy: str = "current", stale: list | None = None) -> set:
    """디렉터리의 산출 **명부** — canonical basename 집합 (Codex R9-02).

    `current` 는 unversioned 이름만 (`_vN` 은 `stale` 에 적고 명부에서 뺀다), `historical` 은 `_vN` 을 뗀 이름으로 센다
    (그 리비전의 정본이 `_v2` 여도 명부의 항목은 하나다). `.meta.json` 은 산출이 아니다.
    """
    names = set()
    if not d.is_dir():
        return names
    for f in sorted(d.glob("degeneracy_*.json")) + sorted(d.glob("matrix_*.csv")) + sorted(d.glob("profile_gamma_*.csv")):
        if f.name.endswith(".meta.json"):
            continue
        if VER.search(f.stem) and policy == "current":
            if stale is not None:
                stale.append(f.name)
            continue
        names.add(VER.sub("", f.stem) + f.suffix)
    return names


def _csv_rows(data: bytes):
    """검증된 bytes → (행 목록, 헤더). 헤더 순서는 producer 가 정렬해 쓰므로 검사는 이름으로만 한다."""
    rd = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
    rows = list(rd)
    return rows, list(rd.fieldnames or [])


def _unit(f: pathlib.Path):
    """검증된 (data, meta) snapshot 만 — 경로를 따로 읽지 않는다 (Codex R8-02). → (ok, why, data, meta)"""
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from provenance import read_unit
    return read_unit(f)


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


def check(new: pathlib.Path, old: pathlib.Path | None, schema_only=False, policy: str = "current") -> dict:
    """새 산출을 명부·스키마·내용·조건·숫자로 대조한다 → 결과 dict (main 이 찍고 종료 코드를 정한다).

    키: seen · missing(열/키 이름 누락) · content(값이 스키마가 아님 — 빈 셀·숫자 아님·receipt·중복 key) · diffs(숫자) ·
    added(정본에 없던 필드) · paired · stale · broken(묶음 불일치/미완) · controls(실행 조건 불일치) ·
    roster_missing(정본에 있는데 새 산출에 없음) · roster_extra(새 산출에만) · n_old · n_new.
    """
    R: dict = {"seen": 0, "missing": [], "content": [], "diffs": [], "added": [], "paired": [], "stale": [],
               "broken": [], "controls": [], "roster_missing": [], "roster_extra": [], "n_old": 0, "n_new": 0}
    new_stale: list = []
    # ⚠ `.meta.json` 은 산출이 아니다 — `degeneracy_*.json` glob 이 `degeneracy_100_Li.json.meta.json` 까지
    #   먹어서 meta 를 산출로 점검했다 (TOCTOU 렌즈 N02 가 소비자 glob 에서 확인한 것과 같은 종류).
    new_names = canonical_names(new, "current", new_stale)
    R["stale"] += [f"{n} (새 산출 디렉터리)" for n in new_stale]
    R["n_new"] = len(new_names)
    if old is not None:
        # ⚠ Codex R9-02: 명부는 new 가 아니라 **정본 ∪ new** 다. 정본에 있는데 new 에 없는 것은 "안 본 것" 이지 "같은 것" 이
        #   아니다 — 전 판은 new 의 1 개만 돌고 "전부 같다" 였다.
        old_names = canonical_names(old, policy, R["stale"])
        R["n_old"] = len(old_names)
        R["roster_missing"] = sorted(old_names - new_names)
        R["roster_extra"] = sorted(new_names - old_names)
    for name in sorted(new_names):
        f = new / name
        R["seen"] += 1
        # ⚠ Codex R8-02: data 와 meta 를 따로 읽고 필드 존재만 보면, 다른 정상 시도가 data 만 게시한 중단 상태
        #   (data B / meta A) 가 "전부 갖췄다 · 전부 같다 · rc 0" 이 된다. 검증된 snapshot 만 검사한다.
        ok, why, data, meta = _unit(f)
        if ok is False:
            R["broken"].append(f"{f.name}: 묶음 불일치/미완 — {why}"); continue
        kind = _kind(f)
        j = rows = hdr = None
        if kind == "degeneracy":
            j = json.loads(data.decode("utf-8"))
            R["missing"] += [f"{f.name}: {k}" for k in JSON_KEYS if j.get(k) in (None, "")]
            R["content"] += [f"{f.name}: {p}" for p in S.check_degeneracy(j) if not p.startswith("키 없음")]
        else:
            rows, hdr = _csv_rows(data)
            R["missing"] += [f"{f.name}: {c}" for c in S.required_columns(kind) if c not in hdr]
            # ⚠ Codex R9-03: 열 이름 다음은 **값**이다 — 필수 셀 nonempty · 숫자 파싱 · receipt · 중복 key (schema-only 에서도)
            R["content"] += [f"{f.name}: {p}" for p in S.check_rows(kind, rows, hdr) if not p.startswith("열 없음")]
        if meta is None:
            R["missing"].append(f"{f.name}: .meta.json 없음")
        else:
            R["missing"] += [f"{f.name}.meta: {k}" for k in META_KEYS if meta.get(k) is None]
        if schema_only or old is None:
            continue
        o = baseline_for(f, old, policy, R["stale"])
        if o is None:
            continue                                            # roster_extra 가 이미 말한다
        R["paired"].append((f.name, o.name))
        ook, owhy, odata, ometa = _unit(o)
        if ook is False:
            R["diffs"].append((f"{o.name}", "정본 묶음 불일치/미완", owhy)); continue
        # ⚠ Codex R9-03 C: 실행 조건이 다르면 같은 실행의 재현이 아니다 — 숫자가 같아도 승격 대상이 아니다
        if meta and ometa:
            for k in META_CONTROLS:
                if k in meta and k in ometa and _num_diff(ometa[k], meta[k]):
                    R["controls"].append((f"{f.name}.meta:{k}", ometa[k], meta[k]))
        if kind == "degeneracy":
            a = json.loads(odata.decode("utf-8"))
            for k in S.DEGENERACY_CONTROLS:
                if k in a and k in j and _num_diff(a[k], j[k]):
                    R["controls"].append((f"{f.name}:{k}", a[k], j[k]))
            for k in JSON_NUM:
                if k not in a and k in j:                        # 정본에 없던 필드 = 스키마 추가분 (U14-02)
                    R["added"].append(f"{f.name}:{k}"); continue
                sub: list = []
                R["diffs"] += [(f"{f.name}:{k}{p and '.' + p}", x, y) for p, x, y in _num_diff(a.get(k), j.get(k), added=sub)]
                R["added"] += [f"{f.name}:{k}.{x}" for x in sub]
        else:
            # ⚠ Codex R8-05: dict comprehension 은 같은 key 의 앞 행을 **조용히** 지운다 — 변환 전에 유일성을 센다.
            #   reader(ne_shape)·checker 가 같은 typed validator 를 쓴다 (Codex R9-05: w_dqdv 는 숫자 key).
            key = S.matrix_key if kind == "matrix" else S.profile_key
            orows, _ = _csv_rows(odata)
            A, dupA, nA = S.unique_rows(orows, key)
            B, dupB, nB = S.unique_rows(rows, key)
            for side, dup in (("정본", dupA), ("새 산출", dupB)):
                for k in dup:
                    R["diffs"].append((f"{f.name}:{k}", f"{side}에 중복 key", "행을 셀 수 없다 (Codex R8-05)"))
            if nA != nB:
                R["diffs"].append((f"{f.name}", f"정본 행 {nA}", f"새 산출 행 {nB}"))
            for k in sorted(set(A) | set(B), key=str):
                if k not in A or k not in B:
                    R["diffs"].append((f"{f.name}:{k}", "정본에만" if k in A else "새 산출에만", "")); continue
                R["added"] += [f"{f.name}:{c}" for c in sorted(set(B[k]) - set(A[k]) - ROW_SKIP)]
                for c in sorted(set(A[k]) & set(B[k]) - ROW_SKIP):
                    R["diffs"] += [(f"{f.name}:{k}:{c}", x, y) for _, x, y in _num_diff(A[k][c], B[k][c])]
    R["added"] = sorted(set(R["added"])); R["stale"] = sorted(set(R["stale"]))
    return R


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
    ap.add_argument("--schema-only", action="store_true", help="숫자 대조 없이 스키마·내용(구조) 검사만")
    ap.add_argument("--subset", action="store_true",
                    help="명시적 **부분** 재실행 계약 (Codex R9-02): 정본 명부 중 일부만 새로 만들었다. 없는 항목을 실패로 세지 "
                         "않는 대신 범위(k/N)를 찍고, 결과는 승격 근거가 아니다")
    ap.add_argument("--max-show", type=int, default=20)
    ap.add_argument("--baseline-policy", choices=("auto", "current", "historical"), default="auto",
                    help="정본 선택 규칙 (Codex R7-04). auto = `--old-rev` 면 historical, 아니면 current. "
                         "옛 커밋의 out/ 을 **손으로 풀어** `--old` 로 줄 때는 historical 을 명시할 것 — 그 시절 "
                         "정본은 가장 높은 `_vN` 이다 (U14-02)")
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
    if old is not None and not old.is_dir():
        print(f"! 정본 디렉터리 {old} 가 없다"); return 2
    policy = a.baseline_policy if a.baseline_policy != "auto" else ("historical" if a.old_rev else "current")
    R = check(new, old, a.schema_only, policy)
    seen, missing, content, diffs = R["seen"], R["missing"], R["content"], R["diffs"]
    added, paired, stale, broken = R["added"], R["paired"], R["stale"], R["broken"]
    controls, r_missing, r_extra = R["controls"], R["roster_missing"], R["roster_extra"]
    print(f"산출 {seen} 개 점검 ({new})")
    if old is not None:
        print(f"  정본 선택 정책: **{policy}** — {POLICY[policy]}")
        print(f"  명부(roster): 정본 {R['n_old']} · 새 산출 {R['n_new']} · 대조 {len(paired)}"
              + (f" — **부분 계약(subset) {len(paired)}/{R['n_old']}**" if a.subset else ""))
    for n, o in paired:
        if n != o:
            print(f"  정본 선택: {n} ↔ **{o}** ({POLICY[policy].split('— ')[-1]})")
    if stale:
        print(f"  ! 정본 디렉터리에 판 번호가 붙은 형제 {len(stale)} 개 — 쓰지 않았다 (`out/archive/` 로 옮길 것): "
              + ", ".join(stale[:6]))
    if not seen:
        print("! 점검할 산출이 없다 — 경로가 맞나?"); return 2
    if r_missing and not a.subset:
        print(f"\n■ 명부(roster) 불일치 — 정본에 있는데 새 산출에 **없음** {len(r_missing)}/{R['n_old']} (Codex R9-02). 부분 "
              f"재실행이면 `--subset` 으로 계약을 명시할 것 — 그래도 승격 대상은 명부 전부({R['n_old']} 개)를 다시 만든 묶음뿐이다")
        for n in r_missing[:a.max_show]:
            print(f"  - {n}: 새 산출에 없음")
        if len(r_missing) > a.max_show:
            print(f"  … 외 {len(r_missing) - a.max_show}")
    elif r_missing:
        print(f"\n  부분 계약(subset): 정본 명부 {R['n_old']} 개 중 {len(paired)} 개만 대조 ({len(paired)}/{R['n_old']}) — "
              f"새 산출에 없음 {len(r_missing)}: {', '.join(r_missing[:a.max_show])}\n"
              f"  → 이 결과는 **부분** 진술이고 승격 근거가 아니다 (전부를 다시 만든 묶음만 정본을 대신한다)")
    if r_extra:
        print(f"\n■ 명부(roster) 불일치 — 새 산출에만 있음 {len(r_extra)} (정본에 없음): {', '.join(r_extra[:a.max_show])}")
    if broken:
        # ⚠ Codex R8-02: 묶음이 안 맞는 산출은 스키마도 숫자도 **대조하지 않는다** — 어느 쪽 bytes 인지 모른다
        print(f"\n■ 묶음 불일치/미완 {len(broken)} — data 와 meta 가 같은 시도의 것이 아니다 (다른 시도가 data 만 게시했거나 "
              f"게시가 중단됐다). 이 산출은 검사하지 않았다 → 게시를 끝내거나(meta) 다시 돌린 뒤 재검사")
        for b in broken[:a.max_show]:
            print(f"  - {b}")
    if missing:
        prov_only = [m for m in missing if m.rsplit(": ", 1)[-1] in PROVENANCE_COLS]
        rest = [m for m in missing if m not in prov_only]
        if rest:
            print(f"\n■ 새 스키마 누락 {len(rest)} — 옛 코드로 만든 산출이거나 묶음이 미완이다 (재실행이 이 트리에서 돌았는지 확인)")
            for m in rest[:a.max_show]:
                print(f"  - {m}")
            if len(rest) > a.max_show:
                print(f"  … 외 {len(rest) - a.max_show}")
        if prov_only:
            print(f"\n■ 기준/대상 입력 **출처 열** 누락 {len(prov_only)} — 이 산출은 **provenance-incomplete** 다 "
                  f"(R7-03·R8-04 스키마 이전 실행). 수치는 그대로 인용할 수 있으나 기준 입력의 출처는 그 묶음에서 회수되지 "
                  f"않는다; 실제 재실행(U18)으로 별도 위치에 만들어 비교·승격한다 — 현재 pathname 해시로 소급 채우지 않는다")
            for m in prov_only[:a.max_show]:
                print(f"  - {m}")
            if len(prov_only) > a.max_show:
                print(f"  … 외 {len(prov_only) - a.max_show}")
    if content:
        print(f"\n■ 내용 검사 실패 {len(content)} — 열은 있는데 값이 스키마가 아니다 (빈 필수 셀 · 숫자 아님 · receipt 의 역할/path/"
              f"64-hex/재계산 digest · 중복 key) (Codex R9-03)")
        for c in content[:a.max_show]:
            print(f"  - {c}")
        if len(content) > a.max_show:
            print(f"  … 외 {len(content) - a.max_show}")
    if not missing and not content:
        print("  새 스키마: 전부 갖췄다 (열·키 이름 + 필수 셀·숫자·receipt·중복 key — `bms_balancing/schema.py` 정본)")
    if controls:
        print(f"\n■ 실행 조건 불일치 {len(controls)} — 같은 실행의 재현이 아니다 (n_starts · seed · n_grid · n_samples · tol · "
              f"state · 소스; Codex R9-03). 숫자가 같아도 승격 대상이 아니다")
        for p, x, y in controls[:a.max_show]:
            print(f"  - {p}: 정본 {x} → 새 {y}")
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
        elif broken or r_extra or controls or (r_missing and not a.subset):
            print("  숫자: 대조 **미완** — 명부/묶음/조건 문제를 뺀 나머지만 같다 (전체를 말할 수 없다)")
        elif a.subset and r_missing:
            print(f"  숫자: 대조한 {len(paired)}/{R['n_old']} 개는 정본과 같다 — **부분(subset)** 진술, 승격 아님")
        else:
            print(f"  숫자: 정본({old})과 전부 같다 — 게시·서명만 바뀌었다")
    contract_broken = bool(missing or broken or content or controls or r_extra or (r_missing and not a.subset))
    return 2 if contract_broken else (1 if diffs else 0)


if __name__ == "__main__":
    sys.exit(main())
