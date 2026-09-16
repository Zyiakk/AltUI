import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def code(mgr, page, slot=None, cat=None):
    mgr.set_editor_property("Page", page)
    if slot: mgr.set_editor_property("CurrentSlot", slot)
    if cat: mgr.set_editor_property("LookCat", cat)
    mgr.call_method("Test Focus Code"); return mgr.get_editor_property("TmpI")

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    expect("clothes boots", code(mgr, "Clothes", slot="Boots"), 105)     # stub ClothesTypeTable
    expect("clothes bra", code(mgr, "Clothes", slot="Bra"), 365)
    expect("clothes all -> none", code(mgr, "Clothes", slot="All"), 0)
    expect("clothes shirt (stub without value)", code(mgr, "Clothes", slot="Shirt"), 0)
    expect("look lips -> face", code(mgr, "Look", cat="Lips"), 983)
    expect("look skin -> none", code(mgr, "Look", cat="Skin"), 0)
    expect("hair -> face", code(mgr, "Hair"), 983)
    expect("options -> none", code(mgr, "Options"), 0)
    # decoding (Test Decode does not set Page/Slot; arithmetic only): h and zoom
    for c, h, zoom in ((983, 83, 22.0 / 78), (165, 65, 1.0), (105, 5, 1.0), (680, 80, 22.0 / 57)):
        mgr.call_method("Test Decode", args=(c,))
        expect("decode h %d" % c, mgr.get_editor_property("TmpI"), h)
        report("decode zoom %d" % c, abs(mgr.get_editor_property("TmpFloat") - zoom) < 0.01, mgr.get_editor_property("TmpFloat"))
run(main)
