# Maya 3D Model & Animation Project

คลังเก็บรวบรวมโมเดลสามมิติและแอนิเมชันสำหรับรายวิชา **Computer Graphics and Animation (Section 01, Group 05)**

## สมาชิกกลุ่มและโครงสร้างไดเรกทอรี

| สมาชิก | โฟลเดอร์ประจำตัว | ขอบเขตงานที่รับผิดชอบ |
|---|---|---|
| **ธนัทภัทร พรหมทอง (Tawan)** | [`Tawan/`](./Tawan/) | Monster Character Model & Rig, Backrooms Modular Architecture, Props, Lighting, Chase Animation (เฟรม 5–14) |
| **นันท์นภัส ชินศิริโชคชัย** | [`Nannapas/`](./Nannapas/) | Main Character (Charlie), Location Bedroom & Furniture, Animation (เฟรม 1–4) |
| **วสวัตติ์ เนตร์พันธ์** | `Wasawat/` | Old Man Model & Rig, Train Station Environment & Props, Walking Cycle & Jumpscare (เฟรม 15–20) |

---

## เอกสารนำเสนอและความคืบหน้าโครงการ

- **เอกสารนำเสนอความคืบหน้าล่าสุด (Week 12 - 30/09/2026):** [`docs/sec01_group05_30_09_2026.pdf`](./docs/sec01_group05_30_09_2026.pdf)
- **วิดีโอตัวอย่างแอนิเมติก (Preview Scene):** [YouTube Link](https://youtu.be/3AwjYuhbZ9c)
- **ความยาวรวมแอนิเมชัน:** 44 วินาที (20 เฟรมสตอรีบอร์ด)
- **สถานะปัจจุบัน (30 กันยายน 2569):** โมเดลหลัก 3 ตัว (Charlie, Monster, Old man) และฉากทั้ง 3 แห่ง (Bedroom, Backrooms, Train Station) ขึ้นรูปและใส่ Rigging ครบถ้วน อยู่ระหว่างการจัดแอนิเมชัน การเคลื่อนไหว จัดแสงไฟ Arnold และเตรียมเรนเดอร์

---

## รายละเอียดงานในโฟลเดอร์ `Tawan/`

- **Scenes:** ซีนสภาพแวดล้อม Backrooms, พร็อพพร้อมจัดแสงไฟ Arnold และซีนแอนิเมชันไล่ล่า (Chase Tracking Camera)
- **Monster Model:** โมเดลสามมิติ Monster ความละเอียดสูงพร้อมโครงสร้างกระดูกและระบบควบคุม (Rigging)
- **Source Images:** พื้นผิวและไฟล์เท็กซ์เจอร์ทั้งหมด (Carpet, Wallpaper, Ceiling Tiles, Monster Maps, Props OBJs)
- **Automation Scripts:** สคริปต์ Python สำหรับการจัดฉาก, สร้าง Rig, เชื่อมต่อ Material และ Headless Rendering
- **Renders & Video:** ภาพเรนเดอร์พรีวิวและวิดีโอแอนิเมชันความละเอียดสูง `Backrooms_Monster_Chase_Full.mp4`

รายละเอียดเชิงลึกและวิธีตั้งค่าโปรเจกต์ใน Autodesk Maya สามารถอ่านต่อได้ที่ [Tawan/README.md](./Tawan/README.md)
