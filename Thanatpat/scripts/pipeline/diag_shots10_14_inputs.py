"""Read-only diagnostic for Shots 10-14: scene state, light preset B attrs, rig placement/visibility, clip lengths and root motion. Nothing is saved."""
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.mel as mel
cmds.loadPlugin("fbxmaya", quiet=True)
SH = r"D:\projects\ProjectAnimation\scenes\Shots\Shot%s.mb"
for sh in ("10", "11", "12", "13", "14"):
    cmds.file(SH % sh, open=True, force=True, loadReferenceDepth="all")
    cmds.currentUnit(time="film")
    cam = "CAM_Shot" + sh; grp = "GRP_CAM_Shot" + sh
    lm = "ENV:LIGHT_MASTER"
    print("S| shot", sh, "range", cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True),
          "refs", [r.split("/")[-1] for r in cmds.file(q=True, reference=True) if "{" not in r])
    print("S|   cam", [round(v, 1) for v in cmds.getAttr(grp + ".translate")[0]], [round(v, 1) for v in cmds.getAttr(grp + ".rotate")[0]], "anim", len(cmds.listConnections(cam, type="animCurve") or []),
          "lightMaster exp", cmds.getAttr(lm + ".exposure"), "flicker", cmds.getAttr(lm + ".flickerEnable") if cmds.attributeQuery("flickerEnable", node=lm, exists=True) else None,
          "expressions", [e for e in cmds.ls(type="expression")][:4])
    for n in ("CHARLIE:GRP_Charlie_Placement", "MONSTER:GRP_Monster_Mixamo"):
        if cmds.objExists(n):
            print("S|  ", n, [round(v, 1) for v in cmds.xform(n, q=True, ws=True, t=True)], "rot", [round(v, 1) for v in cmds.getAttr(n + ".rotate")[0]], "vis", cmds.getAttr(n + ".visibility"))
    if sh == "10":
        mb = cmds.exactWorldBoundingBox("MONSTER:Monster_Buff_Blobbell") if cmds.objExists("MONSTER:Monster_Buff_Blobbell") else None
        print("S|   monster bbox", [round(v, 1) for v in mb] if mb else None)
        ch = cmds.exactWorldBoundingBox("CHARLIE:body") if cmds.objExists("CHARLIE:body") else None
        print("S|   charlie body bbox", [round(v, 1) for v in ch] if ch else None)
        print("S|   flicker-related nodes:", [n for n in cmds.ls("*flicker*", "*Flicker*")][:6], "lights near:", len(cmds.ls(type="aiAreaLight")))
CLIPS = [("charlie", "Walking"), ("charlie", "Look_Around"), ("charlie", "RunningTurn180"), ("charlie", "Terrified_Run"), ("charlie", "Jumping"),
         ("monster", "Walking"), ("monster", "Mutant_Roaring"), ("monster", "Mutant_Run")]
cmds.file(new=True, force=True)
for who, name in CLIPS:
    cmds.file(new=True, force=True)
    mel.eval('FBXImportMode -v "add"'); mel.eval('FBXImportFillTimeline -v false')
    cmds.file(r"D:\projects\ProjectAnimation\raw_assets\mixamo\%s\%s.fbx" % (who, name), i=True, type="FBX", ignoreVersion=True)
    js = cmds.ls(type="joint"); by = {j.split(":")[-1]: j for j in js}
    kt = sorted(set(t for c in cmds.ls(type="animCurve") for t in (cmds.keyframe(c, q=True, timeChange=True) or [])))
    first, last = int(kt[0]), int(kt[-1]); hips = by.get("Hips"); head = by.get("Head")
    def p(j, f):
        cmds.currentTime(f); return cmds.xform(j, q=True, ws=True, t=True)
    h0, h1 = p(hips, first), p(hips, last)
    print("C| %-8s %-16s frames %d-%d joints %d  hips start (%.0f,%.0f,%.0f) end (%.0f,%.0f,%.0f) travel %.0f  head y %.0f..%.0f" % (
        who, name, first, last, len(js), h0[0], h0[1], h0[2], h1[0], h1[1], h1[2], ((h1[0]-h0[0])**2 + (h1[2]-h0[2])**2) ** 0.5,
        min(p(head, f)[1] for f in range(first, last + 1, 4)), max(p(head, f)[1] for f in range(first, last + 1, 4))))
maya.standalone.uninitialize()
