import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Enemy Prune")
    expect("a missing enemy leaves the list", mgr.get_editor_property("TmpI"), 0)
    for v, want in (("EnemyCount", 1), ("EnemyMode", 4), ("EnemyActiveMode", 4)):
        expect("default " + v, mgr.get_editor_property(v), want)
    expect("default EnemyDist", round(mgr.get_editor_property("EnemyDist"), 1), 2.0)


run(main)
