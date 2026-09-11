# data/registry — cell registry (정본)

`cells.csv` 가 **모든 셀 메타데이터의 source of truth** 다. 파일명 파싱(`tools/cells/import_cell.py --propose`)은
제안값일 뿐이며 여기 적힌 값이 우선한다. 스키마와 사용법은 `wiki/experiments/cell-registry.md`.

| 열 | 뜻 | 단위 |
|---|---|---|
| `cell_id` | 셀 ID (파일명의 `Dcell14`·`cell16` 등과 맞춘다) | — |
| `formation_cutoff_v_li` | formation 충전 cut-off | V vs. Li/Li⁺ |
| `active_mass_mg` | **활물질** 질량 (전극 질량이 아니다) | mg |
| `loading_mah_cm2` / `loading_mg_cm2` | 면적용량 / 면적 로딩 | mAh cm⁻² / mg cm⁻² |
| `punch_diameter_mm` | 펀칭 지름 | mm |
| `fab_pressure_mpa` / `anode_fab_pressure_mpa` / `op_pressure_mpa` | 양극+SE 제작압 / 음극 제작압 / 구동압 | MPa |
| `status` | `planned` · `cycling` · `eis` · `rest` · `harvested` · `post-mortem` · `done` | — |
| `raw_file` / `summary_file` | `data/raw/` 안의 파일명 | — |
| `notes` | 비고 (따옴표로 감싼다) | — |

`cells.example.csv` 는 형식 예시다 (값은 예시이지 실측이 아니다).
