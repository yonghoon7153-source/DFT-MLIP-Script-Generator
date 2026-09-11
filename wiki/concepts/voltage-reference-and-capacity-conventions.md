---
title: 전압 기준전극·용량 단위·충방전 용어 규약 (절대 규칙 2·3·4)
description: "vs. Li/Li⁺ = vs. In/Li-In + 0.62 V 변환의 방향, 비용량 vs 면적용량, 충전=delithiation — 위키·webapp·대화가 공유하는 표기 규약과 흔한 실수"
created: 2026-09-11
updated: 2026-09-11
type: concept
tags: [units, reference-electrode, cell-data]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
---

# 전압 기준전극·용량 단위·충방전 용어 규약

## 정의
루트 `CLAUDE.md` [절대 규칙] 2·3·4 의 실무판. 사용자 진술(킥오프 기록 F9·F13)이 근거이며, 상수의 정본은
`config/cells.yaml` 이다.

### 1. 전압에는 항상 기준전극
- 우리 raw 데이터의 전압은 **vs. In/Li-In** 으로 기록된다.
- 변환식: **vs. Li/Li⁺ = vs. In/Li-In + 0.62 V**. 반대 방향은 **vs. In/Li-In = vs. Li/Li⁺ − 0.62 V**.
- 예: main cycle 창 2.5–4.4 V vs. Li/Li⁺ ↔ 장비 설정 1.88–3.78 V vs. In/Li-In. formation cut-off 4.0 V vs. Li/Li⁺ ↔
  3.38 V vs. In/Li-In.
- 논문 값은 **원문 값 + 원문 기준**을 그대로 적고(`voltage.raw_text`·`reference_raw`), 변환값은 사용한 offset 과
  함께 별도 필드(`window_vs_li`·`offset_applied_v`)에 적는다. 논문의 Li-In 음극이 우리와 조성이 다르면 그 논문의
  offset 도 다를 수 있다 — 논문이 자기 offset 을 밝혔으면 그 값을 쓰고 `notes` 에 적는다.
- LTO 음극 셀(operando 압력)의 전압은 full-cell 값인지 vs. Li/Li⁺ 환산인지 반드시 적는다.

### 2. 비용량 ≠ 면적용량 ≠ 절대용량
- **비용량** mAh g⁻¹ — 우리 데이터의 기본 단위. 분모는 **활물질 질량**(registry `active_mass_mg`). 전극 질량이나
  복합체 질량이 분모이면 반드시 그렇게 적는다.
- **면적용량** mAh cm⁻² — 설계 기준(2 mAh cm⁻²)·loading 비교용. 비용량과 섞어 쓰지 않는다.
- **절대용량**(mAh) 으로는 보고하지 않는다 — raw 의 `charge_q`/`discharge_q` (Ah) 는 import 단계에서 mAh g⁻¹ 로
  바꾸고, 절대값은 계산 중간값으로만 둔다.
- 논문의 비용량은 분모(활물질/복합체)와 활물질 함량을 `performance.notes` 에 적어야 비교가 된다.

### 3. 충전 = delithiation, 방전 = lithiation
- 양극 기준 용어다. "충전 cut-off" 는 delithiation 의 상한 전위를 뜻한다.
- LTO 음극 셀·3-전극 셀에서도 양극 기준으로 같은 말을 쓴다.

## 왜 중요한가
0.62 V 는 formation cut-off 6 수준의 간격(0.2 V)의 세 배다 — 기준을 빠뜨리면 DOE 수준이 통째로 어긋난다.
비용량과 면적용량을 섞으면 loading 이 다른 논문과의 비교가 무의미해진다.

## 이 위키에서의 적용
- lint: `canonical-offset`(0.62 사본 대조) · `voltage-reference`(기준 없는 전압 경고) · `unit-rule`(절대용량 경고).
- webapp: `/cells` 는 원본과 변환 전압을 둘 다 보인다 ([[cell-data-module]]); `/compare` 는 원문 기준과 변환값을
  나란히 둔다; `/chat` 은 비교 시 기준전극 차이를 먼저 짚는다 ([[chat-citation-rules]]).

## 관련
- [[cell-registry]] · [[formation-preconditioning-protocol]] · [[nca721-mid-ni-cathode]]
