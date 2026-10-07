"""Hideable tabs (Options > Tabs): Tab Shown (a switched-off tab is still shown while it is the current page; Options always),
First Visible Page, Toggle Tab Hidden (Options never), OptionsCat / HiddenTabs / TabStyle / TabIconRight survive Save/Load Settings."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def names(mgr, prop):
    return [str(n) for n in mgr.get_editor_property(prop)]


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.set_editor_property("PanelOpen", False)
    mgr.set_editor_property("Page", "Options"); mgr.set_editor_property("HiddenTabs", ["Clothes", "Outfits"])
    mgr.call_method("Test Tab Shown", ("Clothes",)); expect("hidden tab not shown", mgr.get_editor_property("TmpBool"), False)
    mgr.call_method("Test Tab Shown", ("Looks",)); expect("other tab shown", mgr.get_editor_property("TmpBool"), True)
    mgr.call_method("Test Tab Shown", ("Options",)); expect("options shown", mgr.get_editor_property("TmpBool"), True)
    mgr.set_editor_property("Page", "Clothes"); mgr.call_method("Test Tab Shown", ("Clothes",))
    expect("current page shown although hidden", mgr.get_editor_property("TmpBool"), True)
    mgr.set_editor_property("Page", "Options"); mgr.call_method("Test First Visible Page")
    expect("first visible skips hidden", str(mgr.get_editor_property("TmpName")), "Looks")
    mgr.set_editor_property("HiddenTabs", ["Clothes", "Outfits", "Looks", "Bag", "Hair", "Poses", "Weapons", "Look", "Body", "Face", "Mods", "Manage", "Ragdolls", "Kodex"])
    mgr.call_method("Test First Visible Page"); expect("all hidden -> Options", str(mgr.get_editor_property("TmpName")), "Options")
    mgr.set_editor_property("HiddenTabs", ["Clothes", "Outfits"])
    mgr.call_method("Test Toggle Tab Hidden", ("Options",)); expect("options never hidden", "Options" in names(mgr, "HiddenTabs"), False)
    mgr.call_method("Test Toggle Tab Hidden", ("Clothes",)); expect("toggle shows again", names(mgr, "HiddenTabs"), ["Outfits"])
    mgr.call_method("Test Toggle Tab Hidden", ("Mods",)); expect("toggle hides", names(mgr, "HiddenTabs"), ["Outfits", "Mods"])
    # settings round trip
    mgr.set_editor_property("OptionsCat", "Camera"); mgr.set_editor_property("TabStyle", 2); mgr.set_editor_property("TabIconRight", True); mgr.call_method("Test Save Settings")
    mgr.set_editor_property("OptionsCat", "General"); mgr.set_editor_property("HiddenTabs", []); mgr.set_editor_property("TabStyle", 0); mgr.set_editor_property("TabIconRight", False)
    mgr.call_method("Test Load Settings")
    expect("tab style round trip", (mgr.get_editor_property("TabStyle"), mgr.get_editor_property("TabIconRight")), (2, True))
    expect("options cat round trip", str(mgr.get_editor_property("OptionsCat")), "Camera")
    expect("hidden tabs round trip", names(mgr, "HiddenTabs"), ["Outfits", "Mods"])
    mgr.set_editor_property("OptionsCat", "General"); mgr.set_editor_property("HiddenTabs", []); mgr.set_editor_property("TabStyle", 0); mgr.set_editor_property("TabIconRight", False)
    mgr.call_method("Test Save Settings")   # leave a sane save behind
run(main)
