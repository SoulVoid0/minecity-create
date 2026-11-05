"""Reusable modern-architecture parts.

Every block id used here is verified against the 1.21.1 sources of the owning mod
(see docs/BLOCK_IDS.md). Anything not listed there must not be added without checking.
"""
from bp import AIR, FILL, KEEP, Blueprint, state

FLOOR_H = 5  # slab + 4 clear blocks

# Which pack is being generated: "full" (Create/AE2/CC&A) or "complete" (every supported mod).
# The Lite pack is derived from "full" by compat.to_lite().
TIER = "full"


def complete() -> bool:
    return TIER == "complete"


class Theme:
    """Material set for one family of buildings."""

    def __init__(self, structure, accent, spandrel, glass, floor, ceiling_light, trim, roof):
        self.structure = structure
        self.accent = accent
        self.spandrel = spandrel
        self.glass = glass
        self.floor = floor
        self.ceiling_light = ceiling_light
        self.trim = trim
        self.roof = roof


OFFICE = Theme(
    structure="minecraft:light_gray_concrete",
    accent="minecraft:gray_concrete",
    spandrel="minecraft:smooth_quartz",
    glass="create:framed_glass",
    floor="create:polished_cut_andesite",
    ceiling_light="minecraft:sea_lantern",
    trim="minecraft:polished_andesite",
    roof="minecraft:gray_concrete",
)
RESIDENTIAL = Theme(
    structure="minecraft:white_concrete",
    accent="create:cut_limestone_bricks",
    spandrel="minecraft:white_concrete",
    glass="create:framed_glass",
    floor="create:polished_cut_limestone",
    ceiling_light="minecraft:pearlescent_froglight",
    trim="minecraft:smooth_quartz",
    roof="minecraft:light_gray_concrete",
)
INDUSTRIAL = Theme(
    structure="create:industrial_iron_block",
    accent="minecraft:gray_concrete",
    spandrel="create:cut_deepslate_bricks",
    glass="create:framed_glass",
    floor="minecraft:smooth_stone",
    ceiling_light="minecraft:sea_lantern",
    trim="create:andesite_casing",
    roof="minecraft:gray_concrete",
)


def foundation(b: Blueprint, x1, z1, x2, z2, y=0, top="minecraft:smooth_stone"):
    """Ground-level floor plate; the layer under it (if any) is solid-substituted."""
    for yy in range(0, y):
        b.fill(x1, yy, z1, x2, yy, z2, FILL)
    b.fill(x1, y, z1, x2, y, z2, top)


def clear(b: Blueprint, x1, y1, z1, x2, y2, z2):
    b.fill(x1, y1, z1, x2, y2, z2, AIR)


def keep_margin(b: Blueprint, x1, z1, x2, z2, y_from, y_to):
    """Mark an area as 'leave the world alone' (terrain around a building)."""
    b.fill(x1, y_from, z1, x2, y_to, z2, KEEP)


def tower(b: Blueprint, t: Theme, x1, z1, x2, z2, floors: int, y0=0, bay=4, open_front=None):
    """Glass curtain-wall tower shell with floor slabs, ceiling lights and a flat roof.

    open_front: (side, a, b) leaves a ground-floor opening on 'north'|'south'|'east'|'west'
    between a..b (inclusive, along the wall) for the entrance.
    Returns the y of the roof slab.
    """
    top = y0 + floors * FLOOR_H
    # interior air
    clear(b, x1 + 1, y0 + 1, z1 + 1, x2 - 1, top - 1, z2 - 1)
    for f in range(floors + 1):
        y = y0 + f * FLOOR_H
        b.fill(x1, y, z1, x2, y, z2, t.accent if f else t.floor)
        if 0 < f < floors:
            b.fill(x1 + 1, y, z1 + 1, x2 - 1, y, z2 - 1, t.floor)
    # perimeter
    for f in range(floors):
        yb = y0 + f * FLOOR_H
        for (x, z) in _perimeter(x1, z1, x2, z2):
            column = _is_column(x, z, x1, z1, x2, z2, bay)
            for dy in range(1, FLOOR_H):
                y = yb + dy
                if column:
                    b.set(x, y, z, t.structure)
                elif dy == FLOOR_H - 1:
                    b.set(x, y, z, t.spandrel)
                else:
                    b.set(x, y, z, t.glass)
        # ceiling lights on the slab above, on a 4-grid
        yc = yb + FLOOR_H
        for x in range(x1 + 2, x2 - 1, 4):
            for z in range(z1 + 2, z2 - 1, 4):
                b.set(x, yc, z, t.ceiling_light)
    # roof parapet
    for (x, z) in _perimeter(x1, z1, x2, z2):
        b.set(x, top + 1, z, t.trim)
    b.fill(x1 + 1, top, z1 + 1, x2 - 1, top, z2 - 1, t.roof)
    if open_front:
        side, a, c = open_front
        for i in range(a, c + 1):
            for dy in range(1, 4):
                x, z = _side_xy(side, i, x1, z1, x2, z2)
                b.set(x, y0 + dy, z, AIR)
            x, z = _side_xy(side, i, x1, z1, x2, z2)
            b.set(x, y0 + 4, z, t.trim)
    return top


def ladder_core(b: Blueprint, x, z, y_from, y_to, facing="south", wall="minecraft:light_gray_concrete"):
    """Citizen-walkable ladder shaft through all floor slabs; wall block behind the ladder."""
    dx, dz = {"north": (0, 1), "south": (0, -1), "east": (-1, 0), "west": (1, 0)}[facing]
    for y in range(y_from, y_to + 1):
        b.set(x, y, z, "minecraft:ladder", facing=facing)
        b.set(x + dx, y, z + dz, wall)


def elevator(b: Blueprint, x1, z1, y_bottom, y_top, floors_y, door_side="south", t: Theme = OFFICE):
    """Create elevator: 3x3 shaft (x1..x1+2, z1..z1+2), pulley on top, contacts at each floor.

    Needs one-time setup in game: power the pulley (CC&A electric motor provided next to it),
    super-glue the car, then right-click the pulley to assemble.
    """
    x2, z2 = x1 + 2, z1 + 2
    for y in range(y_bottom, y_top + 1):
        for (x, z) in _perimeter(x1 - 1, z1 - 1, x2 + 1, z2 + 1):
            b.set(x, y, z, t.structure)
        clear(b, x1, y, z1, x2, y, z2)
    # car: floor plate + controls at the bottom stop
    b.fill(x1, y_bottom, z1, x2, y_bottom, z2, "create:andesite_casing")
    b.set(x1 + 1, y_bottom + 1, z1, "create:contraption_controls", facing="south")
    # machine room
    yp = y_top + 1
    b.fill(x1 - 1, yp, z1 - 1, x2 + 1, yp, z2 + 1, t.structure)
    b.set(x1 + 1, yp, z1 + 1, "create:elevator_pulley", facing="north")
    b.set(x1 + 1, yp, z1 + 2, "createaddition:electric_motor", facing="north")
    # landing doors + call contacts
    for fy in floors_y:
        ox, oz = _door_xy(door_side, x1, z1, x2, z2)
        for i in range(3):
            xx, zz = (ox + i, oz) if door_side in ("north", "south") else (ox, oz + i)
            for dy in (1, 2, 3):
                b.set(xx, fy + dy, zz, AIR)
        cx, cz = (ox - 1, oz) if door_side in ("north", "south") else (ox, oz - 1)
        b.set(cx, fy + 2, cz, "create:elevator_contact", facing=door_side)


def street_light(b: Blueprint, x, y, z, arm="east", height=5):
    """Modern street lamp: deepslate pole, slab arm, froglight head (Macaw's double lamp in Complete)."""
    if complete():
        for i, part in enumerate(("base", "bottom", "middle", "top")):
            b.set(x, y + i, z, "mcwlights:double_street_lamp", facing=arm, part=part, lit=True)
        return
    for dy in range(height):
        b.set(x, y + dy, z, "minecraft:polished_deepslate_wall")
    ax, az = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}[arm]
    b.set(x, y + height, z, "minecraft:polished_deepslate")
    b.set(x + ax, y + height, z + az, "minecraft:polished_deepslate_slab", type="top")
    b.set(x + 2 * ax, y + height, z + 2 * az, "minecraft:polished_deepslate_slab", type="top")
    b.set(x + 2 * ax, y + height - 1, z + 2 * az, "minecraft:pearlescent_froglight")


# ---------------- helpers ----------------
def _perimeter(x1, z1, x2, z2):
    for x in range(x1, x2 + 1):
        yield (x, z1)
        yield (x, z2)
    for z in range(z1 + 1, z2):
        yield (x1, z)
        yield (x2, z)


def _is_column(x, z, x1, z1, x2, z2, bay):
    if x in (x1, x2) and z in (z1, z2):
        return True
    if z in (z1, z2):
        return (x - x1) % bay == 0 or x == x2
    return (z - z1) % bay == 0 or z == z2


def _side_xy(side, i, x1, z1, x2, z2):
    return {"north": (i, z1), "south": (i, z2), "west": (x1, i), "east": (x2, i)}[side]


def _door_xy(side, x1, z1, x2, z2):
    return {"north": (x1, z1 - 1), "south": (x1, z2 + 1), "west": (x1 - 1, z1), "east": (x2 + 1, z1)}[side]
