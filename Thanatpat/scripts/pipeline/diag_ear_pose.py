"""Read-only: which rotate axis of Head / Neck / Spine tilts Charlie's head sideways (lateral flexion), from the Stumble_Backwards frame-0 stance? Also finds the south wall plane near x -300. Nothing is saved."""
import sys
sys.path.insert(0, r"D:\projects\ProjectAnimation\scripts\pipeline")
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.api.OpenMaya as om
from bake_mixamo_clip import bake_clip
cmds.loadPlugin("mtoa", quiet=True)
cmds.file(r"D:\projects\ProjectAnimation\scenes_backup_2026-10-01\Shot05_before_t09.mb", open=True, force=True, loadReferenceDepth="all")
cmds.currentUnit(time="film")
bake_clip(r"D:\projects\ProjectAnimation\raw_assets\mixamo\charlie\Stumble_Backwards.fbx", rig_ns="CHARLIE:", src_first=0, src_last=0, dst_first=1, set_range=False, time_scale=1.0)
PL = "CHARLIE:GRP_Charlie_Placement"
cmds.setAttr(PL + ".translate", -300, -12, 400); cmds.setAttr(PL + ".rotate", 0, -90, 0)
cmds.currentTime(1)
# wall plane
sel = om.MSelectionList(); fns = []
for s in cmds.ls("ENV:*", type="mesh", noIntermediate=True, long=True):
    sel.clear(); sel.add(s); fns.append(om.MFnMesh(sel.getDagPath(0)))
best = 1e9
for fn in fns:
    r = fn.closestIntersection(om.MFloatPoint(-300, 60, 500), om.MFloatVector(0, 0, -1), om.MSpace.kWorld, 600, False)
    if r and r[0] is not None and r[1] is not None and r[1] > 0:
        best = min(best, r[1])
print("E| south wall at z =", round(500 - best, 1), "(ray from z 500 toward -z at x -300, y 60)")
m = om.MMatrix(cmds.xform(PL, q=True, ws=True, m=True)); inv = m.inverse()
def loc(n):
    p = om.MPoint(*cmds.xform(n, q=True, ws=True, t=True)) * inv
    return (round(p.x, 1), round(p.y, 1), round(p.z, 1))
head = "CHARLIE:mixamorig:Head"; top = "CHARLIE:mixamorig:HeadTop_End"
print("E| neutral HeadTop local (x lateral, y up, z forward) =", loc(top), "Head joint", loc(head))
for jn in ("Head", "Neck", "Spine2", "Spine1", "Spine"):
    j = "CHARLIE:mixamorig:" + jn
    for ax in "XYZ":
        attr = j + ".rotate" + ax
        v0 = cmds.getAttr(attr, time=1)
        out = []
        for d in (30.0,):
            cmds.cutKey(j, attribute="rotate" + ax, clear=True) if False else None
            cmds.setAttr(attr, v0 + d)
            t = loc(top)
            out.append((d, t))
            cmds.setAttr(attr, v0)
        base = loc(top)
        dd = (round(out[0][1][0] - base[0], 1), round(out[0][1][1] - base[1], 1), round(out[0][1][2] - base[2], 1))
        print("E| %-7s rotate%s +30deg -> HeadTop moves (dx lateral, dy up, dz forward) = %s" % (jn, ax, dd))
maya.standalone.uninitialize()
