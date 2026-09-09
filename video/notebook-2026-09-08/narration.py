# -*- coding: utf-8 -*-
"""Voice-over for the notebook cut, one line per scene.

Generated with ElevenLabs (multilingual) through the Higgsfield connector,
model text2speech_v2, voice preset "Callan" (d8061b90-ff25-5882-8384-7a6a28806f30).

The first narrated draft used the "Naomi" preset; it read Hebrew numbers
slowly (about 1.4 words a second) and the scenes were re-timed around it.
The client wanted a more energetic read, so presets were sampled on the
same line and scored by faster-whisper transcription accuracy (Hebrew),
pace and loudness dynamics; "Callum" won that round but was then judged to
sound too old ("like a professor"). All male presets in the catalogue were
ranked by median pitch and spectral brightness of their previews, the two
youngest-sounding energetic ones (Andre, Callan) were tried on one Hebrew
line, and Callan won: higher pitch (~147 Hz vs ~127 Hz), brighter timbre,
faster pace (~2.2 words a second) and the cleanest Hebrew transcription.
The copy is the energetic version written for Callum; every Callan clip
fits its scene with at least 0.95 s to spare, so storyboard.py did not need
another re-time.

`start` is where the clip is laid on the 60 s timeline (0.25 s after the
scene opens); `measured` is the clip length ffprobe reported. The mix is
adelay per line -> amix(normalize=0) -> loudnorm(I=-16, TP=-1.5) -> apad,
muxed over the silent render with the video stream copied.
"""

VOICE = dict(provider="elevenlabs", preset="Callan",
             voice_id="d8061b90-ff25-5882-8384-7a6a28806f30")

LINES = [
    dict(scene="title",  start=0.25,  scene_dur=5.0,  measured=4.05,
         text="השבוע במספרים! שמונה בספטמבר — בואו נצלול."),
    dict(scene="boi",    start=5.25,  scene_dur=7.05, measured=4.28,
         text="בנק ישראל הוריד את הריבית לשלוש ורבע — הפחתה שלישית ברציפות!"),
    dict(scene="cpi",    start=12.3,  scene_dur=6.55, measured=4.68,
         text="האינפלציה? אחוז וחצי בלבד. ומדד ספטמבר צפוי לרדת."),
    dict(scene="travel", start=18.85, scene_dur=7.3,  measured=5.64,
         text="ושיא של כל הזמנים: מיליון ומאתיים אלף ישראלים טסו לחו\"ל באוגוסט!"),
    dict(scene="jobs",   start=26.15, scene_dur=6.4,  measured=4.52,
         text="בארצות הברית — הפתעה! דוח התעסוקה פי שלושה מהתחזית."),
    dict(scene="week",   start=32.55, scene_dur=8.65, measured=6.19,
         text="השבוע הקובע: אירופה מעלה ריבית בחמישי, המדד האמריקאי בשישי, והפד מחליט ברביעי!"),
    dict(scene="europe", start=41.2,  scene_dur=8.3,  measured=5.07,
         text="בגוש האירו האינפלציה שלושה ושלוש, והנפט שוב מתקרב למאה דולר לחבית."),
    dict(scene="table",  start=49.5,  scene_dur=4.4,  measured=2.35,
         text="והראל? צופה פסק זמן באוקטובר."),
    dict(scene="cta",    start=53.9,  scene_dur=6.35, measured=4.52,
         text="מה זה אומר על הכסף שלכם? בואו נדבר! גפן ביטוח ופיננסים."),
]

for _l in LINES:
    assert _l["measured"] <= _l["scene_dur"] - 0.4, _l["scene"]
