"""Chip rows in alphabetical order (Sort Chips): Basis / Vanilla first, then by the shown name (case-insensitive, custom names count),
Hidden last; both caption kinds (clothes groups, mods)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    def order(groups, look=False):
        mgr.call_method("Test Sort Chips", args=(groups, look)); return [str(n) for n in mgr.get_editor_property("ChipOrder")]
    expect("groups: Basis first, Hidden last, rest alphabetical", order(["Hidden", "zeta_g", "Basis", "Alpha_g", "mid_g"]), ["Basis", "Alpha_g", "mid_g", "zeta_g", "Hidden"])
    expect("mods: Vanilla first", order(["ZMod", "Vanilla", "amod", "Hidden", "BMod"], True), ["Vanilla", "amod", "BMod", "ZMod", "Hidden"])
    expect("same first 12 characters: the next ones decide", order(["LongModNamePrefix_B", "LongModNamePrefix_A"], True), ["LongModNamePrefix_A", "LongModNamePrefix_B"])
    expect("empty", order([]), [])
    mgr.call_method("Test Set Custom Name", args=("mod", "ZMod", "Aaa first"))
    expect("custom name decides", order(["amod", "ZMod"], True), ["ZMod", "amod"])
    mgr.call_method("Test Set Custom Name", args=("mod", "ZMod", ""))
run(main)
