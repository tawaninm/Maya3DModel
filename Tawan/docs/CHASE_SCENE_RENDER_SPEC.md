# CHASE SCENE RENDER & ANIMATIC SPECIFICATION
**โครงการ**: Backrooms Monster Chase Animation (ProjectAnimation)  
**ฉากเป้าหมาย**: [Backrooms_Chase_Storyboard_Scene.mb](file:///D:/projects/ProjectAnimation/scenes/Backrooms/Backrooms_Chase_Storyboard_Scene.mb)  
**อ้างอิงสตอรี่บอร์ด**: [ProjectDetailPhase2.pdf](file:///D:/projects/ProjectAnimation/docs/ProjectDetailPhase2.pdf) (Frame 12 - 13)  
**สถานะการตัดสินใจ**: ผ่านการตรวจรับรอง (1B, 2A, 3A)

---

## 1. วัตถุประสงค์และขอบเขต (Scope & Objectives)
สร้างและเรนเดอร์ช็อตฉากไล่ล่าในโถงทางเดิน Backrooms จำนวน 2 ช็อตหลัก (120 เฟรม หรือ 5 วินาที ที่ 24 fps) เพื่อใช้เป็นแอนิเมติกส่งตรวจความต่อเนื่องของมุมกล้องและจังหวะเวลา:
1. **Frame 12 (Shot 12)**: Dutch Turn Look-Back (กล้องมุมเอียง 14 องศา เล็งย้อนหลังเห็น Monster วิ่งเข้าหาตัวเอกระยะประชิด)
2. **Frame 13 (Shot 13)**: Dynamic Sprint Chase (กล้องเคลื่อนที่เร็วขนานและตามหลังตัวเอก Cube เห็นทั้ง Cube และ Monster วิ่งกวดตามมา)

---

## 2. ข้อมูลจำเพาะทางเทคนิค (Technical Specifications)

### 2.1 ตัวละครจำลอง (Character Proxy)
- **โหนด**: `MainChar_Proxy_Cube`
- **สัดส่วน**: กว้าง 45 ซม., ลึก 30 ซม., สูง 170 ซม.
- **จุดหมุน (Pivot)**: อยู่ที่ฐานล่างสุดของเท้า (Y = -85 เทียบกับจุดกึ่งกลาง) วางระนาบพื้นพรม Backrooms พอดีที่ Y = 73.1
- **วัสดุ**: `aiStandardSurface` สีฟ้า Cyan Blue (`baseColor`: 0.1, 0.5, 0.85, `roughness`: 0.4)
- **แอนิเมชัน**: วิ่งจาก Z = -210 ไปยัง +60 พร้อมโน้มตัวไปข้างหน้า RotateX = -12 องศา และกระดกขึ้นลงเป็นรอบก้าวทุก 15 เฟรม

### 2.2 โมเดลปีศาจ (Monster)
- **โหนดอ้างอิง**: `Monster_Rigged.mb` (Buff Blobbell)
- **แอนิเมชัน**: วิ่งไล่ตามหลังจาก Z = -350 ไปยัง -80 พร้อมสวิงแขนและรอบขาก้าวตรงจังหวะ

### 2.3 กล้องสตอรี่บอร์ด (Storyboard Cameras)
- **Cam_Shot12_DutchTurn**: ทางยาวโฟกัส 30 มม., มุมเอียง Roll Z = 14 องศา, หมุนมองย้อนกลับ Rotate Y = -168 องศา
- **Cam_Shot13_ChaseRunning**: ทางยาวโฟกัส 24 มม., ตำแหน่งเยื้องข้างและตามหลังตัวเอก เล็งมองตามทางเดินโถงวอลเปเปอร์เหลือง

---

## 3. สถาปัตยกรรมการเรนเดอร์ (Render Pipeline: 1B + 3A)

### 3.1 ลำดับขั้นที่ 1: แอนิเมติกความเร็วสูง (Animatic Delivery via Maya Hardware 2.0)
- **เป้าหมาย**: ตรวจสอบจังหวะเวลาและการเคลื่อนไหวทั้ง 120 เฟรมโดยไม่มีลายน้ำ
- **เอนจิน**: Maya Hardware 2.0 (`hw2`)
- **ความละเอียด**: 1920x1080 Full HD
- **ความเร็ว**: ~1 วินาทีต่อเฟรม (รวมไม่เกิน 2 นาทีต่อช็อต)
- **คำสั่งรันแบทช์**:
  ```powershell
  & "D:\AutoDesk\Maya2027\bin\Render.exe" -r hw2 -cam Cam_Shot12_DutchTurnShape1 -s 1 -e 120 -x 1920 -y 1080 -rd "D:\projects\ProjectAnimation\images\Chase_Storyboard_Renders" "D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
  & "D:\AutoDesk\Maya2027\bin\Render.exe" -r hw2 -cam Cam_Shot13_ChaseRunningShape1 -s 1 -e 120 -x 1920 -y 1080 -rd "D:\projects\ProjectAnimation\images\Chase_Storyboard_Renders" "D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
  ```

### 3.2 ลำดับขั้นที่ 2: ภาพนิ่งคุณภาพสูง (Beauty Keyframe Stills via Arnold GPU)
- **เป้าหมาย**: เรนเดอร์ภาพนิ่งเฟรมสำคัญ (เฟรม 60) ที่มีแสงตกกระทบและวัสดุสมบูรณ์
- **เอนจิน**: Arnold (`mtoa`) โหมด GPU (`-ai:device 1`)
- **การจัดการสิทธิ์**: ปิดการยกเลิกจากสิทธิ์ด้วย `-ai:alf false -ai:slc true`
- **ความละเอียด**: 960x540 (พรีวิวเร็ว) หรือ 1920x1080 (ส่งตรวจภาพนิ่ง)
- **คำสั่งรันแบทช์**:
  ```powershell
  & "D:\AutoDesk\Maya2027\bin\Render.exe" -r arnold -ai:device 1 -ai:alf false -ai:slc true -cam Cam_Shot12_DutchTurnShape1 -s 60 -e 60 -x 960 -y 540 -rd "D:\projects\ProjectAnimation\images\Chase_Storyboard_Renders" "D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
  & "D:\AutoDesk\Maya2027\bin\Render.exe" -r arnold -ai:device 1 -ai:alf false -ai:slc true -cam Cam_Shot13_ChaseRunningShape1 -s 60 -e 60 -x 960 -y 540 -rd "D:\projects\ProjectAnimation\images\Chase_Storyboard_Renders" "D:\projects\ProjectAnimation\scenes\Backrooms\Backrooms_Chase_Storyboard_Scene.mb"
  ```

### 3.3 การรวมภาพ (Single-Pass Compositing)
- ไม่ทำการแยกเลเยอร์เรนเดอร์ใน Maya
- ไฟล์ภาพหรือลำดับภาพที่ได้จะถูกนำเข้า Premiere Pro หรือ After Effects เพื่อร้อยเรียงและตัดต่อเสียงโดยตรง

---

## 4. เกณฑ์การตรวจรับงาน (Acceptance Criteria)
1. มุมกล้อง Shot 12 ต้องมีองศาเอียงชัดเจน เห็น Monster พุ่งเข้าหาในระยะกระชั้นชิดตรงตามสตอรี่บอร์ดหน้า 23
2. มุมกล้อง Shot 13 ต้องเห็นทั้งตัวเอก Cube ด้านหน้าและ Monster ด้านหลังวิ่งตามมาในระนาบสายตาเดียวกันตรงตามสตอรี่บอร์ดหน้า 24
3. ได้ไฟล์ภาพหรือลำดับภาพใน [Chase_Storyboard_Renders](file:///D:/projects/ProjectAnimation/images/Chase_Storyboard_Renders) ครบถ้วนทั้งสองมุมมอง
4. รันผ่านกระบวนการอัตโนมัติได้โดยไม่มีข้อผิดพลาด
