import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"
W = "255.255.255.255"

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Load Settings")
    mgr.set_editor_property("Outfits", None)
    mgr.call_method("Test Load Outfits")
    for pieces in (["A", "B"], ["A", "B"], ["C"]): mgr.call_method("Test Add Outfit", args=(pieces,))
    mgr.call_method("Test Tint Outfit", args=(1, "A", unreal.Color(r=10, g=20, b=30, a=255)))
    def key(i, old=False):
        mgr.call_method("Test Outfit Old Key" if old else "Test Outfit Key", args=(i,)); return mgr.get_editor_property("TmpStr2")
    def name(k):
        mgr.call_method("Test Outfit Name", args=(k,)); return mgr.get_editor_property("TmpStr2")
    k0, k1, k2 = key(0), key(1), key(2)
    expect("key with colours", k0, "A=%s|B=%s" % (W, W))
    expect("colour tells apart", k1 != k0, True)
    expect("old key: pieces only", key(1, old=True), "A|B")
    # a save from before: name, quick item and slot colour on the old key "A|B"
    mgr.call_method("Test Set Outfit Name", args=("A|B", "Duo"))
    mgr.call_method("Test Set Outfit Name", args=("C", "Solo"))
    mgr.set_editor_property("QuickItems", ["look:1", "outfit:A|B", "outfit:C", "outfit:gone"])
    red = unreal.LinearColor(1, 0, 0, 1)
    mgr.set_editor_property("OutfitSlotColors", {"A|B>A#0": red, "other>X#1": red})
    mgr.call_method("Test Migrate Outfit Keys", args=(True,))
    expect("name on the first", name(k0), "Duo")
    expect("name on the tinted one too", name(k1), "Duo")
    expect("old name entry gone", name("A|B"), "")
    expect("single outfit name", name(k2), "Solo")
    expect("quick items", list(mgr.get_editor_property("QuickItems")), ["look:1", "outfit:" + k0, "outfit:" + k2, "outfit:gone"])
    sc = {str(k): v for k, v in mgr.get_editor_property("OutfitSlotColors").items()}
    expect("slot colours", sorted(sc), sorted([k0 + ">A#0", k1 + ">A#0", "other>X#1"]))
    # only once: a second run without the reset changes nothing
    mgr.call_method("Test Set Outfit Name", args=("A|B", "Again"))
    mgr.call_method("Test Migrate Outfit Keys", args=(False,))
    expect("runs once", name(k0), "Duo")
    mgr.call_method("Test Set Outfit Name", args=("A|B", ""))
run(main)
