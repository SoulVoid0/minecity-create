"""Resolve the Modern City test modpack (MC 1.21.1, NeoForge) into exact download URLs.

    python3 tools/modpack/resolve.py > tools/modpack/modpack.json

Modrinth projects are resolved with their required dependencies; the MineColonies chain comes from
the ldtteam maven (MineColonies is not published for NeoForge on Modrinth).
"""
import json
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "moderncity-modpack-resolver/0.1"}
MODRINTH = [
    "create", "ae2", "createaddition",
    "macaws-windows", "macaws-roofs", "macaws-lights-and-lamps", "macaws-bridges", "macaws-paths-and-pavings",
    "macaws-doors", "macaws-fences-and-walls", "macaws-furniture", "macaws-stairs", "macaws-trapdoors",
    "chipped", "tacz-1.21.1", "cold-sweat", "create-tfmg", "extended-ae", "create-diesel-generators",
    "create-radars", "createnuclear", "create-steam-n-rails-1.21.1", "create-ore-excavation", "applied-create",
    "applied-generators", "mega", "appflux", "advancedae", "applied-energistics-2-wireless-terminals",
    "create-new-age", "create-big-cannons", "jei",
]
LDT = "https://ldtteam.jfrog.io/artifactory"
MAVEN = [
    ("minecolonies", f"{LDT}/ldtteam/com/ldtteam/minecolonies/1.1.1403-1.21.1/minecolonies-1.1.1403-1.21.1.jar"),
    ("structurize", f"{LDT}/ldtteam/com/ldtteam/structurize/1.0.832-1.21.1/structurize-1.0.832-1.21.1.jar"),
    ("blockui", f"{LDT}/ldtteam/com/ldtteam/blockui/1.0.209-1.21.1/blockui-1.0.209-1.21.1.jar"),
    ("domum_ornamentum", f"{LDT}/mods-maven/com/ldtteam/domum-ornamentum/1.0.231/domum-ornamentum-1.0.231-main.jar"),
    ("multipiston", f"{LDT}/ldtteam/com/ldtteam/multipiston/1.2.58-1.21.1/multipiston-1.2.58-1.21.1.jar"),
]


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA)))


def latest_version(project):
    q = urllib.parse.urlencode({"loaders": '["neoforge"]', "game_versions": '["1.21.1"]'})
    vs = get(f"https://api.modrinth.com/v2/project/{project}/version?{q}")
    rel = [v for v in vs if v["version_type"] == "release"] or vs
    return rel[0] if rel else None


def main():
    seen, out, todo, files = set(), [], list(MODRINTH), set()
    while todo:
        p = todo.pop(0)
        if p in seen:
            continue
        seen.add(p)
        v = latest_version(p)
        if not v:
            print(f"warning: {p} has no 1.21.1 NeoForge build", file=sys.stderr)
            continue
        f = next((x for x in v["files"] if x["primary"]), v["files"][0])
        seen.add(v["project_id"])
        if f["filename"] in files:
            continue
        files.add(f["filename"])
        proj = get(f"https://api.modrinth.com/v2/project/{v['project_id']}")
        out.append({"name": proj["title"], "slug": proj["slug"], "version": v["version_number"],
                    "file": f["filename"], "url": f["url"], "sha1": f["hashes"]["sha1"]})
        seen.add(proj["slug"])
        for d in v["dependencies"]:
            if d["dependency_type"] == "required" and d.get("project_id") and d["project_id"] not in seen:
                todo.append(d["project_id"])
    for name, url in MAVEN:
        out.append({"name": name, "slug": name, "version": url.split("/")[-2], "file": url.split("/")[-1], "url": url})
    json.dump({"minecraft": "1.21.1", "loader": "neoforge", "mods": out}, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
