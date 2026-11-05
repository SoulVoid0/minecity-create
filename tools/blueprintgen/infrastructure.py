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
