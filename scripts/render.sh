#!/usr/bin/env bash
# Render every fixture to a 2x "above the fold" screenshot for the template gallery.
# Requires Google Chrome (headless). Consistent 1280x860 framing for comparison.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
OUT="$ROOT/paper/figs"
mkdir -p "$OUT"
for f in "$ROOT"/fixtures/*.html; do
  name="$(basename "$f" .html)"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
    --window-size=1280,860 --screenshot="$OUT/shot_${name}.png" "file://$f" >/dev/null 2>&1
  echo "rendered shot_${name}.png"
done
