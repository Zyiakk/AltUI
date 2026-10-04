"""Quick menu: sector under the mouse (dead zone, sector 0 centred at the top, clockwise; 1/2/7/32 sectors), Quick Add / Move /
Remove, QuickItems and QuickKey survive Save/Load Settings, fixed items and tabs are found, unknown targets not."""
import sys, os, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")

    def sector(deg, count, r=100.0, radius=100.0):   # deg clockwise from the top
        a = math.radians(deg); mgr.call_method("Test Quick Sector At", (r * math.sin(a), -r * math.cos(a), radius, count)); return mgr.get_editor_property("TmpI")
    expect("dead zone", sector(10, 7, r=30.0), -1)
    expect("no sectors", sector(10, 0), -1)
    expect("one sector everywhere", [sector(d, 1) for d in (0, 90, 200, 359)], [0, 0, 0, 0])
    expect("two: upper half 0, lower half 1", [sector(0, 2), sector(80, 2), sector(100, 2), sector(180, 2), sector(260, 2), sector(280, 2)], [0, 0, 1, 1, 1, 0])
    w = 360.0 / 7
    expect("seven: centred at the top", [sector(-w / 2 + 1, 7), sector(w / 2 - 1, 7), sector(w / 2 + 1, 7), sector(360 - w / 2 - 1, 7)], [0, 0, 1, 6])
    w = 360.0 / 32
    expect("32: last sector left of the top", [sector(-w, 32), sector(0, 32), sector(w, 32), sector(180, 32)], [31, 0, 1, 16])
    # list editing
    mgr.set_editor_property("QuickItems", [])
    for it in ("freecam", "tab:Clothes", "panel", "freecam"): mgr.call_method("Test Quick Add", (it,))
    expect("add appends once", [str(x) for x in mgr.get_editor_property("QuickItems")], ["freecam", "tab:Clothes", "panel"])
    mgr.call_method("Test Quick Move", ("panel", -1)); expect("move up", [str(x) for x in mgr.get_editor_property("QuickItems")], ["freecam", "panel", "tab:Clothes"])
    mgr.call_method("Test Quick Move", ("freecam", -1)); expect("move at the top: nothing", [str(x) for x in mgr.get_editor_property("QuickItems")], ["freecam", "panel", "tab:Clothes"])
    mgr.call_method("Test Quick Move", ("tab:Clothes", 1)); expect("move at the end: nothing", [str(x) for x in mgr.get_editor_property("QuickItems")], ["freecam", "panel", "tab:Clothes"])
    mgr.call_method("Test Quick Remove", ("panel",)); expect("remove", [str(x) for x in mgr.get_editor_property("QuickItems")], ["freecam", "tab:Clothes"])
    for it, want in (("freecam", True), ("posestop", True), ("tab:Clothes", True), ("tab:Nowhere", False), ("look:99999", False), ("modentry:Nope/Nope", False), ("bogus", False)):
        mgr.call_method("Test Quick Find", (it,)); expect("find " + it, mgr.get_editor_property("TmpBool"), want)
    # a mod item whose target is gone (a mod renamed its row) shows its own id, not the caption looked up before it
    mgr.set_editor_property("QModCaption", "Stale caption")
    mgr.call_method("Test Quick Caption", ("modaction:Gone|Renamed_Row",)); expect("missing mod action: its id", str(mgr.get_editor_property("TmpStr")), "modaction:Gone|Renamed_Row")
    # settings round trip
    mgr.set_editor_property("QuickKey", "F"); mgr.call_method("Test Save Settings")
    mgr.set_editor_property("QuickKey", "4"); mgr.set_editor_property("QuickItems", []); mgr.call_method("Test Load Settings")
    expect("quick key round trip", str(mgr.get_editor_property("QuickKey")), "F")
    expect("quick items round trip", [str(x) for x in mgr.get_editor_property("QuickItems")], ["freecam", "tab:Clothes"])
    # opacity of the wheel's fills: follows the panel background until set, then its own; kept in the settings
    def qa(): mgr.call_method("Test Quick Alpha"); return round(mgr.get_editor_property("TmpFloat"), 3)
    mgr.set_editor_property("QuickAlpha", 0.0); mgr.set_editor_property("BgAlpha", 0.6); expect("quick opacity follows the background", qa(), 0.6)
    mgr.set_editor_property("QuickAlpha", 0.35); expect("own quick opacity", qa(), 0.35)
    mgr.call_method("Test Save Settings"); mgr.set_editor_property("QuickAlpha", 0.0); mgr.call_method("Test Load Settings"); expect("quick opacity round trip", qa(), 0.35)
    mgr.set_editor_property("QuickAlpha", 0.0)
    mgr.set_editor_property("QuickKey", "4"); mgr.set_editor_property("QuickItems", []); mgr.call_method("Test Save Settings")   # leave a sane save behind
run(main)
