"""
=============================================================================
Assemble Monster Rig into Backrooms Scene & Setup Natural Run/Chase Animation
Project: ProjectAnimation (Week 12-14 Milestone)
Target: scenes/Backrooms/Backrooms_Monster_Animation_Scene.mb
=============================================================================
"""

import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass
import maya.cmds as cmds
import os

def assemble_and_animate():
    backrooms_scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Furniture_Scene.mb"
    monster_rig = r"D:\projects\ProjectAnimation\scenes\Monster\Monster_Rigged.mb"
    out_scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Monster_Animation_Scene.mb"

    if not os.path.exists(backrooms_scene):
        raise FileNotFoundError(f"Backrooms scene not found: {backrooms_scene}")
    if not os.path.exists(monster_rig):
        raise FileNotFoundError(f"Monster rig not found: {monster_rig}")

    # 1. Open Backrooms environment
    cmds.file(backrooms_scene, open=True, force=True)

    # Clean existing reference or duplicate if any
    existing_refs = cmds.file(q=True, reference=True) or []
    for ref in existing_refs:
        if "Monster_Rigged" in ref:
            ref_node = cmds.file(ref, q=True, referenceNode=True)
            cmds.file(referenceNode=ref_node, removeReference=True)

    # 2. Reference Monster Rig with namespace MONSTER
    cmds.file(monster_rig, reference=True, namespace="MONSTER", ignoreVersion=True)

    rig_grp = "MONSTER:Monster_Rig_GRP"
    target_ctrl = "MONSTER:CTRL_Master"
    root_jnt = "MONSTER:JNT_Root"
    chest_jnt = "MONSTER:JNT_Chest"
    head_jnt = "MONSTER:JNT_Head"
    arm_l = "MONSTER:JNT_Shoulder_L"
    arm_r = "MONSTER:JNT_Shoulder_R"
    hip_l = "MONSTER:JNT_Hip_L"
    hip_r = "MONSTER:JNT_Hip_R"
    knee_l = "MONSTER:JNT_Knee_L"
    knee_r = "MONSTER:JNT_Knee_R"

    # Reset parent rig group to origin (strictly zero transform to prevent double transform)
    if cmds.objExists(rig_grp):
        cmds.setAttr(f"{rig_grp}.translateX", 0.0)
        cmds.setAttr(f"{rig_grp}.translateY", 0.0)
        cmds.setAttr(f"{rig_grp}.translateZ", 0.0)
        cmds.setAttr(f"{rig_grp}.rotateX", 0.0)
        cmds.setAttr(f"{rig_grp}.rotateY", 0.0)
        cmds.setAttr(f"{rig_grp}.rotateZ", 0.0)

    # 3. Position Monster: feet on floor (-11.90 carpet floor - (-73.33) feet rest = 61.43)
    if cmds.objExists(target_ctrl):
        cmds.setAttr(f"{target_ctrl}.translateX", 0.0)
        cmds.setAttr(f"{target_ctrl}.translateY", 61.43)
        cmds.setAttr(f"{target_ctrl}.translateZ", -350.0)
        cmds.setAttr(f"{target_ctrl}.rotateY", 0.0)

    # 4. Create Keyframe Run/Chase Animation (120 frames = 5 seconds at 24 fps)
    cmds.playbackOptions(minTime=1, maxTime=120)

    # Sprint forward from Z = -350 (frame 1) to Z = -80 (frame 120)
    if cmds.objExists(target_ctrl):
        cmds.setKeyframe(target_ctrl, attribute="translateZ", value=-350.0, time=1)
        cmds.setKeyframe(target_ctrl, attribute="translateZ", value=-80.0, time=120)

    # Torso Lean Forward (menacing posture)
    if cmds.objExists(chest_jnt):
        cmds.setKeyframe(chest_jnt, attribute="rotateX", value=18.0, time=1)
        cmds.setKeyframe(chest_jnt, attribute="rotateX", value=18.0, time=120)

    # Run Cycle Loops (Stride cycle every 20 frames)
    # Frame stride: 1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120
    for f in range(1, 121, 20):
        # Step 1: Left foot forward, Right foot back, Torso bob down
        if cmds.objExists(target_ctrl):
            cmds.setKeyframe(target_ctrl, attribute="translateY", value=61.43, time=f)
        if cmds.objExists(chest_jnt):
            cmds.setKeyframe(chest_jnt, attribute="rotateY", value=-8.0, time=f)
            cmds.setKeyframe(chest_jnt, attribute="rotateZ", value=4.0, time=f)
        if cmds.objExists(hip_l):
            cmds.setKeyframe(hip_l, attribute="rotateX", value=28.0, time=f)
        if cmds.objExists(knee_l):
            cmds.setKeyframe(knee_l, attribute="rotateX", value=12.0, time=f)
        if cmds.objExists(hip_r):
            cmds.setKeyframe(hip_r, attribute="rotateX", value=-25.0, time=f)
        if cmds.objExists(knee_r):
            cmds.setKeyframe(knee_r, attribute="rotateX", value=40.0, time=f)
        # Arms counter-swing (Right arm forward, Left arm back)
        if cmds.objExists(arm_r):
            cmds.setKeyframe(arm_r, attribute="rotateX", value=35.0, time=f)
        if cmds.objExists(arm_l):
            cmds.setKeyframe(arm_l, attribute="rotateX", value=-30.0, time=f)

        f_mid = f + 10
        if f_mid <= 120:
            # Step 2: Right foot forward, Left foot back, Torso bob down
            if cmds.objExists(target_ctrl):
                cmds.setKeyframe(target_ctrl, attribute="translateY", value=64.5, time=f_mid-5)
                cmds.setKeyframe(target_ctrl, attribute="translateY", value=61.43, time=f_mid)
            if cmds.objExists(chest_jnt):
                cmds.setKeyframe(chest_jnt, attribute="rotateY", value=8.0, time=f_mid)
                cmds.setKeyframe(chest_jnt, attribute="rotateZ", value=-4.0, time=f_mid)
            if cmds.objExists(hip_l):
                cmds.setKeyframe(hip_l, attribute="rotateX", value=-25.0, time=f_mid)
            if cmds.objExists(knee_l):
                cmds.setKeyframe(knee_l, attribute="rotateX", value=40.0, time=f_mid)
            if cmds.objExists(hip_r):
                cmds.setKeyframe(hip_r, attribute="rotateX", value=28.0, time=f_mid)
            if cmds.objExists(knee_r):
                cmds.setKeyframe(knee_r, attribute="rotateX", value=12.0, time=f_mid)
            # Arms counter-swing (Left arm forward, Right arm back)
            if cmds.objExists(arm_l):
                cmds.setKeyframe(arm_l, attribute="rotateX", value=35.0, time=f_mid)
            if cmds.objExists(arm_r):
                cmds.setKeyframe(arm_r, attribute="rotateX", value=-30.0, time=f_mid)

    # 5. Save Assembled Animation Scene
    cmds.file(rename=out_scene)
    saved = cmds.file(save=True, type="mayaBinary")
    print(f"SUCCESS: Assembled animation scene with active run cycle saved to {saved}")
    return saved

if __name__ == "__main__":
    assemble_and_animate()
