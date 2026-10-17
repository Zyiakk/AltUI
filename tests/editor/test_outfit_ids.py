import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"
W = "255.255.255.255"

# Outfit ids (Discord 2026-10-17): outfits with the same pieces get "<key>~<n>"; names, remembered slot colours and quick
# menu items follow them through moves and deletes; the old FName map moves over once.

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Load Settings")
    st = mgr.get_editor_property("Settings")
    mgr.set_editor_property("Outfits", None)
    mgr.call_method("Test Load Outfits")
    for pieces in (["A", "B"], ["A", "B"], ["C"], ["A", "B"]): mgr.call_method("Test Add Outfit", args=(pieces,))
    def oid(i):
        mgr.call_method("Test Outfit Id", args=(i,)); return mgr.get_editor_property("TmpStr2")
    def name(k):
        mgr.call_method("Test Outfit Name", args=(k,)); return mgr.get_editor_property("TmpStr2")
    def cols():
        return {str(k): round(v.r, 2) for k, v in st.get_editor_property("OutfitColors").items()}
    k, kc = "A=%s|B=%s" % (W, W), "C=" + W
    expect("ids", [oid(i) for i in range(4)], [k, k + "~1", kc, k + "~2"])
    for key in (k, k + "~1", k + "~2", kc): mgr.call_method("Test Set Outfit Name", args=(key, ""))
    mgr.call_method("Test Set Outfit Name", args=(k, "One")); mgr.call_method("Test Set Outfit Name", args=(k + "~1", "Two")); mgr.call_method("Test Set Outfit Name", args=(k + "~2", "Three"))
    lc = lambda r: unreal.LinearColor(r, 0, 0, 1)
    mgr.call_method("Test Set Outfit Colors", args=({k + ">A#0": lc(0.1), k + "~1>A#0": lc(0.2), k + "~2>A#0": lc(0.3), kc + ">C#0": lc(0.4)},))
    mgr.set_editor_property("QuickItems", ["outfit:" + k + "~1", "outfit:" + k + "~2", "look:1"])
    mgr.set_editor_property("KeyBindKeys", ["F5"]); mgr.set_editor_property("KeyBindItems", ["outfit:" + k])

    # "Three" to the front: every outfit with the pieces A, B gets a new number
    mgr.call_method("Test Move Outfit Keep Ids", args=(3, 0))
    expect("ids after move", [oid(i) for i in range(4)], [k, k + "~1", k + "~2", kc])
    expect("names moved", [name(k), name(k + "~1"), name(k + "~2")], ["Three", "One", "Two"])
    expect("colours moved", cols(), {k + ">A#0": 0.3, k + "~1>A#0": 0.1, k + "~2>A#0": 0.2, kc + ">C#0": 0.4})
    expect("quick items moved", list(mgr.get_editor_property("QuickItems")), ["outfit:" + k + "~2", "outfit:" + k, "look:1"])
    expect("own key moved", list(mgr.get_editor_property("KeyBindItems")), ["outfit:" + k + "~1"])
    mgr.call_method("Test Move Outfit Keep Ids", args=(3, 2))   # past no equal outfit: nothing to rekey
    expect("move past another kind", [oid(i) for i in range(4)], [k, k + "~1", kc, k + "~2"])
    expect("names stay", [name(k), name(k + "~1"), name(k + "~2")], ["Three", "One", "Two"])

    # delete "Three" (first): its name, colours and quick item go, the others move down
    mgr.call_method("Test Delete Outfit In Array", args=(0,))
    expect("ids after delete", [oid(i) for i in range(3)], [k, kc, k + "~1"])
    expect("names after delete", [name(k), name(k + "~1"), name(k + "~2")], ["One", "Two", ""])
    expect("colours after delete", cols(), {k + ">A#0": 0.1, k + "~1>A#0": 0.2, kc + ">C#0": 0.4})
    expect("quick item of the deleted one gone", list(mgr.get_editor_property("QuickItems")), ["outfit:" + k + "~1", "look:1"])
    expect("own key follows", list(mgr.get_editor_property("KeyBindItems")), ["outfit:" + k])

    # migration from OutfitSlotColors (FName keys on the content key)
    for key in (k, k + "~1"): mgr.call_method("Test Set Outfit Name", args=(key, ""))
    mgr.call_method("Test Set Outfit Name", args=(k, "Duo"))
    mgr.call_method("Test Set Outfit Colors", args=({},))
    mgr.set_editor_property("OutfitSlotColors", {k + ">A#1": lc(0.5), kc + ">C#0": lc(0.6), "ERROR_NAME_SIZE_EXCEEDED": lc(0.7)})
    mgr.call_method("Test Migrate Outfit Ids", args=(True,))
    expect("migrated colours, copied to the equal outfit, overflow dropped", cols(), {k + ">A#1": 0.5, k + "~1>A#1": 0.5, kc + ">C#0": 0.6})
    expect("name copied", name(k + "~1"), "Duo")
    mgr.call_method("Test Set Outfit Colors", args=({},))
    mgr.call_method("Test Migrate Outfit Ids", args=(False,))
    expect("runs once", cols(), {})
    for key in (k, k + "~1"): mgr.call_method("Test Set Outfit Name", args=(key, ""))
    mgr.set_editor_property("OutfitSlotColors", {}); mgr.set_editor_property("QuickItems", []); mgr.set_editor_property("KeyBindKeys", []); mgr.set_editor_property("KeyBindItems", [])
run(main)
