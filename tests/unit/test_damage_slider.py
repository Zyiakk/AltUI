"""Clothes menu: a damage slider row (Discord: set the state of clothes). A worn piece goes through Clothes_Comp.Change Damage
(material + stored), any other piece is only stored (Store Clothes Damage) - the game puts it on when the piece is worn."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


def load(name):
    with open(os.path.join(ASSETS, name), encoding="utf-8") as f:
        return json.load(f)


class DamageSlider(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fns = {o["name"]: o for o in walk(load("50_manager_ui.json")) if isinstance(o.get("graph"), dict) and "name" in o}
        cls.row = next(o for o in walk(load("40_widgets.json")) if str(o.get("path", "")).endswith("/W_MenuSlider"))

    def test_clothes_and_backpack_menus_add_the_row_after_the_colours(self):
        for menu, after, before in (("On Item Context", "brc", "ib"), ("On Bag Item Context", "brc", "dm")):
            with self.subTest(menu=menu):
                g = self.fns[menu]["graph"]
                chain = next(c for c in g["exec"] if c and c[0] == "cc_fe:Completed")
                self.assertLess(chain.index(after), chain.index("adr")); self.assertLess(chain.index("adr"), chain.index(before))
                self.assertIn(["brc:else", "adr"], g["exec"])   # no own colour: the slider still comes
                self.assertEqual(next(n for n in g["nodes"] if n["id"] == "adr")["function"], "Add Damage Row")

    def test_row_left_out_for_a_worn_piece_without_damage_map(self):
        g = self.fns["Add Damage Row"]["graph"]; nodes = {n["id"]: n for n in g["nodes"]}
        self.assertIn(["entry", "fc", "b", "dsr_cr", "dsm", "dsi", "dsa"], g["exec"])
        self.assertEqual(nodes["ok"]["in"], {"A": "@nw.ReturnValue", "B": "@has.ReturnValue"})   # not worn OR has damage materials
        self.assertEqual(nodes["dsi"]["in"]["value"], "@idm.v")

    def test_set_item_damage_worn_and_stored(self):
        g = self.fns["Set Item Damage"]["graph"]
        self.assertIn(["entry", "bp", "fc", "bv", "cd"], g["exec"]); self.assertIn(["bv:else", "sd"], g["exec"])
        nodes = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(nodes["cd"]["function"], "Change Damage"); self.assertEqual(nodes["cd"]["in"]["save"], "true")
        self.assertEqual(nodes["sd"]["function"], "Store Clothes Damage")
        self.assertEqual(nodes["cl"]["in"], {"Value": "@entry.v", "Min": "0", "Max": "1"})

    def test_row_reports_while_dragging(self):
        fns = {f["name"]: f for f in self.row["functions"]}
        tick = fns["Tick"]["graph"]
        self.assertTrue(any(n.get("function") == "Set Item Damage" for n in tick["nodes"]))
        self.assertIn(["entry", "b", "sl", "ut", "sd"], tick["exec"])


if __name__ == "__main__":
    unittest.main()
