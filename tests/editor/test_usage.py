import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def names(mgr, var):
    return [str(n) for n in mgr.get_editor_property(var)]

def of(mgr, mod):
    mgr.call_method("Test Usage Of", args=(mod,)); return names(mgr, "TmpNames")

def where(mgr, key):
    mgr.call_method("Test Usage Where", args=(key,)); return str(mgr.get_editor_property("TmpStr2"))

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build"); mgr.call_method("Test Strings", args=(0,))   # 0 = German in the editor; mgr.set_editor_property("PanelOpen", False)
    mgr.set_editor_property("Outfits", None); mgr.call_method("Test Load Outfits"); mgr.call_method("Test Load Settings")
    mgr.set_editor_property("Presets", None); mgr.call_method("Test Load Presets"); mgr.set_editor_property("LooksSave", None); mgr.call_method("Test Load Looks")
    mgr.set_editor_property("Favorites", []); mgr.set_editor_property("ManageSearchText", "")
    # nothing in use: the clothes mod is unused, a DLC row without any content AltUI sees is "not detectable"
    mgr.call_method("Test Scan Usage")
    expect("unused", "SomeMod" in names(mgr, "UsageUnused"), True); expect("no keys", of(mgr, "SomeMod"), [])
    expect("not used", "SomeMod" in names(mgr, "UsageUsed"), False)
    every = set(names(mgr, "UsageUsed")) | set(names(mgr, "UsageUnused")) | set(names(mgr, "UsageUnknown"))
    expect("every mod in one list", len(every), len(names(mgr, "UsageUsed")) + len(names(mgr, "UsageUnused")) + len(names(mgr, "UsageUnknown")))
    # an outfit and a favourite with the mod's piece
    mgr.call_method("Test Add Outfit", args=(["ModThing", "Zeta_Neck"],)); mgr.set_editor_property("Favorites", ["ModThing"])
    mgr.call_method("Test Scan Usage")
    expect("used", "SomeMod" in names(mgr, "UsageUsed"), True); expect("no longer unused", "SomeMod" in names(mgr, "UsageUnused"), False)
    expect("its piece", of(mgr, "SomeMod"), ["item:ModThing"])
    expect("places", where(mgr, "item:ModThing"), "Outfit 1 · Kleidungs-Favorit")
    expect("a vanilla piece has places but no mod", (where(mgr, "item:Zeta_Neck"), any("item:Zeta_Neck" in of(mgr, m) for m in names(mgr, "UsageUsed"))), ("Outfit 1", False))
    # an outfit name of its own
    mgr.call_method("Test Set Outfit Name", args=("ModThing=255.255.255.255|Zeta_Neck=255.255.255.255", "Office")); mgr.call_method("Test Scan Usage")
    expect("named outfit", where(mgr, "item:ModThing"), "Outfit “Office” · Kleidungs-Favorit")
    mgr.call_method("Test Set Outfit Name", args=("ModThing=255.255.255.255|Zeta_Neck=255.255.255.255", ""))
    # the same place twice is listed once
    mgr.call_method("Test Add Outfit", args=(["ModThing"],)); mgr.call_method("Test Scan Usage")
    expect("two outfits", where(mgr, "item:ModThing"), "Outfits 1, 2 · Kleidungs-Favorit")
    mgr.set_editor_property("Favorites", ["ModThing", "ModThing"]); mgr.call_method("Test Scan Usage")
    expect("place once", where(mgr, "item:ModThing"), "Outfits 1, 2 · Kleidungs-Favorit")
    # a run of numbers: 1–3
    mgr.call_method("Test Add Outfit", args=(["ModThing"],)); mgr.call_method("Test Scan Usage")
    expect("range", where(mgr, "item:ModThing"), "Outfits 1–3 · Kleidungs-Favorit")
    # shown name of the piece
    mgr.call_method("Test Usage Part Name", args=("item:ModThing",)); expect("part name", str(mgr.get_editor_property("TmpStr2")) != "", True)
    # search: the Manage rows of Usage = the mods in use the search finds (by mod name or piece name)
    mgr.call_method("Test Manage Rows", args=("Usage", "", True)); expect("rows", [str(s) for s in mgr.get_editor_property("TmpStrings2")], ["mod:SomeMod"])
    mgr.call_method("Test Manage Rows", args=("Usage", "zzz", True)); expect("search miss", [str(s) for s in mgr.get_editor_property("TmpStrings2")], [])
    mgr.call_method("Test Manage Rows", args=("Usage", "modthing", True)); expect("search by piece row", [str(s) for s in mgr.get_editor_property("TmpStrings2")], ["mod:SomeMod"])
    for i in (2, 1, 0): mgr.call_method("Test Delete Outfit In Array", args=(i,))
    mgr.set_editor_property("Favorites", [])

run(main)
