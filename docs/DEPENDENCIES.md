# Dependencies (Minecraft 1.21.1, NeoForge)

**Required:** MineColonies (+ Structurize). **Everything else is optional**: the full *Modern City* pack needs Create, AE2 and Create Crafts & Additions; *Modern City Lite* needs nothing extra.

Checked 2026-11-05 via mod-listing mirrors (Modrinth/CurseForge were not directly reachable from the build environment).

| Mod | 1.21.1 NeoForge? | Version seen | Mod id | Role |
|---|---|---|---|---|
| MineColonies (+ Structurize, BlockUI, Domum Ornamentum) | Yes | 1.1.x | minecolonies / structurize / blockui / domum_ornamentum | Core |
| Create | Yes | 6.0.x | create | Kinetics, elevators, trains |
| Macaw's suite (Bridges, Roofs, Windows, Doors, Trapdoors, Fences, Lights & Lamps, Paths & Pavings, Stairs, Furniture) | Yes | per mod | mcw* | Architecture |
| Applied Energistics 2 | Yes | 19.x | ae2 | Data centers |
| Create Crafts & Additions | Yes | 1.6.0 | createaddition | Electricity, power lines |
| Applied Create | Yes (needs Kotlin for Forge 5+) | 1.1.8 | appliedcreate (verify) | AE2 ↔ Create |
| Applied Generators | Yes | 0.3.1+1.21.1 | appgen (verify) | AE2 power |
| Chipped | Yes | 4.x | chipped | Block variants |
| TaCZ | **Unofficial port only** ("[UNOFFICIAL] TaCZ NeoForge Port", tacz-1.21.1) | — | tacz | Military |
| Cold Sweat | Yes | 2.4.x | cold_sweat | Climate |
| Create: The Factory Must Grow | Yes | 1.2.0 | tfmg | Heavy industry, oil, steel |
| Extended AE | Yes | 1.21.1-2.x | extendedae | Data centers |
| Create: Diesel Generators | Yes | 1.3.15 | createdieselgenerators | Power plants |
| Create: Radars | Yes | 0.4.9.x | create_radar (verify) | Military |
| Create Nuclear | Yes | 1.3.2 | createnuclear | Power plants |
| Steam 'n' Rails | **Separate NeoForge port** ("Steam 'n' Rails Neoforge" on CurseForge) | — | railways | Trains |
| Create Ore Excavation | Yes | 1.6.8 | createoreexcavation | Mines |
| "AE2 addons" | Interpreted as: AE2WTLib, MEGA Cells, Applied Flux, AdvancedAE | — | — | Data centers |

## Added for the build
- Kotlin for Forge 5.x (required by Applied Create)
- Create: New Age (optional, electric motors and solar for power plants)
- JEI (dev convenience)

## Not available / substitutions
- TaCZ: no official 1.21.1 NeoForge build; using the unofficial port. Blueprints only reference TaCZ blocks in armory interiors, so a missing TaCZ leaves gaps, not failures.
- Steam 'n' Rails: use the NeoForge port listed above.

## Verified from 1.21.1 NeoForge jars (Modrinth, 2026-11-05)

Block ids for every mod below were read from the jar's blockstates and stored in `tools/blueprintgen/ids/`.

| Modrinth project | Mod id | Version checked |
|---|---|---|
| macaws-windows | `mcwwindows` | 2.4.2 |
| macaws-roofs | `mcwroofs` | 2.3.2 |
| macaws-lights-and-lamps | `mcwlights` | 1.1.5 |
| macaws-bridges | `mcwbridges` | 3.1.2 |
| macaws-paths-and-pavings | `mcwpaths` | 1.1.1 |
| macaws-doors | `mcwdoors` | 1.1.5 |
| macaws-fences-and-walls | `mcwfences` | 1.2.1 |
| macaws-furniture | `mcwfurnitures` | 3.4.1 |
| macaws-stairs | `mcwstairs` | 1.0.2 |
| macaws-trapdoors | `mcwtrpdoors` | 1.1.5 |
| chipped | `chipped` | 4.0.2 |
| tacz-1.21.1 | `tacz` | 1.1.8-hotfix-r7 |
| cold-sweat | `cold_sweat` | 2.4.5 |
| create-tfmg | `tfmg` | 1.2.0 |
| extended-ae | `extendedae` | 1.21-2.2.35-neoforge |
| create-diesel-generators | `createdieselgenerators` | 1.21.1-1.3.15 |
| create-radars | `create_radar` | 5.0.3-1.21.1 |
| createnuclear | `createnuclear` | 2.0.0 |
| create-steam-n-rails-1.21.1 | `railways` | 0.3.0-beta.2+neoforge-mc1.21.1 |
| create-ore-excavation | `createoreexcavation` | 1.21.1-1.6.8 |
| applied-create | `appliedcreate` | 1.1.8 |
| applied-generators | `appgen` | 0.3.1+1.21.1 |
| mega | `megacells` | 4.11.0 |
| appflux | `appflux` | 1.21-2.1.5-neoforge |
| advancedae | `advanced_ae` | 1.6.12-1.21.1 |
| create-new-age | `create_new_age` | 1.2.0+mc1.21.1 |

## Which pack needs what
- **Modern City Lite**: MineColonies only.
- **Modern City**: + Create, AE2, Create Crafts & Additions.
- **Modern City Complete**: + Macaw's Bridges/Doors/Fences/Furniture/Lights/Paths/Roofs/Stairs/Trapdoors/Windows, Chipped, TFMG, Create Diesel Generators, Create Nuclear, Create Radars, Steam 'n' Rails, Create Ore Excavation, Create: New Age, ExtendedAE, MEGA Cells, AdvancedAE, Applied Create, Applied Generators, Applied Flux, TaCZ, Cold Sweat.
  AE2WTLib needs no blocks, so it works alongside any pack.
