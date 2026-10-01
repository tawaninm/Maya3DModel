import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.file(r"D:\projects\ProjectAnimation\scenes\Characters\Charlie_Mixamo.mb", open=True, force=True)
n = cmds.polyEvaluate("shoes1", vertex=True)
pos = [cmds.xform("shoes1.vtx[%d]" % i, q=True, ws=True, t=True) for i in range(n)]
side = [p[0] > 0 for p in pos]
nf = cmds.polyEvaluate("shoes1", face=True)
span = []
for f in range(nf):
    info = cmds.polyInfo("shoes1.f[%d]" % f, faceToVertex=True)[0].split(":")[1].split()
    vs = [int(v) for v in info]
    if len(set(side[v] for v in vs)) > 1:
        span.append((f, vs))
print("L| verts", n, "faces", nf, "faces spanning both sides:", len(span))
for f, vs in span[:12]:
    ys = [round(pos[v][1], 1) for v in vs]; xs = [round(pos[v][0], 1) for v in vs]; zs = [round(pos[v][2], 1) for v in vs]
    print("L|  face", f, "x", xs, "y", ys, "z", zs)
sh = cmds.polyEvaluate("shoes1", shell=True)
print("L| shells in shoes1:", sh)
maya.standalone.uninitialize()
