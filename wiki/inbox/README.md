# Inbox — ingest 대기 큐

여기에 자료를 던져두면 `/paper`(논문) 또는 `/wiki-inbox`(그 밖)가 처리한다. 이 폴더의 파일은 **임시**다 —
ingest 가 끝나면 원문은 저장소에 남기지 않고(`.gitignore`), digest(`raw/papers/`)·노트(`papers/`)·크로핑
그림(`raw/figures/`)만 커밋된다.

넣는 방법:
- 논문 PDF(+Supplementary): 파일 그대로. WSL 에서 `midni paper <main.pdf> [<si.pdf> …]` 가 여기로 복사한다.
  Supplementary 는 본문 논문과 **같이** 넣는다 — 에이전트가 DOI 로 본문에 연결한다.
- 웹 글: 본문을 `.md` 나 `.txt` 로 저장
- URL 만 모아두기: `urls.md` 파일에 한 줄에 하나씩

처리 흐름: `/paper` → DOI 중복 확인 → digest(sha256) + 노트(`paper:` 스키마) + 그림 → 질문 카드 라우팅 →
index/log → lint 0 errors → inbox 원본 삭제.

이 README 는 삭제하지 않는다.
