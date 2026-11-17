#!/usr/bin/env python3
# Composite: contact header (top) + artwork (bottom) -> 758x1024 grayscale e-ink sleep image.
# Usage: render_scene.py <artwork.jpg> <caption> <out.png> <fontdir>
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

art_path, caption, out, FONTDIR = sys.argv[1:5]
W, H = 758, 1024
BLACK, GRAY = 0, 110
img = Image.new("L", (W, H), 255)
d = ImageDraw.Draw(img)

def F(style, size): return ImageFont.truetype(f"{FONTDIR}/Literata-{style}.ttf", size)
def center(y, text, font, fill=BLACK):
    w = d.textlength(text, font=font); d.text(((W-w)/2, y), text, font=font, fill=fill); return w

# frame
d.rectangle([8, 8, W-9, H-9], outline=BLACK, width=2)

# ---- header (contact) ----
y = 44
center(y, "My E-Reader", F("Bold", 46)); y += 66
cx = W/2
d.line([cx-64, y, cx-16, y], fill=BLACK, width=2); d.line([cx+16, y, cx+64, y], fill=BLACK, width=2)
d.polygon([(cx, y-7), (cx+7, y), (cx, y+7), (cx-7, y)], fill=BLACK); y += 34
center(y, "If found, please return to the owner.", F("Italic", 22)); y += 42
center(y, "Call / WhatsApp", F("Bold", 22)); y += 30
center(y, "+00 000 000 0000", F("Regular", 26)); y += 40
center(y, "Email", F("Bold", 22)); y += 30
center(y, "you@example.com", F("Regular", 24)); y += 46
d.line([40, y, W-40, y], fill=BLACK, width=1); y += 20

# ---- artwork (bottom) ----
area_top, area_bot = y, H - 70
aw_max_w, aw_max_h = W - 72, area_bot - area_top
art = ImageOps.autocontrast(Image.open(art_path).convert("L"), cutoff=1)
# contrast boost for e-ink
art = Image.eval(art, lambda p: 0 if p < 24 else (255 if p > 232 else int((p-24)*255/208)))
art.thumbnail((aw_max_w, aw_max_h))
ax = (W - art.width)//2; ay = area_top + (aw_max_h - art.height)//2
img.paste(art, (ax, ay))
d.rectangle([ax-2, ay-2, ax+art.width+1, ay+art.height+1], outline=BLACK, width=2)

# caption under artwork
cap_y = ay + art.height + 10
if cap_y < H - 40:
    center(cap_y, caption, F("Italic", 18), fill=GRAY)

img.save(out, "PNG", optimize=True)
import os
print("wrote", out, os.path.getsize(out), "bytes")
