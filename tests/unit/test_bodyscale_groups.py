import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts")); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
import bodyscale_groups as bg


class Groups(unittest.TestCase):
    def test_eleven_groups_21_unique_bones(self):
        self.assertEqual(len(bg.GROUPS), 11)
        bones = [b for _, bs, _ in bg.GROUPS for b in bs]
        self.assertEqual(len(bones), 21); self.assertEqual(len(set(bones)), 21); self.assertEqual(bg.GROUPS[-1][:2], ("Waist", ["Morph_Waist"]))
        self.assertEqual(set(m for _, _, m in bg.GROUPS), {"Additive"})   # Replace would shrink bones the game scales itself
        self.assertEqual(bg.BONE_GROUP["Breast_L"], "Breasts"); self.assertEqual(bg.BONE_GROUP["thigh_twist_01_r"], "LowerThighs")

    def test_sliders_cover_all_groups_once(self):
        vs = [v for _, vars_ in bg.SLIDERS for v in vars_]
        self.assertEqual(sorted(vs), sorted(v for v, _, _ in bg.GROUPS)); self.assertEqual(len(bg.SLIDERS), 9); self.assertEqual(bg.N_SLIDERS, 9); self.assertEqual(bg.SLIDERS[-1], ("Waist", ["Waist"]))
        self.assertEqual(bg.AXES["Thighs"], (0, 1, 1)); self.assertEqual(bg.AXES["Hands"], (1, 1, 1)); self.assertEqual(bg.AXES["Waist"], (0.25, 1, 0)); self.assertEqual(bg.SLIDERS[bg.HEIGHT_INDEX], ("Height", []))

    def test_internal_names_match_bpdsl(self):
        from bpdsl import struct, param
        s = struct(bg.STRUCT_PATH, [param(v, "struct:/Script/CoreUObject.Vector") for v, _, _ in bg.GROUPS])
        self.assertEqual([m["internal_name"] for m in s["members"]], [i for _, i in bg.struct_members()])

    def test_slider_mapping(self):
        self.assertAlmostEqual(bg.slider_factor(0.0), 0.5); self.assertAlmostEqual(bg.slider_factor(1.0), 2.0)
        self.assertAlmostEqual(bg.slider_value(bg.slider_factor(0.37)), 0.37); self.assertAlmostEqual(bg.slider_value(1.0), 1 / 3)
        self.assertEqual(bg.factor_range("Height"), (0.9, 1.2)); self.assertEqual(bg.factor_range("Feet"), (0.8, 1.1)); self.assertAlmostEqual(bg.slider_factor(2 / 3, "Feet"), 1.0); self.assertAlmostEqual(bg.slider_value(1.1, "Feet"), 1.0); self.assertEqual(bg.factor_range("Glutes"), (0.5, 2.0))
        self.assertEqual(sorted(bg.SLIDER_ORDER), sorted(k for k, _ in bg.SLIDERS)); self.assertEqual(bg.SLIDER_ORDER[0], "Height")
        for k, _ in bg.SLIDERS: lo, hi = bg.factor_range(k); self.assertTrue(min(lo, hi) <= 1.0 <= max(lo, hi), k)
        self.assertEqual(bg.factor_range("Waist"), (1.5, 0.6)); self.assertAlmostEqual(bg.slider_factor(0.0, "Waist"), 1.5); self.assertAlmostEqual(bg.slider_value(0.6, "Waist"), 1.0)   # left = wider, like the game's slider

    def test_parent_groups(self):
        self.assertEqual(bg.BONE_PARENT["foot_l"], "calf_l"); self.assertEqual(bg.BONE_PARENT["hand_r"], "lowerarm_r"); self.assertEqual(bg.BONE_PARENT["calf_twist_01_l"], "calf_l")
        self.assertEqual(sorted(bg.descendants("thigh_l")), ["calf_l", "calf_twist_01_l", "foot_l", "thigh_twist_01_l"])
        self.assertEqual(bg.descendants("Breast_L"), []); self.assertNotIn("Thighs", bg.PARENT_GROUP)


if __name__ == "__main__": unittest.main()
