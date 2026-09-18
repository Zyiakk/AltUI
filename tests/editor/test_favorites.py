import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def filtered(mgr, slot, only_fav):
    mgr.call_method("Test Filter", args=(slot, "None", "", False, only_fav, False))
    return [str(n) for n in mgr.get_editor_property("TmpNames")]

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build")
    mgr.set_editor_property("Favorites", []); mgr.set_editor_property("PanelOpen", False)
    mgr.call_method("Test Toggle Fav", args=("Zeta_Neck",))
    expect("fav added", filtered(mgr, "Neck", True), ["Zeta_Neck"])
    mgr.call_method("Test Toggle Fav", args=("Alpha_Neck",))
    expect("two favs", filtered(mgr, "Neck", True), ["Alpha_Neck", "Zeta_Neck"])
    mgr.call_method("Test Toggle Fav", args=("Zeta_Neck",))
    expect("fav removed", filtered(mgr, "Neck", True), ["Alpha_Neck"])
    # persistence: discard favourites, reload settings
    mgr.set_editor_property("Favorites", []); mgr.set_editor_property("CurrentSlot", "Boots")
    mgr.call_method("Test Load Settings")
    expect("favs reloaded", [str(n) for n in mgr.get_editor_property("Favorites")], ["Alpha_Neck"])
    report("save exists", unreal.GameplayStatics.does_save_game_exist("AltUI", 0))
run(main)
