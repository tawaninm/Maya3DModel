"""
T07: playblast rigtest_charlie_v3.mp4 — 48 frames, hw2, 960x540.
Uses scenes/Characters/Charlie_Mixamo.mb (built by build_charlie_mixamo_v3.py at 22:26).
Imports Terrified_Run.fbx, renders hw2, encodes mp4.
"""
import os, shutil, subprocess, time

import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.mel as mel

WORKSPACE   = r"D:\projects\ProjectAnimation"
CHARLIE_MB  = os.path.join(WORKSPACE, r"scenes\Characters\Charlie_Mixamo.mb")
RUN_FBX     = os.path.join(WORKSPACE, r"raw_assets\mixamo\charlie\Terrified_Run.fbx")
TEST_SCENE  = os.path.join(WORKSPACE, r"scenes\Characters\_test_charlie_run_v3.mb")
BLAST_DIR   = os.path.join(WORKSPACE, r"movies\playblast\rigtest_charlie_v3")
MP4_OUT     = os.path.join(WORKSPACE, r"movies\playblast\rigtest_charlie.mp4")

os.makedirs(BLAST_DIR, exist_ok=True)

cmds.loadPlugin("fbxmaya", quiet=True)
cmds.file(CHARLIE_MB, open=True, force=True)

# Quick check: where is the character?
char_cx, char_cy, char_cz = 0.0, 70.0, 0.0
for part in ["body", "sweater", "short", "shoes1", "hoodie"]:
    if cmds.objExists(part):
        bb = cmds.exactWorldBoundingBox(part)
        print(f"PLACED {part} bbox: minY={bb[1]:.1f} maxY={bb[4]:.1f}  X={bb[0]:.1f}..{bb[3]:.1f}  Z={bb[2]:.1f}..{bb[5]:.1f}")
        char_cx = (bb[0] + bb[3]) / 2.0
        char_cy = (bb[1] + bb[4]) / 2.0
        char_cz = (bb[2] + bb[5]) / 2.0
        break

# Import Terrified Run animation
mel.eval('FBXImportMode -v "merge"')
mel.eval('FBXImportFillTimeline -v true')
cmds.file(RUN_FBX, i=True)

# 48 frames at 24fps
cmds.currentUnit(time="film")
cmds.playbackOptions(minTime=1, maxTime=48, animationStartTime=1, animationEndTime=48)

# Camera: aim at actual character center
cmds.currentTime(1)
if cmds.objExists("mixamorig:Hips"):
    hx, hy, hz = cmds.xform("mixamorig:Hips", q=True, ws=True, t=True)
    print(f"Hips at frame 1: {hx:.1f}, {hy:.1f}, {hz:.1f}")
    char_cx = hx; char_cz = hz

cam_node = cmds.camera(focalLength=35.0)[0]
cam_node = cmds.rename(cam_node, "CAM_RigTest_CharlieV3")
cam_shape = cmds.listRelatives(cam_node, shapes=True)[0]
# Place camera 300cm in Z from character center, aim at chest height
cmds.xform(cam_node, ws=True, t=[char_cx, char_cy + 20.0, char_cz + 300.0])
cmds.xform(cam_node, ws=True, ro=[-3.0, 0.0, 0.0])

for c in cmds.ls(type="camera"):
    cmds.setAttr(f"{c}.renderable", 1 if c == cam_shape else 0)

# Lights
dl = cmds.directionalLight(name="RigTest_DirLight_Charlie")
dl_xf = cmds.listRelatives(dl, parent=True)[0]
cmds.xform(dl_xf, ws=True, ro=[-35.0, 35.0, 0.0])
al = cmds.ambientLight(name="RigTest_AmbLight_Charlie")
cmds.setAttr(f"{al}.intensity", 0.5)

cmds.setAttr("defaultResolution.width", 960)
cmds.setAttr("defaultResolution.height", 540)
cmds.setAttr("defaultResolution.deviceAspectRatio", 960.0 / 540.0)

cmds.file(rename=TEST_SCENE)
cmds.file(save=True, force=True, type="mayaBinary")
print(f"Test scene saved: {TEST_SCENE}")

maya.standalone.uninitialize()

# Render
render_exe = r"D:\AutoDesk\Maya2027\bin\Render.exe"
cmd = [render_exe, "-r", "hw2",
       "-cam", "CAM_RigTest_CharlieV3",
       "-s", "1", "-e", "48",
       "-x", "960", "-y", "540",
       "-rd", BLAST_DIR, "-im", "charlie_run", "-of", "png",
       TEST_SCENE]

print("Rendering 48 frames Charlie v3...")
log_path = os.path.join(BLAST_DIR, "render_hw2.log")
with open(log_path, "w") as lf:
    proc = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    start = time.time()
    while time.time() - start < 120:
        if proc.poll() is not None:
            break
        last = os.path.join(BLAST_DIR, "charlie_run.png.0048")
        last2 = os.path.join(BLAST_DIR, "charlie_run_0048.png")
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
    if f.startswith("charlie_run.png."):
        num = f.split(".")[-1]
        old = os.path.join(BLAST_DIR, f)
        new = os.path.join(BLAST_DIR, f"charlie_run_{num}.png")
        if os.path.exists(new): os.remove(new)
        os.rename(old, new)

frames = sorted([f for f in os.listdir(BLAST_DIR) if f.startswith("charlie_run") and f.endswith(".png")])
sizes = [os.path.getsize(os.path.join(BLAST_DIR, f)) for f in frames]
print(f"Rendered {len(frames)} frames, sizes: min={min(sizes) if sizes else 0} max={max(sizes) if sizes else 0}")

# Encode
ffmpeg = shutil.which("ffmpeg")
if ffmpeg and len(frames) >= 12:
    pattern = os.path.join(BLAST_DIR, "charlie_run_%04d.png")
    ff_cmd = [ffmpeg, "-y", "-framerate", "24", "-i", pattern,
              "-c:v", "libx264", "-pix_fmt", "yuv420p", MP4_OUT]
    ff = subprocess.run(ff_cmd, capture_output=True, text=True)
    if os.path.exists(MP4_OUT):
        print(f"MP4 done: {MP4_OUT} ({os.path.getsize(MP4_OUT)} bytes)")
    else:
        print(f"ffmpeg error: {ff.stderr[-200:]}")

if os.path.exists(TEST_SCENE):
    os.remove(TEST_SCENE)
    print("Cleaned test scene")

print("CHARLIE V3 PLAYBLAST DONE")
