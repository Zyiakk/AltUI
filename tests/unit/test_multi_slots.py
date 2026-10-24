"""2026-10-18: several pieces in one slot (Options > Slot conflicts, MultiSlots) - for Jodi, looks, followers; the game's slot
exclusivity is dodged by hiding the slot's worn comps (Clothes_Comp.Type) for the one Wear The Clothes call."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, fn_graph, asset, MGR
import multislot as ms

FOL = "/Game/Mod/AltUI/BP_AltUIFollower"


def by_id(g): return {n["id"]: n for n in g["nodes"]}
def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]
def sets(g, var): return [n for n in g["nodes"] if n.get("kind") == "set" and n.get("var") == var]


def chain_order(g, *ids):
    """Every id appears in one exec chain, in this order."""
    for c in g["exec"]:
        if all(i in c for i in ids): return [c.index(i) for i in ids] == sorted(c.index(i) for i in ids)
    return False


class WearKept(unittest.TestCase):
    def test_hold_wear_release(self):
        g = mgr_graph("Wear Kept"); b = by_id(g)
        self.assertEqual(b["hs"]["function"], "Hold Slot"); self.assertEqual(b["rh"]["function"], "Release Held")
        self.assertEqual(b["w"]["function"], "Wear The Clothes"); self.assertEqual(b["w"]["in"]["self"], "@entry.char")
        self.assertTrue(chain_order(g, "hs", "w", "rh"))
        self.assertIn(["bk:else", "csf", "w"], g["exec"])   # keep = false: the slot holds one again first

    def test_not_kept_clears_the_slot(self):
        """ui-test-118 #3: two shoes from a kept slot, slot switched off, a third shoe on - the game took off only the first."""
        g = mgr_graph("Clear Slot For"); b = by_id(g)
        self.assertEqual(b["tsa"]["function"], "Take Off Slot All"); self.assertEqual(b["tsa"]["in"]["slot"], "@br.TypeName")
        self.assertEqual(b["fa"]["in"]["A"], "@tbr.Flag")   # Acc keeps its pieces
        self.assertEqual(b["one"]["in"]["B"], "@nw.ReturnValue")   # a piece worn already takes nothing off
        self.assertIn(["entry", "row", "trow", "bone", "tsa"], g["exec"])

    def test_hold_hides_the_slot(self):
        g = mgr_graph("Hold Slot")
        sh = sets(g, "Type"); self.assertEqual(len(sh), 1); self.assertEqual(sh[0]["in"]["Type"], ms.HELD_TYPE)
        self.assertEqual(by_id(g)["gty"]["var"], "Type")
        r = sets(mgr_graph("Release Held"), "Type"); self.assertEqual(r[0]["in"]["Type"], "@ght.HeldType")

    def test_take_off_slot_all_works_on_a_copy(self):
        g = mgr_graph("Take Off Slot All"); b = by_id(g)
        self.assertEqual(b["fc"]["in"]["Array"], "@gh.HeldComps"); self.assertTrue(calls(g, "Take Off Clothes And Remove Component"))


class Jodi(unittest.TestCase):
    def test_wear_keeps_in_multi_slots(self):
        g = mgr_graph("Wear"); b = by_id(g)
        self.assertEqual(b["w2"]["function"], "Wear Kept"); self.assertEqual(b["w2"]["in"]["keep"], "@kis.keep")
        self.assertEqual(b["tc_to"]["function"], "Take Off Slot All")   # a conflicting slot with two pieces: both off
        k = mgr_graph("Keep In Slot"); self.assertEqual(by_id(k)["gms"]["var"], "MultiSlots")

    def test_look_queue_keeps(self):
        b = by_id(mgr_graph("Wear Queue Step"))
        self.assertEqual(b["we2"]["function"], "Wear Kept"); self.assertEqual(b["we2"]["in"]["keep"], "@kis.keep")
        self.assertEqual(b["tc_to"]["function"], "Take Off Slot All")

    def test_load_puts_the_others_on_again(self):
        g = mgr_graph("Restore Multi Worn"); b = by_id(g)
        self.assertEqual(b["wk"]["function"], "Wear Kept"); self.assertEqual(b["wk"]["in"]["keep"], "true")
        self.assertEqual(b["lw"]["function"], "Loaded Worn"); self.assertEqual(b["lw"]["in"]["char"], "@gpl0.Wearer")   # 2026-10-24: not TKAPlayer
        self.assertIn(["entry", "b", "lw", "bcs", "fw"], g["exec"]); self.assertEqual(b["bcs"]["in"]["Condition"], "@lw.ok")
        self.assertEqual(b["wk"]["in"]["char"], "@gpl3.Wearer")
        self.assertEqual(b["kis"]["in"]["ItemToFind"], "@br.TypeName")   # the menu has no catalog

    def test_menu_and_loading_scene_too(self):
        g = mgr_graph("Find Menu Wearer"); self.assertIn("rmw", next(c for c in g["exec"] if "asb" in c))

    def test_setting_is_saved(self):
        sg = asset("/Game/Mod/AltUI/SG_AltUI"); self.assertIn("MultiSlots", [v["name"] for v in sg["variables"]])
        self.assertIn("MultiSlots", [v["name"] for v in asset(MGR)["variables"]])


class Followers(unittest.TestCase):
    def test_relook_and_give_keep(self):
        r = by_id(mgr_graph("Finish Look Follower"))["rww"]; self.assertEqual(r["function"], "Wear Kept"); self.assertEqual(r["in"]["keep"], "@rkis.keep")
        g = mgr_graph("Fol Clothes Give")
        self.assertTrue(chain_order(g, "hsg", "pt", "rhg")); self.assertIn(["bkis:else", "csfg", "pt"], g["exec"])

    def test_figure_start_puts_the_look_on_again(self):
        g = fn_graph(FOL, "Check Appearence"); b = by_id(g)
        self.assertEqual(b["fw"]["in"]["Array"], "@glw.LookWorn"); self.assertEqual(b["wk"]["in"]["keep"], "true")
        self.assertIn(["fw:Completed", "cc", "bm"], g["exec"])
        self.assertTrue(sets(fn_graph(FOL, "Set Look"), "LookWorn"))
        self.assertIn("Wear Kept", [f["name"] for f in asset(FOL)["functions"]])


class Options(unittest.TestCase):
    def test_chips_skip_the_games_own_multi_slots(self):
        g = mgr_graph("Rebuild Multi Slots"); b = by_id(g)
        self.assertEqual(b["fa"]["in"]["A"], "@br.Flag"); self.assertEqual(b["cci"]["in"]["group"], "@kn.ReturnValue")
        self.assertTrue(calls(mgr_graph("Rebuild Conflicts"), "Rebuild Multi Slots"))

    def test_toggle_saves(self):
        g = mgr_graph("Toggle Multi Slot"); self.assertTrue(calls(g, "Save Settings")); self.assertTrue(calls(g, "Rebuild Multi Slots"))


if __name__ == "__main__":
    unittest.main()
