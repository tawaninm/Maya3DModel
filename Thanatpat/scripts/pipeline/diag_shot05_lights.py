import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.loadPlugin("mtoa", quiet=True)
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot05.mb", open=True, force=True, loadReferenceDepth="all")
lm = cmds.ls("*LIGHT_MASTER", recursive=True)
print("L| LIGHT_MASTER nodes", lm)
for n in lm:
    for a in ("exposure", "flickerEnable"):
        if cmds.attributeQuery(a, node=n, exists=True):
            print("L|  ", n, a, cmds.getAttr(n + "." + a))
cx, cz = 0.0, -60.0
rows = []
for l in cmds.ls(type="aiAreaLight") + cmds.ls(type="aiSkyDomeLight") + cmds.ls(type="areaLight") + cmds.ls(type="pointLight"):
    t = cmds.listRelatives(l, parent=True)[0]
    x, y, z = cmds.xform(t, q=True, ws=True, t=True)
    d = ((x - cx) ** 2 + (z - cz) ** 2) ** 0.5
    rows.append((round(d), t, cmds.nodeType(l), round(x), round(y), round(z), cmds.getAttr(l + ".intensity"), cmds.getAttr(l + ".visibility") if cmds.attributeQuery("visibility", node=l, exists=True) else None))
rows.sort()
print("L| lights total", len(rows))
for r in rows[:8]:
    print("L|  dist,name,type,x,y,z,intensity,vis", r)
print("L| lightLinking", cmds.getAttr("defaultArnoldRenderOptions.lightLinking"))
print("L| light layers off?", [(l, cmds.getAttr(l + ".visibility")) for l in cmds.ls(type="aiAreaLight")][:3])
maya.standalone.uninitialize()
