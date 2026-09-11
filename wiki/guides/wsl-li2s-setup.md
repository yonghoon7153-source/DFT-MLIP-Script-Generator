---
title: WSL(Ubuntu) 에서 li2s webapp·논문 도구 세팅
description: "Ubuntu/WSL 에서 이 저장소를 받아 li2s 한 단어로 대시보드를 열고, PDF 를 inbox 에 넣고, /chat 용 API 키를 두는 절차"
created: 2026-09-11
updated: 2026-09-11
type: guide
tags: [tooling, wiki]
sources: [raw/transcripts/2026-09-11-li2s-wiki-kickoff-session.md]
confidence: medium
explored: false
verificationStatus: unverified
claimType: prescriptive
evidenceScope: user-original
---

# WSL(Ubuntu) 에서 li2s webapp·논문 도구 세팅

## 목적
사용자 환경은 **Windows + WSL Ubuntu**. 모든 명령은 WSL 셸에서 실행한다. 목표는
`li2s` 한 단어로 대시보드가 브라우저에 뜨는 상태.

## 절차

### 1. 저장소 받기 (한 번)
```bash
cd ~ && git clone <이 저장소 URL> Yonghoon-DEM-DFT && cd Yonghoon-DEM-DFT
git checkout <작업 브랜치>      # 이름은 루트 CLAUDE.md 하드룰 1 (여기 적지 않는다)
```

### 2. 세팅 스크립트 (한 번 — apt·venv·의존성·alias)
```bash
bash scripts/setup-wsl.sh
source ~/.bashrc
```
하는 일: `python3-venv` 확인 → `.venv` 생성 → `webapp/requirements.txt` + `pymupdf` 설치 →
`~/.bashrc` 에 `alias li2s='~/Yonghoon-DEM-DFT/webapp/li2s.sh'` 추가(중복 방지) →
`wslu`(wslview) 가 있으면 브라우저 열기에 쓰고 없으면 `explorer.exe` 로 연다.

### 3. 매일
```bash
li2s              # 서버가 없으면 띄우고, 브라우저를 연다 (127.0.0.1:51xx)
li2s open         # 이미 떠 있는 서버를 브라우저로 다시 연다
li2s status       # 떠 있나, 주소가 뭔가
li2s stop         # 내린다
li2s update       # git pull --ff-only 후 재시작
li2s share        # 같은 망(연구실)에서 보여 줄 때 — 0.0.0.0 바인딩, 주소를 찍어 준다
li2s paper <pdf>  # PDF(+SI)를 wiki/inbox/ 로 복사 → Claude 에서 /paper
li2s lint         # 위키 lint
```

### 4. 논문 넣기
Windows 다운로드 폴더의 PDF 는 WSL 에서 `/mnt/c/Users/<계정>/Downloads/…` 로 보인다:
```bash
li2s paper "/mnt/c/Users/<계정>/Downloads/paper.pdf" "/mnt/c/Users/<계정>/Downloads/paper_SI.pdf"
```
그다음 Claude Code 에서 `/paper` (또는 "논문 에이전트 해줘"). 그림 크로핑은 에이전트가
`.venv/bin/python wiki/tools/extract_figures.py` 로 한다.

### 5. /chat (위키 근거 대화) 켜기
서버가 Anthropic API 를 호출한다. 키는 **환경변수로만**, 파일·저장소에 넣지 않는다:
```bash
echo 'export ANTHROPIC_API_KEY=...' >> ~/.bashrc    # 또는 세션마다 export
```
키가 없으면 `/chat` 화면은 "비활성" 안내만 보이고 나머지 화면은 그대로 동작한다.

### 6. `li2s share` 를 WSL 에서 쓸 때
WSL2 는 별도 가상망이라 같은 연구실 PC 에서 보려면 Windows 쪽 포트프록시가 필요하다
(관리자 PowerShell, `<WSL IP>` 는 `li2s share` 가 찍어 준다):
```powershell
netsh interface portproxy add v4tov4 listenport=5100 listenaddress=0.0.0.0 connectport=5100 connectaddress=<WSL IP>
New-NetFirewallRule -DisplayName "li2s 5100" -Direction Inbound -Protocol TCP -LocalPort 5100 -Action Allow
```
끝나면 `netsh interface portproxy delete …` 로 되돌린다. 인증이 없으므로 공개망에 걸지 않는다.

## 문제가 생기면
- `python3 -m venv` 실패 → `sudo apt install python3-venv`.
- 브라우저가 안 열림 → `li2s status` 가 찍는 주소를 Windows 브라우저에 직접 붙여 넣는다.
- 포트 충돌 → `li2s --port 5123`.

## 관련
- [[li2s-assb-reference-cell]] — 이 도구가 섬기는 프로젝트
- [[seminar-prep-from-digest]] — 논문을 넣은 뒤의 워크플로
