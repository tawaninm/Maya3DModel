import json
import struct
import os

glb_path = r"D:\projects\ProjectAnimation\raw_assets\backrooms_vr.glb"

with open(glb_path, "rb") as f:
    f.read(12)
    chunk0_len, _ = struct.unpack("<I4s", f.read(8))
    gltf = json.loads(f.read(chunk0_len).decode("utf-8"))

materials = gltf.get("materials", [])
textures = gltf.get("textures", [])
images = gltf.get("images", [])

print(f"Total materials: {len(materials)}, textures: {len(textures)}, images: {len(images)}")

image_usage = {}

for i, m in enumerate(materials):
    mat_name = m.get("name", f"mat_{i}")
    pbr = m.get("pbrMetallicRoughness", {})
    if "baseColorTexture" in pbr:
        t_idx = pbr["baseColorTexture"]["index"]
        img_idx = textures[t_idx].get("source", t_idx)
        img_name = images[img_idx].get("name", f"img_{img_idx}")
        image_usage.setdefault(img_idx, []).append((mat_name, "baseColor", img_name))
    if "metallicRoughnessTexture" in pbr:
        t_idx = pbr["metallicRoughnessTexture"]["index"]
        img_idx = textures[t_idx].get("source", t_idx)
        img_name = images[img_idx].get("name", f"img_{img_idx}")
        image_usage.setdefault(img_idx, []).append((mat_name, "metallicRoughness", img_name))
    if "normalTexture" in m:
        t_idx = m["normalTexture"]["index"]
        img_idx = textures[t_idx].get("source", t_idx)
        img_name = images[img_idx].get("name", f"img_{img_idx}")
        image_usage.setdefault(img_idx, []).append((mat_name, "normal", img_name))
    if "occlusionTexture" in m:
        t_idx = m["occlusionTexture"]["index"]
        img_idx = textures[t_idx].get("source", t_idx)
        img_name = images[img_idx].get("name", f"img_{img_idx}")
        image_usage.setdefault(img_idx, []).append((mat_name, "occlusion", img_name))
    if "emissiveTexture" in m:
        t_idx = m["emissiveTexture"]["index"]
        img_idx = textures[t_idx].get("source", t_idx)
        img_name = images[img_idx].get("name", f"img_{img_idx}")
        image_usage.setdefault(img_idx, []).append((mat_name, "emissive", img_name))

for img_idx in sorted(image_usage.keys()):
    usages = image_usage[img_idx]
    types = list(set(u[1] for u in usages))
    names = list(set(u[2] for u in usages))
    mats = [u[0] for u in usages]
    print(f"Image {img_idx:02d} ({', '.join(names)}): types={types}, used in mats={mats}")
