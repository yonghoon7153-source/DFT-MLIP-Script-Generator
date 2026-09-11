# webapp — Li2S ASSB 위키 대시보드 (로컬 · 읽기 전용 + 위키 근거 대화)

`wiki/` 를 브라우저에서 읽고, 논문을 나란히 비교하고, 위키 절을 근거로 Claude 와 대화하는 로컬
Flask 앱. **저장소에는 아무것도 쓰지 않는다.** 선행 브랜치(열화 degeneracy 위키 열람기)의 포맷을
이식했고, 이 연구용으로 `/roadmap` `/compare` `/chat` 을 더했다.

## 화면

| 화면 | 소스 | 내용 |
|---|---|---|
| `/` | `wiki/index.md` · `log.md` | 카탈로그 + 열린 질문 + 최근 활동 + "색이 뜻하는 것" |
| `/roadmap` | 킥오프 기록(사본) + 페이지 실물 계수 | 연구 개요 한 장: 30:50:20 삼상 퍼콜레이션 도해 · 병목 후보 H1–H4 · reference cell → anode-free 흐름 · 미결 Q1–Q4 |
| `/papers` · `/paper/<slug>` | `wiki/raw/papers/*.md` + `raw/figures/<slug>/` | digest 카드 / 전문. `Fig. N`·`Fig. Sn`·`Table N` 자동 링크(팝업·라이트박스), `[인쇄]/[도표]/[해석]/[재현]` 색 구분, `compare:` 접이, 목차 스크롤스파이, 하이라이트·메모(브라우저), 전체화면 리더(`F`) |
| `/compare` | 모든 페이지의 frontmatter `compare:` | 논문 비교표 — 첫 행은 우리 자신(entity). 빈 칸 = 논문이 안 준 값. 거르기 입력 |
| `/questions` · `/question/<slug>` | `wiki/questions/` | Evidence For ↔ Against 좌우 맞세움, Status Log 타임라인 |
| `/concepts` `/entities` `/doc/<kind>/<slug>` | 나머지 위키 | 개념 · 프로젝트 · 가이드 · 질의 · 비교 · 세션 기록 |
| `/chat` | 위키 전체 → `content.chat_context` | 질문 → 관련 절을 골라(인용 좌표 포함) Claude 에게 → SSE 로 답. 오른쪽 레일에 근거 페이지·토큰 사용. 기록은 localStorage |
| `/notes` | (서버는 모른다) | 브라우저에 흩어진 메모·하이라이트 모아보기 |
| `/search?q=` | 위키 전부 | 부분 문자열 전문 검색 |
| `/api/palette.json` `/api/figures/<slug>.json` `/api/file/<slug>/<file>` `/api/chat/status` | — | 팔레트(⌘K) · 그림 색인 · 그림 파일(`wiki/raw/figures/` 밖은 404) · chat 상태 |
| `POST /api/chat` `POST /api/md` | — | **허용된 유일한 쓰기 메서드** — 둘 다 파일을 쓰지 않는다 (chat 스트림 / 마크다운 렌더) |

## 실행

```bash
webapp/li2s.sh            # 권장 (alias: li2s) — venv·의존성·빈 포트·브라우저까지
webapp/li2s.sh fg         # 포그라운드 (로그 바로 보기)
python3 webapp/app.py     # 직접 — http://127.0.0.1:5100
```

환경변수: `WEBAPP_HOST`(기본 127.0.0.1) `WEBAPP_PORT`(5100) · chat: `ANTHROPIC_API_KEY`(필수),
`LI2S_CHAT_MODEL`(기본 `claude-opus-5`), `LI2S_CHAT_EFFORT`(high), `LI2S_CHAT_MAX_TOKENS`(8000),
`LI2S_CHAT_FALLBACKS`(1 — 서버측 refusal fallback), `LI2S_CHAT_FAKE`(1 이면 API 없이 근거 선택만 점검).

## 설계 — 무엇을 지켰나

- **읽기 전용 guard**: `before_request` 가 GET/HEAD/OPTIONS 외 메서드를 405 로 막는다. 예외는
  `/api/chat` `/api/md` 두 경로뿐이고 둘 다 저장소를 건드리지 않는다. 새 POST 를 붙이려면 이 목록을
  지나야 한다 (fail-closed).
- **CSP `default-src 'self'`**: CDN·웹폰트·인라인 스크립트 없음. 폰트는 `static/fonts/` (Pretendard 부분집합 +
  JetBrains Mono, OFL — `fonts/LICENSE.md`). 아이콘은 인라인 SVG 스프라이트. 브라우저는 이 서버와만
  말하고, Anthropic API 호출은 서버(`chat.py`)에서만 일어난다.
- **마크다운 2중 방어**: raw HTML 파서 끔 + `href/src` scheme 재검사. chat 답변도 `/api/md` 로 같은
  렌더러를 지난다 (모델 텍스트를 innerHTML 에 직접 넣지 않는다).
- **제목 id 는 우리가 만든다** (`h-1`, `h-2`…): 문서 내용이 id 가 되지 않는다. chat 의 인용 앵커도 같은
  규칙으로 원문 `##/###` 순서를 세어 만든다 (`content._heading_anchor_map`).
- **그림 키 정규화**: `figures.json` 의 `key` 대신 종류 첫 글자 + 라벨 대문자 (`figref.js` 와 동일).
- **숫자를 만들지 않는다**: `/roadmap` 의 조성·목표는 킥오프 기록 사본, 페이지 수만 실물을 센다.
  `/compare` 의 빈 칸은 빈 칸이다.

## chat 의 근거 선택 (`content.chat_context`)

임베딩 없는 최소형이다: 질문 토큰(2자 이상)의 출현 빈도로 페이지 → 절을 고르고, 항상 `index.md`
요약을 앞에 둔다. 절마다 `page / section / url / meta(confidence…)` 를 붙여 시스템 프롬프트의
`<wiki>` 블록에 넣는다. 시스템 프롬프트의 고정 부분에는 `cache_control` 을 둔다. 위키가 수백 페이지가
되면 이 함수 하나만 바꾸면 된다 — `app.py`/`chat.py` 는 결과 형태만 본다.

## 파일

```
webapp/
  li2s.sh              한 단어 런처 (start/open/status/stop/restart/update/share/fg/log/paper/lint/wiki)
  app.py               라우트 + 읽기 전용 guard + 보안 헤더 + chat SSE
  chat.py              위키 근거 대화 (Anthropic SDK, 스트리밍, refusal fallback, FAKE 모드)
  content.py           frontmatter · 마크다운/wikilink · 4구분 표기 · 목차 · 그림 색인 · compare 표 · 검색 · chat 근거 선택
  requirements.txt     Flask · markdown · PyYAML · anthropic (메이저 상한)
  templates/           base(사이드바·스프라이트·팔레트) + 화면 + _macros(배지·태그·sources·목차·4구분 범례)
  static/css/style.css 토큰 두 벌(라이트/다크) + 이 저장소 추가분(비교표·chat·[재현])
  static/js/           boot(테마) · app(팔레트·스크롤스파이·메모) · reader(전체화면) · figref(그림) · notes · chat · compare
  static/fonts/        Pretendard 부분집합 · JetBrains Mono (OFL)
```

## 한계

- 검색·chat 근거 선택 모두 부분 문자열/토큰 빈도다. 뜻으로 찾는 것은 chat 의 모델이 한다.
- chat 답은 **사본**이다 — 인용 링크로 위키 절에 내려가 확인한다. 위키에 없는 것은 없다고 말하도록
  시스템 프롬프트가 지시하지만, 보장은 아니다.
- 그림은 `wiki/raw/figures/<slug>/` 에 있는 것만. SI 그림 캡션은 `figures.json` 이 정본.
