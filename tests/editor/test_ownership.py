"""Ownership options: Can Wear (locked / greyed / like owned) and Shown Owned (tile state) per UnownedMode. No player in the CDO:
In Bag reads a None bag (false), so the backpack path is not covered here."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Set Owned", args=("Dress05", True)); mgr.call_method("Test Set Owned", args=("Briefs03", False))
    def can(name): mgr.call_method("Test Can Wear", args=(name,)); return mgr.get_editor_property("TmpBool")
    def shown(name): mgr.call_method("Test Shown Owned", args=(name,)); return mgr.get_editor_property("TmpBool")
    for mode, wear_unowned, shown_unowned in ((0, False, False), (1, True, False), (2, True, True)):
        mgr.set_editor_property("UnownedMode", mode)
        expect("mode %d owned wearable" % mode, can("Dress05"), True)
        expect("mode %d owned shown" % mode, shown("Dress05"), True)
        expect("mode %d unowned wearable" % mode, can("Briefs03"), wear_unowned)
        expect("mode %d unowned shown" % mode, shown("Briefs03"), shown_unowned)
    mgr.set_editor_property("UnownedMode", 0)
run(main)
