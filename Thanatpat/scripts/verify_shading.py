import os
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds

cmds.file(r"D:\projects\ProjectAnimation\Backrooms_Furniture_Scene.mb", open=True, force=True)

# Check Shading Engines and connections
for shape in cmds.ls(type="mesh"):
    sgs = cmds.listConnections(shape, type="shadingEngine") or []
    print(f"Mesh: {shape} -> SGs: {sgs}")
