# -*- coding: utf-8 -*-
"""Storyboard for the 60s macro-review drone reel (1080x1920, 30fps)."""

W, H, FPS = 1080, 1920, 30

# Brand palette (taken from the Gefen site)
NAVY_DEEP = (18, 29, 54)
NAVY = (28, 42, 74)
ORANGE = (240, 125, 26)
ORANGE_LT = (255, 161, 78)
CREAM = (247, 244, 238)
WHITE = (255, 255, 255)
GREEN = (47, 227, 117)
RED = (255, 99, 99)
MUTED = (168, 186, 214)

# Eight generated drone shots, in order, with their durations.
CLIPS = [
    {"key": "01_space_usa",    "dur": 10},
    {"key": "02_manhattan",    "dur": 10},
    {"key": "03_treasury",     "dur": 5},
    {"key": "04_datacenter",   "dur": 5},
    {"key": "05_oil",          "dur": 5},
    {"key": "06_tetons",       "dur": 5},
    {"key": "07_telaviv",      "dur": 10},
    {"key": "08_jerusalem",    "dur": 10},
]

# Text beats. `clip` = index into CLIPS, times are relative to that clip.
# kind: title | header | card | driver | closing
BEATS = [
    dict(clip=0, t0=0.4, t1=4.3, kind="title",
         kicker="סקירת מאקרו ופיננסים",
         title="השבוע\nבשווקים",
         sub="סיכום שבועי  •  23 באוגוסט 2026"),

    dict(clip=0, t0=4.7, t1=9.7, kind="header", flag="us",
         country="ארצות הברית",
         headline="תשואות האג״ח הארוכות\nגונבות את ההצגה"),

    dict(clip=1, t0=0.4, t1=5.0, kind="card", flag="us",
         eyebrow="וול סטריט  •  סיכום שבועי",
         rows=[("S&P 500", "-1.4%", "neg"),
               ("נאסד״ק 100", "-2.5%", "neg"),
               ("דאו ג׳ונס", "-0.8%", "neg")]),

    dict(clip=1, t0=5.4, t1=9.7, kind="card", flag="us",
         eyebrow="שוק האג״ח האמריקאי",
         rows=[("תשואת אג״ח ל-10 שנים", "4.73%", "up"),
               ("שינוי שבועי (נ״ב)", "+4", "up")],
         foot="השוק מתמחר כמעט שתי העלאות ריבית בשנה הקרובה"),

    dict(clip=2, t0=0.4, t1=4.7, kind="driver", flag="us", num="1",
         title="דומיננטיות פיסקאלית",
         body="החוב הלאומי חצה 40 טריליון דולר.\nכשההיצע גדול מהביקוש — התשואות עולות."),

    dict(clip=3, t0=0.3, t1=4.7, kind="driver", flag="us", num="2",
         title="הנפקות אג״ח למימון AI",
         body="ענקיות הענן מנפיקות בקצב חריג\nומתחרות על אותו בסיס משקיעים."),

    dict(clip=4, t0=0.3, t1=4.7, kind="driver", flag="us", num="3",
         title="אי ודאות גיאופוליטית",
         body="מחירי הנפט חזרו לעלות\nוהחשש מאינפלציה מחודשת שב לשולחן.",
         foot="4. אינפלציה דביקה ושחיקה באמינות הפד"),

    dict(clip=5, t0=0.3, t1=4.7, kind="card", flag="us",
         eyebrow="מדדי מנהלי הרכש  •  אוגוסט",
         rows=[("שירותים", "56.8", "pos"),
               ("תעשייה", "53.2", "neg"),
               ("משולב", "56.0", "pos")],
         foot="הרמה הגבוהה ביותר מאז אפריל 2022 — צמיחה מתקרבת ל-3%"),

    dict(clip=6, t0=0.4, t1=5.0, kind="header", flag="il",
         country="ישראל",
         headline="מגמה מעורבת\nבבורסה המקומית"),

    dict(clip=6, t0=5.4, t1=9.7, kind="card", flag="il",
         eyebrow="מדדי המניות  •  סיכום שבועי",
         rows=[("ת״א 35", "-0.7%", "neg"),
               ("ת״א 90", "+0.8%", "pos"),
               ("ת״א 125", "-0.4%", "neg")]),

    dict(clip=7, t0=0.4, t1=5.0, kind="card", flag="il",
         eyebrow="שוק האג״ח המקומי",
         rows=[("תשואת אג״ח ל-10 שנים", "3.84%", "up"),
               ("הסתברות להפחתת ריבית", "~50%", "neutral")],
         foot="החלטת בנק ישראל הקרובה — 1 בספטמבר"),

    dict(clip=7, t0=5.4, t1=9.8, kind="closing",
         eyebrow="מבט לשבוע הקרוב",
         lines=["נאום יו״ר הפד בג׳קסון הול",
                "דוח הרווחים של אנבידיה"],
         brand="גפן סוכנויות לביטוח ופיננסים"),
]
