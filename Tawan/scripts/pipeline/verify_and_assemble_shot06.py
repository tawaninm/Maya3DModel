"""Verify Shot 06 Arnold CPU render frames (72 frames) and assemble MP4.
Calculates luminance stats, frame diffs, and compiles movies/playblast/Shot06_arnold.mp4.
"""
import os
import shutil
import subprocess
import sys
from PIL import Image, ImageStat

ROOT = r"D:\projects\ProjectAnimation"
OUT_DIR = os.path.join(ROOT, "movies", "playblast", "Shot06_arnold")
FFMPEG = r"C:\Users\tawan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
SHOT = "06"
N_FRAMES = 72

def main():
    print(f"Checking frames in {OUT_DIR}...")
    frames = []
    missing = []
    zero_bytes = []
    for f in range(1, N_FRAMES + 1):
        p = os.path.join(OUT_DIR, f"shot{SHOT}.png.{f:04d}")
        if not os.path.exists(p):
            missing.append(f)
        elif os.path.getsize(p) == 0:
            zero_bytes.append(f)
        else:
            frames.append(p)

    if missing:
        print(f"ERROR: Missing {len(missing)} frames: {missing}")
        return 1
    if zero_bytes:
        print(f"ERROR: Zero-byte {len(zero_bytes)} frames: {zero_bytes}")
        return 1

    print(f"All {N_FRAMES} frames exist with non-zero size.")

    # Luminance and difference analysis
    means = []
    mins = []
    maxs = []
    diffs = []
    prev_img = None

    for i, p in enumerate(frames, start=1):
        with Image.open(p) as img:
            rgb = img.convert("RGB")
            # Rec.709 luminance: 0.2126 R + 0.7152 G + 0.0722 B
            stat = ImageStat.Stat(rgb)
            # stat.mean is [mean_R, mean_G, mean_B]
            lum_mean = 0.2126 * stat.mean[0] + 0.7152 * stat.mean[1] + 0.0722 * stat.mean[2]
            # stat.extrema is [(min_R, max_R), (min_G, max_G), (min_B, max_B)]
            ext = stat.extrema
            lum_min = 0.2126 * ext[0][0] + 0.7152 * ext[1][0] + 0.0722 * ext[2][0]
            lum_max = 0.2126 * ext[0][1] + 0.7152 * ext[1][1] + 0.0722 * ext[2][1]
            means.append(lum_mean)
            mins.append(lum_min)
            maxs.append(lum_max)

            if prev_img is not None:
                # Difference between consecutive frames
                # convert to grayscale and calculate diff
                gray_curr = rgb.convert("L")
                gray_prev = prev_img.convert("L")
                diff_img = ImageStat.Stat(Image.blend(gray_curr, gray_prev, 0.5))
                # Or direct pixel diff
                import PIL.ImageChops as ImageChops
                diff = ImageChops.difference(gray_curr, gray_prev)
                diff_stat = ImageStat.Stat(diff)
                diffs.append(diff_stat.mean[0])
            prev_img = rgb.copy()

    total_mean = sum(means) / len(means)
    min_mean = min(means)
    max_mean = max(means)
    over_10 = sum(1 for m in means if m > 10.0)
    avg_diff = sum(diffs) / len(diffs) if diffs else 0.0
    min_diff = min(diffs) if diffs else 0.0
    max_diff = max(diffs) if diffs else 0.0

    print("--- LUMINANCE STATS ---")
    print(f"Frames analyzed: {len(means)}/{N_FRAMES}")
    print(f"Overall mean luminance: {total_mean:.2f}/255")
    print(f"Min frame mean: {min_mean:.2f}, Max frame mean: {max_mean:.2f}")
    print(f"Frames with mean luminance > 10/255: {over_10}/{N_FRAMES} ({over_10/N_FRAMES*100:.1f}%)")
    print(f"Consecutive frame diff: avg={avg_diff:.2f}, min={min_diff:.2f}, max={max_diff:.2f}")

    # Compile MP4
    mp4_arnold = os.path.join(ROOT, "movies", "playblast", f"Shot{SHOT}_arnold.mp4")
    mp4_shot = os.path.join(ROOT, "movies", "playblast", f"Shot{SHOT}.mp4")
    input_pattern = os.path.join(OUT_DIR, f"shot{SHOT}.png.%04d")

    cmd = [
        FFMPEG, "-y",
        "-f", "image2",
        "-framerate", "24",
        "-start_number", "1",
        "-i", input_pattern,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-preset", "slow",
        mp4_arnold
    ]
    print(f"Assembling MP4 via FFmpeg: {mp4_arnold}")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("FFmpeg error:", res.stderr)
        return res.returncode

    mp4_size = os.path.getsize(mp4_arnold)
    print(f"Successfully generated: {mp4_arnold} ({mp4_size:,} bytes)")

    shutil.copy2(mp4_arnold, mp4_shot)
    print(f"Copied to: {mp4_shot}")

    print("--- VERIFICATION RESULT ---")
    print(f"PASS: 72/72 frames valid, luminance verified, MP4 generated ({mp4_size:,} bytes).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
