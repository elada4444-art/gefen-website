# -*- coding: utf-8 -*-
"""Frame renderer for the notebook cut.

Every frame is painted from scratch: squared paper, then each stroke of the
current scene drawn up to how far the hand has got, then the tool that is
writing, held at the stroke's tip. Hebrew goes to Pillow in logical order and
is laid out by Raqm — never pre-reorder it with python-bidi.
"""
import io
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, features

import storyboard as sb
from storyboard import (W, H, FPS, SCENES, WIPE, PAPER, GRID, MARGIN, INK_BLUE,
                        INK_RED, INK_BLACK, PENCIL, HILITE, CELL, RX)

if not features.check("raqm"):
    raise SystemExit("Pillow lacks Raqm; Hebrew cannot be laid out correctly.")

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "logo.png")

INK = {"pen": INK_BLUE, "red": INK_RED, "marker": INK_BLACK, "pencil": PENCIL}
ALPHA = {"pen": 232, "red": 232, "marker": 246, "pencil": 205}
WIDTH = {"pen": 5, "red": 6, "marker": 14, "pencil": 3}
JITTER = {"pen": 1.4, "red": 1.8, "marker": 1.0, "pencil": 2.4}

# ------------------------------------------------------------------ helpers

_font_cache = {}


def font(tool, size):
    key = (tool, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(os.path.join(HERE, sb.FONTS[tool]), size)
    return _font_cache[key]


def ease_out(p):
    return 1 - (1 - p) ** 3


def clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def resample(pts, step=6.0):
    """Even spacing along a polyline so partial draws and jitter behave."""
    out = [pts[0]]
    carry = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg == 0:
            continue
        d = step - carry
        while d <= seg:
            t = d / seg
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
            d += step
        carry = seg - (d - step)
    if out[-1] != pts[-1]:
        out.append(pts[-1])
    return out


def wobble(pts, amp, seed):
    """Low-frequency hand tremor, deterministic per stroke."""
    if amp <= 0 or len(pts) < 3:
        return pts
    rs = np.random.RandomState(seed)
    n = len(pts)
    noise = np.cumsum(rs.normal(0, 1, (n, 2)), axis=0)
    k = 9
    ker = np.ones(k) / k
    sm = np.stack([np.convolve(noise[:, i], ker, mode="same") for i in range(2)], 1)
    sm -= sm.mean(axis=0)
    scale = amp / (np.abs(sm).max() + 1e-6)
    return [(x + dx * scale, y + dy * scale) for (x, y), (dx, dy) in zip(pts, sm)]


def prefix(pts, p):
    """The first fraction `p` of a polyline (by arc length) and its tip."""
    if p >= 1:
        return pts, pts[-1]
    n = max(1, int(round((len(pts) - 1) * p)))
    return pts[: n + 1], pts[n]


def ink_line(draw, pts, tool, width=None):
    if len(pts) < 2:
        return
    w = width or WIDTH[tool]
    col = INK[tool] + (ALPHA[tool],)
    if tool == "pencil":
        # graphite: a darker core with a lighter, slightly offset grain
        draw.line(pts, fill=INK[tool] + (110,), width=w + 2, joint="curve")
        draw.line([(x + 1, y + 1) for x, y in pts], fill=INK[tool] + (150,), width=w, joint="curve")
    draw.line(pts, fill=col, width=w, joint="curve")
    r = w / 2
    for x, y in (pts[0], pts[-1]):
        draw.ellipse([x - r, y - r, x + r, y + r], fill=col)


# --------------------------------------------------------------------- paper

_paper = None


def paper():
    global _paper
    if _paper is not None:
        return _paper
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    for x in range(0, W, CELL):
        d.line([(x, 0), (x, H)], fill=GRID, width=1)
    for y in range(0, H, CELL):
        d.line([(0, y), (W, y)], fill=GRID, width=1)
    d.line([(RX, 0), (RX, H)], fill=MARGIN, width=3)
    # spiral binding along the top edge
    for x in range(60, W - 40, 72):
        d.ellipse([x - 13, 22, x + 13, 48], fill=(226, 222, 212), outline=(180, 176, 166))
        d.ellipse([x - 9, 26, x + 9, 44], fill=(70, 72, 80))
        d.arc([x - 18, -30, x + 18, 40], 20, 160, fill=(150, 152, 160), width=6)
    # faint paper grain and a soft vignette
    rs = np.random.RandomState(7)
    arr = np.asarray(img).astype(np.int16)
    grain = rs.normal(0, 2.2, (H, W, 1)).astype(np.int16)
    yy, xx = np.mgrid[:H, :W]
    vig = 1 - 0.07 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    arr = np.clip((arr + grain) * vig[..., None], 0, 255).astype(np.uint8)
    _paper = Image.fromarray(arr, "RGB")
    return _paper


# ---------------------------------------------------------------- tool icons

_icons = {}


def icon(tool):
    """The tool drawn tip-at-centre on a square canvas, already tilted."""
    if tool in _icons:
        return _icons[tool]
    S = 720
    c = S // 2
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tool == "pencil":
        d.polygon([(c, c), (c + 34, c - 16), (c + 34, c + 16)], fill=(58, 58, 62))
        d.polygon([(c + 30, c - 15), (c + 92, c - 24), (c + 92, c + 24), (c + 30, c + 15)],
                  fill=(228, 198, 150))
        d.rectangle([c + 90, c - 24, c + 300, c + 24], fill=(246, 196, 44))
        d.rectangle([c + 90, c - 8, c + 300, c + 8], fill=(232, 176, 30))
        d.rectangle([c + 300, c - 26, c + 322, c + 26], fill=(196, 198, 204))
        d.rounded_rectangle([c + 322, c - 24, c + 352, c + 24], radius=8, fill=(236, 150, 160))
    elif tool in ("pen", "red"):
        body = (28, 60, 160) if tool == "pen" else (206, 40, 46)
        d.polygon([(c, c), (c + 44, c - 12), (c + 44, c + 12)], fill=(190, 192, 198))
        d.polygon([(c, c), (c + 12, c - 4), (c + 12, c + 4)], fill=(40, 40, 46))
        d.rectangle([c + 42, c - 20, c + 300, c + 20], fill=body)
        d.rectangle([c + 42, c - 20, c + 300, c - 10], fill=tuple(min(255, v + 40) for v in body))
        d.rounded_rectangle([c + 296, c - 22, c + 318, c + 22], radius=6, fill=(196, 198, 204))
        d.rectangle([c + 215, c - 32, c + 296, c - 22], fill=(196, 198, 204))
    elif tool == "marker":
        d.polygon([(c, c), (c + 40, c - 22), (c + 40, c + 22)], fill=(50, 50, 56))
        d.rectangle([c + 38, c - 32, c + 300, c + 32], fill=(24, 26, 32))
        d.rectangle([c + 38, c - 32, c + 300, c - 20], fill=(58, 60, 68))
        d.rectangle([c + 120, c - 34, c + 134, c + 34], fill=(200, 200, 205))
        d.rounded_rectangle([c + 296, c - 34, c + 330, c + 34], radius=10, fill=(24, 26, 32))
    elif tool == "hilite":
        d.polygon([(c, c - 14), (c, c + 14), (c + 44, c + 30), (c + 44, c - 30)], fill=(255, 236, 90))
        d.rectangle([c + 42, c - 34, c + 300, c + 34], fill=(252, 216, 40))
        d.rectangle([c + 42, c - 34, c + 300, c - 20], fill=(255, 238, 120))
        d.rounded_rectangle([c + 296, c - 36, c + 334, c + 36], radius=10, fill=(230, 190, 20))
    elif tool == "eraser":
        d.rounded_rectangle([c - 110, c - 46, c + 110, c + 46], radius=14, fill=(238, 150, 165))
        d.rounded_rectangle([c - 110, c + 2, c + 110, c + 46], radius=14, fill=(96, 130, 200))
        d.rectangle([c - 110, c - 6, c + 110, c + 12], fill=(96, 130, 200))
    if tool != "eraser":
        im = im.rotate(38, resample=Image.BICUBIC, center=(c, c))
    else:
        im = im.rotate(-12, resample=Image.BICUBIC, center=(c, c))
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    shadow.putalpha(im.getchannel("A").point(lambda v: int(v * 0.32)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(shadow, (10, 14))
    out.alpha_composite(im)
    _icons[tool] = out
    return out


def place_icon(frame, tool, tip, fade=1.0):
    ic = icon(tool)
    if fade < 1:
        ic = ic.copy()
        ic.putalpha(ic.getchannel("A").point(lambda v: int(v * fade)))
    x, y = int(tip[0]) - ic.width // 2, int(tip[1]) - ic.height // 2
    frame.alpha_composite(ic, (x, y))


# ------------------------------------------------------------------ strokes


class Text:
    """Handwriting: each line revealed in its reading direction."""

    def __init__(self, s, seed):
        self.s = s
        self.tool = s["tool"]
        self.f = font(self.tool, s["size"])
        self.lines = s["text"].split("\n")
        asc, desc = self.f.getmetrics()
        self.lh = int((asc + desc) * 1.02)
        self.asc = asc
        self.dir = "ltr" if s.get("ltr") else "rtl"
        counts = [max(1, len(l)) for l in self.lines]
        tot = sum(counts)
        self.spans = []
        acc = 0.0
        for c in counts:
            self.spans.append((acc / tot, (acc + c) / tot))
            acc += c
        # one image per line, plus its bbox on the page
        self.imgs = []
        for k, line in enumerate(self.lines):
            y = s["y"] + k * self.lh
            if "cx" in s:
                anchor, x = "ma", s["cx"]
            elif self.dir == "ltr":
                anchor, x = "ra", s["x"]
            else:
                anchor, x = "ra", s["x"]
            tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
            bb = tmp.textbbox((x, y), line, font=self.f, anchor=anchor,
                              direction=self.dir, language="he")
            pad = 14
            box = (int(bb[0]) - pad, int(bb[1]) - pad, int(bb[2]) + pad, int(bb[3]) + pad)
            im = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), (0, 0, 0, 0))
            dd = ImageDraw.Draw(im)
            dd.text((x - box[0], y - box[1]), line, font=self.f,
                    fill=INK[self.tool] + (ALPHA[self.tool],), anchor=anchor,
                    direction=self.dir, language="he")
            if self.tool == "pencil":          # lighter, grainier hand
                a = np.asarray(im.getchannel("A")).astype(np.float32)
                rs = np.random.RandomState(seed + k)
                a *= 0.78 + 0.22 * rs.rand(*a.shape)
                im.putalpha(Image.fromarray(a.astype(np.uint8), "L"))
            self.imgs.append((im, box))

    def draw(self, p, ink, hl):
        tip = None
        for (im, box), (a, b) in zip(self.imgs, self.spans):
            f = clamp((p - a) / (b - a)) if b > a else 1.0
            if f <= 0:
                continue
            w = box[2] - box[0]
            front = int(w * f)
            if f >= 1:
                ink.alpha_composite(im, (box[0], box[1]))
                continue
            mask = Image.new("L", im.size, 0)
            md = ImageDraw.Draw(mask)
            if self.dir == "rtl":
                md.rectangle([w - front, 0, w, im.height], fill=255)
                tx = box[0] + w - front
            else:
                md.rectangle([0, 0, front, im.height], fill=255)
                tx = box[0] + front
            part = im.copy()
            part.putalpha(Image.fromarray(
                (np.asarray(im.getchannel("A")) * (np.asarray(mask) / 255.0)).astype(np.uint8), "L"))
            ink.alpha_composite(part, (box[0], box[1]))
            tip = (tx, box[1] + 14 + self.asc * 0.72)
            break
        return tip


class Path:
    """Anything drawn as one or more polylines in order (with optional labels
    that appear once the hand passes a point along the way)."""

    def __init__(self, s, seed, polylines, labels=(), width=None, fill_hatch=()):
        self.s = s
        self.tool = s["tool"]
        self.width = width
        amp = JITTER[self.tool]
        self.polys = [wobble(resample(pl), amp, seed + i) for i, pl in enumerate(polylines)]
        lens = [max(1, len(pl) - 1) for pl in self.polys]
        tot = sum(lens)
        self.spans, acc = [], 0
        for n in lens:
            self.spans.append((acc / tot, (acc + n) / tot))
            acc += n
        self.labels = labels            # (progress_at, Text)
        self.hatch = fill_hatch         # (progress_at, polylines) drawn instantly

    def draw(self, p, ink, hl):
        d = ImageDraw.Draw(ink)
        tip = None
        for pl, (a, b) in zip(self.polys, self.spans):
            f = clamp((p - a) / (b - a))
            if f <= 0:
                break
            pts, t = prefix(pl, f)
            ink_line(d, pts, self.tool, self.width)
            if f < 1:
                tip = t
                break
        for at, lines in self.hatch:
            if p >= at:
                for pl in lines:
                    ink_line(d, pl, self.tool, 2)
        for at, txt in self.labels:
            if p >= at:
                q = clamp((p - at) / 0.12)
                txt.draw(q, ink, hl)
        return tip


class Hilite:
    def __init__(self, s, seed):
        self.s = s
        h = s["h"]
        if s.get("vertical"):
            cx = (s["x0"] + s["x1"]) / 2
            pts = [(cx, s["y"]), (cx, s["y"] + h)]
            self.w = abs(s["x0"] - s["x1"])
        else:
            cy = s["y"] + h / 2
            pts = [(s["x0"], cy), (s["x1"], cy)]
            self.w = h
        self.pts = wobble(resample(pts, 8), 3.0, seed)

    def draw(self, p, ink, hl):
        pts, tip = prefix(self.pts, p)
        if len(pts) >= 2:
            d = ImageDraw.Draw(hl)
            d.line(pts, fill=HILITE + (255,), width=self.w)
        return tip if p < 1 else None


class Sticker:
    """The logo dropped onto the page like a sticker, with tape."""

    def __init__(self, s, seed):
        self.s = s
        lg = Image.open(LOGO).convert("RGB")
        w = s["width"]
        lg = lg.resize((w, round(lg.height * w / lg.width)), Image.LANCZOS)
        pad = 26
        card = Image.new("RGBA", (lg.width + 2 * pad, lg.height + 2 * pad), (255, 255, 255, 255))
        card.paste(lg, (pad, pad))
        cd = ImageDraw.Draw(card)
        cd.rectangle([0, 0, card.width - 1, card.height - 1], outline=(225, 222, 214), width=2)
        # two strips of tape
        for x in (24, card.width - 24 - 120):
            tape = Image.new("RGBA", (120, 36), (255, 250, 200, 120))
            tape = tape.rotate(-6 if x < 100 else 7, expand=True, resample=Image.BICUBIC)
            card.alpha_composite(tape, (x, -8))
        card = card.rotate(-2.5, expand=True, resample=Image.BICUBIC)
        shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
        shadow.putalpha(card.getchannel("A").point(lambda v: int(v * 0.28)))
        shadow = shadow.filter(ImageFilter.GaussianBlur(10))
        self.shadow, self.card = shadow, card

    def draw(self, p, ink, hl):
        e = ease_out(p)
        scale = 1.28 - 0.28 * e
        cw, ch = int(self.card.width * scale), int(self.card.height * scale)
        card = self.card.resize((cw, ch), Image.LANCZOS)
        sh = self.shadow.resize((cw, ch), Image.LANCZOS)
        a = int(255 * min(1, p * 2.5))
        card.putalpha(card.getchannel("A").point(lambda v: v * a // 255))
        sh.putalpha(sh.getchannel("A").point(lambda v: v * a // 255))
        x = self.s["cx"] - cw // 2
        y = self.s["y"] - ch // 2
        ink.alpha_composite(sh, (x + 8, y + 14))
        ink.alpha_composite(card, (x, y))
        return None


# ------------------------------------------------------- stroke geometry


def label(tool, text, x, y, size, seed, cx=None, ltr=False):
    s = dict(tool=tool, text=text, size=size, y=y)
    if cx is not None:
        s["cx"] = cx
    else:
        s["x"] = x
    if ltr:
        s["ltr"] = True
    return Text(s, seed)


def build(s, seed):
    k = s["kind"]
    tool = s["tool"]
    if k == "text":
        return Text(s, seed)
    if k == "hilite":
        return Hilite(s, seed)
    if k == "logo":
        return Sticker(s, seed)

    if k == "underline":
        x0, x1, y = s["x0"], s["x1"], s["y"]
        n = 60
        if s.get("wavy"):
            pts = [(x0 + (x1 - x0) * i / n, y + 6 * math.sin(i / n * 2 * math.pi * 9)) for i in range(n + 1)]
        else:
            pts = [(x0, y), (x1, y)]
        polys = [pts]
        if s.get("double"):
            polys.append([(x1 + 20, y + 16), (x0 - 10, y + 16)])
        return Path(s, seed, polys)

    if k == "circle":
        cx, cy, rx, ry = s["x"], s["y"], s["rx"], s["ry"]
        pts = []
        for i in range(0, 140):
            a = math.radians(-70 + i * 2.85)          # 1.1 turns, overlapping like a real loop
            grow = 1 + 0.03 * (i / 140)
            pts.append((cx + rx * grow * math.cos(a), cy + ry * grow * math.sin(a)))
        return Path(s, seed, [pts])

    if k == "arrow":
        x0, y0, x1, y1 = s["x0"], s["y0"], s["x1"], s["y1"]
        ang = math.atan2(y1 - y0, x1 - x0)
        hl_ = 42
        h1 = (x1 - hl_ * math.cos(ang - 0.5), y1 - hl_ * math.sin(ang - 0.5))
        h2 = (x1 - hl_ * math.cos(ang + 0.5), y1 - hl_ * math.sin(ang + 0.5))
        return Path(s, seed, [[(x0, y0), (x1, y1)], [h1, (x1, y1), h2]])

    if k == "axes":
        x0, y0, x1, y1 = s["x0"], s["y0"], s["x1"], s["y1"]
        return Path(s, seed, [[(x0, y1), (x0, y0)], [(x0, y0), (x1, y0)],
                              [(x0 - 10, y1 + 14), (x0, y1), (x0 + 10, y1 + 14)],
                              [(x1 - 14, y0 - 10), (x1, y0), (x1 - 14, y0 + 10)]])

    if k == "stairs":
        x, y = s["x0"], s["y0"]
        sw, sh = s["step_w"], s["step_h"]
        pts = [(x, y)]
        labels = []
        n = len(s["labels"])
        for i, lab in enumerate(s["labels"]):
            pts.append((x + sw, y))
            labels.append(((i + 0.5) / n, label("pen", lab, None, y - 78, 52, seed + 50 + i,
                                                cx=x + sw / 2, ltr=True)))
            if i < n - 1:
                y += sh
                pts.append((x + sw, y))
                x += sw
        return Path(s, seed, [pts], labels=labels)

    if k == "bars":
        base = s["base_y"]
        polys, labels, hatch = [], [], []
        n = len(s["bars"])
        for i, (name, val, x) in enumerate(s["bars"]):
            hgt = val * s["scale"]
            bw = s["bar_w"]
            top = base - hgt
            polys.append([(x - bw / 2, base), (x - bw / 2, top), (x + bw / 2, top), (x + bw / 2, base)])
            lines = []
            for off in range(-int(hgt), int(bw), 26):
                xa, ya = x - bw / 2 + max(0, off), top + max(0, -off)
                xb, yb = x - bw / 2 + min(bw, off + hgt), top + min(hgt, hgt - (off + hgt - bw) if off + hgt > bw else hgt)
                # a simple diagonal: clip to the box
                p0 = (x - bw / 2 + max(0, off), top + max(0, -off))
                p1 = (x - bw / 2 + min(bw, off + hgt), top + min(hgt, hgt - max(0, off + hgt - bw)))
                lines.append(wobble(resample([p0, p1], 8), 1.0, seed + 90 + off))
            at = (i + 1) / n
            hatch.append((at - 0.5 / n * 0.4, lines))
            labels.append((at - 0.5 / n * 0.4, label("pen", f"{val} אלף", None, top - 70, 50, seed + 60 + i, cx=x)))
            labels.append((at - 0.5 / n * 0.6, label("pen", name, None, base + 14, 48, seed + 70 + i, cx=x)))
        return Path(s, seed, polys, labels=labels, fill_hatch=hatch)

    if k == "calendar":
        x0, y0 = s["x0"], s["y0"]
        cw, rh = s["col_w"], s["row_h"]
        ncol = len(s["heads"])
        x1 = x0 - cw * ncol
        yh = y0 + rh[0]
        y1 = yh + rh[1]
        polys = [[(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], [(x0, yh), (x1, yh)]]
        for c in range(1, ncol):
            polys.append([(x0 - cw * c, y0), (x0 - cw * c, y1)])
        labels = [(0.75 + 0.08 * c, label("pencil", hd, None, y0 + 26, 54, seed + 30 + c, cx=x0 - cw * c - cw / 2))
                  for c, hd in enumerate(s["heads"])]
        return Path(s, seed, polys, labels=labels)

    if k == "table":
        x0, y0, cols, rows, rh = s["x0"], s["y0"], s["cols"], s["rows"], s["row_h"]
        x1 = x0 - sum(cols)
        y1 = y0 + rows * rh
        polys = [[(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]]
        for r in range(1, rows):
            polys.append([(x0, y0 + r * rh), (x1, y0 + r * rh)])
        xx = x0
        for c in cols[:-1]:
            xx -= c
            polys.append([(xx, y0), (xx, y1)])
        return Path(s, seed, polys)

    if k == "table_rows":
        x0, y0, cols, rh, size = s["x0"], s["y0"], s["cols"], s["row_h"], s["size"]
        cells = []
        for r, row in enumerate(s["rows"]):
            xx = x0
            for c, (txt, cw) in enumerate(zip(row, cols)):
                if txt:
                    y = y0 + r * rh + 24
                    if c == 0:
                        cells.append(label("pen", txt, xx - 22, y, size, seed + r * 10 + c))
                    else:
                        cells.append(label("pen", txt, None, y, size + 4, seed + r * 10 + c,
                                           cx=xx - cw / 2, ltr=not any("֐" <= ch <= "׿" for ch in txt)))
                xx -= cw
        return Cells(s, cells)

    if k == "doodle_percent":
        cx, cy, r = s["x"], s["y"], s["r"]
        def ring(ox, oy, rr):
            return [(ox + rr * math.cos(math.radians(a)), oy + rr * math.sin(math.radians(a)))
                    for a in range(-90, 290, 6)]
        return Path(s, seed, [[(cx + r * 0.62, cy - r * 0.95), (cx - r * 0.62, cy + r * 0.95)],
                              ring(cx - r * 0.5, cy - r * 0.5, r * 0.36),
                              ring(cx + r * 0.5, cy + r * 0.5, r * 0.36)], width=5)

    if k == "doodle_plane":
        cx, cy, S = s["x"], s["y"], s["size"]
        def P(u, v):
            return (cx + u * S, cy + v * S)
        body = [P(-1.0, 0.05), P(-0.6, -0.12), P(0.7, -0.14), P(1.0, 0.0), P(0.7, 0.16), P(-0.7, 0.18), P(-1.0, 0.05)]
        fin = [P(-0.9, 0.0), P(-0.72, -0.55), P(-0.45, -0.55), P(-0.62, -0.12)]
        wing = [P(0.15, 0.0), P(-0.35, 0.62), P(-0.05, 0.64), P(0.42, 0.02)]
        windows = [[P(-0.4 + i * 0.22, -0.02), P(-0.32 + i * 0.22, -0.02)] for i in range(5)]
        return Path(s, seed, [body, fin, wing] + windows, width=4)

    if k == "doodle_barrel":
        cx, cy, S = s["x"], s["y"], s["size"]
        rx, ry = S * 0.42, S * 0.14
        top = [(cx + rx * math.cos(math.radians(a)), cy - S * 0.5 + ry * math.sin(math.radians(a)))
               for a in range(0, 366, 8)]
        sides = [[(cx - rx, cy - S * 0.5), (cx - rx * 1.05, cy), (cx - rx, cy + S * 0.5)],
                 [(cx + rx, cy - S * 0.5), (cx + rx * 1.05, cy), (cx + rx, cy + S * 0.5)]]
        bottom = [(cx + rx * math.cos(math.radians(a)), cy + S * 0.5 + ry * math.sin(math.radians(a)))
                  for a in range(0, 184, 8)]
        bands = [[(cx - rx * 1.04, cy - S * 0.2 + ry * 0.4 * math.sin(math.radians(a)))
                  for a in (0,)] + [(cx + rx * 1.04 * math.cos(math.radians(a)),
                                    cy - S * 0.2 + ry * math.sin(math.radians(a))) for a in range(180, -4, -8)],
                 [(cx + rx * 1.04 * math.cos(math.radians(a)), cy + S * 0.2 + ry * math.sin(math.radians(a)))
                  for a in range(180, -4, -8)]]
        return Path(s, seed, [top] + sides + [bottom] + bands, width=4)

    raise ValueError(k)


class Cells:
    def __init__(self, s, cells):
        self.s = s
        self.cells = cells
        n = len(cells)
        self.spans = [(i / n, (i + 1) / n) for i in range(n)]

    def draw(self, p, ink, hl):
        tip = None
        for c, (a, b) in zip(self.cells, self.spans):
            f = clamp((p - a) / (b - a))
            if f <= 0:
                break
            t = c.draw(f, ink, hl)
            if f < 1:
                tip = t
                break
        return tip


# ---------------------------------------------------------------- the reel

_built = None


def built():
    global _built
    if _built is None:
        _built = []
        for si, sc in enumerate(SCENES):
            _built.append([(s, build(s, si * 1000 + k * 17)) for k, s in enumerate(sc["strokes"])])
    return _built


def scene_at(T):
    acc = 0.0
    for i, sc in enumerate(SCENES):
        if T < acc + sc["dur"] or i == len(SCENES) - 1:
            return i, T - acc
        acc += sc["dur"]
    return len(SCENES) - 1, SCENES[-1]["dur"]


def render_scene_layers(i, t):
    ink = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    active = None
    for s, obj in built()[i]:
        p = clamp((t - s["at"]) / s["dur"])
        if p <= 0:
            continue
        tip = obj.draw(p, ink, hl)
        if 0 < p < 1 and tip is not None and s["tool"] != "sticker":
            active = (s["tool"], tip, p)
    return ink, hl, active


def multiply(base, hl, strength=0.82):
    b = np.asarray(base).astype(np.float32)
    h = np.asarray(hl).astype(np.float32)
    a = (h[..., 3:4] / 255.0) * strength
    out = b * (1 - a) + b * (h[..., :3] / 255.0) * a
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def compose(ink, hl, active, wipe=None):
    frame = paper().copy()
    if wipe is not None:
        kind, q = wipe
        if kind == "eraser":
            # everything above the sweeping edge is gone; the eraser zigzags along it
            edge = int((H + 120) * q) - 60
            m = np.zeros((H, W), np.float32)
            yy = np.arange(H)[:, None]
            m[:] = np.clip((yy - edge) / 40.0, 0, 1)
            for layer in (ink, hl):
                a = np.asarray(layer.getchannel("A")).astype(np.float32) * m
                layer.putalpha(Image.fromarray(a.astype(np.uint8), "L"))
    if hl.getbbox():
        frame = multiply(frame, hl)
    frame = frame.convert("RGBA")
    frame.alpha_composite(ink)
    if active is not None:
        tool, tip, p = active
        fade = min(1.0, p * 8, (1 - p) * 8 + 0.35)
        place_icon(frame, tool, tip, fade)
    if wipe is not None and wipe[0] == "eraser":
        q = wipe[1]
        edge = int((H + 120) * q) - 60
        x = W / 2 + (W / 2 - 140) * math.sin(q * math.pi * 5)
        place_icon(frame, "eraser", (x, edge - 10))
    return frame


def render_frame(n):
    T = n / FPS
    i, t = scene_at(T)
    sc = SCENES[i]
    ink, hl, active = render_scene_layers(i, t)
    wipe = None
    last = i == len(SCENES) - 1
    if not last and t > sc["dur"] - WIPE:
        q = clamp((t - (sc["dur"] - WIPE)) / WIPE)
        if sc.get("wipe") == "page":
            frame = compose(ink, hl, active)
            # the next page slides up over this one
            nxt = paper().copy().convert("RGBA")
            e = ease_out(q)
            y = int(H * (1 - e))
            shadow = Image.new("RGBA", (W, 60), (0, 0, 0, 0))
            sd = ImageDraw.Draw(shadow)
            for k in range(60):
                sd.line([(0, k), (W, k)], fill=(0, 0, 0, int(70 * (k / 60) ** 2)))
            frame.alpha_composite(shadow, (0, y - 60))
            frame.paste(nxt, (0, y))
            return frame.convert("RGB")
        wipe = ("eraser", q)
    return compose(ink, hl, active, wipe).convert("RGB")


def render_png(n):
    buf = io.BytesIO()
    render_frame(n).save(buf, "PNG", compress_level=1)
    return buf.getvalue()


# ------------------------------------------------------------------ checks


def assert_glyphs():
    """Every character must exist in the font of the tool that writes it."""
    from fontTools.ttLib import TTFont
    cov = {}
    for tool, path in sb.FONTS.items():
        cset = set()
        for tb in TTFont(os.path.join(HERE, path))["cmap"].tables:
            cset |= set(tb.cmap.keys())
        cov[tool] = cset
    bad = {}
    for sc in SCENES:
        for s in sc["strokes"]:
            tool = s["tool"]
            texts = []
            if s["kind"] == "text":
                texts.append((tool, s["text"]))
            for key in ("labels", "heads"):
                for v in s.get(key, []):
                    texts.append(("pen" if key == "labels" else "pencil", v))
            rows = s.get("rows", [])
            for row in (rows if isinstance(rows, list) else []):
                texts += [("pen", c) for c in row]
            for b in s.get("bars", []):
                texts.append(("pen", b[0] + "אלף0123456789 "))
            for tl, txt in texts:
                for ch in txt:
                    if ch not in "\n" and ord(ch) not in cov[tl]:
                        bad.setdefault(tl, set()).add(ch)
    if bad:
        raise SystemExit("missing glyphs: " + "; ".join(
            f"{t}: " + " ".join(f"{c!r}(U+{ord(c):04X})" for c in sorted(cs)) for t, cs in bad.items()))


if __name__ == "__main__":
    assert_glyphs()
    if len(sys.argv) > 1 and sys.argv[1] == "proof":
        os.makedirs(os.path.join(HERE, "proof"), exist_ok=True)
        for T in [float(v) for v in sys.argv[2:]]:
            render_frame(int(T * FPS)).save(os.path.join(HERE, "proof", f"t{T:05.1f}.png"))
            print("proof", T)
    else:
        print("glyphs ok")
