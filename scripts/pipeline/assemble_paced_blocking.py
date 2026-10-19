"""Assemble Shot05 to Shot14 into Backrooms_Blocking_Paced.mp4 with narrative pacing hold frames.

Pacing adjustments:
  Shot05: +1.0s start hold (24 frames) - Ear against wall before startle (48 -> 72 frames)
  Shot06: 72 frames (unchanged)
  Shot07: +1.0s start hold (24 frames) - Static camcorder insert dread (72 -> 96 frames)
  Shot08: 48 frames (unchanged)
  Shot09: 72 frames (unchanged)
  Shot10: 48 frames (unchanged)
  Shot11: +1.5s stop hold (36 frames) - Read "DON'T RUN" text clearly (72 -> 108 frames)
  Shot12: +0.5s stop hold (12 frames) - Monster roar impact (48 -> 60 frames)
  Shot13: 48 frames (unchanged) - Frantic chase
  Shot14: 48 frames (unchanged) - Dive into void

Total: 672 frames (28.00 seconds @ 24 fps)

Usage:
    python scripts/pipeline/assemble_paced_blocking.py
"""
import os
import sys
import subprocess
import shutil
import json

ROOT = r"D:\projects\ProjectAnimation"
BLAST_DIR = os.path.join(ROOT, "movies", "playblast")
PACED_DIR = os.path.join(BLAST_DIR, "_paced")
FFMPEG = r"C:\Users\tawan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
FFPROBE = r"C:\Users\tawan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffprobe.exe"

if not os.path.exists(FFMPEG):
    FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
if not os.path.exists(FFPROBE):
    FFPROBE = shutil.which("ffprobe") or "ffprobe"

PACING_CONFIG = {
    "Shot05": {"start_frames": 24, "stop_frames": 0, "expected_frames": 72, "note": "Ear on wall hold (+1.0s)"},
    "Shot06": {"start_frames": 0, "stop_frames": 0, "expected_frames": 72, "note": "Dutch angle getting up"},
    "Shot07": {"start_frames": 24, "stop_frames": 0, "expected_frames": 96, "note": "Static desk camera dread (+1.0s)"},
    "Shot08": {"start_frames": 0, "stop_frames": 0, "expected_frames": 48, "note": "POV pick up camera"},
    "Shot09": {"start_frames": 0, "stop_frames": 0, "expected_frames": 72, "note": "POV hallway walk"},
    "Shot10": {"start_frames": 0, "stop_frames": 0, "expected_frames": 48, "note": "Monster POV stalking"},
    "Shot11": {"start_frames": 0, "stop_frames": 36, "expected_frames": 108, "note": "Read DONT RUN clearly (+1.5s)"},
    "Shot12": {"start_frames": 0, "stop_frames": 12, "expected_frames": 60, "note": "Monster roar impact (+0.5s)"},
    "Shot13": {"start_frames": 0, "stop_frames": 0, "expected_frames": 48, "note": "Terrified run sprint"},
    "Shot14": {"start_frames": 0, "stop_frames": 0, "expected_frames": 48, "note": "Dive into floor hole"},
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
    os.makedirs(PACED_DIR, exist_ok=True)
    shots = [f"Shot{i:02d}" for i in range(5, 15)]
    paced_shot_paths = []
    total_expected = sum(cfg["expected_frames"] for cfg in PACING_CONFIG.values())
    total_actual = 0

    print("--- Applying Narrative Pacing Adjustments ---")
    for s in shots:
        raw_mp4 = os.path.join(BLAST_DIR, f"{s}.mp4")
        if not os.path.exists(raw_mp4):
            print(f"ERROR: {raw_mp4} not found!")
            return 1

        cfg = PACING_CONFIG[s]
        start_f = cfg["start_frames"]
        stop_f = cfg["stop_frames"]
        target_mp4 = os.path.join(PACED_DIR, f"{s}_paced.mp4")

        filters = []
        if start_f > 0:
            filters.append(f"tpad=start_mode=clone:start={start_f}")
        if stop_f > 0:
            filters.append(f"tpad=stop_mode=clone:stop={stop_f}")
        filters.append("setpts=N/FRAME_RATE/TB")
        vf_str = ",".join(filters)

        cmd = [
            FFMPEG, "-y", "-i", raw_mp4,
            "-vf", vf_str,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", target_mp4
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"Error processing {s}:", r.stderr)
            return 1

        info = probe_video(target_mp4)
        frames = int(info.get("nb_read_packets", 0))
        dur = float(info.get("duration", 0.0))
        exp = cfg["expected_frames"]
        total_actual += frames
        status = "OK" if frames == exp else f"MISMATCH (expected {exp})"
        note = cfg.get("note", "")
        print(f"  {s}: {frames} frames ({dur:.2f}s) - {status} [start+{start_f}f, stop+{stop_f}f] - {note}")
        paced_shot_paths.append(target_mp4)

    concat_txt = os.path.join(PACED_DIR, "_concat_paced.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in paced_shot_paths:
            escaped = p.replace("\\", "/")
            f.write(f"file '{escaped}'\n")

    out_mp4 = os.path.join(BLAST_DIR, "Backrooms_Blocking_Paced.mp4")
    cmd = [
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt, "-c", "copy", out_mp4
    ]
    print("\n--- Concatenating into Backrooms_Blocking_Paced.mp4 ---")
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
        print(f"  Total frames: {full_frames} (expected {total_expected})")
        print(f"  Total duration: {full_dur:.2f} seconds")

        # Verify stream
        vcmd = [FFMPEG, "-v", "error", "-i", out_mp4, "-f", "null", "-"]
        vr = subprocess.run(vcmd, capture_output=True, text=True)
        if vr.returncode == 0:
            print("  Stream integrity check: PASSED (No decode errors)")
        else:
            print("  Stream integrity check: WARNING -", vr.stderr)

    return 0

if __name__ == "__main__":
    sys.exit(main())
