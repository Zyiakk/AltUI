"""Objects tab (docs/specs/2026-10-23-objects-tab-design.md): constants and the rules the manager's graphs follow (gen_manager_ui.py,
section "Objects tab"), written once in Python so the tests can check them.

The catalogue comes from the asset registry at runtime - nothing of the game goes into the pak, only paths are kept. The game's
own models are known to the registry (the game ships AssetRegistry.bin); mod paks are not (measured 2026-09-23, see
docs/specs/2026-09-23-blueprint-loader-discovery.md). AltUI scans them folder by folder (the rows of DLC_MainTable), one folder per
step, and keeps what it found in a save of its own, so only new mod folders are scanned at the next start (ui-test-148: one scan of
all of /Game/Mod/ held the game ~33 s)."""
import re

PROP = "/Game/Mod/AltUI/BP_AltUIProp"
SG_PROPS, PROPS_SLOT = "/Game/Mod/AltUI/SG_Props", "AltUI_Props"   # scenes + positions: Saved/SaveGames/AltUI_Props.sav (spec "Speichern")
S_PROPOBJ, S_PROPSCENE, S_PROPPLACE = "/Game/Mod/AltUI/S_PropObj", "/Game/Mod/AltUI/S_PropScene", "/Game/Mod/AltUI/S_PropPlace"
CACHE_SG, CACHE_SLOT = "/Game/Mod/AltUI/SG_ObjCache", "AltUI_ObjCache"   # mod models found so far: Saved/SaveGames/AltUI_ObjCache.sav
MAP_PREFIX = "Map_"         # map paks: pak "Map_<X>", content in /Game/Mod/<X>/ -> both folders are scanned
SCAN_STEP = 0.01             # s between two mod folders of the scan (one folder per step, the game keeps running)
ROOT_MODELS, ROOT_MAPS, ROOT_MODS = "/Game/Project/Models/", "/Game/Project/Maps/", "/Game/Mod/"
ROOTS = (ROOT_MODELS, ROOT_MAPS, ROOT_MODS)
WEAPON_FOLDER = "Weapon"     # Models/Weapon -> category "Weapons"
OWN_MOD = "AltUI"            # AltUI's own meshes (joint spheres, ...) are no catalogue entries
SPAWN_DIST = 200.0           # cm in front of Jodi, in the camera's direction (as the ragdolls: from the camera it would land on her)
SPAWN_TRACE_UP, SPAWN_TRACE_DOWN = 200.0, 2000.0
ICON_DIR = "SaveGames/ObjectIcons/"
ICON_SIZE = 224               # px: the largest tile shows the picture ~217 px wide at 2560x1440 (88 units x 1.9 x 200 % x ~0.65 px)
PAGE = 120                   # tiles per "show more" step (a category can hold ~1700 models)
FAV_PREFIX = "prop:"         # favourites: "prop:<object path>" in Settings.Favorites
SORT_STEPS = 14              # binary search steps (2^14 > any catalogue)
CAT_ALL, CAT_FAV, CAT_WEAPONS, CAT_MODS = "All", "Fav", "Weapons", "Mods"
CAT_WORLD, CAT_SCENES = "InWorld", "Scenes"   # WORLD part of the left column
SCALE_STEP, SCALE_MIN, SCALE_MAX = 1.1, 0.05, 20.0   # Ctrl + wheel while dragging: x1.1 per notch
TURN_DEG = 0.5               # right drag: degrees per pixel (as the ragdolls)


def category(package_path):
    """Category of a model by its package path, None = not in the catalogue. Models/<folder> -> folder (Models/Weapon -> Weapons),
    Maps/<level> -> Map:<level>, Mod/<mod> -> Mod:<mod> (not AltUI)."""
    for root in ROOTS:
        if package_path.startswith(root):
            first = package_path[len(root):].split("/", 1)[0]
            if not first: return None
            if root == ROOT_MODELS: return "Weapons" if first == WEAPON_FOLDER else first
            if root == ROOT_MAPS: return "Map:" + first
            return None if first == OWN_MOD else "Mod:" + first
    return None


def display_name(asset):
    """Asset name -> shown name: prefix SM_ / S_ off, a space where a small letter meets a capital, "_" -> space."""
    for p in ("SM_", "S_"):
        if asset.startswith(p): asset = asset[len(p):]; break
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", asset).replace("_", " ")


def scan_folders(row):
    """Mod folders the quick scan tries for one row of DLC_MainTable (= pak name). Content in folders named otherwise (a mod
    shipping a second folder) only the full scan finds (ui-test-149: TKA_StripClub in ToxicVelvet.pak, ...)."""
    if row == OWN_MOD: return []
    return [row] + ([row[len(MAP_PREFIX):]] if row.startswith(MAP_PREFIX) and len(row) > len(MAP_PREFIX) else [])


def cat_sort_str(cat, caption=None):
    """Order of the left column: the game's model folders, then the levels, Weapons, the mods - each alphabetically; a mod by the
    name the row shows (caption; its folder name can differ a lot, ui-test-150)."""
    if cat.startswith("Map:"): return "2" + cat[4:]
    if cat.lower().startswith("mod:"): return "4" + (caption if caption is not None else cat[4:])
    if cat == CAT_WEAPONS: return "3"
    return "1" + cat


def is_mod_cat(cat):
    return cat.lower().startswith("mod:")


def in_cat(sel, cat, fav):
    """Does a model of category `cat` (fav = it is a favourite) show under the selected left entry `sel`?"""
    if sel == CAT_ALL: return True
    if sel == CAT_FAV: return fav
    if sel == CAT_MODS: return is_mod_cat(cat)
    return sel.lower() == cat.lower()


def matches(search, name, asset):
    """Search box: empty, or contained (ignoring case) in the shown name or the asset name."""
    s = search.lower()
    return not s or s in name.lower() or s in asset.lower()


def scaled(scale, notches):
    """Ctrl + wheel: the new uniform scale."""
    return min(SCALE_MAX, max(SCALE_MIN, scale * SCALE_STEP ** notches))
