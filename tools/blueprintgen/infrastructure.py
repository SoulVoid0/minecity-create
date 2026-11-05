"""Infrastructure blueprints: miner shaft nodes, roads, street lights, power line poles."""
import kit
from bp import AIR, FILL, Blueprint

OUT = []


def infra(fn):
    OUT.append(fn)
    return fn


# ---------------------------------------------------------------- mineshafts
# MineColonies' miner places these by file name (MineNode.NodeType). Geometry follows the
# shaft/tunnel conventions the miner AI expects (sizes, open sides, ladder + cobble column);
# materials are modern. Legend: . air, S solid-substitution, # wall, L ladder, C cobble, T light.
SHAFT_ROCK = "minecraft:polished_andesite"
SHAFT_FLOOR = "minecraft:smooth_stone"
SHAFT_LIGHT = "minecraft:lantern"

SHAFTS = {
    "minermainshaft": (9, 4, 9, [
        "######### ######### ######### ###...### ###...### ###...### ######### ####L#### ####C####",
        "#S#...#S# S.......S #.#####.# ..#...#.. ..#...#.. ..#...#.. #.#####.# S...L...S #SS#C#SS#",
        "#S#...#S# S.......S #.T.#.T.# ......... ......... ......... #.T...T.# S...L...S #SS#C#SS#",
        "######### #.......# #.......# #.......# #.......# #.......# #.......# #...L...# ####C####",
    ]),
    "minerx2left": (7, 5, 7, [
        "SSSSSSS SSSSSSS SSSSSSS ####SSS SSS#SSS SSS#SSS SSS#SSS",
        "SSSSSSS .#....S .#....S ......S .#....S .##.##S SS....S",
        "SSSSSSS .#....S .#....S ......S .#....S .##.##S SS....S",
        "SSSSSSS .#....S .#....S .#T...S .#....S .#####S SS.T..S",
        "SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS",
    ]),
    "minerx2right": (7, 5, 7, [
        "SSS#SSS SSS#SSS SSS#SSS ####SSS SSSSSSS SSSSSSS SSSSSSS",
        "S.....S .##.##S .#....S ......S .#....S .#....S SSSSSSS",
        "S.....S .##.##S .#....S ......S .#....S .#....S SSSSSSS",
        "S.....S .#####S .#.T..S T#....S .#....S .#....S SSSSSSS",
        "SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS",
    ]),
    "minerx2top": (7, 5, 7, [
        "SSSSSSS SSSSSSS SSSSSSS ####### SSSSSSS SSSSSSS SSSSSSS",
        "SSSSSSS ...#... ...#... ....... ...#... ...#... SSSSSSS",
        "SSSSSSS ...#... ...#... ....... ...#... ...#... SSSSSSS",
        "SSSSSSS ...#... ...#... ...#T.. ...#... ...#... SSSSSSS",
        "SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS",
    ]),
    "minerx3leftright": (7, 5, 7, [
        "SSS#SSS SSS#SSS SSS#SSS ####SSS SSS#SSS SSS#SSS SSS#SSS",
        "S.....S .##.##S .#....S ......S .#....S .##.##S S.....S",
        "S.....S .##.##S .#....S ......S .#....S .##.##S S.....S",
        "S.....S .#####S .#.T.#S T#...#S .#...#S .#####S S..T..S",
        "SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS",
    ]),
    "minerx3topleft": (7, 5, 7, [
        "SSS#SSS SSS#SSS SSS#SSS ####### SSSSSSS SSSSSSS SSSSSSS",
        "S.....S .##.##. .#...#. ....... .#...#. .#...#. SSSSSSS",
        "S.....S .##.##. .#...#. ....... .#...#. .#...#. SSSSSSS",
        "S..T..S .#####. .#...#. .#T..#T .#...#. .#####. SSSSSSS",
        "SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS",
    ]),
    "minerx3topright": (7, 5, 7, [
        "SSSSSSS SSSSSSS SSSSSSS ####### SSS#SSS SSS#SSS SSS#SSS",
        "SSSSSSS .#...#. .#...#. ....... .#...#. .##.##. S.....S",
        "SSSSSSS .#...#. .#...#. ....... .#...#. .##.##. S.....S",
        "SSSSSSS .#####. .#...#. .#T..#T .#...#. .#####. S..T..S",
        "SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS",
    ]),
    "minerx4": (7, 5, 7, [
        "SSS#SSS SSS#SSS SSS#SSS ####### SSS#SSS SSS#SSS SSS#SSS",
        "S.....S .#...#. .#..... ....... .#..... .#...#. S.....S",
        "S.....S .#...#. .#..... ....... .#..... .#...#. S.....S",
        "S..T..S .#####. .#...#. .#T..#T .#...#. .#####. S..T..S",
        "SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS SSSSSSS",
    ]),
}


def _shaft(name, sx, sy, sz, layers):
    b = Blueprint(name=name, folder="infrastructure/mineshafts", sx=sx, sy=sy, sz=sz)
    for y, layer in enumerate(layers):
        rows = layer.split()
        assert len(rows) == sz and all(len(r) == sx for r in rows), name
        for z, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == ".":
                    b.set(x, y, z, AIR)
                elif ch == "S":
                    b.set(x, y, z, FILL)
                elif ch == "#":
                    b.set(x, y, z, SHAFT_FLOOR if y == 0 else SHAFT_ROCK)
                elif ch == "L":
                    b.set(x, y, z, "minecraft:ladder", facing="north")
                elif ch == "C":
                    b.set(x, y, z, "minecraft:cobblestone")
                elif ch == "T":
                    b.set(x, y, z, SHAFT_LIGHT)
    if name == "minermainshaft":
        # level sign the miner rewrites with the shaft depth
        msg = '{"text":"level_placeholder"}'
        from nbtlib import Byte, Compound, List, String
        b.set(4, 2, 2, "minecraft:oak_wall_sign", facing="south", te={
            "id": "minecraft:sign",
            "is_waxed": Byte(0),
            "front_text": Compound({"messages": List[String]([String(msg)] + [String('{"text":""}')] * 3),
                                    "color": String("black"), "has_glowing_text": Byte(0)}),
            "back_text": Compound({"messages": List[String]([String('{"text":""}')] * 4),
                                   "color": String("black"), "has_glowing_text": Byte(0)}),
        })
    return b


@infra
def mineshafts():
    return [_shaft(n, *spec) for n, spec in SHAFTS.items()]


# ---------------------------------------------------------------- roads
ROAD = "minecraft:black_concrete"
LINE_Y = "minecraft:yellow_concrete"
LINE_W = "minecraft:white_concrete"
WALK = "minecraft:smooth_stone"
CURB = "minecraft:polished_andesite"
T = 15  # tile size: 2 sidewalk + 11 road + 2 sidewalk
H = 8


def _road_tile(name, open_dirs, crosswalk=False, lights=True):
    b = Blueprint(name=name, folder="infrastructure/roads/modern", sx=T, sy=H, sz=T)
    b.fill(0, 0, 0, T - 1, 0, T - 1, FILL)
    b.fill(0, 1, 0, T - 1, 1, T - 1, WALK)
    b.fill(0, 2, 0, T - 1, H - 1, T - 1, AIR)
    lo, hi = 2, 12

    def road(x1, z1, x2, z2):
        b.fill(x1, 1, z1, x2, 1, z2, ROAD)

    road(lo, lo, hi, hi)
    if "n" in open_dirs: road(lo, 0, hi, lo)
    if "s" in open_dirs: road(lo, hi, hi, T - 1)
    if "w" in open_dirs: road(0, lo, lo, hi)
    if "e" in open_dirs: road(hi, lo, T - 1, hi)
    # curbs on every road/sidewalk edge
    for x in range(T):
        for z in range(T):
            if b.get(x, 1, z)[0] == WALK and any(
                    0 <= x + dx < T and 0 <= z + dz < T and b.get(x + dx, 1, z + dz)[0] == ROAD
                    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                b.set(x, 1, z, CURB)
    # dashed centre lines on arms
    c = T // 2
    for z in range(T):
        if z % 4 < 2 and ((z < lo and "n" in open_dirs) or (z > hi and "s" in open_dirs)
                          or (lo <= z <= hi and len(open_dirs) == 2 and "n" in open_dirs and "s" in open_dirs)):
            b.set(c, 1, z, LINE_Y)
    for x in range(T):
        if x % 4 < 2 and ((x < lo and "w" in open_dirs) or (x > hi and "e" in open_dirs)
                          or (lo <= x <= hi and len(open_dirs) == 2 and "w" in open_dirs and "e" in open_dirs)):
            b.set(x, 1, c, LINE_Y)
    if crosswalk:
        for x in range(lo, hi + 1, 2):
            for z in range(5, 10):
                b.set(x, 1, z, LINE_W)
    if lights:
        spots = []
        if open_dirs == "ns":
            spots = [(0, c, "east"), (T - 1, c, "west")]
        elif open_dirs == "we":
            spots = [(c, 0, "south"), (c, T - 1, "north")]
        else:
            for (x, z, arm) in ((0, 0, "east"), (T - 1, 0, "west"), (0, T - 1, "east"), (T - 1, T - 1, "west")):
                if b.get(x, 1, z)[0] == WALK:
                    spots.append((x, z, arm))
        for (x, z, arm) in spots:
            kit.street_light(b, x, 2, z, arm=arm, height=4)
    return b


@infra
def roads():
    return [
        _road_tile("straight", "ns"),
        _road_tile("crosswalk", "ns", crosswalk=True),
        _road_tile("corner", "se"),
        _road_tile("tjunction", "nse"),
        _road_tile("intersection", "nsew"),
        _road_tile("deadend", "s"),
    ]


# ---------------------------------------------------------------- street furniture and power
@infra
def street_furniture():
    out = []
    lamp = Blueprint(name="streetlight", folder="infrastructure/roads/modern", sx=3, sy=7, sz=1)
    kit.street_light(lamp, 0, 0, 0, arm="east", height=5)
    out.append(lamp)

    pole = Blueprint(name="powerline_pole", folder="infrastructure/power", sx=5, sy=13, sz=3)
    pole.fill(1, 0, 0, 3, 0, 2, "minecraft:smooth_stone")
    for y in range(1, 11):
        pole.set(2, y, 1, "create:metal_girder")
    pole.fill(0, 11, 1, 4, 11, 1, "create:metal_girder")
    for x in (0, 4):
        pole.set(x, 12, 1, "createaddition:large_connector", facing="down")
    pole.set(2, 12, 1, "createaddition:large_connector", facing="down")
    out.append(pole)

    sub = Blueprint(name="substation", folder="infrastructure/power", sx=7, sy=5, sz=7)
    sub.fill(0, 0, 0, 6, 0, 6, "minecraft:smooth_stone")
    for (x, z) in kit._perimeter(0, 0, 6, 6):
        sub.set(x, 1, z, "minecraft:iron_bars")
        sub.set(x, 2, z, "minecraft:iron_bars")
    for x in (2, 4):
        sub.set(x, 1, 3, "createaddition:modular_accumulator")
        sub.set(x, 2, 3, "createaddition:large_connector", facing="down")
    sub.set(3, 1, 3, "createaddition:redstone_relay")
    out.append(sub)
    return out


def all_blueprints():
    for fn in OUT:
        yield from fn()


# ---------------------------------------------------------------- farm fields
@infra
def fields():
    """Greenhouse crop fields with a scarecrow (field hut) in the middle, assigned to a farmer."""
    out = []
    for name, size in (("greenhouse_small", 9), ("greenhouse", 11), ("greenhouse_large", 15)):
        b = Blueprint(name=name, folder="infrastructure/fields", sx=size, sy=7, sz=size)
        c = size // 2
        b.fill(0, 0, 0, size - 1, 0, size - 1, "minecraft:smooth_stone")
        b.fill(1, 0, 1, size - 2, 0, size - 2, "minecraft:dirt")
        b.fill(0, 1, 0, size - 1, 5, size - 1, AIR)
        for (x, z) in kit._perimeter(0, 0, size - 1, size - 1):
            for y in range(1, 5):
                b.set(x, y, z, "minecraft:glass")
            b.set(x, 5, z, "minecraft:iron_block" if (x + z) % 4 == 0 else "minecraft:glass")
        b.fill(1, 6, 1, size - 2, 6, size - 2, "minecraft:glass")
        for x in range(2, size - 2, 4):
            b.set(x, 6, c, "minecraft:sea_lantern")
        for y in (1, 2):
            b.set(c, y, 0, AIR)
        b.set(c, 0, c, "minecraft:water")
        b.set(c, 1, c, "minecolonies:blockhutfield", half="lower", facing="south",
              te={"id": "minecolonies:scarecrow", "Item": __import__("nbtlib").String("")})
        b.set(c, 0, c, "minecraft:smooth_stone")
        b.set(c + 1, 0, c, "minecraft:water")
        out.append(b)
    return out


# ---------------------------------------------------------------- supply camp / ship
# MineColonies' Supply Camp and Supply Ship items load decorations/supplies/supplycamp and
# supplyship from the selected style pack; without them the placement preview stays empty.
# Placement rules (ItemSupplyCampDeployer / ItemSupplyChestDeployer): every layer below the
# groundlevel tag must be solid ground (camp) or water (ship), and the layer above must be clear.
SUPPLY_TOOLS = [("minecraft:wooden_shovel", 1), ("minecraft:wooden_pickaxe", 1), ("minecraft:wooden_axe", 1),
                ("minecraft:wooden_hoe", 1), ("structurize:caliper", 1)]
SUPPLY_BUILD = [("minecraft:cobblestone", 32), ("minecraft:cobblestone", 32), ("minecraft:oak_log", 16),
                ("minecraft:oak_sapling", 4), ("minecraft:birch_sapling", 4), ("minecraft:torch", 16)]
SUPPLY_FOOD = [("minecraft:bread", 64), ("minecraft:cooked_beef", 16), ("minecraft:baked_potato", 32),
               ("minecraft:apple", 16)]
SUPPLY_START = [("structurize:sceptergold", 1), ("minecolonies:blockhuttownhall", 1)]


def _supply_racks(b, x, y, z, facing, step):
    """Four racks in a row: town hall + build tool, tools, building materials, food."""
    dx, dz = step
    for i, items in enumerate((SUPPLY_START, SUPPLY_TOOLS, SUPPLY_BUILD, SUPPLY_FOOD)):
        b.rack(x + i * dx, y, z + i * dz, facing=facing, items=items)


@infra
def supplies():
    # ---- supply camp: a fenced construction site with a site-office container
    c = Blueprint(name="supplycamp", folder="decorations/supplies", sx=17, sy=8, sz=15)
    c.fill(0, 0, 0, 16, 0, 14, "minecraft:gray_concrete")
    c.fill(0, 1, 0, 16, 7, 14, AIR)
    for x in range(0, 17):
        for z in (0, 14):
            if x % 4 == 0:
                c.set(x, 1, z, "minecraft:stone_brick_wall")
            else:
                c.set(x, 1, z, "minecraft:iron_bars")
    for z in range(1, 14):
        c.set(0, 1, z, "minecraft:iron_bars" if z % 4 else "minecraft:stone_brick_wall")
    for z in range(1, 14):
        if z not in (6, 7, 8):  # site entrance on the east side
            c.set(16, 1, z, "minecraft:iron_bars" if z % 4 else "minecraft:stone_brick_wall")
    # site office container (x 1..8, z 1..6)
    c.fill(1, 0, 1, 8, 0, 6, "minecraft:smooth_stone")
    for (x, z) in kit._perimeter(1, 1, 8, 6):
        for y in (1, 2, 3):
            corner = x in (1, 8) and z in (1, 6)
            c.set(x, y, z, "minecraft:white_concrete" if corner or y != 2 else "minecraft:glass_pane")
    c.fill(1, 4, 1, 8, 4, 6, "minecraft:light_gray_concrete")
    c.fill(2, 4, 2, 7, 4, 5, "minecraft:smooth_stone_slab", type="bottom")
    c.set(5, 1, 6, "minecraft:dark_oak_door", facing="south", half="lower", hinge="left", open=False, powered=False)
    c.set(5, 2, 6, "minecraft:dark_oak_door", facing="south", half="upper", hinge="left", open=False, powered=False)
    _supply_racks(c, 2, 1, 2, "south", (1, 0))
    c.bed(7, 1, 2, "north", color="light_gray")
    c.set(6, 1, 2, "minecraft:crafting_table")
    c.set(2, 1, 5, "minecraft:furnace", facing="east", lit=False)
    c.set(3, 3, 3, "minecraft:sea_lantern")
    c.set(6, 3, 4, "minecraft:sea_lantern")
    # yard: fire pit, workbench, material pallets, flood lights
    c.set(12, 1, 10, "minecraft:campfire", facing="north", lit=True, signal_fire=False, waterlogged=False,
          te={"id": "minecraft:campfire"})
    for (x, z) in ((11, 9), (13, 9), (11, 11), (13, 11)):
        c.set(x, 1, z, "minecraft:polished_andesite_stairs", facing="north" if z == 11 else "south",
              half="bottom", shape="straight", waterlogged=False)
    c.set(12, 1, 2, "minecraft:smithing_table")
    c.set(13, 1, 2, "minecraft:stonecutter", facing="south")
    for (x, z) in ((10, 4), (11, 4), (10, 5)):
        c.set(x, 1, z, "minecraft:spruce_slab", type="bottom", waterlogged=False)
    c.set(10, 2, 4, "minecraft:stone_bricks")
    c.set(11, 2, 4, "minecraft:bricks")
    kit.street_light(c, 15, 1, 1, arm="west")
    kit.street_light(c, 1, 1, 13, arm="east")
    c.marker(12, 1, 7)
    c.tag(12, 0, 7, "groundlevel")  # one ground layer under the camp
    out = [c]

    # ---- supply ship: a small cargo barge with containers and a stern wheelhouse
    W, L = 11, 28
    s = Blueprint(name="supplyship", folder="decorations/supplies", sx=W, sy=12, sz=L)
    hull, stripe, deck = "minecraft:black_concrete", "minecraft:red_concrete", "minecraft:gray_concrete"

    def width_at(z):  # tapered bow at z = 0..3
        return {0: 3, 1: 2, 2: 1}.get(z, 0)

    for z in range(L):
        inset = width_at(z)
        x1, x2 = inset, W - 1 - inset
        for y in range(0, 4):
            ins = inset + (1 if y == 0 else 0)
            a, bb = ins, W - 1 - ins
            if a > bb:
                continue
            for x in range(a, bb + 1):
                edge = x in (a, bb) or z in (0, L - 1) or y == 0 or (z <= 3 and x in (x1, x2))
                if y in (1,) or edge:
                    s.set(x, y, z, stripe if (y == 3 and edge) else hull)
                else:
                    s.set(x, y, z, AIR)
        s.fill(x1, 4, z, x2, 4, z, deck)
        s.fill(x1, 5, z, x2, 11, z, AIR)
        s.set(x1, 5, z, "minecraft:iron_bars")
        s.set(x2, 5, z, "minecraft:iron_bars")
    s.fill(3, 5, 0, 7, 5, 0, "minecraft:iron_bars")
    for z in range(4, L - 4, 3):
        s.set(W // 2, 3, z, "minecraft:sea_lantern")
    # deck cargo: shipping containers (2 wide x 2 tall x 4 long)
    for (x, z, col) in ((2, 5, "minecraft:orange_concrete"), (6, 5, "minecraft:blue_concrete"),
                        (2, 10, "minecraft:white_concrete"), (6, 10, "minecraft:lime_concrete")):
        s.fill(x, 5, z, x + 2, 6, z + 3, col)
    s.fill(2, 7, 5, 4, 8, 8, "minecraft:cyan_concrete")
    # wheelhouse (z 16..25)
    zw1, zw2 = 16, 25
    for (x, z) in kit._perimeter(1, zw1, W - 2, zw2):
        for y in (5, 6, 7):
            corner = x in (1, W - 2) and z in (zw1, zw2)
            s.set(x, y, z, "minecraft:white_concrete" if corner or y == 5 else "minecraft:glass_pane")
    s.fill(1, 8, zw1, W - 2, 8, zw2, "minecraft:light_gray_concrete")
    s.fill(2, 4, zw1 + 1, W - 3, 4, zw2 - 1, "minecraft:smooth_stone")
    s.set(W // 2, 5, zw1, "minecraft:dark_oak_door", facing="north", half="lower", hinge="left", open=False, powered=False)
    s.set(W // 2, 6, zw1, "minecraft:dark_oak_door", facing="north", half="upper", hinge="left", open=False, powered=False)
    _supply_racks(s, 2, 5, zw1 + 2, "east", (0, 1))
    s.bed(8, 5, zw2 - 2, "south", color="blue")
    s.bed(7, 5, zw2 - 2, "south", color="blue")
    s.set(8, 5, zw1 + 2, "minecraft:crafting_table")
    s.set(8, 5, zw1 + 3, "minecraft:furnace", facing="west", lit=False)
    s.set(4, 8, zw1 + 4, "minecraft:sea_lantern")
    s.set(6, 8, zw2 - 3, "minecraft:sea_lantern")
    # mast with a nav light on the wheelhouse roof
    for y in range(9, 11):
        s.set(W // 2, y, zw2 - 1, "minecraft:polished_deepslate_wall")
    s.set(W // 2, 11, zw2 - 1, "minecraft:lantern", hanging=False, waterlogged=False)
    s.marker(W // 2, 5, 13)
    s.tag(W // 2, 3, 13, "groundlevel")  # four water layers (y 0..3) under the deck
    out.append(s)
    return out
