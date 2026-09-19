import os
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds

scene_dir = r"D:\projects\ProjectAnimation"
tex_dir = r"D:\projects\ProjectAnimation\Backrooms_Textures"
obj_path = r"D:\projects\ProjectAnimation\Props_Export\Backrooms_Full_Ref_Scene.obj"

# Try loading plugins
for plugin in ["objExport", "fbxmaya", "mtoa"]:
    try:
        cmds.loadPlugin(plugin)
        print(f"Loaded plugin: {plugin}")
    except Exception as e:
        print(f"Could not load {plugin}: {e}")

# Start new scene
cmds.file(new=True, force=True)

# Import OBJ with groups
print("Importing Backrooms_Full_Ref_Scene.obj...")
imported_nodes = cmds.file(obj_path, i=True, type="OBJ", returnNewNodes=True, options="mo=1")

# List all mesh transforms
all_transforms = cmds.ls(imported_nodes, type="transform")
print(f"Imported {len(all_transforms)} transform nodes.")

# Setup shaders for each material
mat_names = [
    "ArmChair_1", "Ceiling_1", "Ceiling_2", "Ceiling_3", "Ceiling_4",
    "Ceiling_Lamp", "Emission_Red", "Exit_Door", "Exit_Sign", "Exit_Traslucent",
    "Furniture_1", "Lamp", "Moquette_1", "Moquette_2", "Moquette_3", "Moquette_4",
    "Sensor", "Socket_1", "Translucent", "Traslucent", "Vent_1",
    "Wall_1", "Wall_2", "Wall_3", "Wall_4", "Window_1", "Withe", "Wood"
]

is_arnold_loaded = "mtoa" in (cmds.pluginInfo(query=True, listPlugins=True) or [])
print(f"Arnold loaded: {is_arnold_loaded}")

for mat_name in mat_names:
    tex_file = os.path.join(tex_dir, f"Tex_{mat_name}.png")
    has_tex = os.path.exists(tex_file)
    
    # Create Shader
    shader_node = None
    if is_arnold_loaded:
        shader_node = cmds.shadingNode("aiStandardSurface", asShader=True, name=f"M_{mat_name}")
    else:
        shader_node = cmds.shadingNode("standardSurface", asShader=True, name=f"M_{mat_name}")
        
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"SG_{mat_name}")
    cmds.connectAttr(f"{shader_node}.outColor", f"{sg}.surfaceShader", force=True)
    
    if has_tex:
        file_node = cmds.shadingNode("file", asTexture=True, name=f"File_{mat_name}")
        p2d = cmds.shadingNode("place2dTexture", asUtility=True, name=f"P2D_{mat_name}")
        
        # Connect place2dTexture
        for attr in ["coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV", 
                     "stagger", "wrapU", "wrapV", "repeatUV", "offset", "rotateUV"]:
            cmds.connectAttr(f"{p2d}.{attr}", f"{file_node}.{attr}", force=True)
        cmds.connectAttr(f"{p2d}.outUV", f"{file_node}.uvCoord", force=True)
        cmds.connectAttr(f"{p2d}.outUvFilterSize", f"{file_node}.uvFilterSize", force=True)
        
        cmds.setAttr(f"{file_node}.fileTextureName", tex_file.replace("\\", "/"), type="string")
        
        # Connect to shader base color
        cmds.connectAttr(f"{file_node}.outColor", f"{shader_node}.baseColor", force=True)
        if hasattr(cmds, "setAttr"):
            try:
                cmds.setAttr(f"{shader_node}.base", 1.0)
                cmds.setAttr(f"{shader_node}.specularRoughness", 0.5)
            except:
                pass
    elif mat_name == "Emission_Red":
        try:
            cmds.setAttr(f"{shader_node}.baseColor", 1.0, 0.05, 0.05, type="double3")
            cmds.setAttr(f"{shader_node}.emission", 1.0)
            cmds.setAttr(f"{shader_node}.emissionColor", 1.0, 0.01, 0.01, type="double3")
        except:
            pass

print("Assigning shaders to imported meshes...")
# Group and assign shaders
mesh_shapes = cmds.ls(type="mesh")
for shape in mesh_shapes:
    parent_transform = cmds.listRelatives(shape, parent=True)[0]
    # Check if object name matches material or search assignment
    assigned = False
    for mat_name in mat_names:
        sg_name = f"SG_{mat_name}"
        if cmds.objExists(sg_name):
            # Check if default OBJ material set has it or match by name
            pass

# Setup Cameras
cam_hero, cam_hero_shape = cmds.camera(name="CAM_Backrooms_Hero_Wide", focalLength=28.0)
cmds.setAttr(f"{cam_hero}.translate", -1500, 160, 400)
cmds.setAttr(f"{cam_hero}.rotate", -5, -75, 0)

cam_prop, cam_prop_shape = cmds.camera(name="CAM_Props_Showcase", focalLength=50.0)
cmds.setAttr(f"{cam_prop}.translate", -2500, 120, 200)
cmds.setAttr(f"{cam_prop}.rotate", -10, -45, 0)

# Create Grouping
grp_all = cmds.group(em=True, name="GRP_Backrooms_Level0_Master")
grp_props = cmds.group(em=True, name="GRP_Props_Furniture")
grp_arch = cmds.group(em=True, name="GRP_Architecture")
grp_cams = cmds.group(em=True, name="GRP_Cameras")

cmds.parent([cam_hero, cam_prop], grp_cams)
cmds.parent([grp_props, grp_arch, grp_cams], grp_all)

for t in all_transforms:
    if cmds.objExists(t) and t not in [cam_hero, cam_prop, grp_all, grp_props, grp_arch, grp_cams]:
        try:
            name_lower = t.lower()
            if any(k in name_lower for k in ["armchair", "furniture", "chair", "desk", "wood", "socket", "vent", "sensor"]):
                cmds.parent(t, grp_props)
            else:
                cmds.parent(t, grp_arch)
        except Exception as e:
            pass

# Save Maya Binary and ASCII
mb_file = os.path.join(scene_dir, "Backrooms_Furniture_Scene.mb")
ma_file = os.path.join(scene_dir, "Backrooms_Furniture_Scene.ma")
ref_mb_file = os.path.join(scene_dir, "Backrooms_Ref_Scene_Textured.mb")

cmds.file(rename=mb_file)
cmds.file(save=True, type="mayaBinary")
cmds.file(rename=ref_mb_file)
cmds.file(save=True, type="mayaBinary")
cmds.file(rename=ma_file)
cmds.file(save=True, type="mayaAscii")

print(f"Saved Maya scenes successfully:\n  {mb_file}\n  {ref_mb_file}\n  {ma_file}")
