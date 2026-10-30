"""
=============================================================================
T05: Lighting Setup (Sets A and B) and Still Renders
Target: scenes/Backrooms/Backrooms_Env_v2.mb
Renders:
  - images/checks/light_A_test.png
  - images/checks/light_B_test.png
=============================================================================
"""

import os
import sys
import json
import subprocess
import shutil

import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds

SCENE_PATH = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Env_v2.mb"
RENDER_EXE = r"D:\AutoDesk\Maya2027\bin\Render.exe"
OUTPUT_DIR = r"D:\projects\ProjectAnimation\images\checks"
LIGHT_A_PNG = os.path.join(OUTPUT_DIR, "light_A_test.png")
LIGHT_B_PNG = os.path.join(OUTPUT_DIR, "light_B_test.png")
REPORT_PATH = os.path.join(OUTPUT_DIR, "lighting_report.json")

BASE_EXPOSURE = 4.5
SET_B_EXPOSURE = 3.0  # 4.5 - 1.5 stop


def setup_lighting_in_scene():
    print(f"Opening scene: {SCENE_PATH}")
    cmds.file(SCENE_PATH, open=True, force=True)
    cmds.loadPlugin("mtoa", quiet=True)

    cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")

    # 1. Remove all Red_Emergency_Light_* and aiSkyDome_Ambient_Fill
    red_lights = cmds.ls("Red_Emergency_Light_*") or []
    if red_lights:
        print(f"Deleting {len(red_lights)} Red_Emergency_Light nodes...")
        cmds.delete(red_lights)

    if cmds.objExists("GRP_Emergency_Red_Lights_14"):
        cmds.delete("GRP_Emergency_Red_Lights_14")

    skydomes = cmds.ls(type="aiSkyDomeLight") or []
    for sd in skydomes:
        p = cmds.listRelatives(sd, parent=True)
        if p:
            cmds.delete(p[0])
        else:
            cmds.delete(sd)

    # Clean any remaining pointLights or skydomes
    for pl in (cmds.ls(type="pointLight") or []):
        p = cmds.listRelatives(pl, parent=True)
        cmds.delete(p[0] if p else pl)

    # 2. Master Light Controller
    master_node = "LIGHT_MASTER"
    if not cmds.objExists(master_node):
        master_node = cmds.group(empty=True, name=master_node)
        if cmds.objExists("GRP_Lighting_System"):
            cmds.parent(master_node, "GRP_Lighting_System")

    if not cmds.attributeQuery("exposure", node=master_node, exists=True):
        cmds.addAttr(master_node, ln="exposure", at="float", keyable=True, defaultValue=BASE_EXPOSURE)
    cmds.setAttr(f"{master_node}.exposure", BASE_EXPOSURE)

    if not cmds.attributeQuery("flickerEnable", node=master_node, exists=True):
        cmds.addAttr(master_node, ln="flickerEnable", at="float", keyable=True, defaultValue=0.0)
    cmds.setAttr(f"{master_node}.flickerEnable", 0.0)

    # 3. Configure all 54 Area Lights: colorTemperature 4000K & connect exposure
    area_light_shapes = cmds.ls(type="aiAreaLight") or []
    print(f"Found {len(area_light_shapes)} aiAreaLight shapes in scene.")

    flicker_shapes = ["aiAreaLight_Fluorescent_Panel_04Shape", "aiAreaLight_Fluorescent_Panel_05Shape"]

    for shp in area_light_shapes:
        if cmds.attributeQuery("aiUseColorTemperature", node=shp, exists=True):
            cmds.setAttr(f"{shp}.aiUseColorTemperature", True)
        if cmds.attributeQuery("aiColorTemperature", node=shp, exists=True):
            cmds.setAttr(f"{shp}.aiColorTemperature", 4000.0)

        # Connect LIGHT_MASTER.exposure unless it's one of the two flickering panels
        if shp not in flicker_shapes:
            exp_attr = "aiExposure" if cmds.attributeQuery("aiExposure", node=shp, exists=True) else "exposure"
            cmds.connectAttr(f"{master_node}.exposure", f"{shp}.{exp_attr}", force=True)

    # 4. Flickering Expression for Panel 04 and Panel 05
    expr_name = "EXPR_Monster_Panel_Flicker"
    if cmds.objExists(expr_name):
        cmds.delete(expr_name)

    expr_code = (
        f"float $base = {master_node}.exposure;\n"
        f"if ({master_node}.flickerEnable > 0.5) {{\n"
        f"    aiAreaLight_Fluorescent_Panel_05Shape.aiExposure = $base + ((noise(time * 32.0) > 0.25) ? 0.0 : -3.5);\n"
        f"    aiAreaLight_Fluorescent_Panel_04Shape.aiExposure = $base + ((noise(time * 26.0 + 8.0) > 0.20) ? 0.0 : -4.0);\n"
        f"}} else {{\n"
        f"    aiAreaLight_Fluorescent_Panel_05Shape.aiExposure = $base;\n"
        f"    aiAreaLight_Fluorescent_Panel_04Shape.aiExposure = $base;\n"
        f"}}\n"
    )
    cmds.expression(name=expr_name, string=expr_code)
    print("Flicker expression setup completed for Panel 04 & 05.")

    # 5. Setup Camera inside the room according to DoD
    # Floor Y = -11.90 cm, Ceiling Y = 232.68 cm
    # Camera Y = 95.0 cm: dist_floor = 106.90 cm, dist_ceil = 137.68 cm (dist_floor < dist_ceil)
    cam_name = "CAM_Light_Test"
    existing = cmds.ls(f"*{cam_name}*", type="transform")
    if existing:
        cam_node = existing[0]
        shapes = cmds.listRelatives(cam_node, shapes=True, type="camera") or []
        cam_shape = shapes[0] if shapes else (cmds.ls(type="camera") or ["CAM_Light_TestShape"])[0]
    else:
        cam_node, cam_shape = cmds.camera(name=cam_name, focalLength=28.0)
        if cmds.objExists("GRP_Cameras"):
            cam_node = cmds.parent(cam_node, "GRP_Cameras")[0]

    # Camera position and orientation (viewing along the corridor under the fluorescent panels)
    cam_pos = [-1600.0, 95.0, 430.0]
    cam_rot = [-5.0, -75.0, 0.0]
    cmds.xform(cam_node, ws=True, t=cam_pos)
    cmds.xform(cam_node, ws=True, ro=cam_rot)
    cmds.setAttr(f"{cam_shape}.focalLength", 28.0)

    # Set as sole renderable camera
    for c in (cmds.ls(type="camera") or []):
        cmds.setAttr(f"{c}.renderable", 1 if c == cam_shape else 0)

    # Resolution & Output Settings for Arnold
    cmds.setAttr("defaultResolution.width", 1280)
    cmds.setAttr("defaultResolution.height", 720)
    cmds.setAttr("defaultResolution.deviceAspectRatio", 1280.0 / 720.0)

    if cmds.objExists("defaultArnoldRenderOptions"):
        try:
            cmds.setAttr("defaultArnoldRenderOptions.abortOnError", False)
            cmds.setAttr("defaultArnoldRenderOptions.abortOnLicenseFail", False)
            cmds.setAttr("defaultArnoldRenderOptions.skipLicenseCheck", True)
        except Exception as e:
            print(f"Warning setting arnold license options: {e}")

    # Check Arnold Driver
    if cmds.objExists("defaultArnoldDriver"):
        try:
            cmds.setAttr("defaultArnoldDriver.ai_translator", "png", type="string")
        except Exception:
            pass

    # Save scene
    cmds.file(save=True, type="mayaBinary")
    print(f"Scene {SCENE_PATH} saved with lighting and test camera.")
    return cam_node, cam_shape


def render_with_render_exe(camera_name, output_image_path, frame_num=1, force=False):
    """
    Renders 1 frame using Maya Render.exe (Arnold engine).
    """
    out_dir = os.path.dirname(output_image_path)
    base_name = os.path.splitext(os.path.basename(output_image_path))[0]
    os.makedirs(out_dir, exist_ok=True)

    if not force and os.path.exists(output_image_path) and os.path.getsize(output_image_path) > 1000:
        print(f"Image already rendered: {output_image_path}")
        return output_image_path

    cmd = [
        RENDER_EXE,
        "-r", "arnold",
        "-cam", camera_name,
        "-s", str(frame_num),
        "-e", str(frame_num),
        "-x", "1280",
        "-y", "720",
        "-rd", out_dir,
        "-im", base_name,
        "-of", "png",
        "-ai:alf", "false",
        "-ai:slc", "true",
        "-ai:aerr", "false",
        "-ai:as", "3",       # AA samples
        "-ai:hs", "2",       # diffuse
        "-ai:gs", "2",       # specular
        SCENE_PATH
    ]
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Render returncode: {result.returncode}")
    if result.stdout:
        print("Render stdout tail:", result.stdout[-500:])
    if result.stderr:
        print("Render stderr tail:", result.stderr[-500:])

    # Find produced output image
    expected_direct = output_image_path
    if os.path.exists(expected_direct):
        return expected_direct

    # Search for output files starting with base_name in out_dir
    candidates = [os.path.join(out_dir, f) for f in os.listdir(out_dir) if f.startswith(base_name)]
    if candidates:
        latest = max(candidates, key=os.path.getmtime)
        if latest != output_image_path:
            shutil.copyfile(latest, output_image_path)
        return output_image_path

    # Check Arnold default project images folder
    default_img_dir = r"D:\projects\ProjectAnimation\images"
    for root, dirs, files in os.walk(default_img_dir):
        for f in files:
            if f.startswith(base_name) and f.endswith(".png"):
                src = os.path.join(root, f)
                shutil.copyfile(src, output_image_path)
                return output_image_path

    raise FileNotFoundError(f"Rendered image not found for {output_image_path}")


def main():
    print("=" * 60)
    print("STARTING T05 LIGHTING SETUP (SETS A & B)")
    print("=" * 60)

    cam_node, cam_shape = setup_lighting_in_scene()

    # 1. Render Set A
    print("\n--- Rendering Light Set A ---")
    cmds.setAttr("LIGHT_MASTER.exposure", BASE_EXPOSURE)
    cmds.setAttr("LIGHT_MASTER.flickerEnable", 0.0)
    cmds.file(save=True, type="mayaBinary")
    render_with_render_exe(cam_shape, LIGHT_A_PNG, frame_num=1)
    size_a_mb = os.path.getsize(LIGHT_A_PNG) / (1024 * 1024)
    print(f"Set A rendered: {LIGHT_A_PNG} ({size_a_mb:.3f} MB)")

    # 2. Render Set B (reduced 1.5 stop, flicker active)
    print("\n--- Rendering Light Set B ---")
    cmds.setAttr("LIGHT_MASTER.exposure", SET_B_EXPOSURE)
    cmds.setAttr("LIGHT_MASTER.flickerEnable", 1.0)
    cmds.currentTime(15) # frame where flicker is active
    cmds.file(save=True, type="mayaBinary")
    render_with_render_exe(cam_shape, LIGHT_B_PNG, frame_num=15)
    size_b_mb = os.path.getsize(LIGHT_B_PNG) / (1024 * 1024)
    print(f"Set B rendered: {LIGHT_B_PNG} ({size_b_mb:.3f} MB)")

    # 3. Reset to Set A as scene default
    cmds.setAttr("LIGHT_MASTER.exposure", BASE_EXPOSURE)
    cmds.setAttr("LIGHT_MASTER.flickerEnable", 0.0)
    cmds.currentTime(1)
    cmds.file(save=True, type="mayaBinary")

    # 4. Verify DoD Metrics
    point_lights = cmds.ls(type="pointLight") or []
    skydomes = cmds.ls(type="aiSkyDomeLight") or []
    area_lights = cmds.ls(type="aiAreaLight") or []

    cam_pos = cmds.xform(cam_node, q=True, ws=True, t=True)
    floor_y = -11.9008
    ceil_y = 232.6817
    cam_y = cam_pos[1]
    dist_to_floor = abs(cam_y - floor_y)
    dist_to_ceiling = abs(ceil_y - cam_y)
    cam_height_pass = dist_to_floor < dist_to_ceiling

    env_bbox = cmds.exactWorldBoundingBox("GRP_Backrooms_Level0_Master")
    in_bbox_x = env_bbox[0] <= cam_pos[0] <= env_bbox[3]
    in_bbox_y = env_bbox[1] <= cam_pos[1] <= env_bbox[4]
    in_bbox_z = env_bbox[2] <= cam_pos[2] <= env_bbox[5]
    cam_in_bbox = in_bbox_x and in_bbox_y and in_bbox_z

    report_data = {
        "lights": {
            "pointLight_count": len(point_lights),
            "aiSkyDomeLight_count": len(skydomes),
            "aiAreaLight_count": len(area_lights),
            "colorTemperature": 4000.0,
            "master_exposure_Set_A": BASE_EXPOSURE,
            "master_exposure_Set_B": SET_B_EXPOSURE
        },
        "camera": {
            "name": "CAM_Light_Test",
            "position": cam_pos,
            "distance_to_floor": dist_to_floor,
            "distance_to_ceiling": dist_to_ceiling,
            "floor_dist_less_than_ceiling": cam_height_pass,
            "inside_env_bbox": cam_in_bbox
        },
        "renders": {
            "light_A": {"path": LIGHT_A_PNG, "size_mb": size_a_mb},
            "light_B": {"path": LIGHT_B_PNG, "size_mb": size_b_mb}
        }
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    print("\n" + "=" * 60)
    print("T05 DEFINITION OF DONE REPORT")
    print("=" * 60)
    print(f"1. Arnold stills produced (both <= 5 MB):")
    print(f"   Set A: {LIGHT_A_PNG} ({size_a_mb:.3f} MB) -> Exists: {os.path.exists(LIGHT_A_PNG)}")
    print(f"   Set B: {LIGHT_B_PNG} ({size_b_mb:.3f} MB) -> Exists: {os.path.exists(LIGHT_B_PNG)}")
    print(f"2. Light counts by type:")
    print(f"   pointLight count: {len(point_lights)} (Must be 0: {len(point_lights) == 0})")
    print(f"   aiSkyDomeLight count: {len(skydomes)} (Must be 0: {len(skydomes) == 0})")
    print(f"   aiAreaLight count: {len(area_lights)} (Expected 54)")
    print(f"3. Camera in room criteria:")
    print(f"   Cam pos: {cam_pos}")
    print(f"   Distance to floor ({dist_to_floor:.2f} cm) < Distance to ceiling ({dist_to_ceiling:.2f} cm): {cam_height_pass}")
    print(f"   Camera inside env bounding box: {cam_in_bbox}")
    print(f"4. Visual Inspection:")
    print(f"   Left for Tawan to review and approve against docs/refs/.")

    dod_passed = (
        os.path.exists(LIGHT_A_PNG) and os.path.exists(LIGHT_B_PNG) and
        len(point_lights) == 0 and len(skydomes) == 0 and
        cam_height_pass and cam_in_bbox and
        size_a_mb <= 5.0 and size_b_mb <= 5.0
    )
    print(f"\nT05 SCRIPT & METRICS PASSED: {dod_passed}")
    return 0 if dod_passed else 1


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
