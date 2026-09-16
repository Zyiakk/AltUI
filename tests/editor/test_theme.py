import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def rgba(c): return (round(c.r, 3), round(c.g, 3), round(c.b, 3), round(c.a, 3))


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Reset Theme")
    mgr.call_method("Test Theme Color", args=("Accent",))
    expect("accent default", rgba(mgr.get_editor_property("TmpColor")), (0.75, 0.1, 0.1, 1.0))
    mgr.call_method("Test Theme Color", args=("Nope",))
    expect("unknown key -> black", rgba(mgr.get_editor_property("TmpColor")), (0.0, 0.0, 0.0, 0.0))
    expect("version after reset", mgr.get_editor_property("ThemeVersion") >= 1, True)
    v0 = mgr.get_editor_property("ThemeVersion")
    # derived defaults = former constants
    expect("ColBg = bg rgb + BgAlpha", rgba(mgr.get_editor_property("ColBg")), (0.02, 0.02, 0.03, 0.88))
    expect("ColFill", rgba(mgr.get_editor_property("ColFill")), (0.02, 0.02, 0.03, 0.8))
    expect("ColFrame", rgba(mgr.get_editor_property("ColFrame")), (1.0, 1.0, 1.0, 0.35))
    expect("ColFrameWorn", rgba(mgr.get_editor_property("ColFrameWorn")), (0.2, 0.8, 0.3, 0.9))
    expect("ColTextDim", rgba(mgr.get_editor_property("ColTextDim")), (0.6, 0.6, 0.6, 1.0))
    # set + round trip, derived hover lighter than base
    mgr.call_method("Test Set Theme Color", args=("Fill", unreal.LinearColor(0.1, 0.2, 0.3, 1.0)))
    mgr.call_method("Test Theme Color", args=("Fill",))
    expect("fill round trip", rgba(mgr.get_editor_property("TmpColor")), (0.1, 0.2, 0.3, 1.0))
    expect("version bumped", mgr.get_editor_property("ThemeVersion"), v0 + 1)
    base = mgr.get_editor_property("ColFill"); hov = mgr.get_editor_property("ColFillHover")
    expect("fill rgb", rgba(base), (0.1, 0.2, 0.3, 0.8))
    expect("hover lighter", hov.r > base.r and hov.g > base.g and hov.b > base.b, True)
    # opacities scale the tile alphas, not the frames
    mgr.call_method("Test Set Alphas", args=(0.5, 0.5))
    expect("bg alpha", rgba(mgr.get_editor_property("ColBg"))[3], 0.5)
    expect("tile alpha scaled", rgba(mgr.get_editor_property("ColFill"))[3], 0.4)
    expect("chip alpha scaled", rgba(mgr.get_editor_property("ColChip"))[3], 0.275)
    expect("frame alpha fixed", rgba(mgr.get_editor_property("ColFrame"))[3], 0.35)
    mgr.call_method("Test Reset Theme")
    expect("reset restores fill", rgba(mgr.get_editor_property("ColFill")), (0.02, 0.02, 0.03, 0.8))
    # layout fractions (stable indices: 1 third, 2 half, 3 quarter, 4 fifth)
    for idx, frac in ((0, 0.0), (1, 0.3333), (2, 0.5), (3, 0.25), (4, 0.2)):
        mgr.call_method("Test Layout Fraction", args=(idx,))
        expect("fraction %d" % idx, round(mgr.get_editor_property("TmpFloat"), 4), frac)
run(main)
