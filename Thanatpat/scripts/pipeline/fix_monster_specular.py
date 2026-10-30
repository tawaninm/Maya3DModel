"""
T07 fix: set specular = 0.5 on aiStandardSurface_Monster in Monster_Mixamo.mb.
Current value 0.40 is below target 0.5. roughness 0.55 is within range, no change needed.
Backs up before modifying.
"""
import os, shutil
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.loadPlugin("mtoa", quiet=True)

SCENE = r"D:\projects\ProjectAnimation\scenes\Characters\Monster_Mixamo.mb"
BACKUP = r"D:\projects\ProjectAnimation\scenes_backup_2026-09-30\Characters\Monster_Mixamo_specfix.mb"

# Backup
os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
if not os.path.exists(BACKUP):
    shutil.copy2(SCENE, BACKUP)
    print(f"Backed up to {BACKUP}")

cmds.file(SCENE, open=True, force=True)

for sh in cmds.ls("*aiStandardSurface_Monster*", type="aiStandardSurface"):
    old_r = cmds.getAttr(sh + ".specularRoughness")
    old_s = cmds.getAttr(sh + ".specular")
    print(f"BEFORE {sh}: specular={old_s:.4f}  specularRoughness={old_r:.4f}")

    # Only set specular to 0.5 — roughness 0.55 is already within range
    cmds.setAttr(sh + ".specular", 0.5)

    new_r = cmds.getAttr(sh + ".specularRoughness")
    new_s = cmds.getAttr(sh + ".specular")
    print(f"AFTER  {sh}: specular={new_s:.4f}  specularRoughness={new_r:.4f}")

cmds.file(save=True, force=True, type="mayaBinary")
sz = os.path.getsize(SCENE)
print(f"Saved {SCENE} ({sz} bytes)")

maya.standalone.uninitialize()
