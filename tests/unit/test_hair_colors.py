import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
import hair_colors, strings


class HairColors(unittest.TestCase):
    def test_table(self):
        self.assertEqual(len(hair_colors.COLORS), 14)
        keys = [k for k, _, _ in hair_colors.COLORS]; self.assertEqual(len(set(keys)), 14)
        for k, rgb, names in hair_colors.COLORS:
            self.assertEqual(len(rgb), 3, k); self.assertTrue(all(0.0 <= c <= 1.0 for c in rgb), k); self.assertEqual(len(names), 5, k)
            self.assertIn("Hair_" + k, strings.STRINGS)   # tooltips live in the string table

    def test_srgb_to_linear(self):
        self.assertAlmostEqual(hair_colors.lin(0), 0.0); self.assertAlmostEqual(hair_colors.lin(255), 1.0, places=6); self.assertAlmostEqual(hair_colors.lin(128), 0.2158605, places=5)


if __name__ == "__main__":
    unittest.main()
