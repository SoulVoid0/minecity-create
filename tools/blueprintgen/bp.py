"""Structurize v1 blueprint writer.

Mirrors com.ldtteam.structurize.blueprints.v1.BlueprintUtil#writeBlueprintToNBT (Structurize version/1.21)
and the hut block-entity layout MineColonies writes when a building is scanned.
"""
from __future__ import annotations

import gzip
import io
from dataclasses import dataclass, field

import nbtlib
from nbtlib import Byte, Compound, Int, IntArray, List, Short, String

# Minecraft 1.21.1 data version, matches what MineColonies' own 1.21 blueprints carry.
DATA_VERSION = 3955
PACK_NAME = "Modern City"

AIR = "minecraft:air"
KEEP = "structurize:blocksubstitution"        # leave whatever is in the world
FILL = "structurize:blocksolidsubstitution"   # fill with a solid block if the world has air/fluid


def state(spec: str, **props) -> tuple:
    """Parse 'ns:block[k=v,k2=v2]' plus keyword props into a hashable state."""
    name = spec
    parsed = {}
    if "[" in spec:
        name, rest = spec.split("[", 1)
        for kv in rest.rstrip("]").split(","):
            if kv:
                k, v = kv.split("=")
                parsed[k.strip()] = v.strip()
    parsed.update({k: str(v).lower() if isinstance(v, bool) else str(v) for k, v in props.items()})
    if ":" not in name:
        name = "minecraft:" + name
    return name, tuple(sorted(parsed.items()))


def _pos(x, y, z) -> Compound:
    return Compound({"x": Int(x), "y": Int(y), "z": Int(z)})


def _empty_inventory(slots: int = 27) -> List:
    return List[Compound]([Compound({"empty": Byte(1)}) for _ in range(slots)])


@dataclass
class Blueprint:
    name: str           # file name without extension, e.g. "townhall3"
    folder: str         # path inside the pack, e.g. "fundamentals"
    sx: int
    sy: int
    sz: int
    blocks: dict = field(default_factory=dict)   # (x,y,z) -> state
    tes: dict = field(default_factory=dict)      # (x,y,z) -> dict of extra TE fields (must include 'id')
    tags: dict = field(default_factory=dict)     # absolute (x,y,z) -> [tag,...]
    anchor: tuple | None = None
    hut_te_id: str | None = None
    hut_tags: list = field(default_factory=list)  # tags on the anchor itself (relative 0,0,0)
    pack_name: str = PACK_NAME

    # ---------- editing ----------
    def inside(self, x, y, z) -> bool:
        return 0 <= x < self.sx and 0 <= y < self.sy and 0 <= z < self.sz

    def set(self, x, y, z, spec, te: dict | None = None, **props):
        if not self.inside(x, y, z):
            raise IndexError(f"{self.name}: {(x, y, z)} outside {(self.sx, self.sy, self.sz)}")
        st = spec if isinstance(spec, tuple) else state(spec, **props)
        self.blocks[(x, y, z)] = st
        if te is not None:
            self.tes[(x, y, z)] = te
        else:
            self.tes.pop((x, y, z), None)

    def get(self, x, y, z):
        return self.blocks.get((x, y, z), state(AIR))

    def fill(self, x1, y1, z1, x2, y2, z2, spec, **props):
        st = spec if isinstance(spec, tuple) else state(spec, **props)
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, st)

    def tag(self, x, y, z, *names):
        self.tags.setdefault((x, y, z), []).extend(names)

    def hut(self, x, y, z, hut_block: str, facing: str, te_id: str = "minecolonies:colonybuilding"):
        """Place the building's hut block; it becomes the blueprint anchor."""
        self.set(x, y, z, hut_block, facing=facing)
        self.anchor = (x, y, z)
        self.hut_te_id = te_id

    def rack(self, x, y, z, facing="north", variant="blockrackempty"):
        self.set(x, y, z, "minecolonies:blockminecoloniesrack", variant=variant, facing=facing,
                 te={"id": "minecolonies:rack"})

    def bed(self, x, y, z, facing, color="white"):
        """Bed whose head is at (x,y,z); foot is one block opposite to facing."""
        dx, dz = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}[facing]
        self.set(x, y, z, f"minecraft:{color}_bed", part="head", facing=facing, occupied=False,
                 te={"id": "minecraft:bed"})
        self.set(x - dx, y, z - dz, f"minecraft:{color}_bed", part="foot", facing=facing, occupied=False,
                 te={"id": "minecraft:bed"})

    # ---------- serialisation ----------
    @property
    def path(self) -> str:
        return f"{self.folder}/{self.name}.blueprint"

    def primary_offset(self) -> tuple:
        return self.anchor if self.anchor else (self.sx // 2, 0, self.sz // 2)

    def mods(self) -> list:
        ns = sorted({s[0].split(":")[0] for s in self.blocks.values()} |
                    {t["id"].split(":")[0] for t in self.tes.values()})
        return [m for m in ns if m not in ("minecraft", "structurize")]

    def _hut_te(self) -> Compound:
        ax, ay, az = self.anchor
        c1 = (-ax, -ay, -az)
        c2 = (self.sx - 1 - ax, self.sy - 1 - ay, self.sz - 1 - az)
        rel_tags = {}
        if self.hut_tags:
            rel_tags[(0, 0, 0)] = list(self.hut_tags)
        for (x, y, z), names in self.tags.items():
            rel_tags.setdefault((x - ax, y - ay, z - az), []).extend(names)
        pos_tag_map = List[Compound]([
            Compound({"tagPos": _pos(*p),
                      "tagNameList": List[Compound]([Compound({"tagName": String(n)}) for n in names])})
            for p, names in rel_tags.items()
        ])
        provider = Compound({
            "schematicName": String(self.name),
            "corner1": _pos(*c1),
            "corner2": _pos(*c2),
            "posTagMap": pos_tag_map,
            "pack": String(self.pack_name),
            "path": String(self.path),
        })
        return Compound({
            "id": String(self.hut_te_id),
            "x": Short(ax), "y": Short(ay), "z": Short(az),
            "mirror": Byte(0),
            "inWarehouse": Byte(1 if self.hut_te_id == "minecolonies:warehouse" else 0),
            "colony": Int(0),
            "inventory": _empty_inventory(),
            "type": String(self.hut_te_id),
            "version": Int(0),
            "tagSIze": Int(0),
            "Item": String(""),
            "pack": String(self.pack_name),
            "path": String(self.path),
            "blueprintDataProvider": provider,
        })

    def to_nbt(self) -> Compound:
        palette = [state(AIR)]
        index = {state(AIR): 0}
        flat = []
        for y in range(self.sy):
            for z in range(self.sz):
                for x in range(self.sx):
                    st = self.blocks.get((x, y, z), palette[0])
                    if st not in index:
                        index[st] = len(palette)
                        palette.append(st)
                    flat.append(index[st])
        if len(palette) > 32767:
            raise ValueError(f"{self.name}: palette too large")

        # Structurize packs two shorts per int, high half first; odd tail goes in the high half.
        ints = []
        for i in range(0, len(flat), 2):
            hi = flat[i]
            lo = flat[i + 1] if i + 1 < len(flat) else 0
            v = (hi << 16) | lo
            ints.append(v - (1 << 32) if v >= (1 << 31) else v)

        pal_tag = List[Compound]()
        for name, props in palette:
            c = Compound({"Name": String(name)})
            if props:
                c["Properties"] = Compound({k: String(v) for k, v in props})
            pal_tag.append(c)

        te_list = List[Compound]()
        for (x, y, z), extra in sorted(self.tes.items()):
            c = Compound({"x": Short(x), "y": Short(y), "z": Short(z)})
            for k, v in extra.items():
                if k == "id":
                    c["id"] = String(v)
                else:
                    c[k] = v
            if extra["id"] == "minecolonies:rack":
                c.setdefault("inventory", _empty_inventory())
            te_list.append(c)
        if self.anchor:
            te_list.append(self._hut_te())

        ox, oy, oz = self.primary_offset()
        return Compound({
            "version": Byte(1),
            "size_x": Short(self.sx), "size_y": Short(self.sy), "size_z": Short(self.sz),
            "palette": pal_tag,
            "blocks": IntArray(ints),
            "tile_entities": te_list,
            "entities": List[Compound](),
            "required_mods": List[String]([String(m) for m in self.mods()]),
            "name": String(self.name),
            "architects": List[String]([String("SoulVoid0"), String("Modern City generator")]),
            "mcversion": Int(DATA_VERSION),
            "optional_data": Compound({"structurize": Compound({"primary_offset": _pos(ox, oy, oz)})}),
        })

    def write(self, root) -> str:
        import os
        out = os.path.join(root, self.path)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        buf = io.BytesIO()
        nbtlib.File(self.to_nbt()).write(buf)  # big-endian, unnamed root like NbtIo
        # mtime=0 and no file name in the header keep output byte-identical between runs
        with open(out, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as fh:
            fh.write(buf.getvalue())
        return out
