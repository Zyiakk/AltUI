"""Tab order on the real Blueprints: Tab Order Now keeps the list whole, moves pass over tabs the bar does not show, the ends, the edges,
First Visible Page, TabOrder survives Save/Load Settings (internal design notes)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unreal
from edtest_lib import *
M = "/Game/Mod/AltUI"
TOP = ["Clothes", "Outfits", "Looks", "Bag", "Inventory", "Weapons", "Poses", "Hair", "Look", "Body", "Face", "Mods", "Options", "Actions", "Manage", "Ragdolls", "Enemies", "Navigation", "Objects", "Followers", "Kodex", "TV"]


def names(mgr, prop):
    return [str(n) for n in mgr.get_editor_property(prop)]


def main():
    mgr = cdo(M + "/BP_AltUIManager.BP_AltUIManager_C")
    mgr.set_editor_property("PanelOpen", False)
    def order(saved):
        mgr.set_editor_property("TabOrder", saved); mgr.call_method("Test Tab Order Now"); return names(mgr, "TabEff")
    expect("empty = default", order([]), TOP)
    full = ["Hair"] + [p for p in TOP if p != "Hair"]
    expect("own order kept", order(full), full)
    expect("unknown and double names go", order(["Hair", "Bogus", "Hair"] + [p for p in TOP if p != "Hair"]), full)
    no_poses = [p for p in ["Hair", "Weapons"] + TOP if p not in ("Poses",)]; no_poses = list(dict.fromkeys(no_poses))
    got = order(no_poses); expect("missing tab behind its predecessor", got.index("Poses"), got.index("Weapons") + 1)
    got = order([p for p in TOP if p != "Clothes"]); expect("missing first tab to the front", got[0], "Clothes"); expect("nothing lost", sorted(got), sorted(TOP))

    # moves: Looks is hidden, the bar shows Clothes, Outfits, Bag
    mgr.set_editor_property("TabBar", ["Clothes", "Outfits", "Bag"]); mgr.set_editor_property("TabOrder", [])
    mgr.call_method("Test Tab Move Step", ("Clothes", -1)); expect("left edge: nothing, order stays empty", names(mgr, "TabOrder"), [])
    mgr.call_method("Test Tab Move Step", ("Bag", 1)); expect("right edge: nothing", names(mgr, "TabOrder"), [])
    mgr.call_method("Test Tab Move Step", ("Outfits", 1)); got = names(mgr, "TabOrder")
    expect("swaps past the hidden tab", got[:4], ["Clothes", "Bag", "Looks", "Outfits"]); expect("the rest stays", got[4:], TOP[4:])
    mgr.call_method("Test Tab Move End", ("TV", False)); expect("to the start", names(mgr, "TabOrder")[0], "TV")
    mgr.call_method("Test Tab Move End", ("TV", True)); expect("to the end", names(mgr, "TabOrder")[-1], "TV")
    mgr.call_method("Test Tab Move End", ("Options", False)); expect("options can move", names(mgr, "TabOrder")[0], "Options")
    mgr.call_method("Test Tab Move End", ("Bogus", False)); expect("unknown name: nothing", "Bogus" in names(mgr, "TabOrder"), False)

    # first visible follows the order
    mgr.set_editor_property("Page", "Clothes"); mgr.set_editor_property("HiddenTabs", ["Clothes"])
    mgr.set_editor_property("TabOrder", ["Clothes", "Hair"] + [p for p in TOP if p not in ("Clothes", "Hair")])
    mgr.call_method("Test First Visible Page"); expect("first visible of the own order", str(mgr.get_editor_property("TmpName")), "Hair")

    # settings round trip
    saved = names(mgr, "TabOrder"); mgr.set_editor_property("HiddenTabs", []); mgr.call_method("Test Save Settings")
    mgr.set_editor_property("TabOrder", []); mgr.call_method("Test Load Settings"); expect("order round trip", names(mgr, "TabOrder"), saved)
    mgr.set_editor_property("TabOrder", []); mgr.call_method("Test Save Settings")   # leave a sane save behind
run(main)
