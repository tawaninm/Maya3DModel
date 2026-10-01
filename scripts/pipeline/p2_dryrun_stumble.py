import sys
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
sys.path.insert(0, r"D:\projects\ProjectAnimation\scripts\pipeline")
from bake_mixamo_clip import bake_clip
cmds.loadPlugin("mtoa", quiet=True)
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot05.mb", open=True, force=True, loadReferenceDepth="all")
bake_clip(r"D:\projects\ProjectAnimation\raw_assets\mixamo\charlie\Stumble_Backwards.fbx", rig_ns="CHARLIE:", src_first=0, src_last=23, dst_first=1)
def w(n): return [round(v,1) for v in cmds.xform(n, q=True, ws=True, t=True)]
for f in (1, 6, 12, 18, 24):
    cmds.currentTime(f)
    print("L| f%02d hips" % f, w("CHARLIE:mixamorig:Hips"), "head", w("CHARLIE:mixamorig:Head"), "headtop", w("CHARLIE:mixamorig:HeadTop_End"),
          "footL", w("CHARLIE:mixamorig:LeftFoot"), "footR", w("CHARLIE:mixamorig:RightFoot"))
o = "defaultArnoldRenderOptions"
if not cmds.objExists(o):
    import mtoa.core; mtoa.core.createOptions()
for a in ("lightLinking", "shadowLinking", "skipLicenseCheck", "renderDevice", "AASamples", "GIDiffuseSamples", "GIDiffuseDepth", "GITotalDepth"):
    print("L| opt", a, cmds.getAttr(o + "." + a) if cmds.attributeQuery(a, node=o, exists=True) else "n/a")
print("L| currentRenderer", cmds.getAttr("defaultRenderGlobals.currentRenderer"))
print("L| LIGHT_MASTER", [(n, cmds.getAttr(n + ".exposure")) for n in cmds.ls("*LIGHT_MASTER*") if cmds.attributeQuery("exposure", node=n, exists=True)])
print("L| monster vis", [(n, cmds.getAttr(n + ".visibility")) for n in ("MONSTER:GRP_Monster_Mixamo", "MONSTER:Monster_Buff_Blobbell")])
print("L| renderable cams", [c for c in cmds.ls(type="camera") if cmds.getAttr(c + ".renderable")])
print("L| ENV walls near origin (name, bbox) within 600cm of (0,0):")
for t in cmds.ls("ENV:*", type="transform"):
    if "wall" in t.lower() or "pillar" in t.lower():
        bb = cmds.xform(t, q=True, bb=True, ws=True)
        cx, cz = (bb[0] + bb[3]) / 2, (bb[2] + bb[5]) / 2
        if abs(cx) < 700 and abs(cz) < 700:
            print("L|  ", t, [round(v) for v in bb])
maya.standalone.uninitialize()
