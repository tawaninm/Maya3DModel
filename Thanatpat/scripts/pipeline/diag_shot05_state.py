import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.loadPlugin("mtoa", quiet=True)
import sys
for n in (5, 6, 7):
    p = r"D:\projects\ProjectAnimation\scenes\Shots\Shot%02d.mb" % n
    cmds.file(p, open=True, force=True, loadReferenceDepth="all")
    curves = cmds.ls(type="animCurve")
    refs = cmds.file(q=True, reference=True)
    keyed = {}
    for c in curves:
        ns = c.split(":")[0] if ":" in c else "(local)"
        keyed[ns] = keyed.get(ns, 0) + 1
    print("SHOT%02d" % n, "refs", [r.replace("\\", "/").split("/")[-1] for r in refs])
    print("  animCurves total", len(curves), "by ns", keyed)
    print("  range", cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True))
    cams = [c for c in cmds.ls(type="camera") if "CAM_Shot" in c]
    print("  cams", cams, [cmds.getAttr(c + ".renderable") for c in cams])
    for c in cams:
        par = cmds.listRelatives(c, parent=True)[0]
        print("  cam parent chain", cmds.listRelatives(par, parent=True), "focal@1,24", [cmds.getAttr(c + ".focalLength", time=t) for t in (1, 12, 24)])
    print("  expressions", cmds.ls(type="expression"))
maya.standalone.uninitialize()
