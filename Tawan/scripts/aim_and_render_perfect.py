import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
import os
import shutil

def aim_camera_with_constraint(cam, target_pos, roll=0.0):
    loc = cmds.spaceLocator(name="temp_aim_target")[0]
    cmds.setAttr(f"{loc}.translateX", target_pos[0])
    cmds.setAttr(f"{loc}.translateY", target_pos[1])
    cmds.setAttr(f"{loc}.translateZ", target_pos[2])
    
    # In Maya, camera default aim is [0, 0, -1], up is [0, 1, 0]
    cn = cmds.aimConstraint(
        loc, cam,
        aimVector=[0, 0, -1],
        upVector=[0, 1, 0],
        worldUpType="vector",
        worldUpVector=[0, 1, 0]
    )[0]
    
    rot = cmds.getAttr(f"{cam}.rotate")[0]
    cmds.delete(cn)
    cmds.delete(loc)
    
    # Set rotation and add roll
    cmds.setAttr(f"{cam}.rotateX", rot[0])
    cmds.setAttr(f"{cam}.rotateY", rot[1])
    cmds.setAttr(f"{cam}.rotateZ", rot[2] + roll)

def setup_and_render():
    scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
    out_dir = r"D:\projects\ProjectAnimation\images\Chase_Storyboard_Renders"
    os.makedirs(out_dir, exist_ok=True)

    cmds.file(scene, open=True, force=True)

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

    # -------------------------------------------------------------
    # Setup Cam 12 (Shot 12: Dutch Look-Back at Monster)
    # -------------------------------------------------------------
    cam12 = "Cam_Shot12_DutchTurn1"
    cmds.cutKey(cam12)
    # Set focal length
    cam12_shape = cmds.listRelatives(cam12, shapes=True)[0]
    cmds.setAttr(f"{cam12_shape}.focalLength", 30.0)
    
    for t in [1, 60, 120]:
        cmds.currentTime(t)
        mz = cmds.getAttr(f"{monster_ctrl}.translateZ")
        cz = cmds.getAttr(f"{cube}.translateZ")
        # Position slightly to the right of corridor, ahead of cube
        # X=45, Y=95, Z=cz+50. Looking back at monster's chest/face [0, 80, mz]
        c_pos = [45.0, 95.0, cz + 50.0]
        cmds.setAttr(f"{cam12}.translateX", c_pos[0])
        cmds.setAttr(f"{cam12}.translateY", c_pos[1])
        cmds.setAttr(f"{cam12}.translateZ", c_pos[2])
        aim_camera_with_constraint(cam12, [0.0, 75.0, mz], roll=14.0)
        cmds.setKeyframe(cam12, time=t)

    # -------------------------------------------------------------
    # Setup Cam 13 (Shot 13: Dynamic Sprint Chase Tracking)
    # -------------------------------------------------------------
    cam13 = "Cam_Shot13_ChaseRunning1"
    cmds.cutKey(cam13)
    cam13_shape = cmds.listRelatives(cam13, shapes=True)[0]
    cmds.setAttr(f"{cam13_shape}.focalLength", 24.0)

    for t in [1, 60, 120]:
        cmds.currentTime(t)
        mz = cmds.getAttr(f"{monster_ctrl}.translateZ")
        cz = cmds.getAttr(f"{cube}.translateZ")
        # Position behind Monster, offset to left: X=-45, Y=115, Z=mz-190
        # Looking down corridor at midway point [0, 85, (mz + cz)/2]
        c_pos = [-45.0, 115.0, mz - 190.0]
        cmds.setAttr(f"{cam13}.translateX", c_pos[0])
        cmds.setAttr(f"{cam13}.translateY", c_pos[1])
        cmds.setAttr(f"{cam13}.translateZ", c_pos[2])
        aim_camera_with_constraint(cam13, [0.0, 85.0, (mz + cz) / 2.0], roll=-3.0)
        cmds.setKeyframe(cam13, time=t)

    cmds.file(save=True, type="mayaBinary")
    print("Scene saved with Maya native aimConstraint alignment.")

    # Render frame 60
    cmds.currentTime(60)

    # Render Shot 12
    res12 = cmds.render(cam12_shape, x=960, y=540)
    dst12_png = os.path.join(out_dir, "Shot12_DutchAngle_LookBack_f60.png")
    shutil.copyfile(res12, dst12_png)
    print(f"Shot 12 Rendered PNG: {dst12_png}")

    # Render Shot 13
    res13 = cmds.render(cam13_shape, x=960, y=540)
    dst13_png = os.path.join(out_dir, "Shot13_DynamicChase_Running_f60.png")
    shutil.copyfile(res13, dst13_png)
    print(f"Shot 13 Rendered PNG: {dst13_png}")

if __name__ == "__main__":
    setup_and_render()
