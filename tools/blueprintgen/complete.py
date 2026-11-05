"""'Modern City Complete' tier: every supported mod.

1. upgrade(b): swaps generic materials for modded ones (TFMG asphalt and concrete, Chipped panels)
   and adds per-building extras (Cold Sweat hearths, Macaw's furniture, TFMG traffic lights).
2. districts(): blueprints that only make sense with the big tech mods: power plants, data
   center, radar station, armory, ore excavation rig, rail station, highway bridge, skyscraper,
   shopping mall.

Block ids come from the mods' 1.21.1 jars (tools/blueprintgen/ids/, see SOURCES.json); gen.py
refuses to write anything that is not in those lists.
"""
import kit
from bp import AIR, FILL, Blueprint, state
from kit import FLOOR_H, OFFICE

PACK_NAME = "Modern City Complete"

SWAP = {
    "minecraft:black_concrete": "tfmg:asphalt",
    "minecraft:gray_concrete": "tfmg:concrete",
    "minecraft:light_gray_concrete": "chipped:light_gray_concrete_panel",
    "minecraft:white_concrete": "chipped:grid_white_concrete",
    "minecraft:iron_bars": "tfmg:steel_bars",
    "create:industrial_iron_block": "tfmg:steel_block",
    "minecraft:smooth_stone": "mcwpaths:andesite_square_paving",
}


def upgrade(b: Blueprint) -> Blueprint:
    for pos, (name, props) in list(b.blocks.items()):
        if name in SWAP:
            b.blocks[pos] = state(SWAP[name], **dict(props))
    base = b.name.rstrip("0123456789")
    level = int(b.name[len(base):] or 0)
    extra = EXTRAS.get(base)
    if extra:
        extra(b, level)
    return b


# ---------------------------------------------------------------- per-building extras
def _hearth(b, x, z, facing="south"):
    b.set(x, 1, z, "cold_sweat:hearth_bottom", facing=facing)
    b.set(x, 2, z, "cold_sweat:hearth_top", facing=facing)


def _roof_hatch(b, x, z):
    """Macaw's metal trapdoor where the ladder core meets the roof."""
    for y in range(b.sy - 1, 0, -1):
        if b.get(x, y, z)[0] not in ("minecraft:air", "minecraft:ladder") and b.get(x, y - 1, z)[0] == "minecraft:ladder":
            b.set(x, y, z, "mcwtrpdoors:metal_trapdoor", facing="south", half="top", open=False)
            return


def _residence(b, level):
    _hearth(b, 3, 10)
    _roof_hatch(b, 2, 2)
    for i in range(level):
        y = (1 + i) * FLOOR_H + 1
        x = 4 + (i % 2) * 6
        b.set(x, y, 2, "mcwwindows:oak_blinds", facing="south", part="bottom", blindsstate="open")
        b.set(x, y + 1, 2, "mcwwindows:oak_blinds", facing="south", part="top", blindsstate="open")
    b.set(5, 1, 10, "mcwfurnitures:light_gray_couch", facing="north", shape="single")
    if level >= 2:
        b.set(4, 1, 8, "mcwfurnitures:oak_modern_desk", facing="north", connection="single")


def _townhall(b, level):
    _hearth(b, 5, 12)
    _roof_hatch(b, 3, 3)
    for x in (7, 13):
        b.set(x, 1, 12, "mcwfurnitures:oak_modern_chair", facing="south")


def _intersection_lights(b, corners):
    for (x, z, facing) in corners:
        b.set(x, 2, z, "tfmg:concrete_wall")
        b.set(x, 3, z, "tfmg:concrete_wall")
        b.set(x, 4, z, "tfmg:traffic_light", facing=facing)


def _intersection(b, level):
    _intersection_lights(b, [(1, 1, "south"), (13, 1, "west"), (1, 13, "east"), (13, 13, "north")])


def _tjunction(b, level):
    _intersection_lights(b, [(13, 1, "west"), (13, 13, "north")])


def _guardtower(b, level):
    b.set(2, 1, 5, "tacz:gun_smith_table")


def _barracks_like(b, level):
    b.set(2, 1, 6, "tacz:workbench_a")


def _miner(b, level):
    if level >= 3:
        b.set(11, 4, 12, "createoreexcavation:sample_drill")


EXTRAS = {
    "residence": _residence,
    "townhall": _townhall,
    "intersection": _intersection,
    "tjunction": _tjunction,
    "guardtower": _guardtower,
    "combatacademy": _barracks_like,
    "archery": _barracks_like,
    "miner": _miner,
}


# ---------------------------------------------------------------- districts
def _pad(name, folder, sx, sy, sz, top="tfmg:concrete"):
    b = Blueprint(name=name, folder=folder, sx=sx, sy=sy, sz=sz)
    b.fill(0, 0, 0, sx - 1, 0, sz - 1, top)
    b.fill(0, 1, 0, sx - 1, sy - 1, sz - 1, AIR)
    return b


def _shell(b, x1, z1, x2, z2, h, wall="tfmg:concrete", glass="create:framed_glass", roof="tfmg:concrete"):
    for (x, z) in kit._perimeter(x1, z1, x2, z2):
        for y in range(1, h):
            b.set(x, y, z, glass if (y % 4 in (2, 3) and (x + z) % 3) else wall)
    b.fill(x1, h, z1, x2, h, z2, roof)


def diesel_plant():
    b = _pad("diesel_power_plant", "decorations/power", 17, 16, 15)
    _shell(b, 0, 0, 16, 10, 7)
    for i in range(3):
        x = 3 + i * 4
        b.set(x, 1, 4, "createdieselgenerators:large_diesel_engine", facing="east")
        b.set(x + 1, 1, 4, "tfmg:generator", facing="east")
        b.set(x, 1, 7, "create:fluid_tank")
        b.set(x, 2, 7, "create:fluid_tank")
    for y in range(1, 15):
        b.set(14, y, 13, "tfmg:concrete_smokestack")
    b.set(8, 1, 10, AIR)
    b.set(8, 2, 10, AIR)
    b.set(2, 1, 12, "createdieselgenerators:oil_barrel")
    return b


def nuclear_plant():
    b = _pad("nuclear_power_plant", "decorations/power", 23, 22, 21)
    # containment building with reactor block set (assemble per Create Nuclear guide)
    _shell(b, 1, 1, 11, 11, 9, wall="createnuclear:steel_block", glass="createnuclear:reinforced_glass")
    for x in range(4, 9):
        for y in range(1, 6):
            for z in range(4, 9):
                edge = x in (4, 8) or y in (1, 5) or z in (4, 8)
                b.set(x, y, z, "createnuclear:reactor_casing" if edge else "createnuclear:reactor_core")
    b.set(6, 3, 3, "createnuclear:reactor_controller", facing="north", assembled=False, active=False)
    b.set(6, 6, 6, "createnuclear:reactor_rod_input")
    b.set(10, 1, 6, "createnuclear:reactor_alarm")
    # cooling tower
    cx, cz = 17, 10
    for y in range(1, 21):
        r = 5 if y < 4 or y > 16 else 4
        for x in range(cx - r, cx + r + 1):
            for z in range(cz - r, cz + r + 1):
                d = ((x - cx) ** 2 + (z - cz) ** 2) ** 0.5
                if r - 0.6 <= d <= r + 0.4:
                    b.set(x, y, z, "tfmg:concrete")
    # turbine hall
    _shell(b, 1, 13, 11, 19, 6)
    for x in (3, 6, 9):
        b.set(x, 1, 16, "tfmg:turbine_engine", facing="east")
        b.set(x, 2, 16, "tfmg:generator", facing="east")
    return b


def solar_farm():
    b = _pad("solar_farm", "decorations/power", 15, 3, 15, top="minecraft:gravel")
    for x in range(1, 14, 2):
        for z in range(1, 14):
            b.set(x, 1, z, "create_new_age:basic_solar_heating_plate")
    b.set(7, 1, 0, "create_new_age:stirling_engine")
    return b


def substation_complete():
    b = _pad("hv_substation", "decorations/power", 9, 9, 9)
    for (x, z) in kit._perimeter(0, 0, 8, 8):
        b.set(x, 1, z, "tfmg:steel_bars")
        b.set(x, 2, z, "tfmg:steel_bars")
    for x in (2, 6):
        b.set(x, 1, 4, "tfmg:large_transformer", facing="north")
        b.set(x, 1, 2, "tfmg:accumulator", facing="north")
        for y in range(2, 7):
            b.set(x, y, 6, "tfmg:electric_post", axis="y")
        b.set(x, 7, 6, "tfmg:cable_connector", facing="down")
    return b


def power_pylon():
    b = _pad("power_pylon", "decorations/power", 7, 17, 3, top="minecraft:smooth_stone")
    for y in range(1, 15):
        b.set(3, y, 1, "tfmg:steel_truss" if False else "create:metal_girder")
    b.fill(0, 14, 1, 6, 14, 1, "create:metal_girder")
    for x in (0, 3, 6):
        b.set(x, 15, 1, "tfmg:cable_connector", facing="down")
    return b


def data_center():
    b = _pad("data_center", "decorations/datacenter", 19, 11, 17)
    _shell(b, 0, 0, 18, 16, 9, wall="ae2:smooth_sky_stone_block", glass="ae2:quartz_vibrant_glass",
           roof="ae2:smooth_sky_stone_block")
    # controller spine
    for x in range(3, 16):
        b.set(x, 1, 8, "ae2:controller")
    # server rows (drives touch the controller row, so they network without cables)
    for x in range(3, 16):
        for y in (1, 2, 3):
            for z in (7, 9):
                drive = "extendedae:ex_drive" if (x + y) % 2 else "ae2:drive"
                b.set(x, y, z, drive, facing="north" if z == 7 else "south")
        b.set(x, 2, 8, "ae2:controller")
        b.set(x, 3, 8, "ae2:controller")
    # crafting CPU block
    for x in range(3, 8):
        for z in range(2, 5):
            for y in (1, 2):
                b.set(x, y, z, "megacells:mega_crafting_accelerator" if (x + z + y) % 3 else "ae2:crafting_unit")
    b.set(5, 3, 3, "megacells:mega_crafting_monitor")
    # power: Applied Generators + Applied Flux + kinetic acceptor from Create
    b.set(12, 1, 3, "appgen:flux_generator_1k")
    b.set(13, 1, 3, "appflux:flux_accessor")
    b.set(14, 1, 3, "appliedcreate:kinetic_energy_acceptor")
    b.set(15, 1, 3, "megacells:mega_energy_cell")
    b.set(11, 1, 3, "ae2:energy_acceptor")
    # automation: quantum computer + assembler matrix corner
    b.set(14, 1, 13, "advanced_ae:quantum_crafter")
    b.set(12, 1, 13, "extendedae:ex_pattern_provider")
    b.set(10, 1, 13, "appliedcreate:brass_pattern_provider")
    b.set(9, 1, 16, AIR)
    b.set(9, 2, 16, AIR)
    b.set(5, 1, 13, "cold_sweat:icebox", facing="south")  # cooling
    return b


def radar_station():
    b = _pad("radar_station", "decorations/military", 13, 14, 13)
    _shell(b, 2, 2, 10, 10, 5)
    for y in range(6, 11):
        b.set(6, y, 6, "create:metal_girder")
    b.set(6, 11, 6, "create_radar:radar_bearing")
    for x in range(4, 9):
        b.set(x, 12, 6, "create_radar:radar_dish_block", facing="up")
    b.set(6, 2, 3, "create_radar:monitor", facing="south", shape="center")
    b.set(5, 2, 3, "create_radar:monitor", facing="south", shape="center")
    b.set(7, 2, 3, "create_radar:data_link")
    b.set(6, 1, 10, AIR)
    b.set(6, 2, 10, AIR)
    for (x, z) in kit._perimeter(0, 0, 12, 12):
        b.set(x, 1, z, "mcwfences:mesh_metal_fence")
    for x in (5, 6, 7):
        b.set(x, 1, 12, AIR)
    return b


def armory():
    b = _pad("armory", "decorations/military", 15, 7, 13)
    _shell(b, 0, 0, 14, 8, 5, glass="tfmg:steel_bars")
    b.set(2, 1, 2, "tacz:gun_smith_table")
    b.set(4, 1, 2, "tacz:workbench_a")
    b.set(6, 1, 2, "tacz:workbench_b")
    b.set(8, 1, 2, "tacz:workbench_c")
    for x in range(2, 13, 3):
        b.set(x, 1, 12, "tacz:target")
    b.set(7, 1, 8, "mcwdoors:metal_reinforced_door", facing="south", half="lower", hinge="left", open=False)
    b.set(7, 2, 8, "mcwdoors:metal_reinforced_door", facing="south", half="upper", hinge="left", open=False)
    return b


def ore_rig():
    b = _pad("ore_excavation_rig", "decorations/industry", 11, 10, 11)
    b.set(5, 1, 5, "createoreexcavation:drilling_machine", facing="north")
    b.set(5, 1, 7, "createoreexcavation:kinetic_input")
    b.set(5, 1, 8, "create:shaft", axis="z")
    b.set(5, 1, 9, "createaddition:electric_motor", facing="north")
    for (x, z) in ((2, 2), (8, 2), (2, 8), (8, 8)):
        for y in range(1, 8):
            b.set(x, y, z, "create:metal_girder")
    b.fill(2, 8, 2, 8, 8, 8, "tfmg:steel_block")
    b.set(1, 1, 1, "createoreexcavation:sample_drill")
    return b


def oil_field():
    b = _pad("oil_pumpjack", "decorations/industry", 9, 8, 7, top="minecraft:coarse_dirt")
    b.set(4, 1, 3, "tfmg:pumpjack_base")
    b.set(4, 2, 3, "tfmg:pumpjack_crank")
    b.set(1, 1, 3, "tfmg:steel_distillation_controller", facing="east")
    return b


def train_station():
    W, D = 21, 13
    b = _pad("train_station", "decorations/transit", W, 9, D)
    for x in range(W):
        for z in (5, 7):
            b.set(x, 1, z, "create:track", shape="xo")
        b.set(x, 0, 5, "minecraft:gravel")
        b.set(x, 0, 7, "minecraft:gravel")
    b.fill(0, 1, 9, W - 1, 1, 12, "tfmg:concrete")
    b.fill(0, 1, 0, W - 1, 1, 3, "tfmg:concrete")
    for x in range(0, W, 5):
        for z in (2, 10):
            for y in range(2, 7):
                b.set(x, y, z, "create:metal_girder")
    b.fill(0, 7, 0, W - 1, 7, D - 1, "create:framed_glass")
    for x in (0, W - 1):
        b.set(x, 2, 5, "railways:buffer", facing="east" if x == 0 else "west")
    b.set(10, 2, 3, "railways:semaphore", facing="south", flipped=False, full=False, upside_down=False)
    for x in range(W):
        b.set(x, 2, 9, "mcwstairs:andesite_platform")
        b.set(x, 2, 3, "mcwstairs:andesite_platform")
    for x in (4, 9, 14):
        b.set(x, 2, 11, "create:white_seat")
        b.set(x, 6, 2, "tfmg:modern_light", facing="down")
    return b


def highway_bridge():
    L, W = 15, 15
    b = Blueprint(name="highway_bridge", folder="infrastructure/bridges", sx=W, sy=12, sz=L)
    b.fill(0, 0, 0, W - 1, 11, L - 1, AIR)
    deck = 9
    for (x, z) in ((3, 7), (11, 7)):
        for y in range(0, deck):
            b.set(x, y, z, "mcwbridges:iron_bridge_pier")
    b.fill(0, deck, 0, W - 1, deck, L - 1, "tfmg:steel_block")
    b.fill(2, deck + 1, 0, 12, deck + 1, L - 1, "tfmg:asphalt")
    b.fill(0, deck + 1, 0, 1, deck + 1, L - 1, "minecraft:smooth_stone")
    b.fill(13, deck + 1, 0, 14, deck + 1, L - 1, "minecraft:smooth_stone")
    for z in range(L):
        b.set(0, deck + 2, z, "tfmg:steel_bars")
        b.set(W - 1, deck + 2, z, "tfmg:steel_bars")
        if z % 4 < 2:
            b.set(7, deck + 1, z, "minecraft:yellow_concrete")
    return b


def rail_bridge():
    L = 15
    b = Blueprint(name="rail_bridge", folder="infrastructure/bridges", sx=7, sy=11, sz=L)
    b.fill(0, 0, 0, 6, 10, L - 1, AIR)
    for z in (3, 11):
        for y in range(0, 8):
            b.set(3, y, z, "mcwbridges:iron_bridge_pier")
    for z in range(L):
        for x in range(7):
            b.set(x, 8, z, "mcwbridges:iron_bridge", connection="middle_ns")
        b.set(3, 9, z, "create:track", shape="zo")
    return b


def skyscraper():
    floors = 20
    W = 17
    b = Blueprint(name="office_skyscraper", folder="decorations/skyscrapers", sx=W, sy=floors * FLOOR_H + 5, sz=W)
    b.fill(0, 0, 0, W - 1, 0, W - 1, "minecraft:smooth_stone")
    kit.tower(b, OFFICE, 1, 1, W - 2, W - 2, floors, open_front=("south", 7, 9))
    kit.ladder_core(b, 2, 2, 1, floors * FLOOR_H - 1, facing="south")
    kit.elevator(b, 11, 3, 0, (floors - 1) * FLOOR_H + 4, [f * FLOOR_H for f in range(floors)], door_side="south")
    top = floors * FLOOR_H
    for y in range(top + 2, top + 5):
        b.set(8, y, 8, "create:metal_girder")
    b.set(8, top + 4, 8, "minecraft:redstone_lamp")
    _roof_hatch(b, 2, 2)
    return b


def shopping_mall():
    W, D, floors = 27, 21, 2
    b = Blueprint(name="shopping_mall", folder="decorations/commercial", sx=W, sy=floors * FLOOR_H + 3, sz=D)
    b.fill(0, 0, 0, W - 1, 0, D - 1, "minecraft:smooth_stone")
    kit.tower(b, OFFICE, 0, 0, W - 1, D - 3, floors, bay=6, open_front=("south", 11, 15))
    # atrium
    b.fill(9, FLOOR_H, 6, 17, FLOOR_H, 12, AIR)
    # storefront counters on both floors
    for f in range(floors):
        y = f * FLOOR_H + 1
        for x in range(2, W - 2, 5):
            b.set(x, y, 2, "mcwfurnitures:oak_modern_desk", facing="north", connection="single")
            b.set(x, y + 2, 1, "mcwlights:white_ceiling_light", part="base", lit=True)
    kit.ladder_core(b, 1, 1, 1, floors * FLOOR_H - 1, facing="south")
    for x in range(10, 17):
        b.set(x, 4, D - 2, "mcwroofs:gray_concrete_top_roof", part="top_end_0")
    for x in (11, 13, 15):
        b.set(x, 1, D - 3, "mcwdoors:sliding_glass_door", facing="south", half="lower", hinge="right", open=False)
        b.set(x, 2, D - 3, "mcwdoors:sliding_glass_door", facing="south", half="upper", hinge="right", open=False)
    return b


def districts():
    return [diesel_plant(), nuclear_plant(), solar_farm(), substation_complete(), power_pylon(), data_center(),
            radar_station(), armory(), ore_rig(), oil_field(), train_station(), highway_bridge(), rail_bridge(),
            skyscraper(), shopping_mall()]
