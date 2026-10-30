"""
=============================================================================
Render Chase Scene Storyboard Shots (Frame 12 Dutch Turn & Frame 13 Chase)
=============================================================================
"""

import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
import os

def render_shots():
    scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
    out_dir = r"D:\projects\ProjectAnimation\images\Chase_Storyboard_Renders"
    os.makedirs(out_dir, exist_ok=True)

    cmds.file(scene, open=True, force=True)

    # Make sure Arnold is loaded
    if not cmds.pluginInfo("mtoa", q=True, loaded=True):
        cmds.loadPlugin("mtoa")

    import mtoa.cmds.arnoldRender as a_render

    # Find the storyboard cameras
    all_cams = cmds.ls(type="camera")
    cam12_shape = [c for c in all_cams if "Shot12" in c][0]
    cam13_shape = [c for c in all_cams if "Shot13" in c][0]

    print(f"Cam 12 Shape: {cam12_shape}")
    print(f"Cam 13 Shape: {cam13_shape}")

    # Render Settings
    width = 960
    height = 540

    # Ensure output format is JPEG/PNG
    cmds.setAttr("defaultRenderGlobals.imageFormat", 8) # JPEG

    shots_to_render = [
        (cam12_shape, 60, os.path.join(out_dir, "Shot12_DutchAngle_LookBack_f60.jpg")),
        (cam13_shape, 60, os.path.join(out_dir, "Shot13_DynamicChase_Running_f60.jpg"))
    ]

    for cam, frame, out_file in shots_to_render:
        cmds.currentTime(frame)
        print(f"Rendering {cam} at frame {frame} to {out_file}...")
        try:
            # Render via Arnold
            a_render.arnoldRender(width, height, True, True, cam, out_file.replace("\\", "/"))
            print(f"DONE: {out_file} (exists: {os.path.exists(out_file)})")
        except Exception as e:
            print(f"Error rendering {cam}: {e}")

if __name__ == "__main__":
    render_shots()
