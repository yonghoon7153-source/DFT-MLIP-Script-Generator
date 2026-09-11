# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, verify, archive, delete

## [2026-07-30] create | Wiki initialized (kit)
- llm-wiki harness 킷(`llm-wiki-kit_260730`) — tools + commands + hooks + CI. 이 저장소에는 2026-09-11 에 이식했다 (아래).

## [2026-08-06] update | 하네스 v1.8~v1.10 채택 (킷 원본에서 전파)
- frontmatter `claimType`/`evidenceScope`, 타입 2종(`questions/` `syntheses/`), Paper Ingest Mode opt-in, raw changelog `raw/articles/2026-08-06-cmds-llm-wiki-changelog.md`.

## [2026-09-11] create | mid-Ni NCA721 formation 연구 mothership 이식 — wiki/ + webapp + 논문 에이전트 + 셀 데이터 모듈
- 킷을 repo root `wiki/` 로 이식하고 도메인을 **sulfide ASSB 에서 NCA721 formation(pre-conditioning) cut-off 최적화** 로 세웠다. 사용자가 지정한 카테고리를 폴더로 추가: `papers/`(논문 노트) · `mechanisms/` · `protocols/` · `experiments/`. lint 에 절대 규칙 검사 5종(`no-ncm721` `canonical-offset` `voltage-reference` `unit-rule` `doi-unique`) + 선행 브랜치의 drift 검사 3종(`no-hardcoded-branch-name` `no-model-identifier` `parity`) + `paper-note-voltage`.
- 설계 기록: `raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md` (사용자의 연구 설명 원문 + 절대 규칙 + 설계 결정 + 미결 Q1–Q6, sha256 봉인). `wiki/tools/seal.py` 신설 (미봉인 raw 만 봉인).
- 논문은 두 파일: `raw/papers/<slug>.md` digest(불변) + `papers/<slug>.md` 노트(`paper:` 추출 스키마, 값 없으면 null, DOI 가 중복 제거 키). 정본 상수는 `config/cells.yaml` (offset 0.62 V, DOE 창, cut-off 색).

## [2026-09-11] create | 연구 시드 — 메커니즘 7 · 프로토콜 4 · 실험 2 · 비교 1 · 개념 2 · 프로젝트 2 · 질문 3 · 가이드 7 (28 페이지)
- mechanisms: [[cei-formation-sulfide-cathode]] · [[lpscl-oxidative-decomposition-by-voltage]] · [[ni-co-o-redox-and-oxygen-release]] · [[h2-h3-phase-transition-identification]] · [[mid-ni-vs-high-ni-degradation]] · [[mechano-electrochemical-healing]] · [[interface-degradation-cathode-electrolyte-anode]] — 전부 `> [!note] 미검증 배경` + `confidence: low` + `evidenceScope: synthesis-only`. 근거 논문이 0편이므로 인용 근거가 아니며, 각 페이지의 "근거 상태" 절이 투입 예정 논문을 제목 기준으로 지목한다.
- protocols: [[formation-preconditioning-protocol]] · [[cell-fabrication-conditions]] · [[main-cycle-protocol]] · [[auxiliary-measurements]] — 사용자 진술 사본 (`evidenceScope: user-original`), 미기재 항목은 비워 두고 킥오프 기록 Q1–Q6 으로 넘겼다.
- experiments: [[formation-cutoff-doe]] · [[cell-registry]]. comparisons: [[formation-cutoff-vs-degradation-literature]] (투입 예정 10편의 자리). concepts: [[voltage-reference-and-capacity-conventions]] · [[nca721-mid-ni-cathode]]. entities: [[nca721-formation-project]] (`ours:` 블록) · [[followup-high-ni-and-anode-free-pouch]]. questions: [[formation-cutoff-vs-long-term-degradation]] (active, H1–H5) · [[lattice-oxygen-involvement-at-high-cutoff]] · [[contact-loss-vs-cei-growth-attribution]]. guides: [[wsl-midni-setup]] · [[paper-agent-workflow]] · [[cell-data-module]] · [[chat-citation-rules]] · [[terminology-ipa]] · [[new-project-kickoff]] · [[paper-ingest-mode]].
- 원칙: 실험 수치는 위키에 없다 (정본은 `data/`). 전압에는 기준전극을 붙였고 절대용량은 쓰지 않았다.
