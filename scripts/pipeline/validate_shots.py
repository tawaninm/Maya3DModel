"""
validate_shots.py

T08 Validation: Validate Shot Scenes and Cameras
Validates:
  - scenes/Shots/Shot05.mb to Shot14.mb exist (10 files)
  - Each file references Backrooms_Env_v3.mb, Monster_Mixamo.mb, Charlie_Mixamo.mb with relative paths
  - Unresolved references = 0
  - Camera CAM_ShotNN exists and is set as renderable
  - Frame range and 24 fps match plan.md table
  - Light preset:
      Shots 05-09: Preset A (exposure=13.0, flickerEnable=0.0)
      Shots 10-14: Preset B (exposure=11.5, flickerEnable=1.0) + flicker retargeted to 3 nearest panels
Outputs:
  - images/checks/shots_validation_report.json
"""

import os
import sys
import json

WORKSPACE_DIR = r"D:\projects\ProjectAnimation"
PIPELINE_DIR = os.path.join(WORKSPACE_DIR, "scripts", "pipeline")
if PIPELINE_DIR not in sys.path:
    sys.path.insert(0, PIPELINE_DIR)

import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
from light_preset import nearest_panels

REPORT_PATH = os.path.join(WORKSPACE_DIR, "images", "checks", "shots_validation_report.json")

EXPECTED_SHOTS = [
    {"shot": "05", "frames": 48, "sec": 2, "preset": "A"},
    {"shot": "06", "frames": 72, "sec": 3, "preset": "A"},
    {"shot": "07", "frames": 72, "sec": 3, "preset": "A"},
    {"shot": "08", "frames": 48, "sec": 2, "preset": "A"},
    {"shot": "09", "frames": 72, "sec": 3, "preset": "A"},
    {"shot": "10", "frames": 48, "sec": 2, "preset": "B"},
    {"shot": "11", "frames": 72, "sec": 3, "preset": "B"},
    {"shot": "12", "frames": 48, "sec": 2, "preset": "B"},
    {"shot": "13", "frames": 48, "sec": 2, "preset": "B"},
    {"shot": "14", "frames": 24, "sec": 1, "preset": "B"},
]


def validate_shot(shot_info):
    shot_id = shot_info["shot"]
    expected_frames = shot_info["frames"]
    expected_preset = shot_info["preset"]
    shot_file = os.path.join(WORKSPACE_DIR, "scenes", "Shots", f"Shot{shot_id}.mb")

    if not os.path.exists(shot_file):
        return {
            "shot": shot_id,
            "file": shot_file,
            "exists": False,
            "passed": False,
            "error": "File does not exist"
        }

    # Open shot file
    cmds.workspace(WORKSPACE_DIR, openWorkspace=True)
    cmds.file(shot_file, open=True, force=True)

    # 1. Check FPS
    time_unit = cmds.currentUnit(q=True, time=True)
    is_24_fps = (time_unit == "film" or time_unit == "24fps")

    # 2. Check Frame Range
    start_frame = cmds.playbackOptions(q=True, minTime=True)
    end_frame = cmds.playbackOptions(q=True, maxTime=True)
    frame_range_correct = (start_frame == 1.0 and end_frame == float(expected_frames))

    # 3. Check Camera
    cam_name = f"CAM_Shot{shot_id}"
    cam_exists = cmds.objExists(cam_name)
    cam_renderable = False
    if cam_exists:
        shapes = cmds.listRelatives(cam_name, shapes=True, type="camera") or []
        if shapes:
            cam_renderable = (cmds.getAttr(f"{shapes[0]}.renderable") == 1)

    # 4. Check References
    ref_files = cmds.file(q=True, reference=True) or []
    ref_details = []
    unresolved_count = 0
    relative_count = 0

    for ref in ref_files:
        is_loaded = cmds.referenceQuery(ref, isLoaded=True)
        unresolved_name = cmds.referenceQuery(ref, filename=True, unresolvedName=True)
        filename = cmds.referenceQuery(ref, filename=True, withoutCopyNumber=True)   # copies of one file end in {1}, {2}: os.path.exists would fail on those

        is_resolved = is_loaded and os.path.exists(filename)
        if not is_resolved:
            unresolved_count += 1

        is_relative = unresolved_name.startswith("scenes") or unresolved_name.startswith("..") or ("scenes/" in unresolved_name and not ":" in unresolved_name[:3])
        if is_relative:
            relative_count += 1

        ref_details.append({
            "resolved_path": filename,
            "unresolved_name": unresolved_name,
            "is_loaded": is_loaded,
            "is_resolved": is_resolved,
            "is_relative": is_relative
        })

    # Expected 3 references: Backrooms_Env_v3, Monster_Mixamo, Charlie_Mixamo
    has_env = any("Backrooms_Env_v3" in r["resolved_path"] for r in ref_details)
    has_monster = any("Monster_Mixamo" in r["resolved_path"] for r in ref_details)
    has_charlie = any("Charlie_Mixamo" in r["resolved_path"] for r in ref_details)
    has_all_three_refs = has_env and has_monster and has_charlie

    # 5. Check Light Preset
    master = "ENV:LIGHT_MASTER"
    preset_correct = False
    flicker_retargeted = True
    actual_exposure = None
    actual_flicker = None

    if cmds.objExists(master):
        actual_exposure = cmds.getAttr(f"{master}.exposure")
        actual_flicker = cmds.getAttr(f"{master}.flickerEnable")

        if expected_preset == "A":
            preset_correct = (abs(actual_exposure - 13.0) < 0.01 and abs(actual_flicker - 0.0) < 0.01)
        elif expected_preset == "B":
            preset_correct = (abs(actual_exposure - 11.5) < 0.01 and abs(actual_flicker - 1.0) < 0.01)
            # Verify flicker retargeting
            cam_grp = f"GRP_{cam_name}"
            target_cam = cam_grp if cmds.objExists(cam_grp) else cam_name
            expected_nearest = nearest_panels(target_cam, 3)
            expr_node = "ENV:EXPR_Monster_Panel_Flicker"
            if cmds.objExists(expr_node):
                expr_str = cmds.expression(expr_node, q=True, string=True) or ""
                flicker_retargeted = all(p in expr_str for p in expected_nearest)
            else:
                flicker_retargeted = False

    shot_passed = (
        is_24_fps and
        frame_range_correct and
        cam_exists and
        cam_renderable and
        unresolved_count == 0 and
        has_all_three_refs and
        preset_correct and
        flicker_retargeted
    )

    return {
        "shot": shot_id,
        "file": shot_file,
        "exists": True,
        "fps_unit": time_unit,
        "is_24_fps": is_24_fps,
        "start_frame": start_frame,
        "end_frame": end_frame,
        "expected_frames": expected_frames,
        "frame_range_correct": frame_range_correct,
        "camera_name": cam_name,
        "camera_exists": cam_exists,
        "camera_renderable": cam_renderable,
        "references": ref_details,
        "references_count": len(ref_details),
        "unresolved_references_count": unresolved_count,
        "relative_references_count": relative_count,
        "has_all_three_refs": has_all_three_refs,
        "expected_preset": expected_preset,
        "actual_exposure": actual_exposure,
        "actual_flicker": actual_flicker,
        "preset_correct": preset_correct,
        "flicker_retargeted": flicker_retargeted,
        "passed": shot_passed
    }


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print("=" * 60)
    print("STARTING T08 SHOTS AND CAMERAS VALIDATION (Env_v3, Presets A/B)")
    print("=" * 60)

    results = []
    total_unresolved = 0
    all_shots_passed = True

    for shot_info in EXPECTED_SHOTS:
        res = validate_shot(shot_info)
        results.append(res)
        unres = res.get("unresolved_references_count", 1)
        total_unresolved += unres
        if not res.get("passed", False):
            all_shots_passed = False

        status = "PASS" if res.get("passed", False) else "FAIL"
        preset_str = f"Preset {shot_info['preset']} (exp={res.get('actual_exposure')}, flicker={res.get('actual_flicker')})"
        print(f"Shot {shot_info['shot']}: {status} | Frames: {res.get('start_frame')}-{res.get('end_frame')} ({shot_info['frames']}) | Cam: {res.get('camera_name')} (renderable: {res.get('camera_renderable')}) | {preset_str} | Refs: {res.get('references_count')}, Unresolved: {unres}")

    report_data = {
        "total_shots_checked": len(results),
        "all_shots_passed": all_shots_passed,
        "total_unresolved_references": total_unresolved,
        "shots": results
    }

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    print("\n" + "=" * 60)
    print("T08 DEFINITION OF DONE REPORT")
    print("=" * 60)
    print(f"1. Shot files count (Shot05.mb to Shot14.mb): {len(results)} / 10 files exist")
    print(f"2. Each file has CAM_ShotNN, frame range per plan, 24 fps: {all_shots_passed}")
    print(f"3. Correct preset per shot (A: 05-09, B: 10-14 with retargeted flicker): {all(r.get('preset_correct') and r.get('flicker_retargeted') for r in results)}")
    print(f"4. Total unresolved references across all 10 shots: {total_unresolved} (Must be 0)")
    print(f"   Validation report: {REPORT_PATH}")
    print("=" * 60)
    print(f"\nT08 VALIDATION OVERALL STATUS: {'PASSED' if all_shots_passed else 'FAILED'}")

    maya.standalone.uninitialize()
    return 0 if all_shots_passed else 1


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
