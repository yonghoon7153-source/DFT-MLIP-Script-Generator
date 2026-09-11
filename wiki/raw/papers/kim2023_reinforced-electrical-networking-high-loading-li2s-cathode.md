---
title: "Kim et al. 2023 — Long-lasting, reinforced electrical networking in a high-loading Li2S cathode for high-performance Li–S batteries (Carbon Energy 5, e308)"
description: "2D graphene(접촉) + 1D CNT(네트워크) 복합 탄소와 1 GPa 압축 성형으로 micro-Li2S 75 wt% 고로딩 양극을 만들고, 첫 충전의 Li2S→S8 직접 전환을 in situ Raman·OM·cryo-TEM 으로 보인 논문 — 흑연 full cell 800 사이클"
source_url: local-upload/fc3d9daa-Carbon_Energy__2023__Kim__Long_lasting__reinforced_electrical_networking_in_a_high_loading_Li2S_cathode_for.pdf + f09db30e-cey2308sup0002supporting_information_1.docx
doi: 10.1002/cey2.308
ingested: 2026-09-11
sha256: eb11791c1f47fde4004e6cf1817fcb9af7b5b8c23cd1c784d66c54575ec8e6d6
tags: [li2s, carbon, activation, cathode-design, liquid-electrolyte, li-free-anode, seminar]
compare:
  system: "Li–S (liquid, ether)"
  electrolyte: "0.5 M LiTFSI + 0.8 M LiNO3 in DME:DOL 1:1 (half) · 2.5 M LiTFSI + 0.4 M LiNO3 (full)"
  cathode: "Li2S : Gr/CNT = 75 : 25 wt (Gr:CNT 7:1), binder-free pellet"
  li2s_source: "commercial micro Li2S 1–5 µm (Sigma 99.98 %)"
  mixing: "ultrasonic Gr/CNT in NMP → ball milling with Li2S (조건 미기재) → 1 GPa 5 min pellet"
  loading_mg_cm2: "15 (half) · 10 (full, pouch)"
  li2s_wt_pct: 75
  anode: "Li metal 200 µm (half) · graphite N/P 1.2 (full)"
  first_charge: "0.1 C to 3.6 V (half 1.9–3.6 V; full 1.6–3.6 V)"
  first_discharge_mAh_gS: 1150
  first_discharge_mAh_gLi2S: 800
  cycle_capacity_mAh_gS: "899.6 @ 0.5 C (half) · ~760 @ 0.2 C (full)"
  cycle_capacity_mAh_gLi2S: "628 (half) · 530 (full)"
  areal_mAh_cm2: "11.5 → 9.3 (half, 100 cyc) · 5.3 → ~2.3 (full, 800 cyc)"
  cycles: "100 (half, 84.9 %) · 800 (full, 43.0 %)"
  temperature_C: 30
  mechanism: "direct conversion Li2S → S8 (no LiPs), in situ Raman/OM + cryo-TEM"
  our_axis: "탄소 차원 분리·압축 성형·첫 충전 활성화량 → 우리 ASSB reference cell 설계에 이식 가능; 전해질·전압창은 불가"
---

# 수집 목적

H. Kim, K.-J. Min, S. Bang, J.-Y. Hwang, J. H. Kim, C. S. Yoon, Y.-K. Sun,
**"Long-lasting, reinforced electrical networking in a high-loading Li2S cathode
for high-performance lithium–sulfur batteries"**, *Carbon Energy* **5** (2023) e308,
DOI 10.1002/cey2.308 (open access, CC BY) 의 **절별 해체분석** + SI 전문 대조.

이 위키가 이 논문을 첫 번째로 흡수하는 이유는 둘이다.

1. **사용자의 논문 세미나 대상 논문**이다 (2026-09-11 요청). 발표 구성은
   [[kim2023-seminar-prep]] 에 따로 정리한다 — 이 digest 는 그 발표의 **근거 층**이다.
2. 우리 연구([[li2s-assb-reference-cell]]: Li2S:LPSCl:AB = 30:50:20 복합양극, 목표
   500–600 mAh g⁻¹)와 **같은 문제 — 절연체 Li2S 를 어떻게 활성화하고 어떻게 전자
   경로를 유지하는가 — 를 액체 전해질에서 푼 사례**다. 전해질은 다르지만
   (에테르 액체 vs 황화물 고체) **탄소 설계 원리·1 GPa 압축 성형·첫 충전 활성화가
   수명 용량을 결정한다는 관측**은 그대로 우리 축에 걸린다. 같은 학교(한양대
   에너지공학과 선양국 그룹)의 논문이라는 점도 세미나 맥락에서 의미가 있다.

**표기 규칙** (이 위키 관례 3구분 + 1):
- `[인쇄]` — 논문 본문/식/표/SI 에 글자로 있는 것
- `[도표]` — 그림에서 눈으로 읽은 근사값 (**원 데이터가 아니다**)
- `[해석]` — 이 문서를 쓰면서 붙인 판단. **논문의 주장이 아니다**
- `[재현]` — 원문 값을 이 세션에서 산술로 옮긴 것 (계산식을 함께 적는다)

- 원본 파일: 로컬 업로드 PDF 14쪽 + SI(.docx, 그림 11장 + 표 2개). 저장소에 바이너리
  원문은 넣지 않는다.
- 크로핑 그림: `raw/figures/kim2023_reinforced-electrical-networking-high-loading-li2s-cathode/`
  — 본문 Fig. 1–8 은 도구(`wiki/tools/extract_figures.py`)가 캡션 앵커로 잘랐고,
  **SI Fig. S1–S11 은 .docx 에 내장된 이미지를 문서 순서대로 꺼내** `fig_S1.png`…
  `fig_S11.png` 로 두었다 (`figures.json` 에 캡션과 함께 등록). Table S1·S2 는 텍스트
  표라 아래 §9·§10 에 그대로 옮겼다.
- 페이지 참조는 **PDF 페이지**(1–14) = 저널 조판 페이지 ("n of 14").

---

# 원문에 없어서 확인이 필요한 것 (읽기 전에 먼저 본다)

이 절이 이 digest 의 가장 중요한 산출물이다. 아래는 **논문이 답을 주지 않는 것**이고,
그중 여러 개가 우리 연구가 채우거나 세미나에서 물을 수 있는 자리다.

| # | 공백 | 왜 문제인가 |
|---|---|---|
| G1 | **ball milling 조건이 하나도 없다.** `[인쇄, §2.2]` "homogeneously mixed via mechanical ball milling at a 75:25 mass ratio" 가 전부다. 밀 종류(planetary/shaker)·rpm·시간·볼 재질·BPR·건식/습식 어느 것도 없다. | 우리 [[composite-cathode-mixing-routes]] 의 핵심 변수가 바로 이것이다. Li2S 입자가 1–5 µm 로 남은 것(Fig. 2C)으로 보아 **저에너지 혼합**이었을 가능성이 크지만 확인 불가. 재현 불가. |
| G2 | **용량 정규화가 mAh g⁻¹(S)** 다 — Li2S 가 아니라 **황 질량 기준**. 축 라벨이 `mAh g(S)⁻¹` 이다 (Fig. 4, S1, S4, S11). | 우리 목표 500–600 mAh g⁻¹ 이 Li2S 기준이면 이 논문 수치는 **×0.698** 해서 읽어야 한다 (32.065/45.95). 예: 0.5 C 899.6 mAh g⁻¹(S) = **628 mAh g⁻¹(Li2S)**. 정리는 [[capacity-normalization-li2s-vs-sulfur]]. |
| G3 | **본문 수치 하나가 SI 표와 어긋난다.** `[인쇄, p.8]` "899.6 mAh g–1 (11.5 mAh cm–2)" 인데, `[재현]` 899.6 mAh g⁻¹(S) × 15 mg cm⁻² × 0.698 = **9.4 mAh cm⁻²** 이고 Table S1 도 0.5 C cycle capacity 를 **9.3 mAh cm⁻²** 로 적는다. 11.5 는 **0.1 C 첫 방전**의 면적용량이다 (Table S1 "Initial capacity 11.5"). | 괄호 안 값이 다른 조건의 값이다. 세미나에서 그대로 옮기면 틀린다. |
| G4 | **셀 개수·오차 막대가 없다.** Fig. 4D 만 두 셀(Gr/CNT (1),(2))을 겹쳤고 나머지는 단일 곡선. | 15 mg cm⁻² 펠릿 셀의 재현성이 0 이라 Fig. 4B 의 "Gr 이 50 사이클에 죽는다" 가 셀 하나의 사고인지 계통인지 모른다. |
| G5 | **첫 충전 컷오프 3.6 V vs Li/Li⁺, 충전 plateau 3.2 V 이상**. | 우리 황화물 ASSB 에서는 LPSCl 이 그 전위에서 산화 분해된다 (일반 지식 — 이 위키에 아직 근거 논문이 없다, [[li2s-assb-composite-cathode]] 의 미결 항목). 이 논문의 활성화 프로토콜은 **그대로 옮길 수 없다**. |
| G6 | **"direct conversion" 이 왜 이 전극에서 일어나는지의 원인 분리가 없다.** compact geometry 때문인지, 높은 LiNO3 때문인지, Gr 접촉 때문인지 대조 실험이 없다 (Li2S/Gr 대조군의 in situ Raman 은 없고 cryo-TEM 만 있다 — Fig. S6). | 논문은 "compact geometry + 잘 연결된 네트워크가 활성화한다" 고 쓰지만 LiPs 미형성의 **원인**은 추정이다. 세미나에서 물어볼 자리. |
| G7 | **orthorhombic (Pnma) Li2S 의 분율을 모른다.** TEM 몇 입자에서 SAED 로 확인했을 뿐 XRD 가 없다. 벌크 상전이 압력은 문헌상 12 GPa 인데 (ref 34) 성형 압력은 1 GPa. | "고압 준안정상이 활성화를 돕는다" 는 결론(§4)이 **몇 개 입자의 관찰**에 얹혀 있다. |
| G8 | **Li2S/CNT 대조군의 CNT 함량이 25 wt%** (Gr/CNT 를 CNT 로 통째 대체). 그 조건에서 CNT 가 micro-Li2S 를 활성화 못 한다는 것이지, CNT 일반의 성질이 아니다. | "1D 탄소는 활성화에 약하다" 는 문장은 **이 분산 조건·이 함량**에 한정된다. |
| G9 | **전해질/Li2S 12 µL mg⁻¹** 는 lean 이 아니다 (황 기준 ≈17 µL mg⁻¹(S)). lean 7 µL mg⁻¹ 은 SI 에서 **30 사이클만** (Fig. S11). | 800 사이클 full cell 은 풍부한 전해질 조건의 결과다. |
| G10 | **에너지밀도 1006.3 Wh kg⁻¹ 는 "양극 활물질+탄소" 질량만의 값**이다 (Table S2 분모 = Li2S/0.75). 집전체·바인더 없음(펠릿이라 바인더는 실제로 없다)·전해질·음극 제외. | 셀 수준 수치가 아니다. 세미나에서 "양극 재료 수준" 이라고 한정해 말해야 한다. |
| G11 | **파우치 50 사이클**뿐이고, 반쪽셀은 30 사이클 후 CE 요동 (Fig. 8B). | 파우치 결과는 "가능성 시연" 이지 수명 데이터가 아니다. |
| G12 | **XPS 귀속의 근거가 인용뿐**이다 (refs 19, 29, 36, 37). 깊이 프로파일 없음. sulfate/polythionate/thiosulfate 가 Gr 표면 passivation 의 정체라는 주장은 표면 몇 nm 의 관측이다. | Fig. 5 의 "CNT 가 passivation 을 억제한다" 는 SEM 형태 + XPS 상대 세기에서 온 **정성** 결론이다. |
| G13 | **압축 성형 1 GPa 5 min 의 기계적 후처리**(두께 166 µm 의 밀도·공극률)를 재지 않았다. | 우리 ASSB 펠릿도 유사 압력으로 성형한다. 공극률이 없으면 "compact geometry" 의 정도를 비교할 수 없다. |
| G14 | **Gr:CNT 최적(7:1)이 왜 최적인지** — 3.125 wt% 초과 시 활성화가 떨어지는 이유를 "Gr 의 접촉 면적을 CNT 가 대체해 버린다" 정도로만 설명. 분산 상태·CNT 뭉침의 관측 없음. | 우리 AB(acetylene black) 20 wt% 설계와 대조하려면 **탄소 종류별 접촉면적/네트워크 기여**를 분리해야 하는데 그 데이터가 없다. |

---

## 0. 서지사항 (직접 확인)

`[인쇄]` PDF 1쪽 + 메타데이터:

| 항목 | 값 |
|---|---|
| 제목 | Long-lasting, reinforced electrical networking in a high-loading Li2S cathode for high-performance lithium–sulfur batteries |
| 저자 | Hun Kim¹, Kyeong-Jun Min¹, Sangin Bang¹, Jang-Yeon Hwang², Jung Ho Kim³, Chong S. Yoon⁴, **Yang-Kook Sun¹˒³ (교신)** |
| 소속 | 1 한양대 에너지공학과 · 2 전남대 신소재공학과 · 3 Univ. of Wollongong ISEM/AIIM · 4 한양대 신소재공학과 |
| 학술지 | Carbon Energy **5** (2023) e308 (Wenzhou Univ. + Wiley) |
| DOI | 10.1002/cey2.308 |
| 접수/개정/게재 | Received 29 July 2022 · Revised 7 September 2022 · Accepted 30 September 2022 |
| 저작권 | © 2023 The Authors — **CC BY (open access)** |
| 키워드 | carbon nanotubes · electrical network · high energy · high loading · Li2S cathode · lithium–sulfur batteries |
| 지원 | KETEP 20214000000320 · Samsung Research Funding & Incubation Center SRFC-MA1901-06 |
| 이해충돌 | 없음 (선언) |

`[해석]` 이 논문은 같은 그룹의 **Hwang et al. 2019 ACS Energy Lett. 4, 2787
"Nano-compacted Li2S/graphene composite cathode"** (ref 28) 의 직접 후속이다. 그쪽이
Li2S/Gr 압축 양극과 direct conversion 을 처음 보였고, 이 논문은 거기에 **CNT 를 더해
수명**을 잡은 것이다. 세미나에서 "무엇이 새로운가" 를 물으면 답은 **CNT 의 역할 분리
+ 800 사이클 흑연 full cell + in situ/cryo 3종 동시 관측** 셋이다.

---

## 1. 한 문단 요약

`[해석]` 저자들은 상용 마이크로 Li2S(1–5 µm)를 **2D 그래핀 + 1D MWCNT 복합 탄소**와
75:25 로 ball milling 한 뒤 **1 GPa 로 압축 성형**해 바인더·집전체 없는 펠릿 양극을
만들었다 (Li2S 10–15 mg cm⁻², 두께 166 µm). 그래핀은 넓은 접촉 면적으로 절연체
Li2S 의 활성화를 맡고, 소량(양극 전체의 3.125 wt%)의 CNT 는 전극 두께 방향의
**장거리 전자 네트워크**를 만들어 사이클 중 그래핀 표면이 sulfate/polythionate 로
passivation 되어도 전도 경로를 유지한다. 그 결과 15 mg cm⁻² 반쪽셀이 0.5 C 에서
100 사이클(84.9 % 유지), 10 mg cm⁻² **흑연 음극 full cell 이 0.2 C 에서 800 사이클**
(5.3 → 약 2.3 mAh cm⁻²)을 돌았다. 첫 충전은 3.2 V 이상의 단조 증가 plateau 로 진행되며,
in situ Raman(LiPs 밴드 부재, 12 % SoC 부터 S8 출현)·in situ 광학현미경(노란 LiPs
없음)·cryo-TEM(50 % SoC 에서 Li2S 와 β-S8 공존)이 **Li2S → S8 직접 전환**을 세 갈래로
지지한다. 파우치 half/full 셀(10 mg cm⁻² 양면)도 50 사이클 시연했고, Li 금속 반쪽셀은
중심부 Li 고갈로 CE 가 요동해 **Li-free 음극의 필요성**을 강조하며 끝난다.

---

## 2. p.1–2 — Abstract / Introduction

### 2.1 Abstract 의 명제 `[인쇄]`
- 설계: "a high-loading Li2S-based cathode with **micrometric Li2S particles** composed of
  two-dimensional graphene (Gr) and one-dimensional carbon nanotubes (CNTs) in a
  **compact geometry**".
- CNT 의 역할: "CNTs embedded within the Gr sheets create **robust and sustainable
  electron diffusion pathways** while **suppressing the passivation** of the active carbon surface."
- 기전: "during the first charging process, the proposed cathode is fully activated through
  the **direct conversion of Li2S into S8 without inducing lithium polysulfide formation**."
- 관측 도구: in situ Raman + in situ optical microscopy + cryo-TEM.
- 성능: "even with a high Li2S loading of 10 mg cm–2; … Li–S full cell coupled with a
  graphite anode shows ultra-long-term cycling stability **over 800 cycles**."

### 2.2 Introduction 의 문제 설정 `[인쇄]`
- 황 이론용량 1675 mAh g⁻¹; 실용 Li–S 400–500 Wh kg⁻¹ 전망 (refs 3–5).
- **Li2S 계 Li–S 의 존재 이유**: "freedom of anode selection without being limited to the
  use of Li metal anode" — Li2S 가 양극에 Li 원천을 가지므로 graphite·Si·합금 음극 가능
  (refs 6–10). `[해석]` 이것이 우리 [[anode-free-li2s-assb]] 계획의 근거 문장과 정확히 같다.
- 고로딩의 문제: 전극이 두꺼워질수록 전자 이동이 지연; 특히 **절연체 Li2S 함량이 높고
  탄소가 적은** 고에너지 양극에서 균일 전자 전도가 관건 (refs 11, 12).
- Gr·CNT 의 **차원 특성과 역할 분리**가 덜 연구됐다는 진술 (ref 20 Kinloch et al. Science 2018).
- **Li2S 활성화**: 전기화학적으로 절연(~10⁻¹³ S cm⁻¹), 첫 탈리튬화에 높은 활성화 에너지
  (refs 21, 22); **"the initially activated Li2S dominantly determines the energy density and
  cycling capacity of Li2S-based Li–S batteries (Figure S1)"** (refs 7, 23–25).
- Direct conversion (LiPs 중간체 없이 Li2S → S8) 선행 보고 refs 26–28; LiPs 용출이 수명
  한계의 근원이므로 그 형성을 조절하는 것이 중요.
- 목표 세 가지: (i) 합리적 Gr/CNT 복합체, (ii) 그것으로 15 mg cm⁻² 까지 compact 양극을
  **단순 펠릿화**로 제작, (iii) 첫 충전의 독특한 활성화·직접 전환을 in situ + cryo-TEM 으로 규명.

`[해석]` **Fig. S1 이 이 논문에서 우리에게 가장 직접적인 그림이다** (아래 §9.1). "첫 충전에서
얼마나 활성화하느냐가 이후 방전 용량을 정한다" 는 관측은 전해질과 무관하게 우리
reference cell 의 첫 사이클 프로토콜 설계에 그대로 걸린다 — [[li2s-activation-first-charge]].

---

## 3. p.2–4 — §2 Experimental (재현에 필요한 전부)

### 3.1 Gr/CNT 복합체 (§2.1) `[인쇄]`
| 항목 | 값 |
|---|---|
| Gr | 1–5 atomic layer, ACROS |
| CNT | MWCNT 95 %, Nanolab; 평균 직경 ~15 nm (§3.1 본문) |
| 분산 | 각각 NMP(99.50 %, 대정)에 **초음파 30 min**, 다른 분산제 없음 |
| 혼합 | 두 분산액 합쳐 7:1 / 4:1 / 1:1 (질량) → **추가 초음파 30 min** |
| 회수 | 진공 여과 → 에탄올 세척 → 진공 60 °C 1일 이상 → **190 °C 하룻밤** |

`[해석]` 건식 혼합(Fig. S2)은 반데르발스 응집으로 뭉친다는 대조가 있다. 우리
[[composite-cathode-mixing-routes]] 의 "에탄올 용액 경로" 와 통하는 대목 — 탄소를 먼저
용매 분산으로 얽어 두고 활물질과 나중에 섞는 것은 **two-step** 의 한 형태다.

### 3.2 Compact Li2S/Gr/CNT 양극 (§2.2) `[인쇄]`
| 항목 | 값 |
|---|---|
| Li2S | 상용 99.98 %, Sigma-Aldrich; Ar 글로브박스(H2O·O2 < 0.1 ppm)에서 개봉 |
| 혼합 | Li2S : Gr/CNT = **75 : 25 (질량)**, "mechanical ball milling" — **조건 미기재 (G1)** |
| 성형 | 10 mm 펠릿 몰드, **1 GPa, 5 min** → Li2S 10 또는 15 mg cm⁻² (오차 < 0.1 mg cm⁻²) |
| 대조군 | Gr/CNT 자리에 Gr 또는 CNT 만 넣어 같은 ball milling (→ Li2S/Gr, Li2S/CNT) |
| 파우치용 | 30 × 50 mm 직사각 몰드, 10 mg cm⁻² |
| 환경 | 전 과정 Ar 글로브박스 |

`[해석]` **바인더가 없다.** 집전체도 펠릿 자체다(파우치에서만 Al 박에 탭). 이 점에서
우리 ASSB 복합양극(바인더 없이 SE·탄소·활물질을 압축)과 **형태적으로 같은 계열**이다.
차이는 25 wt% 자리를 우리는 SE 50 + C 20 으로 나눈다는 것 — Li2S 함량 75 vs 30.

### 3.3 흑연 음극·파우치 (§2.3–2.4) `[인쇄]`
- Graphite(POSCO Chem) : Super P : PAA(Mv ~450,000) = **92 : 1 : 7**, NMP 슬러리, Cu 박;
  60 °C 1일 → 110 °C 하룻밤. **N/P = 1.2 : 1**.
- 파우치: 양면 양극 30 × 50 mm, Li 금속(200 µm, Hohsen) 또는 흑연 31 × 51 mm, Celgard 2400
  34 × 54 mm, Al 박+Al 탭 / Cu 박+Ni 탭, **winding**, Al-라미네이트 포장. 전해질 비율은
  코인셀과 동일.

### 3.4 전기화학 조건 (§2.5) `[인쇄]`
| 셀 | 전해질 | 첫 사이클 | 이후 사이클 |
|---|---|---|---|
| 코인 반쪽셀, 15 mg cm⁻² | **0.5 M LiTFSI + 0.8 M LiNO3**, DME:DOL 1:1 (v/v) — 고 LiNO3 (refs 28, 29) | 1.9–3.6 V, 0.1 C | 1.8–2.8 V, **0.5 C** |
| 코인 full cell, 10 mg cm⁻² | **2.5 M LiTFSI + 0.4 M LiNO3**, DME:DOL 1:1 (ref 38, 흑연 호환 "Li-ion coordination structure-tailored") | 1.6–3.6 V, 0.1 C | 1.6–2.8 V, **0.2 C** |
| 파우치 반쪽셀, 10 mg cm⁻² × 2면 | 반쪽셀 전해질 | 1.9–3.6 V, 0.05 C | 1.8–2.8 V, 0.05 C |
| 파우치 full cell | full cell 전해질 | 1.6–3.6 V, 0.05 C | 1.6–2.8 V, 0.05 C |

- 1 C = **1675 mA g⁻¹(S)**. 전해질/Li2S = **12 µL mg⁻¹**. 30 °C, TOSCAT-3100.
  Li 금속 200 µm, 14 mm; 양극 10 mm; PP 분리막 19 mm; 2032 코인.
- CV: VMP3, 1.9–3.6 V, 0.3 mV s⁻¹.
- 2-probe 저항: 탄소만 펠릿(10 mm, 두께 0.5 mm), Keithley 2400, 1·2·3·4·5 mV 정전압 →
  평형 전류로 I–V (Fig. S3).

`[재현]` 전류밀도: 15 mg cm⁻² Li2S → 황 10.47 mg cm⁻² → 1 C = 17.5 mA cm⁻² (본문 17.6),
0.5 C = 8.8 mA cm⁻² (Table S1 과 일치). 10 mg cm⁻² full cell 0.2 C = 0.2 × 1675 × 6.98 mg
= 2.34 mA cm⁻² (Table S1 "2.3"). 일치.

### 3.5 분석 (§2.6) `[인쇄]`
SEM Verios G4UC · TEM JEOL NEO ARM + Gatan 613 cooling holder, **cryo 103.15 K** ·
XPS K-Alpha+ · in situ 셀 EL-CELL ECC-Opto-Std(창 달린 밀폐 셀) · Raman DXR3xi 532 nm ·
OM VHX-7000 · in situ 중 **1/5 C 로 3.6 V 까지 충전**. 시료는 Ar 용기로 이송.

---

## 4. p.4–6 — §3.1 Gr/CNT 복합체와 compact 양극의 구조

### 4.1 왜 CNT 인가 `[인쇄]`
- Gr 의 in-plane 전도도는 10⁷–10⁸ S m⁻¹ 로 높지만 **through-plane 은 불만족** (ref 20).
- 설계 의도: "CNT forms an electrical network throughout the electrode" — Gr 층 사이에
  CNT 를 **흩뿌려** 두 성분의 장점을 동시에 쓴다.
- 건식 혼합은 응집(Fig. S2). NMP 초음파 분산 후 혼합하면 "**1D CNTs (~15 nm) interconnect
  each Gr particle**" 하는 3D 네트워크 (Fig. 1B,C).

### 4.2 2-probe I–V (Fig. 1D)
- `[인쇄]` "~35 % higher currents were detected in the Gr/CNT electrode at each applied potential".
- `[도표, Fig. 1D]` 5 mV 에서 Gr ≈ 59 µA, Gr/CNT ≈ 80 µA; 둘 다 원점을 지나는 직선
  (옴 거동). `[재현]` 80/59 ≈ 1.36 → 본문의 ~35 % 와 일치.
- `[해석]` 이것은 **탄소만의 펠릿**(활물질 없음) 두께 방향 저항이다. Li2S 75 % 가 들어간
  실제 양극의 저항이 아니며, 절대 전도도도 적혀 있지 않다(기하는 있으니 계산은 가능:
  R = 5 mV/80 µA = 62.5 Ω, 두께 0.5 mm, 면적 0.785 cm² → ρ ≈ 98 Ω·cm, σ ≈ 0.01 S cm⁻¹
  — 접촉저항 포함이라 하한값이다. `[재현]`).

### 4.3 Compact 양극의 미세구조 (Fig. 2)
- `[인쇄]` 15 mg cm⁻² 펠릿 두께 **166 µm** (Fig. 2B). Li2S 입자 **1–5 µm** 가 Gr/CNT 매트릭스에
  둘러싸임 (Fig. 2C). TEM: Li2S 입자가 2D Gr 시트에 **완전히 캡슐화**되고 그 안에 CNT 가 얽힘.
- `[도표, Fig. 2B]` 단면이 균질한 입상 조직; 스케일바 100 µm 기준으로 두께가 대략 170 µm.
  Fig. 2C 에는 수 µm 크기의 매끈한 Li2S 덩어리가 보인다 — **나노화되지 않은 상용 입자**다.
- 상: [100] zone SAED → **cubic Fm3̄m** Li2S (Fig. 2E). 납작한 막대형 나노입자의 [001] zone →
  **orthorhombic Pnma** Li2S (Fig. 2F,G).
- `[인쇄]` 벌크 Li2S 는 12 GPa 이상에서 antifluorite → Pnma 로 전이하고 감압 시 되돌아온다
  (ref 34 Grzechnik 2000). 저자 추정: 1 GPa 성형 중 **국소 압축 응력**이 임계를 넘었고 Gr
  시트가 측방 팽창을 구속해 준안정상이 남았다 (refs 28, 34). Fig. 3 에 추가 사례.
- `[해석]` **G7**: 분율 미상. 그러나 이 관찰은 우리에게 흥미롭다 — 우리 ASSB 펠릿도
  수백 MPa 로 성형하고 high-energy ball milling 은 국소적으로 훨씬 큰 응력을 준다.
  우리 복합양극의 Li2S 에도 Pnma 흔적이 있는지(XRD 로) 보는 것은 값싼 확인이다.

### 4.4 Fig. 3 — Li2S 다형 (보조)
`[인쇄]` (A) cubic Fm3̄m, (B) orthorhombic Pnma 단위격자; (C,E,G) 명시야 TEM, (D,F,H) SAED —
D·H 는 Orthorhombic 001 zone (200·020 반사 표시), F 는 Cubic 110 zone.
`[도표]` C·G 의 막대형 특징이 500 nm 스케일바 기준 수백 nm 길이의 **얇은 판/막대**로 보인다.

---

## 5. p.6–8 — §3.2 전기화학 성능 (★ 세미나의 본체)

### 5.1 첫 사이클 (Fig. 4A; 15 mg cm⁻², 0.1 C, 1.9–3.6 V, Li 금속)
- `[인쇄]` Gr/CNT 가 세 양극 중 **가장 높은 첫 충전(활성화) 용량**. Li2S 75 %·탄소 25 %
  조건에서 탄소 종류의 역할이 드러난다. 2D Gr 은 벌크 Li2S 와 큰 접촉면적으로 전자 교환;
  **1D CNT(<20 nm)는 micro-Li2S 활성화에 잘 기능하지 않는다**. 그러나 **소량**의 CNT
  (Gr:CNT = 7:1, 양극 전체의 3.125 wt%)를 Gr 자리에 넣으면 3D 네트워크가 생겨 전기적
  고립부가 없어지고 활성화가 좋아진다. **3.125 % 를 넘기면 활성화가 오히려 떨어진다** (Fig. S4).
- `[인쇄]` 첫 충전 곡선이 통상의 Li2S 곡선과 다르다: 통상은 초기 고전압 후 **LiPs 가 redox
  mediator 로 작동하며 전압이 내려가는데**, 이 양극은 **3.2 V 이상에서 시작해 완만히 상승**
  하며 끝까지 유지 — direct conversion 의 서명 (refs 26–28).
- `[도표, Fig. 4A]` 충전: 세 곡선 모두 초기에 ~3.4–3.45 V 로 튄 뒤 3.15–3.2 V 로 내려와 서서히
  상승, 3.6 V 컷오프. 충전 용량 Gr/CNT ≈ 1450–1500, Gr ≈ 1380–1420, CNT ≈ 900–950 mAh g⁻¹(S).
  방전: Gr/CNT ≈ 1150 (=11.5 mAh cm⁻²), Gr ≈ 1080, CNT ≈ 620–650 mAh g⁻¹(S); 방전 plateau
  ~2.35 V 와 ~2.05 V 두 단 (CNT 는 아래 단이 ~2.0 V 로 더 낮다).
- `[재현]` Gr/CNT 첫 방전 11.5 mAh cm⁻² ÷ 10.47 mg cm⁻²(S) = 1098 mAh g⁻¹(S) — 축에서
  읽은 ~1150 과 5 % 안에서 일치. **Li2S 기준으로는 ≈ 770–800 mAh g⁻¹(Li2S)** (×0.698).
- `[해석]` **첫 충전 초기 스파이크(~3.4 V)는 있다** — "활성화 장벽" 자체가 사라진 것이
  아니라 **그 뒤에 전압이 내려가지 않는 것**이 특징이다. 우리 ASSB Li2S 도 첫 충전에 큰
  과전압을 보이므로, 세미나에서 "이 곡선 모양이 우리 셀과 어떻게 다른가" 를 대조 슬라이드로
  만들 수 있다 ([[kim2023-seminar-prep]]).

### 5.2 0.5 C 사이클 (Fig. 4B; 1.8–2.8 V)
- `[인쇄]` 방전 용량 Gr/CNT **899.6 mAh g⁻¹** ("(11.5 mAh cm⁻²)" — **G3: 이 괄호는 틀렸거나
  0.1 C 값**), Li2S/Gr 833.4, Li2S/CNT 205.6 mAh g⁻¹. Gr/CNT 는 100 사이클 동안 높은 CE 로
  안정; Li2S/Gr 은 **약 50 사이클 후 급락**하며 CE 도 떨어진다.
- `[도표, Fig. 4B]` Gr/CNT 면적용량 ≈ 9.4 → 7.9 mAh cm⁻² (100 사이클), CE ≈ 98–99 % 유지.
  Gr ≈ 8.7 → 7.3 mAh cm⁻² 로 완만히 줄다가 **~50 사이클에서 CE 가 100 → 75 % 로 붕괴**하고
  ~52 사이클에서 5.6 mAh cm⁻² 로 떨어지며 끝. CNT ≈ 2.0 mAh cm⁻² 로 24 사이클.
- Table S1 `[인쇄]`: 100 사이클, **84.9 % 유지**, cycle capacity 9.3 mAh cm⁻² at 8.8 mA cm⁻².
- `[재현]` 899.6 × 0.698 = **628 mAh g⁻¹(Li2S)**; 9.3 mAh cm⁻² ÷ 15 mg cm⁻² = 620 mAh g⁻¹(Li2S).

### 5.3 Gr/CNT 비 최적화 (Fig. S4; 15 mg cm⁻², 0.5 C, 30 사이클)
`[도표, Fig. S4]` 초기 → 30 사이클: **7:1 ≈ 905 → 820** · Gr only ≈ 835 → 735 · 4:1 ≈ 825 → 720 ·
1:1 ≈ 680 → 540 mAh g⁻¹(S). CE 는 네 조건 모두 ~98–99 %.
`[해석]` 7:1(3.125 wt%)만 Gr 단독보다 낫고 4:1 은 Gr 단독과 같으며 1:1 은 훨씬 나쁘다.
"CNT 는 적을수록 좋은 첨가제" 형태의 곡선이다. **우리 AB 20 wt% 설계에서 AB 의 일부를 CNT
로 대체할 때 3 wt% 수준의 소량이 출발점**이라는 힌트 — 단 액체 전해질에서의 값이다.

### 5.4 사이클 후 양극 (Fig. 5; §3.2)
- `[인쇄]` 셀 사망 후 Li2S/Gr: Gr 입자 표면에 **심한 passivation** (SEM, Fig. 5A). XPS S 2p:
  sulfate·polythionate·thiosulfate 종 + 잔류 polysulfide 관련 종이 지배 (Fig. 5C).
  같은 사이클 수의 Gr/CNT: passivation 덜함, sulfate/polythionate 적음, **CNT 는 형태 온존**,
  표면 대부분 침전물로 덮이지 않음 (Fig. 5B,D).
- `[도표, Fig. 5C]` Li2S/Gr: 170–171 eV(sulfate)·~169 eV(polythionate) 봉우리가 가장 크고
  ~168 eV thiosulfate, 낮은 결합에너지 쪽 S8/S_t⁻¹ 은 작다; **Li2S 피크 없음** ("No peak curve"
  표시). `[도표, Fig. 5D]` Gr/CNT: 산화황 종이 훨씬 작고 **~160.8 eV 에 Li2S 피크가 뚜렷**
  — 방전 상태의 활물질이 살아 있다.
- `[인쇄]` 해석: Gr 은 큰 접촉면적으로 전환 반응을 **주도**하고, CNT 는 전극 전체의 균일한
  고전도를 **유지**해 반응이 지속되게 한다.
- `[해석]` G12. 그리고 XPS 가 Li2S/Gr 에서 Li2S 피크를 못 본 것은 "활물질이 다 산화황으로
  갔다" 보다 "표면이 두꺼운 passivation 층으로 덮여 아래가 안 보인다" 로도 읽힌다 — 표면
  민감 기법의 한계.

### 5.5 흑연 full cell (Fig. 4D; 10 mg cm⁻², 0.2 C, 1.6–2.8 V, N/P 1.2)
- `[인쇄]` 5.3 mAh cm⁻² at 0.2 C, **800 사이클 이상**. 최초의 이 정도 고로딩 Li2S full cell 이라 주장.
- `[도표, Fig. 4D]` 두 셀 (1),(2) 이 거의 겹침. 초기 ≈ 5.0–5.3 mAh cm⁻² (≈ 720–760 mAh g⁻¹(S)) →
  100 사이클 ≈ 4.3 → 400 사이클 ≈ 3.6 → 800 사이클 ≈ 2.3–2.5 mAh cm⁻² (≈ 330–360 mAh g⁻¹(S)).
  CE ≈ 97–99 % 로 전 구간 평탄.
- Table S1 `[인쇄]`: 초기 6.4 mAh cm⁻² (0.1 C), cycle 5.3 (0.2 C), **800 사이클 43.0 % 유지
  (500 사이클 60.6 %)**.
- `[재현]` 5.3 mAh cm⁻² ÷ 10 mg cm⁻² = **530 mAh g⁻¹(Li2S)** = 760 mAh g⁻¹(S). 800 사이클 후
  ≈ 2.3 mAh cm⁻² → 230 mAh g⁻¹(Li2S).
- `[해석]` "800 사이클 안정" 은 **CE 가 안정**하다는 뜻이지 용량이 안정하다는 뜻이 아니다 —
  용량은 선형에 가깝게 절반 이하로 줄었다. 세미나에서 이 구분을 분명히 해야 한다.
  그래도 흑연 음극(N/P 1.2)으로 800 사이클 CE ~98 % 는 **Li 금속 없이 Li2S 양극이 Li 원천
  역할을 지속했다**는 증거이고, 우리 anode-free 로드맵의 실증 선례로 인용할 수 있다.

### 5.6 율속 (Fig. 4E; 15 mg cm⁻², 0.1 → 1.0 C)
- `[인쇄]` 1.0 C = 17.6 mA cm⁻² 에서 **6 mAh cm⁻² 이상**.
- `[도표, Fig. 4E]` Gr/CNT: 0.1 C ≈ 11.3 · 0.2 C ≈ 9.7 · 0.3 C ≈ 8.9 · 0.5 C ≈ 8.2 · 0.7 C ≈ 7.5 ·
  1.0 C ≈ 6.3 mAh cm⁻²; 0.1 C 복귀 ≈ 9.0 (30 사이클째). Gr 은 각 단에서 0.5–1 mAh cm⁻² 낮고
  CNT 는 1.0 C 에서 ≈ 1.2 mAh cm⁻² 로 붕괴. 인셋 CE 는 율속 전환 직후 90 % 아래로 잠깐 떨어짐.

### 5.7 문헌 비교 (Fig. 4F, Table S1) — 아래 §9.2 에 표 전문.
`[인쇄]` 비교 대상은 refs 6, 39, 40, 41. 이 논문은 반쪽셀 (8.8 mA cm⁻², ~9.3 mAh cm⁻², 100
사이클) 과 full cell (2.3 mA cm⁻², 5.3 mAh cm⁻², 800 사이클) 을 별로 찍었다.

### 5.8 저자가 정리한 세 가지 원인 `[인쇄, p.8]`
(1) compact geometry → Gr 과 활물질의 밀착, (2) CNT 네트워크 → 전극 전체의 균일 반응 유도·유지,
(3) full cell 에서 안정한 Li-free 음극 사용.

---

## 6. p.8–11 — §3.3 첫 충전의 직접 전환 (★ 기전)

### 6.1 In situ Raman (Fig. 6A,B)
- 셀: 양극 쪽 석영 창, Al 메시 아래 양극 (메시 구멍 360 × 900 µm), 1/5 C 로 3.6 V 까지.
- `[인쇄]` 충전 시작 시 **Li2S 밴드 373 cm⁻¹** (refs 42–44) → 충전 진행과 함께 약화.
  **S8 특성 피크 152·220·473 cm⁻¹ 가 SoC 12 % 부터 일찍 출현**. **폴리설파이드 밴드 398 cm⁻¹
  (S8ⁿ⁻ 의 S–S 신축) 과 453 cm⁻¹ (S4²⁻) 은 S8 형성 전에 관측되지 않았다.** 통상 경로
  (Li2S → LiPs → 말기에 S8) 와 달리 **S8 조기 출현 + LiPs 밴드 부재** = 직접 전환의 강한 증거.
- `[도표, Fig. 6B]` 컨투어에서 150·220·470 cm⁻¹ 부근 세 띠가 SoC ≈ 10–15 % 에서 켜져 100 %
  까지 강해진다; 373 cm⁻¹ 의 Li2S 신호는 SoC 0–10 % 에서만 희미하게 보인다. 옆 전압 곡선은
  3.2 V 부근에서 시작해 90 % 이후 급상승.
- `[해석]` 373 cm⁻¹ Li2S 신호가 처음부터 약하다 — Li2S 는 Raman 산란이 약하고 탄소 75 %
  에 덮여 있어서다. "Li2S 가 사라진다" 는 부분은 정성적이다. 반면 **LiPs 밴드의 부재**는
  같은 창·같은 셀에서 Fig. S8 로 양성 대조(노란 LiPs 환경의 Raman)를 두었으므로 더 믿을 만하다.

### 6.2 Cryo-TEM at 50 % SoC (Fig. 7 vs Fig. S6)
- `[인쇄]` Gr/CNT: <10 nm 나노입자 응집체 + 10–100 nm 입자 (Fig. 7A,C,E). **길쭉한
  orthorhombic Li2S 는 관측되지 않음** → 준안정상이 먼저 탈리튬화됐다는 해석. SAED:
  cubic Li2S (113)·(200) + **d = 4.5 Å 의 추가 링 → β-S8 (PDF 65-6467)** (Fig. 7B,D; Gr/CNT 링은
  Fig. S7 로 분리). "**S8 and Li2S coexist even at 50 % SoC**". β-S8 은 전자빔에 약해 103.15 K
  cryo 로 관찰 — "첫 동시 관찰" 주장.
- `[인쇄]` 대조 Li2S/Gr (Fig. S6): Gr 시트 안 Li2S 나노입자 응집체는 비슷하나 **200–500 nm 의
  큰 cubic Li2S 입자가 남아 있다** → CNT 네트워크가 전극 전체의 균일 반응을 유도한다는 방증.
- `[도표, Fig. 7E]` 41·17·12 nm, <10 nm 로 표시된 입자들; Fig. 7B 의 4.5 Å 링은 중심 가까운
  안쪽 링.

### 6.3 In situ 광학현미경 (Fig. 6C)
`[인쇄]` Line 1(저배율): 전 충전 구간에서 **노란 액체 LiPs 가 보이지 않음** (양성 대조 Fig. S8).
Line 2(고배율, 20 µm 스케일바): Li2S 입자가 점차 사라지고 **바로 옆에** 새 S 종(β-S8 로 추정)이
SoC ~10 % 부터 출현, 말기에는 S8 만 남음. Fig. S9(100 % SoC TEM): Li2S 나노입자 거의 소멸,
형태 불명의 황 화합물이 매트릭스 전체에.

### 6.4 종합 `[인쇄]` "a series of analyses provided consistent evidence of a direct conversion
reaction (from Li2S to S8)". `[해석]` 세 기법이 **같은 결론**을 내지만 **같은 원인**을 지목하지는
않는다 (G6). 우리 관점에서 중요한 것은 결론보다 **관측 설계**다 — 창 달린 셀 + 메시 구멍 +
Raman/OM 동시, cryo 로 β-S8 보존. ASSB 에서는 창 셀이 어렵지만 ex situ cryo-TEM/XRD 로
"활성화 중간에 무엇이 있는가" 를 묻는 틀은 같다.

---

## 7. p.11–12 — §3.4 파우치 셀

- `[인쇄]` 양면 양극 10 mg cm⁻²/면, 다층 winding. 반쪽셀 **6.7 mAh cm⁻²**, full cell **5.3 mAh cm⁻²**
  (0.05 C); 50 사이클 유지율 **86.4 % / 92.5 %**. 양극 에너지밀도 **1006.3 Wh kg⁻¹** (Table S2).
- `[도표, Fig. 8B]` 반쪽셀 ≈ 150 mAh (≈ 915 mAh g⁻¹(S)) → 50 사이클 ≈ 130 mAh; **30 사이클
  이후 CE 가 85–100 % 사이로 요동**. `[도표, Fig. 8C]` full cell ≈ 118 mAh (≈ 720 mAh g⁻¹(S)) →
  ≈ 108 mAh, CE ≈ 95 % 평탄.
- `[인쇄]` 반쪽셀의 Li 금속(Fig. S10): **중심부에서 불균일하게 고갈되어 Cu 노출**. LiPs 용출 →
  셔틀 → 두꺼운 passivation → 양 전극의 불균일 반응. 결론: **매우 안정한 Li-free 음극과 그것을
  쓸 수 있는 Li2S 계 전지가 필요하다.**
- `[해석]` 우리 anode-free 계획에 대한 **경고**로 읽는 것이 맞다: Li 원천이 양극에 있어도
  음극 쪽 Li 침적이 불균일하면 셀이 먼저 죽는다. anode-free 는 Li 금속 반쪽셀보다 이 문제가
  **더** 크다 (초기 Li 이 0 이라 여유가 없다).

---

## 8. p.12–13 — §4 Conclusion
`[인쇄]` 기여 요약: Gr 의 평면 형태(대면적 접촉 → 활성화) + CNT 네트워크(장기 균일 반응) +
compact geometry + **고압 성형으로 생긴 고변형 준안정 Li2S** + 직접 전환 — 이 넷이 활성화에
기여. **Lean 전해질 7 µL mg⁻¹ 에서도 0.2 C ~9.7 mAh cm⁻²** (Fig. S11). 파우치 시연.
"advantages of Li2S-based Li–S batteries, which can avoid issues related to safety hazards of Li
metal anodes, will effectively accelerate the practical use."

---

## 9. SI 전문 대조

### 9.1 Fig. S1 — 첫 충전 활성화 용량이 이후 용량을 정한다 (★)
- `[인쇄, 캡션]` (A) 첫 충전 곡선, (B) 첫 충전 용량을 (A) 의 25/50/75/100 % 로 제한한 네 셀의
  첫 충·방전, (C) 이후 사이클에서 **방전 용량이 첫 충전 용량에 비례해 증가**.
- `[도표, Fig. S1]` (A) 충전 ≈ 1450 mAh g⁻¹(S) 까지, 3.1–3.3 V 완만 상승 후 3.6 V.
  (B) 25/50/75/100 % 셀의 첫 방전 ≈ 300 / 570 / 820 / 1080 mAh g⁻¹(S).
  (C) 20 사이클 동안 ≈ 270 / 530 / 730 / 930 mAh g⁻¹(S) 로 **네 층이 그대로 유지**된다.
- `[해석]` **활성화되지 않은 Li2S 는 뒤 사이클에서 자발적으로 깨어나지 않는다** — 적어도 이
  전해질·이 전류에서 20 사이클 안에는. 우리 reference cell 이 500–600 mAh g⁻¹ 을 못 넘는다면
  첫 질문은 "첫 충전에서 얼마를 뽑았는가" 여야 한다. [[li2s-activation-first-charge]] 의 근거 1.
  단, 이 그림의 셀 조건(로딩·탄소)은 캡션에 없다 — 어느 양극인지 불명.

### 9.2 Table S1 — 선행 Li2S 계 Li–S 성능 비교 (전문 옮김) `[인쇄]`

| No. | 전략 | Li2S 로딩 (mg cm⁻²) | Li2S 함량 (%) | 초기 용량 (mAh cm⁻²) @ 전류 (mA cm⁻², C) | 사이클 용량 (mAh cm⁻²) @ 전류 | 사이클 수 | 유지율 (%) | 음극 | Ref |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **This work** | 15 | 75 | 11.5 @ 1.7 (0.1C) | 9.3 @ 8.8 (0.5C) | 100 | 84.9 | Li | — |
| 1 | This work (full) | 10 | 75 | 6.4 @ 1.1 (0.1C) | 5.3 @ 2.3 (0.2C) | 800 (500) | 43.0 (60.6) | Graphite | — |
| 2 | Li2S@graphene cathode | 10 | 72 | 8.0 @ 1.6 (0.1C) | 8.0 @ 1.6 (0.1C) | 200 | 51.7 | Li | S1 (6) Tan 2017 Nat. Energy |
| 2 | 〃 | 2 | — | 1.0 @ 1.6 (0.1C) | 1.0 @ 1.6 (0.1C) | 200 | 58.9 | Graphite | 〃 |
| 3 | Substituted polysulfide additives | 4 | 65 | 3.9 @ 0.2 (0.05C) | 3.4 @ 1.1 (0.2C) | 100 | 70.9 | Li | S2 (39) Nanda 2021 EES |
| 4 | Holey-Li2S nanoarchitectures | 2.1 | 48 | 1.4 @ 1.2 (0.1C) | 1.5 @ 2.4 (0.2C) | 100 | 81.9 | Graphite | S3 (40) Ye 2018 Adv. Sci. |
| 5 | Sparingly solvating electrolyte | 3.65 | 60 | 3.1 @ 0.3 (1/12C) | 2.1 @ 0.4 (1/8C) | 300 | 65 | Graphite | S4 (41) Seita 2020 ACS EL |
| 6 | In situ polysulfide injection | 3 | 70 | 2.1 @ 0.1 (0.05C) | 1.2 @ 0.2 (0.1C) | 200 | 80.4 | Li | S5 Li 2021 JACS |
| 7 | Mo/Li2S-based cathode | 2.5 | 40 | 2.2 @ 1.4 (0.5C) | 2.2 @ 1.4 (0.1C) | 150 | 53.3 | Li | S6 Balach 2017 ESM |
| 7 | 〃 | — | — | 1.9 @ 0.6 | 1.9 @ 0.6 | 150 | 52 | Si-Carbon | 〃 |
| 8 | h-CoN@MCNF/Li2S + gel polymer electrolyte | 2.5 | 65 | 2.7 @ 0.2 (0.1C) | 2.2 @ 0.5 (0.2C) | 200 | 90 | Li | S7 Meng 2021 EES |
| 8 | 〃 | — | — | 1.7 @ 0.5 (0.2C) | 1.7 @ 0.5 (0.2C) | 100 | 68.5 | Si-CNT | 〃 |
| 9 | Sulfone-assisted-NH4I additive | 2.5 | 42 | 2.9 @ 0.1 (0.05C) | 1.5 @ 1.4 (0.5C) | 400 | 67.5 | Li | S8 (24) Shi 2020 CEJ |

(원 표의 빈 칸은 "—". S1 표의 2·7·8 행은 한 참고문헌이 두 음극 조건을 갖는다.)

`[해석]` 이 표는 **전부 액체 전해질**이다. 우리 ASSB 문헌 비교표는 따로 만들어야 하고
([[li2s-assb-reference-cell]] 의 다음 ingest 대상), 그때 이 표의 **열 설계**(로딩·함량·면적용량
@전류·유지율·음극)는 그대로 재사용할 가치가 있다 — webapp `/compare` 의 열이 이 표에서 왔다.

### 9.3 Table S2 — 에너지밀도 계산 `[인쇄]`
비용량 915.6 mAh g⁻¹(S) · 로딩 10 mg cm⁻²(Li2S) · 면적 15 cm² · 전압 2.1 V · Li2S 함량 75 % ·
M(Li2S) 45.95 · M(S) 32.065 →
`(915.6 × 32.065/45.95 × 10 mg cm⁻² × 15 cm² × 2.1 V) / (10 mg cm⁻² / 0.75 × 15 cm²)` = **1006.3 Wh kg⁻¹**.
`[재현]` 분자 = 915.6 × 0.6978 × 0.15 g × 2.1 = 201.3 mWh; 분모 = 0.2 g → 1006 Wh kg⁻¹. 일치.
분모는 **Li2S + 탄소** 만이다 (G10).

### 9.4 Fig. S4 — CNT 함량 (§5.3 에 수치), Fig. S5 — CV
`[인쇄, 캡션]` CV 첫 사이클, 15 mg cm⁻², 1.9–3.6 V, 세 양극; 본문은 "Fig. 4A 와 잘 맞고 Gr/CNT
가 더 좋은 활성" 이라고만 쓴다. (S5 는 이 세션에서 **보지 않았다** — §13.)

### 9.5 Fig. S11 — Lean 전해질 7 µL mg⁻¹
`[도표, Fig. S11]` (A) 0.1 C 첫 사이클: 충전 ≈ 1420 mAh g⁻¹(S), 방전 ≈ 1010 mAh g⁻¹(S) ≈ 10.6 mAh cm⁻²;
(B) 0.2 C 30 사이클 ≈ 9.5–9.7 mAh cm⁻² 로 평탄, CE 첫 사이클 68 % 후 96–100 %.
`[해석]` lean 에서도 활성화는 됐다. 다만 **30 사이클**이다 (G9).

---

## 10. 우리 연구와의 접점 (요약 표)

| 이 논문 | 우리 ([[li2s-assb-reference-cell]]) | 옮겨 올 수 있는 것 | 옮겨 올 수 없는 것 |
|---|---|---|---|
| Li2S : C = 75 : 25, 바인더 없음, 1 GPa 펠릿 | Li2S : LPSCl : AB = 30 : 50 : 20, 펠릿 | **압축 성형 계열의 전자 접촉 논리**, 바인더 프리 | Li2S 함량 (SE 가 50 % 를 차지) |
| 2D Gr(접촉) + 1D CNT(네트워크) 역할 분리 | AB 단일 탄소 | **탄소 차원 분리 설계** — 접촉용 vs 네트워크용 ([[carbon-dimensionality-electron-network]]) | 액체에서의 passivation 화학 (sulfate 등) |
| CNT 3 wt% 소량 최적, 과량은 해 | 탄소 20 wt% | "네트워크용 탄소는 소량" 가설 | 최적값 자체 |
| micro Li2S 1–5 µm 그대로 활성화 | ball milling 으로 나노화 시도 | 활성화가 **접촉·네트워크로도** 되는 사례 | LiNO3·에테르·3.6 V 컷오프 (G5) |
| 첫 충전 활성화량이 이후 용량을 정함 (Fig. S1) | 500–600 mAh g⁻¹ 목표 | **첫 사이클 프로토콜을 변수로 다룰 것** ([[li2s-activation-first-charge]]) | — |
| 직접 전환 Li2S → S8 (LiPs 없음) | 고체라 원래 LiPs 용출 없음 | 고체상 전환의 관측 틀 (S8 조기 출현?) | 창 셀 in situ Raman/OM 그대로 |
| 흑연 full cell 800 사이클, N/P 1.2 | Li-In → anode-free 계획 | Li-free 음극 실증 선례; Li 금속 반쪽셀의 불균일 고갈 경고 | 액체 전해질 SEI 화학 |
| mAh g⁻¹(S) 정규화 | 목표 단위 불명확 | **단위 명시 규율** ([[capacity-normalization-li2s-vs-sulfur]]) | — |

---

## 11. 비판 (이 digest 의 판단)

1. **"800 사이클 안정" 은 CE 의 안정이다.** 용량은 5.3 → ~2.3 mAh cm⁻² 로 절반 이하 (Table S1
   43 %). 초록의 "ultra-long-term cycling stability" 는 CE 기준으로 읽어야 한다.
2. **원인 분리가 없다** (G6). direct conversion 이 compact geometry 의 결과인지 고 LiNO3 전해질
   (0.8 M)의 결과인지 — ref 28 과 같은 전해질을 썼으므로 그 그룹의 조건 안에서만 성립할 수 있다.
3. **본문 수치 오기** (G3): 899.6 mAh g⁻¹ 옆의 11.5 mAh cm⁻² 는 0.1 C 값. SI 표가 정본.
4. **재현성 0** (G4): 단일 셀 곡선. Li2S/Gr 의 50 사이클 급사가 셀 사고일 가능성을 배제 못 한다.
5. **ball milling 미기재** (G1): 이 논문의 "simple pelletization" 이 단순하려면 앞 단계가
   재현돼야 하는데 그 단계가 없다.
6. **에너지밀도의 분모** (G10): 1006 Wh kg⁻¹ 는 재료 수준. 셀 수준으로 환산하면 전해질
   12 µL mg⁻¹ 만으로도 크게 깎인다.
7. 좋은 점도 분명하다: **세 관측(Raman·OM·cryo-TEM)이 독립적으로 같은 방향**이고, 양성 대조
   (Fig. S8)와 음성 대조(Fig. S6, S7)를 두었으며, 파우치까지 갔다. 탄소 **역할 분리**의 논증
   (Fig. 1D → Fig. 4A/B → Fig. 5)은 세미나에서 그대로 쓸 수 있을 만큼 깔끔하다.

---

## 12. 이 저장소가 가져갈 것

- **개념 2개 신설**: [[li2s-activation-first-charge]] (Fig. S1 + 3.2 V plateau + 활성화 결정 요인),
  [[carbon-dimensionality-electron-network]] (2D 접촉 vs 1D 네트워크, 소량 최적, passivation 억제).
- **정규화 규율**: [[capacity-normalization-li2s-vs-sulfur]] — 이 논문 수치를 Li2S 기준으로
  환산한 표를 거기 둔다.
- **질문 카드에 근거 라우팅**: [[reference-cell-500-600-mahg]] (Evidence: 첫 충전 활성화량이
  용량 상한을 정한다; 접촉 탄소 + 네트워크 탄소 분리) · [[one-step-vs-two-step-mixing]]
  (Evidence: 탄소 매트릭스를 먼저 만들고 Li2S 를 뒤에 섞은 two-step 계열의 성공 사례 —
  단 조건 미기재).
- **세미나 자료**: [[kim2023-seminar-prep]].

---

## 13. 그림 판독 기록 (무엇을 보고 무엇을 안 봤는가)

| 그림 | 봤는가 | 어디에 썼는가 |
|---|---|---|
| Fig. 1 (A–D) | ✓ | §4.1–4.2 (I–V 값은 도표 판독) |
| Fig. 2 (A–G) | ✓ | §4.3 |
| Fig. 3 (A–H) | ✓ | §4.4 |
| Fig. 4 (A–F) | ✓ | §5 전체 — 가장 오래 봤다 |
| Fig. 5 (A–D) | ✓ | §5.4 |
| Fig. 6 (A–C) | ✓ | §6.1, 6.3 |
| Fig. 7 (A–E) | ✓ | §6.2 |
| Fig. 8 (A–C) | ✓ | §7 |
| Fig. S1 | ✓ | §9.1 (★) |
| Fig. S4 | ✓ | §5.3 |
| Fig. S11 | ✓ | §9.5 |
| Fig. S2, S3, S5, S6, S7, S8, S9, S10 | **✗ 캡션과 본문 서술만** | 크로핑은 돼 있다 (`fig_S*.png`). 세미나 준비 시 S6(대조 TEM)·S10(Li 고갈 사진)은 직접 볼 것을 권한다. |

본문 서술과 어긋난 그림: **없음**. 본문 안에서 서로 어긋난 수치: G3 하나.
