#!/usr/bin/env python3
"""Crop, resize, compress and optionally annotate a screenshot for the report.

  python3 img.py <src.png> <dst.jpg> [--crop x0,y0,x1,y1] [--width 1400]
                 [--box x0,y0,x1,y1] [--line-y Y] [--label "text"] [--label-pos x,y] [--num N]

Coordinates are in SOURCE pixels (desktop shots are 2160px wide at 1.5x;
mobile shots are 1170px wide at 3x). --box draws a red rounded box, --line-y a
dashed red line (e.g. "content is cut off here"), --label a red pill with white text.
Use when mark.js can't reach the thing (fixed overlays, canvas, text inside images).
"""
import argparse
from PIL import Image, ImageDraw, ImageFont

R = (225, 29, 72)

def font(sz):
    for f in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        try: return ImageFont.truetype(f, sz)
        except Exception: pass
    return ImageFont.load_default()

def main():
    a = argparse.ArgumentParser()
    a.add_argument("src"); a.add_argument("dst")
    a.add_argument("--crop"); a.add_argument("--width", type=int, default=1400)
    a.add_argument("--box", action="append", default=[]); a.add_argument("--line-y", type=int)
    a.add_argument("--label"); a.add_argument("--label-pos"); a.add_argument("--num", type=int, default=0)
    o = a.parse_args()
    im = Image.open(o.src).convert("RGB"); d = ImageDraw.Draw(im); F = font(max(22, im.width // 70))
    n = o.num
    for b in o.box:
        x0, y0, x1, y1 = map(int, b.split(","))
        d.rounded_rectangle((x0, y0, x1, y1), radius=14, outline=R, width=max(4, im.width // 400))
        if n or len(o.box) > 0:
            n += 1; r = max(20, im.width // 90)
            d.ellipse((x0 - r, y0 - r, x0 + r, y0 + r), fill=R); d.text((x0, y0), str(n), font=F, fill="white", anchor="mm")
    if o.line_y is not None:
        for x in range(0, im.width, 34): d.line((x, o.line_y, x + 18, o.line_y), fill=R, width=7)
    if o.label:
        w = d.textlength(o.label, font=F)
        if o.label_pos: lx, ly = map(int, o.label_pos.split(","))
        else: lx, ly = (im.width - w) // 2, (o.line_y or im.height // 2) + 30
        d.rounded_rectangle((lx - 18, ly - 8, lx + w + 18, ly + F.size + 16), radius=12, fill=R)
        d.text((lx, ly), o.label, font=F, fill="white")
    if o.crop: im = im.crop(tuple(map(int, o.crop.split(","))))
    if im.width > o.width: im = im.resize((o.width, int(im.height * o.width / im.width)), Image.LANCZOS)
    im.save(o.dst, quality=85, optimize=True); print(o.dst, im.size)

if __name__ == "__main__":
    main()
