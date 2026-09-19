import json, struct

glb_path = r"D:\projects\ProjectAnimation\backrooms_vr.glb"
with open(glb_path, "rb") as f:
    f.seek(12)
    chunk0_len, _ = struct.unpack("<I4s", f.read(8))
    gltf = json.loads(f.read(chunk0_len).decode("utf-8"))

print(f"Nodes ({len(gltf.get('nodes', []))}):")
for i, n in enumerate(gltf.get("nodes", [])):
    mesh_idx = n.get("mesh")
    mesh_name = gltf["meshes"][mesh_idx].get("name") if mesh_idx is not None else "None"
    print(f"[{i:02d}] Name: {n.get('name')}, Mesh: {mesh_idx} ({mesh_name}), Children: {n.get('children')}, Matrix: {n.get('matrix') is not None}, Trans: {n.get('translation')}, Rot: {n.get('rotation')}, Scale: {n.get('scale')}")

print("\nMeshes:")
for i, m in enumerate(gltf.get("meshes", [])):
    prims = m.get("primitives", [])
    mat_indices = [p.get("material") for p in prims]
    mat_names = [gltf["materials"][idx].get("name") if idx is not None else "None" for idx in mat_indices]
    print(f"Mesh [{i:02d}] '{m.get('name')}': {len(prims)} primitives, Mats: {mat_names}")
