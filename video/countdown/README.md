# "מידע חשוב בנוגע לכסף שלכם בעוד 3…2…1…" — countdown opener

A 6.4s, 1080×1920 (9:16) opener on a white background: the Gefen logo, the
headline revealed word by word, and a 3…2…1 counter. No narration, no music —
the MP4 carries no audio stream at all.

The scene is plain HTML/CSS driven by a single deterministic `render(t)`
function — nothing reads the wall clock, so frame *n* is always identical.
The renderer seeks to `t = n / 30` and screenshots, which is why the output is
reproducible rather than dependent on how fast the machine happens to be.

## Rendering

```bash
./fetch_fonts.sh   # Heebo (the site's own family), inlined as data: URIs
node build.js      # scene.template.html + fonts + logo -> scene.html
node render.js     # scene.html -> frames/0001.png … 0192.png
./encode.sh        # frames -> gefen-countdown-1080x1920.mp4
```

Needs `ffmpeg`, `node`, `playwright-core`, and a Chromium binary
(`render.js` points at `/opt/pw-browsers/chromium`).

The MP4 is not committed — the repo's `.gitignore` keeps `*.mp4` out by design.

## Editing

Everything lives in `scene.template.html`:

- **Copy** — the `LINE1` / `LINE2` arrays and the `#beod` element. Each array
  entry animates as its own word, in RTL order (first entry = rightmost).
- **Timing** — the `T_*` constants. `T_COUNT0` is when the counter starts and
  `T_STEP` is one second per digit; `DUR` is the total length.
- **Digits** — the `DIGITS` array. `calibrate()` measures each glyph's ink box
  and offsets it, because centering the element only centers the *advance* box
  and Heebo's "1" sits noticeably right inside its own.
- **Palette** — `#0a5aa1` and `#fd6802` are sampled from `assets/logo.png`, so
  the type and the ring match the mark exactly.

## Other aspect ratios

Change the `viewport` in `render.js`, the `html,body`/`#stage` size in the
template, and the ffmpeg output name. Positions are absolute pixel values
tuned for 1080×1920, so a 1:1 or 16:9 cut needs the vertical offsets retuned.
