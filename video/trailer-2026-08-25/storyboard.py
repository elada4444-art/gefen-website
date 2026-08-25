# -*- coding: utf-8 -*-
"""Storyboard for the 60s Hollywood-trailer cut of the 25 Aug 2026 macro review.

The cut is an explicit edit decision list: every entry names its source, where
to cut into it and how long it runs, plus the text beats laid over it. Times
inside a beat are relative to the segment it belongs to.
"""

W, H, FPS = 1080, 1920, 24
TOTAL = 60.0

# Brand palette (from the Gefen site)
NAVY_DEEP = (18, 29, 54)
ORANGE = (240, 125, 26)
ORANGE_LT = (255, 161, 78)
CREAM = (247, 244, 238)
WHITE = (255, 255, 255)
MUTED = (176, 190, 212)

BAR = 96              # letterbox bar, top and bottom
GRAIN = 7             # film grain strength

# Stock footage, downloaded by fetch_sources.sh into clips/<key>.mp4
SOURCES = {
    "peaks":    "Aerial view of mountain peaks with clouds at golden hour",
    "podium":   "Empty stage with a microphone before a performance",
    "facade":   "Illuminated neoclassical stone facade at night",
    "press":    "Banknotes running through a money press",
    "foundry":  "Molten metal casting, shower of sparks",
    "robots":   "Automated car assembly line, robotic arms",
    "metro":    "Drone among skyscrapers of a metropolis at night",
    "telaviv":  "Drone over the Yarkon river toward the Tel Aviv skyline",
}

# kind: logo_open | logo_close | card | shot
#   src / start = source clip and its in-point (shots only)
#   beats = (t0, t1, style, lines...) laid over the segment
EDL = [
    dict(kind="logo_open", dur=5.0,
         tagline="מציגה"),

    dict(kind="shot", src="peaks", start=1.0, dur=7.0, beats=[
        dict(t0=2.2, t1=6.7, style="whisper",
             lines=["השבוע, כל העיניים", "נשואות להר אחד"]),
    ]),

    dict(kind="card", dur=1.4, style="slam", lines=["ג׳קסון הול"]),

    dict(kind="shot", src="podium", start=0.0, dur=6.0, beats=[
        dict(t0=0.5, t1=5.7, style="line",
             lines=["ביום שישי נושא קווין וורש", "את נאומו הראשון כנגיד הפד"]),
    ]),

    dict(kind="shot", src="facade", start=1.0, dur=4.5, beats=[
        dict(t0=0.3, t1=4.2, style="line",
             lines=["האוצר האמריקאי קונה זמן"],
             foot="הרכישות החוזרות מוכפלות: מ-2 ל-4 מיליארד דולר"),
    ]),

    dict(kind="shot", src="press", start=1.5, dur=4.5, beats=[
        dict(t0=0.3, t1=4.2, style="stat",
             big="40 טריליון דולר", lines=["החוב האמריקאי חצה את הרף"]),
    ]),

    dict(kind="card", dur=1.2, style="beat", lines=["וזה לא נגמר שם"]),

    dict(kind="shot", src="foundry", start=1.0, dur=4.0, beats=[
        dict(t0=0.2, t1=3.7, style="line",
             lines=["מלחמת הסחר מתלקחת מחדש"],
             foot="מכסים הדדיים בין ארה״ב לקנדה"),
    ]),

    dict(kind="shot", src="robots", start=1.0, dur=4.0, beats=[
        dict(t0=0.2, t1=3.7, style="stat",
             big="52.1", lines=["גוש האירו — התעשייה בשיא של ארבע שנים"]),
    ]),

    dict(kind="shot", src="metro", start=1.0, dur=4.5, beats=[
        dict(t0=0.2, t1=4.2, style="pair",
             pairs=[("בריטניה", "2.9%"), ("יפן", "1.9%")],
             foot="והריביות בעולם מתחילות לזוז"),
    ]),

    dict(kind="card", dur=1.2, style="beat", lines=["ואצלנו?"]),

    dict(kind="shot", src="telaviv", start=0.5, dur=7.0, beats=[
        dict(t0=1.0, t1=6.7, style="slam_over",
             lines=["1 בספטמבר"], foot="החלטת הריבית של בנק ישראל"),
    ]),

    dict(kind="shot", src="telaviv", start=8.0, dur=4.5, beats=[
        dict(t0=0.2, t1=4.2, style="versus",
             first=("השוק מתמחר", "כ-50% להפחתה"),
             second=("הראל צופה", "ללא שינוי")),
    ]),

    dict(kind="logo_close", dur=5.2,
         brand="גפן סוכנויות לביטוח ופיננסים",
         credit="מבוסס על סקירת המאקרו השבועית של הראל פיננסים · 25 באוגוסט 2026",
         disclaimer="אין באמור ייעוץ, שיווק או המלצה להשקעה"),
]
