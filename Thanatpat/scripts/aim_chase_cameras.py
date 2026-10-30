import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
import math
import os
import shutil

def aim_at(cam, target_pos, roll=0.0):
    cam_pos = cmds.xform(cam, q=True, t=True, ws=True)
    dx = target_pos[0] - cam_pos[0]
    dy = target_pos[1] - cam_pos[1]
    dz = target_pos[2] - cam_pos[2]

    # In Maya, camera looks down -Z by default
    # rotY = atan2(dx, -dz)
    rot_y = math.degrees(math.atan2(dx, -dz))
    dist_xz = math.sqrt(dx*dx + dz*dz)
    rot_x = math.degrees(math.atan2(-dy, dist_xz))

    cmds.setAttr(f"{cam}.rotateX", rot_x)
    cmds.setAttr(f"{cam}.rotateY", rot_y)
    cmds.setAttr(f"{cam}.rotateZ", roll)
    return rot_x, rot_y, roll

def setup_and_render():
    scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
    out_dir = r"D:\projects\ProjectAnimation\images\Chase_Storyboard_Renders"
    os.makedirs(out_dir, exist_ok=True)

    cmds.file(scene, open=True, force=True)

    # Clean previous constraints if any
    for cam in ["Cam_Shot12_DutchTurn1", "Cam_Shot13_ChaseRunning1"]:
        if cmds.objExists(cam):
            cmds.cutKey(cam)

    monster_ctrl = "MONSTER:CTRL_Master"
    cube = "MainChar_Proxy_Cube"

    # Setup Monster (Z: 50 at f1 -> 450 at f120)
    cmds.cutKey(monster_ctrl, attribute="translateZ")
    cmds.setKeyframe(monster_ctrl, attribute="translateZ", value=50.0, time=1)
    cmds.setKeyframe(monster_ctrl, attribute="translateZ", value=450.0, time=120)
    cmds.setAttr(f"{monster_ctrl}.translateX", 0.0)
    cmds.setAttr(f"{monster_ctrl}.translateY", 61.43)
    cmds.setAttr(f"{monster_ctrl}.rotateY", 0.0)

    # Setup Cube (Z: 220 at f1 -> 620 at f120)
    cmds.cutKey(cube, attribute="translateZ")
    cmds.setKeyframe(cube, attribute="translateZ", value=220.0, time=1)
    cmds.setKeyframe(cube, attribute="translateZ", value=620.0, time=120)
    cmds.setAttr(f"{cube}.translateX", 0.0)
    cmds.setAttr(f"{cube}.translateY", 73.1)

    # Setup Cam 12 (Shot 12: Dutch Look-Back at Monster)
    # Positions beside Cube, looks back at Monster's chest [0, 80, monster_z]
    cam12 = "Cam_Shot12_DutchTurn1"
    for t in [1, 60, 120]:
        cmds.currentTime(t)
        mz = cmds.getAttr(f"{monster_ctrl}.translateZ")
        cz = cmds.getAttr(f"{cube}.translateZ")
        # Cam12 is slightly ahead of Cube and to the right
        c_pos = [35.0, 105.0, cz + 30.0]
        cmds.setAttr(f"{cam12}.translateX", c_pos[0])
        cmds.setAttr(f"{cam12}.translateY", c_pos[1])
        cmds.setAttr(f"{cam12}.translateZ", c_pos[2])
        aim_at(cam12, [0.0, 75.0, mz], roll=14.0)
        cmds.setKeyframe(cam12, time=t)

    # Setup Cam 13 (Shot 13: Dynamic Chase Tracking from behind)
    # Positions behind Monster, looks ahead at Cube [0, 80, cz]
    cam13 = "Cam_Shot13_ChaseRunning1"
    for t in [1, 60, 120]:
        cmds.currentTime(t)
        mz = cmds.getAttr(f"{monster_ctrl}.translateZ")
        cz = cmds.getAttr(f"{cube}.translateZ")
        # Cam13 is behind Monster and to the left
        c_pos = [-40.0, 135.0, mz - 160.0]
        cmds.setAttr(f"{cam13}.translateX", c_pos[0])
        cmds.setAttr(f"{cam13}.translateY", c_pos[1])
        cmds.setAttr(f"{cam13}.translateZ", c_pos[2])
        aim_at(cam13, [0.0, 75.0, (mz + cz) / 2.0], roll=-3.0)
        cmds.setKeyframe(cam13, time=t)

    cmds.file(save=True, type="mayaBinary")
    print("Scene saved with mathematically precise camera aim.")

    # Render frame 60
    cmds.currentTime(60)
    cam12_shape = cmds.listRelatives(cam12, shapes=True)[0]
    cam13_shape = cmds.listRelatives(cam13, shapes=True)[0]

    res12 = cmds.render(cam12_shape, x=960, y=540)
    dst12_png = os.path.join(out_dir, "Shot12_DutchAngle_LookBack_f60.png")
    shutil.copyfile(res12, dst12_png)
    print(f"Shot 12 PNG: {dst12_png}")

    res13 = cmds.render(cam13_shape, x=960, y=540)
    dst13_png = os.path.join(out_dir, "Shot13_DynamicChase_Running_f60.png")
    shutil.copyfile(res13, dst13_png)
    print(f"Shot 13 PNG: {dst13_png}")

if __name__ == "__main__":
    setup_and_render()
