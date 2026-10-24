"""2026-10-24 (Discord AkimboDK): load a story save with "several pieces in one slot" on -> both outfits. Restore Multi Worn and Fix
Loaded Underwear read TKAPlayer, but a story save dresses Jodi from its own Save Player Clothes (Loading State > 0: Jodi's On Begun
Play skips Load Player Save Data). storysave.Loaded Worn picks the list the level dressed her from."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, asset, MGR
import storysave as ss
from bpdsl import P_PLOTS, P_TKASAVE, P_JODI_SM, P_CB, S_ACTORSAVE


def by_id(g): return {n["id"]: n for n in g["nodes"]}


class LoadedWorn(unittest.TestCase):
    def test_story_save_first_then_chapter_end_then_tkaplayer(self):
        g = mgr_graph("Loaded Worn"); b = by_id(g)
        self.assertEqual(b["gls"]["var"], "Loading State"); self.assertEqual(b["ld"]["in"]["A"], "@gls.Loading State")
        self.assertIn(["entry", "bld", "sw", "rsw"], g["exec"]); self.assertEqual(b["sw"]["function"], "Story Worn")
        self.assertIn(["bld:else", "ble", "sle", "rle"], g["exec"]); self.assertEqual(b["gle"]["var"], "Prev Level End Save")
        self.assertEqual(b["csm"]["class"], P_JODI_SM)   # only Jodi_StoryMode starts from the chapter end state
        self.assertIn(["ble:else", "ex", "be", "ldg", "bcs", "sn", "rtp"], g["exec"]); self.assertEqual(b["ex"]["in"]["SlotName"], "TKAPlayer")
        self.assertEqual(b["rsw"]["in"]["ok"], "@sw.ok")

    def test_story_worn_reads_the_loaded_save_object(self):
        g = mgr_graph("Story Worn"); b = by_id(g)
        self.assertEqual(b["cp"]["class"], P_PLOTS); self.assertEqual(b["gsd"]["var"], "Story Mode Save Game Data")
        self.assertEqual(b["gpd"]["var"], "Player Save Data"); self.assertEqual(b["br"]["struct"], S_ACTORSAVE.split(":", 1)[1])
        self.assertIn(["entry", "clr", "biv", "sb", "ps", "rok"], g["exec"])

    def test_parse_checks_the_layout(self):
        b = by_id(mgr_graph("Parse Save Worn"))
        self.assertEqual(b["fp"]["in"]["name"], "Save Player Clothes")
        self.assertEqual(b["q1"]["in"]["B"], "ArrayProperty"); self.assertEqual(b["q2"]["in"]["B"], "NameProperty")

    def test_both_callers_use_it(self):
        for f, char in (("Fix Loaded Underwear", "@gpl0.Player"), ("Restore Multi Worn", "@gpl0.Wearer")):
            g = mgr_graph(f); lw = by_id(g)["lw"]
            self.assertEqual(lw["function"], "Loaded Worn"); self.assertEqual(lw["in"]["char"], char)
            self.assertFalse([n for n in g["nodes"] if n.get("in", {}).get("SlotName") == "TKAPlayer"], f)

    def test_stubs_and_vars(self):
        self.assertIn("Story Mode Save Game Data", [v["name"] for v in asset(P_PLOTS)["variables"]])
        self.assertEqual(asset(P_TKASAVE)["variables"][0]["type"], S_ACTORSAVE)
        names = [v["name"] for v in asset(MGR)["variables"]]
        for v in ss.variables(): self.assertIn(v["name"], names)
        chars = next(v for v in ss.variables() if v["name"] == "SaveChars")["default"]
        self.assertEqual(len(chars), 95); self.assertEqual(chars[ord("S") - 32], "S")


if __name__ == "__main__":
    unittest.main()
