#!/usr/bin/env python3
"""Draw the animated GIF mascots for the phone book (vector-drawn, supersampled)."""
import math
from PIL import Image, ImageDraw
import numpy as np

S = 4            # supersample factor
SIZE = 160       # output px
NAVY = (18, 29, 54, 255)
NAVY2 = (28, 42, 74, 255)
ORANGE = (240, 125, 26, 255)
ORANGE2 = (255, 161, 78, 255)
CREAM = (247, 242, 230, 255)
LINE = (214, 200, 176, 255)
INK = (14, 18, 30, 255)
WHITE = (255, 255, 255, 255)
OUT = "assets/phonebook/"

def canvas():
    return Image.new("RGBA", (SIZE * S, SIZE * S), (0, 0, 0, 0))

def down(im):
    return im.resize((SIZE, SIZE), Image.LANCZOS)

def save(frames, name, ms):
    sheet = Image.new("RGB", (SIZE * len(frames), SIZE), (0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f.convert("RGB"), (i * SIZE, 0))
    master = sheet.quantize(255, method=Image.Quantize.MEDIANCUT)
    pal = [0, 0, 0] + master.getpalette()[: 255 * 3]
    out = []
    for f in frames:
        q = f.convert("RGB").quantize(palette=master, dither=Image.Dither.NONE)
        arr = np.array(q, dtype=np.uint8).astype(np.uint16) + 1
        alpha = np.array(f.getchannel("A"))
        arr[alpha < 128] = 0
        p = Image.fromarray(arr.astype(np.uint8), "P")
        p.putpalette(pal)
        out.append(p)
    out[0].save(OUT + name, save_all=True, append_images=out[1:], duration=ms,
                loop=0, disposal=2, transparency=0, optimize=False)
    print("wrote", name, len(frames), "frames")

def rot(im, deg, center):
    return im.rotate(deg, resample=Image.BICUBIC, center=center)

# ---------------------------------------------------------------- 1. ringing phone
def draw_phone_base(d, s):
    # rounded base with keypad
    d.rounded_rectangle([28*s, 82*s, 132*s, 142*s], radius=16*s, fill=INK)
    d.rounded_rectangle([31*s, 85*s, 129*s, 139*s], radius=14*s, fill=ORANGE)
    d.rounded_rectangle([31*s, 85*s, 129*s, 112*s], radius=14*s, fill=ORANGE2)
    d.rectangle([31*s, 100*s, 129*s, 112*s], fill=ORANGE)
    # keypad 3x3
    for r in range(3):
        for c in range(3):
            x = 58*s + c*16*s; y = 100*s + r*12*s
            d.rounded_rectangle([x, y, x+10*s, y+7*s], radius=2*s, fill=CREAM)
    # cradle posts
    d.rounded_rectangle([44*s, 66*s, 60*s, 90*s], radius=5*s, fill=INK)
    d.rounded_rectangle([100*s, 66*s, 116*s, 90*s], radius=5*s, fill=INK)
    d.rounded_rectangle([47*s, 69*s, 57*s, 88*s], radius=4*s, fill=NAVY2)
    d.rounded_rectangle([103*s, 69*s, 113*s, 88*s], radius=4*s, fill=NAVY2)

def handset(s):
    im = Image.new("RGBA", (SIZE*s, SIZE*s), (0,0,0,0))
    d = ImageDraw.Draw(im)
    # bar
    d.rounded_rectangle([40*s, 44*s, 120*s, 64*s], radius=10*s, fill=INK)
    d.rounded_rectangle([43*s, 47*s, 117*s, 61*s], radius=8*s, fill=NAVY)
    # ear/mouth pieces
    for cx in (48, 112):
        d.ellipse([(cx-18)*s, 36*s, (cx+18)*s, 72*s], fill=INK)
        d.ellipse([(cx-15)*s, 39*s, (cx+15)*s, 69*s], fill=NAVY)
        d.ellipse([(cx-8)*s, 46*s, (cx+8)*s, 62*s], fill=NAVY2)
    return im

def ring_gif():
    frames = []
    N = 18
    for i in range(N):
        t = i / N
        im = canvas(); d = ImageDraw.Draw(im); s = S
        draw_phone_base(d, s)
        # bounce + tilt handset
        ang = math.sin(t * 2 * math.pi * 2) * 9
        lift = abs(math.sin(t * 2 * math.pi * 2)) * 5 * s
        h = handset(s)
        h = rot(h, ang, (80*s, 54*s))
        im.alpha_composite(h, (0, -int(lift)))
        # sound arcs
        d = ImageDraw.Draw(im)
        for k in range(3):
            ph = (t * 3 - k * 0.33) % 1.0
            a = int(255 * (1 - ph))
            r = (14 + k*10 + ph*8) * s
            w = int(4*s)
            col = (240, 125, 26, a)
            d.arc([30*s - r, 50*s - r, 30*s + r, 50*s + r], 200, 300, fill=col, width=w)
            d.arc([130*s - r, 50*s - r, 130*s + r, 50*s + r], 240, 340, fill=col, width=w)
        frames.append(down(im))
    save(frames, "ring.gif", 55)

# ---------------------------------------------------------------- 2. rotary dial (loader)
def dial_gif():
    frames = []
    N = 24
    for i in range(N):
        t = i / N
        im = canvas(); d = ImageDraw.Draw(im); s = S
        cx = cy = 80*s
        # plate
        d.ellipse([cx-70*s, cy-70*s, cx+70*s, cy+70*s], fill=INK)
        d.ellipse([cx-66*s, cy-66*s, cx+66*s, cy+66*s], fill=CREAM)
        d.ellipse([cx-58*s, cy-58*s, cx+58*s, cy+58*s], fill=LINE)
        # rotating finger plate
        plate = Image.new("RGBA", im.size, (0,0,0,0)); pd = ImageDraw.Draw(plate)
        pd.ellipse([cx-56*s, cy-56*s, cx+56*s, cy+56*s], fill=NAVY)
        for k in range(10):
            a = math.radians(-90 + 20 + k*30)
            hx = cx + math.cos(a)*42*s; hy = cy + math.sin(a)*42*s
            pd.ellipse([hx-10*s, hy-10*s, hx+10*s, hy+10*s], fill=INK)
            pd.ellipse([hx-8*s, hy-8*s, hx+8*s, hy+8*s], fill=CREAM)
        ease = 0.5 - 0.5*math.cos(t * 2*math.pi)
        plate = rot(plate, -ease*300, (cx, cy))
        im.alpha_composite(plate)
        d = ImageDraw.Draw(im)
        # finger stop
        d.rounded_rectangle([cx+34*s, cy+30*s, cx+58*s, cy+42*s], radius=5*s, fill=INK)
        d.rounded_rectangle([cx+36*s, cy+32*s, cx+56*s, cy+40*s], radius=4*s, fill=ORANGE)
        # hub
        d.ellipse([cx-22*s, cy-22*s, cx+22*s, cy+22*s], fill=INK)
        d.ellipse([cx-19*s, cy-19*s, cx+19*s, cy+19*s], fill=ORANGE)
        d.ellipse([cx-8*s, cy-8*s, cx+8*s, cy+8*s], fill=CREAM)
        frames.append(down(im))
    save(frames, "dial.gif", 45)

# ---------------------------------------------------------------- 3. flipping book
def book_gif():
    frames = []
    N = 22
    for i in range(N):
        t = i / N
        im = canvas(); d = ImageDraw.Draw(im); s = S
        # cover
        d.rounded_rectangle([14*s, 40*s, 146*s, 128*s], radius=6*s, fill=INK)
        d.rounded_rectangle([17*s, 43*s, 143*s, 125*s], radius=5*s, fill=NAVY)
        # two pages
        for x0, x1 in ((22, 78), (82, 138)):
            d.rectangle([x0*s, 48*s, x1*s, 120*s], fill=CREAM)
            for k in range(6):
                y = (58 + k*10)*s
                d.line([(x0+6)*s, y, (x1-6)*s, y], fill=LINE, width=int(2*s))
                d.ellipse([(x1-10)*s, y-2*s, (x1-6)*s, y+2*s], fill=ORANGE)
        d.rectangle([78*s, 48*s, 82*s, 120*s], fill=INK)
        # flipping page (RTL: from the left page towards the right)
        ph = (t * 1.0) % 1.0
        ang = ph * math.pi  # 0..pi
        w = math.cos(ang) * 56  # +56 -> -56
        top = 48; bot = 120
        if abs(w) > 1:
            x_hinge = 80
            x_far = x_hinge + w
            shade = CREAM if w > 0 else (236, 228, 210, 255)
            lift = math.sin(ang) * 8
            poly = [(x_hinge*s, top*s), (x_far*s, (top-lift)*s), (x_far*s, (bot-lift)*s), (x_hinge*s, bot*s)]
            d.polygon(poly, fill=shade, outline=INK, width=int(2*s))
            for k in range(6):
                y = 58 + k*10
                xa = x_hinge + w*0.12; xb = x_hinge + w*0.88
                d.line([xa*s, (y - lift*0.12)*s, xb*s, (y - lift*0.88)*s], fill=LINE, width=int(2*s))
        # spine highlight
        d.rectangle([79*s, 44*s, 81*s, 124*s], fill=ORANGE)
        frames.append(down(im))
    save(frames, "book.gif", 60)

# ---------------------------------------------------------------- 4. dangling handset (no results)
def dangle_gif():
    frames = []
    N = 26
    for i in range(N):
        t = i / N
        im = canvas(); d = ImageDraw.Draw(im); s = S
        # wall mount / base at top
        d.rounded_rectangle([50*s, 8*s, 110*s, 36*s], radius=8*s, fill=INK)
        d.rounded_rectangle([53*s, 11*s, 107*s, 33*s], radius=7*s, fill=ORANGE)
        # curly cord: sine wave down to the handset
        swing = math.sin(t*2*math.pi) * 14
        px, py = 80*s, 36*s
        end = (80 + swing, 96)
        pts = []
        for k in range(41):
            u = k/40
            x = 80 + (end[0]-80)*u + math.sin(u*math.pi*8) * 6 * (1-u*0.4)
            y = 36 + (end[1]-36)*u
            pts.append((x*s, y*s))
        d.line(pts, fill=INK, width=int(4*s), joint="curve")
        # handset hanging vertically, swinging
        h = Image.new("RGBA", im.size, (0,0,0,0)); hd = ImageDraw.Draw(h)
        hd.rounded_rectangle([70*s, 92*s, 90*s, 150*s], radius=9*s, fill=INK)
        hd.rounded_rectangle([73*s, 95*s, 87*s, 147*s], radius=7*s, fill=NAVY)
        for cy in (98, 144):
            hd.ellipse([64*s, (cy-14)*s, 96*s, (cy+14)*s], fill=INK)
            hd.ellipse([67*s, (cy-11)*s, 93*s, (cy+11)*s], fill=NAVY)
            hd.ellipse([73*s, (cy-6)*s, 87*s, (cy+6)*s], fill=NAVY2)
        h = rot(h, -swing*1.4, (80*s, 92*s))
        im.alpha_composite(h, (int(swing*s), 0))
        frames.append(down(im))
    save(frames, "dangle.gif", 50)

ring_gif(); dial_gif(); book_gif(); dangle_gif()
