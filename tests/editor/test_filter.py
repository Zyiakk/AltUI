import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def filtered(mgr, slot, group, search, only_owned, only_fav, only_vanilla=False):
    mgr.call_method("Test Filter", args=(slot, group, search, only_owned, only_fav, only_vanilla))
    return [str(n) for n in mgr.get_editor_property("TmpNames")]

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build"); mgr.call_method("Test Strings", args=(1,))
    mgr.set_editor_property("OwnedSet", {"Alpha_Neck", "Zeta_Neck"})   # Is Owned reads the set (Refresh State fills it from Owned)
    mgr.set_editor_property("Favorites", ["Zeta_Neck"])
    expect("no filter", filtered(mgr, "Neck", "None", "", False, False), ["Alpha_Neck", "Casual_Mina_Neck", "Zeta_Neck"])
    expect("group Kpop", filtered(mgr, "Neck", "Kpop", "", False, False), ["Alpha_Neck", "Casual_Mina_Neck"])
    expect("group None=Basis", filtered(mgr, "Neck", "Basis", "", False, False), ["Zeta_Neck"])
    expect("search ci", filtered(mgr, "Neck", "None", "MINA", False, False), ["Casual_Mina_Neck"])
    expect("search none", filtered(mgr, "Neck", "None", "xyz", False, False), [])
    expect("only owned", filtered(mgr, "Neck", "None", "", True, False), ["Alpha_Neck", "Zeta_Neck"])
    expect("only fav", filtered(mgr, "Neck", "None", "", False, True), ["Zeta_Neck"])
    expect("combined", filtered(mgr, "Neck", "Kpop", "", True, False), ["Alpha_Neck"])
    # ModThing comes from the SomeMod stub table (Top slot); "only vanilla" drops it in its slot and in All
    expect("mod item listed", filtered(mgr, "Top", "None", "", False, False), ["ModThing"])
    expect("only vanilla in slot", filtered(mgr, "Top", "None", "", False, False, True), [])
    expect("only vanilla in All", "ModThing" in filtered(mgr, "All", "None", "", False, False, True), False)
    expect("only vanilla keeps vanilla", filtered(mgr, "Neck", "None", "", False, False, True), ["Alpha_Neck", "Casual_Mina_Neck", "Zeta_Neck"])
    # counts per slot under the current filters (left list: "total (filtered)"); slots without a match are absent
    def counts(search, owned, fav, vanilla):
        mgr.call_method("Test Filtered Counts", args=(search, owned, fav, vanilla))
        return {str(k): v for k, v in mgr.get_editor_property("FilteredCounts").items()}
    c = counts("", False, False, False); expect("counts unfiltered", (c.get("Neck"), c.get("Top"), c.get("All")), (3, 1, 18))
    c = counts("", False, False, True); expect("counts only vanilla", (c.get("Neck"), c.get("Top"), c.get("All")), (3, None, 17))
    c = counts("neck", True, False, False); expect("counts search + owned", (c.get("Neck"), c.get("Necklace"), c.get("All")), (2, None, 2))
    mgr.set_editor_property("CurrentGroup", "Kpop"); c = counts("", False, False, False); expect("counts with a group chip", (c.get("Neck"), c.get("Top"), c.get("All")), (2, None, 2))
    mgr.set_editor_property("CurrentGroup", "None")
    mgr.call_method("Test Groups", args=("Neck",))
    expect("groups of slot", sorted(str(n) for n in mgr.get_editor_property("TmpNames")), ["Basis", "Kpop"])
    # "..." chip (pseudo group AltUI_More): toggles SubTabsCollapsed, keeps the current group; only on the clothes page
    mgr.set_editor_property("Page", "Clothes"); mgr.set_editor_property("CurrentGroup", "Kpop"); mgr.set_editor_property("SubTabsCollapsed", False)
    mgr.call_method("Test Select SubTab", args=("AltUI_More",))
    expect("more chip collapses", mgr.get_editor_property("SubTabsCollapsed"), True); expect("more chip keeps group", str(mgr.get_editor_property("CurrentGroup")), "Kpop")
    mgr.call_method("Test Select SubTab", args=("AltUI_More",)); expect("more chip expands", mgr.get_editor_property("SubTabsCollapsed"), False)
    mgr.call_method("Test Select SubTab", args=("Lace",)); expect("group chip selects", str(mgr.get_editor_property("CurrentGroup")), "Lace")
    # slot click keeps the group chip when the new slot has that group, else back to All
    mgr.set_editor_property("CurrentGroup", "Kpop"); mgr.call_method("Test Select Slot", args=("Neck",))
    expect("slot keeps group", (str(mgr.get_editor_property("CurrentSlot")), str(mgr.get_editor_property("CurrentGroup"))), ("Neck", "Kpop"))
    mgr.call_method("Test Select Slot", args=("Necklace",))
    expect("slot without group -> All", (str(mgr.get_editor_property("CurrentSlot")), str(mgr.get_editor_property("CurrentGroup"))), ("Necklace", "None"))
    mgr.call_method("Test Group Caption", args=("AltUI_More",)); expect("caption more", str(mgr.get_editor_property("TmpText")), "...")
    mgr.call_method("Test Group Caption", args=("Kpop",)); expect("caption Kpop", str(mgr.get_editor_property("TmpText")), "KPOP")
    mgr.call_method("Test Group Caption", args=("Lace",)); expect("caption Lace", str(mgr.get_editor_property("TmpText")), "Spitze")
    mgr.call_method("Test Group Caption", args=("Basis",)); expect("caption Basis", str(mgr.get_editor_property("TmpText")), "No group")
    mgr.call_method("Test Group Caption", args=("Nope",)); expect("caption unknown", str(mgr.get_editor_property("TmpText")), "Nope")
    # chip caption: Group Caption shortened to GroupLen characters (0 = unlimited) - cut in the middle, ".." between
    # head and tail (not counted), so groups sharing a prefix stay distinguishable
    mgr.set_editor_property("GroupLen", 4)
    mgr.call_method("Test Chip Caption", args=("Lace", False)); expect("chip cut even", str(mgr.get_editor_property("TmpText")), "Sp..ze")
    mgr.set_editor_property("GroupLen", 5)
    mgr.call_method("Test Chip Caption", args=("Lace", False)); expect("chip cut odd (longer head)", str(mgr.get_editor_property("TmpText")), "Spi..ze")
    mgr.set_editor_property("GroupLen", 4)
    mgr.call_method("Test Chip Caption", args=("Kpop", False)); expect("chip fits", str(mgr.get_editor_property("TmpText")), "KPOP")
    mgr.call_method("Test Chip Caption", args=("Lace", True)); expect("chip full (selected while collapsed)", str(mgr.get_editor_property("TmpText")), "Spitze")
    mgr.set_editor_property("GroupLen", 0)
    mgr.call_method("Test Chip Caption", args=("Lace", False)); expect("chip unlimited", str(mgr.get_editor_property("TmpText")), "Spitze")
    # search over custom names, row names and mod captions (Names loaded from AltUI_Names.sav; Set Custom Name marks the catalog dirty)
    mgr.call_method("Test Load Names"); mgr.call_method("Test Set Custom Name", args=("item", "ModThing", "Fancy Thing"))
    mgr.call_method("Test Build")   # the catalog carries the shown names
    expect("search custom name", filtered(mgr, "Top", "None", "fancy", False, False), ["ModThing"])
    expect("search row name", filtered(mgr, "Top", "None", "modthing", False, False), ["ModThing"])
    expect("search mod caption", filtered(mgr, "Top", "None", "some mod", False, False), ["ModThing"])
    expect("search mod caption misses vanilla", filtered(mgr, "Neck", "None", "some mod", False, False), [])
    mgr.call_method("Test Custom Name", args=("item", "ModThing")); expect("custom name stored", str(mgr.get_editor_property("TmpStr2")), "Fancy Thing")
    mgr.call_method("Test Set Custom Name", args=("item", "ModThing", "")); mgr.call_method("Test Custom Name", args=("item", "ModThing")); expect("custom name removed", mgr.get_editor_property("TmpBool"), False)
    mgr.call_method("Test Build")
    # MergeGroups: two group ids with the same shown caption share one chip and one filter
    def alias(group):
        mgr.call_method("Test Group Alias", args=(group,)); return str(mgr.get_editor_property("TmpName"))
    mgr.call_method("Test Load Names"); mgr.call_method("Test Set Custom Name", args=("group", "Kpop", "Spitze"))
    mgr.set_editor_property("MergeGroups", True); mgr.call_method("Test Build")
    expect("merge: same alias", alias("Kpop") == alias("Lace") and alias("Kpop") in ("Kpop", "Lace"), True)
    mgr.call_method("Test Groups", args=("All",)); expect("merge: one chip", sorted(str(n) for n in mgr.get_editor_property("TmpNames")), sorted(["Basis", alias("Lace"), "SomeGroup"]))   # Kpop gone, the mod group stays
    expect("merge: filter joins both ids", filtered(mgr, "Neck", alias("Lace"), "", False, False), ["Alpha_Neck", "Casual_Mina_Neck"])
    expect("merge: untouched group", alias("Basis"), "Basis")
    mgr.set_editor_property("MergeGroups", False); mgr.call_method("Test Build")
    expect("merge off: identity", alias("Kpop"), "Kpop")
    mgr.call_method("Test Set Custom Name", args=("group", "Kpop", ""))
    # the "..." chip saved the settings: leave a clean save behind (test_content loads the slot and toggles favourites)
    mgr.set_editor_property("Favorites", []); mgr.set_editor_property("SubTabsCollapsed", False); mgr.set_editor_property("CurrentGroup", "None"); mgr.call_method("Test Save Settings")
run(main)
