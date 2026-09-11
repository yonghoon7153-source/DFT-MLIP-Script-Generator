---
title: "Li2S ASSB 위키 킥오프 세션 — 사용자의 연구 설명 원문과 설계 결정 (2026-09-11)"
source_url: local:claude-code-session/2026-09-11-li2s-wiki-kickoff
ingested: 2026-09-11
sha256: 8d2f757fe0c70ea413c3f546ae115a7178da7561eec25871e9e82f9231966cab
---

# Li2S ASSB 위키 킥오프 세션 (2026-09-11)

수집 목적: 이 저장소(`main`)를 Li2S 양극 all-solid-state Li–S 연구의 mothership 위키 +
로컬 webapp 으로 세우기로 한 세션의 **설계 기록**. 사용자의 연구 상황 설명은 이 위키의
시드 페이지(entity·concept·question)의 1차 근거이므로 **원문 그대로** 보존한다.

## 1. 사용자의 연구 설명 (원문, 2026-09-11)

> 나는 지금 Li2S 양극활물질을 활용한 all-solid-state lithium-sulfur batteries에 대한 연구를
> 수행하고 있어. 현재 pristine Li2S 양극활물질을 활용해서 reference cell을 문헌에서 주로
> 보고되고 있는 500~600mAh/g의 비용량을 뽑아내는 것을 목표로 연구를 수행중이고, 해당
> 연구가 끝난 후에는 음극에 기존에 사용하던 Li-In anode 대신 anode-free configuration을
> 적용할 예정이야. 현재 복합양극은 Li2S, argyrodite LPSCl, acetylene black을 30:50:20의
> 질량비로 혼합하여 사용하고 있고, 그 과정에서 세가지 물질을 일괄적으로 ball milling하여
> 양극을 제작하는 one-step mixing process, Li2S-C nanocomposite을 여러가지 방법을 통해
> 제작한 후 LPSCl을 mild mixing 또는 ball milling을 활용하여 추가적으로 혼합하는 two-step
> mixing process, 마지막으로 Li2SO4를 PVP 용액에 용해시킨 후 600~700도에서
> carbonization 이후 900도까지 승온시켜서 Li2S-C nanocomposite을 만든 후 LPSCl을
> 혼합한다거나, Li2S, C, LPSCl을 각각 anhydrous ethanol에 용해시킨 후 stirring 등의 과정을
> 거쳐서 Li2S-LPSCl-C 혼합 composite을 형성하는 등의 방법들을 고려하고 있어. 현재
> 주요하게 사용하는 방법은 ball milling, high energy ball milling (또는 planetary ball
> milling), Thinky ARE-310을 활용한 mixing process 등이 있어.

> 앞으로 내가 주로 할거는 지금까지 내가 모아놨던 li2s 또는 sulfur 관련된 논문을 너한테
> 공유를 해주고 그걸 논문 에이전트로 db화를 하고 서로 논문끼리 비교를 하고, 이
> 대시보드에서는 그 논문 reference를 바탕으로 나랑 얘기해줬으면 좋겠어.

## 2. 설명에서 읽어 낸 사실 (1차 근거로 삼는 것)

| # | 사실 | 확실성 |
|---|---|---|
| F1 | 시스템: **all-solid-state Li–S**, 양극 활물질 **pristine Li2S**, 고체전해질 **argyrodite LPSCl** (Li6PS5Cl 로 추정 — 사용자가 화학식을 적지는 않았다) | 사용자 진술 |
| F2 | 현재 음극 **Li–In**, 다음 단계 **anode-free** | 사용자 진술 |
| F3 | 복합양극 **Li2S : LPSCl : acetylene black = 30 : 50 : 20 (질량)** | 사용자 진술 |
| F4 | 1차 목표: reference cell 에서 **500–600 mAh g⁻¹** — "문헌에서 주로 보고되는" 값. **정규화 기준(Li2S 질량인지 S 질량인지)은 명시되지 않았다** | 사용자 진술 + 미확인 |
| F5 | 혼합 경로 후보: (a) one-step — 세 성분 일괄 ball milling, (b) two-step — Li2S–C 나노복합체 선제작 후 LPSCl 을 mild mixing 또는 ball milling, (c) Li2SO4 + PVP 용액 → 600–700 °C 탄화 → 900 °C 승온 → Li2S–C 나노복합체 → LPSCl 혼합, (d) Li2S·C·LPSCl 을 각각 anhydrous ethanol 에 용해/분산 → stirring → Li2S–LPSCl–C 복합체 | 사용자 진술 |
| F6 | 장비: ball milling, high-energy(planetary) ball milling, **Thinky ARE-310** (자전·공전 믹서) | 사용자 진술 |
| F7 | 운영: 논문을 논문 에이전트로 DB 화 → 논문끼리 비교 → 대시보드에서 논문 근거로 대화 | 사용자 진술 |
| F8 | 환경: **Ubuntu (WSL)**, 명령은 WSL 에서, alias `li2s` 한 단어로 webapp 진입 | 사용자 진술 |

## 3. 이 세션의 설계 결정

1. **저장소 배치**: `main` 브랜치를 Li2S ASSB 연구의 mothership 으로 쓴다. 다른 브랜치
   (DEM/MPM·열화 degeneracy·argyrodite ML 등)는 별개 프로젝트이며 merge 하지 않는다
   (루트 `BRANCHES.md`).
2. **위키 하네스**: llm-wiki-kit(260730) 을 repo root `wiki/` 로 이식하되, 커맨드 `wiki-*`
   접두·hook 위치·repo-root 상대 경로·`<action>(wiki):` 커밋 접두는 선행 브랜치의 적응을
   그대로 따른다. `no-hardcoded-branch-name` lint 검사도 유지한다.
3. **논문 에이전트**: `.claude/agents/paper-curator.md` 를 Li2S/ASSB 축(활물질·SE·탄소·혼합
   공정·활성화·음극)으로 재작성. digest 는 `[인쇄]/[도표]/[해석]/[재현]` 4구분, sha256 봉인,
   그림 크로핑 필수, **frontmatter `compare:` 블록**으로 논문 간 비교 축을 구조화한다.
4. **webapp**: 선행 브랜치의 Flask 열람기 포맷을 이식하고, 이 연구용으로 `/roadmap`
   (연구 개요), `/compare` (논문 비교표 — digest 의 `compare:` 를 표로), `/chat` (위키 근거
   대화 — 서버가 Anthropic API 를 호출하되 키는 환경변수, 저장소에는 아무것도 쓰지 않음) 를
   더한다. 기본 바인딩 127.0.0.1, 읽기 전용 guard 유지 (`/api/chat` 만 POST 허용).
5. **첫 ingest**: Kim et al. 2023 Carbon Energy (사용자 세미나 논문) — digest + 세미나 준비
   페이지([[kim2023-seminar-prep]]).
6. **단위 규율**: 위키의 모든 비용량은 `mAh g⁻¹(S)` 인지 `mAh g⁻¹(Li2S)` 인지 **반드시** 적는다
   (F4 의 미확인 때문에 필요해진 규칙).

## 4. 미결 (사용자에게 확인할 것)

- Q1. 500–600 mAh g⁻¹ 의 정규화 기준 (Li2S 기준이면 S 기준 716–860 mAh g⁻¹ 에 해당).
- Q2. LPSCl 의 정확한 조성(Li6PS5Cl / Li5.5PS4.5Cl1.5 등)과 공급원.
- Q3. 현재 reference cell 의 사이클 프로토콜 (전압창 vs Li–In, C-rate, 온도, 스택 압력).
- Q4. 지금까지 실제로 얻은 최고 비용량과 그때의 혼합 경로.
