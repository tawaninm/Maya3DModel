import json, struct, math

glb_path = r"D:\projects\ProjectAnimation\backrooms_vr.glb"
with open(glb_path, "rb") as f:
    f.seek(12)
    chunk0_len, _ = struct.unpack("<I4s", f.read(8))
    gltf = json.loads(f.read(chunk0_len).decode("utf-8"))
    chunk1_len, _ = struct.unpack("<I4s", f.read(8))
    bin_data = f.read(chunk1_len)

accessors = gltf["accessors"]
bufferViews = gltf["bufferViews"]
meshes = gltf["meshes"]
materials = gltf["materials"]

COMPONENT_TYPES = {
    5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2), 5123: ("H", 2), 5125: ("I", 4), 5126: ("f", 4)
}
TYPE_COUNTS = { "SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16 }

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

# Matrix in column-major order
# [1, 0, 0, 0,
#  0, 0, 1, 0,
#  0,-1, 0, 0,
#  0, 0, 0, 1]
M = gltf["nodes"][0]["matrix"]
def transform_point(p):
    x, y, z = p
    # Column-major multiply
    tx = M[0]*x + M[4]*y + M[8]*z + M[12]
    ty = M[1]*x + M[5]*y + M[9]*z + M[13]
    tz = M[2]*x + M[6]*y + M[10]*z + M[14]
    return (tx, ty, tz)

for i, m in enumerate(meshes):
    prim = m["primitives"][0]
    pos = read_accessor(prim["attributes"]["POSITION"])
    mat_idx = prim.get("material")
    mat_name = materials[mat_idx]["name"] if mat_idx is not None else "none"
    
    # Raw min/max
    xs = [p[0] for p in pos]
    ys = [p[1] for p in pos]
    zs = [p[2] for p in pos]
    
    # Transformed min/max
    t_pos = [transform_point(p) for p in pos]
    txs = [p[0] for p in t_pos]
    tys = [p[1] for p in t_pos]
    tzs = [p[2] for p in t_pos]
    
    print(f"Mesh {i:02d} ({mat_name}):")
    print(f"  Raw: X:[{min(xs):.2f}, {max(xs):.2f}], Y:[{min(ys):.2f}, {max(ys):.2f}], Z:[{min(zs):.2f}, {max(zs):.2f}]")
    print(f"  Transformed: X:[{min(txs):.2f}, {max(txs):.2f}], Y:[{min(tys):.2f}, {max(tys):.2f}], Z:[{min(tzs):.2f}, {max(tzs):.2f}] (Size: dx={max(txs)-min(txs):.2f}, dy={max(tys)-min(tys):.2f}, dz={max(tzs)-min(tzs):.2f})")
