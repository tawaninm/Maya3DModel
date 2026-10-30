import sys
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
for label, path in (("before", r"D:\projects\ProjectAnimation\scenes_backup_2026-10-01\Charlie_Mixamo_before_shoes.mb"), ("after", r"D:\projects\ProjectAnimation\scenes\Characters\Charlie_Mixamo.mb")):
    cmds.file(path, open=True, force=True)
    n = cmds.polyEvaluate("shoes1", vertex=True)
    nf = cmds.polyEvaluate("shoes1", face=True)
    parent = list(range(n))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for f in range(nf):
        vs = [int(v) for v in cmds.polyInfo("shoes1.f[%d]" % f, faceToVertex=True)[0].split(":")[1].split()]
        for v in vs[1:]:
            parent[find(v)] = find(vs[0])
    shell = [find(i) for i in range(n)]
    ids = sorted(set(shell))
    ws = [cmds.xform("shoes1.vtx[%d]" % i, q=True, ws=True, t=True) for i in range(n)]
    for s in ids:
        xs = [ws[i][0] for i in range(n) if shell[i] == s]
        zs = [ws[i][2] for i in range(n) if shell[i] == s]
        print("L|", label, "shell", ids.index(s), "x %.1f..%.1f (centre %.1f)  z %.1f..%.1f" % (min(xs), max(xs), sum(xs) / len(xs), min(zs), max(zs)))
    a = [ws[i] for i in range(n) if shell[i] == ids[0]]; b = [ws[i] for i in range(n) if shell[i] == ids[1]]
    best = min(((sum((p[k] - q[k]) ** 2 for k in range(3)) ** 0.5), p, q) for p in a for q in b)
    print("L|", label, "closest pair dist %.2f between" % best[0], [round(v, 1) for v in best[1]], [round(v, 1) for v in best[2]])
maya.standalone.uninitialize()
