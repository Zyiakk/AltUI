import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.set_editor_property("Outfits", None)
    mgr.call_method("Test Load Outfits")      # no slot "Outfits" in the editor -> new, empty Outfits_Save object
    for p in ("A", "B", "C", "D"): mgr.call_method("Test Add Outfit", args=([p],))
    def order():
        out = []
        for i in range(len(mgr.get_editor_property("Outfits").get_editor_property("outfits"))):
            mgr.call_method("Test Outfit Key", args=(i,)); out.append(mgr.get_editor_property("TmpStr2").split("=")[0])
        return "".join(out)
    expect("start", order(), "ABCD")   # one white piece each: key "<piece>=255.255.255.255"
    mgr.call_method("Test Move Outfit", args=(2, 1)); expect("left", order(), "ACBD")
    mgr.call_method("Test Move Outfit", args=(1, 2)); expect("right", order(), "ABCD")
    mgr.call_method("Test Move Outfit", args=(3, 0)); expect("to start", order(), "DABC")
    mgr.call_method("Test Move Outfit", args=(0, 1000000000)); expect("to end (clamped)", order(), "ABCD")
    mgr.call_method("Test Move Outfit", args=(0, -1)); expect("before the first: clamped, no change", order(), "ABCD")
    mgr.call_method("Test Move Outfit", args=(7, 0)); expect("invalid index: no change", order(), "ABCD")
    expect("count unchanged", len(mgr.get_editor_property("Outfits").get_editor_property("outfits")), 4)
run(main)
