"""
build_charlie_mixamo.py

T07: Builds Charlie_Mixamo.mb from Mixamo T-pose rig and original separate meshes from Nannapas/main_char.fbx.
Steps:
1. Load raw_assets/mixamo/charlie/T_Pose_With_Skin.fbx (Mixamo rig + combined mesh).
2. Restore bind pose.
3. Import Nannapas/main_char.fbx.
4. Scale group3 x20 from [0, 0, 0].
5. Unparent separate meshes (body, sweater, short, shoes1, hoodie) to world and freeze transforms.
6. Unparent eye groups (right_eye_group, right_eye_group1) to world.
7. Bind each mesh part to Mixamo skeleton joints, copy skin weights from Charlie_Upload_Mesh via closestPoint.
8. Delete combined Charlie_Upload_Mesh and empty group3.
9. Parent-constrain eye groups to mixamorig:Head.
10. Test rotating mixamorig:Head 30 degrees and verify eye group world pos before/after.
11. Group skeleton and meshes cleanly under GRP_Charlie_Mixamo.
12. Measure bounding-box height and joint count.
13. Save scenes/Characters/Charlie_Mixamo.mb.
14. Test run cycle with Terrified_Run.fbx: render 12 frames via Render.exe -r hw2 to movies/playblast/rigtest_charlie/ and encode to mp4 via ffmpeg.
"""

import os
import sys
import time
import shutil
import subprocess

import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.mel as mel

cmds.loadPlugin("fbxmaya", quiet=True)

WORKSPACE = r"D:\projects\ProjectAnimation"
CHARLIE_TPOSE_FBX = os.path.join(WORKSPACE, r"raw_assets\mixamo\charlie\T_Pose_With_Skin.fbx")
NANNAPAS_MAIN_CHAR_FBX = os.path.join(WORKSPACE, r"Nannapas\main_char.fbx")
TERRIFIED_RUN_FBX = os.path.join(WORKSPACE, r"raw_assets\mixamo\charlie\Terrified_Run.fbx")

OUTPUT_CHARLIE_MB = os.path.join(WORKSPACE, r"scenes\Characters\Charlie_Mixamo.mb")
TEST_SCENE_MB = os.path.join(WORKSPACE, r"scenes\Characters\test_charlie_run.mb")
PLAYBLAST_DIR = os.path.join(WORKSPACE, r"movies\playblast\rigtest_charlie")

PARTS = ["body", "sweater", "short", "shoes1", "hoodie"]
EYE_GROUPS = ["right_eye_group", "right_eye_group1"]


def unlock_all(node):
    for a in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]:
        try:
            cmds.setAttr(f"{node}.{a}", lock=False)
        except Exception:
            pass


def build_charlie():
    print("=" * 60)
    print("BUILDING CHARLIE_MIXAMO.MB")
    print("=" * 60)

    cmds.file(new=True, force=True)

    # 1. Import Mixamo T_Pose_With_Skin.fbx
    cmds.file(CHARLIE_TPOSE_FBX, i=True)
    mix_sc = "skinCluster1"
    joints = cmds.ls(type="joint")
    print(f"Loaded Mixamo skeleton with {len(joints)} joints.")

    # 2. Restore bind pose.
    # FIX v3 (Claude, 2026-09-30): the FBX carries T-pose keys (frames 0-1) that pull the hips to the origin while the skin is bound at the
    # mesh location (hips 140.9, 41.5, 131.0). Remove those keys, keep the bind pose, and use two parent groups below to move the whole rig
    # to the origin, which is where every Mixamo animation clip expects the skeleton to be.
    cmds.delete(cmds.ls(type="animCurve"))
    if cmds.objExists("bindPose1"):
        cmds.dagPose("bindPose1", restore=True)
    HB = cmds.xform("mixamorig:Hips", q=True, ws=True, t=True)
    print("BIND hips world", [round(v, 2) for v in HB])

    # 3. Import Nannapas main_char.fbx
    cmds.file(NANNAPAS_MAIN_CHAR_FBX, i=True)

    # 4. Scale group3 x20 from [0, 0, 0]
    if cmds.objExists("group3"):
        cmds.scale(20, 20, 20, "group3", r=True, p=[0, 0, 0])

    # 5. Unlock, unparent parts to world, and freeze transforms
    for p in PARTS:
        unlock_all(p)
        cmds.parent(p, world=True)
        cmds.makeIdentity(p, apply=True, t=1, r=1, s=1, n=0)

    # 6. Unlock, unparent eye groups to world
    for eg in EYE_GROUPS:
        unlock_all(eg)
        cmds.parent(eg, world=True)

    # 7. Bind each part and copy skin weights
    for p in PARTS:
        sc = cmds.skinCluster(joints, p, toSelectedBones=True, name=f"skinCluster_{p}")[0]
        cmds.copySkinWeights(
            sourceSkin=mix_sc,
            destinationSkin=sc,
            noMirror=True,
            surfaceAssociation="closestPoint",
            influenceAssociation="oneToOne"
        )
        print(f"Skin weights copied to {p} via {sc}")

    # 8. Delete combined Mixamo mesh and empty group3
    if cmds.objExists("Charlie_Upload_Mesh"):
        cmds.delete("Charlie_Upload_Mesh")
    if cmds.objExists("group3"):
        cmds.delete("group3")

    # 9. Parent-constrain eye groups to mixamorig:Head
    for eg in EYE_GROUPS:
        cmds.parentConstraint("mixamorig:Head", eg, mo=True)
        print(f"Parent-constrained {eg} to mixamorig:Head")

    # 10. Eye rotation test: rotate Head 30 deg and check pos
    pos_before = cmds.xform("right_eye_group", q=True, ws=True, t=True)
    orig_ry = cmds.getAttr("mixamorig:Head.rotateY")
    cmds.setAttr("mixamorig:Head.rotateY", orig_ry + 30.0)
    pos_after = cmds.xform("right_eye_group", q=True, ws=True, t=True)
    cmds.setAttr("mixamorig:Head.rotateY", orig_ry)  # restore original pose

    print(f"right_eye_group world pos before rotation: {pos_before}")
    print(f"right_eye_group world pos after 30 deg rotation: {pos_after}")
    print(f"Eye rotation delta: dx={pos_after[0]-pos_before[0]:.4f}, dy={pos_after[1]-pos_before[1]:.4f}, dz={pos_after[2]-pos_before[2]:.4f}")

    # 11. Hierarchy organization:
    # GRP_Charlie_Mixamo at root
    # Skeleton: mixamorig:Hips under GRP_Charlie_Mixamo
    # Meshes: GRP_Charlie_Meshes (inheritsTransform=False to prevent double transformation)
    # Eyes: GRP_Charlie_Eyes (inheritsTransform=False to prevent double transformation from constraint)
    top_grp = "GRP_Charlie_Mixamo"
    if not cmds.objExists(top_grp):
        top_grp = cmds.group(empty=True, name=top_grp)
    cmds.xform(top_grp, ws=True, t=(HB[0], 0.0, HB[2]))   # sits where the bind-pose hips are; hips keep world position when parented below

    mesh_grp = "GRP_Charlie_Meshes"
    if not cmds.objExists(mesh_grp):
        mesh_grp = cmds.group(empty=True, name=mesh_grp, parent=top_grp)
    cmds.setAttr(f"{mesh_grp}.inheritsTransform", 0)
    for p in PARTS:
        cmds.parent(p, mesh_grp)

    eye_grp = "GRP_Charlie_Eyes"
    if not cmds.objExists(eye_grp):
        eye_grp = cmds.group(empty=True, name=eye_grp, parent=top_grp)
    cmds.setAttr(f"{eye_grp}.inheritsTransform", 0)
    for eg in EYE_GROUPS:
        cmds.parent(eg, eye_grp)

    if cmds.objExists("mixamorig:Hips"):
        cmds.parent("mixamorig:Hips", top_grp)

    # 11b. Placement group: moves the rig (skeleton, skin-deformed meshes, constrained eyes) so the hips sit at the origin like the Mixamo clips
    place = cmds.group(empty=True, name="GRP_Charlie_Placement")
    cmds.parent(top_grp, place)
    # Keep GRP_Charlie_Placement at the origin (so its pivot is under the feet and rotating it turns the character in place) and zero the inner
    # group: hips local (0, 41.5, 0) already puts the skeleton at the origin, the skin delta (bind is 141,131 away) brings the meshes there too.
    cmds.setAttr(top_grp + ".translate", 0.0, 0.0, 0.0)
    cmds.currentTime(1)
    print("PLACED hips world", [round(v, 2) for v in cmds.xform("mixamorig:Hips", q=True, ws=True, t=True)])
    bbp = [cmds.exactWorldBoundingBox(p) for p in PARTS]
    print("PLACED meshes bbox", [round(min(b[0] for b in bbp), 1), round(min(b[1] for b in bbp), 1), round(min(b[2] for b in bbp), 1), round(max(b[3] for b in bbp), 1), round(max(b[4] for b in bbp), 1), round(max(b[5] for b in bbp), 1)])
    print("PLACED eye group world", [round(v, 2) for v in cmds.xform("right_eye_group", q=True, ws=True, t=True)])

    # 12. Measure bounding-box height of Charlie
    bbs = [cmds.exactWorldBoundingBox(p) for p in PARTS]
    min_y = min(b[1] for b in bbs)
    max_y = max(b[4] for b in bbs)
    height = max_y - min_y
    joint_count = len(cmds.ls(type="joint"))

    print(f"Final Charlie Bounding-Box Height: {height:.4f} cm (minY: {min_y:.4f}, maxY: {max_y:.4f})")
    print(f"Joint count in Maya: {joint_count} joints")

    # 13. Save Charlie_Mixamo.mb
    os.makedirs(os.path.dirname(OUTPUT_CHARLIE_MB), exist_ok=True)
    cmds.file(rename=OUTPUT_CHARLIE_MB)
    cmds.file(save=True, force=True, type="mayaBinary")
    file_size = os.path.getsize(OUTPUT_CHARLIE_MB)
    print(f"Successfully saved: {OUTPUT_CHARLIE_MB} ({file_size} bytes)")

    return height, joint_count, pos_before, pos_after


def test_run_cycle():
    print("\n" + "=" * 60)
    print("TESTING CHARLIE RUN CYCLE (Terrified_Run.fbx)")
    print("=" * 60)

    cmds.file(new=True, force=True)
    cmds.file(OUTPUT_CHARLIE_MB, o=True)

    # Import animation onto skeleton
    mel.eval('FBXImportMode -v "merge"')
    mel.eval('FBXImportFillTimeline -v true')
    cmds.file(TERRIFIED_RUN_FBX, i=True)

    # Set frame range 1 to 12
    cmds.playbackOptions(minTime=1.0, maxTime=12.0, animationStartTime=1.0, animationEndTime=12.0)
    cmds.currentUnit(time="film")

    # Clean up any existing test cameras
    for c in cmds.ls("CAM_RigTest_Charlie*", transforms=True):
        if cmds.objExists(c):
            cmds.delete(c)

    # Create camera centered on Charlie: Charlie is at X ~ 140, Y ~ 70, Z ~ 120-180
    cam_node = cmds.camera(focalLength=28.0)[0]
    cam_node = cmds.rename(cam_node, "CAM_RigTest_Charlie")
    cam_shape = cmds.listRelatives(cam_node, shapes=True)[0]
    cmds.xform(cam_node, ws=True, t=[140.0, 75.0, 320.0])
    cmds.xform(cam_node, ws=True, ro=[-5.0, 0.0, 0.0])

    for c in cmds.ls(type="camera"):
        cmds.setAttr(f"{c}.renderable", 1 if c == cam_shape else 0)

    # Lighting for hardware renderer
    dlight = cmds.directionalLight(name="RigTest_DirLight_Charlie")
    dlight_xf = cmds.listRelatives(dlight, parent=True)[0]
    cmds.xform(dlight_xf, ws=True, ro=[-35.0, 35.0, 0.0])

    alight = cmds.ambientLight(name="RigTest_AmbLight_Charlie")
    cmds.setAttr(f"{alight}.intensity", 0.5)

    # Resolution
    cmds.setAttr("defaultResolution.width", 960)
    cmds.setAttr("defaultResolution.height", 540)
    cmds.setAttr("defaultResolution.deviceAspectRatio", 960.0 / 540.0)

    # Save test scene
    cmds.file(rename=TEST_SCENE_MB)
    cmds.file(save=True, force=True, type="mayaBinary")
    print(f"Saved test scene: {TEST_SCENE_MB} (size: {os.path.getsize(TEST_SCENE_MB)} bytes)")
    return cam_node


def render_and_encode(cam_name):
    os.makedirs(PLAYBLAST_DIR, exist_ok=True)
    # Clear out any old test files in PLAYBLAST_DIR
    for f in os.listdir(PLAYBLAST_DIR):
        if f.startswith("charlie_run") or f.startswith("test_char"):
            try:
                os.remove(os.path.join(PLAYBLAST_DIR, f))
            except Exception:
                pass

    render_exe = r"D:\AutoDesk\Maya2027\bin\Render.exe"
    cmd = [
        render_exe,
        "-r", "hw2",
        "-cam", cam_name,
        "-s", "1",
        "-e", "12",
        "-x", "960",
        "-y", "540",
        "-rd", PLAYBLAST_DIR,
        "-im", "charlie_run",
        "-of", "png",
        TEST_SCENE_MB
    ]

    print(f"Rendering 12 frames with Render.exe -r hw2 using camera {cam_name}...")
    log_path = os.path.join(PLAYBLAST_DIR, "render_hw2.log")
    with open(log_path, "w") as log_f:
        proc = subprocess.Popen(cmd, stdout=log_f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)

        # Monitor for frame 12
        start_time = time.time()
        last_frame = "charlie_run.png.0012"
        alt_last_frame = "charlie_run_0012.png"
        done = False

        while time.time() - start_time < 60:
            if proc.poll() is not None:
                done = True
                break
            p1 = os.path.join(PLAYBLAST_DIR, last_frame)
            p2 = os.path.join(PLAYBLAST_DIR, alt_last_frame)
            if (os.path.exists(p1) and os.path.getsize(p1) > 1000) or (os.path.exists(p2) and os.path.getsize(p2) > 1000):
                # Render has completed all 12 frames
                time.sleep(1.0)
                proc.terminate()
                done = True
                break
            time.sleep(1.0)

        if not done:
            proc.kill()

    # Normalize filenames if rendered as charlie_run.png.####
    for f in os.listdir(PLAYBLAST_DIR):
        if f.startswith("charlie_run.png."):
            num = f.split(".")[-1]
            old_p = os.path.join(PLAYBLAST_DIR, f)
            new_p = os.path.join(PLAYBLAST_DIR, f"charlie_run_{num}.png")
            if os.path.exists(new_p):
                os.remove(new_p)
            os.rename(old_p, new_p)

    rendered_files = sorted([f for f in os.listdir(PLAYBLAST_DIR) if f.startswith("charlie_run") and f.endswith(".png")])
    print(f"Rendered PNG frames: {len(rendered_files)} files in {PLAYBLAST_DIR}")
    for rf in rendered_files[:3]:
        print(f"  {rf} ({os.path.getsize(os.path.join(PLAYBLAST_DIR, rf))} bytes)")
    if len(rendered_files) > 3:
        print(f"  ... and {len(rendered_files)-3} more")

    # Encode to mp4 with ffmpeg if available
    ffmpeg = shutil.which("ffmpeg")
    mp4_path = os.path.join(WORKSPACE, r"movies\playblast\rigtest_charlie.mp4")
    if ffmpeg and len(rendered_files) >= 12:
        print(f"Found ffmpeg at {ffmpeg}. Encoding to {mp4_path}...")
        pattern = os.path.join(PLAYBLAST_DIR, "charlie_run_%04d.png")
        if not os.path.exists(os.path.join(PLAYBLAST_DIR, "charlie_run_0001.png")):
            if os.path.exists(os.path.join(PLAYBLAST_DIR, "charlie_run.0001.png")):
                pattern = os.path.join(PLAYBLAST_DIR, "charlie_run.%04d.png")

        ff_cmd = [
            ffmpeg, "-y",
            "-framerate", "24",
            "-i", pattern,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            mp4_path
        ]
        ff_res = subprocess.run(ff_cmd, capture_output=True, text=True)
        if os.path.exists(mp4_path):
            print(f"Successfully generated: {mp4_path} ({os.path.getsize(mp4_path)} bytes)")
        else:
            print(f"ffmpeg error: {ff_res.stderr[-300:]}")

    # Cleanup test scene
    if os.path.exists(TEST_SCENE_MB):
        os.remove(TEST_SCENE_MB)
        print(f"Cleaned up test scene: {TEST_SCENE_MB}")


def main():
    height, joints, p_before, p_after = build_charlie()
    print("BUILD DONE height", round(height, 2), "joints", joints)
    maya.standalone.uninitialize()
    return 0


if __name__ == "__main__":
    sys.exit(main())
