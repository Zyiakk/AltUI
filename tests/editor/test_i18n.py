import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def t(mgr, key):
    mgr.call_method("Test T", args=(key,)); return str(mgr.get_editor_property("TmpText"))

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    for choice, exp in ((1, "Clothes"), (2, "Kleidung"), (3, "服装"), (4, "Одежда"), (5, "Vestimenta")):
        mgr.call_method("Test Strings", args=(choice,))
        expect("tab clothes lang %d" % choice, t(mgr, "Tab_Clothes"), exp)
    expect("unknown key falls back to key", t(mgr, "Slot_Foo"), "Slot_Foo")
    expect("language chip names constant", t(mgr, "Chip_LangEn"), "English"); expect("ru chip name", t(mgr, "Chip_LangRu"), "Русский")
    expect("es look term from game", t(mgr, "Look_Eye"), "Pupilas")
    mgr.call_method("Test Strings", args=(0,))   # Auto: follows the editor/system language
    cur = unreal.InternationalizationLibrary.get_current_language()
    exp = {"de": "Optionen", "zh": "选项", "ru": "Настройки", "es": "Opciones"}.get(cur[:2], "Options")
    expect("auto follows current language (%s)" % cur, t(mgr, "Tab_Options"), exp)
run(main)
