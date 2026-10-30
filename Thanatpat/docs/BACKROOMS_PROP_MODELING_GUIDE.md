# 🏢 Backrooms Props & Scene 3D Modeling Guide (Maya Edition)
> **Project:** ProjectAnimation / Buff Blobbell Animation & Showreel  
> **Target Software:** Autodesk Maya 2024+ / Arnold Renderer (MtoA)  
> **Reference Sources:** `D:/projects/ProjectAnimation/backrooms_vr.glb`, `Meshy_AI_Buff_Blobbell_0821154423_texture_fbx`  
> **Author/Pipeline:** TAWAN-OS 3D Animation Pipeline  

---

## 📌 สรุปภาพรวมและวัตถุประสงค์ (Overview & Concept)

คู่มือนี้จัดทำขึ้นเพื่อให้ Tawan สามารถ **"ปั้นโมเดล Props และสภาพแวดล้อมสไตล์ Backrooms (Level 0 - The Lobby) ขึ้นมาใหม่ทั้งหมดใน Maya"** โดยรักษาความถูกต้องของ Topology (Quad-based, Clean Edge Flow, Support Loops สำหรับ SubD), UV Layout ที่เป็นระเบียบ และการตั้งค่า Material/Lighting ใน Arnold Renderer โดยดึง Reference สัดส่วน, รูปทรง, และดีเทลมาจากไฟล์ `backrooms_vr.glb` และแมตช์สเกลกับตัวละคร **Buff Blobbell**

```
+-------------------------------------------------------------------------------+
|                             BACKROOMS SCENE LAYOUT                            |
|                                                                               |
|   [Ceiling Fluorescent Lamps (4000K-4500K)]                                   |
|   +-----------------------------------------------------------------------+   |
|   | Acoustic Ceiling Tiles (60x60cm / 60x120cm with Water Stains)        |   |
|   +-----------------------------------------------------------------------+   |
|                                                                               |
|   [Wallpaper Wall - Mono-Yellow]                      [Exit Door & Sign]      |
|   +-------------------+                                +---------------+      |
|   |                   |    [Buff Blobbell]             | [EXIT - RED]  |      |
|   |   [Vent Prop]     |        (Center)                |               |      |
|   |   [Power Socket]  |        / \                    |   Solid Wood  |      |
|   |                   |       /   \                   |   Office Door |      |
|   +-------------------+                                +---------------+      |
|                                                                               |
|   [Office Furniture Setup]                                                    |
|   +-------------------+     +-----------------+                               |
|   | Retro Office Desk |     | 90s Armchair    |                               |
|   | & Filing Cabinet  |     | (Fabric/Vinyl)  |                               |
|   +-------------------+     +-----------------+                               |
|                                                                               |
|   +-----------------------------------------------------------------------+   |
|   | Damp Carpet Flooring (Moquette Mono-pattern, Desaturated Yellow/Ochre)|   |
|   +-----------------------------------------------------------------------+   |
+-------------------------------------------------------------------------------+
```

---

## 📏 1. ระบบหน่วยวัดและสเกลมาตรฐาน (World Scale & Grid Settings)

เพื่อให้โมเดลทั้งหมดประกอบฉากร่วมกับ **Buff Blobbell** ได้อย่างถูกต้อง ต้องตั้งค่า Working Units ใน Maya ให้เป็น **Centimeters (cm)** เสมอ:

* **Maya Preferences:** `Windows > Settings/Preferences > Preferences > Settings > Linear = Centimeter`
* **Grid Setup:** `Display > Grid [Options]`
  * Length and width: `1000.0 units`
  * Grid lines every: `100.0 units` (1 เมตร)
  * Subdivisions: `10` (ช่องละ 10 cm)

### ตารางสเกลอ้างอิงของแต่ละชิ้นงาน (Reference Dimensions)
| หมวดหมู่ (Asset) | ความกว้าง (W) | ความลึก (D) | ความสูง (H) | สเกลเปรียบเทียบกับตัวละคร |
| :--- | :--- | :--- | :--- | :--- |
| **Buff Blobbell (Character)** | ~120 cm | ~70 cm | **160 - 180 cm** | มาตรฐานความสูงของมอนสเตอร์ |
| **ผนังห้อง (Modular Wall)** | 200 / 300 cm | 15 - 20 cm | **280 - 320 cm** | สูงกว่าตัวละครประมาณ 1.5 - 1.8 เท่า |
| **แผ่นฝ้าเพดาน (Ceiling Tile)** | 60 cm | 60 cm (หรือ 120 cm) | 2 - 3 cm | ขนาดมาตรฐาน Acoustic Grid |
| **โคมไฟฟลูออเรสเซนต์ (Ceiling Lamp)** | 30 cm | 120 cm | 8 - 12 cm | ฝังแนบหรือห้อยลงมาจากฝ้า 2 cm |
| **โต๊ะทำงานไม้ (Office Desk)** | 140 - 160 cm | 70 - 80 cm | **75 cm** | ระดับเอว/สะโพกของตัวละคร |
| **เก้าอี้อาร์มแชร์ (Armchair_1)** | 85 - 90 cm | 80 - 85 cm | **85 - 90 cm** | เบาะนั่งสูงจากพื้น 42 - 45 cm |
| **ประตูหนีไฟ (Exit Door)** | 90 - 100 cm | 10 cm | **210 cm** | ประตูมาตรฐานบานเดี่ยว |
| **ช่องระบายอากาศ (Wall/Ceiling Vent)** | 40 - 60 cm | 5 cm | 30 - 40 cm | ติดตั้งสูงจากพื้น 220 cm หรือบนเพดาน |
| **เต้ารับปลั๊กไฟ (Wall Socket)** | 8.5 cm | 3 cm | 8.5 cm | ติดตั้งสูงจากพื้น 30 - 40 cm |

---

## 🔨 2. ขั้นตอนการปั้นโมเดลทีละชิ้น (Step-by-Step Modeling Guide)

---

### 🪑 ชิ้นที่ 1: เก้าอี้สำนักงานยุค 90s (90s Retro Armchair / `ArmChair_1`)
> **Vibe & Style:** เก้าอี้หุ้มเบาะผ้าหรือไวนิลทรงตัน สไตล์สำนักงานยุคเก่า ดูเทอะทะ มีความเหี่ยว/นุ่มเล็กน้อย

```
        +-------------------------+   <- Backrest (พนักพิงหลัง)
        |  .-------------------.  |
        |  |  Support Cushion  |  |
        +--+-------------------+--+
        |  |                   |  |
[Armrest]  |   [Seat Cushion]  |  [Armrest] (ที่วางแขนทรงกล่องมน)
   +----+  |  .-------------.  |  +----+
   |    |  |  |             |  |  |    |
   |    |  +--+-------------+--+  |    |
   |    |  |     Base Frame    |  |    |
   +----+  +-------------------+  +----+
             | |           | |    <- 4 Wooden / Metal Peg Legs
```

#### ขั้นตอนการปั้นใน Maya:
1. **Seat Cushion (เบาะนั่ง):**
   * สร้าง `Poly Cube` ขนาด `W: 60, D: 60, H: 15 cm` ใส่ `Subdivisions X/Y/Z = 3, 2, 3`
   * เลือกขอบนอกแล้วใช้คำสั่ง `Bevel (Ctrl + B)`: `Fraction = 0.2`, `Segments = 3`
   * ปรับ Vertex ด้านบนให้ยุบตัวลงตรงกลางเล็กน้อย (Soft Modification Tool หรือ Sculpting Tool เพื่อให้ดูเป็นเบาะที่ถูกใช้งานแล้ว)
2. **Backrest (พนักพิง):**
   * สร้าง `Poly Cube` ขนาด `W: 60, D: 15, H: 55 cm` วางทำมุมเอียงไปข้างหลัง ~7-10 องศา
   * เพิ่ม Edge Loops ตามแนวตั้งและแนวนอน ดึง Vertex ส่วนตรงกลางให้นูนรับสรีระ
3. **Armrests (ที่วางแขนซ้าย-ขวา):**
   * สร้าง `Poly Cube` ขนาด `W: 15, D: 75, H: 50 cm`
   * Extrude ด้านหน้าลงมาจรดฐาน Bevel ขอบด้านบนเพื่อความโค้งมนนุ่มนวล
   * Duplicate Special แบบ Instance (X-Scale = -1) เพื่อให้อีกข้างสมมาตร
4. **Legs (ขาเก้าอี้ 4 ขา):**
   * สร้าง `Poly Cylinder` (8-12 sides) เส้นผ่านศูนย์กลาง 4 cm สูง 15 cm เรียวเล็กลงที่ปลายด้านล่าง (Taper)
   * หมุนทำมุมกางออก 5-8 องศา เพื่อความมั่นคงทางสายตา

---

### 🏢 ชิ้นที่ 2: โต๊ะทำงานไม้ & ตู้ลิ้นชัก (Retro Wooden Office Desk / `Furniture_1`)
> **Vibe & Style:** ไม้อัดปะหน้าฟอร์ไมก้าลายไม้เข้มหรือสีวอลนัท ขอบมน ขาเหล็กกล่องดำ หรือตู้ลิ้นชักประกบข้าง

```
+===================================================+  <- Top Table (ไม้หนา 3-4 cm)
|                                                   |
+==============+                     +==============+
| [ Drawer 1 ] |                     |              |
|--------------|    [ Knee Space     |  Open Frame  |
| [ Drawer 2 ] |     ช่องวางขา ]     |   or Metal   |
|--------------|                     |    Panel     |
| [ Drawer 3 ] |                     |              |
+==============+                     +==============+
  ||        ||                         ||        ||    <- Legs / Base Plinth
```

#### ขั้นตอนการปั้นใน Maya:
1. **Desktop Slab (หน้าโต๊ะ):**
   * `Poly Cube` ขนาด `W: 150, D: 75, H: 4 cm`
   * ใช้ `Insert Edge Loop Tool` ใกล้ขอบ 0.5 cm หรือ `Bevel` ขนาดเล็กมาก (`Fraction = 0.05, Segments = 2`) เพื่อให้ขอบโต๊ะรับแสงไฮไลต์ (Specular Edge Highlight) ไม่คมกริบแบบ CG ลอยๆ
2. **Drawer Pedestal (บล็อกตู้ลิ้นชักด้านข้าง):**
   * `Poly Cube` ขนาด `W: 40, D: 70, H: 65 cm`
   * สร้างหน้าบานลิ้นชัก 3 ชั้น โดยการแยกชิ้นโมเดล (Separate Mesh) ให้มีร่องรอยต่อ (Gap 0.3 cm) เสมือนจริง
3. **Drawer Handles (มือจับลิ้นชัก):**
   * สร้างด้วย `Poly Torus` ครึ่งวง หรือ `Poly Pipe` ทรงสี่เหลี่ยมผืนผ้าโค้งสไตล์ 90s
4. **Modesty Panel & Legs (แผงปิดบังหน้าขาและขาโต๊ะ):**
   * แผ่นไม้หนา 1.8 cm เชื่อมระหว่างตู้ลิ้นชักกับขาโต๊ะฝั่งตรงข้าม

---

### 💡 ชิ้นที่ 3: โคมไฟเพดานฟลูออเรสเซนต์ (Ceiling Fluorescent Fixture / `Ceiling_Lamp`)
> **Vibe & Style:** โคมไฟรางคู่พร้อมแผงตะแกรงกันแสงสะท้อน (Louver Grille) หรือฝาครอบอะคริลิกใสลายเกล็ด

```
+=======================================================+  <- Metal Housing (กล่องเหล็กขาว)
|  +-------------------------------------------------+  |
|  |  ( )========================================( )  |  |  <- Tube 1 (หลอดนีออน T8)
|  |  ( )========================================( )  |  |  <- Tube 2 (หลอดนีออน T8)
|  +-------------------------------------------------+  |
|  [ | | | | | | | | | | | | | | | | | | | | | | | ]   |  <- Louver Blades (แผงกั้นแสง)
+=======================================================+
```

#### ขั้นตอนการปั้นใน Maya:
1. **Light Housing (ตัวถังโคม):**
   * `Poly Cube` ขนาด `W: 30, D: 120, H: 8 cm`
   * ลบ Face ด้านล่างออก แล้วใช้คำสั่ง `Extrude` ดันผนังเข้าไปข้างในเพื่อสร้างขอบเบ้าโคม
2. **Fluorescent Tubes (หลอดไฟ T8):**
   * สร้าง `Poly Cylinder` (12 sides) เส้นผ่านศูนย์กลาง `2.6 cm`, ความยาว `115 cm` จำนวน 2 หลอด
   * หัว-ท้ายใส่ขั้วพลาสติกสีเขียว/ขาว (`Socket Caps`)
3. **Grid Diffuser / Louver (ตะแกรงกรองแสง):**
   * สร้างเส้นแผงกั้นสะท้อนแสงบางๆ ด้วยแผ่น Thin Cubes เรียงเว้นระยะ 5 cm
   * *Tip สำหรับประหยัดโพลีกอน:* สามารถใช้ Texture Alpha / Normal Map แทนการปั้นตะแกรงจริงได้

---

### 🚪 ชิ้นที่ 4: ประตูหนีไฟ & ป้าย EXIT (Exit Door & Emergency Sign)
> **Vibe & Style:** ประตูไม้ตันบานทึบ มีวงกบหนา มือจับก้านโยกสเตนเลส หรือคานผลักหนีไฟ (Panic Bar) พร้อมกล่องไฟ EXIT สีแดงเหนือประตู

1. **Door Frame (วงกบประตู):**
   * `Poly Cube` เจาะช่องเปิด ขนาดภายในกว้าง 90 cm สูง 210 cm ขอบวงกบกว้าง 8 cm หนา 10 cm
   * มีร่องบังใบ (Door Stop Rebate) ลึก 1.5 cm สำหรับรับบานประตู
2. **Door Leaf (บานประตู):**
   * `Poly Cube` ขนาด `W: 88, D: 4, H: 208 cm`
3. **Hardware (อุปกรณ์ประตู):**
   * **Door Handle / Push Bar:** ท่อสเตนเลสกลม ดัดโค้งด้วย Deformer หรือ Curve Extrude
   * **Kick Plate:** แผ่นสเตนเลสกันรอยเท้าด้านล่างประตู สูง 20 cm
4. **EXIT Sign Box:**
   * กล่องไฟขนาด `W: 35, D: 8, H: 20 cm` ติดตั้งเหนือวงกบประตู 15 cm
   * ฝาหน้าเป็นแผ่นอะคริลิกสีขาวสกรีนตัวอักษร "EXIT" สีแดงสด สำหรับใส่ Emission Shader

---

### 🧱 ชิ้นที่ 5: โมดูลาร์ฉาก ผนัง-เสา-พื้น-ฝ้า (Modular Environment Kit)
> **Principle:** สร้างเป็นชิ้นส่วนประกบ (Snapping Kit) เพื่อให้ต่อขยายเขาวงกต Backrooms ได้ไร้รอยต่อ

```
[Ceiling Grid]  ----> [ 60x60 cm Tiles with T-Bar Grid ]
      |
[Wall Module]   ----> [ 200x300 cm Panel ] + [ Corner L-Wall ] + [ Column Pillar 60x60 cm ]
      |
[Baseboard Trim] ---> [ บัวเชิงผนังไม้/ยาง สูง 10 cm หนา 1.5 cm ]
      |
[Floor Module]  ----> [ 200x200 cm หรือ Single Infinite Plane with Seamless UV ]
```

1. **Wall Pieces (ชิ้นผนัง):**
   * `Wall_Straight_2m` (กว้าง 200 cm, สูง 300 cm, หนา 15 cm)
   * `Wall_Corner_90` (ผนังมุมฉาก L-Shape)
   * `Wall_T_Junction` (ผนังแยก 3 ทาง)
   * `Wall_Pillar_60` (เสากลางห้องสี่เหลี่ยม 60x60 cm)
   * *Pivot Point:* ย้าย Pivot ไปไว้ที่มุมล่างซ้าย (Bottom-Left Corner) หรือกึ่งกลางฐานล่างเสมอ เพื่อให้ใช้ Snap to Grid (`กดปุ่ม X ค้างไว้`) ต่อฉากได้ทันที
2. **Baseboard (บัวเชิงผนัง):**
   * ปั้นแนวบัวประกบด้านล่างผนัง สูง 10-12 cm ยื่นออกมา 1.5 cm ปาดมุมบน 45 องศา
3. **Ceiling Grid & Tiles:**
   * ปั้นราง T-Bar คว่ำเป็นตาราง แล้ววางแผ่น Acoustic Tile ขนาด 60x60 cm ลงไป โดยบางแผ่นทำเอียงหลุดร่องหรือหายไปเพื่อสร้างบรรยากาศหลอน

---

## 🗺️ 3. การกาง UV (UV Unwrapping & Texel Density Standards)

1. **Texel Density Consistency:**
   * รักษา Texel Density ให้อยู่ที่ **10.24 px/cm** (หรือ 1024px ต่อ 1 ตารางเมตร) สำหรับ Texture 2K/4K
2. **Straighten UV Shells:**
   * ชิ้นส่วนผนัง, ขอบโต๊ะ, วงกบประตู ให้ใช้คำสั่ง `UV Editor > Unfold > Straighten UVs` เพื่อให้ลายวอลเปเปอร์และลายไม้ไม่บิดเบี้ยว
3. **Seam Placement:**
   * ซ่อนรอยต่อ UV (Seams) ไว้ด้านล่างเก้าอี้, ด้านหลังตู้, หรือใต้บัวเชิงผนัง

---

## 🎨 4. คู่มือการจัด Material & Shader ใน Arnold (MtoA Lookdev)

ใช้ `aiStandardSurface` เป็นหัวใจหลักในการคุมเฉดสีและคุณสมบัติพื้นผิว:

| Asset Part | Shader Type | Base Color | Roughness | Specular / IOR | Emission / Extra |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Wallpaper (ผนังสีเหลืองมัสตาร์ด)** | `aiStandardSurface` | Yellowish-Ochre `#C4A661` + คราบน้ำ | `0.65 - 0.75` | IOR: `1.50` (Rough) | ใส่ Normal Map ลายผ้า/กระดาษย่น |
| **Carpet (พรมเปียกชื้น)** | `aiStandardSurface` | Muddy Yellow-Green `#7E7952` | `0.85 - 0.95` | Sheen Weight: `0.3` | ใส่ Subsurface เล็กน้อยหากต้องการความชุ่ม |
| **Desk Wood (ผิวไม้โต๊ะ)** | `aiStandardSurface` | Warm Walnut / Brown `#5C3A21` | `0.35 - 0.45` | IOR: `1.52`, Anisotropy `0.2` | Normal Map ลายเสี้ยนไม้แนวนอน |
| **Armchair Fabric (ผ้าเก้าอี้)** | `aiStandardSurface` | Muted Beige/Olive `#8A826B` | `0.80` | Sheen: `0.5` (Velvet look) | Bump Map ลายผ้าทอตาถี่ |
| **Fluorescent Tube (หลอดไฟ)** | `aiStandardSurface` | Pure White `#FFFFFF` | `0.10` | Transmission: `0.2` | **Emission Weight: `2.0 - 5.0`**, Color Temp `4200K` |
| **EXIT Acrylic Sign (ป้ายไฟทางออก)** | `aiStandardSurface` | Crimson Red `#D91414` | `0.20` | IOR: `1.49` | **Emission Weight: `3.0`** (Glows in dark) |

---

## 💡 5. การจัดแสงบรรยากาศหลอน (Backrooms Liminal Lighting)

```
                       [Ceiling Arnold Mesh Lights]
                           (Color Temp: 4200K)
                                   |
                                   v  (Direct Downward Harsh Light)
           +-----------------------------------------------+
           |                                               |
           |                  [Scene Fog]                  |
           |             (aiAtmosphereVolume)              |
           |             Density: 0.001 - 0.003            |
           |                                               |
           |                 [Buff Blobbell]               |
           |                  /           \               |
           |    [Fill Area Light]        [Bounce Floor]    |
           |    (Cool Tint 5500K)         (Warm Bounce)    |
           +-----------------------------------------------+
```

1. **Key Lighting (แสงหลัก):**
   * เปลี่ยนหลอดไฟเพดานเป็น **Arnold Mesh Light** หรือสร้าง `aiAreaLight` ทรงกระบอก/สี่เหลี่ยมแนบใต้โคมไฟ
   * ตั้งค่า **Use Color Temperature = ON**, Temperature = `4100K - 4300K` (แสงขาวอมเขียวเหลืองสไตล์ฟลูออเรสเซนต์ราคาถูก)
   * ค่า Exposure ปรับระหว่าง `8.0 - 11.0` (ขึ้นอยู่กับสเกลห้อง)
2. **Atmosphere Volume (หมอกควัน/ฝุ่นลอยในอากาศ):**
   * ไปที่ `Render Settings > Arnold Renderer > Environment > Atmosphere > Create aiAtmosphereVolume`
   * Density: `0.0015` (บางเบามาก อย่าให้หนาเกินไปจนขาวโพลน)
   * Anisotropy (G): `0.3 - 0.5` (ช่วยให้แสงจากโคมไฟพุ่งเป็นลำลงมาสวยงาม)
3. **Flicker Expression (แสงไฟกะพริบอัตโนมัติ):**
   * ใส่ Expression ที่ช่อง Intensity ของโคมไฟหลอดใดหลอดหนึ่งเพื่อความหลอน:
   ```mel
   // Maya MEL Expression for Fluorescent Flicker
   aiAreaLightShape1.intensity = 1000 + (noise(time * 15) > 0.6 ? rand(-800, 200) : 0);
   ```

---

## 🎬 6. การจัดวางตัวละคร Buff Blobbell และมุมกล้อง Showreel

1. **Composition & Staging:**
   * วาง **Buff Blobbell** ยืนเด่นอยู่กึ่งกลางทางแยก (T-Junction) หรือกำลังเดินเลี้ยวพ้นมุมเสา
   * วาง **Armchair** เอียง 45 องศาข้างโต๊ะทำงานในระยะ Mid-ground เพื่อบอกสเกลและสร้างมิติความลึก (Depth of Field)
   * วาง **Exit Door** ไว้สุดปลายทางเดินยาวด้านหลังเพื่อให้เกิดจุดนำสายตา (Leading Lines & Vanishing Point)
2. **Camera Settings:**
   * **Focal Length:** `24mm - 35mm` (Wide Angle เพื่อขับเน้นความเวิ้งว้าง อึดอัด และพื้นที่ไร้จุดสิ้นสุด) หรือ `75mm` สำหรับช็อต Cinematic Portrait ของตัวละคร
   * **Aperture Size / Depth of Field (DoF):** เปิด DoF ใน Arnold Camera Attributes โฟกัสไปที่ใบหน้า/กล้ามของ Buff Blobbell เบลอฉากหลังอย่างนุ่มนวล

---

## 🛠️ 7. Python Quick Script สำหรับ Maya (สร้างโครงสร้างห้องและไฟอัตโนมัติ)

สามารถ Copy สคริปต์นี้ไปรันใน **Maya Script Editor (Python Tab)** เพื่อสร้างบล็อกห้อง Backrooms + ไฟ Arnold อัตโนมัติ:

```python
import maya.cmds as cmds

def generate_backrooms_test_room():
    """Quick procedural blockout for Backrooms test room with Arnold lights"""
    grp_name = "Backrooms_Blockout_GRP"
    if cmds.objExists(grp_name):
        cmds.delete(grp_name)
        
    root_grp = cmds.group(empty=True, name=grp_name)
    
    # 1. Floor & Ceiling
    floor = cmds.polyPlane(name="ENV_Floor_Carpet", width=800, height=800, subdivisionsX=1, subdivisionsY=1)[0]
    ceiling = cmds.polyPlane(name="ENV_Ceiling_Tiles", width=800, height=800, subdivisionsX=1, subdivisionsY=1)[0]
    cmds.setAttr(f"{ceiling}.translateY", 300)
    cmds.setAttr(f"{ceiling}.rotateX", 180)
    
    # 2. Main Walls
    wall_back = cmds.polyCube(name="ENV_Wall_Back", width=800, height=300, depth=15)[0]
    cmds.setAttr(f"{wall_back}.translateY", 150)
    cmds.setAttr(f"{wall_back}.translateZ", -400)
    
    wall_left = cmds.polyCube(name="ENV_Wall_Left", width=15, height=300, depth=800)[0]
    cmds.setAttr(f"{wall_left}.translateY", 150)
    cmds.setAttr(f"{wall_left}.translateX", -400)
    
    # 3. Middle Pillar
    pillar = cmds.polyCube(name="ENV_Center_Pillar", width=80, height=300, depth=80)[0]
    cmds.setAttr(f"{pillar}.translateY", 150)
    cmds.setAttr(f"{pillar}.translateX", 120)
    cmds.setAttr(f"{pillar}.translateZ", -100)
    
    # 4. Grouping
    cmds.parent([floor, ceiling, wall_back, wall_left, pillar], root_grp)
    
    # 5. Arnold Area Light (Fluorescent simulation)
    light_transform = cmds.createNode("transform", name="LGT_Fluorescent_AreaLight")
    light_shape = cmds.createNode("aiAreaLight", name="LGT_Fluorescent_AreaLightShape", parent=light_transform)
    cmds.setAttr(f"{light_transform}.translateY", 290)
    cmds.setAttr(f"{light_transform}.scaleX", 30)
    cmds.setAttr(f"{light_transform}.scaleY", 120)
    cmds.setAttr(f"{light_transform}.rotateX", 90)
    
    # Set Arnold light attributes
    cmds.setAttr(f"{light_shape}.aiExposure", 9.5)
    cmds.setAttr(f"{light_shape}.aiUseColorTemperature", True)
    cmds.setAttr(f"{light_shape}.aiColorTemperature", 4200) # Fluorescent Warm White
    cmds.parent(light_transform, root_grp)
    
    print("✅ Backrooms Blockout & Arnold Light generated successfully!")

# To run:
# generate_backrooms_test_room()
```

---

## 🎯 สรุปสิ่งที่ Tawan ควรลงมือทำ (Action Items)

1. **เปิด Maya** แล้วตั้ง Grid หน่วยวัดเป็น `Centimeter`
2. **ปั้น 3 Props สำคัญก่อน:**
   - [ ] **เก้าอี้อาร์มแชร์ (`ArmChair_1`)** - เน้นฟอร์มมน นุ่มนวล รับแสงสะท้อนขอบ
   - [ ] **โต๊ะทำงาน (`Furniture_1`)** - เน้นเหลี่ยมคมเป๊ะ มีร่องลิ้นชัก
   - [ ] **โคมไฟฟลูออเรสเซนต์ (`Ceiling_Lamp`)** - ใส่หลอดนีออนคู่ด้านใน
3. **Import `Meshy_AI_Buff_Blobbell_0821154423_texture.fbx`** เข้ามาเพื่อเทียบความสูง-ความกว้างกับเก้าอี้และโต๊ะ
4. **จัดฉาก & ทดสอบ Render** ด้วย Arnold RenderView เพื่อดูแสงเงาสไตล์ Liminal Space
