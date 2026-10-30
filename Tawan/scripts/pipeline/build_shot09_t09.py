"""T09 Shot09 pipeline assembly (2026-10-01).

Shot 09: the video-camera view as Charlie walks down the Backrooms main corridor (POV wide, slow cautious walk, head bob).
Duration: 3 seconds = 72 frames (24 fps).
Animation: Walking.fbx source frames 36-107 at 1:1 speed. The clip only travels ~34 units in 72 frames, so the Charlie placement group is
           also keyed along the corridor (about 70 units/s); the feet are out of frame, so foot sliding does not show.
Camera: first person, 24 mm, at Charlie's eye point (head joint collapsed like Shot 08), looks down the corridor toward -X with a slow
        look-around and handheld shake baked into the keys. The old-digital-camcorder look (noise, blur, bloom, vignette) is applied after
        rendering with look_shot.py, not in the scene (plan.md Q19).
Lighting: Preset A (LIGHT_MASTER exposure 13) as in plan.md, no extra lights: the corridor ceiling panels (z about 525) light the walls.
Rerunnable: restores scenes_backup_2026-10-01/Shot09_before_t09.mb before every run.
"""
import math
import os
import shutil
import sys

import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.api.OpenMaya as om

sys.path.insert(0, r"D:\projects\ProjectAnimation\scripts\pipeline")
from bake_mixamo_clip import bake_clip

SHOT = r"D:\projects\ProjectAnimation\scenes\Shots\Shot09.mb"
BACKUP_DIR = r"D:\projects\ProjectAnimation\scenes_backup_2026-10-01"
CLIP = r"D:\projects\ProjectAnimation\raw_assets\mixamo\charlie\Walking.fbx"

N_FRAMES = 72
SRC_FIRST, SRC_LAST = 36, 107
TIME_SCALE = N_FRAMES / float(SRC_LAST - SRC_FIRST + 1)      # 1.0
FLOOR_Y = -12.0
CHAR_YAW = -90.0                       # facing -X, along the corridor (walls at z ~343 and ~707, ceiling panels on z ~525 every ~450 units)
START = (600.0, FLOOR_Y, 470.0)        # east end of the corridor: the dark doorway at x ~ 0 (into the desk room) stays far ahead and small. z 470 keeps the near wall (z 343) left of frame, far wall (z 707) right
TRAVEL_X = 210.0                       # placement travel over the shot (70 units/s) on top of the clip's own ~34 units

FOCAL = 24.0
NEAR_CLIP = 15.0
CAM_FORWARD = 4.0
PITCH_BASE = 5.0                       # tilt up a little so the ceiling panels and wall tops are in frame
LOOK_YAW = 4.0                         # degrees of slow look-around
SHAKE_ROT, SHAKE_TRANS = 0.8, 0.7

os.makedirs(BACKUP_DIR, exist_ok=True)
bk = os.path.join(BACKUP_DIR, "Shot09_before_t09.mb")
if not os.path.exists(bk):
    shutil.copy2(SHOT, bk)
else:
    shutil.copy2(bk, SHOT)
print("L| backup", bk)

cmds.loadPlugin("mtoa", quiet=True)
cmds.file(SHOT, open=True, force=True, loadReferenceDepth="all")
cmds.playbackOptions(min=1, max=N_FRAMES, animationStartTime=1, animationEndTime=N_FRAMES)
cmds.currentUnit(time="film")


def mat(node):
    return om.MMatrix(cmds.xform(node, q=True, ws=True, m=True))


def wpos(n):
    return om.MPoint(*cmds.xform(n, q=True, ws=True, t=True))


def noise(f, seed):
    return (0.5 * math.sin(2 * math.pi * f / 17.0 + seed) + 0.3 * math.sin(2 * math.pi * f / 7.3 + 2.1 * seed)
            + 0.2 * math.sin(2 * math.pi * f / 3.1 + 3.7 * seed))


# 1. Bake the walk, place and move Charlie, hide the Monster
info = bake_clip(CLIP, rig_ns="CHARLIE:", src_first=SRC_FIRST, src_last=SRC_LAST, dst_first=1, time_scale=TIME_SCALE)
cmds.playbackOptions(min=1, max=N_FRAMES, animationStartTime=1, animationEndTime=N_FRAMES)
cmds.cutKey("CHARLIE:*", time=(N_FRAMES + 1, 400), clear=True)
assert info["frames"] == N_FRAMES and not info["missing_dst_joints"], info

for n in ("MONSTER:GRP_Monster_Mixamo", "MONSTER:Monster_Buff_Blobbell"):
    if cmds.objExists(n):
        cmds.setAttr(n + ".visibility", 0)
for ns in ("VCAM", "VCAM1", "VCAM2"):
    if cmds.objExists(ns + ":VideoCamera_GRP"):
        cmds.setAttr(ns + ":VideoCamera_GRP.visibility", 0)

PL = "CHARLIE:GRP_Charlie_Placement"
cmds.cutKey(PL, clear=True)
cmds.setAttr(PL + ".rotate", 0, CHAR_YAW, 0)
for f, x in ((1, START[0]), (N_FRAMES, START[0] - TRAVEL_X)):
    cmds.setKeyframe(PL, attribute="translateX", time=f, value=x)
    cmds.setKeyframe(PL, attribute="translateY", time=f, value=START[1])
    cmds.setKeyframe(PL, attribute="translateZ", time=f, value=START[2])
cmds.keyTangent(PL, attribute=["translateX", "translateY", "translateZ"], inTangentType="linear", outTangentType="linear")
print("L| Charlie walks x %.0f -> %.0f at z %.0f (plus the clip's own root motion)" % (START[0], START[0] - TRAVEL_X, START[2]))

# 2. Eye points from the head joints (recorded before the head is collapsed)
forward = om.MVector(-1, 0, 0)         # yaw -90 faces -X
eyes = {}
for f in range(1, N_FRAMES + 1):
    cmds.currentTime(f)
    head, top = wpos("CHARLIE:mixamorig:Head"), wpos("CHARLIE:mixamorig:HeadTop_End")
    eyes[f] = om.MPoint((head.x + top.x) / 2.0, (head.y + top.y) / 2.0, (head.z + top.z) / 2.0)
print("L| eye height above floor f1 %.1f f36 %.1f f72 %.1f" % (eyes[1].y - FLOOR_Y, eyes[36].y - FLOOR_Y, eyes[72].y - FLOOR_Y))

# 3. First-person trick (same as Shot 08): collapse the Head joint, hide the eye meshes
for ax in "XYZ":
    cmds.setAttr("CHARLIE:mixamorig:Head.scale%s" % ax, 0.001)
for eye_mesh in ("CHARLIE:bevelPolygon1", "CHARLIE:bevelPolygon2"):
    if cmds.objExists(eye_mesh):
        cmds.setAttr(eye_mesh + ".visibility", 0)

# 4. Camera
cam, grp = "CAM_Shot09", "GRP_CAM_Shot09"
shape = cmds.listRelatives(cam, shapes=True)[0]
if not cmds.objExists(grp):
    grp = cmds.group(cam, name=grp)
stray = (cmds.listConnections(cam, type="animCurve") or []) + (cmds.listConnections(grp, type="animCurve") or [])
if stray:
    cmds.delete(stray)
for attr in ("baseTx", "baseTy", "baseTz", "baseRx", "baseRy", "baseRz", "shakeRot", "shakeTrans"):
    if cmds.attributeQuery(attr, node=grp, exists=True):
        cmds.deleteAttr(grp, at=attr)
if cmds.objExists("EXPR_Shot09_Handheld"):
    cmds.delete("EXPR_Shot09_Handheld")
cmds.setAttr(grp + ".translate", 0, 0, 0)
cmds.setAttr(grp + ".rotate", 0, 0, 0)
cmds.setAttr(grp + ".scale", 1, 1, 1)
cmds.setAttr(cam + ".scale", 1, 1, 1)
cmds.cutKey(shape, attribute="focalLength", clear=True)
cmds.setAttr(shape + ".focalLength", FOCAL)
cmds.setAttr(shape + ".nearClipPlane", NEAR_CLIP)
for c in cmds.ls(type="camera"):
    try:
        cmds.setAttr(c + ".renderable", 1 if c == shape else 0)
    except Exception:
        pass

base_yaw = math.degrees(math.atan2(-forward.x, -forward.z))     # 90 for -X
for f in range(1, N_FRAMES + 1):
    pos = eyes[f] + forward * CAM_FORWARD
    look = LOOK_YAW * math.sin(2 * math.pi * (f - 1) / float(N_FRAMES))
    t = (pos.x + SHAKE_TRANS * noise(f, 1.3), pos.y + SHAKE_TRANS * noise(f, 4.1), pos.z + SHAKE_TRANS * 0.6 * noise(f, 7.7))
    r = (PITCH_BASE + SHAKE_ROT * noise(f, 2.9), base_yaw + look + SHAKE_ROT * noise(f, 5.3), SHAKE_ROT * 0.5 * noise(f, 8.9))
    for a, v in zip(("translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"), t + r):
        cmds.setKeyframe(cam, attribute=a, time=f, value=v)
cmds.filterCurve(cam + ".rotateX", cam + ".rotateY", cam + ".rotateZ", filter="euler")

# 5. Render options and lighting (preset A, no extra lights)
o = "defaultArnoldRenderOptions"
if cmds.objExists(o):
    cmds.setAttr(o + ".skipLicenseCheck", 0)
    cmds.setAttr(o + ".lightLinking", 0)
    cmds.setAttr(o + ".shadowLinking", 0)
    cmds.setAttr(o + ".renderDevice", 0)
if cmds.objExists("ENV:LIGHT_MASTER") and cmds.attributeQuery("exposure", node="ENV:LIGHT_MASTER", exists=True):
    cmds.setAttr("ENV:LIGHT_MASTER.exposure", 13.0)
    if cmds.attributeQuery("flickerEnable", node="ENV:LIGHT_MASTER", exists=True):
        cmds.setAttr("ENV:LIGHT_MASTER.flickerEnable", 0.0)        # preset A = steady light (flicker is preset B, shots 10-14)

# 6. Checks: what the camera sees down the corridor (walls left/right, free run ahead, nearest ceiling panel ahead)
sel = om.MSelectionList()
env_fns = []
for s in cmds.ls("ENV:*", type="mesh", noIntermediate=True, long=True):
    sel.clear()
    sel.add(s)
    env_fns.append(om.MFnMesh(sel.getDagPath(0)))


def ray(p, d, limit=4000.0):
    best = limit
    for fn in env_fns:
        r = fn.closestIntersection(om.MFloatPoint(p.x, p.y, p.z), om.MFloatVector(*d), om.MSpace.kWorld, limit, False)
        if r and r[0] is not None and r[1] is not None and r[1] > 0:
            best = min(best, r[1])
    return best


for f in (1, 36, N_FRAMES):
    cmds.currentTime(f)
    p = wpos(cam)
    print("L| f%02d camera (%.0f, %.0f, %.0f) free run ahead (-x) %.0f, wall at +z %.0f, wall at -z %.0f, ceiling %.0f above"
          % (f, p.x, p.y, p.z, ray(p, (-1, 0, 0)), ray(p, (0, 0, 1)), ray(p, (0, 0, -1)), ray(p, (0, 1, 0))))
panels = sorted(l for l in [cmds.xform(cmds.listRelatives(x, parent=True)[0], q=True, ws=True, t=True) for x in cmds.ls(type="aiAreaLight") if x.startswith("ENV:")] if abs(l[2] - 525) < 60)
print("L| ceiling panels on the corridor line, x:", [round(l[0]) for l in panels])

cmds.currentTime(1)
cmds.file(save=True, type="mayaBinary")
print("L| saved", SHOT)
maya.standalone.uninitialize()
