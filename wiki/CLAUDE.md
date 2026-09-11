# CLAUDE.md — LLM Wiki Harness (Li2S ASSB mothership)

이 폴더는 **Karpathy LLM Wiki 패턴을 구현한 위키**다. 너(에이전트)는 이 위키의 컴파일러이자 사서다. 규칙의 원본은 `SCHEMA.md` — 위키 콘텐츠를 만들거나 고치기 전에 반드시 읽는다.

## Essential Rules (요약 — 상세는 SCHEMA.md)

1. **3-Layer 분리**: `raw/` = 불변 원본 (절대 수정 금지) · `concepts|entities|comparisons|queries|guides|questions|syntheses/` = 컴파일된 위키 · `SCHEMA.md` = 규칙.
2. **모든 위키 페이지에 frontmatter 필수**. 새 페이지는 `explored: false` + `verificationStatus: unverified` 로 시작하고 `tools/new-page.py` 로 만든다.
3. **품질 3축은 직교**: `confidence`(증거 강도) / `verificationStatus`(source 대조) / `explored`(사람이 읽음). **`explored` 는 사람만 바꾼다.**
4. 페이지마다 `[[wikilink]]` 2개 이상. 새 페이지는 `index.md` 등록 + `log.md` append (`## [YYYY-MM-DD] action | subject`).
5. 페이지를 고치면 `updated` 를 bump 한다. 작업 마무리는 `python3 wiki/tools/lint.py` 0 errors.
6. **Provenance 축**: `claimType`/`evidenceScope` 기록 (`single-source` 면 `confidence: high` 금지). 페이지에 **모델 식별자를 적지 않는다**. 타입 2종 — `questions/` research-question(열린 질문 추적), `syntheses/` synthesis(논지 방어, 반론 보존). **Paper Ingest Mode 는 opt-in** — 사용자 승인 없이 논문 atomization 금지 (`guides/paper-ingest-mode.md`).
7. **단위 규율**: 비용량에 `(S)`/`(Li2S)` 기준, 전압에 `vs Li/Li⁺`/`vs Li–In` 기준을 항상 적는다. digest 표기는 `[인쇄]/[도표]/[해석]/[재현]` 4구분.

## Operations

/wiki-ingest (자료 흡수) · /wiki-inbox (대기 큐 처리) · /wiki-query (위키 근거 답변) · /wiki-verify (페이지 검증) · /wiki-lint (건강 점검) · /wiki-status (스냅샷) · /wiki-wrap (세션 마무리: lint→log→commit)
논문 전용: **/paper** (논문 에이전트 — digest + 그림 + 컴파일) · **/seminar** (digest 에서 세미나 자료) · **/compare** (digest `compare:` 로 논문 비교표)

CLI (repo root 에서): `python3 wiki/tools/lint.py` · `python3 wiki/tools/status.py` · `python3 wiki/tools/new-page.py <type> <slug>` · `.venv/bin/python wiki/tools/extract_figures.py --slug <slug> --pdf <pdf> --clean`

## Mothership 특칙

이 위키는 **Yonghoon-DEM-DFT `main` 의 mothership**이다 (위치: repo root `wiki/`). 실험 프로젝트(reference cell · anode-free 등)는 `entities/` 1페이지로 등록하고 상태 변화 시 갱신한다 (절차: `guides/new-project-kickoff.md`). Cross-vault 참조는 `[[wikilink]]` 대신 **repo-root 상대 경로**, 내용 복사 금지(living reference). 사용자의 연구 설명·설계 세션 결정은 `raw/transcripts/` 세션 기록으로 남겨 source로 삼는다. **실험 수치의 정본은 실험 노트·원 데이터**이고 위키는 지도다.

## Git

커밋 prefix 는 log action 과 동일하되 scope 를 붙인다: `ingest(wiki):` `update(wiki):` `create(wiki):` `lint(wiki):` `verify(wiki):`. push 는 **루트 `CLAUDE.md` 하드룰 1이 지정한 작업 브랜치**로만 — 브랜치 이름은 여기 적지 않는다 (lint `no-hardcoded-branch-name` 검사).
공유 remote(origin)가 있으면 **세션 시작 시 `git pull --rebase`**, 마무리는 `/wiki-wrap` 이 commit+push 한다. `log.md` 충돌 시 양쪽 항목 모두 보존한다 (append-only).

## 이 저장소에서의 배치 (킷 원본과 다른 점)
- 위키는 별도 저장소가 아니라 repo root `wiki/` 하위다. 슬래시 커맨드는 repo root `.claude/commands/`, hook 은 `wiki/tools/hooks/` + root `.claude/settings.json`, 논문 에이전트는 `.claude/agents/paper-curator.md`.
- webapp(`webapp/`)은 이 위키를 **읽기만** 한다. digest 의 `compare:` frontmatter 가 `/compare` 화면의 정본이고, `/chat` 은 위키 본문을 근거로 답하되 저장소에 쓰지 않는다.

## Parity Contract
`CLAUDE.md` 와 `AGENTS.md` 는 같은 규칙의 미러다. 규칙을 바꾸면 두 파일을 함께 고치고 `python3 wiki/tools/lint.py` 로 parity 를 확인한다.
