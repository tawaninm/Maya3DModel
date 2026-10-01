"""Resumable Arnold CPU batch render for the Backrooms shots (run from a normal terminal, not from an agent session).

Usage (PowerShell, from D:\\projects\\ProjectAnimation):
    python scripts\\pipeline\\render_shots_batch.py 05            # one shot
    python scripts\\pipeline\\render_shots_batch.py 06 07 08      # several shots, in order
    python scripts\\pipeline\\render_shots_batch.py 05 --frames 12-12 --res 160x90 --out C:\\Temp\\t   # quick test

Why it exists: agent sessions kill background renders when a turn ends, and a foreground call is capped at 10 minutes.
This script renders in chunks of CHUNK frames, skips frames that already exist with size > 0 and re-renders 0-byte leftovers,
so you can stop it (Ctrl+C) or lose power and run it again; it continues where it stopped.
Output: movies/playblast/ShotNN_arnold/shotNN.png.####  (Arnold CPU 640x360 by default, about 85 s per frame on the RTX 3050 laptop).
Never use Hardware 2.0 for this scene: it renders black.
"""
import argparse
import os
import subprocess
import sys
import time

ROOT = r"D:\projects\ProjectAnimation"
RENDER = r"D:\AutoDesk\Maya2027\bin\Render.exe"
FRAMES = {"05": 24, "06": 72, "07": 72, "08": 48, "09": 72, "10": 48, "11": 72, "12": 48, "13": 48, "14": 24}  # plan.md shot table
CHUNK = 6


def done(out_dir, shot, f):
    p = os.path.join(out_dir, "shot%s.png.%04d" % (shot, f))
    return os.path.exists(p) and os.path.getsize(p) > 0


def render_shot(shot, first, last, res, out_dir):
    scene = os.path.join(ROOT, "scenes", "Shots", "Shot%s.mb" % shot)
    if not os.path.exists(scene):
        print("SKIP shot %s: %s missing" % (shot, scene))
        return False
    os.makedirs(out_dir, exist_ok=True)
    todo = [f for f in range(first, last + 1) if not done(out_dir, shot, f)]
    print("shot %s: %d frames to render, %d already done" % (shot, len(todo), (last - first + 1) - len(todo)))
    ok = True
    for i in range(0, len(todo), CHUNK):
        chunk = todo[i:i + CHUNK]
        # chunk may be non-contiguous after a partial run; render contiguous runs separately
        runs, start = [], chunk[0]
        for a, b in zip(chunk, chunk[1:] + [None]):
            if b is None or b != a + 1:
                runs.append((start, a))
                start = b
        for s, e in runs:
            t0 = time.time()
            cmd = [RENDER, "-r", "arnold", "-cam", "CAM_Shot%s" % shot, "-s", str(s), "-e", str(e), "-x", str(res[0]), "-y", str(res[1]),
                   "-rd", out_dir, "-im", "shot%s" % shot, "-of", "png", "-pad", "4", scene]
            with open(os.path.join(out_dir, "render_log.txt"), "a", encoding="utf-8", errors="replace") as log:
                rc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT).returncode
            bad = [f for f in range(s, e + 1) if not done(out_dir, shot, f)]
            print("  frames %d-%d rc=%d %.0fs %s" % (s, e, rc, time.time() - t0, "OK" if not bad else "MISSING " + str(bad)))
            ok = ok and rc == 0 and not bad
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots", nargs="+", help="shot numbers such as 05 06")
    ap.add_argument("--frames", help="range like 12-12 (only valid with one shot)")
    ap.add_argument("--res", default="640x360")
    ap.add_argument("--out", help="output folder (default movies/playblast/ShotNN_arnold)")
    a = ap.parse_args()
    res = tuple(int(v) for v in a.res.lower().split("x"))
    allok = True
    for shot in a.shots:
        shot = "%02d" % int(shot)
        if shot not in FRAMES:
            print("unknown shot", shot)
            allok = False
            continue
        first, last = 1, FRAMES[shot]
        if a.frames:
            first, last = (int(v) for v in a.frames.split("-"))
        out = a.out or os.path.join(ROOT, "movies", "playblast", "Shot%s_arnold" % shot)
        allok = render_shot(shot, first, last, res, out) and allok
    print("ALL OK" if allok else "SOME FRAMES FAILED, run the same command again to retry only the missing ones")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
