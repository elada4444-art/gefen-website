# -*- coding: utf-8 -*-
"""Voice-over for the notebook cut, one line per scene.

Generated with ElevenLabs (multilingual) through the Higgsfield connector,
voice preset "Naomi". The first draft ran ~35% longer than the scenes — this
voice reads Hebrew numbers slowly (about 1.4 words a second once you spell
out "מאה שישים ושתיים") — so the copy was cut to headline length and the
scene durations in storyboard.py were re-timed around the measured clips.
`start` is where the clip is laid on the 60s timeline (0.3s after the scene
opens); `measured` is the clip length ffprobe reported.
"""

LINES = [
    dict(scene="title",  start=0.25,  scene_dur=5.0, measured=4.56,
         text="השבוע במספרים. שמונה בספטמבר."),
    dict(scene="boi",    start=5.25,  scene_dur=7.05, measured=6.64,
         text="בנק ישראל הוריד את הריבית לשלוש ורבע. הפחתה שלישית ברציפות."),
    dict(scene="cpi",    start=12.3, scene_dur=6.55, measured=6.14,
         text="האינפלציה ירדה לאחוז וחצי, ומדד ספטמבר צפוי לרדת."),
    dict(scene="travel", start=18.85, scene_dur=7.3, measured=6.87,
         text="ובאוגוסט, מיליון ומאתיים אלף ישראלים טסו לחו\"ל. שיא של כל הזמנים."),
    dict(scene="jobs",   start=26.15, scene_dur=6.4, measured=6.0,
         text="דוח התעסוקה האמריקאי הפתיע: פי שלושה מהתחזית."),
    dict(scene="week",   start=32.55, scene_dur=8.65, measured=8.24,
         text="השבוע: אירופה בחמישי, המדד האמריקאי בשישי, והפד ברביעי."),
    dict(scene="europe", start=41.2, scene_dur=8.3, measured=7.89,
         text="בגוש האירו האינפלציה בשלושה נקודה שלושה אחוזים, והנפט שוב מתקרב למאה דולר."),
    dict(scene="table",  start=49.5, scene_dur=4.4, measured=4.0,
         text="הראל: בנק ישראל ייקח פסק זמן באוקטובר."),
    dict(scene="cta",    start=53.9, scene_dur=6.35, measured=5.84,
         text="מה זה אומר על הכסף שלכם? בואו נדבר. גפן ביטוח ופיננסים."),
]
