import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


# Options sliders added 2026-10-11 (ragdoll lift per wheel notch, slow motion speed) and the time dilation AltUI asks for.
def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    def rv(v, lo, hi, step):
        mgr.call_method("Test Range", args=(v, lo, hi, step)); return round(mgr.get_editor_property("TmpFloat"), 4)
    def rs(value, lo, hi):
        mgr.call_method("Test Range Slider", args=(value, lo, hi)); return round(mgr.get_editor_property("TmpFloat"), 4)
    expect("slider 0 -> lo", rv(0.0, 2.0, 40.0, 1.0), 2.0)
    expect("slider 1 -> hi", rv(1.0, 2.0, 40.0, 1.0), 40.0)
    expect("whole cm", rv(0.5, 2.0, 40.0, 1.0), 21.0)
    expect("5 % steps", rv(0.24, 5.0, 90.0, 5.0), 25.0)
    expect("clamped above", rv(1.3, 5.0, 90.0, 5.0), 90.0)
    expect("back to the slider", rs(25.0, 5.0, 90.0), round(20.0 / 85.0, 4))
    def tw(slow, freeze, pct):
        mgr.set_editor_property("SlowMoOn", slow); mgr.set_editor_property("FreezeOn", freeze); mgr.set_editor_property("SlowMoPct", pct)
        mgr.call_method("Test Time Wanted"); return round(mgr.get_editor_property("TmpFloat"), 5)
    expect("nothing on", tw(False, False, 0.0), 1.0)
    expect("slow motion default 25 %", tw(True, False, 0.0), 0.25)
    expect("slow motion 40 %", tw(True, False, 40.0), 0.4)
    expect("stopped wins", tw(True, True, 40.0), 0.0001)
    tw(False, False, 0.0)
    mgr.set_editor_property("RagWheelCm", 0.0); mgr.call_method("Test Rag Wheel Cm"); expect("wheel default 10 cm", mgr.get_editor_property("TmpFloat"), 10.0)
    mgr.set_editor_property("RagWheelCm", 3.0); mgr.call_method("Test Rag Wheel Cm"); expect("wheel set", mgr.get_editor_property("TmpFloat"), 3.0)
    mgr.set_editor_property("RagWheelCm", 0.0)


run(main)
