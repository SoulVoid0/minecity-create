"""Render front (south) elevations of generated blueprints to PNG for quick visual review."""
import hashlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import buildings, compat

COLORS = {"glass": (150, 200, 230), "concrete": None, "light": (255, 240, 170), "lantern": (255, 220, 120),
          "froglight": (250, 235, 220), "air": None}

def color(name):
    n = name.split(":")[1]
    if "glass" in n: return (140, 190, 225)
    if "lantern" in n or "froglight" in n: return (255, 230, 150)
    if "black_concrete" in n: return (30, 30, 35)
    if "white_concrete" in n or "quartz" in n: return (235, 235, 235)
    if "light_gray" in n: return (170, 170, 170)
    if "gray_concrete" in n or "andesite" in n: return (110, 110, 115)
    if "limestone" in n: return (215, 205, 180)
    if "iron" in n or "girder" in n: return (90, 95, 100)
    h = hashlib.md5(n.encode()).digest(); return (80 + h[0] % 120, 80 + h[1] % 120, 80 + h[2] % 120)

def render(b, px=6):
    img = Image.new("RGB", (b.sx * px, b.sy * px), (35, 40, 55))
    d = ImageDraw.Draw(img)
    for x in range(b.sx):
        for y in range(b.sy):
            for z in range(b.sz - 1, -1, -1):
                name = b.get(x, y, z)[0]
                if name.startswith("structurize") or name == "minecraft:air": continue
                c = color(name); shade = 0.6 + 0.4 * (z / max(1, b.sz - 1))
                c = tuple(int(v * shade) for v in c)
                d.rectangle((x * px, (b.sy - 1 - y) * px, x * px + px - 1, (b.sy - y) * px - 1), fill=c)
                break
    return img

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "previews"
    os.makedirs(out, exist_ok=True)
    tiles = []
    for name, fn in buildings.ALL.items():
        for lvl in (1, 3, 5):
            tiles.append((f"{name}{lvl}", render(fn(lvl))))
    w = sum(t.width for _, t in tiles) + 10 * len(tiles); h = max(t.height for _, t in tiles) + 20
    sheet = Image.new("RGB", (w, h), (20, 22, 30)); d = ImageDraw.Draw(sheet); x = 5
    for label, t in tiles:
        sheet.paste(t, (x, h - t.height - 5)); d.text((x, 2), label, fill=(255, 255, 255)); x += t.width + 10
    sheet.save(os.path.join(out, "elevations.png")); print(os.path.join(out, "elevations.png"))
