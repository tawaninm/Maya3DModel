"""Bright desk lighting for the shots where the camcorder sits on the shelf under the desktop (Shot 07; Shot 08 has the same code inline).

Why: the shelf (y 73.1) under the desktop (y 108.9-111.5) gets almost no ceiling light and the furniture texture there is near black, so the desk read as
black. Tawan (2026-10-01/02): the desk must be bright, it is inside the Backrooms. Rig = overhead panel + small lamp under the desktop above the
camcorder + a pale warm-grey shader on the 17 or so faces of the cavity (scene-only reference edit, the env file is untouched).
Values were tuned with Shot 08 test frames: albedo 0.55 and 0.13 burned the frame to white, 0.045 is right; overhead 12.0, lamp 11.5.

Usage inside mayapy after the shot scene is open:
    from desk_light_rig import apply_desk_rig
    apply_desk_rig(CAMCORDER_POS)
"""
import math

import maya.api.OpenMaya as om
import maya.cmds as cmds

SHELF_TOP_Y = 73.1
CAVITY_X_MAX = -228.0                       # only hits deeper than the front valance (x -217) count, so the valance keeps its texture
CAVITY_ALBEDO = (0.045, 0.042, 0.035)
OVERHEAD_EXP, LAMP_EXP = 12.0, 11.5
KELVIN = 6500.0


def make_area(name, pos, aim, size, exposure):
    if cmds.objExists(name):
        cmds.delete(name)
    shp = cmds.shadingNode("aiAreaLight", asLight=True, name=name)      # returns the transform; the shape carries `name`
    xf = cmds.listRelatives(shp, parent=True)[0] if cmds.nodeType(shp) != "transform" else shp
    dx, dy, dz = aim[0] - pos[0], aim[1] - pos[1], aim[2] - pos[2]
    yaw = math.degrees(math.atan2(-dx, -dz))
    pitch = math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    cmds.xform(xf, ws=True, t=list(pos), ro=[pitch, yaw, 0.0], s=[size[0], size[1], 1.0])
    cmds.setAttr(shp + ".exposure", exposure)
    cmds.setAttr(shp + ".intensity", 50.0)
    cmds.setAttr(shp + ".aiUseColorTemperature", 1)
    cmds.setAttr(shp + ".aiColorTemperature", KELVIN)
    if "defaultLightSet" not in (cmds.listSets(object=shp) or []):
        cmds.sets(shp, add="defaultLightSet")
    for a in ("aiCamera", "primaryVisibility"):          # lights must not show up as white quads in the picture
        if cmds.attributeQuery(a, node=name, exists=True):
            cmds.setAttr(name + "." + a, 0)
    return name


def lighten_cavity(camcorder_pos):
    desk = cmds.ls("ENV:Prop_OfficeDesk_and_Drawers", long=True)[0]
    shape = cmds.listRelatives(desk, shapes=True, fullPath=True, noIntermediate=True)[0]
    sel = om.MSelectionList()
    sel.add(shape)
    fn = om.MFnMesh(sel.getDagPath(0))
    cx, cy, cz = camcorder_pos
    faces = set()

    def cast(origin, direction, y_lo, y_hi, max_dist, x_max=None):
        r = fn.allIntersections(om.MFloatPoint(*origin), om.MFloatVector(*direction), om.MSpace.kWorld, max_dist, False)
        if not r or not len(r[0]):
            return
        for _t, face, y, x in sorted(zip(r[1], r[2], [p.y for p in r[0]], [p.x for p in r[0]])):
            if x_max is not None and x > x_max:
                continue
            if y_lo <= y <= y_hi:
                faces.add(face)
                break

    zs = range(int(cz) - 40, int(cz) + 41, 4)
    for x in range(-262, -214, 4):
        for z in zs:
            cast((x, 100.0, z), (0, -1, 0), SHELF_TOP_Y - 3.0, SHELF_TOP_Y + 3.0, 60.0)                 # shelf top
            cast((x, SHELF_TOP_Y + 3.0, z), (0, 1, 0), 105.0, 112.0, 60.0)                              # cavity ceiling
    for y in range(int(SHELF_TOP_Y) + 4, 108, 4):
        for z in zs:
            cast((cx + 20.0, y, z), (-1, 0, 0), y - 1.0, y + 1.0, 120.0, CAVITY_X_MAX)                  # back wall
        for x in range(-262, -226, 6):
            cast((x, y, cz), (0, 0, 1), y - 1.0, y + 1.0, 80.0)                                          # side walls
            cast((x, y, cz), (0, 0, -1), y - 1.0, y + 1.0, 80.0)
    print("L| cavity faces found:", len(faces))
    if not faces:
        return 0
    mat = cmds.shadingNode("aiStandardSurface", asShader=True, name="Shot_CavityLight_M")
    cmds.setAttr(mat + ".baseColor", CAVITY_ALBEDO[0], CAVITY_ALBEDO[1], CAVITY_ALBEDO[2], type="double3")
    cmds.setAttr(mat + ".specular", 0.1)
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="Shot_CavityLight_SG")
    cmds.connectAttr(mat + ".outColor", sg + ".surfaceShader", force=True)
    cmds.sets([shape + ".f[%d]" % f for f in sorted(faces)], forceElement=sg)
    return len(faces)


def apply_desk_rig(camcorder_pos, overhead_exp=OVERHEAD_EXP, lamp_exp=LAMP_EXP):
    cx, cy, cz = camcorder_pos
    make_area("Desk_Fill_Overhead", (-215.0, 262.0, 190.0), (-215.0, 0.0, 190.0), (130.0, 130.0), overhead_exp)
    make_area("Desk_Fill_UnderDeskLamp", (cx + 6.0, 104.0, cz), (cx + 6.0, 0.0, cz), (35.0, 35.0), lamp_exp)
    n = lighten_cavity(camcorder_pos)
    print("L| desk rig applied: overhead %.1f, lamp %.1f, %d cavity faces" % (overhead_exp, lamp_exp, n))
    return n
