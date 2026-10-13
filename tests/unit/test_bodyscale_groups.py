import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts")); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
import bodyscale_groups as bg


class Groups(unittest.TestCase):
    def test_eleven_groups_21_unique_bones(self):
        self.assertEqual(len(bg.GROUPS), 13)
        bones = [b for _, bs, _ in bg.GROUPS for b in bs]
        self.assertEqual(len(bones), 23); self.assertEqual(len(set(bones)), 23)
        self.assertEqual(bg.GROUPS[10][:2], ("Waist", ["Morph_Waist"]))   # Waist stays at index 10: older Body_Scale rows
        self.assertEqual(bg.GROUPS[11:], [("Pelvis", ["pelvis"], "Additive"), ("PelvisSpine", ["spine_01"], "Additive")])
        self.assertEqual(set(m for _, _, m in bg.GROUPS), {"Additive"})   # Replace would shrink bones the game scales itself
        self.assertEqual(bg.BONE_GROUP["Breast_L"], "Breasts"); self.assertEqual(bg.BONE_GROUP["thigh_twist_01_r"], "LowerThighs")

    def test_sliders_cover_all_groups_once(self):
        vs = [v for _, vars_ in bg.SLIDERS for v in vars_]
        self.assertEqual(sorted(vs), sorted(v for v, _, _ in bg.GROUPS)); self.assertEqual(len(bg.SLIDERS), 17); self.assertEqual(bg.N_SLIDERS, 17)
        self.assertEqual(bg.SLIDERS[8], ("Waist", ["Waist"]))   # the first nine keep their index: saved arrays stay valid
        self.assertEqual([k for k, _ in bg.SLIDERS[9:]], ["Pelvis", "BreastAngle", "GlutesAngle", "BreastJiggle", "BreastSoft", "GlutesJiggle", "GlutesSoft", "Nipple"])
        self.assertEqual(bg.SLIDERS[9], ("Pelvis", ["Pelvis", "PelvisSpine"]))
        self.assertEqual(bg.AXES["Thighs"], (0, 1, 1)); self.assertEqual(bg.AXES["Hands"], (1, 1, 1)); self.assertEqual(bg.AXES["Waist"], (0.25, 1, 0)); self.assertEqual(bg.SLIDERS[bg.HEIGHT_INDEX], ("Height", []))
        # the bust follows Female_Morph_Breasts (scale delta (0.2, 0.35, 0.35) per bone), the glutes have no morph to follow
        self.assertEqual(bg.AXES["Breasts"], (0.571, 1, 1)); self.assertEqual(bg.AXES["GlutesHips"], (1, 1, 1))
        # hip width: pelvis only sideways (local Z); spine_01 gets no factor of its own, only the compensation 1 / pelvis
        self.assertEqual(bg.AXES["Pelvis"], (0, 0, 1)); self.assertEqual(bg.AXES["PelvisSpine"], (0, 0, 0))

    def test_neutral_values(self):
        self.assertEqual(len(bg.NEUTRAL), bg.N_SLIDERS); self.assertEqual(bg.NEUTRAL[:10], [1.0] * 10)
        n = dict(zip([k for k, _ in bg.SLIDERS], bg.NEUTRAL))
        self.assertEqual((n["BreastAngle"], n["GlutesAngle"], n["Nipple"]), (0.0, 0.0, 0.0))
        self.assertEqual((n["BreastJiggle"], n["BreastSoft"], n["GlutesJiggle"], n["GlutesSoft"]), (1.0, 1.0, 1.0, 1.0))
        self.assertEqual(bg.OLDEST_PADDED, 8)

    def test_rotations_and_display(self):
        self.assertEqual(bg.ROTATIONS, [("BreastAngle", ["Breast_L", "Breast_R"]), ("GlutesAngle", ["Hip_L", "Hip_R"])])
        self.assertEqual(bg.DISPLAY["BreastAngle"], "deg"); self.assertEqual(bg.DISPLAY["GlutesJiggle"], "pct"); self.assertEqual(bg.DISPLAY["Nipple"], "num"); self.assertEqual(bg.DISPLAY.get("Thighs", "x"), "x")
        self.assertEqual(bg.ALL_BODIES, {"Height", "BreastJiggle", "GlutesJiggle", "Nipple"}); self.assertEqual(bg.RETIRED, {"BreastSoft", "GlutesSoft"})
        self.assertEqual(bg.PHYS_BONES, {"Breast": ["Breast_L", "Breast_R"], "Glutes": ["Hip_L", "Hip_R"]})
        self.assertEqual(bg.GROUP_HEADS, {"BreastAngle": "Lbl_ScGrpBreast", "Pelvis": "Lbl_ScGrpGlutes"})
        o = bg.SLIDER_ORDER; self.assertEqual(o[9:], ["BreastAngle", "BreastJiggle", "Nipple", "Pelvis", "GlutesAngle", "GlutesJiggle"])   # retired keys: no row

    def test_internal_names_match_bpdsl(self):
        from bpdsl import struct, param
        s = struct(bg.STRUCT_PATH, [param(v, "struct:/Script/CoreUObject.Vector") for v, _, _ in bg.GROUPS])
        self.assertEqual([m["internal_name"] for m in s["members"]], [i for _, i in bg.struct_members()])

    def test_slider_mapping(self):
        self.assertAlmostEqual(bg.slider_factor(0.0), 0.5); self.assertAlmostEqual(bg.slider_factor(1.0), 2.0)
        self.assertAlmostEqual(bg.slider_value(bg.slider_factor(0.37)), 0.37); self.assertAlmostEqual(bg.slider_value(1.0), 1 / 3)
        self.assertEqual(bg.factor_range("Height"), (0.9, 1.2)); self.assertEqual(bg.factor_range("Feet"), (0.8, 1.1)); self.assertAlmostEqual(bg.slider_factor(2 / 3, "Feet"), 1.0); self.assertAlmostEqual(bg.slider_value(1.1, "Feet"), 1.0); self.assertEqual(bg.factor_range("Glutes"), (0.5, 2.0))
        self.assertEqual(bg.SLIDER_ORDER[0], "Height")
        for (k, _), n in zip(bg.SLIDERS, bg.NEUTRAL): lo, hi = bg.factor_range(k); self.assertTrue(min(lo, hi) <= n <= max(lo, hi), k)
        self.assertEqual(sorted(bg.SLIDER_ORDER), sorted(k for k, _ in bg.SLIDERS if k not in bg.RETIRED))
        self.assertEqual(bg.factor_range("BreastAngle"), (-15.0, 15.0)); self.assertEqual(bg.factor_range("BreastJiggle"), (0.0, 1.0))
        self.assertEqual(bg.factor_range("Pelvis"), (0.8, 1.3)); self.assertEqual(bg.factor_range("Nipple"), (-1.0, 1.0))
        self.assertEqual(bg.factor_range("Waist"), (1.5, 0.6)); self.assertAlmostEqual(bg.slider_factor(0.0, "Waist"), 1.5); self.assertAlmostEqual(bg.slider_value(0.6, "Waist"), 1.0)   # left = wider, like the game's slider

    def test_parent_groups(self):
        self.assertEqual(bg.BONE_PARENT["foot_l"], "calf_l"); self.assertEqual(bg.BONE_PARENT["hand_r"], "lowerarm_r"); self.assertEqual(bg.BONE_PARENT["calf_twist_01_l"], "calf_l")
        self.assertEqual(sorted(bg.descendants("thigh_l")), ["calf_l", "calf_twist_01_l", "foot_l", "thigh_twist_01_l"])
        self.assertEqual(bg.descendants("Breast_L"), [])
        self.assertEqual(bg.PARENT_GROUP["Thighs"], "Pelvis"); self.assertEqual(bg.PARENT_GROUP["GlutesHips"], "Pelvis"); self.assertEqual(bg.PARENT_GROUP["PelvisSpine"], "Pelvis")


if __name__ == "__main__": unittest.main()
