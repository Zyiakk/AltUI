import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Build"); mgr.call_method("Test Strings", args=(1,))
    # snapshot carries the body variant (no player in the commandlet: clothes/makeup stay empty)
    mgr.set_editor_property("CurrentBody", "Body_TestBody"); mgr.call_method("Test Snapshot Body")
    expect("snapshot body", str(mgr.get_editor_property("TmpName")), "Body_TestBody")
    # looks save: fresh object, add, name, rename, delete, id never reused
    mgr.set_editor_property("LooksSave", None); mgr.call_method("Test Load Looks")
    ls = mgr.get_editor_property("LooksSave"); expect("looks save valid", ls is not None, True)
    mgr.call_method("Test Looks Count"); expect("no looks", mgr.get_editor_property("TmpI"), 0)
    mgr.call_method("Test Add Look"); mgr.call_method("Test Looks Count"); expect("one look", mgr.get_editor_property("TmpI"), 1)
    mgr.call_method("Test Look Name", args=(0,)); expect("default name", str(mgr.get_editor_property("TmpStr2")), "Look 1")
    mgr.call_method("Test Look Id", args=(0,)); first_id = mgr.get_editor_property("TmpI"); expect("id >= 1", first_id >= 1, True)
    mgr.call_method("Test Set Look Name", args=(0, "  Büro  ")); mgr.call_method("Test Look Name", args=(0,)); expect("renamed", str(mgr.get_editor_property("TmpStr2")), "Büro")
    mgr.call_method("Test Set Look Name", args=(0, "   ")); mgr.call_method("Test Look Name", args=(0,)); expect("blank -> default", str(mgr.get_editor_property("TmpStr2")), "Look 1")
    mgr.call_method("Test Add Look"); mgr.call_method("Test Look Id", args=(1,)); expect("second id", mgr.get_editor_property("TmpI"), first_id + 1)
    mgr.call_method("Test Delete Look", args=(0,)); mgr.call_method("Test Looks Count"); expect("deleted", mgr.get_editor_property("TmpI"), 1)
    mgr.call_method("Test Look Id", args=(0,)); expect("remaining is second", mgr.get_editor_property("TmpI"), first_id + 1)
    mgr.call_method("Test Add Look"); mgr.call_method("Test Look Id", args=(1,)); expect("id not reused", mgr.get_editor_property("TmpI"), first_id + 2)
    mgr.call_method("Test Delete Look", args=(1,)); mgr.call_method("Test Delete Look", args=(0,))
    mgr.call_method("Test Looks Count"); expect("empty again", mgr.get_editor_property("TmpI"), 0)
run(main)
