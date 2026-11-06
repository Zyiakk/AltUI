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
        js = json.dumps(graph("On Inv Context")); self.assertIn("Inv:AutoToggle", js); self.assertIn("InvCtxMarked", js)

    def test_toggle_saves_the_amount(self):
        g = graph("Inv Action"); self.assertTrue(calls(g, "Map_Add")); self.assertTrue(calls(g, "Map_Remove")); self.assertTrue(calls(g, "Save Settings"))
        self.assertIn("InvCtxCount", json.dumps(g))

    def test_level_load_fills_up(self):
        self.assertTrue(calls(graph("Fol Level Start"), "Auto Items Apply"))
        g = graph("Auto Items Apply"); self.assertTrue(calls(g, "Put Item to Bag")); self.assertTrue(calls(g, "Auto Gun Give")); self.assertTrue(calls(g, "Subtract_IntInt"))

    def test_saved_setting(self):
        import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
        import gen_manager as gm
        self.assertIn(("AutoItems", "AutoItems", "copy", None), gm.SETTINGS)

    def test_story_switch(self):
        """Options > General: unticked (InvAutoNoStory, stored inverted) nothing is filled up on story levels (Plots_GameState); nothing else changes."""
        import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
        import gen_manager as gm, gen_widgets as gw, strings
        self.assertIn(("InvAutoNoStory", "InvAutoNoStory", "copy", None), gm.SETTINGS)
        rows = gw.OPT_CAT_ROWS["General"]; self.assertEqual(rows.index("RowInvAutoStory"), rows.index("RowInvAutoEquip") + 1)
        self.assertIn("Opt_InvAutoStory", strings.STRINGS)
        js = json.dumps(graph("Auto Items Apply")); self.assertIn("Plots_GameState", js); self.assertIn("InvAutoNoStory", js)

    def test_gun_comes_back_as_marked(self):
        """A marked gun comes back the way it was when it was marked: marking stores Parts + AmmoName (Init Gun with Data ignores Parts
        when AmmoName is None), carrying it never changes that, the new gun is built from them, full, and a spare part stays."""
        import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
        import gen_manager as gm
        self.assertIn(("AutoGuns", "AutoGuns", "copy", None), gm.SETTINGS)
        self.assertNotIn("AutoGuns", json.dumps(graph("Poll Weapons")))
        self.assertFalse(calls(graph("Poll Weapons"), "Auto Gun Keep"))
        g = graph("Auto Gun Give"); self.assertTrue(calls(g, "Inv Got Gun")); self.assertTrue(calls(g, "Put Item to Bag")); self.assertTrue(calls(g, "Count Items"))
        mk = [n for n in g["nodes"] if n.get("kind") == "make"]
        self.assertEqual(len(mk), 1); inp = mk[0]["in"]
        self.assertEqual(sorted(inp), ["AmmoName", "AmmoinMag", "GunName", "Parts"]); self.assertEqual(str(inp["AmmoinMag"]), "-1")

    def test_marking_stores_the_state(self):
        """Marking stores the state of the stored gun on a box tile, else of the carried gun; a gun of neither kind has none. Unmarking forgets it."""
        g = graph("Inv Action"); self.assertTrue(calls(g, "Auto Gun Mark")); self.assertIn("AutoGuns", json.dumps(g))
        self.assertEqual(sum(1 for n in g["nodes"] if n.get("function") == "Map_Remove" and "AutoGuns" in json.dumps(n)), 1)
        m = graph("Auto Gun Mark"); js = json.dumps(m)
        self.assertTrue(calls(m, "Map_Remove")); self.assertTrue(calls(m, "Map_Add")); self.assertFalse(calls(m, "Save Settings"))
        self.assertIn("InvCtxBox", js); self.assertIn("InvCtxIndex", js); self.assertTrue(calls(m, "Weapon Gun"))

    def test_carried_gun_is_set_back(self):
        """A marked gun she carries at a level load is set back to the marked state with Mount Equipment (a mounted row takes the part off,
        into the backpack); the actor, its magazine and its paint stay. Only without a stored state nothing happens."""
        g = graph("Auto Items Apply"); self.assertTrue(calls(g, "Auto Gun Give")); self.assertTrue(calls(g, "Auto Gun Fit"))
        f = graph("Auto Gun Fit"); self.assertTrue(calls(f, "Mount Equipment")); self.assertTrue(calls(f, "Array_Contains"))
        self.assertTrue(calls(f, "Apply Extra Attributes")); self.assertTrue(calls(f, "Apply Weapon Look"))
        self.assertFalse(calls(f, "Inv Got Gun")); self.assertFalse(calls(f, "Save Settings"))
        self.assertEqual(sum(1 for n in f["nodes"] if n.get("function") == "Mount Equipment"), 2)

    def test_refill_uses_nothing_existing(self):
        """Marked items act on levels whose backpack is lost afterwards: every part is made anew. Mount Equipment takes one from the backpack
        if there is one, so it goes back; the box is never touched."""
        f = graph("Auto Gun Fit"); self.assertTrue(calls(f, "Count Items")); self.assertEqual(len(calls(f, "Put Item to Bag")), 1)
        put = next(n for n in f["nodes"] if n.get("function") == "Put Item to Bag"); self.assertEqual(str(put["in"]["num"]), "1")
        on = [c for c in f["exec"] if "on" in c]; self.assertTrue(any(c.index("on") < len(c) - 1 for c in on))
        for name in ("Auto Gun Fit", "Auto Gun Give", "Auto Gun Mark", "Auto Items Apply"):
            g = graph(name)
            for bad in ("Consume Item", "Consume Item Count", "Remove a Gun", "Inv Take", "Inv Take Gun"): self.assertFalse(calls(g, bad), name + " " + bad)

    def test_stored_gun_mark_needs_its_parts(self):
        """A stored gun counts as marked only when its parts are the marked state's, in any order (ui-test-197 4.2): tile, menu and toggle
        agree. Marking one with other parts replaces the state."""
        m = graph("Auto Gun Marked"); js = json.dumps(m)
        self.assertIn("AutoItems", js); self.assertIn("AutoGuns", js); self.assertTrue(calls(m, "Array_Contains")); self.assertTrue(calls(m, "EqualEqual_IntInt"))
        self.assertTrue(calls(graph("Inv Fill"), "Auto Gun Marked")); self.assertTrue(calls(graph("Inv Set Ctx"), "Auto Gun Marked"))
        self.assertIn("InvCtxMarked", json.dumps(graph("Inv Set Ctx")))
        for name in ("Inv Action", "On Inv Context"):
            g = graph(name); self.assertIn("InvCtxMarked", json.dumps(g))
            self.assertFalse([n for n in calls(g, "Map_Contains") if "AutoItems" in json.dumps(n)], name)
        keys = [str(n["in"]["Key"]) for n in calls(graph("Inv Fill"), "Map_Contains") if "AutoItems" in json.dumps(n)]
        self.assertEqual(keys, ["@ttp.item"])

    def test_tile_mark(self):
        w = {a["path"].rsplit("/", 1)[1]: a for a in load("40_widgets.json")}["W_ClothesButton"]
        self.assertIn("Set Auto Mark", {f["name"] for f in w["functions"]}); self.assertIn("AutoMark", json.dumps(w["widget_tree"]))
        self.assertTrue(calls(graph("Inv Fill"), "Set Auto Mark") or "Set Auto Mark" in json.dumps(graph("Inv Fill Cat")))


if __name__ == "__main__":
    unittest.main()
