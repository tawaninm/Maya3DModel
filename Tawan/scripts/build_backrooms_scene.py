"""
=============================================================================
BACKROOMS PROPS & LEVEL 0 ENVIRONMENT GENERATOR (MAYA / ARNOLD)
=============================================================================
Author: TAWAN-OS 3D Automation Pipeline
Compatible with: Autodesk Maya 2024 / 2025 / 2026 / 2027 + Arnold (MtoA)
Reference: backrooms_vr.glb & Meshy_AI_Buff_Blobbell

Features:
- Clean Quad-based procedural modeling with SubD support and bevel highlights
- Retro 90s Armchair (ArmChair_1) with ergonomic cushions and tapered legs
- Vintage Wooden Office Desk (Furniture_1) with 3-tier drawer gaps and handles
- Fluorescent Ceiling Fixtures (Ceiling_Lamp) with dual T8 tubes and socket caps
- Emergency Exit Door set with lever handles, kickplate, and illuminated EXIT box
- Slotted Wall HVAC Vent and Dual Power Sockets
- Modular Room (Damp carpet, Acoustic ceiling tiles, Mono-yellow walls, Pillar)
- Arnold aiStandardSurface materials with accurate PBR and Color Temperatures
- Multi-point Arnold Area Lights and Cinematic Cameras
=============================================================================
"""

import sys
import os
import math

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# 1. Initialize Maya Standalone if running via mayapy
try:
    import maya.standalone
    maya.standalone.initialize(name="python")
    print("[TAWAN-OS] Maya Standalone Initialized successfully.")
except Exception as e:
    # Already running in GUI or already initialized
    pass

import maya.cmds as cmds


def create_material(mat_name, shader_type="aiStandardSurface", **attrs):
    """Safely creates an Arnold or Maya material and its shading engine."""
    if "ai" in shader_type.lower():
        if not cmds.pluginInfo("mtoa", query=True, loaded=True):
            try:
                cmds.loadPlugin("mtoa")
            except:
                print("[WARNING] Arnold (mtoa) plugin not found. Falling back to standardSurface / phong.")
                shader_type = "standardSurface" if cmds.objExists("standardSurface") else "phong"

    if cmds.objExists(mat_name):
        cmds.delete(mat_name)
    sg_name = f"{mat_name}SG"
    if cmds.objExists(sg_name):
        cmds.delete(sg_name)

    shader = cmds.shadingNode(shader_type, asShader=True, name=mat_name)
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg_name)
    cmds.connectAttr(f"{shader}.outColor", f"{sg}.surfaceShader", force=True)

    for attr, val in attrs.items():
        attr_full = f"{shader}.{attr}"
        if cmds.objExists(attr_full):
            try:
                if isinstance(val, (list, tuple)) and len(val) == 3:
                    cmds.setAttr(attr_full, val[0], val[1], val[2], type="double3")
                elif isinstance(val, (int, float, bool)):
                    cmds.setAttr(attr_full, val)
                elif isinstance(val, str):
                    cmds.setAttr(attr_full, val, type="string")
            except Exception as err:
                print(f"[WARN] Could not set {attr_full} = {val}: {err}")

    return shader, sg


def assign_material(mesh_or_faces, sg_name):
    """Assigns shading group to given transform, shape, or face components."""
    if cmds.objExists(sg_name) and cmds.objExists(mesh_or_faces):
        cmds.sets(mesh_or_faces, edit=True, forceElement=sg_name)


def setup_backrooms_shaders():
    """Builds the complete palette of Arnold PBR materials for Backrooms Level 0."""
    shaders = {}

    _, shaders["wallpaper"] = create_material(
        "M_Backrooms_Wallpaper", "aiStandardSurface",
        base=1.0,
        baseColor=(0.768, 0.651, 0.380),
        specularRoughness=0.72,
        specularIOR=1.50
    )

    _, shaders["carpet"] = create_material(
        "M_Backrooms_Carpet", "aiStandardSurface",
        base=1.0,
        baseColor=(0.494, 0.474, 0.321),
        specularRoughness=0.92,
        sheen=0.35,
        sheenColor=(0.65, 0.62, 0.45)
    )

    _, shaders["ceiling"] = create_material(
        "M_Backrooms_CeilingTile", "aiStandardSurface",
        base=1.0,
        baseColor=(0.721, 0.705, 0.643),
        specularRoughness=0.88,
        specularIOR=1.45
    )

    _, shaders["metal_white"] = create_material(
        "M_Lamp_Housing_White", "aiStandardSurface",
        base=1.0,
        baseColor=(0.88, 0.88, 0.86),
        specularRoughness=0.32,
        specularIOR=1.52
    )

    _, shaders["fluorescent_tube"] = create_material(
        "M_Fluorescent_Tube_Glow", "aiStandardSurface",
        base=0.1,
        baseColor=(1.0, 1.0, 1.0),
        emission=4.5,
        emissionColor=(1.0, 0.94, 0.82)
    )

    _, shaders["wood_walnut"] = create_material(
        "M_Retro_Walnut_Wood", "aiStandardSurface",
        base=1.0,
        baseColor=(0.290, 0.180, 0.094),
        specularRoughness=0.40,
        specularIOR=1.54
    )

    _, shaders["armchair_fabric"] = create_material(
        "M_Armchair_Fabric_Olive", "aiStandardSurface",
        base=1.0,
        baseColor=(0.541, 0.509, 0.419),
        specularRoughness=0.82,
        sheen=0.50,
        sheenColor=(0.75, 0.72, 0.60)
    )

    _, shaders["metal_dark"] = create_material(
        "M_Metal_Dark_Matte", "aiStandardSurface",
        base=0.9,
        baseColor=(0.12, 0.12, 0.13),
        metalness=0.85,
        specularRoughness=0.38
    )

    _, shaders["chrome"] = create_material(
        "M_Stainless_Steel", "aiStandardSurface",
        base=1.0,
        baseColor=(0.92, 0.92, 0.94),
        metalness=0.98,
        specularRoughness=0.15
    )

    _, shaders["exit_red"] = create_material(
        "M_Exit_Sign_Glow", "aiStandardSurface",
        base=0.2,
        baseColor=(0.85, 0.08, 0.08),
        emission=3.2,
        emissionColor=(1.0, 0.1, 0.1)
    )

    _, shaders["plastic_ivory"] = create_material(
        "M_Plastic_WallSocket", "aiStandardSurface",
        base=1.0,
        baseColor=(0.86, 0.84, 0.78),
        specularRoughness=0.45
    )

    return shaders


def build_retro_armchair(shaders):
    chair_grp = cmds.group(empty=True, name="GRP_Retro_Armchair")

    base_frame = cmds.polyCube(name="Armchair_Base_Plinth", width=68, depth=66, height=8)[0]
    cmds.setAttr(f"{base_frame}.translateY", 20)
    cmds.polyBevel3(base_frame, fraction=0.08, offsetAsFraction=True, segments=2)
    assign_material(base_frame, shaders["metal_dark"])
    cmds.parent(base_frame, chair_grp)

    seat = cmds.polyCube(name="Armchair_Seat_Cushion", width=60, depth=58, height=14, 
                         subdivisionsX=4, subdivisionsY=2, subdivisionsZ=4)[0]
    cmds.setAttr(f"{seat}.translateY", 31)
    cmds.setAttr(f"{seat}.translateZ", 2)
    cmds.polyBevel3(seat, fraction=0.18, offsetAsFraction=True, segments=3)
    assign_material(seat, shaders["armchair_fabric"])
    cmds.parent(seat, chair_grp)

    backrest = cmds.polyCube(name="Armchair_Backrest", width=60, depth=14, height=52,
                             subdivisionsX=3, subdivisionsY=3, subdivisionsZ=2)[0]
    cmds.setAttr(f"{backrest}.translateY", 60)
    cmds.setAttr(f"{backrest}.translateZ", -24)
    cmds.setAttr(f"{backrest}.rotateX", -8)
    cmds.polyBevel3(backrest, fraction=0.15, offsetAsFraction=True, segments=3)
    assign_material(backrest, shaders["armchair_fabric"])
    cmds.parent(backrest, chair_grp)

    for side, sign, name in [(1, -1, "L"), (2, 1, "R")]:
        armrest = cmds.polyCube(name=f"Armchair_Armrest_{name}", width=12, depth=72, height=42,
                                subdivisionsX=2, subdivisionsY=2, subdivisionsZ=3)[0]
        cmds.setAttr(f"{armrest}.translateX", sign * 36)
        cmds.setAttr(f"{armrest}.translateY", 42)
        cmds.setAttr(f"{armrest}.translateZ", -2)
        cmds.polyBevel3(armrest, fraction=0.14, offsetAsFraction=True, segments=3)
        assign_material(armrest, shaders["armchair_fabric"])
        cmds.parent(armrest, chair_grp)

    leg_coords = [
        ("FL", -28, 24),
        ("FR", 28, 24),
        ("BL", -28, -24),
        ("BR", 28, -24)
    ]
    for leg_name, lx, lz in leg_coords:
        leg = cmds.polyCylinder(name=f"Armchair_Leg_{leg_name}", radius=2.4, height=16, subdivisionsAxis=12)[0]
        cmds.setAttr(f"{leg}.translateX", lx)
        cmds.setAttr(f"{leg}.translateY", 8)
        cmds.setAttr(f"{leg}.translateZ", lz)
        
        rot_z = 6 if lx < 0 else -6
        rot_x = -6 if lz < 0 else 6
        cmds.setAttr(f"{leg}.rotateX", rot_x)
        cmds.setAttr(f"{leg}.rotateZ", rot_z)
        assign_material(leg, shaders["wood_walnut"])
        cmds.parent(leg, chair_grp)

        foot = cmds.polyCylinder(name=f"Armchair_FootCap_{leg_name}", radius=2.6, height=3.5, subdivisionsAxis=12)[0]
        cmds.setAttr(f"{foot}.translateX", lx)
        cmds.setAttr(f"{foot}.translateY", 1.75)
        cmds.setAttr(f"{foot}.translateZ", lz)
        assign_material(foot, shaders["chrome"])
        cmds.parent(foot, chair_grp)

    cmds.xform(chair_grp, translation=(-140, 0, 60), rotation=(0, 25, 0), worldSpace=True)
    return chair_grp


def build_retro_office_desk(shaders):
    desk_grp = cmds.group(empty=True, name="GRP_Retro_Office_Desk")

    top_slab = cmds.polyCube(name="Desk_Top_Slab", width=150, depth=75, height=3.8)[0]
    cmds.setAttr(f"{top_slab}.translateY", 73.1)
    cmds.polyBevel3(top_slab, fraction=0.03, offsetAsFraction=True, segments=2)
    assign_material(top_slab, shaders["wood_walnut"])
    cmds.parent(top_slab, desk_grp)

    pedestal = cmds.polyCube(name="Desk_Pedestal_Body", width=42, depth=70, height=65)[0]
    cmds.setAttr(f"{pedestal}.translateX", -48)
    cmds.setAttr(f"{pedestal}.translateY", 36.5)
    cmds.polyBevel3(pedestal, fraction=0.02, offsetAsFraction=True, segments=2)
    assign_material(pedestal, shaders["wood_walnut"])
    cmds.parent(pedestal, desk_grp)

    drawer_heights = [18, 18, 24]
    current_y = 61.0

    for i, dh in enumerate(drawer_heights, 1):
        center_y = current_y - (dh / 2.0)
        drawer_face = cmds.polyCube(name=f"Desk_Drawer_Face_{i}", width=40.8, depth=2.2, height=dh - 0.6)[0]
        cmds.setAttr(f"{drawer_face}.translateX", -48)
        cmds.setAttr(f"{drawer_face}.translateY", center_y)
        cmds.setAttr(f"{drawer_face}.translateZ", 35.8)
        cmds.polyBevel3(drawer_face, fraction=0.04, offsetAsFraction=True, segments=2)
        assign_material(drawer_face, shaders["wood_walnut"])
        cmds.parent(drawer_face, desk_grp)

        handle_bar = cmds.polyCube(name=f"Desk_Drawer_Handle_{i}", width=14, depth=1.6, height=1.6)[0]
        cmds.setAttr(f"{handle_bar}.translateX", -48)
        cmds.setAttr(f"{handle_bar}.translateY", center_y)
        cmds.setAttr(f"{handle_bar}.translateZ", 37.8)
        cmds.polyBevel3(handle_bar, fraction=0.1, offsetAsFraction=True, segments=2)
        assign_material(handle_bar, shaders["chrome"])
        cmds.parent(handle_bar, desk_grp)

        current_y -= dh

    modesty_panel = cmds.polyCube(name="Desk_Modesty_Panel", width=102, depth=1.8, height=45)[0]
    cmds.setAttr(f"{modesty_panel}.translateX", 21)
    cmds.setAttr(f"{modesty_panel}.translateY", 46)
    cmds.setAttr(f"{modesty_panel}.translateZ", -28)
    assign_material(modesty_panel, shaders["wood_walnut"])
    cmds.parent(modesty_panel, desk_grp)

    metal_panel = cmds.polyCube(name="Desk_Side_Panel_Right", width=2.8, depth=68, height=68)[0]
    cmds.setAttr(f"{metal_panel}.translateX", 71)
    cmds.setAttr(f"{metal_panel}.translateY", 35)
    assign_material(metal_panel, shaders["metal_dark"])
    cmds.parent(metal_panel, desk_grp)

    for fx, fz in [(-64, 30), (-64, -30), (-32, 30), (-32, -30), (71, 30), (71, -30)]:
        foot = cmds.polyCylinder(name="Desk_Foot_Leveler", radius=1.8, height=2.0, subdivisionsAxis=10)[0]
        cmds.setAttr(f"{foot}.translateX", fx)
        cmds.setAttr(f"{foot}.translateY", 1.0)
        cmds.setAttr(f"{foot}.translateZ", fz)
        assign_material(foot, shaders["metal_dark"])
        cmds.parent(foot, desk_grp)

    cmds.xform(desk_grp, translation=(-160, 0, -40), rotation=(0, 10, 0), worldSpace=True)
    return desk_grp


def build_fluorescent_fixture(name_prefix, x, z, shaders, parent_grp=None):
    lamp_grp = cmds.group(empty=True, name=f"GRP_{name_prefix}")

    housing = cmds.polyCube(name=f"{name_prefix}_Housing", width=34, depth=124, height=8)[0]
    cmds.setAttr(f"{housing}.translateY", 298)
    cmds.polyBevel3(housing, fraction=0.04, offsetAsFraction=True, segments=2)
    assign_material(housing, shaders["metal_white"])
    cmds.parent(housing, lamp_grp)

    for tube_idx, offset_x in enumerate([-6.5, 6.5], 1):
        tube = cmds.polyCylinder(name=f"{name_prefix}_Tube_{tube_idx}", radius=1.3, height=112, subdivisionsAxis=14)[0]
        cmds.setAttr(f"{tube}.translateX", offset_x)
        cmds.setAttr(f"{tube}.translateY", 296.2)
        cmds.setAttr(f"{tube}.rotateX", 90)
        assign_material(tube, shaders["fluorescent_tube"])
        cmds.parent(tube, lamp_grp)

        for cap_idx, cap_z in [(1, -57), (2, 57)]:
            cap = cmds.polyCylinder(name=f"{name_prefix}_Cap_{tube_idx}_{cap_idx}", radius=1.6, height=3.0, subdivisionsAxis=10)[0]
            cmds.setAttr(f"{cap}.translateX", offset_x)
            cmds.setAttr(f"{cap}.translateY", 296.2)
            cmds.setAttr(f"{cap}.translateZ", cap_z)
            cmds.setAttr(f"{cap}.rotateX", 90)
            assign_material(cap, shaders["plastic_ivory"])
            cmds.parent(cap, lamp_grp)

    diffuser = cmds.polyCube(name=f"{name_prefix}_Diffuser", width=30, depth=118, height=0.6)[0]
    cmds.setAttr(f"{diffuser}.translateY", 294.5)
    assign_material(diffuser, shaders["metal_white"])
    cmds.parent(diffuser, lamp_grp)

    try:
        light_xf = cmds.createNode("transform", name=f"LGT_{name_prefix}_AreaLight")
        light_shape = cmds.createNode("aiAreaLight", name=f"LGT_{name_prefix}_AreaLightShape", parent=light_xf)
        cmds.setAttr(f"{light_xf}.translateY", 293.5)
        cmds.setAttr(f"{light_xf}.rotateX", 90)
        cmds.setAttr(f"{light_xf}.scaleX", 30)
        cmds.setAttr(f"{light_xf}.scaleY", 118)
        
        cmds.setAttr(f"{light_shape}.aiExposure", 9.6)
        cmds.setAttr(f"{light_shape}.aiUseColorTemperature", True)
        cmds.setAttr(f"{light_shape}.aiColorTemperature", 4200)
        cmds.setAttr(f"{light_shape}.aiSamples", 2)
        cmds.parent(light_xf, lamp_grp)
    except Exception as e:
        print(f"[WARN] Arnold Area Light skipped: {e}")

    cmds.xform(lamp_grp, translation=(x, 0, z), worldSpace=True)
    if parent_grp:
        cmds.parent(lamp_grp, parent_grp)
    return lamp_grp


def build_exit_door_set(shaders):
    door_grp = cmds.group(empty=True, name="GRP_Exit_Door_Set")

    jamb_l = cmds.polyCube(name="ExitDoor_Jamb_L", width=8, depth=14, height=216)[0]
    cmds.setAttr(f"{jamb_l}.translateX", -49)
    cmds.setAttr(f"{jamb_l}.translateY", 108)
    assign_material(jamb_l, shaders["wood_walnut"])
    cmds.parent(jamb_l, door_grp)

    jamb_r = cmds.polyCube(name="ExitDoor_Jamb_R", width=8, depth=14, height=216)[0]
    cmds.setAttr(f"{jamb_r}.translateX", 49)
    cmds.setAttr(f"{jamb_r}.translateY", 108)
    assign_material(jamb_r, shaders["wood_walnut"])
    cmds.parent(jamb_r, door_grp)

    jamb_top = cmds.polyCube(name="ExitDoor_Jamb_Top", width=106, depth=14, height=8)[0]
    cmds.setAttr(f"{jamb_top}.translateY", 212)
    assign_material(jamb_top, shaders["wood_walnut"])
    cmds.parent(jamb_top, door_grp)

    door_leaf = cmds.polyCube(name="ExitDoor_Leaf", width=88, depth=4.5, height=206)[0]
    cmds.setAttr(f"{door_leaf}.translateY", 104)
    cmds.polyBevel3(door_leaf, fraction=0.015, offsetAsFraction=True, segments=2)
    assign_material(door_leaf, shaders["wood_walnut"])
    cmds.parent(door_leaf, door_grp)

    kickplate = cmds.polyCube(name="ExitDoor_Kickplate", width=86, depth=4.8, height=22)[0]
    cmds.setAttr(f"{kickplate}.translateY", 12)
    assign_material(kickplate, shaders["chrome"])
    cmds.parent(kickplate, door_grp)

    rosette = cmds.polyCylinder(name="ExitDoor_Rosette", radius=3.2, height=0.8, subdivisionsAxis=12)[0]
    cmds.setAttr(f"{rosette}.translateX", 36)
    cmds.setAttr(f"{rosette}.translateY", 100)
    cmds.setAttr(f"{rosette}.translateZ", 2.6)
    cmds.setAttr(f"{rosette}.rotateX", 90)
    assign_material(rosette, shaders["chrome"])
    cmds.parent(rosette, door_grp)

    lever = cmds.polyCube(name="ExitDoor_Lever_Handle", width=14, depth=2.4, height=2.2)[0]
    cmds.setAttr(f"{lever}.translateX", 30)
    cmds.setAttr(f"{lever}.translateY", 100)
    cmds.setAttr(f"{lever}.translateZ", 5.2)
    cmds.polyBevel3(lever, fraction=0.1, offsetAsFraction=True, segments=2)
    assign_material(lever, shaders["chrome"])
    cmds.parent(lever, door_grp)

    sign_box = cmds.polyCube(name="ExitSign_Housing", width=38, depth=8, height=20)[0]
    cmds.setAttr(f"{sign_box}.translateY", 232)
    assign_material(sign_box, shaders["metal_white"])
    cmds.parent(sign_box, door_grp)

    sign_panel = cmds.polyCube(name="ExitSign_Red_Panel", width=34, depth=0.6, height=16)[0]
    cmds.setAttr(f"{sign_panel}.translateY", 232)
    cmds.setAttr(f"{sign_panel}.translateZ", 4.2)
    assign_material(sign_panel, shaders["exit_red"])
    cmds.parent(sign_panel, door_grp)

    cmds.xform(door_grp, translation=(180, 0, -390), rotation=(0, 0, 0), worldSpace=True)
    return door_grp


def build_wall_props(shaders):
    props_grp = cmds.group(empty=True, name="GRP_Wall_Props")

    vent_outer = cmds.polyCube(name="Vent_Grille_Outer", width=54, depth=2.0, height=36)[0]
    cmds.setAttr(f"{vent_outer}.translateX", -390)
    cmds.setAttr(f"{vent_outer}.translateY", 240)
    cmds.setAttr(f"{vent_outer}.translateZ", -120)
    cmds.setAttr(f"{vent_outer}.rotateY", 90)
    assign_material(vent_outer, shaders["metal_white"])
    cmds.parent(vent_outer, props_grp)

    for v_idx, vy in enumerate(range(226, 256, 4), 1):
        blade = cmds.polyCube(name=f"Vent_Blade_{v_idx}", width=48, depth=1.6, height=1.2)[0]
        cmds.setAttr(f"{blade}.translateX", -389.5)
        cmds.setAttr(f"{blade}.translateY", vy)
        cmds.setAttr(f"{blade}.translateZ", -120)
        cmds.setAttr(f"{blade}.rotateY", 90)
        cmds.setAttr(f"{blade}.rotateX", 30)
        assign_material(blade, shaders["metal_white"])
        cmds.parent(blade, props_grp)

    socket_plate = cmds.polyCube(name="Power_Socket_Plate", width=8.6, depth=1.2, height=12.0)[0]
    cmds.setAttr(f"{socket_plate}.translateX", -390)
    cmds.setAttr(f"{socket_plate}.translateY", 38)
    cmds.setAttr(f"{socket_plate}.translateZ", 80)
    cmds.setAttr(f"{socket_plate}.rotateY", 90)
    cmds.polyBevel3(socket_plate, fraction=0.06, offsetAsFraction=True, segments=2)
    assign_material(socket_plate, shaders["plastic_ivory"])
    cmds.parent(socket_plate, props_grp)

    return props_grp


def build_backrooms_environment(shaders):
    env_grp = cmds.group(empty=True, name="GRP_Architecture")

    floor = cmds.polyPlane(name="ENV_Floor_Carpet", width=840, height=840, subdivisionsX=8, subdivisionsY=8)[0]
    assign_material(floor, shaders["carpet"])
    cmds.parent(floor, env_grp)

    ceiling = cmds.polyPlane(name="ENV_Ceiling_Tiles", width=840, height=840, subdivisionsX=14, subdivisionsY=14)[0]
    cmds.setAttr(f"{ceiling}.translateY", 300)
    cmds.setAttr(f"{ceiling}.rotateX", 180)
    assign_material(ceiling, shaders["ceiling"])
    cmds.parent(ceiling, env_grp)

    wall_specs = [
        ("ENV_Wall_Back", 840, 300, 18, 0, 150, -400, 0),
        ("ENV_Wall_Left", 18, 300, 840, -400, 150, 0, 0),
        ("ENV_Wall_Right", 18, 300, 840, 400, 150, 0, 0),
    ]

    for w_name, w_w, w_h, w_d, tx, ty, tz, ry in wall_specs:
        wall = cmds.polyCube(name=w_name, width=w_w, height=w_h, depth=w_d)[0]
        cmds.setAttr(f"{wall}.translateX", tx)
        cmds.setAttr(f"{wall}.translateY", ty)
        cmds.setAttr(f"{wall}.translateZ", tz)
        if ry: cmds.setAttr(f"{wall}.rotateY", ry)
        assign_material(wall, shaders["wallpaper"])
        cmds.parent(wall, env_grp)

        bb_w = w_w if w_w > 50 else w_d
        bb_d = 4.0
        bb = cmds.polyCube(name=f"{w_name}_Baseboard", width=bb_w, height=12.0, depth=bb_d)[0]
        if w_w < 50:
            cmds.setAttr(f"{bb}.rotateY", 90)
            cmds.setAttr(f"{bb}.translateX", tx + (7.0 if tx < 0 else -7.0))
            cmds.setAttr(f"{bb}.translateY", 6.0)
            cmds.setAttr(f"{bb}.translateZ", tz)
        else:
            cmds.setAttr(f"{bb}.translateX", tx)
            cmds.setAttr(f"{bb}.translateY", 6.0)
            cmds.setAttr(f"{bb}.translateZ", tz + 7.0)
        assign_material(bb, shaders["wood_walnut"])
        cmds.parent(bb, env_grp)

    pillar = cmds.polyCube(name="ENV_Center_Pillar", width=80, height=300, depth=80)[0]
    cmds.setAttr(f"{pillar}.translateX", 140)
    cmds.setAttr(f"{pillar}.translateY", 150)
    cmds.setAttr(f"{pillar}.translateZ", 80)
    assign_material(pillar, shaders["wallpaper"])
    cmds.parent(pillar, env_grp)

    pillar_base = cmds.polyCube(name="ENV_Center_Pillar_Baseboard", width=86, height=12, depth=86)[0]
    cmds.setAttr(f"{pillar_base}.translateX", 140)
    cmds.setAttr(f"{pillar_base}.translateY", 6)
    cmds.setAttr(f"{pillar_base}.translateZ", 80)
    assign_material(pillar_base, shaders["wood_walnut"])
    cmds.parent(pillar_base, env_grp)

    return env_grp


def setup_cinematic_cameras(parent_grp=None):
    cam_grp = cmds.group(empty=True, name="GRP_Cameras")

    cam_hero_nodes = cmds.camera(
        focalLength=28.0,
        nearClipPlane=1.0,
        farClipPlane=50000.0,
        displayResolution=True,
        overscan=1.1
    )
    cam_hero = cmds.rename(cam_hero_nodes[0], "CAM_Backrooms_Hero_Wide")
    cmds.setAttr(f"{cam_hero}.translateX", 40)
    cmds.setAttr(f"{cam_hero}.translateY", 145)
    cmds.setAttr(f"{cam_hero}.translateZ", 280)
    cmds.setAttr(f"{cam_hero}.rotateX", -5)
    cmds.setAttr(f"{cam_hero}.rotateY", -8)
    cmds.parent(cam_hero, cam_grp)

    cam_prop_nodes = cmds.camera(
        focalLength=50.0,
        nearClipPlane=1.0,
        farClipPlane=50000.0,
        displayResolution=True
    )
    cam_prop = cmds.rename(cam_prop_nodes[0], "CAM_Props_Showcase_50mm")
    cmds.setAttr(f"{cam_prop}.translateX", -80)
    cmds.setAttr(f"{cam_prop}.translateY", 110)
    cmds.setAttr(f"{cam_prop}.translateZ", 180)
    cmds.setAttr(f"{cam_prop}.rotateX", -12)
    cmds.setAttr(f"{cam_prop}.rotateY", -25)
    cmds.parent(cam_prop, cam_grp)

    if parent_grp:
        cmds.parent(cam_grp, parent_grp)
    return cam_grp


def build_entire_backrooms_scene(output_path=None):
    root_name = "Backrooms_Level0_Master_GRP"
    if cmds.objExists(root_name):
        cmds.delete(root_name)

    master_root = cmds.group(empty=True, name=root_name)
    print("[1/6] Building Arnold Shader Library...")
    shaders = setup_backrooms_shaders()

    print("[2/6] Building Modular Architecture Shell...")
    env_grp = build_backrooms_environment(shaders)
    cmds.parent(env_grp, master_root)

    print("[3/6] Generating Furniture & Props...")
    props_root = cmds.group(empty=True, name="GRP_Props_Backrooms")
    cmds.parent(props_root, master_root)

    armchair = build_retro_armchair(shaders)
    cmds.parent(armchair, props_root)

    desk = build_retro_office_desk(shaders)
    cmds.parent(desk, props_root)

    door = build_exit_door_set(shaders)
    cmds.parent(door, props_root)

    wall_props = build_wall_props(shaders)
    cmds.parent(wall_props, props_root)

    print("[4/6] Generating Fluorescent Light Matrix...")
    lights_root = cmds.group(empty=True, name="GRP_Fluorescent_Lights")
    cmds.parent(lights_root, master_root)

    light_grid_positions = [
        ("Lamp_FL", -180, -180),
        ("Lamp_FR", 180, -180),
        ("Lamp_BL", -180, 180),
        ("Lamp_BR", 180, 180)
    ]
    for lamp_name, lx, lz in light_grid_positions:
        build_fluorescent_fixture(lamp_name, lx, lz, shaders, parent_grp=lights_root)

    print("[5/6] Setting Up Cinematic Cameras...")
    setup_cinematic_cameras(parent_grp=master_root)

    print("[6/6] Finalizing Maya Scene...")
    cmds.select(clear=True)

    if output_path:
        cmds.file(rename=output_path)
        file_type = "mayaBinary" if output_path.endswith(".mb") else "mayaAscii"
        saved_file = cmds.file(save=True, type=file_type, defaultExtensions=True)
        print(f"[SUCCESS] Scene successfully saved to: {saved_file}")

    print("\n[COMPLETE] Backrooms Level 0 Props & Environment generated successfully!")
    return master_root


if __name__ == "__main__":
    out_mb = "D:/projects/ProjectAnimation/Backrooms_Furniture_Scene.mb"
    build_entire_backrooms_scene(output_path=out_mb)
    try:
        import maya.standalone
        maya.standalone.uninitialize()
    except:
        pass