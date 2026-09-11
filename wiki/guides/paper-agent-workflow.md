---
title: 논문 에이전트 워크플로 — PDF(+SI) → DOI 중복 확인 → digest + 노트 + 그림 → 질문 카드
description: "/paper 가 하는 일의 순서와 산출물, DOI 기준 중복 제거와 Supplementary 연결 규칙, 추출 스키마의 null 원칙"
created: 2026-09-11
updated: 2026-09-11
type: guide
tags: [wiki, tooling]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
---

# 논문 에이전트 워크플로

## 목적
사용자가 모아 둔 mid-Ni/high-Ni 양극·황화물 전해질 계면·formation 프로토콜 논문을 **같은 형식**으로 DB 화해,
논문끼리 비교하고(`/compare`) 대화의 근거로 쓰는 것(`/chat`). 정식 절차는 `.claude/agents/paper-curator.md` 와
`.claude/commands/paper.md` 이며 이 페이지는 사람이 읽는 요약이다.

## 절차
1. **넣기**: PDF(+Supplementary) 를 `wiki/inbox/` 에 (`midni paper <main.pdf> <si.pdf>`) 또는 대화에 첨부.
   Supplementary 는 본문 논문과 **같이** 넣는다.
2. **DOI 중복 확인** (가장 먼저): PDF 에서 DOI 를 읽어 `papers/*.md` 의 `paper.bib.doi` 와 대조한다. 같은 논문이
   파일명만 다르게 들어온 것이면 **새 노트를 만들지 않고 기존 노트를 갱신**한다 (digest 는 불변이므로 새로 만들지
   않는다 — 새 판본이 정말 다르면 `-v2` digest). DOI 가 없는 자료(학위논문·프리프린트 초안)는
   `doi_missing_reason` 에 이유를 적는다. lint `doi-unique` 가 중복을 막는다.
3. **읽기**: pymupdf 텍스트 덤프(스크래치패드) — 인용은 거기서 복사한다.
4. **그림**: `extract_figures.py --slug <slug> --pdf <main> --pdf <si> --clean` → `raw/figures/<slug>/`. SI 그림은
   `fig_S<n>.png`. 핵심 그림은 **실제로 본 뒤** 쓴다.
5. **digest**: `raw/papers/<slug>.md` — 절별 해체, 공백표, `[인쇄]/[도표]/[해석]/[재현]`, 우리 접점 표. 해시 먼저
   (`wiki/tools/seal.py`) → 한 번에 Write. 이후 수정 금지.
6. **노트**: `papers/<slug>.md` — frontmatter `raw:` + `paper:` 블록(SCHEMA 의 추출 스키마). **값이 없으면 null**,
   추측으로 채우지 않는다. 전압은 원문 값·기준 그대로 + 변환값·offset 별도. 메커니즘 주장은 **figure/page 근거가
   있는 것만** 항목으로 넣는다. Supplementary 파일명은 `paper.supplementary.files` 에.
7. **컴파일**: 관련 메커니즘 페이지의 `sources` 에 digest 추가 + 근거 상태 갱신(등급 상향은 근거가 붙었을 때만),
   열린 질문 카드 Evidence For/Against 에 날짜·가설 번호와 함께 라우팅, `index.md`·`log.md`, lint 0 errors.
8. **설명**: 사용자에게 — 질문과 답, 핵심 수치(단위·기준 병기), 그림별, 방법, **우리 DOE 와의 접점**(기준전극·조성·
   온도·압력·loading 차이 먼저), 본/안 본 그림.
9. **커밋** `ingest(wiki): <FirstAuthor Year> — …` → push. inbox 원본 삭제.

## 초기 투입 예정 (제목 기준)
[[formation-cutoff-vs-degradation-literature]] 의 표 10편. 첫 논문은 우리 축과 가장 가까운 "Chemo-Mechanical
Behavior of High- and Mid-Ni Cathodes in Sulfide-Based ASSBs (Small Structures 2026, Suppl.)" 를 권한다.

## 관련
- [[chat-citation-rules]] · [[paper-ingest-mode]] · [[nca721-mid-ni-cathode]] (조성 표기 규칙)
