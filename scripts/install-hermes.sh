#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE="$HOME/.hermes"
SKILL="$BASE/skills/redeti-next"
TARGET="$ROOT/skills/redeti-next"
mkdir -p "$BASE/skills"
if [ -e "$SKILL" ] && [ ! -L "$SKILL" ]; then
  echo "ABORT: existing non-symlink skill at $SKILL; preserve manually"
  exit 1
fi
if [ -e "$BASE/redeti-framework" ] && [ ! -L "$BASE/redeti-framework" ]; then
  echo "ABORT: existing non-symlink framework at $BASE/redeti-framework"
  exit 1
fi
python3 -m py_compile "$ROOT/scripts/next_bridge.py"
ln -sfn "$ROOT" "$BASE/redeti-framework"
ln -sfn "$TARGET" "$SKILL"
echo "Framework linked: $BASE/redeti-framework"
echo "Global skill installed: $SKILL"
echo "Open the Hermes chat within a project checkout; run /redeti-next"
echo "No credentials or agent runtime were modified"
