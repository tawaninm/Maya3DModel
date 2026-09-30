"""
=============================================================================
T06: Benchmark Render Time (Arnold GPU 1920x1080 + Denoiser)
Target: scenes/Backrooms/Backrooms_Env_v2.mb
Output:
  - images/checks/benchmark_gpu_1080p.png
  - images/checks/benchmark_report.json
=============================================================================
"""

import os
import sys
import time
import json
import subprocess
import shutil

import maya.standalone
try:
    maya.standalone.initialize(name="python")
except Exception:
    pass

import maya.cmds as cmds

SCENE_PATH = r"D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Env_v2.mb"
RENDER_EXE = r"D:\AutoDesk\Maya2027\bin\Render.exe"
OUTPUT_DIR = r"D:\projects\ProjectAnimation\images\checks"
BENCHMARK_PNG = os.path.join(OUTPUT_DIR, "benchmark_gpu_1080p.png")
REPORT_PATH = os.path.join(OUTPUT_DIR, "benchmark_report.json")


def configure_scene_for_benchmark():
    print(f"Opening scene: {SCENE_PATH}")
    cmds.file(SCENE_PATH, open=True, force=True)
    cmds.loadPlugin("mtoa", quiet=True)

    cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")

    # Set 1920x1080
    cmds.setAttr("defaultResolution.width", 1920)
    cmds.setAttr("defaultResolution.height", 1080)
    cmds.setAttr("defaultResolution.deviceAspectRatio", 1920.0 / 1080.0)

    # Set Arnold GPU (renderDevice = 1)
    if cmds.objExists("defaultArnoldRenderOptions"):
        cmds.setAttr("defaultArnoldRenderOptions.renderDevice", 1)
        cmds.setAttr("defaultArnoldRenderOptions.abortOnError", False)
        cmds.setAttr("defaultArnoldRenderOptions.abortOnLicenseFail", False)
        cmds.setAttr("defaultArnoldRenderOptions.skipLicenseCheck", True)

    # Setup OptiX Denoiser Imager
    imager_name = "aiImagerDenoiserOptix_Benchmark"
    if not cmds.objExists(imager_name):
        imager_name = cmds.createNode("aiImagerDenoiserOptix", name=imager_name)
    
    # Connect to imagers[0]
    cmds.connectAttr(f"{imager_name}.message", "defaultArnoldRenderOptions.imagers[0]", force=True)
    print(f"OptiX Denoiser configured: {imager_name} connected to imagers[0]")

    # Find CAM_Light_Test camera
    cam_name = "CAM_Light_Test"
    existing = cmds.ls(f"*{cam_name}*", type="transform")
    if existing:
        cam_node = existing[0]
        shapes = cmds.listRelatives(cam_node, shapes=True, type="camera") or []
        cam_shape = shapes[0] if shapes else (cmds.ls(type="camera") or ["CAM_Light_TestShape"])[0]
    else:
        cam_shape = cmds.ls(type="camera")[0]

    for c in (cmds.ls(type="camera") or []):
        cmds.setAttr(f"{c}.renderable", 1 if c == cam_shape else 0)

    # Save scene
    cmds.file(save=True, type="mayaBinary")
    print(f"Scene configured and saved: 1920x1080, Arnold GPU, OptiX Denoiser enabled.")
    return cam_shape


def run_benchmark(cam_shape):
    out_dir = os.path.dirname(BENCHMARK_PNG)
    base_name = os.path.splitext(os.path.basename(BENCHMARK_PNG))[0]
    os.makedirs(out_dir, exist_ok=True)

    # UTF-8 safe stdout
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    # If already rendered and reported
    if os.path.exists(REPORT_PATH) and os.path.exists(BENCHMARK_PNG):
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            saved_report = json.load(f)
        duration = saved_report["duration_seconds"]
        decision = saved_report["decision_Q6"]
        file_size_mb = saved_report["image_size_mb"]
        print("\n" + "=" * 60)
        print("T06 BENCHMARK DEFINITION OF DONE REPORT (EXISTING RUN)")
        print("=" * 60)
        print(f"1. Arnold GPU 1920x1080 + denoiser 1 frame: {duration:.2f} seconds per frame")
        print(f"2. Decision based on Q6: {decision}")
        print(f"   Benchmark image size: {file_size_mb:.3f} MB (<= 5 MB: {file_size_mb <= 5.0})")
        print(f"   Report file: {REPORT_PATH}")
        print("=" * 60)
        return duration, decision

    cmd = [
        RENDER_EXE,
        "-r", "arnold",
        "-cam", cam_shape,
        "-s", "1",
        "-e", "1",
        "-x", "1920",
        "-y", "1080",
        "-rd", out_dir,
        "-im", base_name,
        "-of", "png",
        "-ai:device", "1",   # GPU
        "-ai:alf", "false",  # Abort on license fail = false
        "-ai:slc", "true",   # Skip license check = true
        "-ai:aerr", "false", # Abort on error = false
        SCENE_PATH
    ]

    print("\n" + "=" * 60)
    print("STARTING ARNOLD GPU BENCHMARK (1 FRAME 1920x1080 + OPTIX DENOISER)")
    print("=" * 60)
    print(f"Command: {' '.join(cmd)}")

    start_time = time.perf_counter()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.perf_counter()
    render_duration = end_time - start_time

    print(f"Render returncode: {result.returncode}")
    print(f"Total benchmark elapsed time: {render_duration:.2f} seconds")

    if result.stdout:
        print("Render stdout tail:", result.stdout[-500:])
    if result.stderr:
        print("Render stderr tail:", result.stderr[-500:])

    # Locate generated image
    found_image = None
    if os.path.exists(BENCHMARK_PNG):
        found_image = BENCHMARK_PNG
    else:
        candidates = [os.path.join(out_dir, f) for f in os.listdir(out_dir) if f.startswith(base_name)]
        if candidates:
            latest = max(candidates, key=os.path.getmtime)
            if latest != BENCHMARK_PNG:
                shutil.copyfile(latest, BENCHMARK_PNG)
            found_image = BENCHMARK_PNG
        else:
            default_img_dir = r"D:\projects\ProjectAnimation\images"
            for root, dirs, files in os.walk(default_img_dir):
                for f in files:
                    if f.startswith(base_name) and f.endswith(".png"):
                        src = os.path.join(root, f)
                        shutil.copyfile(src, BENCHMARK_PNG)
                        found_image = BENCHMARK_PNG
                        break

    if not found_image or not os.path.exists(found_image):
        raise FileNotFoundError(f"Benchmark rendered image not found at {BENCHMARK_PNG}")

    file_size_mb = os.path.getsize(BENCHMARK_PNG) / (1024 * 1024)
    print(f"Benchmark image created: {BENCHMARK_PNG} ({file_size_mb:.3f} MB)")

    # Decision rule Q6:
    # If <= 60 seconds: Arnold for all shots
    # If > 60 seconds: Hardware 2.0 for Shots 05, 13, 14
    is_under_60 = render_duration <= 60.0
    if is_under_60:
        decision = "Arnold สำหรับทุกช็อต (เวลาไม่เกิน 60 วินาทีต่อเฟรม)"
    else:
        decision = "ช็อต 05, 13, 14 ใช้ Hardware 2.0 ส่วนช็อตอื่นใช้ Arnold (เวลาเกิน 60 วินาทีต่อเฟรม)"

    report = {
        "renderer": "Arnold GPU",
        "render_device": 1,
        "resolution": "1920x1080",
        "denoiser": "OptiX (aiImagerDenoiserOptix)",
        "duration_seconds": round(render_duration, 2),
        "duration_under_60s": is_under_60,
        "decision_Q6": decision,
        "image_path": BENCHMARK_PNG,
        "image_size_mb": round(file_size_mb, 3)
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("T06 BENCHMARK DEFINITION OF DONE REPORT")
    print("=" * 60)
    try:
        print(f"1. Arnold GPU 1920x1080 + denoiser 1 frame: {render_duration:.2f} วินาทีต่อเฟรม")
        print(f"2. การตัดสินใจตามกฎ Q6: {decision}")
    except UnicodeEncodeError:
        print(f"1. Arnold GPU 1920x1080 + denoiser 1 frame: {render_duration:.2f} seconds per frame")
        print(f"2. Decision based on Q6: {decision.encode('ascii', 'replace').decode('ascii')}")
    print(f"   Benchmark image size: {file_size_mb:.3f} MB (<= 5 MB: {file_size_mb <= 5.0})")
    print(f"   Report file: {REPORT_PATH}")
    print("=" * 60)

    return render_duration, decision


def main():
    cam_shape = configure_scene_for_benchmark()
    duration, decision = run_benchmark(cam_shape)
    return 0


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
