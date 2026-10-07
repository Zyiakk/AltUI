"""Moving looks, saved faces and make-up presets (context menu Move left / right / to start / to end): order by id."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Load Settings")
    mgr.set_editor_property("LooksSave", None); mgr.call_method("Test Load Looks"); mgr.set_editor_property("CurrentBody", "Body_TestBody")
    mgr.set_editor_property("FacesSave", None); mgr.set_editor_property("FaceValues", {"Face_Smile": 0.5})
    mgr.set_editor_property("Presets", None); mgr.call_method("Test Load Presets"); mgr.call_method("Test Clear Presets")
    for i in range(4):
        mgr.call_method("Test Add Look"); mgr.call_method("Test Add Face", args=("F%d" % i, False)); mgr.call_method("Test Add Preset Icon", args=(20 + i,))
    count = {"Look": lambda: len(mgr.get_editor_property("LooksSave").get_editor_property("Looks")),
             "Face": lambda: len(mgr.get_editor_property("FacesSave").get_editor_property("Faces")),
             "Preset": lambda: len(mgr.get_editor_property("Presets").get_editor_property("Data"))}
    for kind in ("Look", "Face", "Preset"):
        n = count[kind](); base = n - 4   # the editor's save may hold looks / faces from other tests: the new ones are the last four
        def ids():
            out = []
            for i in range(base, n):
                mgr.call_method("Test Entry Id", args=(kind, i)); out.append(mgr.get_editor_property("TmpI"))
            return out
        a, b, c, d = ids()
        steps = [((base + 2, base + 1), [a, c, b, d], "left"), ((base + 1, base + 2), [a, b, c, d], "right"),
                 ((base + 3, base), [d, a, b, c], "to start"), ((base, 1000000000), [a, b, c, d], "to end")]
        for (i, to), want, label in steps:
            mgr.call_method("Test Move " + kind, args=(i, to)); expect("%s %s" % (kind, label), ids(), want)
        mgr.call_method("Test Move " + kind, args=(n + 3, 0)); expect(kind + " invalid index: no change", ids(), [a, b, c, d])
        expect(kind + " count unchanged", count[kind](), n)
        for _ in range(4):
            if kind != "Preset": mgr.call_method("Test Delete " + kind, args=(base,))
    mgr.call_method("Test Clear Presets")


run(main)
