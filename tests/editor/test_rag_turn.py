"""Turning a ragdoll limb (figure side, no mesh needed): Turn Delta turns one direction onto another, Turn Local applies it to a
bone's world rotation and gives that relative to the parent (spec 2026-10-20-ragdoll-glied-drehen-design)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *


def tf(loc=(0, 0, 0), rot=(0, 0, 0)):
    """rot as (roll, pitch, yaw)"""
    return unreal.Transform(unreal.Vector(*loc), unreal.Rotator(*rot), unreal.Vector(1, 1, 1))


def near(a, b, eps=0.05): return all(abs(x - y) < eps for x, y in zip(a, b))


def rpy(r): return (r.roll, r.pitch, r.yaw)


def main():
    rd = cdo("/Game/Mod/AltUI/BP_AltUIRagdoll.BP_AltUIRagdoll_C")
    turn = lambda f, t, parent, rot: rd.call_method("Test Turn", args=(unreal.Vector(*f), unreal.Vector(*t), parent, unreal.Rotator(*rot)))
    get = lambda n: rpy(rd.get_editor_property(n))
    # X onto Y: 90 deg about Z; parent unturned -> local = world
    turn((1, 0, 0), (0, 1, 0), tf(), (0, 0, 0))
    expect("x onto y = yaw 90", near(get("TmpTurnDelta"), (0, 0, 90)), True)
    expect("world yaw 90", near(get("TmpTurnWorld"), (0, 0, 90)), True)
    expect("local = world under an unturned parent", near(get("TmpTurnLocal"), (0, 0, 90)), True)
    # parent turned yaw 90: the same world rotation is the identity relative to it
    turn((1, 0, 0), (0, 1, 0), tf((5, 5, 5), (0, 0, 90)), (0, 0, 0))
    expect("local relative to a turned parent", near(get("TmpTurnLocal"), (0, 0, 0)), True)
    # the delta goes on top of the bone's rotation in world space: bone pitched 30, then yaw 90 about world Z
    turn((1, 0, 0), (0, 1, 0), tf(), (0, 30, 0))
    w = rd.get_editor_property("TmpTurnWorld"); fwd = w.get_forward_vector()
    expect("pitched bone turned about world Z", near((fwd.x, fwd.y, fwd.z), (0, 0.866, 0.5), 0.01), True)
    # longer / shorter vectors: only the directions count
    turn((3, 0, 0), (0, 0, 0.5), tf(), (0, 0, 0))
    d = rd.get_editor_property("TmpTurnDelta"); f = d.get_forward_vector()
    expect("x onto z", near((f.x, f.y, f.z), (0, 0, 1), 0.01), True)
    # same / zero direction: no turn
    turn((1, 0, 0), (2, 0, 0), tf(), (0, 0, 0))
    expect("parallel = identity", near(get("TmpTurnDelta"), (0, 0, 0)), True)
    turn((1, 0, 0), (0, 0, 0), tf(), (0, 0, 0))
    expect("zero target = identity", near(get("TmpTurnDelta"), (0, 0, 0)), True)


run(main)
