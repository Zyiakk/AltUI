"""TV tab: the office TV's videos (TV_Actor), nearest TV to Jodi, play on click, switch on / off.

The TV reads its file list (<game>/Videos/TV/*.mp4, McoreFunctionLibrary.GetFileList - native, out of AltUI's reach) only on its
first On Use This; so switching on goes through On Use This, and a video chosen while it is off becomes `current video index`
first - the switch-on animation ends with Play Video(current)."""
import unittest
from test_weapon_look_melee import function
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
import gen_manager_ui as ui


def nodes(g): return {x["id"]: x for x in g["nodes"]}


class TvTab(unittest.TestCase):
    def test_last_tab(self):
        self.assertEqual(ui.TOP_TABS[-1], "TV")

    def test_tab_only_with_a_tv_or_the_option(self):
        g = function("Add Top Tab"); n = nodes(g)
        self.assertEqual(n["tvo"]["in"], {"A": "@tvv.ReturnValue", "B": "@gtal.TvAlways"})
        self.assertEqual(n["ftv"]["function"], "Find TV")
        i = ui.TOP_TABS.index("TV")
        self.assertTrue(any(c[:3] == ["bs%d" % i, "ftv", "btv"] for c in g["exec"]))   # switched off -> no Find TV, no tab

    def test_nearest_tv(self):
        n = nodes(function("Find TV"))
        self.assertEqual(n["lt"]["in"], {"A": "@dst.ReturnValue", "B": "@gd.TvDist"})
        self.assertEqual(n["s1"]["in"]["TvActor"], "@ct.AsTV Actor")

    def test_play_on_or_switch_on_with_that_video(self):
        g = function("Tv Play"); n = nodes(g)
        self.assertIn(["entry", "ftv", "bv", "bw", "pv", "rb"], g["exec"])
        self.assertIn(["bw:else", "sci", "on"], g["exec"])
        self.assertEqual(n["sci"]["var"], "current video index")
        self.assertEqual(n["on"]["function"], "Tv On")

    def test_on_and_off_check_the_tv_first(self):
        on = function("Tv On"); off = function("Tv Off")
        self.assertIn(["entry", "ftv", "bv", "bw"], on["exec"]); self.assertIn(["bw:else", "use", "rb"], on["exec"])
        self.assertEqual(nodes(on)["use"]["function"], "On Use This")
        self.assertIn(["entry", "ftv", "bv", "bw", "sa", "te", "rb"], off["exec"])
        self.assertEqual(nodes(off)["sa"]["in"]["working"], "false")

    def test_rows_like_navigation(self):
        # 2026-10-31: rows as in the Navigation tab (W_NavRow: compact, striped, playing one in the heading colour, link at the right
        # edge) instead of slot tabs; the link "TvPlay:<i>" plays video i
        g = function("Rebuild Tv"); n = nodes(g)
        self.assertEqual(n["rw"]["class"], ui.W_NAVROW)
        self.assertEqual(n["ri"]["in"]["header"], "@rsel.ReturnValue")
        self.assertTrue(any(x.get("function") == "Set Stripe" for x in g["nodes"]))
        self.assertEqual(n["aic"]["in"]["A"], "TvPlay:")
        m = function("On Menu Action"); mn = nodes(m)
        self.assertEqual(mn["tvp"]["in"]["InPrefix"], "TvPlay:"); self.assertEqual(mn["tvpt"]["function"], "Tv Play")
        self.assertFalse("stv" in nodes(function("Select Slot")), "rows are no slot tabs any more")

    def test_highlight_follows_the_tv(self):
        # 2026-10-31: the TV plays the next video by itself when one ends - the highlight and the state line follow it (Poll Tv on the TV
        # page: index changed -> Tv Status + Set Header per row, no rebuild, the list keeps its scroll position; on / off changed -> Rebuild Tv)
        import json
        mgr = [a for a in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "50_manager_ui.json")))["assets"] if a.get("event_graph")]
        self.assertTrue(any('"Poll Tv"' in json.dumps(a["event_graph"]) for a in mgr))
        g = function("Poll Tv"); n = nodes(g); js = str(g)
        self.assertIn("current video index", js); self.assertIn("TvShownIdx", js); self.assertIn("TvShownOn", js)
        self.assertTrue(any(x.get("function") == "Set Header" for x in g["nodes"]))
        self.assertTrue(any(x.get("function") == "Tv Status" for x in g["nodes"])); self.assertTrue(any(x.get("function") == "Rebuild Tv" for x in g["nodes"]))
        r = function("Rebuild Tv"); self.assertIn("TvRows", str(r)); self.assertTrue(any(x.get("function") == "Tv Status" for x in r["nodes"]))


if __name__ == "__main__": unittest.main()
