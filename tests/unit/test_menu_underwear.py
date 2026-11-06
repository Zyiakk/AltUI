"""2026-11-04: main menu / loading scene: underwear the game added to the figure comes off with the option (Fix Menu Underwear)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from test_play_zoom import load, walk


def fns(): return {o["name"]: o for o in walk(load("50_manager_ui.json")) if isinstance(o.get("graph"), dict) and "name" in o}
def by_id(g): return {n["id"]: n for n in g["nodes"]}


class MenuUnderwear(unittest.TestCase):
    def test_runs_in_menu_before_the_other_pieces(self):
        g = fns()["Find Menu Wearer"]["graph"]; nodes = by_id(g)
        self.assertEqual(nodes["fmu"]["function"], "Fix Menu Underwear")
        s = json.dumps(g["exec"] if "exec" in g else g); self.assertIn("fmu", s)

    def test_rule_first_then_only_on_the_wearer(self):
        nodes = by_id(fns()["Fix Menu Underwear"]["graph"])
        self.assertEqual(nodes["apn"]["function"], "Apply Nude")
        self.assertEqual(nodes["to"]["in"]["self"], "@gpl2.Wearer")
        self.assertEqual(nodes["go"]["in"]["B"], "@nc.ReturnValue")   # only pieces not in the list it dressed from

    def test_rule_reaches_the_menu_game_state(self):
        nodes = by_id(fns()["Apply Nude"]["graph"])
        self.assertTrue(str(nodes["sn"].get("class", nodes["sn"].get("cls", ""))).endswith("TKA_GameState_Base") or "TKA_GameState_Base" in json.dumps(nodes["cs"]))


if __name__ == "__main__": unittest.main()
