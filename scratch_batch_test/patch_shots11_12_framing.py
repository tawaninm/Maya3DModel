"""One-off patcher (2026-10-02): reframe shots 11 and 12 after the round-3 test frames."""
import io

P = r"D:\projects\ProjectAnimation\scripts\pipeline\build_shots10_14_t09.py"
s = io.open(P, encoding="utf-8").read()

# shot 11: camera further back, text smaller and further right so Charlie's head no longer hides "DO"
s = s.replace("    CX, WALL_Z, CH_Z, CAM_Z = -1250.0, 705.6, 615.0, 470.0\n", "    CX, WALL_Z, CH_Z, CAM_Z = -1250.0, 705.6, 615.0, 430.0\n")
s = s.replace("    make_dontrun_text(CX - 22.0, WALL_Z)\n", "    make_dontrun_text(CX - 55.0, WALL_Z)\n")
s = s.replace("width=130.0, height=32.5", "width=105.0, height=26.25")
s = s.replace("    r = ndc(cam, shape, om.MPoint(CX - 22.0, 92.0, WALL_Z))\n", "    r = ndc(cam, shape, om.MPoint(CX - 55.0, 92.0, WALL_Z))\n")

# shot 12: profile view from the south side of the corridor, both Charlie and the Monster in frame
a = s.index("    cam, shape = camera_nodes(\"12\")")
b = s.index("    ok = report_frustum(cam, shape, \"Charlie head\", lambda: CHARLIE + \"mixamorig:Head\", (1, 17, 48))")
new = '''    cam, shape = camera_nodes("12")
    set_lens(shape, 28.0, 5.0)
    mid = (-1215.0, 75.0, Z)
    # profile view from the south side (z 330): Charlie and the Monster side by side, whip pan from Charlie to the middle, Dutch angle
    key_camera(cam, range(1, N + 1), pos_fn=lambda f: (-1215.0, 85.0, 330.0),
               aim_fn=lambda f: lerp3((CX, 70.0, Z), mid, smooth((f - 8) / 28.0)),
               roll_fn=lambda f: 10.0 + 6.0 * smooth((f - 1) / 47.0), shake_rot=1.0, shake_trans=0.8, seed=12.0)
'''
s = s[:a] + new + s[b:]
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("patched")
