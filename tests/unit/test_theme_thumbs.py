"""2026-10-16: Options > Theme "Show previews" - the picture chips show the picture (AltUI's: textures of their own, the user's:
rendered once into Images/Thumbs), off by default."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, asset
import gen_widgets as gw, gen_manager, theme_images as ti


def by_id(g): return {n["id"]: n for n in g["nodes"]}
def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]


class Setting(unittest.TestCase):
    def test_saved_and_off_by_default(self):
        rows = {m: d for m, _, _, d in gen_manager.SETTINGS}; self.assertIn("ImgThumbs", rows); self.assertIsNone(rows["ImgThumbs"])

    def test_row_before_the_picture_sections(self):
        rows = gw.OPT_CAT_ROWS["Theme"]; self.assertLess(rows.index("LblImgHint"), rows.index("RowImgThumbs")); self.assertLess(rows.index("RowImgThumbs"), rows.index("SecBgPic"))

    def test_chip_switches_without_applying(self):
        g = mgr_graph("Select Image Chip"); b = by_id(g)
        self.assertEqual(b["ImgThumbsis"]["in"]["InPrefix"], "ImgThumbs"); self.assertNotIn("ImgThumbsap", b)
        self.assertTrue(any(c[-2:] == ["ImgThumbsb", "ImgThumbsset"] for c in g["exec"]))


class Chips(unittest.TestCase):
    def test_every_picture_chip_gets_a_preview(self):
        g = mgr_graph("Rebuild Image Chips"); th = [n for n in g["nodes"] if n.get("function") == "Chip Thumb"]
        self.assertEqual(len(th), len(ti.BACKGROUNDS) + len(ti.BUTTONS) + 4)   # built-ins, "none" (height only) and one per user-file loop
        self.assertTrue(all("Thumb" in n["in"]["thumb"] for n in th if n["in"]["thumb"].startswith("b:")))
        self.assertTrue(calls(g, "Array_Clear"))   # render targets freed

    def test_chip_thumb_only_when_on(self):
        g = mgr_graph("Chip Thumb"); self.assertIn(["entry", "bo", "bne", "sth"], g["exec"]); self.assertIn(["bne:else", "tt", "bv", "st", "tip"], g["exec"])
        self.assertIn(["bv:else", "sth"], g["exec"]); self.assertEqual(by_id(g)["bo"]["in"]["Condition"], "@go.ImgThumbs")

    def test_none_chip_as_tall_as_the_previews(self):
        g = mgr_graph("Rebuild Image Chips"); none = [n for n in g["nodes"] if n.get("function") == "Chip Thumb" and n["in"]["thumb"] == ""]
        self.assertEqual(len(none), 2)   # background and button row
        a = asset(gw.W_SUB); self.assertIn("Set Thumb Size", {f["name"] for f in a["functions"]})

    def test_sub_tab_has_the_picture(self):
        a = asset(gw.W_SUB); names = {f["name"] for f in a["functions"]}; self.assertLessEqual({"Set Thumb", "Set Thumb Filters"}, names)
        st = next(f["graph"] for f in a["functions"] if f["name"] == "Set Thumb"); self.assertTrue(calls(st, "SetBrushFromMaterial"))

    def test_filters_follow_live(self):
        self.assertTrue(calls(mgr_graph("Apply Bg Image"), "Bg Thumb Filters")); self.assertTrue(calls(mgr_graph("Apply Button Image"), "Btn Thumb Filters"))


class RedoMenu(unittest.TestCase):
    def test_menu_row_only_for_own_pictures_with_previews(self):
        g = mgr_graph("SubTab Context"); b = by_id(g)
        self.assertEqual(b["isit"]["in"]["B"], "@gith.ImgThumbs"); self.assertEqual(b["bisp"]["in"]["Condition"], "@ismenu.ReturnValue")
        self.assertTrue(any("Menu_ThumbRedo" in str(n.get("in")) for n in g["nodes"]))
        conds = {n["in"]["Condition"] for n in g["nodes"] if n.get("id", "").startswith("cb")}; self.assertIn("@isit.ReturnValue", conds); self.assertIn("@isp.ReturnValue", conds)

    def test_redo_draws_from_the_file_and_rebuilds(self):
        g = mgr_graph("Redo User Thumb"); self.assertIn(["entry", "ric", "rtc", "imp", "biv", "wt", "frt", "abg", "abt", "ric2"], g["exec"])
        self.assertEqual(by_id(g)["sp"]["in"]["InStr"], ":f:")
        self.assertTrue(any(n.get("function") == "Redo User Thumb" for n in mgr_graph("On Menu Action")["nodes"]))


class UserThumbs(unittest.TestCase):
    def test_file_first_then_render(self):
        g = mgr_graph("Thumb Tex"); self.assertTrue(calls(g, "FileExists")); self.assertTrue(calls(g, "Write User Thumb"))
        self.assertEqual(len(calls(g, "ImportFileAsTexture2D")), 2)

    def test_halving_chain(self):
        g = mgr_graph("Write User Thumb"); self.assertEqual(len(calls(g, "K2_DrawTexture")), ti.THUMB_STEPS + 1)
        self.assertEqual(len(calls(g, "ExportRenderTarget")), 1)
        r = mgr_graph("Thumb RTs"); sizes = [(int(n["in"]["Width"]), int(n["in"]["Height"])) for n in calls(r, "CreateRenderTarget2D")]
        self.assertIn(ti.THUMB_PX["bg"], sizes); self.assertIn((ti.THUMB_PX["bg"][0] << ti.THUMB_STEPS, ti.THUMB_PX["bg"][1] << ti.THUMB_STEPS), sizes)

    def test_redrawn_when_the_picture_loads(self):
        g = mgr_graph("Image Tex"); self.assertIn(["bc:else", "imp", "biv", "add", "bth", "wut", "frt", "s3", "return"], g["exec"])

    def test_jpeg_is_found_too(self):
        g = mgr_graph("Scan User Images"); names = {n["in"].get("Value") or n["in"].get("NewItem") for n in g["nodes"] if n.get("function") == "Array_Add"}
        lits = {n.get("value") for n in g["nodes"]} | {str(n.get("in")) for n in g["nodes"]}
        self.assertTrue(any("Background_1.jpeg" in str(x) for x in lits)); self.assertTrue(any("Button_30.jpeg" in str(x) for x in lits))
        import strings; self.assertTrue(all(".jpeg" in v for v in strings.STRINGS["Img_Hint"]))

    def test_builtin_thumbs_have_the_chip_aspect(self):
        import numpy as np
        for kind, (w, h) in ti.THUMB_PX.items():
            self.assertEqual(ti.thumb(np.zeros((300, 500, 3)), kind).size, (w, h))
            self.assertAlmostEqual(w / h, ti.THUMB_UNITS[kind][0] / ti.THUMB_UNITS[kind][1], places=2)


if __name__ == "__main__": unittest.main()

