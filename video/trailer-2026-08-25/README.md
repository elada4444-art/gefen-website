# טריילר סקירת מאקרו — 25 באוגוסט 2026

A 60-second vertical (1080×1920) film-trailer cut of the weekly macro review,
carrying the Gefen logo as an opening sting, a standing corner bug, and a
closing card.

## How it is put together

1. **`storyboard.py`** is the edit decision list: every segment names its
   source, its in-point, its length and the text beats laid over it. Change
   the copy or the cut here and nowhere else.
2. **`render.py`** paints everything that is not footage — the two logo
   stings frame by frame, the black title cards, and one transparent overlay
   per text beat. It lifts the logo off its white background by
   unpremultiplying the white, so the mark sits cleanly on black.
   Hebrew is passed to Pillow in logical order and laid out by Raqm, which
   runs the bidi algorithm itself; pre-reordering with python-bidi would
   reverse it a second time. The renderer refuses to run if Raqm is missing
   or if any character in the storyboard is absent from Heebo.
3. **`build.py`** normalises each segment (grade, vignette, grain, letterbox
   bars, the standing logo bug), dissolves the text on, and concatenates.

## Running it

```bash
./fetch.sh                        # Heebo + the Gefen logo
pip install Pillow numpy fonttools   # the Pillow wheel must include libraqm
python3 render.py                 # -> art/
# put the eight stock shots in clips/ named after storyboard.SOURCES
python3 build.py                  # -> out/gefen_trailer.mp4
```

See `sources.md` for the shot list.
