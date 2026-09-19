import json, struct, os

glb_path = r"D:\projects\ProjectAnimation\backrooms_vr.glb"
tex_dir = r"D:\projects\ProjectAnimation\Backrooms_Textures"
obj_export_dir = r"D:\projects\ProjectAnimation\Props_Export_Textured"
os.makedirs(obj_export_dir, exist_ok=True)
os.makedirs(tex_dir, exist_ok=True)

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
textures = gltf.get("textures", [])
images = gltf.get("images", [])

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

# Extract image filename mapping
mat_to_tex_file = {}
for i, m in enumerate(materials):
    mat_name = m.get("name", f"Material_{i}")
    pbr = m.get("pbrMetallicRoughness", {})
    tex_info = pbr.get("baseColorTexture")
    if tex_info is not None:
        tex_idx = tex_info.get("index")
        img_idx = textures[tex_idx].get("source", tex_idx)
        img_name = images[img_idx].get("name", f"image_{img_idx}")
        clean_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in img_name)
        tex_filename = f"{img_idx:02d}_{clean_name}.png"
        mat_to_tex_file[mat_name] = tex_filename
    else:
        mat_to_tex_file[mat_name] = None

print("Material to texture file mapping:")
for k, v in mat_to_tex_file.items():
    print(f"  {k} -> {v}")
