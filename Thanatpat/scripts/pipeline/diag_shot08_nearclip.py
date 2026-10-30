"""Read-only: which Shot 08 frames have visible Charlie geometry closer than a candidate near-clip depth inside the frame? Nothing is saved."""
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.api.OpenMaya as om
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot08.mb", open=True, force=True, loadReferenceDepth="all")
cmds.currentUnit(time="film")
cam = "CAM_Shot08"; shape = cmds.listRelatives(cam, shapes=True)[0]
asp = cmds.getAttr("defaultResolution.width") / float(cmds.getAttr("defaultResolution.height"))
tr = [t for t in ("CHARLIE:body", "CHARLIE:hoodie", "CHARLIE:sweater", "CHARLIE:short", "CHARLIE:shoes1") if cmds.objExists(t) and cmds.getAttr(t + ".visibility")]
focal = cmds.getAttr(shape + ".focalLength"); hh = cmds.getAttr(shape + ".horizontalFilmAperture") * 25.4 / 2.0
for limit in (14.0, 18.0):
    bad = {}
    for f in range(1, 49):
        cmds.currentTime(f); inv = om.MMatrix(cmds.xform(cam, q=True, ws=True, m=True)).inverse(); worst = None
        for t in tr:
            v = cmds.xform(t + ".vtx[*]", q=True, ws=True, t=True)
            for i in range(0, len(v), 3):
                pc = om.MPoint(v[i], v[i+1], v[i+2]) * inv
                if pc.z < 0 and -pc.z < limit and abs((pc.x / -pc.z) * focal / hh) <= 1.3 and abs((pc.y / -pc.z) * focal / (hh / asp)) <= 1.3:
                    worst = (t.split(":")[-1], round(-pc.z, 1)) if worst is None or -pc.z < worst[1] else worst
        if worst: bad[f] = worst
    print("N| near-clip %.0f would clip geometry in frames:" % limit, bad)
# what is left once everything nearer than 18 is removed: the nearest visible depth per sample frame
for f in (20, 28, 36, 44, 48):
    cmds.currentTime(f); inv = om.MMatrix(cmds.xform(cam, q=True, ws=True, m=True)).inverse(); rows = []
    for t in tr:
        v = cmds.xform(t + ".vtx[*]", q=True, ws=True, t=True)
        d = [-(om.MPoint(v[i], v[i+1], v[i+2]) * inv).z for i in range(0, len(v), 3)]
        d = [x for x in d if x > 0]
        rows.append((t.split(":")[-1], round(min(d), 1) if d else None))
    print("N| f%d nearest depth per mesh" % f, rows)
maya.standalone.uninitialize()
