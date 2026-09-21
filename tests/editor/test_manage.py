import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def rows(mgr, cat, search="", only_mods=True):
    mgr.call_method("Test Manage Rows", args=(cat, search, only_mods)); return [str(s) for s in mgr.get_editor_property("TmpStrings2")]

def custom(mgr, kind, row):
    mgr.call_method("Test Custom Name", args=(kind, row)); return mgr.get_editor_property("TmpBool"), str(mgr.get_editor_property("TmpStr2"))

def origin(mgr, kind, row):
    mgr.call_method("Test Manage Origin", args=(kind, row)); return str(mgr.get_editor_property("TmpText"))

def origin3(mgr, kind, row):
    mgr.call_method("Test Manage Origin", args=(kind, row))
    return (str(mgr.get_editor_property("TmpText")), str(mgr.get_editor_property("TmpMod")), str(mgr.get_editor_property("TmpRest")))

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build"); mgr.call_method("Test Strings", args=(1,)); mgr.call_method("Test Load Names")
    mgr.call_method("Test Set Custom Name", args=("item", "ModThing", "")); mgr.call_method("Test Set Custom Name", args=("group", "SomeGroup", ""))
    # Mods: header, then its groups (indented rows); vanilla has no header
    expect("mods category", rows(mgr, "Mods"), ["mod:SomeMod", "group:SomeGroup"])
    expect("mods search by group keeps the header", rows(mgr, "Mods", "somegroup"), ["mod:SomeMod", "group:SomeGroup"])
    expect("mods search by caption", rows(mgr, "Mods", "some mod"), ["mod:SomeMod"])
    expect("mods search miss", rows(mgr, "Mods", "zzz"), [])
    mgr.set_editor_property("CaseSensitiveNames", True)   # "case-sensitive" checkbox
    expect("case-sensitive: lower-case miss", rows(mgr, "Mods", "some mod"), [])
    expect("case-sensitive: exact hit", rows(mgr, "Mods", "Some Mod"), ["mod:SomeMod"])
    mgr.set_editor_property("CaseSensitiveNames", False)
    expect("case-insensitive: mixed case", rows(mgr, "Mods", "sOmE mOd"), ["mod:SomeMod"])
    # Clothes
    expect("clothes only mods", rows(mgr, "Clothes"), ["item:ModThing"])
    all_rows = rows(mgr, "Clothes", only_mods=False)
    expect("clothes with vanilla", "item:Zeta_Neck" in all_rows and "item:ModThing" in all_rows, True)
    expect("clothes search by row", rows(mgr, "Clothes", "modth", False), ["item:ModThing"])
    expect("clothes search by default name", rows(mgr, "Clothes", "mina", False), ["item:Casual_Mina_Neck", "item:Casual_Mina_Necklace"])
    # custom name: trimmed, searchable, removable, catalog dirty
    mgr.call_method("Test Set Custom Name", args=("item", "ModThing", "  Fancy Thing "))
    expect("custom name trimmed", custom(mgr, "item", "ModThing"), (True, "Fancy Thing"))
    expect("clothes search by custom name", rows(mgr, "Clothes", "fancy", False), ["item:ModThing"])
    expect("catalog dirty after rename", mgr.get_editor_property("CatalogDirty"), True)
    mgr.call_method("Test Set Custom Name", args=("item", "ModThing", "   ")); expect("blank name removes", custom(mgr, "item", "ModThing")[0], False)
    mgr.call_method("Test Set Custom Name", args=("group", "SomeGroup", "Nice Group")); expect("group search by custom name", rows(mgr, "Mods", "nice"), ["mod:SomeMod", "group:SomeGroup"])
    mgr.call_method("Test Set Custom Name", args=("group", "SomeGroup", ""))
    # identifiers column: lower-case prefixes = ids; a shared group lists the other paks by display name with the upper-case PAK: prefix
    mgr.set_editor_property("TmpParentMod", "SomeMod")   # the mod header above the group row (Rebuild Manage sets it while building)
    expect("mod row identifier", origin(mgr, "mod", "SomeMod"), "pak: SomeMod")
    expect("item row: id / pak link / group line", origin3(mgr, "item", "ModThing"), ("id: ModThing", "SomeMod", "g: SomeGroup"))
    expect("vanilla item row", origin3(mgr, "item", "Zeta_Neck"), ("id: Zeta_Neck\nVanilla", "None", ""))
    expect("makeup row: type line", origin3(mgr, "makeup", "Lips_01"), ("id: Lips_01\nVanilla", "None", "Lips"))   # Look Caption: own string key Look_Lips (en)
    expect("unshared group", origin(mgr, "group", "SomeGroup"), "g: SomeGroup")
    mgr.set_editor_property("ModGroupPairs", ["SomeMod|SomeGroup", "OtherMod|SomeGroup"])
    expect("shared group lists the other pak", origin(mgr, "group", "SomeGroup"), "g: SomeGroup\nalso affects:\nPAK: OtherMod")
    mgr.call_method("Test Set Custom Name", args=("mod", "OtherMod", "Other Name"))
    expect("shared group shows the other pak's display name", origin(mgr, "group", "SomeGroup"), "g: SomeGroup\nalso affects:\nPAK: Other Name")
    mgr.call_method("Test Set Custom Name", args=("mod", "OtherMod", "")); mgr.set_editor_property("ModGroupPairs", ["SomeMod|SomeGroup"])
    # rename from context menus: kind of a tile row, inline finish (trim, default = nothing), jump to the Manage row
    def kind(name):
        mgr.call_method("Test Rename Kind", args=(name,)); return str(mgr.get_editor_property("TmpName"))
    expect("rename kind", (kind("ModThing"), kind("TestHair"), kind("Skin_Default"), kind("Eyebrow_01")), ("item", "hair", "skin", "makeup"))
    mgr.set_editor_property("CatalogDirty", False); mgr.call_method("Test Finish Item Rename", args=("ModThing", "  Neu "))
    expect("finish rename stores trimmed", custom(mgr, "item", "ModThing"), (True, "Neu"))
    mgr.call_method("Test Finish Item Rename", args=("ModThing", "ModThing")); expect("finish rename with the default stores nothing", custom(mgr, "item", "ModThing")[0], False)
    mgr.set_editor_property("ManageSearchText", "x"); mgr.call_method("Test Manage Rename", args=("mod", "SomeMod", "Mods"))
    expect("manage rename jumps", (str(mgr.get_editor_property("Page")), str(mgr.get_editor_property("ManageCat")), str(mgr.get_editor_property("ManageSearchText"))), ("Manage", "Mods", ""))
    # Vanilla: the groups with a vanilla piece, catalog order, as group rows without a header; only-mods has no effect
    expect("vanilla groups scanned", [str(n) for n in mgr.get_editor_property("VanillaGroups")], ["Lace", "Kpop"])
    expect("vanilla category", rows(mgr, "Vanilla"), ["group:Lace", "group:Kpop"])
    expect("vanilla category ignores only-mods", rows(mgr, "Vanilla", only_mods=False), ["group:Lace", "group:Kpop"])
    expect("vanilla search by caption", rows(mgr, "Vanilla", "kpop"), ["group:Kpop"])
    expect("vanilla search miss", rows(mgr, "Vanilla", "somegroup"), [])
    mgr.set_editor_property("TmpParentMod", "None"); mgr.set_editor_property("ModGroupPairs", ["SomeMod|Kpop"])
    expect("vanilla group shared with a pak", origin(mgr, "group", "Kpop"), "g: Kpop\nalso affects:\nPAK: Some Mod")   # the pak's display name (DLC caption)
    mgr.set_editor_property("ModGroupPairs", ["SomeMod|SomeGroup"])
    # 'Rename group…' from a tile: vanilla piece -> Vanilla category, mod piece -> Mods
    mgr.call_method("Test Rename Group Of Item", args=("Alpha_Neck",)); expect("rename group of a vanilla piece", str(mgr.get_editor_property("ManageCat")), "Vanilla")
    mgr.call_method("Test Rename Group Of Item", args=("ModThing",)); expect("rename group of a mod piece", str(mgr.get_editor_property("ManageCat")), "Mods")
    # Look = hairstyles + skins + makeup + eyes (vanilla only in the stubs -> empty with only-mods); sub items (ManageSub): Hair / Skin / makeup type; Clothes: slot
    expect("look only mods", rows(mgr, "Look"), [])
    lk = rows(mgr, "Look", only_mods=False)
    expect("look merges hair + skin + makeup + eye tables", lk, ["hair:Hair", "hair:TestHair", "skin:Skin_Default", "makeup:Eyebrow_01", "makeup:Lips_01", "makeup:Lips_02", "makeup:Eye_1"])
    mgr.set_editor_property("ManageSub", "Hair"); expect("look sub hair", rows(mgr, "Look", only_mods=False), ["hair:Hair", "hair:TestHair"]); mgr.set_editor_property("ManageSub", "None")
    expect("look search", rows(mgr, "Look", "eyebrow_01", False), ["makeup:Eyebrow_01"])
    mgr.set_editor_property("ManageSub", "Lips"); expect("look sub type", rows(mgr, "Look", only_mods=False), ["makeup:Lips_01", "makeup:Lips_02"])
    mgr.set_editor_property("ManageSub", "Skin"); expect("look sub skin", rows(mgr, "Look", only_mods=False), ["skin:Skin_Default"])
    mgr.set_editor_property("ManageSub", "Neck"); expect("clothes sub slot", rows(mgr, "Clothes", only_mods=False), ["item:Alpha_Neck", "item:Casual_Mina_Neck", "item:Zeta_Neck"])
    mgr.set_editor_property("ManageSub", "None"); mgr.set_editor_property("OnlyModsNames", False)
    def sub_counts(cat, search="", filtered=False):
        mgr.call_method("Test Manage Sub Counts", args=(cat, search, filtered)); return {str(k): int(v) for k, v in mgr.get_editor_property("ManageSubFiltered" if filtered else "ManageSubCounts").items()}
    expect("look sub counts", sub_counts("Look"), {"Hair": 2, "Skin": 1, "Eyebrow": 1, "Lips": 2, "Eye": 1})
    expect("clothes sub counts (neck)", sub_counts("Clothes").get("Neck"), 3)
    expect("clothes sub hits of a search", sub_counts("Clothes", "mina", True), {"Neck": 1, "Necklace": 1})
    mgr.set_editor_property("ManageSub", "Lips"); mgr.set_editor_property("ManageCat", "Look")
    expect("category count ignores the sub item", (lambda: (mgr.call_method("Test Manage Count", args=("Look",)), int(mgr.get_editor_property("TmpKey")))[1])(), 7)
    mgr.call_method("Test Select Manage Cat", args=("Sub:Look:Eyebrow",)); expect("sub tab selects", (str(mgr.get_editor_property("ManageCat")), str(mgr.get_editor_property("ManageSub"))), ("Look", "Eyebrow"))
    mgr.call_method("Test Select Manage Cat", args=("Sub:Clothes:All",)); expect("sub all", (str(mgr.get_editor_property("ManageCat")), str(mgr.get_editor_property("ManageSub"))), ("Clothes", "None"))
    mgr.set_editor_property("ManageSub", "Lips"); mgr.call_method("Test Select Manage Cat", args=("Clothes",)); expect("category resets the sub item", (str(mgr.get_editor_property("ManageCat")), str(mgr.get_editor_property("ManageSub"))), ("Clothes", "None"))
    mgr.set_editor_property("OnlyModsNames", True); mgr.set_editor_property("ManageCat", "Mods")
    # AltUI_Names.sav written by Set Custom Name
    expect("names save exists", unreal.GameplayStatics.does_save_game_exist("AltUI_Names", 0), True)
run(main)
