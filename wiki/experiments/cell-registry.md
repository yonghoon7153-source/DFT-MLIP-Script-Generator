---
title: Cell registry — 셀 메타데이터의 정본과 파일명 파싱 규칙
description: "data/registry/cells.csv 의 스키마, 파일명은 제안값일 뿐이라는 규칙, 상태 어휘, import 흐름"
created: 2026-09-11
updated: 2026-09-11
type: experiment
tags: [cell-data, units, tooling]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
---

# Cell registry

## 설계
raw 충방전 파일의 이름은 일관되지 않는다 (사용자 진술의 예: `Dcell14_mid_Ni___0.0189g_4.0V_...`,
`cell16_CONT_4.0V_18.5mg_...`, `Dcell49mid_Ni___...` — 질량 단위 g/mg 혼재, 전극 질량인지 활물질 질량인지 불명).
그래서 **파일명 파싱은 제안값**으로만 쓰고, **`data/registry/cells.csv` 가 source of truth** 다.
`tools/cells/import_cell.py --propose <파일>` 은 파일명에서 cell ID·전압·질량을 **제안**하고, 사람이 registry 에
확정값을 적는다. import 는 registry 의 값만 쓴다 (registry 에 질량이 없으면 비용량을 계산하지 않는다 —
추측하지 않는다).

## 변수와 고정 조건 — registry 열

| 열 | 뜻 | 단위 / 어휘 |
|---|---|---|
| `cell_id` | 셀 ID (파일명의 `Dcell14`·`cell16` 과 맞춘다) | — |
| `formation_cutoff_v_li` | formation 충전 cut-off | **V vs. Li/Li⁺** (장비값 vs. In/Li-In 에 +0.62 V) |
| `active_mass_mg` | **활물질** 질량 — 전극 질량이 아니다 | mg |
| `loading_mah_cm2` / `loading_mg_cm2` | 면적용량 / 면적 로딩 | mAh cm⁻² / mg cm⁻² |
| `punch_diameter_mm` | 펀칭 지름 | mm |
| `fab_pressure_mpa` / `anode_fab_pressure_mpa` / `op_pressure_mpa` | 양극+SE 제작압 / 음극 제작압 / 구동압 | MPa |
| `status` | `planned` · `cycling` · `eis` · `rest` · `harvested` · `post-mortem` · `done` | — |
| `raw_file` / `summary_file` | `data/raw/` 안의 파일명 | — |
| `notes` | 비고 — retention 분모 정의, 이상 이벤트, 파일명 질량의 정체 등 | 따옴표로 감싼다 |

형식 예시: `data/registry/cells.example.csv` (값은 예시이지 실측이 아니다).

## 측정·산출물 — import 흐름
1. raw CSV 를 `data/raw/` 에 둔다 (저장소에 커밋하지 않는다 — `.gitignore`).
2. `python3 tools/cells/import_cell.py --propose data/raw/<file>.csv` → 파일명에서 읽은 제안값을 보고 registry 에 행을 적는다.
3. `python3 tools/cells/import_cell.py --cell <cell_id>` → registry 의 `raw_file`·`active_mass_mg` 로
   사이클 요약을 계산해 `data/cells/<cell_id>/cycles.csv` + `summary.json` 을 만든다 (pandas).
   전압은 원본(vs. In/Li-In)과 변환값(vs. Li/Li⁺, offset 병기)을 둘 다 쓴다. 용량은 mAh g⁻¹.
4. webapp `/cells` 가 registry 와 summary 를 읽어 cut-off 별 색(`config/cells.yaml`)으로 그린다.
5. `/chat` 에는 **요약 통계만** 넘어간다 — raw CSV 는 넘기지 않는다.

상세는 [[cell-data-module]]. 관련 DOE 는 [[formation-cutoff-doe]].

## 상태
- **2026-09-11** — registry 비어 있음 (헤더만). 사용자가 셀 목록을 채우면 이 절에 날짜와 함께 요약한다.

## 관련
- [[cell-data-module]] · [[formation-cutoff-doe]] · [[voltage-reference-and-capacity-conventions]]
