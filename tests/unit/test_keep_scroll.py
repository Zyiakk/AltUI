"""2026-10-17: rebuilding a page keeps its scroll position (lists jumped to the top: a pose ending, a button picture chosen, an
outfit clicked); a real page change still starts at the top."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, asset
import gen_widgets as gw

KEEP = ["Select Page", "Rebuild Options", "Rebuild Poses", "Rebuild Outfits", "Rebuild Looks", "Rebuild Inventory", "Rebuild Image Chips"]


def by_id(g): return {n["id"]: n for n in g["nodes"]}


class KeepScroll(unittest.TestCase):
    def test_wrappers_remember_run_restore(self):
        for name in KEEP:
            g = mgr_graph(name, wrapper=True); b = by_id(g)
            self.assertIn(["entry", "b", "rm", "in", "rs", "tm"], g["exec"], name); self.assertEqual(b["in"]["function"], name + " Body")
            self.assertIn(["b:else", "in2"], g["exec"], name); self.assertEqual(b["tm"]["in"]["FunctionName"], "Restore Scrolls Later")

    def test_select_page_only_on_the_same_page(self):
        b = by_id(mgr_graph("Select Page", wrapper=True)); self.assertEqual(b["same"]["in"]["B"], "@entry.name"); self.assertEqual(b["b"]["in"]["Condition"], "@both.ReturnValue")

    def test_panel_covers_every_page_scroll(self):
        fs = {f["name"]: f["graph"] for f in asset(gw.W_PANEL)["functions"]}
        for name, fn_ in (("Remember Scrolls", "GetScrollOffset"), ("Restore Scrolls", "SetScrollOffset")):
            n = sum(1 for x in fs[name]["nodes"] if x.get("function") == fn_); self.assertEqual(n, len(gw.SCROLL_PAGES), name)
        self.assertIn("BodyChipsScroll", gw.SCROLL_PAGES)

    def test_option_cat_to_top_only_on_change_and_forgets(self):
        g = next(f["graph"] for f in asset(gw.W_PANEL)["functions"] if f["name"] == "Set Option Cat")
        self.assertTrue(any(c[-4:] == ["bchg", "ssc", "csm", "sts"] for c in g["exec"]))
        k = next(f["graph"] for f in asset(gw.W_PANEL)["functions"] if f["name"] == "Kodex Scroll Top"); self.assertIn(["entry", "csm", "s"], k["exec"])


if __name__ == "__main__": unittest.main()
