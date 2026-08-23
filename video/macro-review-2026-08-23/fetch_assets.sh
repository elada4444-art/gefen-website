#!/usr/bin/env bash
# Pull the two binary assets the renderer needs: the Heebo family (the site's
# typeface) and the Gefen logo used on the closing card.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p fonts

CSS=$(curl -sS -A "Mozilla/4.0" \
  "https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;900&display=swap")
for w in 400 500 700 900; do
  url=$(grep -A5 "font-weight: $w;" <<<"$CSS" | grep -oE "https://[^)]+\.ttf" | head -1)
  curl -sS "$url" -o "fonts/Heebo-$w.ttf"
done

curl -sS -o logo.png \
  "https://raw.githubusercontent.com/elada4444-art/gefen-website/main/assets/logo.png"

echo "assets ready:"; ls -la fonts logo.png
