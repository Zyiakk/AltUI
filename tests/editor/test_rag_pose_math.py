"""Ragdoll poses (figure side, no mesh needed): Merge Rotations takes only the rotation of the bones a saved pose has and leaves
the root (index 0), the pelvis and every other bone alone; Root Local turns the pelvis' wanted world placement (figure yaw + saved
tilt, current XY, floor height) into the figure's component space."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *


def tf(loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    """rot as (roll, pitch, yaw)"""
    return unreal.Transform(unreal.Vector(*loc), unreal.Rotator(*rot), unreal.Vector(*scale))


def near(a, b, eps=0.01): return all(abs(x - y) < eps for x, y in zip(a, b))


def main():
    rd = cdo("/Game/Mod/AltUI/BP_AltUIRagdoll.BP_AltUIRagdoll_C")
    names = ["root", "pelvis", "spine_01", "head"]
    local = [tf((1, 2, 3), (5, 6, 7), (1, 1, 1.5)) for _ in names]
    rd.call_method("Test Merge Rotations", args=(names, local, ["spine_01", "pelvis", "foo"], [unreal.Rotator(10, 20, 30), unreal.Rotator(40, 50, 60), unreal.Rotator(1, 1, 1)]))
    out = rd.get_editor_property("TmpLocal")
    r = lambda t: (t.rotation.rotator().roll, t.rotation.rotator().pitch, t.rotation.rotator().yaw)
    l = lambda t: (t.translation.x, t.translation.y, t.translation.z)
    expect("same length", len(out), 4)
    expect("spine_01 takes the rotation", near(r(out[2]), (10, 20, 30)), True)
    expect("spine_01 keeps translation + scale", (near(l(out[2]), (1, 2, 3)), near((out[2].scale3d.z,), (1.5,))), (True, True))
    expect("pelvis, root, head untouched", [near(r(out[i]), (5, 6, 7)) for i in (0, 1, 3)], [True, True, True])
    # component at (100,0,0) turned 90 deg; the figure faces yaw 90, saved tilt roll 90 (lying on its side)
    rd.call_method("Test Root Local", args=(tf((100, 0, 0), (0, 0, 90)), 90.0, unreal.Rotator(90, 0, 0), unreal.Vector(100, 50, 999), 20.0, unreal.Vector(1, 1, 1)))
    rl = rd.get_editor_property("TmpRootLocal")
    expect("pelvis location in component space", near(l(rl), (50, 0, 20)), True)
    expect("pelvis tilt relative to the component", near(r(rl), (90, 0, 0)), True)


run(main)
