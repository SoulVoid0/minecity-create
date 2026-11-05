# Test modpack

`modpack.json` lists exact 1.21.1 NeoForge files (Modrinth + ldtteam maven) for MineColonies and every
mod the Modern City packs use, including required dependencies. Regenerate with
`python3 tools/modpack/resolve.py > tools/modpack/modpack.json`.

Needs **NeoForge 21.1.265 or newer** (Create 6.0.10 and CC&A 1.7.2 require it).

## Self-test
Start a server (or client) with `-Dmoderncity.selftest=true` (or `=exit` to stop afterwards). Every
blueprint of every pack whose mods are loaded is checked against the live block, property and
block-entity registries; the log ends with `[Modern City selftest] DONE, N problem(s)`.
Last run (2026-11-05, 45 mods): Modern City 225, Lite 225, Complete 240 blueprints, 0 problems.
