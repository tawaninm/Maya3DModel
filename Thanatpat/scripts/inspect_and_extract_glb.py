import struct
import json
import os

glb_path = r"D:\projects\ProjectAnimation\backrooms_vr.glb"
output_tex_dir = r"D:\projects\ProjectAnimation\Backrooms_Textures"
os.makedirs(output_tex_dir, exist_ok=True)

with open(glb_path, "rb") as f:
    magic, version, length = struct.unpack("<4sII", f.read(12))
    print(f"Magic: {magic}, Version: {version}, Length: {length} bytes ({length / (1024*1024):.2f} MB)")
    
    # Read chunk 0 (JSON)
    chunk0_len, chunk0_type = struct.unpack("<I4s", f.read(8))
    json_bytes = f.read(chunk0_len)
    gltf = json.loads(json_bytes.decode("utf-8"))
    
    # Read chunk 1 (BIN)
    chunk1_len, chunk1_type = struct.unpack("<I4s", f.read(8))
    bin_offset = f.tell()
    print(f"Chunk 1 type: {chunk1_type}, len: {chunk1_len}")
    
    print(f"Total Meshes: {len(gltf.get('meshes', []))}")
    print(f"Total Materials: {len(gltf.get('materials', []))}")
    print(f"Total Textures: {len(gltf.get('textures', []))}")
    print(f"Total Images: {len(gltf.get('images', []))}")
    print(f"Total Nodes: {len(gltf.get('nodes', []))}")
    
    # List nodes and names
    for i, node in enumerate(gltf.get("nodes", [])):
        print(f"Node {i}: {node.get('name')} (mesh: {node.get('mesh')})")
        
    print("\n--- MATERIALS ---")
    for i, m in enumerate(gltf.get("materials", [])):
        print(f"Material {i}: {m.get('name')}")
        print("  pbrMetallicRoughness:", m.get("pbrMetallicRoughness"))
        print("  normalTexture:", m.get("normalTexture"))
        print("  occlusionTexture:", m.get("occlusionTexture"))
        print("  emissiveTexture:", m.get("emissiveTexture"))
        print("  emissiveFactor:", m.get("emissiveFactor"))

    # Extract all images
    bufferViews = gltf.get("bufferViews", [])
    images = gltf.get("images", [])
    
    print("\n--- EXTRACTING IMAGES ---")
    for i, img in enumerate(images):
        name = img.get("name", f"image_{i}")
        mime = img.get("mimeType", "image/png")
        ext = ".png" if "png" in mime else (".jpg" if "jpeg" in mime or "jpg" in mime else ".bin")
        
        bv_idx = img.get("bufferView")
        if bv_idx is not None:
            bv = bufferViews[bv_idx]
            byte_offset = bv.get("byteOffset", 0)
            byte_len = bv.get("byteLength", 0)
            
            f.seek(bin_offset + byte_offset)
            img_data = f.read(byte_len)
            
            clean_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in name)
            out_file = os.path.join(output_tex_dir, f"{i:02d}_{clean_name}{ext}")
            with open(out_file, "wb") as img_out:
                img_out.write(img_data)
            print(f"Saved image {i} ({len(img_data)/1024:.1f} KB): {out_file}")
