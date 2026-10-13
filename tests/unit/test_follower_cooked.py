"""BP_AltUIFollower as cooked: child of NPC_Female, overrides Need to Save / Mutate / delay to mutant (followers spec, step 1).
Skips without a cooked kit (COOKED from config.sh)."""
import os, sys, unittest
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts")); sys.path.insert(0, H)
import cfg, uasset_funcs

COOKED = cfg.path("COOKED")
PATH = os.path.join(COOKED, "Mod/AltUI/BP_AltUIFollower.uasset")


@unittest.skipUnless(COOKED and os.path.exists(PATH), "no cooked BP_AltUIFollower")
class Cooked(unittest.TestCase):
    def test_child_of_npc_female(self):
        d = uasset_funcs.dump(PATH)
        self.assertIn("NPC_Female_C", d["class"]["super"])

    def test_overrides(self):
        d = uasset_funcs.dump(PATH)
        for f in ("Need to Save", "Mutate", "delay to mutant", "Apply Npc Appearance", "Apply Look", "Set Look"):
            self.assertIn(f, d["functions"])


if __name__ == "__main__":
    unittest.main()
