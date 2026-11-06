"""Tab order (internal design notes): the default order, the saved list, the tab menu, the reset chip. The rules of
Tab Order Now and the moves run on the real Blueprints in tests/editor/test_tab_order.py."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
import gen_manager, gen_widgets, gen_manager_ui as ui
from test_options_cats import graph, after, calls


class TabOrder(unittest.TestCase):
    def test_weapons_and_hair_swapped_rest_stays(self):
        self.assertEqual(ui.TOP_TABS[:9], ["Clothes", "Outfits", "Looks", "Bag", "Inventory", "Weapons", "Poses", "Hair", "Look"])
        self.assertEqual(len(ui.TOP_TABS), len(set(ui.TOP_TABS)))

    def test_bar_runs_over_the_users_order(self):
        g = graph("50_manager_ui.json", "Rebuild TopTabs")
        self.assertEqual(len(calls(g, "Tab Order Now")), 1); self.assertEqual(len(calls(g, "Add Top Tab")), 1)
        self.assertIn("at", after(g, "fe")); self.assertIn("ton", after(g, "cb"))   # TabBar emptied first

    def test_every_tab_shown_lands_in_tab_bar(self):
        g = graph("50_manager_ui.json", "Add Top Tab")
        for i, _ in enumerate(ui.TOP_TABS): self.assertIn("tb%d" % i, after(g, "at%d" % i))

    def test_menu_rows_and_conditions(self):
        g = graph("50_manager_ui.json", "Tab Context Menu"); actions = [n["in"]["action"] for n in g["nodes"] if n.get("function") == "Init" and "action" in n["in"]]
        self.assertEqual(actions, ["TabLeft", "TabRight", "TabFirst", "TabLast", "QuickCtx", "Cancel"])
        branches = {n["id"]: n["in"]["Condition"] for n in g["nodes"] if n.get("kind") == "branch" and n["id"].startswith("cb")}
        self.assertEqual(branches, {"cb0": "@nf.ReturnValue", "cb1": "@nl.ReturnValue", "cb2": "@nf.ReturnValue", "cb3": "@nl.ReturnValue"})

    def test_menu_actions(self):
        for d in ("Left", "Right", "First", "Last"): self.assertIn(("Tab" + d, "Tab Move " + d, "ContextItem"), ui.MENU_ACTIONS)

    def test_reset_chip_reaches_select_tab_style_and_empties_the_order(self):
        g = graph("50_manager_ui.json", "Select SubTab")
        self.assertTrue(any(n.get("in", {}).get("InPrefix") == "TabOrder" for n in g["nodes"]))
        g = graph("50_manager_ui.json", "Select Tab Style"); self.assertIn("oc", after(g, "ob")); self.assertIn("sv", after(g, "oc"))

    def test_saved_with_the_settings(self):
        self.assertIn('("TabOrder", "TabOrder", "copy", None)', open(os.path.join(H, "..", "..", "assets", "gen", "gen_manager.py"), encoding="utf-8").read())


if __name__ == "__main__": unittest.main()
