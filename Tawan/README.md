# Tawan - Maya 3D Model & Animation Project

**สมาชิกผู้รับผิดชอบ:** ธนัทภัทร พรหมทอง (Tawan)  
**วิชา:** Computer Graphics and Animation (Section 01, Group 05)  
**ขอบเขตงานที่รับผิดชอบ:**
1. **Monster Character Model & Rig:** โมเดลสามมิติตัวละคร Monster พร้อมกระดูกและคอนโทรลเลอร์ริก
2. **Backrooms Modular Architecture & Props:** สภาพแวดล้อมห้อง Backrooms พร้อมพร็อพตกแต่ง (Armchair, Retro Desk, Exit Door, Ceiling Lamps, Vents, Sockets)
3. **Materials & Lighting:** เชดเดอร์ Arnold aiStandardSurface และระบบแสงฟลูออเรสเซนต์ 4000K
4. **Chase Animation & Camera Tracking:** แอนิเมชันฉากไล่ล่าระหว่าง Monster และตัวเอก Cube พร้อมระบบกล้องติดตาม (Tracking Camera)

---

## โครงสร้างโฟลเดอร์ (Directory Structure)

```text
Tawan/
├── scenes/
│   ├── Backrooms/
│   │   ├── Backrooms_Chase_Storyboard_Scene.mb    # ซีนแอนิเมชันฉากไล่ล่าสมบูรณ์ (เฟรม 1–120)
│   │   ├── Backrooms_Furniture_Scene.mb          # ซีนสภาพแวดล้อม Backrooms และพร็อพพร้อมจัดแสง
│   │   └── Backrooms_Monster_Animation_Scene.mb  # ซีนแอนิเมชันทดสอบท่าทาง Monster
│   └── Monster/
│       ├── MonsterMain.mb                        # โมเดล Monster ต้นฉบับ (Clean Mesh)
│       └── Monster_Rigged.mb                     # โมเดล Monster พร้อมโครงสร้างกระดูกและ Rigging
├── sourceimages/
│   ├── Backrooms_Textures/                       # เท็กซ์เจอร์ผนัง พรม และฝ้าเพดาน Backrooms
│   ├── Meshy_AI_Buff_Blobbell_.../               # เท็กซ์เจอร์และโมเดล FBX ของ Monster
│   ├── Props_Export/                             # โมเดลสามมิติ OBJ/MTL ของพร็อพทั้งหมด
│   └── ModelRef/                                 # ภาพอ้างอิงสำหรับการขึ้นรูปโมเดล
├── scripts/
│   ├── render_actual_chase_mp4.py                # สคริปต์เรนเดอร์ Maya Arnold และประกอบไฟล์ MP4
│   ├── fix_mainchar_chase_rig.py                 # สคริปต์สร้าง Rig และแอนิเมชันตัวเอก (Charlie) ในฉากไล่ล่า
│   ├── setup_chase_storyboard_scene.py           # สคริปต์จัดฉากและคีย์เฟรมฉากไล่ล่า
│   ├── build_backrooms_scene.py                  # สคริปต์สร้างห้องและจัดวางสถาปัตยกรรม
│   ├── build_backrooms_lighting_scene.py         # สคริปต์จัดแสงไฟ Arnold Area Lights
│   ├── build_monster_rig.py                      # สคริปต์สร้าง Rigging สำหรับ Monster
│   ├── wire_all_textures_clean.py                # สคริปต์เชื่อมต่อ Texture Maps อัตโนมัติ
│   └── ...                                       # สคริปต์ยูทิลิตีสำหรับการตรวจสอบฉากและกล้อง
├── images/
│   ├── Monster_Chasing_Cube_f60.jpg              # ภาพนิ่งเรนเดอร์คีย์เฟรม 60 มุมมองไล่ล่า
│   ├── arnold_render_desk_preview.png            # ภาพพรีวิวเรนเดอร์โต๊ะทำงาน Arnold
│   └── arnold_render_preview.png                 # ภาพพรีวิวเรนเดอร์ Arnold
├── movies/
│   ├── Backrooms_Monster_Chase_Full.mp4          # วิดีโอฉากไล่ล่าสมบูรณ์ (1.04 MB, H.264 640x360 24fps)
│   └── Backrooms_Chase_Animatic_Full_120f.mp4    # คลิปแอนิเมติก 120 เฟรม (103 KB)
├── docs/
│   ├── sec01_group05_30_09_2026.pdf              # สไลด์นำเสนอความคืบหน้าฉบับล่าสุด (30/09/2026, 35 หน้า)
│   ├── 12_project_presentation.pdf               # สไลด์นำเสนอความคืบหน้าสัปดาห์ที่ 12
│   ├── BACKROOMS_PROP_MODELING_GUIDE.md          # สเปกและคู่มือการสร้างพร็อพ Backrooms
│   ├── CHASE_SCENE_RENDER_SPEC.md                # สเปกเทคนิคการเรนเดอร์ฉากไล่ล่า
│   ├── Develope_Plan_All.pdf                     # แผนผังการพัฒนารวมทั้งโปรเจกต์
│   ├── ProjectDetailPhase2.pdf                   # เอกสารรายละเอียดโครงงานและสตอรีบอร์ดเฟส 2
│   └── Animation_Before_final.md                 # สรุปและแผนงานแอนิเมชันก่อนไฟนอล
└── workspace.mel                                 # ไฟล์กำหนดการตั้งค่าโปรเจกต์ของ Autodesk Maya
```

---

## วิธีเปิดใช้งานใน Autodesk Maya

1. เปิดโปรแกรม **Autodesk Maya** (รองรับเวอร์ชัน 2024 ขึ้นไป)
2. ไปที่เมนู `File -> Set Project...`
3. เลือกโฟลเดอร์ `Tawan` เพื่อให้ Maya กำหนดเส้นทางโฟลเดอร์ Assets ทั้งหมดอัตโนมัติ
4. ไปที่ `File -> Open Scene...` แล้วเลือกไฟล์ซีนที่ต้องการ:
   - เปิดซีนฉากไล่ล่า: `scenes/Backrooms/Backrooms_Chase_Storyboard_Scene.mb`
   - เปิดซีนโมเดลตัวละคร: `scenes/Monster/Monster_Rigged.mb`

---

## การเรนเดอร์ด้วยสคริปต์ Python (Headless Rendering)

สามารถรันคำสั่งเรนเดอร์ผ่าน PowerShell โดยใช้ `mayapy.exe` ได้ทันที:

```powershell
& "C:\Program Files\Autodesk\Maya<Version>\bin\mayapy.exe" "scripts\render_actual_chase_mp4.py"
```
สคริปต์จะเรนเดอร์ภาพผ่าน Arnold Engine และรวมไฟล์วิดีโอ MP4 อัตโนมัติด้วย ffmpeg
