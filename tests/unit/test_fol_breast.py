"""Followers / NPCs made from a look: the game's breast and waist sliders (Makeup Data Boobs Size / Waist) come along.
The figure's anim reads them through Get Boobs Size / Get Waist Adjust, which NPC_Female answers from `breasts size` / `waist adjust` -
the game rolls those in Init Npc Appearance, the follower's override rolls nothing, so they stayed at 0 (report 2026-10-31)."""
import json, os, unittest
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def graph(name):
    for f in ("30_manager.json", "50_manager_ui.json"):
        with open(os.path.join(ASSETS, f)) as fh:
            for a in json.load(fh)["assets"]:
                for e in a.get("functions", []):
                    if e.get("name") == name and e.get("graph"): return e["graph"]
    raise AssertionError(name)


def sets(g, var): return [n for n in g["nodes"] if n.get("kind") == "set" and n.get("var") == var]


class FollowerBreast(unittest.TestCase):
    def test_record_has_breast_and_waist(self):
        with open(os.path.join(ASSETS, "30_manager.json")) as fh:
            st = next(a for a in json.load(fh)["assets"] if a.get("path", "").endswith("/S_Follower"))
        names = [m["name"] for m in st.get("members", st.get("fields", []))]
        self.assertEqual(names[-2:], ["Boobs", "Waist"])   # appended: older records keep their layout

    def test_taken_from_the_look(self):
        js = json.dumps(graph("Finish Look Follower"))
        self.assertIn("Boobs Size", js); self.assertIn('"Boobs": "@gfbo.FolBoobs"', js); self.assertIn('"Waist": "@gfwa.FolWaist"', js)

    def test_set_on_the_figure(self):
        for name in ("Fol Spawn", "Finish Look Follower"):
            g = graph(name)
            self.assertTrue(sets(g, "breasts size"), name); self.assertTrue(sets(g, "waist adjust"), name)


if __name__ == "__main__":
    unittest.main()
