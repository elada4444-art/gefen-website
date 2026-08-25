# Shot sources

Every shot is real footage licensed through the account's Freepik Premium+
plan, not AI generation — the Magnific credit balance was down to 935 when
this was cut, and licensed stock suits a trailer better anyway.

| # | key | Freepik id | shot |
|---|-----|-----------|------|
| 1 | `peaks`   | 8236540 | Aerial view of mountain peaks with clouds at golden hour |
| 2 | `podium`  | 7568048 | Empty stage with a microphone before a performance |
| 3 | `facade`  | 8959310 | Illuminated neoclassical stone facade at night |
| 4 | `press`   | 4647459 | Banknotes running through a money press |
| 5 | `foundry` | 5949871 | Molten metal casting, shower of sparks |
| 6 | `robots`  | 7103005 | Automated car assembly line, robotic arms |
| 7 | `metro`   | 5843983 | Drone among the skyscrapers of a metropolis at night |
| 8 | `telaviv` | 6215319 | Drone over the Yarkon river toward the Tel Aviv skyline |

Download URLs are signed per account and expire within hours, so they are
passed to the build at run time rather than committed.

Source lengths constrain the cut: `podium` runs exactly 6.000s, so its
segment starts at 0.0 rather than part-way in. `build.py` will silently
produce a short segment if a segment asks for more than its source holds —
check `start + dur` against the clip length when re-timing.
