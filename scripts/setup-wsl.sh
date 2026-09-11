#!/usr/bin/env bash
# setup-wsl.sh — WSL(Ubuntu) 에서 이 저장소를 한 번에 세팅한다.
#
#   bash scripts/setup-wsl.sh            # venv + 의존성 + alias midni
#   bash scripts/setup-wsl.sh --no-alias # alias 는 손대지 않는다
#
# 하는 일 (전부 멱등 — 여러 번 돌려도 안전):
#   1. python3 / python3-venv 확인 (없으면 apt 안내 — sudo 는 여기서 실행하지 않는다)
#   2. .venv 생성, webapp/requirements.txt (Flask·markdown·PyYAML·pandas·anthropic) + pymupdf·pillow(그림 크로핑) 설치
#   3. ~/.bashrc (있으면 ~/.zshrc 도) 에  alias midni='<이 저장소>/webapp/midni.sh'  추가
#   4. wslu(wslview) 가 있는지 알려 준다 — 없어도 midni 는 powershell.exe/cmd.exe 로 브라우저를 연다
#   5. 검증: 위키 lint · webapp smoke · 셀 모듈 테스트를 한 번 돌린다
set -uo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
NO_ALIAS=0
[[ "${1:-}" == "--no-alias" ]] && NO_ALIAS=1

echo "== 1. python =="
command -v python3 >/dev/null || { echo "✗ python3 가 없다:  sudo apt update && sudo apt install -y python3 python3-venv"; exit 1; }
python3 -c "import venv, ensurepip" 2>/dev/null || { echo "✗ python3-venv 가 없다:  sudo apt install -y python3-venv"; exit 1; }
python3 --version

echo "== 2. venv + 의존성 =="
[[ -x "$ROOT/.venv/bin/python" ]] || python3 -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/pip" install --quiet --upgrade pip
"$ROOT/.venv/bin/pip" install --quiet -r "$ROOT/webapp/requirements.txt" pymupdf pillow
sha256sum "$ROOT/webapp/requirements.txt" | cut -d' ' -f1 > "$ROOT/.venv/.midni.reqs.sha256"
"$ROOT/.venv/bin/python" - <<'PY'
import importlib.metadata as m
for pkg in ("flask", "markdown", "PyYAML", "pandas", "anthropic", "pymupdf"):
    try:
        print(f"· {pkg} {m.version(pkg)}")
    except m.PackageNotFoundError:
        print(f"· {pkg} 없음")
PY

echo "== 3. alias =="
if [[ $NO_ALIAS -eq 0 ]]; then
  bash "$ROOT/scripts/install-alias.sh" midni
else
  echo "· 건너뜀 (--no-alias)"
fi

echo "== 4. 브라우저 열기 =="
if command -v wslview >/dev/null 2>&1; then echo "· wslview 있음";
elif grep -qi microsoft /proc/version 2>/dev/null; then echo "· wslview 없음 — powershell.exe 로 연다 (원하면: sudo apt install -y wslu)";
else echo "· WSL 이 아니다 — xdg-open 을 쓴다"; fi

echo "== 5. /chat 키 =="
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then echo "· ANTHROPIC_API_KEY 있음 — /chat 켜진다";
else echo "· ANTHROPIC_API_KEY 없음 — /chat 은 비활성. 켜려면:  echo 'export ANTHROPIC_API_KEY=…' >> ~/.bashrc"; fi

echo "== 6. 검증 =="
( cd "$ROOT" && python3 wiki/tools/lint.py | tail -n 3 )
( cd "$ROOT" && "$ROOT/.venv/bin/python" webapp/smoke.py | tail -n 2 )
( cd "$ROOT" && "$ROOT/.venv/bin/python" -m unittest discover -s tests 2>&1 | tail -n 2 )

echo
echo "✓ 끝. 새 셸을 열거나  source ~/.bashrc  한 뒤:   midni"
