"""Diagnostic script to inspect Shot05 end state and Getting_Up.fbx animation."""
import os
import sys

import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.mel as mel

# 1. Inspect Getting_Up.fbx
cmds.file(new=True, force=True)
cmds.loadPlugin("fbxmaya", quiet=True)
mel.eval('FBXImportMode -v "add"')
mel.eval('FBXImportFillTimeline -v false')
fbx_path = r"D:\projects\ProjectAnimation\raw_assets\mixamo\charlie\Getting_Up.fbx"
cmds.file(fbx_path, i=True, type="FBX", ignoreVersion=True)

curves = cmds.ls(type="animCurve")
kt = sorted(set(t for c in curves for t in (cmds.keyframe(c, q=True, timeChange=True) or [])))
joints = cmds.ls(type="joint")
hips = [j for j in joints if j.endswith("Hips")][0]
head = [j for j in joints if j.endswith("Head")][0]

print("GETTING_UP_FBX:")
print("  Total joints:", len(joints))
print("  Curves:", len(curves))
print("  Key range:", kt[0] if kt else None, "to", kt[-1] if kt else None, "total:", len(kt))
cmds.currentTime(kt[0])
print("  Hips at start (f%s):" % kt[0], cmds.xform(hips, q=True, ws=True, t=True))
cmds.currentTime(kt[-1])
print("  Hips at end (f%s):" % kt[-1], cmds.xform(hips, q=True, ws=True, t=True))

# 2. Inspect Shot05 end state at frame 48
cmds.file(new=True, force=True)
shot05 = r"D:\projects\ProjectAnimation\scenes\Shots\Shot05.mb"
cmds.file(shot05, open=True, force=True)
cmds.currentTime(48)
print("SHOT05 at frame 48:")
print("  Charlie Placement:", cmds.getAttr("CHARLIE:GRP_Charlie_Placement.translate"))
print("  Charlie Hips ws pos:", cmds.xform("CHARLIE:mixamorig:Hips", q=True, ws=True, t=True))
print("  Charlie Head ws pos:", cmds.xform("CHARLIE:mixamorig:Head", q=True, ws=True, t=True))

# 3. Inspect Shot06 current state
cmds.file(new=True, force=True)
shot06 = r"D:\projects\ProjectAnimation\scenes\Shots\Shot06.mb"
cmds.file(shot06, open=True, force=True)
print("SHOT06 current state:")
print("  Frame range:", cmds.playbackOptions(q=True, minTime=True), "to", cmds.playbackOptions(q=True, maxTime=True))
print("  Cameras:", [c for c in cmds.ls(type="camera") if "Shot" in c])
print("  Objects:", cmds.ls("GRP_CAM_Shot06", "CAM_Shot06"))
print("  Charlie Placement exists:", cmds.objExists("CHARLIE:GRP_Charlie_Placement"))
if cmds.objExists("CHARLIE:GRP_Charlie_Placement"):
    print("  Charlie Placement:", cmds.getAttr("CHARLIE:GRP_Charlie_Placement.translate"))

maya.standalone.uninitialize()
