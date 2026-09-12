
import csv, json, os, sys, time, pathlib
a = sys.argv[1:]; sub = a[0]
role = os.environ["ROLE"]; fx = pathlib.Path(os.environ["FIXTURE"])
starts = int(a[a.index("--starts") + 1]); state = a[a.index("--state") + 1]
rid = os.environ.get("BMS_RUN_ID")
(fx / f"{role}.started").write_text("1")
t = time.monotonic() + 120
while not (fx / f"{role}.go").exists():
    assert time.monotonic() < t, "go timeout"; time.sleep(0.01)
if sub == "degeneracy":
    out = {"state": state, "n_starts": starts, "run_id": rid, "role": role,
           "best_modes_percent": {"LAM_PE": 1.0 if role == "A" else 9.0},
           "pad": os.environ.get("PAD", "")}
    print(json.dumps(out))                       # 실제 명령처럼 stdout 으로만
elif sub == "matrix":
    outp = pathlib.Path(a[a.index("--out") + 1])
    tmp = outp.with_name(outp.name + f".{os.getpid()}.part")
    lo = 1.0 if role == "A" else 7.0                     # role 마다 다른 숫자 (compare_states 가 폭을 계산한다)
    with tmp.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["half_cell", "si", "w_dqdv", "run_id", "role", "LAM_PE_pct", "LAM_NE_pct",
                                           "LLI_pct", "bounds", "ref_bounds", "gamma_Si", "ref_gamma_Si"])
        w.writeheader()
        for k in (0.0, 1.0 if role == "A" else 2.0):
            w.writerow({"half_cell": "GITT", "si": "Li", "w_dqdv": 0, "run_id": rid, "role": role, "LAM_PE_pct": lo + k,
                        "LAM_NE_pct": lo + k, "LLI_pct": lo + k, "bounds": "-", "ref_bounds": "-", "gamma_Si": 0.4, "ref_gamma_Si": 0.3})
    import fcntl
    with open(str(outp) + ".lock", "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX); os.replace(tmp, outp)
    print(f"wrote {outp} (run_id {rid})")
(fx / f"{role}.printed").write_text("1")
