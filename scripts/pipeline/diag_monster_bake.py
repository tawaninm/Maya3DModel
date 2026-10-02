"""Read-only: compare the Mutant_Run clip's own joint values over time with the keys baked on the Monster rig in Shot13. Nothing is saved."""
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.mel as mel
cmds.loadPlugin("fbxmaya", quiet=True)
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot13.mb", open=True, force=True, loadReferenceDepth="all")
cmds.currentUnit(time="film")
j = "MONSTER:mixamorig:LeftArm.rotateX"
crv = cmds.listConnections(j, s=True, d=False, type="animCurve") or []
print("B| rig curve on", j, crv)
if crv:
    kt = cmds.keyframe(crv[0], q=True, timeChange=True) or []
    kv = cmds.keyframe(crv[0], q=True, valueChange=True) or []
    print("B|   keys", len(kt), "times", kt[:6], "...", kt[-2:], "values", [round(v, 1) for v in kv[:8]], "min/max", round(min(kv), 1), round(max(kv), 1))
for jn in ("MONSTER:mixamorig:Hips", "MONSTER:mixamorig:RightUpLeg", "MONSTER:mixamorig:Spine"):
    for a in ("rotateX", "rotateY", "translateY"):
        c = cmds.listConnections(jn + "." + a, s=True, d=False, type="animCurve") or []
        if c:
            kv = cmds.keyframe(c[0], q=True, valueChange=True) or []
            print("B|  ", jn.split(":")[-1], a, "keys", len(kv), "range", round(min(kv), 1), round(max(kv), 1))
# the clip itself
before = set(cmds.ls(type="joint")); bc = set(cmds.ls(type="animCurve"))
mel.eval('FBXImportMode -v "add"'); mel.eval('FBXImportFillTimeline -v false')
cmds.file(r"D:\projects\ProjectAnimation\raw_assets\mixamo\monster\Mutant_Run.fbx", i=True, type="FBX", ignoreVersion=True)
nj = [x for x in cmds.ls(type="joint") if x not in before]
by = {x.split(":")[-1]: x for x in nj}
print("B| clip joints:", len(nj), "sample names:", sorted(by)[:5])
la = by.get("LeftArm")
print("B| clip LeftArm node", la, "rotateX connections:", cmds.listConnections(la + ".rotateX", s=True, d=False), "rotate compound conn:", cmds.listConnections(la + ".rotate", s=True, d=False))
for f in (0, 5, 10, 15, 20):
    print("B|   clip LeftArm f%d rot %s" % (f, [round(cmds.getAttr(la + "." + a, time=f), 1) for a in ("rotateX", "rotateY", "rotateZ")]))
newc = [x for x in cmds.ls(type="animCurve") if x not in bc]
print("B| new anim curves from the clip:", len(newc), "types", sorted({cmds.nodeType(c) for c in newc}))
maya.standalone.uninitialize()
