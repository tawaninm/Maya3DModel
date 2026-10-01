"""Read-only: which Charlie mesh forms the bright dome in the lower-left of Shot 08 frames 44-48? Counts vertices per mesh in the lower-left screen region. Nothing is saved."""
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.api.OpenMaya as om
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot08.mb", open=True, force=True, loadReferenceDepth="all")
cmds.currentUnit(time="film")
cam = "CAM_Shot08"; shape = cmds.listRelatives(cam, shapes=True)[0]
asp = cmds.getAttr("defaultResolution.width") / float(cmds.getAttr("defaultResolution.height"))
tr = [t for t in cmds.ls("CHARLIE:*", type="transform") if cmds.listRelatives(t, shapes=True, type="mesh")]
print("D| charlie meshes:", [(t, cmds.getAttr(t + ".visibility")) for t in tr])
for f in (44, 46, 48):
    cmds.currentTime(f); inv = om.MMatrix(cmds.xform(cam, q=True, ws=True, m=True)).inverse()
    focal = cmds.getAttr(shape + ".focalLength"); hh = cmds.getAttr(shape + ".horizontalFilmAperture") * 25.4 / 2.0
    rows = []
    for t in tr:
        if not cmds.getAttr(t + ".visibility"): continue
        v = cmds.xform(t + ".vtx[*]", q=True, ws=True, t=True); inside = ll = 0; depth = []
        for i in range(0, len(v), 3):
            pc = om.MPoint(v[i], v[i+1], v[i+2]) * inv
            if pc.z >= 0: continue
            x, y = (pc.x / -pc.z) * focal / hh, (pc.y / -pc.z) * focal / (hh / asp)
            if abs(x) <= 1 and abs(y) <= 1:
                inside += 1; depth.append(-pc.z)
                if x < -0.1 and y < 0.2: ll += 1
        rows.append((ll, inside, round(min(depth), 1) if depth else None, t.split(":")[-1]))
    print("D| f%d (lower-left verts, in-frame verts, nearest depth, mesh):" % f, sorted(rows, reverse=True)[:5])
maya.standalone.uninitialize()
