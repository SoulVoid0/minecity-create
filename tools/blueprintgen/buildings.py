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


# ================================================================ generic halls
def hall(name, folder, hut, level, theme=INDUSTRIAL, W=15, D=15, floors=1, bay=4, plaza=2, decorate=None):
    """Shared shell for workplace huts: steel/glass hall, entrance south, hut just inside."""
    b = _base(f"{name}{level}", folder, W, floors * FLOOR_H + 3, D)
    b.fill(0, 0, 0, W - 1, 0, D - 1, "minecraft:smooth_stone")
    zf = D - 1 - plaza
    cx = W // 2
    kit.tower(b, theme, 0, 0, W - 1, zf, floors, bay=bay, open_front=("south", cx - 1, cx + 1))
    b.hut(cx, 1, zf - 2, f"minecolonies:blockhut{hut}", facing="south",
          te_id="minecolonies:enchanter" if hut == "enchanter" else "minecolonies:colonybuilding")
    _ground_tag(b, cx, zf - 2)
    if floors > 1:
        kit.ladder_core(b, 1, 1, 1, floors * FLOOR_H - 1, facing="south")
    if decorate:
        decorate(b, level, 1, 1, 1, W - 2, zf - 1)
    return b


def _row(b, x1, z, n, spec, y=1, step=1, **props):
    for i in range(n):
        b.set(x1 + i * step, y, z, spec, **props)


def _furnaces(b, level, x1, z, y=1):
    _row(b, x1, z, level + 1, "minecraft:furnace", y=y, facing="south")
    for i in range(level + 1):
        b.tes[(x1 + i, y, z)] = {"id": "minecraft:furnace"}


def _register_hall(name, folder, hut=None, **kw):
    def fn(level):
        return hall(name, folder, hut or name, level, **kw)
    fn.__name__ = name
    ALL[name] = fn


# ---- craftsmanship: factories
def _sawmill(b, lvl, x1, y, z1, x2, z2):
    _row(b, x1 + 1, z1, min(lvl, 4), "create:mechanical_saw", y=y, step=2, facing="up")
    _row(b, x1 + 1, z1 + 1, min(lvl, 4), "create:shaft", y=y, step=2, axis="x")


def _smith(b, lvl, x1, y, z1, x2, z2):
    _furnaces(b, lvl, x1 + 1, z1)
    _row(b, x1 + 1, z1 + 2, min(lvl, 3), "minecraft:anvil", y=y, step=2, facing="north")
    if lvl >= 3:
        b.set(x2 - 1, y, z1, "create:mechanical_press", facing="south")
        b.set(x2 - 1, y, z1 + 1, "create:depot")


def _mason(b, lvl, x1, y, z1, x2, z2):
    _row(b, x1 + 1, z1, min(lvl + 1, 5), "minecraft:stonecutter", y=y, step=2, facing="south")


def _crusher(b, lvl, x1, y, z1, x2, z2):
    b.set(x1 + 2, y, z1 + 1, "create:crushing_wheel", axis="y")
    b.set(x1 + 4, y, z1 + 1, "create:crushing_wheel", axis="y")
    if lvl >= 3:
        b.set(x1 + 6, y, z1 + 1, "create:millstone")


def _sifter(b, lvl, x1, y, z1, x2, z2):
    _row(b, x1 + 1, z1, lvl, "minecraft:composter", y=y, step=2)


def _mechanic(b, lvl, x1, y, z1, x2, z2):
    _row(b, x1 + 1, z1, lvl, "minecraft:hopper", y=y, step=2, facing="down")
    b.set(x2 - 1, y, z1, "create:mechanical_mixer")
    b.set(x2 - 1, y + 2, z1 + 2, "create:deployer", facing="down")


def _glass(b, lvl, x1, y, z1, x2, z2):
    _furnaces(b, lvl, x1 + 1, z1)
    _row(b, x1 + 1, z1 + 2, 3, "create:tiled_glass", y=y, step=1)


def _dyer(b, lvl, x1, y, z1, x2, z2):
    _row(b, x1 + 1, z1, lvl, "minecraft:cauldron", y=y, step=2)


def _concrete(b, lvl, x1, y, z1, x2, z2):
    # mixer needs water source blocks inside the building
    for i in range(lvl):
        b.set(x1 + 1 + i * 2, y - 1, z1 + 1, "minecraft:water")
        b.set(x1 + 1 + i * 2, y, z1 + 1, "minecraft:air")
    b.set(x2 - 1, y, z1, "create:mechanical_mixer")


def _fletcher(b, lvl, x1, y, z1, x2, z2):
    _row(b, x1 + 1, z1, lvl, "minecraft:fletching_table", y=y, step=2)


def _smeltery(b, lvl, x1, y, z1, x2, z2):
    _furnaces(b, lvl + 1, x1 + 1, z1)
    b.set(x2 - 1, y, z1, "create:fluid_tank")
    b.set(x2 - 1, y + 1, z1, "create:fluid_tank")


def _baker(b, lvl, x1, y, z1, x2, z2):
    _furnaces(b, lvl, x1 + 1, z1)
    _row(b, x1 + 1, z1 + 2, 3, "minecraft:smooth_quartz_slab", y=y, type="bottom")


def _alchemist(b, lvl, x1, y, z1, x2, z2):
    _row(b, x1 + 1, z1, lvl, "minecraft:brewing_stand", y=y, step=2)
    for i in range(lvl):
        b.tes[(x1 + 1 + i * 2, y, z1)] = {"id": "minecraft:brewing_stand"}
        b.set(x1 + 1 + i * 2, y - 1, z1 + 2, "minecraft:soul_sand")
    _row(b, x1 + 1, z1 + 4, lvl, "minecraft:oak_leaves", y=y + 2, step=2, persistent=True)


for _n, _f, _deco in [
    ("sawmill", "craftsmanship/carpentry", _sawmill),
    ("fletcher", "craftsmanship/carpentry", _fletcher),
    ("blacksmith", "craftsmanship/metallurgy", _smith),
    ("mechanic", "craftsmanship/metallurgy", _mechanic),
    ("smeltery", "craftsmanship/metallurgy", _smeltery),
    ("stonemason", "craftsmanship/masonry", _mason),
    ("crusher", "craftsmanship/masonry", _crusher),
    ("sifter", "craftsmanship/masonry", _sifter),
    ("stonesmeltery", "craftsmanship/masonry", _smeltery),
    ("glassblower", "craftsmanship/luxury", _glass),
    ("dyer", "craftsmanship/luxury", _dyer),
    ("concretemixer", "craftsmanship/luxury", _concrete),
    ("baker", "craftsmanship/luxury", _baker),
    ("alchemist", "craftsmanship/luxury", _alchemist),
]:
    _register_hall(_n, _f, decorate=_deco, floors=1)


# ---- food, health, education (multi-storey civic buildings)
def _cook(b, lvl, x1, y, z1, x2, z2):
    _furnaces(b, lvl, x1 + 1, z1)
    for i in range(2 + lvl):
        x = x1 + 1 + (i % 4) * 3
        z = z1 + 4 + (i // 4) * 3
        if x <= x2 - 1 and z <= z2 - 2:
            b.set(x, y, z, "create:white_seat")
            b.tag(x, y, z, "sit")


def _hospital(b, lvl, x1, y, z1, x2, z2):
    for i in range(lvl + 1):
        b.bed(x1 + 1 + i * 2, y, z1, facing="north", color="white")


def _library(b, lvl, x1, y, z1, x2, z2):
    for i in range(lvl * 4):
        b.set(x1 + 1 + (i % 10), y + (i // 10) % 3, z1, "minecraft:bookshelf")


def _school(b, lvl, x1, y, z1, x2, z2):
    for i in range(lvl * 2):
        x = x1 + 1 + (i % 5) * 2
        z = z1 + 2 + (i // 5) * 2
        if z <= z2 - 2:
            b.set(x, y, z, "minecraft:light_blue_carpet")
            b.tag(x, y, z, "sit")


def _tavern(b, lvl, x1, y, z1, x2, z2):
    for i in range(min(lvl, 3) + 1):
        b.bed(x1 + 1 + i * 2, y, z1, facing="north", color="red")
    _cook(b, lvl, x1, y, z1 + 3, x2, z2)


for _n, _f, _deco, _fl in [
    ("cook", "fundamentals", _cook, 1),
    ("hospital", "fundamentals", _hospital, 1),
    ("tavern", "fundamentals", _tavern, 1),
    ("library", "education", _library, 2),
    ("school", "education", _school, 1),
    ("university", "education", _library, 2),
]:
    _register_hall(_n, _f, decorate=_deco, floors=_fl, theme=OFFICE, W=17, D=17)


# ---- agriculture
def _farm(b, lvl, x1, y, z1, x2, z2):
    for i in range(lvl * 2):
        b.set(x1 + 1 + i, y - 1, z1 + 1, "minecraft:farmland", moisture=7)
        b.set(x1 + 1 + i, y, z1 + 1, "minecraft:air")
    b.set(x1, y - 1, z1 + 1, "minecraft:water")


def _composter(b, lvl, x1, y, z1, x2, z2):
    for i in range(lvl):
        b.set(x1 + 1 + i * 2, y, z1, "minecolonies:barrel_block", facing="south", te={"id": "minecolonies:barrel"})


def _florist(b, lvl, x1, y, z1, x2, z2):
    for i in range(lvl * 2):
        b.set(x1 + 1 + i, y - 1, z1 + 1, "minecolonies:composted_dirt")
        b.set(x1 + 1 + i, y, z1 + 1, "minecraft:air")


def _beekeeper(b, lvl, x1, y, z1, x2, z2):
    for i in range(lvl):
        b.set(x1 + 1 + i * 2, y, z1, "minecraft:beehive", facing="south", te={"id": "minecraft:beehive"})
    _row(b, x1 + 1, z1 + 2, lvl * 2, "minecraft:cornflower", y=y)


def _pen(b, lvl, x1, y, z1, x2, z2):
    b.fill(x1, y - 1, z1, x2, y - 1, z1 + 3, "minecraft:grass_block")
    for x in range(x1, x2 + 1):
        b.set(x, y, z1 + 4, "minecraft:iron_bars")
    b.set((x1 + x2) // 2, y, z1 + 4, "minecraft:air")


def _fisher(b, lvl, x1, y, z1, x2, z2):
    b.fill(x1 + 1, y - 1, z1 + 1, x2 - 1, y - 1, z1 + 3, "minecraft:water")


def _lumber(b, lvl, x1, y, z1, x2, z2):
    _row(b, x1 + 1, z1, min(lvl, 4), "create:mechanical_saw", y=y, step=3, facing="up")


for _n, _f, _deco in [
    ("farmer", "agriculture/horticulture", _farm),
    ("composter", "agriculture/horticulture", _composter),
    ("florist", "agriculture/horticulture", _florist),
    ("beekeeper", "agriculture/husbandry", _beekeeper),
    ("chickenherder", "agriculture/husbandry", _pen),
    ("cowboy", "agriculture/husbandry", _pen),
    ("shepherd", "agriculture/husbandry", _pen),
    ("swineherder", "agriculture/husbandry", _pen),
    ("rabbithutch", "agriculture/husbandry", _pen),
    ("fisherman", "agriculture/husbandry", _fisher),
    ("lumberjack", "fundamentals", _lumber),
]:
    _register_hall(_n, _f, decorate=_deco, theme=RESIDENTIAL if "husbandry" in _f else INDUSTRIAL)


# ---- military
def _guard(b, lvl, x1, y, z1, x2, z2):
    b.bed(x1 + 1, y, z1, facing="north", color="gray")


def _archery(b, lvl, x1, y, z1, x2, z2):
    for i in range(lvl):
        b.set(x1 + 1 + i * 2, y, z1, "minecraft:target")
        b.set(x1 + 1 + i * 2, y, z1 + 5, "minecraft:polished_andesite_slab", type="bottom")
        b.tag(x1 + 1 + i * 2, y, z1 + 5, "work")
    b.set(x2 - 1, y, z1, "minecraft:glowstone")


def _academy(b, lvl, x1, y, z1, x2, z2):
    for i in range(lvl):
        b.set(x1 + 1 + i * 2, y, z1, "minecraft:hay_block", axis="y")
        b.set(x1 + 1 + i * 2, y + 1, z1, "minecraft:carved_pumpkin", facing="south")


for _n, _f, _deco, _fl in [
    ("guardtower", "military", _guard, 3),
    ("archery", "military", _archery, 1),
    ("combatacademy", "military", _academy, 1),
]:
    _register_hall(_n, _f, decorate=_deco, floors=_fl,
                   theme=INDUSTRIAL, W=11 if _n == "guardtower" else 15, D=11 if _n == "guardtower" else 15)

# ---- mystic
_register_hall("enchanter", "mystic", decorate=_library, theme=OFFICE, hut="enchanter")
ALL_LEVELS = {name: range(1, 6) for name in ALL}
