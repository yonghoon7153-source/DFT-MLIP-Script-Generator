# BRANCHES.md — 이 저장소의 브랜치 지도 (Li2S ASSB 브랜치 관점)

작성: 2026-09-11. 이 저장소는 이름만 하나이고 실제로는 **서로 무관한 프로젝트 여럿이 브랜치로
병렬 존재**한다. `main` 은 GitHub 이 만든 `Initial commit` 하나뿐이다 (2026-09-11 에 잠시 Li2S 작업이
올라갔다가 사용자 요청으로 **`claude/li2s-assb-wiki`** 브랜치로 이전하고 `main` 은 되돌렸다).

## 규칙

1. **`claude/li2s-assb-wiki` = Li2S ASSB 연구** (`wiki/` · `webapp/` · `.claude/` · `scripts/` · 루트 문서).
   이 브랜치에서는 이 경로들만 건드린다. `main` 은 비워 둔다.
2. **다른 계열 브랜치를 이 브랜치로 merge 하지 않는다.** 같은 경로 이름(`webapp/`, `wiki/`, `.claude/`)을
   다른 내용으로 쓰는 브랜치가 있어 합치면 충돌만 남는다.
3. 원격 브랜치 삭제는 **사람 승인 후에만**.
4. 브랜치 이름의 정본은 루트 `CLAUDE.md` 하드룰 1 하나다. 위키·스크립트는 이름을 옮겨 적지 않는다
   (`wiki/tools/lint.py` 의 `no-hardcoded-branch-name` 검사).

## 계열 (관측 — 정확한 tip 은 `git branch -r` 로 그 자리에서 센다)

| 계열 | 무엇 | `main` 과의 관계 |
|---|---|---|
| **Li2S ASSB** (`claude/li2s-assb-wiki`) | 이 문서가 속한 것 | — |
| 배터리 열화 degeneracy | PyBaMM 합성 truth 로 LLI/LAM fitting degeneracy 판별, 게이트 리뷰 루프, 자체 wiki/webapp | **이 브랜치의 webapp·wiki 하네스의 원형** — 코드 포맷을 가져왔고 내용은 가져오지 않았다 |
| DEM/MPM | LIGGGHTS/MPM 복합 양극 시뮬레이션 | 무관 |
| 저항 네트워크 / GB 보정 | `dem_scripts/`, `GB_correction_*` | 무관 |
| argyrodite ML | `db/ kb/ tools/` | 무관 (도메인은 가깝지만 코드는 별개) |
| 웹앱/기타 | DFT 입력 생성기(Vite/React), 챗봇, 발표자료 | 무관 |
| 타임로그/lineage | `TIMELOG.md`, `archive/ data/ db/` | 무관 |

## 재현 명령

```bash
git fetch origin
git branch -r | grep -v HEAD                         # 전체 목록
git log --oneline origin/claude/li2s-assb-wiki | head   # 이 브랜치의 이력
git merge-base --is-ancestor origin/main origin/<b> && echo "main 은 <b> 의 조상"
```

`origin/main` 의 첫 커밋(`Initial commit`)은 모든 브랜치의 공통 조상이다 (선행 문서의 실측). 그래서
"main 이 고립돼 있다" 는 진단은 shallow clone 의 착시다 — `git fetch --unshallow` 후 다시 본다.
