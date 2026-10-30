import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.loadPlugin("mtoa", quiet=True)
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot05.mb", open=True, force=True, loadReferenceDepth="all")
print("L| transforms top-level:", cmds.ls(assemblies=True))
for n in ("GRP_CAM_Shot05", "CAM_Shot05", "CHARLIE:GRP_Charlie_Placement", "MONSTER:GRP_Monster_Placement"):
    if cmds.objExists(n):
        print("L|", n, "t", [round(v,1) for v in cmds.xform(n, q=True, ws=True, t=True)], "ro", [round(v,1) for v in cmds.xform(n, q=True, ws=True, ro=True)])
    else:
        print("L|", n, "MISSING")
print("L| CHARLIE nodes top:", [n for n in cmds.ls("CHARLIE:*", assemblies=True)])
print("L| MONSTER nodes top:", [n for n in cmds.ls("MONSTER:*", assemblies=True)])
cam = "CAM_Shot05Shape5"
print("L| film", cmds.getAttr(cam+".horizontalFilmAperture"), cmds.getAttr(cam+".verticalFilmAperture"), "res", cmds.getAttr("defaultResolution.width"), cmds.getAttr("defaultResolution.height"))
print("L| hips world", [round(v,1) for v in cmds.xform("CHARLIE:mixamorig:Hips", q=True, ws=True, t=True)])
print("L| monster hips", [round(v,1) for v in cmds.xform("MONSTER:mixamorig:Hips", q=True, ws=True, t=True)] if cmds.objExists("MONSTER:mixamorig:Hips") else "n/a")
print("L| shot ranges", cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True), "fps", cmds.currentUnit(q=True, time=True))
print("L| env floor/walls near origin: ENV nodes", len(cmds.ls("ENV:*")))
maya.standalone.uninitialize()
