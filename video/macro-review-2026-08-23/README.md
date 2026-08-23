# סרטון סקירת מאקרו — מעבר רחפן

Pipeline that turns a weekly macro/markets review into a 60-second vertical
(1080×1920) drone-flyover reel with Hebrew data cards.

## How it is put together

1. **Eight aerial shots** are generated with Kling 2.5 (1080p, 9:16) — the
   flight path follows the review: orbit → US east coast → Wall Street →
   the Treasury in Washington → an AI data-center campus → a Gulf oil
   terminal → the Tetons → the Mediterranean into Tel Aviv → Jerusalem.
   Prompts live in `prompts.md`.
2. **`render_overlays.py`** draws one transparent 1080×1920 PNG per text beat
   (`storyboard.py` holds the copy, the timings and the palette). Hebrew goes
   to Pillow in logical order and Raqm lays it out — it runs bidi and the
   OpenType shaper itself, so pre-reordering the strings with python-bidi
   would reverse them a second time and render mirrored gibberish. Every
   string is shrink-to-fit so nothing can run off the frame.
3. **`build_reel.py`** dissolves each card onto its shot with ffmpeg, then
   concatenates the eight segments and draws the right-to-left progress rail.

## Running it

```bash
./fetch_assets.sh                 # Heebo + the Gefen logo
pip install Pillow numpy      # the Pillow wheel must include libraqm
python3 render_overlays.py        # -> overlays/beat_NN.png
# put the eight source shots in clips/ named after storyboard.CLIPS keys
python3 build_reel.py             # -> out/gefen_macro_reel.mp4
```

Editing the copy or the beat timings only means editing `storyboard.py` — the
renderer and the assembly both read their layout from it.
