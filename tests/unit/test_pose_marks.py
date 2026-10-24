"""2026-10-24: a pose click only updates the marking of the tiles that are there - Pose Clicked / Stop Pose rebuilt the whole
poses list twice per click (new tiles + tooltips each time) and quick pose changes ran the game out of memory."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, fn_graph


def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]


class PoseMarks(unittest.TestCase):
    def test_click_and_stop_do_not_rebuild(self):
        for name in ("Pose Clicked", "Stop Pose", "Pose Loop Tick", "Scan Tick"):
            g = mgr_graph(name); self.assertFalse(calls(g, "Rebuild Poses"), name)
        for name in ("Pose Clicked", "Stop Pose"):
            self.assertTrue(calls(mgr_graph(name), "Refresh Pose Marks"), name)

    def test_rebuild_keeps_the_tiles(self):
        g = mgr_graph("Rebuild Poses")
        self.assertTrue(any(n.get("function") == "Array_Clear" and "PoseTiles" in str(n.get("in")) for n in g["nodes"]))
        self.assertEqual(sum(1 for n in calls(g, "Array_Add") if "PoseTiles" in str(n.get("in"))), 3)   # favourites, default, all
        self.assertIn("cpt", next(c for c in g["exec"] if c[0] == "entry"))

    def test_refresh_sets_worn_on_each_tile(self):
        g = mgr_graph("Refresh Pose Marks"); self.assertTrue(calls(g, "Set Worn")); self.assertFalse(calls(g, "Create"))
        b = fn_graph("/Game/Mod/AltUI/W_ClothesButton", "Set Worn")
        self.assertEqual([n["function"] for n in b["nodes"] if n.get("function") in ("Compute Colors", "Apply Colors")], ["Compute Colors", "Apply Colors"])

    def test_second_click_only_stops(self):
        """ui-test-158: stop branch and play branch shared one Stop Pose node, so the stop branch went on to play the pose again."""
        g = mgr_graph("Pose Clicked"); ex = g["exec"]
        stops = [n["id"] for n in calls(g, "Stop Pose")]; self.assertEqual(len(stops), 2)
        play = next(n["id"] for n in calls(g, "Change Next Action Animation"))
        nxt = {}
        for c in ex:
            for a, b in zip(c, c[1:]): nxt.setdefault(a, set()).add(b)
        def reach(a, seen=None):
            seen = seen or set()
            for b in nxt.get(a, ()):
                if b not in seen: seen.add(b); reach(b, seen)
            return seen
        self.assertEqual(sum(play in reach(s) for s in stops), 1)


if __name__ == "__main__":
    unittest.main()
