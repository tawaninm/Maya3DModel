"""Read-only diagnostic for Shot 08 (2026-10-01). Does not save any scene.
Prints: Picking_Up_Object clip length and hand/head trajectories, desk geometry near the camcorder, current Shot08.mb camera state.
Run: D:\\AutoDesk\\Maya2027\\bin\\mayapy.exe scripts\\pipeline\\diag_shot08_inputs.py
"""
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.mel as mel

SHOT = r"D:\projects\ProjectAnimation\scenes\Shots\Shot08.mb"
CLIP = r"D:\projects\ProjectAnimation\raw_assets\mixamo\charlie\Picking_Up_Object.fbx"
CAMCORDER_POS = (-238.0, 73.06, 185.0)   # same as Shot 07

cmds.loadPlugin("fbxmaya", quiet=True)
cmds.file(SHOT, open=True, force=True, loadReferenceDepth="all")
cmds.currentUnit(time="film")

print("D| namespaces:", [n for n in cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True) or []])
print("D| refs:", cmds.file(q=True, reference=True))
print("D| range:", cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True))
for n in ("GRP_CAM_Shot08", "CAM_Shot08"):
    if cmds.objExists(n):
        print("D|", n, "t", [round(v, 2) for v in cmds.getAttr(n + ".translate")[0]], "r", [round(v, 2) for v in cmds.getAttr(n + ".rotate")[0]],
              "anim", cmds.listConnections(n, type="animCurve") or [])
print("D| cameras:", [(cmds.listRelatives(c, parent=True)[0], cmds.getAttr(c + ".renderable")) for c in cmds.ls(type="camera")])
print("D| Charlie placement:", cmds.objExists("CHARLIE:GRP_Charlie_Placement"),
      [round(v, 2) for v in cmds.xform("CHARLIE:GRP_Charlie_Placement", q=True, ws=True, t=True)] if cmds.objExists("CHARLIE:GRP_Charlie_Placement") else None)
print("D| charlie meshes:", sorted({cmds.listRelatives(m, parent=True)[0] for m in cmds.ls("CHARLIE:*", type="mesh", noIntermediate=True)}))
print("D| env LIGHT_MASTER exposure:", cmds.getAttr("ENV:LIGHT_MASTER.exposure") if cmds.objExists("ENV:LIGHT_MASTER.exposure") else None)
print("D| key light exists:", cmds.objExists("Shot07_Desk_KeyLight"))

# desk / table geometry near the camcorder (env meshes whose bbox contains the camcorder xz and top near 73)
cx, cy, cz = CAMCORDER_POS
near = []
for t in cmds.ls("ENV:*", type="transform"):
    if not cmds.listRelatives(t, shapes=True, noIntermediate=True):
        continue
    try:
        bb = cmds.exactWorldBoundingBox(t)
    except Exception:
        continue
    if bb[0] - 60 <= cx <= bb[3] + 60 and bb[2] - 60 <= cz <= bb[5] + 60 and bb[1] < 120:
        near.append((t, [round(v, 1) for v in bb]))
for t, bb in near[:25]:
    print("D| near camcorder:", t, bb)

# clip analysis: import, sample hands / head / hips, then discard (scene is never saved)
before_j = set(cmds.ls(type="joint"))
before_c = set(cmds.ls(type="animCurve"))
mel.eval('FBXImportMode -v "add"')
mel.eval('FBXImportFillTimeline -v false')
cmds.file(CLIP, i=True, type="FBX", ignoreVersion=True)
new_j = [j for j in cmds.ls(type="joint") if j not in before_j]
new_c = [c for c in cmds.ls(type="animCurve") if c not in before_c]
by_leaf = {j.split(":")[-1]: j for j in new_j}
kt = sorted(set(t for c in new_c for t in (cmds.keyframe(c, q=True, timeChange=True) or [])))
print("D| clip key range:", kt[0], kt[-1], "count", len(kt))
first, last = int(kt[0]), int(kt[-1])
probe = ["Hips", "Head", "RightHand", "LeftHand", "RightFoot", "LeftFoot"]
for f in range(first, last + 1, max(1, (last - first) // 20)):
    row = []
    for p in probe:
        v = cmds.xform(by_leaf[p], q=True, ws=True, t=True, **{}) if False else None
    cmds.currentTime(f)
    for p in probe:
        v = cmds.xform(by_leaf[p], q=True, ws=True, t=True)
        row.append("%s(%.1f,%.1f,%.1f)" % (p, v[0], v[1], v[2]))
    print("D| f%03d" % f, " ".join(row))

best = {}
for hand in ("RightHand", "LeftHand"):
    lo = None
    for f in range(first, last + 1):
        cmds.currentTime(f)
        y = cmds.xform(by_leaf[hand], q=True, ws=True, t=True)[1]
        if lo is None or y < lo[1]:
            lo = (f, y)
    best[hand] = lo
print("D| lowest hand y (frame, y):", best)
cmds.currentTime(first)
print("D| hips at start:", [round(v, 1) for v in cmds.xform(by_leaf["Hips"], q=True, ws=True, t=True)],
      "head y:", round(cmds.xform(by_leaf["Head"], q=True, ws=True, t=True)[1], 1))
print("D| rig (shot) hips/head y:", [round(cmds.xform("CHARLIE:mixamorig:" + n, q=True, ws=True, t=True)[1], 1) for n in ("Hips", "Head")])
print("D| DONE (nothing saved)")
maya.standalone.uninitialize()
