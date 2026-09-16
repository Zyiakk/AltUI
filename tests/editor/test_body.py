import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Body Mods")   # stub DLC_MainTable: Body_TestBody + SomeMod
    expect("body mods filtered by prefix", [str(n) for n in mgr.get_editor_property("BodyMods")], ["Body_TestBody"])
    mgr.call_method("Test Body Caption", args=("Body_TestBody",))
    expect("caption from mod table", str(mgr.get_editor_property("TmpText")), "Test Body")
    mgr.call_method("Test Body Mods")
    expect("rescan does not duplicate", len(mgr.get_editor_property("BodyMods")), 1)
run(main)
