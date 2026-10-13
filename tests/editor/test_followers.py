"""Followers: a record goes through AltUI_Followers.sav and comes back (Save Fol Save / Load Fol Save / Fol Index); the figure class
is a child of NPC_Female and the game's Need to Save is overridden (docs/specs/2026-10-09-followers-design.md)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Fol Round Trip", args=("EdTest Figure",))
    expect("record found again after reload", mgr.get_editor_property("TmpI") >= 0, True)
    expect("record name after reload", mgr.get_editor_property("TmpStr"), "EdTest Figure")
    # real clothes (2026-10-12): the new fields go through the save and come back
    expect("worn pieces after reload", [str(n) for n in mgr.get_editor_property("TmpNames")], ["EdTop", "EdPants"])
    expect("hair after reload", str(mgr.get_editor_property("TmpName")), "EdHair")
    # "..." > Remove > yes: the record is gone from the save
    mgr.call_method("Test Fol Add", args=("EdTestRm",)); idx = mgr.get_editor_property("TmpI"); expect("record to remove added", idx >= 0, True)
    mgr.call_method("Test Fol Menu Action", args=("Fol:RemoveYes", idx)); mgr.call_method("Test Fol Index", args=("EdTestRm",))
    expect("removed via the menu", mgr.get_editor_property("TmpI"), -1)
    # top columns: folding one unfolds the other, in both directions (2026-10-10: the box would not fold with the backpack folded)
    def fold(chip, bag, box):
        mgr.set_editor_property("FolFoldBag", bag); mgr.set_editor_property("FolFoldBox", box); mgr.call_method("Test Fol Chip", args=(chip,))
        return (mgr.get_editor_property("FolFoldBag"), mgr.get_editor_property("FolFoldBox"))
    expect("fold box while the backpack is folded", fold("FolFoldBox", True, False), (False, True))
    expect("fold backpack while the box is folded", fold("FolFoldBag", False, True), (True, False))
    expect("unfold the backpack", fold("FolFoldBag", True, False), (False, False))
    mgr.set_editor_property("FolFoldBag", False); mgr.set_editor_property("FolFoldBox", False)
    cls = unreal.load_object(None, M + "/BP_AltUIFollower.BP_AltUIFollower_C")
    expect("follower class loads", cls is not None, True)
    npc = unreal.load_object(None, "/Game/Project/Character/Npc/NPC_Female.NPC_Female_C")
    expect("follower is an NPC_Female", cls is not None and npc is not None and unreal.MathLibrary.class_is_child_of(cls, npc), True)
run(main)
