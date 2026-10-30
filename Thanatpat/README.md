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
- `archive/Backrooms_needs_Tiling_textures/Backrooms_Env_v3.mb`: รุ่นที่ใช้ในช็อต 05-14 ต้องใช้ texture `Backrooms_Tiling/` 3 ไฟล์ที่ไม่เคยถูก commit (`Carpet_Tile.png`, `Ceiling_Tile.png`, `Wall_Chevron.png`) จึงไม่ได้ส่งเป็นงานหลัก

ไม่มีไฟล์ Blender (`.blend`) ใน repo โมเดลทั้งหมดเป็น Maya (`.mb`) และ FBX/OBJ

## โครงสร้าง

```text
Thanatpat/
├── workspace.mel                 # ตั้งค่า Maya project
├── scenes/
│   ├── Characters/               # Charlie_Mixamo_v2.mb, Monster_Mixamo.mb
│   ├── Monster/                  # MonsterMain.mb, Monster_Rigged.mb
│   └── Backrooms/                # Backrooms_Env_v2.mb และซีนฉาก/ไล่ล่า
├── sourceimages/
│   ├── charlie_v2/               # texture ของ Charlie v2
│   ├── Meshy_AI_Buff_Blobbell_.../  # FBX และ texture ของ Monster
│   ├── Backrooms_Textures/       # texture ผนัง พรม เพดาน พร็อพ
│   ├── Props_Export/             # OBJ/MTL ของพร็อพ (MTL อ้าง ../Backrooms_Textures/)
│   └── ModelRef/                 # ภาพอ้างอิงที่ใช้เป็น image plane
├── raw_assets/mixamo/            # FBX ที่อัปโหลด/ดาวน์โหลดจาก Mixamo (charlie, charlie_v2, monster)
├── scripts/                      # สคริปต์สร้างฉาก/rig/แสง (ใช้เครื่อง Thanatpat ไม่จำเป็นต่อการเปิดซีน)
│   ├── pipeline/                 # สคริปต์ชุดช็อต 05-14 (T01-T10)
│   └── relink_project_paths.py   # ตัวเลือก: บันทึก path ในซีนใหม่ให้สะอาดเมื่อมี Maya
├── images/                       # ภาพพรีวิวและรายงานตรวจสอบ (images/checks)
├── docs/                         # เอกสารนำเสนอและสเปก
└── archive/                      # backup ซีน, Shot WIP, ไฟล์ทดสอบ (ไม่จำเป็นต่อการตรวจ)
```

## วิธีเปิดใน Autodesk Maya

1. เปิด Maya 2024 ขึ้นไป
2. `File -> Set Project...` เลือก folder `Thanatpat`
3. `File -> Open Scene...` เลือกซีนจากตารางด้านบน
4. ถ้ามีหน้าต่างแจ้ง texture หาย: `Windows -> General Editors -> File Path Editor` แล้ว Repath ไปที่ `Thanatpat/sourceimages/`

## สถานะ path ในซีน

ซีน `.mb` เดิมบันทึก path แบบ absolute `D:/projects/ProjectAnimation/...` ของเครื่อง Thanatpat ตอนนี้ถูกแทนที่ด้วย path แบบ relative กับ Maya project (`sourceimages/...`, `scenes/...`) ในซีนทั้ง 8 ไฟล์ใน `scenes/` ตรวจแล้วว่า path ทั้ง 142 รายการชี้ไปไฟล์ที่มีอยู่จริงใน folder นี้

- ใน path จะมีเครื่องหมาย `/` ซ้ำกันหลายตัว (เช่น `sourceimages/////charlie_v2/...`) เพราะการแก้ใช้ข้อความความยาวเท่าเดิมเพื่อไม่ให้โครงสร้างไฟล์ binary เปลี่ยน ใช้งานได้ปกติ
- ภาพอ้างอิง `ModelRef` 2 ภาพที่ใช้เป็น image plane ใน `MonsterMain.mb`, `Monster_Rigged.mb`, `Monster_Mixamo.mb` (`24.png`, `sec01_group05 (1).png`) ยังชี้ `D:/sec01_group05 (1)/` อยู่ ภาพอ้างอิงนี้ไม่ส่งผลต่อโมเดลและการเรนเดอร์
- การแก้ทำนอก Maya ยังไม่ได้ทดสอบเปิดใน Maya จริง ถ้าซีนใดเปิดไม่ได้ ให้ย้อนด้วย `git revert` ของ commit ที่แก้ path แล้วใช้ `scripts/relink_project_paths.py` บนเครื่องที่มี Maya แทน

## หมายเหตุ

- สคริปต์ใน `scripts/` มี path ของเครื่อง Thanatpat (`D:\projects\ProjectAnimation`, `D:\AutoDesk\Maya2027`) ไว้รันซ้ำบนเครื่องเดิม ไม่ได้เกี่ยวกับการเปิดซีน
- วิดีโอ (playblast, showreel) ถูกเอาออกจาก repo ตามที่ตกลง ยังกู้ได้จาก git history ก่อน commit ที่จัดโครงสร้างนี้
- ซีนช็อต `Shot05.mb` อยู่ใน `archive/Shots_WIP/` ซีนช็อตรุ่นล่าสุด Shot06-14 ยังไม่ได้ถูก commit (มีเฉพาะ backup รุ่น `before_t09` ใน `archive/`)
