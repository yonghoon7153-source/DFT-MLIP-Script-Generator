#!/usr/bin/env python3
"""LHS 130 구조 디스크립터 수확기 — **일곱 등록 열을 원 dump 에서** 낸다.

    python3 scripts/lhs_descriptor_harvest.py --atom post/atom_2425000.liggghts \\
        --contact post/contact_2425000.liggghts --mesh post/mesh.stl \\
        --n-types 3 --case lhs00_000
    python3 scripts/lhs_descriptor_harvest.py --selftest

이 파일은 **판정문 §7 의 최소 계약 6개**를 도구에 고정한 것이다.
판정 = `docs/reviews/codex_verdict_lhs_descriptors_20260913.md` (HOLD) · 원장 `DESC-01~09`.
선례 = `lhs_perc_extract.py` — *"추출기와 경계 fixture 를 **결과 전에** 커밋해야 이 규약이
실재한다"* (Codex R11 B1).  그 파일의 덤프 읽기·경계 검사·쌍 찾기를 **재사용**한다
(규율 ①: 새로 짜기 전에 리포에 있는 것부터 — 어댑터에서 `run_contract.py` 를 못 보고 새로
짠 것이 `PA12-01~05` 의 절반이었다).

═══ 왜 `full_metrics.json` 을 읽지 않나 ═══

`DESC-01` 이 재현한 것: `dem_analysis_core.py:938` 이 `phi_se` 를 **이미 계산해 놓고**
`:941` 에서 τ 가 없으면 `return None` 하고, `analyze_contacts.py:430` 의 `if eff_cond:`
가드가 **기하량인 φ 두 개를 통째로 누락**시킨다.  `NET_MERGE_KEYS` 에도 φ 가 없어 복구되지
않는다.  ⇒ 완전행 필터로 학습셋을 만들면 **연결성이 약한 침대가 구조 타깃째 탈락**한다
= 결측이 물리와 상관된다.  파생물을 읽으면 그 결함을 그대로 상속한다.

═══ 계약 ① — 일곱 별칭 ↔ 실제 계산량 ═══

기호: `V_B = L_x·L_y·H` (H = **플래튼 높이**, §계약⑤) · `V_i = 4πr_i³/3`.

| 등록 별칭 | 이 도구가 내는 양 |
|---|---|
| `phi_se`  | `Σ_{i∈SE} V_i / V_B`.  **τ·전도도와 무관하게** 항상 낸다 (계약②) |
| `phi_am`  | `Σ_{i∈AM} V_i / V_B` — **직접 합**이다.  `1−φ_SE−ε/100` 같은 잔차가 아니다 |
| `coverage_AM_P_hertz_pct` | 아래 `c_i` 의 **AM_P 입자별 산술평균** (유효 분모만) |
| `coverage_AM_S_hertz_pct` | 같은 계산의 AM_S 평균 |
| `coverage_AM_total_hertz_pct` | `(N_P·C_P + N_S·C_S)/(N_P+N_S)`, **실측 입자수** 가중 |
| `tortuosity_dijkstra_SE` | SE 접촉그래프 최단경로 / 끝점 z 거리 — 아래 §τ |
| `porosity_sphere_pct_RECORD_ONLY` | `100(1 − Σ_i V_i / V_B)`.  겹침을 빼지 않는다 |

**Hertz 피복률의 정확한 정의** (`dem_analysis_core.py:172` 규약):
```
F_i = 4π r_i²  −  Σ(i 에 붙은 AM–AM 접촉면적)
c_i = min(100, 100 · Σ(i 에 붙은 AM–SE 접촉면적) / F_i)      [F_i > 0]
c_i = FREE_SURFACE_INVALID                                    [F_i ≤ 0]
```
분자는 **LIGGGHTS 가 보고한 `contact_area`**(`c_cpl[22]`)다 — 이 도구가 `πR*δ` 를 다시
계산하는 것이 **아니다**.  ⚠ `F_i ≤ 0` 을 **0 으로 접지 않는다** (`DESC-05`: 실제 무접촉과
분모 붕괴가 섞인다).  cap 발동 횟수와 분모붕괴 횟수를 **따로** 보고한다.

⚠ **전체 평균의 함정** (판정문 반례): P 1개·10 % · S 3개·각 90 % 이면 **전체 70 %** 다.
상 평균의 평균은 50 %, 총면적비는 30 %, 질량가중은 18 % — **넷이 다른 양**이다.

⚠ **Physics 피복률은 여기서 계산하지 않는다** (계약④).  `DESC-03` 이 `plastic_coverage.py`
의 `A_volume = V_overlap / H_FILM_MIN` 에서 **확대 DEM 길이 ÷ 미확대 5 nm** 혼용을
재현했고, 그 때문에 `min(caps)` 의 binding cap 이 `tabor ↔ volume` 로 뒤집힌다.  Hertz 는
그 영향 밖이지만(재현 결과 불변), **섞지 않기 위해** 이 도구는 Physics 를 아예 안 부른다.

═══ §τ — 계약 ③ ═══

`DESC-02` 가 양방향 반례를 냈다:
① `dem_analysis_core.py:502-509` 가 바닥판 source 가 없으면 **위판에 닿는 성분의 최저 z**
   를 새 source 로 승격한다 ⇒ `percolation_pct = 0` 인데 `τ = 1` 이 나온다.
② 같은 함수 `:517-522` 가 `src × top` 전수 쌍을 shuffle 해 앞 200 개만 남기므로 **서로 다른
   성분의 무경로 쌍**이 예산을 먹는다 ⇒ 관통 성분이 200 개여도 `τ = None` 이 된다.

이 도구의 규약 (**legacy 와 다르다 — 같은 컬럼에 섞지 말 것**, `DESC-04`):
- **fallback source 승격 없음.**  source = 아래 슬래브의 SE **이면서** 위 슬래브에 닿는
  성분의 구성원.  없으면 `NOT_PERCOLATING` 이고 **유한 τ 를 내지 않는다**.
- **쌍은 같은 성분 안에서만** 뽑는다 ⇒ 예산이 무경로 쌍에 소진되지 않는다.
- 슬래브 = 고체(AM ∪ SE) z 범위 `[min(z−r), max(z+r)]` 의 양 끝, 두께 = `r_SE,max`.
  (`lhs_perc_extract` ④ 와 같은 사고 — AM 만의 범위를 쓰면 희박한 침대에서 판정이 쉬워진다.)
- 통계량을 **이름으로 가른다**: `tau_mean`(절단본, legacy 호환) · `tau_median` ·
  `tau_mean_untruncated` · `n_truncated`.  등록 별칭 `tortuosity_dijkstra_SE` = **`tau_mean`**.
  ⚠ 판정문 반례: `[1,1,10]` → mean **4** / recommended **1**; `[1, 20.024984]` → 절단 후
  mean **1** vs 무절단 **10.512492**.  이름이 통계량을 정하지 않으면 target 이 갈린다.

═══ 계약 ⑤ — 프로비넌스 fail-closed ═══

- atom · contact 덤프의 **TIMESTEP 이 같아야** 한다.  다르면 거부.
  (`DESC-06`: `parse_liggghts.py:243` 은 종류별 최신 파일을 **독립 선택**해 `atom_100 +
  contact_200` 을 rc=0 으로 받았다.  그리고 그 파서는 **모든 프레임 행을 이어 붙인다**.)
- `H`(플래튼 높이)는 **mesh STL 또는 명시 `--plate-z`** 로만 받는다.  **추정 금지** —
  `dem_analysis_core.py:110` 의 "mesh 없으면 최고 입자 중심" 이 부피분율에 **5.263 %**
  상대차를 낸다.
- 모든 원파일의 **sha256** 과 상별 입자수, **target 별 상태**를 함께 낸다.
- `--n-types` **필수** (`lhs_perc_extract` ⑥ 과 같은 이유: AM_P 가 우연히 0개면 2-type 으로
  보이고 AM_S 가 SE 로 오사상된다).

═══ 계약 ⑥ — 130 단독 ═══

출력은 자기 CSV/JSON 이다.  `design_performance_corpus.csv` 291 행과 **합치지 않는다**
(`DESC-08`: `d_am=0` 40 건이 지금도 학습 입력에 들어가고 `use_porosity_pct` closure 잔차가
ε SD 의 77.82 % 다).  `docs/lhs_design_dataset_20260818.md` §O-4 ⑤ 와 같은 결론.

═══ 상태 코드 ═══

`OK` · `N_A_PHASE_ABSENT`(없는 상 — 존재하는데 무접촉인 `0` 과 다르다) ·
`NOT_PERCOLATING` · `NO_VALID_SAMPLED_PAIR` · `FREE_SURFACE_INVALID` · `INPUT_MISSING`.
⚠ 한 타깃이 미정의라고 **다른 타깃이 있는 행을 통째로 버리지 않는다** (`DESC-01` 의 교훈).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#  ★ 규율 ①: 덤프 읽기·경계 검사·주기 쌍 찾기·상 사상은 **이미 봉인돼 있다**.
from lhs_perc_extract import (  # noqa: E402
    AM_LABELS, BedRefusal, REQUIRED_BC, TYPE_MAP,
    _pairs_within, check_boundary_flags, read_atom_dump,
)

#: 계약 ③ — τ 표본 예산.  legacy 와 같은 수지만 **같은 성분 안에서만** 쓴다.
N_TAU_PAIRS = 200
#: 계약 ③ — legacy 절단 구간 (`dem_analysis_core.py:533`).
TAU_LO, TAU_HI = 1.0, 20.0
#: 접촉 덤프의 면적·겹침 열 (`parse_liggghts.py:47` 과 같은 규약).
COL_AREA, COL_D1, COL_D2 = 'c_cpl[22]', 'c_cpl[7]', 'c_cpl[8]'

STATUS_OK = 'OK'
STATUS_ABSENT = 'N_A_PHASE_ABSENT'
STATUS_NOPERC = 'NOT_PERCOLATING'
STATUS_NOPAIR = 'NO_VALID_SAMPLED_PAIR'
STATUS_MISSING = 'INPUT_MISSING'


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for blk in iter(lambda: fh.read(1 << 20), b''):
            h.update(blk)
    return h.hexdigest()


def last_timestep(path):
    """마지막 `ITEM: TIMESTEP` 값.  atom·contact 덤프 모두에 쓴다 (계약⑤)."""
    ts = None
    with open(path, 'r', encoding='utf-8', errors='replace') as fh:
        want = False
        for ln in fh:
            if want:
                try:
                    ts = int(float(ln.split()[0]))
                except (ValueError, IndexError):
                    pass
                want = False
            elif ln.startswith('ITEM: TIMESTEP'):
                want = True
    if ts is None:
        raise BedRefusal(f'{path}: `ITEM: TIMESTEP` 이 없다')
    return ts


def read_contact_dump(path):
    """**마지막 프레임만**의 (id1, id2, contact_area).

    ⚠ `parse_liggghts.parse_contact_file` 은 모든 프레임 행을 **이어 붙인다**
    (`DESC-06`).  여기서는 마지막 `ITEM: ENTRIES` 블록만 읽는다.
    """
    with open(path, 'r', encoding='utf-8', errors='replace') as fh:
        lines = fh.read().splitlines()
    starts = [i for i, ln in enumerate(lines) if ln.startswith('ITEM: ENTRIES')]
    if not starts:
        raise BedRefusal(f'{path}: `ITEM: ENTRIES` 가 없다 — LIGGGHTS local 덤프가 아니다')
    i = starts[-1]
    headers = lines[i].replace('ITEM: ENTRIES', '').strip().split()
    for col in (COL_D1, COL_D2, COL_AREA):
        if col not in headers:
            raise BedRefusal(
                f'{path}: 접촉 열 {col} 이 없다 (있는 열: {headers}).  '
                'DEM contact-area 규약을 모르는 채로 피복률을 내지 않는다')
    ia, i1, i2 = headers.index(COL_AREA), headers.index(COL_D1), headers.index(COL_D2)
    id1, id2, area = [], [], []
    i += 1
    while i < len(lines) and not lines[i].startswith('ITEM:'):
        v = lines[i].split()
        if len(v) == len(headers):
            id1.append(int(float(v[i1])))
            id2.append(int(float(v[i2])))
            area.append(float(v[ia]))
        i += 1
    return (np.asarray(id1, dtype=np.int64), np.asarray(id2, dtype=np.int64),
            np.asarray(area, dtype=np.float64), tuple(headers))


def plate_z_from_stl(path):
    """`parse_liggghts.parse_mesh_stl` 과 **같은 정의** — 전 꼭짓점 z 평균."""
    zs = []
    with open(path, 'r', encoding='utf-8', errors='replace') as fh:
        for ln in fh:
            p = ln.split()
            if len(p) == 4 and p[0] == 'vertex':
                zs.append(float(p[3]))
    if not zs:
        raise BedRefusal(f'{path}: STL 에 vertex 가 없다')
    return float(np.mean(zs))


def phase_labels(types, n_types):
    """계약⑤ — 선언 밖 type 이 있으면 거부한다."""
    tmap = TYPE_MAP[n_types]
    seen = set(int(t) for t in np.unique(types))
    bad = sorted(seen - set(tmap))
    if bad:
        raise BedRefusal(f'선언(--n-types {n_types}) 밖 type {bad} 이 파일에 있다')
    return np.asarray([tmap[int(t)] for t in types], dtype=object), tmap


def volumes_and_phi(atoms, labels, box_lo, box_hi, plate_z):
    """계약② — φ 는 **기하만**으로, τ·전도도 성공과 무관하게."""
    r = atoms['radius']
    v = (4.0 / 3.0) * np.pi * r ** 3
    lx = float(box_hi[0] - box_lo[0])
    ly = float(box_hi[1] - box_lo[1])
    h = float(plate_z - box_lo[2])
    if not (lx > 0 and ly > 0 and h > 0):
        raise BedRefusal(f'전극 부피가 양수가 아니다: lx={lx} ly={ly} H={h}')
    v_box = lx * ly * h
    is_se = labels == 'SE'
    is_am = np.asarray([l in AM_LABELS for l in labels])
    phi_se = float(v[is_se].sum() / v_box)
    phi_am = float(v[is_am].sum() / v_box)
    eps = 100.0 * (1.0 - float(v.sum()) / v_box)
    return dict(phi_se=phi_se, phi_am=phi_am,
                porosity_sphere_pct_RECORD_ONLY=eps,
                V_box_sim=v_box, H_sim=h, lx_sim=lx, ly_sim=ly,
                closure_residual=phi_se + phi_am + eps / 100.0 - 1.0)


def coverage_hertz(ids, labels, radius, c1, c2, carea):
    """계약① — Hertz 피복률.  단위는 면적/면적이라 **scale 에 불변**이다."""
    pos = {int(a): k for k, a in enumerate(ids)}
    n = len(ids)
    free = 4.0 * np.pi * radius ** 2
    am_se = np.zeros(n)
    for a, b, ar in zip(c1, c2, carea):
        ka, kb = pos.get(int(a)), pos.get(int(b))
        if ka is None or kb is None:
            continue
        la, lb = labels[ka], labels[kb]
        a_am, b_am = la in AM_LABELS, lb in AM_LABELS
        if a_am and b_am:
            free[ka] -= ar
            free[kb] -= ar
        elif a_am and lb == 'SE':
            am_se[ka] += ar
        elif b_am and la == 'SE':
            am_se[kb] += ar

    out, n_cap, n_bad = {}, 0, 0
    per = np.full(n, np.nan)
    for k in range(n):
        if labels[k] not in AM_LABELS:
            continue
        if free[k] <= 0:
            n_bad += 1
            continue
        c = 100.0 * am_se[k] / free[k]
        if c > 100.0:
            c, n_cap = 100.0, n_cap + 1
        per[k] = c

    counts = {}
    for lab in ('AM_P', 'AM_S', 'AM'):
        sel = np.asarray([l == lab for l in labels])
        n_exist = int(sel.sum())
        vals = per[sel & ~np.isnan(per)]
        counts[lab] = dict(n_particles=n_exist, n_valid=int(vals.size))
        if n_exist == 0:
            out[lab] = (None, STATUS_ABSENT)
        elif vals.size == 0:
            out[lab] = (None, 'FREE_SURFACE_INVALID')
        else:
            out[lab] = (float(vals.mean()), STATUS_OK)

    #  ★ 전체 = **실측 입자수 가중** (상 평균의 평균도, 총면적비도, 질량가중도 아니다).
    num = den = 0.0
    for lab in ('AM_P', 'AM_S', 'AM'):
        val, st = out[lab]
        if st == STATUS_OK:
            w = counts[lab]['n_valid']
            num += w * val
            den += w
    total = (float(num / den), STATUS_OK) if den > 0 else (None, 'FREE_SURFACE_INVALID')
    return dict(per_phase=out, total=total, counts=counts,
                n_capped=n_cap, n_free_surface_invalid=n_bad)


def tortuosity_se(atoms, labels, box_lo, box_hi, n_pairs=N_TAU_PAIRS, seed=42):
    """계약③ — fallback source 승격 **없음**, 쌍은 **같은 성분 안에서만**."""
    import networkx as nx

    sel = np.flatnonzero(np.asarray([l == 'SE' for l in labels]))
    base = dict(tau_mean=None, tau_median=None, tau_mean_untruncated=None,
                n_sampled=0, n_valid=0, n_truncated=0, status=STATUS_NOPERC,
                tau_convention='harvest_v1/solid_zrange/rSEmax/no_fallback/same_component')
    if sel.size < 2:
        base['status'] = STATUS_ABSENT
        return base

    r_all, z_all = atoms['radius'], atoms['z']
    z_lo = float((z_all - r_all).min())
    z_hi = float((z_all + r_all).max())
    xyz = np.column_stack([atoms['x'][sel], atoms['y'][sel], atoms['z'][sel]])
    rad = r_all[sel]
    t = float(rad.max())
    lx = float(box_hi[0] - box_lo[0])
    ly = float(box_hi[1] - box_lo[1])

    pairs = _pairs_within(xyz, rad, lx, ly, z_pad=t)
    G = nx.Graph()
    G.add_nodes_from(range(sel.size))
    for i, j in pairs:
        d = float(np.linalg.norm(xyz[i] - xyz[j]))
        G.add_edge(int(i), int(j), distance=d)

    bot = set(np.flatnonzero((xyz[:, 2] - rad) <= z_lo + t).tolist())
    top = set(np.flatnonzero((xyz[:, 2] + rad) >= z_hi - t).tolist())
    if not bot or not top:
        return base

    cands = []
    for comp in nx.connected_components(G):
        cb, ct = comp & bot, comp & top
        if cb and ct:
            cands.append((sorted(cb), sorted(ct)))
    if not cands:                                   # ⇒ 유한 τ 를 내지 않는다
        return base

    rng = np.random.default_rng(seed)
    allp = [(s, tt) for cb, ct in cands for s in cb for tt in ct if s != tt]
    if not allp:
        base['status'] = STATUS_NOPAIR
        return base
    idx = rng.permutation(len(allp))[:n_pairs]
    taus = []
    for k in idx:
        s, tt = allp[int(k)]
        try:
            path = nx.shortest_path(G, s, tt, weight='distance')
        except nx.NetworkXNoPath:                   # 같은 성분이라 원래 안 난다
            continue
        plen = sum(float(np.linalg.norm(xyz[path[m]] - xyz[path[m + 1]]))
                   for m in range(len(path) - 1))
        dz = abs(float(xyz[tt, 2] - xyz[s, 2]))
        if dz > 0:
            taus.append(plen / dz)

    if not taus:
        base['status'] = STATUS_NOPAIR
        base['n_sampled'] = int(len(idx))
        return base
    raw = np.asarray(taus)
    keep = raw[(raw >= TAU_LO) & (raw < TAU_HI)]
    base.update(n_sampled=int(len(idx)), n_valid=int(raw.size),
                n_truncated=int(raw.size - keep.size),
                tau_mean_untruncated=float(raw.mean()))
    if keep.size == 0:
        base['status'] = STATUS_NOPAIR
        return base
    base.update(tau_mean=float(keep.mean()), tau_median=float(np.median(keep)),
                status=STATUS_OK)
    return base


def harvest(atom_path, contact_path, n_types, case, plate_z=None, mesh_path=None,
            allow_any_bc=False, n_pairs=N_TAU_PAIRS):
    for p in (atom_path, contact_path):
        if not os.path.exists(p):
            raise BedRefusal(f'{p}: 없다')
    ts_a, ts_c = last_timestep(atom_path), last_timestep(contact_path)
    if ts_a != ts_c:
        raise BedRefusal(
            f'TIMESTEP 불일치: atom={ts_a} contact={ts_c}.  '
            '종류별 최신 파일을 독립 선택하면 다른 프레임이 섞인다 (DESC-06)')

    atoms, box_lo, box_hi, bc = read_atom_dump(atom_path)
    bc_note = check_boundary_flags(bc, allow_any_bc)
    if 'id' not in atoms:
        pass
    labels, tmap = phase_labels(atoms['type'], n_types)

    if (plate_z is None) == (mesh_path is None):
        raise BedRefusal('플래튼 높이는 --mesh 또는 --plate-z 로 **정확히 하나** 주어야 한다.  '
                         '추정하지 않는다 (DESC-06: 최고 입자 중심 추정은 5.263 % 상대차)')
    if mesh_path is not None:
        if not os.path.exists(mesh_path):
            raise BedRefusal(f'{mesh_path}: 없다')
        plate_z = plate_z_from_stl(mesh_path)
        h_src = 'mesh_stl'
    else:
        h_src = 'cli_explicit'

    phi = volumes_and_phi(atoms, labels, box_lo, box_hi, plate_z)

    ids = _atom_ids(atom_path)
    c1, c2, carea, cheaders = read_contact_dump(contact_path)
    cov = coverage_hertz(ids, labels, atoms['radius'], c1, c2, carea)
    tau = tortuosity_se(atoms, labels, box_lo, box_hi, n_pairs=n_pairs)

    raw = {'atom': dict(path=os.path.basename(atom_path), sha256=sha256_of(atom_path)),
           'contact': dict(path=os.path.basename(contact_path),
                           sha256=sha256_of(contact_path))}
    if mesh_path:
        raw['mesh'] = dict(path=os.path.basename(mesh_path), sha256=sha256_of(mesh_path))

    cp, sp = cov['per_phase']['AM_P']
    cs, ss = cov['per_phase']['AM_S']
    ca, sa = cov['per_phase']['AM']
    ct, st = cov['total']
    if n_types == 2:                       # 2-type 침대는 AM 이 한 상이다
        cp, sp = None, STATUS_ABSENT
        cs, ss = None, STATUS_ABSENT
        ct, st = (ca, sa)

    return dict(
        case=case, timestep=ts_a, n_types=n_types, type_map=tmap,
        phase_counts={k: int(sum(1 for l in labels if l == k)) for k in tmap.values()},
        boundary=bc_note, plate_z_sim=float(plate_z), plate_z_source=h_src,
        phi_se=phi['phi_se'], phi_am=phi['phi_am'],
        porosity_sphere_pct_RECORD_ONLY=phi['porosity_sphere_pct_RECORD_ONLY'],
        closure_residual=phi['closure_residual'],
        coverage_AM_P_hertz_pct=cp, coverage_AM_S_hertz_pct=cs,
        coverage_AM_total_hertz_pct=ct, coverage_AM_only_hertz_pct=ca,
        tortuosity_dijkstra_SE=tau['tau_mean'],
        status=dict(phi=STATUS_OK, porosity=STATUS_OK,
                    coverage_AM_P=sp, coverage_AM_S=ss, coverage_AM_total=st,
                    tortuosity=tau['status']),
        tau_detail=tau, coverage_detail=dict(
            n_capped=cov['n_capped'],
            n_free_surface_invalid=cov['n_free_surface_invalid'],
            counts=cov['counts'], contact_headers=cheaders),
        V_box_sim=phi['V_box_sim'], raw=raw,
        contract='codex_verdict_lhs_descriptors_20260913 §7 (1~6)')


def _atom_ids(path):
    """원자 덤프의 `id` 열 (접촉 덤프의 id 와 맞춘다)."""
    with open(path, 'r', encoding='utf-8', errors='replace') as fh:
        lines = fh.read().splitlines()
    starts = [i for i, ln in enumerate(lines) if ln.startswith('ITEM: ATOMS')]
    i = starts[-1]
    headers = lines[i].replace('ITEM: ATOMS', '').strip().split()
    if 'id' not in headers:
        raise BedRefusal(f'{path}: `id` 열이 없다 — 접촉 덤프와 입자를 맞출 수 없다')
    k = headers.index('id')
    out = []
    i += 1
    while i < len(lines) and not lines[i].startswith('ITEM:'):
        v = lines[i].split()
        if len(v) == len(headers):
            out.append(int(float(v[k])))
        i += 1
    return np.asarray(out, dtype=np.int64)


# ──────────────────────────────────────────────────────────────────────────────
# 자기검사 — **각 P1 의 반례를 먼저 재현**한다 (규율 ②)
# ──────────────────────────────────────────────────────────────────────────────

_FAILS = []


def chk(name, ok):
    print(('  ✓ ' if ok else '  ✗ ') + name)
    if not ok:
        _FAILS.append(name)


def neg(name, fn, want=BedRefusal):
    """음성대조 — **그 오류 종류로** 거부해야 통과.  아무 예외나 세지 않는다.

    (`PA12-09`: 어댑터의 ⑨ 가 `SystemExit` 이면 전부 성공으로 세어 **장식**이었다.)
    """
    try:
        fn()
    except want as e:
        print(f'  ✓ {name} — 거부: {str(e)[:72]}')
        return
    except Exception as e:                                    # noqa: BLE001
        chk(f'{name} (기대 {want.__name__}, 실제 {type(e).__name__}: {e})', False)
        return
    chk(f'{name} (거부하지 않았다)', False)


def _atom_file(tmp, rows, name='atom_100.liggghts', ts=100,
               lo=(0.0, 0.0, 0.0), hi=(10.0, 10.0, 20.0), bc='pp pp ff'):
    """rows = (id, x, y, z, radius, type)"""
    p = os.path.join(tmp, name)
    with open(p, 'w') as fh:
        fh.write(f'ITEM: TIMESTEP\n{ts}\nITEM: NUMBER OF ATOMS\n{len(rows)}\n')
        fh.write(f'ITEM: BOX BOUNDS {bc}\n')
        for k in range(3):
            fh.write(f'{lo[k]} {hi[k]}\n')
        fh.write('ITEM: ATOMS id x y z radius type\n')
        for r in rows:
            fh.write(' '.join(str(x) for x in r) + '\n')
    return p


def _contact_file(tmp, rows, name='contact_100.liggghts', ts=100, headers=None):
    """rows = (id1, id2, area)"""
    p = os.path.join(tmp, name)
    hd = headers or [COL_D1, COL_D2, COL_AREA]
    with open(p, 'w') as fh:
        fh.write(f'ITEM: TIMESTEP\n{ts}\nITEM: NUMBER OF ENTRIES\n{len(rows)}\n')
        fh.write('ITEM: ENTRIES ' + ' '.join(hd) + '\n')
        for r in rows:
            fh.write(' '.join(str(x) for x in r) + '\n')
    return p


def _stl(tmp, z=20.0, name='mesh.stl'):
    p = os.path.join(tmp, name)
    with open(p, 'w') as fh:
        fh.write('solid p\nfacet normal 0 0 1\nouter loop\n')
        for xy in ((0, 0), (1, 0), (0, 1)):
            fh.write(f'vertex {xy[0]} {xy[1]} {z}\n')
        fh.write('endloop\nendfacet\nendsolid p\n')
    return p


def selftest():
    import tempfile

    print('lhs_descriptor_harvest — 자기검사 (계약 6개 + P1 반례)')
    with tempfile.TemporaryDirectory() as tmp:

        # ── ① DESC-01 반례: τ 가 없어도 φ 는 나온다 ──────────────────────────
        #  SE 두 알이 서로 안 닿고 슬래브도 못 채운다 ⇒ τ = NOT_PERCOLATING.
        rows = [(1, 2.0, 2.0, 1.0, 0.5, 1), (2, 8.0, 8.0, 18.0, 0.5, 2)]
        a = _atom_file(tmp, rows)
        c = _contact_file(tmp, [])
        r = harvest(a, c, 2, 'desc01', mesh_path=_stl(tmp))
        chk('① DESC-01: τ 실패인데 phi_se 가 나온다',
            r['status']['tortuosity'] != STATUS_OK and r['phi_se'] is not None)
        chk('① DESC-01: phi_am 도 나온다', r['phi_am'] is not None)
        v = (4 / 3) * np.pi * 0.5 ** 3
        chk('① phi 값이 기하 그대로 (V_i/V_B)',
            abs(r['phi_se'] - v / 2000.0) < 1e-12 and abs(r['phi_am'] - v / 2000.0) < 1e-12)
        chk('① 공극률 closure 가 항등식', abs(r['closure_residual']) < 1e-12)

        # ── ② DESC-02 ①: 비관통에 유한 τ 를 주지 않는다 ────────────────────
        #  아래판에 닿는 SE 3알(고립) + 위쪽에 닿는 기둥 3알(아래판 미연결).
        rows = [(1, 1.0, 1.0, 0.5, 0.5, 2), (2, 3.0, 1.0, 0.5, 0.5, 2),
                (3, 5.0, 1.0, 0.5, 0.5, 2),
                (4, 9.0, 9.0, 18.5, 0.5, 2), (5, 9.0, 9.0, 19.4, 0.5, 2),
                (6, 9.0, 9.0, 19.9, 0.5, 2), (7, 5.0, 5.0, 10.0, 0.5, 1)]
        a2 = _atom_file(tmp, rows, name='atom_200.liggghts', ts=200)
        c2 = _contact_file(tmp, [], name='contact_200.liggghts', ts=200)
        r2 = harvest(a2, c2, 2, 'desc02a', mesh_path=_stl(tmp))
        chk('② DESC-02①: 비관통 → τ = None · NOT_PERCOLATING',
            r2['tortuosity_dijkstra_SE'] is None
            and r2['status']['tortuosity'] == STATUS_NOPERC)

        # ── ③ DESC-02 ②: 관통 성분이 있으면 예산이 무경로 쌍에 안 샌다 ──────
        #  관통 기둥 하나 + 무관한 고립 SE 덩어리 300알.
        col = [(i + 1, 5.0, 5.0, 0.5 + 0.9 * i, 0.5, 2) for i in range(22)]
        junk = [(1000 + i, 1.0 + 0.01 * i, 1.0, 10.0, 0.05, 2) for i in range(300)]
        a3 = _atom_file(tmp, col + junk, name='atom_300.liggghts', ts=300,
                        hi=(10.0, 10.0, 21.0))
        c3 = _contact_file(tmp, [], name='contact_300.liggghts', ts=300)
        r3 = harvest(a3, c3, 2, 'desc02b', mesh_path=_stl(tmp, z=21.0))
        chk('③ DESC-02②: 무경로 쌍이 예산을 안 먹는다 (τ 가 나온다)',
            r3['status']['tortuosity'] == STATUS_OK and r3['tortuosity_dijkstra_SE'] is not None)
        chk('③ 직선 기둥이면 τ ≈ 1', abs(r3['tortuosity_dijkstra_SE'] - 1.0) < 1e-6)
        chk('③ 표본이 전부 유효 (무경로 0건)',
            r3['tau_detail']['n_valid'] == r3['tau_detail']['n_sampled'])

        # ── ④ 계약①: 전체 피복률은 **실측 입자수 가중** ─────────────────────
        #  판정문 반례: P 1개 10 % · S 3개 90 % → 70 % (상평균평균 50 · 면적비 30).
        #  자유표면 4πr² = 4π, AM–SE 면적을 c% 가 되게 준다.
        fp = 4.0 * np.pi
        rows = [(1, 1.0, 1.0, 5.0, 1.0, 1), (2, 3.0, 1.0, 5.0, 1.0, 2),
                (3, 5.0, 1.0, 5.0, 1.0, 2), (4, 7.0, 1.0, 5.0, 1.0, 2),
                (90, 1.0, 5.0, 5.0, 1.0, 3), (91, 3.0, 5.0, 5.0, 1.0, 3),
                (92, 5.0, 5.0, 5.0, 1.0, 3), (93, 7.0, 5.0, 5.0, 1.0, 3)]
        con = [(1, 90, 0.10 * fp), (2, 91, 0.90 * fp),
               (3, 92, 0.90 * fp), (4, 93, 0.90 * fp)]
        a4 = _atom_file(tmp, rows, name='atom_400.liggghts', ts=400)
        c4 = _contact_file(tmp, con, name='contact_400.liggghts', ts=400)
        r4 = harvest(a4, c4, 3, 'cov', mesh_path=_stl(tmp))
        chk('④ P 평균 = 10 %', abs(r4['coverage_AM_P_hertz_pct'] - 10.0) < 1e-9)
        chk('④ S 평균 = 90 %', abs(r4['coverage_AM_S_hertz_pct'] - 90.0) < 1e-9)
        chk('④ 전체 = 70 % (상평균평균 50 이 아니다)',
            abs(r4['coverage_AM_total_hertz_pct'] - 70.0) < 1e-9)

        # ── ⑤ 계약④: Hertz 는 길이 scale 에 불변 ────────────────────────────
        k = 1000.0
        rows_s = [(r[0], r[1] * k, r[2] * k, r[3] * k, r[4] * k, r[5]) for r in rows]
        con_s = [(x[0], x[1], x[2] * k * k) for x in con]
        a5 = _atom_file(tmp, rows_s, name='atom_500.liggghts', ts=500,
                        hi=(10.0 * k, 10.0 * k, 20.0 * k))
        c5 = _contact_file(tmp, con_s, name='contact_500.liggghts', ts=500)
        r5 = harvest(a5, c5, 3, 'scale', plate_z=20.0 * k)
        chk('⑤ 계약④: scale ×1000 에도 Hertz 피복률 불변',
            abs(r5['coverage_AM_total_hertz_pct']
                - r4['coverage_AM_total_hertz_pct']) < 1e-9)
        chk('⑤ φ 도 불변 (무차원)', abs(r5['phi_se'] - r4['phi_se']) < 1e-12)

        # ── ⑥ DESC-05: 없는 상 = N/A, 존재하는데 무접촉 = 0 ─────────────────
        rows = [(1, 1.0, 1.0, 5.0, 1.0, 2), (90, 5.0, 5.0, 5.0, 1.0, 3)]
        a6 = _atom_file(tmp, rows, name='atom_600.liggghts', ts=600)
        c6 = _contact_file(tmp, [], name='contact_600.liggghts', ts=600)
        r6 = harvest(a6, c6, 3, 'absent', mesh_path=_stl(tmp))
        chk('⑥ DESC-05: 없는 AM_P → N/A (0 이 아니다)',
            r6['coverage_AM_P_hertz_pct'] is None
            and r6['status']['coverage_AM_P'] == STATUS_ABSENT)
        chk('⑥ DESC-05: 존재하는데 무접촉 AM_S → 0.0',
            r6['coverage_AM_S_hertz_pct'] == 0.0
            and r6['status']['coverage_AM_S'] == STATUS_OK)

        # ── ⑦ DESC-05: free surface ≤ 0 은 0 이 아니라 invalid ──────────────
        rows = [(1, 1.0, 1.0, 5.0, 1.0, 1), (2, 3.0, 1.0, 5.0, 1.0, 1),
                (90, 5.0, 5.0, 5.0, 1.0, 3)]
        con = [(1, 2, 99.0 * fp), (1, 90, 0.5 * fp)]
        a7 = _atom_file(tmp, rows, name='atom_700.liggghts', ts=700)
        c7 = _contact_file(tmp, con, name='contact_700.liggghts', ts=700)
        r7 = harvest(a7, c7, 3, 'freebad', mesh_path=_stl(tmp))
        chk('⑦ DESC-05: 분모붕괴가 0 으로 안 접힌다',
            r7['coverage_detail']['n_free_surface_invalid'] == 2)

        # ── ⑧ 음성대조: DESC-06 — 프레임이 섞이면 거부 ──────────────────────
        neg('⑧ DESC-06: atom_100 + contact_200 을 거부',
            lambda: harvest(a, c2, 2, 'mix', mesh_path=_stl(tmp)))

        # ── ⑨ 음성대조: 플래튼 높이 추정 금지 ───────────────────────────────
        neg('⑨ 계약⑤: mesh 도 --plate-z 도 없으면 거부',
            lambda: harvest(a, c, 2, 'noh'))
        neg('⑨ 계약⑤: 둘 다 주면 거부',
            lambda: harvest(a, c, 2, 'bothh', plate_z=20.0, mesh_path=_stl(tmp)))

        # ── ⑩ 음성대조: 선언 밖 type · 경계 플래그 ──────────────────────────
        bad = _atom_file(tmp, [(1, 1.0, 1.0, 5.0, 0.5, 9)],
                         name='atom_900.liggghts', ts=900)
        neg('⑩ 계약⑤: 선언 밖 type 을 거부',
            lambda: harvest(bad, _contact_file(tmp, [], name='contact_900.liggghts', ts=900),
                            2, 'badtype', mesh_path=_stl(tmp)))
        bbc = _atom_file(tmp, [(1, 1.0, 1.0, 5.0, 0.5, 1)],
                         name='atom_950.liggghts', ts=950, bc='pp pp pp')
        neg('⑩ 경계 플래그가 규약과 다르면 거부',
            lambda: harvest(bbc, _contact_file(tmp, [], name='contact_950.liggghts', ts=950),
                            2, 'badbc', mesh_path=_stl(tmp)))

        # ── ⑪ 음성대조: 접촉 면적 열이 없으면 거부 ──────────────────────────
        noarea = _contact_file(tmp, [(1, 2)], name='contact_960.liggghts', ts=960,
                               headers=[COL_D1, COL_D2])
        a11 = _atom_file(tmp, [(1, 1.0, 1.0, 5.0, 0.5, 1), (2, 2.0, 1.0, 5.0, 0.5, 2)],
                         name='atom_960.liggghts', ts=960)
        neg('⑪ 계약④: contact_area 열이 없으면 거부 (규약을 모른 채 안 낸다)',
            lambda: harvest(a11, noarea, 2, 'noarea', mesh_path=_stl(tmp)))

        # ── ⑫ 음성대조가 장식이 아닌지 (PA12-09 의 교훈) ────────────────────
        #  ⑧ 의 가드를 퇴행시키면 ⑧ 이 **반드시** 깨져야 한다.
        import lhs_descriptor_harvest as M
        keep = M.last_timestep
        M.last_timestep = lambda p: 0                     # 항상 같은 값 = 검사 무력화
        broke = False
        try:
            M.harvest(a, c2, 2, 'mut', mesh_path=_stl(tmp))
        except BedRefusal:
            broke = True
        except Exception:                                 # noqa: BLE001
            broke = True
        M.last_timestep = keep
        chk('⑫ PA12-09: TIMESTEP 가드를 퇴행시키면 ⑧ 이 실제로 뚫린다 (대조가 살아있다)',
            not broke)

        # ── ⑬ 계약⑥: 291 코퍼스를 읽지 않는다 (정적) ────────────────────────
        src = open(os.path.abspath(__file__), encoding='utf-8').read()
        chk('⑬ 계약⑥: design_performance_corpus 를 읽는 코드가 없다',
            'design_performance_corpus' not in src.split('"""')[2])
        chk('⑬ full_metrics.json 을 읽는 코드가 없다',
            'full_metrics' not in src.split('"""')[2])
        chk('⑬ DESC-03: plastic_coverage 를 부르지 않는다',
            'plastic_coverage' not in src.split('"""')[2])

    print()
    if _FAILS:
        print(f'✗ {len(_FAILS)} 건 실패')
        for f in _FAILS:
            print('   -', f)
        return 1
    print('✓ 전부 통과   ⚠ 이 통과는 **계약이 도구에 박혔다**는 뜻이지 '
          '실제 130 배치가 깨끗하다는 뜻이 아니다')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description='LHS 130 구조 디스크립터 수확 — 판정문 §7 계약 6개를 고정한다')
    ap.add_argument('--atom')
    ap.add_argument('--contact')
    ap.add_argument('--mesh', help='플래튼 STL (--plate-z 와 택일)')
    ap.add_argument('--plate-z', type=float, help='플래튼 높이 직접 지정 (--mesh 와 택일)')
    ap.add_argument('--n-types', type=int, choices=(2, 3),
                    help='필수 — 자동 추론은 거부한다 (AM_P 가 0개면 오사상된다)')
    ap.add_argument('--case', default='')
    ap.add_argument('--allow-any-bc', action='store_true')
    ap.add_argument('--n-pairs', type=int, default=N_TAU_PAIRS)
    ap.add_argument('--out', help='결과 JSON 경로')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()
    if not (a.atom and a.contact and a.n_types):
        ap.error('--atom · --contact · --n-types 는 필수다')
    try:
        r = harvest(a.atom, a.contact, a.n_types, a.case or os.path.basename(a.atom),
                    plate_z=a.plate_z, mesh_path=a.mesh,
                    allow_any_bc=a.allow_any_bc, n_pairs=a.n_pairs)
    except BedRefusal as e:
        print(f'거부 — {e}', file=sys.stderr)
        return 2
    txt = json.dumps(r, ensure_ascii=False, indent=1, default=str)
    if a.out:
        open(a.out, 'w', encoding='utf-8').write(txt + '\n')
        print(f'→ {a.out}')
    else:
        print(txt)
    return 0


if __name__ == '__main__':
    sys.exit(main())
