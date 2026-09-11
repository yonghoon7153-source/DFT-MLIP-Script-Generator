---
title: 셀 데이터 모듈 (prototype) — 스키마·import·설정
description: "raw 충방전 CSV(utf-8-sig) 를 pandas 로 사이클 요약으로 바꾸고, registry 를 정본으로 두며, 전압 원본·변환값과 mAh g⁻¹ 을 함께 주는 모듈의 사용법"
created: 2026-09-11
updated: 2026-09-11
type: guide
tags: [cell-data, units, tooling]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
---

# 셀 데이터 모듈 (prototype)

## 목적
prototype 범위는 **스키마와 import 까지** (사용자 진술 [4]). 이후 확장(그래프 비교·통계)은 같은 요약 파일 위에 얹는다.

## 절차

### 파일 배치
| 경로 | 내용 | git |
|---|---|---|
| `config/cells.yaml` | offset +0.62 V (vs. In/Li-In → vs. Li/Li⁺, 정본) · DOE 창 · cut-off 별 색 · CSV 열 정의 · 경로 | 커밋 (사용자가 직접 고친다) |
| `data/registry/cells.csv` | **cell registry — 정본** ([[cell-registry]]) | 커밋 |
| `data/raw/*.csv` | raw 충방전 CSV, 사이클 요약 CSV | **커밋하지 않는다** |
| `data/cells/<cell_id>/cycles.csv` · `summary.json` | import 산출물 (pandas 요약) | 커밋 (작다) |

### raw CSV 스키마 (사용자 진술)
열: timestamp, test_time_s, step_time_s, cycle_time_s, channel, step_index, total_step, cycle_index, run_status,
running_status, cell_status, i_range_index, i_range, voltage, current, charge_q (Ah), discharge_q (Ah), charge_e (Wh),
discharge_e (Wh), aux_voltage, temperature, ocp. **UTF-8 BOM** 이 붙어 있으므로 `utf-8-sig` 로 읽는다.
전압 열은 **vs. In/Li-In** 원본이다.

### 사이클 요약 스키마 (import 산출물)
cycle, charge_capacity_mah_g, discharge_capacity_mah_g, charge_capacity_mah, discharge_capacity_mah,
coulombic_efficiency, charge_energy_wh, discharge_energy_wh, energy_efficiency, mean_charge_voltage,
mean_discharge_voltage, voltage_hysteresis, v_max, v_min, duration_s, points, complete — 전압 열은 원본(vs. In/Li-In)이고
`summary.json` 에 변환값(vs. Li/Li⁺, offset 병기)이 함께 실린다. 사용자의 장비가 만든 사이클 요약 CSV 도 같은
이름 규칙으로 읽는다 (열 이름은 소문자·공백 제거 후 대응).

### 명령
```bash
python3 tools/cells/import_cell.py --propose data/raw/Dcell14_mid_Ni___0.0189g_4.0V_x.csv   # 파일명 → 제안값
python3 tools/cells/import_cell.py --cell Dcell14        # registry 기준 import
python3 tools/cells/import_cell.py --all                 # registry 의 raw_file 이 있는 셀 전부
python3 -m unittest tests/test_cells.py                  # 합성 데이터 테스트
```
`--propose` 는 **registry 에 쓰지 않는다** — 화면에 제안만 찍는다. 질량은 g/mg 를 모두 mg 로 환산해 보이되
"전극 질량인지 활물질 질량인지 미확인" 을 붙인다.

### 규칙 (절대 규칙의 적용)
- 비용량은 `active_mass_mg`(활물질) 로 나눈 mAh g⁻¹. registry 에 질량이 없으면 mAh g⁻¹ 열은 비운다 (추측 금지).
- 전압 변환은 `config/cells.yaml` 의 `in_to_li_offset_v` 만 쓴다 ([[voltage-reference-and-capacity-conventions]]).
- LLM(`/chat`) 에는 `summary.json` 의 요약 통계(사이클 수, 첫/마지막 방전 비용량, retention, CE 평균, hysteresis
  추세)만 넘어간다. raw CSV 는 넘기지 않는다.

### 그래프 색
`config/cells.yaml` 의 `colors` 가 formation cut-off(vs. Li/Li⁺ 문자열 키)별 색이다. webapp `/cells` 의
방전 비용량 vs 사이클 차트가 이 색을 쓴다 — 사용자가 직접 바꾼다.

## 관련
- [[cell-registry]] · [[formation-cutoff-doe]] · [[wsl-midni-setup]]
