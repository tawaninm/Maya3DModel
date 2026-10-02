"""T09 Shot 10-14 assembly (2026-10-02). Run one shot at a time:  mayapy build_shots10_14_t09.py 10
Every run restores scenes_backup_2026-10-02/ShotNN_before_t09.mb first, so it can be repeated.
All five shots play in the bright Backrooms corridor (Preset B: LIGHT_MASTER 11.5 + panel flicker on panels 02/03 at x -1478/-1024), so the
action is placed around x -900 to -1450, z 525 (corridor centre).  Plan table: plan.md "ช็อตของตะวัน".
"""
import math
import os
import sys

import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.api.OpenMaya as om

sys.path.insert(0, r"D:\projects\ProjectAnimation\scripts\pipeline")
from shot_lib import *  # noqa: F401,F403,E402


# ---------------------------------------------------------------------------------------------------------------------------------
def shot10():
    """Shot 10 (48 f): Monster POV, low slow push. The camera is the Monster's eye, so the Monster stays behind it (hidden); Charlie walks away."""
    N = 48
    src = open_shot("10", N)
    show(MONSTER, False)
    show(CHARLIE, True)
    bake_loop(CHARLIE, "charlie", "Walking", N, 20, 67, in_place=True)
    X0, Z = -1150.0, 525.0
    cx = lambda f: X0 - 120.0 * (f - 1) / (N - 1)                      # slow cautious walk, 60 units/s
    key_placement(CHARLIE, range(1, N + 1), lambda f: (cx(f), FLOOR_Y, Z), lambda f: -90.0)
    cam, shape = camera_nodes("10")
    set_lens(shape, 24.0, 5.0)
    key_camera(cam, range(1, N + 1), pos_fn=lambda f: (-880.0 - 50.0 * (f - 1) / (N - 1), 28.0, 532.0),
               aim_fn=lambda f: (cx(f), 42.0, Z), shake_rot=0.5, shake_trans=0.4, seed=10.0)
    ok = report_frustum(cam, shape, "Charlie head", lambda: CHARLIE + "mixamorig:Head", (1, 24, 48))
    print("L| Charlie head inside the frame at every checked frame:", ok)
    save(src)


# ---------------------------------------------------------------------------------------------------------------------------------
def make_dontrun_text(cx, z):
    """'DON'T RUN' (PNG from make_dontrun_png.py) on a plane just in front of the north wall (z about 707)"""
    png = os.path.join(ROOT, "sourceimages", "Backrooms_Tiling", "DontRun_text.png")      # drawn by make_dontrun_png.py (mayapy has no Pillow)
    assert os.path.exists(png), "run make_dontrun_png.py first"
    name = "WallText_DontRun"
    if cmds.objExists(name):
        cmds.delete(name)
    plane = cmds.polyPlane(name=name, width=105.0, height=26.25, subdivisionsX=1, subdivisionsY=1, axis=(0, 0, -1))[0]
    cmds.xform(plane, ws=True, t=(cx, 92.0, z))
    mat = cmds.shadingNode("aiStandardSurface", asShader=True, name="DontRun_M")
    fl = cmds.shadingNode("file", asTexture=True, isColorManaged=True, name="DontRun_File")
    cmds.setAttr(fl + ".fileTextureName", png.replace("\\", "/"), type="string")
    cmds.connectAttr(fl + ".outColor", mat + ".baseColor", force=True)
    for ch in "RGB":
        cmds.connectAttr(fl + ".outAlpha", "%s.opacity%s" % (mat, ch), force=True)
    cmds.setAttr(mat + ".specular", 0.15)
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="DontRun_SG")
    cmds.connectAttr(mat + ".outColor", sg + ".surfaceShader", force=True)
    cmds.sets(plane, forceElement=sg)
    shp = cmds.listRelatives(plane, shapes=True)[0]
    cmds.setAttr(shp + ".castsShadows", 0)
    print("L| wall text", plane, "at", (cx, 92.0, z), png)


def shot11():
    """Shot 11 (72 f): CU eye level, rack focus from Charlie to the 'DON'T RUN' text on the wall behind him (Charlie looks around)."""
    N = 72
    src = open_shot("11", N)
    show(MONSTER, False)
    show(CHARLIE, True)
    bake_loop(CHARLIE, "charlie", "Look_Around", N, 0, N - 1, in_place=False)
    CX, WALL_Z, CH_Z, CAM_Z = -1250.0, 705.6, 615.0, 430.0
    key_placement(CHARLIE, range(1, N + 1), lambda f: (CX + 30.0, FLOOR_Y, CH_Z), lambda f: 180.0)       # faces -Z, towards the camera
    make_dontrun_text(CX - 55.0, WALL_Z)
    cmds.currentTime(1)
    eye_y = wpos(CHARLIE + "mixamorig:Head").y + 20.0          # the Head joint is at the base of the skull; the eyes are about 20 units above it
    cam, shape = camera_nodes("11")
    set_lens(shape, 40.0, 5.0)
    key_camera(cam, range(1, N + 1), pos_fn=lambda f: (CX, eye_y, CAM_Z + 10.0 * (f - 1) / (N - 1)),
               aim_fn=lambda f: (CX + 12.0, eye_y - 2.0, CH_Z), shake_rot=0.25, shake_trans=0.2, seed=11.0)
    # rack focus: Charlie first, then the wall text
    d_char = math.hypot(CX + 30.0 - CX, CH_Z - (CAM_Z + 5.0))
    d_wall = math.hypot(0.0, WALL_Z - (CAM_Z + 5.0))
    dof = {a: cmds.attributeQuery(a, node=shape, exists=True) for a in ("aiEnableDOF", "aiApertureSize", "aiFocusDistance", "focusDistance", "depthOfField", "fStop")}
    print("L| DOF attributes present:", dof)
    if dof["aiEnableDOF"]:
        cmds.setAttr(shape + ".aiEnableDOF", 1)
        cmds.setAttr(shape + ".aiApertureSize", 1.4)
    if dof["depthOfField"]:
        cmds.setAttr(shape + ".depthOfField", 1)
    fd_attr = "aiFocusDistance" if dof["aiFocusDistance"] else "focusDistance"
    cmds.cutKey(shape, attribute=fd_attr, clear=True)
    for f, v in ((1, d_char), (24, d_char), (44, d_wall), (N, d_wall)):
        cmds.setKeyframe(shape, attribute=fd_attr, time=f, value=v)
    print("L| rack focus %s: %.0f (Charlie) -> %.0f (wall text) between frames 24 and 44" % (fd_attr, d_char, d_wall))
    ok = report_frustum(cam, shape, "Charlie head", lambda: CHARLIE + "mixamorig:Head", (1, 36, 72))      # the joint is below the eyes, so an NDC y around -0.6 is expected
    r = ndc(cam, shape, om.MPoint(CX - 55.0, 92.0, WALL_Z))
    print("L| wall text centre NDC", None if r is None else (round(r[0], 2), round(r[1], 2)))
    save(src)



# ---------------------------------------------------------------------------------------------------------------------------------
def shot12():
    """Shot 12 (48 f): MCU, Dutch angle, fast turn. Charlie spins 180 degrees (RunningTurn180, 17 f) and freezes facing the roaring Monster."""
    N = 48
    src = open_shot("12", N)
    show(CHARLIE, True)
    show(MONSTER, True)
    CX, MX, Z = -1300.0, -1130.0, 525.0
    bake_loop(CHARLIE, "charlie", "RunningTurn180", 17, 0, 16, in_place=False)
    freeze_from(CHARLIE, 17, N)                                         # holds the end pose after the turn
    bake_loop(MONSTER, "monster", "Mutant_Roaring", N, 15, 62, in_place=False)
    key_placement(CHARLIE, range(1, N + 1), lambda f: (CX, FLOOR_Y, Z), lambda f: -90.0)       # starts facing -X, the turn ends facing +X (the Monster)
    key_placement(MONSTER, range(1, N + 1), lambda f: (MX, FLOOR_Y, Z), lambda f: -90.0)       # faces -X, towards Charlie
    cam, shape = camera_nodes("12")
    set_lens(shape, 24.0, 5.0)
    mid = (-1215.0, 75.0, Z)
    # profile view from the south side of the corridor (z 372; the south wall is at z 343, z 330 was behind it and rendered black): Charlie and the Monster side by side, whip pan from Charlie to the middle, Dutch angle
    key_camera(cam, range(1, N + 1), pos_fn=lambda f: (-1215.0, 85.0, 372.0),
               aim_fn=lambda f: lerp3((CX, 70.0, Z), mid, smooth((f - 8) / 28.0)),
               roll_fn=lambda f: 10.0 + 6.0 * smooth((f - 1) / 47.0), shake_rot=1.0, shake_trans=0.8, seed=12.0)
    ok = report_frustum(cam, shape, "Charlie head", lambda: CHARLIE + "mixamorig:Head", (1, 17, 48))
    ok2 = report_frustum(cam, shape, "Monster head", lambda: MONSTER + "mixamorig:Head", (1, 24, 48))
    print("L| Charlie in frame:", ok, " Monster in frame:", ok2)
    save(src)


# ---------------------------------------------------------------------------------------------------------------------------------
def shot13():
    """Shot 13 (48 f): POV running, handheld sprint. The camera starts looking back at the Monster chasing 110 units behind, whips forward and sprints."""
    N = 48
    src = open_shot("13", N)
    show(CHARLIE, True)
    show(MONSTER, True)
    bake_loop(CHARLIE, "charlie", "Terrified_Run", N, 0, 26, in_place=True)
    bake_loop(MONSTER, "monster", "Mutant_Run", N, 0, 21, in_place=True)
    X0, Z = -950.0, 525.0
    xc = lambda f: X0 - 7.1 * (f - 1)                                   # about 170 units/s
    xm = lambda f: X0 + 110.0 - 6.3 * (f - 1)                           # about 150 units/s: slowly losing ground
    key_placement(CHARLIE, range(1, N + 1), lambda f: (xc(f), FLOOR_Y, Z), lambda f: -90.0)
    key_placement(MONSTER, range(1, N + 1), lambda f: (xm(f), FLOOR_Y, Z), lambda f: -90.0)
    eyes = eye_points(CHARLIE, range(1, N + 1))
    collapse_head(CHARLIE)
    cam, shape = camera_nodes("13")
    set_lens(shape, 24.0, 15.0)
    w = lambda f: smooth((f - 6) / 14.0)
    key_camera(cam, range(1, N + 1), pos_fn=lambda f: (eyes[f].x - 4.0, eyes[f].y, eyes[f].z),
               rot_fn=lambda f: (8.0 + (-4.0 - 8.0) * w(f), -90.0 + 180.0 * w(f)),                  # yaw -90 = looking back (+X), +90 = forward (-X)
               roll_fn=lambda f: 3.0 * math.sin(f * 0.5), shake_rot=1.6, shake_trans=1.2, seed=13.0)
    ok = report_frustum(cam, shape, "Monster head", lambda: MONSTER + "mixamorig:Head", (1, 4, 8))
    print("L| Monster visible while looking back:", ok)
    save(src)


# ---------------------------------------------------------------------------------------------------------------------------------
def make_hole(cx, cz, size=130.0):
    """floor hole: a black plane just above the floor (y -11.6); Charlie sinks below it and disappears"""
    if cmds.objExists("Hole_Floor"):
        cmds.delete("Hole_Floor")
    plane = cmds.polyPlane(name="Hole_Floor", width=size, height=size, subdivisionsX=1, subdivisionsY=1)[0]
    cmds.xform(plane, ws=True, t=(cx, FLOOR_Y + 0.4, cz))
    mat = cmds.shadingNode("aiStandardSurface", asShader=True, name="Hole_M")
    cmds.setAttr(mat + ".baseColor", 0.0, 0.0, 0.0, type="double3")
    cmds.setAttr(mat + ".specular", 0.0)
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="Hole_SG")
    cmds.connectAttr(mat + ".outColor", sg + ".surfaceShader", force=True)
    cmds.sets(plane, forceElement=sg)
    print("L| floor hole at", (cx, FLOOR_Y + 0.4, cz), "size", size)


def shot14():
    """Shot 14 (48 f, the file had 24): wide bird's-eye, fast tilt down. Charlie jumps and dives into a hole in the floor."""
    N = 48
    src = open_shot("14", N)
    show(MONSTER, False)
    show(CHARLIE, True)
    HX, HZ = -1400.0, 525.0
    make_hole(HX, HZ)
    bake_loop(CHARLIE, "charlie", "Jumping", 46, 0, 45, in_place=False)
    freeze_from(CHARLIE, 46, N)
    px = lambda f: (HX + 90.0) + (HX - (HX + 90.0)) * smooth((f - 12) / 22.0)                    # steps towards the hole while jumping
    py = lambda f: FLOOR_Y - 170.0 * smooth((f - 34) / 14.0)                                      # sinks below the black plane at the end
    key_placement(CHARLIE, range(1, N + 1), lambda f: (px(f), py(f), HZ), lambda f: -90.0)
    cam, shape = camera_nodes("14")
    set_lens(shape, 24.0, 5.0)
    t = lambda f: smooth((f - 1) / 35.0)
    cpos = lambda f: lerp3((HX + 430.0, 170.0, HZ), (HX + 8.0, 238.0, HZ), t(f))
    target = lambda f: lerp3((px(f), 50.0, HZ), (HX, FLOOR_Y, HZ), t(f))

    def rot(f):
        pitch, _ = look_at(cpos(f), target(f))
        return max(-88.0, pitch), 90.0                                  # yaw fixed (looking -X), tilt only: no yaw flip when it points straight down

    key_camera(cam, range(1, N + 1), pos_fn=cpos, rot_fn=rot, shake_rot=0.6, shake_trans=0.5, seed=14.0)
    ok = report_frustum(cam, shape, "Charlie head", lambda: CHARLIE + "mixamorig:Head", (1, 20, 30))
    r = ndc(cam, shape, om.MPoint(HX, FLOOR_Y, HZ))
    print("L| hole centre NDC at frame", N, None if r is None else (round(r[0], 2), round(r[1], 2)))
    save(src)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else ""
    {"10": shot10, "11": shot11, "12": shot12, "13": shot13, "14": shot14}.get(which, lambda: print("usage: build_shots10_14_t09.py 10|11|12|13|14"))()
    maya.standalone.uninitialize()
