import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.set_editor_property("Outfits", None)
    mgr.call_method("Test Load Outfits")      # no slot "Outfits" in the editor -> new Outfits_Save object
    o = mgr.get_editor_property("Outfits")
    report("outfits object created", o is not None)
    expect("outfits class", o.get_class().get_name(), "Outfits_Save_C")
    expect("outfits empty", len(o.get_editor_property("outfits")), 0)
run(main)
