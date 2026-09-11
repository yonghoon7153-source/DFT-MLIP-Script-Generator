# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, verify, archive, delete

## [2026-07-30] create | Wiki initialized (kit)
- llm-wiki harness 킷(`llm-wiki-kit_260730`) — tools + commands + hooks + CI. 이 저장소에는 2026-09-11 에 이식했다 (아래).

## [2026-08-06] update | 하네스 v1.8~v1.10 채택 (킷 원본에서 전파)
- frontmatter `claimType`/`evidenceScope`, 타입 2종(`questions/` `syntheses/`), Paper Ingest Mode opt-in, raw changelog `raw/articles/2026-08-06-cmds-llm-wiki-changelog.md`.

## [2026-09-11] create | Li2S ASSB mothership 이식 — `main` 브랜치, wiki/ + webapp + 논문 에이전트
- 킷과 선행 브랜치의 적응(`wiki-*` 커맨드, hook 위치, repo-root 상대 경로, `<action>(wiki):` 접두, `no-hardcoded-branch-name` lint)을 그대로 가져와 도메인을 **Li2S 양극 all-solid-state Li–S** 로 바꿨다. SCHEMA 에 단위 규율·digest 4구분·`compare:` 블록·Li2S 태그 시드를 추가. 페이지에 모델 식별자를 적지 않는 규칙.
- 설계 기록: `raw/transcripts/2026-09-11-li2s-wiki-kickoff-session.md` (사용자의 연구 설명 원문 + 설계 결정 + 미결 Q1–Q4, sha256 봉인).

## [2026-09-11] create | 연구 시드 — satellite 2 · 개념 5 · 비교 1 · 질문 2 · 가이드 4
- entities: [[li2s-assb-reference-cell]] (진행 중) · [[anode-free-li2s-assb]] (계획).
- concepts: [[li2s-assb-composite-cathode]] · [[li2s-activation-first-charge]] · [[carbon-dimensionality-electron-network]] · [[capacity-normalization-li2s-vs-sulfur]] · [[mixing-equipment-ball-mill-thinky]].
- comparison: [[composite-cathode-mixing-routes]]. questions: [[reference-cell-500-600-mahg]] (active) · [[one-step-vs-two-step-mixing]] (open).
- guides: [[new-project-kickoff]] (상대 경로판) · [[paper-ingest-mode]] (모델 필드 제거) · [[seminar-prep-from-digest]] (신설) · [[wsl-li2s-setup]] (신설).
- 원칙: 사용자 진술만이 근거인 페이지는 `evidenceScope: user-original`, 일반 지식은 "미검증 배경" 으로 표시하고 인용 금지. 실험 수치는 위키에 없다 (정본은 실험 노트).

## [2026-09-11] ingest | Kim et al. 2023 — Long-lasting, reinforced electrical networking in a high-loading Li2S cathode (Carbon Energy 5, e308)
- raw 봉인: `raw/papers/kim2023_reinforced-electrical-networking-high-loading-li2s-cathode.md` (14쪽 본문 절별 해체 + SI 전문 대조, 공백표 G1–G14, `[인쇄]/[도표]/[해석]/[재현]` 4구분, `compare:` frontmatter). 그림: 본문 8장은 `extract_figures.py` 캡션 앵커 크로핑, SI 11장은 .docx 내장 이미지 → `raw/figures/kim2023_…/` (19장, `figures.json`).
- 판독: Fig. 1–8, S1, S4, S11 을 직접 봤다. S2·S3·S5–S10 은 캡션·본문만.
- 발견: 본문 p.8 "899.6 mAh g⁻¹ (11.5 mAh cm⁻²)" 의 괄호는 0.1 C 값 — 0.5 C 는 Table S1 의 9.3 mAh cm⁻² (G3). "800 사이클 안정" 은 CE 기준, 용량은 43 %.
- 컴파일: [[li2s-activation-first-charge]] · [[carbon-dimensionality-electron-network]] · [[capacity-normalization-li2s-vs-sulfur]] 의 근거. RQ 라우팅: [[reference-cell-500-600-mahg]] Evidence For(H1·H2·H4) · [[one-step-vs-two-step-mixing]] Evidence For(H1).

## [2026-09-11] query | Kim 2023 논문 세미나 준비
- [[kim2023-seminar-prep]]: 한 줄 메시지, 5막 스토리라인, 16장 슬라이드(그림 파일·패널 지정), 양단위 숫자표, 비판 3+3, 우리 연결 표, 예상 질문 10, 체크리스트. 절차는 [[seminar-prep-from-digest]] 로 가이드화.

## [2026-09-11] query | Kim 2023 세미나 초안 덱 (pptx)
- `queries/kim2023-seminar-draft.pptx` — [[kim2023-seminar-prep]] 의 슬라이드 표를 18장 덱으로 (그림은 `raw/figures/kim2023_…/` 크롭, 발표자 노트 포함, 발표자·날짜는 빈칸). 텍스트는 그 페이지에서만 가져왔고 수치의 `[도표]` 표시를 유지했다. 이 환경에는 렌더러(LibreOffice Impress)가 없어 시각 QA 는 휴리스틱(텍스트 상자 폭·높이 계산)으로만 했다 — 열어서 한 번 훑을 것.

## [2026-09-11] update | 작업 브랜치 이전 — `main` → 루트 CLAUDE.md 하드룰 1 의 브랜치
- 사용자 요청: main 에서 작업하지 않는다. 오늘의 커밋 5개를 새 브랜치로 옮기고 main 은 Initial commit 으로 되돌렸다. 킥오프 기록(raw, 불변)의 "main 을 mothership 으로" 결정은 이 항목으로 정정한다. 브랜치 이름은 위키에 적지 않는다.
