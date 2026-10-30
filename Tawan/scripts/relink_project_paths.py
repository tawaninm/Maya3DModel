"""Rewrite the absolute D:/projects/ProjectAnimation paths in Tawan's Maya scenes to project-relative paths.

Run once on the machine that has Maya, then commit the re-saved scenes:

    mayapy relink_project_paths.py            # dry run, prints what would change
    mayapy relink_project_paths.py --apply    # re-saves every scene under scenes/ in place

Textures are looked up by file name under sourceimages/. References are looked up by file name under scenes/.
Archived scenes (archive/) are left alone.
"""
import os
import sys
from pathlib import Path

import maya.standalone

maya.standalone.initialize(name="python")
import maya.cmds as cmds  # noqa: E402  (needs standalone.initialize first)

PROJECT = Path(__file__).resolve().parents[1]
APPLY = "--apply" in sys.argv


def build_index(folder):
    index = {}
    for path in folder.rglob("*"):
        if path.is_file():
            index.setdefault(path.name.lower(), []).append(path.relative_to(PROJECT).as_posix())
    return index


TEXTURES = build_index(PROJECT / "sourceimages")
SCENES = build_index(PROJECT / "scenes")


def resolve(old_path, index):
    """Return the project-relative path for old_path, preferring the match with the same parent folder."""
    candidates = index.get(os.path.basename(old_path).lower(), [])
    if not candidates:
        return None
    parent = os.path.basename(os.path.dirname(old_path.replace("\\", "/"))).lower()
    for c in candidates:
        if os.path.basename(os.path.dirname(c)).lower() == parent:
            return c
    return candidates[0]


def relink_attr(node, attr):
    old = cmds.getAttr(f"{node}.{attr}") or ""
    if not old or cmds.referenceQuery(node, isNodeReferenced=True):
        return 0
    new = resolve(old, TEXTURES)
    if new is None:
        print(f"    MISSING  {node}.{attr}: {old}")
        return 0
    if new == old:
        return 0
    print(f"    {node}.{attr}: {old} -> {new}")
    if APPLY:
        cmds.setAttr(f"{node}.{attr}", new, type="string")
    return 1


def relink_references():
    changed = 0
    for old in cmds.file(query=True, reference=True) or []:
        if os.path.exists(old):
            continue
        new = resolve(old, SCENES)
        node = cmds.referenceQuery(old, referenceNode=True)
        if new is None:
            print(f"    MISSING  reference {node}: {old}")
            continue
        print(f"    reference {node}: {old} -> {new}")
        changed += 1
        if APPLY:
            cmds.file(new, loadReference=node)
    return changed


def main():
    cmds.workspace(str(PROJECT), openWorkspace=True)
    scenes = sorted(p for p in (PROJECT / "scenes").rglob("*.mb"))
    for scene in scenes:
        print(f"\n{scene.relative_to(PROJECT).as_posix()}")
        cmds.file(str(scene), open=True, force=True, ignoreVersion=True, loadReferenceDepth="none")
        changed = relink_references()
        for node in cmds.ls(type="file"):
            changed += relink_attr(node, "fileTextureName")
        for node in cmds.ls(type="imagePlane"):
            changed += relink_attr(node, "imageName")
        if APPLY and changed:
            cmds.file(save=True, type="mayaBinary", force=True)
            print(f"    saved ({changed} changes)")
        elif not changed:
            print("    nothing to change")
    cmds.file(new=True, force=True)


if __name__ == "__main__":
    main()
    maya.standalone.uninitialize()
