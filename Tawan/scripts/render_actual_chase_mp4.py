import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
import os
import shutil
import subprocess

def render_chase_mp4():
    scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
    out_dir = r"D:\projects\ProjectAnimation\images\Chase_Storyboard_Renders"
    frames_dir = os.path.join(out_dir, "monster_chase_frames")
    
    # Keep existing frames to resume quickly
    os.makedirs(frames_dir, exist_ok=True)

    cmds.file(scene, open=True, force=True)

    monster_ctrl = "MONSTER:CTRL_Master"
    cube = "MainChar_Proxy_Cube"

    # Setup Monster (Z: 50 at f1 -> 450 at f120)
    cmds.cutKey(monster_ctrl, attribute="translateZ")
    cmds.setKeyframe(monster_ctrl, attribute="translateZ", value=50.0, time=1)
    cmds.setKeyframe(monster_ctrl, attribute="translateZ", value=450.0, time=120)
    cmds.setAttr(f"{monster_ctrl}.translateX", 0.0)
    cmds.setAttr(f"{monster_ctrl}.translateY", 61.43)
    cmds.setAttr(f"{monster_ctrl}.rotateY", 0.0)

    # Setup Cube (Z: 220 at f1 -> 620 at f120)
    cmds.cutKey(cube, attribute="translateZ")
    cmds.setKeyframe(cube, attribute="translateZ", value=220.0, time=1)
    cmds.setKeyframe(cube, attribute="translateZ", value=620.0, time=120)
    cmds.setAttr(f"{cube}.translateX", 0.0)
    cmds.setAttr(f"{cube}.translateY", 73.1)

    # Setup Chase Camera
    cam_name = "Cam_Monster_Chase_Tracking"
    if cmds.objExists(cam_name):
        cmds.delete(cam_name)
    cam_trans, cam_shape = cmds.camera(name=cam_name, focalLength=28.0, nearClipPlane=1.0, farClipPlane=10000.0)
    cmds.setAttr(f"{cam_shape}.renderable", 1)

    loc = cmds.spaceLocator(name="temp_target_loc")[0]
    cn = cmds.aimConstraint(loc, cam_trans, aimVector=[0, 0, -1], upVector=[0, 1, 0], worldUpType="vector", worldUpVector=[0, 1, 0])[0]

    # Position camera behind monster at f1 and f60
    cmds.currentTime(1)
    mz1 = cmds.getAttr(f"{monster_ctrl}.translateZ")
    cz1 = cmds.getAttr(f"{cube}.translateZ")
    
    cmds.currentTime(60)
    mz60 = cmds.getAttr(f"{monster_ctrl}.translateZ")
    cz60 = cmds.getAttr(f"{cube}.translateZ")

    # Key camera translate
    cmds.setKeyframe(cam_trans, attribute="translateX", value=-40.0, time=1)
    cmds.setKeyframe(cam_trans, attribute="translateY", value=145.0, time=1)
    cmds.setKeyframe(cam_trans, attribute="translateZ", value=mz1 - 158.0, time=1)

    cmds.setKeyframe(cam_trans, attribute="translateX", value=-40.0, time=60)
    cmds.setKeyframe(cam_trans, attribute="translateY", value=145.0, time=60)
    cmds.setKeyframe(cam_trans, attribute="translateZ", value=mz60 - 158.0, time=60)

    # Key aim locator
    cmds.setKeyframe(loc, attribute="translateX", value=0.0, time=1)
    cmds.setKeyframe(loc, attribute="translateY", value=80.0, time=1)
    cmds.setKeyframe(loc, attribute="translateZ", value=(mz1 + cz1) / 2.0, time=1)

    cmds.setKeyframe(loc, attribute="translateX", value=0.0, time=60)
    cmds.setKeyframe(loc, attribute="translateY", value=80.0, time=60)
    cmds.setKeyframe(loc, attribute="translateZ", value=(mz60 + cz60) / 2.0, time=60)

    print("Camera tracking setup complete. Rendering 60 frames...")

    # Render frames 1 to 60 (skipping already rendered frames)
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")
    for f in range(1, 61):
        dst = os.path.join(frames_dir, f"chase_{f:04d}.png")
        if os.path.exists(dst) and os.path.getsize(dst) > 1000:
            continue
        cmds.currentTime(f)
        p = cmds.render(cam_shape, x=640, y=360)
        shutil.copyfile(p, dst)
        if f % 10 == 0 or f == 60:
            print(f"Rendered frame {f}/60: {dst}")

    print("Rendering finished. Now assembling MP4 via ffmpeg...")
    
    ffmpeg_exe = r"C:\Users\tawan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0-full_build\bin\ffmpeg.exe"
    mp4_out = os.path.join(out_dir, "Backrooms_Monster_Chase_Full.mp4")
    
    cmd = [
        ffmpeg_exe, "-y",
        "-framerate", "24",
        "-start_number", "1",
        "-i", os.path.join(frames_dir, "chase_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "20",
        mp4_out
    ]
    subprocess.run(cmd, check=True)
    print(f"SUCCESS: MP4 created at {mp4_out}")

if __name__ == "__main__":
    render_chase_mp4()
