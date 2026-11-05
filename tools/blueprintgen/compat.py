"""Compatibility layer.

Structurize disables a whole style pack when any mod in its pack.json "mods" list is missing,
and turns unknown blocks into air. To work in as many modpacks as possible we ship two packs:

  * Modern City       - full version, needs Create + AE2 + Create Crafts & Additions
  * Modern City Lite  - same buildings, every non-vanilla block swapped for a vanilla look-alike,
                        so it loads with nothing but MineColonies installed.

Every non-vanilla, non-MineColonies block a generator uses must have an entry in FALLBACK;
to_lite() fails loudly otherwise, so the Lite pack can never silently lose blocks.
"""
import copy

from bp import Blueprint, state

LITE_PACK_NAME = "Modern City Lite"
ALWAYS_PRESENT = ("minecraft", "structurize", "minecolonies")

FALLBACK = {
    # Create: decoration
    "create:framed_glass": "minecraft:glass",
    "create:polished_cut_andesite": "minecraft:polished_andesite",
    "create:polished_cut_limestone": "minecraft:smooth_sandstone",
    "create:cut_limestone_bricks": "minecraft:sandstone",
    "create:cut_deepslate_bricks": "minecraft:deepslate_bricks",
    "create:industrial_iron_block": "minecraft:iron_block",
    "create:andesite_casing": "minecraft:stripped_spruce_wood",
    "create:andesite_scaffolding": "minecraft:scaffolding",
    "create:metal_girder": "minecraft:iron_bars",
    "create:white_seat": "minecraft:white_carpet",
    "create:red_postbox": "minecraft:barrel",
    "create:depot": "minecraft:smooth_stone_slab",
    # Create: machinery (non-functional stand-ins)
    "create:large_cogwheel": "minecraft:polished_andesite",
    "create:elevator_pulley": "minecraft:iron_block",
    "create:elevator_contact": "minecraft:polished_andesite",
    "create:contraption_controls": "minecraft:lever",
    "create:mechanical_saw": "minecraft:stonecutter",
    "create:shaft": "minecraft:chain",
    "create:mechanical_press": "minecraft:piston",
    "create:crushing_wheel": "minecraft:polished_andesite",
    "create:millstone": "minecraft:grindstone",
    "create:mechanical_mixer": "minecraft:cauldron",
    "create:deployer": "minecraft:dispenser",
    "create:fluid_tank": "minecraft:copper_block",
    "create:tiled_glass": "minecraft:glass",
    # Create Crafts & Additions
    "createaddition:electric_motor": "minecraft:iron_block",
    "createaddition:large_connector": "minecraft:lightning_rod",
    "createaddition:modular_accumulator": "minecraft:iron_block",
    "createaddition:redstone_relay": "minecraft:repeater",
    # AE2
    "ae2:controller": "minecraft:lodestone",
    "ae2:drive": "minecraft:dispenser",
    "ae2:chest": "minecraft:chest",
    "ae2:wireless_access_point": "minecraft:end_rod",
}

# Properties the fallback block understands; everything else is dropped.
KEEP_PROPS = {
    "minecraft:end_rod": {"facing"}, "minecraft:lightning_rod": {"facing"},
    "minecraft:dispenser": {"facing"}, "minecraft:chest": {"facing"},
    "minecraft:barrel": {"facing"}, "minecraft:lever": {"facing"},
    "minecraft:repeater": {"facing"}, "minecraft:stripped_spruce_wood": {"axis"},
    "minecraft:chain": {"axis"}, "minecraft:piston": {"facing"},
}
FALLBACK_TE = {"minecraft:chest": "minecraft:chest", "minecraft:barrel": "minecraft:barrel"}
_HORIZONTAL = {"north", "south", "east", "west"}


def lite_state(st):
    name, props = st
    if name.split(":")[0] in ALWAYS_PRESENT:
        return st, None
    if name not in FALLBACK:
        raise KeyError(f"no vanilla fallback for {name}; add one to compat.FALLBACK")
    new = FALLBACK[name]
    keep = KEEP_PROPS.get(new, set())
    p = {k: v for k, v in props if k in keep}
    if new in ("minecraft:chest", "minecraft:barrel", "minecraft:repeater") and p.get("facing") not in _HORIZONTAL:
        p.pop("facing", None)
    if new == "minecraft:lever":
        p = {"face": "floor", **({"facing": props_dict(props)["facing"]} if props_dict(props).get("facing") in _HORIZONTAL else {})}
    return state(new, **p), FALLBACK_TE.get(new)


def props_dict(props):
    return dict(props)


def to_lite(b: Blueprint) -> Blueprint:
    out = copy.deepcopy(b)
    for pos, st in list(out.blocks.items()):
        new, te_id = lite_state(st)
        if new is st:
            continue
        out.blocks[pos] = new
        if te_id:
            out.tes[pos] = {"id": te_id}
        elif pos in out.tes and out.tes[pos]["id"].split(":")[0] not in ALWAYS_PRESENT:
            del out.tes[pos]
    leftover = [m for m in out.mods() if m not in ALWAYS_PRESENT]
    assert not leftover, f"{out.path}: lite pack still uses {leftover}"
    return out
