# -*- coding: utf-8 -*-
"""Storyboard for the 60s "maths notebook" cut of the 8 Sep 2026 macro review.

Everything is drawn on squared paper by a small cast of writing tools. A scene
is a list of strokes; each stroke names its tool, when it starts (seconds into
the scene), how long the hand takes, and what it draws. Scenes end with an
eraser wipe unless `wipe="page"` turns the page instead. Coordinates are
pixels on a 1080x1920 page; text is right-anchored (RTL) unless `ltr=True`.

Tools: pen (blue ballpoint, the main hand) · red (red pen: circles, arrows,
underlines) · marker (thick black, titles) · pencil (grey, thin, notes and
sketches) · hilite (translucent yellow highlighter) · sticker (the logo).
"""

W, H, FPS = 1080, 1920, 24
TOTAL = 60.0

PAPER = (251, 249, 243)
GRID = (188, 210, 230)
MARGIN = (222, 96, 96)
INK_BLUE = (28, 52, 140)
INK_RED = (208, 38, 44)
INK_BLACK = (30, 32, 40)
PENCIL = (96, 98, 108)
HILITE = (255, 228, 54)

CELL = 45
RX = W - 3 * CELL            # the red margin rule; Hebrew notebooks keep it on the right
L = RX - 30                  # right edge for text (a little in from the rule)

FONTS = {
    "pen":    "fonts/Gveret_Levin_0.ttf",
    "red":    "fonts/Gveret_Levin_0.ttf",
    "marker": "fonts/Karantina_1.ttf",
    "pencil": "fonts/Amatic_SC_1.ttf",
}

SCENES = [
    dict(name="title", dur=5.0, wipe="page", strokes=[
        dict(tool="marker", at=0.26, dur=1.21, kind="text",
             text="השבוע במספרים", size=150, x=L, y=500),
        dict(tool="pen", at=1.56, dur=0.86, kind="text",
             text="סקירת מאקרו · 8 בספטמבר 2026", size=62, x=L, y=690),
        dict(tool="red", at=2.51, dur=0.43, kind="underline",
             x0=L, x1=L - 720, y=790, wavy=True),
        dict(tool="pencil", at=2.51, dur=0.86, kind="doodle_percent",
             x=330, y=1150, r=140),
    ]),

    dict(name="boi", dur=7.05, strokes=[
        dict(tool="marker", at=0.17, dur=0.69, kind="text",
             text="ריבית בנק ישראל", size=96, x=L, y=290),
        dict(tool="pencil", at=0.86, dur=0.6, kind="axes",
             x0=170, y0=1120, x1=930, y1=470),
        dict(tool="pen", at=1.46, dur=1.64, kind="stairs",
             x0=230, y0=600, step_w=220, step_h=160,
             labels=["3.75%", "3.50%", "3.25%"]),
        dict(tool="red", at=3.19, dur=0.52, kind="circle",
             x=780, y=845, rx=125, ry=70),
        dict(tool="pen", at=3.79, dur=0.95, kind="text",
             text="הפחתה שלישית ברציפות", size=66, x=L, y=1230),
        dict(tool="hilite", at=4.82, dur=0.52, kind="hilite",
             x0=L + 10, x1=L - 760, y=1268, h=76),
        dict(tool="pencil", at=5.34, dur=0.86, kind="text",
             text="(השוק תמחר את זה ב-50% בלבד)", size=54, x=L, y=1370),
    ]),

    dict(name="cpi", dur=6.55, strokes=[
        dict(tool="marker", at=0.18, dur=0.64, kind="text",
             text="אינפלציה", size=96, x=L, y=290),
        dict(tool="pen", at=0.82, dur=0.73, kind="text",
             text="1.5%", size=230, x=L, y=400, ltr=True),
        dict(tool="red", at=1.64, dur=0.46, kind="arrow",
             x0=330, y0=470, x1=330, y1=690),
        dict(tool="pen", at=2.19, dur=1.0, kind="text",
             text="תחזית מדד ספטמבר: 0.3%-", size=64, x=L, y=790),
        dict(tool="pencil", at=3.19, dur=0.91, kind="text",
             text="בגלל הפחתת הבלו על הדלק בחצי שקל", size=52, x=L, y=900),
        dict(tool="pen", at=4.11, dur=0.82, kind="text",
             text="12 חודשים קדימה: ~1.9%", size=64, x=L, y=1040),
        dict(tool="hilite", at=4.93, dur=0.46, kind="hilite",
             x0=L + 10, x1=L - 660, y=1076, h=76),
    ]),

    dict(name="travel", dur=7.3, strokes=[
        dict(tool="pencil", at=0.2, dur=1.2, kind="doodle_plane",
             x=190, y=500, size=170),
        dict(tool="pen", at=0.5, dur=1.0, kind="text",
             text="1.2 מיליון", size=150, x=L, y=360),
        dict(tool="pen", at=1.6, dur=1.1, kind="text",
             text="ישראלים טסו לחו״ל באוגוסט", size=64, x=L, y=590),
        dict(tool="red", at=2.8, dur=0.9, kind="text",
             text="שיא של כל הזמנים!", size=96, x=L, y=770),
        dict(tool="red", at=3.8, dur=0.5, kind="underline",
             x0=L, x1=L - 690, y=900, double=True),
    ]),

    dict(name="jobs", dur=6.4, strokes=[
        dict(tool="marker", at=0.15, dur=0.63, kind="text",
             text="ארה״ב: דוח תעסוקה", size=92, x=L, y=290),
        dict(tool="pencil", at=0.78, dur=0.47, kind="axes",
             x0=200, y0=980, x1=930, y1=440),
        dict(tool="pen", at=1.26, dur=1.1, kind="bars",
             base_y=980, bars=[("תחזית", 55, 320), ("בפועל", 162, 720)],
             scale=3.0, bar_w=170),
        dict(tool="pen", at=2.35, dur=0.63, kind="text",
             text="162 אלף משרות חדשות", size=68, x=L, y=1060),
        dict(tool="red", at=2.98, dur=0.63, kind="text",
             text="כמעט פי 3 מהתחזית", size=68, x=L, y=1160),
        dict(tool="pencil", at=3.69, dur=1.02, kind="text",
             text="אבל: שני שליש מהמשרות במסעדות,\nבמלונאות ובחינוך המקומי", size=50,
             x=L, y=1280),
        dict(tool="pen", at=4.71, dur=0.55, kind="text",
             text="אבטלה: 4.1%", size=62, x=L, y=1440),
        dict(tool="red", at=5.26, dur=0.39, kind="circle",
             x=L - 270, y=1478, rx=100, ry=58),
    ]),

    dict(name="week", dur=8.65, strokes=[
        dict(tool="marker", at=0.19, dur=0.74, kind="text",
             text="השבוע הקובע", size=96, x=L, y=290),
        dict(tool="pencil", at=0.93, dur=0.83, kind="calendar",
             x0=L + 10, y0=430, col_w=300, row_h=[110, 240],
             heads=["חמישי", "שישי", "רביעי הבא"]),
        dict(tool="pen", at=1.76, dur=0.83, kind="text",
             text="ה-ECB מעלה\nל-2.5%", size=46, cx=L + 10 - 150, y=560),
        dict(tool="pen", at=2.59, dur=0.83, kind="text",
             text="מדד המחירים\nבארה״ב", size=46, cx=L + 10 - 450, y=560),
        dict(tool="pen", at=3.42, dur=0.83, kind="text",
             text="החלטת\nהריבית בפד", size=46, cx=L + 10 - 750, y=560),
        dict(tool="red", at=4.26, dur=0.56, kind="circle",
             x=L + 10 - 450, y=660, rx=150, ry=118),
        dict(tool="red", at=4.81, dur=0.74, kind="text",
             text="האירוע המרכזי", size=62, cx=L + 10 - 450, y=800),
        dict(tool="pencil", at=5.55, dur=0.74, kind="text",
             text="נתון גבוה = הפד חוזר להעלאות, לראשונה מאז 2023",
             size=46, x=L, y=930),
    ]),

    dict(name="europe", dur=8.3, strokes=[
        dict(tool="marker", at=0.2, dur=0.7, kind="text",
             text="גוש האירו", size=96, x=L, y=290),
        dict(tool="pen", at=0.9, dur=1.1, kind="text",
             text="אינפלציה 3.3% · ליבה 2.4%", size=64, x=L, y=430),
        dict(tool="pencil", at=2.0, dur=1.0, kind="doodle_barrel",
             x=250, y=760, size=190),
        dict(tool="pen", at=2.3, dur=0.9, kind="text",
             text="נפט: כמעט 100$", size=110, x=L, y=660),
        dict(tool="red", at=3.3, dur=0.5, kind="arrow",
             x0=L - 560, y0=830, x1=L - 560, y1=640),
        dict(tool="pencil", at=3.9, dur=1.1, kind="text",
             text="חילופי האש במפרץ מחזיקים את המחיר גבוה", size=50,
             x=L, y=920),
    ]),

    dict(name="table", dur=4.4, wipe="page", strokes=[
        dict(tool="marker", at=0.12, dur=0.49, kind="text",
             text="השוק מול הראל", size=96, x=L, y=290),
        dict(tool="pencil", at=0.62, dur=0.62, kind="table",
             x0=L + 10, y0=430, cols=[400, 200, 200], rows=4, row_h=110),
        dict(tool="pen", at=1.23, dur=1.48, kind="table_rows",
             x0=L + 10, y0=430, cols=[400, 200, 200], row_h=110, size=46,
             rows=[["", "השוק", "הראל"],
                   ["ריבית בעוד 6 חודשים", "3.0-3.25%", "3.0%"],
                   ["דולר-שקל", "₪3.00", "₪2.95"],
                   ["מדד ספטמבר", "-0.2%", "-0.3%"]]),
        dict(tool="hilite", at=2.72, dur=0.43, kind="hilite",
             x0=L + 10 - 600, x1=L + 10 - 800, y=545, h=330, vertical=True),
        dict(tool="pencil", at=3.09, dur=0.56, kind="text",
             text="הראל: בנק ישראל לוקח פסק זמן באוקטובר", size=50,
             x=L, y=920),
    ]),

    dict(name="cta", dur=6.35, wipe=None, strokes=[
        dict(tool="marker", at=0.24, dur=1.06, kind="text",
             text="מה זה אומר\nעל הכסף שלכם?", size=104, x=L, y=380),
        dict(tool="sticker", at=1.38, dur=0.49, kind="logo", cx=W // 2, y=800, width=760),
        dict(tool="pen", at=1.95, dur=0.65, kind="text",
             text="בואו נדבר", size=96, x=L, y=1080),
        dict(tool="pen", at=2.68, dur=0.81, kind="text",
             text="03-5727277", size=90, x=L, y=1210, ltr=True),
        dict(tool="pen", at=3.57, dur=0.65, kind="text",
             text="או בוואטסאפ", size=60, x=L, y=1340),
        dict(tool="red", at=4.3, dur=0.49, kind="circle",
             x=L - 250, y=1262, rx=300, ry=82),
        dict(tool="pencil", at=4.79, dur=0.81, kind="text",
             text="מבוסס על סקירת המאקרו של הראל פיננסים · 8.9.26\nאין באמור ייעוץ, שיווק או המלצה להשקעה",
             size=36, x=L, y=1640),
    ]),
]

WIPE = 0.7          # seconds the eraser (or page turn) takes at the end of a scene

_total = sum(s["dur"] for s in SCENES)
assert abs(_total - TOTAL) < 1e-6, _total
