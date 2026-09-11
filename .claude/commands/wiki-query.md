---
description: 컴파일된 위키를 근거로 질문에 답하고(출처·DB 외 구분·비교 시 다섯 차이), 재사용 가치가 있으면 file-back
---

> 이 위키는 repo root `wiki/` 하위다 (킷 원본과 배치가 다름 — `wiki/README.md` 참조). 아래 절차의 모든 경로는 repo root 기준이다. 절대 규칙(루트 `CLAUDE.md` 맨 아래)을 지킨다.

이 LLM Wiki 를 근거로 다음 질문에 답한다: $ARGUMENTS

절차 (webapp /chat 과 같은 규칙 — `wiki/guides/chat-citation-rules.md`):

1. `wiki/index.md` 에서 관련 페이지를 고르고 읽는다. 논문이면 노트(`papers/`)의 `paper:` 와 digest(`raw/papers/`)까지 내려간다.
2. 답변에 **사용한 페이지와 좌표를 명시**한다: 논문은 `(1저자 연도, 저널, Fig. N / p. M)`. 인용하는 페이지의 `verificationStatus`·
   `confidence`·`evidenceScope` 를 확인해 — verified + high 면 단언, unverified 나 medium 이하면 그렇다고 밝히고, disputed 면 양쪽 제시.
   `> [!note] 미검증 배경` 페이지의 내용은 `[DB 외 일반 지식/추론]` 으로 표시한다.
3. 위키에 근거가 없으면 없다고 말한다. 지어내지 않는다.
4. 논문끼리 또는 논문과 우리 실험을 비교하면 **전압 기준전극·양극 조성(원문 표기)·온도·압력(제작/구동)·loading** 차이를 먼저 표로 짚는다.
   우리 조건은 `wiki/entities/nca721-formation-project.md` 의 `ours:`. 우리 셀 수치는 `data/cells/*/summary.json` 요약만 본다.
5. 영어 용어를 설명할 때는 IPA·강세를 붙인다 (`wiki/guides/terminology-ipa.md`).
6. **File-back 판단**: 답변이 한 번 쓰고 버리기 아까운 것(비교, 의사결정, 종합)이면 `wiki/queries/` (비교성이면 `wiki/comparisons/`) 에
   저장을 제안한다. 저장 시: SCHEMA frontmatter (`type: query`, `explored: false`, `verificationStatus: unverified`), 질문/짧은 답/근거/관련 구조,
   `wiki/index.md` 등록, `wiki/log.md` 에 `## [YYYY-MM-DD] query | {질문}` 기록, lint 실행.
