"""Clothes drawers (spec 2026-10-20-drawers-design): new drawers are numbered, pieces go in / out, a drawer filters the list and
counts like Default over its pieces only, rename / move / delete, kept in AltUI_Drawers.sav."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def filtered(mgr, slot, search=""):
    mgr.call_method("Test Filter", args=(slot, "None", search, False, False, False, False))
    return [str(n) for n in mgr.get_editor_property("TmpNames")]


def drawers(mgr):
    """(Id, Name, sorted Items) per drawer (Test Drawer Dump: Python cannot read a user struct's fields)."""
    mgr.call_method("Test Drawer Dump")
    ids, names, items = (list(mgr.get_editor_property(k)) for k in ("TmpDrawerIds", "TmpDrawerNames", "TmpDrawerItems"))
    return [(i, str(n), sorted(x for x in str(t).split("|") if x)) for i, n, t in zip(ids, names, items)]


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build"); mgr.call_method("Test Strings", args=(1,)); mgr.set_editor_property("PanelOpen", False)   # 1 = English
    mgr.set_editor_property("Favorites", []); mgr.set_editor_property("Worn", [])
    mgr.call_method("Test Drawers Reset")
    mgr.call_method("Test Drawer New", args=("None",)); a = mgr.get_editor_property("TmpDrawerId")
    mgr.call_method("Test Drawer New", args=("Zeta_Neck",)); b = mgr.get_editor_property("TmpDrawerId")
    expect("ids and numbered names", [(i, n) for i, n, _ in drawers(mgr)], [(a, "Drawer 1"), (b, "Drawer 2")])
    expect("new with a piece", drawers(mgr)[1][2], ["Zeta_Neck"])
    # default shows everything; drawer a gets two pieces of two slots
    expect("default = all", filtered(mgr, "Neck"), ["Alpha_Neck", "Casual_Mina_Neck", "Zeta_Neck"])
    mgr.call_method("Test Drawer Toggle", args=(a, "Alpha_Neck")); mgr.call_method("Test Drawer Toggle", args=(a, "ModThing"))
    mgr.call_method("Test Select Drawer", args=(a,))
    expect("drawer filters", filtered(mgr, "Neck"), ["Alpha_Neck"])
    expect("drawer + search", (filtered(mgr, "Neck", "alpha"), filtered(mgr, "Neck", "zeta")), (["Alpha_Neck"], []))
    c = {str(k): v for k, v in mgr.get_editor_property("DrawerCounts").items()}
    expect("counts over the drawer", (c.get("Neck"), c.get("Top"), c.get("All")), (1, 1, 2))
    # group chips: only the groups of the drawer's pieces; a chosen group the drawer lacks goes back to All
    groups = lambda slot: (mgr.call_method("Test Groups", args=(slot,)), sorted(str(n) for n in mgr.get_editor_property("TmpNames")))[1]
    expect("drawer groups", (groups("Neck"), groups("Top")), (["Kpop"], ["SomeGroup"]))
    mgr.set_editor_property("CurrentSlot", "Neck"); mgr.set_editor_property("CurrentGroup", "Basis"); mgr.call_method("Test Select Drawer", args=(a,))
    expect("group not in the drawer -> All", str(mgr.get_editor_property("CurrentGroup")), "None")
    mgr.set_editor_property("CurrentGroup", "Kpop"); mgr.call_method("Test Select Drawer", args=(a,)); expect("drawer group kept", str(mgr.get_editor_property("CurrentGroup")), "Kpop")
    mgr.set_editor_property("CurrentGroup", "None")
    # a piece in two drawers; out again
    mgr.call_method("Test Drawer Toggle", args=(b, "Alpha_Neck")); expect("in two drawers", drawers(mgr)[1][2], ["Alpha_Neck", "Zeta_Neck"])
    mgr.call_method("Test Drawer Toggle", args=(a, "Alpha_Neck")); expect("out of the shown drawer", filtered(mgr, "Neck"), [])
    expect("still in the other", drawers(mgr)[1][2], ["Alpha_Neck", "Zeta_Neck"])
    # "Remove from this drawer" (menu row) on the shown drawer
    mgr.call_method("Test Select Drawer", args=(b,)); mgr.set_editor_property("ContextItem", "Zeta_Neck")
    mgr.call_method("Test Drawer Action", args=("Drw:RemoveHere",)); expect("remove here", filtered(mgr, "Neck"), ["Alpha_Neck"])
    mgr.call_method("Test Drawer Action", args=("Drw:T:%d" % b,)); expect("submenu row toggles", filtered(mgr, "Neck"), ["Alpha_Neck", "Zeta_Neck"])
    # rename (empty keeps the name), move, the next free number
    mgr.call_method("Test Drawer Rename", args=(a, "  Summer ")); mgr.call_method("Test Drawer Rename", args=(b, "   "))
    expect("renamed", [n for _, n, _ in drawers(mgr)], ["Summer", "Drawer 2"])
    mgr.call_method("Test Drawer Move", args=(b, -1)); expect("moved left", [i for i, _, _ in drawers(mgr)], [b, a])
    mgr.call_method("Test Drawer Move", args=(b, -1)); expect("no move past the start", [i for i, _, _ in drawers(mgr)], [b, a])
    mgr.call_method("Test Drawer New", args=("None",)); c3 = mgr.get_editor_property("TmpDrawerId")
    expect("next free number", drawers(mgr)[2][1], "Drawer 1")
    # saved: drop the object, load again
    mgr.set_editor_property("DrawerSave", None); mgr.call_method("Test Select Drawer", args=(b,))
    expect("reloaded", [(i, n) for i, n, _ in drawers(mgr)], [(b, "Drawer 2"), (a, "Summer"), (c3, "Drawer 1")])
    # deleting the shown drawer shows Default; ids are not reused
    mgr.call_method("Test Drawer Delete", args=(b,)); expect("deleted -> default", (mgr.get_editor_property("CurrentDrawer"), len(drawers(mgr))), (0, 2))
    expect("default after delete", filtered(mgr, "Neck"), ["Alpha_Neck", "Casual_Mina_Neck", "Zeta_Neck"])
    expect("default groups", groups("Neck"), ["Basis", "Kpop"])
    mgr.call_method("Test Drawer New", args=("None",)); expect("ids not reused", mgr.get_editor_property("TmpDrawerId") > c3, True)
    # a drawer that is gone (other save) -> Default
    mgr.call_method("Test Select Drawer", args=(999,)); expect("unknown drawer -> default", mgr.get_editor_property("CurrentDrawer"), 0)
    mgr.call_method("Test Drawers Reset"); mgr.call_method("Test Strings", args=(0,)); mgr.call_method("Test Drawer New", args=("None",))   # 0 = German
    expect("name in the panel language", drawers(mgr)[0][1], "Schublade 1")
    mgr.call_method("Test Drawers Reset"); mgr.call_method("Test Strings", args=(1,))
    mgr.get_editor_property("DrawerSave"); unreal.GameplayStatics.delete_game_in_slot("AltUI_Drawers", 0)


run(main)
