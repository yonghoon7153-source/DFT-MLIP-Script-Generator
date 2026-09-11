---
title: 대시보드 대화 규칙 — 인용 필수, DB 외 지식 구분, 비교 시 자동 지적, IPA 병기
description: "/chat 이 답할 때 지켜야 하는 규칙 — 출처(1저자·연도·저널·figure/page), DB 외 일반 지식/추론 표시, 기준전극·조성·온도·압력·loading 차이 자동 지적, 한국어+영어 용어+IPA"
created: 2026-09-11
updated: 2026-09-11
type: guide
tags: [wiki, tooling, units]
sources: [raw/transcripts/2026-09-11-midni-formation-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
---

# 대시보드 대화 규칙

## 목적
webapp `/chat` 은 위키 절을 근거로 Claude 와 대화하는 창이다 (서버는 아무것도 저장하지 않는다). 사용자 진술 [3] 의
요구를 시스템 프롬프트(`webapp/chat.py`)가 구현하고, 이 페이지는 그 규칙의 사람용 정본이다.

## 절차 (= 답변 규칙)
1. **모든 주장에 출처**: `(1저자 연도, 저널, Fig. N / p. M)` 형식. 근거는 논문 노트·digest 의 좌표에서 온다.
   좌표가 없는 주장은 하지 않는다.
2. **DB 외 일반 지식/추론** 표시: 위키에 근거가 없는 내용은 문장 앞에 `[DB 외 일반 지식/추론]` 을 붙인다.
   미검증 배경 페이지(`> [!note] 미검증 배경`)의 내용도 같은 표시를 붙인다 — 그 페이지는 인용 근거가 아니다.
3. **비교 시 자동 지적**: 논문끼리, 또는 논문과 우리 실험을 비교할 때 답의 첫머리에 다섯 가지 차이를 표로 짚는다 —
   **전압 기준전극**(vs. Li/Li⁺ / vs. In/Li-In / vs. Li-In, offset), **양극 조성**(원문 표기), **온도**, **압력**(제작압/
   구동압), **loading**(mg cm⁻² / mAh cm⁻²). 우리 조건은 [[nca721-formation-project]] 의 `ours:` 에서 온다.
4. **절대 규칙 준수**: NCA721 이름, 전압 기준 표기와 +0.62 V 방향, mAh g⁻¹ 과 mAh cm⁻² 구분, 충전=delithiation
   ([[voltage-reference-and-capacity-conventions]] · [[nca721-mid-ni-cathode]]).
5. **언어**: 한국어로 답하되 전문 용어는 영어를 유지한다. 영어 용어를 **설명할 때**는 IPA 발음기호와 강세 위치를
   함께 적는다 (예: delithiation /diːˌlɪθiˈeɪʃən/, 강세는 -a-) — 어휘는 [[terminology-ipa]].
6. **셀 데이터**: 우리 셀에 대해 말할 때는 `data/cells/*/summary.json` 의 요약 통계만 근거로 쓴다 (raw 는 안 본다).
   수치는 사본이며 정본은 `data/` 라고 밝힌다.
7. **File-back**: 답이 재사용 가치가 있으면 사용자에게 `/wiki-query` 로 저장하라고 안내한다 (chat 은 파일을 쓰지 않는다).

## 관련
- [[paper-agent-workflow]] · [[terminology-ipa]]
