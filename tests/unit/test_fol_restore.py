"""Followers / enemy figures: "Restore outfit (no sewing kit)" in the gear menu, "Restore all outfits" for the Followers tab."""
import json, os, unittest
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def graph(name):
    for f in ("30_manager.json", "50_manager_ui.json"):
        with open(os.path.join(ASSETS, f)) as fh:
            for a in json.load(fh)["assets"]:
                for e in a.get("functions", []):
                    if e.get("name") == name and e.get("graph"): return e["graph"]
    raise AssertionError(name)


def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]


class Restore(unittest.TestCase):
    def test_gear_menu_row(self):
        self.assertIn("Fol:Restore", json.dumps(graph("Fol Menu")))
        self.assertTrue(calls(graph("Fol Menu Action"), "Fol Restore Outfit"))

    def test_no_sewing_kit(self):
        g = graph("Fol Restore Outfit"); js = json.dumps(g)
        self.assertTrue(calls(g, "Change Damage")); self.assertNotIn("Consume Item", js); self.assertIn("Save Clothes Damaged", js)
        self.assertIn('"Damage": "@gd0.FolDamage0"', js)   # a figure out of the world: its record's damage emptied

    def test_all_followers_not_enemies(self):
        g = graph("Fol Restore All Outfits"); self.assertTrue(calls(g, "Fol Restore Outfit")); self.assertTrue(calls(g, "NotEqual_IntInt"))
        self.assertIn("FolRestoreAll", json.dumps(graph("Rebuild Status")))


    def test_torn_off_pieces_come_back(self):
        # the game takes a torn-off piece out of the bag (Try to Destruct Clothing): the figure notes it, the record keeps it, restore gives it back
        with open(os.path.join(ASSETS, "29b_follower.json")) as fh:
            fol = {a["path"].rsplit("/", 1)[1]: a for a in json.load(fh)["assets"]}["BP_AltUIFollower"]
        ttd = next(f for f in fol["functions"] if f["name"] == "Try to Destruct Clothing"); self.assertIn("LostPieces", json.dumps(ttd))
        self.assertIn('"Lost": "@glp.LostPieces"', json.dumps(graph("Fol Sync")))
        g = graph("Fol Restore Outfit"); self.assertTrue(calls(g, "Put Item to Bag")); self.assertTrue(calls(g, "Wear The Clothes"))
        self.assertIn('"Lost": "@gl0.FolLost0"', json.dumps(g))
        # its slot (and clashing ones) free first: the figure may wear another piece there by now (play test 2026-10-30)
        self.assertTrue([n for n in g["nodes"] if n.get("function") == "Take Off Slot All"]); self.assertTrue([n for n in g["nodes"] if n.get("function") == "Conflicting Slots"])

    def test_record_keeps_every_field(self):
        # fol_put rebuilds the record from FOL_FIELDS: a field missing there is emptied by every sync (Mutation was, until 2026-10-30)
        import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
        import gen_manager_ui as ui
        with open(os.path.join(ASSETS, "30_manager.json")) as fh:
            st = next(a for a in json.load(fh)["assets"] if a.get("path", "").endswith("/S_Follower"))
        self.assertEqual(sorted(m["name"] for m in st.get("members", st.get("fields", []))), sorted(ui.FOL_FIELDS))


    def test_exactly_the_looks_outfit(self):
        # play test 2026-10-30: trousers taken away did not come back, a skirt given instead stayed on
        js = json.dumps(graph("Finish Look Follower")); self.assertIn('"Outfit": "@gfwn.FolWorn"', js)   # new figure and new look
        g = graph("Fol Restore Outfit"); js = json.dumps(g)
        self.assertIn("Outfit", js); self.assertTrue(calls(g, "Take off this clothes")); self.assertIn("Clothes in bag", js)
        self.assertTrue(calls(g, "is clothes wearing")); self.assertIn('"Worn": "@glw2.FolLostW"', js)


if __name__ == "__main__":
    unittest.main()
