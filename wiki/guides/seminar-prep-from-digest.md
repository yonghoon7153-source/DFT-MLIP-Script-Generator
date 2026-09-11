---
title: Digest 에서 세미나 자료 만들기 (/seminar)
description: "논문 digest 하나를 논문 세미나 발표로 옮기는 표준 절차 — 공백표에서 시작해 스토리라인·막별 참고 대본·슬라이드별 그림·양단위 숫자표·비판·예상 질문·우리 연결까지"
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
4. **막별 참고 대본** (2026-09-11 추가 — 사용자 요청). 막마다 **대여섯 문장**의 구어체 원고를
   적는다. 읽어 내려가는 원고가 아니라 **발표 중 눈으로 한 번 훑는 것**이므로 짧게. 각 막은
   네 덩이로 쓴다:
   - **여는 말** — 이 막이 답하는 질문 한 문장.
   - **본문** — 3–4 문장. 숫자를 문장 안에 넣되 **단위 기준을 말로 붙인다** ("황 기준 899.6",
     "Li2S 기준으로는 628"). `[도표]` 값은 대본에서도 **"그림에서 읽은 값이라"** 라고 말하게 쓴다.
   - **넘기는 말** — 다음 막으로 잇는 한 문장. 막과 막 사이에서 말이 끊기는 게 제일 흔한 사고다.
   - **여기서 틀리기 쉬운 것** — 그 막 고유의 함정 한 줄 (단위 뒤집힘, 원문 오기, "안정" 의 뜻).
   대본의 수치도 전부 digest 를 거친다. 발표 시간을 막별로 배분해 대본 머리에 `(슬라이드 N–M,
   약 X분)` 을 적는다.
5. **슬라이드별 표**: 제목 · 보여줄 그림(`raw/figures/<slug>/fig_N.png`, 패널 지정) · 말할 3가지 ·
   발표자 노트 · 시간. 그림은 digest 의 "그림 판독 기록" 에서 **직접 본 것**만 고른다; 안 본
   그림을 쓰려면 먼저 본다.
6. **숫자표는 양단위**로 — 비용량 `(S)`/`(Li2S)`, 면적용량은 로딩과 함께
   ([[capacity-normalization-li2s-vs-sulfur]]). digest 의 `[도표]` 값은 발표에서도 "그림에서
   읽은 근사값" 이라고 말한다.
7. **비판 슬라이드**: digest §비판 에서 3개 고른다. 칭찬으로 끝내지 않는다.
8. **우리 연결 슬라이드**: digest 의 "우리 연구와의 접점" 표 → 옮겨 올 것 / 못 옮길 것.
9. **예상 질문 10개 + 답** — 답에는 근거 위치(digest §, Fig.)를 붙인다. 모르는 것은 "논문에
   없다" 로 답한다.
10. **발표 체크리스트**: 단위 · 오기 정정 · "안정" 의 뜻(CE 인가 용량인가) · 셀 개수.
11. 선택: `/seminar <slug> --pptx` 로 pptx 초안 생성 (본문 텍스트는 이 페이지에서 가져온다).

## 규칙
- 발표 자료의 모든 수치는 digest 를 거친다 — 논문 PDF 에서 바로 옮기지 않는다 (digest 가
  `[인쇄]/[도표]` 를 갈라 두었기 때문).
- **대본은 대본일 뿐이다** — 발표장에서 그대로 읽으면 티가 난다. 숫자와 전환만 눈에 담고
  말은 그 자리에서 만든다. 대본이 길어지면(한 막 10문장 넘으면) 슬라이드가 너무 무겁다는 신호다.
- 이 페이지는 `queries/` 에 두고 `verificationStatus: unverified` 로 시작한다. 발표가 끝나면
  받은 질문을 "Status" 절에 append 한다 — 다음 발표의 예상 질문이 된다.

## 관련
- [[kim2023-seminar-prep]] — 첫 적용
- [[paper-ingest-mode]] — 집필용 opt-in 모드 (이것과 다르다)
