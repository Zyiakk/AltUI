import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"

def near(name, v, x, y, z):
    ok = abs(v.x - x) < 0.01 and abs(v.y - y) < 0.01 and abs(v.z - z) < 0.01
    report(name, ok, "" if ok else "got (%.3f, %.3f, %.3f)" % (v.x, v.y, v.z))

def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    def d(keys, yaw, pitch=0.0):
        mgr.call_method("Test Free Cam Dir", args=(keys, yaw, pitch)); return mgr.get_editor_property("TmpVector")
    near("W yaw 0", d(1, 0.0), 1, 0, 0)
    near("S yaw 0", d(2, 0.0), -1, 0, 0)
    near("D yaw 90 -> -X", d(8, 90.0), -1, 0, 0)
    near("A yaw 90 -> +X", d(4, 90.0), 1, 0, 0)
    near("W+D yaw 0 normalised", d(9, 0.0), 0.7071, 0.7071, 0)
    near("Q down", d(16, 0.0), 0, 0, -1)
    near("E up", d(32, 0.0), 0, 0, 1)
    near("W+S cancel", d(3, 0.0), 0, 0, 0)
    near("none", d(0, 0.0), 0, 0, 0)
    near("shift bit ignored", d(64, 0.0), 0, 0, 0)
    near("W pitch 90 flies up", d(1, 0.0, 90.0), 0, 0, 1)
    near("W pitch -45 flies down", d(1, 0.0, -45.0), 0.7071, 0, -0.7071)
    near("S pitch -45 flies up-back", d(2, 0.0, -45.0), -0.7071, 0, 0.7071)
    near("D pitch 60 stays horizontal", d(8, 0.0, 60.0), 0, 1, 0)
    def c(cx, cy, cz, tx, ty, tz):
        mgr.call_method("Test Free Cam Clamp", args=(cx, cy, cz, tx, ty, tz)); return mgr.get_editor_property("TmpVector")
    near("inside unchanged", c(0, 0, 0, 100, 200, -50), 100, 200, -50)
    near("outside pulled to 600", c(0, 0, 0, 1000, 0, 0), 600, 0, 0)
    near("outside with center", c(100, 100, 100, 100, 100, 1000), 100, 100, 700)
run(main)
