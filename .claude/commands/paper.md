---
description: 논문 에이전트 — PDF(+SI)를 DOI 로 중복 확인하고 봉인 digest + paper: 노트 + 그림으로 위키에 흡수, 메커니즘·질문 카드에 근거 라우팅
---

논문 에이전트(`.claude/agents/paper-curator.md`)를 실행한다. 대상: $ARGUMENTS
(비우면 `wiki/inbox/` 의 PDF/.docx 전부 — 먼저 목록을 보이고 어느 것을 할지, Supplementary 는 어느 본문에 붙는지 **한 번에** 묻는다.)

절차는 에이전트 파일의 Procedure 0–8 을 그대로 따른다. 요약:

0. **DOI 중복 확인** — 있으면 새로 만들지 않고 기존 노트를 갱신한다. SI 는 본문 노트에 연결.
1. **Read** — pymupdf 텍스트 덤프(스크래치패드). 인용은 거기서 복사.
2. **Extract** — `wiki/SCHEMA.md` 의 `paper:` 스키마 그대로 (값 없으면 null): 서지 · 양극(원문 표기, 결정, 코팅, 공정, loading,
   조성비) · 전해질 · 음극 · 전압(원문 값+기준 / 변환값+offset) · formation · main cycle(제작압/구동압) · 성능 · 기법 ·
   메커니즘 주장(근거 figure/page 필수).
3. **Crop + LOOK** — `extract_figures.py --slug <slug> --pdf … --clean`; SI 그림은 `fig_S<n>.png`; 핵심 그림을 Read 한 뒤 쓴다.
4. **Digest** — `wiki/raw/papers/<slug>.md` (공백표 G1…, 절별 해체, 4구분 표기, 우리 접점 표) → `wiki/tools/seal.py` 봉인.
5. **Note** — `new-page.py paper-note <slug>` → `paper:` 채우기 → 본문(요약·주장/근거 표·접점·DOE 관계·비판).
6. **Compile** — 메커니즘 페이지 sources/근거 상태, 질문 카드 Evidence(가설 번호), 비교 페이지 상태, index/log,
   `python3 wiki/tools/lint.py` 0 errors, `python3 webapp/smoke.py` 0 failures.
7. **Explain** — 질문과 답 · 수치(단위·기준·분모) · 그림별 · 방법 · **우리 DOE 와의 다섯 차이** · 다음 실험 · 본/안 본 그림.
8. **Commit** `ingest(wiki): …` → push (루트 CLAUDE.md 하드룰 1 브랜치). PR 없음. inbox 원본 삭제.

금지: raw 수정, 모델 식별자 기재, 기준전극 없는 전압, NCA↔NCM 변환, 추측으로 채운 `paper:` 값, 검증 없는 "끝났다".
