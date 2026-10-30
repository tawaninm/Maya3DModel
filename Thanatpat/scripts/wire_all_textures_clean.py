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
    
    current_shader = cmds.listConnections(f"{sg}.surfaceShader")
    if not current_shader:
        continue
        
    sh = current_shader[0]
    clean_mat = sg.replace("SG_", "").rstrip("0123456789")
    
    # Match exact or prefix
    matched_tex = None
    direct_tex = os.path.join(tex_dir, f"Tex_{sg.replace('SG_', '')}.png")
    if os.path.exists(direct_tex):
        matched_tex = direct_tex
    else:
        for f in os.listdir(tex_dir):
            if f.startswith("Tex_") and clean_mat.lower() in f.lower():
                matched_tex = os.path.join(tex_dir, f)
                break
                
    print(f"SG: {sg} -> Shader: {sh} -> Tex: {matched_tex}")
    
    if matched_tex:
        # Check if already has file node
        incoming = []
        if cmds.attributeQuery("color", node=sh, exists=True):
            incoming += cmds.listConnections(f"{sh}.color") or []
        if cmds.attributeQuery("baseColor", node=sh, exists=True):
            incoming += cmds.listConnections(f"{sh}.baseColor") or []
            
        file_nodes = [n for n in incoming if cmds.nodeType(n) == "file"]
        
        if not file_nodes:
            fn = cmds.shadingNode("file", asTexture=True, name=f"FileTex_{sg}")
            p2d = cmds.shadingNode("place2dTexture", asUtility=True, name=f"P2D_{sg}")
            for attr in ["coverage", "translateFrame", "rotateFrame", "mirrorU", "mirrorV", 
                         "stagger", "wrapU", "wrapV", "repeatUV", "offset", "rotateUV"]:
                cmds.connectAttr(f"{p2d}.{attr}", f"{fn}.{attr}", force=True)
            cmds.connectAttr(f"{p2d}.outUV", f"{fn}.uvCoord", force=True)
            cmds.connectAttr(f"{p2d}.outUvFilterSize", f"{fn}.uvFilterSize", force=True)
            cmds.setAttr(f"{fn}.fileTextureName", matched_tex.replace("\\", "/"), type="string")
            
            if cmds.attributeQuery("color", node=sh, exists=True):
                cmds.connectAttr(f"{fn}.outColor", f"{sh}.color", force=True)
            if cmds.attributeQuery("baseColor", node=sh, exists=True):
                cmds.connectAttr(f"{fn}.outColor", f"{sh}.baseColor", force=True)
            print(f"  --> Successfully connected {fn} to {sh}")

# Save updated scene
cmds.file(save=True, type="mayaBinary")
cmds.file(rename=r"D:\projects\ProjectAnimation\Backrooms_Ref_Scene_Textured.mb")
cmds.file(save=True, type="mayaBinary")
cmds.file(rename=r"D:\projects\ProjectAnimation\Backrooms_Furniture_Scene.ma")
cmds.file(save=True, type="mayaAscii")
print("ALL TEXTURES WIRED AND SCENE SAVED SUCCESSFULLY!")
