import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def filtered(mgr, slot, group):
    mgr.call_method("Test Filter", args=(slot, group, "", False, False))
    return [str(n) for n in mgr.get_editor_property("TmpNames")]

def groups(mgr, slot):
    mgr.call_method("Test Groups", args=(slot,))
    return [str(n) for n in mgr.get_editor_property("TmpNames")]

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build"); mgr.call_method("Test Strings", args=(1,))   # English strings -> captions "Base"/"Hidden"
    mgr.set_editor_property("HiddenItems", []); mgr.set_editor_property("Favorites", []); mgr.set_editor_property("PanelOpen", False)
    expect("neck groups before", sorted(groups(mgr, "Neck")), ["Basis", "Kpop"])
    mgr.call_method("Test Toggle Hidden", args=("Zeta_Neck",))
    expect("hidden gone from list", filtered(mgr, "Neck", "None"), ["Alpha_Neck", "Casual_Mina_Neck"])
    expect("hidden gone from All", "Zeta_Neck" in filtered(mgr, "All", "None"), False)
    expect("hidden subtab", filtered(mgr, "Neck", "Hidden"), ["Zeta_Neck"])
    expect("neck groups with hidden", groups(mgr, "Neck")[-1], "Hidden"); expect("neck groups count", len(groups(mgr, "Neck")), 3)
    expect("all groups with hidden", groups(mgr, "All")[-1], "Hidden")
    expect("boots groups unchanged", groups(mgr, "Boots"), ["Basis"])
    mgr.call_method("Test Group Caption", args=("Hidden",)); expect("caption hidden", str(mgr.get_editor_property("TmpText")), "Hidden")
    mgr.call_method("Test Toggle Hidden", args=("Zeta_Neck",))
    expect("unhidden back", filtered(mgr, "Neck", "None"), ["Alpha_Neck", "Casual_Mina_Neck", "Zeta_Neck"])
    expect("neck groups after", sorted(groups(mgr, "Neck")), ["Basis", "Kpop"])
    # persistence: hidden + toggles survive Save/Load Settings
    mgr.call_method("Test Toggle Hidden", args=("Alpha_Neck",))
    mgr.call_method("Test Set Toggles", args=(True, False)); mgr.call_method("Test Save Settings")
    mgr.set_editor_property("HiddenItems", []); mgr.set_editor_property("CachedOnlyOwned", False); mgr.set_editor_property("CachedOnlyFav", True)
    mgr.call_method("Test Load Settings")
    expect("hidden reloaded", [str(n) for n in mgr.get_editor_property("HiddenItems")], ["Alpha_Neck"])
    expect("owned toggle reloaded", mgr.get_editor_property("CachedOnlyOwned"), True)
    expect("fav toggle reloaded", mgr.get_editor_property("CachedOnlyFav"), False)
    mgr.call_method("Test Toggle Hidden", args=("Alpha_Neck",)); mgr.call_method("Test Save Settings")
    # tooltip: name, slot label, origin (stub rows are all vanilla) [, row name when it differs]
    mgr.call_method("Test Item Tip", args=("Casual_Mina_Neck",)); tip = str(mgr.get_editor_property("TmpText"))
    expect("tip lines", tip.split("\n"), ["Casual_Mina_Neck", "Neck", "Vanilla · KPOP"])   # row name == display name -> no 4th line
    mgr.call_method("Test Item Tip", args=("Zeta_Neck",)); tip2 = str(mgr.get_editor_property("TmpText"))
    expect("tip vanilla without group", tip2.split("\n")[2], "Vanilla")
    mgr.call_method("Test Item Tip", args=("ModThing",)); tip3 = str(mgr.get_editor_property("TmpText"))
    expect("tip mod origin", tip3.split("\n"), ["ModThing", "Top", "Some Mod"])   # caption of the SomeMod row in the stub DLC_MainTable
run(main)
