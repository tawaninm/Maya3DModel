import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot10.mb", open=True, force=True, loadReferenceDepth="all")
e = "ENV:EXPR_Monster_Panel_Flicker"
print("F| expression:", cmds.expression(e, q=True, string=True))
print("F| LIGHT_MASTER attrs:", [(a, cmds.getAttr("ENV:LIGHT_MASTER." + a)) for a in (cmds.listAttr("ENV:LIGHT_MASTER", userDefined=True) or [])])
for l in cmds.ls("ENV:*", type="aiAreaLight")[:3]:
    print("F| light", l, [a for a in (cmds.listAttr(l, userDefined=True) or [])][:6])
print("F| floor/ceiling/walls:", [(n, [round(v) for v in cmds.exactWorldBoundingBox(n)]) for n in ("ENV:Arch_Floor_Moquette_1", "ENV:Arch_Wall_Sector_1") if cmds.objExists(n)])
maya.standalone.uninitialize()
