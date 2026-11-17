#!/usr/bin/env python3
"""Thumbnail 1080x1920: 'NEVER LOOK OUTSIDE AT 2:17 AM' over the mom-in-the-window still (local, no credits)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
W, H = 1080, 1920
F = os.path.join(ROOT, "assets", "fonts", "Poppins-800.ttf")
bg = Image.open(os.path.join(ROOT, "assets", "hf", "16_puddle_reflection.jpg")).convert("RGB")
s = max(W / bg.width, H / bg.height) * 1.18
bg = bg.resize((int(bg.width * s), int(bg.height * s)), Image.LANCZOS)
x0 = (bg.width - W) // 2; y0 = int((bg.height - H) * 0.22)
bg = ImageEnhance.Contrast(bg.crop((x0, y0, x0 + W, y0 + H))).enhance(1.15)
# dark gradient top for text
grad = Image.new("L", (W, H))
gd = ImageDraw.Draw(grad)
for y in range(H):
    a = max(0, 1 - y / (H * 0.42)) * 235
    gd.line([(0, y), (W, y)], fill=int(a))
bg.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), grad)
# red glow ring around the mom
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse([W * 0.20, H * 0.42, W * 0.80, H * 0.80], outline=(255, 30, 30, 255), width=14)
bg.paste(glow.filter(ImageFilter.GaussianBlur(3)), (0, 0), glow.filter(ImageFilter.GaussianBlur(3)))
d = ImageDraw.Draw(bg)
def line(txt, y, size, col):
    f = ImageFont.truetype(F, size)
    d.text((W // 2, y), txt, font=f, anchor="mm", fill=col, stroke_width=max(size // 12, 6), stroke_fill=(0, 0, 0))
line("PART 2", 150, 110, (255, 38, 38))
line("DON'T LOOK AT", 300, 128, (255, 255, 255))
line("YOUR", 440, 128, (255, 255, 255))
line("REFLECTION", 590, 150, (255, 38, 38))
bg.save(os.path.join(ROOT, "output", "thumbnail_part2.png"))
print("thumbnail written")
