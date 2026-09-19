"""
=============================================================================
Maya 3D Model Showreel & Turntable Camera Rig Generator
Designed for TAWAN-OS Project Animation (MonsterMain.mb / Meshy AI Models)
=============================================================================
"""

import maya.cmds as cmds
import math

def setup_reel_showcase(target_mesh="Monster_Buff_Blobbell", 
                       start_frame=1, 
                       end_frame=240, 
                       cam_focal_length=75.0, 
                       cam_distance=360.0,
                       cam_height=20.0,
                       create_lights=True,
                       create_floor=True,
                       mode="turntable_360"):
    """
    Creates a professional Showreel camera rig, 3-point lighting, and turntable animation.
    """
    # 1. Check if mesh exists
    if not cmds.objExists(target_mesh):
        meshes = cmds.ls(type='mesh')
        if meshes:
            target_mesh = cmds.listRelatives(meshes[0], parent=True)[0]
        else:
            cmds.warning("No mesh found in scene. Creating centered camera rig.")
            target_mesh = None

    # Calculate center and bounding box
    if target_mesh and cmds.objExists(target_mesh):
        bb = cmds.exactWorldBoundingBox(target_mesh)
        center_x = (bb[0] + bb[3]) / 2.0
        center_y = (bb[1] + bb[4]) / 2.0
        center_z = (bb[2] + bb[5]) / 2.0
        height = bb[4] - bb[1]
        width = bb[3] - bb[0]
        max_dim = max(height, width, bb[5] - bb[2])
        # Auto calculate optimal distance if default
        if cam_distance == 360.0:
            cam_distance = max_dim * 1.8
    else:
        center_x, center_y, center_z = 0.0, 0.0, 0.0
        height = 150.0
        max_dim = 150.0
        cam_distance = 360.0

    # 2. Cleanup existing Reel Rig if any
    if cmds.objExists("Reel_Showcase_GRP"):
        cmds.delete("Reel_Showcase_GRP")

    # 3. Create Root Hierarchy
    root_grp = cmds.group(empty=True, name="Reel_Showcase_GRP")
    
    # Aim Target Locator
    aim_loc = cmds.spaceLocator(name="Reel_Cam_Aim_LOC")[0]
    cmds.xform(aim_loc, translation=(center_x, center_y, center_z), worldSpace=True)
    cmds.setAttr(f"{aim_loc}.visibility", 0) # hide locator by default
    cmds.parent(aim_loc, root_grp)

    # Turntable Rotation Center Group
    turntable_grp = cmds.group(empty=True, name="Reel_Cam_Turntable_GRP")
    cmds.xform(turntable_grp, translation=(center_x, center_y, center_z), worldSpace=True)
    cmds.parent(turntable_grp, root_grp)

    # Pitch / Elevation Tilt Group
    pitch_grp = cmds.group(empty=True, name="Reel_Cam_Pitch_GRP")
    cmds.xform(pitch_grp, translation=(center_x, center_y, center_z), worldSpace=True)
    cmds.parent(pitch_grp, turntable_grp)

    # 4. Create Showreel Camera
    cam_nodes = cmds.camera(
        focalLength=cam_focal_length,
        nearClipPlane=1.0,
        farClipPlane=100000.0,
        displayResolution=True,
        displayFilmGate=False,
        displaySafeAction=True,
        overscan=1.1
    )
    cam_transform = cmds.rename(cam_nodes[0], "Reel_Cam")
    cam_shape = cmds.listRelatives(cam_transform, shapes=True)[0]
    cmds.parent(cam_transform, pitch_grp)

    # Position Camera
    cmds.setAttr(f"{cam_transform}.translateX", 0)
    cmds.setAttr(f"{cam_transform}.translateY", cam_height)
    cmds.setAttr(f"{cam_transform}.translateZ", cam_distance)
    cmds.setAttr(f"{cam_transform}.rotateX", 0)
    cmds.setAttr(f"{cam_transform}.rotateY", 0)
    cmds.setAttr(f"{cam_transform}.rotateZ", 0)

    # Aim Constraint from Camera to Target Locator
    cmds.aimConstraint(
        aim_loc,
        cam_transform,
        offset=(0, 0, 0),
        weight=1,
        aimVector=(0, 0, -1),
        upVector=(0, 1, 0),
        worldUpType="vector",
        worldUpVector=(0, 1, 0)
    )

    # 5. Set Playback Timeline
    cmds.playbackOptions(min=start_frame, max=end_frame, ast=start_frame, aet=end_frame)
    cmds.currentTime(start_frame)

    # 6. Setup Animation based on Mode
    if mode == "turntable_360":
        # 360 Continuous Turntable Orbit
        cmds.setKeyframe(turntable_grp, attribute="rotateY", time=start_frame, value=0.0)
        cmds.setKeyframe(turntable_grp, attribute="rotateY", time=end_frame, value=360.0)
        
        # Set tangents to linear for seamless endless loop
        cmds.keyTangent(turntable_grp, attribute="rotateY", inTangentType="linear", outTangentType="linear")

    elif mode == "cinematic_reel":
        # Multi-stage presentation
        # Stage 1 (1-60): Dynamic Close-up sweep on Head/Details
        f_mid1 = start_frame + int((end_frame - start_frame) * 0.25)
        f_mid2 = start_frame + int((end_frame - start_frame) * 0.75)

        # Turntable Rotation
        cmds.setKeyframe(turntable_grp, attribute="rotateY", time=start_frame, value=-45.0)
        cmds.setKeyframe(turntable_grp, attribute="rotateY", time=f_mid1, value=45.0)
        cmds.setKeyframe(turntable_grp, attribute="rotateY", time=f_mid2, value=315.0)
        cmds.setKeyframe(turntable_grp, attribute="rotateY", time=end_frame, value=360.0)

        # Camera Distance Zoom (Close-up -> Full body reveal -> Hero pose)
        cmds.setKeyframe(cam_transform, attribute="translateZ", time=start_frame, value=cam_distance * 0.6)
        cmds.setKeyframe(cam_transform, attribute="translateZ", time=f_mid1, value=cam_distance)
        cmds.setKeyframe(cam_transform, attribute="translateZ", time=f_mid2, value=cam_distance * 1.1)
        cmds.setKeyframe(cam_transform, attribute="translateZ", time=end_frame, value=cam_distance * 0.9)

        # Smooth tangents
        cmds.keyTangent(turntable_grp, attribute="rotateY", inTangentType="auto", outTangentType="auto")
        cmds.keyTangent(cam_transform, attribute="translateZ", inTangentType="auto", outTangentType="auto")

    # 7. Create Studio 3-Point Light Rig (Optional)
    if create_lights:
        lights_grp = cmds.group(empty=True, name="Reel_StudioLights_GRP")
        cmds.parent(lights_grp, root_grp)

        # Key Light (Warm Key)
        key_light = cmds.directionalLight(name="Reel_KeyLight_DIR", intensity=1.2)
        key_trans = cmds.listRelatives(key_light, parent=True)[0]
        cmds.xform(key_trans, translation=(center_x + max_dim, center_y + max_dim * 1.5, center_z + max_dim))
        cmds.setAttr(f"{key_light}.color", 1.0, 0.96, 0.92, type="double3")
        cmds.aimConstraint(aim_loc, key_trans, aimVector=(0, 0, -1), upVector=(0, 1, 0))
        cmds.parent(key_trans, lights_grp)

        # Fill Light (Cool Soft Fill)
        fill_light = cmds.directionalLight(name="Reel_FillLight_DIR", intensity=0.5)
        fill_trans = cmds.listRelatives(fill_light, parent=True)[0]
        cmds.xform(fill_trans, translation=(center_x - max_dim * 1.2, center_y + max_dim * 0.8, center_z + max_dim * 0.8))
        cmds.setAttr(f"{fill_light}.color", 0.88, 0.92, 1.0, type="double3")
        cmds.aimConstraint(aim_loc, fill_trans, aimVector=(0, 0, -1), upVector=(0, 1, 0))
        cmds.parent(fill_trans, lights_grp)

        # Rim / Back Light (Silhouette Highlight)
        rim_light = cmds.directionalLight(name="Reel_RimLight_DIR", intensity=1.5)
        rim_trans = cmds.listRelatives(rim_light, parent=True)[0]
        cmds.xform(rim_trans, translation=(center_x, center_y + max_dim * 1.2, center_z - max_dim * 1.5))
        cmds.setAttr(f"{rim_light}.color", 1.0, 1.0, 1.0, type="double3")
        cmds.aimConstraint(aim_loc, rim_trans, aimVector=(0, 0, -1), upVector=(0, 1, 0))
        cmds.parent(rim_trans, lights_grp)

    # 8. Create Studio Floor Disc (Optional)
    if create_floor:
        floor_y = bb[1] if (target_mesh and cmds.objExists(target_mesh)) else -73.33
        floor_radius = max_dim * 2.5
        floor_disc = cmds.polyCylinder(
            name="Reel_StudioFloor_GEO", 
            radius=floor_radius, 
            height=0.5, 
            subdivisionsX=36, 
            subdivisionsY=1, 
            subdivisionsZ=1
        )[0]
        cmds.xform(floor_disc, translation=(center_x, floor_y - 0.25, center_z))
        cmds.parent(floor_disc, root_grp)

    # 9. Set Render Globals (1920x1080 HD, 24 fps)
    cmds.setAttr("defaultResolution.width", 1920)
    cmds.setAttr("defaultResolution.height", 1080)
    cmds.setAttr("defaultResolution.pixelAspect", 1.0)
    cmds.setAttr("defaultResolution.deviceAspectRatio", 1.777)
    cmds.currentUnit(time="film") # 24 fps

    print(f"Showreel Camera Rig successfully created for '{target_mesh}'!")
    print(f"Camera: Reel_Cam (Focal Length: {cam_focal_length}mm, Distance: {cam_distance:.1f})")
    print(f"Timeline: Frame {start_frame} to {end_frame} (24 FPS, 10s Turntable)")
    return "Reel_Cam"

if __name__ == "__main__":
    setup_reel_showcase()
