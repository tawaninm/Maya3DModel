"""Bake a Mixamo clip (FBX without skin) onto the joints of a Mixamo-rigged character already in the scene.

Usage (inside mayapy, after the rig scene/reference is loaded):
    from bake_mixamo_clip import bake_clip
    info = bake_clip(r"...\\Stumble_Backwards.fbx", rig_ns="CHARLIE:", src_first=0, src_last=23, dst_first=1)

Scale: the clips Mixamo exports for a character already use that character's bone lengths. Charlie_Mixamo.mb was checked on 2026-09-30:
hips->head is 50.02 in the rig and 49.3-50.0 in the clips, so the translation scale ratio is 1.0. `bake_clip` still prints the measured ratio.
How it works: the FBX ignores the namespace flag when names clash with the rig, so the clip's joints are found as "joints that did not exist
before the import" (Maya renames them, e.g. mixamorig1:Hips). Every keyed channel is sampled per frame and keyed on the rig joint with the same
leaf name, then the imported joints, curves and namespaces are removed. Works on referenced rigs (keys are stored in the shot file)."""
import maya.cmds as cmds

ATTRS = ("translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ")


def _dist(a, b):
    pa, pb = cmds.xform(a, q=True, ws=True, t=True), cmds.xform(b, q=True, ws=True, t=True)
    return sum((pa[i] - pb[i]) ** 2 for i in range(3)) ** 0.5


def bake_clip(fbx, rig_ns="", src_first=0, src_last=None, dst_first=1, set_range=True):
    cmds.loadPlugin("fbxmaya", quiet=True)
    before_j = set(cmds.ls(type="joint"))
    before_c = set(cmds.ls(type="animCurve"))
    before_ns = set(cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True) or [])
    # the FBX plugin remembers its last import mode; "merge" would key the existing joints directly and create no new ones
    import maya.mel as mel
    mel.eval('FBXImportMode -v "add"')
    mel.eval('FBXImportFillTimeline -v false')
    cmds.file(fbx, i=True, type="FBX", ignoreVersion=True)
    new_j = [j for j in cmds.ls(type="joint") if j not in before_j]
    new_c = [c for c in cmds.ls(type="animCurve") if c not in before_c]
    if not new_j:
        raise RuntimeError("no new joints after importing %s" % fbx)
    by_leaf = {j.split(":")[-1]: j for j in new_j}
    kt = sorted(set(t for c in new_c for t in (cmds.keyframe(c, q=True, timeChange=True) or [])))
    if src_last is None:
        src_last = int(kt[-1])
    cmds.currentTime(kt[0])
    rig_hips, rig_head = rig_ns + "mixamorig:Hips", rig_ns + "mixamorig:Head"
    ratio = _dist(rig_hips, rig_head) / max(1e-6, _dist(by_leaf["Hips"], by_leaf["Head"]))
    n_keys, missing = 0, []
    for leaf, sj in by_leaf.items():
        dj = rig_ns + "mixamorig:" + leaf
        if not cmds.objExists(dj):
            missing.append(leaf)
            continue
        for a in ATTRS:
            if not cmds.listConnections(sj + "." + a, s=True, d=False):
                continue
            for f in range(int(src_first), int(src_last) + 1):
                v = cmds.getAttr(sj + "." + a, time=f)
                cmds.setKeyframe(dj, attribute=a, time=f - int(src_first) + dst_first, value=v)
                n_keys += 1
    # clean up: imported joints (roots first), leftover curves, new namespaces
    roots = [j for j in new_j if (cmds.listRelatives(j, parent=True) or [None])[0] not in new_j]
    for r in roots:
        if cmds.objExists(r):
            cmds.delete(r)
    for c in new_c:
        if cmds.objExists(c):
            cmds.delete(c)
    for ns in sorted(set(cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True) or []) - before_ns, reverse=True):
        if cmds.namespace(exists=ns) and not (cmds.namespaceInfo(ns, listNamespace=True) or []):
            cmds.namespace(removeNamespace=ns)
    n_frames = int(src_last) - int(src_first) + 1
    if set_range:
        cmds.playbackOptions(min=dst_first, max=dst_first + n_frames - 1, animationStartTime=dst_first, animationEndTime=dst_first + n_frames - 1)
    info = {"keys": n_keys, "frames": n_frames, "translate_scale_ratio": round(ratio, 3), "missing_dst_joints": missing,
            "dst_range": (dst_first, dst_first + n_frames - 1)}
    print("BAKE", fbx.replace("\\", "/").split("/")[-1], info)
    return info
