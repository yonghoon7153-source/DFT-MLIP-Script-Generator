#!/usr/bin/env bash
# li2s — Li2S ASSB 위키 대시보드 한 단어 실행 (WSL/Ubuntu)
#
#   설치 (한 번):  bash scripts/setup-wsl.sh        ← venv·의존성·alias 까지 해 준다
#   그 뒤:         li2s                              ← 서버가 없으면 띄우고 브라우저를 연다
#
# 쓰기:
#   li2s              서버 기동(백그라운드) + 브라우저 열기. 이미 떠 있으면 열기만
#   li2s open         브라우저만 다시 연다
#   li2s status       떠 있나 · 주소 · pid · chat 상태
#   li2s stop         내린다
#   li2s restart      내리고 다시 띄운다
#   li2s update       git pull --ff-only (갈라져 있으면 알리기만) 후 restart
#   li2s share        같은 망의 다른 사람도 보게 (0.0.0.0) — 주소를 찍어 준다
#   li2s fg           포그라운드로 띄운다 (로그를 바로 본다, Ctrl-C 로 끔)
#   li2s log          서버 로그 tail
#   li2s paper <pdf> [<si.pdf> …]   PDF 를 wiki/inbox/ 로 복사 (그다음 Claude 에서 /paper)
#   li2s lint         위키 lint     ·  li2s wiki   위키 status
#   li2s smoke        webapp 라우트 전수 점검 (서버 없이)
#   li2s --port 5123  포트 지정 (기본: 5100 부터 빈 포트)
#
# 설계 메모
#   · 브랜치를 하드코딩하지 않는다 — 현재 체크아웃을 따라간다 (정본: 루트 CLAUDE.md 하드룰 1).
#   · git 이 갈라져 있으면 멈추지 않고 알린 뒤 그대로 띄운다. 자동 merge·reset 안 한다.
#   · 기본 바인딩 127.0.0.1. `share` 만 경계를 연다 (인증 없음 — 공개망 금지).
#   · /chat 은 ANTHROPIC_API_KEY 환경변수가 서버 프로세스에 보여야 켜진다. 이 스크립트는
#     키를 저장하지 않는다 — 셸에 export 해 두고 li2s 를 띄운다.
set -uo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"
RUN="$VENV/.li2s"          # 런타임 파일 (pid·url·log) — 저장소에 커밋되지 않는다
mkdir -p "$RUN" 2>/dev/null || true
PIDF="$RUN/pid"; URLF="$RUN/url"; LOGF="$RUN/server.log"
PORT=""; BIND="127.0.0.1"; CMD=""

usage() { sed -n '2,25p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

# ── 인자 ──────────────────────────────────────────────────────────────────
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --port) PORT="${2:-}"; shift 2 ;;
    -h|--help|help) usage; exit 0 ;;
    *) ARGS+=("$1"); shift ;;
  esac
done
CMD="${ARGS[0]:-start}"

cd "$ROOT" || exit 1

# ── 도우미 ────────────────────────────────────────────────────────────────
alive() { [[ -f "$PIDF" ]] && kill -0 "$(cat "$PIDF")" 2>/dev/null; }
url()   { [[ -f "$URLF" ]] && cat "$URLF"; }
is_wsl() { grep -qi microsoft /proc/version 2>/dev/null; }

open_browser() {
  local u="$1"
  if command -v wslview >/dev/null 2>&1; then wslview "$u" >/dev/null 2>&1 && return 0; fi
  if is_wsl; then
    # WSL 에서 Windows 기본 브라우저 — cmd.exe 는 & 를 싫어하므로 URL 을 따옴표로
    if command -v powershell.exe >/dev/null 2>&1; then powershell.exe -NoProfile -Command "Start-Process '$u'" >/dev/null 2>&1 && return 0; fi
    if command -v cmd.exe >/dev/null 2>&1; then cmd.exe /c start "" "$u" >/dev/null 2>&1 && return 0; fi
    if command -v explorer.exe >/dev/null 2>&1; then explorer.exe "$u" >/dev/null 2>&1; return 0; fi
  fi
  if command -v xdg-open >/dev/null 2>&1; then xdg-open "$u" >/dev/null 2>&1 && return 0; fi
  echo "· 브라우저를 자동으로 못 열었다 — 이 주소를 직접 연다:  $u"
  return 1
}

ensure_venv() {
  local REQ="$ROOT/webapp/requirements.txt"
  [[ -f "$REQ" ]] || { echo "✗ $REQ 가 없다" >&2; exit 1; }
  if [[ ! -x "$VENV/bin/python" ]]; then
    echo "· venv 를 만든다 (.venv)"
    python3 -m venv "$VENV" || { echo "✗ venv 생성 실패 — sudo apt install python3-venv" >&2; exit 1; }
  fi
  local STAMP="$VENV/.li2s.reqs.sha256" NOW
  NOW="$(sha256sum "$REQ" | cut -d' ' -f1)"
  if [[ ! -f "$STAMP" ]] || [[ "$(cat "$STAMP")" != "$NOW" ]]; then
    echo "· 의존성 동기화"
    "$VENV/bin/pip" install --quiet --upgrade pip >/dev/null 2>&1
    "$VENV/bin/pip" install --quiet -r "$REQ" || { echo "✗ pip install 실패" >&2; exit 1; }
    echo "$NOW" > "$STAMP"
  fi
}

pick_port() {
  if [[ -n "$PORT" ]]; then echo "$PORT"; return; fi
  "$VENV/bin/python" - <<'PY'
import socket
for p in range(5100, 5200):
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", p)); print(p); break
    except OSError:
        continue
    finally:
        s.close()
else:
    s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()
PY
}

git_note() {
  [[ -e "$ROOT/.git" ]] || return 0
  local BR; BR="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
  echo "· 브랜치: $BR"
  if git fetch --quiet origin "$BR" 2>/dev/null; then
    local AHEAD BEHIND
    AHEAD=$(git rev-list --count "origin/$BR..HEAD" 2>/dev/null || echo 0)
    BEHIND=$(git rev-list --count "HEAD..origin/$BR" 2>/dev/null || echo 0)
    if   [[ "$AHEAD" == "0" && "$BEHIND" == "0" ]]; then echo "· 최신"
    elif [[ "$AHEAD" == "0" ]]; then git merge --ff-only "origin/$BR" --quiet && echo "· $BEHIND 커밋 당겼다"
    else
      echo "⚠ 로컬에 push 안 된 커밋 $AHEAD 개 — 자동 갱신 건너뜀 (원격에 $BEHIND 개 더). 합치려면: git pull --rebase origin $BR"
    fi
  else
    echo "⚠ fetch 실패 — 네트워크? 지금 트리 그대로"
  fi
}

start_server() {   # $1 = bind
  ensure_venv
  local P; P="$(pick_port)"
  local U="http://127.0.0.1:$P"
  echo "$U" > "$URLF"
  ( cd "$ROOT/webapp" && WEBAPP_HOST="$1" WEBAPP_PORT="$P" nohup "$VENV/bin/python" app.py >> "$LOGF" 2>&1 & echo $! > "$PIDF" )
  # 뜰 때까지 잠깐 기다린다 (최대 10초)
  "$VENV/bin/python" - "$P" <<'PY'
import socket, sys, time
p = int(sys.argv[1])
for _ in range(40):
    try:
        s = socket.create_connection(("127.0.0.1", p), timeout=0.5); s.close(); sys.exit(0)
    except OSError:
        time.sleep(0.25)
sys.exit(1)
PY
  if [[ $? -ne 0 ]]; then echo "✗ 서버가 뜨지 않았다 — li2s log 로 확인" >&2; return 1; fi
  echo "· 기동 → $U"
  if [[ "$1" == "0.0.0.0" ]]; then
    local LANIP; LANIP="$(ip -4 -o addr show scope global 2>/dev/null | awk '{split($4,a,"/"); print a[1]; exit}')"
    [[ -z "$LANIP" ]] && LANIP="$(hostname -I 2>/dev/null | awk '{print $1}')"
    [[ -n "$LANIP" ]] && echo "· 같은 망에서는 →  http://$LANIP:$P   (WSL 이면 Windows 포트프록시 필요 — wiki/guides/wsl-li2s-setup.md)"
    echo "· ⚠ 인증이 없다. 같은 망의 누구나 열람한다 (읽기 전용 + chat). 공개망에 걸지 말 것"
  fi
  if [[ -n "${ANTHROPIC_API_KEY:-}${ANTHROPIC_AUTH_TOKEN:-}" ]]; then echo "· chat: 켜짐 (키가 이 셸에 있다)"; else echo "· chat: 꺼짐 — export ANTHROPIC_API_KEY=… 후 li2s restart"; fi
  echo "·   끄기: li2s stop · 로그: li2s log"
}

# ── 명령 ──────────────────────────────────────────────────────────────────
case "$CMD" in
  start)
    if alive; then echo "· 이미 떠 있다 (pid $(cat "$PIDF")) → $(url)"; open_browser "$(url)"; exit 0; fi
    git_note
    start_server "$BIND" && open_browser "$(url)"
    ;;
  open)
    alive || { echo "· 떠 있는 서버가 없다 — li2s 로 띄운다"; exit 1; }
    open_browser "$(url)"
    ;;
  status)
    if alive; then echo "· 떠 있다 (pid $(cat "$PIDF")) → $(url)"; curl -s "$(url)/api/chat/status" 2>/dev/null && echo; else echo "· 떠 있지 않다"; fi
    ;;
  stop)
    if alive; then kill "$(cat "$PIDF")" && rm -f "$PIDF" && echo "· 내렸다"; else echo "· 떠 있는 li2s 가 없다"; rm -f "$PIDF"; fi
    ;;
  restart)
    "$0" stop; exec "$0" start ${PORT:+--port "$PORT"}
    ;;
  update)
    git_note; "$0" stop; exec "$0" start ${PORT:+--port "$PORT"}
    ;;
  share)
    if alive; then echo "· 이미 127.0.0.1 로 떠 있다 — 내리고 0.0.0.0 으로 다시 띄운다"; "$0" stop; fi
    git_note
    start_server "0.0.0.0" && open_browser "$(url)"
    ;;
  fg)
    ensure_venv; P="$(pick_port)"; echo "· 포그라운드 → http://127.0.0.1:$P  (Ctrl-C 로 끔)"
    cd "$ROOT/webapp" && exec env WEBAPP_HOST="$BIND" WEBAPP_PORT="$P" "$VENV/bin/python" app.py
    ;;
  log)
    [[ -f "$LOGF" ]] && tail -n 40 "$LOGF" || echo "· 로그가 없다"
    ;;
  paper)
    [[ ${#ARGS[@]} -ge 2 ]] || { echo "쓰기: li2s paper <pdf> [<si.pdf> …]" >&2; exit 2; }
    mkdir -p "$ROOT/wiki/inbox"
    for f in "${ARGS[@]:1}"; do
      [[ -f "$f" ]] || { echo "✗ 없음: $f" >&2; continue; }
      cp -n -- "$f" "$ROOT/wiki/inbox/" && echo "· inbox ← $(basename -- "$f")"
    done
    echo "· 다음: Claude Code 에서  /paper   (또는 \"논문 에이전트 해줘\")"
    ;;
  lint) exec python3 "$ROOT/wiki/tools/lint.py" ;;
  smoke) ensure_venv; exec "$VENV/bin/python" "$ROOT/webapp/smoke.py" ;;
  wiki) exec python3 "$ROOT/wiki/tools/status.py" ;;
  *) echo "모르는 명령: $CMD" >&2; usage; exit 2 ;;
esac
