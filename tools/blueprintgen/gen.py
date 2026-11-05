"""Generate the Modern City style pack.

    python3 tools/blueprintgen/gen.py            # writes into src/main/resources/blueprints/moderncity/modern_city
    python3 tools/blueprintgen/gen.py --check    # also re-reads every file and validates it

Requires: pip install nbtlib pillow
"""
import argparse
import gzip
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import nbtlib  # noqa: E402

import buildings  # noqa: E402
import infrastructure  # noqa: E402
import compat  # noqa: E402
from bp import PACK_NAME  # noqa: E402

PACKS_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "src", "main", "resources", "blueprints", "moderncity"))
ROOT = os.path.join(PACKS_DIR, "modern_city")
LITE_ROOT = os.path.join(PACKS_DIR, "modern_city_lite")
DOCS = os.path.normpath(os.path.join(HERE, "..", "..", "docs"))

VERIFIED = {}
for fn in os.listdir(os.path.join(HERE, "ids")):
    ns = fn.replace("_blocks.txt", "")
    VERIFIED[ns] = set(open(os.path.join(HERE, "ids", fn)).read().split())
VERIFIED["minecolonies"] |= {"blockminecoloniesrack"}
STRUCTURIZE = {"blocksubstitution", "blocksolidsubstitution", "blockfluidsubstitution"}

CATEGORY_COLORS = {
    "fundamentals": (70, 130, 180), "craftsmanship": (205, 133, 63), "infrastructure": (90, 90, 90),
    "agriculture": (60, 160, 60), "military": (120, 30, 30), "education": (120, 80, 160),
    "decorations": (200, 180, 60), "mystic": (90, 40, 140),
}


def collect():
    bps = []
    for name, fn in buildings.ALL.items():
        for level in buildings.ALL_LEVELS[name]:
            bps.append(fn(level))
    bps.extend(infrastructure.all_blueprints())
    return bps


def validate_ids(bps):
    problems = []
    used = {}
    for b in bps:
        for (name, _props) in set(b.blocks.values()):
            ns, path = name.split(":", 1)
            used.setdefault(name, set()).add(b.path)
            if ns == "minecraft":
                continue
            if ns == "structurize":
                if path not in STRUCTURIZE:
                    problems.append(f"{b.path}: unknown structurize block {name}")
            elif ns not in VERIFIED:
                problems.append(f"{b.path}: namespace {ns} has no verified id list")
            elif path not in VERIFIED[ns]:
                problems.append(f"{b.path}: {name} is not a {ns} block in 1.21.1")
    return problems, used


def _unpack(ints, n):
    out = []
    for v in ints:
        v &= 0xFFFFFFFF
        out += [(v >> 16) & 0xFFFF, v & 0xFFFF]
    return out[:n]


def check_file(path):
    """Re-read a written blueprint the way Structurize does and sanity-check it."""
    with gzip.open(path, "rb") as fh:
        raw = fh.read()
    assert raw[:3] == b"\x0a\x00\x00", f"{path}: root must be an unnamed compound"
    tag = nbtlib.File.parse(__import__("io").BytesIO(raw))
    sx, sy, sz = int(tag["size_x"]), int(tag["size_y"]), int(tag["size_z"])
    blocks = _unpack(tag["blocks"], sx * sy * sz)
    assert len(blocks) == sx * sy * sz, path
    assert max(blocks) < len(tag["palette"]), f"{path}: palette index out of range"
    assert str(tag["palette"][0]["Name"]) == "minecraft:air"
    for te in tag["tile_entities"]:
        x, y, z = int(te["x"]), int(te["y"]), int(te["z"])
        assert 0 <= x < sx and 0 <= y < sy and 0 <= z < sz, f"{path}: TE outside bounds"
        if "blueprintDataProvider" in te:
            idx = blocks[(y * sz + z) * sx + x]
            hut = str(tag["palette"][idx]["Name"])
            assert hut.startswith("minecolonies:blockhut"), f"{path}: hut TE not on a hut block ({hut})"
            off = tag["optional_data"]["structurize"]["primary_offset"]
            assert (int(off["x"]), int(off["y"]), int(off["z"])) == (x, y, z), f"{path}: anchor mismatch"
            c1 = te["blueprintDataProvider"]["corner1"]
            assert (int(c1["x"]), int(c1["y"]), int(c1["z"])) == (-x, -y, -z), f"{path}: corner1 mismatch"
    return sx, sy, sz


def write_icons(root, folders):
    from PIL import Image, ImageDraw

    def icon(path, rgb, label, disabled=False):
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        col = tuple(int(c * 0.35 + 90) for c in rgb) if disabled else rgb
        d.rounded_rectangle((2, 2, 61, 61), 10, fill=col + (255,))
        # skyline glyph
        for i, h in enumerate((22, 36, 28, 44, 18)):
            d.rectangle((8 + i * 10, 58 - h, 15 + i * 10, 54), fill=(255, 255, 255, 230))
        d.text((6, 4), label[:2].upper(), fill=(255, 255, 255, 255))
        img.save(path)

    icon(os.path.join(root, "icon.png"), (40, 110, 170), "MC")
    for f in folders:
        rgb = CATEGORY_COLORS.get(f, (100, 100, 100))
        icon(os.path.join(root, f, "icon.png"), rgb, f)
        icon(os.path.join(root, f, "icon_disabled.png"), rgb, f, disabled=True)


def write_pack(bps, out, pack_name, check, desc):
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    for b in bps:
        b.pack_name = pack_name
        b.write(out)
    mods = sorted({m for b in bps for m in b.mods()})
    with open(os.path.join(out, "pack.json"), "w") as fh:
        json.dump({
            "name": pack_name,
            "icon": "icon.png",
            "authors": ["SoulVoid0"],
            "desc": desc,
            # Structurize skips the whole pack if any mod listed here is missing.
            "mods": ["structurize"] + mods,
            "version": 1,
            "pack-format": 1,
        }, fh, indent=2)
    write_icons(out, sorted({b.folder.split("/")[0] for b in bps}))
    if check:
        for b in bps:
            check_file(os.path.join(out, b.path))
    print(f"{pack_name}: {len(bps)} blueprints -> {out}; mods {mods}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", default=ROOT)
    args = ap.parse_args()

    bps = collect()
    problems, used = validate_ids(bps)
    if problems:
        print("\n".join(problems))
        sys.exit("unverified block ids, refusing to write")

    write_pack(bps, args.out, PACK_NAME, args.check,
               "Modular modern city: glass towers, apartments with Create elevators, steel factories, "
               "AE2 data rooms, power grid, roads and street lights.")
    lite = [compat.to_lite(b) for b in bps]
    write_pack(lite, LITE_ROOT, compat.LITE_PACK_NAME, args.check,
               "Modern City using only Minecraft + MineColonies blocks. Works in any modpack; "
               "functional Create/AE2 machinery is replaced by look-alike vanilla blocks.")

    # docs: inventory + block id manifest
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS, "BLUEPRINTS.md"), "w") as fh:
        fh.write("# Generated blueprints\n\nRegenerate with `python3 tools/blueprintgen/gen.py --check`.\n\n")
        fh.write("| File | Size (x×y×z) | Mods |\n|---|---|---|\n")
        for b in bps:
            fh.write(f"| `{b.path}` | {b.sx}×{b.sy}×{b.sz} | {', '.join(b.mods())} |\n")
    with open(os.path.join(DOCS, "BLOCK_IDS.md"), "w") as fh:
        fh.write("# Block ids used\n\nNon-vanilla ids are checked against the 1.21.1 sources "
                 "(lists in `tools/blueprintgen/ids/`) before anything is written.\n\n")
        for name in sorted(used):
            fh.write(f"- `{name}` ({len(used[name])} files)\n")


if __name__ == "__main__":
    main()
