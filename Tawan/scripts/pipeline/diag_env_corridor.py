"""Read-only: map the Backrooms env for Shot 09. Ray-casts walls from a grid of floor points, lists ceiling lights, prints the hero corridor camera. Nothing is saved."""
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.api.OpenMaya as om
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot09.mb", open=True, force=True, loadReferenceDepth="all")
for c in ("ENV:CAM_Backrooms_Hero_Corridor1", "ENV:CAM_Light_Test1", "ENV:CAM_Props_Showcase_Desk1"):
    if cmds.objExists(c):
        print("E|", c, "t", [round(v, 1) for v in cmds.xform(c, q=True, ws=True, t=True)], "r", [round(v, 1) for v in cmds.xform(c, q=True, ws=True, ro=True)], "focal", cmds.getAttr(cmds.listRelatives(c, shapes=True)[0] + ".focalLength"))
lights = [cmds.xform(cmds.listRelatives(l, parent=True)[0], q=True, ws=True, t=True) for l in cmds.ls(type="aiAreaLight") if "ENV:" in l and "Shot" not in l]
xs = sorted(round(l[0]) for l in lights); zs = sorted(round(l[2]) for l in lights)
print("E| env area lights:", len(lights), "x values", sorted(set(xs)), "z values", sorted(set(zs)), "y", sorted(set(round(l[1]) for l in lights))[:3])
sel = om.MSelectionList(); fns = []
for s in cmds.ls("ENV:*", type="mesh", noIntermediate=True, long=True):
    sel.clear(); sel.add(s); fns.append(om.MFnMesh(sel.getDagPath(0)))
def dist(x, y, z, d):
    best = 1e9
    for fn in fns:
        r = fn.closestIntersection(om.MFloatPoint(x, y, z), om.MFloatVector(*d), om.MSpace.kWorld, 3000, False)
        if r and r[0] is not None and r[1] is not None and r[1] > 0: best = min(best, r[1])
    return best
print("E| grid (x,z): wall distance at eye height y=100 toward +x, -x, +z, -z (3000 = none)")
for x in range(-1000, 601, 200):
    row = []
    for z in range(0, 701, 175):
        row.append("(%d,%d):%s" % (x, z, "/".join(str(min(3000, int(dist(x, 100, z, d)))) for d in ((1,0,0), (-1,0,0), (0,0,1), (0,0,-1)))))
    print("E|", "  ".join(row))
maya.standalone.uninitialize()
