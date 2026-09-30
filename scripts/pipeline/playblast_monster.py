"""
T07: playblast rigtest_monster.mp4 — 48 frames, hw2, 960x540.
Opens Monster_Mixamo.mb, imports Walking.fbx animation, renders hw2 12→48 frames, encodes mp4.
"""
import os, shutil, subprocess, time

import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.mel as mel

WORKSPACE = r"D:\projects\ProjectAnimation"
MONSTER_MB = os.path.join(WORKSPACE, r"scenes\Characters\Monster_Mixamo.mb")
WALK_FBX   = os.path.join(WORKSPACE, r"raw_assets\mixamo\monster\Walking.fbx")
TEST_SCENE  = os.path.join(WORKSPACE, r"scenes\Characters\_test_monster_walk.mb")
BLAST_DIR   = os.path.join(WORKSPACE, r"movies\playblast\rigtest_monster")
MP4_OUT     = os.path.join(WORKSPACE, r"movies\playblast\rigtest_monster.mp4")

os.makedirs(BLAST_DIR, exist_ok=True)

cmds.loadPlugin("fbxmaya", quiet=True)
cmds.file(MONSTER_MB, open=True, force=True)

# Import walk animation
mel.eval('FBXImportMode -v "merge"')
mel.eval('FBXImportFillTimeline -v true')
cmds.file(WALK_FBX, i=True)

# Set 48 frames at 24fps
cmds.currentUnit(time="film")
cmds.playbackOptions(minTime=1, maxTime=48, animationStartTime=1, animationEndTime=48)

# Camera: Monster is ~170cm tall, around origin after Mixamo import
cam_node = cmds.camera(focalLength=35.0)[0]
cam_node = cmds.rename(cam_node, "CAM_RigTest_Monster")
cam_shape = cmds.listRelatives(cam_node, shapes=True)[0]
cmds.xform(cam_node, ws=True, t=[0.0, 100.0, 400.0])
cmds.xform(cam_node, ws=True, ro=[-5.0, 0.0, 0.0])

for c in cmds.ls(type="camera"):
    cmds.setAttr(f"{c}.renderable", 1 if c == cam_shape else 0)

# Lights
dl = cmds.directionalLight(name="RigTest_DirLight_Monster")
dl_xf = cmds.listRelatives(dl, parent=True)[0]
cmds.xform(dl_xf, ws=True, ro=[-35.0, 35.0, 0.0])
al = cmds.ambientLight(name="RigTest_AmbLight_Monster")
cmds.setAttr(f"{al}.intensity", 0.5)

# Resolution
cmds.setAttr("defaultResolution.width", 960)
cmds.setAttr("defaultResolution.height", 540)
cmds.setAttr("defaultResolution.deviceAspectRatio", 960.0 / 540.0)

# Save test scene
cmds.file(rename=TEST_SCENE)
cmds.file(save=True, force=True, type="mayaBinary")
print(f"Test scene saved: {TEST_SCENE} ({os.path.getsize(TEST_SCENE)} bytes)")

maya.standalone.uninitialize()

# Render with Render.exe -r hw2
render_exe = r"D:\AutoDesk\Maya2027\bin\Render.exe"
cmd = [render_exe, "-r", "hw2",
       "-cam", "CAM_RigTest_Monster",
       "-s", "1", "-e", "48",
       "-x", "960", "-y", "540",
       "-rd", BLAST_DIR, "-im", "monster_walk", "-of", "png",
       TEST_SCENE]

print(f"Rendering 48 frames...")
log_path = os.path.join(BLAST_DIR, "render_hw2.log")
with open(log_path, "w") as lf:
    proc = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    start = time.time()
    while time.time() - start < 120:
        if proc.poll() is not None:
            break
        last = os.path.join(BLAST_DIR, "monster_walk.png.0048")
        last2 = os.path.join(BLAST_DIR, "monster_walk_0048.png")
        if (os.path.exists(last) and os.path.getsize(last) > 500) or \
           (os.path.exists(last2) and os.path.getsize(last2) > 500):
            time.sleep(1.0)
            proc.terminate()
            break
        time.sleep(1.5)
    else:
        proc.kill()

# Normalize filenames
for f in os.listdir(BLAST_DIR):
    if f.startswith("monster_walk.png."):
        num = f.split(".")[-1]
        old = os.path.join(BLAST_DIR, f)
        new = os.path.join(BLAST_DIR, f"monster_walk_{num}.png")
        if os.path.exists(new): os.remove(new)
        os.rename(old, new)

frames = sorted([f for f in os.listdir(BLAST_DIR) if f.startswith("monster_walk") and f.endswith(".png")])
print(f"Rendered {len(frames)} frames")

# Encode to mp4
ffmpeg = shutil.which("ffmpeg")
if ffmpeg and len(frames) >= 12:
    pattern = os.path.join(BLAST_DIR, "monster_walk_%04d.png")
    ff_cmd = [ffmpeg, "-y", "-framerate", "24", "-i", pattern,
              "-c:v", "libx264", "-pix_fmt", "yuv420p", MP4_OUT]
    ff = subprocess.run(ff_cmd, capture_output=True, text=True)
    if os.path.exists(MP4_OUT):
        print(f"MP4 done: {MP4_OUT} ({os.path.getsize(MP4_OUT)} bytes)")
    else:
        print(f"ffmpeg error: {ff.stderr[-200:]}")
else:
    print(f"Skipping ffmpeg (found={ffmpeg}, frames={len(frames)})")

# Cleanup test scene
if os.path.exists(TEST_SCENE):
    os.remove(TEST_SCENE)
    print(f"Cleaned test scene")

print("MONSTER PLAYBLAST DONE")
