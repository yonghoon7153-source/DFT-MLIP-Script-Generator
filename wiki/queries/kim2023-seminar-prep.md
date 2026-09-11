---
title: Kim 2023 (Carbon Energy) 논문 세미나 준비
description: "Li2S/Gr/CNT compact 양극 논문을 ASSB Li2S 연구실 세미나에서 발표하기 위한 한 줄 메시지·5막 스토리라인·16장 슬라이드 설계·양단위 숫자표·비판·예상 질문 10·발표 체크리스트"
created: 2026-09-11
updated: 2026-09-11
type: query
tags: [seminar, li2s, carbon, activation, liquid-electrolyte]
sources: [raw/papers/kim2023_reinforced-electrical-networking-high-loading-li2s-cathode.md, raw/transcripts/2026-09-11-li2s-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: interpretive
evidenceScope: single-source
---

# Kim 2023 (Carbon Energy) 논문 세미나 준비

근거는 전부 digest `raw/papers/kim2023_reinforced-electrical-networking-high-loading-li2s-cathode.md`
(이하 "digest §n"). 그림 파일은 `raw/figures/kim2023_…/fig_N.png`, SI 는 `fig_S<n>.png`.
절차는 [[seminar-prep-from-digest]] 를 따랐다.

## 0. 한 줄 메시지

> **"절연체 Li2S 를 살리는 탄소의 일은 둘이다 — 넓게 닿는 것과 끝까지 잇는 것 — 그리고 그 둘을
> 차원이 다른 탄소에 나눠 맡기자 15 mg cm⁻² 고로딩에서도 첫 충전 활성화와 800 사이클 수명이
> 같이 왔다."**

부제(우리 관점): 액체계 논문이지만, **탄소 설계·압축 성형·첫 충전 활성화량이 수명 용량을
정한다는 관측** 세 가지는 우리 ASSB reference cell 에 그대로 걸린다.

## 1. 청중 가정과 시간

- 청중: ASSB Li–S 를 하는 연구실 구성원. Li2S 활성화 문제는 알지만 액체계 in situ 기법은 낯설 수 있다.
- 시간: 발표 20–25 분 + 질의 10 분 기준으로 16 장. 15 분이면 §3 의 ★ 표시 슬라이드만.
- 같은 학교(한양대 선양국 그룹) 논문이라는 점은 도입에서 한 줄만.

## 2. 스토리라인 (5막)

| 막 | 질문 | 답 (슬라이드) |
|---|---|---|
| I 문제 | 왜 Li2S 이고, 고로딩에서 무엇이 막히나 | 2–4 |
| II 설계 | 탄소 두 종류를 왜 어떻게 섞었나 | 5–7 |
| III 증거·성능 | 활성화·수명·율속·full cell | 8–10 |
| IV 증거·기전 | 왜 오래 가나(passivation), 첫 충전에서 무슨 일이 | 11–13 |
| V 한계·우리 | 못 믿을 것, 우리가 가져갈 것 | 14–16 |

## 3. 슬라이드 설계

| # | 제목 | 그림 | 말할 것 (3) | 노트 | 분 |
|---|---|---|---|---|---|
| 1 | 표지 | — | 서지: Carbon Energy 5 (2023) e308 · 한양대 선양국 그룹 · CC BY | 한 줄 메시지를 미리 말하지 않는다 | 0.5 |
| 2 ★ | 왜 Li2S 인가 | (텍스트) | ① 양극에 Li 원천 → Li-free 음극(흑연·Si·**anode-free**) 가능 ② S 이론 1675 mAh g⁻¹(S) = Li2S 1166 mAh g⁻¹(Li2S) ③ 대가: 절연체(~10⁻¹³ S cm⁻¹)의 첫 충전 활성화 | digest §2.2; 단위 두 개를 **여기서** 못 박는다 ([[capacity-normalization-li2s-vs-sulfur]]) | 1.5 |
| 3 ★ | 첫 충전에서 살린 만큼만 쓴다 | **fig_S1.png** (B,C) | ① 첫 충전을 25/50/75/100 % 로 끊음 ② 이후 방전 ≈ 270/530/730/930 mAh g⁻¹(S) 층이 20 사이클 유지 ③ 활성화 안 된 Li2S 는 안 깨어난다 | `[도표]` 값임을 말한다. 우리 [[li2s-activation-first-charge]] 의 근거 1 | 1.5 |
| 4 | 고로딩의 문제 | (도식 — 두꺼운 전극, 전자 경로) | ① 두꺼워질수록 전자 이동 지연 ② Li2S 75 %·탄소 25 % 에서 탄소 종류가 드러남 ③ Gr 은 in-plane 10⁷–10⁸ S m⁻¹ 이지만 through-plane 약함 | digest §2.2, §4.1 | 1 |
| 5 ★ | 설계: 2D 접촉 + 1D 네트워크 | **fig_1.png** (A,C) + fig_4.png 패널 C | ① Gr = 넓은 접촉면 ② CNT(~15 nm) = 두께 방향 고속도로 ③ NMP 초음파 분산 후 혼합 (건식은 응집, S2) | 패널 C 의 세 원(CNT-only / Gr-only / Gr+CNT)이 논문 전체의 논리 그림이다 | 2 |
| 6 | 탄소만으로 먼저 증명 | fig_1.png (D) + fig_S3 | ① 활물질 없는 탄소 펠릿 두께 방향 I–V ② Gr/CNT 가 ~35 % 높은 전류 ③ 옴 거동, 5 mV 에서 59 → 80 µA `[도표]` | 절대 전도도는 안 준다 — 접촉저항 포함 하한 (digest §4.2) | 1 |
| 7 | Compact 양극 만들기 | **fig_2.png** (A,B,C) + fig_3 (한 패널) | ① Li2S(1–5 µm 상용) + Gr/CNT 75:25 **ball milling(조건 미기재)** → 1 GPa 5 min 펠릿, 바인더·집전체 없음 ② 15 mg cm⁻² 에서 166 µm ③ 고압으로 준안정 orthorhombic Li2S 일부 (Pnma, 벌크는 12 GPa) | **우리와 형태적으로 같은 계열** (압축 펠릿). 분율 미상(G7) | 2 |
| 8 ★ | 첫 사이클 — 활성화 | **fig_4.png** (A) | ① Gr/CNT > Gr ≫ CNT-only (방전 ≈ 1150/1080/630 mAh g⁻¹(S) `[도표]`; 11.5 mAh cm⁻² `[인쇄]`) ② 충전이 3.2 V 에서 **내려가지 않고** 상승 — LiPs 매개 없음 ③ CNT 는 3.125 wt%(7:1) 소량이 최적, 과량은 해 (S4) | 스파이크 ~3.4 V 는 있다 — "장벽이 없다" 가 아니라 "그 뒤가 다르다" | 2 |
| 9 ★ | 수명·율속 | fig_4.png (B,E) | ① 0.5 C 100 사이클: Gr/CNT 899.6 mAh g⁻¹(S)=**628 (Li2S)**, 84.9 % 유지; Gr-only 는 ~50 사이클 급사 ② 1 C(17.6 mA cm⁻²)에서 >6 mAh cm⁻² ③ **본문의 "(11.5 mAh cm⁻²)" 는 0.1 C 값 — 0.5 C 는 9.3** | G3 정정을 발표에서 스스로 말한다 | 1.5 |
| 10 ★ | 흑연 full cell 800 사이클 | fig_4.png (D,F) | ① 10 mg cm⁻², N/P 1.2, 0.2 C: 5.3 mAh cm⁻² (=530 mAh g⁻¹(Li2S)) ② 800 사이클 후 ≈ 2.3 mAh cm⁻² — **CE 는 안정, 용량은 43 %** ③ 문헌 대비 위치 (F) | "ultra-long-term stability" 를 CE 로 읽어 준다. 우리 [[anode-free-li2s-assb]] 의 선례 | 1.5 |
| 11 | 왜 Gr-only 는 죽고 Gr/CNT 는 사나 | **fig_5.png** | ① Gr 표면 passivation(sulfate·polythionate·thiosulfate, XPS) ② Gr/CNT: CNT 형태 온존, Li2S 피크 잔존 ③ 분업: Gr 이 반응을 **주도**, CNT 가 전도를 **유지** | 표면 기법의 한계(G12) 한 줄 | 1.5 |
| 12 ★ | 첫 충전에서 무슨 일이 — in situ | **fig_6.png** (A,B,C) | ① 창 달린 셀 + Al 메시 구멍(360×900 µm) ② Raman: S8(152·220·473) 이 12 % SoC 부터, LiPs(398·453) 없음 ③ OM: 노란 LiPs 없음, S8 이 Li2S 옆에 ~10 % 부터 | 양성 대조 S8 그림이 있다는 점을 말한다 | 2 |
| 13 | cryo-TEM 50 % SoC | **fig_7.png** + fig_S6 (대조) | ① <10–100 nm Li2S + β-S8 링(4.5 Å) 공존 ② Gr-only 대조는 200–500 nm 큰 Li2S 잔존 → 네트워크가 균일 반응 ③ "첫 동시 관찰" 주장 | Li2S → S8 직접 전환이 **고체계에서는 기본 경로**라는 점으로 넘어간다 | 1.5 |
| 14 | 파우치와 음극의 교훈 | fig_8.png (B,C) + fig_S10 | ① 양면 10 mg cm⁻², 6.7/5.3 mAh cm⁻², 50 사이클 86.4/92.5 % ② Li 금속 반쪽셀은 30 사이클 후 CE 요동 — 중심부 Li 고갈 ③ 1006 Wh kg⁻¹ 는 **양극 재료 기준** | G10, G11 | 1 |
| 15 ★ | 비판 | (텍스트) | ① "800 사이클 안정" = CE (용량 43 %) ② 원인 분리 없음 — compact 인가 LiNO3 0.8 M 인가 ③ 셀 개수·오차 없음, BM 조건 없음, 본문 오기 하나 | digest §11 | 1.5 |
| 16 ★ | 우리에게 | (표) | 옮길 것: 탄소 차원 분리 → AB 일부를 CNT 로 · 압축 성형 논리 · **첫 충전량 vs 이후 용량 진단(Fig. S1 재현)** / 못 옮길 것: 에테르·LiNO3·3.6 V 컷오프 · Li2S 75 % (우리는 SE 50 %) | [[reference-cell-500-600-mahg]] 의 H1·H2 가 이 슬라이드에서 나온다 | 2 |

## 4. 핵심 숫자표 (양단위)

| 항목 | 값 | 단위 주의 |
|---|---|---|
| 조성 | Li2S : Gr/CNT = 75 : 25 wt, Gr:CNT = 7:1 (CNT 3.125 wt% of cathode) | — |
| 로딩·두께 | 15 mg cm⁻²(Li2S) → 166 µm; 10 mg cm⁻² (full·파우치) | 로딩은 Li2S 질량 |
| 성형 | 1 GPa, 5 min, 10 mm | — |
| 첫 방전 (0.1 C) | 11.5 mAh cm⁻² · ≈ 1150 mAh g⁻¹(S) · ≈ 800 mAh g⁻¹(Li2S) | (S)·(Li2S) 둘 다 말한다 |
| 0.5 C 사이클 | 899.6 (S) = 628 (Li2S); 9.3 mAh cm⁻²; 100 cyc 84.9 % | 본문 괄호 11.5 는 오기 |
| Full cell 0.2 C | 5.3 mAh cm⁻² = 530 (Li2S) = ≈ 760 (S); 800 cyc 43 %, 500 cyc 60.6 % | CE ≈ 98 % |
| 율속 1 C | 17.6 mA cm⁻², > 6 mAh cm⁻² | — |
| 전해질 | 반쪽 0.5 M LiTFSI + 0.8 M LiNO3; full 2.5 M LiTFSI + 0.4 M LiNO3; DME:DOL 1:1; 12 µL mg⁻¹(Li2S) | lean 7 µL mg⁻¹ 은 30 cyc 만 |
| Raman | Li2S 373; S8 152·220·473; LiPs 398·453 (부재) cm⁻¹ | — |
| 에너지밀도 | 1006.3 Wh kg⁻¹ — 분모 = Li2S + 탄소 | 셀 수준 아님 |

## 5. 비판적 읽기 포인트 (발표에 넣을 3 + 예비 3)

1. "안정" 의 정의 — CE 인가 용량인가 (§5.5).
2. direct conversion 의 원인 분리 부재 — 같은 그룹 ref 28 과 같은 고 LiNO3 전해질 (G6).
3. 재현성 — 단일 셀 곡선, BM 조건 미기재 (G1, G4).
- 예비: 준안정 Pnma Li2S 의 분율 미상(G7) · CNT-only 대조군의 25 wt% 조건(G8) · 에너지밀도 분모(G10).

## 6. 우리 연구 연결 (슬라이드 16 의 본문)

| 이 논문 | 우리 | 판단 |
|---|---|---|
| 접촉 탄소 + 네트워크 탄소 분리 | AB 단일 20 wt% | **가져온다** — AB 일부를 소량 CNT 로 ([[carbon-dimensionality-electron-network]]) |
| 1 GPa 압축, 바인더 없음 | 펠릿 압축 | 같은 계열 — 우리 압력·공극률을 적어 비교 |
| Fig. S1: 첫 충전량이 이후 용량을 정함 | 500–600 목표 | **가장 먼저 재현할 진단** ([[li2s-activation-first-charge]]) |
| 3.6 V 컷오프, LiNO3, 에테르 | 황화물 SE, Li–In | 못 가져온다 — 전압창 다름 ([[li2s-assb-composite-cathode]]) |
| 흑연 full cell N/P 1.2 | anode-free 계획 | 선례이자 경고 (Li 고갈 불균일) |
| mAh g⁻¹(S) 표기 | 목표 단위 미확인 | 발표 전에 우리 목표의 단위를 확정한다 |

## 7. 예상 질문 10 과 답

1. **Q. 직접 전환이 정말 LiPs 없이 일어났다는 증거가 충분한가?** — Raman 에서 LiPs 밴드 부재 +
   OM 에서 노란 용액 부재 + cryo-TEM 에서 50 % SoC 에 S8 공존, 세 기법 일치 (digest §6). 단
   Raman 의 Li2S 신호 자체가 약하고, **원인**(compact vs LiNO3) 은 분리되지 않았다 (G6).
2. **Q. 왜 CNT 를 많이 넣으면 나빠지나?** — 저자 설명은 접촉면적을 가진 Gr 을 CNT 가 대체해서.
   분산·응집 관측은 없다 (G14). Fig. S4 수치는 `[도표]`.
3. **Q. 800 사이클 동안 용량은?** — 5.3 → ≈ 2.3 mAh cm⁻² (43 %). 안정한 것은 CE (§5.5).
4. **Q. 이 결과가 고체전해질에도 적용되나?** — 전해질·전압창은 아니다. 적용되는 것은 탄소
   역할 분리·압축 성형·활성화량 논리 (§10 표). 고체계에서는 탄소가 SE 이온 경로를 막지 않아야
   하는 조건이 추가된다.
5. **Q. ball milling 조건은?** — 논문에 없다 (G1). 입자가 1–5 µm 로 남은 것으로 보아 저에너지 추정.
6. **Q. orthorhombic Li2S 가 활성화를 돕는다는 근거는?** — 50 % SoC 에서 길쭉한 입자가 사라졌다는
   TEM 관찰 (§6.2). 분율·XRD 없음 (G7). 우리 펠릿도 XRD 로 볼 가치가 있다.
7. **Q. 1006 Wh kg⁻¹ 는 어떤 기준?** — Li2S + 탄소 질량, 2.1 V, Table S2 (§9.3). 셀 수준 아님.
8. **Q. Li 금속 반쪽셀 파우치의 CE 요동 원인?** — 중심부 Li 고갈·Cu 노출 (Fig. S10), LiPs 셔틀 →
   passivation. 그래서 Li-free 음극 주장 (§7).
9. **Q. lean 전해질에서는?** — 7 µL mg⁻¹ 에서 0.2 C ~9.7 mAh cm⁻², 30 사이클만 (Fig. S11, G9).
10. **Q. 우리가 당장 할 실험 하나는?** — 우리 셀에서 Fig. S1 재현: 첫 충전을 25/50/75/100 % 로
    끊고 이후 방전이 층으로 남는지 본다. 남으면 활성화 제한(H1), 따라 올라오면 동역학(H2/H3)
    ([[reference-cell-500-600-mahg]]).

## 8. 발표 체크리스트

- [ ] 모든 비용량에 (S)/(Li2S) 표시, 면적용량에 로딩 표시
- [ ] "899.6 mAh g⁻¹ (11.5 mAh cm⁻²)" 인용하지 않기 — 0.5 C 는 9.3
- [ ] "800 사이클 안정" 을 CE 로 한정
- [ ] `[도표]` 값은 "그림에서 읽은 근사값" 이라고 말하기
- [ ] 셀 개수(단일 곡선)·BM 조건 미기재 언급
- [ ] 슬라이드 16 의 "못 가져올 것" 을 빼먹지 않기 (전압창)
- [ ] 발표 후 받은 질문을 아래 Status 에 append

## Status
- [2026-09-11] 초안. 발표 후 실제 질문을 추가한다.
