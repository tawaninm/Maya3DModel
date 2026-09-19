"""
=============================================================================
Setup Chase Scene with Cube Main Character & Storyboard Cameras (Frames 12-13)
Project: ProjectAnimation
Target Scene: scenes/Backrooms/Backrooms_Chase_Storyboard_Scene.mb
=============================================================================
"""

import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
import os

def setup_chase():
    base_scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Monster_Animation_Scene.mb"
    out_scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
    render_dir = r"D:\projects\ProjectAnimation\images\Chase_Storyboard_Renders"

    os.makedirs(render_dir, exist_ok=True)
    cmds.file(base_scene, open=True, force=True)

    # 1. Main Character Proxy (Cube)
    proxy_name = "MainChar_Proxy_Cube"
    if cmds.objExists(proxy_name):
        cmds.delete(proxy_name)

    # Create Human-sized proxy box (W: 45cm, D: 30cm, H: 170cm)
    cube_shape = cmds.polyCube(name=proxy_name, width=45, depth=30, height=170, sx=1, sy=3, sz=1)[0]
    
    # Move pivot to bottom of feet (Y = -85 to 0)
    cmds.xform(cube_shape, pivots=(0, -85, 0), ws=True)
    # Ground height in Backrooms is Y = -11.90, so center Y is -11.90 + 85 = 73.1
    floor_y = 73.1

    # Clean distinct proxy material (Cyan/Blue)
    mat_name = "M_MainChar_Proxy"
    sg_name = f"{mat_name}_SG"
    if not cmds.objExists(mat_name):
        sh = cmds.shadingNode("aiStandardSurface", asShader=True, name=mat_name)
        cmds.setAttr(f"{sh}.baseColor", 0.1, 0.5, 0.85, type="double3") # Cyan Blue
        if cmds.attributeQuery("specularRoughness", node=sh, exists=True):
            cmds.setAttr(f"{sh}.specularRoughness", 0.4)
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg_name)
        cmds.connectAttr(f"{sh}.outColor", f"{sg}.surfaceShader", force=True)
    cmds.sets(cube_shape, edit=True, forceElement=sg_name)

    # Animate Cube sprinting ahead of Monster (Z: -210 at f1 -> +60 at f120)
    cmds.playbackOptions(minTime=1, maxTime=120)
    cmds.setKeyframe(cube_shape, attribute="translateZ", value=-210.0, time=1)
    cmds.setKeyframe(cube_shape, attribute="translateZ", value=60.0, time=120)
    cmds.setKeyframe(cube_shape, attribute="translateX", value=0.0, time=1)
    cmds.setKeyframe(cube_shape, attribute="translateX", value=5.0, time=120)
    cmds.setKeyframe(cube_shape, attribute="rotateX", value=-12.0, time=1) # Sprint lean forward
    cmds.setKeyframe(cube_shape, attribute="rotateX", value=-12.0, time=120)

    # Sprint step bobbing
    for f in range(1, 121, 15):
        cmds.setKeyframe(cube_shape, attribute="translateY", value=floor_y, time=f)
        if f + 7 <= 120:
            cmds.setKeyframe(cube_shape, attribute="translateY", value=floor_y + 4.5, time=f + 7)

    # 2. Storyboard Camera 1: Frame 12 - Medium Close-Up Dutch Angle Look Back
    # หันหลังมองเห็น Monster พุ่งเข้ามาในระยะกระชั้นชิด
    cam12 = "Cam_Shot12_DutchTurn"
    if cmds.objExists(cam12):
        cmds.delete(cam12)
    cam12_trans, cam12_shape = cmds.camera(name=cam12, focalLength=30.0)
    cmds.setAttr(f"{cam12_shape}.renderable", 1)

    # Camera 12 follows beside/ahead of Cube looking backwards at Monster
    cmds.setKeyframe(cam12_trans, attribute="translateX", value=32.0, time=1)
    cmds.setKeyframe(cam12_trans, attribute="translateY", value=145.0, time=1) # Eye level
    cmds.setKeyframe(cam12_trans, attribute="translateZ", value=-170.0, time=1)
    cmds.setKeyframe(cam12_trans, attribute="rotateX", value=-8.0, time=1)
    cmds.setKeyframe(cam12_trans, attribute="rotateY", value=-168.0, time=1) # Look backward at monster
    cmds.setKeyframe(cam12_trans, attribute="rotateZ", value=14.0, time=1) # Dutch angle tension

    cmds.setKeyframe(cam12_trans, attribute="translateX", value=37.0, time=120)
    cmds.setKeyframe(cam12_trans, attribute="translateY", value=145.0, time=120)
    cmds.setKeyframe(cam12_trans, attribute="translateZ", value=100.0, time=120)
    cmds.setKeyframe(cam12_trans, attribute="rotateX", value=-8.0, time=120)
    cmds.setKeyframe(cam12_trans, attribute="rotateY", value=-168.0, time=120)
    cmds.setKeyframe(cam12_trans, attribute="rotateZ", value=14.0, time=120)

    # 3. Storyboard Camera 2: Frame 13 - Over-The-Shoulder Dynamic Chase Tracking Camera
    # กล้องวิ่งตามตัวเอก (Cube) เห็นด้านหลัง Cube กำลังวิ่ง และเห็น Monster ยักษ์วิ่งไล่ตามมาในโถงทางเดิน
    cam13 = "Cam_Shot13_ChaseRunning"
    if cmds.objExists(cam13):
        cmds.delete(cam13)
    cam13_trans, cam13_shape = cmds.camera(name=cam13, focalLength=24.0)
    cmds.setAttr(f"{cam13_shape}.renderable", 1)

    # Camera 13 positioned behind & above Cube looking down corridor
    cmds.setKeyframe(cam13_trans, attribute="translateX", value=-25.0, time=1)
    cmds.setKeyframe(cam13_trans, attribute="translateY", value=160.0, time=1)
    cmds.setKeyframe(cam13_trans, attribute="translateZ", value=-280.0, time=1)
    cmds.setKeyframe(cam13_trans, attribute="rotateX", value=-10.0, time=1)
    cmds.setKeyframe(cam13_trans, attribute="rotateY", value=8.0, time=1)
    cmds.setKeyframe(cam13_trans, attribute="rotateZ", value=-4.0, time=1)

    cmds.setKeyframe(cam13_trans, attribute="translateX", value=-20.0, time=120)
    cmds.setKeyframe(cam13_trans, attribute="translateY", value=160.0, time=120)
    cmds.setKeyframe(cam13_trans, attribute="translateZ", value=-10.0, time=120)
    cmds.setKeyframe(cam13_trans, attribute="rotateX", value=-10.0, time=120)
    cmds.setKeyframe(cam13_trans, attribute="rotateY", value=8.0, time=120)
    cmds.setKeyframe(cam13_trans, attribute="rotateZ", value=-4.0, time=120)

    # Arnold Render Settings: 960x540 for fast preview renders
    if cmds.objExists("defaultResolution"):
        cmds.setAttr("defaultResolution.width", 960)
        cmds.setAttr("defaultResolution.height", 540)
        cmds.setAttr("defaultResolution.deviceAspectRatio", 1.777)
        cmds.setAttr("defaultResolution.pixelAspect", 1.0)

    # Save setup scene
    cmds.file(rename=out_scene)
    saved = cmds.file(save=True, type="mayaBinary")
    print(f"SUCCESS: Chase Storyboard Scene saved to {saved}")
    return saved

if __name__ == "__main__":
    setup_chase()
