import json, struct, os, shutil
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds

glb_path = r"D:\projects\ProjectAnimation\backrooms_vr.glb"
tex_dir = r"D:\projects\ProjectAnimation\Backrooms_Textures"
obj_export_dir = r"D:\projects\ProjectAnimation\Props_Export"
os.makedirs(tex_dir, exist_ok=True)
os.makedirs(obj_export_dir, exist_ok=True)

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

# Extract and name textures
mat_to_tex_path = {}
for i, m in enumerate(materials):
    mat_name = m.get("name", f"Material_{i}")
    pbr = m.get("pbrMetallicRoughness", {})
    tex_info = pbr.get("baseColorTexture")
    if tex_info is not None:
        tex_idx = tex_info.get("index")
        img_idx = textures[tex_idx].get("source", tex_idx)
        img = images[img_idx]
        bv_idx = img.get("bufferView")
        bv = bufferViews[bv_idx]
        byte_offset = bv.get("byteOffset", 0)
        byte_len = bv.get("byteLength", 0)
        
        img_bytes = bin_data[byte_offset : byte_offset + byte_len]
        tex_filename = f"Tex_{mat_name}.png"
        tex_filepath = os.path.join(tex_dir, tex_filename)
        with open(tex_filepath, "wb") as out_f:
            out_f.write(img_bytes)
        mat_to_tex_path[mat_name] = tex_filepath
    else:
        mat_to_tex_path[mat_name] = None

print(f"Extracted {len(mat_to_tex_path)} texture files into {tex_dir}")

# Transform point from glTF Y-up with Sketchfab matrix (Z-up conversion) and scale to Maya cm (1m = 100cm)
# glTF Sketchfab matrix: [1, 0, 0, 0,  0, 0, 1, 0,  0, -1, 0, 0,  0, 0, 0, 1]
M = gltf["nodes"][0]["matrix"]
def transform_pos(p):
    x, y, z = p
    tx = (M[0]*x + M[4]*y + M[8]*z + M[12]) * 100.0
    ty = (M[1]*x + M[5]*y + M[9]*z + M[13]) * 100.0
    tz = (M[2]*x + M[6]*y + M[10]*z + M[14]) * 100.0
    return (tx, ty, tz)

def transform_normal(n):
    x, y, z = n
    tx = M[0]*x + M[4]*y + M[8]*z
    ty = M[1]*x + M[5]*y + M[9]*z
    tz = M[2]*x + M[6]*y + M[10]*z
    return (tx, ty, tz)

# Export individual OBJ files with MTL
def export_mesh_to_obj(mesh_indices, output_obj_path, mtl_name):
    mtl_path = os.path.splitext(output_obj_path)[0] + ".mtl"
    
    # Write MTL
    used_mats = set()
    for m_idx in mesh_indices:
        for prim in meshes[m_idx]["primitives"]:
            mat_idx = prim.get("material")
            if mat_idx is not None:
                used_mats.add(materials[mat_idx]["name"])
    
    with open(mtl_path, "w", encoding="utf-8") as fm:
        for mat_name in used_mats:
            fm.write(f"newmtl {mat_name}\n")
            fm.write("Ka 1.0 1.0 1.0\n")
            fm.write("Kd 1.0 1.0 1.0\n")
            fm.write("Ks 0.2 0.2 0.2\n")
            fm.write("Ns 20.0\n")
            fm.write("d 1.0\n")
            fm.write("illum 2\n")
            tex_file = mat_to_tex_path.get(mat_name)
            if tex_file:
                # relative or absolute
                rel_tex = os.path.relpath(tex_file, os.path.dirname(output_obj_path)).replace("\\", "/")
                fm.write(f"map_Kd {rel_tex}\n")
            fm.write("\n")
            
    # Write OBJ
    with open(output_obj_path, "w", encoding="utf-8") as fo:
        fo.write(f"mtllib {os.path.basename(mtl_path)}\n")
        v_offset = 1
        vt_offset = 1
        vn_offset = 1
        
        for m_idx in mesh_indices:
            m = meshes[m_idx]
            m_name = m.get("name", f"mesh_{m_idx}")
            fo.write(f"o {m_name}\n")
            fo.write(f"g {m_name}\n")
            
            for prim in m["primitives"]:
                mat_idx = prim.get("material")
                mat_name = materials[mat_idx]["name"] if mat_idx is not None else "default"
                fo.write(f"usemtl {mat_name}\n")
                
                attrs = prim.get("attributes", {})
                pos_list = read_accessor(attrs["POSITION"]) if "POSITION" in attrs else []
                uv_list = read_accessor(attrs["TEXCOORD_0"]) if "TEXCOORD_0" in attrs else []
                norm_list = read_accessor(attrs["NORMAL"]) if "NORMAL" in attrs else []
                idx_list = read_accessor(prim["indices"]) if "indices" in prim else []
                
                # Write vertices (in cm, Y-up)
                for p in pos_list:
                    tp = transform_pos(p)
                    fo.write(f"v {tp[0]:.4f} {tp[1]:.4f} {tp[2]:.4f}\n")
                
                # Write UVs (invert V for standard OBJ)
                for uv in uv_list:
                    fo.write(f"vt {uv[0]:.5f} {1.0 - uv[1]:.5f}\n")
                    
                # Write normals
                for n in norm_list:
                    tn = transform_normal(n)
                    fo.write(f"vn {tn[0]:.4f} {tn[1]:.4f} {tn[2]:.4f}\n")
                    
                # Write faces (triangles)
                has_uv = len(uv_list) > 0
                has_vn = len(norm_list) > 0
                
                for i in range(0, len(idx_list), 3):
                    i0 = idx_list[i]
                    i1 = idx_list[i+1]
                    i2 = idx_list[i+2]
                    
                    v0 = v_offset + i0
                    v1 = v_offset + i1
                    v2 = v_offset + i2
                    
                    if has_uv and has_vn:
                        fo.write(f"f {v0}/{v0}/{v0} {v1}/{v1}/{v1} {v2}/{v2}/{v2}\n")
                    elif has_uv:
                        fo.write(f"f {v0}/{v0} {v1}/{v1} {v2}/{v2}\n")
                    elif has_vn:
                        fo.write(f"f {v0}//{v0} {v1}//{v1} {v2}//{v2}\n")
                    else:
                        fo.write(f"f {v0} {v1} {v2}\n")
                        
                v_offset += len(pos_list)
                vt_offset += len(uv_list)
                vn_offset += len(norm_list)

print("Exporting individual prop OBJs with textures...")
export_mesh_to_obj([26], os.path.join(obj_export_dir, "Prop_ArmChair_Ref.obj"), "Armchair")
export_mesh_to_obj([8], os.path.join(obj_export_dir, "Prop_OfficeDesk_Ref.obj"), "Desk")
export_mesh_to_obj([2, 9], os.path.join(obj_export_dir, "Prop_CeilingLamp_Ref.obj"), "Lamp")
export_mesh_to_obj([27, 28], os.path.join(obj_export_dir, "Prop_ExitDoor_Ref.obj"), "Door")
export_mesh_to_obj([6, 7], os.path.join(obj_export_dir, "Prop_ExitSign_Ref.obj"), "ExitSign")
export_mesh_to_obj([20], os.path.join(obj_export_dir, "Prop_WallVent_Ref.obj"), "Vent")
export_mesh_to_obj([10, 11], os.path.join(obj_export_dir, "Prop_WallSocketSensor_Ref.obj"), "Socket")
export_mesh_to_obj([12, 14, 21, 23], os.path.join(obj_export_dir, "Prop_Walls_Ref.obj"), "Walls")
export_mesh_to_obj([16, 17, 18, 19], os.path.join(obj_export_dir, "Prop_CarpetFloors_Ref.obj"), "Carpet")
export_mesh_to_obj([0, 1, 3, 4], os.path.join(obj_export_dir, "Prop_CeilingTiles_Ref.obj"), "Ceiling")
# Full scene
export_mesh_to_obj(list(range(len(meshes))), os.path.join(obj_export_dir, "Backrooms_Full_Ref_Scene.obj"), "FullScene")

print("All OBJs and MTLs generated successfully!")
