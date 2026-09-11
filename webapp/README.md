# webapp — mid-Ni NCA721 formation 위키 대시보드 (로컬 · 읽기 전용 + 대화 + 셀 요약)

이 저장소의 **위키를 브라우저에서 읽고, 논문을 나란히 놓고, 위키 근거로 대화하고, 셀 요약을 보기 위한** 로컬 Flask 앱이다.
저장소의 어떤 파일도 쓰지 않는다. 선행 브랜치의 열람기 포맷(읽기 전용 guard · CSP · 우리가 만드는 제목 id · 4구분 표기 · 질문 카드 ·
메모/리더/그림 팝업)을 그대로 가져왔고, 이 연구용 화면을 얹었다.

## 화면

| 화면 | 소스 | 내용 |
|---|---|---|
| `/` | `wiki/index.md` · `wiki/log.md` | 카탈로그 + 최근 활동 + 3층 범례 + 열린 질문 |
| `/roadmap` | `config/cells.yaml` + 페이지 계수 | 연구 한 장 — 셀 구성·프로토콜·cut-off 6 수준의 구조(그림)·메커니즘 7 축·측정 흐름·미결 Q1–Q6. **숫자는 config 의 사본** |
| `/papers` `/paper/<slug>` | `wiki/papers/*.md` + `wiki/raw/papers/*.md` + `wiki/raw/figures/<slug>/` | 논문 = 노트(`paper:` 스키마 표, 내 DOE 겹침 칩) + digest 전문(4구분 표기, `Fig. N` 자동 링크, 메모·리더) |
| `/compare` | 노트의 `paper:` + 프로젝트 카드의 `ours:` | 비교표 — 양극(원문 표기)·공정·loading·전해질·음극·전압창(원문 기준 / vs. Li/Li⁺+offset)·formation·cut-off·main cycle(제작/구동압)·성능·기법·메커니즘 주장. **상한 전압/cut-off 정렬**, **내 DOE 겹침 거르기** |
| `/mechanisms` `/protocols` `/experiments` `/concepts` `/entities` + 문서 | `wiki/<dir>/*.md` | 목록 카드(미검증 배경 표시) + 문서 (callout·목차·배지) |
| `/questions` `/question/<slug>` | `wiki/questions/*.md` | 질문 카드 — Evidence For/Against 좌우 맞세움, Status Log 타임라인 |
| `/cells` `/cell/<id>` `/api/cells.json` | `data/registry/cells.csv` + `data/cells/<id>/` | cut-off 별 n · 방전 비용량 vs 사이클(색 = config) · registry 표 · 셀별 사이클 표(전압 raw → vs. Li/Li⁺) |
| `/chat` `/api/chat` `/api/md` | 위키 절 + `ours:` + 셀 요약 | 위키 근거 대화 (SSE). 출처 필수 · `[DB 외 일반 지식/추론]` · 비교 시 다섯 차이 · IPA. 서버는 저장하지 않는다 |
| `/notes` · `/search` · `/api/palette.json` · `/api/figures/<slug>.json` · `/api/file/<slug>/<file>` | | 메모 모아보기(브라우저) · 부분 문자열 검색 · 팔레트(⌘K) · 그림 색인 · 그림 파일(`wiki/raw/figures/` 밖은 404) |

## 실행

```bash
webapp/midni.sh              # 권장 (alias midni) — venv·의존성·빈 포트를 알아서 잡고 브라우저를 연다
webapp/midni.sh stop
# 직접:
.venv/bin/python webapp/app.py   # http://127.0.0.1:5100  (WEBAPP_HOST / WEBAPP_PORT 로 바꾼다)
```

- 바인딩 기본값은 **127.0.0.1** (인증이 없다). `midni share` 만 0.0.0.0 으로 연다 — 사내망 한정, 공개망 금지. WSL 은 Windows 포트프록시가 한 겹 더 (`wiki/guides/wsl-midni-setup.md`).
- 서버는 요청마다 파일을 다시 읽는다. 위키·registry·config 를 고치면 **새로고침만으로** 반영된다.
- `/chat`: `ANTHROPIC_API_KEY` 가 서버 프로세스 환경에 있어야 켜진다. 모델은 `MIDNI_CHAT_MODEL` (기본값은 `chat.py` 의 한 줄 —
  저장소에서 모델 문자열이 있는 유일한 자리), effort `MIDNI_CHAT_EFFORT`, 오프라인 점검 `MIDNI_CHAT_FAKE=1`.

## 왜 읽기 전용인가

`wiki/raw/` 는 sha256 으로 봉인된 불변층이고, `data/registry/cells.csv` 와 `config/cells.yaml` 은 사람이 고치는 정본이다. 웹에서 쓸 수 있으면
그 규율이 무의미해진다. 구현은 세 겹: 쓰기 라우트가 없다 · `before_request` 의 `_guard_mutation` 이 GET/HEAD/OPTIONS 외를 405 로 막는다
(`/api/chat` `/api/md` 만 예외, 둘 다 파일을 쓰지 않는다) · 파일 서빙은 `content.safe_file` 하나만 통과한다 (허용 뿌리 + resolve + is_relative_to).

## 파일

```
webapp/
  midni.sh              한 줄 실행 런처 (git 갱신 → venv → 빈 포트 → 기동 · paper/cells/lint/smoke/test 부명령)
  app.py                라우트 + 읽기 전용 guard + 보안 헤더
  content.py            등록부 · frontmatter · 마크다운/wikilink/callout 렌더 · 4구분 표기 · 그림 색인 · paper: 평탄화 + DOE 겹침 · 검색 · chat 근거
  chat.py               /chat 서버 쪽 (시스템 프롬프트 = 절대 규칙 + 대화 규칙, SSE)
  cells.py              /cells 화면 (registry + 요약 + SVG 차트 기하)
  smoke.py              라우트 전수 점검 (서버 없이) — CI 게이트
  requirements.txt      Flask · markdown · PyYAML · pandas · anthropic (메이저 상한)
  templates/            base(사이드바·스프라이트·팔레트) + 화면 16종 + _macros(배지·태그·sources·목차·범례·DOE 칩·카드)
  static/css/style.css  선행 브랜치 토큰 두 벌(라이트/다크) + 이 저장소 추가(비교표·대화·callout·셀·칩)
  static/js/            boot(테마) · app(팔레트·스크롤스파이·메모) · reader(전체화면) · figref(그림 팝업) · notes(메모 모아보기) · chat(SSE) · compare(정렬·거르기)
```

## 검증

```bash
python3 webapp/smoke.py                          # 라우트·그림·정적자산·게이트·경로탈출·헤더·XSS·비교표·셀·절대 규칙(NCM721 없음)
.venv/bin/python -m unittest discover -s tests   # 셀 모듈 + content 순수 함수
```
