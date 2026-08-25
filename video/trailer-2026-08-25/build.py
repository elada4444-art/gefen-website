# -*- coding: utf-8 -*-
"""Cut the trailer: normalise every segment of the EDL, burn its text on, and
concatenate. Expects clips/<key>.mp4 and the rendered art/ tree to exist."""
import os
import subprocess
import sys

from storyboard import EDL, FPS, BAR, GRAIN, TOTAL

HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(HERE, "clips")
ART = os.path.join(HERE, "art")
WORK = os.path.join(HERE, "work")
OUT = os.path.join(HERE, "out")
for d in (WORK, OUT):
    os.makedirs(d, exist_ok=True)

FADE = 0.35                       # text dissolve
MARK = os.path.join(ART, "logo_mark.png")


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        sys.stderr.write(p.stdout.decode("utf-8", "replace")[-4000:])
        raise SystemExit("ffmpeg failed on: %s" % " ".join(cmd[:8]))


def letterbox_and_mark(tag, idx):
    """Cinematic bars plus the standing Gefen bug, kept on every shot."""
    return (
        "[%s]drawbox=x=0:y=0:w=iw:h=%d:color=black@1:t=fill,"
        "drawbox=x=0:y=ih-%d:w=iw:h=%d:color=black@1:t=fill[bx];"
        "[%d:v]format=rgba,colorchannelmixer=aa=0.5[mk];"
        "[bx][mk]overlay=46:%d[vout]" % (tag, BAR, BAR, BAR, idx, BAR + 34)
    )


def build_shot(i, seg):
    dst = os.path.join(WORK, "seg_%02d.mp4" % i)
    src = os.path.join(CLIPS, seg["src"] + ".mp4")
    dur, start = seg["dur"], seg["start"]
    beats = seg.get("beats", [])

    cmd = ["ffmpeg", "-y", "-ss", str(start), "-t", str(dur + 0.4), "-i", src]
    for j, _ in enumerate(beats):
        cmd += ["-loop", "1", "-t", str(dur), "-i",
                os.path.join(ART, "ov_%02d_%d.png" % (i, j))]
    cmd += ["-loop", "1", "-t", str(dur), "-i", MARK]

    fc = ["[0:v]trim=0:%.3f,setpts=PTS-STARTPTS,"
          "scale=1080:1920:force_original_aspect_ratio=increase,"
          "crop=1080:1920,fps=%d,setsar=1,"
          "eq=contrast=1.09:saturation=0.90:gamma=0.97,"
          "vignette=PI/4.2,noise=alls=%d:allf=t+u,format=yuv420p[v0]"
          % (dur, FPS, GRAIN)]

    for j, b in enumerate(beats):
        t0, t1 = b["t0"], min(b["t1"], dur)
        fc.append("[%d:v]format=rgba,setpts=PTS-STARTPTS,"
                  "fade=in:st=%.3f:d=%.2f:alpha=1,"
                  "fade=out:st=%.3f:d=%.2f:alpha=1[o%d]"
                  % (j + 1, t0, FADE, max(t0, t1 - FADE), FADE, j))
        fc.append("[v%d][o%d]overlay=0:0:format=auto:"
                  "enable='between(t,%.3f,%.3f)'[v%d]"
                  % (j, j, max(0.0, t0 - 0.05), t1 + 0.05, j + 1))

    fc.append(letterbox_and_mark("v%d" % len(beats), len(beats) + 1))
    cmd += ["-filter_complex", ";".join(fc), "-map", "[vout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "16",
            "-pix_fmt", "yuv420p", "-an", "-t", str(dur), dst]
    run(cmd)
    return dst


def build_card(i, seg):
    dst = os.path.join(WORK, "seg_%02d.mp4" % i)
    dur = seg["dur"]
    cmd = ["ffmpeg", "-y",
           "-loop", "1", "-t", str(dur), "-i", os.path.join(ART, "card_%02d.png" % i),
           "-loop", "1", "-t", str(dur), "-i", MARK]
    fc = ["[0:v]fps=%d,setsar=1,noise=alls=4:allf=t+u,format=yuv420p[v0]" % FPS,
          letterbox_and_mark("v0", 1)]
    cmd += ["-filter_complex", ";".join(fc), "-map", "[vout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "16",
            "-pix_fmt", "yuv420p", "-an", "-t", str(dur), dst]
    run(cmd)
    return dst


def build_sequence(i, seg):
    """The logo stings, already rendered frame by frame."""
    dst = os.path.join(WORK, "seg_%02d.mp4" % i)
    run(["ffmpeg", "-y", "-framerate", str(FPS),
         "-i", os.path.join(ART, "seq_%02d" % i, "f_%04d.png"),
         "-vf", "setsar=1,format=yuv420p",
         "-c:v", "libx264", "-preset", "medium", "-crf", "16",
         "-pix_fmt", "yuv420p", "-an", dst])
    return dst


def main():
    segs = []
    for i, seg in enumerate(EDL):
        kind = seg["kind"]
        if kind == "shot":
            segs.append(build_shot(i, seg))
        elif kind == "card":
            segs.append(build_card(i, seg))
        else:
            segs.append(build_sequence(i, seg))
        print("built segment %02d  %-10s %.1fs" % (i, kind, seg["dur"]))

    listf = os.path.join(WORK, "list.txt")
    with open(listf, "w") as fh:
        for s in segs:
            fh.write("file '%s'\n" % s)

    final = os.path.join(OUT, "gefen_trailer.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listf,
         "-c:v", "libx264", "-preset", "slow", "-crf", "20",
         "-profile:v", "high", "-level", "4.1", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", "-r", str(FPS), "-an", final])
    print("wrote", final, "target", TOTAL, "s")


if __name__ == "__main__":
    main()
