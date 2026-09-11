---
title: "Huang et al. 2026 — Tailoring high-entropy sulfides as kinetic accelerators for all-solid-state lithium-sulfur batteries (J. Energy Chem. 118, 352–360)"
description: "고엔트로피 황화물 NiCoCuFeMnSx 를 S/KB/LPSCl 복합양극에 6 wt% 넣어 상온 ASSLSB 의 황 이용률을 39 → 76 %(0.1 C 첫 방전)로 올린 논문 — 우리와 같은 LPSCl·Li–In 계이지만 활물질이 Li2S 가 아니라 S8 이라 첫 충전 활성화에는 근거를 주지 않는다"
source_url: local-upload/bdb71cfd-2._HES_as_kinetic_accelerators_for_ASSLSBs.pdf + 8a30c901-supporting-information.docx
doi: 10.1016/j.jechem.2026.03.054
ingested: 2026-09-11
sha256: 80d112fa2f70651637c5c56f1bbb2882e2f36bb54126219f9b5a8a8682310db0
tags: [assb, sulfide-electrolyte, composite-cathode, carbon, mixing-process, li-in, units]
compare:
  system: "ASSB Li–S (S8 양극, Li2S 아님)"
  electrolyte: "Li6PS5Cl (LPSC) — 분리층 100 mg @350 MPa, 양극 내 40 wt%"
  cathode: "S : HES(NiCoCuFeMnSx) : Ketjen Black : LPSC = 42 : 6 : 12 : 40 wt% [재현] (S복합체 70:10:20 을 LPSC 와 6:4 로 혼합), 바인더 언급 없음"
  li2s_source: "해당 없음 — 원소 S8 출발 (Li2S 는 방전 생성물)"
  mixing: "S+KB 그라인딩 → 첨가제와 155 °C 12 h 융합 → LPSC 와 planetary BM 350 rpm 4 h (불활성); 볼 재질·BPR·용기 미기재"
  loading_mg_cm2: "1.5–1.7 (S) 표준 · 6.0 (S) 고로딩 시험 [재현] 양극층으로는 3.8 / 14.3"
  anode: "Li–In (Li:In 비·두께·N/P 미기재)"
  first_charge: "해당 없음 — S8 양극이라 첫 스텝이 방전. 창 0.9–2.4 V vs Li–In, 상온"
  first_discharge_mAh_gS: "1025.2 @0.5 C · 925.1 @1 C · ≈1280 @0.1 C (HES 10 wt% 조건) [도표]"
  first_discharge_mAh_gLi2S: "715.6 / 645.7 / ≈893 [재현] ×0.698"
  cycle_capacity_mAh_gS: "960.4 @0.5 C 100 cyc · 777.5 @1 C 160 cyc · 683.7 @2 C(5.4 mA cm⁻²)"
  cycle_capacity_mAh_gLi2S: "670.4 / 542.7 / 477.2 [재현] ×0.698"
  areal_mAh_cm2: "1.64 @0.5 C (1.6 mg cm⁻² S) [재현] · 5.8 → 5.0 (15 cyc, 6.0 mg cm⁻² S, 0.05 C = 0.50 mA cm⁻²)"
  cycles: "100 (0.5 C, 91.4 %) · 160 (1 C, 84.0 %, 평균 CE > 99.89 %) · 15 (고로딩) — 셀 개수·오차 없음"
  temperature_C: "room temperature (수치 미기재)"
  mechanism: "혼합 이온–전자 전도체 6 wt% 로 삼상 계면 재구성 — DC 분극 전도도(σe 14배·σi 270배), 토모그래피 분산, GITT D_Li+, DFT NEB 0.20 vs 0.25 eV, 사이클 후 크랙 유무"
  our_axis: "AB 단일 탄소 복합양극의 퍼콜레이션 한계(H2)에 대한 고체계 직접 근거 + DC 분극 전도도 측정법의 이식. 단 S8 계라 Li2S 첫 충전 활성화(H1)에는 무근거이고, 탄소를 첨가제로 대체한 실험은 아니다"
---

# 수집 목적

Y. Huang, Y. Song, W. Huang, W. Zhao, Q. Liu, J. Wang, J. Song, B. Lu, X. Xie, L. Huang,
**"Tailoring high-entropy sulfides as kinetic accelerators for all-solid-state lithium-sulfur
batteries"**, *Journal of Energy Chemistry* **118** (2026) 352–360, DOI 10.1016/j.jechem.2026.03.054
의 **절별 해체분석** + SI(.docx, 그림 19장 · 식 3개 · 표 3개) 전문 대조.

이 위키가 이 논문을 흡수하는 이유는 셋이다.

1. **우리와 같은 셀 계다.** Li6PS5Cl 펠릿 + Li–In 음극 + 상온 + 냉간 가압 성형 — 즉
   [[li2s-assb-reference-cell]] 과 **전해질·음극·온도가 같다**. 이 위키가 지금까지 가진
   유일한 논문(Kim 2023)은 액체계였으므로, **고체계 수치를 처음으로 들여오는 digest** 다.
2. **우리의 열린 질문 H2(퍼콜레이션 제한)에 정면으로 걸린다.** 이 논문의 모든 논증은
   "탄소만으로는 삼상 계면이 모자라다 → **혼합 이온–전자 전도체를 소량 넣어라**" 다.
   우리 복합양극의 AB 20 wt% 를 어떻게 다룰지에 직접 닿는다
   ([[reference-cell-500-600-mahg]] H2, [[carbon-dimensionality-electron-network]]).
3. **그러나 활물질이 Li2S 가 아니라 S8 이다.** 그래서 **첫 충전 활성화라는 우리 최대 난점에
   대해서는 아무 근거도 주지 않는다.** 이 경계선을 digest 안에 명시적으로 긋는 것 자체가
   수집 목적의 일부다 (§10, §11).

**표기 규칙** (이 위키 관례 3구분 + 1):
- `[인쇄]` — 논문 본문/식/표/SI 에 글자로 있는 것 (그림 안에 인쇄된 라벨 포함, 그때는 위치를 밝힌다)
- `[도표]` — 그림에서 눈으로 읽은 근사값 (**원 데이터가 아니다**)
- `[해석]` — 이 문서를 쓰면서 붙인 판단. **논문의 주장이 아니다**
- `[재현]` — 원문 값을 이 세션에서 산술로 옮긴 것 (계산식을 함께 적는다)

- 원본 파일: 로컬 업로드 PDF 9쪽(저널 조판 352–360) + SI(.docx). 저장소에 바이너리 원문은 넣지 않는다.
- 크로핑 그림: `raw/figures/huang2026_high-entropy-sulfides-kinetic-accelerators-assb/`
  — 본문 Fig. 1–5 는 도구(`wiki/tools/extract_figures.py`)가 캡션 앵커로 잘랐고,
  **SI Fig. S1–S19 는 .docx 내장 이미지를 문서 순서대로 꺼내** `fig_S1.png`…`fig_S19.png` 로
  두었다 (`figures.json` 에 캡션과 함께 등록, 투명 배경은 흰색으로 합성). 식 S1–S3 은 WMF
  수식 객체라 이미지로 꺼내지 않고 §9.3 에 텍스트로 옮겼다. 표 S1–S3 도 §9.4 에 전문을 옮겼다.
- **단위 규율**: 이 논문은 `[인쇄, §2.3]` "The specific capacity is calculated based on the mass
  of sulfur" — 즉 **모든 비용량이 `mAh g⁻¹(S)`** 다. 우리 목표(500–600)는 기준이 미확정이므로
  이 digest 는 모든 용량에 대해 `(S)` / `(Li2S 환산)` / `(composite)` **세 기준을 병기**한다
  (환산식은 §5.2 머리말). Li2S 환산값은 "같은 전하량을, 그것이 만들어 낼 Li2S 의 질량으로
  나눈 값" 이라는 **가상의 정규화**이며 이 논문에 Li2S 는 출발물질로 존재하지 않는다.
- 전압은 전부 **vs Li–In** 이다 (`[인쇄, §2.5]` 0.9–2.4 V, 그림 축 라벨도 `V vs.Li-In`).
  Li/Li⁺ 기준 환산은 하지 않는다 — Li–In 평탄전위 값의 근거 raw 가 이 위키에 아직 없다.

---

# 원문에 없어서 확인이 필요한 것 (읽기 전에 먼저 본다)

이 절이 이 digest 의 가장 중요한 산출물이다. **논문이 답을 주지 않는 것**과, 논문 안에서
서로 어긋나는 것을 먼저 모은다.

| # | 공백 / 불일치 | 왜 문제인가 |
|---|---|---|
| G1 | **운전 중 스택 압력이 없다.** `[인쇄, §2.3]` 에 성형 압력 두 개(SE 350 MPa, 양극 450 MPa)만 있고, 사이클 중 유지 압력은 한 글자도 없다. 셀은 지름 10 mm 스테인리스 컬럼 몰드. | ASSB 황 양극은 방전 시 팽창·충전 시 수축한다. **압력이 성능의 1차 변수**인데 그 값이 없으면 §7 의 "HES 가 크랙을 막는다" 를 재현할 수 없다. 우리 셀과의 비교도 불가. |
| G2 | **1 C 의 정의(mA g⁻¹)가 없다.** 본문·SI 어디에도 없다. | `[재현]` 결론의 "683.7 mAh g⁻¹ at 5.4 mA cm⁻²" 가 Fig. 3f 의 2 C 값이므로 5.4 / (2 × 1.6 mg cm⁻²) = **1687 mA g⁻¹(S) ≈ 1675 = S 의 이론용량**. 즉 **1 C ≡ 1675 mA g⁻¹(S)** 로 읽힌다. 그러나 이건 우리가 역산한 값이지 논문이 적은 값이 아니다. |
| G3 | **같은 수치의 전류밀도가 본문 안에서 두 개다.** `[인쇄, 초록]` "683.7 mAh g⁻¹ at 5.4 mA cm⁻²" · `[인쇄, §1 마지막 문단]` "at the high current density of **6.83 mA cm⁻²** … 683.7 mAh g⁻¹" · `[인쇄, §4]` 다시 "5.4 mA cm⁻²". | `[재현]` 6.83 mA cm⁻² 가 되려면 로딩이 2.04 mg cm⁻² 여야 하는데 §2.3 은 1.5–1.7 mg cm⁻² 라 한다. **서론의 6.83 이 오기**로 보인다 (683.7 의 자릿수 전치). 인용할 때 5.4 를 쓴다. |
| G4 | **셀 개수·오차 막대가 하나도 없다.** 모든 사이클 곡선이 단일 셀. | 91.4 % vs 85.7 % (0.5 C), 84.0 % vs 76.9 % (1 C) 같은 **한 자릿수 차이의 유지율 비교**가 셀 편차 안인지 밖인지 판단할 수 없다. |
| G5 | **§3.3 본문의 Fig. 5 패널 지시가 그림과 어긋난다.** `[인쇄, §3.3]` "As depicted in Fig. 5(a), the S/HES cathode exhibits a dense and homogenous surface morphology without cracks" 인데 `[도표]` 실제 패널 (a)는 **"Cycled S/Co₉S₈ electrode — Crack"**, (b)가 "Cycled S/HES electrode — No crack" 이다. 캡션은 그림과 맞다. 같은 문단의 "In agreement with Fig. 5(b)" (크랙 누적)도 뒤집혀 있고, "illustrate … in Fig. 5(f)" 는 도식이 아니라 S/HES 단면 SEM 이다 (도식은 (e),(g)). | 캡션을 믿고 본문을 무시해야 한다. **그림을 직접 보지 않고 본문만 옮기면 결론이 정반대**가 된다. 이 digest 가 그림을 먼저 본 이유의 실례. |
| G6 | **Table S3 의 시료 정체가 불명확하다.** "S-HES / S-Co₉S₈ / S-KB" 가 **LPSC 를 포함한 최종 복합양극**인지, 볼밀 전의 융합 복합체(S/KB/HES)인지 적지 않았다. Fig. S13 캡션은 "different composite", 두께 "about 1.8 mm". | `[해석]` σ_Li⁺(S-HES) = 6.5×10⁻³ mS cm⁻¹ 는 LPSC 를 40 wt% 함유한 복합체 값으로는 **너무 낮다** — LPSC 없는 융합 복합체일 가능성이 크다. 어느 쪽이냐에 따라 "HES 가 이온 경로를 만든다" 의 의미가 완전히 달라진다 (SE 를 대신하는가, SE 가 없는 구역을 잇는가). |
| G7 | **DC 분극에 건 전압 U 가 없다.** 식 S3 에 U 가 들어가는데 값이 없다. | `[재현]` 전자 전도도는 U = 1 V 로 놓아야 표 S3 이 재현된다 (HES: 85 mA × 0.025 cm ÷ (1 V × 0.785 cm²) = 2.7×10⁻³ S cm⁻¹ ≈ 2.49 mS cm⁻¹). 이온 전도도는 U ≈ 10–20 mV 를 넣어야 맞는다. **두 측정의 U 가 다르다는 사실이 적혀 있지 않다.** |
| G8 | **Fig. S12(b1) 의 "정상 전류" 가 정상이 아니다.** `[도표]` HES 의 electron-blocking 전류는 2000 s 동안 ≈22 → ≈8 µA 로 **계속 감소**하는데 끝점 7.03 µA 를 σ_Li⁺ 로 썼다. | 정상상태에 도달하지 않은 값이다. HES 의 이온 전도도(2×10⁻⁵ S cm⁻¹)는 **상한**으로 읽어야 한다. |
| G9 | **0 wt% HES 대조군의 조성이 불명확하다.** `[인쇄, §3.1]` "x wt% HES (x = 0, 10, and 20)" 만 있고, HES 를 뺀 자리를 S 로 채웠는지 KB 로 채웠는지 없다. | 0 wt% 곡선(Fig. S4a, ≈660 mAh g⁻¹(S))이 **우리 AB-단일탄소 양극의 대리 대조군**이라 조성이 중요하다. 활물질 비율이 다르면 비용량 비교가 성립하지 않는다. |
| G10 | **0 wt% HES 셀의 사이클 데이터가 없다.** 0 wt% 는 Fig. S4 의 0.1 C 첫 사이클에만 나온다. 100/160 사이클 비교는 전부 **HES vs Co₉S₈** (둘 다 금속황화물 첨가) 이다. | 즉 "첨가제 없는 S/KB 대비 수명이 얼마나 좋아지는가" 는 **측정되지 않았다**. 논문의 대조군은 "첨가제 없음" 이 아니라 "덜 좋은 첨가제" 다. 우리에게 가장 필요한 대조가 빠져 있다. |
| G11 | **HES 함량 격자가 0 / 10 / 20 wt% 세 점뿐**이고 5 wt% 나 15 wt% 가 없다. 게다가 10·20 wt% 는 **S 복합체 기준** 이므로 최종 양극 기준으로는 6 · 12 wt% 다. | 최적값 "10 wt%" 를 그대로 우리 조성에 옮기면 **기준 질량을 혼동**한다. 최적 위치도 세 점으로는 결정되지 않는다. |
| G12 | **HES–LPSC 화학적 양립성 시험이 없다.** HES 는 전자 전도체(2.49 mS cm⁻¹)이고 전이금속 황화물인데, LPSC 와 직접 접촉한 상태로 350 rpm 4 h 볼밀된다. 계면 XPS·자가방전·플로팅 시험 없음. | `[해석]` 전자 전도성 첨가제가 SE 와 넓게 접촉하면 SE 분해의 촉매가 될 수 있다. 160 사이클에서 문제가 안 보였다는 것이 전부. |
| G13 | **황·HES 의 입도 분포가 없다.** HES 는 `[인쇄]` "spherical particles with a diameter of approximately 2 µm" 하나뿐이고, 볼밀 후 입도·BET·기공률은 없다. Fig. 2g 에 S 입자가 색칠돼 있을 뿐. | 우리 [[mixing-equipment-ball-mill-thinky]] 표의 칸을 채울 수 없다. 2 µm 구형 입자가 26 µm 전극 안에서 "연속 골격" 을 이룬다는 주장(§4.3)의 정량 근거도 없다. |
| G14 | **볼밀 세부가 반쯤 없다.** `[인쇄, §2.2]` 고에너지 planetary, **350 r min⁻¹, 4 h, 불활성 분위기** 까지는 있다. 없는 것: 볼 재질·직경·개수, **BPR**, 용기 재질·용량, 정/역회전·휴지 주기, 총 투입량. | Kim 2023 의 G1(전부 없음)보다는 낫지만 **재현에는 여전히 부족**하다. [[composite-cathode-mixing-routes]] 의 칸이 반만 찬다. |
| G15 | **"significantly lower overpotential" 의 크기가 2 mV 다.** `[인쇄, Fig. S14d 라벨]` 방전 η_max: S/HES **0.1943 V**, S/Co₉S₈ **0.1963 V**. 충전은 0.6098 vs 0.6501 V. | 방전 쪽 차이는 **0.2 %** 다. 본문의 "significantly" 는 충전 쪽(40 mV)에만 해당한다. 셀 하나씩이라(G4) 2 mV 는 잡음이다. |
| G16 | **Fig. S6a 의 환원 피크는 두 시료가 사실상 같은 전위다.** `[인쇄, §3.2]` "the S/HES cathode manifests the **higher reduction** and lower oxidation potential" 인데, `[도표]` 확대해 보면 환원 최저점은 S/HES ≈1.15 V, S/Co₉S₈ ≈1.16 V vs Li–In 으로 **S/HES 가 오히려 근소하게 낮거나 같다**. 다른 것은 전위가 아니라 **전류 크기**(−1.10 vs −1.00 mA mg⁻¹). 산화 쪽만 1.90 vs ≈1.93 V 로 주장과 맞다. | 논문이 CV 에서 읽어 낸 "더 작은 분극" 의 절반은 그림에 없다. |
| G17 | **사이클 후 EIS 원자료가 DRT 서사와 어긋나 보인다.** `[도표, Fig. S19b]` 사이클 후 고주파 절편이 S/HES ≈75 Ω, S/Co₉S₈ ≈45 Ω 이고 전 구간에서 S/HES 의 Z′ 가 더 크다 (범례 색이 본문 그림과 **반대**다 — 여기선 S/HES 가 하늘색). 그런데 Fig. 5c 의 DRT 는 S/HES 가 더 낮다고 한다. 등가회로 피팅값·저항 수치는 어디에도 없다. | DRT 는 EIS 의 변환이므로 두 결론이 다르면 어느 주파수 대역을 세었는지가 문제다. **숫자가 없어 검증 불가.** |
| G18 | **고로딩(6 mg cm⁻²) 실험의 조건이 본문에 숨어 있다.** `[인쇄, Fig. S11 캡션]` **0.05 C**, `[도표]` **15 사이클**. 초록·결론은 "A high areal capacity of 5.8 mAh cm⁻² is demonstrated at a high sulfur loading of 6 mg cm⁻²" 라고만 쓴다. | `[재현]` 0.05 C ≈ 84 mA g⁻¹(S) ≈ **0.50 mA cm⁻²** — 같은 논문이 자랑하는 5.4 mA cm⁻² 의 1/11 이다. 5.8 mAh cm⁻² 는 **저율·단기** 값이다. |
| G19 | **온도가 "room temperature" 뿐**이고 숫자가 없다. 글로브박스·시험 챔버 온도 제어 여부도 없다. | 황화물 ASSB 는 25 vs 30 °C 에서 용량이 유의하게 다르다. 우리 셀과의 정량 비교가 막힌다. |
| G20 | **Li–In 음극의 사양이 없다.** `[인쇄, §2.3]` "The Li-In anode was attached to the other side" 가 전부 — Li:In 비, 두께, 면적, N/P 비 없음. | 160 사이클 동안 음극이 제한 요소가 아니었다는 보장이 없다. anode-free 로 가는 우리 2단계와의 접점이 끊긴다. |
| G21 | **바인더·집전체 언급이 없다.** 건식 분말을 몰드에서 가압한 것으로 보이나 명시가 없다. | 우리 공정과의 1:1 비교에 필요한 정보다. |
| G22 | **Fig. S3 의 축 단위가 틀렸다.** `[도표]` "3D Area (×1000 **mm²**)" — 520 × 390 × 26 µm 시야 안의 입자 표면적이 13 000 mm² 일 수 없다. µm² 의 오기로 보인다. | 이 그림은 "HES 분산" 의 정량 근거로 인용되는데 단위가 틀려 있다. 게다가 0/10/20 wt% 의 입자 수·부피가 **거의 함량에 비례**할 뿐이라, "10 wt% 가 더 고르게 분산됐다" 는 주장을 지지하지 않는다. |

---

## 0. 서지사항 (직접 확인)

`[인쇄]` PDF 1쪽(=저널 352쪽):

| 항목 | 값 |
|---|---|
| 제목 | Tailoring high-entropy sulfides as kinetic accelerators for all-solid-state lithium-sulfur batteries |
| 저자 | Yating Huang ᵃ, Yajie Song ᵇ, Wenze Huang ᵃ, Wei Zhao ᵇ, Qingsong Liu ᵇ, **Jiajun Wang ᵇ (교신)**, Jinpeng Song ᵃ, Bo Lu ᵃ, Xiang Xie ᵃ, **Lujun Huang ᵃ˒ᶜ (교신)** |
| 소속 | a 하얼빈공업대 재료과학공학부 · b 하얼빈공업대 화학화공학부 · c 하얼빈공업대 선진용접·접합 국가중점연구실 |
| 교신 이메일 | jiajunhit@hit.edu.cn · huanglujun@hit.edu.cn |
| 학술지 | Journal of Energy Chemistry **118** (2026) 352–360 (Science Press + Dalian Inst. Chem. Phys., CAS / Elsevier) |
| DOI | 10.1016/j.jechem.2026.03.054 |
| 접수/개정/게재 | Received 18 January 2026 · Revised 30 March 2026 · Accepted 30 March 2026 · Available online 7 April 2026 |
| 저작권 | © 2026 Science Press and DICP, CAS. Published by Elsevier B.V. **All rights reserved** (open access 아님) |
| 키워드 | High-entropy sulfides · Ion-electron mixed conductivity · Sulfur redox reaction kinetics · Composite cathode · All-solid-state lithium-sulfur batteries |
| 지원 | NSFC 22309101 · U22A20113 · 52261135543 · 중앙대학 기본연구비 AUGA5710012925 · 구이저우성 과제 2건 |
| 이해충돌 | 없음 (선언) |

`[해석]` 저자 목록 중 Yating Huang·Jiajun Wang·Bo Lu 는 본문 인용 [22] (Y.-T. Huang et al.,
*J. Energy Chem.* **102** (2025) 263–270) 의 저자와 겹친다 — 같은 그룹의 ASSLSB 양극 연재물
중 한 편이다. 또 [34] (W. Zhao, …, S. Lou, J. Wang, *Angew. Chem.* 2025) 도 자기 인용이다.

---

## 1. 한 문단 요약

`[해석]` 저자들은 NiCl₂·CoCl₂·CuCl₂·FeCl₂·MnCl₂ 를 등몰로 DMF 에 녹이고 티오요소와 함께
180 °C 16 h 용매열 반응 → Ar 중 450 °C 2 h 어닐링으로 **고엔트로피 황화물 NiCoCuFeMnSₓ(HES,
Co₉S₈형 cubic, 약 2 µm 구형)** 를 만들었다. 이것을 S:첨가제:Ketjen Black = 70:10:20 으로 155 °C
12 h 융합(melt-diffusion)하고, 그 복합체를 **Li₆PS₅Cl(LPSC)과 6:4 로 350 rpm 4 h planetary
볼밀**해 최종 양극 분말을 얻었다 (`[재현]` 최종 조성 **S 42 / HES 6 / KB 12 / LPSC 40 wt%**).
셀은 지름 10 mm 몰드에 LPSC 100 mg 을 350 MPa 로 누른 뒤 양극을 얹어 450 MPa, 반대편에
Li–In — 즉 우리 reference cell 과 같은 계다. 주장은 **"HES 가 이온과 전자를 동시에 나르고
촉매도 해서 삼상 계면을 재구성한다"**이고, 근거는 (i) 싱크로트론 X-ray 토모그래피로 본 HES
의 균일 분산·"연속 골격", (ii) DC 분극으로 잰 복합체 전도도(S-KB 대비 전자 14배·이온 270배),
(iii) GITT 의 Li⁺ 확산계수와 과전압, (iv) DFT(NEB 장벽 0.20 vs 0.25 eV, d-band center, DOS),
(v) 사이클 후 SEM 의 크랙 유무다. 성능은 상온에서 `[인쇄]` 0.5 C 100 사이클 후
**960.4 mAh g⁻¹(S)**, 1 C 초기 925.1 → 160 사이클 **777.5 mAh g⁻¹(S) (84.0 %, 평균 CE > 99.89 %)**,
2 C(= 5.4 mA cm⁻²) **683.7 mAh g⁻¹(S)**, 그리고 6 mg cm⁻² 로딩에서 **5.8 mAh cm⁻²** (단
`[인쇄, Fig. S11 캡션]` 0.05 C, `[도표]` 15 사이클). 대조군은 같은 방법으로 만든 **Co₉S₈** 이고,
**첨가제 없는 S/KB 는 첫 사이클(Fig. S4)에만 등장**한다.

---

## 2. p.352–353 — Abstract / Introduction

### 2.1 Abstract 의 명제 `[인쇄]`

> "All-solid-state lithium-sulfur batteries (ASSLSBs) hold promise … yet their practical
> deployment is hindered by **sluggish sulfur redox kinetics and restricted triple-phase
> interfaces**. Here, we designed a high-entropy sulfide (HES) material with **mixed
> ionic-electronic conductivity as a multifunctional mediator** to engineer robust ion/electron
> transport pathways and abundant catalytic sites within the cathode. … HES-incorporated
> ASSLSBs exhibit superior performance at room temperature, achieving **84.0 % capacity
> retention over 160 cycles at 1 C**, a high capacity of **683.7 mAh g⁻¹ at 5.4 mA cm⁻²**, and an
> exceptional areal capacity of **5.8 mAh cm⁻² with a sulfur loading of 6 mg cm⁻²**."

`[해석]` 초록의 세 수치는 **서로 다른 세 셀·세 조건**이다 (1 C 장기 / 2 C 율속 / 0.05 C 고로딩).
한 셀이 셋을 동시에 한 것이 아니다.

### 2.2 Introduction 의 문제 설정 `[인쇄]`

- ASSLSB 의 매력: 저비용·고안전·비에너지 "up to 2600 Wh kg⁻¹", 무기 SE 가 폴리설파이드
  셔틀과 불안정 계면을 원천 차단.
- 그럼에도 **S → Li₂S 반응의 에너지 장벽이 높고 반응물(S, Li₂S) 둘 다 이온·전자 전도도가
  낮아** 동역학이 느리다. 그 결과 **삼상 계면(SE | 활물질 | 탄소)에 갇힌 비활성 황**이 생기고
  상온 성능이 나쁘다 (Fig. 1a).
- 선행 전략 셋: (i) 삼상 계면 밀도를 높이는 양극 설계 [14], (ii) SE 개질 [15], (iii) S–SE 사이
  보호 중간층 [16].
- 선행 첨가제 비판 두 건 — **이 논문의 논증 구조를 만드는 부분이라 그대로 옮긴다**:
  - `[인쇄]` Zheng 등 [20]: Co₃O₄ + 질소도핑탄소. "improved electronic (via nitrogen-doped
    carbon) and ionic transport (via Co₃O₄) **individually**", 그러나 "poor coupling between
    the two conducting networks and the insufficiency of catalytic sites" → **60 °C 필요**.
  - `[인쇄]` Ge 등 [21]: MXene 위 Co 단원자 촉매. "the atomically dispersed Co sites break S–S
    bonds" 그러나 "owing to the **isolation between catalytic sites and electronic/ionic
    transport**" → 최고 운전 전류 **2.8 mA cm⁻²** 에 머문다.
- 그래서 HES 를 고른다: `[인쇄]` "HES exhibit superior catalytic capability owing to the
  **'cocktail effect'** [25]" + "both the excellent electronic conductivity and catalytic
  capability of metal sulfides, as well as the **high ionic conductivity derived from the
  high-entropy cation mixing** [26]".

`[해석]` 논증의 핵심 주장은 **"세 기능(전자·이온·촉매)을 한 입자에 얹으면 결합 손실이
없다"** 이다. 그런데 §3.3 에서 그 셋을 분리하려는 실험은 하지 않는다 — HES vs Co₉S₈ 비교는
세 기능이 **동시에** 달라진 두 재료의 비교이므로 어느 기능이 얼마나 기여했는지 가르지
못한다 (§11-2).

### 2.3 Fig. 1 — 이 논문의 그림 하나짜리 주장

`[도표, Fig. 1]` (a) 전통 ASSLSB: 노란 SE 구, 검은 KB 구, 주황 S 입자. S 입자 중 SE 또는 KB
한쪽만 닿은 것은 "Inactive sulfur"(회색 점선, "two-phase interfaces"), 둘 다 닿은 얇은 영역만
"Active sulfur"(빨간 실선, "three-phase interfaces"). (b) HES 도입: S 입자 둘레가 **알록달록한
HES 구로 둘러싸이고** 모든 S 가 "Active sulfur" 가 된다. 범례는 "Ionic-electronic conductor".

`[해석]` 이 도식은 HES 가 S 입자를 **둘러쌀 만큼** 많은 것처럼 그려져 있으나, 실제 HES 는
최종 양극의 **6 wt%**(§3.2)이고 입경 2 µm 로 S 입자와 비슷하다. 그림과 조성의 스케일이 맞지
않는다. 이건 이 논문만의 문제가 아니라 첨가제 논문의 흔한 관행이지만, 우리가 조성을 옮길
때 그림이 아니라 **wt% 를 봐야 한다**는 점에서 중요하다.

---

## 3. p.353–354 — §2 Experimental (재현에 필요한 전부)

### 3.1 HES·Co₉S₈ 합성 (§2.1) `[인쇄]`

| 단계 | 조건 |
|---|---|
| 금속 전구체 | NiCl₂·6H₂O, CoCl₂·6H₂O, CuCl₂·2H₂O, FeCl₂·4H₂O, MnCl₂·4H₂O **각 0.8 mmol (등몰)** |
| 용매 | DMF 30 mL, 연속 자력 교반으로 균일 용액 |
| 황원 | **티오요소 10 mmol** 을 별도 DMF 30 mL 에 교반 용해 |
| 반응 | 두 용액을 섞어 100 mL PTFE 라이너로 옮겨 **180 °C 16 h** (용매열) |
| 회수 | 원심분리로 고체 분말 회수 (세척 용매·횟수 **미기재**) |
| 어닐링 | **Ar 흐름 중 450 °C 2 h** → NiCoCuFeMnSₓ |
| 대조군 | **Co₉S₈ 를 같은 절차로** 합성 (CoCl₂ 만; 몰수 미기재) |

`[해석]` 전구체는 등몰인데 **생성물의 금속 조성은 등몰이 아니다** (Table S1: Ni 15.68 > Co
11.76 > Fe 10.24 > Mn 8.09 > Cu 7.91 at%). 2배 가까운 편차다. "equimolar" 는 투입 기준일 뿐이다.

### 3.2 복합양극 (§2.2) `[인쇄]` ★ 우리 축

| 단계 | 조건 | 빠진 것 |
|---|---|---|
| ① 그라인딩 | S 와 Ketjen Black 을 갈아 섞는다 (Fig. 2a "Grinding") | 장비(막자사발?), 시간, 분위기 **전부 미기재** |
| ② 융합 (melt-diffusion) | S(70 wt%) + HES 또는 Co₉S₈(10 wt%) + KB(20 wt%) 를 **155 °C 12 h 열처리** | 용기, 분위기(밀봉?), 승온속도 미기재 |
| ③ 볼밀 | 위 복합체 : **Li₆PS₅Cl = 6 : 4 (질량)**, **불활성 분위기**의 볼밀 용기로 옮겨 **고에너지 planetary 밀, 350 r min⁻¹, 4 h** | **볼 재질·크기·개수, BPR, 용기 재질·용량, 정역회전/휴지, 총 투입량 미기재** (G14) |

`[재현]` 최종 복합양극 조성 = 0.6 × (70/10/20) + 0.4 × LPSC
→ **S 42.0 / HES 6.0 / KB 12.0 / LPSC 40.0 wt%**.
우리 [[li2s-assb-reference-cell]] 의 Li2S : LPSCl : AB = 30 : 50 : 20 과 나란히 두면
**활물질 42 vs 30, SE 40 vs 50, 탄소 12 vs 20, 첨가제 6 vs 0** 이다.

`[해석]` 공정 순서로 보면 이것은 [[one-step-vs-two-step-mixing]] 카드의 **two-step 계열**이다
(활물질–탄소 복합체를 먼저 만들고 SE 를 나중에). 다만 "나중" 단계가 mild mixing 이 아니라
**350 rpm 4 h 고에너지 볼밀**이어서, 카드의 H2(SE 를 고에너지 단계에서 빼는 것이 이득)를
지지하지도 반박하지도 않는다 — SE 는 고에너지 단계에 **들어가 있다**.

### 3.3 셀 조립 (§2.3) `[인쇄]`

| 항목 | 값 |
|---|---|
| 몰드 | 스테인리스 컬럼, **지름 10 mm** (`[재현]` 면적 0.785 cm²) |
| SE 층 | **LPSC 100 mg 을 350 MPa 로 가압** |
| 양극 | 복합양극 분말을 LPSC 시트 한쪽에 균일하게 올리고 **450 MPa** |
| 음극 | **Li–In** 을 반대쪽에 부착 (조성·두께·N/P **미기재**, G20) |
| 분위기 | 전 공정 Ar 글로브박스 |
| 로딩 | **황 기준 1.5–1.7 mg cm⁻²** (고로딩 시험만 6.0 mg cm⁻², Fig. S11) |
| 용량 기준 | **"The specific capacity is calculated based on the mass of sulfur"** |

`[재현]` 양극층 총 로딩 = 1.6 ÷ 0.42 ≈ **3.8 mg cm⁻²** (6 mg cm⁻² 시험은 **14.3 mg cm⁻²**).
`[도표, Fig. 2f·S2]` 토모그래피 라벨의 전극 두께 **26 µm** 과 합치면 겉보기 밀도
`[재현]` 3.8×10⁻³ g cm⁻² ÷ 26×10⁻⁴ cm ≈ **1.5 g cm⁻³**.
`[해석]` 같은 라벨의 "150 µm SSEs" 는 100 mg LPSC 펠릿 전체 두께가 아니라 **촬영한 부분
체적**(520 × 390 µm 시야)의 일부로 보인다. 분리층 실제 두께는 논문에 없다.

### 3.4 전기화학·분석 (§2.4–2.5) `[인쇄]`

| 항목 | 조건 |
|---|---|
| 충방전 | Neware CT-4008T, **0.9–2.4 V vs Li–In**, 상온 |
| CV | CHI 760e, **0.1–0.5 mV s⁻¹**, 같은 창 |
| GITT | **0.1 C 로 30 min 펄스 + 150 min 휴지**, 0.9–2.4 V |
| EIS | **10⁻¹ – 10⁶ Hz** (진폭 미기재) |
| XRD | Panalytical X'Pert, Cu Kα, **10–60° 2θ** |
| XPS | ESCALAB 250Xi, Al Kα, **C 1s 를 248.8 eV 로 보정** |
| SEM/EDS | Zeiss Supra 55 Sapphire |
| TEM | FEI TECNAI G2 F30 |
| 토모그래피 | **상하이 방사광(SSRF) BL13HB**, 기울기 **−60°~+60°, 1° 간격, 노출 2 s/장**, X Radia XMR 로 3D 재구성 |

`[해석]` XPS 보정값 "248.8 eV" 는 통상 **284.8 eV** 의 오타로 보인다 (C 1s adventitious carbon).
토모그래피는 ±60° 제한 각도라 **missing wedge** 가 있는 재구성이다 — 복셀 크기·분해능이
적히지 않아 "2 µm HES 입자의 연속 골격" 판정의 신뢰 구간을 알 수 없다.

### 3.5 DFT (§2.6) `[인쇄]`

VASP, GGA-PBE, PAW, cut-off **450 eV**, 잔류력 < **0.05 eV Å⁻¹**, 에너지 수렴 < **10⁻⁵ eV**,
k-point **1×1×1 (Γ)**, c축 진공층 **15 Å**, Bader 전하 해석. Li₂S 산화 경로는 **NEB**.

`[해석]` Γ-점 하나로 5원소 무질서 표면의 DOS·d-band center 를 논하는 것은 관례적이지만
정밀도가 낮다. HES 모델의 **양이온 배열을 어떻게 정했는지**(SQS? 임의?) 가 §2.6 에도
Fig. S17 캡션("Theoretical model of (a) HES")에도 없다 — 고엔트로피 재료 계산의 핵심 정보가 빠졌다.

---

## 4. p.354–355 — §3.1 HES 와 복합양극의 구조 (Fig. 2)

### 4.1 HES 자체 `[인쇄]` + `[도표, Fig. 2b–d]`

- 형태: **약 2 µm 구형 입자** (Fig. 2b; 삽입도 1 µm 스케일에서 표면이 나노 입자로 뭉친 구
  — 라즈베리형). `[도표]` 구 크기 분포는 대략 1–5 µm 로 보인다.
- EDS 맵(Fig. 2c): Ni, Co, Cu, Fe, Mn, S 가 한 입자 안에 균일 분포.
- 조성(Table S1) `[인쇄]`: Ni 15.68, Co 11.76, Cu 7.91, Fe 10.24, Mn 8.09, **S 46.32 at%**.
  `[재현]` 금속 합 53.68 : S 46.32 = **1.16 : 1**, Co₉S₈ 의 9:8 = 1.125 와 거의 같다 →
  화학식은 사실상 (Ni,Co,Cu,Fe,Mn)₉S₈ 계열이다.
- 배치 엔트로피(Table S2) `[인쇄]`: HES **1.54R**, Co₉S₈ **0.69R**. 본문은 "exceeds 1.5R,
  enabling its classification as a high entropy material [27]".
- HRTEM(Fig. 2d) `[도표]`: 격자 줄무늬 선명, **d₍₂₀₀₎ = 0.492 nm** 라벨, 삽입 FFT 는
  **[001] 정대, Fm-3m** 로 지수화. `[재현]` a = 2 × 0.492 = 0.984 nm (Co₉S₈ 의 a ≈ 0.993 nm 와
  1 % 이내).
- XPS(Fig. S1) `[인쇄]`: S 2p 는 **S²⁻ 와 S₂²⁻** → 금속황화물 존재. **sulfate 피크**도 있고
  "originates from the slight reaction between HES and oxygen [28]". 전이금속 중 **Cu·Fe·Mn 은
  단일 산화상태, Ni·Co 는 복수 산화상태**.

### 4.2 배치 엔트로피 계산의 재현 `[재현]` ★

식 S1 은 양이온 항과 음이온 항을 함께 쓰는 형태로 제시된다(§9.3). Table S1 의 at% 를 **모든
원소를 한 배치 풀로** 넣어 −R Σ xᵢ ln xᵢ 를 계산하면:

- HES: Ni .1568, Co .1176, Cu .0791, Fe .1024, Mn .0809, S .4632 → **1.536R ≈ 1.54R** ✓ 정확히 일치
- Co₉S₈: Co .5525, S .4475 → **0.687R ≈ 0.69R** ✓ 정확히 일치

즉 논문의 1.54R 은 **황을 배치 무질서의 구성원으로 세어** 얻은 값이고, 그 덕에 0.36R 가량이
더해졌다. `[재현]` 양이온 자리만으로 다시 계산하면 (Ni .292, Co .219, Fe .191, Mn .151, Cu .147)
→ **1.58R** 이므로 결론(> 1.5R)은 어느 셈법으로도 살아남는다. 다만 **같은 식으로 Co₉S₈ 에
0.69R 을 부여하는 것은 의미가 없다** — 정비 화합물의 "배치 엔트로피" 가 아니라 화학식 조성의
Shannon 엔트로피일 뿐이다. `[해석]` "고엔트로피" 라벨은 유효하나, 표 S2 가 보여 주는 "HES 2.2배
Co₉S₈" 라는 대비는 물리적 의미가 약하다.

### 4.3 복합양극의 구조 `[인쇄]` + `[도표, Fig. 2e–h]`

- XRD(Fig. 2e): HES 는 **PDF#65-6801(Co₉S₈)과 같은 단일상**, 불순물 없음. `[인쇄]` **29.8° 주피크가
  저각으로 약간 이동** → "additional multiple metal atoms (Ni, Cu, Fe, and Mn) occupy the lattice
  of Co [29]". S/HES/KB 에서는 S 특성 피크가 보이고, **LPSC 와 섞은 뒤에는 S 피크가 흐려진다**
  → `[인쇄]` "LPSC has covered the surface of sulfur [30]".
  `[해석]` 피크 감소는 피복만이 아니라 **볼밀에 의한 S 의 미세화/비정질화**로도 설명된다.
  논문은 그 대안을 검토하지 않는다.
- 토모그래피(Fig. 2f, f1, f2) `[도표]`: 재구성 부피 **520 × 390 µm**, **전극 26 µm + SSEs 150 µm**.
  (f1) "HES skeleton" — 전극 부피 안에 청록 점(HES)이 고르게 흩뿌려져 있다. (f2) "S loading" 은
  전극 전체를 통짜 슬래브로 렌더링. `[인쇄]` "the HES is homogeneously dispersed throughout the
  cathode, **forming a continuous HES skeleton structure**".
  `[해석]` (f1) 은 **점의 균일 분포**를 보여 주지 검은 점끼리의 **연결(percolation)** 을 보여 주지
  않는다. 연결성을 주장하려면 연결 성분 분석(labeling)이나 유효 전도도 계산이 필요한데 없다.
- 볼밀 후 분말 SEM(Fig. 2g) `[도표]`: 10 µm 스케일. **파랗게 칠한 S 입자가 2–6 µm**, 나머지 회색
  입자가 LPSC·HES. S 가 LPSC 에 완전히 피복된 모습은 아니고 **독립 입자로 보인다**.
- 단면 SEM(Fig. 2h) `[도표]`: 20 µm 스케일, 위 S/HES 층과 아래 SE 층이 `[인쇄]` "seamless
  interface" 로 맞물린다. 양극층 두께는 스케일바로 재면 **10–15 µm 정도로 보이나** 토모그래피
  라벨(26 µm)과 다르다 — 어느 쪽도 본문에 숫자로 없다.

### 4.4 HES 함량 최적화 (Fig. S4, S2, S3) ★ 우리 축

`[인쇄, §3.1]` "A series of sulfur composite cathodes with x wt% HES (x = 0, 10, and 20) …
Notably, the sulfur composite cathode with **10 wt% HES** exhibits higher specific capacity and
lower polarization voltage (Fig. S4). This improvement can be attributed to the fact that a
**higher HES content (20 wt%) may block the original electron conduction pathways established by
the conductive carbon**, thereby compromising the specific capacity … The poor electrochemical
performance of the composite cathode **without HES is due to the insufficient triple-phase
boundary**."

`[도표, Fig. S4]` 0.1 C 첫 사이클(0.9–2.4 V vs Li–In), 용량 축 라벨은 `mAh/g` (기준 미표기 —
§2.3 에 따라 S 기준으로 읽는다):

| HES 함량 (S 복합체 기준) | 최종 양극 기준 `[재현]` | 첫 방전 `[도표]` mAh g⁻¹(S) | (Li2S 환산) | (composite) | S 이용률 `[재현]` | 분극전압 `[도표, S4b]` |
|---|---|---|---|---|---|---|
| 0 wt% | 0 wt% | ≈ 660 | ≈ 461 | ≈ 277 | 39 % | **0.56 V** |
| **10 wt%** | **6 wt%** | ≈ **1280** | ≈ **893** | ≈ **538** | **76 %** | **0.38 V** |
| 20 wt% | 12 wt% | ≈ 970 | ≈ 677 | ≈ 407 | 58 % | 0.45 V |

`[해석]` **이 표가 이 논문에서 우리에게 가장 값진 한 칸이다.** 같은 LPSC 40 wt%, 같은 KB,
같은 성형 압력에서 **첨가제 없는 탄소 단독 양극은 S 이용률 39 % 에 그쳤다.** 소량(최종 6 wt%)
혼합전도체를 넣자 76 % 로 두 배가 됐고, 두 배(12 wt%) 넣자 다시 떨어졌다. **"소량이 최적"**
이라는 형태는 Kim 2023 의 CNT 3.1 wt% 최적과 같은 모양이다
([[carbon-dimensionality-electron-network]]).

`[도표, Fig. S2]` 0 wt% 와 20 wt% 의 토모그래피. 라벨은 둘 다 전극 26 µm / SSEs 150 µm /
520 × 390 µm. 0 wt% 의 "skeleton" 상자는 **비어 있다**("Skeleton-free"), 20 wt% 는 점이 촘촘하다.
`[도표, Fig. S3]` 입자 수 0 / ≈840 / ≈1910, 3D 면적 0 / ≈13.4 / ≈31.5 (×1000 **mm²** — 단위 오기,
G22), 3D 부피 0 / ≈5.8 / ≈14.6 (×1000 µm³).
`[재현]` 20 wt% / 10 wt% 비 = 입자수 2.27, 면적 2.35, 부피 2.52 — **거의 함량비(2배)** 다.
`[해석]` 따라서 Fig. S3 은 "분산 품질" 이 아니라 **넣은 만큼 보인다**는 확인일 뿐이고, 10 wt%
가 20 wt% 보다 나은 이유를 설명하지 못한다. 설명(전자 경로 차단)은 **측정되지 않은 추정**이다.

---

## 5. p.355–356 — §3.2 전기화학 성능 (★ 본체)

### 5.1 용량 환산 규칙 (이 절 전체에 적용) `[재현]`

- 원문 기준: **mAh g⁻¹(S)**.
- Li2S 환산: × **0.698** (= M(S)/M(Li₂S) = 32.06/45.95). "같은 전하량을 그것이 만들어 낼 Li₂S 의
  질량으로 나눈 값" — 우리 [[capacity-normalization-li2s-vs-sulfur]] 와 맞추기 위한 **가상 정규화**다.
- composite 환산: × **0.42** (S 가 최종 양극의 42 wt%).
- S 이용률: ÷ **1675 mAh g⁻¹(S)**.
- 면적용량: × **1.6 mg cm⁻²** (표준 셀).
- 전류밀도 `[재현]`: 1 C ≡ 1675 mA g⁻¹(S) → 1.6 mg cm⁻² 에서 **1 C = 2.68 mA cm⁻²**,
  0.5 C = 1.34, 2 C = 5.36 (≈ 원문 5.4), 3 C = 8.04 mA cm⁻².

### 5.2 핵심 수치표 (양단위 — 이 digest 의 결론 표)

| 조건 | `[인쇄]` mAh g⁻¹(S) | `[재현]` (Li2S 환산) | `[재현]` (composite) | `[재현]` 이용률 | `[재현]` mAh cm⁻² |
|---|---|---|---|---|---|
| 0.1 C 첫 방전 (10 wt% HES) `[도표]` | ≈1280 | ≈893 | ≈538 | 76 % | ≈2.05 |
| 0.5 C 1st (율속 시험) | **1025.2** | 715.6 | 430.6 | 61 % | 1.64 |
| 0.5 C 100th | **960.4** | 670.4 | 403.4 | 57 % | 1.54 |
| 1 C 1st | **925.1** | 645.7 | 388.5 | 55 % | 1.48 |
| 1 C 160th | **777.5** | 542.7 | 326.6 | 46 % | 1.24 |
| 1 C (율속 시험) | **909.3** | 634.7 | 381.9 | 54 % | 1.45 |
| 2 C = 5.4 mA cm⁻² | **683.7** | 477.2 | 287.2 | 41 % | 1.09 |
| 3 C | **376.4** | 262.7 | 158.1 | 23 % | 0.60 |
| 6 mg cm⁻², 0.05 C, 1st | `[재현]` 967 (= 5.8/6.0) | 675 | 406 | 58 % | **5.8** `[인쇄]` |
| 6 mg cm⁻², 0.05 C, 15th | `[재현]` 833 (= 5.0/6.0) | 582 | 350 | 50 % | **5.0** `[인쇄]` |
| 대조군 S/Co₉S₈ 0.5 C 100th | **558.6** | 389.9 | — | 33 % | 0.89 |
| 대조군 **첨가제 없음** 0.1 C 1st `[도표]` | ≈660 | ≈461 | ≈277 | 39 % | ≈1.06 |

`[해석]` 우리 목표 **500–600 mAh g⁻¹** 이 `(Li2S)` 기준이라면, 이 논문의 1 C 160사이클 값
(542.7) 과 0.5 C 100사이클 값(670.4) 사이에 있다. 즉 **문헌 수준 500–600 은 고체계 S8 양극이
상온에서 실제로 내는 범위와 겹친다** — 다만 그건 **활성화가 필요 없는 S8** 의 숫자다.

### 5.3 CV (Fig. 3a, b; Fig. S6)

- `[도표, Fig. 3a]` S/HES, 0.1→0.5 mV s⁻¹, 0.9–2.4 V vs Li–In. **환원 Peak I ≈ 0.95–1.15 V**
  (속도 증가에 따라 좌측 이동), **산화 Peak II ≈ 1.95–2.05 V**. 중간 단계 피크가 없다 →
  `[인쇄]` "solid-to-solid transition between Li₂S and S, **without any polysulfide intermediates**".
- `[도표, Fig. S6a]` 0.1 mV s⁻¹ 직접 비교(축 단위가 여기선 **mA mg⁻¹**, Fig. 3a 는 mA — 정규화가
  패널마다 다르다). 라벨: S/HES 환원 **1.15 V**, 산화 **1.90 V**.
  확대해 보면 **환원 최저점은 두 곡선이 거의 겹치고**(S/Co₉S₈ 도 ≈1.16 V), S/HES 쪽이 더 깊다
  (≈ −1.10 vs −1.00 mA mg⁻¹). 산화는 S/Co₉S₈ 가 ≈1.93 V 로 30 mV 높다. → **G16**.
- `[인쇄, 그림 내 라벨 Fig. 3b]` Randles–Ševčík 기울기 k: 산화 **S/HES 121.8 vs S/Co₉S₈ 86.2**,
  환원 **−117.6 vs −107.9**. `[재현]` 기울기비의 제곱이 D 비이므로 산화에서
  (121.8/86.2)² = **2.0배**, 환원에서 (117.6/107.9)² = **1.19배**.
  `[해석]` 논문은 "qualitative assessment" 라고 옳게 한정했다. 고체 복합전극에서 S, C₀ 가
  시료마다 다르므로 이 배율은 D 의 절대 비교가 아니다.

### 5.4 사이클 (Fig. 3c, d; Fig. S7, S8) ★ "안정" 이 무엇인가

| 셀 | 전류 | 초기 `[도표/인쇄]` | 말기 `[인쇄]` | 유지율 `[인쇄, 그림 내]` | CE |
|---|---|---|---|---|---|
| **S/HES** | 0.5 C | ≈1050 | **960.4** @100 | **91.4 %** (100 cyc) | `[도표]` ≈100 % |
| S/Co₉S₈ | 0.5 C | `[도표]` ≈650 | **558.6** @100 | `[도표, S7a]` **85.7 %** | ≈100 % |
| **S/HES** | 1 C | **925.1** | **777.5** @160 | **84.0 %** | `[인쇄, §4]` 평균 **> 99.89 %** |
| S/Co₉S₈ | 1 C | `[도표, S8]` ≈510 | `[도표]` ≈400 @160 | `[도표, S8]` **76.9 %** | ≈99 % |

`[해석]` **유지율에서 HES 가 이기는 폭은 크지 않다** (0.5 C 에서 91.4 vs 85.7 %p, 1 C 에서
84.0 vs 76.9 %p). HES 의 진짜 이득은 **절대 용량**이다 (0.5 C 100사이클에서 960.4 vs 558.6 =
1.72배). 초록의 헤드라인이 "84.0 % capacity retention" 인 것은 **자기 강점을 약한 축으로
광고**하는 셈이다. 셀이 하나씩이라(G4) 7 %p 차이는 더더욱 단정할 수 없다.

`[도표, Fig. 3d]` 1 C 곡선에는 **28–30 사이클 부근에 불연속**(≈890 → ≈865)이 있고 120–150
사이클 구간에서 CE 가 눈에 띄게 흔들린다. 본문은 언급하지 않는다.

`[인쇄, 그림 내 라벨 Fig. S7b]` 평균 충·방전 전압차: **S/HES 0.65 V(초기) → 0.69 V(100th)**,
**S/Co₉S₈ 0.78 → 0.82 V**. `[해석]` 0.5 C 에서조차 분극이 **0.65 V** 다. 0.9–2.4 V 창의 1/2 이
분극으로 쓰인다는 뜻이고, 이것이 이 계의 실제 상태다.

`[도표, Fig. 3e]` 0.5 C 의 1st vs 100th 곡선: S/HES 는 1st ≈1050 → 100th ≈1000 으로 평탄부
모양이 거의 안 변한다. S/Co₉S₈ 는 ≈650 → ≈560. 방전 평탄부는 **≈1.4 V vs Li–In**, 충전 평탄부는
**≈1.8–1.9 V vs Li–In** 로 읽힌다.

### 5.5 율속 (Fig. 3f, g; Fig. S10)

`[인쇄]` S/HES: **1025.2 / 909.3 / 683.7 / 376.4 mAh g⁻¹(S)** @ 0.5 / 1 / 2 / 3 C, 1 C 복귀 시
"essentially recovers" (`[도표]` ≈900).
`[도표, Fig. 3f]` S/Co₉S₈: ≈600 / ≈490 / ≈380→≈290 / ≈150, 복귀 ≈550.
`[재현]` 서론의 "1.8 times higher" 를 역산하면 대조군 2 C = 683.7/1.8 = **380** — Fig. 3f 의 2 C
**첫 점**과 맞는다. 구간 끝점(≈290)으로 재면 2.4배다. 즉 "1.8배" 는 가장 보수적인 읽기이며
이 경우엔 논문이 자기에게 유리하게 고르지 않았다.

`[인쇄, 그림 내 막대 Fig. 3g]` 과전압:

| C-rate | S/HES | S/Co₉S₈ |
|---|---|---|
| 0.5 C | `[도표]` 0.64 V | 0.73 V |
| 1 C | 0.76 V | 0.96 V |
| 2 C | 0.95 V | 0.98 V |
| 3 C | 1.07 V | 1.17 V |

`[해석]` **2 C 에서는 두 시료의 과전압이 사실상 같다**(0.95 vs 0.98 V). 그런데도 용량은 2.4배
차이가 난다. 즉 고율에서 갈리는 것은 전압 강하가 아니라 **몇 %의 황이 반응에 참여하는가**다 —
이 관측 자체는 논문의 "삼상 계면 밀도" 서사와 잘 맞고, 우리에게도 중요한 형태다.

`[도표, Fig. S10]` 두 시료의 율속 충방전 곡선. S/HES 는 3 C 에서도 평탄부가 남아 있고,
S/Co₉S₈ 는 2 C 부터 평탄부가 무너져 S 자 곡선이 된다.

### 5.6 고로딩 (Fig. S11) ★ 면적용량

`[인쇄, 캡션]` "charge-discharge curves and cycling stability **at 0.05 C** of S/HES and S/Co₉S₈
with a sulfur loading of **6.0 mg cm⁻²**".
`[도표]` (a) 첫 사이클: S/HES 방전 **5.8 mAh cm⁻²**, S/Co₉S₈ **2.9 mAh cm⁻²**.
(b) **15 사이클**: S/HES 5.8 → **5.0**, S/Co₉S₈ 2.9 → **≈2.2**.
`[재현]` 유지율 5.0/5.8 = **86 % (15 사이클)**; 비 5.0/2.2 = **2.3배** (본문은 "2.5 times").
`[재현]` 비용량 967 → 833 mAh g⁻¹(S) (Li2S 환산 675 → 582).
`[재현]` 0.05 C = 83.8 mA g⁻¹(S) × 6.0 mg cm⁻² = **0.50 mA cm⁻²**.

`[해석]` 5.8 mAh cm⁻² 는 이 분야에서 의미 있는 숫자지만 **0.50 mA cm⁻², 15 사이클**의 값이다.
초록이 "exceptional areal capacity" 라고 쓸 때 이 두 조건이 같이 적혀 있지 않다 (G18).

### 5.7 HES 자체의 용량 기여 (Fig. S9)

`[도표]` HES 를 활물질로 쓴 셀: **0.01 C 에서 37 → 33 mAh g⁻¹(HES)**, 0.5 C 에서 ≈2, 1 C 이상은
**≈0**. `[인쇄]` "the HES contributes a negligible discharge capacity".
`[재현]` 최종 양극에서 HES 는 6 wt%, S 는 42 wt% 이므로 S 기준으로 환산하면
37 × (6/42) = **5.3 mAh g⁻¹(S)** — 1025 의 0.5 % 다. **기여는 정말 무시할 수준이고, 이 대조는
논문에서 가장 깔끔한 대조 실험이다.**

### 5.8 문헌 비교 (Fig. 3h)

`[도표]` 3축 산점도 — x: 전류밀도(mA cm⁻²), y: 온도(°C, 위로 갈수록 낮음), z: 면적용량
(mAh cm⁻²). 참고문헌 [32,36–51] 20편이 점으로, 이 논문이 **빨간 별**로 오른쪽 위(고전류·저온·
고면적용량) 구석에 찍혀 있다. 수치 표는 없다.
`[해석]` 이 별의 좌표는 **서로 다른 셀의 최고치를 합성한 것**이다 — 면적용량 5.8 은 0.05 C
셀, 전류 5.4 mA cm⁻² 는 1.6 mg cm⁻² 셀이다. 한 셀이 동시에 낸 점이 아니다. 이 그림 하나만
보고 인용하면 안 된다.

---

## 6. p.356–357 — §3.3 개선의 근원: 전도도·GITT·DFT (Fig. 4)

### 6.1 DC 분극 전도도 (Fig. S12, S13, Table S3) ★★ 이 논문에서 가장 이식성 높은 방법

`[도표, Fig. S12]` 두 셀 구성이 도식으로 그려져 있다:
- **Ion-blocking (전자 전도도)**: SS | **시료** | SS.
- **Electron-blocking (이온 전도도)**: SS | Cu | LPSC | Li–In | **시료** | Li–In | LPSC | Cu | SS.

`[인쇄, 캡션]` 순물질(HES, Co₉S₈) 시료 두께 **0.2–0.3 mm**, 복합체(S/HES, S/Co₉S₈, S/KB) 시료
두께 **약 1.8 mm**.

`[인쇄, 그림 내 라벨]` 정상 전류:

| 시료 | ion-blocking (전자) | electron-blocking (이온) |
|---|---|---|
| HES | 85 mA | 7.03 µA (**2000 s 동안 22→8 µA 로 계속 감소**, G8) |
| Co₉S₈ | 7.49 mA | 0.14 µA |
| S/HES | 104 mA | 0.57 µA |
| S/Co₉S₈ | 44 mA | 0.017 µA |
| S/KB | 7.4 mA | 2.1×10⁻³ µA |

`[인쇄, Table S3]` 환산 결과 (단위 mS cm⁻¹):

| 시료 | σ_e⁻ | σ_Li⁺ |
|---|---|---|
| HES | **2.49** | **0.02** |
| Co₉S₈ | 0.19 | 4.09×10⁻⁴ |
| **S-HES** | **23.80** | **6.50×10⁻³** |
| S-Co₉S₈ | 10.10 | 1.95×10⁻⁴ |
| S-KB | 1.71 | 2.41×10⁻⁵ |

`[재현]` 식 S3 (σ = I·l /(U·S))로 검산: HES 전자, l = 0.025 cm, S = 0.785 cm², I = 85 mA →
σ = 2.71×10⁻³/U. Table S3 의 2.49×10⁻³ S cm⁻¹ 를 맞추려면 **U ≈ 1.09 V**. 반면 HES 이온,
I = 7.03 µA → σ = 2.24×10⁻⁷/U 이고 표의 2×10⁻⁵ S cm⁻¹ 를 맞추려면 **U ≈ 11 mV**. 두 측정의
인가 전압이 두 자릿수 다른데 **U 가 적혀 있지 않다** (G7).

`[재현]` 첨가제 효과 (S-KB 대비): 전자 1.71 → 23.80 = **13.9배**, 이온 2.41×10⁻⁵ → 6.50×10⁻³ =
**270배**.
`[해석]` **이 두 배율이 이 논문의 실질적 발견이다.** 다만 (i) 시료가 LPSC 를 포함한 최종
양극인지 불명(G6), (ii) 절대값 σ_Li⁺(S-HES) = 6.5×10⁻⁶ S cm⁻¹ 는 황화물 SE 의 통상 전도도보다
두세 자릿수 낮다 — 따라서 **HES 가 SE 를 대신해 이온을 나른다는 그림은 성립하지 않고**,
"SE 가 닿지 않는 국소 구간을 잇는다" 정도가 데이터가 허락하는 해석이다.
또 (iii) **HES 자체의 σ_Li⁺ 0.02 mS cm⁻¹ 는 감소하는 전류의 끝점**이며(G8), 이것이 진짜
Li⁺ 전도인지 잔류 전자 누설인지 가르는 대조(예: 시간에 따른 완전 포화 확인)가 없다.

### 6.2 GITT (Fig. 4a–c, Fig. S14)

- `[도표, Fig. 4a]` 정규화 용량 0→100 %(방전), 100→200 %(충전). S/HES 의 인가 전압과 OCV 의
  간격이 S/Co₉S₈ 보다 작다. `[인쇄]` "the S/HES cathode demonstrates a lower deviation in the
  corresponding normalized capacity".
- `[인쇄, 그림 내 라벨 Fig. S14c,d]` 최대 과전압:
  **충전 S/HES 0.6098 V vs S/Co₉S₈ 0.6501 V** (차 40 mV),
  **방전 S/HES 0.1943 V vs S/Co₉S₈ 0.1963 V** (차 **2 mV**, G15).
- `[인쇄, 그림 내 라벨 Fig. 4b,c]` log D_Li⁺ (cm² s⁻¹):

| | S/HES max | S/HES min | S/Co₉S₈ max | S/Co₉S₈ min |
|---|---|---|---|---|
| 방전 | −10.27 | −11.76 | −10.86 | −12.04 |
| 충전 | −9.85 | −12.21 | −10.46 | −12.49 |

`[재현]` 최대값 기준 HES 가 **3.9배(방전) / 4.1배(충전)** 높고, 최소값 기준 **1.9배 / 1.9배**다.
`[해석]` GITT 로 얻는 D 는 "apparent" 값이고 확산길이·계면면적 가정을 포함한다. 논문도
"apparent" 라고 적었다. 두 시료의 활성 면적이 다르면(바로 그것이 논문의 주장이다) **D 의
차이는 면적 차이의 되풀이**일 수 있다 — 즉 순환논증 위험이 있다.

### 6.3 dQ/dV 의 사이클 이동 (Fig. 4d, e; Fig. S15)

`[인쇄]` S/Co₉S₈ 는 1 C 160 사이클 후 환원 피크가 **−42.2 mV** 이동하고 세기가 크게 줄었다.
`[도표, Fig. 4d 삽입도]` S/HES 는 **−33.8 mV**.
`[해석]` 42.2 vs 33.8 mV — 8 mV 차이다. 피크 **세기** 감쇠의 차이가 훨씬 크다 (Fig. 4d 는 4사이클
곡선이 거의 겹치는 반면 Fig. 4e 는 1st 대비 160th 가 절반 이하). **이동이 아니라 세기**가
이 비교의 실질이다. Fig. S15 는 같은 것을 0.5 C 에서 반복한 것 (이 세션에서 보지 않았다 — §13).

### 6.4 DFT (Fig. 4f–i, Fig. S16–S18)

- **Li⁺ 이동 장벽 (NEB)**: `[인쇄, 그림 내 라벨 Fig. 4f]` HES 경로 0.121 / **0.202** / 0.188 /
  0.115 / −0.025 eV, Co₉S₈ 경로 0.146 / **0.253** / 0.247 / 0.154 / 0.012 eV. 본문은 **0.20 vs
  0.25 eV** 로 인용. `[재현]` 차이 0.051 eV — 상온에서 exp(0.051/0.0257) ≈ **7.3배**의 호핑 속도차.
- **자유에너지 도식 (Fig. 4g)**: `[도표]` x축 S₈ → Li₂S\* → Li₂S, y축 free energy 0–30 eV,
  "16 e⁻" 화살표, 중간체 Li₂S\* 가 **≈25 eV** 높이에 있고 두 곡선 차이가 **0.966 eV**.
  `[해석]` 16전자 반응 전체를 한 덩어리로 묶은 도식이라 **중간체가 25 eV 위에 있는** 비물리적
  형태가 됐다. 의미 있는 것은 두 재료의 차 0.966 eV 뿐이고, 그것도 어떤 표면·흡착구조에서
  계산했는지 §2.6 에 없다.
- **TDOS (Fig. 4h)**: `[도표]` 두 재료 모두 E_f 에 상태가 연속 → 금속성. `[인쇄, 그림 내 라벨]`
  d-band center: HES **−1.60 / −1.42 eV** (스핀 업/다운), Co₉S₈ **−1.80 / −1.49 eV**.
  → HES 가 E_f 에 더 가깝다 = `[인쇄]` "enhanced catalytic activity … from the synergetic
  interplay effects among multi-element composition [55]".
- **ELF (Fig. 4i, S18)**: `[도표]` HES 의 S 원자 주변 ELF 가 더 국재(붉은 고리). `[인쇄]` "HES can
  facilitate efficient charge transfer when introduced into the cathode".
  `[해석]` ELF 국재도가 높다 → 전하 전달이 잘 된다는 추론은 **논리가 연결되지 않는다**
  (ELF 국재는 보통 공유결합성/전자 국소화를 뜻한다). 인용 [56] 에 기댄 문장이다.

`[해석]` DFT 세 가지(NEB, 자유에너지, DOS)는 모두 **HES 표면 vs Co₉S₈ 표면**을 비교한다.
그러나 실험에서 달라진 것은 그것만이 아니다 — 두 재료는 전자 전도도가 13배, 이온 전도도가
50배 다르고(Table S3) 입자 형상도 다르다(Fig. 2b vs S5). **촉매 효과와 수송 효과를 가르는
실험은 없다** (§11-2).

---

## 7. p.357–358 — §3.3 후반: 사이클 후 구조와 DRT (Fig. 5, S19)

**주의 — 본문의 패널 지시가 그림과 어긋난다 (G5). 아래는 그림·캡션 기준으로 다시 쓴 것이다.**

- `[도표, Fig. 5a]` **Cycled S/Co₉S₈ electrode** (10 µm 스케일): 표면 전체에 **그물 모양 크랙**.
- `[도표, Fig. 5b]` **Cycled S/HES electrode**: 크랙 없음, 치밀·균질.
- `[도표, Fig. 5d]` Cycled S/Co₉S₈ **단면** (20 µm): 양극 내부와 양극|SE 계면에 **공동(void)/
  크랙**이 점선 타원으로 표시.
- `[도표, Fig. 5f]` Cycled S/HES 단면: 계면이 "Conformal interface" 로 붙어 있다.
- `[도표, Fig. 5e, g]` 도식: 비활성 황이 많으면 **활성 황에만 부피변화가 몰려 국부 응력 →
  크랙**; HES 가 있으면 활성 황이 고르게 퍼져 **균질 응력 → 구조 유지**.
- `[도표, Fig. 5c]` DRT: 두 피크 — **P1 (τ ≈ 0.3–1 s, 고체 확산)**, **P2 (τ ≈ 0.01–0.02 s, 전하이동)**.
  γ(τ) 최대: S/HES-pristine ≈250 Ω, S/HES-cycled ≈470 Ω, S/Co₉S₈-pristine ≈340 Ω,
  S/Co₉S₈-cycled ≈700 Ω. 즉 **네 곡선 모두 사이클 후 커지고, 항상 S/HES 가 더 작다**.
  `[인쇄]` 본문의 P1/P2 τ 범위 표기는 "10⁻¹–10⁰ s" 와 "10⁻²–10⁻¹ s".
- `[도표, Fig. S19]` 원 EIS. **범례 색이 본문 그림과 반대다** (여기선 S/HES 가 하늘색,
  S/Co₉S₈ 가 주황). (a) fresh: 둘 다 고주파 절편 ≈25–30 Ω, 반원이 뚜렷하지 않고 거의 직선.
  (b) cycled: S/HES 절편 **≈75 Ω**, S/Co₉S₈ **≈45 Ω**, 전 구간에서 S/HES 의 Z′ 가 더 크다.

`[해석]` **Fig. S19(b) 와 Fig. 5(c) 는 같은 방향을 가리키지 않는다** (G17). 등가회로 피팅값이
없으므로 어느 쪽이 옳은지 이 digest 로는 판정할 수 없다. 다만 **"HES 셀의 사이클 후 총
임피던스가 더 작다" 는 주장은 Fig. S19 에서 읽히지 않는다**는 사실은 기록해 둔다.

`[해석]` 크랙 SEM 은 이 논문에서 가장 설득력 있는 그림이다. 다만 **압력 조건이 없어(G1)**
"크랙이 생겼다/안 생겼다" 가 재료 차이인지 셀 조립·해체 과정의 차이인지 분리되지 않는다.
사이클 수·SoC(충전 상태에서 해체했는지 방전 상태인지)도 적혀 있지 않다.

---

## 8. p.358 — §4 Conclusions

`[인쇄]` 요지:
1. HES 를 복합 황 양극에 넣는 것이 황 산화환원 동역학을 조절하는 핵심 전략이다.
2. **다금속 자리의 시너지 촉매 효과**가 전하 전달 효율을 높이고 반응 장벽을 낮춘다.
3. **싱크로트론 X-ray 토모그래피**로 HES 의 균일 분산을 확인했고, 그것이 더 많은 활물질을
   반응에 참여시킨다.
4. 활물질의 **균질한 이용이 응력 집중을 억제**하고 사이클 후 구조 건전성을 유지한다.
5. 성능: **683.7 mAh g⁻¹ @ 5.4 mA cm⁻²**, **84.0 % @ 160 cycles, 1 C (평균 CE > 99.89 %)**,
   **5.8 mAh cm⁻² @ 6 mg cm⁻²(S)**.
6. 전망: 인공 SEI [58], redox-mediating glassy sulfides [59], **합금 음극** [60] 과의 결합.
   고엔트로피 설계는 수계 아연전지·금속공기전지·슈퍼커패시터로도 일반화될 수 있다.
7. `[인쇄]` "advanced structure-function studies are needed to **decouple the synergistic roles
   and operational mechanisms of constituent elements**" — **저자들 스스로 원소별 역할 분리가
   안 됐음을 인정한다.**

`[해석]` 7번 문장이 이 논문의 가장 정직한 부분이고, 우리가 §11-2 에서 적을 비판과 같은 내용이다.

---

## 9. SI 전문 대조

SI(.docx)는 **그림 19장 + 식 3개 + 표 3개 + 참고문헌 4개**로 이뤄져 있고 본문 서술은 거의 없다
(캡션이 전부다). 아래에 **캡션 전문**을 옮기고, 이 세션에서 실제로 본 그림에는 판독값을 붙였다.

### 9.1 SI 그림 목록 (캡션 `[인쇄]`)

| # | 캡션 | 이 digest 에서 |
|---|---|---|
| S1 | XPS of HES. (a) S 2p. (b) Ni 2p. (c) Co 2p. (d) Cu 2p. (e) Fe 2p. (f) Mn 2p. | §4.1 (캡션·본문 서술만) |
| S2 | Synchrotron X-ray tomography … spatial distribution of S and HES. (a) 0 wt% HES. (b) 20 wt% HES. | §4.4 ✓본 |
| S3 | Statistical distribution characteristics of HES. (a) Particle number. (b) 3D area. (c) 3D volume. | §4.4 ✓본 (단위 오기 G22) |
| S4 | Electrochemical performance of different cathodes. (a) The initial charge-discharge curves at 0.1 C current density. (b) The corresponding polarization voltage. | §4.4 ✓본 ★ |
| S5 | (a) SEM image of Co₉S₈. (b)-(c) the corresponding EDS elemental maps | 미열람 |
| S6 | CV curves of different cathodes. (a) CV curves of S/HES and S/Co₉S₈ at a scan rate of 0.1 mV s⁻¹. (b) CV curves of S/Co₉S₈ at a scan rate of 0.1-0.5 mV s⁻¹. | §5.3 ✓본 (확대 판독) |
| S7 | (a) Cycling stability of S/Co₉S₈ at 0.5 C. (b) Average charge and discharge voltage during cycling. | §5.4 ✓본 ★ |
| S8 | Cycling stability of S/Co₉S₈ at 1 C. | §5.4 ✓본 |
| S9 | The discharge capacity of the batteries using HES as the active materials. | §5.7 ✓본 ★ |
| S10 | The charge-discharge curves of (a) S/HES. (b) S/Co₉S₈. at different current densities. | §5.5 ✓본 |
| S11 | The (a) charge-discharge curves and (b) cycling stability at 0.05 C of S/HES and S/Co₉S₈ with a sulfur loading of 6.0 mg cm⁻². | §5.6 ✓본 ★ |
| S12 | Electronic/ionic conductivity measurement of different materials [4]. (a) … ion-blocking conditions … (b) … electron-blocking conditions … The thickness of the sample is 0.2~0.3 mm. | §6.1 ✓본 ★ |
| S13 | Electronic/ionic conductivity measurement of different composite. … The thickness of the sample is about 1.8 mm. | §6.1 ✓본 ★ |
| S14 | GITT measurement of ASSLSBs. (a) Basic unit during the charge process. (b) … discharge … (c) Overpotential during the charge process. (d) … discharge. | §6.2 ✓본 ★ |
| S15 | The differential capacity (dQ/dV) curves of a) S/HES, b) S/Co₉S₈ with different cycle numbers at 0.5 C. | 미열람 |
| S16 | Diffusion path of Li⁺ on Co₉S₈ surface. | 미열람 |
| S17 | Theoretical model of (a) HES. (b) Co₉S₈. The charge density maps of (c) HES. (d) Co₉S₈. | 미열람 |
| S18 | The electron localization function of Co₉S₈. | 미열람 |
| S19 | Electrochemical impedance spectra of fresh batteries and cycled batteries. | §7 ✓본 ★ |

`[해석]` SI 의 인용 [4] 는 **C.Y. Kwok, S. Xu, I. Kochetkov, L. Zhou, L.F. Nazar, *Energy
Environ. Sci.* 16 (2023) 610–618** — DC 분극 셀 구성을 그대로 따온 출처다. 우리가 같은 측정을
할 때 1차 참고문헌이 된다.

### 9.2 SI 참고문헌 `[인쇄]`

[1] S.-J. Yang et al., *Chem. Eng. J.* 502 (2024) 157789 · [2] Z.-M. Qiang et al., *Sci. Bull.* 2025 ·
[3] J.-L. Yang et al., *Nat. Commun.* 16 (2025) 8910 · [4] C.Y. Kwok et al., *Energy Environ. Sci.*
16 (2023) 610–618.

### 9.3 Supporting Equations `[인쇄]` (수식 자체는 WMF 객체 — 변수 정의를 옮긴다)

- **Eq. S1 (배치 엔트로피)**: `M, N` = 양이온·음이온 원소 종의 수, `xᵢ, xⱼ` = 양이온·음이온
  자리의 몰분율, `R` = 기체상수. → §4.2 에서 재현 (모든 원소를 한 풀로 세면 1.54R 이 정확히 나온다).
- **Eq. S2 (Randles–Ševčík)**: `Ip` = CV 피크 전류(A), `n` = 전달 전자수, `S` = 양극 표면적(cm²),
  `C₀` = 양극 내 Li⁺ 농도(mol cm⁻³), `v` = 주사속도(V/s), `D_Li⁺` = Li⁺ 확산계수(cm² s⁻¹).
- **Eq. S3 (DC 분극 전도도)**: `k = e⁻ 또는 Li⁺`, `σ_k` = 전자/이온 전도도(S cm⁻¹),
  `I_k` = 정상 전류(A), `l` = 시료 두께(cm), `U` = DC 분극 전압(V), `S` = 시료 면적(cm⁻² *원문 표기*).
  → **U 의 값이 어디에도 없다** (G7).

### 9.4 Supporting Tables `[인쇄]` (전문)

**Table S1 — 원소 조성 (at%)**

| Sample | Ni | Co | Cu | Fe | Mn | S |
|---|---|---|---|---|---|---|
| HES | 15.68 | 11.76 | 7.91 | 10.24 | 8.09 | 46.32 |
| Co₉S₈ | – | 55.25 | – | – | – | 44.75 |

**Table S2 — 배치 엔트로피**: HES **1.54R**, Co₉S₈ **0.69R**.

**Table S3 — 전자/이온 전도도 (mS cm⁻¹)**: §6.1 의 표 그대로.

---

## 10. 우리 연구와의 접점

### 10.1 조성·공정 나란히 보기

| 축 | 이 논문 (S/HES) | 우리 [[li2s-assb-reference-cell]] | 비고 |
|---|---|---|---|
| 활물질 | **S₈ 42 wt%** | **Li₂S 30 wt%** | 방향이 반대 (방전 시작 vs 충전 시작) |
| SE | LPSC **40 wt%**, 분리층 100 mg @350 MPa | LPSCl **50 wt%** | 같은 계열 |
| 탄소 | **Ketjen Black 12 wt%** | **AB 20 wt%** | KB 는 고표면적 0D, AB 도 0D |
| 첨가제 | **HES 6 wt%** | 없음 | ← 이 논문의 변수 |
| 성형 | 양극 **450 MPa** | (기록 필요) | 이식 가능 |
| 운전 압력 | **미기재 (G1)** | (기록 필요) | 비교 불가 |
| 음극 | **Li–In** (사양 미기재) | Li–In → anode-free | 같은 출발점 |
| 창 | **0.9–2.4 V vs Li–In** | (Li₂S 는 더 높은 상한 필요) | 그대로는 못 옮김 |
| 온도 | "room temperature" (수치 없음) | 상온 | |
| 혼합 | 그라인딩 → **155 °C 12 h 융합** → LPSC 와 **350 rpm 4 h planetary** | (경로 비교 중) | two-step 계열, SE 는 고에너지 단계에 포함 |

### 10.2 옮길 수 있는 것 / 없는 것

| 이 논문이 보여 준 것 | 우리에게 옮길 수 있는가 | 왜 |
|---|---|---|
| **탄소 단독 양극의 S 이용률이 39 % 에 그친다** (Fig. S4, 0 wt% HES) | **부분적으로 ○** — "탄소만으로는 삼상 계면이 부족하다" 의 고체계 직접 근거 | 단 S8 이고 사이클 데이터가 없다(G10) |
| **소량(6 wt%) 혼합전도체 첨가 → 이용률 39→76 %** | **○ 가설로** — 우리 AB 20 wt% 의 일부를 첨가제로 바꾸는 실험 설계 가능 | 이 논문은 **탄소를 줄이지 않았다**. HES 는 활물질/탄소 비를 유지한 채 **추가**된 것이다 (§10.3) |
| **12 wt% 는 오히려 나쁘다** ("전자 경로 차단") | **○ 경고로** | 근거는 측정이 아니라 추정 (G22 참조) |
| **DC 분극으로 복합체 σ_e⁻·σ_Li⁺ 를 따로 재는 셀 구성** (Fig. S12, 출처 Kwok 2023) | **◎ 가장 값싼 이식** — 우리 30:50:20 펠릿의 두 전도도를 직접 잴 수 있다 | 우리 H2(퍼콜레이션)를 **셀 조립 없이** 가르는 유일한 수단 |
| LPSC 40 wt% + KB 12 wt% + 450 MPa 로 상온 55–61 % 이용률 | **○ 기준선으로** | 우리 SE 50 wt% 와 조성이 다르다 |
| 사이클 후 크랙 유무가 이용률과 연결된다는 그림 | **△** | 압력 미기재(G1)로 인과가 갇혀 있다 |
| **첫 충전 활성화** | **✗ — 이 논문에 없다** | S8 출발이라 첫 스텝이 방전이다. Li₂S 활성화 과전압·컷오프에 대해 **한 글자도 없다** |
| 0.9–2.4 V vs Li–In 창 | **✗ 그대로는** | Li₂S 를 충전하려면 상한을 더 올려야 하고, 그러면 LPSCl 산화 문제가 새로 생긴다 |
| Li 재고·N/P·anode-free | **✗** | Li–In 사양이 없다 (G20) |
| 에너지밀도 | **✗** | 논문에 셀 수준 계산이 없다 |

### 10.3 가장 중요한 한 가지 오해 방지 `[해석]`

사용자의 질문 형태는 "**우리 AB 20 wt% 를 HES 로 일부 대체할 수 있는가**" 였다. 이 논문은
그 질문에 답하지 않는다:

- HES 10 wt% 는 **S 복합체 안에서 S 를 밀어낸 것**이다 (S:첨가제:KB = 70:10:20 — KB 는 세
  조건에서 20 wt% 로 **고정**). 즉 **탄소를 줄인 것이 아니라 활물질을 줄였다**.
  (0 wt% 조건에서 그 10 wt% 를 무엇으로 채웠는지는 미기재 — G9.)
- 따라서 이 논문이 지지하는 설계는 "**AB 를 HES 로 바꾼다**" 가 아니라
  "**활물질을 조금 덜어 혼합전도체를 넣는다** (탄소는 그대로)" 이다.
- 우리 셀로 옮기면: Li₂S 30 / LPSCl 50 / AB 20 → **Li₂S 26–28 / LPSCl 50 / AB 20 / 첨가제 2–4**
  가 이 논문의 논리에 가장 가까운 변형이다. AB 를 깎는 변형(AB 16 + 첨가제 4)은 **이 논문의
  근거 밖**이며, 오히려 논문이 "전자 경로 차단" 을 걱정한 방향이다.

### 10.4 가장 값싼 다음 실험 `[해석]`

1. **셀을 만들지 않고**: 우리 30:50:20 복합양극 펠릿을 Fig. S12 의 두 구성
   (SS|시료|SS, SS|Cu|LPSCl|Li–In|시료|Li–In|LPSCl|Cu|SS)으로 눌러 **σ_e⁻ 와 σ_Li⁺ 를 잰다**.
   인가 전압(전자 1 V / 이온 10–20 mV)과 두께를 우리는 반드시 기록한다(G7 을 반복하지 않기).
   → [[reference-cell-500-600-mahg]] H2 를 **한 번의 측정으로** 가른다.
2. 같은 측정을 **AB 함량 10 / 20 / 30 wt%** 로 반복하면 "탄소가 모자란가 남는가" 가 곧장 나온다.
3. 그 다음에야 첨가제(상용 Co₉S₈·FeS·NiS 등 값싼 전이금속 황화물 2–4 wt%)를 얹고,
   **첫 충전 활성화량**을 지표로 본다 — 이 논문이 답하지 않은 축이므로 여기부터는 우리가
   새로 만드는 데이터다.

---

## 11. 비판 (이 digest 의 판단)

1. **대조군이 "첨가제 없음" 이 아니라 "덜 좋은 첨가제" 다** (G10). 100·160 사이클 비교는 전부
   HES vs Co₉S₈ 이고, 우리가 가장 알고 싶은 **S/KB 단독의 수명**은 측정되지 않았다. Fig. S4 의
   0 wt% 곡선 하나(0.1 C 첫 사이클)가 전부다.
2. **세 기능(전자 전도·이온 전도·촉매)이 분리되지 않았다.** HES 와 Co₉S₈ 는 세 축이 동시에
   다르다. 논문의 DFT 는 촉매/이동장벽만 비교하고, Table S3 은 수송만 비교하며, 둘을 가르는
   실험은 없다. **저자들도 결론에서 이를 인정한다** (§8-7). 예컨대 "같은 전도도의 비촉매성
   혼합전도체" 나 "촉매성이지만 절연인 입자" 대조가 있었으면 갈렸다.
3. **"84.0 % 유지율" 은 이 논문의 강점이 아니다.** 대조군도 76.9 %(1 C)·85.7 %(0.5 C)로 비슷하다.
   실제 차이는 **절대 용량 1.7–2.4배**인데 초록은 유지율을 앞세운다. 게다가 셀은 하나씩이다(G4).
4. **초록의 세 수치가 세 셀·세 조건이다.** 특히 5.8 mAh cm⁻² 는 **0.05 C·15 사이클**(G18)이고,
   5.4 mA cm⁻² 는 1.6 mg cm⁻² 셀의 2 C 값이다. Fig. 3h 의 "빨간 별" 은 이 둘을 한 점에 합성한
   그림이다 — 인용 시 반드시 조건을 붙여야 한다.
5. **논문 내부 수치 불일치 1건**(서론 6.83 vs 초록·결론 5.4 mA cm⁻², G3), **본문의 그림 패널
   지시 오류 1건**(Fig. 5, G5), **XPS 보정값 오타 추정 1건**(248.8 eV), **SI 축 단위 오기 1건**
   (Fig. S3 의 mm², G22). 편집 품질이 고르지 않다.
6. **"고이온전도" 라는 수사가 데이터와 맞지 않는다.** HES 의 σ_Li⁺ 는 **2×10⁻⁵ S cm⁻¹**
   (그것도 감소 중인 전류의 끝점, G8)로, 황화물 SE 보다 두세 자릿수 낮다. 정확히 말하면
   HES 는 **"전자는 잘 나르고 이온도 아주 조금은 나르는" 입자**이며, 그 "아주 조금" 이
   SE 가 닿지 않는 구간을 메웠다는 것이 가능한 해석이다. 서론이 인용한 [26]의 "high ionic
   conductivity derived from high-entropy cation mixing" 은 이 재료에서 입증되지 않았다.
7. **엔트로피 계산이 음이온을 배치 무질서에 포함한다** (§4.2). 결론(>1.5R)은 양이온만 세도
   유지되지만, Co₉S₈ 에 0.69R 을 부여해 대비를 만드는 방식은 의미가 없다.
8. **압력·온도·음극 사양·바인더·집전체가 없다** (G1, G19, G20, G21). ASSB 논문에서 스택 압력이
   없는 것은 재현성 측면에서 가장 큰 결손이다.
9. **좋은 점도 분명하다**: (i) HES 자체의 용량 기여를 따로 측정한 Fig. S9 는 첨가제 논문에서
   드물게 깔끔한 음성 대조다. (ii) DC 분극으로 σ_e⁻·σ_Li⁺ 를 **복합체 수준에서** 따로 잰 것은
   우리가 그대로 베낄 만한 방법이다. (iii) 토모그래피로 첨가제 분산을 3D 로 본 것은 SEM
   이상의 정보다. (iv) 사이클 후 크랙 SEM 은 시각적으로 설득력이 높다. (v) 결론에서 스스로
   "원소별 역할이 분리되지 않았다" 고 적은 정직함.

---

## 12. 이 저장소가 가져갈 것

- **개념 신설 후보**: `mixed-conductor-cathode-additive` — "삼상 계면을 늘리기 위해 **소량의
  혼합 이온–전자 전도체**를 복합양극에 넣는다" 는 설계 원리. 이 논문이 첫 근거이고,
  [[carbon-dimensionality-electron-network]] 의 자매 개념이다 (탄소 차원 분리 ↔ 전도 기능 분리).
- **개념 신설 후보**: `dc-polarization-conductivity` — ion-blocking / electron-blocking 셀로
  복합양극의 σ_e⁻·σ_Li⁺ 를 따로 재는 절차 (Fig. S12–S13, 출처 Kwok 2023 *EES* 16, 610).
  우리 H2 를 가르는 **가장 값싼 측정**이므로 guide 로 만들어도 좋다.
- **기존 개념 갱신**: [[li2s-assb-composite-cathode]] 에 고체계 실측 조성/압력/두께
  (S 42 / 첨가제 6 / KB 12 / LPSC 40 wt%, 450 MPa, 26 µm, 겉보기 1.5 g cm⁻³) 를 더한다.
  [[capacity-normalization-li2s-vs-sulfur]] 에 §5.2 의 양단위 표를 더한다 (ASSB 문헌도 (S) 기준).
  [[mixing-equipment-ball-mill-thinky]] 에 "planetary 350 rpm 4 h, S 복합체 + LPSC, Ar" 한 줄과
  빠진 칸(BPR·볼·용기)을 기록한다.
- **질문 카드 라우팅**:
  - [[reference-cell-500-600-mahg]] — **H2(퍼콜레이션 제한)에 고체계 직접 근거**:
    첨가제 없는 S/KB/LPSC 양극의 0.1 C 첫 방전이 **≈660 mAh g⁻¹(S) = 이용률 39 %**,
    혼합전도체 6 wt% 로 **76 %** (Fig. S4). 복합체 전도도는 σ_e⁻ 1.71→23.80 mS cm⁻¹,
    σ_Li⁺ 2.41×10⁻⁵→6.50×10⁻³ mS cm⁻¹ (Table S3). **H1(활성화)에는 근거를 주지 않는다**
    (S8 양극). **H4(단위)**: 이 논문은 (S) 기준을 명시하며, 우리 목표 500–600 을 (Li2S) 로
    읽으면 이 논문의 1 C 160사이클 값(542.7)과 겹친다. **H3(입자)**: 근거 없음.
  - [[one-step-vs-two-step-mixing]] — **two-step(활물질–탄소 먼저, SE 나중) 계열의 고체계
    성공 사례**. 단 "나중" 이 mild mixing 이 아니라 **350 rpm 4 h 고에너지 볼밀**이므로
    카드의 H2(SE 를 고에너지 단계에서 빼야 한다)를 **지지하지 않는다** — SE 를 고에너지에
    넣고도 상온 55–61 % 이용률이 나왔다는 **H2 에 대한 약한 반대 근거**로 기록해야 한다.
- **비교 페이지**: digest 가 2편이 됐으므로 `comparisons/` 에 "액체계 Li2S(Kim 2023) vs 고체계
  S8(Huang 2026)" 의 조성·단위·활성화 대조표를 만들 수 있다.

---

## 13. 그림 판독 기록 (무엇을 보고 무엇을 안 봤는가)

| 그림 | 봤는가 | 어디에 썼는가 |
|---|---|---|
| Fig. 1 (a,b) | ✓ | §2.3 (도식의 스케일 문제 지적) |
| Fig. 2 (a–h) | ✓ | §3.2, §4.1, §4.3 (26 µm·520×390 µm·d₍₂₀₀₎ 는 그림 내 라벨) |
| Fig. 3 (a–h) | ✓ | §5 전체 — 가장 오래 봤다 |
| Fig. 4 (a–i) | ✓ | §6.2–6.4 (NEB·d-band·logD 는 그림 내 라벨) |
| Fig. 5 (a–g) | ✓ | §7 — **본문 패널 지시 오류(G5)를 여기서 잡았다** |
| Fig. S2 | ✓ | §4.4 |
| Fig. S3 | ✓ | §4.4 (단위 오기 G22) |
| Fig. S4 | ✓ | §4.4 ★ 이 digest 에서 가장 중요한 SI 그림 |
| Fig. S6 | ✓ (확대 판독) | §5.3 — **G16 을 여기서 잡았다** |
| Fig. S7 | ✓ | §5.4 |
| Fig. S8 | ✓ | §5.4 |
| Fig. S9 | ✓ | §5.7 |
| Fig. S10 | ✓ | §5.5 |
| Fig. S11 | ✓ | §5.6 ★ |
| Fig. S12 | ✓ | §6.1 ★ — G8 을 여기서 잡았다 |
| Fig. S13 | ✓ | §6.1 ★ |
| Fig. S14 | ✓ | §6.2 — G15 를 여기서 잡았다 |
| Fig. S19 | ✓ | §7 — G17 을 여기서 잡았다 |
| **Fig. S1, S5, S15, S16, S17, S18** | **✗ 캡션과 본문 서술만** | 크로핑은 돼 있다 (`fig_S1.png` 등). S1(XPS 귀속)·S17(DFT 모델)은 위 §11-2·§3.5 의 비판을 더 단단히 하려면 직접 볼 것. |

본문 서술과 어긋난 그림: **Fig. 5 (G5), Fig. S6a (G16), Fig. S19 vs Fig. 5c (G17)** — 셋.
본문 안에서 서로 어긋난 수치: **G3** (5.4 vs 6.83 mA cm⁻²) 하나.
