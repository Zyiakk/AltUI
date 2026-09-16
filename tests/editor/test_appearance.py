import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def count(mgr, t):
    mgr.call_method("Test Look Count", args=(t,)); return mgr.get_editor_property("TmpI")

def caption(mgr, t):
    mgr.call_method("Test Look Caption", args=(t,)); return str(mgr.get_editor_property("TmpText"))

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    # stub tables: SkinTable 1 row, MakeupTable Lips x2 / Eyebrow x1, EyeTable Eye x1 (type Eye is EyeTable)
    expect("skin count", count(mgr, "Skin"), 1)
    expect("lips count", count(mgr, "Lips"), 2)
    expect("eyebrow count", count(mgr, "Eyebrow"), 1)
    expect("eye count (EyeTable)", count(mgr, "Eye"), 1)
    expect("cheeks count", count(mgr, "Cheeks"), 0)
    mgr.call_method("Test Strings", args=(2,))   # German: own key Look_Lips
    expect("caption lips", caption(mgr, "Lips"), "Lippen")
    mgr.call_method("Test Strings", args=(3,)); expect("caption lips zh", caption(mgr, "Lips"), "嘴唇")
    expect("caption cheeks zh", caption(mgr, "Cheeks"), "脸颊")
    expect("caption unknown", caption(mgr, "Foo"), "Foo")
run(main)
