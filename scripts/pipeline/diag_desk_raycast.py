"""Read-only: shoot rays straight down at the camcorder spot (and neighbours) to list every ENV surface and its height. Nothing is saved."""
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.api.OpenMaya as om
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot08.mb", open=True, force=True, loadReferenceDepth="all")
sel = om.MSelectionList()
meshes = []
for s in cmds.ls("ENV:*", type="mesh", noIntermediate=True, long=True):
    sel.clear(); sel.add(s)
    meshes.append((s.split("|")[-2] if "|" in s else s, om.MFnMesh(sel.getDagPath(0))))
def cast(x, z):
    hits = []
    for name, fn in meshes:
        r = fn.allIntersections(om.MFloatPoint(x, 400, z), om.MFloatVector(0, -1, 0), om.MSpace.kWorld, 1000, False)
        if r and r[0]:
            for p in r[0]:
                hits.append((round(p.y, 1), name))
    return sorted(set(hits), reverse=True)
for (x, z) in [(-238, 185), (-225, 185), (-238, 165), (-238, 205), (-260, 185), (-210, 185), (-197, 195)]:
    print("R| ray down at x=%d z=%d:" % (x, z), cast(x, z)[:8])
print("R| camcorder bbox y:", [round(v, 1) for v in cmds.exactWorldBoundingBox("VCAM:VideoCamera_GRP")])
maya.standalone.uninitialize()
