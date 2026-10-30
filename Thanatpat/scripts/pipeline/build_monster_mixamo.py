"""
Build scenes/Characters/Monster_Mixamo.mb from Mixamo T-Pose FBX and test run cycle.
DoD (T07 Monster):
- Monster_Mixamo.mb built from raw_assets/mixamo/monster/T_Pose-With_skin.fbx (66 LimbNodes / 33 joints)
- Scaled to 170 cm tall (170 +/- 2 cm)
- Original shader applied from scenes/Monster/MonsterMain.mb (mesh Monster_Buff_Blobbell)
- specularRoughness 0.45-0.65, specular <= 0.5
- Print bounding-box height, both shader values, joint count
- Import Mutant_Run.fbx animation onto rig and render 12 frames with Render.exe -r hw2 into movies/playblast/rigtest_monster/ (PNG)
- Encode to mp4 if ffmpeg is on PATH
"""
import os
import sys
import subprocess
import shutil

import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
import maya.mel as mel

WORKSPACE = r"D:\projects\ProjectAnimation"
MONSTER_FBX = os.path.join(WORKSPACE, r"raw_assets\mixamo\monster\T_Pose-With_skin.fbx")
MONSTER_MAIN_MB = os.path.join(WORKSPACE, r"scenes\Monster\MonsterMain.mb")
MONSTER_OUT_MB = os.path.join(WORKSPACE, r"scenes\Characters\Monster_Mixamo.mb")
MUTANT_RUN_FBX = os.path.join(WORKSPACE, r"raw_assets\mixamo\monster\Mutant_Run.fbx")
PLAYBLAST_DIR = os.path.join(WORKSPACE, r"movies\playblast\rigtest_monster")
TEST_SCENE_MB = os.path.join(WORKSPACE, r"scenes\Characters\test_monster_run.mb")


def build_monster():
    cmds.workspace(WORKSPACE, openWorkspace=True)
    cmds.loadPlugin("fbxmaya", quiet=True)
    cmds.loadPlugin("mtoa", quiet=True)

    print("=" * 60)
    print("BUILDING MONSTER_MIXAMO.MB")
    print("=" * 60)

    # 1. Start new scene
    cmds.file(new=True, force=True)

    # 2. Import T-Pose FBX
    cmds.file(MONSTER_FBX, i=True)

    # 3. Check original height and scale to 170 cm
    bb_orig = cmds.exactWorldBoundingBox("Monster_Buff_BlobbellShape")
    h_orig = bb_orig[4] - bb_orig[1]
    target_height = 170.0
    scale_val = target_height / h_orig
    print(f"Original Monster height: {h_orig:.4f} cm")
    print(f"Target height: {target_height:.1f} cm -> scale factor: {scale_val:.6f}")

    # Scale skeleton root (mixamorig:Hips)
    cmds.setAttr("mixamorig:Hips.scaleX", scale_val)
    cmds.setAttr("mixamorig:Hips.scaleY", scale_val)
    cmds.setAttr("mixamorig:Hips.scaleZ", scale_val)

    # Adjust Hips Y so feet sit at Y = 0
    bb_scaled = cmds.exactWorldBoundingBox("Monster_Buff_BlobbellShape")
    cmds.setAttr("mixamorig:Hips.translateY", cmds.getAttr("mixamorig:Hips.translateY") - bb_scaled[1])

    # Final bounding box check
    bb_final = cmds.exactWorldBoundingBox("Monster_Buff_BlobbellShape")
    h_final = bb_final[4] - bb_final[1]
    print(f"Final Bounding-Box Height: {h_final:.4f} cm (minY: {bb_final[1]:.4f}, maxY: {bb_final[4]:.4f})")

    # Joint count
    joints = cmds.ls(type="joint")
    with open(MONSTER_FBX, "rb") as f:
        limb_nodes = f.read().count(b"LimbNode")
    print(f"Joint count in Maya: {len(joints)} joints (FBX LimbNode count: {limb_nodes})")

    # Group skeleton under GRP_Monster_Mixamo as rig master
    grp = cmds.group("mixamorig:Hips", name="GRP_Monster_Mixamo")

    # 4. Import original Monster shader from MonsterMain.mb
    cmds.file(
        MONSTER_MAIN_MB,
        i=True,
        type="mayaBinary",
        ignoreVersion=True,
        ra=True,
        mergeNamespacesOnClash=False,
        namespace="ORIG_MONSTER",
        options="v=0;"
    )

    mat = "ORIG_MONSTER:M_Monster_BuffBlobbell"
    sg = "ORIG_MONSTER:M_Monster_BuffBlobbell_SG"

    # Disconnect file texture from specularRoughness if connected
    conns = cmds.listConnections(f"{mat}.specularRoughness", s=True, d=False, p=True) or []
    for c in conns:
        cmds.disconnectAttr(c, f"{mat}.specularRoughness")

    # Set specularRoughness 0.55 (0.45-0.65) and specular 0.45 (at most 0.5)
    cmds.setAttr(f"{mat}.specularRoughness", 0.55)
    cmds.setAttr(f"{mat}.specular", 0.45)

    spec_val = cmds.getAttr(f"{mat}.specular")
    rough_val = cmds.getAttr(f"{mat}.specularRoughness")
    print(f"Shader specular: {spec_val:.4f} (<= 0.5)")
    print(f"Shader specularRoughness: {rough_val:.4f} (0.45 - 0.65)")

    # Assign shader to Monster mesh
    cmds.sets("Monster_Buff_Blobbell", e=True, forceElement=sg)

    # Clean up imported auxiliary transforms from MonsterMain
    for node in cmds.ls("ORIG_MONSTER:*"):
        if cmds.objExists(node) and cmds.nodeType(node) == "transform":
            if any(k in node for k in ["Floor", "Reel", "Monster", "aiSkyDome"]):
                try:
                    cmds.delete(node)
                except Exception:
                    pass

    # Save Monster_Mixamo.mb
    os.makedirs(os.path.dirname(MONSTER_OUT_MB), exist_ok=True)
    cmds.file(rename=MONSTER_OUT_MB)
    cmds.file(save=True, force=True, type="mayaBinary")
    print(f"Successfully saved: {MONSTER_OUT_MB} ({os.path.getsize(MONSTER_OUT_MB)} bytes)")

    return h_final, spec_val, rough_val, len(joints), scale_val


def test_run_cycle(scale_val):
    print("\n" + "=" * 60)
    print("TESTING MONSTER RUN CYCLE")
    print("=" * 60)

    # Open Monster_Mixamo.mb
    cmds.file(MONSTER_OUT_MB, open=True, force=True)

    # Import Mutant_Run.fbx animation in merge mode
    mel.eval('FBXImportMode -v "merge"')
    mel.eval('FBXImportFillTimeline -v true')
    cmds.file(MUTANT_RUN_FBX, i=True)

    # Ensure Hips scale is maintained
    cmds.setAttr("mixamorig:Hips.scaleX", scale_val)
    cmds.setAttr("mixamorig:Hips.scaleY", scale_val)
    cmds.setAttr("mixamorig:Hips.scaleZ", scale_val)

    # Scale translateY animation curve on Hips
    anim_curves = cmds.findKeyframe("mixamorig:Hips", curve=True, at="translateY") or []
    if anim_curves:
        cmds.scaleKey(anim_curves[0], valueScale=scale_val, valuePivot=0.0)

    # Set frame range 1 to 12
    cmds.playbackOptions(minTime=1.0, maxTime=12.0, animationStartTime=1.0, animationEndTime=12.0)
    cmds.currentUnit(time="film")

    # Clean up existing test cameras
    for c in cmds.ls("CAM_RigTest_Monster*"):
        if cmds.objExists(c):
            cmds.delete(c)

    # Create camera for playblast test
    cam_name = "CAM_RigTest_Monster"
    cam_node, cam_shape = cmds.camera(name=cam_name, focalLength=35.0)
    cmds.xform(cam_node, ws=True, t=[0.0, 95.0, 260.0])
    cmds.xform(cam_node, ws=True, ro=[-8.0, 0.0, 0.0])

    for c in cmds.ls(type="camera"):
        cmds.setAttr(f"{c}.renderable", 1 if c == cam_shape else 0)

    # Add lighting for viewport hardware renderer
    dlight = cmds.directionalLight(name="RigTest_DirLight")
    dlight_xf = cmds.listRelatives(dlight, parent=True)[0]
    cmds.xform(dlight_xf, ws=True, ro=[-35.0, 45.0, 0.0])

    alight = cmds.ambientLight(name="RigTest_AmbLight")
    cmds.setAttr(f"{alight}.intensity", 0.4)

    # Set resolution
    cmds.setAttr("defaultResolution.width", 960)
    cmds.setAttr("defaultResolution.height", 540)
    cmds.setAttr("defaultResolution.deviceAspectRatio", 960.0 / 540.0)

    # Save test scene
    cmds.file(rename=TEST_SCENE_MB)
    res = cmds.file(save=True, force=True, type="mayaBinary")
    print(f"Saved test scene: {TEST_SCENE_MB} (size: {os.path.getsize(TEST_SCENE_MB)} bytes)")
    return cam_node


def render_and_encode(cam_name):
    os.makedirs(PLAYBLAST_DIR, exist_ok=True)

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
        "-im", "monster_run",
        "-of", "png",
        TEST_SCENE_MB
    ]

    print(f"Rendering 12 frames with Render.exe -r hw2 using camera {cam_name}...")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=45)
        print(f"Render.exe exit code: {res.returncode}")
        if res.returncode != 0:
            print(f"Render stdout: {res.stdout[-300:]}")
            print(f"Render stderr: {res.stderr[-300:]}")
    except subprocess.TimeoutExpired:
        print("Render.exe timed out waiting for process cleanup, checking rendered frames...")

    # Normalize filenames if rendered as monster_run.png.####
    for f in os.listdir(PLAYBLAST_DIR):
        if f.startswith("monster_run.png."):
            num = f.split(".")[-1]
            old_p = os.path.join(PLAYBLAST_DIR, f)
            new_p = os.path.join(PLAYBLAST_DIR, f"monster_run_{num}.png")
            if os.path.exists(new_p):
                os.remove(new_p)
            os.rename(old_p, new_p)

    rendered_files = sorted([f for f in os.listdir(PLAYBLAST_DIR) if f.startswith("monster_run") and f.endswith(".png")])
    print(f"Rendered PNG frames: {len(rendered_files)} files in {PLAYBLAST_DIR}")
    for rf in rendered_files[:3]:
        print(f"  {rf} ({os.path.getsize(os.path.join(PLAYBLAST_DIR, rf))} bytes)")
    if len(rendered_files) > 3:
        print(f"  ... and {len(rendered_files)-3} more")

    # Encode to mp4 with ffmpeg if available
    ffmpeg = shutil.which("ffmpeg")
    mp4_path = os.path.join(WORKSPACE, r"movies\playblast\rigtest_monster.mp4")
    if ffmpeg and len(rendered_files) >= 12:
        print(f"Found ffmpeg at {ffmpeg}. Encoding to {mp4_path}...")
        pattern = os.path.join(PLAYBLAST_DIR, "monster_run_%04d.png")
        if not os.path.exists(os.path.join(PLAYBLAST_DIR, "monster_run_0001.png")):
            # Check for alternative naming
            if os.path.exists(os.path.join(PLAYBLAST_DIR, "monster_run.0001.png")):
                pattern = os.path.join(PLAYBLAST_DIR, "monster_run.%04d.png")

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
    h, spec, rough, joints, scale_val = build_monster()
    cam_name = test_run_cycle(scale_val)
    maya.standalone.uninitialize()
    render_and_encode(cam_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
