import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot05.mb", open=True, force=True, loadReferenceDepth="all")
print("L| range", cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True), "fps unit", cmds.currentUnit(q=True, time=True))
shape = cmds.listRelatives("CAM_Shot05", shapes=True)[0]
print("L| focal f1,36,37,42,48", [round(cmds.getAttr(shape + ".focalLength", time=t), 1) for t in (1, 36, 37, 42, 48)])
c = cmds.keyframe("CHARLIE:mixamorig:Hips", q=True, attribute="translateZ", timeChange=True)
print("L| hips keys", int(min(c)), "to", int(max(c)), "count", len(c))
print("L| hips z f1,24,47,48", [round(cmds.getAttr("CHARLIE:mixamorig:Hips.translateZ", time=t), 2) for t in (1, 24, 47, 48)])
maya.standalone.uninitialize()
