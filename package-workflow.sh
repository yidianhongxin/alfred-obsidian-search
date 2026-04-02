#!/bin/bash
# 将 alfred-workflow-source 打成 Alfred 可导入的 .alfredworkflow（ZIP）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/Obsidian Search.alfredworkflow"
cp "$ROOT/search.py" "$ROOT/alfred-workflow-source/search.py"
rm -f "$OUT"
( cd "$ROOT/alfred-workflow-source" && zip -rq "$OUT" . )
echo "已生成: $OUT"
