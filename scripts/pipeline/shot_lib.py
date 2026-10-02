"""Shared helpers for the Shot 10-14 builders (2026-10-02). Used inside mayapy.

Corridor facts (ray-cast, diag_env_corridor.py): main corridor runs along X, walls at z about 343 and 707, floor y -12, ceiling y 274.7,
ceiling panels on z 525 at x -1478, -1024, -570, -40, 564. Panels 02/03 (x -1478/-1024) carry the Preset B flicker expression.
Rigs face +Z at rotateY 0; facing direction for yaw t is (sin t, 0, cos t).
"""
import math
import os
import shutil
import sys

import maya.cmds as cmds
import maya.api.OpenMaya as om

sys.path.insert(0, r"D:\projects\ProjectAnimation\scripts\pipeline")
from bake_mixamo_clip import bake_clip  # noqa: E402

ROOT = r"D:\projects\ProjectAnimation"
BACKUP_DIR = os.path.join(ROOT, "scenes_backup_2026-10-02")
CLIPS = os.path.join(ROOT, "raw_assets", "mixamo")
FLOOR_Y = -12.0
PRESET_B_EXPOSURE = 13.0     # plan.md said 11.5; test frames at 11.5 had mean 16-43/255 and 12.5 gave 36 (Tawan wants the Backrooms bright, shot 09 = 125), so B uses the A exposure and keeps the panel flicker as its difference
CHARLIE, MONSTER = "CHARLIE:", "MONSTER:"
CAM_ATTRS = ("translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ")


def clip(who, name):
    return os.path.join(CLIPS, who, name + ".fbx")


def open_shot(shot, n_frames):
    """restore the pristine scene from the backup (rerunnable), open it with all references, set range/units and the Arnold options"""
    src = os.path.join(ROOT, "scenes", "Shots", "Shot%s.mb" % shot)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    bk = os.path.join(BACKUP_DIR, "Shot%s_before_t09.mb" % shot)
    if not os.path.exists(bk):
        shutil.copy2(src, bk)
    else:
        shutil.copy2(bk, src)
    print("L| backup", bk)
    cmds.loadPlugin("mtoa", quiet=True)
    cmds.file(src, open=True, force=True, loadReferenceDepth="all")
    cmds.playbackOptions(min=1, max=n_frames, animationStartTime=1, animationEndTime=n_frames)
    cmds.currentUnit(time="film")
    o = "defaultArnoldRenderOptions"
    if cmds.objExists(o):
        cmds.setAttr(o + ".skipLicenseCheck", 0)
        cmds.setAttr(o + ".lightLinking", 0)
        cmds.setAttr(o + ".shadowLinking", 0)
        cmds.setAttr(o + ".renderDevice", 0)
    cmds.setAttr("ENV:LIGHT_MASTER.exposure", PRESET_B_EXPOSURE)   # Preset B (plan.md Q11): darker than A (13.0), flicker on
    cmds.setAttr("ENV:LIGHT_MASTER.flickerEnable", 1.0)
    for ns in ("VCAM", "VCAM1", "VCAM2"):
        if cmds.objExists(ns + ":VideoCamera_GRP"):
            cmds.setAttr(ns + ":VideoCamera_GRP.visibility", 0)
    return src


def noise(f, seed):
    return (0.5 * math.sin(2 * math.pi * f / 17.0 + seed) + 0.3 * math.sin(2 * math.pi * f / 7.3 + 2.1 * seed)
            + 0.2 * math.sin(2 * math.pi * f / 3.1 + 3.7 * seed))


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def lerp3(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def wpos(n):
    return om.MPoint(*cmds.xform(n, q=True, ws=True, t=True))


def show(ns, visible):
    for n in (ns + "GRP_Charlie_Placement", ns + "Charlie_Mixamo") if ns == CHARLIE else (ns + "GRP_Monster_Mixamo", ns + "Monster_Buff_Blobbell"):
        if cmds.objExists(n):
            cmds.setAttr(n + ".visibility", 1 if visible else 0)


def placement(ns):
    return ns + ("GRP_Charlie_Placement" if ns == CHARLIE else "GRP_Monster_Mixamo")


def key_placement(ns, frames, pos_fn, yaw_fn):
    """key the rig's placement group every frame: pos_fn(f) -> (x, y, z), yaw_fn(f) -> degrees about Y"""
    g = placement(ns)
    cmds.cutKey(g, clear=True)
    for f in frames:
        p = pos_fn(f)
        for a, v in zip(("translateX", "translateY", "translateZ"), p):
            cmds.setKeyframe(g, attribute=a, time=f, value=v)
        cmds.setKeyframe(g, attribute="rotateY", time=f, value=yaw_fn(f))
        cmds.setKeyframe(g, attribute="rotateX", time=f, value=0.0)
        cmds.setKeyframe(g, attribute="rotateZ", time=f, value=0.0)
    cmds.filterCurve(g + ".rotateY", filter="euler")


def bake_loop(ns, who, name, n_total, src_first, src_last, in_place, scale=1.0, dst_first=1):
    """bake a Mixamo clip onto the rig for n_total frames, repeating it if the clip is shorter; in_place freezes the hips X/Z travel
    (the placement group moves the character instead, so loops do not jump back)."""
    path = clip(who, name)
    clip_len = int(round((src_last - src_first + 1) * scale))
    done = 0
    while done < n_total:
        n_this = min(clip_len, n_total - done)
        sl = src_first + int(math.ceil(n_this / scale)) - 1
        info = bake_clip(path, rig_ns=ns, src_first=src_first, src_last=sl, dst_first=dst_first + done, set_range=False, time_scale=scale)
        assert not info["missing_dst_joints"], info
        done += n_this
    cmds.playbackOptions(min=1, max=max(cmds.playbackOptions(q=True, max=True), n_total), animationStartTime=1)
    hips = ns + "mixamorig:Hips"
    if in_place:
        for a in ("translateX", "translateZ"):
            v0 = cmds.getAttr(hips + "." + a, time=dst_first)
            cmds.cutKey(hips, attribute=a, clear=True)
            for f in range(dst_first, dst_first + n_total):
                cmds.setKeyframe(hips, attribute=a, time=f, value=v0)
    cmds.cutKey(ns + "*", time=(dst_first + n_total, dst_first + n_total + 400), clear=True)


def freeze_from(ns, f0, last):
    """hold the pose of frame f0 from f0+1 to last on every animated joint channel"""
    for j in cmds.ls(ns + "mixamorig:*", type="joint"):
        for a in CAM_ATTRS:
            if cmds.listConnections(j + "." + a, s=True, d=False):
                v = cmds.getAttr(j + "." + a, time=f0)
                cmds.cutKey(j, attribute=a, time=(f0 + 1, last + 400), clear=True)
                for f in range(f0 + 1, last + 1):
                    cmds.setKeyframe(j, attribute=a, time=f, value=v)


def eye_points(ns, frames):
    """eye = middle of Head and HeadTop_End, per frame (read BEFORE the head is collapsed)"""
    out = {}
    for f in frames:
        cmds.currentTime(f)
        h, t = wpos(ns + "mixamorig:Head"), wpos(ns + "mixamorig:HeadTop_End")
        out[f] = om.MPoint((h.x + t.x) / 2.0, (h.y + t.y) / 2.0, (h.z + t.z) / 2.0)
    return out


def collapse_head(ns):
    """first-person trick: collapse the Head joint so a camera at eye height does not sit inside the big head; hide the eye meshes"""
    for ax in "XYZ":
        cmds.setAttr("%smixamorig:Head.scale%s" % (ns, ax), 0.001)
    for m in (ns + "bevelPolygon1", ns + "bevelPolygon2"):
        if cmds.objExists(m):
            cmds.setAttr(m + ".visibility", 0)


def camera_nodes(shot):
    cam, grp = "CAM_Shot" + shot, "GRP_CAM_Shot" + shot
    shape = cmds.listRelatives(cam, shapes=True)[0]
    if not cmds.objExists(grp):
        grp = cmds.group(cam, name=grp)
    stray = (cmds.listConnections(cam, type="animCurve") or []) + (cmds.listConnections(grp, type="animCurve") or [])
    if stray:
        cmds.delete(stray)
    for e in cmds.ls("EXPR_Shot%s_*" % shot, type="expression"):
        cmds.delete(e)
    for attr in ("baseTx", "baseTy", "baseTz", "baseRx", "baseRy", "baseRz", "shakeRot", "shakeTrans"):
        if cmds.attributeQuery(attr, node=grp, exists=True):
            cmds.deleteAttr(grp, at=attr)
    for n in (grp,):
        cmds.setAttr(n + ".translate", 0, 0, 0)
        cmds.setAttr(n + ".rotate", 0, 0, 0)
        cmds.setAttr(n + ".scale", 1, 1, 1)
    cmds.setAttr(cam + ".scale", 1, 1, 1)
    for c in cmds.ls(type="camera"):
        try:
            cmds.setAttr(c + ".renderable", 1 if c == shape else 0)
        except Exception:
            pass
    return cam, shape


def look_at(pos, target):
    dx, dy, dz = target[0] - pos[0], target[1] - pos[1], target[2] - pos[2]
    return math.degrees(math.atan2(dy, math.hypot(dx, dz))), math.degrees(math.atan2(-dx, -dz))


def key_camera(cam, frames, pos_fn, aim_fn=None, rot_fn=None, roll_fn=None, shake_rot=0.5, shake_trans=0.5, seed=0.0):
    """key the camera every frame. aim_fn(f) -> target point (pitch/yaw from look_at) or rot_fn(f) -> (pitch, yaw); roll_fn(f) -> roll degrees.
    Handheld shake is baked into the keys (no expression)."""
    for f in frames:
        p = pos_fn(f)
        if rot_fn is not None:
            pitch, yaw = rot_fn(f)
        else:
            pitch, yaw = look_at(p, aim_fn(f))
        roll = roll_fn(f) if roll_fn else 0.0
        t = (p[0] + shake_trans * noise(f, 1.3 + seed), p[1] + shake_trans * noise(f, 4.1 + seed), p[2] + shake_trans * 0.6 * noise(f, 7.7 + seed))
        r = (pitch + shake_rot * noise(f, 2.9 + seed), yaw + shake_rot * noise(f, 5.3 + seed), roll + shake_rot * 0.5 * noise(f, 8.9 + seed))
        for a, v in zip(CAM_ATTRS, t + r):
            cmds.setKeyframe(cam, attribute=a, time=f, value=v)
    cmds.filterCurve(cam + ".rotateX", cam + ".rotateY", cam + ".rotateZ", filter="euler")


def set_lens(shape, focal, near=1.0):
    cmds.cutKey(shape, attribute="focalLength", clear=True)
    cmds.setAttr(shape + ".focalLength", focal)
    cmds.setAttr(shape + ".nearClipPlane", near)


def ndc(cam, shape, point):
    asp = cmds.getAttr("defaultResolution.width") / float(cmds.getAttr("defaultResolution.height"))
    hh = cmds.getAttr(shape + ".horizontalFilmAperture") * 25.4 / 2.0
    pc = point * om.MMatrix(cmds.xform(cam, q=True, ws=True, m=True)).inverse()
    if pc.z >= 0:
        return None
    f = cmds.getAttr(shape + ".focalLength")
    return (pc.x / -pc.z) * f / hh, (pc.y / -pc.z) * f / (hh / asp)


def report_frustum(cam, shape, label, joint_fn, frames):
    """print where a tracked point (joint_fn() -> node name) falls in the frame; returns True if inside at every checked frame"""
    ok = True
    for f in frames:
        cmds.currentTime(f)
        r = ndc(cam, shape, wpos(joint_fn()))
        inside = r is not None and abs(r[0]) <= 1.0 and abs(r[1]) <= 1.0
        ok = ok and inside
        print("L| frustum f%02d %s %s %s" % (f, label, None if r is None else (round(r[0], 2), round(r[1], 2)), "in" if inside else "OUT"))
    return ok


def save(src):
    cmds.currentTime(1)
    cmds.file(save=True, type="mayaBinary")
    print("L| saved", src)
