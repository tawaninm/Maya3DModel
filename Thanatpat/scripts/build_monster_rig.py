"""
=============================================================================
Procedural Lean Biped Rig Generator for Monster_Buff_Blobbell (Maya / Arnold)
Project: ProjectAnimation (Week 12-14 Milestone)
Target: scenes/Monster/MonsterMain.mb -> scenes/Monster/Monster_Rigged.mb
=============================================================================
"""

import maya.cmds as cmds
import os

def create_ctrl(name, shape="circle", radius=10.0, color=17):
    """Creates a clean NURBS curve controller with colored wireframe."""
    if shape == "circle":
        ctrl = cmds.circle(name=name, radius=radius, normal=(0, 1, 0), ch=False)[0]
    elif shape == "box":
        r = radius
        pts = [(-r,r,-r),(r,r,-r),(r,r,r),(-r,r,r),(-r,r,-r),(-r,-r,-r),(r,-r,-r),(r,-r,r),(-r,-r,r),(-r,-r,-r),(r,-r,-r),(r,r,-r),(r,r,r),(r,-r,r),(-r,-r,r),(-r,r,r)]
        ctrl = cmds.curve(name=name, d=1, p=pts)
    else:
        ctrl = cmds.circle(name=name, radius=radius, normal=(0, 0, 1), ch=False)[0]

    # Color index in Maya: 17=Yellow, 6=Blue (Left), 13=Red (Right)
    cmds.setAttr(f"{ctrl}.overrideEnabled", 1)
    cmds.setAttr(f"{ctrl}.overrideColor", color)
    return ctrl

def build_monster_skeleton():
    mesh_name = "Monster_Buff_Blobbell"
    if not cmds.objExists(mesh_name):
        raise RuntimeError(f"Mesh '{mesh_name}' not found in current scene!")

    # 1. Clean up old turntable reel elements and old skinCluster/joints
    for old_obj in ["Reel_Showcase_GRP", "Reel_StudioFloor_GEO", "Reel_StudioLights_GRP", "Reel_Cam", "Monster_Rig_GRP", "Monster_Geometry_GRP", "Monster_Controllers_GRP", "Monster_Skeleton_GRP"]:
        if cmds.objExists(old_obj):
            cmds.delete(old_obj)

    # Ensure mesh is parented to world root before binding
    parent_node = cmds.listRelatives(mesh_name, parent=True)
    if parent_node:
        cmds.parent(mesh_name, world=True)

    # Remove existing skinClusters if any
    old_clusters = cmds.ls(type="skinCluster")
    if old_clusters:
        cmds.delete(old_clusters)

    # Delete history on mesh
    cmds.delete(mesh_name, ch=True)

    # Freeze transformations on mesh so bind pose is clean
    cmds.select(mesh_name)
    cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)

    # 2. Bone Joint Hierarchy (Coordinates scaled to Blobbell BBox: Y: -73.3 to +73.3, Height: 146.7)
    cmds.select(clear=True)
    root_jnt = cmds.joint(name="JNT_Root", position=(0, 0, 0))
    spine1 = cmds.joint(name="JNT_Spine1", position=(0, 15, 0))
    spine2 = cmds.joint(name="JNT_Spine2", position=(0, 30, 0))
    chest = cmds.joint(name="JNT_Chest", position=(0, 45, 0))
    neck = cmds.joint(name="JNT_Neck", position=(0, 58, 0))
    head = cmds.joint(name="JNT_Head", position=(0, 68, 0))
    head_tip = cmds.joint(name="JNT_HeadTip", position=(0, 75, 0))

    # Arms (Left)
    cmds.select(chest)
    clav_l = cmds.joint(name="JNT_Clavicle_L", position=(12, 44, 2))
    shld_l = cmds.joint(name="JNT_Shoulder_L", position=(28, 40, -1))
    elbw_l = cmds.joint(name="JNT_Elbow_L", position=(46, 25, -6))
    wrst_l = cmds.joint(name="JNT_Wrist_L", position=(60, 12, -2))
    hand_l = cmds.joint(name="JNT_Hand_L", position=(68, 4, 0))

    # Arms (Right)
    cmds.select(chest)
    clav_r = cmds.joint(name="JNT_Clavicle_R", position=(-12, 44, 2))
    shld_r = cmds.joint(name="JNT_Shoulder_R", position=(-28, 40, -1))
    elbw_r = cmds.joint(name="JNT_Elbow_R", position=(-46, 25, -6))
    wrst_r = cmds.joint(name="JNT_Wrist_R", position=(-60, 12, -2))
    hand_r = cmds.joint(name="JNT_Hand_R", position=(-68, 4, 0))

    # Legs (Left)
    cmds.select(root_jnt)
    hip_l = cmds.joint(name="JNT_Hip_L", position=(18, -6, 0))
    knee_l = cmds.joint(name="JNT_Knee_L", position=(20, -36, 4))
    ankl_l = cmds.joint(name="JNT_Ankle_L", position=(22, -66, -2))
    foot_l = cmds.joint(name="JNT_Foot_L", position=(22, -73, 12))

    # Legs (Right)
    cmds.select(root_jnt)
    hip_r = cmds.joint(name="JNT_Hip_R", position=(-18, -6, 0))
    knee_r = cmds.joint(name="JNT_Knee_R", position=(-20, -36, 4))
    ankl_r = cmds.joint(name="JNT_Ankle_R", position=(-22, -66, -2))
    foot_r = cmds.joint(name="JNT_Foot_R", position=(-22, -73, 12))

    # 3. Gather ALL joints in hierarchy for smooth skin binding
    all_joints = cmds.listRelatives(root_jnt, allDescendents=True, type="joint") or []
    all_joints.append(root_jnt)
    print(f"Total joints gathered for binding: {len(all_joints)}")

    # Smooth Skin Binding to all joints
    skin_cluster = cmds.skinCluster(
        all_joints,
        mesh_name,
        toSelectedBones=True,
        bindMethod=0, # Closest joint
        skinMethod=0, # Classical Linear
        normalizeWeights=1,
        maximumInfluences=4,
        dropoffRate=3.0,
        name="Monster_SkinCluster"
    )[0]
    print(f"SkinCluster created: {skin_cluster}")

    # 4. Master Rig Group & Hierarchy (Direct Hierarchy, Zero Double Transform)
    rig_grp = cmds.group(empty=True, name="Monster_Rig_GRP")
    geo_grp = cmds.group(mesh_name, name="Monster_Geometry_GRP")
    cmds.setAttr(f"{geo_grp}.inheritsTransform", 0)

    # Master Control
    master_ctrl = create_ctrl("CTRL_Master", shape="circle", radius=60.0, color=17) # Yellow
    ctrl_grp = cmds.group(master_ctrl, name="Monster_Controllers_GRP")

    # Parent Root Joint directly to CTRL_Master
    cmds.parent(root_jnt, master_ctrl)

    # Assemble under Rig Group
    cmds.parent(ctrl_grp, geo_grp, rig_grp)

    print("Monster lean skeleton & skin bind generated successfully with all influences!")
    return rig_grp

def build_rig_file():
    import maya.standalone
    try:
        maya.standalone.initialize(name="python")
    except Exception:
        pass
    in_scene = r"D:\projects\ProjectAnimation\scenes\Monster\MonsterMain.mb"
    out_scene = r"D:\projects\ProjectAnimation\scenes\Monster\Monster_Rigged.mb"
    if not os.path.exists(in_scene):
        raise FileNotFoundError(f"Input scene not found: {in_scene}")
    cmds.file(in_scene, open=True, force=True)
    build_monster_skeleton()

    # Re-link texture paths to sourceimages canonical folder
    tex_dir = r"D:/projects/ProjectAnimation/sourceimages/Meshy_AI_Buff_Blobbell_0821154423_texture_fbx"
    file_nodes = {
        "file_Monster_BaseColor": f"{tex_dir}/Meshy_AI_Buff_Blobbell_0821154423_texture.png",
        "file_Monster_Roughness": f"{tex_dir}/Meshy_AI_Buff_Blobbell_0821154423_texture_roughness.png",
        "file_Monster_Metallic": f"{tex_dir}/Meshy_AI_Buff_Blobbell_0821154423_texture_metallic.png",
    }
    for node, pth in file_nodes.items():
        if cmds.objExists(node) and os.path.exists(pth):
            cmds.setAttr(f"{node}.fileTextureName", pth, type="string")

    cmds.file(rename=out_scene)
    saved = cmds.file(save=True, type="mayaBinary")
    print(f"SUCCESS: Rigged monster saved to {saved}")
    return saved

if __name__ == "__main__":
    build_rig_file()
