"""Draw 'DON'T RUN' (red paint with drips, transparent background) to sourceimages/Backrooms_Tiling/DontRun_text.png. Run with the normal python (needs Pillow);
build_shots10_14_t09.py only loads the file because mayapy has no PIL."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = r"D:\projects\ProjectAnimation"
png = os.path.join(ROOT, "sourceimages", "Backrooms_Tiling", "DontRun_text.png")
os.makedirs(os.path.dirname(png), exist_ok=True)
W, H = 1024, 256
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
font = ImageFont.truetype(r"C:\Windows\Fonts\impact.ttf", 200)
txt = "DON'T RUN"
d = ImageDraw.Draw(img)
tw = d.textlength(txt, font=font)
pos = ((W - tw) / 2.0, 14)
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(shadow).text((pos[0] + 5, pos[1] + 6), txt, font=font, fill=(40, 0, 0, 200))
img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(3)))
d = ImageDraw.Draw(img)
d.text(pos, txt, font=font, fill=(185, 14, 14, 255))
for i, x in enumerate(range(90, W - 60, 74)):
    h = 20 + (i * 37) % 55
    d.rectangle((x, 175, x + 7, 175 + h), fill=(160, 10, 10, 235))
    d.ellipse((x - 2, 171 + h, x + 9, 183 + h), fill=(160, 10, 10, 235))
from PIL import ImageOps
img = img.rotate(180)          # the polyPlane (axis -Z) shows its texture rotated 180 degrees to the camera (checked on a test render), so pre-rotate
img.save(png)
print("saved", png, img.size)
