import json, struct, os, shutil
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds

scene_dir = r"D:\projects\ProjectAnimation"
tex_dir = r"D:\projects\ProjectAnimation\Backrooms_Textures"
obj_path = r"D:\projects\ProjectAnimation\Props_Export\Backrooms_Full_Ref_Scene.obj"
glb_path = r"D:\projects\ProjectAnimation\backrooms_vr.glb"

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
            cmds.setAttr(f"{sh}.specularRoughness", 0.65)
        except:
            pass
            
        # Add emission if it's lamp or emission texture
        if "lamp" in clean_name.lower() or "ceiling_lamp" in clean_name.lower():
            try:
                cmds.setAttr(f"{sh}.emission", 4.0)
                cmds.setAttr(f"{sh}.emissionColor", 1.0, 0.96, 0.82, type="double3")
            except:
                pass
        print(f"Connected {matched_tex} to {sg} -> {sh}")
    elif "emission" in clean_name.lower() or "red" in clean_name.lower():
        try:
            cmds.setAttr(f"{sh}.baseColor", 1.0, 0.05, 0.05, type="double3")
            cmds.setAttr(f"{sh}.emission", 3.5)
            cmds.setAttr(f"{sh}.emissionColor", 1.0, 0.05, 0.05, type="double3")
        except:
            pass

grp_master = cmds.group(em=True, name="GRP_Backrooms_Level0_Master")
grp_props = cmds.group(em=True, name="GRP_Props_Furniture")
grp_arch = cmds.group(em=True, name="GRP_Architecture")
grp_lights = cmds.group(em=True, name="GRP_Lighting_System")
grp_fluor_lights = cmds.group(em=True, name="GRP_Fluorescent_Ceiling_Lamps_54")
grp_red_lights = cmds.group(em=True, name="GRP_Emergency_Red_Lights_14")
grp_cams = cmds.group(em=True, name="GRP_Cameras")

cmds.parent([grp_fluor_lights, grp_red_lights], grp_lights)
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

# Parse GLB for exact 54 lamp cluster locations and 14 red emergency light locations
with open(glb_path, "rb") as f:
    f.seek(12)
    c0_len, _ = struct.unpack("<I4s", f.read(8))
    gltf = json.loads(f.read(c0_len).decode("utf-8"))
    c1_len, _ = struct.unpack("<I4s", f.read(8))
    bin_data = f.read(c1_len)

accessors = gltf["accessors"]
bufferViews = gltf["bufferViews"]
meshes = gltf["meshes"]

def get_clusters(mesh_idx, threshold=180.0):
    acc = accessors[meshes[mesh_idx]["primitives"][0]["attributes"]["POSITION"]]
    bv = bufferViews[acc["bufferView"]]
    offset = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    count = acc["count"]
    raw_coords = struct.unpack_from(f"<{count*3}f", bin_data, offset)
    M = gltf["nodes"][0]["matrix"]
    points = []
    for i in range(0, len(raw_coords), 3):
        x, y, z = raw_coords[i], raw_coords[i+1], raw_coords[i+2]
        tx = (M[0]*x + M[4]*y + M[8]*z + M[12]) * 100.0
        ty = (M[1]*x + M[5]*y + M[9]*z + M[13]) * 100.0
        tz = (M[2]*x + M[6]*y + M[10]*z + M[14]) * 100.0
        points.append((tx, ty, tz))
    clusters = []
    for p in points:
        matched = False
        for c in clusters:
            dx = c["center"][0] - p[0]
            dz = c["center"][2] - p[2]
            if (dx*dx + dz*dz) < threshold*threshold:
                c["points"].append(p)
                pts = c["points"]
                c["center"] = (sum(pt[0] for pt in pts)/len(pts), sum(pt[1] for pt in pts)/len(pts), sum(pt[2] for pt in pts)/len(pts))
                matched = True
                break
        if not matched:
            clusters.append({"center": p, "points": [p]})
    return clusters

lamp_clusters = get_clusters(2, threshold=180.0) # 54 ceiling lamps
red_clusters = get_clusters(5, threshold=100.0)  # 14 red emission lights

print(f"Creating {len(lamp_clusters)} Arnold Fluorescent Area Lights across the ceiling...")
for i, c in enumerate(lamp_clusters):
    cx, cy, cz = c["center"]
    light_shape = cmds.createNode("aiAreaLight", name=f"aiAreaLight_Fluorescent_Panel_{i+1:02d}Shape")
    p_trans = cmds.listRelatives(light_shape, parent=True)
    light_trans = p_trans[0] if p_trans else f"aiAreaLight_Fluorescent_Panel_{i+1:02d}"
    light_trans = cmds.rename(light_trans, f"aiAreaLight_Fluorescent_Panel_{i+1:02d}")
    
    # Place right below ceiling panel fixture
    cmds.setAttr(f"{light_trans}.translate", cx, cy - 2.0, cz)
    cmds.setAttr(f"{light_trans}.rotate", -90, 0, 0) # Face down towards the floor
    cmds.setAttr(f"{light_trans}.scale", 70, 70, 1)  # 70x70 cm square fixture
    
    try:
        cmds.setAttr(f"{light_shape}.intensity", 50.0)
        cmds.setAttr(f"{light_shape}.exposure", 4.5)
        cmds.setAttr(f"{light_shape}.aiUseColorTemperature", True)
        cmds.setAttr(f"{light_shape}.aiColorTemperature", 4200.0) # 4200K Fluorescent Warm White
        cmds.setAttr(f"{light_shape}.aiSpread", 0.85) # Focused beam down to carpet
        cmds.setAttr(f"{light_shape}.aiSamples", 2)
        cmds.setAttr(f"{light_shape}.aiCastShadows", True)
    except Exception as e:
        print("Arnold attr err:", e)
        
    cmds.parent(light_trans, grp_fluor_lights)

print(f"Creating {len(red_clusters)} Emergency Red Point Lights...")
for i, c in enumerate(red_clusters):
    cx, cy, cz = c["center"]
    red_light = cmds.pointLight(name=f"Red_Emergency_Light_{i+1:02d}")
    p_trans = cmds.listRelatives(red_light, parent=True)[0]
    cmds.setAttr(f"{p_trans}.translate", cx, cy - 5.0, cz)
    cmds.setAttr(f"{red_light}.color", 1.0, 0.05, 0.05, type="double3")
    cmds.setAttr(f"{red_light}.intensity", 20.0)
    try:
        cmds.setAttr(f"{red_light}.aiExposure", 2.0)
        cmds.setAttr(f"{red_light}.aiRadius", 5.0)
    except:
        pass
    cmds.parent(p_trans, grp_red_lights)

# Create subtle Ambient / SkyDome Fill Light for soft dark corners
try:
    skydome = cmds.createNode("aiSkyDomeLight", name="aiSkyDome_Ambient_FillShape")
    skydome_trans = cmds.listRelatives(skydome, parent=True)[0]
    skydome_trans = cmds.rename(skydome_trans, "aiSkyDome_Ambient_Fill")
    cmds.setAttr(f"{skydome}.intensity", 0.08)
    cmds.setAttr(f"{skydome}.color", 0.92, 0.88, 0.75, type="double3") # Warm beige ambient
    cmds.setAttr(f"{skydome}.camera", 0.0) # Don't render in background
    cmds.parent(skydome_trans, grp_lights)
    print("Created aiSkyDomeLight Ambient Fill.")
except Exception as e:
    print("SkyDome error:", e)

# Setup Arnold Atmospheric Volume for foggy fluorescent god rays
try:
    if cmds.objExists("defaultArnoldRenderOptions"):
        vol_name = "aiAtmosphereVolume_BackroomsHaze"
        if not cmds.objExists(vol_name):
            vol = cmds.shadingNode("aiAtmosphereVolume", asShader=True, name=vol_name)
            cmds.setAttr(f"{vol}.density", 0.001)
            cmds.setAttr(f"{vol}.anisotropy", 0.6) # Forward god rays
            cmds.setAttr(f"{vol}.rgb", 0.95, 0.92, 0.80, type="double3")
            cmds.connectAttr(f"{vol}.message", "defaultArnoldRenderOptions.atmosphere", force=True)
            print("Connected Arnold Atmosphere Volume (God Rays / Fluorescent Haze).")
except Exception as e:
    print("Atmosphere error:", e)

# Create Cameras
cam_hero, _ = cmds.camera(name="CAM_Backrooms_Hero_Corridor", focalLength=28.0)
cmds.setAttr(f"{cam_hero}.translate", -1500, 160, 400)
cmds.setAttr(f"{cam_hero}.rotate", -5, -75, 0)

cam_prop, _ = cmds.camera(name="CAM_Props_Showcase_Desk", focalLength=50.0)
cmds.setAttr(f"{cam_prop}.translate", -2500, 120, 200)
cmds.setAttr(f"{cam_prop}.rotate", -10, -45, 0)

cam_exit, _ = cmds.camera(name="CAM_Exit_Doorway_RedGlow", focalLength=35.0)
cmds.setAttr(f"{cam_exit}.translate", -4600, 150, 400)
cmds.setAttr(f"{cam_exit}.rotate", -8, -120, 0)

cmds.parent([cam_hero, cam_prop, cam_exit], grp_cams)

mb_file = os.path.join(scene_dir, "Backrooms_Furniture_Scene.mb")
ma_file = os.path.join(scene_dir, "Backrooms_Furniture_Scene.ma")

cmds.file(rename=mb_file)
cmds.file(save=True, type="mayaBinary")

cmds.file(rename=ma_file)
cmds.file(save=True, type="mayaAscii")

print("LIGHTING_SETUP_COMPLETE_SUCCESS")
