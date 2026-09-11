#!/bin/bash
# PreToolUse hook: enforce raw source immutability (wiki/SCHEMA.md Layer 1 rule).
# Blocks Edit/Write on EXISTING files under wiki/raw/. Creating new raw files is allowed.
# (킷 원본은 위키가 저장소 루트였다 — 이 저장소는 repo root `wiki/` 하위라 경로에 wiki/ 가 붙는다.)

INPUT=$(cat)
FILE=$(printf '%s' "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)

case "$FILE" in
  "$CLAUDE_PROJECT_DIR"/wiki/raw/*)
    if [ -f "$FILE" ]; then
      echo "BLOCKED: $FILE is an existing raw source — wiki/raw/ is the immutable layer (wiki/SCHEMA.md)." >&2
      echo "원본이 바뀌었다면: 새 -v2 파일 + supersedes/superseded-by 링크. 정정은 2층(papers/ 노트 등)에 적는다." >&2
      exit 2
    fi
    ;;
esac
exit 0
