"""Saved colour schemes (Options > Colours): Save Theme Preset stores the base colours + opacities under a trimmed name (empty: nothing,
the same name in another case overwrites), Apply Theme Preset ("ThemeP:<name>") brings them back, Delete removes, the settings keep them."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def col(mgr, key):
    c = mgr.get_editor_property("Theme" + key); return (round(c.r, 3), round(c.g, 3), round(c.b, 3))


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.set_editor_property("PanelOpen", False); mgr.set_editor_property("ThemePresets", {})
    def keys(): return sorted(str(k) for k in mgr.get_editor_property("ThemePresets").keys())
    mgr.set_editor_property("ThemeAccent", unreal.LinearColor(0.1, 0.2, 0.3, 1)); mgr.set_editor_property("BgAlpha", 0.5)
    mgr.call_method("Test Save Theme Preset", args=("  Dunkel ",)); expect("saved, name trimmed", keys(), ["Dunkel"])
    mgr.call_method("Test Save Theme Preset", args=("   ",)); expect("empty name stores nothing", keys(), ["Dunkel"])
    mgr.set_editor_property("ThemeAccent", unreal.LinearColor(0.9, 0.8, 0.7, 1)); mgr.set_editor_property("BgAlpha", 0.7)
    mgr.call_method("Test Save Theme Preset", args=("Hell",)); expect("second scheme", keys(), ["Dunkel", "Hell"])
    mgr.call_method("Test Apply Theme Preset", args=("ThemeP:Dunkel",))
    expect("apply brings colours and opacity back", (col(mgr, "Accent"), round(mgr.get_editor_property("BgAlpha"), 3)), ((0.1, 0.2, 0.3), 0.5))
    mgr.set_editor_property("ThemeAccent", unreal.LinearColor(0.4, 0.4, 0.4, 1)); mgr.call_method("Test Save Theme Preset", args=("dunkel",))
    expect("same name in another case overwrites", len(keys()), 2)
    mgr.call_method("Test Apply Theme Preset", args=("ThemeP:Hell",)); mgr.call_method("Test Apply Theme Preset", args=("ThemeP:Dunkel",))
    expect("overwritten scheme", col(mgr, "Accent"), (0.4, 0.4, 0.4))
    mgr.call_method("Test Apply Theme Preset", args=("ThemeP:Nope",)); expect("unknown scheme changes nothing", col(mgr, "Accent"), (0.4, 0.4, 0.4))
    mgr.call_method("Test Save Settings"); mgr.set_editor_property("ThemePresets", {}); mgr.call_method("Test Load Settings"); expect("settings keep them", len(keys()), 2)
    mgr.call_method("Test Delete Theme Preset", args=("ThemeP:Hell",)); expect("delete", len(keys()), 1)
    mgr.set_editor_property("ThemePresets", {})
    mgr.call_method("Test Save Settings")   # leave a sane save behind
run(main)
