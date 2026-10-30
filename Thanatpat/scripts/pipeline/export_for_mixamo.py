"""
=============================================================================
T01: Export Meshes for Mixamo Auto-Rig
Target:
  - raw_assets/mixamo/monster/Monster_upload.fbx
  - raw_assets/mixamo/charlie/Charlie_upload.fbx
=============================================================================
"""

import os
import sys
import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds
import maya.mel as mel

REPO_ROOT = r"D:\projects\ProjectAnimation"
MONSTER_SRC = os.path.join(REPO_ROOT, "scenes", "Monster", "MonsterMain.mb")
CHARLIE_SRC = os.path.join(REPO_ROOT, "Nannapas", "main_char.fbx")

MONSTER_OUT = os.path.join(REPO_ROOT, "raw_assets", "mixamo", "monster", "Monster_upload.fbx")
CHARLIE_OUT = os.path.join(REPO_ROOT, "raw_assets", "mixamo", "charlie", "Charlie_upload.fbx")

MAX_FILE_SIZE_MB = 8.0


def setup_fbx_export_settings():
    cmds.loadPlugin("fbxmaya", quiet=True)
    mel.eval("FBXResetExport")
    mel.eval("FBXExportInAscii -v false")
    mel.eval('FBXExportFileVersion -v "FBX202000"')
    mel.eval('FBXExportUpAxis "y"')
    mel.eval("FBXExportScaleFactor 1.0")
    mel.eval("FBXExportAnimationOnly -v false")
    mel.eval("FBXExportBakeComplexAnimation -v false")
    mel.eval("FBXExportCameras -v false")
    mel.eval("FBXExportLights -v false")
    mel.eval("FBXExportEmbeddedTextures -v false")
    mel.eval("FBXExportSkins -v false")
    mel.eval("FBXExportShapes -v false")
    mel.eval("FBXExportConstraints -v false")


def export_monster():
    print("\n" + "=" * 60)
    print("Processing Monster for Mixamo...")
    print("=" * 60)

    cmds.file(new=True, force=True)
    cmds.file(MONSTER_SRC, open=True, force=True)

    mesh_name = "Monster_Buff_Blobbell"
    if not cmds.objExists(mesh_name):
        raise RuntimeError(f"Mesh {mesh_name} not found in {MONSTER_SRC}")

    # Remove history
    cmds.delete(mesh_name, ch=True)

    # Parent to world if inside a group
    parent = cmds.listRelatives(mesh_name, parent=True)
    if parent:
        cmds.parent(mesh_name, world=True)

    # Delete all other transforms / scene nodes except default cameras
    default_cams = ["persp", "top", "front", "side"]
    for node in cmds.ls(assemblies=True):
        if node not in default_cams and node != mesh_name:
            try:
                cmds.delete(node)
            except Exception:
                pass

    # Initial BBox
    bbox = cmds.exactWorldBoundingBox(mesh_name)
    min_y = bbox[1]
    print(f"Original Monster BBox: min Y = {min_y:.4f}, max Y = {bbox[4]:.4f}")

    # Move so feet are at Y = 0
    cmds.xform(mesh_name, ws=True, t=[0, -min_y, 0], relative=True)

    # Facing +Z: verify nose is facing +Z, freeze
    cmds.makeIdentity(mesh_name, apply=True, t=1, r=1, s=1, n=0)
    cmds.delete(mesh_name, ch=True)

    bbox_after = cmds.exactWorldBoundingBox(mesh_name)
    height = bbox_after[4] - bbox_after[1]
    print(f"Monster BBox after grounding: min Y = {bbox_after[1]:.4f}, height = {height:.4f} cm")

    faces_before = cmds.polyEvaluate(mesh_name, face=True)
    print(f"Monster faces: {faces_before}")

    os.makedirs(os.path.dirname(MONSTER_OUT), exist_ok=True)
    setup_fbx_export_settings()
    cmds.select(mesh_name)
    out_escaped = MONSTER_OUT.replace("\\", "/")
    mel.eval(f'FBXExport -f "{out_escaped}" -s')

    size_mb = os.path.getsize(MONSTER_OUT) / (1024 * 1024)
    print(f"Saved Monster FBX: {MONSTER_OUT} ({size_mb:.2f} MB)")

    # PolyReduce check if > 8 MB
    if size_mb > MAX_FILE_SIZE_MB:
        print(f"Warning: Monster FBX ({size_mb:.2f} MB) exceeds {MAX_FILE_SIZE_MB} MB. Applying polyReduce...")
        reduce_node = cmds.polyReduce(mesh_name, percentage=50, keepBorder=True, keepHardEdge=True, ch=False)
        cmds.delete(mesh_name, ch=True)
        faces_after = cmds.polyEvaluate(mesh_name, face=True)
        print(f"Faces before: {faces_before}, after reduce: {faces_after}")
        mel.eval(f'FBXExport -f "{out_escaped}" -s')
        size_mb = os.path.getsize(MONSTER_OUT) / (1024 * 1024)
        print(f"Saved reduced Monster FBX: {size_mb:.2f} MB")

    return MONSTER_OUT


def export_charlie():
    print("\n" + "=" * 60)
    print("Processing Charlie for Mixamo...")
    print("=" * 60)

    cmds.file(new=True, force=True)
    cmds.loadPlugin("fbxmaya", quiet=True)
    cmds.file(CHARLIE_SRC, i=True)

    # Components to duplicate: body, sweater, short, shoes1, hoodie
    # hair is composed of pCube3-5 which are excluded per spec ("ไม่เอาชุดตาและ pCube3-5")
    components = ["body", "sweater", "short", "shoes1", "hoodie"]
    for comp in components:
        if not cmds.objExists(comp):
            raise RuntimeError(f"Required component '{comp}' not found in {CHARLIE_SRC}")

    dup_list = []
    for comp in components:
        d = cmds.duplicate(comp, name=f"{comp}_dup")[0]
        # Unparent to world
        p = cmds.listRelatives(d, parent=True)
        if p:
            cmds.parent(d, world=True)
        dup_list.append(d)

    # Combine into single mesh
    combined_name = "Charlie_Upload_Mesh"
    combined = cmds.polyUnite(dup_list, ch=False, name=combined_name)[0]
    cmds.delete(combined, ch=True)
    cmds.makeIdentity(combined, apply=True, t=1, r=1, s=1, n=0)

    # Delete all other objects
    default_cams = ["persp", "top", "front", "side"]
    for node in cmds.ls(assemblies=True):
        if node not in default_cams and node != combined:
            try:
                cmds.delete(node)
            except Exception:
                pass

    bbox = cmds.exactWorldBoundingBox(combined)
    min_y = bbox[1]
    height = bbox[4] - bbox[1]
    faces_before = cmds.polyEvaluate(combined, face=True)

    print(f"Charlie BBox: min Y = {min_y:.4f}, max Y = {bbox[4]:.4f}, height = {height:.4f} cm")
    print(f"Charlie faces: {faces_before}")

    os.makedirs(os.path.dirname(CHARLIE_OUT), exist_ok=True)
    setup_fbx_export_settings()
    cmds.select(combined)
    out_escaped = CHARLIE_OUT.replace("\\", "/")
    mel.eval(f'FBXExport -f "{out_escaped}" -s')

    size_mb = os.path.getsize(CHARLIE_OUT) / (1024 * 1024)
    print(f"Saved Charlie FBX: {CHARLIE_OUT} ({size_mb:.2f} MB)")

    if size_mb > MAX_FILE_SIZE_MB:
        print(f"Warning: Charlie FBX ({size_mb:.2f} MB) exceeds {MAX_FILE_SIZE_MB} MB. Applying polyReduce...")
        cmds.polyReduce(combined, percentage=50, keepBorder=True, keepHardEdge=True, ch=False)
        cmds.delete(combined, ch=True)
        faces_after = cmds.polyEvaluate(combined, face=True)
        print(f"Faces before: {faces_before}, after reduce: {faces_after}")
        mel.eval(f'FBXExport -f "{out_escaped}" -s')
        size_mb = os.path.getsize(CHARLIE_OUT) / (1024 * 1024)
        print(f"Saved reduced Charlie FBX: {size_mb:.2f} MB")

    return CHARLIE_OUT


def validate_exported_fbx(fbx_path, label):
    print("\n" + "-" * 50)
    print(f"Validating {label}: {fbx_path}")
    print("-" * 50)

    if not os.path.exists(fbx_path):
        raise FileNotFoundError(f"Exported FBX not found: {fbx_path}")

    size_bytes = os.path.getsize(fbx_path)
    size_mb = size_bytes / (1024 * 1024)
    print(f"[{label}] File size: {size_bytes} bytes ({size_mb:.3f} MB) [<= 8 MB: {size_mb <= 8.0}]")

    cmds.file(new=True, force=True)
    cmds.loadPlugin("fbxmaya", quiet=True)
    cmds.file(fbx_path, i=True)

    joints = cmds.ls(type="joint") or []
    limb_nodes = len(joints)
    deformers = cmds.ls(type=["skinCluster", "blendShape", "geometryFilter", "cluster", "wire", "lattice"]) or []
    deformer_count = len(deformers)

    print(f"[{label}] LimbNode (joints) count: {limb_nodes}")
    print(f"[{label}] Deformer count: {deformer_count}")

    meshes = cmds.ls(type="mesh") or []
    bbox = cmds.exactWorldBoundingBox(meshes)
    min_y = bbox[1]
    max_y = bbox[4]
    height = max_y - min_y

    min_y_pass = abs(min_y) <= 0.5
    print(f"[{label}] Bounding Box min Y: {min_y:.4f} (pass 0 +/- 0.5: {min_y_pass})")
    print(f"[{label}] Bounding Box height: {height:.4f} cm (min Y: {min_y:.4f}, max Y: {max_y:.4f})")

    # Binary scan check for FBX LimbNode and Deformer
    with open(fbx_path, "rb") as f:
        data = f.read()
    raw_limb_count = data.count(b"LimbNode")
    raw_deformer_count = data.count(b"Deformer")
    print(f"[{label}] Raw FBX binary LimbNode occurrences: {raw_limb_count}")
    print(f"[{label}] Raw FBX binary Deformer occurrences: {raw_deformer_count}")

    return {
        "label": label,
        "path": fbx_path,
        "size_mb": size_mb,
        "limb_nodes": limb_nodes,
        "deformers": deformer_count,
        "min_y": min_y,
        "height": height,
        "min_y_pass": min_y_pass,
        "size_pass": size_mb <= 8.0,
        "limbs_pass": limb_nodes == 0,
        "deformers_pass": deformer_count == 0,
    }


def main():
    print("=" * 60)
    print("STARTING T01 PIPELINE EXPORT FOR MIXAMO")
    print("=" * 60)

    monster_file = export_monster()
    charlie_file = export_charlie()

    m_res = validate_exported_fbx(monster_file, "Monster")
    c_res = validate_exported_fbx(charlie_file, "Charlie")

    print("\n" + "=" * 60)
    print("T01 DEFINITION OF DONE REPORT")
    print("=" * 60)
    print(f"1. Files exist and <= 8 MB:")
    print(f"   Monster: {m_res['path']} -> {m_res['size_mb']:.3f} MB (Pass: {m_res['size_pass']})")
    print(f"   Charlie: {c_res['path']} -> {c_res['size_mb']:.3f} MB (Pass: {c_res['size_pass']})")
    print(f"2. LimbNode = 0 and Deformer = 0:")
    print(f"   Monster: LimbNode = {m_res['limb_nodes']}, Deformer = {m_res['deformers']} (Pass: {m_res['limbs_pass'] and m_res['deformers_pass']})")
    print(f"   Charlie: LimbNode = {c_res['limb_nodes']}, Deformer = {c_res['deformers']} (Pass: {c_res['limbs_pass'] and c_res['deformers_pass']})")
    print(f"3. Min Y in 0 +/- 0.5 and Heights:")
    print(f"   Monster: min Y = {m_res['min_y']:.4f} cm, height = {m_res['height']:.4f} cm (Pass: {m_res['min_y_pass']})")
    print(f"   Charlie: min Y = {c_res['min_y']:.4f} cm, height = {c_res['height']:.4f} cm (Pass: {c_res['min_y_pass']})")

    all_passed = (
        m_res['size_pass'] and c_res['size_pass'] and
        m_res['limbs_pass'] and m_res['deformers_pass'] and
        c_res['limbs_pass'] and c_res['deformers_pass'] and
        m_res['min_y_pass'] and c_res['min_y_pass']
    )
    print(f"\nT01 ALL DOD CRITERIA PASSED: {all_passed}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
