import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.loadPlugin("mtoa", quiet=True)
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot05.mb", open=True, force=True, loadReferenceDepth="all")
def w(n): return [round(v,1) for v in cmds.xform(n, q=True, ws=True, t=True)]
g = "GRP_CAM_Shot05"
print("L| children of GRP:", cmds.listRelatives(g, children=True, fullPath=True))
print("L| GRP local t/r", cmds.getAttr(g+".translate")[0], cmds.getAttr(g+".rotate")[0], "parent", cmds.listRelatives(g, parent=True))
print("L| constraints:", cmds.ls(type="constraint"))
cam = cmds.listRelatives(g, children=True, type="transform")[0]
print("L| cam transform", cam, "local t", cmds.getAttr(cam+".translate")[0], "r", cmds.getAttr(cam+".rotate")[0], "s", cmds.getAttr(cam+".scale")[0])
print("L| cam ws", w(cam), "ro", [round(v,1) for v in cmds.xform(cam, q=True, ws=True, ro=True)])
print("L| keyframes on cam/grp:", cmds.keyframe(g, q=True, name=True), cmds.keyframe(cam, q=True, name=True))
for h in cmds.ls("*Hero*", type="transform") + cmds.ls("ENV:*CAM*", type="transform"):
    print("L| env cam", h, w(h), [round(v,1) for v in cmds.xform(h, q=True, ws=True, ro=True)])
# env floor extents from the master group
vs = cmds.xform("ENV:GRP_Backrooms_Level0_Master", q=True, bb=True, ws=True)
print("L| ENV master bbox", [round(v) for v in vs])
for n in cmds.ls("ENV:*", type="transform")[:0]: pass
fl = [t for t in cmds.ls("ENV:*", type="transform") if "floor" in t.lower() or "carpet" in t.lower()][:6]
print("L| floor-ish", fl)
for f in fl[:3]:
    print("L|  ", f, [round(v) for v in cmds.xform(f, q=True, bb=True, ws=True)])
maya.standalone.uninitialize()
