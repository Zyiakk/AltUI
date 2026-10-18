"""2026-10-18: Body Shape keeps "Reset shape" bottom right in the status bar, not as a link below the sliders."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from test_fol_tab import mgr_graph


def by_id(g): return {n["id"]: n for n in g["nodes"]}
def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]


class BodyResetInStatus(unittest.TestCase):
    def test_status_bar_on_the_body_page(self):
        g = mgr_graph("Rebuild Status"); b = by_id(g)
        self.assertEqual(b["isbd"]["in"]["B"], "Body")
        self.assertEqual(b["bsi"]["in"]["action"], "BodyScReset"); self.assertEqual(b["abs"]["function"], "Add Status Right")
        chain = next(c for c in g["exec"] if "bbd" in c); i = chain.index("bbd")
        self.assertEqual(chain[i:i + 6], ["bbd", "bsr_cr", "smbs", "bsi", "abs", "bth"])
        self.assertIn(["bbd:else", "bth"], g["exec"])

    def test_no_link_below_the_sliders(self):
        g = mgr_graph("Rebuild Body")
        self.assertFalse(calls(g, "Add Body Link")); self.assertFalse(calls(g, "Clear Body Links"))


if __name__ == "__main__":
    unittest.main()
