"""
=============================================================================
Maya Showreel & Turntable Camera GUI Tool (Python)
Can be run inside Maya Script Editor or added to Maya Shelf.
=============================================================================
"""

import maya.cmds as cmds
import math

class MayaReelToolGUI:
    def __init__(self):
        self.window_name = "MayaReelCameraToolWin"
        self.build_ui()

    def build_ui(self):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)

        self.win = cmds.window(
            self.window_name,
            title="🎬 3D Showreel & Turntable Rig Tool",
            widthHeight=(360, 480),
            sizeable=False
        )

        cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnOffset=["both", 12])
        
        # Header Banner
        cmds.text(label="✨ Reel & Turntable Camera Generator", font="boldLabelFont", height=30, align="center")
        cmds.separator(height=10, style="in")

        # Mesh Selection
        cmds.text(label="1. Target Model / Character:", font="smallBoldLabelFont", align="left")
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(240, 90), adjustableColumn=1)
        self.mesh_field = cmds.textField(text="Monster_Buff_Blobbell")
        cmds.button(label="Get Selected", command=self.get_selected_mesh, backgroundColor=[0.25, 0.45, 0.65])
        cmds.setParent("..")

        cmds.separator(height=8, style="single")

        # Camera Settings
        cmds.text(label="2. Camera & Presentation Settings:", font="smallBoldLabelFont", align="left")
        
        self.focal_menu = cmds.optionMenuGrp(label="Focal Length:", columnWidth=(1, 100))
        cmds.menuItem(label="50 mm (Standard)")
        cmds.menuItem(label="75 mm (Portrait / Cinematic)")
        cmds.menuItem(label="85 mm (Character Hero)")
        cmds.menuItem(label="105 mm (Telephoto Tele)")
        cmds.optionMenuGrp(self.focal_menu, edit=True, select=2)

        self.mode_menu = cmds.optionMenuGrp(label="Reel Style:", columnWidth=(1, 100))
        cmds.menuItem(label="360 Turntable (Seamless Loop)")
        cmds.menuItem(label="Cinematic Dynamic (Detail to Hero)")
        cmds.optionMenuGrp(self.mode_menu, edit=True, select=1)

        self.frames_slider = cmds.intSliderGrp(
            label="Duration (Frames):",
            field=True,
            minValue=60,
            maxValue=720,
            fieldMinValue=24,
            fieldMaxValue=3600,
            value=240,
            columnWidth3=(110, 50, 160)
        )

        cmds.separator(height=8, style="single")

        # Environment & Lighting
        cmds.text(label="3. Studio Environment:", font="smallBoldLabelFont", align="left")
        self.lights_check = cmds.checkBox(label="Create 3-Point Studio Lights (Key/Fill/Rim)", value=True)
        self.floor_check = cmds.checkBox(label="Create Studio Floor Shadow Disc", value=True)

        cmds.separator(height=12, style="in")

        # Action Buttons
        cmds.button(
            label="🚀 Create / Update Reel Camera Rig",
            height=40,
            backgroundColor=[0.2, 0.65, 0.35],
            command=self.create_rig
        )

        cmds.rowLayout(numberOfColumns=2, columnWidth2=(165, 165))
        cmds.button(
            label="🎥 Look Through Reel Cam",
            height=32,
            backgroundColor=[0.3, 0.45, 0.6],
            command=self.look_through_cam
        )
        cmds.button(
            label="▶️ Play / Loop Preview",
            height=32,
            backgroundColor=[0.35, 0.35, 0.5],
            command=self.toggle_play
        )
        cmds.setParent("..")

        cmds.button(
            label="🎞️ Quick Playblast Reel Video (HD)",
            height=35,
            backgroundColor=[0.8, 0.45, 0.15],
            command=self.playblast_reel
        )

        cmds.button(
            label="🗑️ Remove Reel Rig",
            height=26,
            backgroundColor=[0.55, 0.25, 0.25],
            command=self.remove_rig
        )

        cmds.showWindow(self.win)

    def get_selected_mesh(self, *args):
        sel = cmds.ls(selection=True, transforms=True)
        if sel:
            cmds.textField(self.mesh_field, edit=True, text=sel[0])
        else:
            cmds.warning("Please select a transform node / mesh in Maya viewport first.")

    def create_rig(self, *args):
        target = cmds.textField(self.mesh_field, query=True, text=True)
        focal_text = cmds.optionMenuGrp(self.focal_menu, query=True, value=True)
        focal_val = float(focal_text.split()[0])
        
        mode_idx = cmds.optionMenuGrp(self.mode_menu, query=True, select=True)
        mode_str = "turntable_360" if mode_idx == 1 else "cinematic_reel"
        
        frames = cmds.intSliderGrp(self.frames_slider, query=True, value=True)
        do_lights = cmds.checkBox(self.lights_check, query=True, value=True)
        do_floor = cmds.checkBox(self.floor_check, query=True, value=True)

        from create_reel_rig import setup_reel_showcase
        setup_reel_showcase(
            target_mesh=target,
            start_frame=1,
            end_frame=frames,
            cam_focal_length=focal_val,
            create_lights=do_lights,
            create_floor=do_floor,
            mode=mode_str
        )
        self.look_through_cam()
        cmds.inViewMessage(amg="<hl>Reel Camera Rig Created Successfully!</hl>", pos="midCenter", fade=True)

    def look_through_cam(self, *args):
        if cmds.objExists("Reel_Cam"):
            current_panel = cmds.getPanel(withFocus=True)
            if not current_panel or "modelPanel" not in current_panel:
                panels = cmds.getPanel(type="modelPanel")
                if panels:
                    current_panel = panels[0]
            if current_panel and "modelPanel" in current_panel:
                cmds.lookThru(current_panel, "Reel_Cam")
                cmds.modelEditor(current_panel, edit=True, displayAppearance="smoothShaded", displayTextures=True)
        else:
            cmds.warning("Reel_Cam does not exist. Click 'Create Reel Camera Rig' first.")

    def toggle_play(self, *args):
        if cmds.play(query=True, state=True):
            cmds.play(state=False)
        else:
            cmds.play(forward=True)

    def playblast_reel(self, *args):
        if not cmds.objExists("Reel_Cam"):
            self.create_rig()
        self.look_through_cam()
        
        # Open Playblast Option or Run HD Playblast
        cmds.playblast(
            format="avi",
            compression="none",
            filename="D:/projects/ProjectAnimation/Monster_Reel_Showcase",
            forceOverwrite=True,
            sequenceTime=0,
            clearCache=1,
            viewer=True,
            showOrnaments=False,
            fp=4,
            percent=100,
            widthHeight=(1920, 1080)
        )

    def remove_rig(self, *args):
        if cmds.objExists("Reel_Showcase_GRP"):
            cmds.delete("Reel_Showcase_GRP")
            cmds.inViewMessage(amg="Reel Rig Removed.", pos="midCenter", fade=True)

def show_reel_ui():
    return MayaReelToolGUI()

if __name__ == "__main__":
    show_reel_ui()
