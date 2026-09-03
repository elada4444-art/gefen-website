#!/usr/bin/env bash
# Pulls the Heebo faces the scene uses (same family the site loads) and inlines
# them as data: URIs, so the render never depends on the network being up.
set -euo pipefail
cd "$(dirname "$0")"
curl -sS -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36" \
  "https://fonts.googleapis.com/css2?family=Heebo:wght@400;700;800;900&display=swap" -o heebo.css
node inline_fonts.js
