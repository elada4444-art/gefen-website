#!/usr/bin/env bash
# Compose the Gefen savings marketing video (robust + fast).
set -euo pipefail

CLIPS="${1:?clips dir}"
OV="${2:?overlays dir}"
OUT="${3:?output file}"
WORK="$(mktemp -d)"
W=1080; H=1920; FPS=30
OV_Y=150
XF=0.4
PRESET=veryfast

dur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }

norm() { # in out [trim_start]
  local in="$1" out="$2" ss="${3:-0}"
  ffmpeg -y -ss "$ss" -i "$in" \
    -vf "scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},fps=${FPS},setsar=1,format=yuv420p" \
    -c:v libx264 -preset "$PRESET" -crf 18 \
    -c:a aac -ar 48000 -ac 2 -b:a 160k -movflags +faststart "$out"
}

burn() { # clip overlay_png start_t out
  local clip="$1" png="$2" st="$3" out="$4"; local D; D=$(dur "$clip")
  ffmpeg -y -i "$clip" -loop 1 -t "$D" -i "$png" -filter_complex \
    "[1]format=rgba,fade=in:st=${st}:d=0.4:alpha=1[o];[0:v][o]overlay=(W-w)/2:${OV_Y}:enable='gte(t,${st})'[v]" \
    -map "[v]" -map 0:a -c:v libx264 -preset "$PRESET" -crf 18 -pix_fmt yuv420p -c:a aac -b:a 160k "$out"
}

burn_dan() { # clip out
  local clip="$1" out="$2"; local D; D=$(dur "$clip")
  ffmpeg -y -i "$clip" -loop 1 -t "$D" -i "$OV/dan.png" -loop 1 -t "$D" -i "$OV/dan-truth.png" -filter_complex \
    "[1]format=rgba,fade=in:st=0.6:d=0.4:alpha=1[a];\
     [2]format=rgba,fade=in:st=3.6:d=0.4:alpha=1[b];\
     [0:v][a]overlay=(W-w)/2:${OV_Y}:enable='gte(t,0.6)'[t1];\
     [t1][b]overlay=(W-w)/2:H-h-240:enable='gte(t,3.6)'[v]" \
    -map "[v]" -map 0:a -c:v libx264 -preset "$PRESET" -crf 18 -pix_fmt yuv420p -c:a aac -b:a 160k "$out"
}

echo "== normalize =="
norm "$CLIPS/clip1.mp4" "$WORK/n1.mp4" 0
norm "$CLIPS/clip2.mp4" "$WORK/n2.mp4" 0.7
norm "$CLIPS/clip3.mp4" "$WORK/n3.mp4" 0.7
norm "$CLIPS/clip4.mp4" "$WORK/n4.mp4" 0.7

echo "== burn overlays =="
burn "$WORK/n1.mp4" "$OV/amit.png"   1.0 "$WORK/b1.mp4"
burn "$WORK/n2.mp4" "$OV/michal.png" 0.5 "$WORK/b2.mp4"
burn "$WORK/n3.mp4" "$OV/noam.png"   0.5 "$WORK/b3.mp4"
burn_dan "$WORK/n4.mp4" "$WORK/b4.mp4"

echo "== end card =="
ffmpeg -y -loop 1 -t 4.5 -i "$OV/endcard.png" -i "$WORK/n4.mp4" -filter_complex \
  "[0:v]scale=${W}:${H},fps=${FPS},setsar=1,format=yuv420p,fade=in:st=0:d=0.5[v];\
   [1:a]atrim=0:4.5,afade=t=out:st=3.5:d=1,asetpts=PTS-STARTPTS[a]" \
  -map "[v]" -map "[a]" -shortest -c:v libx264 -preset "$PRESET" -crf 18 -pix_fmt yuv420p -c:a aac -ar 48000 -ac 2 -b:a 160k "$WORK/end.mp4"

echo "== crossfade concat =="
D1=$(dur "$WORK/b1.mp4"); D2=$(dur "$WORK/b2.mp4"); D3=$(dur "$WORK/b3.mp4"); D4=$(dur "$WORK/b4.mp4")
O1=$(awk -v a="$D1" -v x="$XF" 'BEGIN{printf "%.3f", a-x}')
O2=$(awk -v a="$D1" -v b="$D2" -v x="$XF" 'BEGIN{printf "%.3f", a+b-2*x}')
O3=$(awk -v a="$D1" -v b="$D2" -v c="$D3" -v x="$XF" 'BEGIN{printf "%.3f", a+b+c-3*x}')
O4=$(awk -v a="$D1" -v b="$D2" -v c="$D3" -v d="$D4" -v x="$XF" 'BEGIN{printf "%.3f", a+b+c+d-4*x}')

ffmpeg -y -i "$WORK/b1.mp4" -i "$WORK/b2.mp4" -i "$WORK/b3.mp4" -i "$WORK/b4.mp4" -i "$WORK/end.mp4" \
 -filter_complex "\
 [0:v][1:v]xfade=transition=fade:duration=${XF}:offset=${O1}[v1];\
 [v1][2:v]xfade=transition=fade:duration=${XF}:offset=${O2}[v2];\
 [v2][3:v]xfade=transition=fade:duration=${XF}:offset=${O3}[v3];\
 [v3][4:v]xfade=transition=fade:duration=${XF}:offset=${O4}[v];\
 [0:a][1:a]acrossfade=d=${XF}[a1];\
 [a1][2:a]acrossfade=d=${XF}[a2];\
 [a2][3:a]acrossfade=d=${XF}[a3];\
 [a3][4:a]acrossfade=d=${XF}[a]" \
 -map "[v]" -map "[a]" -c:v libx264 -preset "$PRESET" -crf 19 -pix_fmt yuv420p -c:a aac -ar 48000 -b:a 160k -movflags +faststart "$WORK/base.mp4"

# The per-clip audio Seedance returns is uneven (some clips are near-silent), so lay a
# continuous, normalized restaurant-ambience bed under the whole video with a gentle fade-out.
AMB="${CLIPS}/ambience.mp3"
if [ -f "$AMB" ]; then
  echo "== mix restaurant ambience bed =="
  TOT=$(dur "$WORK/base.mp4"); FO=$(awk -v d="$TOT" 'BEGIN{printf "%.2f", d-1.2}')
  ffmpeg -y -i "$WORK/base.mp4" -stream_loop -1 -i "$AMB" -filter_complex \
    "[1:a]atrim=0:${TOT},asetpts=PTS-STARTPTS,loudnorm=I=-19:TP=-1.5:LRA=11,afade=t=out:st=${FO}:d=1.2[amb];\
     [0:a]volume=0.7[clip];\
     [clip][amb]amix=inputs=2:duration=first:normalize=0[mix];\
     [mix]loudnorm=I=-16:TP=-1.5[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -ar 48000 -ac 2 -b:a 160k -movflags +faststart "$WORK/mixed.mp4"
else
  echo "== no ambience bed found ($AMB); keeping clip audio =="
  cp "$WORK/base.mp4" "$WORK/mixed.mp4"
fi

# Extras: a permanent bottom-right disclaimer, and a top-left intro caption that
# "types" itself over the first ~5s then fades out. Frames come from render-extras.js
# (overlays/extras/disc.png + intro_%03d.png, played back at 10fps).
EX="$OV/extras"
if [ -f "$EX/disc.png" ] && [ -f "$EX/intro_001.png" ]; then
  echo "== burn disclaimer + intro caption =="
  ffmpeg -y -i "$WORK/mixed.mp4" -loop 1 -i "$EX/disc.png" \
    -filter_complex "[1:v]format=rgba[d];[0:v][d]overlay=0:0:shortest=1[v]" \
    -map "[v]" -map 0:a -c:v libx264 -preset "$PRESET" -crf 19 -pix_fmt yuv420p -c:a copy -movflags +faststart "$WORK/disc.mp4"
  ffmpeg -y -i "$WORK/disc.mp4" -framerate 10 -i "$EX/intro_%03d.png" \
    -filter_complex "[1:v]format=rgba,fade=t=out:st=4.2:d=0.8:alpha=1,setpts=PTS-STARTPTS[intro];\
                     [0:v][intro]overlay=0:0:enable='lt(t,5.2)'[v]" \
    -map "[v]" -map 0:a -c:v libx264 -preset "$PRESET" -crf 19 -pix_fmt yuv420p -c:a copy -movflags +faststart "$OUT"
else
  echo "== no extras found ($EX); skipping caption/disclaimer =="
  cp "$WORK/mixed.mp4" "$OUT"
fi

echo "done: $OUT"
ffprobe -v error -show_entries format=duration:stream=width,height,codec_type -of default=noprint_wrappers=1 "$OUT"
rm -rf "$WORK"
