"""scripts/animcurves.py: curves of a cooked AnimSequence (docs/specs/2026-10-06-anim-pipeline-design.md). Needs the game's Female_Walk /
Female_Run extracted to build/anim/src (scripts/anim_extract.sh); skipped otherwise."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts"))
SRC = os.path.join(H, "..", "..", "build", "anim", "src", "TheKillingAntidote", "Content", "Project", "Character", "Jodi", "Animations")


def src(name):
    p = os.path.join(SRC, name + ".uasset")
    if not os.path.exists(p): raise unittest.SkipTest("no extracted " + name)
    return p


class Curves(unittest.TestCase):
    def test_female_walk(self):
        import animcurves
        c = animcurves.read(src("Female_Walk"))
        self.assertEqual(sorted(c["curves"]), sorted(["MoveData_Speed", "MoveData_FootPhase", "Enable_LeanLR", "Upper Body Yaw Ratio", "Rotation Speed", "Face_Idle", "Forward Moving Alpha"]))
        ev = lambda n, t: animcurves.evaluate(c["curves"][n], t)
        self.assertAlmostEqual(ev("MoveData_Speed", 0.5), 208.0, places=3); self.assertAlmostEqual(ev("Rotation Speed", 1.0), 120.0, places=3)
        self.assertAlmostEqual(ev("Forward Moving Alpha", 0.3), 1.0, places=3)
        phase = [ev("MoveData_FootPhase", i / 30.0) for i in range(56)]
        self.assertTrue(all(-1.5 <= v <= 1.5 for v in phase), phase)
        self.assertGreater(max(phase) - min(phase), 0.2)   # a real phase curve, not a constant

    def test_sample_rows(self):
        import animcurves
        c = animcurves.read(src("Female_Walk")); rows = animcurves.sample(c, 30.0)
        self.assertEqual(len(rows["MoveData_Speed"]), 57); self.assertAlmostEqual(rows["MoveData_Speed"][-1][0], 56 / 30.0, places=3)
