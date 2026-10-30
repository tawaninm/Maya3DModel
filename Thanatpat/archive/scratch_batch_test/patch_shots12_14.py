"""One-off patcher (2026-10-02): wall text orientation, Preset B exposure 13.0, add shots 12-14 to build_shots10_14_t09.py, make shot 14 48 frames in the validators."""
import io

R = r"D:\projects\ProjectAnimation\scripts\pipeline"


def rd(n):
    return io.open(R + "\\" + n, encoding="utf-8").read()


def wr(n, s):
    io.open(R + "\\" + n, "w", encoding="utf-8", newline="").write(s)


# 1) text orientation + exposure
s = rd("make_dontrun_png.py")
s = s.replace("img = ImageOps.mirror(img)     # the plane faces -Z, so +X is on the viewer's left: pre-mirror the text so it reads correctly",
              "img = img.rotate(180)          # the polyPlane (axis -Z) shows its texture rotated 180 degrees to the camera (checked on a test render), so pre-rotate")
wr("make_dontrun_png.py", s)
s = rd("shot_lib.py")
s = s.replace("PRESET_B_EXPOSURE = 12.5 ", "PRESET_B_EXPOSURE = 13.0 ", 1)
s = s.replace("# plan.md said 11.5; test frames at 11.5 had mean 16-43/255 (Tawan wants the Backrooms bright, shot 09 = 125), 12.5 keeps B darker than A",
              "# plan.md said 11.5; test frames at 11.5 had mean 16-43/255 and 12.5 gave 36 (Tawan wants the Backrooms bright, shot 09 = 125), so B uses the A exposure and keeps the panel flicker as its difference")
wr("shot_lib.py", s)

# 2) shots 12-14
NEW = '''
# ---------------------------------------------------------------------------------------------------------------------------------
def shot12():
    """Shot 12 (48 f): MCU, Dutch angle, fast turn. Charlie spins 180 degrees (RunningTurn180, 17 f) and freezes facing the roaring Monster."""
    N = 48
    src = open_shot("12", N)
    show(CHARLIE, True)
    show(MONSTER, True)
    CX, MX, Z = -1300.0, -1130.0, 525.0
    bake_loop(CHARLIE, "charlie", "RunningTurn180", 17, 0, 16, in_place=False)
    freeze_from(CHARLIE, 17, N)                                         # holds the end pose after the turn
    bake_loop(MONSTER, "monster", "Mutant_Roaring", N, 15, 62, in_place=False)
    key_placement(CHARLIE, range(1, N + 1), lambda f: (CX, FLOOR_Y, Z), lambda f: -90.0)       # starts facing -X, the turn ends facing +X (the Monster)
    key_placement(MONSTER, range(1, N + 1), lambda f: (MX, FLOOR_Y, Z), lambda f: -90.0)       # faces -X, towards Charlie
    cam, shape = camera_nodes("12")
    set_lens(shape, 35.0, 5.0)
    mid = (-1215.0, 100.0, Z)
    key_camera(cam, range(1, N + 1), pos_fn=lambda f: (-1372.0, 95.0, 454.0),
               aim_fn=lambda f: lerp3((CX, 80.0, Z), mid, smooth((f - 8) / 28.0)),          # starts on Charlie, whips round to take in the Monster
               roll_fn=lambda f: 10.0 + 6.0 * smooth((f - 1) / 47.0), shake_rot=1.0, shake_trans=0.8, seed=12.0)
    ok = report_frustum(cam, shape, "Charlie head", lambda: CHARLIE + "mixamorig:Head", (1, 17, 48))
    ok2 = report_frustum(cam, shape, "Monster head", lambda: MONSTER + "mixamorig:Head", (1, 24, 48))
    print("L| Charlie in frame:", ok, " Monster in frame:", ok2)
    save(src)


# ---------------------------------------------------------------------------------------------------------------------------------
def shot13():
    """Shot 13 (48 f): POV running, handheld sprint. The camera starts looking back at the Monster chasing 110 units behind, whips forward and sprints."""
    N = 48
    src = open_shot("13", N)
    show(CHARLIE, True)
    show(MONSTER, True)
    bake_loop(CHARLIE, "charlie", "Terrified_Run", N, 0, 26, in_place=True)
    bake_loop(MONSTER, "monster", "Mutant_Run", N, 0, 21, in_place=True)
    X0, Z = -950.0, 525.0
    xc = lambda f: X0 - 7.1 * (f - 1)                                   # about 170 units/s
    xm = lambda f: X0 + 110.0 - 6.3 * (f - 1)                           # about 150 units/s: slowly losing ground
    key_placement(CHARLIE, range(1, N + 1), lambda f: (xc(f), FLOOR_Y, Z), lambda f: -90.0)
    key_placement(MONSTER, range(1, N + 1), lambda f: (xm(f), FLOOR_Y, Z), lambda f: -90.0)
    eyes = eye_points(CHARLIE, range(1, N + 1))
    collapse_head(CHARLIE)
    cam, shape = camera_nodes("13")
    set_lens(shape, 24.0, 15.0)
    w = lambda f: smooth((f - 6) / 14.0)
    key_camera(cam, range(1, N + 1), pos_fn=lambda f: (eyes[f].x - 4.0, eyes[f].y, eyes[f].z),
               rot_fn=lambda f: (8.0 + (-4.0 - 8.0) * w(f), -90.0 + 180.0 * w(f)),                  # yaw -90 = looking back (+X), +90 = forward (-X)
               roll_fn=lambda f: 3.0 * math.sin(f * 0.5), shake_rot=1.6, shake_trans=1.2, seed=13.0)
    ok = report_frustum(cam, shape, "Monster head", lambda: MONSTER + "mixamorig:Head", (1, 4, 8))
    print("L| Monster visible while looking back:", ok)
    save(src)


# ---------------------------------------------------------------------------------------------------------------------------------
def make_hole(cx, cz, size=130.0):
    """floor hole: a black plane just above the floor (y -11.6); Charlie sinks below it and disappears"""
    if cmds.objExists("Hole_Floor"):
        cmds.delete("Hole_Floor")
    plane = cmds.polyPlane(name="Hole_Floor", width=size, height=size, subdivisionsX=1, subdivisionsY=1)[0]
    cmds.xform(plane, ws=True, t=(cx, FLOOR_Y + 0.4, cz))
    mat = cmds.shadingNode("aiStandardSurface", asShader=True, name="Hole_M")
    cmds.setAttr(mat + ".baseColor", 0.0, 0.0, 0.0, type="double3")
    cmds.setAttr(mat + ".specular", 0.0)
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="Hole_SG")
    cmds.connectAttr(mat + ".outColor", sg + ".surfaceShader", force=True)
    cmds.sets(plane, forceElement=sg)
    print("L| floor hole at", (cx, FLOOR_Y + 0.4, cz), "size", size)


def shot14():
    """Shot 14 (48 f, the file had 24): wide bird's-eye, fast tilt down. Charlie jumps and dives into a hole in the floor."""
    N = 48
    src = open_shot("14", N)
    show(MONSTER, False)
    show(CHARLIE, True)
    HX, HZ = -1400.0, 525.0
    make_hole(HX, HZ)
    bake_loop(CHARLIE, "charlie", "Jumping", 46, 0, 45, in_place=False)
    freeze_from(CHARLIE, 46, N)
    px = lambda f: (HX + 90.0) + (HX - (HX + 90.0)) * smooth((f - 12) / 22.0)                    # steps towards the hole while jumping
    py = lambda f: FLOOR_Y - 170.0 * smooth((f - 34) / 14.0)                                      # sinks below the black plane at the end
    key_placement(CHARLIE, range(1, N + 1), lambda f: (px(f), py(f), HZ), lambda f: -90.0)
    cam, shape = camera_nodes("14")
    set_lens(shape, 24.0, 5.0)
    t = lambda f: smooth((f - 1) / 35.0)
    cpos = lambda f: lerp3((HX + 300.0, 215.0, HZ), (HX + 8.0, 238.0, HZ), t(f))
    target = lambda f: lerp3((px(f), 50.0, HZ), (HX, FLOOR_Y, HZ), t(f))

    def rot(f):
        pitch, _ = look_at(cpos(f), target(f))
        return max(-88.0, pitch), 90.0                                  # yaw fixed (looking -X), tilt only: no yaw flip when it points straight down

    key_camera(cam, range(1, N + 1), pos_fn=cpos, rot_fn=rot, shake_rot=0.6, shake_trans=0.5, seed=14.0)
    ok = report_frustum(cam, shape, "Charlie head", lambda: CHARLIE + "mixamorig:Head", (1, 20, 30))
    r = ndc(cam, shape, om.MPoint(HX, FLOOR_Y, HZ))
    print("L| hole centre NDC at frame", N, None if r is None else (round(r[0], 2), round(r[1], 2)))
    save(src)

'''
s = rd("build_shots10_14_t09.py")
marker = 'if __name__ == "__main__":'
assert marker in s and "def shot12" not in s
s = s.replace(marker, NEW + "\n" + marker, 1)
s = s.replace('{"10": shot10, "11": shot11}.get(which', '{"10": shot10, "11": shot11, "12": shot12, "13": shot13, "14": shot14}.get(which')
wr("build_shots10_14_t09.py", s)

# 3) shot 14 = 48 frames in the validators
for fn in ("validate_shots.py", "render_shots_batch.py"):
    t = rd(fn)
    t = t.replace('{"shot": "14", "frames": 24, "sec": 1, "preset": "B"}', '{"shot": "14", "frames": 48, "sec": 2, "preset": "B"}')
    t = t.replace('"13": 48, "14": 24}', '"13": 48, "14": 48}')
    wr(fn, t)
print("patched")
