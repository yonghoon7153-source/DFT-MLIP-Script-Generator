---
title: 복합양극 혼합 경로 비교 — one-step · two-step · 탄화 · 용액
description: "Li2S–LPSCl–C 복합양극을 만드는 네 경로(+Kim 2023 의 액체계 선례)를 무엇을 제어하고 무엇을 위험에 빠뜨리는가로 비교"
created: 2026-09-11
updated: 2026-09-11
type: comparison
tags: [mixing-process, composite-cathode, li2s, sulfide-electrolyte]
sources: [raw/transcripts/2026-09-11-li2s-wiki-kickoff-session.md, raw/papers/kim2023_reinforced-electrical-networking-high-loading-li2s-cathode.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: mixed
evidenceScope: user-original
---

# 복합양극 혼합 경로 비교

## 비교 이유

[[li2s-assb-composite-cathode]] 의 세 네트워크(e⁻·Li⁺·활물질)는 **혼합 순서와 에너지**가
만든다. 사용자가 고려 중인 경로는 넷이고, 문헌 선례로 Kim 2023 의 액체계 절차를 다섯째 열에
둔다. 이 표가 [[one-step-vs-two-step-mixing]] 카드의 가설 목록이다.

## 비교표

| 기준 | ① One-step BM | ② Two-step (Li2S–C 선제작 → +LPSCl) | ③ Li2SO4–PVP 탄화 | ④ 에탄올 용액 | ⑤ Kim 2023 (액체계 선례) |
|---|---|---|---|---|---|
| 절차 (사용자 진술 / 원문) | Li2S·LPSCl·AB 일괄 ball milling | Li2S–C 나노복합체를 여러 방법으로 만든 뒤 LPSCl 을 **mild mixing 또는 BM** 으로 추가 | Li2SO4 를 PVP 용액에 용해 → 600–700 °C 탄화 → 900 °C 승온 → Li2S–C → LPSCl 혼합 | Li2S·C·LPSCl 각각 anhydrous ethanol 에 용해/분산 → stirring → Li2S–LPSCl–C | Gr·CNT 를 NMP 초음파 분산 → 여과·건조 → Li2S 와 BM(75:25, 조건 미기재) → 1 GPa 펠릿 |
| 무엇을 제어하나 | 한 번에 세 상을 나노 스케일로 섞음; 공정 최단 | **Li2S/C 계면을 먼저 확보**하고 SE 는 나중에 — SE 를 고에너지에서 보호 | Li2S 입자를 **탄소 안에서 생성** — 입자 크기·분산이 합성으로 정해짐 | 분자/콜로이드 수준 혼합 — 가장 균일한 삼상 접촉을 노림 | 탄소 골격을 먼저 얽고 활물질을 뒤에 — ②의 액체계 판 |
| 기대 미세구조 | Li2S·SE 모두 미세화·비정질화 가능; 세 상 무작위 분포 | Li2S–C 도메인 + 그 사이 SE; C 가 Li2S 를 감싼 채 SE 와 접함 | 탄소 매트릭스에 박힌 nano-Li2S; SE 는 도메인 밖 | 이론상 가장 균일; 실제는 용해도·재석출에 좌우 | micro-Li2S(1–5 µm)가 Gr 시트에 캡슐화 + CNT 네트워크 |
| 주요 위험 (가설) | 고에너지 BM 이 **LPSCl 을 손상**(비정질화·전도도 저하·탄소와 부반응)할 수 있음 | 2단계 mild mixing 이 SE–Li2S 접촉을 충분히 못 만들 수 있음; BM 이면 ①의 위험 재발 | 900 °C 공정·잔류 Li2SO4/황화물 부산물·탄소 함량 제어; 수율 | **LPSCl 이 극성 용매에서 분해될 위험** — 이 위키에 근거 없음(확인 필요); Li2S 의 에탄올 용해도·재석출 형태 | 액체 전해질 전용 — SE 없음. 이온 경로 문제가 애초에 없다 |
| 장비 | planetary/high-energy BM | BM 또는 Thinky(mild) | 관로·튜브 퍼니스 + BM/Thinky | 교반·건조 + Thinky | 초음파·여과·BM·프레스 |
| 위키의 근거 | 사용자 진술 | 사용자 진술 + Kim 2023 (구조적 유사) | 사용자 진술 | 사용자 진술 | `raw/papers/kim2023_…` §3 |
| 상태 | 사용 중 (주요) | 고려 중 | 고려 중 | 고려 중 | 문헌 |

장비별 성격은 [[mixing-equipment-ball-mill-thinky]].

## 결론

지금 말할 수 있는 것은 **구조**뿐이다: ①은 SE 를 활물질·탄소와 같은 에너지에 노출시키고,
②③④ 는 모두 **Li2S–C 계면을 먼저 만들고 SE 를 나중에 붙이는** 전략이다. Kim 2023 은 액체계
이지만 ②의 논리(탄소 골격 선제작)로 micro-Li2S 를 활성화했고 소량의 1D 탄소가 네트워크를
유지했다([[carbon-dimensionality-electron-network]]). 어느 경로가 우리 셀에서 이기는지는
**위키에 데이터가 없다** — 다음 ingest 와 실험이 채운다.

## 불확실성

- 위 표의 "주요 위험" 열은 전부 가설이다. 특히 ④ 의 용매–SE 상용성과 ① 의 SE 손상은 근거
  논문을 ingest 하기 전에는 인용하지 않는다.
- 사용자의 실제 BM 조건(rpm·시간·BPR·볼 재질·분위기)이 위키에 없다 — 기록 양식은
  [[mixing-equipment-ball-mill-thinky]] 에 두었다.
