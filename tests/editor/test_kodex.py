"""Kodex tab: which selections exist (manual chapters from assets/manual/en.md, encyclopedia, passwords), the default."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
import unreal
from edtest_lib import *
import manual
M = "/Game/Mod/AltUI"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    def valid(n):
        mgr.call_method("Test Kodex Valid", args=(n,)); return mgr.get_editor_property("TmpBool")
    for n in ["Man:" + i for i in manual.chapters()] + ["Encyclopedia", "Passwords"]:
        expect("valid " + n, valid(n), True)
    for n in ("Man:gone", "None", "Options"):
        expect("not valid " + n, valid(n), False)
    expect("default = encyclopedia", str(mgr.get_editor_property("KodexSel")), "Encyclopedia")
    # encyclopedia unlock (stub table: Arch_A..Arch_F): rows 0-3 always, the rest from Note_Save.Notes, all with KodexAll
    rows = lambda: [str(n) for n in mgr.get_editor_property("KodexRows")]
    keep = mgr.get_editor_property("KodexAll"); mgr.set_editor_property("KodexAll", False)
    mgr.call_method("Test Kodex Unlocked", args=(["Arch_F", "Arch_Z"],)); expect("first four + unlocked", rows(), ["Arch_A", "Arch_B", "Arch_C", "Arch_D", "Arch_F"])
    mgr.call_method("Test Kodex Unlocked", args=([],)); expect("nothing unlocked: first four", rows(), ["Arch_A", "Arch_B", "Arch_C", "Arch_D"])
    mgr.call_method("Test Kodex Archive Rows"); expect("no game state (editor): first four", rows(), ["Arch_A", "Arch_B", "Arch_C", "Arch_D"])
    mgr.set_editor_property("KodexAll", True)
    mgr.call_method("Test Kodex Unlocked", args=([],)); expect("KodexAll: all", rows(), ["Arch_A", "Arch_B", "Arch_C", "Arch_D", "Arch_E", "Arch_F"])
    mgr.set_editor_property("KodexAll", keep)
    # passwords: where a lock is (cm), in English
    mgr.call_method("Test Strings", args=(1,))
    def place(d, z):
        mgr.call_method("Test Kodex Place Text", args=(d, z)); return mgr.get_editor_property("TmpStr2")
    expect("same floor", place(1234.0, 0.0), "12 m")
    expect("below the threshold", place(800.0, 200.0), "8 m")
    expect("one floor up", place(800.0, 300.0), "8 m \u00b7 one floor up")
    expect("just past the threshold down", place(800.0, -260.0), "8 m \u00b7 one floor down")
    expect("two floors down", place(800.0, -600.0), "8 m \u00b7 2 floors down")
    mgr.call_method("Test Strings", args=(0,))


run(main)
