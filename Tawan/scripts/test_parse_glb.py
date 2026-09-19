import json, struct, os

glb_path = r"D:\projects\ProjectAnimation\backrooms_vr.glb"
with open(glb_path, "rb") as f:
    magic, version, length = struct.unpack("<4sII", f.read(12))
    chunk0_len, _ = struct.unpack("<I4s", f.read(8))
    gltf = json.loads(f.read(chunk0_len).decode("utf-8"))
    chunk1_len, _ = struct.unpack("<I4s", f.read(8))
    bin_data = f.read(chunk1_len)

accessors = gltf["accessors"]
bufferViews = gltf["bufferViews"]
meshes = gltf["meshes"]
materials = gltf["materials"]

COMPONENT_TYPES = {
    5120: ("b", 1), # BYTE
    5121: ("B", 1), # UNSIGNED_BYTE
    5122: ("h", 2), # SHORT
    5123: ("H", 2), # UNSIGNED_SHORT
    5125: ("I", 4), # UNSIGNED_INT
    5126: ("f", 4)  # FLOAT
}

TYPE_COUNTS = {
    "SCALAR": 1,
    "VEC2": 2,
    "VEC3": 3,
    "VEC4": 4,
    "MAT4": 16
}

def read_accessor(acc_idx):
    acc = accessors[acc_idx]
    bv = bufferViews[acc["bufferView"]]
    byte_offset = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    count = acc["count"]
    comp_type, comp_size = COMPONENT_TYPES[acc["componentType"]]
    num_comps = TYPE_COUNTS[acc["type"]]
    stride = bv.get("byteStride", comp_size * num_comps)
    
    fmt = f"<{num_comps}{comp_type}"
    data = []
    for i in range(count):
        offset = byte_offset + i * stride
        val = struct.unpack_from(fmt, bin_data, offset)
        data.append(val if num_comps > 1 else val[0])
    return data

print(f"Read GLB successfully! Testing mesh extraction...")
for i, m in enumerate(meshes):
    for p_idx, prim in enumerate(m.get("primitives", [])):
        attrs = prim.get("attributes", {})
        pos = read_accessor(attrs["POSITION"]) if "POSITION" in attrs else []
        uvs = read_accessor(attrs["TEXCOORD_0"]) if "TEXCOORD_0" in attrs else []
        normals = read_accessor(attrs["NORMAL"]) if "NORMAL" in attrs else []
        indices = read_accessor(prim["indices"]) if "indices" in prim else []
        mat_idx = prim.get("material")
        mat_name = materials[mat_idx]["name"] if mat_idx is not None else "default"
        print(f"Mesh {i:02d} ({m.get('name')}): Mat={mat_name}, Pos={len(pos)}, UV={len(uvs)}, Normals={len(normals)}, Indices={len(indices)}")
