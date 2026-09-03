#!/usr/bin/env bash
# Build the shortened (30-40s, 5-scene) explainer: layout the timeline, mix audio, render.
set -euo pipefail
S=/tmp/claude-0/-home-user-gefen-website/d7cc3944-8b91-561b-b675-19160c1e1a80/scratchpad
VO=$S/vo; V=$S/video; OUT=$V/out; mkdir -p "$OUT"
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")

echo "== convert opus -> wav (already 1.5x speed) for scenes 1-4, wav already exists for scene 5"
for n in 01 02 03 04; do
  [ -s "$VO/fast$n.opus" ] || { echo "missing $VO/fast$n.opus"; exit 1; }
  "$FF" -v error -y -i "$VO/fast$n.opus" -ac 1 -ar 48000 -c:a pcm_s16le "$VO/short$n.wav"
done
cp "$VO/fast08.wav" "$VO/short05.wav"
for n in 01 02 03 04 05; do
  printf 'short%s %s\n' "$n" "$("$FF" -hide_banner -i "$VO/short$n.wav" 2>&1 | sed -n 's/.*Duration: \([0-9:.]*\).*/\1/p')"
done

echo "== timeline"
python3 - "$FF" "$VO" > "$V/timeline.json" <<'PY'
import json, re, subprocess, sys
ff, vo = sys.argv[1], sys.argv[2]
caps = [
 "פוליסות החיסכון גייסו <b>21.8 מיליארד ₪</b> במחצית הראשונה של 2026 — זינוק של 57% לעומת אשתקד.",
 "<b>הפניקס</b> מובילה בפער גדול: 7.55 מיליארד ₪, עלייה של 18%.",
 "ההפתעה: <b>איילון</b> קפצה מ-315 מיליון ₪ ל-3.19 מיליארד. זינוק של כ-910%, ישר למקום השני.",
 "איילון חוזרת גם לענף <b>הגמל</b>, עם הערכות לגיוס של כמיליארד ₪ כבר בחודש הראשון.",
 "רוצים להבין מה זה אומר על החיסכון שלכם? <b>גפן ביטוח ופיננסים</b> · מלווים אתכם בהחלטות.",
]
def dur(p):
    out = subprocess.run([ff, "-i", p], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)
scenes = []
for i in range(5):
    a = dur(f"{vo}/short{i+1:02d}.wav")
    lead = 0.8 if i == 0 else 0.45
    tail = 1.8 if i == 4 else 0.6
    scenes.append({"id": f"s{i+1}", "audio": round(a, 3), "lead": lead,
                   "dur": round(a + lead + tail, 3), "cap": caps[i]})
print(json.dumps({"scenes": scenes}, ensure_ascii=False, indent=1))
PY
python3 -c "import json;t=json.load(open('$V/timeline.json'));print('total',round(sum(s[\"dur\"] for s in t['scenes']),2),[s['dur'] for s in t['scenes']])"

echo "== mix audio"
python3 - "$FF" "$V/timeline.json" "$VO" "$OUT/mix_short.wav" <<'PY'
import json, subprocess, sys
ff, tl, vo, out = sys.argv[1:5]
t = json.load(open(tl)); acc = 0.0; inputs = []; filt = []
for i, s in enumerate(t["scenes"]):
    start = acc + s["lead"]; acc += s["dur"]
    inputs += ["-i", f"{vo}/short{i+1:02d}.wav"]
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
  --html anim.html --timeline timeline.json --audio "$OUT/mix_short.wav" \
  --out "$OUT/gefen_savings_policies_h1_2026_short.mp4" --fps 30
"$FF" -v error -i "$OUT/gefen_savings_policies_h1_2026_short.mp4" -f null - && echo "decode ok"
ls -la "$OUT"
