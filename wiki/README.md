# LLM Wiki — Li2S ASSB mothership (Yonghoon-DEM-DFT)

Karpathy LLM Wiki 패턴 킷(`llm-wiki-kit_260730`)을 이 저장소 root `wiki/` 로 이식·적응한
위키. **규칙 원본은 `SCHEMA.md`** — 콘텐츠를 만들거나 고치기 전에 반드시 읽는다.
도메인은 **Li2S 양극 all-solid-state Li–S 전지** 연구다 (reference cell 500–600 mAh g⁻¹ →
anode-free).

## 구성

| 경로 | 역할 |
|---|---|
| `SCHEMA.md` | 규칙 원본 (frontmatter, 품질 3축, 단위 규율, digest 4구분, `compare:` 블록, 태그) |
| `CLAUDE.md` / `AGENTS.md` | 에이전트 스키마 (Parity Contract 미러) |
| `raw/papers/` | **논문 digest** (sha256 봉인, 절별 해체분석, `compare:` frontmatter) |
| `raw/figures/<slug>/` | digest 마다 크로핑 그림 + `figures.json` (webapp 이 `Fig. N` 을 자동 링크) |
| `raw/transcripts|articles|repositories/` | 세션 기록·웹 글·저장소 감사 (불변) |
| `concepts|entities|comparisons|queries|guides|questions|syntheses/` | 컴파일된 위키 |
| `inbox/` | ingest 대기 큐 — PDF 를 여기 두고 `/paper` 또는 `/wiki-inbox` |
| `index.md` / `log.md` | 카탈로그 / append-only 로그 |
| `tools/` | `lint.py` `status.py` `new-page.py` + `hooks/` (stdlib) · `extract_figures.py` (PDF 그림 크로핑, pymupdf — 저장소 `.venv` 에 있다) |

## 일상 사용 (WSL, repo root 에서)

```bash
python3 wiki/tools/status.py            # 스냅샷
python3 wiki/tools/lint.py              # 0 errors 확인
python3 wiki/tools/new-page.py concept <slug>
.venv/bin/python wiki/tools/extract_figures.py --slug <slug> --pdf <pdf> --clean
li2s                                    # webapp 열기 (alias — 루트 README)
```

논문 흡수: PDF(+SI)를 `wiki/inbox/` 에 넣거나 대화에 첨부하고 **`/paper`** (논문 에이전트).
세미나 자료: **`/seminar <slug>`**. 논문 비교: **`/compare`** 또는 webapp `/compare`.
세션 마무리: `/wiki-wrap` (lint → log → commit → push).

## 킷 원본과 다른 점

1. **배치**: 별도 저장소가 아니라 repo root `wiki/`. 커맨드는 root `.claude/commands/` 에 `wiki-` 접두 (+ `/paper` `/seminar` `/compare`), hook 은 `wiki/tools/hooks/` + root `.claude/settings.json`.
2. **Cross-vault 참조**: 절대 경로 대신 repo-root 상대 경로 (WSL·서버 clone 경로가 다르다).
3. **논문 digest 가 1급 객체**: `raw/papers/` 의 digest 가 그림·비교표·세미나·chat 의 공통 근거다. 그래서 raw 층에 `compare:` 구조화 필드와 `[인쇄]/[도표]/[해석]/[재현]` 표기 규율을 둔다.
4. **모델 식별자 미기재**: 페이지 frontmatter 에 `model`/`effort` 를 적지 않는다.
5. **CI**: `.github/workflows/wiki-lint.yml` — `wiki/**` 를 건드린 push 만 lint.
