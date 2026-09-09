---
title: frame[4] — DEM↔MPM 상호 보정 금지 (독립 보정 인식론)
created: 2026-08-11
updated: 2026-09-09
type: concept
tags: [epistemology, calibration, dem, mpm]
sources: [CLAUDE.md, docs/mpm3d_calibration.md, docs/mpm_dem_wallP_crossvalidation.md]
confidence: high
explored: false
verificationStatus: unverified
author: agent
claimType: prescriptive
evidenceScope: multi-source-primary
anchored: n-a
scope: n-a
---

# frame[4] — DEM↔MPM 상호 보정 금지

## 정의
DEM 과 MPM 은 각각 **실험에만** 독립적으로 보정한다.  한쪽을 다른 쪽에 맞추는 것
(예: MPM σ_y 를 DEM Heckel σ_y_eff 에 튜닝)은 **순환**이라 금지.

## 왜 중요한가
- **발산**하면 = 정량화된 모델 한계 (DEM 탄성연화 한계 or MPM 연속체근사 한계) — 출판 가능한
  정보이지 실패가 아니다.  이 절반은 그대로 선다.
- ⚠⚠ **수렴하면 교차검증 증거** 라는 나머지 절반은 **조건부다** — 두 모델이 **같은 기하를
  공유**하면 일치는 자동이고 증거가 아니다.  ⇒ **일치를 인용하기 전에** 그 양이 서로 독립인지
  먼저 보일 것.
- ⛔ **철회된 두 예시** (2026-08-12 반증, 여기 반영 2026-09-09 전수 감사 P0):
  - ~~real_14 scaffold 의 porosity 16.7 ↔ 15.6 % 일치가 증거~~ → **아니다.**  SE 씨앗이
    DEM 압축 **후** 좌표라 `solid_vol` 이 상수이고 MPM 의 유일한 출력은 `wall_z` 다.
    플래튼을 DEM 높이에 두면 `ε_sphere` 는 DEM porosity 를 **산술적으로** 돌려준다 = 순환.
    게다가 공통 관례(ε_sphere)로 읽으면 **14.70 vs 15.63 = 0.93 %p 과압축**이고, 보이던
    "일치" 는 **관례 오프셋 1.251 %p 와 과압축의 상쇄**였다.
  - ~~512 격자수렴이 1.2 %p 를 수렴된 구성모델 차이로 확인~~ → **아니다.**  그 1.2 %p 는
    **부기 관례 오프셋**이라 **정의상 격자 무관**이다 — 격자수렴 시험이 원리적으로 못 잡는
    부류이고, 384↔512 가 같이 나온 것은 증거가 아니라 항등식이다.
  - 살아남는 스캐폴드 산출물은 **응력-정지 두께**(29.95 vs 30.28 µm) 하나다.
  정본: `docs/mpm_platen_kinematic_stop_defect.md` · `docs/mpm_scaffold_reliability_and_am_freeze.md`
  머리 배너 · CLAUDE.md 트랙 2.

## 이 리포에서의 위치
- 보정 앵커는 공유하되 (Minnmann pure-SE 10 % @300 MPa) 서로의 출력은 앵커가 아니다.
- [[frame5-division-of-labor]] 와 쌍 — 분업은 frame[5], 보정 독립은 frame[4].
- ⚠ σ 이중화에는 **그대로 적용되지 않는다** (2026-09-08 CL-81): [[network-vs-voxel-sigma]] 의
  두 솔버는 대등한 독립 측정이 **아니다** — 복셀 FV 는 접촉망이 스스로 `CONTACT_FREE —
  upper bound, ideal contact limit` 이라 부르는 **가지 위에 있다** (SE–SE 면을 harmonic mean
  으로만 이어 계면 저항 항이 **정확히 0**).  크기는 코퍼스에 이미 저장돼 있다 —
  `R_brug_over_full` n=157 중앙값 **4.04×**(Hertz) · **6.69×**(소성면적), 범위 2.3~13.6×.
  ⇒ 두 σ_ion 의 일치를 교차검증으로 인용하지 말 것.  정본 `docs/voxel_contact_free_gap.md`.
- 위키 규범으로서: 페이지끼리 충돌하면 한쪽을 다른 쪽에 맞추지 말고 양쪽 기록
  (SCHEMA Update Policy 와 동형).
