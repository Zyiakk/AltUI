"""A paint the game put on (spray can -> Change Gun Paint -> Gun Data.PaintName) must survive opening the panel: Apply Weapon
Look first runs Sync Weapon Paint, which takes the game's paint over when it differs from what AltUI left on the weapon."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.call_method("Test Load Settings")
    keep_skins, keep_applied = dict(mgr.get_editor_property("WeaponSkins")), dict(mgr.get_editor_property("AppliedPaint"))
    def state(w):
        sk = {str(k): str(v) for k, v in mgr.get_editor_property("WeaponSkins").items()}
        ap = {str(k): str(v) for k, v in mgr.get_editor_property("AppliedPaint").items()}
        return sk.get(w), ap.get(w)
    def setup(skins, applied):
        mgr.set_editor_property("WeaponSkins", skins); mgr.set_editor_property("AppliedPaint", applied)
    sync = lambda w, p: mgr.call_method("Test Sync Weapon Paint", args=(w, p))

    setup({}, {}); sync("UMP", "GunPaint_Red")
    expect("no choice, nothing known: game paint taken over", state("UMP"), ("GunPaint_Red", "GunPaint_Red"))
    setup({}, {}); sync("UMP", "None")
    expect("unpainted, no choice: stays original", state("UMP"), (None, "None"))
    setup({"UMP": "GunPaint_Blue"}, {}); sync("UMP", "GunPaint_Red")
    expect("own choice, nothing known yet: own choice stays", state("UMP"), ("GunPaint_Blue", "GunPaint_Blue"))
    setup({"UMP": "GunPaint_Blue"}, {"UMP": "GunPaint_Blue"}); sync("UMP", "GunPaint_Blue")
    expect("unchanged: own choice stays", state("UMP"), ("GunPaint_Blue", "GunPaint_Blue"))
    setup({"UMP": "GunPaint_Blue"}, {"UMP": "GunPaint_Blue"}); sync("UMP", "GunPaint_Red")
    expect("sprayed over AltUI's paint: spray wins", state("UMP"), ("GunPaint_Red", "GunPaint_Red"))
    setup({}, {"UMP": "None"}); sync("UMP", "GunPaint_Red")
    expect("sprayed an original weapon: spray wins", state("UMP"), ("GunPaint_Red", "GunPaint_Red"))
    setup({"UMP": "GunPaint_Blue"}, {"UMP": "GunPaint_Blue"}); sync("UMP", "None")
    expect("paint removed in the game: original", state("UMP"), (None, "None"))
    setup({"UMP": "GunPaint_Blue"}, {"UMP": "GunPaint_Blue"}); sync("Glock", "GunPaint_Red")
    expect("other weapons untouched", state("UMP"), ("GunPaint_Blue", "GunPaint_Blue"))
    setup(keep_skins, keep_applied); mgr.call_method("Test Save Settings")   # Sync saved the test entries


run(main)
