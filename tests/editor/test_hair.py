import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def swatch(mgr, key):
    mgr.call_method("Test Swatch Color", args=(key,)); c = mgr.get_editor_property("ColorCur")
    return mgr.get_editor_property("TmpBool"), (round(c.r, 4), round(c.g, 4), round(c.b, 4))

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build"); mgr.call_method("Test Strings", args=(1,))
    mgr.set_editor_property("HairSwatchesOpen", False)
    mgr.call_method("Test Toggle Hair Swatches"); expect("toggle opens", mgr.get_editor_property("HairSwatchesOpen"), True)
    mgr.call_method("Test Toggle Hair Swatches"); expect("toggle closes", mgr.get_editor_property("HairSwatchesOpen"), False)
    # preset colours: sRGB -> linear (assets/gen/hair_colors.py: Chestnut = rgb(92, 54, 32))
    expect("chestnut", swatch(mgr, "Chestnut"), (True, (0.107, 0.0369, 0.0144)))
    expect("black is dark", swatch(mgr, "Black")[1][0] < 0.01, True); expect("platinum is bright", swatch(mgr, "Platinum")[1][0] > 0.85, True)
    expect("unknown key not found", swatch(mgr, "NoSuchKey")[0], False)
    # the setting survives Save/Load Settings
    mgr.set_editor_property("HairSwatchesOpen", True); mgr.call_method("Test Save Settings"); mgr.set_editor_property("HairSwatchesOpen", False)
    mgr.call_method("Test Load Settings"); expect("swatches open persisted", mgr.get_editor_property("HairSwatchesOpen"), True)
    mgr.set_editor_property("HairSwatchesOpen", False); mgr.call_method("Test Save Settings")
run(main)
