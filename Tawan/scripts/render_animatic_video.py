import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
import os
import shutil
import subprocess

def render_animatic():
    scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
    out_dir = r"D:\projects\ProjectAnimation\images\Chase_Storyboard_Renders"
    temp_frames_dir = os.path.join(out_dir, "temp_frames")
    os.makedirs(temp_frames_dir, exist_ok=True)

    cmds.file(scene, open=True, force=True)

    # Shot 12: Frames 1 to 60 (Cam_Shot12_DutchTurnShape1)
    cam12 = "Cam_Shot12_DutchTurnShape1"
    for f in range(1, 61):
        cmds.currentTime(f)
        p = cmds.render(cam12, x=960, y=540)
        dst = os.path.join(temp_frames_dir, f"frame_{f:04d}.png")
        shutil.copyfile(p, dst)
        if f % 15 == 0:
            print(f"Shot 12 progress: {f}/60")

    # Shot 13: Frames 61 to 120 (Cam_Shot13_ChaseRunningShape1)
    cam13 = "Cam_Shot13_ChaseRunningShape1"
    for f in range(61, 121):
        cmds.currentTime(f)
        p = cmds.render(cam13, x=960, y=540)
        dst = os.path.join(temp_frames_dir, f"frame_{f:04d}.png")
        shutil.copyfile(p, dst)
        if f % 15 == 0:
            print(f"Shot 13 progress: {f}/120")

    print("All 120 frames rendered. Now compiling MP4 via ffmpeg...")
    
    # 1. Full animatic MP4 (120 frames @ 24fps)
    full_mp4 = os.path.join(out_dir, "Backrooms_Chase_Animatic_Full_120f.mp4")
    cmd_full = [
        "ffmpeg", "-y",
        "-framerate", "24",
        "-start_number", "1",
        "-i", os.path.join(temp_frames_dir, "frame_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        full_mp4
    ]
    subprocess.run(cmd_full, check=True)
    print(f"FULL ANIMATIC CREATED: {full_mp4}")

    # 2. Shot 12 MP4 (frames 1-60)
    s12_mp4 = os.path.join(out_dir, "Shot12_DutchAngle_LookBack_60f.mp4")
    cmd_s12 = [
        "ffmpeg", "-y",
        "-framerate", "24",
        "-start_number", "1",
        "-i", os.path.join(temp_frames_dir, "frame_%04d.png"),
        "-vframes", "60",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        s12_mp4
    ]
    subprocess.run(cmd_s12, check=True)
    print(f"SHOT 12 MP4 CREATED: {s12_mp4}")

    # 3. Shot 13 MP4 (frames 61-120)
    s13_mp4 = os.path.join(out_dir, "Shot13_DynamicChase_Running_60f.mp4")
    cmd_s13 = [
        "ffmpeg", "-y",
        "-framerate", "24",
        "-start_number", "61",
        "-i", os.path.join(temp_frames_dir, "frame_%04d.png"),
        "-vframes", "60",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        s13_mp4
    ]
    subprocess.run(cmd_s13, check=True)
    print(f"SHOT 13 MP4 CREATED: {s13_mp4}")

    # Clean up temp frames
    try:
        shutil.rmtree(temp_frames_dir)
    except Exception as e:
        print(f"Warning cleaning temp_frames: {e}")

    print("ALL DONE SUCCESSFULLY!")

if __name__ == "__main__":
    render_animatic()
