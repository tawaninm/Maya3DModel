"""Read-only: which non-ENV meshes have vertices inside CAM_Shot08's frame at frames 36-48? (finds the hair that shows in Shot 08). Nothing is saved."""
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.api.OpenMaya as om
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot08.mb", open=True, force=True, loadReferenceDepth="all")
cmds.currentUnit(time="film")
cam = "CAM_Shot08"; shape = cmds.listRelatives(cam, shapes=True)[0]
W, H = cmds.getAttr("defaultResolution.width"), cmds.getAttr("defaultResolution.height"); asp = W / float(H)
print("V| names with hair/head:", cmds.ls("*hair*", "*Hair*", "*head*", "*Head*", long=False, type="transform")[:20])
meshes = [m for m in cmds.ls(type="mesh", noIntermediate=True, long=True) if not cmds.ls(m, long=True)[0].split("|")[-2].startswith("ENV:")]
tr = sorted({cmds.listRelatives(m, parent=True, fullPath=True)[0] for m in meshes})
tr = [t for t in tr if ":Arch" not in t and "ENV:" not in t and "UI:" not in t]
def vis(t):
    n = t
    while n:
        if not cmds.getAttr(n + ".visibility"): return False
        p = cmds.listRelatives(n, parent=True, fullPath=True); n = p[0] if p else None
    return True
for f in (36, 40, 44, 48):
    cmds.currentTime(f)
    inv = om.MMatrix(cmds.xform(cam, q=True, ws=True, m=True)).inverse()
    focal = cmds.getAttr(shape + ".focalLength"); hh = cmds.getAttr(shape + ".horizontalFilmAperture") * 25.4 / 2.0
    cp = om.MPoint(*cmds.xform(cam, q=True, ws=True, t=True)); rows = []
    for t in tr:
        if not vis(t): continue
        v = cmds.xform(t + ".vtx[*]", q=True, ws=True, t=True); pts = [om.MPoint(v[i], v[i+1], v[i+2]) for i in range(0, len(v), 3)]
        inside = 0; dmin = 1e9
        for p in pts:
            pc = p * inv
            if pc.z < 0 and abs((pc.x / -pc.z) * focal / hh) <= 1 and abs((pc.y / -pc.z) * focal / (hh / asp)) <= 1: inside += 1
            dmin = min(dmin, cp.distanceTo(p))
        rows.append((inside, len(pts), round(dmin, 1), t.split("|")[-1]))
    print("V| f%d" % f, sorted(rows, reverse=True)[:6])
maya.standalone.uninitialize()
