import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.mel as mel
cmds.loadPlugin("fbxmaya", quiet=True)
FBX = r"D:\projects\ProjectAnimation\raw_assets\mixamo\charlie\Terrified_Run.fbx"
cmds.file(r"D:\projects\ProjectAnimation\scenes\Characters\Charlie_Mixamo.mb", open=True, force=True)
for mode in ("add", "exmerge", "merge"):
    cmds.file(r"D:\projects\ProjectAnimation\scenes\Characters\Charlie_Mixamo.mb", open=True, force=True)
    bj, bc = set(cmds.ls(type="joint")), set(cmds.ls(type="animCurve"))
    mel.eval('FBXImportMode -v "%s"' % mode)
    mel.eval('FBXImportFillTimeline -v false')
    try:
        cmds.file(FBX, i=True, type="FBX", ignoreVersion=True)
    except Exception as e:
        print("MODE", mode, "ERR", e)
        continue
    nj = [j for j in cmds.ls(type="joint") if j not in bj]
    nc = [c for c in cmds.ls(type="animCurve") if c not in bc]
    hips = cmds.ls("*Hips*", type="joint")
    print("MODE", mode, "joints", len(bj), "->", len(cmds.ls(type="joint")), "new", len(nj), nj[:3], "newCurves", len(nc), "hips", hips)
    print("   hips keyed:", bool(cmds.listConnections("mixamorig:Hips.rotateX", s=True, d=False)), "FBXImportMode:", mel.eval('FBXImportMode -q'))
maya.standalone.uninitialize()
