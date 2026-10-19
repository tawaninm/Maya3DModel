import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot10.mb", open=True, force=True, loadReferenceDepth="all")
s = cmds.expression("ENV:EXPR_Monster_Panel_Flicker", q=True, string=True)
print("F| EXPR:", s.replace("\n", " ## "))
ls = cmds.ls("ENV:*", type="aiAreaLight")
named = [l for l in ls if "Fluorescent_Panel" in l]
print("F| panel lights:", len(named))
for l in named[:3]:
    print("F| ", l, "exposure conn:", cmds.listConnections(l + ".exposure", s=True, d=False, plugs=True), "value", round(cmds.getAttr(l + ".exposure"), 2))
print("F| positions of first 8 panels:", [(l.split(":")[-1][-12:], [round(v) for v in cmds.xform(cmds.listRelatives(l, parent=True)[0], q=True, ws=True, t=True)]) for l in named[:8]])
maya.standalone.uninitialize()
