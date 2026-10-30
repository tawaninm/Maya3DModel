# Thanatpat - Maya 3D Model & Animation Project

**สมาชิกผู้รับผิดชอบ:** ธนัทภัทร พรหมทอง (Thanatpat)
**วิชา:** Computer Graphics and Animation (Section 01, Group 05)

folder นี้เป็น Maya project ที่เปิดใช้ได้ด้วยตัวเอง รวมซีน โมเดล texture และไฟล์ที่ซีนอ้างถึงไว้ครบ ไม่แนบวิดีโอ

## ไฟล์ที่ควรเปิดตรวจ

| งาน | ไฟล์ที่เปิด | ไฟล์ที่ซีนใช้ (อยู่ใน folder นี้ทั้งหมด) |
|---|---|---|
| Charlie v2 (Mixamo rig) | `scenes/Characters/Charlie_Mixamo_v2.mb` | `sourceimages/charlie_v2/` (4 texture), `raw_assets/mixamo/charlie_v2/` (FBX ท่าเคลื่อนไหว 9 ไฟล์) |
| Monster (Mixamo rig) | `scenes/Characters/Monster_Mixamo.mb` | `sourceimages/Meshy_AI_Buff_Blobbell_0821154423_texture_fbx/` (FBX ต้นฉบับและ texture), `sourceimages/ModelRef/` (image plane อ้างอิง), `raw_assets/mixamo/monster/` |
| Monster (ต้นฉบับและ rig รุ่นแรก) | `scenes/Monster/MonsterMain.mb`, `scenes/Monster/Monster_Rigged.mb` | texture ชุดเดียวกับข้างบน |
| Backrooms | `scenes/Backrooms/Backrooms_Env_v2.mb` | `sourceimages/Backrooms_Textures/` (27 texture) |

ซีน Backrooms อื่นในโฟลเดอร์เดียวกัน:

- `Backrooms_Furniture_Scene.mb`: ฉากพร้อมพร็อพและแสง Arnold
- `Backrooms_Chase_Storyboard_Scene.mb`, `Backrooms_Monster_Animation_Scene.mb`: ซีนแอนิเมชันไล่ล่า อ้าง `scenes/Monster/Monster_Rigged.mb`
- `Backrooms_Env_v3.mb`: รุ่นที่ใช้ในช็อต 05-14 ใช้ texture `sourceimages/Backrooms_Tiling/` อีก 3 ไฟล์ที่ **ยังไม่ได้อยู่ใน repo** (ดูหัวข้อ "สิ่งที่ยังต้องทำ")

ไม่มีไฟล์ Blender (`.blend`) ใน repo โมเดลทั้งหมดเป็น Maya (`.mb`) และ FBX/OBJ

## โครงสร้าง

```text
Thanatpat/
├── workspace.mel                 # ตั้งค่า Maya project
├── scenes/
│   ├── Characters/               # Charlie_Mixamo_v2.mb, Monster_Mixamo.mb
│   ├── Monster/                  # MonsterMain.mb, Monster_Rigged.mb
│   └── Backrooms/                # Backrooms_Env_v2/v3.mb และซีนฉาก/ไล่ล่า
├── sourceimages/
│   ├── charlie_v2/               # texture ของ Charlie v2
│   ├── Meshy_AI_Buff_Blobbell_.../  # FBX และ texture ของ Monster
│   ├── Backrooms_Textures/       # texture ผนัง พรม เพดาน พร็อพ
│   ├── Props_Export/             # OBJ/MTL ของพร็อพ (MTL อ้าง ../Backrooms_Textures/)
│   └── ModelRef/                 # ภาพอ้างอิงที่ใช้เป็น image plane
├── raw_assets/mixamo/            # FBX ที่อัปโหลด/ดาวน์โหลดจาก Mixamo (charlie, charlie_v2, monster)
├── scripts/                      # สคริปต์สร้างฉาก/rig/แสง (ใช้เครื่อง Thanatpat ไม่จำเป็นต่อการเปิดซีน)
│   ├── pipeline/                 # สคริปต์ชุดช็อต 05-14 (T01-T10)
│   └── relink_project_paths.py   # แก้ path ในซีนให้เป็น relative
├── images/                       # ภาพพรีวิวและรายงานตรวจสอบ (images/checks)
├── docs/                         # เอกสารนำเสนอและสเปก
└── archive/                      # backup ซีน, Shot WIP, ไฟล์ทดสอบ (ไม่จำเป็นต่อการตรวจ)
```

## วิธีเปิดใน Autodesk Maya

1. เปิด Maya 2024 ขึ้นไป
2. `File -> Set Project...` เลือก folder `Thanatpat`
3. `File -> Open Scene...` เลือกซีนจากตารางด้านบน
4. ถ้ามีหน้าต่างแจ้ง texture หาย: `Windows -> General Editors -> File Path Editor` แล้ว Repath ไปที่ `Thanatpat/sourceimages/`

## สิ่งที่ยังต้องทำ (Thanatpat)

1. **แก้ path ในซีน** ซีน `.mb` ทั้งหมดบันทึก path แบบ absolute `D:/projects/ProjectAnimation/...` ของเครื่อง Thanatpat เครื่องอื่นไม่มี path นี้ ให้รันบนเครื่องที่มี Maya หนึ่งครั้งแล้ว commit ซีนที่บันทึกใหม่:

   ```powershell
   mayapy Thanatpat\scripts\relink_project_paths.py            # ดูก่อนว่าจะแก้อะไร (dry run)
   mayapy Thanatpat\scripts\relink_project_paths.py --apply    # แก้จริงและบันทึกทับ
   ```

2. **เพิ่ม texture ที่ขาด** ก๊อปจาก `D:\projects\ProjectAnimation\sourceimages\Backrooms_Tiling\` มาไว้ที่ `Thanatpat/sourceimages/Backrooms_Tiling/`: `Carpet_Tile.png`, `Ceiling_Tile.png`, `Wall_Chevron.png` (ซีน `Backrooms_Env_v3.mb` ต้องใช้)

## หมายเหตุ

- สคริปต์ใน `scripts/` มี path ของเครื่อง Thanatpat (`D:\projects\ProjectAnimation`, `D:\AutoDesk\Maya2027`) ไว้รันซ้ำบนเครื่องเดิม ไม่ได้เกี่ยวกับการเปิดซีน
- วิดีโอ (playblast, showreel) ถูกเอาออกจาก repo ตามที่ตกลง ยังกู้ได้จาก git history ก่อน commit ที่จัดโครงสร้างนี้
- ซีนช็อต `Shot05.mb` อยู่ใน `archive/Shots_WIP/` ซีนช็อตรุ่นล่าสุด Shot06-14 ยังไม่ได้ถูก commit (มีเฉพาะ backup รุ่น `before_t09` ใน `archive/`)
