import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Load Settings")                 # creates the Settings object if no save exists (a direct call fails on locals)
    mgr.call_method("Test Join Names", args=(["Zeta_Neck", "Boots02"],))
    expect("join keeps map order", mgr.get_editor_property("TmpStr2"), "Zeta_Neck|Boots02")
    mgr.call_method("Test Join Names", args=([],))
    expect("join empty", mgr.get_editor_property("TmpStr2"), "")
    mgr.call_method("Test Set Outfit Name", args=("k1", "  Büro "))
    mgr.call_method("Test Outfit Name", args=("k1",))
    expect("trimmed name round-trip", mgr.get_editor_property("TmpStr2"), "Büro")
    mgr.call_method("Test Set Outfit Name", args=("k1", "x" * 60))
    mgr.call_method("Test Outfit Name", args=("k1",))
    expect("cut to 40", len(mgr.get_editor_property("TmpStr2")), 40)
    mgr.call_method("Test Set Outfit Name", args=("k1", "   "))
    mgr.call_method("Test Outfit Name", args=("k1",))
    expect("blank removes", mgr.get_editor_property("TmpStr2"), "")
    mgr.call_method("Test Outfit Name", args=("unknown",))
    expect("unknown key empty", mgr.get_editor_property("TmpStr2"), "")
run(main)
