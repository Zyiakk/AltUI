import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def filtered(mgr, slot, group):
    mgr.call_method("Test Filter", args=(slot, group, "", False, False, False))
    return [str(n) for n in mgr.get_editor_property("TmpNames")]

def groups(mgr, slot):
    mgr.call_method("Test Groups", args=(slot,))
    return [str(n) for n in mgr.get_editor_property("TmpNames")]

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build"); mgr.call_method("Test Strings", args=(1,))   # English strings -> captions "No group"/"Hidden"
    mgr.set_editor_property("HiddenItems", []); mgr.set_editor_property("Favorites", []); mgr.set_editor_property("PanelOpen", False)
    expect("neck groups before", sorted(groups(mgr, "Neck")), ["Basis", "Kpop"])
    mgr.call_method("Test Toggle Hidden", args=("Zeta_Neck",))
    expect("hidden gone from list", filtered(mgr, "Neck", "None"), ["Alpha_Neck", "Casual_Mina_Neck"])
    expect("hidden gone from All", "Zeta_Neck" in filtered(mgr, "All", "None"), False)
    expect("hidden subtab", filtered(mgr, "Neck", "Hidden"), ["Zeta_Neck"])
    expect("neck groups with hidden", groups(mgr, "Neck")[-1], "Hidden"); expect("neck groups count", len(groups(mgr, "Neck")), 3)
    expect("all groups with hidden", groups(mgr, "All")[-1], "Hidden")
    expect("boots groups unchanged", groups(mgr, "Boots"), ["Basis"])
    mgr.call_method("Test Group Caption", args=("Hidden",)); expect("caption hidden", str(mgr.get_editor_property("TmpText")), "Hidden")
    mgr.call_method("Test Toggle Hidden", args=("Zeta_Neck",))
    expect("unhidden back", filtered(mgr, "Neck", "None"), ["Alpha_Neck", "Casual_Mina_Neck", "Zeta_Neck"])
    expect("neck groups after", sorted(groups(mgr, "Neck")), ["Basis", "Kpop"])
    # persistence: hidden + toggles survive Save/Load Settings
    mgr.call_method("Test Toggle Hidden", args=("Alpha_Neck",))
    mgr.call_method("Test Set Toggles", args=(True, False)); mgr.call_method("Test Save Settings")
    mgr.set_editor_property("HiddenItems", []); mgr.set_editor_property("CachedOnlyOwned", False); mgr.set_editor_property("CachedOnlyFav", True)
    mgr.call_method("Test Load Settings")
    expect("hidden reloaded", [str(n) for n in mgr.get_editor_property("HiddenItems")], ["Alpha_Neck"])
    expect("owned toggle reloaded", mgr.get_editor_property("CachedOnlyOwned"), True)
    expect("fav toggle reloaded", mgr.get_editor_property("CachedOnlyFav"), False)
    mgr.call_method("Test Toggle Hidden", args=("Alpha_Neck",)); mgr.call_method("Test Save Settings")
    # tooltip: shown name, [Default: default when a custom name is set], "s: " slot label, origin (Vanilla / "PAK: " caption + "pak: " id),
    # ["G: " group caption + "g: " id], "id: " row - the id lines always (since 2026-09-21), TipNoIds drops them  (spec docs/specs/2026-09-20-tooltip-prefixes-design.md)
    def tip(name, kind="item", category=""):
        mgr.call_method("Test Item Tip", args=(name, kind, category)); return str(mgr.get_editor_property("TmpText")).split("\n")
    expect("tip lines", tip("Casual_Mina_Neck"), ["Casual_Mina_Neck", "s: Neck", "Vanilla", "G: KPOP", "g: Kpop", "id: Casual_Mina_Neck"])
    expect("tip vanilla without group", tip("Zeta_Neck"), ["Zeta_Neck", "s: Neck", "Vanilla", "id: Zeta_Neck"])
    expect("tip mod origin", tip("ModThing"), ["ModThing", "s: Top", "PAK: Some Mod", "pak: SomeMod", "G: SomeGroup", "g: SomeGroup", "id: ModThing"])   # caption of the SomeMod row in the stub DLC_MainTable
    mgr.call_method("Test Load Names"); mgr.call_method("Test Set Custom Name", args=("item", "ModThing", "Fancy Thing")); mgr.call_method("Test Build")
    expect("tip with custom name", tip("ModThing"), ["Fancy Thing", "Default: ModThing", "s: Top", "PAK: Some Mod", "pak: SomeMod", "G: SomeGroup", "g: SomeGroup", "id: ModThing"])
    mgr.call_method("Test Set Custom Name", args=("mod", "SomeMod", "My Mod")); mgr.call_method("Test Set Custom Name", args=("group", "SomeGroup", "Nice Group"))
    expect("tip with custom mod + group names", tip("ModThing")[3:7], ["PAK: My Mod", "pak: SomeMod", "G: Nice Group", "g: SomeGroup"])
    # look tiles: the category text is the "s:" line, no group
    expect("tip hair", tip("TestHair", "hair", "Hair"), ["TestHair", "s: Hair", "Vanilla", "id: TestHair"])
    mgr.call_method("Test Set Custom Name", args=("hair", "TestHair", "Bob")); expect("tip hair custom name", tip("TestHair", "hair", "Hair")[:2], ["Bob", "Default: TestHair"])
    mgr.call_method("Test Set Custom Name", args=("hair", "TestHair", ""))
    # options: TipNoPrefix keeps the lines without the prefixes, TipNoIds drops the pak: / g: / id: lines
    mgr.set_editor_property("TipNoPrefix", True)
    expect("tip without prefixes", tip("ModThing"), ["Fancy Thing", "Default: ModThing", "Top", "My Mod", "SomeMod", "Nice Group", "SomeGroup", "ModThing"])
    mgr.set_editor_property("TipNoPrefix", False); mgr.set_editor_property("TipNoIds", True)
    expect("tip without ids", tip("ModThing"), ["Fancy Thing", "Default: ModThing", "s: Top", "PAK: My Mod", "G: Nice Group"])
    expect("tip hair without ids", tip("TestHair", "hair", "Hair"), ["TestHair", "s: Hair", "Vanilla"])
    mgr.set_editor_property("TipNoPrefix", True)
    expect("tip names only", tip("ModThing"), ["Fancy Thing", "Default: ModThing", "Top", "My Mod", "Nice Group"])
    mgr.set_editor_property("TipNoPrefix", False); mgr.set_editor_property("TipNoIds", False)
    mgr.call_method("Test Set Custom Name", args=("item", "ModThing", "")); mgr.call_method("Test Set Custom Name", args=("mod", "SomeMod", "")); mgr.call_method("Test Set Custom Name", args=("group", "SomeGroup", "")); mgr.call_method("Test Build")
run(main)
