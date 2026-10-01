"""T09 Shot05 pipeline test (Claude, 2026-10-01). Edits scenes/Shots/Shot05.mb in place after copying it to scenes_backup_2026-10-01/.

Steps: bake Stumble_Backwards (frames 0-23 -> 1-24) onto CHARLIE:mixamorig:*, place Charlie, hide the Monster (not in this shot),
reset the camera (run 3 left a garbage local transform and two stray keys on CAM_Shot05), add handheld shake (expression on GRP_CAM_Shot05)
and a crash zoom 24 -> 45 mm over the last 8 frames, print bounding boxes and a frustum test.
Layout (cm): Charlie faces +Z, falls backwards towards -Z. Camera is in front of him at +Z, low (35 cm), 24 mm, looking slightly up.
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

SHOT = r"D:\projects\ProjectAnimation\scenes\Shots\Shot05.mb"
BACKUP_DIR = r"D:\projects\ProjectAnimation\scenes_backup_2026-10-01"
CLIP = r"D:\projects\ProjectAnimation\raw_assets\mixamo\charlie\Stumble_Backwards.fbx"
CHAR_POS = (-40.0, -12.0, 300.0)      # env floor is at y = -12; moved next to the panel row at z=525 (panels 05/04), the area near the origin has no light within 5 m
CAM_POS = (-40.0, 35.0, 640.0)
AIM_AT = (-40.0, 75.0, 300.0)

os.makedirs(BACKUP_DIR, exist_ok=True)
bk = os.path.join(BACKUP_DIR, "Shot05_before_t09.mb")
if not os.path.exists(bk):
    shutil.copy2(SHOT, bk)
else:
    shutil.copy2(bk, SHOT)   # re-run: start again from the pre-T09 file so nothing is baked twice
print("L| backup", bk)

cmds.loadPlugin("mtoa", quiet=True)
cmds.file(SHOT, open=True, force=True, loadReferenceDepth="all")
cmds.playbackOptions(min=1, max=24, animationStartTime=1, animationEndTime=24)

# 1. bake Charlie animation
bake_clip(CLIP, rig_ns="CHARLIE:", src_first=0, src_last=23, dst_first=1)

# 2. place Charlie and hide the Monster
cmds.setAttr("CHARLIE:GRP_Charlie_Placement.translate", *CHAR_POS)
for n in ("MONSTER:GRP_Monster_Mixamo", "MONSTER:Monster_Buff_Blobbell"):
    cmds.setAttr(n + ".visibility", 0)

# 3. camera: remove the stray keys, reset the child, aim the group
grp, cam = "GRP_CAM_Shot05", "CAM_Shot05"
shape = cmds.listRelatives(cam, shapes=True)[0]
stray = [c for c in (cmds.listConnections(cam, type="animCurve") or [])]
print("L| stray curves on", cam, stray)
if stray:
    cmds.delete(stray)
cmds.setAttr(cam + ".translate", 0, 0, 0)
cmds.setAttr(cam + ".rotate", 0, 0, 0)
dx, dy, dz = (AIM_AT[i] - CAM_POS[i] for i in range(3))
yaw = math.degrees(math.atan2(-dx, -dz))                       # 0 when looking down -Z
pitch = math.degrees(math.atan2(dy, math.hypot(dx, dz)))       # positive = look up
base = dict(Tx=CAM_POS[0], Ty=CAM_POS[1], Tz=CAM_POS[2], Rx=pitch, Ry=yaw, Rz=0.0)
cmds.setAttr(grp + ".translate", base["Tx"], base["Ty"], base["Tz"])
cmds.setAttr(grp + ".rotate", base["Rx"], base["Ry"], base["Rz"])
print("L| camera group base", {k: round(v, 2) for k, v in base.items()})

# 4. handheld shake: expression drives the group, base pose lives in custom attributes
for k, v in base.items():
    cmds.addAttr(grp, longName="base" + k, attributeType="double", defaultValue=v)
    cmds.setAttr(grp + ".base" + k, v)
cmds.addAttr(grp, longName="shakeRot", attributeType="double", defaultValue=0.4)
cmds.addAttr(grp, longName="shakeTrans", attributeType="double", defaultValue=0.5)
expr = (
    "float $f = frame;\n"
    "{g}.rotateX = {g}.baseRx + {g}.shakeRot * noise($f * 0.37 + 11.3);\n"
    "{g}.rotateY = {g}.baseRy + {g}.shakeRot * noise($f * 0.41 + 37.1);\n"
    "{g}.rotateZ = {g}.baseRz + {g}.shakeRot * 0.5 * noise($f * 0.33 + 71.9);\n"
    "{g}.translateX = {g}.baseTx + {g}.shakeTrans * noise($f * 0.29 + 5.7);\n"
    "{g}.translateY = {g}.baseTy + {g}.shakeTrans * noise($f * 0.31 + 23.9);\n"
    "{g}.translateZ = {g}.baseTz + {g}.shakeTrans * 0.6 * noise($f * 0.27 + 47.3);\n"
).format(g=grp)
cmds.expression(name="EXPR_Shot05_Handheld", string=expr, alwaysEvaluate=True)

# 5. crash zoom over the last 8 frames
cmds.cutKey(shape, attribute="focalLength", clear=True)
cmds.setAttr(shape + ".focalLength", 24)
cmds.setKeyframe(shape, attribute="focalLength", time=16, value=24, inTangentType="linear", outTangentType="linear")
cmds.setKeyframe(shape, attribute="focalLength", time=24, value=45, inTangentType="linear", outTangentType="linear")
print("L| film fit", cmds.getAttr(shape + ".filmFit"), "hfa", cmds.getAttr(shape + ".horizontalFilmAperture"))

# 6. measurements
def wpos(n):
    return om.MPoint(*cmds.xform(n, q=True, ws=True, t=True))


def vertex_bbox(nodes):
    xs = []
    for n in nodes:
        for s in cmds.listRelatives(n, shapes=True, noIntermediate=True, fullPath=True) or []:
            xs += cmds.xform(s + ".vtx[*]", q=True, ws=True, t=True)
    px, py, pz = xs[0::3], xs[1::3], xs[2::3]
    return [round(min(px), 1), round(min(py), 1), round(min(pz), 1), round(max(px), 1), round(max(py), 1), round(max(pz), 1)]


meshes = [m for m in cmds.ls("CHARLIE:*", type="mesh", noIntermediate=True)]
mesh_tr = list({cmds.listRelatives(m, parent=True)[0] for m in meshes})
W, H = cmds.getAttr("defaultResolution.width"), cmds.getAttr("defaultResolution.height")
aspect = W / float(H)
points = ["CHARLIE:mixamorig:HeadTop_End", "CHARLIE:mixamorig:Head", "CHARLIE:mixamorig:Hips", "CHARLIE:mixamorig:LeftFoot", "CHARLIE:mixamorig:RightFoot"]


def ndc(point):
    focal = cmds.getAttr(shape + ".focalLength")
    h = cmds.getAttr(shape + ".horizontalFilmAperture") * 25.4 / 2.0
    m = om.MMatrix(cmds.xform(cam, q=True, ws=True, m=True))
    pc = point * m.inverse()
    if pc.z >= 0:
        return None
    return (pc.x / -pc.z) * focal / h, (pc.y / -pc.z) * focal / (h / aspect)


for f in range(1, 25):
    cmds.currentTime(f)
    res = {}
    for p in points:
        r = ndc(wpos(p))
        res[p.split(":")[-1]] = None if r is None else (round(r[0], 2), round(r[1], 2), abs(r[0]) <= 1 and abs(r[1]) <= 1)
    if f in (1, 12, 24) or f % 6 == 0:
        print("L| frustum f%02d focal %.1f" % (f, cmds.getAttr(shape + ".focalLength")), res)
        print("L| bbox f%02d Charlie meshes (xmin,ymin,zmin,xmax,ymax,zmax)" % f, vertex_bbox(mesh_tr))
cmds.currentTime(1)
shake = [(round(cmds.getAttr(grp + ".rotateX", time=f), 3), round(cmds.getAttr(grp + ".translateY", time=f), 3)) for f in (1, 2, 3, 4)]
print("L| shake sample (rotX, transY) f1-4", shake)

# 7. save
cmds.file(save=True, type="mayaBinary")
print("L| saved", SHOT)
maya.standalone.uninitialize()
