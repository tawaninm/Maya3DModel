import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.loadPlugin("mtoa", quiet=True)
cmds.file(r"D:\projects\ProjectAnimation\scenes\Shots\Shot08.mb", open=True, force=True, loadReferenceDepth="all")
ks = [l for l in cmds.ls(type="aiAreaLight") if "Shot08" in l or "Shot08" in (cmds.listRelatives(l, parent=True) or [""])[0]]
print("K| key light shapes", ks)
cmds.setAttr(ks[0] + ".exposure", 13.0)
cmds.file(rename=r"D:\projects\ProjectAnimation\scratch_batch_test\Shot08_keytest.mb")
cmds.file(save=True, type="mayaBinary")
print("K| saved keytest, key exposure", cmds.getAttr(ks[0] + ".exposure"))
maya.standalone.uninitialize()
