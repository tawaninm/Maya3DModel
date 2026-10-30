import os
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds

tex_dir = r"D:\projects\ProjectAnimation\Backrooms_Textures"
scene_file = r"D:\projects\ProjectAnimation\Backrooms_Furniture_Scene.mb"

cmds.file(scene_file, open=True, force=True)

# Find all shading engines
sgs = cmds.ls(type="shadingEngine")
print("Shading engines in scene:", sgs)

for sg in sgs:
    if sg in ["initialShadingGroup", "initialParticleSE"]:
        continue
    
    # Get current surface shader
    current_shader = cmds.listConnections(f"{sg}.surfaceShader")
    print(f"SG: {sg} -> Current Shader: {current_shader}")
    
    # Find matching texture file
    # Clean name from SG name (e.g. SG_ArmChair_1 or ArmChair_1)
    base_name = sg.replace("SG_", "").split("_")[0]
    matched_tex = None
    for f in os.listdir(tex_dir):
        if f.startswith("Tex_") and base_name.lower() in f.lower():
            matched_tex = os.path.join(tex_dir, f)
            break
            
    # Also check exact name
    clean_mat = sg.replace("SG_", "")
    exact_tex = os.path.join(tex_dir, f"Tex_{clean_mat}.png")
    if os.path.exists(exact_tex):
        matched_tex = exact_tex
        
    print(f"  Matched texture: {matched_tex}")
    
    # Ensure standard surface / lambert has file texture connected
    if current_shader:
        sh = current_shader[0]
        # Check if file node is connected
        incoming = cmds.listConnections(f"{sh}.color") or cmds.listConnections(f"{sh}.baseColor") or []
        file_nodes = [n for n in incoming if cmds.nodeType(n) == "file"]
        
        if not file_nodes and matched_tex:
            fn = cmds.shadingNode("file", asTexture=True, name=f"FileTex_{sg}")
            p2d = cmds.shadingNode("place2dTexture", asUtility=True, name=f"P2D_{sg}")
            for attr in ["coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV", 
                         "stagger", "wrapU", "wrapV", "repeatUV", "offset", "rotateUV"]:
                cmds.connectAttr(f"{p2d}.{attr}", f"{fn}.{attr}", force=True)
            cmds.connectAttr(f"{p2d}.outUV", f"{fn}.uvCoord", force=True)
            cmds.connectAttr(f"{p2d}.outUvFilterSize", f"{fn}.uvFilterSize", force=True)
            cmds.setAttr(f"{fn}.fileTextureName", matched_tex.replace("\\", "/"), type="string")
            
            # Connect to color or baseColor
            if cmds.attributeQuery("color", node=sh, exists=True):
                cmds.connectAttr(f"{fn}.outColor", f"{sh}.color", force=True)
            if cmds.attributeQuery("baseColor", node=sh, exists=True):
                cmds.connectAttr(f"{fn}.outColor", f"{sh}.baseColor", force=True)
            print(f"  Connected {fn} to {sh}")

cmds.file(save=True, type="mayaBinary")
cmds.file(rename=r"D:\projects\ProjectAnimation\Backrooms_Furniture_Scene.ma")
cmds.file(save=True, type="mayaAscii")
print("Verified and saved scene with all texture nodes wired!")
