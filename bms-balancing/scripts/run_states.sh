#!/usr/bin/env bash
# 다른 상태 일반화 — `300_0009` 에서 한 것을 100 · 200 · 300_0147 에도 그대로.
#
# 왜 스크립트로 두나: 아홉 번의 실행이 **같은 설정**이어야 비교가 성립한다.
# 손으로 아홉 줄을 치면 한 줄에서 `--starts` 를 흘리는 순간 그 행만 다른
# 조건이 되고, 나중에 그것을 알아챌 방법이 없다. 여기 적힌 플래그가
# 산출의 provenance 다.
#
#   export BMS_DATA_ROOT='/mnt/d/…/degradation mode'
#   ./scripts/run_states.sh                    # 세 상태 전부
#   STATES=100 ./scripts/run_states.sh         # 하나만
#   STARTS=6 STATES=100 ./scripts/run_states.sh   # 배관 확인용 (수치는 못 씀)
#
# 산출은 전부 `out/` 에. 원자료는 하나도 안 들어간다 — 파라미터와 요약뿐이다.

set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE" || exit 1
: "${BMS_DATA_ROOT:?BMS_DATA_ROOT 를 먼저 export 하라}"

STATES="${STATES:-100 200 300_0147}"
STARTS="${STARTS:-24}"
SI="${SI:-Li}"
# SRC 를 주면 그 소스로 **고정**한다 (없으면 그 상태는 건너뛴다).
# 안 주면 상태마다 GITT -> step_005C 순으로 있는 것을 고른다 (pick_src).
FORCE_SRC="${SRC:-}"
USED=""            # 상태별로 실제 무엇을 썼는지 — 마지막에 찍는다
OUT="${OUT:-out}"  # 산출 디렉터리. 시험 실행은 여기를 바꿔서 out/ 을 안 더럽힌다

# ⚠ 산출마다 **설정을 옆에 적는다** (`.meta.json`). 2026-09-10 실측: 합성
#   데이터로 STARTS=4 짜리 시험을 돌렸더니 `out/matrix_300_0147.csv` 가
#   생겼는데, **파일 이름만으로는 진짜 산출과 구별이 안 됐다.** 정본이
#   artifact 인 저장소에서 그건 치명적이다. 무엇으로 만든 값인지가 파일에
#   붙어 있어야 한다.
# ⚠ Codex R4-06: meta 는 **이번 시도**의 산출에만 붙는다. `run` 이 만든 run id(`LAST_RUN_ID`)가 파일
#   안에 있어야 하고, 없으면 meta 를 쓰지 않는다 — 시각이 아니라 id 가 계산과 게시 bytes 를 잇는다.
# ⚠ Codex R4-07: git_dirty 는 **코드**(산출 디렉터리 밖 추적 파일)만 본다. 산출 디렉터리 안에서 수정된
#   다른 추적 파일은 `git_modified_outputs` 로 따로 적는다 (입력으로 쓰는 artifact 의 변경을 숨기지 않게).
# ⚠ Codex R5-04: 산출 게시와 meta 게시가 한 시도의 **한 묶음**이어야 한다. run id 검사 뒤 meta 를 쓰기 전에 다른
#   시도가 산출을 바꾸면 "CSV 는 B, meta 는 A" 가 남았다. 이제 meta 작성자는 `<산출>.lock`(verify.py 의
#   게시가 잡는 것과 같은 flock) 안에서 id 를 **필드로 다시** 확인하고, 그 순간의 bytes 해시를 meta 에 적는다.
#   실패하면 meta 를 쓰지 않는다 — 마지막 실행의 온전한 묶음만 남는다.
# ⚠ Codex R5-08: id 검사는 grep(파일 어디든 문자열)이 아니라 CSV 의 `run_id` 열 전 행 / JSON 의 `run_id` 필드다.
LAST_RUN_ID=""
write_meta () {  # write_meta <산출파일> <state> <src>   (LAST_RUN_ID 는 직전 run 이 준다)
  local art="$1" st="$2" src="$3" rid="${LAST_RUN_ID:-}"
  if [ -z "$rid" ] || ! check_run_id "$art" "$rid"; then
    say '   %s: run id (%s) 가 산출물의 필드에 없다 — 이번 시도의 산출이 아니므로 meta 를 쓰지 않는다\n' "$art" "${rid:-없음}"
    return 1
  fi
  if ! python3 - "$art" "$st" "$src" "$STARTS" "$SI" "${BMS_DATA_ROOT}" "$rid" "${OUT:-out}" \
        "${LAST_PRE_PV:-{\}}" "${LAST_STARTED_UTC:-}" <<'PYMETA'
import fcntl, json, os, sys, datetime, pathlib, tempfile
art, st, src, starts, si, root, rid, out_dir, pre_json, started = sys.argv[1:11]
try:
    pre = json.loads(pre_json) if pre_json else {}
except json.JSONDecodeError:
    pre = {}
sys.path.insert(0, "scripts")
from provenance import git_provenance, check_run_id, sha256_file   # R4-07 · R5-08 · R5-04
with open(art + ".lock", "a+") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)                                  # verify.py 의 게시와 같은 잠금
    ok, why = check_run_id(art, rid)
    if not ok:
        print(f"run id 재확인 실패: {why}", file=sys.stderr); sys.exit(1)
    pv = git_provenance(artifact=art, output_roots=(out_dir, "out"))
    meta = {
        "artifact": pathlib.Path(art).name, "state": st, "half_cell_source": src,
        "si_source": si, "starts": int(starts), "seed": 0, "w_dqdv_note": "명령별",
        "data_root": root, "run_id": rid, "sha256": sha256_file(art),
        "git_commit": pv["git_commit"], "git_dirty": pv["git_dirty"],
        "git_modified_outputs": pv["git_modified_outputs"], "git_modified_code": pv["git_modified_code"],
        # R6 내부 F04: 계산 **전** 상태도 적고 둘이 다르면 표시한다 — 뒤에서 한 번 샘플한 값은 "돌린 코드가
        #   commit 과 같았나" 에 거짓 답을 줄 수 있다 (실행 중 checkout/커밋).
        "git_commit_at_start": pre.get("git_commit"), "git_dirty_at_start": pre.get("git_dirty"),
        "git_modified_code_at_start": pre.get("git_modified_code"),
        "git_state_changed_during_run": bool(pre) and (
            pre.get("git_commit") != pv["git_commit"] or pre.get("git_dirty") != pv["git_dirty"]
            or pre.get("git_modified_code") != pv["git_modified_code"]),
        "started_utc": started or None,
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(art)), prefix=os.path.basename(art) + ".meta.", suffix=".part")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    os.replace(tmp, art + ".meta.json")
PYMETA
  then
    say '   %s: 잠금 안 재확인에서 이번 시도의 산출이 아니었다 (다른 시도가 게시함) — meta 를 쓰지 않는다\n' "$art"
    return 1
  fi
}
# R6 내부 F05a·F05b: 게시 뒤 묶음 검사는 **이 시도의 id** 로 하고, 실패 이유는 버리지 않고 말한다
verify_unit_or_say () {  # verify_unit_or_say <산출파일> <run id>
  local why
  if why="$(python3 scripts/provenance.py --verify-unit "$1" "$2" 2>&1)"; then return 0; fi
  say '   %s: 묶음 검사 실패 — %s\n' "$1" "$why"
  return 1
}
mkdir -p "$OUT"

# ⚠ 진행 표시는 **전부 stderr 로**. degeneracy 는 전 판에 JSON 을 stdout 으로 냈고
#   stdout 에 한 줄이라도 찍으면 그 줄이 **JSON 안에 섞였다** (2026-09-10 실측:
#   첫 판이 그랬고, exit code 가 0 이라 스크립트는 "전부 통과" 라고 말했다).
#   R6 내부 F01 부터 degeneracy 도 `--out` 으로 잠금 안 원자적 게시 — stdout 은 로그다.
say () { printf "$@" >&2; }

# R5-08: run id 는 산출물의 **필드**로 확인한다 (CSV 의 run_id 열 전 행 / JSON 의 run_id) — grep 은 다른 칸의 문자열도 통과시켰다
check_run_id () {  # check_run_id <산출파일> <run id>
  python3 scripts/provenance.py --check-run-id "$1" "$2" >/dev/null 2>&1
}

# 종료 코드는 산출이 쓸 만한지 말해 주지 않는다. 실제로 열어서 읽는다.
check_artifact () {
  local f="$1"
  [ -s "$f" ] || { say '   %s: 파일이 비었다\n' "$f"; return 1; }
  case "$f" in
    *.json|*.part)
      python3 -c 'import json,sys
d = json.load(open(sys.argv[1]))
sys.exit(0 if isinstance(d, dict) and d else 1)' "$f" 2>/dev/null \
        || { say '   %s: JSON 이 아니다 (stdout 오염?)\n' "$f"; return 1; } ;;
    *.csv)
      python3 -c 'import csv,sys
r = list(csv.DictReader(open(sys.argv[1])))
sys.exit(0 if r and r[0] else 1)' "$f" 2>/dev/null \
        || { say '   %s: CSV 에 행이 없다\n' "$f"; return 1; } ;;
  esac
  return 0
}

# run <라벨> <검사할 산출> <stdout 받을 파일 | -> <로그> <명령...>
#   리다이렉트를 **호출부가 아니라 여기서** 건다. 호출부에서 걸면 say 의
#   stderr 까지 로그로 빨려 들어가 화면에 진행이 안 보인다.
#
# ⚠ 2026-09-11 Codex R3-08: 전 판은 rc 0 + '비어 있지 않은 파일' 만 봤다. profile 이 전부
#   실패해 아무것도 안 쓰면 **이전 실행의 CSV** 가 그 검사를 통과해 "OK" 가 찍히고
#   `write_meta` 가 옛 파일에 새 provenance 를 붙였다.
# ⚠ Codex R4-06 · Q4: 그 다음 판의 시각 도장(`find -newer`)은 옛 파일을 `touch` 만 해도 통과시켰다 —
#   시각은 시도와 계산 bytes 를 잇는 증거가 아니다. 이제 `run` 이 시도마다 run id 를 만들어 명령에
#   `BMS_RUN_ID` 로 주고(verify.py 의 세 명령이 산출물 안에 박는다), 게시된 파일이 **그 id 를 담고
#   있어야** OK 다. 옛 파일은 지우지 않는다 — 보존은 하되 새 결과로 세지 않는다.
run () {
  local label="$1" art="$2" redir="$3" log="$4"; shift 4
  say '\n\033[1m== %s\033[0m\n' "$label"
  local t0=$SECONDS rc=0
  local rid; rid="$(python3 -c 'import uuid; print(uuid.uuid4().hex)')"
  LAST_RUN_ID="$rid"                                # write_meta 가 같은 id 를 확인·기록한다
  # R6 내부 F04: 명령 **전** 의 git 상태·시작 시각 — write_meta 가 계산 뒤 상태와 비교한다
  LAST_PRE_PV="$(python3 scripts/provenance.py "$art" 2>/dev/null || echo '{}')"
  LAST_STARTED_UTC="$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).isoformat())')"
  if [ "$redir" = "-" ]; then
    BMS_RUN_ID="$rid" "$@" > "$log" 2>&1 || rc=1
  else
    BMS_RUN_ID="$rid" "$@" > "$redir" 2> "$log" || rc=1
  fi
  local bound=0
  [ -e "$art" ] && check_run_id "$art" "$rid" && bound=1     # R5-08: 필드로 확인 (grep 아님)
  if [ "$rc" -eq 0 ] && [ "$bound" -eq 1 ] && check_artifact "$art"; then
    say '   OK   (%d 초)  → %s  [run_id %s]\n' "$((SECONDS - t0))" "$art" "$rid"
    return 0
  fi
  if [ "$rc" -eq 0 ] && [ "$bound" -eq 0 ]; then
    say '   %s: 이번 시도의 run id 가 산출물의 run_id 필드에 없다 (이전 산출이 남아 있거나 touch 만 됐다) — 새 결과로 세지 않는다\n' "$art"
  fi
  say '   \033[31mFAIL\033[0m (%d 초) — 로그: %s\n' "$((SECONDS - t0))" "$log"
  return 1
}

fail=0
# 상태마다 반쪽전지 소스를 고른다. `GITT` 에 그 상태 파일이 없으면
# `step_005C` 로 넘어간다 — 2026-09-10 실측: `300_0147` 이 GITT 에만 없어서
# degeneracy 가 죽었다 (`dd_verify('check')` 의 "상태 파일 4/5" 가 이것이다).
# ⚠ 소스가 섞이면 **행끼리 비교하면 안 된다.** 그래서 무엇을 썼는지 찍는다.
pick_src () {
  local st="$1"
  if [ -n "$FORCE_SRC" ]; then
    case "$FORCE_SRC" in
      GITT)      [ -f "$BMS_DATA_ROOT/data/half_cell/GITT/${st}.xlsx" ] && echo GITT ;;
      step_005C) [ -f "$BMS_DATA_ROOT/data/half_cell/step_005C/${st}_005C.xlsx" ] \
                   && echo step_005C ;;
    esac
    return
  fi
  if [ -f "$BMS_DATA_ROOT/data/half_cell/GITT/${st}.xlsx" ]; then echo GITT
  elif [ -f "$BMS_DATA_ROOT/data/half_cell/step_005C/${st}_005C.xlsx" ]; then echo step_005C
  else echo ""; fi
}

for st in $STATES; do
  SRC="$(pick_src "$st")"
  if [ -z "$SRC" ]; then
    say '\n\033[31m== %s 건너뜀\033[0m — 어느 소스에도 반쪽전지가 없다\n' "$st"
    fail=$((fail+1)); continue
  fi
  USED="$USED $st=$SRC"
  say '\n\033[1m-- %s : 반쪽전지 소스 %s --\033[0m\n' "$st" "$SRC"
  # R6 내부 F01: 전 판은 stdout 을 고정 이름 `.part` 로 받아 shell 이 `flock mv` 했다 — producer 의 stdout fd 가
  #   rename 을 넘어 살아남아, 빠른 다른 시도가 게시·meta·검사를 끝낸 뒤 느린 시도가 게시된 inode 에 잠금 밖에서
  #   썼다 (JSON=B, meta=A, 두 wrapper 는 "통과"). 이제 matrix·profile 과 같이 `--out` 으로 잠금 안 원자적 게시.
  run "degeneracy $st" "$OUT/degeneracy_${st}_${SI}.json" - "$OUT/degeneracy_${st}_${SI}.json.log" \
    env PYTHONUNBUFFERED=1 python3 -m bms_balancing.verify degeneracy \
      --state "$st" --si-source "$SI" --source "$SRC" --w-dqdv 0 \
      --tol 0.01 --starts "$STARTS" --seed 0 --grid 21 --samples 400 \
      --out "$OUT/degeneracy_${st}_${SI}.json" \
      && write_meta "$OUT/degeneracy_${st}_${SI}.json" "$st" "$SRC" \
      && verify_unit_or_say "$OUT/degeneracy_${st}_${SI}.json" "$LAST_RUN_ID" \
      || fail=$((fail+1))

  run "matrix $st" "$OUT/matrix_${st}.csv" - "$OUT/matrix_${st}.csv.log" \
    env PYTHONUNBUFFERED=1 python3 -m bms_balancing.verify matrix \
      --state "$st" --starts "$STARTS" --seed 0 \
      --out "$OUT/matrix_${st}.csv" && write_meta "$OUT/matrix_${st}.csv" "$st" "$SRC" \
      && verify_unit_or_say "$OUT/matrix_${st}.csv" "$LAST_RUN_ID" \
      || fail=$((fail+1))

  run "profile $st" "$OUT/profile_gamma_${st}_${SI}.csv" - \
      "$OUT/profile_gamma_${st}_${SI}.csv.log" \
    env PYTHONUNBUFFERED=1 python3 -m bms_balancing.verify profile \
      --state "$st" --si-source "$SI" --source "$SRC" --w-dqdv 0 \
      --starts "$STARTS" --seed 0 --grid 21 \
      --out "$OUT/profile_gamma_${st}_${SI}.csv" \
      && write_meta "$OUT/profile_gamma_${st}_${SI}.csv" "$st" "$SRC" \
      && verify_unit_or_say "$OUT/profile_gamma_${st}_${SI}.csv" "$LAST_RUN_ID" \
      || fail=$((fail+1))
done

say '\n=====================================\n'
if [ "$fail" -eq 0 ]; then
  say '전부 통과 — 산출 %d개, 전부 열어서 읽히는 것을 확인했다\n' \
      "$((3 * $(echo $STATES | wc -w)))"
else
  say '실패 %d 건 — 위의 .log 를 볼 것\n' "$fail"
fi
say "설정: STATES='%s' STARTS=%s SI=%s\n" "$STATES" "$STARTS" "$SI"
say "반쪽전지 소스:%s\n" "$USED"
say "⚠ 소스가 섞였으면 그 상태끼리는 직접 비교하지 말 것 (축이 다르다)\n"
exit $((fail > 0))
