import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
import os
import shutil

scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
out_dir = r"D:\projects\ProjectAnimation\images\Chase_Storyboard_Renders"
cmds.file(scene, open=True, force=True)
cmds.currentTime(60)

cam_name = "Cam_Chase_Overview"
if cmds.objExists(cam_name):
    cmds.delete(cam_name)
cam_trans, cam_shape = cmds.camera(name=cam_name, focalLength=28.0, nearClipPlane=1.0, farClipPlane=10000.0)
cmds.setAttr(f"{cam_shape}.renderable", 1)

# Monster is at Z=248, Cube is at Z=418
# Place camera behind monster and elevated to frame both
cmds.setAttr(f"{cam_trans}.translateX", -40.0)
cmds.setAttr(f"{cam_trans}.translateY", 145.0)
cmds.setAttr(f"{cam_trans}.translateZ", 90.0)

loc = cmds.spaceLocator(name="temp_target_loc")[0]
cmds.setAttr(f"{loc}.translateX", 0.0)
cmds.setAttr(f"{loc}.translateY", 80.0)
cmds.setAttr(f"{loc}.translateZ", 330.0)

cn = cmds.aimConstraint(loc, cam_trans, aimVector=[0, 0, -1], upVector=[0, 1, 0], worldUpType="vector", worldUpVector=[0, 1, 0])[0]
rot = cmds.getAttr(f"{cam_trans}.rotate")[0]
cmds.delete(cn)
cmds.delete(loc)
cmds.setAttr(f"{cam_trans}.rotate", rot[0], rot[1], rot[2])

print(f"Cam positioned: {cmds.getAttr(f'{cam_trans}.translate')[0]}, rot={rot}")

# Check renderer
cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")
res = cmds.render(cam_shape, x=960, y=540)
dst_png = os.path.join(out_dir, "Monster_Chasing_Cube_f60.png")
shutil.copyfile(res, dst_png)
print(f"SUCCESS: {dst_png}")
