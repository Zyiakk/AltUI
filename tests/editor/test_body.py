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
    # bone-scale factors per body (Settings.BodyScales) and the generated post-process ABP
    mgr.call_method("Test Body Scales", args=("Body_Nope",))
    expect("missing body -> nine 1.0", [round(x, 3) for x in mgr.get_editor_property("TmpFloats")], [1.0] * 9)
    mgr.call_method("Test Set Body Scales", args=("Body_X", [1.2, 1.0, 0.8, 1.0, 1.0, 1.5, 0.7, 1.1, 0.9]))
    mgr.call_method("Test Body Scales", args=("Body_X",))
    expect("saved factors returned", [round(x, 3) for x in mgr.get_editor_property("TmpFloats")], [1.2, 1.0, 0.8, 1.0, 1.0, 1.5, 0.7, 1.1, 0.9])
    mgr.call_method("Test Set Body Scales", args=("Body_Pre", [1.2, 1.0, 0.8, 1.0, 1.0, 1.5, 0.7, 1.1]))   # saved before the waist slider -> padded with 1.0
    mgr.call_method("Test Body Scales", args=("Body_Pre",))
    expect("eight entries -> waist 1.0 appended", [round(x, 3) for x in mgr.get_editor_property("TmpFloats")], [1.2, 1.0, 0.8, 1.0, 1.0, 1.5, 0.7, 1.1, 1.0])
    mgr.call_method("Test Set Body Scales", args=("Body_Old", [1.2, 1.0, 0.8, 1.0, 1.0, 1.5]))   # saved with fewer sliders -> ignored
    mgr.call_method("Test Body Scales", args=("Body_Old",))
    expect("older layout -> nine 1.0", [round(x, 3) for x in mgr.get_editor_property("TmpFloats")], [1.0] * 9)
    mgr.call_method("Test Vector Or One", args=(unreal.Vector(0, 0, 0),)); expect("zero default -> one", mgr.get_editor_property("TmpVector"), unreal.Vector(1, 1, 1))
    mgr.call_method("Test Vector Or One", args=(unreal.Vector(1.3, 1.2, 1.15),)); expect("real default kept", mgr.get_editor_property("TmpVector"), unreal.Vector(1.3, 1.2, 1.15))
    abp = cdo(M + "/ABP_BodyScale.ABP_BodyScale_C")
    expect("ABP default Breasts", abp.get_editor_property("Breasts"), unreal.Vector(1, 1, 1))
    expect("ABP default Waist", abp.get_editor_property("Waist"), unreal.Vector(1, 1, 1))
run(main)
