import json, struct

glb_path = r"D:\projects\ProjectAnimation\backrooms_vr.glb"
with open(glb_path, "rb") as f:
    f.seek(12)
    chunk0_len, _ = struct.unpack("<I4s", f.read(8))
    gltf = json.loads(f.read(chunk0_len).decode("utf-8"))

for i, n in enumerate(gltf.get("nodes", [])):
    if n.get("matrix") or n.get("translation") or n.get("rotation") or n.get("scale"):
        print(f"Node {i} ({n.get('name')}): matrix={n.get('matrix')}, t={n.get('translation')}, r={n.get('rotation')}, s={n.get('scale')}")
