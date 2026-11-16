#!/usr/bin/env python3
# Render the lost&found sleep screen for the e-reader (758x1024, grayscale, e-ink).
import sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
FONTDIR = sys.argv[2]  # dir with Literata-*.ttf

W, H = 758, 1024
BLACK, WHITE, GRAY = 0, 255, 110
img = Image.new("L", (W, H), WHITE)
d = ImageDraw.Draw(img)

def F(style, size):
    return ImageFont.truetype(f"{FONTDIR}/Literata-{style}.ttf", size)

def center(y, text, font, fill=BLACK):
    w = d.textlength(text, font=font)
    d.text(((W - w) / 2, y), text, font=font, fill=fill)

def wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

# outer frame
d.rectangle([10, 10, W - 11, H - 11], outline=BLACK, width=3)
d.rectangle([20, 20, W - 21, H - 21], outline=BLACK, width=1)

M = 56  # content margin
y = 70

# Title
center(y, "My E-Reader", F("Bold", 54)); y += 82
# drawn ornament divider: two short rules flanking a small diamond
cx = W / 2
d.line([cx - 70, y, cx - 18, y], fill=BLACK, width=2)
d.line([cx + 18, y, cx + 70, y], fill=BLACK, width=2)
d.polygon([(cx, y - 8), (cx + 8, y), (cx, y + 8), (cx - 8, y)], fill=BLACK)
y += 44

# Contact block
center(y, "If found, please return to the owner.", F("Italic", 24)); y += 46
center(y, "Call / WhatsApp", F("Bold", 24)); y += 34
center(y, "+00 000 000 0000", F("Regular", 30)); y += 48
center(y, "Email", F("Bold", 24)); y += 34
center(y, "you@example.com", F("Regular", 28)); y += 58

# divider line
d.line([M, y, W - M, y], fill=BLACK, width=2); y += 34

# Reading list
d.text((M, y), "Currently Reading", font=F("Bold", 34), fill=BLACK); y += 58

books = [
    ("The Brothers Karamazov", "Fyodor Dostoevsky", 89),
    ("Seven Husbands of Evelyn Hugo", "Taylor Jenkins Reid", 12),
    ("Homo Deus", "Yuval Noah Harari", 3),
    ("Why Nations Fail", "Acemoglu & Robinson", 2),
    ("The Red Deal", "The Red Nation", 1),
]
tfont = F("Bold", 26)
afont = F("Italic", 21)
pfont = F("Regular", 22)
barw = 150
textw = W - 2 * M - barw - 16
for title, author, pct in books:
    tlines = wrap(title, tfont, textw)
    # title (first line) + percent bar on same baseline
    d.text((M, y), tlines[0], font=tfont, fill=BLACK)
    # progress bar on the right
    bx0, bx1 = W - M - barw, W - M
    by0 = y + 4
    by1 = by0 + 20
    d.rectangle([bx0, by0, bx1, by1], outline=BLACK, width=2)
    fillw = int((bx1 - bx0 - 4) * pct / 100)
    if fillw > 0:
        d.rectangle([bx0 + 2, by0 + 2, bx0 + 2 + fillw, by1 - 2], fill=BLACK)
    d.text((bx0, by1 + 3), f"{pct}%", font=pfont, fill=GRAY)
    y += 34
    for extra in tlines[1:]:
        d.text((M, y), extra, font=tfont, fill=BLACK); y += 32
    d.text((M + 14, y), author, font=afont, fill=GRAY); y += 40

img.save(OUT, "PNG", optimize=True)
import os
print("wrote", OUT, os.path.getsize(OUT), "bytes", img.size)
