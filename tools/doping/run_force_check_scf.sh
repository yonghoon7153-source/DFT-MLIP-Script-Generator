#!/usr/bin/env bash
# =============================================================================
# run_force_check_scf.sh — 힘 대조 카드 §4 의 DFT 단일점 20점을 순서대로 돌린다.
#
#   카드: db/properties/b2o3_uma_vs_dft_force_prereg_2026_09_08.json (ratified 2판)
#   입력: generate_dft_inputs.py --from_traj 가 만든 <OUT>/<label>_<seed>_t<NN>ps/scf.in
#
# 실행 (kgy):
#   bash tools/doping/run_force_check_scf.sh $HOME/work/runs/force_check_700K
#   DRY_RUN=1 bash tools/doping/run_force_check_scf.sh <dir>     # 점검만, 계산 안 함
#   NP=8 bash tools/doping/run_force_check_scf.sh <dir>          # 랭크 수 지정
#
# ⛔ 이 스크립트가 **못 하는 것**
#   · 수렴을 보장하지 않는다 — 실패한 점을 세어 보고할 뿐이고, 실패를 **대체하지 않는다**
#     (카드 §8: 20점 중 하나라도 실패한 채 19점으로 판정하지 않는다).
#   · 힘의 물리적 타당성을 보지 않는다. pw.x 가 냈다는 사실만 확인한다.
#   · UMA 힘을 계산하지 않는다 (같은 frame.xyz 로 따로 돈다).
#   · 병렬로 여러 점을 돌리지 않는다 — CPU 빌드 16코어를 한 점에 다 준다.
#     (동시에 돌리면 코어를 나눠 갖게 되고, 총 시간은 그대로인데 개별 실패 진단만 어려워진다.)
# =============================================================================
set -u
ROOT=${1:-}
[ -n "$ROOT" ] || { echo "usage: $0 <스냅샷 디렉터리> [NP=16]"; exit 2; }
[ -d "$ROOT" ] || { echo "⛔ 디렉터리가 없다: $ROOT"; exit 2; }
# ⚠ 랭크 수 기본값 = **물리코어**. `nproc` 은 하이퍼스레드를 포함하는데 Open MPI 는
#   기본적으로 물리코어만 슬롯으로 세어, nproc 을 그대로 주면 "not enough slots" 로
#   **전 점이 0분 만에 즉사**한다 (2026-09-08 실측: 16 요청 → 20/20 실패).
#   QE 는 하이퍼스레드에서 거의 안 빨라지므로 물리코어가 성능 면에서도 맞다.
_phys_cores() {
  if command -v lscpu >/dev/null 2>&1; then
    local n; n=$(lscpu -p=Core,Socket 2>/dev/null | grep -v '^#' | sort -u | wc -l)
    [ "${n:-0}" -gt 0 ] && { echo "$n"; return; }
  fi
  getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1
}
NP=${NP:-$(_phys_cores)}
PWX=${PWX:-$HOME/apps/qe-7.4.1-cpu/bin/pw.x}
DRY_RUN=${DRY_RUN:-0}

ts() { date '+%m-%d %H:%M:%S'; }

# ── 중복 실행 가드 (CLAUDE.md 공통 관례 · pgrep 이 아니라 flock) ──────────────
#   pgrep 로 세면 래퍼(sh -c … | tee)까지 세어 시작하자마자 죽는 사고가 있었다.
LOCK=${LOCK:-/tmp/force_check_scf.lock}
exec 9>"$LOCK" || { echo "⛔ 락 파일을 못 연다: $LOCK"; exit 1; }
if command -v flock >/dev/null 2>&1; then
  flock -n 9 || { echo "[$(ts)] 이미 도는 인스턴스가 있다 (flock $LOCK) — 중단"; exit 0; }
fi

# ── 사전점검: 있어야 하는 것이 다 있나 (없으면 **시작하지 않는다**) ──────────
[ -x "$PWX" ] || { echo "⛔ pw.x 를 못 찾는다: $PWX  (PWX=... 로 지정)"; exit 2; }
MPI=""
# Open MPI 면 --oversubscribe 를 붙인다 (슬롯 계산이 빡빡한 빌드에서 즉사 방지 · gabia 관례).
_OS=""
if command -v mpirun >/dev/null 2>&1; then
  mpirun --version 2>&1 | grep -qi "open mpi" && _OS="--oversubscribe"
  MPI="mpirun $_OS -np $NP"
elif command -v mpiexec >/dev/null 2>&1; then MPI="mpiexec -n $NP"
else echo "[$(ts)] ⚠ mpirun/mpiexec 없음 — 직렬로 돈다 (느리다)"; NP=1; fi
echo "[$(ts)] 코어: 물리 $(_phys_cores) · 논리 $(getconf _NPROCESSORS_ONLN 2>/dev/null) → 랭크 $NP

mapfile -t INS < <(find "$ROOT" -mindepth 2 -maxdepth 2 -name scf.in | sort)
[ "${#INS[@]}" -gt 0 ] || { echo "⛔ scf.in 이 없다: $ROOT/*/scf.in"; exit 2; }

# 유사포텐셜이 실제로 있나 — scf.in 이 가리키는 경로를 그대로 확인한다
PSD=$(grep -a -m1 "pseudo_dir" "${INS[0]}" | sed "s/.*=\s*'\([^']*\)'.*/\1/")
MISS=0
# ⚠ ATOMIC_SPECIES 블록은 **다음 카드 키워드까지**만 읽는다. -A20 으로 훑으면
#   CELL_PARAMETERS 의 좌표 3열까지 유사포텐셜 이름으로 읽는다 (자체시험에서 잡힌 사고).
for f in $(awk 'FNR==1{c=0}
                /^ATOMIC_SPECIES/{c=1; next}
                /^(CELL_PARAMETERS|ATOMIC_POSITIONS|K_POINTS|OCCUPATIONS|CONSTRAINTS|ATOMIC_VELOCITIES|ATOMIC_FORCES)/{c=0}
                c && NF==3 {print $3}' "${INS[@]}" | sort -u); do
  [ -f "$PSD/$f" ] || { echo "⛔ 유사포텐셜 없음: $PSD/$f"; MISS=1; }
done
[ "$MISS" = 0 ] || { echo "⛔ 유사포텐셜이 빠졌다 — 시작하지 않는다"; exit 2; }

echo "[$(ts)] 점 ${#INS[@]}개 · $MPI · pw.x=$PWX · pseudo=$PSD"
if [ "$DRY_RUN" = 1 ]; then
  for i in "${INS[@]}"; do
    d=$(dirname "$i")
    st="대기"
    grep -aq "JOB DONE" "$d/scf.out" 2>/dev/null && st="완료(건너뜀)"
    printf "  %-28s %s\n" "$(basename "$d")" "$st"
  done
  echo "[$(ts)] DRY_RUN — 계산은 하지 않았다"; exit 0
fi

done_n=0; skip_n=0; fail_n=0; t0=$(date +%s)
for i in "${INS[@]}"; do
  d=$(dirname "$i"); n=$(basename "$d")
  # 재개: 이미 끝난 점은 다시 돌지 않는다 (JOB DONE 이 있어야 완료로 센다)
  if grep -aq "JOB DONE" "$d/scf.out" 2>/dev/null; then
    echo "[$(ts)] skip $n (JOB DONE)"; skip_n=$((skip_n+1)); continue
  fi
  s=$(date +%s)
  ( cd "$d" && $MPI "$PWX" -in scf.in > scf.out 2>&1 )
  e=$(date +%s)
  # ⚠ grep -a — 출력에 NUL 이 섞이면 grep 이 binary 로 보고 조용히 넘어간다
  if grep -aq "JOB DONE" "$d/scf.out" && grep -aq "convergence has been achieved" "$d/scf.out" \
     && grep -aq "Forces acting on atoms" "$d/scf.out"; then
    echo "[$(ts)] ✓ $n  $(( (e-s)/60 ))분"; done_n=$((done_n+1))
  else
    echo "[$(ts)] ⛔ $n  실패 — $d/scf.out 마지막 줄:"
    tail -3 "$d/scf.out" | sed 's/^/       /'
    fail_n=$((fail_n+1))
    # ⚠ 첫 점이 **1분 안에** 죽으면 환경 문제다 (MPI 슬롯·유사포텐셜·바이너리).
    #   같은 실패를 20번 반복해 로그만 채우지 않는다 — 실측 2026-09-08 (20/20 즉사).
    if [ "$done_n" = 0 ] && [ $((e-s)) -lt 60 ]; then
      echo "[$(ts)] ⛔ 첫 점이 $((e-s))초 만에 죽었다 — 환경 문제로 보고 **중단**한다."
      echo "   나머지 $(( ${#INS[@]} - fail_n )) 점은 던지지 않았다. 위 메시지를 먼저 고쳐라."
      break
    fi
  fi
done

echo "[$(ts)] 끝 — 완료 $done_n · 건너뜀 $skip_n · 실패 $fail_n · 총 $(( ($(date +%s)-t0)/60 ))분"
if [ "$fail_n" -gt 0 ]; then
  echo "⛔ 실패한 점이 있다. 카드 §8 무효 조건: **19점으로 판정하지 않는다** —"
  echo "   그 점을 다시 돌리거나, 규칙에 미리 적은 대체(실패 프레임의 +1 ps)를 쓴다."
  exit 1
fi
echo "다음: UMA 힘 (같은 frame.xyz) → 분석"
