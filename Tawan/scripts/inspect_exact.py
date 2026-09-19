import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds

def inspect():
    scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
    cmds.file(scene, open=True, force=True)
    cmds.currentTime(60)

    print("=== MONSTER BBOX ===")
    print(cmds.exactWorldBoundingBox("MONSTER:Monster_Buff_BlobbellShape"))

    print("=== MONSTER VISIBILITY ===")
    print("Shape vis:", cmds.getAttr("MONSTER:Monster_Buff_BlobbellShape.visibility"))
    print("Parent vis:", cmds.getAttr("MONSTER:Monster_Buff_Blobbell.visibility"))

    print("=== MONSTER TRANSLATES ===")
    print("Mesh:", cmds.xform("MONSTER:Monster_Buff_Blobbell", q=True, t=True, ws=True))
    print("Rig GRP:", cmds.xform("MONSTER:Monster_Rig_GRP", q=True, t=True, ws=True))
    print("Master CTRL:", cmds.xform("MONSTER:CTRL_Master", q=True, t=True, ws=True))
    print("Root JNT:", cmds.xform("MONSTER:JNT_Root", q=True, t=True, ws=True))

    print("=== CUBE TRANSLATES ===")
    print(cmds.xform("MainChar_Proxy_Cube", q=True, t=True, ws=True))

    print("=== CAM12 ===")
    print("Pos:", cmds.xform("Cam_Shot12_DutchTurn1", q=True, t=True, ws=True))
    print("Rot:", cmds.xform("Cam_Shot12_DutchTurn1", q=True, ro=True, ws=True))

    print("=== CAM13 ===")
    print("Pos:", cmds.xform("Cam_Shot13_ChaseRunning1", q=True, t=True, ws=True))
    print("Rot:", cmds.xform("Cam_Shot13_ChaseRunning1", q=True, ro=True, ws=True))

    print("=== ARMCHAIR ===")
    chairs = [m for m in cmds.ls(type="mesh") if "chair" in m.lower()]
    for ch in chairs:
        print(ch, cmds.exactWorldBoundingBox(ch))

if __name__ == "__main__":
    inspect()
