---
title: Anode-free Li2S ASSB
description: "reference cell 이 끝난 뒤 Li–In 음극을 anode-free 구성으로 바꾸는 2단계 프로젝트 — Li 원천이 양극(Li2S)에만 있으므로 첫 사이클 손실과 Li 침적 균일성이 전부다"
created: 2026-09-11
updated: 2026-09-11
type: entity
tags: [project, satellite, anode-free, li2s, assb]
sources: [raw/transcripts/2026-09-11-li2s-wiki-kickoff-session.md, raw/papers/kim2023_reinforced-electrical-networking-high-loading-li2s-cathode.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
---

# Anode-free Li2S ASSB

## 개요

[[li2s-assb-reference-cell]] 의 다음 단계. Li–In 음극을 빼고 집전체 위에 Li 를 **셀 안에서
처음으로** 석출시키는 anode-free 구성. 계획 단계이며 실험은 시작되지 않았다 (2026-09-11).

## 왜 Li2S 여야 가능한가

Li2S 는 방전 상태의 활물질이라 **Li 원천이 양극에 있다**. 그래서 Li-free 음극(흑연·Si·집전체만)이
가능하다 — Kim et al. 2023 이 도입부에서 그대로 쓰는 논거이고(`raw/papers/kim2023_…` §2.2),
그 논문은 흑연 음극(N/P 1.2)으로 800 사이클을 돌렸다. anode-free 는 그 극한(N/P → 0)이다.

## 이 구성이 참이려면 참이어야 하는 것

1. **첫 충전에서 Li2S 가 충분히 활성화**되어야 한다 — 활성화 안 된 Li2S 는 뒤 사이클에서도
   깨어나지 않는다(Kim 2023 Fig. S1, [[li2s-activation-first-charge]]). anode-free 는 Li 재고가
   양극 활성화량 **그 자체**다.
2. **첫 사이클 비가역 손실이 작아야** 한다 — SEI 형성·SE 분해·Li 데드 형성이 전부 재고에서 빠진다.
3. **Li 침적이 균일**해야 한다 — Kim 2023 의 Li 금속 파우치 반쪽셀조차 중심부 Li 고갈로 30 사이클
   뒤 CE 가 요동했다(Fig. S10). 초기 Li 가 0 인 구성은 여유가 더 없다.
4. **스택 압력·집전체 계면**이 침적 형태를 정한다 — 이 위키에 아직 근거 논문이 없다 (ingest 필요).

## 상태

- **2026-09-11** — 계획. reference cell 이 목표를 달성하면 착수. 그전에 anode-free ASSB 문헌
  (Li 석출 균일성·집전체 코팅·압력) 을 ingest 해 이 페이지의 4번 항목을 채운다.

## 관련

- [[li2s-assb-reference-cell]] — 선행 프로젝트
- [[reference-cell-500-600-mahg]] — 그쪽 답이 이쪽의 Li 재고 상한을 정한다
- [[li2s-activation-first-charge]]
