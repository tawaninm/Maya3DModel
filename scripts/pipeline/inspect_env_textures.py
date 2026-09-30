import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
import os

scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Furniture_Scene.mb"
cmds.file(scene, open=True, force=True)

file_nodes = cmds.ls(type="file")
print(f"Total file nodes in scene: {len(file_nodes)}")

for fn in file_nodes:
    tex_path = cmds.getAttr(f"{fn}.fileTextureName") or ""
    cs = cmds.getAttr(f"{fn}.colorSpace") if cmds.attributeQuery("colorSpace", node=fn, exists=True) else "N/A"
    
    # check outgoing connections
    connections = cmds.listConnections(fn, source=False, destination=True, plugs=True) or []
    print(f"\nNode: {fn}")
    print(f"  Texture: {tex_path}")
    print(f"  colorSpace: {cs}")
    print(f"  Outputs ({len(connections)}):")
    for conn in connections:
        print(f"    -> {conn}")
