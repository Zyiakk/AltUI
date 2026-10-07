"""Every text key the generators look up must be in the strings table: a missing one shows its raw key in the game
("Kodex_Passwords" as the heading of Codex > Passwords, 2026-10-07). Literal keys of tt() / ts() calls, plus the keys
built from lists (every fixed key tt() / ts() saw while generating)."""
import unittest, os, sys, re, glob
H = os.path.dirname(os.path.abspath(__file__)); GEN = os.path.join(H, "..", "..", "assets", "gen"); sys.path.insert(0, GEN)
from strings import STRINGS

CALL = re.compile(r'\b(?:tt|ts)\(\s*\w+\s*,\s*[^,()]+,\s*"([A-Za-z0-9_]+)"\s*\)')


class StringKeys(unittest.TestCase):
    def test_literal_keys(self):
        missing = sorted({(os.path.basename(f), k) for f in glob.glob(os.path.join(GEN, "*.py"))
                          for k in CALL.findall(open(f, encoding="utf-8").read()) if k not in STRINGS})
        self.assertEqual(missing, [])

    def test_kodex_sections(self):
        import gen_manager_ui
        for k in gen_manager_ui.KODEX_SECTIONS:
            self.assertIn("Kodex_" + k, STRINGS)

    def test_every_key_used_while_generating(self):
        """Also the keys built from lists ("Joint_" + bone showed raw in the Ragdolls tab, 2026-10-07)."""
        import gen_manager_ui
        self.assertGreater(len(gen_manager_ui.USED_KEYS), 200)
        self.assertEqual(sorted(k for k in gen_manager_ui.USED_KEYS if k not in STRINGS), [])


if __name__ == "__main__":
    unittest.main()
