# AGENTS.md — LLM Wiki Harness (portable)

이 파일은 **Claude Code 이외의 코딩 에이전트**(Codex · Cursor · Windsurf · Gemini CLI 등)를 위한 스키마다. `CLAUDE.md` 의 미러이며, 두 파일은 **Parity Contract** 로 동일하게 유지된다. 규칙의 원본은 `SCHEMA.md` — 위키 콘텐츠를 만들거나 고치기 전에 반드시 읽는다. 연구 도메인의 절대 규칙은 루트 `CLAUDE.md` 맨 아래 [절대 규칙].

## Essential Rules (요약 — 상세는 SCHEMA.md)

1. **3-Layer 분리**: `raw/` = 불변 원본 (절대 수정 금지) · `papers|mechanisms|protocols|experiments|comparisons|concepts|entities|queries|guides|questions|syntheses/` = 컴파일된 위키 · `SCHEMA.md` = 규칙.
2. **모든 위키 페이지에 frontmatter 필수**. 새 페이지는 `explored: false` + `verificationStatus: unverified` 로 시작하고 `wiki/tools/new-page.py` 로 만든다. 모델 식별자는 적지 않는다.
3. **품질 3축은 직교**: `confidence`(증거 강도) / `verificationStatus`(source 대조) / `explored`(사람이 읽음). **`explored` 는 사람만 바꾼다.**
4. 페이지마다 `[[wikilink]]` 2개 이상. 새 페이지는 `index.md` 등록 + `log.md` append (`## [YYYY-MM-DD] action | subject`).
5. 페이지를 고치면 `updated` 를 bump 한다. 작업 마무리는 `python3 wiki/tools/lint.py` 0 errors.
6. **논문은 두 파일**: `raw/papers/<slug>.md` digest(sha256 봉인, 4구분 표기) + `papers/<slug>.md` 노트(`paper:` 추출 스키마, DOI 가 중복 제거 키, 값이 없으면 null). 근거 없는 배경 지식은 `> [!note] 미검증 배경` + `confidence: low` + `evidenceScope: synthesis-only`. **Paper Ingest Mode 는 opt-in**.
7. **절대 규칙**: NCA721 을 NCM721 로 바꾸지 않는다 · 전압에는 기준전극 필수, vs. Li/Li⁺ = vs. In/Li-In + 0.62 V · mAh g⁻¹ 과 mAh cm⁻² 혼동 금지, 절대용량 보고 금지 · 충전 = delithiation, 방전 = lithiation.

## Operations

Operation 의 정식 절차는 repo root `.claude/commands/{operation}.md` 에 마크다운으로 있다. `/` 트리거는 Claude Code 전용이지만 파일은 어느 에이전트나 읽을 수 있다 — operation 전에 해당 파일을 읽고 따른다.

/paper · /compare · /cells · /wiki-ingest · /wiki-inbox · /wiki-query · /wiki-verify · /wiki-lint · /wiki-status · /wiki-wrap

CLI (에이전트 무관, repo root 에서): `python3 wiki/tools/lint.py` · `python3 wiki/tools/status.py` · `python3 wiki/tools/new-page.py <type> <slug>` · `.venv/bin/python wiki/tools/extract_figures.py --slug <slug> --pdf <pdf> --clean`

## Agent-specific Notes

- **Codex/Cursor/Windsurf**: 이 `AGENTS.md` 를 자동 로드. `raw/` 는 불변 — 수정 금지 (Claude 는 hook 으로 강제되지만 다른 에이전트는 스스로 지킨다).
- **Gemini 등 `GEMINI.md` 를 찾는 에이전트**: `ln -s AGENTS.md GEMINI.md` 심링크.
- **자동 게이트**: raw 보호 hook 과 편집 후 자동 lint 는 root `.claude/settings.json` + `wiki/tools/hooks/` 에 있어 Claude Code 전용. 다른 에이전트는 편집 후 `python3 wiki/tools/lint.py` 를 수동 실행.

## Git

커밋 prefix 는 log action 과 동일하되 scope 를 붙인다: `ingest(wiki):` `update(wiki):` `create(wiki):` `lint(wiki):` `verify(wiki):`. push 는 루트 `CLAUDE.md` 하드룰 1 의 브랜치로만. 공유 remote 가 있으면 **세션 시작 시 `git pull --rebase`**, 마무리는 `/wiki-wrap` 절차가 commit+push 한다. `log.md` 충돌 시 양쪽 항목 모두 보존한다 (append-only).

## Parity Contract (CLAUDE.md ↔ AGENTS.md)

두 파일은 미러다. Essential Rules / Operations / Git 규약이 동일해야 한다. 한쪽만 편집하면 drift — `python3 wiki/tools/lint.py` 가 parity 를 검사한다.
