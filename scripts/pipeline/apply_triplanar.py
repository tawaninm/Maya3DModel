"""
=============================================================================
T04: Triplanar Projection for Walls, Carpet, and Ceiling
Target: scenes/Backrooms/Backrooms_Env_v2.mb
Report: images/checks/triplanar_report.json
=============================================================================
"""

import os
import sys
import json

import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds

SCENE_PATH = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Env_v2.mb"
REPORT_PATH = r"D:\projects\ProjectAnimation\images\checks\triplanar_report.json"

# Scale in world space: 0.005 = 1 repeat per 200 cm (2 meters)
TRIPLANAR_SCALE = 0.005
TRIPLANAR_BLEND = 0.2


def apply_triplanar_projection():
    print(f"Opening scene: {SCENE_PATH}")
    cmds.file(SCENE_PATH, open=True, force=True)
    cmds.loadPlugin("mtoa", quiet=True)

    # Shading engines to inspect
    all_sgs = cmds.ls(type="shadingEngine") or []

    wall_shaders = []
    carpet_shaders = []
    ceiling_shaders = []
    prop_shaders = []

    for sg in all_sgs:
        if sg in ["initialShadingGroup", "initialParticleSE"]:
            continue
        sh_conn = cmds.listConnections(f"{sg}.surfaceShader")
        if not sh_conn:
            continue
        shader = sh_conn[0]
        s_lower = shader.lower()

        if "wall" in s_lower:
            wall_shaders.append((sg, shader))
        elif "moquette" in s_lower or "carpet" in s_lower:
            carpet_shaders.append((sg, shader))
        elif "ceiling" in s_lower and "lamp" not in s_lower:
            ceiling_shaders.append((sg, shader))
        else:
            prop_shaders.append((sg, shader))

    # Remove duplicates
    wall_shaders = list(dict.fromkeys(wall_shaders))
    carpet_shaders = list(dict.fromkeys(carpet_shaders))
    ceiling_shaders = list(dict.fromkeys(ceiling_shaders))
    prop_shaders = list(dict.fromkeys(prop_shaders))

    print(f"Identified {len(wall_shaders)} wall shaders: {[s[1] for s in wall_shaders]}")
    print(f"Identified {len(carpet_shaders)} carpet shaders: {[s[1] for s in carpet_shaders]}")
    print(f"Identified {len(ceiling_shaders)} ceiling shaders: {[s[1] for s in ceiling_shaders]}")
    print(f"Identified {len(prop_shaders)} prop shaders: {[s[1] for s in prop_shaders]}")

    triplanar_targets = wall_shaders + carpet_shaders + ceiling_shaders
    modified_records = []
    untouched_prop_records = []

    # 1. Process Wall, Carpet, Ceiling shaders
    for sg, shader in triplanar_targets:
        # Determine color attribute
        color_attr = "baseColor" if cmds.attributeQuery("baseColor", node=shader, exists=True) else "color"

        # Find incoming connection
        incoming = cmds.listConnections(f"{shader}.{color_attr}", source=True, destination=False) or []
        file_node = None
        current_triplanar = None

        for src in incoming:
            if cmds.nodeType(src) == "file":
                file_node = src
            elif cmds.nodeType(src) == "aiTriplanar":
                current_triplanar = src
                # Find file node feeding the triplanar
                tri_in = cmds.listConnections(f"{current_triplanar}.input", source=True, destination=False) or []
                for t_src in tri_in:
                    if cmds.nodeType(t_src) == "file":
                        file_node = t_src

        if not file_node and not current_triplanar:
            print(f"Warning: No file node or triplanar found for {shader}.{color_attr}")
            continue

        if not current_triplanar:
            triplanar_name = f"aiTriplanar_{shader}"
            if cmds.objExists(triplanar_name):
                cmds.delete(triplanar_name)
            current_triplanar = cmds.shadingNode("aiTriplanar", asTexture=True, name=triplanar_name)

        # Set world space (0) and uniform scale
        cmds.setAttr(f"{current_triplanar}.coordSpace", 0) # 0 = world
        cmds.setAttr(f"{current_triplanar}.scale", TRIPLANAR_SCALE, TRIPLANAR_SCALE, TRIPLANAR_SCALE, type="float3")
        cmds.setAttr(f"{current_triplanar}.blend", TRIPLANAR_BLEND)

        # Connect file node to aiTriplanar input
        if file_node:
            cmds.connectAttr(f"{file_node}.outColor", f"{current_triplanar}.input", force=True)

        # Connect aiTriplanar to shader
        cmds.connectAttr(f"{current_triplanar}.outColor", f"{shader}.{color_attr}", force=True)

        # Record details
        cs_val = cmds.getAttr(f"{current_triplanar}.coordSpace")
        scale_val = cmds.getAttr(f"{current_triplanar}.scale")[0]
        tex_path = cmds.getAttr(f"{file_node}.fileTextureName") if file_node else "N/A"

        modified_records.append({
            "shading_group": sg,
            "shader": shader,
            "category": "wall" if "wall" in shader.lower() else ("carpet" if "moquette" in shader.lower() else "ceiling"),
            "file_node": file_node,
            "texture": tex_path,
            "triplanar_node": current_triplanar,
            "coordSpace": "world" if cs_val == 0 else f"other({cs_val})",
            "scale": scale_val,
            "status": "connected_aiTriplanar_world"
        })
        print(f"  [OK] Wired {shader} -> {current_triplanar} (coordSpace=world, scale={scale_val})")

    # 2. Verify Prop shaders remain untouched (direct file / UV connections)
    for sg, shader in prop_shaders:
        color_attr = "baseColor" if cmds.attributeQuery("baseColor", node=shader, exists=True) else "color"
        incoming = cmds.listConnections(f"{shader}.{color_attr}", source=True, destination=False) or []
        has_triplanar = any(cmds.nodeType(n) == "aiTriplanar" for n in incoming)
        file_nodes = [n for n in incoming if cmds.nodeType(n) == "file"]
        tex_path = cmds.getAttr(f"{file_nodes[0]}.fileTextureName") if file_nodes else "None/Color"

        untouched_prop_records.append({
            "shading_group": sg,
            "shader": shader,
            "incoming_nodes": incoming,
            "texture": tex_path,
            "has_triplanar": has_triplanar,
            "status": "untouched_uv_mapping"
        })

    # Save scene
    cmds.file(save=True, type="mayaBinary")
    print(f"Updated Backrooms_Env_v2.mb saved successfully.")

    # Save report JSON
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    report_data = {
        "modified_shaders_count": len(modified_records),
        "untouched_prop_shaders_count": len(untouched_prop_records),
        "triplanar_scale": TRIPLANAR_SCALE,
        "triplanar_coord_space": "world",
        "modified_wall_carpet_ceiling": modified_records,
        "untouched_props": untouched_prop_records
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    print(f"Triplanar report saved to: {REPORT_PATH}")

    # DoD Verification
    all_target_world = all(r["coordSpace"] == "world" for r in modified_records)
    all_scales_equal = all(r["scale"] == modified_records[0]["scale"] for r in modified_records) if modified_records else False
    all_props_untouched = all(not r["has_triplanar"] for r in untouched_prop_records)

    print("\n" + "=" * 60)
    print("T04 DEFINITION OF DONE REPORT")
    print("=" * 60)
    print(f"1. Wall, carpet, ceiling shaders wired to aiTriplanar (world space, uniform scale):")
    print(f"   Modified shaders count: {len(modified_records)}")
    print(f"   All in world space: {all_target_world} (Pass: {all_target_world})")
    print(f"   All scales equal: {all_scales_equal} (Scale: {TRIPLANAR_SCALE}) (Pass: {all_scales_equal})")
    print(f"2. Prop shaders untouched (direct UV mapping):")
    print(f"   Prop shaders count: {len(untouched_prop_records)}")
    print(f"   All props untouched: {all_props_untouched} (Pass: {all_props_untouched})")

    dod_passed = all_target_world and all_scales_equal and all_props_untouched and len(modified_records) > 0
    print(f"\nT04 ALL DOD CRITERIA PASSED: {dod_passed}")
    return 0 if dod_passed else 1


if __name__ == "__main__":
    ret = apply_triplanar_projection()
    sys.exit(ret)
