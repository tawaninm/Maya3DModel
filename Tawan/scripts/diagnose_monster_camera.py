import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds

def diagnose():
    scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
    cmds.file(scene, open=True, force=True)

    print("--- ALL CAMERAS ---")
    cams = cmds.ls(type="camera")
    for c in cams:
        trans = cmds.listRelatives(c, parent=True)[0]
        print(f"Cam: {c}, Parent: {trans}")
        print(f"  Pos: {cmds.xform(trans, q=True, t=True, ws=True)}")
        print(f"  Rot: {cmds.xform(trans, q=True, ro=True, ws=True)}")

    print("\n--- MONSTER RIG CONTROLS & ANIMATION ---")
    ctrls = [n for n in cmds.ls() if "CTRL_Master" in n or "MainChar" in n]
    for n in ctrls:
        print(f"Node: {n}")
        for t in [1, 60, 120]:
            cmds.currentTime(t)
            pos = cmds.xform(n, q=True, t=True, ws=True)
            print(f"  t={t}: pos={pos}")

    print("\n--- MONSTER GEOMETRY BOUNDS ---")
    geo = [n for n in cmds.ls(type="mesh") if "monster" in n.lower() or "blob" in n.lower()]
    for g in geo[:5]:
        p = cmds.listRelatives(g, parent=True)[0]
        bb = cmds.exactWorldBoundingBox(p)
        vis = cmds.getAttr(f"{p}.visibility")
        print(f"Mesh: {g} (Parent: {p}), BBox: {bb}, Vis: {vis}")

    print("\n--- CORRIDOR / WALL GEOMETRY BOUNDS ---")
    env = [n for n in cmds.ls(type="mesh") if "wall" in n.lower() or "room" in n.lower() or "floor" in n.lower() or "prop" in n.lower() or "corridor" in n.lower()]
    print(f"Env mesh count: {len(env)}")
    for e in env[:5]:
        p = cmds.listRelatives(e, parent=True)[0]
        bb = cmds.exactWorldBoundingBox(p)
        print(f"Env: {e} ({p}), BBox: {bb}")

if __name__ == "__main__":
    diagnose()
