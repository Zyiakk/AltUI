import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def key(mgr, name):
    mgr.call_method("Test Look Key", args=(name,)); return str(mgr.get_editor_property("TmpName"))

def count(mgr, t, filtered=False):
    mgr.call_method("Test Look Count", args=(t, filtered)); return mgr.get_editor_property("TmpI")

def groups(mgr, t="All"):
    mgr.call_method("Test Collect Look Rows", args=(t,)); mgr.call_method("Test Look Groups"); return [str(n) for n in mgr.get_editor_property("TmpNames")]

def names(mgr, prop): return [str(n) for n in mgr.get_editor_property(prop)]

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Strings", args=(1,)); mgr.call_method("Test Load Names")
    mgr.set_editor_property("Favorites", []); mgr.set_editor_property("HiddenItems", []); mgr.set_editor_property("LookGroup", "None"); mgr.set_editor_property("LookOnlyFav", False); mgr.set_editor_property("LookSearchText", "")
    # keys: skin table row -> skin:, everything else (make-up, eyes) -> makeup:
    expect("look keys", (key(mgr, "Skin_Default"), key(mgr, "Lips_01"), key(mgr, "Eye_1")), ("skin:Skin_Default", "makeup:Lips_01", "makeup:Eye_1"))
    # collected rows: skins, MakeupTable rows, EyeTable rows (stub tables)
    mgr.call_method("Test Collect Look Rows", args=("All",))
    expect("rows of All", list(zip(names(mgr, "LookRowKinds"), names(mgr, "LookRows"))), [("skin", "Skin_Default"), ("makeup", "Eyebrow_01"), ("makeup", "Lips_01"), ("makeup", "Lips_02"), ("makeup", "Eye_1")])
    mgr.call_method("Test Collect Look Rows", args=("Lips",)); expect("rows of Lips", names(mgr, "LookRows"), ["Lips_01", "Lips_02"])
    mgr.call_method("Test Collect Look Rows", args=("Eye",)); expect("rows of Eye (EyeTable)", names(mgr, "LookRows"), ["Eye_1"])
    mgr.call_method("Test Collect Look Rows", args=("Presets",)); expect("presets: no rows", names(mgr, "LookRows"), [])
    # favourites / hidden with the prefixed keys
    mgr.call_method("Test Toggle Look Favorite", args=("Lips_01",)); expect("favourite added", names(mgr, "Favorites"), ["makeup:Lips_01"])
    mgr.call_method("Test Toggle Look Favorite", args=("Lips_01",)); expect("favourite removed", names(mgr, "Favorites"), [])
    mgr.call_method("Test Toggle Look Favorite", args=("Skin_Default",)); expect("skin favourite", names(mgr, "Favorites"), ["skin:Skin_Default"])
    mgr.call_method("Test Toggle Look Hidden", args=("Lips_01",)); expect("hidden added", names(mgr, "HiddenItems"), ["makeup:Lips_01"])
    # chips: Vanilla + one per mod (ItemOriginMod), Hidden last while a row is hidden
    origin = mgr.get_editor_property("ItemOriginMod"); origin["Lips_02"] = "ModA"; mgr.set_editor_property("ItemOriginMod", origin)
    expect("groups of All", groups(mgr), ["Vanilla", "ModA", "Hidden"])
    expect("groups of Skin (nothing to choose)", groups(mgr, "Skin"), ["Vanilla"])
    # counts: total ignores the filters; filtered = chip + only favourites (+ search)
    expect("total All", count(mgr, "All"), 5)
    expect("All, no filter: hidden row dropped", count(mgr, "All", True), 4)
    mgr.set_editor_property("LookGroup", "ModA"); expect("chip ModA", count(mgr, "All", True), 1)
    mgr.set_editor_property("LookGroup", "Vanilla"); expect("chip Vanilla (Lips_01 hidden)", count(mgr, "All", True), 3)
    mgr.set_editor_property("LookGroup", "Hidden"); expect("chip Hidden", count(mgr, "All", True), 1)
    mgr.set_editor_property("LookGroup", "None"); mgr.set_editor_property("LookOnlyFav", True); expect("only favourites", (count(mgr, "All", True), count(mgr, "Skin", True), count(mgr, "Lips", True)), (1, 1, 0))
    mgr.set_editor_property("LookSearchText", "skin"); expect("search + only favourites", count(mgr, "All", True), 1); mgr.set_editor_property("LookSearchText", "lips_0"); expect("search miss on favourites", count(mgr, "All", True), 0)
    mgr.set_editor_property("LookSearchText", ""); mgr.set_editor_property("LookOnlyFav", False)
    # unhide: chip Hidden without a hidden row left -> All
    mgr.set_editor_property("LookGroup", "Hidden"); mgr.call_method("Test Toggle Look Hidden", args=("Lips_01",)); expect("unhidden", names(mgr, "HiddenItems"), []); expect("chip back to All", str(mgr.get_editor_property("LookGroup")), "None")
    expect("groups without hidden", groups(mgr), ["Vanilla", "ModA"])
    # category change keeps the chip when the new category has that group, else All (Select Look Cat; Panel is None in the editor -> widgets untouched)
    mgr.set_editor_property("LookGroup", "ModA"); mgr.call_method("Test Select Look Cat", args=("Lips",)); expect("chip kept (Lips has ModA)", str(mgr.get_editor_property("LookGroup")), "ModA")
    mgr.call_method("Test Select Look Cat", args=("Skin",)); expect("chip dropped (Skin has no ModA)", str(mgr.get_editor_property("LookGroup")), "None")
    mgr.set_editor_property("LookGroup", "Vanilla"); mgr.call_method("Test Select Look Cat", args=("All",)); expect("Vanilla kept", str(mgr.get_editor_property("LookGroup")), "Vanilla")
    mgr.set_editor_property("LookCat", "Skin")
    # MergeMods: mods with the same shown name share one chip and one filter (own option, appearance only)
    def alias(mod):
        mgr.call_method("Test Mod Alias", args=(mod,)); return str(mgr.get_editor_property("TmpName"))
    origin["Eyebrow_01"] = "ModB"; mgr.set_editor_property("ItemOriginMod", origin); mgr.set_editor_property("ModList", ["ModA", "ModB"])
    mgr.call_method("Test Set Custom Name", args=("mod", "ModA", "Same")); mgr.call_method("Test Set Custom Name", args=("mod", "ModB", "Same"))
    mgr.set_editor_property("MergeMods", True); mgr.call_method("Test Build Group Aliases")
    expect("merge mods: alias", (alias("ModA"), alias("ModB"), alias("Vanilla")), ("ModA", "ModA", "Vanilla"))
    expect("merge mods: one chip", groups(mgr), ["Vanilla", "ModA"])
    mgr.set_editor_property("LookGroup", "ModA"); expect("merge mods: filter joins both", count(mgr, "All", True), 2)
    # renaming one of them apart ends the merge (Set Custom Name marks the catalog dirty; the appearance page rebuilds it like the clothes page)
    mgr.call_method("Test Set Custom Name", args=("mod", "ModB", "Other")); expect("rename marks dirty", mgr.get_editor_property("CatalogDirty"), True)
    mgr.call_method("Test Select Page", args=("Look",)); expect("appearance page rebuilds the dirty catalog", mgr.get_editor_property("CatalogDirty"), False)
    origin = mgr.get_editor_property("ItemOriginMod"); origin["Lips_02"] = "ModA"; origin["Eyebrow_01"] = "ModB"; mgr.set_editor_property("ItemOriginMod", origin); mgr.set_editor_property("ModList", ["ModA", "ModB"])   # Build Catalog rescanned the stub tables (the map proxy is live)
    mgr.call_method("Test Build Group Aliases"); expect("renamed apart: own alias", alias("ModB"), "ModB")
    mgr.call_method("Test Set Custom Name", args=("mod", "ModB", "Same")); mgr.call_method("Test Build Group Aliases")
    mgr.set_editor_property("MergeMods", False); mgr.call_method("Test Build Group Aliases")
    expect("merge mods off: identity", alias("ModB"), "ModB"); expect("merge mods off: two chips (row order)", groups(mgr), ["Vanilla", "ModB", "ModA"]); expect("merge mods off: own filter", count(mgr, "All", True), 1)
    mgr.set_editor_property("LookGroup", "None"); mgr.call_method("Test Set Custom Name", args=("mod", "ModA", "")); mgr.call_method("Test Set Custom Name", args=("mod", "ModB", "")); del origin["Eyebrow_01"]; mgr.set_editor_property("ModList", [])
    # settings roundtrip
    mgr.set_editor_property("LookOnlyFav", True); mgr.set_editor_property("LookChipsCollapsed", True); mgr.call_method("Test Save Settings")
    mgr.set_editor_property("LookOnlyFav", False); mgr.set_editor_property("LookChipsCollapsed", False); mgr.call_method("Test Load Settings")
    expect("settings roundtrip", (mgr.get_editor_property("LookOnlyFav"), mgr.get_editor_property("LookChipsCollapsed"), names(mgr, "Favorites")), (True, True, ["skin:Skin_Default"]))
    # clean up
    del origin["Lips_02"]; mgr.set_editor_property("ItemOriginMod", origin)
    mgr.set_editor_property("Favorites", []); mgr.set_editor_property("HiddenItems", []); mgr.set_editor_property("LookOnlyFav", False); mgr.set_editor_property("LookChipsCollapsed", False); mgr.set_editor_property("LookGroup", "None"); mgr.call_method("Test Save Settings")
run(main)
