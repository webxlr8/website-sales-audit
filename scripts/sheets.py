#!/usr/bin/env python3
"""Make contact sheets so you can eyeball many screenshots at once.

  python3 sheets.py long  <full_page.jpg> <out.jpg> [width=500] [segment=1000]
      -> one tall page cut into side-by-side columns (read a whole page in one image)
  python3 sheets.py grid  <out.jpg> <w> <h> <cols> <img1> <img2> ...
      -> top part of many pages in a grid (spot broken layouts fast)

Thumbnails are low-res: never report a typo or tiny detail from a sheet.
Re-check it at full size (Read the original, or shoot.py) first.
"""
import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

def long(src, out, w=500, seg=1000):
    im = Image.open(src).convert("RGB"); im = im.resize((w, int(im.height * w / im.width)))
    parts = [im.crop((0, y, w, min(y + seg, im.height))) for y in range(0, im.height, seg)]
    S = Image.new("RGB", (w * len(parts) + 6 * (len(parts) - 1), seg), "#ff00ff")
    for i, p in enumerate(parts): S.paste(p, (i * (w + 6), 0))
    S.save(out, quality=80); print(out, S.size)

def grid(out, w, h, cols, files):
    ims = []
    for f in files:
        im = Image.open(f).convert("RGB"); im = im.resize((w, int(im.height * w / im.width))); ims.append(im.crop((0, 0, w, h)))
    rows = (len(ims) + cols - 1) // cols
    S = Image.new("RGB", (cols * (w + 6), rows * (h + 6)), "#ff00ff")
    for i, im in enumerate(ims): S.paste(im, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
    S.save(out, quality=78); print(out, S.size)

if __name__ == "__main__":
    a = sys.argv
    if a[1] == "long": long(a[2], a[3], int(a[4]) if len(a) > 4 else 500, int(a[5]) if len(a) > 5 else 1000)
    else: grid(a[2], int(a[3]), int(a[4]), int(a[5]), a[6:])
