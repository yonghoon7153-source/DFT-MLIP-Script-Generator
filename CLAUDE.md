# CLAUDE.md — Yonghoon-DEM-DFT `main` · Li2S ASSB 연구 mothership

이 저장소를 여는 모든 에이전트가 먼저 읽는 상시 규칙. 위키 규칙의 원본은 `wiki/SCHEMA.md`,
webapp 은 `webapp/README.md`, 브랜치 지도는 `BRANCHES.md`.

## 저장소 지도

| 경로 | 무엇 |
|---|---|
| `wiki/` | **mothership LLM Wiki** — Li2S 양극 all-solid-state Li–S 연구의 논문 digest·개념·열린 질문·프로젝트 상태·세미나 자료 (`wiki/README.md`, 규칙 `wiki/SCHEMA.md`) |
| `wiki/raw/papers/` + `wiki/raw/figures/` | 논문 digest(sha256 봉인) + 크로핑 그림 — `/paper` 논문 에이전트가 만든다 |
| `webapp/` | 로컬 Flask 대시보드 — 위키 열람 + 논문 비교표 + 위키 근거 대화. WSL 에서 `li2s` 한 단어 (`webapp/li2s.sh`) |
| `scripts/` | `setup-wsl.sh`(venv·의존성·alias) · `install-alias.sh` |
| `.claude/` | 커맨드(`/paper` `/seminar` `/compare` `/wiki-*`), 논문 에이전트(`agents/paper-curator.md`), hook(raw 보호·편집 후 lint) |
| 다른 브랜치들 | DEM/MPM·열화 degeneracy·argyrodite ML 등 **별개 프로젝트** — merge 하지 않는다 (`BRANCHES.md`) |

## 하드 룰

1. **브랜치**: 이 연구의 작업 브랜치는 **`main`** 이다. 세션 하네스가 다른 이름을 지정하면 하네스가
   우선이고 이 줄을 같이 고친다. 브랜치 이름의 정본은 **이 줄 하나** — `wiki/`·`.claude/`·스크립트는
   이름을 옮겨 적지 않고 여기를 참조한다 (`wiki/tools/lint.py` 의 `no-hardcoded-branch-name` 검사).
   다른 계열 브랜치를 `main` 으로 merge 하지 않는다.
2. **비밀정보**: 토큰·API 키를 대화나 파일에 넣지 않는다. `/chat` 의 `ANTHROPIC_API_KEY` 는 셸 환경변수로만.
3. **raw 불변**: `wiki/raw/` 는 sha256 봉인. 기존 raw 파일은 수정하지 않는다 (hook 이 막는다). 정정은
   컴파일 페이지(2층)에 적는다.
4. **정본**: 실험 수치의 정본은 **실험 노트·원 데이터**. 위키·webapp·대화에 적힌 우리 수치는 사본이며
   인용 근거가 아니다. 논문 수치의 정본은 digest 의 `[인쇄]` 항목 → 원문.
5. **단위**: 비용량은 `mAh g⁻¹(S)` / `(Li2S)` / `(composite)`, 전압은 `vs Li/Li⁺` / `vs Li–In` 을 항상 적는다.
6. **모델 식별자 금지**: 위키 페이지·코드·커밋 본문에 넣지 않는다 (세션 하네스가 자동으로 붙이는 `Co-Authored-By` 트레일러는 예외).

## 작업 규율

- **검증 없는 완료 선언 금지** — "됐다" 는 **방금 실행한 출력**으로만. 이 저장소의 증명 명령:
  `python3 wiki/tools/lint.py` (0 errors) · `webapp/li2s.sh status` / `curl` 라우트 점검 · 논문 에이전트는
  그림을 **실제로 Read** 한 뒤 쓴다.
- **논문은 `/paper` 로.** 요약 한 장이 아니라 절별 전문 digest + 공백표 + `compare:` + 그림. 액체계 논문은
  "고체계에 옮길 수 없는 것" 을 반드시 적는다.
- **질문 카드가 축이다.** 새 자료가 들어오면 `wiki/questions/` 의 열린 카드에 어느 가설의 근거인지 적는다.
- **컨텍스트**: 큰 파일은 `offset/limit` 로, 위치는 Grep 으로. digest 는 6만 자가 넘는다.

## 커맨드

| 커맨드 | 용도 |
|---|---|
| `/paper [pdf…]` | 논문 에이전트 — digest·그림·compare·질문 카드 라우팅·설명 |
| `/seminar <slug> [--pptx]` | digest → 세미나 준비 페이지 (스토리라인·슬라이드·양단위 숫자표·예상 질문) |
| `/compare [축]` | digest 들의 `compare:` 대조, file-back |
| `/wiki-ingest` `/wiki-inbox` `/wiki-query` `/wiki-verify` `/wiki-lint` `/wiki-status` `/wiki-wrap` | LLM Wiki 운영 7종 (`wiki/README.md`) |

## 일상 (WSL)

```bash
bash scripts/setup-wsl.sh     # 한 번
li2s                          # 대시보드 (브라우저가 열린다)
li2s paper ~/Downloads/x.pdf  # inbox 로 → Claude Code 에서 /paper
python3 wiki/tools/lint.py    # 0 errors
```
