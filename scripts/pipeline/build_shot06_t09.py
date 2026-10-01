"""T09 Shot06 pipeline assembly (2026-10-01).

Shot 06: Charlie gets up from the floor after stumbling into Backrooms.
Duration: 3 seconds = 72 frames (24 fps).
Animation: Getting_Up.fbx (66 frames stretched to 72 frames).
Camera: Medium Shot, Dutch angle (8 deg), Handheld shake, 35 mm lens.
Lighting: Light Preset A (exposure 13.0).
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

SHOT = r"D:\projects\ProjectAnimation\scenes\Shots\Shot06.mb"
BACKUP_DIR = r"D:\projects\ProjectAnimation\scenes_backup_2026-10-01"
CLIP = r"D:\projects\ProjectAnimation\raw_assets\mixamo\charlie\Getting_Up.fbx"

# Position continuous with Shot 05
CHAR_POS = (-40.0, -12.0, 300.0)
CAM_POS = (-40.0, 58.0, 520.0)
AIM_AT = (-40.0, 55.0, 300.0)
DUTCH_ANGLE = 8.0  # degrees roll
FOCAL_LENGTH = 35.0  # mm
N_FRAMES = 72

os.makedirs(BACKUP_DIR, exist_ok=True)
bk = os.path.join(BACKUP_DIR, "Shot06_before_t09.mb")
if not os.path.exists(bk):
    shutil.copy2(SHOT, bk)
else:
    shutil.copy2(bk, SHOT)
print("L| backup", bk)

cmds.loadPlugin("mtoa", quiet=True)
cmds.file(SHOT, open=True, force=True, loadReferenceDepth="all")
cmds.playbackOptions(min=1, max=N_FRAMES, animationStartTime=1, animationEndTime=N_FRAMES)
cmds.currentUnit(time="film")

# 1. Bake Charlie Getting_Up animation (source 0..65 -> exactly 72 frames)
bake_clip(CLIP, rig_ns="CHARLIE:", src_first=0, src_last=65, dst_first=1, time_scale=71.0 / 65.0)
cmds.playbackOptions(min=1, max=N_FRAMES, animationStartTime=1, animationEndTime=N_FRAMES)
cmds.cutKey("CHARLIE:*", time=(N_FRAMES + 1, 100), clear=True)

# 2. Place Charlie and hide Monster
cmds.setAttr("CHARLIE:GRP_Charlie_Placement.translate", *CHAR_POS)
for n in ("MONSTER:GRP_Monster_Mixamo", "MONSTER:Monster_Buff_Blobbell"):
    if cmds.objExists(n):
        cmds.setAttr(n + ".visibility", 0)

# 3. Camera setup: CAM_Shot06
grp, cam = "GRP_CAM_Shot06", "CAM_Shot06"
shape = cmds.listRelatives(cam, shapes=True)[0]

stray = [c for c in (cmds.listConnections(cam, type="animCurve") or [])]
if stray:
    cmds.delete(stray)

cmds.setAttr(cam + ".translate", 0, 0, 0)
cmds.setAttr(cam + ".rotate", 0, 0, 0)

dx, dy, dz = (AIM_AT[i] - CAM_POS[i] for i in range(3))
yaw = math.degrees(math.atan2(-dx, -dz))
pitch = math.degrees(math.atan2(dy, math.hypot(dx, dz)))

base = dict(Tx=CAM_POS[0], Ty=CAM_POS[1], Tz=CAM_POS[2], Rx=pitch, Ry=yaw, Rz=DUTCH_ANGLE)
cmds.setAttr(grp + ".translate", base["Tx"], base["Ty"], base["Tz"])
cmds.setAttr(grp + ".rotate", base["Rx"], base["Ry"], base["Rz"])
print("L| camera group base", {k: round(v, 2) for k, v in base.items()})

# 4. Handheld shake expression
for k, v in base.items():
    if not cmds.attributeQuery("base" + k, node=grp, exists=True):
        cmds.addAttr(grp, longName="base" + k, attributeType="double", defaultValue=v)
    cmds.setAttr(grp + ".base" + k, v)

if not cmds.attributeQuery("shakeRot", node=grp, exists=True):
    cmds.addAttr(grp, longName="shakeRot", attributeType="double", defaultValue=0.4)
if not cmds.attributeQuery("shakeTrans", node=grp, exists=True):
    cmds.addAttr(grp, longName="shakeTrans", attributeType="double", defaultValue=0.5)

expr_name = "EXPR_Shot06_Handheld"
if cmds.objExists(expr_name):
    cmds.delete(expr_name)

expr = (
    "float $f = frame;\n"
    "{g}.rotateX = {g}.baseRx + {g}.shakeRot * noise($f * 0.35 + 15.1);\n"
    "{g}.rotateY = {g}.baseRy + {g}.shakeRot * noise($f * 0.39 + 42.7);\n"
    "{g}.rotateZ = {g}.baseRz + {g}.shakeRot * 0.5 * noise($f * 0.31 + 83.3);\n"
    "{g}.translateX = {g}.baseTx + {g}.shakeTrans * noise($f * 0.27 + 7.9);\n"
    "{g}.translateY = {g}.baseTy + {g}.shakeTrans * noise($f * 0.33 + 29.1);\n"
    "{g}.translateZ = {g}.baseTz + {g}.shakeTrans * 0.6 * noise($f * 0.25 + 51.7);\n"
).format(g=grp)
cmds.expression(name=expr_name, string=expr, alwaysEvaluate=True)

# 5. Lens configuration (35 mm)
cmds.cutKey(shape, attribute="focalLength", clear=True)
cmds.setAttr(shape + ".focalLength", FOCAL_LENGTH)

# 6. Verify Frustum & Visibility
def wpos(n):
    return om.MPoint(*cmds.xform(n, q=True, ws=True, t=True))

def vertex_bbox(nodes):
    xs = []
    for n in nodes:
        for s in cmds.listRelatives(n, shapes=True, noIntermediate=True, fullPath=True) or []:
            xs += cmds.xform(s + ".vtx[*]", q=True, ws=True, t=True)
    if not xs:
        return [0, 0, 0, 0, 0, 0]
    px, py, pz = xs[0::3], xs[1::3], xs[2::3]
    return [round(min(px), 1), round(min(py), 1), round(min(pz), 1), round(max(px), 1), round(max(py), 1), round(max(pz), 1)]

meshes = [m for m in cmds.ls("CHARLIE:*", type="mesh", noIntermediate=True)]
mesh_tr = list({cmds.listRelatives(m, parent=True)[0] for m in meshes})
W = cmds.getAttr("defaultResolution.width")
H = cmds.getAttr("defaultResolution.height")
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

all_inside = True
for f in (1, 18, 36, 54, 72):
    cmds.currentTime(f)
    res = {}
    for p in points:
        r = ndc(wpos(p))
        inside = (r is not None and abs(r[0]) <= 1.1 and abs(r[1]) <= 1.1)
        res[p.split(":")[-1]] = None if r is None else (round(r[0], 2), round(r[1], 2), inside)
        if p in ("CHARLIE:mixamorig:Head", "CHARLIE:mixamorig:Hips") and not inside:
            all_inside = False
    print("L| frustum f%02d focal %.1f" % (f, cmds.getAttr(shape + ".focalLength")), res)
    print("L| bbox f%02d Charlie meshes" % f, vertex_bbox(mesh_tr))

cmds.currentTime(1)
print("L| Frustum check result (Head & Hips inside):", all_inside)

# 7. Save Shot06.mb
cmds.file(save=True, type="mayaBinary")
print("L| saved", SHOT)
maya.standalone.uninitialize()
