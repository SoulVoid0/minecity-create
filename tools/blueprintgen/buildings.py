"""Modern City building definitions.

Each builder(level) returns a Blueprint. All levels of a hut keep the same footprint and anchor
so MineColonies can upgrade in place; only height and interior change.
Coordinates: x east, y up, z south. y=0 is the ground floor plate (tagged 'groundlevel').
"""
import kit
from bp import AIR, FILL, KEEP, Blueprint
from kit import FLOOR_H, INDUSTRIAL, OFFICE, RESIDENTIAL

ALL = {}


def building(fn):
    ALL[fn.__name__] = fn
    return fn


def _base(name, folder, sx, sy, sz):
    return Blueprint(name=name, folder=folder, sx=sx, sy=sy, sz=sz)


def _ground_tag(b: Blueprint, x=0, z=0):
    b.tag(x, 0, z, "groundlevel")


def _plaza(b: Blueprint, x1, z1, x2, z2):
    """Paved forecourt with planters, at ground level."""
    b.fill(x1, 0, z1, x2, 0, z2, "minecraft:smooth_stone")
    for x in range(x1, x2 + 1, 4):
        b.set(x, 0, z1, "minecraft:polished_andesite")


# ---------------------------------------------------------------- town hall
@building
def townhall(level):
    """Civic center: glass office tower growing 1 -> 9 floors, Create elevator from level 3."""
    floors = [1, 2, 4, 6, 9][level - 1]
    W, D = 21, 21
    sy = floors * FLOOR_H + 2 + 2  # parapet + machine room
    b = _base(f"townhall{level}", "fundamentals", W, sy, D)
    _plaza(b, 0, 16, W - 1, D - 1)
    kit.tower(b, OFFICE, 2, 2, W - 3, 15, floors, open_front=("south", 9, 11))
    b.hut(10, 1, 12, "minecolonies:blockhuttownhall", facing="south")
    _ground_tag(b, 10, 12)
    # reception desk and banners of colony color
    b.fill(8, 1, 10, 12, 1, 10, "minecraft:smooth_quartz_slab", type="bottom")
    if floors > 1:
        kit.ladder_core(b, 3, 3, 1, floors * FLOOR_H - 1, facing="south")
    if level >= 3:
        kit.elevator(b, 15, 4, 0, (floors - 1) * FLOOR_H + 4,
                     [f * FLOOR_H for f in range(floors)], door_side="south")
    # rooftop: AE2 data uplink at top levels
    if level == 5:
        top = floors * FLOOR_H
        b.set(10, top + 1, 8, "ae2:wireless_access_point", facing="up")
        b.set(10, top + 1, 9, "ae2:controller")
    return b


# ---------------------------------------------------------------- builder
@building
def builder(level):
    """Construction company: site office + materials yard that grows with level."""
    floors = [1, 1, 2, 2, 3][level - 1]
    W, D = 15, 15
    b = _base(f"builder{level}", "fundamentals", W, floors * FLOOR_H + 3, D)
    b.fill(0, 0, 0, W - 1, 0, D - 1, "minecraft:gravel" if level < 3 else "minecraft:smooth_stone")
    kit.tower(b, INDUSTRIAL, 1, 1, 9, 9, floors, open_front=("south", 4, 5))
    b.hut(5, 1, 7, "minecolonies:blockhutbuilder", facing="south")
    _ground_tag(b, 5, 7)
    b.set(2, 1, 2, "minecraft:crafting_table")
    b.set(3, 1, 2, "minecraft:barrel", facing="up", te={"id": "minecraft:barrel"})
    # yard: scaffolding stacks and a crane mast from level 4
    for i in range(min(level, 4)):
        b.set(11 + (i % 2) * 2, 1, 2 + (i // 2) * 3, "create:andesite_scaffolding")
        b.set(11 + (i % 2) * 2, 2, 2 + (i // 2) * 3, "create:andesite_scaffolding")
    if level >= 4:
        mast = floors * FLOOR_H + 2
        for y in range(1, mast + 1):
            b.set(13, y, 12, "create:metal_girder")
        for x in range(8, 14):
            b.set(x, mast, 12, "create:metal_girder")
    if floors > 1:
        kit.ladder_core(b, 2, 8, 1, floors * FLOOR_H - 1, facing="north")
    return b


# ---------------------------------------------------------------- residence / apartments
@building
def residence(level):
    """Apartment block: 2 floors per level (2 -> 10), one bed per level, elevator from level 3."""
    floors = level * 2
    W, D = 15, 15
    b = _base(f"residence{level}", "fundamentals", W, floors * FLOOR_H + 4, D)
    _plaza(b, 0, 13, W - 1, D - 1)
    kit.tower(b, RESIDENTIAL, 1, 1, W - 2, 12, floors, open_front=("south", 6, 8))
    b.hut(7, 1, 10, "minecolonies:blockhutcitizen", facing="south")
    _ground_tag(b, 7, 10)
    kit.ladder_core(b, 2, 2, 1, floors * FLOOR_H - 1, facing="south")
    # one apartment (bed + lamp + seat) per level, upper floors first so the lobby stays open
    for i in range(level):
        y = (1 + i) * FLOOR_H + 1 if floors > 1 else 1
        x = 4 + (i % 2) * 6
        b.bed(x, y, 3, facing="north", color=["white", "light_gray", "gray", "cyan", "light_blue"][i])
        b.set(x + 1, y, 3, "minecraft:lantern")
        b.set(x, y, 7, "create:white_seat")
    if level >= 3:
        kit.elevator(b, 9, 8, 0, (floors - 1) * FLOOR_H + 4,
                     [f * FLOOR_H for f in range(floors)], door_side="west", t=RESIDENTIAL)
    return b


# ---------------------------------------------------------------- warehouse
@building
def warehouse(level):
    """Logistics hub: steel hall with rack aisles (8 racks per level) and an AE2 terminal room at 5."""
    W, D = 19, 19
    floors = 1 if level < 4 else 2
    b = _base(f"warehouse{level}", "craftsmanship/storage", W, floors * FLOOR_H + 3, D)
    _plaza(b, 0, 16, W - 1, D - 1)
    kit.tower(b, INDUSTRIAL, 1, 1, W - 2, 15, floors, bay=6, open_front=("south", 8, 10))
    b.hut(9, 1, 13, "minecolonies:blockhutwarehouse", facing="south", te_id="minecolonies:warehouse")
    _ground_tag(b, 9, 13)
    racks = 8 * level
    placed = 0
    for fy in range(floors):
        for x in (3, 4, 7, 8, 11, 12, 15):
            for z in range(3, 11):
                if placed >= racks:
                    break
                for dy in (1, 2):
                    if placed >= racks:
                        break
                    b.rack(x, fy * FLOOR_H + dy, z, facing="east" if x % 2 else "west")
                    placed += 1
    if floors > 1:
        kit.ladder_core(b, 2, 14, 1, floors * FLOOR_H - 1, facing="north")
    if level == 5:
        b.set(15, 1, 13, "ae2:controller")
        b.set(16, 1, 13, "ae2:drive", facing="west")
        b.set(16, 1, 12, "ae2:chest", facing="west")
    return b


# ---------------------------------------------------------------- courier
@building
def deliveryman(level):
    """Courier depot: loading bay with Create depots and postboxes."""
    W, D = 11, 11
    b = _base(f"deliveryman{level}", "craftsmanship/storage", W, FLOOR_H + 3, D)
    b.fill(0, 0, 0, W - 1, 0, D - 1, "minecraft:smooth_stone")
    kit.tower(b, INDUSTRIAL, 1, 1, 9, 8, 1, open_front=("south", 3, 7))
    b.hut(5, 1, 6, "minecolonies:blockhutdeliveryman", facing="south")
    _ground_tag(b, 5, 6)
    for i in range(level):
        b.set(2 + i, 1, 2, "create:depot")
    b.set(1, 1, 10, "create:red_postbox", facing="south")
    return b


# ---------------------------------------------------------------- miner
@building
def miner(level):
    """Mine headframe: open shaft pit with ladder + cobble anchor, Ore Excavation drill yard later."""
    W, D = 13, 15
    under = 3
    sy = under + FLOOR_H * 2 + 3
    b = _base(f"miner{level}", "fundamentals", W, sy, D)
    g = under  # ground plate y
    for y in range(under):
        b.fill(0, y, 0, W - 1, y, D - 1, FILL)
    b.fill(0, g, 0, W - 1, g, D - 1, "minecraft:smooth_stone")
    # office
    kit.tower(b, INDUSTRIAL, 0, 9, 8, 14, 1, y0=g, open_front=("north", 3, 5))
    b.hut(4, g + 1, 12, "minecolonies:blockhutminer", facing="north")
    b.tag(4, g, 12, "groundlevel")
    for i in range(level):
        b.rack(1 + i, g + 1, 13, facing="north", variant="blockrackemptysingle")
    # shaft collar: ladder on the east face of a cobble column, open pit around it
    lx, lz = 6, 4
    for y in range(0, g + 1):
        b.set(lx - 1, y, lz, "minecraft:cobblestone")
        b.set(lx, y, lz, "minecraft:ladder", facing="east")
    b.tag(lx, g, lz, "ladder")
    b.tag(lx - 1, g, lz, "cobble")
    # headframe tower over the pit
    frame_h = 6 + level
    for (x, z) in ((3, 1), (9, 1), (3, 7), (9, 7)):
        for y in range(g + 1, min(g + frame_h, sy - 1)):
            b.set(x, y, z, "create:metal_girder")
    top = min(g + frame_h, sy - 1)
    b.fill(3, top, 1, 9, top, 7, "create:industrial_iron_block")
    b.set(6, top, 4, "create:large_cogwheel", axis="z")
    for x in range(3, 10):
        b.set(x, g + 1, 1, "minecraft:iron_bars")
        b.set(x, g + 1, 7, "minecraft:iron_bars")
    return b


ALL_LEVELS = {name: range(1, 6) for name in ALL}
