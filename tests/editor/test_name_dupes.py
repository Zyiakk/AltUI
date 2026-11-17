"""2026-11-16: a Manage row whose default name another group / mod shows too gets " (?)" and a tooltip (Name Dupe Tip): mods
that share a text ID show one display string for all of them (seen with two installed mods, 2026-11-16)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build"); mgr.call_method("Test Strings", args=(1,))
    t = lambda s: unreal.Text(s)
    mgr.set_editor_property("ModCaption", {"ModA": t("Same"), "ModB": t("Same"), "ModC": t("Other")})
    def tip(kind, default): mgr.call_method("Test Name Dupe Tip", args=(kind, default)); return str(mgr.get_editor_property("TmpStr2"))
    a = tip("mod", "Same")
    expect("shared mod name has a tip", a != "", True)
    expect("tip lists both", ("pak: ModA" in a, "pak: ModB" in a), (True, True))
    expect("unique mod name: no tip", tip("mod", "Other"), "")
    expect("unique group name: no tip", tip("group", "KPOP"), "")
    expect("other kinds: no tip", tip("item", "Same"), "")
    mgr.set_editor_property("ModCaption", {})
run(main)
