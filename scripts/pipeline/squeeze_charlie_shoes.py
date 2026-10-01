"""RESULT 2026-10-01: NOT ENOUGH, reverted. Closest vertex distance between the shoes went 0.33 -> 0.39 cm only, because the shoes point inward about 30 deg and their toes cross near x = 0
(shell 0 spans x -6.8..17.0, shell 1 spans -20.7..5.6). Squeezing or shifting along X cannot separate crossed toes; rotating each shoe outward is needed.
Charlie_Mixamo.mb was restored from scenes_backup_2026-10-01/Charlie_Mixamo_before_shoes.mb. Do not run this script again as it is.
B (Tawan 2026-10-01): the two shoes of Charlie_Mixamo.mb (mesh shoes1, 2 shells) nearly touch at the toes.
Scale each shoe shell 85% along X around its own centre and move it 1.2 cm outward, on the intermediate (pre-skin) shape. Shells are found by face connectivity:
splitting by the sign of world X is wrong because each shoe points inward and crosses x = 0.
Idempotent: always restores the pre-edit backup first, then applies the change once."""
import os
import shutil
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds

SRC = r"D:\projects\ProjectAnimation\scenes\Characters\Charlie_Mixamo.mb"
BK = r"D:\projects\ProjectAnimation\scenes_backup_2026-10-01\Charlie_Mixamo_before_shoes.mb"
FACTOR = 0.85
SHIFT = 1.2   # cm each shoe moves outward after the squeeze (scaling alone only moved the toes 0.3 cm apart)
if not os.path.exists(BK):
    shutil.copy2(SRC, BK)
else:
    shutil.copy2(BK, SRC)
print("L| restored from backup", BK)
cmds.file(SRC, open=True, force=True)
n = cmds.polyEvaluate("shoes1", vertex=True)
nf = cmds.polyEvaluate("shoes1", face=True)
parent = list(range(n))


def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a


for f in range(nf):
    vs = [int(v) for v in cmds.polyInfo("shoes1.f[%d]" % f, faceToVertex=True)[0].split(":")[1].split()]
    for v in vs[1:]:
        parent[find(v)] = find(vs[0])
shell = [find(i) for i in range(n)]
ids = sorted(set(shell))
print("L| shells", len(ids), [shell.count(s) for s in ids])
ws = [cmds.xform("shoes1.vtx[%d]" % i, q=True, ws=True, t=True) for i in range(n)]


def min_gap():
    a = [ws[i] for i in range(n) if shell[i] == ids[0]]
    b = [ws[i] for i in range(n) if shell[i] == ids[1]]
    return round(min(sum((p[k] - q[k]) ** 2 for k in range(3)) ** 0.5 for p in a for q in b), 2)


print("L| true min distance between the two shoes before:", min_gap(), "cm; shell world x centres", [round(sum(ws[i][0] for i in range(n) if shell[i] == s) / shell.count(s), 1) for s in ids])
orig = [s for s in cmds.listRelatives("shoes1", shapes=True, fullPath=True) if cmds.getAttr(s + ".intermediateObject")][0]
pts = [cmds.xform("%s.vtx[%d]" % (orig, i), q=True, os=True, t=True) for i in range(n)]
for s in ids:
    members = [i for i in range(n) if shell[i] == s]
    c = sum(pts[i][0] for i in members) / len(members)
    out = SHIFT if sum(ws[i][0] for i in members) / len(members) > 0 else -SHIFT   # world +x shoe goes +x, the other goes -x (os x axis matches world x)
    for i in members:
        cmds.xform("%s.vtx[%d]" % (orig, i), os=True, t=(c + (pts[i][0] - c) * FACTOR + out, pts[i][1], pts[i][2]))
ws = [cmds.xform("shoes1.vtx[%d]" % i, q=True, ws=True, t=True) for i in range(n)]
print("L| true min distance after:", min_gap(), "cm")
cmds.file(save=True, type="mayaBinary")
print("L| saved", SRC)
maya.standalone.uninitialize()
