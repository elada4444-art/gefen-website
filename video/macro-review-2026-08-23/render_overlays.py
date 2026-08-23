# -*- coding: utf-8 -*-
"""Render one transparent 1080x1920 PNG per text beat of the macro reel."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from storyboard import (W, H, BEATS, NAVY_DEEP, ORANGE, ORANGE_LT,
                        WHITE, GREEN, RED, MUTED, CREAM)

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "overlays")
os.makedirs(OUT, exist_ok=True)

try:                                     # python-bidi >= 0.6
    from bidi import get_display
except ImportError:                      # older releases
    from bidi.algorithm import get_display


def rtl(s):
    """Reorder a Hebrew (RTL base direction) string for visual rendering."""
    return "\n".join(get_display(line, base_dir="R") for line in s.split("\n"))


def ltr(s):
    """Numeric/Latin values render as-is; only mixed strings need reordering."""
    if all(ord(c) < 0x0590 for c in s):
        return s
    return "\n".join(get_display(line, base_dir="L") for line in s.split("\n"))


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONTS, f"Heebo-{weight}.ttf"), size)


F = {
    "display": lambda s: font(900, s),
    "bold":    lambda s: font(700, s),
    "medium":  lambda s: font(500, s),
    "regular": lambda s: font(400, s),
}

RIGHT = W - 88          # right text margin (RTL start edge)
LEFT = 88               # left text margin

# ---------------------------------------------------------------- primitives


def new_layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def bottom_scrim(img, top, strength=232, curve=2.1):
    """Soft transparent->navy gradient rising from the bottom of the frame."""
    h = H - top
    ramp = (np.linspace(0.0, 1.0, h) ** curve) * strength
    a = np.zeros((H, W), dtype=np.uint8)
    a[top:, :] = ramp[:, None].astype(np.uint8)
    grad = np.zeros((H, W, 4), dtype=np.uint8)
    grad[..., 0], grad[..., 1], grad[..., 2] = NAVY_DEEP
    grad[..., 3] = a
    img.alpha_composite(Image.fromarray(grad, "RGBA"))


def top_scrim(img, bottom, strength=190, curve=2.0):
    ramp = (np.linspace(1.0, 0.0, bottom) ** curve) * strength
    a = np.zeros((H, W), dtype=np.uint8)
    a[:bottom, :] = ramp[:, None].astype(np.uint8)
    grad = np.zeros((H, W, 4), dtype=np.uint8)
    grad[..., 0], grad[..., 1], grad[..., 2] = NAVY_DEEP
    grad[..., 3] = a
    img.alpha_composite(Image.fromarray(grad, "RGBA"))


def text_r(d, xy, s, f, fill, spacing=14):
    """Draw right-anchored text (RTL)."""
    d.multiline_text(xy, s, font=f, fill=fill, anchor="ra",
                     align="right", spacing=spacing)


def text_l(d, xy, s, f, fill):
    d.text(xy, s, font=f, fill=fill, anchor="la")


def fit(weight, size, s, max_w, spacing=14, min_size=22):
    """Largest size <= `size` at which every line of `s` fits in `max_w`."""
    while size > min_size:
        f = font(weight, size)
        if measure(f, s, spacing)[0] <= max_w:
            return f
        size -= 2
    return font(weight, min_size)


def measure(f, s, spacing=14):
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    box = tmp.multiline_textbbox((0, 0), s, font=f, spacing=spacing)
    return box[2] - box[0], box[3] - box[1]


def flag_chip(d, x_right, y, kind, label, chip_h=64):
    """Small flag + country label chip, laid out right-to-left."""
    fw, fh = 60, 40
    fx = x_right - fw
    fy = y + (chip_h - fh) // 2

    if kind == "us":
        d.rectangle([fx, fy, fx + fw, fy + fh], fill=(178, 34, 52))
        for i in range(1, 13, 2):                       # white stripes
            sy = fy + int(fh * i / 13)
            d.rectangle([fx, sy, fx + fw, sy + int(fh / 13)], fill=WHITE)
        d.rectangle([fx, fy, fx + int(fw * 0.42), fy + int(fh * 0.54)],
                    fill=(35, 51, 110))
        for r in range(4):
            for c in range(5):
                cx = fx + 5 + c * 4.6
                cy = fy + 4 + r * 4.6
                d.ellipse([cx, cy, cx + 2.0, cy + 2.0], fill=WHITE)
    else:                                               # Israel
        d.rectangle([fx, fy, fx + fw, fy + fh], fill=WHITE)
        blue = (0, 56, 148)
        d.rectangle([fx, fy + 4, fx + fw, fy + 10], fill=blue)
        d.rectangle([fx, fy + fh - 10, fx + fw, fy + fh - 4], fill=blue)
        cx, cy, r = fx + fw / 2, fy + fh / 2, 10.5
        import math
        for rot in (0, 180):
            pts = [(cx + r * math.sin(math.radians(rot + a)),
                    cy - r * math.cos(math.radians(rot + a)))
                   for a in (0, 120, 240)]
            d.line(pts + [pts[0]], fill=blue, width=3, joint="curve")

    d.rectangle([fx - 2, fy - 2, fx + fw + 2, fy + fh + 2], outline=(255, 255, 255, 70), width=2)

    f = F["bold"](40)
    text_r(d, (fx - 22, y + (chip_h - 48) // 2), rtl(label), f, WHITE)


def accent_rule(d, x_right, y, w=132, h=7, color=ORANGE):
    d.rounded_rectangle([x_right - w, y, x_right, y + h], radius=h // 2, fill=color)


# ------------------------------------------------------------------- layouts

BODY_W = RIGHT - LEFT          # widest a full-bleed text block may be


def draw_title(b):
    img = new_layer()
    d = ImageDraw.Draw(img)
    # full-frame darkening so the opening title reads over bright city lights
    img.alpha_composite(Image.new("RGBA", (W, H), NAVY_DEEP + (110,)))
    bottom_scrim(img, 900, strength=225)

    kicker, title, sub = rtl(b["kicker"]), rtl(b["title"]), rtl(b["sub"])
    f_t = fit(900, 148, title, BODY_W, spacing=4)

    y = 1085
    text_r(d, (RIGHT, y), kicker, fit(700, 46, kicker, BODY_W), ORANGE_LT)
    y += 78
    accent_rule(d, RIGHT, y, w=150, h=8)
    y += 52
    text_r(d, (RIGHT, y), title, f_t, WHITE, spacing=4)
    y += measure(f_t, title, 4)[1] + 54
    text_r(d, (RIGHT, y), sub, fit(500, 42, sub, BODY_W), MUTED)
    return img


def draw_header(b):
    img = new_layer()
    d = ImageDraw.Draw(img)
    top_scrim(img, 460, strength=170)
    bottom_scrim(img, 980, strength=228)

    flag_chip(d, RIGHT, 170, b["flag"], b["country"])

    head = rtl(b["headline"])
    f_h = fit(900, 104, head, BODY_W, spacing=18)
    y = 1210
    accent_rule(d, RIGHT, y, w=150, h=8)
    y += 54
    text_r(d, (RIGHT, y), head, f_h, WHITE, spacing=18)
    return img


def draw_card(b):
    img = new_layer()
    d = ImageDraw.Draw(img)
    top_scrim(img, 380, strength=150)

    rows, foot = b["rows"], b.get("foot")
    card_h = 240 + len(rows) * 122 + (108 if foot else 0)
    card_y0 = H - 190 - card_h
    card_x0, card_x1 = 60, W - 60

    bottom_scrim(img, card_y0 - 220, strength=235)

    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle(
        [card_x0, card_y0, card_x1, card_y0 + card_h], radius=46,
        fill=NAVY_DEEP + (214,), outline=(255, 255, 255, 38), width=2)
    img.alpha_composite(panel)

    # orange rail down the right (RTL leading) edge of the card
    d.rounded_rectangle([card_x1 - 12, card_y0 + 34, card_x1 - 5,
                         card_y0 + card_h - 34], radius=4, fill=ORANGE)

    pad_r, pad_l = card_x1 - 52, card_x0 + 52
    inner = pad_r - pad_l
    y = card_y0 + 48

    eyebrow = rtl(b["eyebrow"])
    if b.get("flag"):
        flag_chip(d, pad_r, y - 6, b["flag"], "", chip_h=52)
        text_r(d, (pad_r - 84, y + 2), eyebrow,
               fit(700, 40, eyebrow, inner - 100), ORANGE_LT)
    else:
        text_r(d, (pad_r, y + 2), eyebrow, fit(700, 40, eyebrow, inner), ORANGE_LT)
    y += 96
    d.line([pad_l, y, pad_r, y], fill=(255, 255, 255, 46), width=2)
    y += 34

    tone = {"pos": GREEN, "neg": RED, "up": ORANGE_LT, "neutral": WHITE}
    for i, (label, value, kind) in enumerate(rows):
        val, lbl = ltr(value), rtl(label)
        f_v = fit(900, 64, val, inner * 0.45)
        vw = measure(f_v, val)[0]
        text_l(d, (pad_l, y - 6), val, f_v, tone[kind])
        text_r(d, (pad_r, y), lbl, fit(500, 50, lbl, inner - vw - 46), (226, 234, 247))
        y += 122
        if i < len(rows) - 1:
            d.line([pad_l, y - 30, pad_r, y - 30], fill=(255, 255, 255, 22), width=2)

    if foot:
        ft = rtl(foot)
        text_r(d, (pad_r, y + 6), ft, fit(500, 38, ft, inner), MUTED)
    return img


def draw_driver(b):
    img = new_layer()
    d = ImageDraw.Draw(img)
    top_scrim(img, 380, strength=150)
    bottom_scrim(img, 900, strength=234)

    title, body = rtl(b["title"]), rtl(b["body"])
    r, y = 46, 1140

    # numbered badge
    d.ellipse([RIGHT - 2 * r, y, RIGHT, y + 2 * r], fill=ORANGE)
    d.text((RIGHT - r, y + r - 2), b["num"], font=F["display"](56),
           fill=(20, 24, 38), anchor="mm")
    text_r(d, (RIGHT - 2 * r - 30, y + 6), title,
           fit(900, 72, title, BODY_W - 2 * r - 30), WHITE)

    y += 2 * r + 46
    accent_rule(d, RIGHT, y, w=110, h=6, color=(255, 255, 255, 90))
    y += 44
    f_b = fit(500, 50, body, BODY_W, spacing=18)
    text_r(d, (RIGHT, y), body, f_b, (222, 231, 245), spacing=18)

    if b.get("foot"):
        ft = rtl(b["foot"])
        y += measure(f_b, body, 18)[1] + 44
        text_r(d, (RIGHT, y), ft, fit(700, 40, ft, BODY_W), ORANGE_LT)
    return img


def draw_closing(b):
    img = new_layer()
    d = ImageDraw.Draw(img)
    img.alpha_composite(Image.new("RGBA", (W, H), NAVY_DEEP + (150,)))
    bottom_scrim(img, 820, strength=240)

    eyebrow = rtl(b["eyebrow"])
    y = 1010
    text_r(d, (RIGHT, y), eyebrow, fit(700, 46, eyebrow, BODY_W), ORANGE_LT)
    y += 76
    accent_rule(d, RIGHT, y, w=150, h=8)
    y += 60

    for line in b["lines"]:
        s_ = rtl(line)
        d.ellipse([RIGHT - 16, y + 22, RIGHT - 2, y + 36], fill=ORANGE)
        text_r(d, (RIGHT - 42, y), s_, fit(700, 62, s_, BODY_W - 42), WHITE)
        y += 106

    y += 40
    d.line([LEFT, y, RIGHT, y], fill=(255, 255, 255, 52), width=2)
    y += 44

    brand = rtl(b["brand"])
    logo_p = os.path.join(HERE, "logo.png")
    if os.path.exists(logo_p):
        logo = Image.open(logo_p).convert("RGBA")
        lh = 132
        lw = int(logo.width * lh / logo.height)
        logo = logo.resize((lw, lh), Image.LANCZOS)
        img.alpha_composite(logo, (RIGHT - lw, y))
        text_r(d, (RIGHT - lw - 34, y + 34), brand,
               fit(700, 40, brand, BODY_W - lw - 34), CREAM)
    else:
        text_r(d, (RIGHT, y + 10), brand, fit(700, 48, brand, BODY_W), CREAM)
    return img


DRAW = {"title": draw_title, "header": draw_header, "card": draw_card,
        "driver": draw_driver, "closing": draw_closing}


def main():
    for i, b in enumerate(BEATS):
        img = DRAW[b["kind"]](b)
        path = os.path.join(OUT, f"beat_{i:02d}.png")
        img.save(path)
        print("wrote", path, b["kind"])


if __name__ == "__main__":
    main()
