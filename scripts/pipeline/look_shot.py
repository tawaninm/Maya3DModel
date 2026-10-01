"""Apply the old-digital-camcorder look (camcorder_look.look) to every rendered frame of a shot and build a preview mp4.

Usage:  python scripts\\pipeline\\look_shot.py 09 [strength 0.0-2.0, default 1.0]
In:     movies\\playblast\\Shot09_arnold\\shot09.png.####   (the clean Arnold render)
Out:    movies\\playblast\\Shot09_look\\shot09_look.####.png  and  movies\\playblast\\Shot09_look.mp4
Noise is re-seeded per frame so the grain moves like real sensor noise. The clean render and Shot09.mp4 are not touched.
The look is a preview/grade step (plan.md Q19); the same grade can be done in DaVinci Resolve for the final.
"""
import glob
import os
import subprocess
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from camcorder_look import look  # noqa: E402

ROOT = r"D:\projects\ProjectAnimation"
FFMPEG = r"C:\Users\tawan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    shot = "%02d" % int(sys.argv[1])
    k = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    src = os.path.join(ROOT, "movies", "playblast", "Shot%s_arnold" % shot)
    dst = os.path.join(ROOT, "movies", "playblast", "Shot%s_look" % shot)
    frames = sorted(glob.glob(os.path.join(src, "shot%s.png.[0-9][0-9][0-9][0-9]" % shot)))
    if not frames:
        print("no frames in", src)
        return 1
    os.makedirs(dst, exist_ok=True)
    for i, p in enumerate(frames, start=1):
        n = int(p.rsplit(".", 1)[-1])
        with Image.open(p) as im:
            look(im, k, seed=n).save(os.path.join(dst, "shot%s_look.%04d.png" % (shot, n)))
        if i % 12 == 0 or i == len(frames):
            print("  looked %d/%d" % (i, len(frames)))
    mp4 = os.path.join(ROOT, "movies", "playblast", "Shot%s_look.mp4" % shot)
    cmd = [FFMPEG, "-y", "-f", "image2", "-framerate", "24", "-start_number", "1", "-i", os.path.join(dst, "shot%s_look.%%04d.png" % shot),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "slow", mp4]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("FFmpeg error:", res.stderr)
        return res.returncode
    print("Generated %s (%s bytes), strength %.1f" % (mp4, "{:,}".format(os.path.getsize(mp4)), k))
    return 0


if __name__ == "__main__":
    sys.exit(main())
