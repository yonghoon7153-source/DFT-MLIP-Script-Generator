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
SRC="${SRC:-GITT}"
mkdir -p out

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
run () {
  local label="$1" art="$2" redir="$3" log="$4"; shift 4
  say '\n\033[1m== %s\033[0m\n' "$label"
  local t0=$SECONDS rc=0
  if [ "$redir" = "-" ]; then
    "$@" > "$log" 2>&1 || rc=1
  else
    "$@" > "$redir" 2> "$log" || rc=1
  fi
  if [ "$rc" -eq 0 ] && check_artifact "$art"; then
    say '   OK   (%d 초)  → %s\n' "$((SECONDS - t0))" "$art"
    return 0
  fi
  say '   \033[31mFAIL\033[0m (%d 초) — 로그: %s\n' "$((SECONDS - t0))" "$log"
  return 1
}

fail=0
for st in $STATES; do
  # 검사 대상은 **명령이 실제로 쓴 파일**(임시)이다. 최종 경로를 보게 두면
  # mv 전이라 늘 "없다" 가 나오고 mv 가 영영 안 된다 (2026-09-10 실측).
  tmp="out/.degeneracy_${st}_${SI}.part"
  if run "degeneracy $st" "$tmp" "$tmp" "out/degeneracy_${st}_${SI}.json.log" \
      env PYTHONUNBUFFERED=1 python3 -m bms_balancing.verify degeneracy \
        --state "$st" --si-source "$SI" --source "$SRC" --w-dqdv 0 \
        --tol 0.01 --starts "$STARTS" --seed 0 --grid 21 --samples 400; then
    mv "$tmp" "out/degeneracy_${st}_${SI}.json"
  else
    fail=$((fail+1)); rm -f "$tmp"
  fi

  run "matrix $st" "out/matrix_${st}.csv" - "out/matrix_${st}.csv.log" \
    env PYTHONUNBUFFERED=1 python3 -m bms_balancing.verify matrix \
      --state "$st" --starts "$STARTS" --seed 0 \
      --out "out/matrix_${st}.csv" || fail=$((fail+1))

  run "profile $st" "out/profile_gamma_${st}_${SI}.csv" - \
      "out/profile_gamma_${st}_${SI}.csv.log" \
    env PYTHONUNBUFFERED=1 python3 -m bms_balancing.verify profile \
      --state "$st" --si-source "$SI" --source "$SRC" --w-dqdv 0 \
      --starts "$STARTS" --seed 0 --grid 21 \
      --out "out/profile_gamma_${st}_${SI}.csv" || fail=$((fail+1))
done

say '\n=====================================\n'
if [ "$fail" -eq 0 ]; then
  say '전부 통과 — 산출 %d개, 전부 열어서 읽히는 것을 확인했다\n' \
      "$((3 * $(echo $STATES | wc -w)))"
else
  say '실패 %d 건 — 위의 .log 를 볼 것\n' "$fail"
fi
say "설정: STATES='%s' STARTS=%s SI=%s SRC=%s\n" "$STATES" "$STARTS" "$SI" "$SRC"
exit $((fail > 0))
