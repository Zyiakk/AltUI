"""Ragdoll figure: the joint list (Toggle Joint, Lock All, Free All) while frozen - no constraints then, only the list."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *


def main():
    rd = cdo("/Game/Mod/AltUI/BP_AltUIRagdoll.BP_AltUIRagdoll_C")
    locked = lambda: [str(n) for n in rd.get_editor_property("LockedJoints")]
    rd.set_editor_property("Active", False); rd.set_editor_property("LockedJoints", [])
    rd.call_method("Test Toggle Joint", args=("calf_l",)); expect("one joint locked", locked(), ["calf_l"])
    rd.call_method("Test Toggle Joint", args=("calf_l",)); expect("and free again", locked(), [])
    rd.call_method("Test Toggle Joint", args=("head",))
    rd.call_method("Test Lock All", args=(["calf_l", "head", "calf_r"],)); expect("lock all adds the free ones", locked(), ["head", "calf_l", "calf_r"])
    rd.call_method("Test Free All"); expect("free all", locked(), [])
    # (Lock All also skips bones the figure's mesh lacks - not testable here: the CDO's Body is None, GetBoneIndex then answers 0)
    expect("frozen: no constraints made", len(rd.get_editor_property("Locks")), 0)
    # posing: loose joints (the CDO has no mesh, so Loose Root only sees the clicked bone itself)
    loose = lambda: [str(n) for n in rd.get_editor_property("LooseJoints")]
    rd.set_editor_property("LooseJoints", [])
    rd.call_method("Test Toggle Loose", args=("lowerarm_l",)); expect("elbow loose", loose(), ["lowerarm_l"])
    rd.call_method("Test Loose Root", args=("lowerarm_l",)); expect("loose root of the joint itself", str(rd.get_editor_property("LooseFound")), "lowerarm_l")
    rd.call_method("Test Loose Root", args=("head",)); expect("no loose joint above", str(rd.get_editor_property("LooseFound")), "None")
    rd.call_method("Test Toggle Loose", args=("lowerarm_l",)); expect("elbow fixed again", loose(), [])


run(main)
