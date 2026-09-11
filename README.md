# Yonghoon-DEM-DFT — mid-Ni NCA721 formation 연구 위키 + 대시보드 (브랜치 `claude/midni-formation-wiki`)

sulfide 기반 all-solid-state battery 에서 **NCA721 (mid-Ni) 양극의 formation(pre-conditioning) 충전 cut-off** 가 장기 사이클
성능과 열화 메커니즘(CEI 형성 · LPSCl 산화 분해 · lattice oxygen 관여 · 계면 contact loss)에 주는 영향을 연구하는 저장소.
**mothership LLM Wiki**(논문 노트·메커니즘·프로토콜·DOE·비교)와, 그 위키를 읽고 논문을 비교하고 대화하는 **로컬 대시보드**,
그리고 **셀 데이터 모듈(prototype)** 로 이루어진다. 논문은 `/paper` 논문 에이전트가 DOI 로 중복을 걸러 봉인 digest + 구조화 노트로 흡수한다.

> 다른 브랜치(DEM/MPM · 열화 degeneracy · Li2S 위키 · argyrodite ML …)는 별개 프로젝트다 — `BRANCHES.md`.

## 3분 시작 (WSL / Ubuntu)

```bash
git clone <이 저장소> ~/Yonghoon-DEM-DFT && cd ~/Yonghoon-DEM-DFT
git checkout claude/midni-formation-wiki   # 작업 브랜치 (정본: CLAUDE.md 하드룰 1)
bash scripts/setup-wsl.sh                  # .venv + 의존성 + alias midni  (한 번)
source ~/.bashrc
midni                                      # 서버를 띄우고 브라우저를 연다 → http://127.0.0.1:51xx
```

| 명령 | 뜻 |
|---|---|
| `midni` | 서버 기동(백그라운드) + 브라우저. 이미 떠 있으면 열기만 |
| `midni open` · `status` · `stop` · `restart` · `update` · `log` | 보통의 것들 |
| `midni share` | 같은 망의 다른 PC 에서 보게 (0.0.0.0, 인증 없음 — 공개망 금지; WSL 은 포트프록시 필요) |
| `midni paper <pdf> [<si>…]` | PDF(+SI) 를 `wiki/inbox/` 로 → Claude Code 에서 `/paper` |
| `midni cells propose <csv>` · `cells import <id>` · `cells all` | raw 파일명 제안 (registry 는 사람이 적는다) · 사이클 요약 import |
| `midni lint` · `midni smoke` · `midni test` · `midni wiki` | 위키 lint / webapp 라우트 점검 / 셀 모듈 테스트 / 위키 상태 |

`/chat`(위키 근거 대화)을 켜려면 서버를 띄우는 셸에 `export ANTHROPIC_API_KEY=…` 가 있어야 한다. 키는 파일·저장소에 두지 않는다.
alias 이름을 하나 더 두려면 `bash scripts/install-alias.sh <이름>`. 자세한 절차는 `wiki/guides/wsl-midni-setup.md`.

## 무엇이 있나

| 경로 | 역할 |
|---|---|
| `wiki/` | 위키 — `raw/`(digest·그림·세션 기록, 불변) · `papers/ mechanisms/ protocols/ experiments/ comparisons/ concepts/ entities/ questions/ guides/` (컴파일) · `index.md` `log.md` · `tools/`(lint·status·new-page·seal·extract_figures) |
| `webapp/` | Flask 대시보드: 홈 · 연구 로드맵 · 논문(노트+digest, 그림 팝업·메모) · **논문 비교표**(`paper:` 블록 + 내 DOE 겹침, 상한 전압/cut-off 정렬) · 열화 메커니즘 · 프로토콜 · 실험 · 열린 질문(찬반 맞세움) · 개념 · 프로젝트 · **위키와 대화** · **셀 데이터** · 검색. 읽기 전용 (`/api/chat` `/api/md` 만 POST, 둘 다 파일을 쓰지 않는다) |
| `config/cells.yaml` | 정본 상수 — 전압 offset(+0.62 V), DOE 창, 셀 제작 조건, cut-off 별 그래프 색, CSV 열 정의 |
| `data/registry/cells.csv` · `data/raw/` · `data/cells/` | cell registry(정본) · raw CSV(커밋 안 함) · import 요약 |
| `tools/cells/` · `tests/` | 셀 데이터 모듈 · 단위 테스트 |
| `.claude/` | `/paper` `/compare` `/cells` `/wiki-*` 커맨드, 논문 에이전트, hook |
| `scripts/` | WSL 세팅·alias |

## 논문 워크플로

1. PDF(+SI)를 `wiki/inbox/` 에 넣는다 (`midni paper …`) 또는 대화에 첨부.
2. Claude Code 에서 **`/paper`** → DOI 로 중복 확인 → `wiki/raw/papers/<slug>.md`(봉인 digest, `[인쇄]/[도표]/[해석]/[재현]`) +
   `wiki/papers/<slug>.md`(노트 — `paper:` 추출 스키마: 서지·양극(원문 표기)·전해질·음극·전압(원문 기준 + 변환·offset)·formation·main cycle·
   성능·기법·메커니즘 주장+근거) + `wiki/raw/figures/<slug>/`(크로핑 PNG) + 메커니즘 페이지·질문 카드 갱신 + lint 0 errors.
3. 대시보드 `/papers` → 노트+digest 읽기, `/compare` → 논문 나란히 (내 DOE 창과 겹침·정렬·거르기), `/chat` → 위키 근거로 토론
   (출처 필수, DB 외 지식 구분, 비교 시 기준전극·조성·온도·압력·loading 자동 지적, IPA 병기).

초기 투입 예정 논문 10편의 자리는 `wiki/comparisons/formation-cutoff-vs-degradation-literature.md`.

## 셀 데이터 워크플로 (prototype — 스키마와 import 까지)

1. raw CSV(utf-8-sig) 를 `data/raw/` 에 둔다. `midni cells propose <csv>` 로 파일명 제안값을 보고 **registry 에 사람이 확정값**을 적는다
   (활물질 질량·cut-off vs. Li/Li⁺·loading·펀칭 지름·제작압/구동압·상태·비고).
2. `midni cells import <cell_id>` → `data/cells/<cell_id>/cycles.csv` + `summary.json` (pandas; 전압 원본 vs. In/Li-In 과 변환값 vs. Li/Li⁺ 병기, 용량 mAh g⁻¹).
3. 대시보드 `/cells` — cut-off 별 n, 방전 비용량 vs 사이클(색은 `config/cells.yaml`), registry 표. `/chat` 에는 요약 통계만 넘어간다.

## 규칙 (요약 — 정본은 `CLAUDE.md` 맨 아래 [절대 규칙] · `wiki/SCHEMA.md`)

- 우리 양극재는 **NCA721** — NCM721 로 바꿔 부르지 않는다. 논문 조성은 원문 표기 그대로 (NCA↔NCM 변환 금지).
- 전압에는 항상 기준전극. **vs. Li/Li⁺ = vs. In/Li-In + 0.62 V**.
- 비용량(mAh g⁻¹) ≠ 면적용량(mAh cm⁻²). 절대용량(mAh)으로 보고하지 않는다.
- 충전 = delithiation, 방전 = lithiation.
- `wiki/raw/` 는 고치지 않는다. 실험 수치의 정본은 `data/`. 커밋 prefix: `ingest(wiki):` `update(wiki):` `create(wiki):` `lint(wiki):`
  `verify(wiki):` `webapp:` `cells:`.
