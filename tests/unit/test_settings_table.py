"""The settings table (gen_manager.SETTINGS) drives Load Settings and Save Settings: what is missing there is neither
written nor read back, so a colour of one's own would be gone after a restart."""
import unittest, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
import gen_manager as gm


class SettingsTable(unittest.TestCase):
    def test_own_colours_are_saved(self):
        mgr_vars = [e[0] for e in gm.SETTINGS]
        for v in ("SlotColors", "EyeColors", "MakeupColors", "OutfitSlotColors"):
            self.assertIn(v, mgr_vars, v)


if __name__ == "__main__":
    unittest.main()
