import maya.standalone, math
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.loadPlugin("mtoa", quiet=True)
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot05.mb", open=True, force=True, loadReferenceDepth="all")
cmds.currentUnit(time="film")
for f in (47, 48, 49):
    cmds.currentTime(f)
    bad = []
    for n in cmds.ls(type=("joint", "transform")):
        for a in ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"):
            try:
                v = cmds.getAttr(n + "." + a)
            except Exception:
                continue
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v) or abs(v) > 1e6):
                bad.append((n, a, v))
    cam = "CAM_Shot05"; sh = cmds.listRelatives(cam, shapes=True)[0]
    print("D| f%d bad values: %s | cam t %s r %s focal %s" % (f, bad[:5], [round(v, 1) for v in cmds.xform(cam, q=True, ws=True, t=True)], [round(v, 1) for v in cmds.xform(cam, q=True, ws=True, ro=True)], round(cmds.getAttr(sh + ".focalLength"), 2)))
    hp = cmds.xform("CHARLIE:mixamorig:Head", q=True, ws=True, t=True)
    print("D|   head", [round(v, 1) for v in hp], "light exposure", cmds.getAttr("ENV:LIGHT_MASTER.exposure"), "keys on cam focal:", cmds.keyframe(sh + ".focalLength", q=True, timeChange=True))
maya.standalone.uninitialize()
