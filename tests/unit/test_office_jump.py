"""2026-11-04: Options > Movement "Jumping in the office" (OfficeJump -> JodiOffice_GameState.Allow Player Climbing And Jumping)."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
import gen_manager, gen_widgets as gw
from bpdsl import P_OFFICE, P_GS2
from strings import STRINGS, LANGS
from test_play_zoom import load, walk

RULE = "Allow Player Climbing And Jumping"


def fns(name="50_manager_ui.json"): return {o["name"]: o for o in walk(load(name)) if isinstance(o.get("graph"), dict) and "name" in o}
def by_id(g): return {n["id"]: n for n in g["nodes"]}


class Option(unittest.TestCase):
    def test_saved_default_off(self):
        rows = {m: (k, d) for m, _, k, d in gen_manager.SETTINGS}
        self.assertEqual(rows["OfficeJump"][0], "copy")
        mgr = next(o for o in walk(load("30_manager.json")) if str(o.get("path", "")).endswith("/BP_AltUIManager") and o.get("variables"))
        v = next(v for v in mgr["variables"] if v["name"] == "OfficeJump")
        self.assertIn(v.get("default", "false"), ("false", None, ""))

    def test_row_in_movement(self):
        self.assertIn("RowOfficeJump", gw.OPT_CAT_ROWS["Move"])

    def test_strings(self):
        self.assertEqual(len(STRINGS["Lbl_OfficeJump"]), len(LANGS))
        self.assertTrue(all(STRINGS["Lbl_OfficeJump"]))

    def test_checks_round_trip(self):
        w = fns("40_widgets.json")
        self.assertTrue(any(n.get("in", {}).get("InIsChecked") == "@entry.officejump" for n in w["Set Option Checks"]["graph"]["nodes"]))
        self.assertIn("officejump", [p["name"] for p in w["Get Option Values"]["outputs"]])


class Apply(unittest.TestCase):
    def test_only_the_office_state_gets_the_rule(self):
        nodes = by_id(fns()["Apply Office Jump"]["graph"])
        self.assertTrue(nodes["co"].get("cls", nodes["co"].get("class", "")).endswith("JodiOffice_GameState") or P_OFFICE in str(nodes["co"]))
        self.assertEqual(nodes["sa"]["in"][RULE], "@gj.OfficeJump")
        self.assertEqual(nodes["sa"]["in"]["self"], "@co.AsJodiOffice_GameState")

    def test_begin_play_and_option_change_apply(self):
        fs = fns()
        hits = [n for f, o in fs.items() for n in o["graph"]["nodes"] if n.get("function") == "Apply Office Jump"]
        self.assertEqual(len(hits), 1)   # the option change; Begin Play sits in the event graph
        self.assertIn('"function": "Apply Office Jump"', open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json"), encoding="utf-8").read())


if __name__ == "__main__": unittest.main()
