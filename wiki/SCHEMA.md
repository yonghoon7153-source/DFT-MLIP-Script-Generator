# Wiki Schema

## Domain
Yonghoon-DEM-DFT 저장소의 mothership LLM Wiki (작업 브랜치는 루트 `CLAUDE.md` 하드룰 1). **Li2S 양극 all-solid-state
Li–S 전지** 연구 — pristine Li2S reference cell(목표 500–600 mAh g⁻¹, 단위 기준 명시 필수),
복합양극 Li2S:LPSCl:C 혼합 공정(one-step / two-step / 탄화 / 용액 경로), Li2S 활성화,
Li–In → anode-free 전환 — 에 관한 **논문 digest, 개념, 열린 질문, 논문 간 비교, 세미나
자료**를 등록·연결·재사용한다. 실험 프로젝트는 satellite(entity)로 등록해 상태를 추적한다.

## Conventions
- File names: lowercase, hyphens, no spaces.
- Raw source files live under `raw/` and are treated as immutable.
- Wiki pages live under `concepts/`, `entities/`, `comparisons/`, `queries/`, `guides/`, `questions/`, `syntheses/`.
- Every wiki page starts with YAML frontmatter (below).
- Use `[[wikilinks]]` for internal links; each page should target at least 2 related pages.
- Every new page must be listed in `index.md`. Every meaningful action goes to `log.md`.
- When updating a page, bump `updated`.
- 새 페이지는 `python3 wiki/tools/new-page.py <type> <slug>` 스캐폴더로 만든다.
- Lint: `python3 wiki/tools/lint.py` (repo root 기준) · Status: `python3 wiki/tools/status.py`
- Claude Code 커맨드 (repo root `.claude/commands/`): /wiki-ingest /wiki-inbox /wiki-query /wiki-verify /wiki-lint /wiki-status /wiki-wrap · 논문 전용: /paper (논문 에이전트) /seminar (세미나 자료) /compare (논문 비교)

### 이 저장소 특칙
- **단위 규율**: 비용량은 반드시 `mAh g⁻¹(S)` 또는 `mAh g⁻¹(Li2S)` 로 기준을 적는다 (환산 ×0.698). 면적용량은 `mAh cm⁻²` 와 함께 로딩(mg cm⁻², 무엇의 질량인지)을 적는다. 전압은 `vs Li/Li⁺` 또는 `vs Li–In` 을 적는다 (Li–In ≈ +0.62 V vs Li/Li⁺ — 이 값 자체는 아직 이 위키에 근거 raw 가 없다, 인용 금지).
- **논문 digest 는 `raw/papers/`** 에 sha256 봉인. 표기 4구분 `[인쇄]`(원문 글자) / `[도표]`(그림 판독 근사값) / `[해석]`(우리 판단) / `[재현]`(원문 값의 산술 환산, 식 병기). `[해석]` 표시 없는 문장은 원문이 실제로 말한 것이어야 한다.
- **digest frontmatter 의 `compare:` 블록**은 논문 간 비교의 정본 필드다 (`system` `electrolyte` `cathode` `li2s_source` `mixing` `loading_mg_cm2` `li2s_wt_pct` `anode` `first_charge` `first_discharge_mAh_gS` `first_discharge_mAh_gLi2S` `cycle_capacity_mAh_gS` `cycle_capacity_mAh_gLi2S` `areal_mAh_cm2` `cycles` `temperature_C` `mechanism` `our_axis`). 없는 값은 쓰지 않는다 (webapp `/compare` 가 빈 칸으로 보인다 — 물음표를 채우지 않는다).
- **그림**: digest 마다 `raw/figures/<slug>/` 에 크로핑 PNG + `figures.json`. 본문의 `Fig. N` 표기를 webapp 이 자동 링크한다. SI 그림은 `fig_S<n>.png`.
- Satellite 프로젝트(실험 단계)는 `entities/` 1페이지로 등록하고, 상태가 바뀌면 `updated`와 상태 섹션을 갱신한다. 등록 절차는 `guides/new-project-kickoff.md`.
- Cross-vault 참조는 `[[wikilink]]` 대신 **repo-root 상대 경로**로 표기한다 (clone 경로가 WSL·서버마다 다르다). 내용 복사는 금지, 참조만 한다 (living reference).
- 설계 세션·사용자의 연구 설명은 `raw/transcripts/`에 세션 기록으로 남겨 페이지의 source로 삼는다.
- **실험 수치의 정본은 실험 노트·원 데이터**다. 위키에 적힌 우리 수치는 사본이며 인용 근거가 아니다.

## Frontmatter
```yaml
---
title: Page Title
description: "한 줄 요약 — 콜론·괄호가 들어가면 따옴표 필수"
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: concept | entity | comparison | query | guide | research-question | synthesis
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
- `research-question` (`questions/`): `status: open | active | answered | abandoned`, `feedsInto:` (답이 흘러갈 곳 — 실험·발표·결정)
- `synthesis` (`syntheses/`): `targetVenue:` (논지를 쓸 곳)

### 세 가지 직교 품질 축
| 필드 | 추적 대상 | 규칙 |
|---|---|---|
| `confidence` | 증거 강도 | high 로 올릴 때 반대해석/데이터 공백 1줄 기록 |
| `verificationStatus` | source 대조 검증 | 새 페이지 `unverified`, 검증 후 `verified`, 충돌은 양쪽 `disputed` |
| `explored` | 사람이 읽었는가 | **사람만** `true` 로 바꾼다 |

### Provenance
- `claimType`(지배적 주장 유형)과 `evidenceScope`(근거 폭)를 기록한다. **`evidenceScope: single-source` 페이지는 `confidence: high` 금지** — 근거 폭이 confidence 상한을 정한다 (lint warning). 사용자의 구두/텍스트 설명만이 근거이면 `user-original`.
- 이 저장소는 페이지에 **모델 식별자를 적지 않는다** (`model`/`effort` 필드 생략 — 하네스 규칙). 에이전트가 썼다는 사실은 `log.md` 항목으로 남는다.
- `description` 등 자유 텍스트 frontmatter 값에 콜론·괄호가 들어가면 따옴표로 감싼다 (YAML 파싱 보호). lint 가 검사한다.

### 페이지 3분법
- **위키 페이지** (concept/entity/comparison/query/guide) = 배운 것의 기록.
- **research-question** = 답이 안 나온, 계속 돌아오는 질문의 추적. 본문: 질문 1문장 → 왜 중요한가 → 가설 → Evidence For / Against → Status Log(날짜별). `/wiki-ingest`·`/paper` 때마다 열린 카드(status: open|active)에 새 자료가 근거를 주는지 확인해 축적한다.
- **synthesis** = 논지 하나의 방어. 본문: Thesis 1문장 → Argument → Counter-arguments(반론 **보존**, 삭제 금지) → Gap(빈 근거). 답이 모인 research-question 이 synthesis 로 승격될 수 있다.

### Paper Ingest Mode (opt-in)
논문의 수치·정의·인용문을 verbatim 재사용 가능한 atom 으로 분해하는 모드. **자동 실행 금지** — 사용자 승인 후, 필요한 좌표만. 절차: `guides/paper-ingest-mode.md`. (이 저장소의 기본 논문 처리는 `/paper` 의 **전문 digest** 이며, 그것만으로 대부분의 재조회가 해결된다.)

## Raw Frontmatter
```yaml
---
source_url: https://example.com/article      # 로컬 업로드면 local-upload/<파일명>
ingested: YYYY-MM-DD
sha256: <hex digest of body after frontmatter, leading blank lines stripped>
# 논문 digest 는 여기에 title / description / doi / tags / compare: 를 더 둔다
---
```

## Tag Taxonomy
규칙: 소문자, 하이픈, 페이지 3개 이상 모일 주제만 태그로 승격.

시드 (mothership 공통):
- project: 진행 중인 프로젝트 · satellite: 별도 폴더/저장소로 운영되는 참조 · research: 연구 내용 일반 · design: 설계 결정 · tooling: 개발 환경·도구 · wiki: LLM Wiki 운영 자체

시드 (이 도메인):
- li2s: Li2S 양극 활물질 일반
- assb: all-solid-state 셀 구성·공정
- sulfide-electrolyte: LPSCl 등 황화물 고체전해질
- composite-cathode: 복합양극 설계(조성·미세구조·삼상 퍼콜레이션)
- mixing-process: ball milling / planetary / Thinky / 용액 / 탄화 등 혼합·합성 경로
- activation: Li2S 첫 충전 활성화·과전압·직접 전환
- carbon: 도전재(AB·CNT·graphene) 역할
- anode-free: anode-free 구성과 Li 침적
- li-in: Li–In 음극 기준전위·거동
- liquid-electrolyte: 액체 Li–S 문헌 (비교 대상, 직접 이식 불가 표시)
- li-free-anode: 흑연·Si 등 Li-free 음극 full cell
- units: 용량 정규화·단위 환산
- seminar: 세미나·발표 자료

## Page Thresholds
- Create a page when a concept is central to a source or recurs across sources.
- Do not create pages for passing mentions.
- Split pages over ~200 lines (guides·digest 제외).

## Update Policy
새 정보가 기존 내용과 충돌하면: 날짜/출처 품질 확인 → 양쪽 입장 기록(덮어쓰기 금지) → confidence 하향 또는 disputed → lint 에서 표면화.

## Git
커밋 prefix 는 log action 과 동일하되 scope 를 붙인다: `ingest(wiki):` `update(wiki):` `create(wiki):` `lint(wiki):` `verify(wiki):`. webapp 은 `webapp:`.
push 는 항상 **루트 `CLAUDE.md` 하드룰 1이 지정한 작업 브랜치**로만 한다. 브랜치 이름을 여기 적지 않는다 (lint `no-hardcoded-branch-name` 검사 — 선행 브랜치에서 이름 drift 로 8곳이 깨진 전례).
