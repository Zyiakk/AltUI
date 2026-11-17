import sys, os, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
import share_format as sf
from edtest_lib import *
M = "/Game/Mod/AltUI"

def stamps(mgr, i):
    mgr.call_method("Test Look Stamps", args=(i,)); return mgr.get_editor_property("TmpKey1"), mgr.get_editor_property("TmpKey2")

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build"); mgr.call_method("Test Strings", args=(1,))
    mgr.set_editor_property("CurrentBody", "Body_TestBody"); mgr.call_method("Test Snapshot Body")
    unreal.GameplayStatics.delete_game_in_slot("AltUI_Looks", 0); mgr.set_editor_property("LooksSave", None); mgr.call_method("Test Load Looks")
    mgr.call_method("Test Looks Count"); expect("no looks", mgr.get_editor_property("TmpI"), 0)
    mgr.call_method("Test Now Stamp"); now = mgr.get_editor_property("TmpKey")
    expect("now > 2026-01-01", now > 1767225600, True); expect("now < 2100", now < 4102444800, True)
    mgr.call_method("Test Now Offset"); off = mgr.get_editor_property("TmpI")
    expect("offset in quarter hours", off % 15, 0); expect("offset within 14 h", abs(off) <= 840, True)
    mgr.call_method("Test Add Look"); c, ch = stamps(mgr, 0)
    expect("add: created > 0", c > 1767225600, True); expect("add: created == changed", c, ch)
    time.sleep(1.1)
    mgr.call_method("Test Update Look Keep", args=(0,)); c2, ch2 = stamps(mgr, 0)
    expect("update: created kept", c2, c); expect("update: changed later", ch2 > ch, True)
    mgr.call_method("Test Set Look Name", args=(0, "Renamed")); c3, ch3 = stamps(mgr, 0)
    expect("rename: created same", c3, c2); expect("rename: changed same", ch3, ch2)
    # import (full, keeping a piece that is not installed): a new look with both stamps = now
    mgr.call_method("Test Share Real Item"); real = str(mgr.get_editor_property("TmpName"))
    lk = sf.sample_look(1); d = lk["data"]
    d.update({"Worn": [real, "NoSuchPiece"], "Colors": {real: [1.0, 0.0, 0.0, 1.0], "NoSuchPiece": [0.0, 1.0, 0.0, 1.0]}, "Hair": "None", "Skin": "None", "Body": "None", "Makeup": {}, "SlotColors": {}})
    lk["refs"] = [{"type": "clothes", "item": "NoSuchPiece", "label": "Ghost skirt", "mod": "NoSuchMod"}]
    doc = sf.encode({"altui": "share", "version": 1, "entries": [lk], "mods": {"NoSuchMod": "Ghost Mod"}})
    time.sleep(1.1)
    mgr.call_method("Test Share Import", args=(doc, False))   # the hook reads the imported look's stamps into TmpKey1/2 and removes it again
    ic, ich = mgr.get_editor_property("TmpKey1"), mgr.get_editor_property("TmpKey2")
    expect("import: created == changed", ic, ich); expect("import: stamp new", ic > c2, True)
    mgr.call_method("Test Looks Count"); expect("import: look removed by hook", mgr.get_editor_property("TmpI"), 1)
    # clean copy of a look holding a piece that is not installed: a new look right after it, stamps new
    mgr.set_editor_property("TmpNames", ["NoSuchPiece"]); mgr.call_method("Test Look Worn", args=(0,))
    time.sleep(1.1)
    mgr.call_method("Test Look Clean Copy", args=(0,)); mgr.call_method("Test Looks Count"); expect("clean copy made", mgr.get_editor_property("TmpI"), 2)
    cc, cch = stamps(mgr, 1)
    expect("clean: created == changed", cc, cch); expect("clean: stamps new", cc > c3 and cc > ch3, True)
    mgr.call_method("Test Delete Look", args=(1,)); mgr.call_method("Test Delete Look", args=(0,))
    mgr.call_method("Test Looks Count"); expect("empty again", mgr.get_editor_property("TmpI"), 0)
    # display order: beta, Alpha, alpha, Gamma; changed 0, 300, 100, 0
    for n in ("beta", "Alpha", "alpha", "Gamma"):
        mgr.call_method("Test Add Look"); mgr.call_method("Test Looks Count"); mgr.call_method("Test Set Look Name", args=(mgr.get_editor_property("TmpI") - 1, n))
    for i, ch in enumerate((0, 300, 100, 0)): mgr.call_method("Test Set Look Stamps", args=(i, 1000 + i, ch))
    def order(mode):
        mgr.set_editor_property("LooksSort", mode); mgr.call_method("Test Look Order"); return list(mgr.get_editor_property("TmpInts"))
    for mode, want in ((0, [0, 1, 2, 3]), (1, [1, 2, 0, 3]), (2, [3, 0, 1, 2]), (3, [3, 2, 1, 0]), (4, [0, 1, 2, 3]), (5, [1, 2, 0, 3]), (6, [0, 3, 2, 1])):
        expect("order mode %d" % mode, order(mode), want)
    # display position 1 in mode 1 is the look with array index 2 ("alpha"): a tile gets that index, not its position (On Look Clicked is not callable from Python)
    expect("mode 1 order", order(1), [1, 2, 0, 3]); mgr.call_method("Test Look Order"); pos1 = list(mgr.get_editor_property("TmpInts"))[1]
    mgr.call_method("Test Look Name", args=(pos1,)); expect("position 1 holds alpha", str(mgr.get_editor_property("TmpStr2")), "alpha")
    # Quick Find resolves "look:<Id>" to the array index, whatever the display order (mode 1: "alpha" is shown at 1 but sits at array index 2)
    mgr.call_method("Test Look Id", args=(2,)); lid = mgr.get_editor_property("TmpI")
    mgr.call_method("Test Quick Find", ("look:%d" % lid,)); expect("quick find ok", mgr.get_editor_property("TmpBool"), True)
    expect("quick find: array index, not position", mgr.get_editor_property("TmpI"), 2)
    mgr.call_method("Test Look Id", args=(3,)); lid3 = mgr.get_editor_property("TmpI")
    mgr.set_editor_property("LooksSort", 2); mgr.call_method("Test Quick Find", ("look:%d" % lid3,)); expect("quick find mode 2 (Gamma shown first)", mgr.get_editor_property("TmpI"), 3)
    mgr.set_editor_property("LooksSort", 0)
    for _ in range(4): mgr.call_method("Test Delete Look", args=(0,))
    mgr.call_method("Test Looks Count"); expect("empty at the end", mgr.get_editor_property("TmpI"), 0)
    # the "Sort: ..." link: Set Looks Sort saves and rebuilds the status bar; the link shows the order
    mgr.call_method("Set Looks Sort", args=(3,)); expect("Set Looks Sort(3)", mgr.get_editor_property("LooksSort"), 3)
    mgr.set_editor_property("LooksSort", 0); mgr.call_method("Test Load Settings"); expect("saved with the settings", mgr.get_editor_property("LooksSort"), 3)
    mgr.call_method("Test T", args=("Sort_Newest",)); newest = str(mgr.get_editor_property("TmpText"))
    mgr.call_method("Test Looks Sort Caption"); cap = str(mgr.get_editor_property("TmpText"))
    expect("link shows Sort_Newest", newest in cap and cap != newest, True)
    mgr.call_method("Test Menu Action", args=("LookSort1",)); expect("On Menu Action(LookSort1)", mgr.get_editor_property("LooksSort"), 1)
    mgr.call_method("Test Looks Sort Caption"); expect("caption follows the order", newest in str(mgr.get_editor_property("TmpText")), False)
    mgr.call_method("Set Looks Sort", args=(0,)); expect("back to Custom", mgr.get_editor_property("LooksSort"), 0)
    # tile tooltip: local date YYYY-MM-DD (noon UTC: any offset <= 12 h stays on the day)
    import datetime
    mgr.call_method("Test Now Offset"); offm = mgr.get_editor_property("TmpI")
    for t in (86400 * 20404 + 43200, 86400 * 19000 + 5):
        want = (datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=t, minutes=offm)).strftime("%Y-%m-%d")
        mgr.call_method("Test Stamp Date", args=(t,)); expect("stamp date %d" % t, str(mgr.get_editor_property("TmpStr")), want)
    mgr.call_method("Test Add Look"); mgr.call_method("Test Set Look Stamps", args=(0, 0, 0))
    mgr.call_method("Test Look Date Tip", args=(0,)); expect("date tip: both 0 = empty", str(mgr.get_editor_property("TmpStr")), "")
    mgr.call_method("Test Set Look Stamps", args=(0, 86400 * 20404 + 43200, 0))
    mgr.call_method("Test Look Date Tip", args=(0,)); tip = str(mgr.get_editor_property("TmpStr"))
    expect("date tip: created only", tip.startswith("Created 2025-11-1") and " · " not in tip, True)
    mgr.call_method("Test Set Look Stamps", args=(0, 86400 * 20404 + 43200, 86400 * 20405 + 43200))
    mgr.call_method("Test Look Date Tip", args=(0,)); tip = str(mgr.get_editor_property("TmpStr"))
    expect("date tip: both parts", tip.startswith("Created 2025-11-1") and " · Changed 2025-11-1" in tip, True)
    mgr.call_method("Test Set Look Stamps", args=(0, 0, 86400 * 20405 + 43200))
    mgr.call_method("Test Look Date Tip", args=(0,)); expect("date tip: changed only", str(mgr.get_editor_property("TmpStr")).startswith("Changed 2025-11-1"), True)
    mgr.call_method("Test Delete Look", args=(0,))
run(main)
