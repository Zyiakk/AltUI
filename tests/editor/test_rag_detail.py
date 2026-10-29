"""BP_AltUIRagdoll fingers and eyes: curl in the bone's space, lid in the parent's, gaze from a target (CDO, test events)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *

M = unreal.MathLibrary


def rnd(r): return (round(r.pitch, 2), round(r.yaw, 2), round(r.roll, 2))


def main():
    f = cdo("/Game/Mod/AltUI/BP_AltUIRagdoll.BP_AltUIRagdoll_C")
    ref = unreal.Rotator(roll=93.685, pitch=-35.202, yaw=-20.241); axis = unreal.Vector(0, 0, -1)
    f.call_method("Test Curl Rot", args=(ref, axis, 0.0)); expect("curl 0 = base pose", rnd(f.get_editor_property("TmpTurnLocal")), rnd(ref))
    f.call_method("Test Curl Rot", args=(ref, axis, 60.0))
    want = M.compose_rotators(M.rotator_from_axis_and_angle(axis, 60.0), ref)   # A = delta, B = ref: in the bone's own space
    expect("curl 60 in the bone's space", rnd(f.get_editor_property("TmpTurnLocal")), rnd(want))
    flat = unreal.Rotator(0, 0, 0)
    f.call_method("Test Curl Rot", args=(flat, axis, 90.0)); expect("about -Z from zero: yaw -90", rnd(f.get_editor_property("TmpTurnLocal")), (0.0, -90.0, 0.0))
    lref = unreal.Rotator(roll=-174.902, pitch=4.482, yaw=-14.831); lax = unreal.Vector(-0.052, 0.106, 0.993)
    f.call_method("Test Lid Rot", args=(lref, lax, 40.0))
    expect("lid in the parent's space", rnd(f.get_editor_property("TmpTurnWorld")), rnd(M.compose_rotators(lref, M.rotator_from_axis_and_angle(lax, 40.0))))
    head = unreal.Transform(); eyes = unreal.Vector(0, 0, 0)
    def gz(t): f.call_method("Test Gaze", args=(head, eyes, t)); v = f.get_editor_property("TmpGaze"); return (round(v.x, 2), round(v.y, 2))
    expect("straight ahead", gz(unreal.Vector(0, 100, 0)), (0.0, 0.0))
    expect("10 deg to her left", gz(unreal.Vector(0, 100, -17.633)), (-0.4, 0.0))
    expect("far right: capped", gz(unreal.Vector(0, 100, 100)), (1.0, 0.0))
    expect("up 11.3 deg", gz(unreal.Vector(20, 100, 0)), (0.0, 0.57))
    expect("down: capped", gz(unreal.Vector(-100, 100, 0)), (0.0, -1.0))


run(main)
