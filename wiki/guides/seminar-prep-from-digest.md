---
title: Digest 에서 세미나 자료 만들기 (/seminar)
description: "논문 digest 하나를 논문 세미나 발표로 옮기는 표준 절차 — 공백표에서 시작해 스토리라인·슬라이드별 그림·양단위 숫자표·비판·예상 질문·우리 연결까지"
created: 2026-09-11
updated: 2026-09-11
type: guide
tags: [seminar, wiki]
sources: [raw/transcripts/2026-09-11-li2s-wiki-kickoff-session.md, raw/papers/kim2023_reinforced-electrical-networking-high-loading-li2s-cathode.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
---

# Digest 에서 세미나 자료 만들기 (/seminar)

## 목적
사용자의 논문 세미나(journal club) 준비를 **digest 위에서** 한다. digest 가 없으면 먼저 `/paper`.
산출물은 `wiki/queries/<slug>-seminar-prep.md` (type: query) 이고 webapp `/doc/queries/…` 에서
읽는다. 첫 적용: [[kim2023-seminar-prep]].

## 절차

1. **공백표부터 읽는다** — digest 의 "원문에 없어서 확인이 필요한 것" 표. 세미나에서 가장 좋은
   질문과 가장 위험한 실수가 여기서 나온다 (예: Kim 2023 G3 — 본문 수치가 SI 표와 어긋남).
2. **한 줄 메시지**를 정한다 — 청중이 가져갈 문장 하나. 논문 초록의 문장이 아니라 **우리 관점**
   에서 다시 쓴다.
3. **스토리라인 5막**: 문제 → 설계 → 증거(성능) → 증거(기전) → 한계와 우리 연결.
4. **슬라이드별 표**: 제목 · 보여줄 그림(`raw/figures/<slug>/fig_N.png`, 패널 지정) · 말할 3가지 ·
   발표자 노트 · 시간. 그림은 digest 의 "그림 판독 기록" 에서 **직접 본 것**만 고른다; 안 본
   그림을 쓰려면 먼저 본다.
5. **숫자표는 양단위**로 — 비용량 `(S)`/`(Li2S)`, 면적용량은 로딩과 함께
   ([[capacity-normalization-li2s-vs-sulfur]]). digest 의 `[도표]` 값은 발표에서도 "그림에서
   읽은 근사값" 이라고 말한다.
6. **비판 슬라이드**: digest §비판 에서 3개 고른다. 칭찬으로 끝내지 않는다.
7. **우리 연결 슬라이드**: digest 의 "우리 연구와의 접점" 표 → 옮겨 올 것 / 못 옮길 것.
8. **예상 질문 10개 + 답** — 답에는 근거 위치(digest §, Fig.)를 붙인다. 모르는 것은 "논문에
   없다" 로 답한다.
9. **발표 체크리스트**: 단위 · 오기 정정 · "안정" 의 뜻(CE 인가 용량인가) · 셀 개수.
10. 선택: `/seminar <slug> --pptx` 로 pptx 초안 생성 (본문 텍스트는 이 페이지에서 가져온다).

## 규칙
- 발표 자료의 모든 수치는 digest 를 거친다 — 논문 PDF 에서 바로 옮기지 않는다 (digest 가
  `[인쇄]/[도표]` 를 갈라 두었기 때문).
- 이 페이지는 `queries/` 에 두고 `verificationStatus: unverified` 로 시작한다. 발표가 끝나면
  받은 질문을 "Status" 절에 append 한다 — 다음 발표의 예상 질문이 된다.

## 관련
- [[kim2023-seminar-prep]] — 첫 적용
- [[paper-ingest-mode]] — 집필용 opt-in 모드 (이것과 다르다)
