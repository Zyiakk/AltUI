import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def count(mgr, t, filtered=False):
    mgr.call_method("Test Look Count", args=(t, filtered)); return mgr.get_editor_property("TmpI")

def caption(mgr, t):
    mgr.call_method("Test Look Caption", args=(t,)); return str(mgr.get_editor_property("TmpText"))

def type_of(mgr, name):
    mgr.call_method("Test Look Type Of", args=(name,)); return str(mgr.get_editor_property("TmpName"))

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    # stub tables: SkinTable 1 row, MakeupTable Lips x2 / Eyebrow x1, EyeTable Eye x1 (type Eye is EyeTable)
    expect("skin count", count(mgr, "Skin"), 1)
    expect("lips count", count(mgr, "Lips"), 2)
    expect("eyebrow count", count(mgr, "Eyebrow"), 1)
    expect("eye count (EyeTable)", count(mgr, "Eye"), 1)
    expect("cheeks count", count(mgr, "Cheeks"), 0)
    expect("all count = skin + every make-up type (no presets)", count(mgr, "All"), 5)
    expect("type of a row", (type_of(mgr, "Skin_Default"), type_of(mgr, "Lips_01"), type_of(mgr, "Eye_1"), type_of(mgr, "Foo")), ("Skin", "Lips", "Eye", "None"))
    mgr.call_method("Test Strings", args=(2,))   # German: own key Look_Lips
    expect("caption lips", caption(mgr, "Lips"), "Lippen")
    expect("caption all", caption(mgr, "All"), "Alle")
    mgr.call_method("Test Strings", args=(3,)); expect("caption lips zh", caption(mgr, "Lips"), "嘴唇")
    expect("caption cheeks zh", caption(mgr, "Cheeks"), "脸颊")
    expect("caption unknown", caption(mgr, "Foo"), "Foo")
    # appearance search (LookSearchText): row name, custom name, mod caption; counts "total (hits)" via Look Count(filtered)
    mgr.call_method("Test Strings", args=(1,)); mgr.call_method("Test Load Names")
    mgr.set_editor_property("LookSearchText", "lips_0"); expect("search: row names", (count(mgr, "Lips", True), count(mgr, "Eyebrow", True), count(mgr, "Lips"), count(mgr, "All", True)), (2, 0, 2, 2))
    mgr.set_editor_property("LookSearchText", "EYEBROW"); expect("search: case-insensitive", count(mgr, "Eyebrow", True), 1)
    mgr.call_method("Test Set Custom Name", args=("makeup", "Lips_02", "Rot")); mgr.set_editor_property("LookSearchText", "rot")
    expect("search: custom name", count(mgr, "Lips", True), 1); mgr.call_method("Test Set Custom Name", args=("makeup", "Lips_02", ""))
    mgr.set_editor_property("LookSearchText", "zzz"); expect("search: miss", (count(mgr, "Skin", True), count(mgr, "Skin")), (0, 1))
    mgr.set_editor_property("LookSearchText", "")
run(main)