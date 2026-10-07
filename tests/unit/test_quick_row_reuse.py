"""W_QuickRow is pooled by the virtual list "Qa" (Options › Quick menu): Init must set every part it can hide back to visible, or a
row that showed an item without an icon keeps its icon hidden for the next item it is given (game test 2026-10-06: icons missing
in view depending on the scroll position)."""
import unittest, os, json
from tests.unit.test_options_cats import after

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def init_graph():
    for a in json.load(open(os.path.join(ASSETS, "40_widgets.json")))["assets"]:
        if a["path"].endswith("/W_QuickRow"): return [f for f in a["functions"] if f["name"] == "Init"][0]["graph"]


def shows(g, start, widget):
    """Some node reachable from `start` sets `widget` to a visible state."""
    nodes = {n["id"]: n for n in g["nodes"]}
    return any(nodes[i].get("function") == "SetVisibility" and nodes[i]["in"]["self"].endswith("." + widget)
               and nodes[i]["in"]["InVisibility"] in ("Visible", "SelfHitTestInvisible", "HitTestInvisible") for i in after(g, start) if i in nodes)


class QuickRowReuse(unittest.TestCase):
    def test_icon_shown_again(self):
        self.assertTrue(shows(init_graph(), "bi", "IconBox"))

    def test_check_box_shown_again(self):
        self.assertTrue(shows(init_graph(), "bc", "CheckBox"))


if __name__ == "__main__": unittest.main()
