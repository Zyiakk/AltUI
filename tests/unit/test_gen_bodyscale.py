import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, "..", "..")
sys.path.insert(0, os.path.join(W, "assets", "gen")); sys.path.insert(0, os.path.join(W, "scripts"))
import bodyscale_groups as bg
import footik


class GenBodyScale(unittest.TestCase):
    def setUp(self):
        import gen_bodyscale   # writes assets/25_bodyscale.json on import
        assets = json.load(open(os.path.join(W, "assets", "25_bodyscale.json")))["assets"]
        self.a = next(a for a in assets if a["type"] == "animblueprint"); self.stubs = [a for a in assets if a["type"] == "animsequence_stub"]

    def test_asset(self):
        self.assertEqual(self.a["type"], "animblueprint"); self.assertEqual(self.a["path"], bg.ABP_PATH)
        self.assertEqual(self.a["skeleton"], "/Game/Project/Character/Jodi/Body/Female_Skeleton")
        variables = self.a["variables"][:-len(footik.ABP_VARS)]
        self.assertEqual([v["name"] for v in variables], [v for v, _, _ in bg.GROUPS] + [v for v, _ in bg.SHIFTS] + [v for v, _ in bg.LATE_SHIFTS] + [v for v, _ in bg.ROTATIONS] + ["EyeClosedL", "EyeClosedR"])
        for v in variables:
            if v["name"] in ("EyeClosedL", "EyeClosedR"):
                self.assertEqual((v["type"], v["default"]), ("float", "0.0")); continue
            if v["name"] in dict(bg.ROTATIONS):
                self.assertEqual(v["type"], "struct:/Script/CoreUObject.Rotator"); self.assertEqual(v["default"], "(P=0,Y=0,R=0)"); continue
            self.assertEqual(v["type"], "struct:/Script/CoreUObject.Vector")
            self.assertEqual(v["default"], "(X=0,Y=0,Z=0)" if v["name"] in dict(bg.SHIFTS + bg.LATE_SHIFTS) else "(X=1,Y=1,Z=1)")

    def test_foot_ik_last(self):
        """Foot IK (2026-11-09): BenenG47's 15 nodes after the rotations; IK reads the scaled, shifted pose."""
        n = len(footik.abp_nodes())
        self.assertEqual(n, 15)
        self.assertEqual(self.a["nodes"][-n:], footik.abp_nodes())
        self.assertEqual(self.a["nodes"][-n - len(bg.ROTATIONS) * 2:-n], [{"bone": b, "kind": "rotate", "var": v} for v, bs in bg.ROTATIONS for b in bs])
        ik = {v["name"]: v for v in self.a["variables"][-len(footik.ABP_VARS):]}
        self.assertEqual([(k, v["type"], v["default"]) for k, v in ik.items()], footik.ABP_VARS)
        self.assertTrue(all(d in ("(X=0,Y=0,Z=0)", "(P=0,Y=0,R=0)", "0.0") for _, _, d in footik.ABP_VARS))

    def test_eyes_closed(self):
        """Face tab "Eyes closed" / one eye: the game's additive blink animation on top of the pose, once per lid (limited to its bone),
        alpha = EyeClosedL / R; its kit stand-in is additive."""
        eye = "/Game/Project/Character/Jodi/Animations/Female_EyeClosed"
        self.assertEqual(self.a["additive"], [{"asset": eye, "alpha": "EyeClosedL", "time": 1.0, "bones": ["Eye_L"]},
                                              {"asset": eye, "alpha": "EyeClosedR", "time": 1.0, "bones": ["Eye_R"]}])   # held on the closed frame, never played
        self.assertEqual(self.stubs, [{"type": "animsequence_stub", "path": eye, "skeleton": self.a["skeleton"], "additive": True}])

    def test_nodes(self):
        # floor compensation first, then the scale nodes (23), the leg shift, the rotation nodes (4)
        nodes = self.a["nodes"][:-15]; late = nodes[-len(bg.ROTATIONS) * 2 - 2:-len(bg.ROTATIONS) * 2]
        self.assertEqual(late, [{"bone": "thigh_l", "kind": "translate", "var": "LegShiftL"}, {"bone": "thigh_r", "kind": "translate", "var": "LegShiftR"}])   # behind pelvis' scale, which would scale the shift
        nodes = [n for n in nodes if n not in late]; shifts = [n for n in nodes if n.get("kind") == "translate"]; rots = [n for n in nodes if n.get("kind") == "rotate"]
        scales = [n for n in nodes if n.get("kind") not in ("translate", "rotate")]
        self.assertEqual(nodes[:len(shifts)], shifts); self.assertEqual(len(scales), 23); self.assertEqual(nodes[-len(rots):], rots)
        self.assertEqual([(n["bone"], n["var"]) for n in shifts], [(b, v) for v, bs in bg.SHIFTS for b in bs])
        self.assertEqual([n["bone"] for n in scales], [b for _, bs, _ in bg.GROUPS for b in bs])
        self.assertEqual([(n["bone"], n["var"]) for n in rots], [(b, v) for v, bs in bg.ROTATIONS for b in bs])
        for n in scales:
            self.assertEqual(n["var"], bg.BONE_GROUP[n["bone"]]); self.assertEqual(n["mode"], dict((v, m) for v, _, m in bg.GROUPS)[n["var"]])

    def test_shift_formulas(self):
        # root: sole S below the mesh origin scaled by h -> component-space shift S(1 - 1/h) keeps it on the floor; feet: A(f - 1) keeps the heel down
        self.assertAlmostEqual(bg.root_shift(1.0), 0.0); self.assertLess(bg.root_shift(0.9), 0); self.assertGreater(bg.root_shift(1.2), 0)
        self.assertAlmostEqual(bg.root_shift(0.9) * 0.9, -(1 - 0.9) * bg.SOLE_BELOW_ORIGIN)   # world shift = component shift x h
        self.assertAlmostEqual(bg.feet_shift(1.0), 0.0); self.assertAlmostEqual(bg.feet_shift(0.8), -0.2 * bg.ANKLE_TO_SOLE); self.assertAlmostEqual(bg.feet_shift(1.1), 0.1 * bg.ANKLE_TO_SOLE)


if __name__ == "__main__": unittest.main()
