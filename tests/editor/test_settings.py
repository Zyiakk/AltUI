"""Save Settings -> Load Settings round trip: values that are legitimately 0 (camera distance 0 %, opacity 0 %) survive
(SaveVersion >= 1), the panel key and the layout come back, an unset key keeps the manager default."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.set_editor_property("CamDist", 0.0); mgr.set_editor_property("BgAlpha", 0.0); mgr.set_editor_property("TileAlpha", 0.0)
    mgr.set_editor_property("CamFov", 0.45); mgr.set_editor_property("ToggleKey", "G"); mgr.set_editor_property("LeftFree", 3); mgr.set_editor_property("LangChoice", 2); mgr.set_editor_property("GroupLen", 7); mgr.set_editor_property("ChipH", 300)
    mgr.set_editor_property("TipNoPrefix", True); mgr.set_editor_property("TipNoIds", True)
    mgr.set_editor_property("UnownedMode", 2); mgr.set_editor_property("RagKey", "H")
    mgr.call_method("Test Save Settings")
    sg = mgr.get_editor_property("Settings")
    expect("save version written", sg.get_editor_property("SaveVersion"), 2)
    expect("theme flag written", sg.get_editor_property("ThemeSet"), True)
    # scramble, then reload
    mgr.set_editor_property("CamDist", 1.0); mgr.set_editor_property("BgAlpha", 0.5); mgr.set_editor_property("TileAlpha", 0.5)
    mgr.set_editor_property("CamFov", 0.8); mgr.set_editor_property("ToggleKey", "B"); mgr.set_editor_property("LeftFree", 0); mgr.set_editor_property("LangChoice", 0); mgr.set_editor_property("GroupLen", 0); mgr.set_editor_property("ChipH", 0)
    mgr.set_editor_property("TipNoPrefix", False); mgr.set_editor_property("TipNoIds", False)
    mgr.set_editor_property("UnownedMode", 0); mgr.set_editor_property("RagKey", "G")
    mgr.call_method("Test Load Settings")
    expect("ragdoll key round trip", str(mgr.get_editor_property("RagKey")), "H")
    expect("unowned mode round trip", mgr.get_editor_property("UnownedMode"), 2)
    expect("tooltip options round trip", (mgr.get_editor_property("TipNoPrefix"), mgr.get_editor_property("TipNoIds")), (True, True))
    expect("cam dist 0 survives", mgr.get_editor_property("CamDist"), 0.0)
    expect("bg alpha 0 survives", mgr.get_editor_property("BgAlpha"), 0.0)
    expect("tile alpha 0 survives", mgr.get_editor_property("TileAlpha"), 0.0)
    expect("fov round trip", round(mgr.get_editor_property("CamFov"), 3), 0.45)
    expect("key round trip", str(mgr.get_editor_property("ToggleKey")), "G")
    expect("layout round trip", mgr.get_editor_property("LeftFree"), 3)
    expect("language round trip", mgr.get_editor_property("LangChoice"), 2)
    expect("group length round trip", mgr.get_editor_property("GroupLen"), 7)
    expect("chip height round trip", mgr.get_editor_property("ChipH"), 300)
    expect("derived bg alpha follows", round(mgr.get_editor_property("ColBg").a, 3), 0.0)
    # legacy save (SaveVersion 0): 0 means "never set" -> defaults; unset key -> manager default stays
    mgr.call_method("Test Legacy Save"); mgr.set_editor_property("ToggleKey", "B"); mgr.call_method("Test Load Settings")
    expect("legacy cam dist default", mgr.get_editor_property("CamDist"), 1.0)
    expect("legacy scroll default", mgr.get_editor_property("ScrollMult"), 4.0)
    expect("unset key keeps default", str(mgr.get_editor_property("ToggleKey")), "B")
    expect("legacy keeps the other values", mgr.get_editor_property("LeftFree"), 3)
    # layout: a save from before version 2 holds the old default "no space" (0) -> "one third" (1) once; a 0 saved since stays
    mgr.call_method("Test Legacy Layout"); mgr.call_method("Test Load Settings")
    expect("old layout default becomes one third", mgr.get_editor_property("LeftFree"), 1)
    mgr.set_editor_property("LeftFree", 0); mgr.call_method("Test Save Settings"); mgr.set_editor_property("LeftFree", 3); mgr.call_method("Test Load Settings")
    expect("a chosen 'no space' stays", mgr.get_editor_property("LeftFree"), 0)
    mgr.set_editor_property("CamDist", 1.0); mgr.set_editor_property("BgAlpha", 0.88); mgr.set_editor_property("TileAlpha", 1.0); mgr.set_editor_property("CamFov", 0.8)
    # walk / run speed (Options > Move): round trip, 0 = never set = 100 %, slider <-> percent
    mgr.set_editor_property("MoveOn", True); mgr.set_editor_property("WalkSpeedPct", 75.0); mgr.set_editor_property("RunSpeedPct", 160.0)
    mgr.call_method("Test Save Settings")
    mgr.set_editor_property("MoveOn", False); mgr.set_editor_property("WalkSpeedPct", 0.0); mgr.set_editor_property("RunSpeedPct", 0.0)
    mgr.call_method("Test Load Settings")
    expect("move on round trip", mgr.get_editor_property("MoveOn"), True)
    expect("walk speed round trip", round(mgr.get_editor_property("WalkSpeedPct"), 1), 75.0)
    expect("run speed round trip", round(mgr.get_editor_property("RunSpeedPct"), 1), 160.0)
    def pct(v): mgr.call_method("Test Speed Pct", args=(v,)); return round(mgr.get_editor_property("TmpFloat"), 2)
    def sld(p): mgr.call_method("Test Speed Slider", args=(p,)); return round(mgr.get_editor_property("TmpFloat"), 3)
    expect("slider 0 = 50 %", pct(0.0), 50.0); expect("slider 1 = 200 %", pct(1.0), 200.0); expect("snaps to 5 %", pct(0.34), 100.0)
    expect("100 % = 1/3", sld(100.0), 0.333); expect("never set = 100 %", sld(0.0), 0.333); expect("200 % = 1", sld(200.0), 1.0)
    mgr.set_editor_property("MoveOn", False); mgr.set_editor_property("WalkSpeedPct", 0.0); mgr.set_editor_property("RunSpeedPct", 0.0)
    # walk / run style: chips "MStyleW<key>" / "MStyleR<key>", kept in the settings
    mgr.set_editor_property("WalkStyle", "None"); mgr.set_editor_property("RunStyle", "None")
    mgr.call_method("Test Select Move Style", args=("MStyleWHurt",)); expect("walk style chip", str(mgr.get_editor_property("WalkStyle")), "Hurt")
    mgr.call_method("Test Select Move Style", args=("MStyleRNormal",)); expect("run style chip", str(mgr.get_editor_property("RunStyle")), "Normal")
    expect("walk style untouched by the run chip", str(mgr.get_editor_property("WalkStyle")), "Hurt")
    mgr.call_method("Test Save Settings"); mgr.set_editor_property("WalkStyle", "None"); mgr.call_method("Test Load Settings")
    expect("walk style round trip", str(mgr.get_editor_property("WalkStyle")), "Hurt")
    mgr.set_editor_property("WalkStyle", "None"); mgr.set_editor_property("RunStyle", "None")
    mgr.set_editor_property("LeftFree", 0); mgr.set_editor_property("LangChoice", 0); mgr.set_editor_property("GroupLen", 0); mgr.set_editor_property("ChipH", 0); mgr.set_editor_property("RagKey", "G"); mgr.call_method("Test Save Settings")   # leave a sane save behind
run(main)
