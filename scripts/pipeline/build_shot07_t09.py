"""T09 Shot07 pipeline assembly (2026-10-01).

Shot 07: Insert shot of the video camera resting on an office desk in Backrooms.
Duration: 3 seconds = 72 frames (24 fps).
Animation: None (static prop shot).
Camera: Insert + medium high angle static, 40 mm lens, looking down at camcorder on desk.
Lighting: Light Preset A with dedicated insert key light (exposure 15.5, 6500K) on defaultLightSet.
"""
import math
import os
import shutil
import sys

import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.api.OpenMaya as om

SHOT = r"D:\projects\ProjectAnimation\scenes\Shots\Shot07.mb"
BACKUP_DIR = r"D:\projects\ProjectAnimation\scenes_backup_2026-10-01"
CAM_PROP = r"D:\projects\ProjectAnimation\scenes\Props\VideoCamera.mb"

# Desk tabletop position & camera placement
TABLE_TOP_Y = 73.06
CAMCORDER_POS = (-238.0, TABLE_TOP_Y, 185.0)
CAMCORDER_ROT = (0.0, -35.0, 0.0)

# Camera framing (medium high angle insert shot)
CAM_POS = (-202.0, 96.0, 222.0)
AIM_AT = (-238.0, TABLE_TOP_Y + 5.0, 185.0)  # center of camcorder body
FOCAL_LENGTH = 40.0  # mm
N_FRAMES = 72

os.makedirs(BACKUP_DIR, exist_ok=True)
bk = os.path.join(BACKUP_DIR, "Shot07_before_t09.mb")
if not os.path.exists(bk):
    shutil.copy2(SHOT, bk)
else:
    shutil.copy2(bk, SHOT)
print("L| backup", bk)

cmds.loadPlugin("mtoa", quiet=True)
cmds.file(SHOT, open=True, force=True, loadReferenceDepth="all")
cmds.playbackOptions(min=1, max=N_FRAMES, animationStartTime=1, animationEndTime=N_FRAMES)
cmds.currentUnit(time="film")

# 1. Clean up duplicate VideoCamera references if present
for ref_node in ("VCAMRN1", "VCAMRN2"):
    if cmds.objExists(ref_node):
        try:
            ref_file = cmds.referenceQuery(ref_node, filename=True)
            cmds.file(ref_file, removeReference=True)
            print("L| removed duplicate ref:", ref_node)
        except Exception as e:
            print("L| warn removing ref:", ref_node, e)

# Ensure primary VCAM reference exists
if not cmds.objExists("VCAM:VideoCamera_GRP"):
    print("L| adding VCAM reference...")
    cmds.file(CAM_PROP, reference=True, namespace="VCAM", mergeNamespacesOnClash=False)

# 2. Place VideoCamera prop on desk tabletop
if cmds.objExists("VCAM:VideoCamera_GRP"):
    cmds.setAttr("VCAM:VideoCamera_GRP.translate", *CAMCORDER_POS)
    cmds.setAttr("VCAM:VideoCamera_GRP.rotate", *CAMCORDER_ROT)
    cmds.setAttr("VCAM:VideoCamera_GRP.scale", 1, 1, 1)
    cmds.setAttr("VCAM:VideoCamera_GRP.visibility", 1)
    print("L| placed VCAM at", CAMCORDER_POS, "rot", CAMCORDER_ROT)
else:
    print("ERROR: VCAM:VideoCamera_GRP not found!")

# 3. Hide Charlie and Monster (Shot 07 is prop insert only)
for n in ("CHARLIE:GRP_Charlie_Placement", "CHARLIE:Charlie_Mixamo",
          "MONSTER:GRP_Monster_Mixamo", "MONSTER:Monster_Buff_Blobbell"):
    if cmds.objExists(n):
        cmds.setAttr(n + ".visibility", 0)

for m in cmds.ls("CHARLIE:*", "MONSTER:*", type="mesh"):
    tr = cmds.listRelatives(m, parent=True)
    if tr and cmds.objExists(tr[0]):
        try:
            cmds.setAttr(tr[0] + ".visibility", 0)
        except:
            pass

# 4. Camera setup: CAM_Shot07 & GRP_CAM_Shot07
cam = "CAM_Shot07"
if not cmds.objExists(cam):
    for c in cmds.ls(type="camera"):
        xf = (cmds.listRelatives(c, parent=True) or [None])[0]
        if xf and "Shot07" in xf:
            cam = xf
            break

shape = cmds.listRelatives(cam, shapes=True)[0]
grp = "GRP_CAM_Shot07"
if not cmds.objExists(grp):
    parent = cmds.listRelatives(cam, parent=True)
    if parent and "GRP" in parent[0]:
        grp = parent[0]
    else:
        grp = cmds.group(cam, name="GRP_CAM_Shot07")

# Clear any animation curves on camera and group
for node in (cam, grp):
    stray = cmds.listConnections(node, type="animCurve") or []
    if stray:
        cmds.delete(stray)

cmds.setAttr(cam + ".translate", 0, 0, 0)
cmds.setAttr(cam + ".rotate", 0, 0, 0)

dx = AIM_AT[0] - CAM_POS[0]
dy = AIM_AT[1] - CAM_POS[1]
dz = AIM_AT[2] - CAM_POS[2]
dist_xz = math.hypot(dx, dz)
yaw = math.degrees(math.atan2(-dx, -dz))
pitch = math.degrees(math.atan2(dy, dist_xz))

cmds.setAttr(grp + ".translate", CAM_POS[0], CAM_POS[1], CAM_POS[2])
cmds.setAttr(grp + ".rotate", pitch, yaw, 0.0)
print("L| camera pos", CAM_POS, "pitch", round(pitch, 2), "yaw", round(yaw, 2))

# Static shot (no shake noise)
for attr in ("baseTx", "baseTy", "baseTz", "baseRx", "baseRy", "baseRz", "shakeRot", "shakeTrans"):
    if cmds.attributeQuery(attr, node=grp, exists=True):
        cmds.deleteAttr(grp, at=attr)

if cmds.objExists("EXPR_Shot07_Handheld"):
    cmds.delete("EXPR_Shot07_Handheld")

# Lens focal length
cmds.cutKey(shape, attribute="focalLength", clear=True)
cmds.setAttr(shape + ".focalLength", FOCAL_LENGTH)

# Ensure CAM_Shot07 is the only renderable camera
for c in cmds.ls(type="camera"):
    try:
        cmds.setAttr(c + ".renderable", 1 if c == shape else 0)
    except:
        pass

# 5. Dedicated Desk Key Light for Insert Shot (Preset A)
light_name = "Shot07_Desk_KeyLight"
if not cmds.objExists(light_name):
    ls = cmds.shadingNode("aiAreaLight", asLight=True, name=light_name)
    lt = cmds.listRelatives(ls, parent=True)[0] if cmds.nodeType(ls) != "transform" else ls
else:
    ls = light_name if cmds.nodeType(light_name) == "aiAreaLight" else cmds.listRelatives(light_name, shapes=True)[0]
    lt = cmds.listRelatives(ls, parent=True)[0]

cmds.xform(lt, ws=True, t=[-220.0, 180.0, 195.0], ro=[-60, 30, 0], s=[140.0, 140.0, 1.0])
cmds.setAttr(ls + ".exposure", 15.5)
cmds.setAttr(ls + ".intensity", 50.0)
cmds.setAttr(ls + ".aiColorTemperature", 6500.0)
cmds.setAttr(ls + ".aiUseColorTemperature", 1)

# Ensure light is in defaultLightSet
light_sets = cmds.listSets(object=ls) or []
if "defaultLightSet" not in light_sets:
    cmds.sets(ls, add="defaultLightSet")
    print("L| added keylight to defaultLightSet")

# Arnold render options
o = "defaultArnoldRenderOptions"
if cmds.objExists(o):
    cmds.setAttr(o + ".skipLicenseCheck", 0)
    cmds.setAttr(o + ".lightLinking", 0)
    cmds.setAttr(o + ".shadowLinking", 0)
    cmds.setAttr(o + ".renderDevice", 0)

master = "ENV:LIGHT_MASTER"
if cmds.objExists(master) and cmds.attributeQuery("exposure", node=master, exists=True):
    cmds.setAttr(master + ".exposure", 13.0)

# Verify Frustum of VideoCamera
def wpos(n):
    return om.MPoint(*cmds.xform(n, q=True, ws=True, t=True))

W = cmds.getAttr("defaultResolution.width")
H = cmds.getAttr("defaultResolution.height")
aspect = W / float(H)

def ndc(point):
    focal = cmds.getAttr(shape + ".focalLength")
    h = cmds.getAttr(shape + ".horizontalFilmAperture") * 25.4 / 2.0
    m = om.MMatrix(cmds.xform(cam, q=True, ws=True, m=True))
    pc = point * m.inverse()
    if pc.z >= 0:
        return None
    return (pc.x / -pc.z) * focal / h, (pc.y / -pc.z) * focal / (h / aspect)

cam_bb = cmds.exactWorldBoundingBox("VCAM:VideoCamera_GRP")
print("L| VCAM bbox:", [round(v, 2) for v in cam_bb])
cam_center = om.MPoint((cam_bb[0] + cam_bb[3])/2.0, (cam_bb[1] + cam_bb[4])/2.0, (cam_bb[2] + cam_bb[5])/2.0)
cam_ndc = ndc(cam_center)
print("L| VCAM center NDC:", cam_ndc)

# Save Shot07.mb
cmds.file(save=True, type="mayaBinary")
print("L| saved", SHOT)
maya.standalone.uninitialize()
