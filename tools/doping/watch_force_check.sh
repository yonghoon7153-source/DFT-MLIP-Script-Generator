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
fc_state() {   # $1 = scf.out 경로 [$2 = 정체 판정 분(기본 STALL_MIN)] → "상태|비고"
  local f="$1"
  [ -f "$f" ] || { echo "대기|scf.out 이 없다 — 아직 차례가 안 왔다"; return; }
  # ⚠ grep -a — pw.x 출력에 NUL 이 섞이면 grep 이 binary 로 보고 조용히 넘어간다
  if grep -aq "not enough slots\|There are not enough slots" "$f"; then
    echo "☠ 즉사|MPI 슬롯 부족 — 랭크를 물리코어 이하로 (NP=… 또는 --oversubscribe)"; return; fi
  # ⛔ 2026-09-08 실측 — 이 서명을 몰라서 **죽은 잡을 3시간 동안 '진행' 으로 보고했다.**
  #   QE-GPU 가 NVHPC 번들 Open MPI(hpcx)로 빌드됐는데 PATH 의 다른 mpirun 이 잡히면
  #   MPI 초기화에서 죽고 pw.x 는 한 줄도 못 찍는다 → 아래 어느 패턴에도 안 걸렸다.
  if grep -aq "MPI_Init_thread\|Local abort before MPI_INIT\|orte_init:startup\|MPI_ERRORS_ARE_FATAL" "$f"; then
    echo "☠ MPI초기화|빌드와 다른 mpirun 이 잡혔다 — NP=1 이면 mpirun 없이 직접 실행(러너가 자동)"; return; fi
  if grep -aq "mpirun detected that one or more processes exited with non-zero" "$f"; then
    echo "☠ 즉사|mpirun 이 비정상 종료를 보고했다 — scf.out 뒷부분을 직접 볼 것"; return; fi
  if grep -aq "Error in routine" "$f"; then
    echo "☠ 오류|$(grep -a -A1 'Error in routine' "$f" | tail -1 | tr -s ' ')"; return; fi
  if grep -aq "JOB DONE" "$f"; then
    if grep -aq "convergence has been achieved" "$f" && grep -aq "Forces acting on atoms" "$f"; then
      echo "✓ 완료|$(grep -a 'convergence has been achieved' "$f" | tail -1 | tr -s ' ')"
    else
      echo "⚠ 완료(불완전)|JOB DONE 인데 수렴 또는 힘 블록이 없다"; fi
    return; fi
  local it; it=$(grep -ac "^     iteration #" "$f" 2>/dev/null)
  # ⛔ 패턴 목록으로 죽음을 쫓는 것은 두더지잡기다. **일반 규칙**을 하나 둔다:
  #   반복이 0 인데 파일이 오래 안 변했으면 도는 게 아니라 죽은 것이다.
  #   (SCF 첫 반복은 초기화 몇 분 안에 찍힌다 — 그보다 오래 0 이면 시작을 못 한 것이다.)
  local lim=${2:-${STALL_MIN:-45}} age=999999
  age=$(( ( $(date +%s) - $(stat -c %Y "$f" 2>/dev/null || echo 0) ) / 60 ))
  if [ "${it:-0}" = 0 ] && [ "$age" -ge "$lim" ]; then
    echo "☠ 무진행|${age}분째 SCF 반복 0회 — 시작을 못 했다(도는 중 아님). scf.out 끝을 볼 것"; return; fi
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
  # ⛔음성: '옛 실패' 판정은 fc_state 가 아니라 호출부(mtime 비교)가 한다 —
  #   fc_state 자체는 옛/새를 모른다. 그 경계를 시험으로 못박는다.
  chk "fc_state 는 옛/새를 모른다 (그 구분은 호출부 몫)" \
      "$(fc_state "$t/a" | cut -d'|' -f1)" "☠ 즉사"
  # ⛔음성 (2026-09-08 실측 회귀): MPI 초기화 실패를 '진행' 으로 읽으면 안 된다.
  #   실제로 이걸 놓쳐 죽은 잡을 3시간 '진행' 으로 보고했다.
  printf 'Sorry! You were supposed to get help about:\n    orte_init:startup:internal-failure\n*** An error occurred in MPI_Init_thread\n*** on a NULL communicator\n' > "$t/f"
  chk "⛔음성: MPI 초기화 실패를 진행으로 읽지 않음" "$(fc_state "$t/f" | cut -d'|' -f1)" "☠ MPI초기화"
  printf 'mpirun detected that one or more processes exited with non-zero status\n' > "$t/g"
  chk "⛔음성: mpirun 비정상 종료를 잡는다" "$(fc_state "$t/g" | cut -d'|' -f1)" "☠ 즉사"
  # ⛔음성 (일반 규칙): 반복 0 + 정체 = 죽음. 패턴을 몰라도 잡혀야 한다.
  printf 'some unknown launcher noise we have never seen\n' > "$t/h"
  touch -d '3 hours ago' "$t/h"
  chk "⛔음성: 모르는 실패도 '반복0+정체' 로 잡힌다" "$(fc_state "$t/h" 45 | cut -d'|' -f1)" "☠ 무진행"
  # ⭕양성 경계: 방금 만들어진 반복 0 은 아직 '진행' 이다 (초기화 중일 수 있다)
  printf 'starting up\n' > "$t/i"
  chk "⭕양성: 갓 시작한 반복 0 은 진행" "$(fc_state "$t/i" 45 | cut -d'|' -f1)" "… 진행"
  # ⭕양성 경계: 반복이 찍히고 있으면 오래돼도 '진행' 이다 (정체 경고는 호출부가 낸다)
  printf '     iteration #  1\n' > "$t/j"; touch -d '3 hours ago' "$t/j"
  chk "⭕양성: 반복이 있으면 오래돼도 진행" "$(fc_state "$t/j" 45 | cut -d'|' -f1)" "… 진행"
  rm -rf "$t"; echo "  selftest: ⭕ $ok · ⛔ $bad"; [ "$bad" = 0 ] || exit 1; exit 0
fi

[ -d "$W" ] || { echo "⛔ 디렉터리가 없다: $W"; exit 2; }
MARK="$W/.fc_run_started"
echo "═══ 힘 대조 DFT 20점 · $(date '+%m-%d %H:%M') · $W"
[ -f "$MARK" ] && echo "    이번 실행 시작 $(date -r "$MARK" '+%m-%d %H:%M')"
printf "%-20s %-16s %s\n" "점" "상태" "비고"
tot=0; don=0; run=0; dead=0; wait_n=0
declare -A SUM CNT
for d in $(find "$W" -mindepth 1 -maxdepth 1 -type d | sort); do
  n=$(basename "$d"); tot=$((tot+1))
  IFS='|' read -r st note <<< "$(fc_state "$d/scf.out")"
  # 이번 실행보다 **오래된** 실패는 아직 차례가 안 온 점의 옛 출력이다 — 재시도 대상으로 표시한다.
  case "$st" in ☠*|"⚠ 완료(불완전)")
    if [ -f "$MARK" ] && [ -f "$d/scf.out" ] && [ "$d/scf.out" -ot "$MARK" ]; then
      st="↻ 옛 실패"; note="이전 배치의 출력 — 차례가 오면 덮어쓴다"
    fi ;;
  esac
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
    "↻ 옛 실패") wait_n=$((wait_n+1)) ;;
  esac
done
echo "───"
echo "완료 $don / $tot · 진행 $run · 문제 $dead" \
     "$( [ "$wait_n" -gt 0 ] && echo "· 재시도 대기 $wait_n (이전 배치 출력)" )"
for sys in "${!CNT[@]}"; do
  echo "  $sys 점당 평균 $(( SUM[$sys] / CNT[$sys] / 60 ))분 (${CNT[$sys]}점 기준)"
done
if [ "$dead" -gt 0 ]; then
  echo "⛔ 문제 점이 있다 — 카드 §8: 빠뜨린 채 판정하지 않는다. 고쳐서 같은 명령으로 이어 돌리면"
  echo "   끝난 점은 건너뛴다."
elif [ "$don" = "$tot" ] && [ "$tot" -gt 0 ]; then
  echo "★ 전부 완료 — 다음: --collect 로 회수 → force_contrast 로 판정"
fi
