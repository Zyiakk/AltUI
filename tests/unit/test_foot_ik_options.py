"""2026-11-09: Options > Movement "Feet follow the ground" / "Knees and hands follow the ground" (FootIKOn / FootContactOn -> BP_AltUIFootIK)."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
import gen_manager, gen_manager_ui, gen_widgets as gw
from gen_footik import FOOTIK
from strings import STRINGS, LANGS
from strings_fr import FR
from test_play_zoom import load, walk, exec_has

OPTS = (("FootIKOn", "footik", "FootIK"), ("FootContactOn", "footcontact", "FootContact"))   # manager variable, panel pin, widget suffix


def fns(name="50_manager_ui.json"): return {o["name"]: o for o in walk(load(name)) if isinstance(o.get("graph"), dict) and "name" in o}
def by_id(g): return {n["id"]: n for n in g["nodes"]}


def event_graph():
    for o in walk(load("50_manager_ui.json")):
        if isinstance(o.get("nodes"), list) and any(n.get("kind") == "event" and n.get("name") == "ReceiveBeginPlay" for n in o["nodes"]): return o
    raise AssertionError("no BeginPlay graph")


class Option(unittest.TestCase):
    def test_saved_default_off(self):
        rows = {m: (k, d) for m, _, k, d in gen_manager.SETTINGS}
        mgr = next(o for o in walk(load("30_manager.json")) if str(o.get("path", "")).endswith("/BP_AltUIManager") and o.get("variables"))
        for v, _, _ in OPTS:
            self.assertEqual(rows[v][0], "copy", v)
            mv = next(x for x in mgr["variables"] if x["name"] == v)
            self.assertIn(mv.get("default", "false"), ("false", None, ""), v)

    def test_rows_after_office_jump(self):
        rows = gw.OPT_CAT_ROWS["Move"]; i = rows.index("RowOfficeJump")
        self.assertEqual(rows[i + 1:i + 4], ["RowFootIK", "RowFootContact", "HintFootIK"])

    def test_strings(self):
        for k in ("Lbl_FootIK", "Lbl_FootContact", "Hint_FootIK"):
            self.assertEqual(len(STRINGS[k]), len(LANGS), k); self.assertTrue(all(STRINGS[k]), k); self.assertTrue(FR.get(k), k)
        self.assertEqual(STRINGS["Lbl_FootIK"][0], "Feet follow the ground")
        for pin, widget, key in (("footik", "LblFootIK", "Lbl_FootIK"), ("footcontact", "LblFootContact", "Lbl_FootContact"), ("footikhint", "HintFootIK", "Hint_FootIK")):
            self.assertIn((pin, widget), gw.PANEL_TEXTS); self.assertIn((pin, key), gen_manager_ui.PANEL_STRINGS)
        self.assertIn("LblFootIK", gw.PANEL_TEXT_COLORS["ColText"]); self.assertIn("LblFootContact", gw.PANEL_TEXT_COLORS["ColText"])
        self.assertIn("HintFootIK", gw.PANEL_TEXT_COLORS["ColTextDim"])

    def test_checks_round_trip(self):
        w = fns("40_widgets.json"); ui = fns()
        su = ui["Rebuild Options Body"]["graph"]["nodes"]
        for v, pin, _ in OPTS:
            self.assertTrue(any(n.get("in", {}).get("InIsChecked") == "@entry." + pin for n in w["Set Option Checks"]["graph"]["nodes"]), pin)
            self.assertIn(pin, [p["name"] for p in w["Get Option Values"]["outputs"]])
            self.assertTrue(any(n.get("function") == "Set Option Checks" and str(n.get("in", {}).get(pin, "")).endswith("." + v) for n in su), pin)


class Apply(unittest.TestCase):
    def test_change_sets_applies_and_saves(self):
        g = fns()["Poll Options"]["graph"]; nodes = by_id(g)
        for v, pin, _ in OPTS:
            s = next(i for i, n in nodes.items() if n.get("kind") == "set" and n.get("var") == v and n["in"].get(v) == "@gv." + pin)
            a = next(i for i, n in nodes.items() if n.get("function") == "Apply Foot IK" and any(s in ch and i in ch and ch.index(i) == ch.index(s) + 1 for ch in g["exec"]))
            self.assertTrue(any(a in ch and ch.index(a) + 1 < len(ch) and nodes[ch[ch.index(a) + 1]].get("function") == "Save Settings" for ch in g["exec"]), v)

    def test_apply_wakes_the_driver(self):
        g = fns()["Apply Foot IK"]["graph"]; nodes = by_id(g)
        wake = next(n for n in nodes.values() if n.get("function") == "Wake")
        self.assertEqual(wake.get("class"), FOOTIK)
        self.assertEqual(nodes[wake["in"]["self"][1:].split(".")[0]].get("var"), "FootIK")

    def test_begin_play_spawns_and_wires_the_driver(self):
        g = event_graph(); nodes = by_id(g)
        sp = next(i for i, n in nodes.items() if n.get("kind") == "spawn" and n.get("class") == FOOTIK)
        sv = next(i for i, n in nodes.items() if n.get("kind") == "set" and n.get("var") == "FootIK" and n["in"].get("FootIK") == "@%s.ReturnValue" % sp)
        sm = next(i for i, n in nodes.items() if n.get("kind") == "set" and n.get("var") == "Manager" and n["in"].get("self") == "@%s.ReturnValue" % sp)
        self.assertEqual(nodes[nodes[sm]["in"]["Manager"][1:].split(".")[0]].get("kind"), "self")
        ap = next(i for i, n in nodes.items() if n.get("function") == "Apply Foot IK")
        self.assertTrue(exec_has(g, "ahd", sp, sv, sm, ap))   # Manager set before the first Apply (the driver reads it every tick)


if __name__ == "__main__": unittest.main()
