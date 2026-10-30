"""One-off patcher (2026-10-02): Shot 05 v2 = starts with Charlie's ear against the corridor wall (continuity with the bedroom scene test02.mp4)."""
import io
import os
import shutil

R = r"D:\projects\ProjectAnimation\scripts\pipeline"


def rd(n):
    return io.open(R + "\\" + n, encoding="utf-8").read()


def wr(n, s):
    io.open(R + "\\" + n, "w", encoding="utf-8", newline="").write(s)


# shot_lib: lighting preset argument
s = rd("shot_lib.py")
assert "preset=" not in s
s = s.replace("def open_shot(shot, n_frames):", 'def open_shot(shot, n_frames, preset="B"):')
s = s.replace('    cmds.setAttr("ENV:LIGHT_MASTER.exposure", PRESET_B_EXPOSURE)   # Preset B (plan.md Q11): darker than A (13.0), flicker on\n    cmds.setAttr("ENV:LIGHT_MASTER.flickerEnable", 1.0)\n',
              '    if preset == "A":                                              # shots 05-09: steady bright light\n        cmds.setAttr("ENV:LIGHT_MASTER.exposure", 13.0)\n        cmds.setAttr("ENV:LIGHT_MASTER.flickerEnable", 0.0)\n    else:\n        cmds.setAttr("ENV:LIGHT_MASTER.exposure", PRESET_B_EXPOSURE)   # Preset B (plan.md Q11): darker than A (13.0), flicker on\n        cmds.setAttr("ENV:LIGHT_MASTER.flickerEnable", 1.0)\n')
assert 'preset == "A"' in s
wr("shot_lib.py", s)

# pristine Shot05 backup for the new builder (open_shot restores from scenes_backup_2026-10-02)
src = r"D:\projects\ProjectAnimation\scenes_backup_2026-10-01\Shot05_before_t09.mb"
dst = r"D:\projects\ProjectAnimation\scenes_backup_2026-10-02\Shot05_before_t09.mb"
os.makedirs(os.path.dirname(dst), exist_ok=True)
if not os.path.exists(dst):
    shutil.copy2(src, dst)
    print("copied pristine Shot05 backup")

NEW = '''
# ---------------------------------------------------------------------------------------------------------------------------------
EAR_Z = {"Spine": 8.0, "Spine1": 8.0, "Spine2": 6.0, "Neck": 14.0, "Head": 24.0}      # rotateZ added to the clip's frame-0 stance = lean + head tilt to Charlie's right
SOUTH_WALL_Z = 347.9                                                                    # ray-cast (diag_ear_pose.py)


def shot05():
    """Shot 05 v2 (48 f): continues the bedroom scene (test02.mp4 ends with the character's ear against the wall). Charlie stands side-on to the south
    corridor wall with his right ear on it (frames 1-8), is startled, spins to face the wall (9-12) and stumbles backwards (Stumble_Backwards at 0.75x
    speed, 13-44), then holds. Wide low-angle handheld camera with the crash zoom on frames 37-48. Preset A light."""
    N = 48
    HOLD, BLEND, STUM = 8, 12, 13
    scale = 4.0 / 3.0
    src = open_shot("05", N, preset="A")
    show(MONSTER, False)
    show(CHARLIE, True)
    path = clip("charlie", "Stumble_Backwards")
    bake_clip(path, rig_ns=CHARLIE, src_first=0, src_last=0, dst_first=1, set_range=False, time_scale=float(BLEND))          # stance of frame 0 for frames 1-12
    bake_clip(path, rig_ns=CHARLIE, src_first=0, src_last=23, dst_first=STUM, set_range=False, time_scale=scale)             # 32 frames, 13-44
    cmds.playbackOptions(min=1, max=N, animationStartTime=1, animationEndTime=N)
    cmds.cutKey(CHARLIE + "*", time=(45, 400), clear=True)
    freeze_from(CHARLIE, 44, N)
    # ear pose: add the lean/tilt on top of the baked stance, fading out between HOLD and BLEND
    for f in range(1, BLEND + 1):
        w = 1.0 if f <= HOLD else 1.0 - smooth((f - HOLD) / float(BLEND - HOLD))
        for jn, off in EAR_Z.items():
            j = CHARLIE + "mixamorig:" + jn
            v = cmds.getAttr(j + ".rotateZ", time=f)
            sway = 1.2 * math.sin(f * 0.9) * w
            cmds.setKeyframe(j, attribute="rotateZ", time=f, value=v + (off + sway) * w)
    # place Charlie so the nearest point of his body touches the wall (ear or shoulder) at frame 1
    X = -300.0
    g = placement(CHARLIE)
    cmds.setAttr(g + ".translate", X, FLOOR_Y, 400.0)
    cmds.setAttr(g + ".rotate", 0, -90.0, 0)
    cmds.currentTime(1)
    meshes = [m for m in {cmds.listRelatives(x, parent=True, fullPath=True)[0] for x in cmds.ls(CHARLIE + "*", type="mesh", noIntermediate=True, long=True)}
              if cmds.getAttr(m + ".visibility")]
    zmin = 1e9
    for m in meshes:
        v = cmds.xform(m + ".vtx[*]", q=True, ws=True, t=True)
        zmin = min(zmin, min(v[i] for i in range(2, len(v), 3)))
    ZC = 400.0 + (SOUTH_WALL_Z + 0.5 - zmin)
    print("L| nearest body point to the wall at 400: z %.1f -> Charlie placed at z %.1f (wall %.1f)" % (zmin, ZC, SOUTH_WALL_Z))
    yaw = lambda f: -90.0 if f <= HOLD else -90.0 - 90.0 * smooth((f - HOLD) / float(BLEND - HOLD))
    key_placement(CHARLIE, range(1, N + 1), lambda f: (X, FLOOR_Y, ZC), yaw)
    # camera: wide, low, handheld; aims at the head; crash zoom 24 -> 45 mm on frames 37-48
    head, hips = {}, {}
    for f in range(1, N + 1):
        cmds.currentTime(f)
        hp = wpos(CHARLIE + "mixamorig:Head")
        head[f] = (hp.x, hp.y + 15.0, hp.z)
    cam, shape = camera_nodes("05")
    set_lens(shape, 24.0, 5.0)
    key_camera(cam, range(1, N + 1), pos_fn=lambda f: (-120.0, 28.0, 545.0), aim_fn=lambda f: head[f], shake_rot=0.8, shake_trans=0.6, seed=5.0)
    for f, v in ((1, 24.0), (36, 24.0), (42, 33.5), (48, 45.0)):
        cmds.setKeyframe(shape, attribute="focalLength", time=f, value=v)
    ok = report_frustum(cam, shape, "Charlie head", lambda: CHARLIE + "mixamorig:Head", (1, 8, 12, 24, 36, 48))
    ok2 = report_frustum(cam, shape, "Charlie hips", lambda: CHARLIE + "mixamorig:Hips", (1, 24, 48))
    print("L| head in frame:", ok, " hips in frame:", ok2)
    save(src)

'''
s = rd("build_shots10_14_t09.py")
assert "def shot05" not in s
marker = 'if __name__ == "__main__":'
s = s.replace(marker, NEW + "\n" + marker, 1)
s = s.replace('{"10": shot10,', '{"05": shot05, "10": shot10,')
wr("build_shots10_14_t09.py", s)
print("patched")
