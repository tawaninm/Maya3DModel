"""
=============================================================================
T03: Fix Color Space and View Transform for Backrooms Environment
Source: scenes/Backrooms/Backrooms_Furniture_Scene.mb
Target: scenes/Backrooms/Backrooms_Env_v2.mb
Report: images/checks/colorspace_report.json
=============================================================================
"""

import os
import sys
import json
import struct

import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds

REPO_ROOT = r"D:\projects\ProjectAnimation"
GLB_PATH = os.path.join(REPO_ROOT, "raw_assets", "backrooms_vr.glb")
SRC_SCENE = os.path.join(REPO_ROOT, "scenes", "Backrooms", "Backrooms_Furniture_Scene.mb")
OUT_SCENE = os.path.join(REPO_ROOT, "scenes", "Backrooms", "Backrooms_Env_v2.mb")
REPORT_PATH = os.path.join(REPO_ROOT, "images", "checks", "colorspace_report.json")

RAW_ATTR_KEYWORDS = ["roughness", "specularroughness", "normal", "normalcamera", "metalness", "metallic", "bump", "displacement", "bumpvalue", "height"]


def parse_glb_texture_types(glb_file):
    """
    Parses materials and textures from the GLB using inspect_and_extract_glb.py logic
    to determine if any texture in the GLB is non-color (roughness, normal, etc.).
    """
    print(f"Reading GLB texture mapping from: {glb_file}")
    with open(glb_file, "rb") as f:
        f.read(12)
        chunk0_len, _ = struct.unpack("<I4s", f.read(8))
        gltf = json.loads(f.read(chunk0_len).decode("utf-8"))

    materials = gltf.get("materials", [])
    textures = gltf.get("textures", [])
    images = gltf.get("images", [])

    tex_map_types = {} # img_name -> set of types

    for m in materials:
        pbr = m.get("pbrMetallicRoughness", {})
        if "baseColorTexture" in pbr:
            idx = pbr["baseColorTexture"]["index"]
            img_idx = textures[idx].get("source", idx)
            name = images[img_idx].get("name", f"img_{img_idx}")
            tex_map_types.setdefault(name.lower(), set()).add("baseColor")
        if "metallicRoughnessTexture" in pbr:
            idx = pbr["metallicRoughnessTexture"]["index"]
            img_idx = textures[idx].get("source", idx)
            name = images[img_idx].get("name", f"img_{img_idx}")
            tex_map_types.setdefault(name.lower(), set()).add("metallicRoughness")
        if "normalTexture" in m:
            idx = m["normalTexture"]["index"]
            img_idx = textures[idx].get("source", idx)
            name = images[img_idx].get("name", f"img_{img_idx}")
            tex_map_types.setdefault(name.lower(), set()).add("normal")
        if "occlusionTexture" in m:
            idx = m["occlusionTexture"]["index"]
            img_idx = textures[idx].get("source", idx)
            name = images[img_idx].get("name", f"img_{img_idx}")
            tex_map_types.setdefault(name.lower(), set()).add("occlusion")

    print(f"GLB contains {len(images)} images across {len(materials)} materials.")
    return tex_map_types


def fix_scene_colorspace():
    print(f"Opening scene: {SRC_SCENE}")
    cmds.file(SRC_SCENE, open=True, force=True)

    # 1. Enable Color Management and set view transform to ACES 1.0 SDR-video
    cmds.colorManagementPrefs(e=True, cmEnabled=True)
    all_views = cmds.colorManagementPrefs(q=True, viewTransformNames=True) or []
    target_view = "ACES 1.0 SDR-video (sRGB)"
    if target_view not in all_views:
        # Fallback to any matching ACES view
        for v in all_views:
            if "ACES" in v and "SDR" in v:
                target_view = v
                break
    cmds.colorManagementPrefs(e=True, viewTransformName=target_view)
    actual_view = cmds.colorManagementPrefs(q=True, viewTransformName=True)
    actual_cm = cmds.colorManagementPrefs(q=True, cmEnabled=True)
    print(f"Color Management Enabled: {actual_cm}")
    print(f"View Transform set to: {actual_view}")

    glb_map_types = parse_glb_texture_types(GLB_PATH)

    # 2. Inspect and fix all file nodes
    file_nodes = cmds.ls(type="file")
    print(f"Found {len(file_nodes)} file nodes in scene.")

    report_entries = []
    non_raw_noncolor_count = 0

    for fn in file_nodes:
        tex_path = cmds.getAttr(f"{fn}.fileTextureName") or ""
        tex_base = os.path.basename(tex_path).lower()

        # Find connected plugs
        dest_plugs = cmds.listConnections(fn, source=False, destination=True, plugs=True) or []
        connected_channels = []
        is_raw_channel = False

        for plug in dest_plugs:
            attr_name = plug.split(".")[-1].lower()
            if "texturelist" in plug.lower():
                continue
            connected_channels.append(plug)
            for kw in RAW_ATTR_KEYWORDS:
                if kw in attr_name:
                    is_raw_channel = True
                    break

        # Check GLB texture type as well
        if any(kw in tex_base for kw in ["rough", "norm", "metal", "bump", "disp", "height"]):
            is_raw_channel = True

        # Unlock color space rule so manual assignment sticks
        if cmds.attributeQuery("ignoreColorSpaceFileRules", node=fn, exists=True):
            cmds.setAttr(f"{fn}.ignoreColorSpaceFileRules", 1)

        # Set appropriate color space
        if is_raw_channel:
            target_cs = "Raw"
        else:
            target_cs = "sRGB"

        # Apply target color space
        available_spaces = cmds.colorManagementPrefs(q=True, inputSpaceNames=True) or []
        # Find exact space name
        matched_cs = target_cs
        for s in available_spaces:
            if s.lower() == target_cs.lower() or (target_cs == "sRGB" and "srgb" in s.lower() and "rec.709" in s.lower()):
                matched_cs = s
                break

        try:
            cmds.setAttr(f"{fn}.colorSpace", matched_cs, type="string")
        except Exception as e:
            print(f"Warning setting colorSpace on {fn}: {e}")

        final_cs = cmds.getAttr(f"{fn}.colorSpace")

        # Verify DoD rule: map connected to roughness, normal, metalness, bump, displacement must NOT be sRGB
        is_srgb = ("srgb" in final_cs.lower())
        if is_raw_channel and is_srgb:
            non_raw_noncolor_count += 1

        entry = {
            "node": fn,
            "texture_path": tex_path,
            "connected_channels": connected_channels,
            "is_raw_channel": is_raw_channel,
            "colorSpace": final_cs,
            "valid": not (is_raw_channel and is_srgb)
        }
        report_entries.append(entry)

    # 3. Save report JSON
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    report_data = {
        "scene": OUT_SCENE,
        "viewTransform": actual_view,
        "colorManagementEnabled": actual_cm,
        "total_file_nodes": len(file_nodes),
        "non_raw_utility_maps_count": non_raw_noncolor_count,
        "file_nodes": report_entries
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    print(f"Report saved to: {REPORT_PATH}")

    # 4. Save As scenes/Backrooms/Backrooms_Env_v2.mb (never overwrite existing scenes)
    os.makedirs(os.path.dirname(OUT_SCENE), exist_ok=True)
    cmds.file(rename=OUT_SCENE)
    saved = cmds.file(save=True, type="mayaBinary")
    print(f"Saved new environment scene to: {saved}")

    # DoD Summary
    print("\n" + "=" * 60)
    print("T03 DEFINITION OF DONE REPORT")
    print("=" * 60)
    print(f"1. colorspace_report.json exists: {os.path.exists(REPORT_PATH)} ({len(report_entries)} file nodes recorded)")
    print(f"2. Maps connected to roughness/normal/metalness/bump/displacement with sRGB: {non_raw_noncolor_count} (Pass: {non_raw_noncolor_count == 0})")
    print(f"3. View transform: '{actual_view}' (Pass: {'ACES 1.0 SDR-video' in actual_view})")
    all_passed = (os.path.exists(REPORT_PATH) and non_raw_noncolor_count == 0 and "ACES 1.0 SDR-video" in actual_view and os.path.exists(OUT_SCENE))
    print(f"\nT03 ALL DOD CRITERIA PASSED: {all_passed}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    ret = fix_scene_colorspace()
    sys.exit(ret)
