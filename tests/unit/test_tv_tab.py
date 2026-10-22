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
        g = function("Rebuild TopTabs"); n = nodes(g)
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

    def test_row_click_goes_to_tv_play(self):
        g = function("Select Slot"); n = nodes(g)
        self.assertEqual(n["stv"]["function"], "Tv Play")
        self.assertTrue(any("bptv" in c and "stv" in c for c in g["exec"]))


if __name__ == "__main__": unittest.main()
