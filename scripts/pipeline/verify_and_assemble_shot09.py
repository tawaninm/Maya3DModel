"""Verify Shot 09 Arnold CPU render frames (72 frames) and assemble the MP4.

Run after:  python scripts\\pipeline\\render_shots_batch.py 09
Shot 09 must be bright with both corridor walls visible (Tawan, 2026-10-01), so besides the checks of shots 05-08
(file exists, Arnold license_state valid, frame mean > 10/255) it measures the brightness of the left and right 22% strips of every
frame (the walls) and flags the shot if the frame mean, the wall strips, or the share of near-black pixels is out of range.
Exit code 1 if frames are missing, empty or watermarked (the MP4 is not built then).
To fix watermarked frames: delete just those frames from movies\\playblast\\Shot09_arnold and run render_shots_batch.py 09 again.
Next step for the camcorder look:  python scripts\\pipeline\\look_shot.py 09
"""
import os
import shutil
import subprocess
import sys

import PIL.ImageChops as ImageChops
from PIL import Image, ImageStat

ROOT = r"D:\projects\ProjectAnimation"
OUT_DIR = os.path.join(ROOT, "movies", "playblast", "Shot09_arnold")
FFMPEG = r"C:\Users\tawan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
SHOT = "09"
N_FRAMES = 72
MIN_FRAME_MEAN = 10.0     # unusable below this (same as shots 05-08)
MIN_SHOT_MEAN = 80.0      # this shot must read as the bright corridor (test frames were 117-148)
MIN_WALL_MEAN = 60.0      # left/right 22% strips, per frame
MAX_DARK_SHARE = 0.20     # share of pixels below 20/255, per frame
STRIP = 0.22


def lum(m):
    return 0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2]


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
    if missing or empty:
        print(f"ERROR: missing {missing}  zero-byte {empty}")
        return 1

    means, left, right, dark_share, diffs = [], [], [], [], []
    invalid, too_dark = [], []
    prev = None
    for f, p in paths:
        with Image.open(p) as raw:
            if raw.info.get("arnold/license_state") != "valid":
                invalid.append(f)
            rgb = raw.convert("RGB")
        w, h = rgb.size
        m = lum(ImageStat.Stat(rgb).mean)
        means.append(m)
        if m <= MIN_FRAME_MEAN:
            too_dark.append(f)
        left.append(lum(ImageStat.Stat(rgb.crop((0, 0, int(w * STRIP), h))).mean))
        right.append(lum(ImageStat.Stat(rgb.crop((int(w * (1 - STRIP)), 0, w, h))).mean))
        grey = rgb.convert("L")
        hist = grey.histogram()
        dark_share.append(sum(hist[:20]) / float(sum(hist)))
        if prev is not None:
            diffs.append(ImageStat.Stat(ImageChops.difference(grey, prev)).mean[0])
        prev = grey

    total = sum(means) / len(means)
    print("--- LICENSE ---")
    print(f"WATERMARKED: {len(invalid)} frames: {invalid}" if invalid else f"all {N_FRAMES} frames license_state = valid")
    print("--- LUMINANCE ---")
    print(f"Overall mean: {total:.2f}/255   min frame {min(means):.1f} (frame {means.index(min(means)) + 1})   max frame {max(means):.1f} (frame {means.index(max(means)) + 1})")
    print(f"Wall strips (left/right {STRIP * 100:.0f}%): left mean {sum(left) / len(left):.1f} (min {min(left):.1f})   right mean {sum(right) / len(right):.1f} (min {min(right):.1f})")
    print(f"Near-black pixels (<20): average {sum(dark_share) / len(dark_share) * 100:.1f}%   worst {max(dark_share) * 100:.1f}% (frame {dark_share.index(max(dark_share)) + 1})")
    print(f"Mean by third: frames 1-24 {sum(means[:24]) / 24:.1f}   25-48 {sum(means[24:48]) / 24:.1f}   49-72 {sum(means[48:]) / 24:.1f}")
    bad_wall = [i + 1 for i in range(N_FRAMES) if left[i] < MIN_WALL_MEAN or right[i] < MIN_WALL_MEAN]
    bad_dark = [i + 1 for i in range(N_FRAMES) if dark_share[i] > MAX_DARK_SHARE]
    verdict = []
    if too_dark:
        verdict.append(f"TOO DARK: frames {too_dark} at or below {MIN_FRAME_MEAN:.0f}/255")
    if total < MIN_SHOT_MEAN:
        verdict.append(f"DARK: shot mean {total:.1f} below {MIN_SHOT_MEAN:.0f}")
    if bad_wall:
        verdict.append(f"WALL STRIP below {MIN_WALL_MEAN:.0f}/255 in {len(bad_wall)} frames: {bad_wall[:12]}{'...' if len(bad_wall) > 12 else ''}")
    if bad_dark:
        verdict.append(f"MORE THAN {MAX_DARK_SHARE * 100:.0f}% near-black pixels in {len(bad_dark)} frames: {bad_dark[:12]}{'...' if len(bad_dark) > 12 else ''}")
    print("Brightness verdict:", "OK (bright, both walls visible)" if not verdict else "; ".join(verdict))
    print(f"Consecutive-frame diff: avg={sum(diffs) / len(diffs):.2f} min={min(diffs):.2f} max={max(diffs):.2f}")

    if invalid:
        print("STOP: watermarked frames present, MP4 not built. Delete those frames and run render_shots_batch.py 09 again.")
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
    print(f"RESULT: {N_FRAMES}/{N_FRAMES} frames valid, MP4 built. Camcorder look next: python scripts\\pipeline\\look_shot.py {SHOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
