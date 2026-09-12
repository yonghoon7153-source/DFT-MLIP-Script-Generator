#!/usr/bin/env bash
# =============================================================================
# build_qe_neb_gpu_kgy.sh — QE 7.4.1 GPU 빌드 (pw [+neb]).
#
# 이름 유래: 2026-07-22 에 kgy 에서 neb.x 를 확보하려고 쓴 스크립트다. 기존
#   qe-7.4.1-gpu 빌드 트리가 소멸(설치 bin만 남음)해 from-source GPU 빌드가
#   필요했다. 2026-09-13 에 **기계를 가리지 않게** 일반화했다 — V100(cc70) 에
#   같은 빌드를 올려야 했는데, kgy 전용으로 박힌 값이 셋(NVHPC 경로 · cuda-cc ·
#   neb 강제) 뿐이었기 때문이다. kgy 기본값은 **그대로 보존**돼 그때 명령이
#   그대로 재현된다 (run_elastic_relaxedion_gabia.sh 와 같은 관례).
#
# 쓰는 법
#   bash tools/vgcf_hbn/build_qe_neb_gpu_kgy.sh configure   # 다운로드+configure (GPU 감지 확인)
#   # -> make.inc에 'DFLAGS ... -D__CUDA' 뜨는지 확인 후:
#   bash tools/vgcf_hbn/build_qe_neb_gpu_kgy.sh build       # make pw [neb] (~30-45min)
#   bash tools/vgcf_hbn/build_qe_neb_gpu_kgy.sh --selftest  # 유도 로직만 검사 (빌드 안 함)
#
# 환경변수 (없으면 유도하거나 kgy 기본값)
#   NVROOT    NVHPC 루트. 기본: kgy 경로 → 없으면 /opt/nvidia/hpc_sdk/… 최신
#   CUDA_CC   compute capability 두자리(86/70/…). 기본: **nvidia-smi 에서 유도**
#   SRC       QE 소스 트리        (기본 $HOME/apps/qe-7.4.1-src)
#   GPUBIN    산출 bin 배치처      (기본 $HOME/apps/qe-7.4.1-gpu/bin)
#   JOBS      make -j             (기본 8)
#   WANT_NEB  1=neb 까지, 0=pw 만 (기본 1)
#
# ⛔ cuda-cc 를 상수로 두지 않는 이유 — 기계마다 다르다. RTX3090=86, V100=70,
#   A6000=86. 틀리면 조용히 느려지거나 런타임에 죽는다. 그래서 **기계에게 묻는다**
#   (`nvidia-smi --query-gpu=compute_cap`). CLAUDE.md 의 `ldd` 규율과 같은 원칙:
#   규칙이 아니라 기계가 근거다. 못 읽고 CUDA_CC 도 없으면 **시작하지 않는다**.
#
# 이 스크립트가 **못 하는 것**
#   · 빌드가 물리적으로 맞는지 보지 않는다. 링크가 됐는지만 본다 (ldd).
#   · 드라이버/CUDA 판 호환을 검사하지 않는다.
#   · 여러 기계의 산출물이 수치적으로 같음을 보증하지 않는다.
# =============================================================================
set -u; set +H
# ⚠ conda(uma) 환경이 CFLAGS="-march=nocona ..."를 심음 -> nvc가 nocona 거부(2026-07-22).
# 빌드 전 conda 컴파일 플래그 전부 제거 (gabia_cdd_phx.md "conda deactivate 필수").
unset CFLAGS CPPFLAGS CXXFLAGS FFLAGS FCFLAGS F90FLAGS LDFLAGS DEBUG_CFLAGS DEBUG_CXXFLAGS DEBUG_FFLAGS \
      LD AR RANLIB NM AS STRIP OBJCOPY OBJDUMP READELF ADDR2LINE SIZE STRINGS GPROF ELFEDIT DWP LD_GOLD \
      CC CXX FC F77 F90 CPP CXXCPP GCC GXX GFORTRAN GCC_AR GCC_NM GCC_RANLIB \
      HOST BUILD CONDA_TOOLCHAIN_HOST CONDA_TOOLCHAIN_BUILD CMAKE_ARGS 2>/dev/null || true

# ── 유도 함수 (selftest 가 이것들을 친다) ────────────────────────────────────
# compute capability: 명시값 > nvidia-smi. "8.6" -> "86". 실패하면 빈 문자열.
_derive_cc() {
  if [ -n "${CUDA_CC:-}" ]; then printf '%s' "$CUDA_CC"; return 0; fi
  local cap
  cap=$(${_NVSMI:-nvidia-smi} --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -1 | tr -d ' ')
  case "$cap" in
    [0-9].[0-9]|[0-9][0-9].[0-9]) printf '%s' "${cap%.*}${cap#*.}" ;;
    *) printf '' ;;
  esac
}
# NVHPC 루트: 명시값 > kgy 기본 > /opt 최신. 없으면 빈 문자열.
_derive_nvroot() {
  if [ -n "${NVROOT:-}" ]; then [ -d "$NVROOT" ] && printf '%s' "$NVROOT"; return 0; fi
  local kgy="$HOME/apps/nvhpc/Linux_x86_64/24.11"
  [ -d "$kgy" ] && { printf '%s' "$kgy"; return 0; }
  local o; o=$(ls -d ${_OPTROOT:-/opt/nvidia/hpc_sdk}/Linux_x86_64/*/ 2>/dev/null | sort -V | tail -1)
  [ -n "$o" ] && printf '%s' "${o%/}"
}

# ── --selftest : 유도의 양성·음성 경로 ───────────────────────────────────────
if [ "${1:-configure}" = "--selftest" ]; then
  _T=$(mktemp -d); _n=0; _f=0
  _eq() { if [ "$2" = "$3" ]; then _n=$((_n+1)); else _f=$((_f+1)); echo "  ✗ $1: '$2' != '$3'"; fi; }
  # ⚠ `VAR=x _eq "$(_derive_cc)"` 는 **안 된다** — 명령치환이 _eq 보다 먼저 풀려서
  #   VAR 이 유도 함수에 안 닿는다 (2026-09-13 실측: 음성 4건만 통과해 초록으로 보였다).
  #   그래서 래퍼를 둔다 — 유도는 래퍼 **안에서** 일어난다.
  _cc()  { _NVSMI="$1" CUDA_CC="${2:-}" _derive_cc; }
  _nvr() { NVROOT="${1:-}" _OPTROOT="${2:-/없음}" HOME="${3:-/없음}" _derive_nvroot; }
  # 가짜 nvidia-smi
  printf '#!/bin/sh\necho "8.6"\n' > "$_T/smi86"; chmod +x "$_T/smi86"
  printf '#!/bin/sh\necho "7.0"\n' > "$_T/smi70"; chmod +x "$_T/smi70"
  printf '#!/bin/sh\nexit 1\n'     > "$_T/smibad"; chmod +x "$_T/smibad"
  _eq "3090 -> 86"                  "$(_cc "$_T/smi86")"     "86"
  _eq "V100 -> 70"                  "$(_cc "$_T/smi70")"     "70"
  _eq "명시가 이긴다(CUDA_CC)"       "$(_cc "$_T/smi70" 90)"  "90"
  _eq "⛔ 못 읽으면 빈값(=시작 거부)" "$(_cc "$_T/smibad")"    ""
  _eq "⛔ nvidia-smi 부재도 빈값"     "$(_cc "$_T/없는것")"    ""
  _eq "⛔ 쓰레기 출력도 빈값"         "$(_cc /bin/echo)"       ""
  # NVROOT 유도
  mkdir -p "$_T/opt/Linux_x86_64/24.11" "$_T/opt/Linux_x86_64/26.5"
  _eq "/opt 최신 선택"        "$(_nvr "" "$_T/opt" "$_T/nohome")" "$_T/opt/Linux_x86_64/26.5"
  mkdir -p "$_T/h/apps/nvhpc/Linux_x86_64/24.11"
  _eq "kgy 기본이 우선(재현성)" "$(_nvr "" "$_T/opt" "$_T/h")"     "$_T/h/apps/nvhpc/Linux_x86_64/24.11"
  _eq "명시가 이긴다(NVROOT)"   "$(_nvr "$_T/opt/Linux_x86_64/24.11" "$_T/opt" "$_T/h")" "$_T/opt/Linux_x86_64/24.11"
  _eq "⛔ 명시했는데 없으면 빈값" "$(_nvr "$_T/없는경로" "$_T/opt" "$_T/h")" ""
  _eq "⛔ 아무데도 없으면 빈값"   "$(_nvr "" "$_T/빈곳" "$_T/nohome")"      ""
  rm -rf "$_T"; echo "selftest: $_n 통과 · $_f 실패"; [ "$_f" = 0 ]; exit $?
fi

PHASE=${1:-configure}
SRC=${SRC:-$HOME/apps/qe-7.4.1-src}
GPUBIN=${GPUBIN:-$HOME/apps/qe-7.4.1-gpu/bin}
JOBS=${JOBS:-8}
WANT_NEB=${WANT_NEB:-1}

NV=$(_derive_nvroot)
[ -n "$NV" ] || { echo "⛔ NVHPC 루트를 못 찾았다 (NVROOT= 로 지정) — 시작하지 않는다"; exit 1; }
CC_ARCH=$(_derive_cc)
[ -n "$CC_ARCH" ] || { echo "⛔ compute capability 를 못 읽었다. CUDA_CC=70 처럼 지정해라 (V100=70 · 3090/A6000=86) — 시작하지 않는다"; exit 1; }

HPCX="$(ls -d "$NV"/comm_libs/*/hpcx/hpcx-*/ompi 2>/dev/null | sort | tail -1)"
[ -n "$HPCX" ] || HPCX="$NV/comm_libs/mpi"        # hpcx 가 없는 설치도 있다 (번들 openmpi)
CUDAHOME=$NV/cuda/12.6
[ -d "$CUDAHOME" ] || CUDAHOME="$(ls -d "$NV"/cuda/12.* 2>/dev/null | sort -V | tail -1)"
[ -d "$CUDAHOME" ] || { echo "⛔ 번들 CUDA 12.x 를 못 찾았다: $NV/cuda — 시작하지 않는다"; exit 1; }
CUDA_RT=$(basename "$CUDAHOME")                    # configure 에 넘길 runtime 판

# conda bin 경로 완전 제거 (2026-07-22): CFLAGS unset만으론 부족 — conda binutils
# (x86_64-conda-linux-gnu-ld/ar)가 NVHPC GPU 링크(-cuda/-gpu/-acc)를 깨뜨림.
# PATH에서 conda/miniforge/envs 경로 싹 걷어내고 NVHPC만 앞세움 (=conda deactivate 등가).
PATH="$(printf '%s' "$PATH" | tr ':' '\n' | grep -viE 'conda|miniforge|mamba|/envs/' | paste -sd: -)"
export PATH="$NV/compilers/bin:$HPCX/bin:/usr/bin:/bin:$PATH"
export LD_LIBRARY_PATH="$NV/compilers/lib:$CUDAHOME/lib64:$NV/math_libs/lib64:$HPCX/lib:${LD_LIBRARY_PATH:-}"
export OPAL_PREFIX="$HPCX" OMPI_FC=nvfortran OMPI_CC=nvc
echo "════════ QE-GPU 빌드 ════════"
echo "  NVHPC     $NV"
echo "  CUDA      $CUDAHOME  (runtime $CUDA_RT)"
echo "  MPI       $HPCX"
echo "  cuda-cc   $CC_ARCH   ${CUDA_CC:+(명시)}${CUDA_CC:-(nvidia-smi 에서 유도)}"
echo "  소스      $SRC"
echo "  bin       $GPUBIN    · make -j$JOBS · neb=$WANT_NEB"
echo "toolchain: $(command -v nvfortran) | $(command -v mpif90)"
command -v nvfortran >/dev/null && command -v mpif90 >/dev/null || { echo "⛔ nvfortran/mpif90 없음 (NVHPC env 확인)"; exit 1; }

if [ "$PHASE" = configure ]; then
  mkdir -p "$(dirname "$SRC")"; cd "$(dirname "$SRC")"
  if [ ! -f "$SRC/configure" ]; then
    echo "[dl] QE 7.4.1 source (gitlab archive)..."
    wget -q "https://gitlab.com/QEF/q-e/-/archive/qe-7.4.1/q-e-qe-7.4.1.tar.gz" -O qe741.tar.gz \
      || { echo "다운로드 실패 — URL/네트워크 확인 (대안: github releases)"; exit 1; }
    tar xzf qe741.tar.gz && rm -rf "$SRC" && mv q-e-qe-7.4.1 "$SRC"
  fi
  cd "$SRC"
  echo "[env] conda 플래그 제거 확인: CFLAGS='${CFLAGS:-(빔)}'"
  ./configure --with-cuda="$CUDAHOME" --with-cuda-cc="$CC_ARCH" --with-cuda-runtime="$CUDA_RT" \
     --enable-openmp F90=nvfortran CC=nvc MPIF90=mpif90 2>&1 | tail -35
  # make.inc 잔재 소거 (이중 안전): conda 컴파일 플래그 + conda binutils.
  # LD는 QE 관례상 컴파일러(mpif90)가 드라이브 -> -cuda/-gpu/-acc 이해. AR/RANLIB은 시스템.
  sed -i -E \
    -e 's/-march=nocona[^ ]*//g; s/-mtune=[^ ]*//g' \
    -e 's|^(LD *=).*|\1 mpif90|' \
    -e 's|x86_64-conda-linux-gnu-ar|ar|g; s|x86_64-conda-linux-gnu-ranlib|ranlib|g' \
    -e 's|x86_64-conda-linux-gnu-nm|nm|g; s|x86_64-conda-linux-gnu-||g' \
    "$SRC"/make.inc 2>/dev/null || true
  echo "[make.inc] LD=$(grep -E '^LD *=' "$SRC"/make.inc) | AR=$(grep -E '^AR *=' "$SRC"/make.inc) | conda잔재 $(grep -c conda "$SRC"/make.inc)"
  echo "── GPU 감지 (make.inc) ──"
  grep -iE "__CUDA|cuda|GPU_ARCH|MANUAL_DFLAGS" "$SRC"/make.inc 2>/dev/null | head -6
  echo ">> make.inc에 -D__CUDA 보이면 GPU OK -> 'build' 단계로"

elif [ "$PHASE" = build ]; then
  [ -f "$SRC/make.inc" ] || { echo "⛔ configure 먼저 (make.inc 없음)"; exit 1; }
  cd "$SRC"
  # ⚠ 'make -j8 pw neb'(동시 goal)은 병렬 경합으로 externals 직후 죽음(2026-07-22).
  # -> pw 먼저 완성 후 neb 링크. 전체 로그 파일 보존(tail 파이프 금지).
  echo "[build] make -j$JOBS pw  ($(date +%H:%M:%S)) -> ~/qe_pw_build.log"
  make -j"$JOBS" pw > "$HOME/qe_pw_build.log" 2>&1; pw_rc=$?
  echo "  pw rc=$pw_rc  (tail:)"; tail -4 "$HOME/qe_pw_build.log"
  [ "$pw_rc" = 0 ] && [ -f "$SRC/bin/pw.x" ] || {
    echo "!! pw 빌드 실패 — 에러:"; grep -inE "error|cannot|undefined|No rule|Stop|fatal" "$HOME/qe_pw_build.log" | tail -15; exit 1; }
  mkdir -p "$GPUBIN"; cp "$SRC/bin/pw.x" "$GPUBIN/" && echo "pw.x -> $GPUBIN/"
  echo "── pw.x GPU 링크 확인 (여기가 근거다) ──"
  ldd "$GPUBIN/pw.x" 2>/dev/null | grep -iE "cufft|cudart|cuda|libmpi|libnvomp|libgomp" | head -8

  if [ "$WANT_NEB" = 1 ]; then
    echo "[build] make neb  ($(date +%H:%M:%S)) -> ~/qe_neb_build.log"
    make neb > "$HOME/qe_neb_build.log" 2>&1
    if [ -f "$SRC/bin/neb.x" ]; then
      cp "$SRC/bin/neb.x" "$GPUBIN/" && echo "neb.x -> $GPUBIN/ (배치완료)"; ls -la "$GPUBIN/neb.x"
      ldd "$GPUBIN/neb.x" 2>/dev/null | grep -iE "cufft|cudart|cuda" | head -4
    else
      echo "!! neb.x 생성 실패 — 에러:"; grep -inE "error|cannot|undefined|Stop" "$HOME/qe_neb_build.log" | tail -15
    fi
  else
    echo "(WANT_NEB=0 — neb 는 건너뛴다)"
  fi
  echo ">> 다음: ldd 로 실제 링크된 MPI 를 보고 런타임 env 를 짠다 (CLAUDE.md §kgy)"
fi
