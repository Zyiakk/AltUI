import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
import bpdsl as b

SK = "/Game/X/SK"


class BlendSpaceDslTest(unittest.TestCase):
    def test_ok(self):
        d = b.blendspace1d("/Game/X/BS", SK, "Speed", 0, 360, 36, [("/Game/X/A", 0), ("/Game/X/B", 40), ("/Game/X/C", 360)], smoothing=0.3)
        self.assertEqual(d["type"], "blendspace1d"); self.assertEqual(d["axis"], {"name": "Speed", "min": 0.0, "max": 360.0, "grid": 36})
        self.assertEqual(d["samples"][1], ["/Game/X/B", 40.0]); self.assertEqual(d["smoothing"], 0.3)

    def test_refusals(self):
        for samples, text in (([("/A", 0), ("/B", 45)], "off the grid"), ([("/A", 0), ("/B", 400)], "outside"),
                              ([("/A", 0), ("/B", 0)], "twice"), ([("/A", 0)], "at least two")):
            with self.assertRaisesRegex(ValueError, text): b.blendspace1d("/Game/X/BS", SK, "Speed", 0, 360, 36, samples)


class AnimPlayerDslTest(unittest.TestCase):
    def test_entry(self):
        d = b.animplayer("/Game/X/ABP", SK, "/Game/X/BS", "/Game/X/Ov", add_slot=True, make_overlay_additive=True)
        self.assertEqual(d, {"type": "animplayer", "path": "/Game/X/ABP", "skeleton": SK, "blendspace": "/Game/X/BS", "overlay": "/Game/X/Ov",
                             "speed_var": "Speed", "alpha_var": "OverlayAlpha", "alpha_default": 1.0, "slot": "DefaultSlot",
                             "add_slot": True, "make_overlay_additive": True})

    def test_refusals(self):
        with self.assertRaisesRegex(ValueError, "same name"): b.animplayer("/A", SK, "/B", "/C", speed_var="X", alpha_var="X")
        with self.assertRaisesRegex(ValueError, "slot"): b.animplayer("/A", SK, "/B", "/C", slot="")


if __name__ == "__main__":
    unittest.main()
