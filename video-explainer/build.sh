#!/usr/bin/env bash
# Assemble voice-over from transferred chunks, build the scene timeline, mix audio, render the video.
set -euo pipefail
S=/tmp/claude-0/-home-user-gefen-website/d7cc3944-8b91-561b-b675-19160c1e1a80/scratchpad
VO=$S/vo; V=$S/video; OUT=$V/out; mkdir -p $OUT
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
FP="$(dirname $FF)/ffprobe"; [ -x "$FP" ] || FP=/opt/pw-browsers/ffmpeg-1011/ffmpeg-linux

declare -A MD5=( [01]=7112ea06c49ce1b850fa2887b41fd4f1 [02]=32b57a372b6868595334e5af8a22ee58 [03]=dc25dca65a58edd174446f3816611908 [04]=4667ddc62eae1bf7a3008943bf319b89 [05]=565da1a793fe7b20d59dc6cb957073c2 [06]=040f4c4e7fd9b28355ee625d6301d115 [07]=aed9028c518d3a0e28c78a2b37e1fee4 [08]=d09b0fa8eedf5e09771fb6a7756d04d4 )

echo "== reassemble + verify"
for n in 01 02 03 04 05 06 07 08; do
  cat $(ls $VO/c${n}_* | sort) | tr -d '\n' | base64 -d > $VO/vo$n.opus
  got=$(md5sum $VO/vo$n.opus | cut -c1-32)
  [ "$got" = "${MD5[$n]}" ] || { echo "MD5 MISMATCH vo$n: $got"; exit 1; }
  $FF -v error -y -i $VO/vo$n.opus -ac 1 -ar 48000 -c:a pcm_s16le $VO/vo$n.wav
  echo "vo$n ok"
done

echo "== timeline"
python3 - "$FF" <<'PY' > $V/timeline.json
import json, subprocess, sys
ff = sys.argv[1]
VO = "/tmp/claude-0/-home-user-gefen-website/d7cc3944-8b91-561b-b675-19160c1e1a80/scratchpad/vo"
caps = [
 "<b>21.8 מיליארד ₪</b> בחצי שנה. זה מה שגייסו פוליסות החיסכון במחצית הראשונה של 2026.",
 "לעומת 13.9 מיליארד אשתקד: תוספת של כמעט <b>8 מיליארד ₪</b>, זינוק של כ-57%.",
 "<b>הפניקס</b> במקום הראשון, בפער גדול: 7.55 מיליארד ₪, עלייה של 18%.",
 "ההפתעה: <b>איילון</b>. מ-315 מיליון ₪ ל-3.19 מיליארד. זינוק של כ-910%, ישר למקום השני.",
 "<b>מגדל</b> במקום השלישי, בפער קטן מאיילון. <b>הכשרה</b> שומרת על כוחה עם כ-2.5 מיליארד ₪.",
 "גם <b>ביטוח ישיר</b> צומחת: 160 מיליון ₪ לעומת 52 מיליון. עלייה של כ-208%.",
 "הסיפור הבא: <b>קופות הגמל</b>. איילון חזרה לענף, וההערכות מדברות על כמיליארד ₪ כבר בחודש הראשון.",
 "רוצים להבין מה זה אומר על החיסכון שלכם? <b>גפן ביטוח ופיננסים</b> · מלווים אתכם בהחלטות.",
]
def dur(p):
    out = subprocess.run([ff, "-i", p], capture_output=True, text=True).stderr
    import re
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    h, mi, s = m.groups(); return int(h)*3600 + int(mi)*60 + float(s)
scenes = []
for i in range(8):
    a = dur(f"{VO}/vo{i+1:02d}.wav")
    lead = 0.9 if i == 0 else 0.5
    tail = 1.6 if i == 7 else 0.7
    scenes.append({"id": f"s{i+1}", "audio": round(a, 3), "lead": lead, "dur": round(max(4.0, a + lead + tail), 3), "cap": caps[i]})
print(json.dumps({"scenes": scenes}, ensure_ascii=False, indent=1))
PY
python3 -c "import json;t=json.load(open('$V/timeline.json'));print('total', round(sum(s['dur'] for s in t['scenes']),2), [s['dur'] for s in t['scenes']])"

echo "== mix audio"
python3 - "$FF" "$V/timeline.json" "$VO" "$OUT/mix.wav" <<'PY'
import json, subprocess, sys
ff, tl, vo, out = sys.argv[1:5]
t = json.load(open(tl)); acc = 0.0; inputs = []; filt = []
for i, s in enumerate(t["scenes"]):
    start = acc + s["lead"]; acc += s["dur"]
    inputs += ["-i", f"{vo}/vo{i+1:02d}.wav"]
    filt.append(f"[{i}]adelay={int(start*1000)}|{int(start*1000)}[a{i}]")
total = acc
n = len(t["scenes"])
filt.append("".join(f"[a{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0:dropout_transition=0,apad=whole_dur={total:.3f},atrim=0:{total:.3f},loudnorm=I=-16:TP=-1.5:LRA=11[out]")
cmd = [ff, "-y", "-v", "error"] + inputs + ["-filter_complex", ";".join(filt), "-map", "[out]", "-ar", "48000", "-ac", "2", out]
subprocess.run(cmd, check=True); print("mix ok, total", round(total, 2))
PY

echo "== render"
cd $V && NODE_PATH=$S/pwtest/node_modules node render.js --html anim.html --timeline timeline.json --audio $OUT/mix.wav --out $OUT/gefen_savings_policies_h1_2026.mp4 --fps 30
$FF -v error -i $OUT/gefen_savings_policies_h1_2026.mp4 -f null - && echo "decode ok"
ls -la $OUT
