# 61차 게이트 리뷰 작업 상태 (정본)

판정: **NO-GO** (2026-09-09). 새 **P0 2건 · P1 4건 · P2 1건**.
검토 head `f7cce7406e9ac233ad4727f6fa3bb4fc538b1de9` · 판정 대상 RUN_SCOPE
`c4e710040c2631d4f8140ee31c2f3c5004d9bcbb` · `source_digest d29650980daf6b9a`
(실측 일치 확인됨).

리뷰어가 **새 발견으로 세지 않은 것**: 요청문 §0 의 미착수·신고 항목,
환경 결손(`pybamm`·`tqdm` 부재)으로 인한 전체 회귀·lifecycle E2E 중단,
리뷰어 환경 receipt 가 달라 fail-closed 한 coverage 합집합.
`--check-preimages` 통과 · 60차 전용 회귀 49건 전부 통과 · wiki lint 0 errors.

## 판정의 한 문장

> **가장 강한 반례 둘은 공격이 아니라 정상 production 순서다.**

60차에도 같은 문장을 들었고, 같은 실수를 한 번 더 했다. 60차는 "report 를
**처음** 더하는" 경우만 시험했고, 61차가 낸 것은 "**이미 report 가 있는**
run 을 resume 한 뒤 그 report 를 갱신하는" 경우다. 시험이 production 의
**순서**가 아니라 순서의 **한 조각**을 봤다.

## 발견 원장

| ID | 무엇이 틀렸나 | 무효화하는 것 | 묶음 | 상태 |
|---|---|---|---|---|
| P0-1 | resume 시 시간 봉인이 **옛 report 를 흡수**한다. 이어지는 정상 report 갱신이 봉인을 stale 로 만들고, 새 content id 에는 class 가 없어 마지막 승격이 거부된다 | P0-1 종결 · 정상 resume 가용성 · execution class | α | 착수 |
| P0-2 | fit 이 논리 경로를 `/proc/self/fd/N` 으로 **대체**하고 그것을 durable manifest·summary·phase receipt 에 적는다. 성공하면 fd 가 닫히고 staged input 도 지워져 **존재하지 않는 경로가 provenance 가 된다** | P0-4 종결 · provenance · 재현 명령 | β | 대기 |
| P1-1 | capability 를 **마지막 사용자보다 먼저** 닫는다 — 닫힌 경로로 phase receipt 를 쓰고 lock 삭제가 `OSError` 를 삼켜 `.fit.lock` 이 남는다 | staged handle 수명 · phase receipt · 정상 cleanup | β | 대기 |
| P1-2 | 복수 `PYTHONPATH` root 의 **동명 module** 이 basename key 하나로 합쳐진다 (root 순서를 뒤집으면 digest 가 바뀐다) | P1-4 importable roots 증언 | γ | 대기 |
| P1-3 | startup-history **측정 실패**가 성공 영수증이 된다 (`{"<unmeasured>": "1"}`) — child rc 미검사 · 해석 실패 누락 · 예외를 정상 dict 로 | P1-3 증언 · coverage evidence 의 fail-closed 주장 | γ | 대기 |
| P1-4 | comprehension 결속을 **부모 scope 에 적용**한다 (Python 3 에서 comprehension target 은 별도 scope) | P0-11 scope 모델의 정확성 | δ | 대기 |
| P2 | `STAGE3_CONTRACT.md:1071` 은 AST 정규형에서 docstring 이 사라진다고 적는데 현재 코드는 보존한다 — 계약 문구가 현재 규칙과 **반대** | 계약 문서의 정확성 | ε | 대기 |

## 묶음

| 묶음 | 축 | 발견 |
|---|---|---|
| α | 내용 identity 의 **member 집합을 무엇이 정하는가** — 우연한 파일 존재가 아니라 선언 | P0-1 |
| β | **논리 경로와 I/O handle 경로의 분리** · capability 수명 | P0-2 · P1-1 |
| γ | 증언의 **키 공간과 실패 전파** | P1-2 · P1-3 |
| δ | producer scope 모델을 Python 과 맞춘다 | P1-4 |
| ε | 계약 문구 | P2 |

## 이번 라운드의 규율 (60차에서 이어받음)

- 발견마다 **RED 를 먼저 눈으로 본다**. 리뷰어 반례는 그대로 회귀로 고정한다.
- **production 의 순서 전체**를 도는 회귀를 쓴다. 조각만 보는 시험이 60차
  P0-1 을 통과시켰다.
- 방어를 심으면 **축을 심는다**. 그리고 방어를 넓히면 **다른 시험의 축이
  가려지는지** 마감에 다시 센다 (60차에 네 번 났다).
- 새 시험이 처음부터 통과하면 fixture 가 진실을 가린 신호다.

## 좌표

- 봉인: `tools/preserve.py` `RUN_MANIFEST_SCHEMA:4254` · `_sealed_manifest_parts` ·
  `_present_manifest_parts:4420` · `seal_run_identity:4446` · `run_content_id:4528`
- staging: `src/fitting.py:1011`(경로 대체) · `:1571`(`manifest.input`) ·
  `:1587`(`fits_parquet`) · `:1594-1597`(commit 뒤 fd 경로 반환) ·
  `:1028`(phase receipt) · `:1031`(lock 삭제)
- lock 삭제가 오류를 삼키는 자리: `src/io.py:518`
- 증언: `docs/22p_gap/mutation_replay.py:4295`(child rc) · `:4305-4312`(해석·예외) ·
  `:4322`(basename key) · `:4423-4429`(receipt reader)
- scope: `docs/22p_gap/row_projection.py:1427`(`_own_shadows`) · `:1456-1467`
- 계약: `docs/22p_gap/STAGE3_CONTRACT.md:1071`
