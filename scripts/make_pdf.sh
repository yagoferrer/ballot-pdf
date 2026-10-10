#!/bin/bash
# Build HTML + printable PDF from ballot-data.json, then render page previews for checking.
# Usage: make_pdf.sh <ballot-data.json> <output-basename> [preview-dir]
#   e.g. make_pdf.sh 2026-11-03-general/ballot-data.json 2026-11-03-general/san-diego-nov-2026-ballot
set -euo pipefail
DATA="$1"; OUT="$2"; PREV="${3:-${TMPDIR:-/tmp}/ballot-preview}"
HERE="$(cd "$(dirname "$0")" && pwd)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

python3 -I "$HERE/build_ballot.py" "$DATA" "$OUT.html"
ABS="$(cd "$(dirname "$OUT.html")" && pwd)/$(basename "$OUT.html")"
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="${ABS%.html}.pdf" "file://$ABS" >/dev/null 2>&1

pdfinfo "$OUT.pdf" | grep -E "Pages|Page size"
pdftotext "$OUT.pdf" - | grep -oE "(Page|Página) [0-9]+ (of|de) [0-9]+" | tr '\n' ' '; echo
mkdir -p "$PREV" && rm -f "$PREV"/pg-*.png
pdftoppm -r 60 -png "$OUT.pdf" "$PREV/pg"
echo "previews: $(ls "$PREV"/pg-*.png | tr '\n' ' ')"
