#!/usr/bin/env bash
# Build the explainer: speed the narration up 1.5x, lay out the timeline, mix the audio, render the video.
set -euo pipefail
S=/tmp/claude-0/-home-user-gefen-website/d7cc3944-8b91-561b-b675-19160c1e1a80/scratchpad
VO=$S/vo; V=$S/video; OUT=$V/out; mkdir -p "$OUT"
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
TEMPO=1.5   # narration speed-up; atempo preserves pitch

echo "== speed narration to ${TEMPO}x"
for n in 01 02 03 04 05 06 07; do
  [ -s "$VO/vo$n.opus" ] || { echo "missing $VO/vo$n.opus"; exit 1; }
  "$FF" -v error -y -i "$VO/vo$n.opus" -filter:a "atempo=$TEMPO" -ac 1 -ar 48000 -c:a pcm_s16le "$VO/fast$n.wav"
done
"$FF" -v error -y -i "$VO/vo08b.opus" -filter:a "atempo=$TEMPO" -ac 1 -ar 48000 -c:a pcm_s16le "$VO/fast08.wav"
for n in 01 02 03 04 05 06 07 08; do
  printf 'fast%s %s\n' "$n" "$("$FF" -hide_banner -i "$VO/fast$n.wav" 2>&1 | sed -n 's/.*Duration: \([0-9:.]*\).*/\1/p')"
done

echo "== timeline"
python3 - "$FF" "$VO" > "$V/timeline.json" <<'PY'
import json, re, subprocess, sys
ff, vo = sys.argv[1], sys.argv[2]
caps = [
 "<b>21.8 מיליארד ₪</b> בחצי שנה. זה מה שגייסו פוליסות החיסכון במחצית הראשונה של 2026.",
 "לעומת 13.9 מיליארד אשתקד: תוספת של כמעט <b>8 מיליארד ₪</b>, זינוק של כ-57%.",
 "<b>הפניקס</b> במקום הראשון, בפער גדול: 7.55 מיליארד ₪, עלייה של 18%.",
 "ההפתעה: <b>איילון</b>. מ-315 מיליון ₪ ל-3.19 מיליארד. זינוק של כ-910%, ישר למקום השני.",
 "<b>מגדל</b> במקום השלישי, בפער קטן מאיילון. <b>הכשרה</b> שומרת על כוחה עם כ-2.5 מיליארד ₪.",
 "גם <b>ביטוח ישיר</b> צומחת: 160 מיליון ₪ לעומת 52 מיליון. עלייה של כ-208%.",
 "הסיפור הבא: <b>קופות הגמל</b>. איילון חזרה לענף, וההערכות מדברות על כמיליארד ₪ כבר בחודש הראשון.",
 "כמו שאתם רואים, <b>רוב החוסכים</b> כבר הבינו איפה נכון להשקיע את הכסף שלהם. <b>צרו איתנו קשר עוד היום</b>.",
]
def dur(p):
    out = subprocess.run([ff, "-i", p], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)
scenes = []
for i in range(8):
    a = dur(f"{vo}/fast{i+1:02d}.wav")
    lead = 0.8 if i == 0 else 0.45
    tail = 1.8 if i == 7 else 0.6
    scenes.append({"id": f"s{i+1}", "audio": round(a, 3), "lead": lead,
                   "dur": round(a + lead + tail, 3), "cap": caps[i]})
print(json.dumps({"scenes": scenes}, ensure_ascii=False, indent=1))
PY
python3 -c "import json;t=json.load(open('$V/timeline.json'));print('total',round(sum(s[\"dur\"] for s in t['scenes']),2),[s['dur'] for s in t['scenes']])"

echo "== mix audio"
python3 - "$FF" "$V/timeline.json" "$VO" "$OUT/mix.wav" <<'PY'
import json, subprocess, sys
ff, tl, vo, out = sys.argv[1:5]
t = json.load(open(tl)); acc = 0.0; inputs = []; filt = []
for i, s in enumerate(t["scenes"]):
    start = acc + s["lead"]; acc += s["dur"]
    inputs += ["-i", f"{vo}/fast{i+1:02d}.wav"]
    filt.append(f"[{i}]adelay={int(start*1000)}|{int(start*1000)}[a{i}]")
n = len(t["scenes"]); total = acc
filt.append("".join(f"[a{i}]" for i in range(n)) +
            f"amix=inputs={n}:normalize=0:dropout_transition=0,"
            f"apad=whole_dur={total:.3f},atrim=0:{total:.3f},loudnorm=I=-16:TP=-1.5:LRA=11[out]")
subprocess.run([ff, "-y", "-v", "error"] + inputs +
               ["-filter_complex", ";".join(filt), "-map", "[out]", "-ar", "48000", "-ac", "2", out], check=True)
print("mix ok, total", round(total, 2))
PY

echo "== render"
cd "$V" && NODE_PATH=$S/pwtest/node_modules node render.js \
  --html anim.html --timeline timeline.json --audio "$OUT/mix.wav" \
  --out "$OUT/gefen_savings_policies_h1_2026.mp4" --fps 30
"$FF" -v error -i "$OUT/gefen_savings_policies_h1_2026.mp4" -f null - && echo "decode ok"
ls -la "$OUT"
