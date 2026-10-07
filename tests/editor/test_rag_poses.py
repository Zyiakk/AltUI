"""Ragdoll poses (data level, no figures in the editor): the type a figure's poses go by (Jodi copy, base kind for variants), save
under a name and type, the same name (case does not matter) and type overwrites, the same name in another type is a pose of its
own, an empty name saves nothing, delete removes. Leaves the editor's AltUI_Ragdolls slot as it was (deletes what it added)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *


def main():
    mgr = cdo("/Game/Mod/AltUI/BP_AltUIManager.BP_AltUIManager_C")
    def ptype(kind):
        mgr.call_method("Test Rag Pose Type", args=(kind,)); return mgr.get_editor_property("TmpStr")
    expect("Jodi copy", ptype(""), "Jodi")
    expect("variant -> base kind", ptype("/Game/Project/Zombie/Brute_Armed.Brute_Armed_C"), "Brute")
    expect("base class", ptype("/Game/Project/Zombie/Crawler.Crawler_C"), "Crawler")
    expect("NPC", ptype("/Game/Project/Character/Npc/NPC_Female.NPC_Female_C"), "Npc")
    expect("unknown class keeps its path", ptype("/Game/X/Y.Y_C"), "/Game/X/Y.Y_C")
    def poses(i=0):
        mgr.call_method("Test Rag Poses", args=(i,)); return mgr.get_editor_property("TmpI"), mgr.get_editor_property("TmpStr2")
    n0, _ = poses()
    mgr.call_method("Test Store Rag Pose", args=("  Sitzen ", "Jodi")); expect("saved, trimmed", poses(n0), (n0 + 1, "Sitzen|Jodi"))
    mgr.call_method("Test Store Rag Pose", args=("sitzen", "Jodi")); expect("same name + type overwrites", poses(n0), (n0 + 1, "sitzen|Jodi"))
    mgr.call_method("Test Store Rag Pose", args=("Sitzen", "Brute")); expect("same name, other type adds", poses(n0 + 1), (n0 + 2, "Sitzen|Brute"))
    mgr.call_method("Test Store Rag Pose", args=("  ", "Jodi")); expect("empty name saves nothing", poses(n0)[0], n0 + 2)
    mgr.call_method("Test Delete Rag Pose", args=(n0 + 1,)); mgr.call_method("Test Delete Rag Pose", args=(n0,))
    expect("deleted again", poses()[0], n0)


run(main)
