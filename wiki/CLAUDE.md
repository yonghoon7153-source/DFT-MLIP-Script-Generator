# CLAUDE.md — LLM Wiki Harness

이 폴더는 **Karpathy LLM Wiki 패턴을 구현한 위키**다. 너(에이전트)는 이 위키의 컴파일러이자 사서다. 규칙의 원본은 `SCHEMA.md` — 위키 콘텐츠를 만들거나 고치기 전에 반드시 읽는다. 연구 도메인의 절대 규칙은 루트 `CLAUDE.md` 맨 아래 [절대 규칙] (NCA721 · 전압 기준전극 · 용량 단위 · 충방전 용어).

## Essential Rules (요약 — 상세는 SCHEMA.md)

1. **3-Layer 분리**: `raw/` = 불변 원본 (절대 수정 금지) · `papers|mechanisms|protocols|experiments|comparisons|concepts|entities|queries|guides|questions|syntheses/` = 컴파일된 위키 · `SCHEMA.md` = 규칙.
2. **모든 위키 페이지에 frontmatter 필수**. 새 페이지는 `explored: false` + `verificationStatus: unverified` 로 시작하고 `wiki/tools/new-page.py` 로 만든다. 모델 식별자는 적지 않는다.
3. **품질 3축은 직교**: `confidence`(증거 강도) / `verificationStatus`(source 대조) / `explored`(사람이 읽음). **`explored` 는 사람만 바꾼다.**
4. 페이지마다 `[[wikilink]]` 2개 이상. 새 페이지는 `index.md` 등록 + `log.md` append (`## [YYYY-MM-DD] action | subject`).
5. 페이지를 고치면 `updated` 를 bump 한다. 작업 마무리는 `python3 wiki/tools/lint.py` 0 errors.
6. **논문은 두 파일**: `raw/papers/<slug>.md` digest(sha256 봉인, 4구분 표기) + `papers/<slug>.md` 노트(`paper:` 추출 스키마, DOI 가 중복 제거 키, 값이 없으면 null). 근거 없는 배경 지식은 `> [!note] 미검증 배경` + `confidence: low` + `evidenceScope: synthesis-only`. **Paper Ingest Mode 는 opt-in**.
7. **절대 규칙**: NCA721 을 NCM721 로 바꾸지 않는다 · 전압에는 기준전극 필수, vs. Li/Li⁺ = vs. In/Li-In + 0.62 V · mAh g⁻¹ 과 mAh cm⁻² 혼동 금지, 절대용량 보고 금지 · 충전 = delithiation, 방전 = lithiation.

## Operations

/paper (논문 에이전트: digest + 노트 + 그림 + 질문 카드 라우팅) · /compare (논문 비교) · /cells (셀 데이터 import) · /wiki-ingest (자료 흡수) · /wiki-inbox (대기 큐 처리) · /wiki-query (위키 근거 답변) · /wiki-verify (페이지 검증) · /wiki-lint (건강 점검) · /wiki-status (스냅샷) · /wiki-wrap (세션 마무리: lint→log→commit)

CLI (repo root 에서): `python3 wiki/tools/lint.py` · `python3 wiki/tools/status.py` · `python3 wiki/tools/new-page.py <type> <slug>` · `.venv/bin/python wiki/tools/extract_figures.py --slug <slug> --pdf <pdf> --clean`

## Mothership 특칙

이 위키는 **Yonghoon-DEM-DFT 의 mid-Ni formation 연구 mothership** 이다 (위치: repo root `wiki/`). 실험 프로젝트(satellite)는 `entities/` 1페이지로 등록하고 상태 변화 시 갱신한다. Cross-vault 참조는 `[[wikilink]]` 대신 **repo-root 상대 경로**(`data/…`, `config/…`), 내용 복사 금지(living reference). 설계 세션·사용자의 연구 설명은 `raw/transcripts/` 세션 기록으로 남겨 source 로 삼는다. 실험 수치의 정본은 `data/raw/` 원 데이터와 `data/registry/cells.csv` 다.

## Git

커밋 prefix 는 log action 과 동일하되 scope 를 붙인다: `ingest(wiki):` `update(wiki):` `create(wiki):` `lint(wiki):` `verify(wiki):`. push 는 루트 `CLAUDE.md` 하드룰 1 의 브랜치로만. 공유 remote 가 있으면 **세션 시작 시 `git pull --rebase`**, 마무리는 `/wiki-wrap` 이 commit+push 한다. `log.md` 충돌 시 양쪽 항목 모두 보존한다 (append-only).

## Parity Contract
`CLAUDE.md` 와 `AGENTS.md` 는 같은 규칙의 미러다. 규칙을 바꾸면 두 파일을 함께 고치고 `python3 wiki/tools/lint.py` 로 parity 를 확인한다 (검사 `parity`).
