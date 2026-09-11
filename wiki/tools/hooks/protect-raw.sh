#!/bin/bash
# PreToolUse hook: enforce raw source immutability (wiki/SCHEMA.md Layer 1 rule).
# Blocks Edit/Write on EXISTING files under wiki/raw/. Creating new raw files is allowed.
# 킷 원본과 다른 점: 위키가 repo root 가 아니라 `wiki/` 하위라 경로에 wiki/ 가 붙는다.

INPUT=$(cat)
FILE=$(printf '%s' "$INPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)

case "$FILE" in
  "$CLAUDE_PROJECT_DIR"/wiki/raw/*)
    if [ -f "$FILE" ]; then
      echo "BLOCKED: $FILE is an existing raw source — wiki/raw/ is the immutable layer (wiki/SCHEMA.md)." >&2
      echo "원본이 바뀌었다면 새 -v2 파일 + supersedes/superseded-by 링크로 처리하라." >&2
      # raw/figures/ 의 `figures.json` · `_sources.json` 은 봉인 소스가 아니라 **생성 색인**이다
      # (sha256 이 없고 extract_figures.py 가 매번 덮어쓴다). 손으로 고치지 말고 도구로 재생성하라 —
      # 그래서 이 hook 은 그것들도 막는다. 2026-09-11: `_sources.json` 이 SI 처리 후 재생성되지
      # 않아 그림 8/19 · 소스 1/2 로 낡아 있었다.
      case "$FILE" in
        */raw/figures/*.json)
          echo "↳ 이 파일은 생성 색인이다. 손으로 고치지 말고 재생성하라:" >&2
          echo "   .venv/bin/python wiki/tools/extract_figures.py --slug <slug> --pdf <pdf>" >&2
          echo "   (PDF 없이 색인만 갱신하려면 extract_figures.py 의 _write_sources_index() 로직을 그대로 돌린다)" >&2
          ;;
      esac
      exit 2
    fi
    ;;
esac
exit 0
