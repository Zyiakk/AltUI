import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def filtered(mgr, slot, group, search, only_owned, only_fav):
    mgr.call_method("Test Filter", args=(slot, group, search, only_owned, only_fav))
    return [str(n) for n in mgr.get_editor_property("TmpNames")]

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build"); mgr.call_method("Test Strings", args=(1,))
    mgr.set_editor_property("OwnedSet", {"Alpha_Neck", "Zeta_Neck"})   # Is Owned reads the set (Refresh State fills it from Owned)
    mgr.set_editor_property("Favorites", ["Zeta_Neck"])
    expect("no filter", filtered(mgr, "Neck", "None", "", False, False), ["Alpha_Neck", "Casual_Mina_Neck", "Zeta_Neck"])
    expect("group Kpop", filtered(mgr, "Neck", "Kpop", "", False, False), ["Alpha_Neck", "Casual_Mina_Neck"])
    expect("group None=Basis", filtered(mgr, "Neck", "Basis", "", False, False), ["Zeta_Neck"])
    expect("search ci", filtered(mgr, "Neck", "None", "MINA", False, False), ["Casual_Mina_Neck"])
    expect("search none", filtered(mgr, "Neck", "None", "xyz", False, False), [])
    expect("only owned", filtered(mgr, "Neck", "None", "", True, False), ["Alpha_Neck", "Zeta_Neck"])
    expect("only fav", filtered(mgr, "Neck", "None", "", False, True), ["Zeta_Neck"])
    expect("combined", filtered(mgr, "Neck", "Kpop", "", True, False), ["Alpha_Neck"])
    mgr.call_method("Test Groups", args=("Neck",))
    expect("groups of slot", sorted(str(n) for n in mgr.get_editor_property("TmpNames")), ["Basis", "Kpop"])
    mgr.call_method("Test Group Caption", args=("Kpop",)); expect("caption Kpop", str(mgr.get_editor_property("TmpText")), "KPOP")
    mgr.call_method("Test Group Caption", args=("Lace",)); expect("caption Lace", str(mgr.get_editor_property("TmpText")), "Spitze")
    mgr.call_method("Test Group Caption", args=("Basis",)); expect("caption Basis", str(mgr.get_editor_property("TmpText")), "Base")
    mgr.call_method("Test Group Caption", args=("Nope",)); expect("caption unknown", str(mgr.get_editor_property("TmpText")), "Nope")
run(main)
