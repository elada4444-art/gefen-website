# -*- coding: utf-8 -*-
"""Burn the Hebrew data overlays onto the eight drone shots and assemble the
60-second reel. Expects clips/<key>.mp4 and overlays/beat_NN.png to exist."""
import os
import subprocess
import sys

from storyboard import CLIPS, BEATS

HERE = os.path.dirname(os.path.abspath(__file__))
CLIPDIR = os.path.join(HERE, "clips")
OVL = os.path.join(HERE, "overlays")
WORK = os.path.join(HERE, "work")
OUT = os.path.join(HERE, "out")
os.makedirs(WORK, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

FPS = 24
FADE = 0.45                       # cross-dissolve on every text card
BAR_H = 10
TOTAL = sum(c["dur"] for c in CLIPS)


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        sys.stderr.write(p.stdout.decode("utf-8", "replace")[-4000:])
        raise SystemExit("ffmpeg failed: %s" % " ".join(cmd[:6]))


def build_segment(i, clip):
    """One drone shot, normalised, with its text cards dissolved in and out."""
    beats = [(n, b) for n, b in enumerate(BEATS) if b["clip"] == i]
    dur = clip["dur"]
    src = os.path.join(CLIPDIR, clip["key"] + ".mp4")
    dst = os.path.join(WORK, "seg_%02d.mp4" % i)

    cmd = ["ffmpeg", "-y", "-i", src]
    for n, _ in beats:
        cmd += ["-loop", "1", "-t", str(dur),
                "-i", os.path.join(OVL, "beat_%02d.png" % n)]

    fc = ["[0:v]trim=0:%.3f,setpts=PTS-STARTPTS,"
          "scale=1080:1920:force_original_aspect_ratio=increase,"
          "crop=1080:1920,fps=%d,setsar=1,format=yuv420p[v0]" % (dur, FPS)]

    for k, (n, b) in enumerate(beats):
        t0, t1 = b["t0"], min(b["t1"], dur)
        fc.append("[%d:v]format=rgba,setpts=PTS-STARTPTS,"
                  "fade=in:st=%.3f:d=%.2f:alpha=1,"
                  "fade=out:st=%.3f:d=%.2f:alpha=1[o%d]"
                  % (k + 1, t0, FADE, max(t0, t1 - FADE), FADE, k))
        fc.append("[v%d][o%d]overlay=0:0:format=auto:"
                  "enable='between(t,%.3f,%.3f)'[v%d]"
                  % (k, k, max(0.0, t0 - 0.05), t1 + 0.05, k + 1))

    cmd += ["-filter_complex", ";".join(fc),
            "-map", "[v%d]" % len(beats),
            "-c:v", "libx264", "-preset", "medium", "-crf", "16",
            "-pix_fmt", "yuv420p", "-an", dst]
    run(cmd)
    return dst


def main():
    segs = [build_segment(i, c) for i, c in enumerate(CLIPS)]
    print("segments built:", len(segs))

    listf = os.path.join(WORK, "list.txt")
    with open(listf, "w") as fh:
        for s in segs:
            fh.write("file '%s'\n" % s)

    # thin progress rail that drains right-to-left, matching the RTL reading
    bar = ("drawbox=x=0:y=ih-%d:w=iw:h=%d:color=0x0C1426@0.55:t=fill,"
           "drawbox=x='iw-iw*t/%d':y=ih-%d:w='iw*t/%d':h=%d:"
           "color=0xF07D1A@0.95:t=fill" % (BAR_H, BAR_H, TOTAL, BAR_H, TOTAL, BAR_H))

    final = os.path.join(OUT, "gefen_macro_reel.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listf,
         "-vf", bar,
         "-c:v", "libx264", "-preset", "slow", "-crf", "20",
         "-profile:v", "high", "-level", "4.1", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", "-r", str(FPS), "-an", final])
    print("wrote", final)


if __name__ == "__main__":
    main()
