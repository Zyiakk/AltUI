"""Outfit / look tiles: own sizes (0 = never set -> the general tile size) and the outfit grid (0 -> 3 x 3); they survive Save/Load Settings."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    def val(fn):   # pure BP functions are not callable from Python: the Test wrappers write TmpFloat / TmpI / TmpIdx
        if fn in ("Outfit Scale", "Look Scale"): mgr.call_method("Test " + fn); return round(mgr.get_editor_property("TmpFloat"), 3)
        mgr.call_method("Test Outfit Grid"); return mgr.get_editor_property("TmpI" if fn == "Outfit Cols" else "TmpIdx")
    for k, v in (("OutfitScale", 0.0), ("LookScale", 0.0), ("OutfitCols", 0), ("OutfitRows", 0)): mgr.set_editor_property(k, v)
    mgr.set_editor_property("TileScale", 1.4)
    expect("unset sizes follow the tile size", (val("Outfit Scale"), val("Look Scale")), (1.4, 1.4))
    expect("unset grid is 3 x 3", (val("Outfit Cols"), val("Outfit Rows")), (3, 3))
    mgr.set_editor_property("OutfitScale", 0.8); mgr.set_editor_property("LookScale", 1.75); mgr.set_editor_property("OutfitCols", 5); mgr.set_editor_property("OutfitRows", 2)
    expect("own values", (val("Outfit Scale"), val("Look Scale"), val("Outfit Cols"), val("Outfit Rows")), (0.8, 1.75, 5, 2))
    mgr.call_method("Test Save Settings")
    for k, v in (("OutfitScale", 0.0), ("LookScale", 0.0), ("OutfitCols", 0), ("OutfitRows", 0)): mgr.set_editor_property(k, v)
    mgr.call_method("Test Load Settings")
    expect("settings round trip", (round(mgr.get_editor_property("OutfitScale"), 3), round(mgr.get_editor_property("LookScale"), 3), mgr.get_editor_property("OutfitCols"), mgr.get_editor_property("OutfitRows")), (0.8, 1.75, 5, 2))
    for k, v in (("OutfitScale", 0.0), ("LookScale", 0.0), ("OutfitCols", 0), ("OutfitRows", 0)): mgr.set_editor_property(k, v)
    mgr.set_editor_property("TileScale", 1.0); mgr.call_method("Test Save Settings")   # leave a sane save behind
run(main)
