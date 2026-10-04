"""Camera follows slot / face: every focus sets FocusHeight to the slot's height (clamped to the camera height band); while a slot is
focused the camera aims at FocusHeight and a drag moves it, otherwise at the saved CamHeight. Both live in the same fixed band
HEIGHT_MIN..HEIGHT_MAX around Jodi - the reachable range does not move with the slot (game test 2026-10-03)."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, os.path.join(H, "..", ".."))
from tests.unit.test_options_cats import graph, after
import gen_manager_ui as ui


class FocusHeight(unittest.TestCase):
    def test_focus_sets_the_slot_height_clamped(self):
        g = graph("50_manager_ui.json", "Update Focus"); nodes = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(nodes["sfb"]["var"], "FocusHeight"); self.assertEqual(nodes["bfb"]["in"]["Condition"], "@a2.ReturnValue")
        self.assertEqual(nodes["sfb"]["in"]["FocusHeight"], "@fzc.ReturnValue")
        self.assertEqual((float(nodes["fzc"]["in"]["Min"]), float(nodes["fzc"]["in"]["Max"])), (ui.HEIGHT_MIN, ui.HEIGHT_MAX))
        self.assertIn("sfb", after(g, "bfb")); self.assertNotIn("sfb", after(g, "bfb:else"))

    def test_target_is_focus_height_or_camera_height(self):
        g = graph("50_manager_ui.json", "Set View Shift"); nodes = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(nodes["hrel"]["in"], {"A": "@gfh.FocusHeight", "B": "@gch.CamHeight", "bPickA": "@gfo2.FocusOn"})
        self.assertEqual(nodes["sfz"]["in"]["FocusZ"], "0.0")   # the modifier must not add the slot height a second time

    def test_drag_moves_the_active_height_in_the_band(self):
        g = graph("50_manager_ui.json", "Jodi Drag"); nodes = {n["id"]: n for n in g["nodes"]}
        for c in ("nfc", "nhc"): self.assertEqual((float(nodes[c]["in"]["Min"]), float(nodes[c]["in"]["Max"])), (ui.HEIGHT_MIN, ui.HEIGHT_MAX))
        self.assertIn("sfh", after(g, "bfo")); self.assertNotIn("sch", after(g, "bfo")); self.assertIn("sch", after(g, "bfo:else"))


if __name__ == "__main__": unittest.main()
