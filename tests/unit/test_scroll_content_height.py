"""2026-10-31 (Nexus report: the TV tab offered only 17 of 50 videos): a fixed height (SizeBox HeightOverride) on the content of a
scroll box keeps the box from scrolling - the rows are drawn past it (a SizeBox does not clip), the scroll box measures only the
override and clips the rest. The content of a scroll box takes its height from its rows."""
import json, os, unittest
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


class ScrollContentHeight(unittest.TestCase):
    def test_no_fixed_height_inside_a_scroll_box(self):
        bad = []
        with open(os.path.join(ASSETS, "40_widgets.json")) as fh:
            for a in json.load(fh)["assets"]:
                def walk(n):
                    if n.get("class", "").endswith("ScrollBox"):
                        bad.extend("%s %s > %s" % (a["path"].rsplit("/", 1)[1], n["name"], c["name"]) for c in n.get("children", [])
                                   if c.get("props", {}).get("bOverride_HeightOverride"))
                    for c in n.get("children", []): walk(c)
                if a.get("widget_tree"): walk(a["widget_tree"])
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
