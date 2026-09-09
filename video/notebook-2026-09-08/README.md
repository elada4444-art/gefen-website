# סרטון "מחברת חשבון" — סקירת 8 בספטמבר 2026

A 60-second vertical (1080×1920) explainer drawn entirely in code: squared
notebook paper, and a cast of writing tools — blue ballpoint, red pen, black
marker, pencil, highlighter and an eraser — that write, sketch, circle and
wipe the review's numbers, ending on a call to action with the Gefen logo
stuck to the page. No AI generation and no stock footage: zero credits, and
every frame can be inspected locally.

## How it is put together

- **`storyboard.py`** — the whole film as data: nine scenes, each a list of
  strokes with a tool, a start time, a duration and what it draws (text,
  underline, circle, arrow, axes, staircase, bars, calendar, table,
  highlighter, three doodles, the logo sticker). Change copy or timing here.
- **`render.py`** — paints one frame for any time: the paper (grid, red
  margin on the right, spiral binding, grain), every stroke of the current
  scene drawn as far as the hand has got, then the tool held at the stroke's
  tip. Text is revealed in its reading direction; lines get a deterministic
  hand tremor; pencil is grainy; the highlighter multiplies like real ink;
  the eraser wipe and page turn live here too. It refuses to run without Raqm
  or if any character is missing from the font that writes it.
- **`encode.py`** — renders all 1,440 frames on four processes and streams
  them straight into ffmpeg (libx264, CRF 18).

Fonts (all OFL, from Google Fonts): Gveret Levin for the pens, Karantina Bold
for the marker, Amatic SC Bold for the pencil.

## Running it

```bash
./fetch.sh                                  # the logo
pip install Pillow numpy fonttools imageio-ffmpeg   # Pillow wheel must include libraqm
python3 render.py                            # glyph check only
python3 render.py proof 1.2 8.6 55.0         # PNGs of chosen seconds into proof/
python3 encode.py                            # -> out/gefen_notebook.mp4
```
