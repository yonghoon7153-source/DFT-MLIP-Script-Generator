# 위키 색인

> 내용 목록. 모든 위키 페이지를 종류별로 한 줄 요약과 함께 싣는다. 논문 digest(`raw/papers/`)는 컴파일 페이지가
> 아니므로 여기 세지 않고 아래 "Raw 논문" 절에 참고로만 적는다 (논문 **노트** `papers/` 는 센다).
> 마지막 갱신: 2026-09-11 | 전체 페이지: 28 | Total pages: 28

## Papers (논문별 노트 — `paper:` 추출 스키마, DOI 정본)

(아직 없음 — 첫 논문은 `/paper` 로. 투입 예정 10편은 [[formation-cutoff-vs-degradation-literature]] 의 표.)

## Mechanisms (열화 메커니즘 — 지금은 전부 미검증 배경, 논문이 들어오면 근거를 붙인다)

- [[cei-formation-sulfide-cathode]] — NCA721 | LPSCl 계면의 CEI 정의, 관측 지표, formation cut-off 와의 가설.
- [[lpscl-oxidative-decomposition-by-voltage]] — LPSCl 산화 분해 산물(S, P2Sx, LiCl, sulfate/phosphate)의 전압대 표 — 논문 [인쇄] 값으로만 채운다.
- [[ni-co-o-redox-and-oxygen-release]] — 고 SOC 에서 전이금속·산소 redox 와 격자 산소 손실, 황화물 SE 와의 연결.
- [[h2-h3-phase-transition-identification]] — H2–H3 전이 판별법(dQ/dV·XRD·operando 압력), mid-Ni 에서의 위치 확인 절차.
- [[mid-ni-vs-high-ni-degradation]] — Ni 함량에 따른 지배 열화 축 비교표, SE 산화는 전위의 함수라는 논점.
- [[mechano-electrochemical-healing]] — 구동압 아래 접촉 회복 개념, 100 MPa 셀과 저압 파우치의 차이.
- [[interface-degradation-cathode-electrolyte-anode]] — 세 계면(양극–SE, SE, SE–Li-In)의 열화 지도.

## Protocols (프로토콜 — 사용자 진술 사본, 정본은 실험 노트·registry)

- [[formation-preconditioning-protocol]] — 0.1C/0.1C 2 cycles, 충전 cut-off 3.6–4.6 V vs. Li/Li⁺, 장비값은 vs. In/Li-In.
- [[cell-fabrication-conditions]] — 10Φ 몰드, 양극+SE 462 MPa 2.5 min, 음극 277 MPa 5 min, 구동압 100 MPa.
- [[main-cycle-protocol]] — 2.5–4.4 V vs. Li/Li⁺, 0.5C, 45 °C, 200 cycles, 2번째 사이클 SOC 100 % EIS.
- [[auxiliary-measurements]] — 24 h rest · 3-전극 EIS/DRT · operando 압력(LTO) · 사후분석 — 각각이 겨냥하는 메커니즘.

## Experiments (실험 — DOE, registry)

- [[formation-cutoff-doe]] — 단일 변수(cut-off 6 수준) 설계, 산출물 정의, 가설 연결, 수준 구조 읽기.
- [[cell-registry]] — `data/registry/cells.csv` 스키마, 파일명은 제안값일 뿐, import 흐름.

## Comparisons (논문 간 비교)

- [[formation-cutoff-vs-degradation-literature]] — 비교 축 정의(상한 전압/formation cut-off vs 열화 거동) + 투입 예정 10편의 자리.

## Concepts (개념·규약)

- [[voltage-reference-and-capacity-conventions]] — vs. Li/Li⁺ = vs. In/Li-In + 0.62 V, 비용량/면적용량/절대용량, 충전=delithiation.
- [[nca721-mid-ni-cathode]] — 우리 양극재는 NCA721, 논문 조성은 원문 표기 그대로 (절대 규칙 1).

## Entities (프로젝트 카드)

- [[nca721-formation-project]] — 진행 중 satellite. `ours:` 블록이 /compare 의 첫 행.
- [[followup-high-ni-and-anode-free-pouch]] — 후순위 두 갈래 (계획).

## Questions (열린 질문)

- [[formation-cutoff-vs-long-term-degradation]] — (status: active) 핵심 질문, 가설 H1–H5.
- [[lattice-oxygen-involvement-at-high-cutoff]] — (status: open) 4.4–4.6 V 에서 격자 산소 관여 여부.
- [[contact-loss-vs-cei-growth-attribution]] — (status: open) 저항 증가의 귀속 방법론.

## Guides (절차)

- [[wsl-midni-setup]] — WSL 에서 `midni` 한 단어로 대시보드, PDF 넣기, /chat 키.
- [[paper-agent-workflow]] — /paper 의 순서와 산출물, DOI 중복 제거, SI 연결, null 원칙.
- [[cell-data-module]] — 셀 데이터 모듈 스키마·import·설정 (prototype).
- [[chat-citation-rules]] — /chat 의 인용·DB 외 표시·비교 시 자동 지적·IPA 규칙.
- [[terminology-ipa]] — 영어 용어 IPA·강세 용어집.
- [[new-project-kickoff]] — 새 satellite 등록 킥오프 프롬프트 (repo-root 상대 경로판).
- [[paper-ingest-mode]] — verbatim atom 분해 opt-in 모드.

## Syntheses (종합)

(아직 없음 — 질문 카드에 답이 모이면 승격)

## Queries (질의 기록)

(아직 없음)

## Raw 논문 (참고 — 색인 카운트에 포함하지 않음)

(아직 없음 — `raw/papers/` 비어 있음)

## Raw 세션 기록

- `raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md` — 사용자의 연구 설명 원문 + 설계 결정 + 미결 Q1–Q6 (sha256 봉인).
