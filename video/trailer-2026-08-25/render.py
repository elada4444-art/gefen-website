# -*- coding: utf-8 -*-
"""Render every painted element of the trailer: the logo open and close frame
sequences, the full-frame title cards, and one transparent overlay per text
beat.

Hebrew is handed to Pillow in logical order and laid out by Raqm, which runs
the bidi algorithm itself. Never pre-reorder with python-bidi here — that
reverses the strings a second time and renders mirrored gibberish.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, features

from storyboard import (W, H, FPS, EDL, NAVY_DEEP, ORANGE, ORANGE_LT,
                           CREAM, WHITE, MUTED, BAR)

if not features.check("raqm"):
    raise SystemExit("Pillow lacks Raqm; Hebrew cannot be laid out correctly.")

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "art")
os.makedirs(OUT, exist_ok=True)

MID = W // 2
SAFE = W - 150            # widest a centred line may be


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONTS, f"Heebo-{weight}.ttf"), size)


def measure(f, s, spacing=16, direction="rtl"):
    d = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    b = d.multiline_textbbox((0, 0), s, font=f, spacing=spacing,
                             direction=direction, language="he")
    return b[2] - b[0], b[3] - b[1]


def fit(weight, size, s, max_w, spacing=16, min_size=20, direction="rtl"):
    while size > min_size:
        f = font(weight, size)
        if measure(f, s, spacing, direction)[0] <= max_w:
            return f
        size -= 2
    return font(weight, min_size)


def text_c(d, xy, s, f, fill, spacing=16, direction="rtl", shadow=True):
    """Centred text with a soft drop shadow so it holds over live footage."""
    kw = dict(font=f, anchor="ma", align="center", spacing=spacing,
              direction=direction, language="he" if direction == "rtl" else None)
    if shadow:
        for dx, dy in ((0, 4), (0, 3)):
            d.multiline_text((xy[0] + dx, xy[1] + dy), s, fill=(0, 0, 0, 150), **kw)
    d.multiline_text(xy, s, fill=fill, **kw)


def joined(lines):
    return "\n".join(lines)


def assert_glyph_coverage():
    """Every character in the storyboard must exist in Heebo."""
    from fontTools.ttLib import TTFont
    covered = set()
    for w in (400, 500, 700, 900):
        for table in TTFont(os.path.join(FONTS, f"Heebo-{w}.ttf"))["cmap"].tables:
            covered |= set(table.cmap.keys())

    def walk(node):
        if isinstance(node, str):
            yield node
        elif isinstance(node, dict):
            for v in node.values():
                yield from walk(v)
        elif isinstance(node, (list, tuple)):
            for v in node:
                yield from walk(v)

    missing = {c for s in walk(EDL) for c in s
               if ord(c) not in covered and c not in "\n"}
    if missing:
        raise SystemExit("Heebo cannot render: " +
                         " ".join(f"{c!r} (U+{ord(c):04X})" for c in sorted(missing)))


# ------------------------------------------------------------------ the logo


def logo_rgba():
    """The Gefen logo lifted off its white background.

    The artwork is ink on white, so the white is unpremultiplied out: alpha
    comes from how far each pixel sits from white, and the colour is recovered
    by removing the white that was showing through.
    """
    src = np.asarray(Image.open(os.path.join(HERE, "logo.png")).convert("RGB")).astype(np.float32)
    a = 1.0 - src.min(axis=2) / 255.0
    a = np.clip(a * 1.06, 0.0, 1.0)
    safe = np.maximum(a, 1e-4)[..., None]
    rgb = np.clip((src - 255.0 * (1.0 - safe)) / safe, 0, 255)
    out = np.dstack([rgb, a * 255.0]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def scaled_logo(width, halo=True):
    lg = logo_rgba()
    lg = lg.resize((width, max(1, round(lg.height * width / lg.width))), Image.LANCZOS)
    if not halo:
        return lg
    # the wordmark is dark navy ink; on black it needs a soft light backing to
    # separate from the background without touching the brand colours
    pad = 34
    out = Image.new("RGBA", (lg.width + pad * 2, lg.height + pad * 2), (0, 0, 0, 0))
    glow = Image.new("RGBA", out.size, (255, 240, 220, 0))
    mask = Image.new("L", out.size, 0)
    mask.paste(lg.getchannel("A"), (pad, pad))
    glow.putalpha(mask.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.45)))
    out.alpha_composite(glow)
    out.alpha_composite(lg, (pad, pad))
    return out


def radial_glow(radius, colour, peak=0.55):
    """Soft circular bloom used behind the logo on the open and close."""
    y, x = np.ogrid[:H, :W]
    r = np.hypot(x - MID, y - H / 2) / radius
    a = np.clip(1.0 - r, 0.0, 1.0) ** 2.2 * peak * 255
    g = np.zeros((H, W, 4), np.uint8)
    g[..., 0], g[..., 1], g[..., 2] = colour
    g[..., 3] = a.astype(np.uint8)
    return Image.fromarray(g, "RGBA")


def ease(t):
    return 0.0 if t <= 0 else 1.0 if t >= 1 else 1 - pow(1 - t, 3)


# ----------------------------------------------------------- logo sequences


def logo_open_frame(t, dur, tagline):
    """t seconds into the opening sting."""
    img = Image.new("RGB", (W, H), (0, 0, 0)).convert("RGBA")

    glow = ease((t - 0.35) / 1.5)
    if glow > 0:
        img.alpha_composite(radial_glow(760, ORANGE, 0.42 * glow))

    appear = ease((t - 0.5) / 1.1)
    if appear > 0:
        lw = round(720 * (1.06 - 0.06 * appear))
        lg = scaled_logo(lw)
        lg.putalpha(lg.getchannel("A").point(lambda v: int(v * appear)))

        # a hard light sweep travelling across the mark
        sweep = (t - 1.5) / 1.1
        if 0.0 <= sweep <= 1.0:
            band = Image.new("L", lg.size, 0)
            bd = ImageDraw.Draw(band)
            cx = int(-lg.width * 0.4 + sweep * lg.width * 1.8)
            bd.polygon([(cx, lg.height), (cx + 90, lg.height),
                        (cx + 190, 0), (cx + 100, 0)], fill=190)
            band = band.filter(ImageFilter.GaussianBlur(18))
            shine = Image.new("RGBA", lg.size, (255, 255, 255, 0))
            shine.putalpha(Image.composite(band, Image.new("L", lg.size, 0),
                                           lg.getchannel("A")))
            lg.alpha_composite(shine)

        img.alpha_composite(lg, (MID - lg.width // 2, H // 2 - lg.height // 2 - 60))

    rule = ease((t - 2.3) / 0.8)
    if rule > 0:
        half = int(230 * rule)
        ImageDraw.Draw(img).rounded_rectangle(
            [MID - half, H // 2 + 120, MID + half, H // 2 + 127], radius=4, fill=ORANGE)

    tag = ease((t - 2.9) / 0.9)
    if tag > 0 and tagline:
        d = ImageDraw.Draw(img)
        f = fit(500, 46, tagline, SAFE)
        text_c(d, (MID, H // 2 + 180), tagline, f,
               (*CREAM, int(235 * tag)), shadow=False)

    # a single frame of near-white to cut out on
    if t >= dur - 2.0 / FPS:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 245, 232, 210)))
    return img.convert("RGB")


def logo_close_frame(t, dur, brand, credit, disclaimer):
    img = Image.new("RGB", (W, H), (0, 0, 0)).convert("RGBA")
    up = ease(t / 0.9)
    if up <= 0:
        return img.convert("RGB")

    img.alpha_composite(radial_glow(820, ORANGE, 0.34 * up))

    lg = scaled_logo(760)
    lg.putalpha(lg.getchannel("A").point(lambda v: int(v * up)))
    img.alpha_composite(lg, (MID - lg.width // 2, H // 2 - lg.height // 2 - 150))

    d = ImageDraw.Draw(img)
    rule = ease((t - 0.7) / 0.7)
    if rule > 0:
        half = int(250 * rule)
        d.rounded_rectangle([MID - half, H // 2 + 10, MID + half, H // 2 + 17],
                            radius=4, fill=ORANGE)

    b = ease((t - 1.0) / 0.8)
    if b > 0:
        text_c(d, (MID, H // 2 + 70), brand, fit(700, 52, brand, SAFE),
               (*WHITE, int(245 * b)), shadow=False)

    c = ease((t - 1.8) / 0.9)
    if c > 0:
        text_c(d, (MID, H // 2 + 190), credit, fit(400, 32, credit, SAFE - 60),
               (*MUTED, int(225 * c)), shadow=False)
        text_c(d, (MID, H // 2 + 246), disclaimer,
               fit(400, 28, disclaimer, SAFE - 60), (*MUTED, int(180 * c)), shadow=False)

    out = ease((t - (dur - 0.8)) / 0.8)
    if out > 0:
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * out))))
    return img.convert("RGB")


# ------------------------------------------------------------- title cards


def card(style, lines):
    """A full-frame cut-to-black title card."""
    img = Image.new("RGB", (W, H), (0, 0, 0)).convert("RGBA")
    img.alpha_composite(radial_glow(900, (40, 58, 96), 0.5))
    d = ImageDraw.Draw(img)
    s = joined(lines)

    if style == "slam":
        f = fit(900, 168, s, SAFE, spacing=6)
        h = measure(f, s, 6)[1]
        text_c(d, (MID, H // 2 - h // 2 - 40), s, f, WHITE, spacing=6, shadow=False)
        d.rounded_rectangle([MID - 150, H // 2 + h // 2 + 20,
                             MID + 150, H // 2 + h // 2 + 28], radius=4, fill=ORANGE)
    else:                                     # "beat"
        f = fit(700, 96, s, SAFE, spacing=8)
        h = measure(f, s, 8)[1]
        text_c(d, (MID, H // 2 - h // 2), s, f, CREAM, spacing=8, shadow=False)
    return img.convert("RGB")


# ------------------------------------------------- overlays laid over footage


def scrim(img, top, strength=224, curve=2.0):
    h = H - top
    ramp = (np.linspace(0.0, 1.0, h) ** curve) * strength
    a = np.zeros((H, W), np.uint8)
    a[top:, :] = ramp[:, None].astype(np.uint8)
    g = np.zeros((H, W, 4), np.uint8)
    g[..., 0], g[..., 1], g[..., 2] = (6, 10, 20)
    g[..., 3] = a
    img.alpha_composite(Image.fromarray(g, "RGBA"))


def overlay(beat):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    style = beat["style"]

    if style == "whisper":
        scrim(img, 980, 200)
        s = joined(beat["lines"])
        f = fit(500, 74, s, SAFE, spacing=22)
        text_c(d, (MID, 1240), s, f, (238, 244, 255), spacing=22)

    elif style in ("line", "slam_over"):
        scrim(img, 1010, 232)
        s = joined(beat["lines"])
        size, weight = (168, 900) if style == "slam_over" else (86, 900)
        f = fit(weight, size, s, SAFE, spacing=14)
        y = 1300 if style == "slam_over" else 1250
        text_c(d, (MID, y), s, f, WHITE, spacing=14)
        if beat.get("foot"):
            ft = beat["foot"]
            y += measure(f, s, 14)[1] + 44
            text_c(d, (MID, y), ft, fit(500, 42, ft, SAFE), ORANGE_LT)

    elif style == "stat":
        scrim(img, 980, 232)
        big = beat["big"]
        bdir = beat.get("big_dir", "rtl")
        fb = fit(900, 190, big, SAFE, direction=bdir)
        text_c(d, (MID, 1150), big, fb, ORANGE_LT, direction=bdir)
        s = joined(beat["lines"])
        y = 1150 + measure(fb, big)[1] + 40
        text_c(d, (MID, y), s, fit(500, 50, s, SAFE, spacing=14), WHITE, spacing=14)

    elif style == "pair":
        scrim(img, 980, 232)
        y = 1180
        for name, value in beat["pairs"]:
            text_c(d, (MID + 210, y), name, fit(500, 52, name, 380), (226, 234, 247))
            text_c(d, (MID - 190, y - 8), value, fit(900, 76, value, 380),
                   ORANGE_LT, direction="ltr")
            y += 118
        if beat.get("foot"):
            text_c(d, (MID, y + 24), beat["foot"],
                   fit(500, 42, beat["foot"], SAFE), WHITE)

    elif style == "versus":
        scrim(img, 900, 240)
        y = 1120
        for i, (cap, val) in enumerate((beat["first"], beat["second"])):
            cx = MID + (250 if i == 0 else -250)
            colour = ORANGE_LT if i == 0 else (226, 234, 247)
            text_c(d, (cx, y), cap, fit(500, 40, cap, 430), MUTED)
            text_c(d, (cx, y + 58), val, fit(900, 62, val, 430), colour, spacing=8)
        d.rounded_rectangle([MID - 3, y - 10, MID + 3, y + 190],
                            radius=3, fill=(255, 255, 255, 70))
    return img


# --------------------------------------------------------------------- main


def main():
    assert_glyph_coverage()
    logo_rgba().save(os.path.join(OUT, "logo_alpha.png"))
    scaled_logo(230, halo=False).save(os.path.join(OUT, "logo_mark.png"))

    seq = 0
    for i, seg in enumerate(EDL):
        kind = seg["kind"]
        if kind in ("logo_open", "logo_close"):
            d = os.path.join(OUT, "seq_%02d" % i)
            os.makedirs(d, exist_ok=True)
            n = int(round(seg["dur"] * FPS))
            for k in range(n):
                t = k / FPS
                if kind == "logo_open":
                    f = logo_open_frame(t, seg["dur"], seg["tagline"])
                else:
                    f = logo_close_frame(t, seg["dur"], seg["brand"],
                                         seg["credit"], seg["disclaimer"])
                f.save(os.path.join(d, "f_%04d.png" % k))
            seq += 1
            print("rendered", kind, n, "frames")
        elif kind == "card":
            card(seg["style"], seg["lines"]).save(
                os.path.join(OUT, "card_%02d.png" % i))
            print("rendered card", i, seg["lines"])
        else:
            for j, b in enumerate(seg.get("beats", [])):
                overlay(b).save(os.path.join(OUT, "ov_%02d_%d.png" % (i, j)))
                print("rendered overlay", i, j, b["style"])


if __name__ == "__main__":
    main()
