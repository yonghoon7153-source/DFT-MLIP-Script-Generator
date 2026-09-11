# LLM Wiki — mid-Ni NCA721 formation 연구 mothership (Yonghoon-DEM-DFT)

Karpathy LLM Wiki 패턴 킷(`llm-wiki-kit_260730`)을 이 저장소 root `wiki/` 로 이식·적응한 위키.
**규칙 원본은 `SCHEMA.md`** — 콘텐츠를 만들거나 고치기 전에 반드시 읽는다. 도메인은
**sulfide ASSB 에서 mid-Ni NCA721 의 formation(pre-conditioning) 프로토콜 최적화** 연구다
(formation 충전 cut-off → 장기 사이클 성능·열화 메커니즘).

## 구성

| 경로 | 역할 |
|---|---|
| `SCHEMA.md` | 규칙 원본 (frontmatter, 품질 3축, 절대 규칙, `paper:` 추출 스키마, 비교표 축, 태그) |
| `CLAUDE.md` / `AGENTS.md` | 에이전트 스키마 (Parity Contract 미러) |
| `raw/papers/` | **논문 digest** (sha256 봉인, 절별 해체, `[인쇄]/[도표]/[해석]/[재현]`) |
| `raw/figures/<slug>/` | digest 마다 크로핑 그림 + `figures.json` (webapp 이 `Fig. N` 을 자동 링크) |
| `raw/transcripts|articles|repositories/` | 세션 기록(사용자 연구 설명 원문)·웹 글·저장소 감사 (불변) |
| `papers/` | **논문 노트** — `paper:` 구조화 추출(서지·양극·전해질·음극·전압·formation·main cycle·성능·기법·메커니즘 주장+근거), DOI 로 중복 제거 |
| `mechanisms/` | 열화 메커니즘 — CEI · LPSCl 산화 분해 · Ni/Co/O redox·산소 방출 · H2–H3 판별 · mid- vs high-Ni · healing · 계면 열화 |
| `protocols/` | formation/pre-conditioning · 셀 제작 조건 · main cycle · 보조 측정 |
| `experiments/` | DOE · cell registry (정본은 `data/registry/cells.csv`) |
| `comparisons/` | 논문 간 비교표 (formation cut-off / 상한 전압 vs 열화 거동 축) |
| `concepts|entities|questions|guides|queries|syntheses/` | 개념 · 프로젝트 카드 · 열린 질문 · 절차 · 질의 기록 · 논지 |
| `inbox/` | ingest 대기 큐 — PDF(+SI) 를 여기 두고 `/paper` |
| `index.md` / `log.md` | 카탈로그 / append-only 로그 |
| `tools/` | `lint.py` `status.py` `new-page.py` + `hooks/` (stdlib) · `extract_figures.py` (PDF 그림 크로핑, pymupdf — 저장소 `.venv` 에 있다) |

## 일상 사용 (WSL, repo root 에서)

```bash
python3 wiki/tools/status.py            # 스냅샷
python3 wiki/tools/lint.py              # 0 errors 확인
python3 wiki/tools/new-page.py mechanism <slug>
.venv/bin/python wiki/tools/extract_figures.py --slug <slug> --pdf <pdf> --clean
midni                                   # webapp 열기 (alias — 루트 README)
```

논문 흡수: PDF(+SI)를 `wiki/inbox/` 에 넣거나 대화에 첨부하고 **`/paper`** (논문 에이전트).
논문 비교: **`/compare`** 또는 webapp `/compare`. 셀 데이터: **`/cells`** 또는 `tools/cells/import_cell.py`.
세션 마무리: `/wiki-wrap` (lint → log → commit → push).

## 킷 원본과 다른 점

1. **배치**: 별도 저장소가 아니라 repo root `wiki/`. 커맨드는 root `.claude/commands/` 에 `wiki-` 접두
   (+ `/paper` `/compare` `/cells`), hook 은 `wiki/tools/hooks/` + root `.claude/settings.json`.
2. **디렉터리 4종 추가**: `papers/`(paper-note) · `mechanisms/` · `protocols/` · `experiments/` — 연구 카테고리를
   폴더로 세운다. lint/status/new-page 가 모두 안다.
3. **논문이 두 파일**: raw digest(불변) + papers 노트(`paper:` 스키마, 수정 가능, DOI 정본).
4. **절대 규칙 lint**: `no-ncm721` · `canonical-offset`(+0.62 V 상수는 `config/cells.yaml` 이 정본) · `unit-rule` ·
   `voltage-reference` · `doi-unique` · `no-hardcoded-branch-name` · `no-model-identifier` · `parity`.
5. **Cross-vault 참조**: 절대 경로 대신 repo-root 상대 경로 (WSL·서버 clone 경로가 다르다).
6. **모델 식별자 미기재**: 페이지 frontmatter 에 `model`/`effort` 를 적지 않는다.
