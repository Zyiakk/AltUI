"""2026-10-17: Body Shape chips (many body mods) in a scroll box as tall as the group chip area option."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import asset
import gen_widgets as gw


class BodyChipsScroll(unittest.TestCase):
    """2026-10-17: Body Shape chips (many body mods) in a scroll box as tall as the group chip area option."""
    def test_box_and_option(self):
        a = asset(gw.W_PANEL); sth = next(f["graph"] for f in a["functions"] if f["name"] == "Set SubTabs Height")
        self.assertTrue(any(n.get("in", {}).get("self") == "@gbb.BodyChipsBox" for n in sth["nodes"]))
        self.assertIn("BodyChipsScroll", gw.SCROLL_PAGES)
        def find(n, name): return n if n.get("name") == name else next((r for c in n.get("children", []) for r in [find(c, name)] if r), None)
        box = find(a["widget_tree"], "BodyChipsBox"); self.assertEqual(box["children"][0]["name"], "BodyChipsScroll")
        self.assertEqual(box["children"][0]["children"][0]["name"], "BodyChips")


class BodySliderScroll(unittest.TestCase):
    """2026-10-31 (ui-test-183): the preset bar pushed the last sliders under the status bar - the slider rows scroll in a box that
    fills the rest of the page; body chips and presets stay above it."""
    def test_rows_scroll(self):
        def find(n, name): return n if n.get("name") == name else next((r for c in n.get("children", []) for r in [find(c, name)] if r), None)
        body = find(asset(gw.W_PANEL)["widget_tree"], "BodyBox")
        kids = [c["name"] for c in body["children"]]
        self.assertEqual(kids, ["BodyChipsBox", "BodyPresetBar", "BodyPresetBox", "BodySliderScroll"])
        sc = body["children"][3]; self.assertIn("SizeRule=Fill", sc["slot"].get("Size", ""))
        for row in ["Row" + k for k, _ in gw.BODY_ROWS + gw.SCALE_ROWS] + ["LblScaleHint"]: self.assertTrue(find(sc, row), row)
        self.assertIn("BodySliderScroll", gw.SCROLL_PAGES)


if __name__ == "__main__": unittest.main()
