---
title: "mid-Ni NCA721 formation 위키 킥오프 세션 — 사용자의 연구 설명 원문과 설계 결정 (2026-09-11)"
source_url: local:claude-code-session/2026-09-11-midni-formation-wiki-kickoff
ingested: 2026-09-11
sha256: 987bfbde3ebfed3ec9ae26d7a3ae9ddefea5588af1c2ad20140875c31faaa4b9
---

# mid-Ni NCA721 formation 위키 킥오프 세션 (2026-09-11)

수집 목적: 이 저장소를 **sulfide ASSB mid-Ni NCA721 formation(pre-conditioning) 프로토콜 최적화 연구**의
mothership 위키 + 로컬 webapp 으로 세우기로 한 세션의 **설계 기록**. 사용자의 연구 설명은 이 위키의
시드 페이지(protocol·experiment·mechanism·entity·question)의 1차 근거이므로 **원문 그대로** 보존한다.
표기 규칙: 이 파일의 인용 블록은 전부 `[인쇄]`(사용자 원문)이고, §2 이하는 세션의 `[해석]` 이다.

## 1. 사용자의 연구 설명 (원문, 2026-09-11)

> 나는 현재 sulfide 기반 all-solid-state battery(ASSB)에서 mid-Ni 양극재 NCA721의 formation(pre-conditioning)
> 프로토콜 최적화 연구를 수행하고 있어. 논문 main concept은 "4.4 V 고전압 구동을 위한 Mid-/High-Ni 양극재 열화
> 메커니즘 규명 및 해당 메커니즘 기반 pre-conditioning 사이클 설계"이고, 핵심 질문은 formation 충전 cut-off
> 전압이 장기 사이클 성능과 열화 메커니즘(CEI 형성, LPSCl 산화 분해, lattice oxygen 관여, 계면 contact loss
> 등)에 어떤 영향을 주는지야.
>
> 셀 구성은 NCA721 건식(dry-processed) 복합양극(2 mAh cm⁻² 기준) | argyrodite LPSCl(Li6PS5Cl) | Li-In 합금
> 음극이야. 10Φ 몰드 기준으로 양극+전해질은 462 MPa에서 2.5 min, 음극(In foil 9Φ + Li foil 4Φ)은 277 MPa에서
> 5 min 동안 가압해서 제작하고, 구동압은 100 MPa야. Formation은 0.1C/0.1C 2 cycles로 고정하고 충전 cut-off를
> 3.6/3.8/4.0/4.2/4.4/4.6 V vs. Li/Li⁺로 바꿔가며 평가하고 있고, main cycle은 2.5–4.4 V vs. Li/Li⁺, 0.5C,
> 45 °C, 200 cycles야. 보조 실험으로는 main cycle 두 번째 사이클 SOC 100%에서의 EIS(RT 온도 평형 후 측정),
> formation 후 24 h rest 전압 tracking, NCA721 양극 | Ag-C 음극 | Ag wire 기준전극 3-전극 셀 EIS/DRT,
> Mid-Ni || LTO 셀로 4.6 V까지 0.05C 충전하며 operando 압력 측정, 200 cycle 후 SOC 100%로 수득한 양극의
> 사후분석(XRD, XPS, ToF-SIMS depth profiling, FIB-SEM, HAADF-STEM/FFT, Raman)을 진행 또는 계획 중이야.
> High-Ni 비교 실험과 anode-free 저압 파우치셀 평가는 후순위로 이어질 예정이야.
>
> Raw 충방전 데이터는 전부 vs. In/Li-In 기준으로 기록되어 있어서 +0.62 V를 더해야 vs. Li/Li⁺ 값이 되고,
> 용량은 항상 비용량(mAh g⁻¹)으로 다뤄.

> 내가 연구하고 있는 내용은 이거이고, 이제 이 repo를 위 내용과 관련된 db, md 등으로 채워나갈 거야. 첨부한
> llm-wiki를 참고해서 repo를 체계적으로 구축해주고, [선행 브랜치의 webapp 을] 전적으로 reference로 삼아서
> webapp을 구축해줘. 기능은 앞으로 더 추가되겠지만, 우선은 그 브랜치의 webapp 포맷과 논문 에이전트를 위 연구
> 내용에 맞춰 prototype으로 만들어줘. 앞으로 이 웹앱을 내 연구를 발전시키는 창구로 쓸 거야. (…) 나는 ubuntu를
> 사용하고 있어서 관련된 명령어들은 wsl 환경에서 사용할 수 있게 해주고 나중에 host 주소 들어가는 거 관련해서
> alias로 li2s만 치면 들어갈 수 있게 해줘. 앞으로 내가 주로 할거는 지금까지 내가 모아놨던 li2s 또는 sulfur 관련된
> 논문을 너한테 공유를 해주고 그걸 논문 에이전트로 db화를 하고 서로 논문끼리 비교를 하고, 이 대시보드에서는 그
> 논문 reference를 바탕으로 나랑 얘기해줬으면 좋겠어. 관련해서 시간걸려도 되니까 확실하게 구축을 해줘.

> [1. Repo / wiki 구조]
> - llm-wiki 구조를 따르되 다음 카테고리를 기본으로 만들어줘: papers(논문별 노트), mechanisms(CEI, LPSCl
>   전압대별 산화 분해 산물, Ni/Co/O redox와 산소 방출, H2–H3 상전이 판별 분석법, mid-Ni vs high-Ni 열화 차이,
>   mechano-electrochemical healing, 양극/전해질/음극 계면 열화), protocols(formation/pre-conditioning 프로토콜,
>   셀 제작 조건), experiments(DOE, cell registry), comparisons(논문 간 비교표).
> - 루트 CLAUDE.md에 맨 아래 [절대 규칙]을 명시해줘.
>
> [2. 논문 에이전트]
> - 입력은 PDF(+Supplementary). DOI 기준으로 중복 제거하고(같은 논문이 파일명만 다르게 여러 번 들어올 수 있음),
>   Supplementary는 본문 논문에 연결해줘.
> - 추출 스키마 (값이 없으면 null, 추측으로 채우지 말 것):
>   · 서지: 저자, 연도, 저널, DOI
>   · 양극: 조성 원문 표기 그대로(NCA/NCM/LCO, Ni 함량), single/poly-crystal, 코팅 여부·종류, 전극 공정
>     (dry/slurry/powder), loading(mg cm⁻², mAh cm⁻²), 복합양극 조성비
>   · 전해질 종류(LPSCl, LGPS, LPS 등), 음극 종류(Li-In(조성 명시 시 기록), Li, Ag-C, anode-free, LTO 등)
>   · 전압: 논문 원문 값과 기준전극(vs. Li/Li⁺, vs. In/Li-In 등)을 그대로 저장하고, 변환값은 사용한 offset과
>     함께 별도 필드에 저장
>   · Formation/pre-conditioning: cut-off, C-rate, cycle 수, rest 시간, 온도
>   · Main cycle: 전압창, C-rate, 온도, stack pressure(제작압/구동압 구분), 사이클 수
>   · 성능: 초기 방전 비용량, ICE, N cycle 후 capacity retention, 과전압/voltage hysteresis 추세
>   · 분석 기법: XPS, ToF-SIMS, XRD, TEM, FIB-SEM, EIS/DRT, dQ/dV, operando pressure 등
>   · 열화 메커니즘 주장: 분해 산물(S, P2Sx, LiCl, sulfate/phosphate 등)과 발생 전압대, rock-salt 상 형성,
>     crack/void, lattice oxygen 관여, CEI 특성 — 주장마다 근거 figure/page를 기록
> - 비교 기능: 논문 간 조건·성능 비교표, "formation cut-off 또는 상한 전압 vs 열화 거동" 축으로 정렬/필터, 내
>   DOE 전압창(2.5–4.4 V vs. Li/Li⁺, formation 3.6–4.6 V)과 겹치는 조건과 벗어나는 조건을 표시.
> - 초기 투입 예정 논문(파일 제목 기준): Chemo-Mechanical Behavior of High- and Mid-Ni Cathodes in Sulfide-Based
>   ASSBs (Small Structures 2026, Suppl. 포함), Compromise between energy density and stability (capacity
>   balancing), Engineering Stable Decomposition Products on Cathode Surfaces to Enable High Voltage,
>   Mechanoelectrochemical healing at NCM/LPSCl interfaces, Interfacial degradation of the NMC/Li6PS5Cl
>   composite cathode, Decoupling first-cycle capacity loss mechanisms in sulfide SSBs, Li10GeP2S12/NCM622
>   interface stability, Failure mechanisms of dry-processed thick electrodes, Dual-ion modification for
>   high-voltage mid-Ni single-crystal cathode, High/Mid-Ni Nano Convergence modeling paper.
>
> [3. 대시보드 채팅]
> - DB에 들어간 논문 reference를 바탕으로 나와 대화해줘. 모든 주장에는 출처(1저자, 연도, 저널, figure/page)를
>   붙이고, DB에 근거가 없는 내용은 "DB 외 일반 지식/추론"으로 명확히 구분해줘.
> - 논문끼리 또는 논문과 내 실험을 비교할 때 전압 기준전극, 양극 조성, 온도, 압력, loading 차이를 자동으로 짚어줘.
> - 한국어로 대화하되 전문 용어는 영어로 유지하고, 영어 용어를 설명할 때는 IPA 발음기호와 강세 위치를 함께 표기해줘.
>
> [4. (확장 대비) 셀 데이터 모듈 — prototype에서는 스키마와 import까지만]
> - Raw CSV 컬럼: timestamp, test_time_s, step_time_s, cycle_time_s, channel, step_index, total_step,
>   cycle_index, run_status, running_status, cell_status, i_range_index, i_range, voltage, current,
>   charge_q (Ah), discharge_q (Ah), charge_e (Wh), discharge_e (Wh), aux_voltage, temperature, ocp.
>   UTF-8 BOM이 붙어 있으니 utf-8-sig로 읽을 것.
> - 사이클 요약 CSV 컬럼: cycle, charge/discharge_capacity (mAh/g, mAh), coulombic_efficiency,
>   charge/discharge_energy, energy_efficiency, mean_charge/discharge_voltage, voltage_hysteresis, v_max,
>   v_min, duration, points, complete.
> - 파일명 규칙이 일관되지 않음 (예: Dcell14_mid_Ni___0.0189g_4.0V_..., cell16_CONT_4.0V_18.5mg_...,
>   Dcell49mid_Ni___...; 질량 단위 g/mg 혼재, 전극 질량인지 활물질 질량인지 불명확). 파일명 파싱은 제안값으로만
>   쓰고, cell registry(cell ID, formation cut-off, 활물질 질량, loading, 펀칭 지름, 제작압/구동압, 상태
>   (cycling/EIS/수득 완료 등), 비고)를 source of truth로 둬줘.
> - 전압은 vs. In/Li-In 원본을 보존하고 vs. Li/Li⁺ 변환값(+0.62 V, config 상수로 관리)을 함께 제공, 용량은 mAh/g.
> - cut-off 조건별 그래프 색상은 config 파일에서 내가 직접 지정할 수 있게 해줘.
> - LLM 컨텍스트에 raw CSV를 통째로 넣지 말고, pandas로 계산한 요약 통계만 넘겨줘.
>
> [5. 환경]
> - 나는 Ubuntu(WSL)를 쓰니까 설치·실행 명령어는 WSL 환경 기준으로 작성하고, host 주소 접속은 ~/.bashrc에
>   alias를 걸어서 midni 만 치면 들어갈 수 있게 해줘.
>
> [절대 규칙]
> - 내 실험 데이터의 양극재는 전부 NCA721이다. NCM721로 바꿔 부르거나 그렇게 해석하지 말 것. 논문 속 양극 조성도
>   원문 표기(NCM622, NCM85 등) 그대로 두고 NCA↔NCM 간 임의 변환 금지.
> - 전압에는 항상 기준전극을 표기할 것. 변환식: vs. Li/Li⁺ = vs. In/Li-In + 0.62 V (방향 혼동 금지).
> - 비용량(mAh g⁻¹)과 면적용량(mAh cm⁻²)을 혼동하지 말 것. 절대용량(mAh)으로 보고하지 말 것.
> - 충전 = delithiation, 방전 = lithiation. 용어 혼동 금지.
>
> 앞으로 내가 주로 할 일은 그동안 모아둔 mid-Ni/high-Ni 양극, sulfide 전해질 계면, formation 프로토콜 관련
> 논문을 공유해서 논문 에이전트로 DB화하고, 논문끼리 비교하고, 이 대시보드에서 그 reference를 바탕으로 내 실험
> 결과를 해석하는 거야. 시간 걸려도 되니까 확실하게 구축해줘.

세션 중 추가 지시 (원문): "그리고 단독적인 브랜치에 만들어줘" · "main 말고".

## 2. 설명에서 읽어 낸 사실 (1차 근거로 삼는 것)

| # | 사실 | 확실성 |
|---|---|---|
| F1 | 시스템: **sulfide 기반 ASSB**, 양극재 **NCA721 (mid-Ni)**, 건식(dry-processed) 복합양극, **2 mAh cm⁻² 기준** | 사용자 진술 |
| F2 | 고체전해질 **argyrodite LPSCl = Li6PS5Cl** | 사용자 진술 |
| F3 | 음극 **Li-In 합금**: In foil 9Φ + Li foil 4Φ (조성비·두께는 미기재) | 사용자 진술 |
| F4 | 셀 제작 (10Φ 몰드): 양극+SE **462 MPa · 2.5 min**, 음극 **277 MPa · 5 min**, **구동압 100 MPa** | 사용자 진술 |
| F5 | Formation 고정: **0.1C/0.1C · 2 cycles**; 변수: 충전 cut-off **3.6 / 3.8 / 4.0 / 4.2 / 4.4 / 4.6 V vs. Li/Li⁺** | 사용자 진술 |
| F6 | Main cycle: **2.5–4.4 V vs. Li/Li⁺ · 0.5C · 45 °C · 200 cycles** | 사용자 진술 |
| F7 | 보조 실험: main 2번째 사이클 SOC 100 % EIS(RT 평형 후) · formation 후 24 h rest 전압 tracking · NCA721 \| Ag-C \| Ag wire RE 3-전극 EIS/DRT · Mid-Ni \|\| LTO 셀 0.05C 로 4.6 V 까지 충전하며 operando 압력 · 200 cycle 후 SOC 100 % 수득 양극 사후분석 (XRD·XPS·ToF-SIMS depth profiling·FIB-SEM·HAADF-STEM/FFT·Raman) | 사용자 진술 (진행 또는 계획) |
| F8 | 후순위: High-Ni 비교 실험, anode-free 저압 파우치셀 | 사용자 진술 |
| F9 | Raw 데이터 전압은 **vs. In/Li-In**; **+0.62 V → vs. Li/Li⁺**; 용량은 항상 **비용량 mAh g⁻¹** | 사용자 진술 |
| F10 | Raw CSV 22개 열(위 원문), 사이클 요약 열, 파일명 불일치(g/mg 혼재, 질량의 정체 불명), registry 가 정본 | 사용자 진술 |
| F11 | 환경 Ubuntu(WSL); alias 는 첫 문단에서 `li2s`, [5] 에서 `midni` → **midni 로 확정** (li2s 는 선행 Li2S 위키 브랜치의 이름) | 사용자 진술 + 세션 판단 |
| F12 | 초기 투입 예정 논문 10편 (제목 기준, 위 원문) | 사용자 진술 |
| F13 | 절대 규칙 4개 (위 원문) | 사용자 진술 |

## 3. 이 세션의 설계 결정

1. **브랜치**: `main` 이 아닌 단독 작업 브랜치 (이름의 정본은 루트 `CLAUDE.md` 하드룰 1 — 여기 적지 않는다).
   다른 계열 브랜치(DEM/MPM·열화 degeneracy·Li2S 위키 등)는 merge 하지 않는다.
2. **위키 하네스**: llm-wiki-kit(260730) 을 repo root `wiki/` 로 이식. 킷의 7개 폴더에 **`papers/` `mechanisms/`
   `protocols/` `experiments/` 4개를 더해** 사용자가 지정한 카테고리를 폴더로 세운다. lint 에 절대 규칙 검사
   (`no-ncm721` `canonical-offset` `voltage-reference` `unit-rule` `doi-unique`) 를 추가.
3. **논문 = 두 파일**: `raw/papers/<slug>.md` digest(sha256 봉인, 4구분 표기) + `papers/<slug>.md` 노트(`paper:`
   추출 스키마 — 값이 없으면 null, DOI 가 중복 제거 키, Supplementary 는 본문 노트에 연결).
4. **webapp**: 선행 브랜치의 Flask 읽기 전용 열람기 포맷을 이식하고 `/roadmap`(연구 한 장) · `/compare`(paper:
   블록 표, DOE 겹침 표시, cut-off/상한 전압 정렬·거르기) · `/mechanisms` `/protocols` `/experiments` ·
   `/chat`(위키 근거 대화 — 인용 필수, "DB 외 일반 지식/추론" 구분, 비교 시 기준전극·조성·온도·압력·loading
   자동 지적, IPA 병기) · `/cells`(registry + import 요약 + cut-off 색 차트) 를 더한다. 기본 바인딩 127.0.0.1.
5. **셀 데이터 모듈 (prototype)**: `config/cells.yaml`(offset 0.62 V 정본, DOE 창, 색) · `data/registry/cells.csv`
   (정본) · `tools/cells/import_cell.py`(utf-8-sig raw → pandas 사이클 요약, 파일명 파싱은 제안) · LLM 에는
   요약만.
6. **alias**: `midni` 한 단어 (`scripts/install-alias.sh`). 선행 위키의 `li2s` 와 충돌하지 않는다.
7. **일반 지식 취급**: 근거 논문이 없는 메커니즘 설명은 `> [!note] 미검증 배경` + `confidence: low` +
   `evidenceScope: synthesis-only`. `/chat` 은 이를 "DB 외 일반 지식/추론" 으로 표시한다.

## 4. 미결 (사용자에게 확인할 것)

- Q1. 파일명의 질량(`0.0189g`, `18.5mg`)이 **전극 질량인지 활물질 질량인지** — registry `active_mass_mg` 의 정의.
- Q2. 복합양극 조성비 (NCA721 : LPSCl : 도전재 : 바인더, wt%) 와 2 mAh cm⁻² 에 해당하는 mg cm⁻² 로딩.
- Q3. Li-In 음극의 실제 조성(Li/In 몰비) 또는 두께 — 논문의 `vs. Li-In` 값과 비교할 때 필요.
- Q4. formation 두 사이클 사이·후의 rest 시간(24 h rest 는 formation 후만인지), 방전 cut-off (2.5 V 로 추정 — 미확인).
- Q5. 사후분석의 "SOC 100 %" 정의 (4.4 V 충전 상태에서 수득인지).
- Q6. 이미 사이클을 마친 셀 목록 (registry 채우기).
