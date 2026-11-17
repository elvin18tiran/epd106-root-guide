#!/usr/bin/env python3
# Boot logo (758x1024) + dot loader + a simple walking-cat silhouette whose legs/tail move.
import sys, os, math
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]; FONTDIR = sys.argv[2]
W, H = 758, 1024
os.makedirs(OUT, exist_ok=True)
def F(style, size): return ImageFont.truetype(f"{FONTDIR}/Literata-{style}.ttf", size)

def draw_cat(d, cx, cy, phase):
    """Minimalist side-view cat silhouette, facing right. phase 0..3 animates legs + tail."""
    k = 1.0
    body_w, body_h = 150, 70
    # body (rounded)
    bx0, by0 = cx - body_w/2, cy - body_h/2
    bx1, by1 = cx + body_w/2, cy + body_h/2
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=30, fill=0)
    # head (front = right side)
    hx, hy, hr = bx1 - 2, cy - 18, 34
    d.ellipse([hx-hr, hy-hr, hx+hr, hy+hr], fill=0)
    # ears (two triangles on head)
    d.polygon([(hx-18, hy-hr+6), (hx-26, hy-hr-20), (hx-4, hy-hr-4)], fill=0)
    d.polygon([(hx+10, hy-hr+6), (hx+18, hy-hr-22), (hx+28, hy-hr+2)], fill=0)
    # eye (white dot on head)
    d.ellipse([hx+6, hy-8, hx+14, hy], fill=255)
    # nose
    d.polygon([(hx+hr-2, hy+4), (hx+hr+8, hy), (hx+hr+8, hy+8)], fill=0)
    # tail (curved), swishes with phase
    sw = [20, 40, 20, 0][phase % 4]
    tx, ty = bx0 + 4, cy
    d.line([tx, ty, tx-30, ty-10, tx-50, ty-40-sw, tx-44, ty-70-sw], fill=0, width=12, joint="curve")
    # legs: 4 legs, walk cycle (front pair / back pair alternate)
    leg_y = by1 - 2
    foot = 26
    # phase determines which legs are forward
    off = [6, -6, 6, -6][phase % 4]
    xs = [bx0+30, bx0+58, bx1-52, bx1-26]
    for i, lx in enumerate(xs):
        dx = off if i % 2 == 0 else -off
        d.line([lx, leg_y, lx+dx, leg_y+foot], fill=0, width=12)

def frame(i):
    img = Image.new("L", (W, H), 255); d = ImageDraw.Draw(img); cx = W/2
    # title
    t = "My E-Reader"; f = F("Bold", 58)
    d.text(((W - d.textlength(t, font=f))/2, 360), t, font=f, fill=0)
    # ornament
    y = 450
    d.line([cx-70, y, cx-18, y], fill=0, width=2); d.line([cx+18, y, cx+70, y], fill=0, width=2)
    d.polygon([(cx, y-8), (cx+8, y), (cx, y+8), (cx-8, y)], fill=0)
    # dots
    r = 7; gap = 34; x0 = cx - gap
    for j in range(3):
        x = x0 + j*gap
        d.ellipse([x-r, 520-r, x+r, 520+r], outline=0, width=2, fill=(0 if j <= i-0 and j < i+1 and j < (i+1) else 255))
    # fill dots 0..i
    for j in range(3):
        x = x0 + j*gap
        if j < (i % 4):
            d.ellipse([x-r, 520-r, x+r, 520+r], fill=0)
        else:
            d.ellipse([x-r, 520-r, x+r, 520+r], outline=0, width=2, fill=255)
    # cat
    draw_cat(d, cx, 700, i)
    return img

for i in range(4):
    frame(i).save(f"{OUT}/{i:05d}.png", "PNG", optimize=True)
print("wrote 4 frames (with cat) to", OUT)
