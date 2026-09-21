import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def conflicts(mgr, a, b):
    mgr.call_method("Test Conflicts With", args=(a, b)); return mgr.get_editor_property("TmpBool")

def freed(mgr, a, b):
    mgr.call_method("Test Is Freed", args=(a, b)); return mgr.get_editor_property("TmpBool")

def conflicting(mgr, slot, worn):
    mgr.call_method("Test Conflicting Slots", args=(slot, worn)); return sorted(str(n) for n in mgr.get_editor_property("TmpNames"))

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build"); mgr.call_method("Test Build Conflicts"); mgr.set_editor_property("FreedConflicts", [])
    # stub ClothesTypeTable: Top -> [Bra], Dress -> [Bra, Panties, Top], Pants -> [Socks]; at runtime the pairs are symmetric
    pairs = sorted(str(n) for n in mgr.get_editor_property("ConflictPairs"))
    expect("pairs from the table", pairs, ["Dress|Bra", "Dress|Panties", "Dress|Top", "Pants|Socks", "Top|Bra"])
    expect("symmetric", (conflicts(mgr, "Bra", "Top"), conflicts(mgr, "Top", "Bra"), conflicts(mgr, "Bra", "Dress"), conflicts(mgr, "Bra", "Pants")), (True, True, True, False))
    # worn pieces of the stub catalog: Dress05 (Dress), Briefs03 (Briefs), Casual_Mina_Neck (Neck)
    expect("conflicting worn slots", conflicting(mgr, "Bra", ["Dress05", "Briefs03", "Casual_Mina_Neck"]), ["Dress"])
    expect("same slot is not a conflict (exclusivity is the game's)", conflicting(mgr, "Dress", ["Dress05"]), [])
    mgr.call_method("Test Set Freed", args=("Bra", "Dress", True)); expect("freed pair", (freed(mgr, "Bra", "Dress"), freed(mgr, "Dress", "Bra")), (True, True))
    expect("freed pair stays on", conflicting(mgr, "Bra", ["Dress05", "Briefs03"]), [])
    expect("other pairs untouched", conflicting(mgr, "Top", ["Dress05"]), ["Dress"])
    mgr.call_method("Test Set Freed", args=("Dress", "Bra", False)); expect("un-freed (other spelling)", freed(mgr, "Bra", "Dress"), False)
    expect("conflict is back", conflicting(mgr, "Bra", ["Dress05"]), ["Dress"])
    mgr.call_method("Test Set Freed", args=("Bra", "Dress", True)); mgr.call_method("Test Set Freed", args=("Bra", "Dress", True))
    expect("no duplicate keys", [str(n) for n in mgr.get_editor_property("FreedConflicts")], ["Bra|Dress"])
    # settings roundtrip
    mgr.call_method("Test Save Settings"); mgr.set_editor_property("FreedConflicts", []); mgr.call_method("Test Load Settings")
    expect("freed pairs saved", [str(n) for n in mgr.get_editor_property("FreedConflicts")], ["Bra|Dress"])
    mgr.set_editor_property("FreedConflicts", []); mgr.call_method("Test Save Settings")
run(main)
