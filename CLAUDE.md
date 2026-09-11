# CLAUDE.md — Yonghoon-DEM-DFT · mid-Ni NCA721 formation 연구 mothership (작업 브랜치 `claude/midni-formation-wiki`)

이 저장소를 여는 모든 에이전트가 먼저 읽는 상시 규칙. 위키 규칙의 원본은 `wiki/SCHEMA.md`, webapp 은 `webapp/README.md`,
브랜치 지도는 `BRANCHES.md`. **맨 아래 [절대 규칙] 은 어떤 작업에서도 어길 수 없다.**

## 연구 (한 줄)

sulfide 기반 all-solid-state battery(ASSB) 에서 mid-Ni 양극재 **NCA721** 의 formation(pre-conditioning) 프로토콜 최적화 —
"4.4 V 고전압 구동을 위한 Mid-/High-Ni 양극재 열화 메커니즘 규명 및 해당 메커니즘 기반 pre-conditioning 사이클 설계".
핵심 질문: **formation 충전 cut-off 전압(3.6–4.6 V vs. Li/Li⁺)이 장기 사이클 성능과 열화 메커니즘(CEI 형성, LPSCl 산화 분해,
lattice oxygen 관여, 계면 contact loss 등)에 어떤 영향을 주는가.** 사용자 진술 원문은
`wiki/raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md` (봉인).

## 저장소 지도

| 경로 | 무엇 |
|---|---|
| `wiki/` | **mothership LLM Wiki** — `papers/`(논문 노트, `paper:` 추출 스키마) · `mechanisms/` · `protocols/` · `experiments/` · `comparisons/` · `concepts/` · `entities/` · `questions/` · `guides/` · `raw/`(digest·그림·세션 기록, 불변) (`wiki/README.md`, 규칙 `wiki/SCHEMA.md`) |
| `webapp/` | 로컬 Flask 대시보드 — 위키 열람 · 논문 비교표(내 DOE 겹침) · 열화 메커니즘/프로토콜/실험 · 위키 근거 대화(`/chat`) · 셀 데이터(`/cells`). WSL 에서 `midni` 한 단어 (`webapp/midni.sh`) |
| `config/cells.yaml` | **정본 상수**: 전압 offset(+0.62 V), DOE 창, 셀 제작 조건, cut-off 별 그래프 색, CSV 열 정의 — 사용자가 직접 고친다 |
| `data/registry/cells.csv` | **cell registry — 셀 메타데이터의 source of truth** (파일명 파싱은 제안값일 뿐) |
| `data/raw/` (gitignore) · `data/cells/<id>/` | raw 충방전 CSV (커밋 안 함) · import 산출물 (`cycles.csv`, `summary.json`) |
| `tools/cells/` · `tests/` | 셀 데이터 모듈 (`cellio.py`, `import_cell.py`) · 단위 테스트 |
| `scripts/` | `setup-wsl.sh`(venv·의존성·alias) · `install-alias.sh` |
| `.claude/` | 커맨드(`/paper` `/compare` `/cells` `/wiki-*`), 논문 에이전트(`agents/paper-curator.md`), hook(raw 보호·편집 후 lint) |
| 다른 브랜치들 | DEM/MPM · 열화 degeneracy · Li2S 위키 · argyrodite ML 등 **별개 프로젝트** — merge 하지 않는다 (`BRANCHES.md`) |

## 하드 룰

1. **브랜치**: 이 연구의 작업 브랜치는 **`claude/midni-formation-wiki`** 이다 (2026-09-11 사용자 지시 "main 말고, 단독 브랜치에").
   세션 하네스가 다른 이름을 지정하면 하네스가 우선이고 이 줄을 같이 고친다. 브랜치 이름의 정본은 **이 줄 하나** — `wiki/`·
   `.claude/`·스크립트는 이름을 옮겨 적지 않고 여기를 참조한다 (`wiki/tools/lint.py` 의 `no-hardcoded-branch-name` 검사).
   다른 계열 브랜치를 이 브랜치로 merge 하지 않고, 이 브랜치를 `main` 에 올리는 것도 사용자 승인 후에만.
2. **비밀정보**: 토큰·API 키를 대화나 파일에 넣지 않는다. `/chat` 의 `ANTHROPIC_API_KEY` 는 셸 환경변수로만.
3. **raw 불변**: `wiki/raw/` 는 sha256 봉인. 기존 raw 파일은 수정하지 않는다 (hook 이 막는다). 정정은 2층(논문 노트 등)에 적는다.
   새 raw 는 `wiki/tools/seal.py` 로 봉인한다.
4. **정본**: 실험 수치의 정본은 **`data/raw/` 원 데이터·실험 노트와 `data/registry/cells.csv`**. 위키·webapp·대화에 적힌 우리 수치는
   사본이며 인용 근거가 아니다. 논문 수치의 정본은 digest 의 `[인쇄]` 항목 → 원문. 상수(offset·DOE·셀 조건)의 정본은 `config/cells.yaml`.
5. **논문은 두 파일**: `wiki/raw/papers/<slug>.md` digest(봉인) + `wiki/papers/<slug>.md` 노트(`paper:` 스키마 — 값이 없으면 null,
   추측 금지; DOI 가 중복 제거 키; Supplementary 는 본문 노트에 연결). 근거 논문 없는 배경 지식은 `> [!note] 미검증 배경` +
   `confidence: low` + `evidenceScope: synthesis-only` 이며 인용 근거가 아니다.
6. **모델 식별자 금지**: 위키 페이지·코드·커밋 본문에 넣지 않는다. 예외는 둘 — (a) 세션 하네스가 자동으로 붙이는 `Co-Authored-By`
   트레일러, (b) API 호출에 쓰는 모델 문자열 **`webapp/chat.py` 의 `MIDNI_CHAT_MODEL` env 기본값 한 줄** (그 문서화인 `webapp/README.md` 포함).
   그 밖의 자리는 `wiki/tools/lint.py` 의 `no-model-identifier` 검사가 막는다.
7. **LLM 컨텍스트에 raw CSV 를 통째로 넣지 않는다.** `/chat` 과 `/cells` 해석은 pandas 요약(`summary.json`)만 쓴다.

## 작업 규율

- **검증 없는 완료 선언 금지** — "됐다" 는 **방금 실행한 출력**으로만. 이 저장소의 증명 명령: `python3 wiki/tools/lint.py` (0 errors) ·
  `python3 webapp/smoke.py` (라우트 전수 점검) · `.venv/bin/python -m unittest discover -s tests` · `webapp/midni.sh status`. 논문 에이전트는
  그림을 **실제로 Read** 한 뒤 쓴다.
- **논문은 `/paper` 로.** DOI 중복 확인 → digest + 노트 + 그림 → 메커니즘 페이지·질문 카드 라우팅. 액체계·저압·저로딩 논문은
  "우리 조건에 옮길 수 없는 것" 을 반드시 적는다.
- **비교할 때는 다섯 차이부터**: 전압 기준전극(offset) · 양극 조성(원문 표기) · 온도 · 압력(제작압/구동압) · loading.
- **질문 카드가 축이다.** 새 자료가 들어오면 `wiki/questions/` 의 열린 카드에 어느 가설(H1…)의 근거인지 적는다.
- **대화 규칙**(`/chat`·`/wiki-query`): 모든 주장에 출처(1저자·연도·저널·figure/page), DB 에 없는 것은 `[DB 외 일반 지식/추론]`,
  한국어 + 영어 용어 유지, 영어 용어 설명 시 IPA·강세 병기 (`wiki/guides/chat-citation-rules.md`).
- **컨텍스트**: 큰 파일은 `offset/limit` 로, 위치는 Grep 으로. digest 는 3만 자 안팎이 될 것이다 — 한 번에 읽지 말 것.

## 커맨드

| 커맨드 | 용도 |
|---|---|
| `/paper [pdf…]` | 논문 에이전트 — DOI 중복 확인·digest·노트(`paper:`)·그림·근거 라우팅·설명 |
| `/compare [축]` | 노트들의 `paper:` 대조 (내 DOE 겹침), file-back |
| `/cells [대상]` | raw 파일명 제안 → registry(사람이 확정) → import → 요약 통계로 해석 |
| `/wiki-ingest` `/wiki-inbox` `/wiki-query` `/wiki-verify` `/wiki-lint` `/wiki-status` `/wiki-wrap` | LLM Wiki 운영 7종 (`wiki/README.md`) |

## 일상 (WSL)

```bash
bash scripts/setup-wsl.sh        # 한 번 — venv·의존성·alias midni
midni                            # 대시보드 (브라우저가 열린다)
midni paper ~/Downloads/x.pdf    # inbox 로 → Claude Code 에서 /paper
midni cells propose data/raw/x.csv && midni cells import <cell_id>
python3 wiki/tools/lint.py       # 0 errors
```

## [절대 규칙]

- 내 실험 데이터의 양극재는 전부 **NCA721** 이다. NCM721 로 바꿔 부르거나 그렇게 해석하지 말 것. 논문 속 양극 조성도 원문 표기
  (NCM622, NCM85 등) 그대로 두고 NCA↔NCM 간 임의 변환 금지. (lint `no-ncm721`)
- 전압에는 항상 기준전극을 표기할 것. 변환식: **vs. Li/Li⁺ = vs. In/Li-In + 0.62 V** (방향 혼동 금지). 상수의 정본은
  `config/cells.yaml` `voltage.in_to_li_offset_v`. (lint `canonical-offset` · `voltage-reference`)
- 비용량(mAh g⁻¹)과 면적용량(mAh cm⁻²)을 혼동하지 말 것. 절대용량(mAh)으로 보고하지 말 것. (lint `unit-rule`)
- 충전 = delithiation, 방전 = lithiation. 용어 혼동 금지.
