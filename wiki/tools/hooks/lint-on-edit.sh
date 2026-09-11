#!/bin/bash
# PostToolUse hook: run the wiki lint after any Edit/Write to a wiki .md file.
# Read-only check — reports errors back to the agent (exit 2), never modifies files.

INPUT=$(cat)
FILE=$(printf '%s' "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)

W="$CLAUDE_PROJECT_DIR/wiki"
case "$FILE" in
  "$W"/papers/*.md|"$W"/mechanisms/*.md|"$W"/protocols/*.md|"$W"/experiments/*.md|\
  "$W"/concepts/*.md|"$W"/entities/*.md|"$W"/comparisons/*.md|"$W"/queries/*.md|\
  "$W"/guides/*.md|"$W"/questions/*.md|"$W"/syntheses/*.md|"$W"/raw/*|\
  "$W"/index.md|"$W"/SCHEMA.md|"$W"/CLAUDE.md|"$W"/AGENTS.md|"$CLAUDE_PROJECT_DIR"/config/cells.yaml)
    ;;
  *)
    exit 0
    ;;
esac

OUT=$(python3 "$W/tools/lint.py" 2>&1)
if [ $? -ne 0 ]; then
  echo "wiki lint failed after editing $FILE:" >&2
  printf '%s\n' "$OUT" | grep -A100 'ERRORS' | head -40 >&2
  exit 2
fi
exit 0
