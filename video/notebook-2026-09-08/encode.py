# -*- coding: utf-8 -*-
"""Render every frame in parallel and stream them straight into ffmpeg."""
import os, subprocess, sys, time
from multiprocessing import Pool
import imageio_ffmpeg
import render
from storyboard import FPS, TOTAL

N = int(round(TOTAL * FPS))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
dst = os.path.join(OUT, "gefen_notebook.mp4")

if __name__ == "__main__":
    render.assert_glyphs()
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart", dst]
    t0 = time.time()
    with subprocess.Popen(cmd, stdin=subprocess.PIPE) as proc, Pool(4) as pool:
        for i, png in enumerate(pool.imap(render.render_png, range(N), chunksize=6)):
            proc.stdin.write(png)
            if i % 120 == 0:
                print(f"frame {i}/{N}  {time.time()-t0:5.0f}s", flush=True)
        proc.stdin.close()
        proc.wait()
    print("done", proc.returncode, dst, f"{time.time()-t0:.0f}s", flush=True)
