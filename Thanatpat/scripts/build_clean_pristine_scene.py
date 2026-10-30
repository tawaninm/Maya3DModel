import os, shutil
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds

scene_dir = r"D:\projects\ProjectAnimation"
tex_dir = r"D:\projects\ProjectAnimation\Backrooms_Textures"
obj_path = r"D:\projects\ProjectAnimation\Props_Export\Backrooms_Full_Ref_Scene.obj"

for plugin in ["objExport", "fbxmaya", "mtoa"]:
    try:
        cmds.loadPlugin(plugin)
    except:
        pass

cmds.file(new=True, force=True)
print("Importing Backrooms_Full_Ref_Scene.obj...")
imported_nodes = cmds.file(obj_path, i=True, type="OBJ", returnNewNodes=True, options="mo=1")
all_mesh_transforms = cmds.ls(imported_nodes, type="transform")

sgs = cmds.ls(type="shadingEngine")
print("Imported Shading Engines:", sgs)

tex_files = {f.lower(): os.path.join(tex_dir, f) for f in os.listdir(tex_dir) if f.endswith(".png")}

for sg in sgs:
    if sg in ["initialShadingGroup", "initialParticleSE"]:
        continue
    
    clean_name = sg
    matched_tex = None
    direct_key = f"tex_{clean_name.lower()}.png"
    if direct_key in tex_files:
        matched_tex = tex_files[direct_key]
    else:
        base = clean_name.split("_")[0].lower()
        for k, v in tex_files.items():
            if base in k:
                matched_tex = v
                break
    
    shader_name = f"M_{clean_name}"
    if cmds.objExists(shader_name):
        cmds.delete(shader_name)
    
    try:
        sh = cmds.shadingNode("aiStandardSurface", asShader=True, name=shader_name)
    except:
        sh = cmds.shadingNode("standardSurface", asShader=True, name=shader_name)
        
    cmds.connectAttr(f"{sh}.outColor", f"{sg}.surfaceShader", force=True)
    
    if matched_tex and os.path.exists(matched_tex):
        file_node = cmds.shadingNode("file", asTexture=True, name=f"File_{clean_name}")
        p2d = cmds.shadingNode("place2dTexture", asUtility=True, name=f"P2D_{clean_name}")
        for attr in ["coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV", 
                     "stagger", "wrapU", "wrapV", "repeatUV", "offset", "rotateUV"]:
            cmds.connectAttr(f"{p2d}.{attr}", f"{file_node}.{attr}", force=True)
        cmds.connectAttr(f"{p2d}.outUV", f"{file_node}.uvCoord", force=True)
        cmds.connectAttr(f"{p2d}.outUvFilterSize", f"{file_node}.uvFilterSize", force=True)
        cmds.setAttr(f"{file_node}.fileTextureName", matched_tex.replace("\\", "/"), type="string")
        
        cmds.connectAttr(f"{file_node}.outColor", f"{sh}.baseColor", force=True)
        try:
            cmds.setAttr(f"{sh}.base", 1.0)
            cmds.setAttr(f"{sh}.specularRoughness", 0.6)
        except:
            pass
        print(f"Connected {matched_tex} to {sg} -> {sh}")
    elif "emission" in clean_name.lower() or "red" in clean_name.lower():
        try:
            cmds.setAttr(f"{sh}.baseColor", 1.0, 0.05, 0.05, type="double3")
            cmds.setAttr(f"{sh}.emission", 2.5)
            cmds.setAttr(f"{sh}.emissionColor", 1.0, 0.05, 0.05, type="double3")
        except:
            pass

grp_master = cmds.group(em=True, name="GRP_Backrooms_Level0_Master")
grp_props = cmds.group(em=True, name="GRP_Props_Furniture")
grp_arch = cmds.group(em=True, name="GRP_Architecture")
grp_lights = cmds.group(em=True, name="GRP_Lighting_4200K")
grp_cams = cmds.group(em=True, name="GRP_Cameras")

cmds.parent([grp_props, grp_arch, grp_lights, grp_cams], grp_master)

name_mapping = {
    "Object_26": "Prop_Retro_Armchair_90s",
    "Object_8": "Prop_OfficeDesk_and_Drawers",
    "Object_25": "Prop_Wood_Cabinets",
    "Object_2": "Prop_Ceiling_Fluorescent_Housing",
    "Object_9": "Prop_Fluorescent_Tubes",
    "Object_27": "Prop_Exit_Door_Frame",
    "Object_28": "Prop_Exit_Door_Leaf",
    "Object_6": "Prop_Exit_Sign_Housing",
    "Object_5": "Prop_Exit_Sign_Emission_Red",
    "Object_7": "Prop_Exit_Sign_Glass",
    "Object_10": "Prop_Wall_Power_Sockets",
    "Object_11": "Prop_Security_Motion_Sensor",
    "Object_20": "Prop_Wall_Air_Vent",
    "Object_13": "Prop_Window_Glass_Frame",
    "Object_15": "Prop_Ceiling_Diffuser_Panels",
    "Object_24": "Prop_Exit_Translucent_Cover",
    "Object_22": "Arch_Wall_White_Accents",
    "Object_12": "Arch_Wall_Sector_1",
    "Object_14": "Arch_Wall_Sector_2",
    "Object_21": "Arch_Wall_Sector_3",
    "Object_23": "Arch_Wall_Sector_4",
    "Object_16": "Arch_Floor_Moquette_1",
    "Object_17": "Arch_Floor_Moquette_2",
    "Object_18": "Arch_Floor_Moquette_3",
    "Object_19": "Arch_Floor_Moquette_4",
    "Object_0": "Arch_Ceiling_Tiles_1",
    "Object_1": "Arch_Ceiling_Tiles_2",
    "Object_3": "Arch_Ceiling_Tiles_3",
    "Object_4": "Arch_Ceiling_Tiles_4",
}

for old_t in all_mesh_transforms:
    if not cmds.objExists(old_t):
        continue
    new_name = name_mapping.get(old_t, old_t)
    renamed_t = cmds.rename(old_t, new_name)
    name_l = renamed_t.lower()
    if name_l.startswith("prop_"):
        cmds.parent(renamed_t, grp_props)
    else:
        cmds.parent(renamed_t, grp_arch)

light_positions = [
    (-2800, 290, 400),
    (-2200, 290, 400),
    (-1600, 290, 400),
    (-1000, 290, 400),
    (-2800, 290, -400),
    (-2200, 290, -400),
    (-1600, 290, -400),
]
for i, pos in enumerate(light_positions):
    light_transform = cmds.createNode("aiAreaLight", name=f"aiAreaLight_Fluorescent_{i+1}")
    p_trans = cmds.listRelatives(light_transform, parent=True)
    light_trans = p_trans[0] if p_trans else light_transform
    cmds.setAttr(f"{light_trans}.translate", pos[0], pos[1], pos[2])
    cmds.setAttr(f"{light_trans}.rotate", -90, 0, 0)
    cmds.setAttr(f"{light_trans}.scale", 120, 30, 1)
    try:
        cmds.setAttr(f"{light_transform}.intensity", 15.0)
        cmds.setAttr(f"{light_transform}.exposure", 2.0)
        cmds.setAttr(f"{light_transform}.aiUseColorTemperature", True)
        cmds.setAttr(f"{light_transform}.aiColorTemperature", 4200.0)
    except:
        pass
    cmds.parent(light_trans, grp_lights)

cam_hero, _ = cmds.camera(name="CAM_Backrooms_Hero_Wide", focalLength=28.0)
cmds.setAttr(f"{cam_hero}.translate", -1500, 160, 400)
cmds.setAttr(f"{cam_hero}.rotate", -5, -75, 0)

cam_prop, _ = cmds.camera(name="CAM_Props_Showcase_Desk", focalLength=50.0)
cmds.setAttr(f"{cam_prop}.translate", -2500, 120, 200)
cmds.setAttr(f"{cam_prop}.rotate", -10, -45, 0)

cmds.parent([cam_hero, cam_prop], grp_cams)

mb_file = os.path.join(scene_dir, "Backrooms_Furniture_Scene.mb")
ma_file = os.path.join(scene_dir, "Backrooms_Furniture_Scene.ma")

cmds.file(rename=mb_file)
cmds.file(save=True, type="mayaBinary")

cmds.file(rename=ma_file)
cmds.file(save=True, type="mayaAscii")

# Clean duplicate files
duplicate_files = [
    os.path.join(scene_dir, "Backrooms_Ref_Scene_Textured.mb"),
    os.path.join(scene_dir, "build_backrooms_ref_cleanwalls.py"),
    os.path.join(scene_dir, "build_clean_topology_backrooms.py"),
    os.path.join(scene_dir, "export_clean_objs.py"),
    os.path.join(scene_dir, "Props_Export", "Backrooms_Full_Ref_CleanWalls_Scene.obj"),
    os.path.join(scene_dir, "Props_Export", "Backrooms_Full_Ref_CleanWalls_Scene.mtl"),
    os.path.join(scene_dir, "Props_Export", "Backrooms_Full_Ref_Textured_Scene.obj"),
    os.path.join(scene_dir, "Props_Export", "Backrooms_Full_Ref_Textured_Scene.mtl"),
    os.path.join(scene_dir, "Props_Export", "Backrooms_Level0_Full_Scene.obj"),
    os.path.join(scene_dir, "Props_Export", "Backrooms_Level0_Full_Scene.mtl"),
]
for df in duplicate_files:
    if os.path.exists(df):
        try:
            os.remove(df)
            print("Removed:", df)
        except Exception as e:
            print("Err removing", df, e)

for cd in [os.path.join(scene_dir, "Props_Export", "Clean_Modular"), os.path.join(scene_dir, "Props_Export", "Clean_Planes")]:
    if os.path.exists(cd):
        try:
            shutil.rmtree(cd)
            print("Removed dir:", cd)
        except Exception as e:
            print("Err removing dir", cd, e)

print("ALL_DONE_CLEAN_SUCCESS")
