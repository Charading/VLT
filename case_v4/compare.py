"""Contact sheet of the three v4 variants: one row per style, the same views side by side → out/compare.jpg"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROUNDS = {"compare": ["ore", "envy", "blade"], "compare_round2": ["syrin", "velota", "icev", "deck", "brassbar"]}
NAME = sys.argv[1] if len(sys.argv) > 1 else "compare"
STYLES = ROUNDS[NAME]
VIEWS = ["iso_front_right", "side_right_low", "bottom_iso", "back_iso"]
CELL_W, CELL_H = 900, 560

font = ImageFont.truetype("arial.ttf", 34) if os.path.exists("C:/Windows/Fonts/arial.ttf") else ImageFont.load_default()
sheet = Image.new("RGB", (len(VIEWS) * CELL_W, len(STYLES) * (CELL_H + 44)), (24, 24, 26))
d = ImageDraw.Draw(sheet)
for r, s in enumerate(STYLES):
    y0 = r * (CELL_H + 44)
    d.text((12, y0 + 6), "v4 %s" % s.upper(), fill=(255, 210, 60), font=font)
    for c, v in enumerate(VIEWS):
        p = os.path.join(HERE, "out", s, "png", v + ".png")
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGB")
        im.thumbnail((CELL_W - 10, CELL_H - 10))
        sheet.paste(im, (c * CELL_W + (CELL_W - im.width) // 2, y0 + 44 + (CELL_H - im.height) // 2))
out = os.path.join(HERE, "out", NAME + ".jpg")
sheet.save(out, quality=88)
print("wrote", out)
