#!/usr/bin/env bash
# =============================================================================
# watch_force_check.sh — 힘 대조 DFT 단일점 20점 감시
#
#   bash tools/doping/watch_force_check.sh [snapshot_dir]
#   watch -n 300 "bash ~/work/Yonghoon-DEM-DFT/tools/doping/watch_force_check.sh"
#   bash tools/doping/watch_force_check.sh --selftest
#
# ⛔ 이 도구가 **못 하는 것**
#   · 힘을 판정하지 않는다 — `mlip_committee.py force_contrast` 몫이고, 그 판정은
#     카드의 문턱을 읽어서 한다. 여기 찍히는 것은 **진행 상황**뿐이다.
#   · 수렴을 물리로 판정하지 않는다. pw.x 가 찍은 문자열만 읽는다.
#   · 남은 시간을 예측하지 않는다 — b2o3(128원자)와 modelc(62원자)의 점당 시간이
#     크게 달라 평균 하나로 외삽하면 틀린다. 계별 평균을 따로 찍는다.
#   · 죽은 점을 되살리지 않는다.
# =============================================================================
set -uo pipefail

W=${1:-$HOME/work/runs/force_check_700K}
STALL_MIN=${STALL_MIN:-45}

# ── 점 하나의 상태 (한 곳에만 둔다 — selftest 가 이 함수를 그대로 부른다) ────
fc_state() {   # $1 = scf.out 경로 → "상태|비고"
  local f="$1"
  [ -f "$f" ] || { echo "대기|scf.out 이 없다 — 아직 차례가 안 왔다"; return; }
  # ⚠ grep -a — pw.x 출력에 NUL 이 섞이면 grep 이 binary 로 보고 조용히 넘어간다
  if grep -aq "not enough slots\|There are not enough slots" "$f"; then
    echo "☠ 즉사|MPI 슬롯 부족 — 랭크를 물리코어 이하로 (NP=… 또는 --oversubscribe)"; return; fi
  if grep -aq "Error in routine" "$f"; then
    echo "☠ 오류|$(grep -a -A1 'Error in routine' "$f" | tail -1 | tr -s ' ')"; return; fi
  if grep -aq "JOB DONE" "$f"; then
    if grep -aq "convergence has been achieved" "$f" && grep -aq "Forces acting on atoms" "$f"; then
      echo "✓ 완료|$(grep -a 'convergence has been achieved' "$f" | tail -1 | tr -s ' ')"
    else
      echo "⚠ 완료(불완전)|JOB DONE 인데 수렴 또는 힘 블록이 없다"; fi
    return; fi
  local it; it=$(grep -ac "^     iteration #" "$f" 2>/dev/null)
  echo "… 진행|SCF 반복 ${it:-0}회"
}

if [ "${1:-}" = "--selftest" ]; then
  ok=0; bad=0
  t=$(mktemp -d); chk() { if [ "$2" = "$3" ]; then echo "  ⭕ $1"; ok=$((ok+1));
                          else echo "  ⛔ $1 — 얻음 '$2' 기대 '$3'"; bad=$((bad+1)); fi; }
  chk "없는 파일은 대기" "$(fc_state "$t/nope" | cut -d'|' -f1)" "대기"
  printf 'There are not enough slots available\n' > "$t/a"
  chk "MPI 슬롯 부족을 즉사로" "$(fc_state "$t/a" | cut -d'|' -f1)" "☠ 즉사"
  printf '     iteration #  1\n     iteration #  2\n' > "$t/b"
  chk "진행 중" "$(fc_state "$t/b" | cut -d'|' -f1)" "… 진행"
  printf 'convergence has been achieved in 9 iterations\nForces acting on atoms\nJOB DONE.\n' > "$t/c"
  chk "완료" "$(fc_state "$t/c" | cut -d'|' -f1)" "✓ 완료"
  # ⛔음성: JOB DONE 만 있고 수렴·힘이 없으면 완료로 세면 안 된다
  printf 'JOB DONE.\n' > "$t/d"
  chk "⛔음성: JOB DONE 만으로 완료 아님" "$(fc_state "$t/d" | cut -d'|' -f1)" "⚠ 완료(불완전)"
  printf 'Error in routine electrons (1):\n     charge is wrong\n' > "$t/e"
  chk "⛔음성: pw.x 오류를 진행으로 읽지 않음" "$(fc_state "$t/e" | cut -d'|' -f1)" "☠ 오류"
  rm -rf "$t"; echo "  selftest: ⭕ $ok · ⛔ $bad"; [ "$bad" = 0 ] || exit 1; exit 0
fi

[ -d "$W" ] || { echo "⛔ 디렉터리가 없다: $W"; exit 2; }
echo "═══ 힘 대조 DFT 20점 · $(date '+%m-%d %H:%M') · $W"
printf "%-20s %-16s %s\n" "점" "상태" "비고"
tot=0; don=0; run=0; dead=0
declare -A SUM CNT
for d in $(find "$W" -mindepth 1 -maxdepth 1 -type d | sort); do
  n=$(basename "$d"); tot=$((tot+1))
  IFS='|' read -r st note <<< "$(fc_state "$d/scf.out")"
  printf "%-20s %-16s %s\n" "$n" "$st" "${note:0:52}"
  case "$st" in
    "✓ 완료") don=$((don+1))
      # 계별 평균 소요 — mtime 차이로 잰다 (로그가 없어도 된다)
      if [ -f "$d/scf.in" ] && [ -f "$d/scf.out" ]; then
        sec=$(( $(stat -c %Y "$d/scf.out") - $(stat -c %Y "$d/scf.in") ))
        sys=${n%%_*}; SUM[$sys]=$(( ${SUM[$sys]:-0} + sec )); CNT[$sys]=$(( ${CNT[$sys]:-0} + 1 ))
      fi ;;
    "… 진행") run=$((run+1))
      age=$(( ($(date +%s) - $(stat -c %Y "$d/scf.out")) / 60 ))
      [ "$age" -ge "$STALL_MIN" ] && echo "    ⚠ ${age}분째 출력 없음 (STALL_MIN=$STALL_MIN)" ;;
    ☠*|"⚠ 완료(불완전)") dead=$((dead+1)) ;;
  esac
done
echo "───"
echo "완료 $don / $tot · 진행 $run · 문제 $dead"
for sys in "${!CNT[@]}"; do
  echo "  $sys 점당 평균 $(( SUM[$sys] / CNT[$sys] / 60 ))분 (${CNT[$sys]}점 기준)"
done
if [ "$dead" -gt 0 ]; then
  echo "⛔ 문제 점이 있다 — 카드 §8: 빠뜨린 채 판정하지 않는다. 고쳐서 같은 명령으로 이어 돌리면"
  echo "   끝난 점은 건너뛴다."
elif [ "$don" = "$tot" ] && [ "$tot" -gt 0 ]; then
  echo "★ 전부 완료 — 다음: --collect 로 회수 → force_contrast 로 판정"
fi
