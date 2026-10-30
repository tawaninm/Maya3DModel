import sys
import os
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except:
    pass

import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds

# Load objExport plugin
if not cmds.pluginInfo("objExport", query=True, loaded=True):
    try:
        cmds.loadPlugin("objExport")
    except Exception as e:
        print("[WARN] objExport plugin failed:", e)

if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
    try:
        cmds.loadPlugin("fbxmaya")
    except Exception as e:
        print("[WARN] fbxmaya plugin failed:", e)

# Open scene
mb_path = "D:/projects/ProjectAnimation/Backrooms_Furniture_Scene.mb"
cmds.file(mb_path, open=True, force=True)

# Also save as .ma
ma_path = "D:/projects/ProjectAnimation/Backrooms_Furniture_Scene.ma"
cmds.file(rename=ma_path)
cmds.file(save=True, type="mayaAscii", defaultExtensions=True)
print("[SUCCESS] Exported .ma scene:", ma_path)

# Export individual props to OBJ
props_dir = "D:/projects/ProjectAnimation/Props_Export"
if not os.path.exists(props_dir):
    os.makedirs(props_dir)

targets = [
    ("GRP_Retro_Armchair", "Prop_Retro_Armchair_90s"),
    ("GRP_Retro_Office_Desk", "Prop_Retro_Office_Desk"),
    ("GRP_Exit_Door_Set", "Prop_Exit_Door_Set"),
    ("GRP_Wall_Props", "Prop_Wall_Vent_and_Socket"),
    ("GRP_Fluorescent_Lights", "Prop_Fluorescent_Ceiling_Lamps"),
    ("GRP_Architecture", "Prop_Modular_Architecture_Room"),
    ("Backrooms_Level0_Master_GRP", "Backrooms_Level0_Full_Scene")
]

for grp_node, out_name in targets:
    if cmds.objExists(grp_node):
        cmds.select(grp_node, hierarchy=True)
        obj_out = f"{props_dir}/{out_name}.obj"
        cmds.file(obj_out, force=True, options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", type="OBJexport", exportSelected=True)
        print(f"[SUCCESS] Exported OBJ: {obj_out}")

print("[ALL EXPORTS FINISHED]")
maya.standalone.uninitialize()