"""Verify the Arnold CPU render of any shot and build its MP4 (used for shots 10-14; shots 05-09 have their own verify_and_assemble_shotNN.py).

Usage:  python scripts\\pipeline\\verify_shot.py 10
Checks per frame: file exists and is not empty, Arnold license_state is "valid" (a watermarked frame appears now and then, render_shots_batch.py cannot
see it), mean luminance, share of near-black (<20) and clipped (>240) pixels.  Then prints a brightness verdict and builds
movies/playblast/ShotNN_arnold.mp4 and ShotNN.mp4.  Exit code 1 if frames are missing, empty or watermarked (no MP4 in that case).
To fix watermarked frames: delete just those frames from movies\\playblast\\ShotNN_arnold and run render_shots_batch.py NN again.
Flicker (Preset B, shots 10-14) makes some frames dip on purpose, so a frame below the dark threshold is reported but only the shot mean decides the verdict.
"""
import os
import shutil
import subprocess
import sys

import PIL.ImageChops as ImageChops
from PIL import Image, ImageStat

ROOT = r"D:\projects\ProjectAnimation"
FFMPEG = r"C:\Users\tawan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
FRAMES = {"05": 48, "06": 72, "07": 72, "08": 48, "09": 72, "10": 48, "11": 72, "12": 48, "13": 48, "14": 48}
DARK_FRAME = 10.0
MIN_SHOT_MEAN = 60.0
CLIP_SHARE = 0.20
DARK_SHARE = 0.35


def lum(m):
    return 0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    shot = "%02d" % int(sys.argv[1])
    n = FRAMES[shot]
    out_dir = os.path.join(ROOT, "movies", "playblast", "Shot%s_arnold" % shot)
    print("Checking %d frames in %s ..." % (n, out_dir))
    paths, missing, empty = [], [], []
    for f in range(1, n + 1):
        p = os.path.join(out_dir, "shot%s.png.%04d" % (shot, f))
        if not os.path.exists(p):
            missing.append(f)
        elif os.path.getsize(p) == 0:
            empty.append(f)
        else:
            paths.append((f, p))
    if missing or empty:
        print("ERROR: missing %s  zero-byte %s" % (missing, empty))
        return 1
    means, invalid, dark_frames, clipped, murky, diffs = [], [], [], [], [], []
    prev = None
    for f, p in paths:
        with Image.open(p) as raw:
            if raw.info.get("arnold/license_state") != "valid":
                invalid.append(f)
            rgb = raw.convert("RGB")
        m = lum(ImageStat.Stat(rgb).mean)
        means.append(m)
        if m <= DARK_FRAME:
            dark_frames.append(f)
        grey = rgb.convert("L")
        hist = grey.histogram()
        tot = float(sum(hist))
        if sum(hist[241:]) / tot > CLIP_SHARE:
            clipped.append(f)
        if sum(hist[:20]) / tot > DARK_SHARE:
            murky.append(f)
        if prev is not None:
            diffs.append(ImageStat.Stat(ImageChops.difference(grey, prev)).mean[0])
        prev = grey
    total = sum(means) / len(means)
    print("--- LICENSE ---")
    print("WATERMARKED: %d frames: %s" % (len(invalid), invalid) if invalid else "all %d frames license_state = valid" % n)
    print("--- LUMINANCE ---")
    print("Overall mean: %.2f/255   min frame %.1f (frame %d)   max frame %.1f (frame %d)" % (total, min(means), means.index(min(means)) + 1, max(means), means.index(max(means)) + 1))
    third = max(1, n // 3)
    print("Mean by third: %.1f / %.1f / %.1f" % (sum(means[:third]) / third, sum(means[third:2 * third]) / third, sum(means[2 * third:]) / max(1, n - 2 * third)))
    verdict = []
    if total < MIN_SHOT_MEAN:
        verdict.append("DARK: shot mean %.1f below %.0f" % (total, MIN_SHOT_MEAN))
    if dark_frames:
        verdict.append("frames at or below %.0f/255 (flicker dips?): %s" % (DARK_FRAME, dark_frames))
    if clipped:
        verdict.append("BLOWN OUT: more than %d%% of pixels above 240 in frames %s" % (CLIP_SHARE * 100, clipped))
    if murky:
        verdict.append("more than %d%% near-black pixels in %d frames: %s%s" % (DARK_SHARE * 100, len(murky), murky[:10], "..." if len(murky) > 10 else ""))
    print("Verdict:", "OK" if not verdict else "; ".join(verdict))
    print("Consecutive-frame diff: avg=%.2f min=%.2f max=%.2f (largest at frame %d)" % (sum(diffs) / len(diffs), min(diffs), max(diffs), diffs.index(max(diffs)) + 2))
    if invalid:
        print("STOP: watermarked frames present, MP4 not built. Delete those frames and run render_shots_batch.py %s again." % shot)
        return 1
    mp4a = os.path.join(ROOT, "movies", "playblast", "Shot%s_arnold.mp4" % shot)
    mp4 = os.path.join(ROOT, "movies", "playblast", "Shot%s.mp4" % shot)
    cmd = [FFMPEG, "-y", "-f", "image2", "-framerate", "24", "-start_number", "1", "-i", os.path.join(out_dir, "shot%s.png.%%04d" % shot),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", mp4a]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("FFmpeg error:", res.stderr)
        return res.returncode
    shutil.copy2(mp4a, mp4)
    print("Generated %s (%s bytes) and copied to %s" % (mp4a, "{:,}".format(os.path.getsize(mp4a)), mp4))
    print("RESULT: %d/%d frames valid, MP4 built." % (n, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
