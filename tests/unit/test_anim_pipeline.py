"""Animation pipeline (docs/specs/2026-10-06-anim-pipeline-design.md): foot phase from sync markers, psa reader, style -> animation list."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, "..", "..")
sys.path[:0] = [os.path.join(W, "scripts"), os.path.join(W, "assets", "anim"), os.path.join(W, "assets", "gen")]


class FootPhase(unittest.TestCase):
    def ev(self, keys, t):
        v = keys[0][1]
        for kt, kv, _ in keys:
            if kt <= t + 1e-9: v = kv
        return v

    def test_like_female_run(self):
        """Female_Run's own FootPhase: 1 around L, 0 around R, switching about halfway between the markers."""
        import anim_build
        keys = anim_build.foot_phase([["L", 0.014], ["R", 0.406], ["L", 0.744], ["R", 1.102]], 1.4)
        game = [(0.0, 1.0), (0.2, 0.0), (0.533, 1.0), (0.9, 0.0), (1.267, 1.0)]   # scripts/animcurves.py on Female_Run
        for t in [i / 30.0 for i in range(42)]:
            want = [v for kt, v in game if kt <= t + 1e-9][-1]
            if any(abs(t - kt) < 0.05 for kt, _ in game): continue      # the switch itself may sit up to a frame apart
            self.assertEqual(self.ev(keys, t), want, t)
        self.assertTrue(all(m == "constant" for _, _, m in keys))

    def test_two_markers_cyclic(self):
        import anim_build
        keys = anim_build.foot_phase([["R", 0.41], ["L", 0.8]], 0.8)   # Female_Run_Hurt: L at the loop end = start
        self.assertEqual(self.ev(keys, 0.05), 1.0); self.assertEqual(self.ev(keys, 0.4), 0.0); self.assertEqual(self.ev(keys, 0.7), 1.0)


class Styles(unittest.TestCase):
    def test_every_style_animation_is_built(self):
        import gen_move
        from anims import ANIMS
        for key, path in gen_move.WALK_STYLES + gen_move.RUN_STYLES:
            if path: self.assertIn(path.rsplit("/", 1)[1], ANIMS, key)
        for name, spec in ANIMS.items():
            self.assertIn("source", spec)
            if spec.get("modifier"): self.assertTrue(os.path.exists(os.path.join(W, "assets", "anim", "blender", spec["modifier"] + ".py")), name)

    def test_injured_key_not_the_old_one(self):
        import gen_move   # a user's save still holds "hurt" from the removed first try - it must stay unknown (= Normal)
        self.assertNotIn("hurt", [k.lower() for k, _ in gen_move.WALK_STYLES + gen_move.RUN_STYLES])


class Psa(unittest.TestCase):
    def test_female_walk(self):
        p = os.path.join(W, "build", "anim", "psa", "Project", "Character", "Jodi", "Animations", "Female_Walk.psa")
        if not os.path.exists(p): self.skipTest("no psa (scripts/anim_extract.sh)")
        import psa
        d = psa.read(p); a = d["anims"][0]
        self.assertEqual(a["frames"], 57); self.assertEqual(len(d["bones"]), 88); self.assertEqual(len(d["keys"]), 57 * 88)
        self.assertEqual([b["name"] for b in d["bones"]][:2], ["root", "pelvis"])
