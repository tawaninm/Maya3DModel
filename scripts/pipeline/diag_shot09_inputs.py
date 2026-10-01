"""Read-only diagnostic for Shot 09: scene state, Walking.fbx length and root motion, head bob. Nothing is saved."""
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.mel as mel
cmds.loadPlugin("fbxmaya", quiet=True)
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot09.mb", open=True, force=True, loadReferenceDepth="all")
cmds.currentUnit(time="film")
print("W| range", cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True), "refs", [r.split("/")[-1] for r in cmds.file(q=True, reference=True)])
for n in ("GRP_CAM_Shot09", "CAM_Shot09"):
    print("W|", n, [round(v, 1) for v in cmds.getAttr(n + ".translate")[0]], [round(v, 1) for v in cmds.getAttr(n + ".rotate")[0]], "anim", cmds.listConnections(n, type="animCurve") or [])
print("W| LIGHT_MASTER exposure", cmds.getAttr("ENV:LIGHT_MASTER.exposure"), "flicker attrs", [a for a in (cmds.listAttr("ENV:LIGHT_MASTER", userDefined=True) or [])][:8])
print("W| Charlie placement t", [round(v, 1) for v in cmds.xform("CHARLIE:GRP_Charlie_Placement", q=True, ws=True, t=True)], "visible Monster", cmds.getAttr("MONSTER:GRP_Monster_Mixamo.visibility") if cmds.objExists("MONSTER:GRP_Monster_Mixamo") else None)
before = set(cmds.ls(type="joint")); bc = set(cmds.ls(type="animCurve"))
mel.eval('FBXImportMode -v "add"'); mel.eval('FBXImportFillTimeline -v false')
cmds.file(r"D:\projects\ProjectAnimation\raw_assets\mixamo\charlie\Walking.fbx", i=True, type="FBX", ignoreVersion=True)
nj = [j for j in cmds.ls(type="joint") if j not in before]; nc = [c for c in cmds.ls(type="animCurve") if c not in bc]
by = {j.split(":")[-1]: j for j in nj}
kt = sorted(set(t for c in nc for t in (cmds.keyframe(c, q=True, timeChange=True) or [])))
print("W| Walking key range", kt[0], kt[-1], "count", len(kt))
first, last = int(kt[0]), int(kt[-1])
for f in range(first, last + 1, max(1, (last - first) // 12)):
    cmds.currentTime(f)
    h = cmds.xform(by["Hips"], q=True, ws=True, t=True); hd = cmds.xform(by["Head"], q=True, ws=True, t=True)
    print("W| f%03d hips (%.1f, %.1f, %.1f) head (%.1f, %.1f, %.1f)" % (f, h[0], h[1], h[2], hd[0], hd[1], hd[2]))
maya.standalone.uninitialize()
