import unittest, os, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
from PIL import Image
import gen_textures


class RoundBox(unittest.TestCase):
    def test_png_shape_and_corners(self):
        d = tempfile.mkdtemp(); p = os.path.join(d, "rb.png")
        gen_textures.round_box(p, size=48, radius=10)
        im = Image.open(p); self.assertEqual(im.mode, "RGBA"); self.assertEqual(im.size, (48, 48))
        px = im.load()
        self.assertEqual(px[0, 0][3], 0)                       # corner transparent
        self.assertEqual(px[24, 24], (255, 255, 255, 255))     # centre white, opaque
        self.assertEqual(px[24, 0], (255, 255, 255, 255))      # edge centre opaque (9-slice border)
        self.assertEqual(px[0, 24], (255, 255, 255, 255))

    def test_asset_json(self):
        d = tempfile.mkdtemp(); out = os.path.join(d, "05_textures.json")
        assets = gen_textures.build(d)
        self.assertEqual(assets[0]["type"], "texture")
        self.assertEqual(assets[0]["path"], "/Game/Mod/AltUI/T_RoundBox")
        self.assertTrue(os.path.isfile(os.path.join(d, assets[0]["file"])))
        self.assertEqual(assets[0]["props"]["CompressionSettings"], "TC_EditorIcon")
        self.assertEqual([a["path"].rsplit("/", 1)[-1] for a in assets], ["T_RoundBox", "T_CheckOn", "T_CheckOff", "T_Undo", "T_Redo", "T_Plus", "T_Minus", "T_Colorize"])
        on = Image.open(os.path.join(d, "tex", "check_on.png")).load(); off = Image.open(os.path.join(d, "tex", "check_off.png")).load()
        self.assertEqual(off[24, 24][3], 169); self.assertTrue(40 <= off[24, 24][0] <= 45)            # fill like the search field (frame + fill layer combined)
        self.assertGreater(off[24, 1][3], 40); self.assertGreater(off[24, 1][0], 200)   # light frame
        self.assertGreater(on[20, 31][0], 200)                     # white check mark
        self.assertEqual(on[0, 0][3], 0)


if __name__ == "__main__": unittest.main()
