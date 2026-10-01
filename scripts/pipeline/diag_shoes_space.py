import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.file(r"D:\projects\ProjectAnimation\scenes\Characters\Charlie_Mixamo.mb", open=True, force=True)
tr = "shoes1"
print("L| matrix", [round(v, 3) for v in cmds.xform(tr, q=True, ws=True, m=True)])
orig = [s for s in cmds.listRelatives(tr, shapes=True, fullPath=True) if cmds.getAttr(s + ".intermediateObject")][0]
n = cmds.polyEvaluate(orig, vertex=True)
o = [cmds.xform("%s.vtx[%d]" % (orig, i), q=True, os=True, t=True) for i in range(n)]
w = [cmds.xform("shoes1.vtx[%d]" % i, q=True, ws=True, t=True) for i in range(n)]
print("L| orig os x range", round(min(p[0] for p in o), 2), round(max(p[0] for p in o), 2), "y", round(min(p[1] for p in o), 2), round(max(p[1] for p in o), 2), "z", round(min(p[2] for p in o), 2), round(max(p[2] for p in o), 2))
print("L| deformed ws x range", round(min(p[0] for p in w), 2), round(max(p[0] for p in w), 2))
print("L| sample vtx0 orig os", [round(v, 2) for v in o[0]], "ws", [round(v, 2) for v in w[0]])
d = max(abs(o[i][k] - w[i][k]) for i in range(n) for k in range(3))
print("L| max |os - ws| over all verts", round(d, 4))
maya.standalone.uninitialize()
