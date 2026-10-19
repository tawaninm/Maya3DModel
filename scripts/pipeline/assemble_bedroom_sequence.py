"""Assemble BedRoom scene and Backrooms sequence into full preview videos.

Inputs:
  - BedRoom: movies/playblast/BedRoom/test02.mp4 (1280x720, 240 frames @ 29.97fps, resampled to 24fps -> 8.0s)
  - Backrooms Paced: movies/playblast/Backrooms_Blocking_Paced.mp4 (640x360, 672 frames @ 24fps -> 28.0s)
  - Backrooms Full: movies/playblast/Backrooms_Blocking_Full.mp4 (640x360, 576 frames @ 24fps -> 24.0s)

Outputs:
  - movies/playblast/Sequence_Bedroom_Backrooms_Paced.mp4 (36.0s, 864 frames @ 24fps, 1280x720)
  - movies/playblast/Sequence_Bedroom_Backrooms_Full.mp4 (32.0s, 768 frames @ 24fps, 1280x720)

Usage:
    python scripts/pipeline/assemble_bedroom_sequence.py
"""
import os
import sys
import subprocess
import shutil
import json

ROOT = r"D:\projects\ProjectAnimation"
BLAST_DIR = os.path.join(ROOT, "movies", "playblast")
BEDROOM_MP4 = os.path.join(BLAST_DIR, "BedRoom", "test02.mp4")
BACKROOMS_PACED = os.path.join(BLAST_DIR, "Backrooms_Blocking_Paced.mp4")
BACKROOMS_FULL = os.path.join(BLAST_DIR, "Backrooms_Blocking_Full.mp4")

FFMPEG = r"C:\Users\tawan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
FFPROBE = r"C:\Users\tawan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffprobe.exe"

if not os.path.exists(FFMPEG):
    FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
if not os.path.exists(FFPROBE):
    FFPROBE = shutil.which("ffprobe") or "ffprobe"

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

def assemble(backrooms_input, output_path, label):
    if not os.path.exists(BEDROOM_MP4):
        print(f"ERROR: BedRoom video not found: {BEDROOM_MP4}")
        return False
    if not os.path.exists(backrooms_input):
        print(f"ERROR: Backrooms input not found: {backrooms_input}")
        return False

    print(f"\n--- Assembling {label} ---")
    filter_complex = (
        "[0:v]fps=24,scale=1280:720,setsar=1[v0];"
        "[1:v]scale=1280:720:flags=lanczos,fps=24,setsar=1[v1];"
        "[v0][v1]concat=n=2:v=1:a=0[v]"
    )

    cmd = [
        FFMPEG, "-y",
        "-i", BEDROOM_MP4,
        "-i", backrooms_input,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FFmpeg error: {r.stderr}")
        return False

    info = probe_video(output_path)
    if info:
        frames = int(info.get("nb_read_packets", 0))
        dur = float(info.get("duration", 0.0))
        sz = os.path.getsize(output_path)
        print(f"SUCCESS: {output_path}")
        print(f"  Resolution: {info.get('width')}x{info.get('height')}")
        print(f"  Frames: {frames} ({dur:.2f}s @ 24 fps)")
        print(f"  Size: {sz:,} bytes")

    # Integrity check
    vcmd = [FFMPEG, "-v", "error", "-i", output_path, "-f", "null", "-"]
    vr = subprocess.run(vcmd, capture_output=True, text=True)
    if vr.returncode == 0:
        print("  Stream integrity: PASSED")
    else:
        print(f"  Stream integrity WARNING: {vr.stderr}")
    return True

def main():
    out_paced = os.path.join(BLAST_DIR, "Sequence_Bedroom_Backrooms_Paced.mp4")
    out_full = os.path.join(BLAST_DIR, "Sequence_Bedroom_Backrooms_Full.mp4")

    ok1 = assemble(BACKROOMS_PACED, out_paced, "BedRoom + Backrooms Paced")
    ok2 = assemble(BACKROOMS_FULL, out_full, "BedRoom + Backrooms Full")

    if ok1 and ok2:
        print("\nAll sequence assemblies finished successfully.")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
