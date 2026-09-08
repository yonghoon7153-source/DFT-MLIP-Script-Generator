---
title: "리뷰 요청 BI — 웹앱 철회 결속을 claim ID 구조로 바꿨습니다 (BG ② 이행) + 남은 다섯의 마감 조건"
date: 2026-09-08
updated: 2026-09-08
tags: [review, codex, prompt, webapp, governance, claim-binding]
status: 작성 — 발송 대기
kind: review-prompt
system: repo
confidence: medium
verificationStatus: unverified
explored: false
authoredBy: agent
claimType: prescriptive
evidenceScope: multi-source-primary
---

# 리뷰 요청 BI

> 앞 요청: `codex_BG_prompt_webapp_aw_release_2026_09_07.md` (AW 해제조건 6건 + 판정 셋)
> 대상 브랜치: `claude/friendly-meitner-lldvar` · 대상 커밋 `10fd99b0b`
> 이번 요청은 **하나**입니다 — BG ②(철회 결속)를 구조로 바꿨는데, **그 구조가 맞는지**와
> **남은 다섯을 어떤 조건에서 닫을지**를 봐 주십시오.

---

## 0. 먼저 자백할 것 — 이 요청의 제일 약한 고리

**BG ② 를 "이행" 이라 부르지만, 실제로 결속된 것은 18곳 중 3곳입니다.** 나머지 15곳은
"더 나빠지지 않는다" 만 보장하는 래칫에 묶어 뒀습니다. 저희는 이것을 완료가 아니라
**구조 전환 + 이주 시작**으로 보고 있고, 그 판단 자체를 검토받고 싶습니다.

그리고 종전 검사가 **초록이었는데도 실제로 누출이 있었습니다.** 아래 §1 이 그 실측입니다.

---

## 1. 무엇이 틀렸었나 (실측)

종전 결속 검사는 *"철회값 앞뒤 140자 안에 금지 표지(⛔·철회·보류…)가 있나"* 였습니다.
세 가지가 동시에 틀렸습니다.

| | 결함 | 실측 증거 |
|---|---|---|
| ① | 표지가 **그 값에 대한 것인지** 못 본다 | 옆 문단의 ⚠ 도 통과로 셌습니다 |
| ② | 표 셀이 길면 표지가 창 밖으로 밀린다 | `/governance` 인용위험 표의 `Ea … 0.199±0.034` 행은 **스스로가 위험 경고**인데 미결속으로 잡혔습니다 |
| ③ | 검사 표면이 **손 목록 7개** 였다 | 28개 라우트 중 21개가 사각지대. 그 사각지대(`/governance`)에 **실제 미결속 노출이 있었습니다** |

③ 이 제일 나빴습니다. 검사가 초록인 이유가 "고쳤기 때문" 이 아니라 **"안 봤기 때문"** 이었습니다.

## 2. 무엇으로 바꿨나

**결속을 근접성이 아니라 구조로 만들었습니다.** 철회·비인용 값을 그리는 요소(또는 그 조상)가
`data-claim="<metric>@<system>"` 로 **어느 주장인지 이름을 대야** 결속입니다. 이름이 맞으면
근접성은 보지 않습니다 — 표 안이든 긴 문단이든 결속이 성립합니다.

- `webapp/canonical.py`
  - `claim_id(metric, system)` → `"<metric>@<system>"` (레지스트리 파생 · 별도 목록 없음)
  - `bound_claims()` — `status=retracted` + `citable:false`. **4글자 미만 숫자는 스캔에서 뺍니다**
    (σ 비의 `1.08` 같은 값을 전 화면에서 찾으면 무관한 표에 걸려 검사가 소음이 됩니다) →
    그런 항목은 **id 유효성만** 검사합니다. ← **Q3 의 대상입니다.**
  - `scan_claim_bindings()` — stdlib `html.parser` 로 `data-claim` **조상 추적**.
    `bound` / `unbound` / `dangling`(레지스트리에 없는 id 선언)을 돌려줍니다.
    유령 판정은 **레지스트리 전체** 기준입니다(결속 대상만으로 하면 정상 항목 참조가 유령이 됩니다 — 실측 정정).
- 배선한 곳 — `/governance` 인용위험 표(`citation_hazards` 에 `claim` 필드 신설),
  같은 화면 게이트 평가 표(`claim_ref` 의 `value:M/S` → `claim_ref_to_id()`), `/log` 저널 항목.
- **저널 본문은 고치지 않았습니다.** 2026-08-06 기록의 *"MD Ea(0.199)가 modelc(0.197)와
  사실상 같다"* 는 당시 판단이라 지우지 않고 `claims` 필드로만 결속했습니다. ← **Q4.**
- 시험 — 라우트 **자동 열거**(손 목록 폐기) + 구조 결속 + 레거시 래칫 + 유령 id + 음성 7건.
  음성 중 핵심: *근접 표지만 있고 id 가 없으면 여전히 `unbound`* (±140자 방식으로의 회귀 차단).

현황: **결속 3 · 미결속 15(8화면) · 유령 0** · webapp 시험 171 통과 · convention 0 위반.

---

## 3. 여쭙는 것

### Q1. 이 결속 구조가 맞습니까?
`data-claim` 조상 추적으로 "이 숫자는 어느 주장인가" 를 선언시키는 방식이 옳은 층위인지.
저희가 못 보는 우회로가 있습니까 — 예를 들어 **선언이 거짓인 경우**(아무 값에나 붙이는 것)를
`dangling` 만으로 막는 것이 충분합니까?

### Q2. 래칫이 이주 장치로 정당합니까, 누출을 덮습니까?
`_LEGACY_UNBOUND = {"/":1, "/cascade":1, "/compare":1, "/explorer":1, "/glossary":1,
"/methods":4, "/requests":4, "/todo":2}`. 목록 밖 화면은 미결속 0 강제, 목록 안은 **늘면 실패**,
**줄었는데 표를 안 줄여도 실패**(표가 실물보다 헐거워지는 것 차단).
이것이 "안 고치고 통과시키는 장치" 로 쓰일 위험을 어떻게 보십니까.

### Q3. 숫자 없는 금지 주장은 화면에서 어떻게 강제합니까?
σ 비 3항목(`MD_sigma_ratio_{600,800,1000}K`)은 `value` 가 없고 표시 문자열(`1.08 ± 0.18`)만
있습니다. 금지 목록은 `statistically_equivalent_transport`·`conductivity_preserved`·
`any_ranking_claim` 처럼 **문장 수준**입니다. 지금 저희 검사는 이걸 **못 잡습니다**(id 유효성만 봅니다).
어휘 매칭은 오탐이 클 것 같아 안 넣었는데, 이 공백을 메울 방법이 있습니까 — 아니면
"화면 검사로는 못 잡는다" 를 명시하고 다른 층(원고 체크리스트)으로 넘기는 것이 맞습니까?

### Q4. 이력을 고치지 않고 결속만 붙인 처리가 맞습니까?
저널의 옛 문장은 **당시 판단**이고, 그 값은 나중에 철회됐습니다. 저희는 본문을 보존하고
`claims` 로만 결속했습니다. 다만 그 문장은 지금 기준으로는 금지 주장
(`statistically_equivalent_transport`)에 해당합니다. 보존이 맞습니까, 아니면 결속에 더해
**그 자리에서 철회 사실을 함께 렌더**해야 합니까?

### Q5. 남은 다섯의 **마감 조건**을 무엇으로 잡아야 합니까?
미이행: **hazard 전행·전필드 대조**, **P1 Q2(화면 파생 fit 출처)**, **Q4(카드 범위)**, **Q5**,
**Q7(별칭 3상태)**. 저희 규율은 *"닫힘 조건을 먼저 박고, 채워졌으므로 닫는다"* 입니다
(SDCP 를 조건 없이 두 번 닫았다 두 번 물린 뒤 채택). 그래서 **닫기 전에** 조건을 적으려 하는데,
래칫을 몇까지 내려야 "결속 이행" 입니까 — 0 입니까, 아니면 현재-facing 화면만 0 이면 됩니까?

---

## 4. 확인 방법 (재현)

```bash
git checkout claude/friendly-meitner-lldvar && git log -1 --format=%H   # 10fd99b0b…
python3 -m pytest webapp/tests -q                                       # 171 passed
python3 - <<'PY'
import sys; sys.path.insert(0,"webapp"); import app as A, canonical as C
cl = C.bound_claims(); c = A.app.test_client()
for u in sorted({str(r) for r in A.app.url_map.iter_rules()
                 if not r.arguments and "GET" in r.methods
                 and not str(r).startswith(("/static","/api"))}):
    r = c.get(u)
    if r.status_code != 200 or "html" not in (r.headers.get("Content-Type") or ""): continue
    s = C.scan_claim_bindings(r.get_data(as_text=True), cl)
    if s["bound"] or s["unbound"] or s["dangling"]:
        print(f"{u:16s} bound {len(s['bound'])} · unbound {len(s['unbound'])} · dangling {s['dangling']}")
PY
```

## 5. 저희가 답을 못 내는 것 (사실 보고)

- **Codex 는 이 변경을 아직 못 봤습니다.** v40 R4 에서 배운 구분(소스 수정 확인 ≠ 승인)이
  여기도 걸립니다 — 저희가 "고쳤다" 고 닫으면 그 상황이 반복됩니다.
- 래칫 15건의 이주 **순서**를 정하지 못했습니다. `/methods`·`/requests` 가 4건씩으로 가장 많은데,
  그 화면들은 표가 아니라 산문이라 결속 단위(문단? 표행? 값?)를 무엇으로 잡을지 미정입니다.
- `citation_hazards` 25행 중 `claim` 을 단 것은 **1행**입니다. 나머지 24행에 claim 을 다는 것이
  hazard 전행 대조와 같은 작업인지, 다른 작업인지 저희 판단이 갈립니다.
