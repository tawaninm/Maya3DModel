"""
=============================================================================
Rig and Animate Main Character in Backrooms Chase Scene
- Fixes Position to run directly ahead of Monster_Master_GRP (Frames 1-120)
- Builds full Humanoid Joint Rig (Spine, Head, Arms, Legs)
- Fixes T-Pose: Poses into forward dynamic sprint with arm swings & leg runs
- Aligns floor to Y = -11.90
=============================================================================
"""

import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
import math
import os

def build_chase_mainchar():
    scene_path = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_MainCharacter_Scene.mb"
    fbx_path = r"D:\projects\ProjectAnimation\Nannapas\main_char.fbx"

    if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
        cmds.loadPlugin("fbxmaya")

    cmds.file(scene_path, open=True, force=True)

    # 1. Clean up old MainChar_Grp and loose character joints if any
    old_nodes = ["MainChar_Grp", "Jnt_Root", "Jnt_Spine", "Jnt_Chest", "Jnt_Head",
                 "MainChar_Ctrl_Master", "MainChar_Rig_GRP"]
    for n in old_nodes:
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception as e:
                print(f"Notice deleting {n}: {e}")

    # Also remove any dangling Charlie / unused quickrig character transforms
    for extra in ["MainCharacter_Master_GRP", "CHARLIE:QuickRigCharacter2_Reference1", "group"]:
        if cmds.objExists(extra):
            try:
                cmds.delete(extra)
            except Exception:
                pass

    # 2. Import fresh clean FBX
    before_nodes = set(cmds.ls(assemblies=True))
    cmds.file(fbx_path, i=True, mergeNamespacesOnClash=False, namespace="CHAR", returnNewNodes=True)
    after_nodes = set(cmds.ls(assemblies=True))
    new_assemblies = list(after_nodes - before_nodes)
    print("Imported assemblies:", new_assemblies)

    # Group all imported pieces into a single MainChar_Grp
    main_grp = cmds.group(em=True, name="MainChar_Grp")
    for a in new_assemblies:
        if cmds.objExists(a):
            cmds.parent(a, main_grp)

    # 3. Normalize Model: Scale to target height (150cm) and center pivot
    bb = cmds.exactWorldBoundingBox(main_grp)
    orig_w = bb[3] - bb[0]
    orig_h = bb[4] - bb[1]
    orig_d = bb[5] - bb[2]
    orig_cx = (bb[0] + bb[3]) / 2.0
    orig_cy_bottom = bb[1]
    orig_cz = (bb[2] + bb[5]) / 2.0

    target_h = 150.0
    scale_factor = target_h / max(orig_h, 0.001)

    # Center mesh vertices or shift group pivot
    cmds.xform(main_grp, pivots=[orig_cx, orig_cy_bottom, orig_cz], ws=True)
    cmds.move(-orig_cx, -orig_cy_bottom, -orig_cz, main_grp, r=True)
    cmds.makeIdentity(main_grp, apply=True, t=1, r=1, s=1, n=0)

    cmds.scale(scale_factor, scale_factor, scale_factor, main_grp)
    cmds.makeIdentity(main_grp, apply=True, t=1, r=1, s=1, n=0)

    # Check bounds after normalization
    bb_norm = cmds.exactWorldBoundingBox(main_grp)
    print(f"Normalized MainChar bounds: {bb_norm}")
    # Now model bottom is at Y=0, center is at X=0, Z=0, top is at Y=150.0

    # 4. Build Complete Humanoid Skeleton Rig
    cmds.select(clear=True)
    
    # Spine & Head Chain
    jnt_root = cmds.joint(name="MC_Jnt_Root", p=(0, 70.0, 0))
    jnt_spine = cmds.joint(name="MC_Jnt_Spine", p=(0, 92.0, 0))
    jnt_chest = cmds.joint(name="MC_Jnt_Chest", p=(0, 114.0, 0))
    jnt_neck  = cmds.joint(name="MC_Jnt_Neck", p=(0, 128.0, 0))
    jnt_head  = cmds.joint(name="MC_Jnt_Head", p=(0, 142.0, 0))

    # Left Arm
    cmds.select(jnt_chest)
    jnt_clav_l = cmds.joint(name="MC_Jnt_Clavicle_L", p=(10.0, 114.0, 0))
    jnt_shld_l = cmds.joint(name="MC_Jnt_Shoulder_L", p=(24.0, 112.0, 0))
    jnt_elbw_l = cmds.joint(name="MC_Jnt_Elbow_L",    p=(44.0, 106.0, 0))
    jnt_hand_l = cmds.joint(name="MC_Jnt_Hand_L",     p=(64.0, 98.0, 0))

    # Right Arm
    cmds.select(jnt_chest)
    jnt_clav_r = cmds.joint(name="MC_Jnt_Clavicle_R", p=(-10.0, 114.0, 0))
    jnt_shld_r = cmds.joint(name="MC_Jnt_Shoulder_R", p=(-24.0, 112.0, 0))
    jnt_elbw_r = cmds.joint(name="MC_Jnt_Elbow_R",    p=(-44.0, 106.0, 0))
    jnt_hand_r = cmds.joint(name="MC_Jnt_Hand_R",     p=(-64.0, 98.0, 0))

    # Left Leg
    cmds.select(jnt_root)
    jnt_hip_l  = cmds.joint(name="MC_Jnt_Hip_L",   p=(12.0, 68.0, 0))
    jnt_knee_l = cmds.joint(name="MC_Jnt_Knee_L",  p=(12.0, 36.0, 0))
    jnt_ankl_l = cmds.joint(name="MC_Jnt_Ankle_L", p=(12.0, 10.0, 0))
    jnt_foot_l = cmds.joint(name="MC_Jnt_Foot_L",  p=(12.0, 0.0, 6.0))

    # Right Leg
    cmds.select(jnt_root)
    jnt_hip_r  = cmds.joint(name="MC_Jnt_Hip_R",   p=(-12.0, 68.0, 0))
    jnt_knee_r = cmds.joint(name="MC_Jnt_Knee_R",  p=(-12.0, 36.0, 0))
    jnt_ankl_r = cmds.joint(name="MC_Jnt_Ankle_R", p=(-12.0, 10.0, 0))
    jnt_foot_r = cmds.joint(name="MC_Jnt_Foot_R",  p=(-12.0, 0.0, 6.0))

    all_mc_joints = [
        jnt_root, jnt_spine, jnt_chest, jnt_neck, jnt_head,
        jnt_clav_l, jnt_shld_l, jnt_elbw_l, jnt_hand_l,
        jnt_clav_r, jnt_shld_r, jnt_elbw_r, jnt_hand_r,
        jnt_hip_l, jnt_knee_l, jnt_ankl_l, jnt_foot_l,
        jnt_hip_r, jnt_knee_r, jnt_ankl_r, jnt_foot_r
    ]

    # Group Skeleton
    rig_grp = cmds.group(jnt_root, name="MainChar_Rig_GRP")

    # 5. Bind Skin cleanly to meshes
    # Find all polygon meshes inside MainChar_Grp
    all_meshes = cmds.listRelatives(main_grp, allDescendents=True, type="mesh") or []
    mesh_transforms = list(set([cmds.listRelatives(m, parent=True)[0] for m in all_meshes]))
    print(f"Binding {len(mesh_transforms)} meshes to humanoid skeleton...")

    for mesh_node in mesh_transforms:
        try:
            cmds.skinCluster(all_mc_joints, mesh_node, toSelectedBones=True,
                             bindMethod=0, normalizeWeights=1, weightDistribution=0,
                             mi=4, omi=True, name=f"MC_Skin_{mesh_node.split(':')[-1]}")
        except Exception as err:
            print(f"Skin binding notice on {mesh_node}: {err}")

    # Parent Rig and Model under MainChar_Grp for master transforms
    cmds.parent(rig_grp, main_grp)

    # 6. Break T-Pose into a Natural Sprint/Running Posture
    # - Arms down from T-pose (Shoulders ~ -55 to -60 deg on Z)
    # - Elbows bent forward ~ 75-80 deg
    # - Torso leaned forward ~ 14 deg for forward sprint velocity
    # - Head facing forward and slightly up

    cmds.setAttr(f"{jnt_spine}.rotateX", 8.0)
    cmds.setAttr(f"{jnt_chest}.rotateX", 10.0)
    cmds.setAttr(f"{jnt_neck}.rotateX", -6.0) # head up looking ahead

    # Default rest sprint angles (breaking T-pose)
    cmds.setAttr(f"{jnt_shld_l}.rotateZ", -55.0)
    cmds.setAttr(f"{jnt_shld_l}.rotateY", 25.0)
    cmds.setAttr(f"{jnt_elbw_l}.rotateZ", 75.0)

    cmds.setAttr(f"{jnt_shld_r}.rotateZ", 55.0)
    cmds.setAttr(f"{jnt_shld_r}.rotateY", -25.0)
    cmds.setAttr(f"{jnt_elbw_r}.rotateZ", -75.0)

    # 7. Animate Sprint Cycles (No T-pose, Dynamic Arm Swings & Leg Runs)
    # Cycle duration = 16 frames (8 frames per step)
    cycle_len = 16
    for f in range(1, 121):
        phase = (f % cycle_len) / float(cycle_len) * 2.0 * math.pi
        
        # Legs: alternate forward/backward reach and knee bend
        hip_swing_l = math.sin(phase) * 35.0
        hip_swing_r = math.sin(phase + math.pi) * 35.0
        
        knee_bend_l = max(0, -math.sin(phase)) * 45.0 + 10.0
        knee_bend_r = max(0, -math.sin(phase + math.pi)) * 45.0 + 10.0
        
        cmds.setKeyframe(jnt_hip_l, attribute="rotateX", value=hip_swing_l, time=f)
        cmds.setKeyframe(jnt_knee_l, attribute="rotateX", value=knee_bend_l, time=f)
        
        cmds.setKeyframe(jnt_hip_r, attribute="rotateX", value=hip_swing_r, time=f)
        cmds.setKeyframe(jnt_knee_r, attribute="rotateX", value=knee_bend_r, time=f)

        # Arms: swing opposite to legs
        arm_swing_l = math.sin(phase + math.pi) * 38.0
        arm_swing_r = math.sin(phase) * 38.0
        
        cmds.setKeyframe(jnt_shld_l, attribute="rotateX", value=arm_swing_l, time=f)
        cmds.setKeyframe(jnt_shld_r, attribute="rotateX", value=arm_swing_r, time=f)

        # Torso & Pelvis Bobbing and twist
        bob_y = math.sin(phase * 2.0) * 3.5
        cmds.setKeyframe(jnt_root, attribute="translateY", value=70.0 + bob_y, time=f)
        twist_y = math.sin(phase) * 8.0
        cmds.setKeyframe(jnt_spine, attribute="rotateY", value=twist_y, time=f)

    # 8. Animate MainChar_Grp Trajectory: Run Directly Ahead of Monster_Master_GRP
    # Ground floor is Y = -11.90
    floor_y = -11.90

    # Keyframes precisely coordinated with Monster:
    # Monster: F1: [-1050, 300], F30: [-1450, 300], F60: [-1850, 300], F80: [-2200, 310], F95: [-2250, 430], F120: [-2250, 680]
    # Character runs ahead by ~300 to 350 units:
    
    trajectory_keys = [
        # (Frame, X, Y, Z, RotX, RotY, RotZ)
        (1,   -1380.0, floor_y, 300.0, 0.0, -90.0, 0.0),
        (30,  -1760.0, floor_y, 300.0, 0.0, -90.0, 0.0),
        (60,  -2120.0, floor_y, 300.0, 0.0, -90.0, 0.0),
        (75,  -2250.0, floor_y, 360.0, 0.0, -50.0, 0.0), # smooth corner turn
        (90,  -2250.0, floor_y, 560.0, 0.0,   0.0, 0.0), # full turn into new hallway
        (120, -2250.0, floor_y, 960.0, 0.0,   0.0, 0.0)  # sprinting down long corridor ahead
    ]

    for f, x, y, z, rx, ry, rz in trajectory_keys:
        cmds.setKeyframe(main_grp, attribute="translateX", value=x, time=f)
        cmds.setKeyframe(main_grp, attribute="translateY", value=y, time=f)
        cmds.setKeyframe(main_grp, attribute="translateZ", value=z, time=f)
        cmds.setKeyframe(main_grp, attribute="rotateX", value=rx, time=f)
        cmds.setKeyframe(main_grp, attribute="rotateY", value=ry, time=f)
        cmds.setKeyframe(main_grp, attribute="rotateZ", value=rz, time=f)

    # Set smooth tangents on the trajectory curves
    for attr in ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]:
        cmds.keyTangent(main_grp, attribute=attr, itt="spline", ott="spline")

    # 9. Verify Setup at Key Frames
    print("\n=== VERIFICATION OF RUN TRAJECTORY ===")
    for test_f in [1, 30, 60, 75, 90, 120]:
        cmds.currentTime(test_f)
        c_pos = cmds.xform(main_grp, q=True, ws=True, t=True)
        m_pos = cmds.xform("Monster_Master_GRP", q=True, ws=True, t=True)
        # distance in XZ plane
        dist = math.sqrt((c_pos[0] - m_pos[0])**2 + (c_pos[2] - m_pos[2])**2)
        print(f"Frame {test_f:3d}: Character=[{c_pos[0]:.1f}, {c_pos[1]:.1f}, {c_pos[2]:.1f}] | Monster=[{m_pos[0]:.1f}, {m_pos[1]:.1f}, {m_pos[2]:.1f}] | Lead Distance={dist:.1f} units")

    # 10. Save back to Scene
    saved_path = cmds.file(save=True, type="mayaBinary")
    print(f"\nSUCCESS: Successfully updated and saved scene to: {saved_path}")
    return saved_path

if __name__ == "__main__":
    build_chase_mainchar()
