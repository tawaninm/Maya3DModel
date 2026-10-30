import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
cmds.loadPlugin("mtoa", quiet=True)

tp = cmds.shadingNode("aiTriplanar", asTexture=True)
print("Created aiTriplanar:", tp)
for a in ["input", "scale", "coordSpace", "blend", "cell", "rotate"]:
    if cmds.attributeQuery(a, node=tp, exists=True):
        val = cmds.getAttr(f"{tp}.{a}")
        t = cmds.getAttr(f"{tp}.{a}", type=True)
        print(f"  {a}: type={t}, value={val}")

# Check enum values for coordSpace
enums = cmds.attributeQuery("coordSpace", node=tp, listEnum=True)
print("coordSpace enums:", enums)
