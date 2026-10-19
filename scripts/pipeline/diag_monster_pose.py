"""Read-only: why is the Monster in a T-pose in Shots 12/13? Checks keys on the Monster joints, which joints the mesh skin uses, skinCluster envelope. Nothing is saved."""
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot13.mb", open=True, force=True, loadReferenceDepth="all")
cmds.currentUnit(time="film")
joints = cmds.ls("MONSTER:*", type="joint", long=True)
print("P| monster joints:", len(joints), "namespaces:", sorted({j.split("|")[-1].rsplit(":", 1)[0] for j in joints}))
keyed = [j for j in joints if cmds.listConnections(j, type="animCurve")]
print("P| joints with anim curves:", len(keyed), "e.g.", [j.split("|")[-1] for j in keyed[:3]])
meshes = cmds.ls("MONSTER:*", type="mesh", noIntermediate=True, long=True)
print("P| meshes:", [(m.split("|")[-2] if "|" in m else m) for m in meshes])
for m in meshes:
    tr = cmds.listRelatives(m, parent=True, fullPath=True)[0]
    hist = cmds.listHistory(m) or []
    sc = [h for h in hist if cmds.nodeType(h) == "skinCluster"]
    print("P| mesh", tr.split("|")[-1], "visible", cmds.getAttr(tr + ".visibility"), "skinClusters", sc)
    for s in sc:
        infl = cmds.skinCluster(s, q=True, influence=True) or []
        print("P|   ", s, "envelope", cmds.getAttr(s + ".envelope"), "influences", len(infl), infl[:4], "keyed influences:", sum(1 for i in infl if cmds.listConnections(i, type="animCurve")))
hips = [j for j in joints if j.endswith("mixamorig:Hips")]
print("P| hips candidates:", [h.split("|")[-1] + " (%s)" % h.count("|") for h in hips])
for h in hips[:2]:
    for f in (1, 10, 24):
        cmds.currentTime(f)
        print("P|   %s f%d rot %s" % (h.split("|")[-1], f, [round(v, 1) for v in cmds.getAttr(h + ".rotate")[0]]))
for jn in ("MONSTER:mixamorig:LeftArm", "MONSTER:mixamorig:RightUpLeg"):
    if cmds.objExists(jn):
        for f in (1, 10, 24):
            cmds.currentTime(f)
            print("P|   %s f%d rot %s anim %s" % (jn, f, [round(v, 1) for v in cmds.getAttr(jn + ".rotate")[0]], bool(cmds.listConnections(jn, type="animCurve"))))
maya.standalone.uninitialize()
