import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds, os
for n in (7, 8):
    p = r"D:\projects\ProjectAnimation\scenes\Shots\Shot%02d.mb" % n
    cmds.file(p, open=True, force=True, loadReferenceDepth="none")
    for r in cmds.file(q=True, reference=True):
        path = cmds.referenceQuery(r, filename=True, withoutCopyNumber=True)
        print("L| shot%02d" % n, os.path.basename(path), "exists" if os.path.exists(path) else "MISSING", path)
maya.standalone.uninitialize()
