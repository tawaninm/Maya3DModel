"""Part 1c: throw-away stage for the Charlie run test. Opens Charlie_Mixamo.mb, bakes Terrified_Run, adds skydome + grey floor + tracking camera,
saves ONLY scenes/Characters/_test_charlie_stage.mb, renders frames 1-12 (Arnold CPU 640x360)."""
import subprocess
import sys
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
sys.path.insert(0, r"D:\projects\ProjectAnimation\scripts\pipeline")
from bake_mixamo_clip import bake_clip

cmds.loadPlugin("mtoa", quiet=True)
SRC = r"D:\projects\ProjectAnimation\scenes\Characters\Charlie_Mixamo.mb"
DST = r"D:\projects\ProjectAnimation\scenes\Characters\_test_charlie_stage.mb"
OUTDIR = r"D:\projects\ProjectAnimation\movies\playblast\rigtest_charlie_v3"
cmds.file(SRC, open=True, force=True)
bake_clip(r"D:\projects\ProjectAnimation\raw_assets\mixamo\charlie\Terrified_Run.fbx", rig_ns="", src_first=0, src_last=11, dst_first=1)

cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")
try:
    import mtoa.core
    mtoa.core.createOptions()
except Exception as e:
    print("createOptions:", e)
o = "defaultArnoldRenderOptions"
cmds.setAttr(o + ".skipLicenseCheck", 0)
cmds.setAttr(o + ".renderDevice", 0)
cmds.setAttr(o + ".AASamples", 3)
cmds.setAttr(o + ".GIDiffuseSamples", 1)

floor = cmds.polyPlane(w=2000, h=2000, sx=1, sy=1, name="STAGE_floor")[0]
fs = cmds.shadingNode("aiStandardSurface", asShader=True, name="STAGE_floor_M")
cmds.setAttr(fs + ".baseColor", 0.5, 0.5, 0.5, type="double3")
fg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="STAGE_floor_SG")
cmds.connectAttr(fs + ".outColor", fg + ".surfaceShader", force=True)
cmds.sets(floor, forceElement=fg)
dome = cmds.shadingNode("aiSkyDomeLight", asLight=True)
cmds.setAttr(cmds.listRelatives(dome, shapes=True)[0] + ".intensity", 1.0)

cam, cshape = cmds.camera(name="STAGE_cam", focalLength=35)
cmds.xform(cam, ws=True, t=(90, 90, 380))
cmds.aimConstraint("mixamorig:Hips", cam, aimVector=(0, 0, -1), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(0, 1, 0))
cmds.setAttr(cshape + ".renderable", 1)
for c in ("persp", "top", "front", "side"):
    cmds.setAttr(c + "Shape.renderable", 0)
cmds.file(rename=DST)
cmds.file(save=True, type="mayaBinary")
cmd = [r"D:\AutoDesk\Maya2027\bin\Render.exe", "-r", "arnold", "-cam", cshape, "-s", "1", "-e", "12", "-x", "640", "-y", "360",
       "-rd", OUTDIR, "-im", "charlie_run", "-of", "png", "-pad", "4", DST]
r = subprocess.run(cmd, capture_output=True, text=True)
print("RENDER rc", r.returncode)
maya.standalone.uninitialize()
