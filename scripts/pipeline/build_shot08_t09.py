"""T09 Shot08 pipeline assembly (2026-10-01).

Shot 08: Charlie bends/reaches and picks up the video camera from the office desk (same desk and prop position as Shot 07).
Duration: 2 seconds = 48 frames (24 fps).
Animation: Picking_Up_Object.fbx, source frames 0-48 (hand reaches f0-24, holds f24-32, pulls back f32-48) at about 1:1 speed.
        The tail of the clip (hand dropping beside the hips) is cut: the chibi belly hides the camcorder from the POV camera there.
Camera: POV eye level (Tawan chose option A, 2026-10-01): position follows Charlie's eye point (head joint collapsed), aim tracks the camcorder, handheld shake baked into the camera keys. 28 mm lens.
Lighting: Preset A (exposure 13) + two steady fill lights on the desk (overhead panel + under-desktop lamp), bright desk per Tawan 2026-10-01.
Rerunnable: restores scenes_backup_2026-10-01/Shot08_before_t09.mb before every run.
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

SHOT = r"D:\projects\ProjectAnimation\scenes\Shots\Shot08.mb"
BACKUP_DIR = r"D:\projects\ProjectAnimation\scenes_backup_2026-10-01"
CLIP = r"D:\projects\ProjectAnimation\raw_assets\mixamo\charlie\Picking_Up_Object.fbx"
CAM_PROP = r"D:\projects\ProjectAnimation\scenes\Props\VideoCamera.mb"

N_FRAMES = 48
SRC_FIRST, SRC_LAST = 0, 48
TIME_SCALE = N_FRAMES / float(SRC_LAST - SRC_FIRST + 1)      # 48 / 49
GRAB_SRC = 28                                                  # hand holds at its furthest reach in source frames 24-32
GRAB_DST = int(round(1 + (GRAB_SRC - SRC_FIRST) * TIME_SCALE))
HAND = "CHARLIE:mixamorig:RightHand"
FLOOR_Y = -12.0

TABLE_TOP_Y = 73.06                                            # same prop pose as Shot 07
CAMCORDER_POS = (-238.0, TABLE_TOP_Y, 185.0)
CAMCORDER_ROT = (0.0, -35.0, 0.0)
CHAR_YAW = -90.0                                               # Charlie faces -X (towards the desk); Mixamo rigs face +Z at yaw 0

FOCAL = 28.0
NEAR_CLIP = 15.0   # the collapsed head leaves the hoodie 9.6-14 units from the camera in frames 38-48 (diag_shot08_nearclip.py); nothing else in frame is nearer than 15
CAM_FORWARD = 4.0            # camera sits this far ahead of the eye point (head is collapsed, see step 6)
SHELF_LIP_X = -217.3         # front edge of the desk unit (ray-cast 2026-10-01); the camcorder rests on the lower shelf (y 73.1) under the desktop (y 108.9-111.5)
AIM_UP = 6.0                 # aim above the shelf camcorder: -2 burned Charlie's lap white along the bottom (19% above 240), +9 shows more scalloped plate on top; 6 with the plates hidden
SHAKE_ROT, SHAKE_TRANS = 0.6, 0.6
SHELF_TOP_Y = 73.1
LIFT_START, LIFT_END = GRAB_DST + 2, GRAB_DST + 10   # camcorder rests on the shelf until LIFT_START, is at the held pose by LIFT_END
HOLD_DIST = 30.0       # held pose: this far in front of the camera (along Charlie's facing)
HOLD_Y_CANDIDATES = (86.0, 82.0, 78.0)   # highest y with a clear line of sight under the valance
HOLD_WRIST_RIGHT, HOLD_WRIST_DOWN = 8.0, 7.0   # while lifted the wrist sits lower-right of the camcorder (screen space), so the forearm no longer runs along the view axis and hides it
HOLD_AIM_UP = -3.0      # aim this far above (negative = below) the held camcorder; below keeps the valance edge out of the top of the frame
CAVITY_ALBEDO = (0.045, 0.042, 0.035)   # pale warm grey for the cavity faces (0.55 burned 80%+ of the frame to white; the original texels are near black)
VALANCE_RAY = 22.0                   # camera rays hide desk faces in y 85-111 within this distance of the lens (the back wall is ~37 away)
VALANCE_X = (-222.0, -212.0)         # x window of the desk front panel / valance
CAVITY_X_MAX = -228.0                # only count hits deeper than the front valance (x -217) so the valance keeps its own texture
FILL_OVERHEAD_EXP, FILL_LAMP_EXP = 12.0, 11.5   # exposure of the overhead panel and of the under-desktop lamp (tuned with test frames 1, 22, 38, 44, 48)

os.makedirs(BACKUP_DIR, exist_ok=True)
bk = os.path.join(BACKUP_DIR, "Shot08_before_t09.mb")
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


def flat(m):
    return [m.getElement(r, c) for r in range(4) for c in range(4)]


def wpos(n):
    return om.MPoint(*cmds.xform(n, q=True, ws=True, t=True))


def bbox_center(n):
    b = cmds.exactWorldBoundingBox(n)
    return om.MPoint((b[0] + b[3]) / 2.0, (b[1] + b[4]) / 2.0, (b[2] + b[5]) / 2.0)


def noise(f, seed):
    """cheap deterministic hand-shake noise in about [-1, 1]"""
    return (0.5 * math.sin(2 * math.pi * f / 17.0 + seed) + 0.3 * math.sin(2 * math.pi * f / 7.3 + 2.1 * seed)
            + 0.2 * math.sin(2 * math.pi * f / 3.1 + 3.7 * seed))


# 1. Remove the duplicate VideoCamera references left by earlier runs ({1}, {2}); keep the primary VCAM one
for ref in cmds.file(q=True, reference=True) or []:
    if ref.endswith("}") and "VideoCamera.mb" in ref:
        try:
            cmds.file(ref, removeReference=True)
            print("L| removed duplicate ref", ref)
        except Exception as e:
            print("L| WARN could not remove", ref, e)
if not cmds.objExists("VCAM:VideoCamera_GRP"):
    cmds.file(CAM_PROP, reference=True, namespace="VCAM", mergeNamespacesOnClash=False)
VC = "VCAM:VideoCamera_GRP"
for ns in ("VCAM1", "VCAM2"):
    if cmds.objExists(ns + ":VideoCamera_GRP"):
        cmds.setAttr(ns + ":VideoCamera_GRP.visibility", 0)

# 2. Bake the clip onto Charlie
info = bake_clip(CLIP, rig_ns="CHARLIE:", src_first=SRC_FIRST, src_last=SRC_LAST, dst_first=1, time_scale=TIME_SCALE)
cmds.playbackOptions(min=1, max=N_FRAMES, animationStartTime=1, animationEndTime=N_FRAMES)
cmds.cutKey("CHARLIE:*", time=(N_FRAMES + 1, 400), clear=True)
assert info["frames"] == N_FRAMES and not info["missing_dst_joints"], info
# The clip's second half (hand pulled to the torso, head leaning over) is not used any more: Charlie holds the camcorder up from LIFT_END to the last
# frame. Freezing the body pose also keeps the arm IK target reachable (with a moving torso the wrist drifted off the camcorder at frames 44-48).
for _j in cmds.ls("CHARLIE:mixamorig:*", type="joint"):
    for _a in ("translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"):
        if cmds.listConnections(_j + "." + _a, s=True, d=False):
            _v = cmds.getAttr(_j + "." + _a, time=LIFT_END)
            cmds.cutKey(_j, attribute=_a, time=(LIFT_END + 1, N_FRAMES), clear=True)
            for _f in range(LIFT_END + 1, N_FRAMES + 1):
                cmds.setKeyframe(_j, attribute=_a, time=_f, value=_v)
print("L| Charlie pose frozen from frame", LIFT_END)
print("L| grab frame (dst)", GRAB_DST)

# 3. Camcorder on the desk (Shot 07 pose), Monster hidden
cmds.setAttr(VC + ".translate", *CAMCORDER_POS)
cmds.setAttr(VC + ".rotate", *CAMCORDER_ROT)
cmds.setAttr(VC + ".scale", 1, 1, 1)
cmds.setAttr(VC + ".visibility", 1)
for n in ("MONSTER:GRP_Monster_Mixamo", "MONSTER:Monster_Buff_Blobbell"):
    if cmds.objExists(n):
        cmds.setAttr(n + ".visibility", 0)
for a in ("CHARLIE:GRP_Charlie_Placement", "CHARLIE:Charlie_Mixamo"):
    if cmds.objExists(a):
        cmds.setAttr(a + ".visibility", 1)
desk_center = bbox_center(VC)
desk_matrix = mat(VC)
print("L| camcorder desk center", [round(desk_center[i], 2) for i in range(3)])

# 4. Place Charlie so the right wrist meets the camcorder at the grab frame
PL = "CHARLIE:GRP_Charlie_Placement"
cmds.setAttr(PL + ".rotate", 0, CHAR_YAW, 0)
cmds.setAttr(PL + ".translate", 0, FLOOR_Y, 0)
cmds.currentTime(GRAB_DST)
h = wpos(HAND)
tx, ty, tz = (desk_center[0] - h[0], FLOOR_Y + (desk_center[1] - h[1]), desk_center[2] - h[2])
cmds.setAttr(PL + ".translate", tx, ty, tz)
h = wpos(HAND)
print("L| Charlie placement", [round(v, 2) for v in (tx, ty, tz)], "lift above floor", round(ty - FLOOR_Y, 2),
      "wrist at grab", [round(h[i], 2) for i in range(3)])
# ponytail: the Mixamo clip reaches ~55 units above the floor but the desk top is 85 units up; the body is lifted instead of re-posing the arm.
# Fine while the feet stay out of frame (checked below); replace with an IK reach if a later shot shows the feet.

# 5. The camcorder stays on the shelf for now (all frames keyed at the desk pose); step 6b lifts it after the grab.
cmds.currentTime(GRAB_DST)
offset = desk_matrix * mat(HAND).inverse()          # camcorder = offset * wrist  ->  wrist = offset.inverse() * camcorder
for f in range(1, N_FRAMES + 1):
    cmds.currentTime(f)
    cmds.xform(VC, ws=True, m=flat(desk_matrix))
    cmds.setKeyframe(VC, attribute=["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"], time=f)

# 6. POV camera
cam, grp = "CAM_Shot08", "GRP_CAM_Shot08"
shape = cmds.listRelatives(cam, shapes=True)[0]
if not cmds.objExists(grp):
    grp = cmds.group(cam, name=grp)
stray = (cmds.listConnections(cam, type="animCurve") or []) + (cmds.listConnections(grp, type="animCurve") or [])
if stray:
    cmds.delete(stray)
for attr in ("baseTx", "baseTy", "baseTz", "baseRx", "baseRy", "baseRz", "shakeRot", "shakeTrans"):
    if cmds.attributeQuery(attr, node=grp, exists=True):
        cmds.deleteAttr(grp, at=attr)
if cmds.objExists("EXPR_Shot08_Handheld"):
    cmds.delete("EXPR_Shot08_Handheld")
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

forward = om.MVector(0, 0, 1) * om.MTransformationMatrix(mat(PL)).asMatrix()   # Charlie facing (rotation only matters)
forward = om.MVector(forward.x, 0, forward.z).normal()
print("L| Charlie facing", [round(forward[i], 3) for i in range(3)])

# Eye positions come from the head joints, so record them for every frame BEFORE the head is collapsed.
eyes = {}
for f in range(1, N_FRAMES + 1):
    cmds.currentTime(f)
    head, top = wpos("CHARLIE:mixamorig:Head"), wpos("CHARLIE:mixamorig:HeadTop_End")
    eyes[f] = om.MPoint((head.x + top.x) / 2.0, (head.y + top.y) / 2.0, (head.z + top.z) / 2.0)

# First-person trick: Charlie's chibi head is ~30 units in radius, so a camera outside the face sits above the hand. Collapse the Head joint
# (skinned head vertices fold into one point) and hide the eye meshes, then the camera can sit at eye height.
# ponytail: neck vertices that are partly weighted to Head fold into a small cone under the camera; check the test frames and
# repaint weights (or use a head-less duplicate mesh) only if the cone shows in frame.
# Late in the clip the head leans over the camcorder (src 44-48) and drags the eye-following camera down onto Charlie's torso: the picture jumps
# (frame diff 58.7 at frame 48) and the sweater/skin burn to white (22% above 240). Let the camera position stop following the head from frame 43
# and be fully still by frame 46; the aim still tracks the camcorder. Only frames 44-48 change.
HOLD_FROM, HOLD_FULL = 43, 46
for _f in range(HOLD_FROM + 1, N_FRAMES + 1):
    _w = min(1.0, (_f - HOLD_FROM) / float(HOLD_FULL - HOLD_FROM))
    _w = _w * _w * (3.0 - 2.0 * _w)
    eyes[_f] = eyes[HOLD_FROM] + (eyes[_f] - eyes[HOLD_FROM]) * (1.0 - _w)
print("L| camera position held from frame", HOLD_FROM, "to", HOLD_FULL)

HEAD = "CHARLIE:mixamorig:Head"
for ax in "XYZ":
    cmds.setAttr("%s.scale%s" % (HEAD, ax), 0.001)
for eye_mesh in ("CHARLIE:bevelPolygon1", "CHARLIE:bevelPolygon2"):
    if cmds.objExists(eye_mesh):
        cmds.setAttr(eye_mesh + ".visibility", 0)
        print("L| hid", eye_mesh, [round(v, 1) for v in cmds.exactWorldBoundingBox(eye_mesh)])

env_fns = []
_sel = om.MSelectionList()
for _s in cmds.ls("ENV:*", type="mesh", noIntermediate=True, long=True):
    _sel.clear()
    _sel.add(_s)
    env_fns.append(om.MFnMesh(_sel.getDagPath(0)))


def blocked(p0, p1):
    d = p1 - p0
    dist = d.length()
    d.normalize()
    for fn in env_fns:
        r = fn.allIntersections(om.MFloatPoint(p0.x, p0.y, p0.z), om.MFloatVector(d.x, d.y, d.z), om.MSpace.kWorld, dist - 1.0, False)
        if r and r[0] and len(r[0]):
            return True
    return False


# The eye is above the desktop lip, so the line to the camcorder (on the shelf under it) hits the slab. The head is gone, so the camera may
# sit lower than the eye point: take the smallest drop that gives a clear line of sight over the frames where the camcorder is under the desk.
LOS_FRAMES = [1, 5, 10, 15, GRAB_DST, 26, 30]
targets = {}
for f in LOS_FRAMES:
    cmds.currentTime(f)
    targets[f] = bbox_center(VC)
drop = None
for d_try in range(0, 81, 4):
    ok = all(not blocked(eyes[f] + forward * CAM_FORWARD - om.MVector(0, d_try, 0), targets[f]) for f in LOS_FRAMES)
    if ok:
        drop = float(d_try)
        break
if drop is None:
    drop = 80.0
    print("L| WARN no clear line of sight found, using max drop")
print("L| camera drop below eye point", drop, "(0 = eye height)")


def hold_point(f, y):
    """where the lifted camcorder is at frame f: HOLD_DIST in front of the (unshaken) camera, at height y"""
    p = eyes[f] + forward * CAM_FORWARD - om.MVector(0, drop, 0)
    return om.MPoint(p.x + forward.x * HOLD_DIST, y, p.z + forward.z * HOLD_DIST)


hold_y, _clear = HOLD_Y_CANDIDATES[-1], False
for _y in HOLD_Y_CANDIDATES:
    _p0 = eyes[LIFT_END] + forward * CAM_FORWARD - om.MVector(0, drop, 0)
    if not blocked(om.MPoint(_p0.x, _p0.y, _p0.z), hold_point(LIFT_END, _y)):
        hold_y, _clear = _y, True
        break
print("L| held camcorder height", hold_y, "(clear line of sight)" if _clear else "(WARN: blocked at the lowest candidate)")

char_meshes = [m for m in sorted({cmds.listRelatives(x, parent=True)[0] for x in cmds.ls("CHARLIE:*", type="mesh", noIntermediate=True)})
               if cmds.getAttr(m + ".visibility")]
for f in range(1, N_FRAMES + 1):
    cmds.currentTime(f)
    pos = eyes[f] + forward * CAM_FORWARD - om.MVector(0, drop, 0)
    desk_target = om.MPoint(desk_center.x, desk_center.y + AIM_UP, desk_center.z)
    if f <= GRAB_DST:
        target = desk_target
    else:
        w = min(1.0, (f - GRAB_DST) / float(LIFT_END - GRAB_DST))
        w = w * w * (3.0 - 2.0 * w)
        hp = hold_point(f, hold_y)
        target = desk_target + (om.MPoint(hp.x, hp.y + HOLD_AIM_UP, hp.z) - desk_target) * w
    dx, dy, dz = target.x - pos.x, target.y - pos.y, target.z - pos.z
    yaw = math.degrees(math.atan2(-dx, -dz))
    pitch = math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    t = (pos.x + SHAKE_TRANS * noise(f, 1.3), pos.y + SHAKE_TRANS * noise(f, 4.1), pos.z + SHAKE_TRANS * 0.6 * noise(f, 7.7))
    r = (pitch + SHAKE_ROT * noise(f, 2.9), yaw + SHAKE_ROT * noise(f, 5.3), SHAKE_ROT * 0.5 * noise(f, 8.9))
    for a, v in zip(("translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"), t + r):
        cmds.setKeyframe(cam, attribute=a, time=f, value=v)
cmds.filterCurve(cam + ".rotateX", cam + ".rotateY", cam + ".rotateZ", filter="euler")

# 6b. Tawan 2026-10-02: grab the camcorder and lift it in front of the head, not pull it to the torso. After LIFT_START the camcorder rises from the
# shelf to HOLD_DIST in front of the camera (it stays under the desktop, so it never crosses the valance) and the right arm follows it with IK.
desk_t = om.MTransformationMatrix(desk_matrix).translation(om.MSpace.kWorld)
for f in range(LIFT_START, N_FRAMES + 1):
    s_ = min(1.0, (f - LIFT_START) / float(LIFT_END - LIFT_START))
    s_ = s_ * s_ * (3.0 - 2.0 * s_)
    _hp = hold_point(f, hold_y)
    hold = om.MVector(_hp.x, _hp.y, _hp.z)
    pos_f = om.MVector(desk_t.x, desk_t.y, desk_t.z) + (hold - om.MVector(desk_t.x, desk_t.y, desk_t.z)) * s_
    tm = om.MTransformationMatrix(desk_matrix)
    tm.setTranslation(pos_f, om.MSpace.kWorld)
    cmds.currentTime(f)
    cmds.xform(VC, ws=True, m=flat(tm.asMatrix()))
    cmds.setKeyframe(VC, attribute=["translateX", "translateY", "translateZ"], time=f)
cmds.filterCurve(VC + ".rotateX", VC + ".rotateY", VC + ".rotateZ", filter="euler")

# right arm IK: the handle follows the wrist position that keeps the camcorder in the hand (wrist = offset.inverse() * camcorder)
ARM, HAND_J = "CHARLIE:mixamorig:RightArm", HAND
cmds.currentTime(GRAB_DST)
if cmds.objExists("IK_Shot08_RightArm"):
    cmds.delete("IK_Shot08_RightArm")
ikh, eff = cmds.ikHandle(startJoint=ARM, endEffector=HAND_J, solver="ikRPsolver", name="IK_Shot08_RightArm")
cmds.setAttr(ikh + ".visibility", 0)
for f in range(GRAB_DST, N_FRAMES + 1):
    cmds.currentTime(f)
    wrist = om.MTransformationMatrix(offset.inverse() * mat(VC)).translation(om.MSpace.kWorld)
    _s = min(1.0, max(0.0, (f - LIFT_START) / float(LIFT_END - LIFT_START)))
    _s = _s * _s * (3.0 - 2.0 * _s)
    _right = forward ^ om.MVector(0, 1, 0)
    wrist = om.MVector(wrist.x, wrist.y, wrist.z) + _right * (HOLD_WRIST_RIGHT * _s) + om.MVector(0, -HOLD_WRIST_DOWN * _s, 0)
    for a_, v_ in zip(("translateX", "translateY", "translateZ"), (wrist.x, wrist.y, wrist.z)):
        cmds.setKeyframe(ikh, attribute=a_, time=f, value=v_)
cmds.setKeyframe(ikh, attribute="ikBlend", time=GRAB_DST - 1, value=0.0)
cmds.setKeyframe(ikh, attribute="ikBlend", time=GRAB_DST, value=1.0)
cmds.keyTangent(ikh, attribute="ikBlend", inTangentType="linear", outTangentType="linear")
print("L| arm IK", ikh, "on", ARM, "->", HAND_J, "from frame", GRAB_DST)

# nearest visible Charlie vertex to the camera must be farther than the near clip plane
worst = 1e9
for f in (1, 8, 15, GRAB_DST, 30, 38, 44, N_FRAMES):
    cmds.currentTime(f)
    cp = wpos(cam)
    for mnode in char_meshes:
        v = cmds.xform(mnode + ".vtx[*]", q=True, ws=True, t=True)
        worst = min(worst, min(cp.distanceTo(om.MPoint(v[i], v[i + 1], v[i + 2])) for i in range(0, len(v), 3)))
print("L| nearest Charlie vertex to camera over checked frames:", round(worst, 2), "(near clip %.1f)" % NEAR_CLIP)

# 7. Desk lighting. The desk room is lit by almost nothing from the ceiling panels, and the camcorder sits on a shelf under the desktop, so
# the desk read as black. Tawan (2026-10-01): the desk must be bright, it is inside the Backrooms. Two steady panels (no keyed exposure): one overhead like a
# ceiling panel and a small lamp under the desktop above the camcorder. Low flank fills were tried and removed: they blew out the desk fascia,
# Charlie's hand and belly (17-28% of pixels above 240) and made frames render in 143 s.
def make_area(name, pos, aim, size, exposure):
    shape_name = name
    if cmds.objExists(shape_name):
        cmds.delete(shape_name)
    shp = cmds.shadingNode("aiAreaLight", asLight=True, name=name)
    xf = cmds.listRelatives(shp, parent=True)[0] if cmds.nodeType(shp) != "transform" else shp
    dx, dy, dz = aim[0] - pos[0], aim[1] - pos[1], aim[2] - pos[2]
    yaw = math.degrees(math.atan2(-dx, -dz))
    pitch = math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    cmds.xform(xf, ws=True, t=list(pos), ro=[pitch, yaw, 0.0], s=[size[0], size[1], 1.0])
    cmds.setAttr(shp + ".exposure", exposure)
    cmds.setAttr(shp + ".intensity", 50.0)
    cmds.setAttr(shp + ".aiUseColorTemperature", 1)
    cmds.setAttr(shp + ".aiColorTemperature", FILL_KELVIN)
    if "defaultLightSet" not in (cmds.listSets(object=shp) or []):
        cmds.sets(shp, add="defaultLightSet")
    # the panels must light the set without showing up as white quads in the picture; shadingNode returns the transform, the shape has our name
    for a_name in ("aiCamera", "primaryVisibility"):
        if cmds.attributeQuery(a_name, node=name, exists=True):
            cmds.setAttr(name + "." + a_name, 0)
            print("L| light", name, a_name, "= 0")
    return shp


FILL_KELVIN = 6500.0
make_area("Shot08_Fill_Overhead", (-215.0, 262.0, 190.0), (-215.0, 0.0, 190.0), (130.0, 130.0), FILL_OVERHEAD_EXP)
# small panel under the desktop right above the camcorder (31 units above the shelf): the shelf top is lit straight on instead of at a grazing angle
make_area("Shot08_Fill_UnderDeskLamp", (CAMCORDER_POS[0] + 6.0, 104.0, CAMCORDER_POS[2]), (CAMCORDER_POS[0] + 6.0, 0.0, CAMCORDER_POS[2]), (35.0, 35.0), FILL_LAMP_EXP)
# once the camcorder is out of the cavity the lamp is only 28 units from Charlie's belly and burns it to white (26% of pixels above 240 at frame 48): fade it 1.8 stops while the camcorder is lifted (-1.0 left 21-22% of the pixels above 240, -3.0 left the frame at mean 30-38) (it is then 12 units under the lamp) (2.5 left frame 44 at mean 27-39 once the cavity faces were lightened)
cmds.cutKey("Shot08_Fill_UnderDeskLamp", attribute="exposure", clear=True)
for kf, kv in ((1, FILL_LAMP_EXP), (GRAB_DST, FILL_LAMP_EXP), (LIFT_END, FILL_LAMP_EXP - 1.8), (N_FRAMES, FILL_LAMP_EXP - 1.8)):
    cmds.setKeyframe("Shot08_Fill_UnderDeskLamp", attribute="exposure", time=kf, value=kv)
cmds.keyTangent("Shot08_Fill_UnderDeskLamp", attribute="exposure", inTangentType="linear", outTangentType="linear")
# 8. Lighter surfaces inside the cavity under the desktop (Tawan 2026-10-01: Shot 08 must be about as bright as Shot 09, mean 125).
# Raising the furniture texture gain did nothing (the shelf and walls are near-black texels, test frames 66.6/74.6/27.6 vs 62.4/74.0/27.4), and more light
# burns the hand and belly. So the faces that make up the cavity get a pale warm-grey shader in THIS shot file only (reference edit, env file untouched).
# Faces are found with rays: shelf top (down), back wall and side walls (horizontal), cavity ceiling = underside of the desktop (up).
_desk_shape = [s for s in cmds.ls("ENV:Prop_OfficeDesk_and_Drawers", long=True)][0]
_desk_shape = cmds.listRelatives(_desk_shape, shapes=True, fullPath=True, noIntermediate=True)[0]
_sel = om.MSelectionList()
_sel.add(_desk_shape)
_fn = om.MFnMesh(_sel.getDagPath(0))
_cx, _cy, _cz = CAMCORDER_POS
_faces = set()


def _cast(origin, direction, y_lo, y_hi, max_dist, first_only, x_max=None):
    r = _fn.allIntersections(om.MFloatPoint(*origin), om.MFloatVector(*direction), om.MSpace.kWorld, max_dist, False)
    if not r or not len(r[0]):
        return
    hits = sorted(zip(r[1], r[2], [p.y for p in r[0]], [p.x for p in r[0]]))
    for _t, face, y, x in hits:
        if x_max is not None and x > x_max:
            continue
        if y_lo <= y <= y_hi:
            _faces.add(face)
            if first_only:
                break


for _x in range(-262, -214, 4):
    for _z in range(int(_cz) - 40, int(_cz) + 41, 4):
        _cast((_x, 100.0, _z), (0, -1, 0), SHELF_TOP_Y - 3.0, SHELF_TOP_Y + 3.0, 60.0, True)          # shelf top
        _cast((_x, SHELF_TOP_Y + 3.0, _z), (0, 1, 0), 105.0, 112.0, 60.0, True)                       # cavity ceiling
for _y in range(int(SHELF_TOP_Y) + 4, 108, 4):
    for _z in range(int(_cz) - 40, int(_cz) + 41, 4):
        _cast((_cx + 20.0, _y, _z), (-1, 0, 0), _y - 1.0, _y + 1.0, 120.0, True, CAVITY_X_MAX)                      # back wall
    for _x in range(-262, -226, 6):
        _cast((_x, _y, _cz), (0, 0, 1), _y - 1.0, _y + 1.0, 80.0, True)                                # side walls
        _cast((_x, _y, _cz), (0, 0, -1), _y - 1.0, _y + 1.0, 80.0, True)
print("L| cavity faces found:", len(_faces))
if _faces:
    _mat = cmds.shadingNode("aiStandardSurface", asShader=True, name="Shot08_CavityLight_M")
    cmds.setAttr(_mat + ".baseColor", CAVITY_ALBEDO[0], CAVITY_ALBEDO[1], CAVITY_ALBEDO[2], type="double3")
    cmds.setAttr(_mat + ".specular", 0.1)
    _sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="Shot08_CavityLight_SG")
    cmds.connectAttr(_mat + ".outColor", _sg + ".surfaceShader", force=True)
    try:
        cmds.sets([_desk_shape + ".f[%d]" % f for f in sorted(_faces)], forceElement=_sg)
        print("L| cavity shader assigned to", len(_faces), "faces, albedo", CAVITY_ALBEDO)
    except Exception as e:
        print("L| WARN could not assign the cavity shader:", e)

# 9. Hide the desk's front valance in this shot (Tawan 2026-10-02: "ยังเห็นผมของ Charlie"). The brown-orange scalloped band hanging across the top of the
# frame in frames 1-34 is the wood valance of the desk front (x about -217, y 92-109), not hair: the camera sits 4 units behind it. Its faces get a fully
# transparent shader in THIS shot file only (reference edit, env untouched); transparent for camera and shadow rays.
_val = set()
for _y in range(78, 109, 3):
    for _z in range(int(_cz) - 70, int(_cz) + 71, 3):
        _r = _fn.allIntersections(om.MFloatPoint(-190.0, _y, _z), om.MFloatVector(-1, 0, 0), om.MSpace.kWorld, 60.0, False)
        if not _r or not len(_r[0]):
            continue
        for _t, _face, _px, _py in sorted(zip(_r[1], _r[2], [p.x for p in _r[0]], [p.y for p in _r[0]])):
            if VALANCE_X[0] <= _px <= VALANCE_X[1]:
                _val.add(_face)
                break
# The valance has several layers (front, thickness, scallop edges) and some sit outside the x window above, so also hide every desk face that is the
# thing hit in front of the lens (all layers): rays from the real camera through a grid of the frame at sample frames, within VALANCE_RAY units, y 85-107.5
# (the desktop itself starts at y 108.9 and the cavity ceiling is handled above).
_asp = cmds.getAttr("defaultResolution.width") / float(cmds.getAttr("defaultResolution.height"))
_hh = cmds.getAttr(shape + ".horizontalFilmAperture") * 25.4 / 2.0
_fl = cmds.getAttr(shape + ".focalLength")
_n_region = len(_val)
for _f in (1, 8, 16, 24, 28, 32, 36, 42, 48):
    cmds.currentTime(_f)
    _m = om.MMatrix(cmds.xform(cam, q=True, ws=True, m=True))
    _o = wpos(cam)
    for _ix in range(-8, 9):
        for _iy in range(-5, 6):
            _dx, _dy, _dz = (_ix / 8.0) * _hh / _fl, (_iy / 5.0) * (_hh / _asp) / _fl, -1.0
            _d = om.MVector(_dx * _m.getElement(0, 0) + _dy * _m.getElement(1, 0) + _dz * _m.getElement(2, 0),
                            _dx * _m.getElement(0, 1) + _dy * _m.getElement(1, 1) + _dz * _m.getElement(2, 1),
                            _dx * _m.getElement(0, 2) + _dy * _m.getElement(1, 2) + _dz * _m.getElement(2, 2)).normal()
            _r = _fn.allIntersections(om.MFloatPoint(_o.x, _o.y, _o.z), om.MFloatVector(_d.x, _d.y, _d.z), om.MSpace.kWorld, VALANCE_RAY, False)
            if not _r or not len(_r[0]):
                continue
            for _t, _face, _py in sorted(zip(_r[1], _r[2], [p.y for p in _r[0]])):
                if 85.0 <= _py <= 111.0:
                    _val.add(_face)       # every layer of the valance/plates in the band, not only the first (the inner layer read as grey hair)
                else:
                    break
print("L| valance faces from camera rays:", len(_val) - _n_region, "(region pass:", _n_region, ")")
cmds.currentTime(1)
print("L| valance faces found:", len(_val))
if _val:
    _vm = cmds.shadingNode("aiStandardSurface", asShader=True, name="Shot08_ValanceHidden_M")
    cmds.setAttr(_vm + ".opacity", 0.0, 0.0, 0.0, type="double3")
    _vsg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="Shot08_ValanceHidden_SG")
    cmds.connectAttr(_vm + ".outColor", _vsg + ".surfaceShader", force=True)
    try:
        cmds.sets([_desk_shape + ".f[%d]" % f for f in sorted(_val)], forceElement=_vsg)
        print("L| valance hidden on", len(_val), "faces")
    except Exception as e:
        print("L| WARN could not hide the valance:", e)

o = "defaultArnoldRenderOptions"
if cmds.objExists(o):
    cmds.setAttr(o + ".skipLicenseCheck", 0)
    cmds.setAttr(o + ".lightLinking", 0)
    cmds.setAttr(o + ".shadowLinking", 0)
    cmds.setAttr(o + ".renderDevice", 0)
if cmds.objExists("ENV:LIGHT_MASTER") and cmds.attributeQuery("exposure", node="ENV:LIGHT_MASTER", exists=True):
    cmds.setAttr("ENV:LIGHT_MASTER.exposure", 13.0)

# 8. Frustum checks: camcorder, wrist, feet (feet must stay out of frame because the body is lifted)
W, H = cmds.getAttr("defaultResolution.width"), cmds.getAttr("defaultResolution.height")
aspect = W / float(H)


def ndc(point):
    focal = cmds.getAttr(shape + ".focalLength")
    hh = cmds.getAttr(shape + ".horizontalFilmAperture") * 25.4 / 2.0
    pc = point * mat(cam).inverse()
    if pc.z >= 0:
        return None
    return (pc.x / -pc.z) * focal / hh, (pc.y / -pc.z) * focal / (hh / aspect)


def inside(r):
    return r is not None and abs(r[0]) <= 1.0 and abs(r[1]) <= 1.0


cam_in, feet_visible = True, []
for f in (1, 8, 15, GRAB_DST, 30, 38, 44, N_FRAMES):
    cmds.currentTime(f)
    rc = ndc(bbox_center(VC))
    rh = ndc(wpos(HAND))
    feet = {n: ndc(wpos("CHARLIE:mixamorig:" + n)) for n in ("LeftFoot", "RightFoot")}
    if not inside(rc):
        cam_in = False
    feet_visible += [n for n, r in feet.items() if inside(r)]
    fmt = lambda r: None if r is None else (round(r[0], 2), round(r[1], 2))
    print("L| frustum f%02d camcorder %s wrist %s feet %s" % (f, fmt(rc), fmt(rh), {k: fmt(v) for k, v in feet.items()}))
print("L| camcorder inside frame at all checked frames:", cam_in)
print("L| feet visible in frame:", sorted(set(feet_visible)) or "none")

cmds.currentTime(1)
cmds.file(save=True, type="mayaBinary")
print("L| saved", SHOT)
maya.standalone.uninitialize()
