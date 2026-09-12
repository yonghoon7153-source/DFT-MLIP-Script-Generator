#!/usr/bin/env bash
# watch_li2s_layer1.sh — Li₂S 1층 melt-quench 진행 감시. **요약만 찍고 판정하지 않는다** (지표 문턱은 카드 §2).
#   watch -n 60 bash /data/work/repo/tools/ionic/watch_li2s_layer1.sh [/data/work/runs/li2s_layer1]
#   보는 것: GPU · 실행 중 프로세스 · 시드별 phase(melt/quench/hold) · t_ps · T · 밀도 · ps/h · ETA · 완료 시 지표 3개
#   못 하는 것: 담금질이 물리적으로 괜찮은지 · 결정화 여부 · 판정. 갱신이 10분 넘게 멈추면 ⚠ 만 찍는다.
R=${1:-/data/work/runs/li2s_layer1}
echo "════════ $(date '+%m-%d %H:%M:%S')  Li2S layer-1 melt-quench — $R ════════"
G=$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader 2>/dev/null); echo "■ GPU ${G:-n/a}"
P=$(pgrep -af "melt_quench_uma.py" | grep -v "pgrep\|watch_" | head -1)
if [ -n "$P" ]; then echo "■ 실행: $(echo "$P" | grep -o -- '--system [^ ]* --seed [^ ]*')"; else echo "■ 실행 중인 melt_quench 없음"; fi
python3 - "$R" <<'PY'
import sys, os, json, time, glob
R = sys.argv[1]; now = time.time(); rows = []; modes = set()
def g(I, k):
    v = I.get(k); return "  —  " if v is None else f"{v:5.2f}"
for plan in sorted(glob.glob(os.path.join(R, "*", "seed*", "plan.json"))):
    d = os.path.dirname(plan); sysn = os.path.basename(os.path.dirname(d)); seed = os.path.basename(d)
    try:
        Pj = json.load(open(plan))
    except Exception as e:
        rows.append(f"  {sysn:16s} {seed:6s} ⚠ plan.json 못 읽음 ({e})"); continue
    total = Pj["melt_ps"] + Pj["quench_ps"] + Pj["hold_ps"]
    mode = Pj.get("uma_inference_mode") or "?"          # turbo / default — 시드마다 같아야 한다
    modes.add(mode)
    res, th = os.path.join(d, "result.json"), os.path.join(d, "thermo.csv")
    if os.path.isfile(res):
        try:
            I = json.load(open(res))["indicators"]
            rows.append(f"  {sysn:16s} {seed:6s} ✅ 완료   ρ {I['density_g_cm3']:.3f}  PS4 {g(I,'PS4_fraction')}  Cl6 {g(I,'Cl_6coord_fraction')}  S-Li8 {g(I,'S_Li8_fraction_Li2S_like')}")
        except Exception as e:
            rows.append(f"  {sysn:16s} {seed:6s} ⚠ result.json 못 읽음 ({e})")
        continue
    el = (now - os.path.getmtime(plan)) / 60
    if not os.path.isfile(th) or os.path.getsize(th) < 60:
        rows.append(f"  {sysn:16s} {seed:6s} … 준비(prerelax/초기)  {el:.0f} 분 경과"); continue
    last = open(th).read().strip().splitlines()[-1].split(",")
    try:
        t, T, Tset, rho = float(last[0]), float(last[1]), float(last[2]), float(last[3])
        P = float(last[6]) if len(last) > 6 else float("nan")     # P_GPa (옛 런은 열이 없다)
    except ValueError:
        rows.append(f"  {sysn:16s} {seed:6s} … thermo.csv 헤더만"); continue
    if t >= total - 1e-9:
        phase = "relax"
    else:
        phase = "melt" if t < Pj["melt_ps"] else ("quench" if t < Pj["melt_ps"] + Pj["quench_ps"] else "hold")
    rate = t / el if el > 0 else 0.0                       # ps/min
    eta = (total - t) / rate / 60 if rate > 0 else float("nan")
    stale = (now - os.path.getmtime(th)) / 60
    flag = f"  ⚠ 갱신 {stale:.0f}분 전" if stale > 10 else ""
    pstr = f"P {P:+6.3f}" if P == P else "P   —  "            # ⛔ 옛 런은 배로스탯 제어변수를 기록 안 했다
    rows.append(f"  {sysn:16s} {seed:6s} {phase:6s} t {t:7.1f}/{total:.0f} ps  T {T:6.0f}(set {Tset:5.0f}) K  ρ {rho:.3f}  {pstr}  {rate*60:5.1f} ps/h  ETA {eta:4.1f} h{flag}")
print("\n".join(rows) if rows else "  (plan.json 없음 — 아직 시작 안 함)")
if len(modes) > 1:
    print(f"  ⛔ UMA 실행모드가 시드마다 다르다 {sorted(modes)} — 한 묶음으로 못 쓴다")
elif modes:
    print(f"  UMA 실행모드 {modes.pop()} (전 시드 동일) · 담금질 {Pj['quench_rate_K_s']:.0e} K/s")
PY
echo "  ⛔ 지표(PS4·Cl6·S-Li8)는 카드 §2 문턱과 사람이 대조한다 — 이 표는 판정하지 않는다"
