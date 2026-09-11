#!/usr/bin/env bash
# =============================================================================
# run_elastic_relaxedion_gabia.sh — relaxed-ion stress–strain full Cij (gabia).
#
# 이름 유래: run_comp2_elastic_uspp_gabia.sh (comp2 의 PAW 철회 후 USPP 재계산).
#   comp2 기본값은 **그대로 보존**돼 있어 그때 명령이 그대로 재현된다.
#   2026-09-10 에 계 선택(SYS)만 붙여 일반화했다 — b2o3 재측정과 LPSCl1.6 124원자
#   통제군을 **같은 러너**로 돌려야 두 결과가 비교 가능해지기 때문이다.
#
# 쓰는 법
#   SYS=modelc_2x DRY_RUN=1 bash tools/elastic/run_elastic_relaxedion_gabia.sh   # 설정만 본다
#   SYS=b2o3   tmux new -s el_b -d 'bash tools/elastic/run_elastic_relaxedion_gabia.sh > ~/el_b2o3.log 2>&1'
#
# ⛔ strain 기본값이 왜 0.005 인가 (2026-09-10 판단)
#   b2o3 의 2026-07-03 전단 실패 카드는 재시도로 `strain 0.01 (2x signal)` 을 적어
#   뒀고 두 기계에 그 입력이 스테이징돼 있다(둘 다 안 돌았고 서로 설정이 다르다).
#   그런데 이 러너의 목적은 **'셀이냐 조성이냐'** 이고, 그건 원장의 나머지 넷
#   (comp1·modelc·lpsocl·comp2, 전부 strain 0.005)과 **같은 창**에서 물어야 한다.
#   strain 을 같이 바꾸면 두 변수가 동시에 움직여 어느 쪽도 못 가른다.
#   ⇒ 0.005 로 먼저 돌린다. 여기서 modelc_2x 가 성립하고 b2o3 가 또 깨지면
#     그것이 곧 답(조성)이다. 그때 비로소 `STRAIN=0.01` 재시도가 **b2o3 한 계에만**
#     필요해진다 — 12잡을 나중에, 필요할 때만 쓴다.
#
# 이 러너가 **못 하는 것**
#   · clamped-ion 을 하지 않는다 (1저자 결정 2026-09-10). 내부이완을 금지하면
#     구조적으로 항상 positive-definite 라 **실패할 수 없는 검사**다.
#   · V0 부피를 정하지 않는다. STRUCT 가 이미 BM-EOS V0 여야 한다.
#   · 필요 VRAM 을 예측하지 않는다. MINFREE 는 **실측에서 온 수**다 —
#     2026-09-10 에 14000 으로 잡았다가 124원자 V0 relax 가 OOM 으로 죽었고,
#     그 출력이 `Estimated max dynamical RAM per process > 23.83 GB` 를 찍었다
#     (newd_gpu:newq_gpu 에서 7.98 GB 단일 할당 실패 · 가용 4.84 GB).
#     26000 으로 올렸더니 이번엔 통과했고, 실제 점유가 **29552 MiB** 로 찍혔다
#     (nvidia-smi, modelc_2x V0 relax). 즉 26000 은 여전히 실사용보다 낮아서
#     free 가 딱 26 GB 인 순간에 던지면 또 죽는다 ⇒ **32000**.
#     ⇒ 128원자급은 32000. 다른 크기를 돌릴 때는 첫 잡의 `Estimated max dynamical
#       RAM` 줄과 **실제 nvidia-smi 점유**를 둘 다 보고 고친다 (추정치보다 실측이 크다).
#   · 계 간 비교 가능성을 보증하지 않는다 — 그건 설정이 같은지 사람이 보는 일이고,
#     그래서 DRY_RUN 이 해석된 설정을 전부 찍는다.
# =============================================================================
set -u; set +H
SYS=${SYS:-comp2}
# ⛔⛔ 2026-09-10 실측 — 종전엔 `$HOME/Yonghoon-DEM-DFT` 를 먼저 봤다. gabia 에는
#   repo 가 **두 벌**(/root/Yonghoon-DEM-DFT · /data/work/repo) 있어서, /data/work/repo
#   에서 pull 하고 그 스크립트를 실행해도 REPO 는 /root 쪽으로 잡혔다 ⇒ **스크립트는
#   새 판인데 빌더·피터는 옛 repo 에서 가져오는** 계보 혼합이 조용히 생긴다.
#   ⇒ 기본값은 **이 스크립트 자신이 있는 repo** 다. 명시 REPO 는 그대로 존중한다.
REPO=${REPO:-$(cd "$(dirname "$(realpath "$0")")/../.." 2>/dev/null && pwd)}
[ -d "${REPO:-}/tools/elastic" ] || { echo "⛔ REPO 를 못 찾았다: ${REPO:-<빈값>}"; exit 1; }
echo "  repo      $REPO  (git $(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo '?'))"

# ── 계별 설정 (한 곳) ───────────────────────────────────────────────────────
case "$SYS" in
  comp2)      # 2026-07-26 실행분. 값을 바꾸지 않는다 — 그때 명령의 재현성이 여기 걸려 있다.
    STRUCT_D=$REPO/db/structures/comp2_V0_v3_relaxed.xyz
    ECUTWFC=52; ECUTRHO=520; KLINE_D="4 4 4 0 0 0"; STRAIN_D=0.005
    DEGAUSS=0.01; CONV_THR=1e-8; MIXBETA=0.3; MIXMODE=""; NOSYM=""
    PREFIX=c2v0
    PSEUDOS='{"Li":"li_pbe_v1.4.uspp.F.UPF","P":"P.pbe-n-rrkjus_psl.1.0.0.UPF","S":"s_pbe_v1.4.uspp.F.UPF","Cl":"cl_pbe_v1.4.uspp.F.UPF","Br":"br_pbe_v1.4.uspp.F.UPF"}'
    MINFREE=6000 ;;
  b2o3)       # 128원자 · B2O3-doped LPSCl1.6. O 는 v1.4 USPP set 에 없어 kjpaw
              # (lpsocl 도 같은 혼합이다 — 그 계의 recipe 필드 참조).
    STRUCT_D=$REPO/db/structures/b2o3_relaxV0.xyz
    ECUTWFC=60; ECUTRHO=480; KLINE_D="2 2 1 0 0 0"; STRAIN_D=0.005
    DEGAUSS=0.01; CONV_THR=1e-10; MIXBETA=0.2; MIXMODE="local-TF"; NOSYM="1"
    PREFIX=b2o3v0
    PSEUDOS='{"Li":"li_pbe_v1.4.uspp.F.UPF","P":"P.pbe-n-rrkjus_psl.1.0.0.UPF","S":"s_pbe_v1.4.uspp.F.UPF","Cl":"cl_pbe_v1.4.uspp.F.UPF","B":"b_pbe_v1.4.uspp.F.UPF","O":"O.pbe-n-kjpaw_psl.0.1.UPF"}'
    MINFREE=32000 ;;
  modelc_2x)  # 124원자 무도핑 통제군. b2o3 와 **같은 프레임**이다
              # (7.007/7.007/70.071 Å vs 6.997/6.984/70.387 · Cl 16개로 동일).
    STRUCT_D=$REPO/db/structures/modelc_2x_V0.xyz
    ECUTWFC=60; ECUTRHO=480; KLINE_D="2 2 1 0 0 0"; STRAIN_D=0.005
    DEGAUSS=0.01; CONV_THR=1e-10; MIXBETA=0.2; MIXMODE="local-TF"; NOSYM="1"
    PREFIX=mc2xv0
    PSEUDOS='{"Li":"li_pbe_v1.4.uspp.F.UPF","P":"P.pbe-n-rrkjus_psl.1.0.0.UPF","S":"s_pbe_v1.4.uspp.F.UPF","Cl":"cl_pbe_v1.4.uspp.F.UPF"}'
    MINFREE=32000 ;;
  *) echo "⛔ SYS 를 모른다: '$SYS' (아는 것: comp2 · b2o3 · modelc_2x) — 시작하지 않는다"; exit 2 ;;
esac
STRUCT=${STRUCT:-$STRUCT_D}; STRAIN=${STRAIN:-$STRAIN_D}; KLINE=${KLINE:-$KLINE_D}
# ── 수렴 문턱 — **계에 묶는다** (2026-09-11 개정안 shear_b2o3_vs_lpscl16_2x_amendment) ──
#   modelc_2x V0_relax 가 forc 1e-4 에서 21 BFGS·809 SCF·12 h 동안 |F| 2.5–3.2e-3 으로
#   진동만 했다. 개정: b2o3·modelc_2x **두 계 모두** forc 1e-3 · etot 1e-5 (QE 기본값).
#   ⛔ comp2 는 1e-4/1e-6 으로 이미 돌았으므로 **바꾸지 않는다** — 같은 계 안에서
#     설정이 갈리면 그 계의 Cij 가 무효다. 그래서 기본값을 SYS 로 가른다.
case "$SYS" in
  b2o3|modelc_2x) FORC_CONV_D=1e-3; ETOT_CONV_D=1e-5 ;;
  *)              FORC_CONV_D=1e-4; ETOT_CONV_D=1e-6 ;;
esac
FORC_CONV=${FORC_CONV:-$FORC_CONV_D}; ETOT_CONV=${ETOT_CONV:-$ETOT_CONV_D}
WORK=${WORK:-/data/work/runs/elastic_${SYS}}
MINFREE=${MINFREE_MIB:-$MINFREE}

echo "════════ elastic relaxed-ion · SYS=$SYS ════════"
printf "  구조      %s\n  작업방    %s\n" "$STRUCT" "$WORK"
printf "  ecut      %s / %s Ry\n  k         %s\n  strain    ±%s\n  conv      forc %s · etot %s (SYS 로 갈린다)\n" \
       "$ECUTWFC" "$ECUTRHO" "$KLINE" "$STRAIN" "$FORC_CONV" "$ETOT_CONV"
printf "  smearing  mv %s\n  conv_thr  %s\n  mixing    beta %s%s\n  nosym     %s\n" \
       "$DEGAUSS" "$CONV_THR" "$MIXBETA" "${MIXMODE:+ · $MIXMODE}" "${NOSYM:+.true.}"
echo   "  pseudo    $PSEUDOS"
printf "  VRAM 가드 %s MiB\n" "$MINFREE"
[ -f "$STRUCT" ] || { echo "⛔ 구조가 없다: $STRUCT"; exit 1; }
python3 - "$STRUCT" <<'PY'
import sys, numpy as np
n = int(open(sys.argv[1]).readline())
com = open(sys.argv[1]).readlines()[1]
v = np.array(com.split('Lattice="')[1].split('"')[0].split(), float).reshape(3, 3)
L = np.linalg.norm(v, axis=1)
print(f"  셀        {n}원자 · {L[0]:.3f}/{L[1]:.3f}/{L[2]:.3f} Å · V {abs(np.linalg.det(v)):.1f} Å³")
PY
if [ -n "${DRY_RUN:-}" ]; then echo "  ⇢ DRY_RUN — 계산은 하지 않았다"; exit 0; fi
[ "$(pgrep -fc run_elastic_relaxedion)" -le 2 ] || { echo "⛔ 이미 실행중"; exit 1; }
mkdir -p "$WORK"

# ── gabia QE-GPU env (lpsocl/comp2 suite 와 동일) ──────────────────────────
HPCX=/data/apps/nvhpc/Linux_x86_64/24.11/comm_libs/12.6/hpcx/hpcx-2.20/ompi
export PATH=$HPCX/bin:$PATH
export LD_LIBRARY_PATH=$HPCX/lib:/data/apps/nvhpc/Linux_x86_64/24.11/compilers/lib:/usr/local/cuda-12.6/lib64:${LD_LIBRARY_PATH:-}
export OPAL_PREFIX=$HPCX OMP_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=0 OMPI_ALLOW_RUN_AS_ROOT=1 OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
QE=/data/apps/qe-7.4.1-gpu/bin; MPIRUN=$HPCX/bin/mpirun
ts(){ date +%H:%M:%S; }
wait_gpu(){ local free
  while :; do
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0 2>/dev/null | head -1); [ -z "$free" ] && free=0
    [ "$free" -ge "$MINFREE" ] && { echo "[$(ts)] GPU free ${free} MiB — go"; return; }
    echo "[$(ts)] GPU free ${free} < $MINFREE 대기"; sleep 60
  done; }
run_pw(){ grep -q "JOB DONE" "$2" 2>/dev/null && { echo "[$(ts)] $2 DONE skip"; return 0; }
  wait_gpu; echo "[$(ts)] pw.x $1"
  "$MPIRUN" -np 1 "$QE/pw.x" -npool 1 -in "$1" > "$2" 2>&1
  grep -q "JOB DONE" "$2" && echo "[$(ts)] $1 OK" || { echo "[$(ts)] $1 FAIL:"; tail -12 "$2"; return 1; } }

# ── pseudo — find-or-fail ────────────────────────────────────────────────────
PSE=$WORK/pseudo; mkdir -p "$PSE"
NEED=$(python3 -c "import json,sys;print(' '.join(json.loads(sys.argv[1]).values()))" "$PSEUDOS")
for p in $NEED; do
  [ -s "$PSE/$p" ] && continue
  src=$(find /data/work/pseudo /data/work/bml/manuscript_support -name "$p" 2>/dev/null | head -1)
  [ -n "$src" ] && { cp "$src" "$PSE/$p"; echo "  pseudo $p <- $src"; } || { echo "⛔ pseudo $p 못찾음 — 시작하지 않는다"; exit 1; }
done
echo "[$(ts)] pseudo $(echo $NEED | wc -w)종 확보"

# ── V0 relax 입력 (계 설정 그대로) ──────────────────────────────────────────
if [ ! -f "$WORK/V0_relax.in" ]; then
  echo "[$(ts)] V0_relax.in 생성"
  python3 - "$STRUCT" "$PSE" "$WORK" "$PSEUDOS" "$ECUTWFC" "$ECUTRHO" "$DEGAUSS" \
             "$CONV_THR" "$MIXBETA" "$MIXMODE" "$NOSYM" "$PREFIX" "$KLINE" \
             "$FORC_CONV" "$ETOT_CONV" << 'PY'
import sys, json, numpy as np
from ase.io import read, write
(struct, pse, work, pj, ecw, ecr, dg, cth, mb, mm, ns, pfx, kline, fcv, ecv) = sys.argv[1:16]
a = read(struct)
sysd = {"ecutwfc": float(ecw), "ecutrho": float(ecr), "occupations": "smearing",
        "smearing": "mv", "degauss": float(dg)}
if ns: sysd["nosym"] = True          # 변형셀은 대칭을 끈다 (strain 입력이 이걸 승계한다)
el = {"conv_thr": float(cth), "mixing_beta": float(mb)}
if mm: el["mixing_mode"] = mm
inp = {"control": {"calculation": "relax", "restart_mode": "from_scratch",
                   "tprnfor": True, "tstress": True, "etot_conv_thr": float(ecv),
                   "forc_conv_thr": float(fcv), "pseudo_dir": pse, "outdir": "./tmp_v0",
                   "prefix": pfx},
       "system": sysd, "electrons": el, "ions": {"ion_dynamics": "bfgs"}}
k = tuple(int(x) for x in kline.split()[:3])
write(work + "/V0_relax.in", a, format="espresso-in", input_data=inp,
      pseudopotentials=json.loads(pj), kpts=k)
print(f"  V0_relax.in: {len(a)} atoms, V={abs(np.linalg.det(a.cell)):.2f} A^3, k={k}, "
      f"forc_conv={fcv}, etot_conv={ecv}")
PY
fi

cd "$WORK"
run_pw V0_relax.in V0_relax.out || { echo "⛔ V0 relax FAIL"; exit 1; }

if [ ! -f "$WORK/strain_11_p.in" ]; then
  echo "[$(ts)] build 12 strain (relaxed-ion, ±$STRAIN, k=$KLINE)"
  python3 "$REPO/tools/comp1_v3/build_elastic_strain_inputs.py" --relaxed_ion \
    --src_in "$WORK/V0_relax.in" --src_out "$WORK/V0_relax.out" \
    --strain "$STRAIN" --workdir "$WORK" --prefix_base strain \
    --kpoints "$KLINE" || { echo "⛔ strain 생성 실패"; exit 1; }
fi
TAGS="strain_11_p strain_11_m strain_22_p strain_22_m strain_33_p strain_33_m \
      strain_23_p strain_23_m strain_13_p strain_13_m strain_12_p strain_12_m"
for t in $TAGS; do
  sed -i "s|outdir *=.*|outdir='./tmp_$t'|; s|prefix *=.*|prefix='$t'|; s|pseudo_dir *=.*|pseudo_dir='$PSE'|" "$t.in"
done
for t in $TAGS; do run_pw "$t.in" "$t.out" || echo "  ($t FAIL — fit 전 재실행 필요)"; done

# ⛔ 12점이 다 끝나야 fit 한다. 11점으로 Cij 를 맞추면 한 열이 통째로 비어
#   고유값이 무의미해진다 — b2o3 2026-07-03 판이 정확히 그 종류의 오염이었다.
NDONE=$(for t in $TAGS; do grep -qa "JOB DONE" "$t.out" 2>/dev/null && echo x; done | wc -l)
echo "[$(ts)] 완료 $NDONE/12"
[ "$NDONE" = 12 ] || { echo "⛔ 12점이 안 찼다 — fit 하지 않는다. 실패한 점을 다시 돌려라."; exit 1; }
echo "[$(ts)] fit Cij -> VRH ($SYS · ecut $ECUTWFC/$ECUTRHO · k $KLINE · ±$STRAIN):"
python3 "$REPO/tools/modelc_v3/fit_elastic_cij_stress.py" --workdir "$WORK" --strain "$STRAIN" \
  --struct "$STRUCT" | tee "$WORK/elastic_fit.txt"
echo ""; echo ">> $WORK/elastic_fit.txt 붙여줘 — 고유값 전부 >0 인지, 금지 off-diagonal 크기부터 본다."
