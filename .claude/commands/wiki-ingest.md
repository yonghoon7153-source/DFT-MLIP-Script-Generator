---
description: 외부 자료(논문 아닌 글·전사·저장소)를 raw source 로 저장하고 위키 페이지로 컴파일 — 논문은 /paper
---

> 이 위키는 repo root `wiki/` 하위다 (킷 원본과 배치가 다름 — `wiki/README.md` 참조). 아래 절차의 모든 경로는 repo root 기준이다. 절대 규칙(루트 `CLAUDE.md` 맨 아래)을 지킨다.

새 자료를 이 LLM Wiki 에 ingest 한다. 대상: $ARGUMENTS (논문 PDF 면 이 커맨드가 아니라 **/paper** 다.)

`wiki/SCHEMA.md` 의 규칙을 따른다. 절차:

1. **목적 확인 (Collection Purpose Gate)**: 사용자에게 딱 한 번 묻는다 — "이 자료를 왜 수집하나요? 어디에 쓸 예정인가요?"
2. **Raw 저장**: 본문을 가능한 한 원형 그대로 `wiki/raw/articles/YYYY-MM-DD-{slug}.md` (전사면 `wiki/raw/transcripts/`, 레포 감사면
   `wiki/raw/repositories/`) 에 저장한다. frontmatter 는 `source_url`, `ingested`, `sha256: PENDING` → `python3 wiki/tools/seal.py <file>` 로 봉인.
   수집 목적은 raw 파일 본문 상단에 한 줄 기록한다.
3. **중복 확인**: `wiki/index.md` 를 읽고 이미 있는 페이지와 겹치는지 확인한다. 겹치면 새 페이지 대신 기존 페이지를 갱신한다 (`updated` bump).
4. **RQ 라우팅**: `wiki/questions/` 의 열린 카드(status: open|active)를 훑고, 이 자료가 근거를 주면 Evidence For/Against 와 Status Log 에 추가한다.
5. **컴파일**: 핵심 개념/메커니즘/프로토콜을 위키 페이지로 만든다 (보통 1~3개, `python3 wiki/tools/new-page.py <type> <slug>`). 새 페이지는
   `explored: false`, `verificationStatus: unverified`, `confidence` 는 정직하게 + `claimType`/`evidenceScope`. 근거 논문 없는 배경이면
   `> [!note] 미검증 배경` + `confidence: low` + `evidenceScope: synthesis-only`. 각 페이지에 `[[wikilink]]` 2개 이상 + 역링크.
   전압에는 기준전극, 용량은 mAh g⁻¹/mAh cm⁻² 구분.
6. **등록**: `wiki/index.md` 에 한 줄 요약과 함께 등록하고, `wiki/log.md` 에 `## [YYYY-MM-DD] ingest | {제목}` 항목을 append 한다.
7. **Lint**: `python3 wiki/tools/lint.py` 를 실행해 0 errors 를 확인하고 결과를 보고한다.

Raw source 는 절대 수정하지 않는다. 해석은 위키 페이지에서만 한다.
