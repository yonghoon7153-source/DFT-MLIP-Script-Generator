---
title: "코팅 계보 #6·#7·#8 digest 가 서로 다른 말을 하는 세 자리 — 우리 값이 문헌의 어느 양인가"
date: 2026-09-13
updated: 2026-09-13
tags: [coating-lineage, litdb, esw, citation-hazard, reduction-limit]
status: open
confidence: medium
verificationStatus: unverified
explored: false
authoredBy: agent
effort: medium
claimType: interpretive
evidenceScope: multi-source-primary
feedsInto: kb/syntheses/cathode_coating_computational_lineage.md
---

## 질문

같은 날 나온 계보 digest 셋(#6 Honrao 2021 · #7 Nolan 2018 · #8 Xiao 2020)이 **세 자리에서 서로 다른 말을
한다.** 셋 다 우리 값을 문헌에 붙이는 대목이라, 합치기 전에 갈라야 한다.

> ⛔ 이 카드는 **판정이 아니다.** MERGE(2026-09-13) 때 세 digest 를 공유 파일에 합치면서
> **조용히 한쪽으로 정리하지 않으려고** 따로 뺀 것이다. 해소는 1저자 또는 별도 조사.

---

## 충돌 1 — ★ **1.7 V 근처 숫자가 셋인데, 우리 것이 어느 쪽인가**

우리 원장에는 1.7 V 근처 값이 **둘** 있고, 두 digest 가 **서로 다른 쪽**을 문헌의 *reduction/cathodic limit*
자리에 놓았다.

| digest | 우리 값 | 문헌 값 | 주장 |
|---|---|---|---|
| **#6 Honrao 2021** | `ocv_self_decomposition_V` **1.717** | `Li₆PS₅I` **1.722** · `Li₃PS₄` **1.702–1.722** (figure-read) | `Fig. S2` 의 *"Li uptake = 0 평탄구간"* 정의로 재면 **1.717 이 그 자리**이고 `reduction_limit_V` 1.242 는 **다른 양**이다 |
| **#7 Nolan 2018** | `reduction_limit_V` **1.242** | LGPS **1.7** (`Fig. 6A`) | **1.242 가 그 자리**이고 0.46 V 차가 문제다. 우리 **1.717** 과 `Fig. 6A` 의 **1.72** 의 일치는 **우연**이다 (그쪽은 *LGPS 의 환원한계*, 우리는 *`Li₆PS₅Cl` 중성 자기분해 OCV*) |

**둘 다 맞을 수는 없다.** 갈라야 하는 것:

1. 우리 `reduction_limit_V` **1.242** 와 `ocv_self_decomposition_V` **1.717** 은 **각각 어떤 연산으로 나온 값인가.**
   (grand-potential 개방계에서 μ_Li 를 올리며 상평형이 깨지는 φ 인가, 아니면 닫힌계 자기분해 반응의 OCV 인가.)
2. #6 의 *"Li uptake = 0 평탄구간"* 정의와 #7 의 *"reduction reaction 이 열역학적으로 유리해지는 전위"* 정의가
   **같은 양인가.**
3. 셋 중 어느 것이 `db/properties/canonical_registry.json` 의 정의와 일치하는가.

⚠ **숫자 일치가 우연인 사례가 이미 확인됐다**(#7). 그러니 *"값이 비슷하니 같은 양"* 논증은 이 자리에서 금지다.
`citation_hazards.json` 에 항목을 세울지도 같이 판단한다.

---

## 충돌 2 — #7 카드가 *"정의 문장이 있는 유일한 편"* 이라 적었는데 #8 에도 있다

계보 카드가 #4·#5 digest 끝에 남긴 물음 — *"anodic limit 의 정의가 활자로 있는가"* — 에 대해

- **#7 digest**: 있다. *Joule* **2**, p. 2022, Eq 4 직후.
  *"The cathodic and anodic limits of a material are the potentials at which the reduction and the oxidation
  reactions become thermodynamically favorable, respectively."*
- **#8 digest**: *"#7 카드가 '정의 문장이 있는 유일한 편' 이라 적었는데 **#8 에도 있다**"* — §7c 에 우열표를 넣고
  **#7 카드 완화 편집이 필요**하다고 §10-12 에 기록했다(남의 파일은 안 건드렸다).

⇒ **#7 행의 "유일한" 을 지우고 두 편을 같이 세우는 편집이 필요하다.** 다만 어느 쪽 문장이 더 연산적인지
(=우리가 2.256 V 를 인용할 때 어느 쪽을 대야 하는지)는 두 digest 의 §7c·§4e 를 나란히 놓고 봐야 한다.

⚠ 두 digest 가 **공통으로** 말하는 것 하나는 확실하다: **연산 규칙**(`E_D^open(φ) ≠ 0` 인 최초 φ)은
**계보 8편 통틀어 없다.** #5 가 식을 주고 #7·#8 이 정의를 준다 ⇒ **우리 원고는 우리 정의를 스스로 써야 한다.**

---

## 충돌 3 — "황화물 계보 최초" 는 누구도 아니다 (초고 주장 철회됨)

#8 초고가 *"황화물이 계보에서 처음 다뤄진다"* 고 썼다가, 동시에 돌던 #7 digest 를 확인하고 **4곳에서 철회**했다.

| | 황화물 취급 |
|---|---|
| #1–#6 | 없다 (#4 Ed 데이터셋 황화물 0 · #5 무대 가넷 · #6 `E_hull ≤30 meV` 가 `Li₆PS₅Cl`·`Li₆PS₅Br` 을 자른다) |
| **#7 Nolan 2018** | **수치를 준다** — LGPS 가 전편 중심, `Li₆PS₅Cl` 본문 **3회**(p. 2031 창 1.7–2.4 V · p. 2036 계면산물 · p. 2040 Li 금속 type 3). **전용 소절은 없다** |
| **#8 Xiao 2020** | **전용 소절이 있다** — 「Sulfides」 대절 3.5 pp + 「Argyrodites」 소절 + `Fig. 5a` 에 `LPSCl` 이름. **고유 수치는 안 준다**(*"다른 황화물과 유사할 것"* 한 문장) |

⇒ **성격이 정반대인 두 편이 함께 우리 계를 들여온다.** 계보 카드 서사에 그렇게 적어야 하고,
*"최초"* 라는 말은 어느 쪽에도 붙이지 않는다.

⛔ 그리고 **염화물 SE 는 두 편 다 0 회**다 (#7 `Fig. 8` 의 "halides" 는 X ∈ {N,O,S,F} = **불화물**).
**Cl-rich 축은 여전히 문헌 공백**이고, 그것이 우리 캠페인의 자리다.

---

## 반론 / 이 카드가 틀릴 수 있는 곳

- **충돌 1 이 충돌이 아닐 수 있다.** #6 과 #7 이 *다른 논문의 다른 그림*을 읽은 것이므로, 두 논문이 각각
  자기 정의를 갖고 있고 우리 두 값이 각각 그 둘에 대응할 수도 있다. 그러면 "둘 다 맞을 수 없다" 는 내 문장이
  틀린다. **확인 순서는 우리 값의 연산부터**다 — 문헌이 아니라.
- **충돌 2 의 "완화 편집" 은 #8 digest 의 자기주장이다.** #7 의 문장과 #8 의 문장을 직접 나란히 놓고
  누가 더 연산적인지 보기 전까지는 #7 카드를 고치지 않는다.
- 충돌 3 은 이미 #8 이 스스로 철회했으므로 **분쟁이 아니라 기록**이다. 여기 둔 것은 계보 카드 서사에
  반영하기 위해서다.

## 다음

1. `db/properties/canonical_registry.json` 에서 `reduction_limit_V` · `ocv_self_decomposition_V` 두 항목의
   `method` · `source_path` 를 읽고 **각각 어떤 연산인지** 적는다. (계산 0 · 원장 읽기만)
2. 그 결과로 충돌 1 을 닫거나, 못 닫으면 `citation_hazards.json` 에 CONDITIONAL 항목을 세운다.
3. 충돌 2 는 #7·#8 digest 의 해당 절을 나란히 놓고 계보 카드 #7 행을 편집한다.
4. 충돌 3 은 계보 카드 "흐름 한 줄" 과 #7·#8 행에 이미 반영됐다 — 추가 작업 없음.
