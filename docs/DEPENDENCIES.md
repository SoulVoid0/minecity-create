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
