"""A mod greys out a field (internal design notes): AltUI's own message call
Get AltUI Greyed, made from BP_AltUIManager (Test Mod Greyed), against
- the example lamp, which fills it (Brightness greyed while the light is off),
- BP_ModNoGreyed, an actor implementing BPI_AltUIMod like a mod built before the function existed (fills Get AltUI Value only),
- a PointLight, which does not implement the interface at all.
Backward compatibility: the last two must answer false = not greyed, and the value call must still arrive."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
import modui as mu
M = "/Game/Mod/AltUI"
EX = "/Game/Mod/AltUIMod_Example/BP_AltUIModExample.BP_AltUIModExample_C"


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")

    def ask(target, key):
        mgr.call_method("Test Mod Greyed", args=(target, key))
        return mgr.get_editor_property("TmpBool"), round(mgr.get_editor_property("TmpFloat"), 3)

    bpi = unreal.load_object(None, mu.INTERFACE + "." + mu.INTERFACE.rsplit("/", 1)[1])
    expect("interface asset loads", bpi is not None, True)

    old = cdo(mu.TEST_NOGREY + "." + mu.TEST_NOGREY.rsplit("/", 1)[1] + "_C")
    expect("mod without Greyed: not greyed, its value still arrives", ask(old, "Brightness"), (False, float(mu.TEST_NOGREY_VALUE)))
    expect("mod without Greyed, another key", ask(old, "Light"), (False, float(mu.TEST_NOGREY_VALUE)))

    pl = cdo("/Script/Engine.PointLight")
    expect("object without the interface: not greyed, value 0", ask(pl, "Brightness"), (False, 0.0))

    ex = cdo(EX)
    ex.set_editor_property("LightOn", False)
    expect("example, light off: Brightness greyed", ask(ex, "Brightness")[0], True)
    expect("example, light off: Light itself not greyed", ask(ex, "Light")[0], False)
    ex.set_editor_property("LightOn", True)
    expect("example, light on: Brightness not greyed", ask(ex, "Brightness")[0], False)
    expect("example, light on: value of Light", ask(ex, "Light"), (False, 1.0))


run(main)
