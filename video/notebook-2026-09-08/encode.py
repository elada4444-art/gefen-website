# -*- coding: utf-8 -*-
"""Render every frame to disk in parallel, make sure none is missing, then
encode the sequence with ffmpeg. Rendering and encoding are kept apart on
purpose: streaming PNGs into ffmpeg's stdin from a worker pool deadlocked at
an 8 MiB pipe boundary, and a run that stalls is worse than one that is a
little slower."""
import os, subprocess, sys, time
from multiprocessing import Pool
import imageio_ffmpeg
import render
from storyboard import FPS, TOTAL

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(HERE, "frames")
OUT = os.path.join(HERE, "out")
N = int(round(TOTAL * FPS))


def write_frame(n):
    path = os.path.join(FRAMES, "f_%04d.png" % n)
    if not os.path.exists(path):
        render.render_frame(n).save(path + ".tmp", "PNG", compress_level=1)
        os.replace(path + ".tmp", path)
    return n


if __name__ == "__main__":
    render.assert_glyphs()
    os.makedirs(FRAMES, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    with Pool(4, maxtasksperchild=200) as pool:
        for k, n in enumerate(pool.imap_unordered(write_frame, range(N), chunksize=4)):
            if k % 120 == 0:
                print(f"{k}/{N} frames  {time.time()-t0:4.0f}s", flush=True)
    missing = [n for n in range(N) if not os.path.exists(os.path.join(FRAMES, "f_%04d.png" % n))]
    if missing:
        print("re-rendering missing frames:", missing, flush=True)
        for n in missing:
            write_frame(n)
    print(f"all {N} frames on disk  {time.time()-t0:.0f}s", flush=True)

    dst = os.path.join(OUT, "gefen_notebook.mp4")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    r = subprocess.run([ff, "-y", "-loglevel", "error", "-framerate", str(FPS),
                        "-i", os.path.join(FRAMES, "f_%04d.png"),
                        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                        "-pix_fmt", "yuv420p", "-profile:v", "high",
                        "-movflags", "+faststart", dst])
    print("ffmpeg exit", r.returncode, dst, f"{time.time()-t0:.0f}s total", flush=True)
    sys.exit(r.returncode)
