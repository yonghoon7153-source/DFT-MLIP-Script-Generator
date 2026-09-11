# Yonghoon-DEM-DFT — Li2S ASSB 연구 위키 + 대시보드 (브랜치 `claude/li2s-assb-wiki`)

pristine Li2S 양극 all-solid-state Li–S 전지 연구(reference cell 500–600 mAh g⁻¹ → anode-free)의
**mothership LLM Wiki** 와, 그 위키를 읽고 논문을 비교하고 대화하는 **로컬 대시보드**.
논문은 `/paper` 논문 에이전트가 sha256 봉인 digest 로 흡수한다.

> 다른 브랜치(DEM/MPM · 열화 degeneracy · argyrodite ML …)는 별개 프로젝트다 — `BRANCHES.md`.

## 3분 시작 (WSL / Ubuntu)

```bash
git clone <이 저장소> ~/Yonghoon-DEM-DFT && cd ~/Yonghoon-DEM-DFT
git checkout claude/li2s-assb-wiki     # 작업 브랜치 (정본: CLAUDE.md 하드룰 1)
bash scripts/setup-wsl.sh        # .venv + 의존성 + alias li2s   (한 번)
source ~/.bashrc
li2s                             # 서버를 띄우고 브라우저를 연다 → http://127.0.0.1:51xx
```

| 명령 | 뜻 |
|---|---|
| `li2s` | 서버 기동(백그라운드) + 브라우저. 이미 떠 있으면 열기만 |
| `li2s open` · `status` · `stop` · `restart` · `update` · `log` | 보통의 것들 |
| `li2s share` | 같은 망의 다른 PC 에서 보게 (0.0.0.0, 인증 없음 — 공개망 금지; WSL 은 포트프록시 필요) |
| `li2s paper <pdf> [<si>…]` | PDF 를 `wiki/inbox/` 로 → Claude Code 에서 `/paper` |
| `li2s lint` · `li2s wiki` | 위키 lint / 상태 |

`/chat`(위키 근거 대화)을 켜려면 서버를 띄우는 셸에 `export ANTHROPIC_API_KEY=…` 가 있어야 한다.
키는 파일·저장소에 두지 않는다. 자세한 절차는 `wiki/guides/wsl-li2s-setup.md`.

## 무엇이 있나

| 경로 | 역할 |
|---|---|
| `wiki/` | 위키 — `raw/`(digest·그림·세션 기록, 불변) · `concepts/ entities/ questions/ comparisons/ queries/ guides/` (컴파일) · `index.md` `log.md` · `tools/`(lint·status·new-page·extract_figures) |
| `webapp/` | Flask 대시보드: 홈 · 연구 로드맵 · 논문 digest(그림 팝업·메모) · **논문 비교표**(`compare:`) · 열린 질문(찬반 맞세움) · 개념 · 프로젝트 · **위키와 대화** · 검색. 읽기 전용 (`/api/chat` `/api/md` 만 POST, 둘 다 파일을 쓰지 않는다) |
| `.claude/` | `/paper` `/seminar` `/compare` `/wiki-*` 커맨드, 논문 에이전트, hook |
| `scripts/` | WSL 세팅·alias |

## 논문 워크플로

1. PDF(+SI)를 `wiki/inbox/` 에 넣는다 (`li2s paper …`) 또는 대화에 첨부.
2. Claude Code 에서 **`/paper`** → `wiki/raw/papers/<slug>.md` (절별 해체, 공백표, `[인쇄]/[도표]/[해석]/[재현]`,
   `compare:` frontmatter) + `wiki/raw/figures/<slug>/` (크로핑 PNG) + 개념·질문 카드 갱신 + lint 0 errors.
3. 대시보드 `/papers` → digest 읽기 (Fig. N 에 마우스를 올리면 그림), `/compare` → 논문 나란히,
   `/chat` → 위키 근거로 토론.
4. 세미나 논문이면 **`/seminar <slug>`** → `wiki/queries/<slug>-seminar-prep.md`.

첫 논문: Kim et al. 2023 *Carbon Energy* 5, e308 (Li2S/Gr/CNT compact 양극) — digest, 그림 19장,
세미나 준비 페이지가 들어 있다.

## 규칙 (요약 — 정본은 `CLAUDE.md` · `wiki/SCHEMA.md`)

- `wiki/raw/` 는 고치지 않는다. 정정은 2층 페이지에.
- 실험 수치의 정본은 실험 노트. 위키의 우리 수치는 사본.
- 비용량 단위 `(S)`/`(Li2S)`/`(composite)`, 전압 기준 `vs Li/Li⁺`/`vs Li–In` 항상 명시.
- 커밋 prefix: `ingest(wiki):` `update(wiki):` `create(wiki):` `lint(wiki):` `verify(wiki):` `webapp:`.
