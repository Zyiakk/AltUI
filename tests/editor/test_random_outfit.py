"""Random outfit (ui-test-204/4-6, open-since-2.12.0 F2): the pieces it may pick in a slot (Random Candidates) - only owned ones
while "not owned items" is hidden, every shown one when greyed / like owned; hidden pieces never; with a drawer open only its
pieces. No player in the CDO: In Bag reads a None bag (false), so the backpack path is not covered here (test_ownership)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build"); mgr.call_method("Test Strings", args=(1,)); mgr.set_editor_property("PanelOpen", False)
    mgr.set_editor_property("HiddenItems", []); mgr.set_editor_property("Favorites", []); mgr.set_editor_property("Worn", [])
    mgr.call_method("Test Drawers Reset")
    mgr.call_method("Test Set Owned", args=("Zeta_Neck", True)); mgr.call_method("Test Set Owned", args=("Alpha_Neck", False)); mgr.call_method("Test Set Owned", args=("Casual_Mina_Neck", False))
    def cands(slot="Neck"): mgr.call_method("Test Random Candidates", args=(slot,)); return sorted(str(n) for n in mgr.get_editor_property("RandCands"))
    everything = ["Alpha_Neck", "Casual_Mina_Neck", "Zeta_Neck"]
    mgr.set_editor_property("UnownedMode", 0); expect("not owned hidden: only owned", cands(), ["Zeta_Neck"])
    mgr.set_editor_property("UnownedMode", 1); expect("not owned greyed: all shown", cands(), everything)
    mgr.set_editor_property("UnownedMode", 2); expect("like owned: all shown", cands(), everything)
    mgr.set_editor_property("UnownedMode", 1)
    mgr.call_method("Test Toggle Hidden", args=("Zeta_Neck",)); expect("hidden piece never picked", cands(), ["Alpha_Neck", "Casual_Mina_Neck"])
    mgr.set_editor_property("UnownedMode", 0); expect("hidden + not owned hidden: nothing", cands(), [])
    mgr.call_method("Test Toggle Hidden", args=("Zeta_Neck",)); expect("unhidden back", cands(), ["Zeta_Neck"])
    mgr.call_method("Test Drawer New", args=("Alpha_Neck",)); d = mgr.get_editor_property("TmpDrawerId"); mgr.call_method("Test Select Drawer", args=(d,))
    mgr.set_editor_property("UnownedMode", 1); expect("open drawer: only its pieces", cands(), ["Alpha_Neck"])
    mgr.set_editor_property("UnownedMode", 0); expect("open drawer, its piece not owned: nothing", cands(), [])
    expect("open drawer, slot without its pieces", cands("Boots"), [])
    mgr.call_method("Test Select Drawer", args=(0,)); expect("default drawer: all again", cands(), ["Zeta_Neck"])
    mgr.call_method("Test Drawers Reset"); mgr.set_editor_property("UnownedMode", 0)
run(main)
