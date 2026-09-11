#!/usr/bin/env bash
# install-alias.sh — `midni` alias 를 ~/.bashrc (와 있으면 ~/.zshrc) 에 멱등하게 넣는다.
#   bash scripts/install-alias.sh            # alias midni='<저장소>/webapp/midni.sh'
#   bash scripts/install-alias.sh li2s       # 다른 이름을 하나 더 (예: li2s) — 같은 런처를 가리킨다
# 경로는 **이 저장소를 받아 둔 자리**로 고정된다 (이름이 Yonghoon-DEM-DFT 가 아니어도 된다).
set -uo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="${1:-midni}"
[[ "$NAME" =~ ^[A-Za-z_][A-Za-z0-9_-]*$ ]] || { echo "✗ alias 이름이 이상하다: $NAME" >&2; exit 2; }
LINE="alias $NAME='$ROOT/webapp/midni.sh'"
MARK="# $NAME — NCA721 formation wiki dashboard (managed by scripts/install-alias.sh)"
chmod +x "$ROOT/webapp/midni.sh" "$ROOT/scripts/"*.sh 2>/dev/null || true
for RC in "$HOME/.bashrc" "$HOME/.zshrc"; do
  [[ -f "$RC" ]] || { [[ "$RC" == "$HOME/.bashrc" ]] && touch "$RC" || continue; }
  if grep -qF "$MARK" "$RC"; then
    # 이미 있으면 경로만 최신으로 (저장소를 옮겼을 때)
    python3 - "$RC" "$MARK" "$LINE" "$NAME" <<'PY'
import sys, pathlib
rc, mark, line, name = sys.argv[1:]
p = pathlib.Path(rc); lines = p.read_text().splitlines()
out, i = [], 0
while i < len(lines):
    out.append(lines[i])
    if lines[i] == mark and i + 1 < len(lines) and lines[i+1].startswith(f"alias {name}="):
        out.append(line); i += 2; continue
    i += 1
p.write_text("\n".join(out) + "\n")
PY
    echo "· $RC: alias $NAME 갱신"
  else
    printf '\n%s\n%s\n' "$MARK" "$LINE" >> "$RC"
    echo "· $RC: alias $NAME 추가"
  fi
done
echo "· 적용:  source ~/.bashrc   (또는 새 터미널)  →  $NAME"
