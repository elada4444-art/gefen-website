#!/usr/bin/env bash
# The Gefen logo is the only binary asset not kept here; the three OFL fonts are.
set -euo pipefail
cd "$(dirname "$0")"
curl -sS -o logo.png \
  "https://raw.githubusercontent.com/elada4444-art/gefen-website/main/assets/logo.png"
echo "logo ready"
