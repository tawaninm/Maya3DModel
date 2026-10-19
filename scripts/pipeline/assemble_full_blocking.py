"""Assemble Shot05 to Shot14 into Backrooms_Blocking_Full.mp4.

Usage:
    python scripts/pipeline/assemble_full_blocking.py
"""
import os
import sys
import subprocess
import shutil
import json

ROOT = r"D:\projects\ProjectAnimation"
BLAST_DIR = os.path.join(ROOT, "movies", "playblast")
FFMPEG = r"C:\Users\tawan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
FFPROBE = r"C:\Users\tawan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffprobe.exe"

if not os.path.exists(FFMPEG):
    FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
if not os.path.exists(FFPROBE):
    FFPROBE = shutil.which("ffprobe") or "ffprobe"

EXPECTED_FRAMES = {
    "Shot05": 48,
    "Shot06": 72,
    "Shot07": 72,
    "Shot08": 48,
    "Shot09": 72,
    "Shot10": 48,
    "Shot11": 72,
    "Shot12": 48,
    "Shot13": 48,
    "Shot14": 48,
}

def probe_video(path):
    cmd = [
        FFPROBE, "-v", "error", "-select_streams", "v:0", "-count_packets",
        "-show_entries", "stream=nb_read_packets,r_frame_rate,width,height,duration",
        "-of", "json", path
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    data = json.loads(r.stdout)
    return data["streams"][0]

def main():
    shots = [f"Shot{i:02d}" for i in range(5, 15)]
    missing = []
    shot_paths = []
    total_expected_frames = sum(EXPECTED_FRAMES.values())
    total_actual_frames = 0

    print("Checking 10 shots in movies/playblast ...")
    for s in shots:
        mp4_name = f"{s}.mp4"
        p = os.path.join(BLAST_DIR, mp4_name)
        if not os.path.exists(p):
            missing.append(mp4_name)
            continue
        info = probe_video(p)
        if not info:
            print(f"  {s}: Failed to probe")
            missing.append(mp4_name)
            continue
        frames = int(info.get("nb_read_packets", 0))
        total_actual_frames += frames
        dur = float(info.get("duration", 0.0))
        exp = EXPECTED_FRAMES[s]
        status = "OK" if frames == exp else f"MISMATCH (expected {exp})"
        print(f"  {s}: {frames} frames ({dur:.2f}s) - {status}")
        shot_paths.append(p)

    if missing:
        print(f"ERROR: Missing shots: {missing}")
        return 1

    concat_txt = os.path.join(BLAST_DIR, "_concat_blocking.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in shot_paths:
            escaped_path = p.replace("\\", "/")
            f.write(f"file '{escaped_path}'\n")

    out_mp4 = os.path.join(BLAST_DIR, "Backrooms_Blocking_Full.mp4")
    cmd = [
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt, "-c", "copy", out_mp4
    ]
    print("\nConcatenating shots into Backrooms_Blocking_Full.mp4 ...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg concat error:", res.stderr)
        return res.returncode

    if os.path.exists(out_mp4):
        sz = os.path.getsize(out_mp4)
        full_info = probe_video(out_mp4)
        full_frames = int(full_info.get("nb_read_packets", 0))
        full_dur = float(full_info.get("duration", 0.0))
        print(f"\nSUCCESS: Generated {out_mp4}")
        print(f"  File size: {sz:,} bytes")
        print(f"  Total frames: {full_frames} (expected {total_expected_frames})")
        print(f"  Total duration: {full_dur:.2f}s ({full_dur*24:.0f} frames at 24fps)")
        print(f"  Resolution: {full_info.get('width')}x{full_info.get('height')}")
        return 0
    else:
        print("ERROR: Output file not created")
        return 1

if __name__ == "__main__":
    sys.exit(main())
