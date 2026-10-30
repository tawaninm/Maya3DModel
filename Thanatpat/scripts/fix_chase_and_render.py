import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
import os
import shutil

def fix_and_render():
    scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
    out_dir = r"D:\projects\ProjectAnimation\images\Chase_Storyboard_Renders"
    os.makedirs(out_dir, exist_ok=True)

    cmds.file(scene, open=True, force=True)

    # 1. Update Monster animation in open room bounds (Z: 50 -> 450)
    monster_ctrl = "MONSTER:CTRL_Master"
    if cmds.objExists(monster_ctrl):
        cmds.cutKey(monster_ctrl, attribute="translateZ")
        cmds.setKeyframe(monster_ctrl, attribute="translateZ", value=50.0, time=1)
        cmds.setKeyframe(monster_ctrl, attribute="translateZ", value=450.0, time=120)
        cmds.setAttr(f"{monster_ctrl}.translateX", 0.0)
        cmds.setAttr(f"{monster_ctrl}.translateY", 61.43)
        cmds.setAttr(f"{monster_ctrl}.rotateY", 0.0)

    # 2. Update Cube animation ahead of monster (Z: 200 -> 600)
    cube = "MainChar_Proxy_Cube"
    floor_y = 73.1
    if cmds.objExists(cube):
        cmds.cutKey(cube, attribute="translateZ")
        cmds.cutKey(cube, attribute="translateX")
        cmds.setKeyframe(cube, attribute="translateZ", value=200.0, time=1)
        cmds.setKeyframe(cube, attribute="translateZ", value=600.0, time=120)
        cmds.setKeyframe(cube, attribute="translateX", value=0.0, time=1)
        cmds.setKeyframe(cube, attribute="translateX", value=0.0, time=120)

    # 3. Update Camera 12 (Shot 12: Dutch Angle Look-Back at Monster)
    # Cam12 sits slightly ahead & beside Cube, looking backwards towards -Z (at Monster)
    cam12 = "Cam_Shot12_DutchTurn1"
    if not cmds.objExists(cam12):
        cams = [c for c in cmds.ls(type="camera") if "Shot12" in c]
        cam12 = cmds.listRelatives(cams[0], parent=True)[0]

    cmds.cutKey(cam12, attribute="translateX")
    cmds.cutKey(cam12, attribute="translateY")
    cmds.cutKey(cam12, attribute="translateZ")
    cmds.cutKey(cam12, attribute="rotateX")
    cmds.cutKey(cam12, attribute="rotateY")
    cmds.cutKey(cam12, attribute="rotateZ")

    cmds.setKeyframe(cam12, attribute="translateX", value=45.0, time=1)
    cmds.setKeyframe(cam12, attribute="translateY", value=120.0, time=1)
    cmds.setKeyframe(cam12, attribute="translateZ", value=260.0, time=1)
    cmds.setKeyframe(cam12, attribute="rotateX", value=-4.0, time=1)
    cmds.setKeyframe(cam12, attribute="rotateY", value=-162.0, time=1)
    cmds.setKeyframe(cam12, attribute="rotateZ", value=14.0, time=1)

    cmds.setKeyframe(cam12, attribute="translateX", value=45.0, time=120)
    cmds.setKeyframe(cam12, attribute="translateY", value=120.0, time=120)
    cmds.setKeyframe(cam12, attribute="translateZ", value=660.0, time=120)
    cmds.setKeyframe(cam12, attribute="rotateX", value=-4.0, time=120)
    cmds.setKeyframe(cam12, attribute="rotateY", value=-162.0, time=120)
    cmds.setKeyframe(cam12, attribute="rotateZ", value=14.0, time=120)

    # 4. Update Camera 13 (Shot 13: Dynamic Chase Tracking behind Monster & Cube)
    cam13 = "Cam_Shot13_ChaseRunning1"
    if not cmds.objExists(cam13):
        cams = [c for c in cmds.ls(type="camera") if "Shot13" in c]
        cam13 = cmds.listRelatives(cams[0], parent=True)[0]

    cmds.cutKey(cam13, attribute="translateX")
    cmds.cutKey(cam13, attribute="translateY")
    cmds.cutKey(cam13, attribute="translateZ")
    cmds.cutKey(cam13, attribute="rotateX")
    cmds.cutKey(cam13, attribute="rotateY")
    cmds.cutKey(cam13, attribute="rotateZ")

    cmds.setKeyframe(cam13, attribute="translateX", value=-45.0, time=1)
    cmds.setKeyframe(cam13, attribute="translateY", value=140.0, time=1)
    cmds.setKeyframe(cam13, attribute="translateZ", value=-10.0, time=1)
    cmds.setKeyframe(cam13, attribute="rotateX", value=-6.0, time=1)
    cmds.setKeyframe(cam13, attribute="rotateY", value=6.0, time=1)
    cmds.setKeyframe(cam13, attribute="rotateZ", value=-3.0, time=1)

    cmds.setKeyframe(cam13, attribute="translateX", value=-45.0, time=120)
    cmds.setKeyframe(cam13, attribute="translateY", value=140.0, time=120)
    cmds.setKeyframe(cam13, attribute="translateZ", value=390.0, time=120)
    cmds.setKeyframe(cam13, attribute="rotateX", value=-6.0, time=120)
    cmds.setKeyframe(cam13, attribute="rotateY", value=6.0, time=120)
    cmds.setKeyframe(cam13, attribute="rotateZ", value=-3.0, time=120)

    # Save scene
    cmds.file(save=True, type="mayaBinary")
    print("Scene updated with open-hallway coordinates.")

    # 5. Render Frame 60 for both shots
    cmds.currentTime(60)
    cam12_shape = cmds.listRelatives(cam12, shapes=True)[0]
    cam13_shape = cmds.listRelatives(cam13, shapes=True)[0]

    print(f"Rendering {cam12_shape} at frame 60...")
    res12 = cmds.render(cam12_shape, x=960, y=540)
    dst12_png = os.path.join(out_dir, "Shot12_DutchAngle_LookBack_f60.png")
    shutil.copyfile(res12, dst12_png)
    print(f"Saved Shot 12: {dst12_png}")

    print(f"Rendering {cam13_shape} at frame 60...")
    res13 = cmds.render(cam13_shape, x=960, y=540)
    dst13_png = os.path.join(out_dir, "Shot13_DynamicChase_Running_f60.png")
    shutil.copyfile(res13, dst13_png)
    print(f"Saved Shot 13: {dst13_png}")

if __name__ == "__main__":
    fix_and_render()
