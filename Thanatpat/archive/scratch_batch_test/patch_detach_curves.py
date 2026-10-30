import io
P = r"D:\projects\ProjectAnimation\scripts\pipeline\shot_lib.py"
s = io.open(P, encoding="utf-8").read()
old = 'def bake_loop(ns, who, name, n_total, src_first, src_last, in_place, scale=1.0, dst_first=1):'
assert old in s and "def detach_referenced_curves" not in s
new = '''def detach_referenced_curves(ns):
    """Monster_Mixamo.mb ships with animation curves of its own (one key at frame 0, the T-pose). setKeyframe on a joint driven by such a REFERENCED curve
    edits the referenced node, and that edit is not saved with the shot: the reopened scene shows the T-pose (Shots 12/13, found 2026-10-02).
    Disconnect the referenced curves first so the bake creates new curves that live in the shot file."""
    n = 0
    for j in cmds.ls(ns + "mixamorig:*", type="joint"):
        for a in CAM_ATTRS:
            plug = j + "." + a
            for c in cmds.listConnections(plug, s=True, d=False, type="animCurve") or []:
                if cmds.referenceQuery(c, isNodeReferenced=True):
                    cmds.disconnectAttr(c + ".output", plug)
                    n += 1
    print("L| detached %d referenced animation curves on %s" % (n, ns))
    return n


'''
s = s.replace(old, new + old, 1)
s = s.replace('    path = clip(who, name)\n    clip_len', '    detach_referenced_curves(ns)\n    path = clip(who, name)\n    clip_len', 1)
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("patched")
