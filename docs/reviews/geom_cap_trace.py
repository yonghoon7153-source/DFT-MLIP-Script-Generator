import importlib.util, numpy as np
spec = importlib.util.spec_from_file_location('PC', 'scripts/plastic_coverage.py')
PC = importlib.util.module_from_spec(spec); spec.loader.exec_module(PC)

print('=== geom cap 이 결속하는 접촉 하나를 실제 함수로 통과시킨다 ===')
#  작은 SE(0.5 µm) ↔ 큰 AM(6 µm), 겹침을 키워 Tabor 가 2πR_min² 를 넘게 한다
r_se, r_am = 0.5, 6.0
R_star = (r_se*r_am)/(r_se+r_am); R_min = r_se
for delta in (0.02, 0.05, 0.10, 0.20):
    A, regime, comp = PC.film_area_from_overlap(
        delta*1e-6, R_star*1e-6, R_min=R_min*1e-6, ligg_area=0.0,
        mode='physics', return_components=True)
    um2 = lambda v: None if v is None else v*1e12
    a = np.sqrt(A/np.pi)*1e6                       # solver:323 와 같은 읽기 (µm)
    a_eff = min(a, R_min)                          # solver:395
    psi = max(1.0 - a_eff/R_min, 0.0)**1.5         # solver:396
    R = 0.0 if psi <= 1e-4 else 1.0/(1.0*1.0*2*a_eff*psi)
    print(f'\n δ={delta:.2f} µm  binding={comp["binding"]}')
    print(f'   A_tabor={um2(comp["A_tabor"]):.6f}  A_volume={um2(comp["A_volume"])}  '
          f'A_geom={um2(comp["A_geom"]):.6f} µm²')
    print(f'   A_final={um2(comp["A_final"]):.6f} µm²  →  a={a:.6f} µm  '
          f'(r_min={R_min})  a/r_min={a/R_min:.6f}')
    print(f'   clamp 발동={a>R_min}   a_eff={a_eff:.6f}   ψ={psi:.10f}   '
          f'R_constriction={R:.10f}')
