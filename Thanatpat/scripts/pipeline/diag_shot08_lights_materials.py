"""Read-only: (1) real attribute names of the aiAreaLight shape (camera visibility), (2) shader base colours of the desk unit. Nothing is saved."""
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.loadPlugin("mtoa", quiet=True)
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot08.mb", open=True, force=True, loadReferenceDepth="all")
for l in cmds.ls("Shot08_Fill*", "transform1", "transform2", "transform3", long=False)[:6]:
    print("M| node", l, cmds.nodeType(l), "shapes", cmds.listRelatives(l, shapes=True), "parent", cmds.listRelatives(l, parent=True))
shp = [x for x in cmds.ls(type="aiAreaLight") if "ENV:" not in x][0]
print("M| area light shape", shp, "attrs with cam/vis/visible:", [a for a in cmds.listAttr(shp) if any(k in a.lower() for k in ("cam", "visib", "primary"))])
desk = cmds.ls("ENV:Prop_OfficeDesk_and_Drawers", long=True)[0]
shapes = cmds.listRelatives(desk, shapes=True, fullPath=True)
sgs = sorted(set(cmds.listConnections(shapes, type="shadingEngine") or []))
print("M| desk shading groups:", sgs)
for sg in sgs:
    for sh in cmds.listConnections(sg + ".surfaceShader") or []:
        row = {}
        for a in ("baseColor", "base", "specularRoughness", "emission"):
            if cmds.attributeQuery(a, node=sh, exists=True):
                con = cmds.listConnections(sh + "." + a, s=True, d=False)
                row[a] = ("tex:" + con[0]) if con else cmds.getAttr(sh + "." + a)
        print("M|", sg, sh, cmds.nodeType(sh), row)
maya.standalone.uninitialize()
