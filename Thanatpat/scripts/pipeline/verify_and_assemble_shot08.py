"""Verify Shot 08 Arnold CPU render frames (48 frames) and assemble the MP4.

Run after:  python scripts\\pipeline\\render_shots_batch.py 08
Checks, per frame: file exists and is not empty, Arnold license_state is "valid" (a watermarked frame is written when the license check
fails now and then; render_shots_batch.py cannot see that), mean luminance, and the share of near-black / clipped pixels.
Then prints the shot-level darkness verdict and builds movies/playblast/Shot08_arnold.mp4 + Shot08.mp4.
Exit code 1 if frames are missing, empty, or watermarked (the MP4 is not built in that case).
To fix watermarked frames: delete just those frames from movies\\playblast\\Shot08_arnold and run render_shots_batch.py 08 again.
"""
import os
import shutil
import subprocess
import sys

import PIL.ImageChops as ImageChops
from PIL import Image, ImageStat

ROOT = r"D:\projects\ProjectAnimation"
OUT_DIR = os.path.join(ROOT, "movies", "playblast", "Shot08_arnold")
FFMPEG = r"C:\Users\tawan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
SHOT = "08"
N_FRAMES = 48
DARK_MEAN = 10.0      # frame mean below this = unusable (same threshold as shots 05-07)
LOW_MEAN = 25.0       # shot mean below this = flag as dark (shot 07 was 19.18 and accepted, shot 06 was 24.77)
CLIP_SHARE = 0.20     # more than 20% of pixels above 240 = flag as blown out


def lum(rgb_stat):
    return 0.2126 * rgb_stat[0] + 0.7152 * rgb_stat[1] + 0.0722 * rgb_stat[2]


def main():
    print(f"Checking frames in {OUT_DIR}...")
    paths, missing, empty = [], [], []
    for f in range(1, N_FRAMES + 1):
        p = os.path.join(OUT_DIR, f"shot{SHOT}.png.{f:04d}")
        if not os.path.exists(p):
            missing.append(f)
        elif os.path.getsize(p) == 0:
            empty.append(f)
        else:
            paths.append((f, p))
    if missing:
        print(f"ERROR: missing {len(missing)} frames: {missing}")
    if empty:
        print(f"ERROR: zero-byte {len(empty)} frames: {empty}")
    if missing or empty:
        return 1

    means, diffs, invalid, dark_frames, clipped = [], [], [], [], []
    prev = None
    for f, p in paths:
        with Image.open(p) as raw:
            if raw.info.get("arnold/license_state") != "valid":
                invalid.append(f)
            rgb = raw.convert("RGB")
        m = lum(ImageStat.Stat(rgb).mean)
        means.append(m)
        if m <= DARK_MEAN:
            dark_frames.append(f)
        grey = rgb.convert("L")
        hist = grey.histogram()
        total = float(sum(hist))
        if sum(hist[241:]) / total > CLIP_SHARE:
            clipped.append(f)
        if prev is not None:
            diffs.append(ImageStat.Stat(ImageChops.difference(grey, prev)).mean[0])
        prev = grey

    total_mean = sum(means) / len(means)
    print("--- LICENSE ---")
    if invalid:
        print(f"WATERMARKED (license_state != valid): {len(invalid)} frames: {invalid}")
    else:
        print(f"all {N_FRAMES} frames license_state = valid")
    print("--- LUMINANCE ---")
    print(f"Overall mean: {total_mean:.2f}/255   min frame {min(means):.2f} (frame {means.index(min(means)) + 1})   max frame {max(means):.2f} (frame {means.index(max(means)) + 1})")
    print(f"Frames with mean > {DARK_MEAN:.0f}/255: {N_FRAMES - len(dark_frames)}/{N_FRAMES}")
    print(f"Mean by third: frames 1-16 {sum(means[:16]) / 16:.1f}   17-32 {sum(means[16:32]) / 16:.1f}   33-48 {sum(means[32:]) / 16:.1f}")
    verdict = []
    if dark_frames:
        verdict.append(f"TOO DARK: frames {dark_frames} are at or below {DARK_MEAN:.0f}/255")
    if total_mean < LOW_MEAN:
        verdict.append(f"DARK: shot mean {total_mean:.1f} is below {LOW_MEAN:.0f} (shots 06/07 were 24.8/19.2)")
    if clipped:
        verdict.append(f"BLOWN OUT: frames {clipped} have more than {CLIP_SHARE * 100:.0f}% of pixels above 240")
    print("Darkness verdict:", "OK (no frame too dark, no frame blown out)" if not verdict else "; ".join(verdict))
    print(f"Consecutive-frame diff: avg={sum(diffs) / len(diffs):.2f} min={min(diffs):.2f} max={max(diffs):.2f}")

    if invalid:
        print("STOP: watermarked frames present, MP4 not built. Delete those frames and run render_shots_batch.py 08 again.")
        return 1

    mp4_arnold = os.path.join(ROOT, "movies", "playblast", f"Shot{SHOT}_arnold.mp4")
    mp4_shot = os.path.join(ROOT, "movies", "playblast", f"Shot{SHOT}.mp4")
    cmd = [FFMPEG, "-y", "-f", "image2", "-framerate", "24", "-start_number", "1", "-i", os.path.join(OUT_DIR, f"shot{SHOT}.png.%04d"),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", mp4_arnold]
    print(f"Assembling MP4 via FFmpeg: {mp4_arnold}")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("FFmpeg error:", res.stderr)
        return res.returncode
    size = os.path.getsize(mp4_arnold)
    shutil.copy2(mp4_arnold, mp4_shot)
    print(f"Generated {mp4_arnold} ({size:,} bytes) and copied to {mp4_shot}")
    print(f"RESULT: {N_FRAMES}/{N_FRAMES} frames valid, MP4 built.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
