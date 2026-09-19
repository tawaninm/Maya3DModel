import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
import os
import shutil

def render_and_save():
    scene = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
    out_dir = r"D:\projects\ProjectAnimation\images\Chase_Storyboard_Renders"
    os.makedirs(out_dir, exist_ok=True)

    cmds.file(scene, open=True, force=True)
    cmds.currentTime(60)

    shots = [
        ("Cam_Shot12_DutchTurnShape1", "Shot12_DutchAngle_LookBack_f60.png"),
        ("Cam_Shot13_ChaseRunningShape1", "Shot13_DynamicChase_Running_f60.png")
    ]

    for cam, filename in shots:
        print(f"Rendering {cam} at frame 60...")
        rendered_path = cmds.render(cam, x=960, y=540)
        print(f"Rendered to: {rendered_path}")
        if rendered_path and os.path.exists(rendered_path):
            dst_path = os.path.join(out_dir, filename)
            shutil.copyfile(rendered_path, dst_path)
            print(f"SUCCESS_SAVED: {dst_path}")

if __name__ == "__main__":
    render_and_save()
