import unittest, os, sys, re
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
from strings import STRINGS, LANGS, rows
from slots import SLOTS, GROUPS


class Strings(unittest.TestCase):
    def test_keys_and_english(self):
        self.assertEqual(LANGS, ["en", "de", "zh", "ru", "es"])
        for k, v in STRINGS.items():
            self.assertRegex(k, r"^[A-Za-z0-9_]+$"); self.assertEqual(len(v), len(LANGS), k); self.assertTrue(v[0].strip(), k)

    def test_all_langs_complete(self):
        missing = [(k, l) for k, v in STRINGS.items() for l, t in zip(LANGS, v) if not t.strip()]
        self.assertEqual(missing, [])

    def test_slots_and_groups(self):
        for s in SLOTS + ["Unknown", "All"]:
            self.assertIn("Slot_" + s, STRINGS)
        for g in GROUPS + ["Basis"]:
            self.assertIn("Group_" + g, STRINGS)

    def test_lang_chips(self):
        for l in LANGS:
            self.assertIn("Chip_Lang" + l.capitalize(), STRINGS)
        self.assertEqual(set(STRINGS["Chip_LangRu"]), {"Русский"}); self.assertEqual(set(STRINGS["Chip_LangEs"]), {"Español"})

    def test_rows(self):
        r = rows(); self.assertEqual(r["Tab_Clothes"], {"en": "Clothes", "de": "Kleidung", "zh": "服装", "ru": "Одежда", "es": "Vestimenta"}); self.assertEqual(len(r), len(STRINGS))


if __name__ == "__main__":
    unittest.main()
