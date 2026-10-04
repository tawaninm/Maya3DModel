"""One-off patcher (2026-10-02): shot 12 camera was behind the south wall (z 330 < 343) -> black; shot 14 starts lower and further away."""
import io

P = r"D:\projects\ProjectAnimation\scripts\pipeline\build_shots10_14_t09.py"
s = io.open(P, encoding="utf-8").read()
s = s.replace("    set_lens(shape, 28.0, 5.0)\n    mid = (-1215.0, 75.0, Z)\n    # profile view from the south side (z 330)", "    set_lens(shape, 24.0, 5.0)\n    mid = (-1215.0, 75.0, Z)\n    # profile view from the south side of the corridor (z 372; the south wall is at z 343, z 330 was behind it and rendered black)")
s = s.replace("pos_fn=lambda f: (-1215.0, 85.0, 330.0)", "pos_fn=lambda f: (-1215.0, 85.0, 372.0)")
s = s.replace("cpos = lambda f: lerp3((HX + 300.0, 215.0, HZ), (HX + 8.0, 238.0, HZ), t(f))", "cpos = lambda f: lerp3((HX + 430.0, 170.0, HZ), (HX + 8.0, 238.0, HZ), t(f))")
io.open(P, "w", encoding="utf-8", newline="").write(s)
print("patched", s.count("372.0"), s.count("HX + 430.0"))
