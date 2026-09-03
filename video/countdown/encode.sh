#!/usr/bin/env bash
# frames/*.png -> H.264 MP4. No audio track: the brief calls for no narration
# and no music. Add `-f lavfi -i anullsrc -c:a aac -shortest` if an uploader
# insists on an audio stream.
set -euo pipefail
cd "$(dirname "$0")"
ffmpeg -y -framerate 30 -i frames/%04d.png \
  -c:v libx264 -profile:v high -level 4.1 -pix_fmt yuv420p -crf 18 -preset slow \
  -x264-params "keyint=60:min-keyint=30" -movflags +faststart \
  gefen-countdown-1080x1920.mp4
