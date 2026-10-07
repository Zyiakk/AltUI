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
        self.assertEqual([a["path"].rsplit("/", 1)[-1] for a in assets], ["T_RoundBox", "T_CheckOn", "T_CheckOff", "T_Undo", "T_Redo", "T_Plus", "T_Minus", "T_Colorize", "T_Cam", "T_Photo", "T_RagMode", "T_Pose", "T_AltUI"] +
                         ["T_Tab" + k for k in gen_textures.TAB_ICON_DRAW])
        # tab icons + panel icon: a texture for every tab (Poses reuses the stick figure), white glyph without ring - transparent corners
        self.assertEqual(set(gen_textures.TAB_ICONS), {"Clothes", "Outfits", "Looks", "Bag", "Hair", "Poses", "Weapons", "Look", "Body", "Face", "Mods", "Options", "Manage", "Ragdolls", "Kodex"})
        self.assertEqual(gen_textures.TAB_ICONS["Poses"], gen_textures.T_POSE)
        for f in ["altui.png"] + ["tab_%s.png" % k.lower() for k in gen_textures.TAB_ICON_DRAW]:
            im = Image.open(os.path.join(d, "tex", f)); self.assertEqual(im.size, (128, 128), f); px = im.load()
            self.assertEqual(px[0, 0][3], 0, f); self.assertEqual(px[127, 127][3], 0, f) if f != "tab_bag.png" else None
            self.assertGreater(sum(px[x, y][3] > 200 for x in range(128) for y in range(128)), 1500, f)   # a solid glyph, not a hairline
            x0, y0, x1, y1 = im.split()[3].point(lambda v: 255 if v > 20 else 0).getbbox()   # centred: icons of any height share the centre line next to the text
            self.assertLessEqual(abs((y0 + y1) / 2 - 64), 1, f); self.assertLessEqual(abs((x0 + x1) / 2 - 64), 1, f)
        for f in ("cam.png", "photo.png"):   # camera / aperture glyph: white ring (edge centre opaque), transparent corner, something white in the middle third
            px = Image.open(os.path.join(d, "tex", f)).load()
            self.assertEqual(px[0, 0][3], 0); self.assertGreater(px[32, 4][3], 200)
            self.assertTrue(any(px[x, y][3] > 200 for x in range(22, 42) for y in range(22, 42)), f)
        px = Image.open(os.path.join(d, "tex", "pose.png")).load()   # stick figure: transparent corner, body line through the centre
        self.assertEqual(px[0, 0][3], 0); self.assertGreater(px[64, 60][3], 200)
        on = Image.open(os.path.join(d, "tex", "check_on.png")).load(); off = Image.open(os.path.join(d, "tex", "check_off.png")).load()
        self.assertEqual(off[24, 24][3], 169); self.assertTrue(40 <= off[24, 24][0] <= 45)            # fill like the search field (frame + fill layer combined)
        self.assertGreater(off[24, 1][3], 40); self.assertGreater(off[24, 1][0], 200)   # light frame
        self.assertGreater(on[20, 31][0], 200)                     # white check mark
        self.assertEqual(on[0, 0][3], 0)


if __name__ == "__main__": unittest.main()
