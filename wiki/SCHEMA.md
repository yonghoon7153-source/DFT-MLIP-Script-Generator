# Wiki Schema

## Domain
Yonghoon-DEM-DFT 저장소의 mothership LLM Wiki (작업 브랜치는 루트 `CLAUDE.md` 하드룰 1).
**sulfide 기반 all-solid-state battery(ASSB) 에서 mid-Ni 양극재 NCA721 의 formation(pre-conditioning)
프로토콜 최적화** 연구 — 논문 main concept은 "4.4 V 고전압 구동을 위한 Mid-/High-Ni 양극재 열화 메커니즘
규명 및 해당 메커니즘 기반 pre-conditioning 사이클 설계". 핵심 질문은 **formation 충전 cut-off 전압이
장기 사이클 성능과 열화 메커니즘(CEI 형성, LPSCl 산화 분해, lattice oxygen 관여, 계면 contact loss 등)에
어떤 영향을 주는가**다. 이 위키는 그 연구를 위한 **논문 노트·열화 메커니즘·프로토콜·실험(DOE·cell registry)·
논문 간 비교**를 등록·연결·재사용한다. 실험 데이터(충방전 CSV)는 위키 밖 `data/` 에 두고 요약만 참조한다.

## Conventions
- File names: lowercase, hyphens, no spaces.
- Raw source files live under `raw/` and are treated as immutable.
- Wiki pages live under `papers/`, `mechanisms/`, `protocols/`, `experiments/`, `comparisons/`,
  `concepts/`, `entities/`, `queries/`, `guides/`, `questions/`, `syntheses/`.
- Every wiki page starts with YAML frontmatter (below).
- Use `[[wikilinks]]` for internal links; each page should target at least 2 related pages.
- Every new page must be listed in `index.md`. Every meaningful action goes to `log.md`.
- When updating a page, bump `updated`.
- 새 페이지는 `python3 wiki/tools/new-page.py <type> <slug>` 스캐폴더로 만든다.
- Lint: `python3 wiki/tools/lint.py` (repo root 기준) · Status: `python3 wiki/tools/status.py`
- Claude Code 커맨드 (repo root `.claude/commands/`): /wiki-ingest /wiki-inbox /wiki-query /wiki-verify
  /wiki-lint /wiki-status /wiki-wrap · 논문 전용: /paper (논문 에이전트) /compare (논문 비교) · 셀 데이터: /cells

## 이 저장소 특칙

### 절대 규칙 (루트 `CLAUDE.md` 맨 아래 [절대 규칙] 과 동일 — 위키 페이지·webapp·대화 모두에 적용)
1. **양극재 이름**: 우리 실험 데이터의 양극재는 전부 **NCA721** 이다. NCM721 로 바꿔 부르거나 그렇게
   해석하는 것은 금지 (lint `no-ncm721` — 금지 문장 자체만 예외). 논문 속 양극 조성도 원문 표기
   (NCM622, NCM85, NCA, LCO …) 그대로 두고 **NCA↔NCM 간 임의 변환 금지**.
2. **전압 기준전극**: 전압에는 항상 기준전극을 표기한다. 변환식은
   **vs. Li/Li⁺ = vs. In/Li-In + 0.62 V** (방향 혼동 금지). 상수의 정본은 `config/cells.yaml` 의
   `voltage.in_to_li_offset_v` 하나이고, 위키·webapp 에 적힌 값은 lint `canonical-offset` 이 대조한다.
   논문 값은 **원문 값 + 원문 기준전극을 그대로** 적고, 변환값은 사용한 offset 과 함께 **별도 필드**에 적는다.
3. **용량 단위**: 비용량(mAh g⁻¹)과 면적용량(mAh cm⁻²)을 혼동하지 않는다. 절대용량(mAh)으로 보고하지
   않는다 (lint `unit-rule` 경고). 우리 데이터의 용량은 항상 비용량(mAh g⁻¹).
4. **용어**: 충전 = delithiation, 방전 = lithiation. 용어 혼동 금지.

### 층 구조 — 논문은 두 파일이다
- **`raw/papers/<slug>.md` = digest** (1층, sha256 봉인). 논문을 절별로 해체한 전문 기록. 표기 4구분
  `[인쇄]`(원문 글자) / `[도표]`(그림 판독 근사값) / `[해석]`(우리 판단) / `[재현]`(원문 값의 산술 환산, 식 병기).
  `[해석]` 표시 없는 문장은 원문이 실제로 말한 것이어야 한다. 정정은 여기서 하지 않는다.
- **`papers/<slug>.md` = 논문 노트** (2층, 수정 가능). frontmatter 의 **`paper:` 블록**이 아래 추출 스키마
  그대로의 구조화 기록이고, `raw:` 가 digest 경로, `doi` 가 **중복 제거 키**다. 본문은 한 문단 요약·핵심
  주장·우리 접점·메커니즘 페이지 링크. 같은 논문이 파일명만 다르게 다시 들어오면 DOI 로 잡아 **새 노트를
  만들지 않고 기존 노트를 갱신**한다 (lint `doi-unique`). Supplementary 는 본문 논문 노트의
  `paper.supplementary` 에 연결하고 그림은 `raw/figures/<slug>/fig_S<n>.png` 로 같은 폴더에 둔다.
- `mechanisms/` (type `mechanism`) 열화 메커니즘 한 축당 한 페이지 · `protocols/` (type `protocol`)
  formation·셀 제작·main cycle·보조 측정 절차 · `experiments/` (type `experiment`) DOE 와 cell registry ·
  `comparisons/` 논문 간 비교표 · `concepts/` 그 밖의 개념 · `entities/` 우리 프로젝트(satellite) 카드 ·
  `questions/` 열린 질문 · `guides/` 절차 · `queries/` 질의 기록 · `syntheses/` 논지 방어.
- **근거 없는 일반 지식**: 근거 논문이 아직 없는 배경 설명은 `confidence: low`, `evidenceScope: synthesis-only`
  로 두고 본문 머리에 `> [!note] 미검증 배경` callout 을 붙인다. 이런 페이지는 인용 근거가 아니다 — 논문이
  ingest 되면 `sources` 에 digest 를 추가하고 등급을 올린다. webapp `/chat` 은 이 callout 을 보고
  "DB 외 일반 지식/추론" 으로 표시하게 되어 있다.
- **실험 수치의 정본은 원 데이터(`data/raw/`)와 cell registry(`data/registry/cells.csv`)** 다. 위키에 적힌
  우리 수치는 사본이며 인용 근거가 아니다. LLM 컨텍스트에는 raw CSV 를 통째로 넣지 않고 pandas 요약만 넘긴다.

### `paper:` 블록 — 논문 노트 추출 스키마 (값이 없으면 `null`, 추측으로 채우지 않는다)
```yaml
paper:
  bib:
    first_author: null          # 1저자 성 (인용 표기용)
    authors: null               # 저자 전체 (원문 순서)
    year: null
    journal: null
    title: null
    doi: null                   # "10.xxxx/…" — 중복 제거 키. 없으면 doi_missing_reason 에 이유
    doi_missing_reason: null
  supplementary:
    files: []                   # SI 원본 파일명 (저장소에 바이너리는 넣지 않는다)
    raw: null                   # SI 를 별도 digest 로 만들었으면 raw/papers/<slug>-si.md
  cathode:
    composition_verbatim: null  # 원문 표기 그대로 (NCM622 · NCA · LCO · Ni 함량 표기 포함). 변환 금지
    ni_content: null            # 원문 표기 그대로 (예 "Ni 0.62", "Ni 80 %")
    crystal: null               # single | poly | null
    coating: null               # true | false | null
    coating_type: null
    electrode_process: null     # dry | slurry | powder | null
    loading_mg_cm2: null
    loading_mah_cm2: null
    composite_ratio: null       # 복합양극 조성비 원문 그대로 (예 "AM:SE:C = 70:30:3 wt")
  electrolyte:
    type: null                  # LPSCl | LGPS | LPS | LiCl-LPS | … (원문 표기)
    detail: null
  anode:
    type: null                  # Li-In | Li | Ag-C | anode-free | LTO | graphite | …
    composition: null           # 조성이 명시된 경우만 (예 "Li0.5In")
  voltage:
    raw_text: null              # 원문 값 그대로 (예 "2.5–4.3 V")
    reference_raw: null         # 원문 기준전극 그대로 (예 "vs. Li/Li+", "vs. In/Li-In", "vs. Li-In")
    window_vs_li: null          # [lo, hi] 변환값 vs. Li/Li⁺ (숫자)
    offset_applied_v: null      # 변환에 더한 값 (원문이 이미 vs Li/Li⁺ 이면 0.0)
    notes: null
  formation:
    described: null             # true | false | null — 논문이 formation/pre-conditioning 을 별도 기술하는가
    cutoff_v_raw: null          # 원문 값 + 기준 (문자열)
    cutoff_v_li: null           # 변환값 vs. Li/Li⁺ (숫자)
    c_rate: null
    cycles: null
    rest_h: null
    temperature_c: null
  main_cycle:
    window_raw: null            # 원문 값 + 기준 (문자열)
    window_vs_li: null          # [lo, hi] 변환값 vs. Li/Li⁺
    c_rate: null
    temperature_c: null
    pressure_fab_mpa: null      # 제작압
    pressure_op_mpa: null       # 구동압
    cycles: null
  performance:
    initial_discharge_mah_g: null   # 초기 방전 비용량 (mAh g⁻¹ — 분모가 무엇인지 notes 에)
    ice_pct: null                   # 초기 쿨롱 효율
    retention_pct: null
    retention_cycles: null          # retention_pct 가 몇 사이클 후인가
    overpotential_trend: null       # 문자열 (예 "증가", "Fig. 4c 에서 100 사이클 후 +80 mV")
    hysteresis_trend: null
    notes: null
  techniques: []                # [XPS, ToF-SIMS, XRD, TEM, HAADF-STEM, FIB-SEM, EIS, DRT, dQ/dV, operando-pressure, Raman, …]
  mechanisms: []                # 주장 하나당 항목 하나 — evidence 필수
  # - claim: "…"                            # 논문의 주장 (요약; 원문 인용은 digest 에)
  #   products: [S, P2Sx, LiCl]              # 분해 산물 (있으면)
  #   voltage_range: "≥ 3.8 V vs. Li/Li+"    # 발생 전압대 + 기준
  #   evidence: "Fig. 3b, p.5"               # 근거 figure/page — 없으면 주장을 적지 않는다
  #   tags: [lpscl-oxidation]                # 아래 어휘에서만
```
메커니즘 태그 어휘: `cei` · `lpscl-oxidation` · `rock-salt` · `crack` · `void` · `contact-loss` ·
`lattice-oxygen` · `h2-h3` · `healing` · `anode-interface` · `other`.

우리 프로젝트 카드(`entities/`)는 같은 구조의 블록을 **`ours:`** 키로 둔다 — webapp `/compare` 의 첫 행
("우리 (사본)")이 여기서 온다. 값은 프로토콜 페이지의 사본이며 정본은 프로토콜·registry 다.

### 비교표 (webapp `/compare`)
`papers/*.md` 의 `paper:` + `entities/*.md` 의 `ours:` 를 평탄화해 표로 편다. 빈 칸은 논문이 그 값을 주지
않았다는 뜻이고 물음표를 채우지 않는다. 축: 양극·공정·로딩·전해질·음극·전압창(원문 / vs Li/Li⁺)·formation
cut-off·main cycle·성능·기법·메커니즘 태그, 그리고 **내 DOE 창과의 겹침** (`config/cells.yaml` 의
`doe.main_window_v_li` = 2.5–4.4 V vs. Li/Li⁺, `doe.formation_cutoffs_v_li` = 3.6–4.6 V) 표시.
정렬·거르기 축은 formation cut-off 와 상한 전압.

### 그림
digest 마다 `raw/figures/<slug>/` 에 크로핑 PNG + `figures.json` (`wiki/tools/extract_figures.py`). 본문의
`Fig. N` · `Fig. S<n>` · `Table N` 표기를 webapp 이 자동 링크한다. SI 그림은 `fig_S<n>.png`.

### 그 밖
- Satellite 프로젝트(실험 단계)는 `entities/` 1페이지로 등록하고, 상태가 바뀌면 `updated` 와 상태 절을 갱신한다.
- Cross-vault 참조는 `[[wikilink]]` 대신 **repo-root 상대 경로**(`data/…`, `config/…`)로 표기한다.
- 설계 세션·사용자의 연구 설명은 `raw/transcripts/` 에 세션 기록으로 남겨 페이지의 source 로 삼는다.
- 영어 용어를 **설명할 때**는 IPA 발음기호와 강세 위치를 함께 적는다 (어휘는 [[terminology-ipa]]).

## Frontmatter
```yaml
---
title: Page Title
description: "한 줄 요약 — 콜론·괄호가 들어가면 따옴표 필수"
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: paper-note | mechanism | protocol | experiment | concept | entity | comparison | query | guide | research-question | synthesis
tags: []
sources: [raw/papers/source-name.md]
confidence: high | medium | low
explored: false
verificationStatus: unverified | verified | disputed
verifiedAt: YYYY-MM-DD            # verified 일 때만
verifiedBy: agent | human | both  # verified 일 때만
claimType: definition | empirical | theoretical | historical | prescriptive | interpretive | mixed
evidenceScope: single-source | multi-source-primary | multi-source-mixed | synthesis-only | user-original
---
```

타입별 추가 키:
- `paper-note` (`papers/`): `raw:` (digest 경로), `paper:` (위 스키마)
- `entity` (`entities/`): 우리 셀이면 `ours:` (위 스키마와 같은 구조)
- `research-question` (`questions/`): `status: open | active | answered | abandoned`, `feedsInto:`
- `synthesis` (`syntheses/`): `targetVenue:`

### 세 가지 직교 품질 축
| 필드 | 추적 대상 | 규칙 |
|---|---|---|
| `confidence` | 증거 강도 | high 로 올릴 때 반대해석/데이터 공백 1줄 기록 |
| `verificationStatus` | source 대조 검증 | 새 페이지 `unverified`, 검증 후 `verified`, 충돌은 양쪽 `disputed` |
| `explored` | 사람이 읽었는가 | **사람만** `true` 로 바꾼다 |

### Provenance
- `claimType`(지배적 주장 유형)과 `evidenceScope`(근거 폭)를 기록한다. **`evidenceScope: single-source` 페이지는
  `confidence: high` 금지** — 근거 폭이 confidence 상한을 정한다 (lint warning). 사용자의 설명만이 근거이면
  `user-original`, 근거 논문 없는 배경 지식이면 `synthesis-only` + `confidence: low`.
- 이 저장소는 페이지에 **모델 식별자를 적지 않는다** (`model`/`effort` 필드 생략 — 루트 하드룰). 에이전트가
  썼다는 사실은 `log.md` 항목으로 남는다.
- `description` 등 자유 텍스트 frontmatter 값에 콜론·괄호가 들어가면 따옴표로 감싼다 (YAML 파싱 보호).

### 페이지 3분법
- **위키 페이지** (paper-note/mechanism/protocol/experiment/concept/entity/comparison/query/guide) = 배운 것의 기록.
- **research-question** = 답이 안 나온, 계속 돌아오는 질문의 추적. 본문: 질문 1문장 → 왜 중요한가 → 가설 →
  Evidence For / Against → Status Log(날짜별). `/paper`·`/wiki-ingest` 때마다 열린 카드(status: open|active)에
  새 자료가 근거를 주는지 확인해 축적한다.
- **synthesis** = 논지 하나의 방어. Thesis → Argument → Counter-arguments(반론 **보존**) → Gap.

### Paper Ingest Mode (opt-in)
논문의 수치·정의를 verbatim atom 으로 분해하는 모드 — **자동 실행 금지**, 사용자 승인 후 필요한 좌표만.
절차: `guides/paper-ingest-mode.md`. (이 저장소의 기본 논문 처리는 `/paper` 의 **digest + 논문 노트** 다.)

## Raw Frontmatter
```yaml
---
source_url: https://example.com/article      # 로컬 업로드면 local-upload/<파일명>
ingested: YYYY-MM-DD
sha256: <hex digest of body after frontmatter, leading blank lines stripped>
# digest 는 title / description / doi / tags 를 더 둔다 (구조화 추출은 papers/ 노트의 paper: 에)
---
```

## Tag Taxonomy
규칙: 소문자, 하이픈, 페이지 3개 이상 모일 주제만 태그로 승격.

시드 (mothership 공통): project · satellite · research · design · tooling · wiki

시드 (이 도메인):
- nca721: 우리 양극재 · mid-ni · high-ni: Ni 함량 계열
- sulfide-electrolyte: LPSCl 등 황화물 고체전해질 · lpscl-oxidation: 전해질 산화 분해
- formation: formation / pre-conditioning 프로토콜 · cutoff-voltage: 충전 cut-off 축
- cei: cathode–electrolyte interphase · contact-loss: 계면 접촉 손실 · crack: 입자 균열/공극
- lattice-oxygen: 격자 산소 관여·산소 방출 · h2-h3: 상전이 · rock-salt: 표면 상 변화
- healing: mechano-electrochemical healing · anode-interface: Li-In / Ag-C 계면
- dry-electrode: 건식 전극 공정 · pressure: 제작압/구동압 · reference-electrode: 3-전극·기준전극
- post-mortem: 사후분석 (XPS·ToF-SIMS·XRD·FIB-SEM·STEM·Raman) · eis: EIS/DRT
- cell-data: 충방전 데이터·registry · units: 단위·기준전극 규율
- liquid-electrolyte: 액체계 문헌 (비교 대상, 직접 이식 불가 표시)

## Page Thresholds
- Create a page when a concept is central to a source or recurs across sources.
- Do not create pages for passing mentions.
- Split pages over ~200 lines (guides·digest 제외).

## Update Policy
새 정보가 기존 내용과 충돌하면: 날짜/출처 품질 확인 → 양쪽 입장 기록(덮어쓰기 금지) → confidence 하향 또는
disputed → lint 에서 표면화.

## Git
커밋 prefix 는 log action 과 동일하되 scope 를 붙인다: `ingest(wiki):` `update(wiki):` `create(wiki):`
`lint(wiki):` `verify(wiki):`. webapp 은 `webapp:`, 셀 데이터 도구는 `cells:`.
push 는 항상 **루트 `CLAUDE.md` 하드룰 1이 지정한 작업 브랜치**로만 한다. 브랜치 이름을 여기 적지 않는다
(lint `no-hardcoded-branch-name`).
