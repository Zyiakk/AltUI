"""Inventory tab: the stubs it reads (ItemTable columns, storage box classes) and, from step 1 task 4 on, the manager's helpers."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *


def column(table, col):
    rows = [str(n) for n in unreal.DataTableFunctionLibrary.get_data_table_row_names(table)]
    vals = unreal.DataTableFunctionLibrary.get_data_table_column_as_string(table, col)
    return dict(zip(rows, vals))


def main():
    t = unreal.load_asset("/Game/Project/Tables/ItemTable")
    expect("NumberOfPick GlockAmmo", column(t, "NumberOfPick").get("GlockAmmo"), "10")
    expect("IsConsumable GlockAmmo", column(t, "IsConsumable").get("GlockAmmo"), "True")
    expect("Weight Glock", column(t, "Weight").get("Glock"), "100")
    expect("Flag Glock", column(t, "Flag").get("Glock"), "2")
    expect("ItemClass Glock", column(t, "ItemClass").get("Glock"), "Weapon")   # display name of NewEnumerator3
    expect("HyperBoxGroup EntryCard_Red", column(t, "HyperBoxGroup").get("EntryCard_Red"), "None")
    hb = unreal.load_object(None, "/Game/Project/Classes/Misc/HyperBoxData.HyperBoxData_C")
    expect("HyperBoxData stub", hb is not None, True)
    save = unreal.load_object(None, "/Game/Project/Classes/Save/HyperBox_Save.Default__HyperBox_Save_C")
    expect("HyperBox_Save Save Items_0", isinstance(save.get_editor_property("Save Items_0"), unreal.Map), True)
    # manager helpers
    mgr = cdo("/Game/Mod/AltUI/BP_AltUIManager.BP_AltUIManager_C")
    def row(item):
        mgr.call_method("Test Inv Row", args=(item,))
        return (str(mgr.get_editor_property("TmpName")), mgr.get_editor_property("TmpI"), str(mgr.get_editor_property("TmpName2")), mgr.get_editor_property("TmpBool"))
    expect("row GlockAmmo", row("GlockAmmo"), ("Ammo", 1, "ammo", True))
    expect("row Glock", row("Glock"), ("Weapon", 100, "gun", True))
    expect("row Flashlight", row("Flashlight")[0::2], ("Tool", "usable"))
    expect("row Pills kind", row("Pills")[2], "usable")
    expect("row Optics_RedDot kind", row("Optics_RedDot")[0::2], ("Equipment", "other"))
    expect("row EntryCard_Red group", row("EntryCard_Red")[0], "None")
    # all-items catalogue rule (no name list): box group, else Collect unless ItemClass 2 (keys / cards) or no actor class
    def cat(item):
        mgr.call_method("Test Inv Row", args=(item,)); return mgr.get_editor_property("InvTestStr")
    expect("cat GlockAmmo", cat("GlockAmmo"), "Ammo")
    expect("cat Decor_Dog", cat("Decor_Dog"), "Collect")
    expect("cat EntryCard_Blue (key, has actor)", cat("EntryCard_Blue"), "None")
    expect("cat InvisibleHand (no actor, but works in the bag)", cat("InvisibleHand"), "Collect")
    # weapons tab, attachments: a GunEquipment row fits a slot of the current weapon (type, Guns list, a part class)
    def att(weapon, row, t):
        mgr.call_method("Test Att Matches", args=(weapon, row, t)); return mgr.get_editor_property("TmpBool")
    expect("att UMP45 sights red dot", att("UMP45", "Optics_RedDot", 0), True)
    expect("att UMP45 barrel red dot", att("UMP45", "Optics_RedDot", 1), False)
    expect("att Glock sights red dot", att("Glock", "Optics_RedDot", 0), False)
    expect("att Glock barrel silencer", att("Glock", "Silencer_PRS", 1), True)
    expect("att plain magazine row", att("UMP45", "UMP45", 3), False)
    expect("att any slot", att("Glock", "Silencer_PRS", -1), True)
    def cap(c, n):
        mgr.call_method("Test Inv Tile Caption", args=(c, n)); return mgr.get_editor_property("InvTestStr")
    expect("caption 1", cap("Pills", 1), "Pills")
    expect("caption 3", cap("Pills", 3), "Pills ×3")
    def parse(n):
        mgr.call_method("Test Inv Tile Parse", args=(n,))
        return (str(mgr.get_editor_property("TmpName")), str(mgr.get_editor_property("TmpName2")), mgr.get_editor_property("TmpI"))
    expect("parse bag", parse("bag:GlockAmmo")[:2], ("bag", "GlockAmmo"))
    expect("parse box", parse("box:Pills")[:2], ("box", "Pills"))
    expect("parse gun", (parse("gun:3")[0], parse("gun:3")[2]), ("gun", 3))
    # storing never moves more than the backpack holds: the game leaves a used-up entry at 0 in bag Tools (Bag.Consume Item),
    # and Add Item would put it into the box anyway (2026-10-08: the last item of a stack was duplicated into the box)
    def clamp(n, have):
        mgr.call_method("Test Inv Clamp", args=(n, have)); return mgr.get_editor_property("TmpI")
    expect("clamp 1 of 0", clamp(1, 0), 0)
    expect("clamp 5 of 3", clamp(5, 3), 3)
    expect("clamp 2 of 9", clamp(2, 9), 2)
    expect("clamp 1 of -1", clamp(1, -1), 0)
    # list heads: "..." folds, the full-height chip takes one list up; "..." on another list while one has the full height brings that one back
    def heads(*clicks):
        for k, v in (("InvFoldBag", False), ("InvFoldBox", False), ("InvFoldCat", False), ("InvMax", "None")): mgr.set_editor_property(k, v)
        for c in clicks: mgr.call_method("Test Inv Head Clicked", args=(c,))
        return (mgr.get_editor_property("InvFoldBag"), mgr.get_editor_property("InvFoldBox"), mgr.get_editor_property("InvFoldCat"), str(mgr.get_editor_property("InvMax")))
    expect("fold bag", heads("InvFoldBag"), (True, False, False, "None"))
    expect("fold bag twice", heads("InvFoldBag", "InvFoldBag"), (False, False, False, "None"))
    expect("max box", heads("InvMaxBox"), (False, False, False, "Box"))
    expect("max box twice", heads("InvMaxBox", "InvMaxBox"), (False, False, False, "None"))
    expect("max opens a folded list", heads("InvFoldBox", "InvMaxBox"), (False, False, False, "Box"))
    expect("fold other while max: back, open", heads("InvFoldBag", "InvMaxBox", "InvFoldBag"), (False, False, False, "None"))
    expect("fold the max list: ends it, folded", heads("InvMaxCat", "InvFoldCat"), (False, False, True, "None"))
    for k, v in (("InvFoldBag", False), ("InvFoldBox", False), ("InvFoldCat", False), ("InvMax", "None")): mgr.set_editor_property(k, v)
    mgr.call_method("Test Save Settings")   # leave the settings as they were
    # Options > General: weapons from box / catalogue into the hand - stored inverted (0 = never set = the game's auto-equip on)
    mgr.set_editor_property("InvNoAutoEquip", True); mgr.call_method("Test Save Settings")
    mgr.set_editor_property("InvNoAutoEquip", False); mgr.call_method("Test Load Settings")
    expect("no auto-equip survives the settings", mgr.get_editor_property("InvNoAutoEquip"), True)
    mgr.set_editor_property("InvNoAutoEquip", False); mgr.call_method("Test Save Settings")


run(main)
