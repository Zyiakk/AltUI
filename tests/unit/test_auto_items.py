"""Inventory "always auto-equip" (2026-10-30): marked items are put into Jodi's backpack after each level load, made anew, up to the
amount on the tile when marked; the tile shows a loop arrow and a frame in the heading colour."""
import json, os, unittest
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def load(f):
    with open(os.path.join(ASSETS, f)) as fh: return json.load(fh)["assets"]


def graph(name):
    for f in ("30_manager.json", "50_manager_ui.json"):
        for a in load(f):
            for e in a.get("functions", []):
                if e.get("name") == name and e.get("graph"): return e["graph"]
    raise AssertionError(name)


def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]


class AutoItems(unittest.TestCase):
    def test_menu_row(self):
        js = json.dumps(graph("On Inv Context")); self.assertIn("Inv:AutoToggle", js); self.assertIn("AutoItems", js)

    def test_toggle_saves_the_amount(self):
        g = graph("Inv Action"); self.assertTrue(calls(g, "Map_Add")); self.assertTrue(calls(g, "Map_Remove")); self.assertTrue(calls(g, "Save Settings"))
        self.assertIn("InvCtxCount", json.dumps(g))

    def test_level_load_fills_up(self):
        self.assertTrue(calls(graph("Fol Level Start"), "Auto Items Apply"))
        g = graph("Auto Items Apply"); self.assertTrue(calls(g, "Put Item to Bag")); self.assertTrue(calls(g, "Inv Got Gun")); self.assertTrue(calls(g, "Subtract_IntInt"))

    def test_saved_setting(self):
        import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
        import gen_manager as gm
        self.assertIn(("AutoItems", "AutoItems", "copy", None), gm.SETTINGS)

    def test_tile_mark(self):
        w = {a["path"].rsplit("/", 1)[1]: a for a in load("40_widgets.json")}["W_ClothesButton"]
        self.assertIn("Set Auto Mark", {f["name"] for f in w["functions"]}); self.assertIn("AutoMark", json.dumps(w["widget_tree"]))
        self.assertTrue(calls(graph("Inv Fill"), "Set Auto Mark") or "Set Auto Mark" in json.dumps(graph("Inv Fill Cat")))


if __name__ == "__main__":
    unittest.main()
