"""Ragdolls scenes with zombie figures: S_RagFigure.Kind / Parts (S_RagPart with S_RagMat parameter lists) survive SaveGameToSlot /
LoadGameFromSlot (own slot, deleted again). The structs are not reachable from Python in 4.27 - the BP event builds, saves, loads
and writes what came back into the manager's Tmp variables."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *


def main():
    mgr = cdo("/Game/Mod/AltUI/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Rag Parts Round Trip")
    expect("kind", mgr.get_editor_property("TmpStr"), "/Game/Project/Zombie/Brute.Brute_C")
    expect("part mesh and socket", (mgr.get_editor_property("TmpStr2"), str(mgr.get_editor_property("TmpName"))), ("/Game/X/SM_Crystal.SM_Crystal", "head"))
    expect("texture path", mgr.get_editor_property("TmpStr3"), "/Game/X/T_Mask.T_Mask")
    expect("scalar + colour + offset (1.5 + 0.3 + 3)", round(mgr.get_editor_property("TmpFloat"), 3), 4.8)
    expect("dynamic, scalar names in order", mgr.get_editor_property("TmpBool"), True)


run(main)
