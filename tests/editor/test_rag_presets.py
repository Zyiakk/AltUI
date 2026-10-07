"""Ragdolls scenes (data level, no figures in the editor): save under a name, the same name overwrites (case-insensitive), another
name adds, delete removes. Starts from and leaves the editor's AltUI_Ragdolls slot as it was (deletes what it added)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *


def main():
    mgr = cdo("/Game/Mod/AltUI/BP_AltUIManager.BP_AltUIManager_C")
    def count(i=0):
        mgr.call_method("Test Rag Presets", args=(i,)); return mgr.get_editor_property("TmpI"), mgr.get_editor_property("TmpStr2")
    n0, _ = count()
    mgr.call_method("Test Save Rag Preset", args=("  Szene A ",)); expect("saved, trimmed", count(n0), (n0 + 1, "Szene A"))
    mgr.call_method("Test Save Rag Preset", args=("szene a",)); expect("same name overwrites", count(n0), (n0 + 1, "szene a"))
    mgr.call_method("Test Save Rag Preset", args=("   ",)); expect("empty name saves nothing", count(n0)[0], n0 + 1)
    mgr.call_method("Test Save Rag Preset", args=("Szene B",)); expect("another name adds", count(n0 + 1), (n0 + 2, "Szene B"))
    mgr.call_method("Test Delete Rag Preset", args=(n0 + 1,)); mgr.call_method("Test Delete Rag Preset", args=(n0,))
    expect("deleted again", count()[0], n0)


run(main)
