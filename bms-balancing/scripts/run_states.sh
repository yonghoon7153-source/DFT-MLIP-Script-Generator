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
LAST_RUN_ID=""
write_meta () {  # write_meta <산출파일> <state> <src>   (LAST_RUN_ID 는 직전 run 이 준다)
  local art="$1" st="$2" src="$3" rid="${LAST_RUN_ID:-}"
  if [ -z "$rid" ] || ! grep -qF -- "$rid" "$art"; then
    say '   %s: run id (%s) 가 파일 안에 없다 — 이번 시도의 산출이 아니므로 meta 를 쓰지 않는다\n' "$art" "${rid:-없음}"
    return 1
  fi
  python3 - "$art" "$st" "$src" "$STARTS" "$SI" "${BMS_DATA_ROOT}" "$rid" "${OUT:-out}" <<'PYMETA'
import json, sys, datetime, pathlib
art, st, src, starts, si, root, rid, out_dir = sys.argv[1:9]
sys.path.insert(0, "scripts")
from provenance import git_provenance     # 코드 dirty 와 수정된 산출물을 분리 (R4-07); 산출물 자신은 제외
pv = git_provenance(artifact=art, output_roots=(out_dir, "out"))
pathlib.Path(art + ".meta.json").write_text(json.dumps({
    "artifact": pathlib.Path(art).name, "state": st, "half_cell_source": src,
    "si_source": si, "starts": int(starts), "seed": 0, "w_dqdv_note": "명령별",
    "data_root": root, "run_id": rid,
    "git_commit": pv["git_commit"], "git_dirty": pv["git_dirty"],
    "git_modified_outputs": pv["git_modified_outputs"], "git_modified_code": pv["git_modified_code"],
    "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PYMETA
}
mkdir -p "$OUT"

# ⚠ 진행 표시는 **전부 stderr 로**. degeneracy 는 JSON 을 stdout 으로만 내므로
#   stdout 에 한 줄이라도 찍으면 그 줄이 **JSON 안에 섞인다** (2026-09-10 실측:
#   첫 판이 그랬고, exit code 가 0 이라 스크립트는 "전부 통과" 라고 말했다).
say () { printf "$@" >&2; }

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
  if [ "$redir" = "-" ]; then
    BMS_RUN_ID="$rid" "$@" > "$log" 2>&1 || rc=1
  else
    BMS_RUN_ID="$rid" "$@" > "$redir" 2> "$log" || rc=1
  fi
  local bound=0
  [ -e "$art" ] && grep -qF -- "$rid" "$art" && bound=1
  if [ "$rc" -eq 0 ] && [ "$bound" -eq 1 ] && check_artifact "$art"; then
    say '   OK   (%d 초)  → %s  [run_id %s]\n' "$((SECONDS - t0))" "$art" "$rid"
    return 0
  fi
  if [ "$rc" -eq 0 ] && [ "$bound" -eq 0 ]; then
    say '   %s: 이번 시도의 run id 가 파일 안에 없다 (이전 산출이 남아 있거나 touch 만 됐다) — 새 결과로 세지 않는다\n' "$art"
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
  # 검사 대상은 **명령이 실제로 쓴 파일**(임시)이다. 최종 경로를 보게 두면
  # mv 전이라 늘 "없다" 가 나오고 mv 가 영영 안 된다 (2026-09-10 실측).
  tmp="$OUT/.degeneracy_${st}_${SI}.part"
  if run "degeneracy $st" "$tmp" "$tmp" "$OUT/degeneracy_${st}_${SI}.json.log" \
      env PYTHONUNBUFFERED=1 python3 -m bms_balancing.verify degeneracy \
        --state "$st" --si-source "$SI" --source "$SRC" --w-dqdv 0 \
        --tol 0.01 --starts "$STARTS" --seed 0 --grid 21 --samples 400; then
    mv "$tmp" "$OUT/degeneracy_${st}_${SI}.json"
    write_meta "$OUT/degeneracy_${st}_${SI}.json" "$st" "$SRC"
  else
    fail=$((fail+1)); rm -f "$tmp"
  fi

  run "matrix $st" "$OUT/matrix_${st}.csv" - "$OUT/matrix_${st}.csv.log" \
    env PYTHONUNBUFFERED=1 python3 -m bms_balancing.verify matrix \
      --state "$st" --starts "$STARTS" --seed 0 \
      --out "$OUT/matrix_${st}.csv" && write_meta "$OUT/matrix_${st}.csv" "$st" "$SRC" \
      || fail=$((fail+1))

  run "profile $st" "$OUT/profile_gamma_${st}_${SI}.csv" - \
      "$OUT/profile_gamma_${st}_${SI}.csv.log" \
    env PYTHONUNBUFFERED=1 python3 -m bms_balancing.verify profile \
      --state "$st" --si-source "$SI" --source "$SRC" --w-dqdv 0 \
      --starts "$STARTS" --seed 0 --grid 21 \
      --out "$OUT/profile_gamma_${st}_${SI}.csv" \
      && write_meta "$OUT/profile_gamma_${st}_${SI}.csv" "$st" "$SRC" \
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
