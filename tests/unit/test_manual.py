"""AltUI manual (Kodex tab): assets/manual/<lang>.md -> Strings keys Man_<id>_T / Man_<id>_B."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
import manual
from strings import STRINGS, LANGS, rows


class Manual(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(manual.parse("intro ignored\n## A {#a}\nx\n\n- y\n## B {#b}\nz\n"),
                         [("a", "A", "x\n\n• y"), ("b", "B", "z")])

    def test_chapter_needs_id(self):
        with self.assertRaises(ValueError): manual.parse("## No id\ntext")

    def test_same_chapters_in_every_language(self):
        ids = manual.chapters()
        self.assertTrue(ids)
        for lang in LANGS:
            self.assertEqual([i for i, _, _ in manual.load(lang)], ids, lang)

    def test_nothing_empty(self):
        for lang in LANGS:
            for i, t, b in manual.load(lang):
                self.assertTrue(t.strip(), (lang, i)); self.assertTrue(b.strip(), (lang, i))

    def test_in_strings(self):
        r = rows()
        for i in manual.chapters():
            for k in ("Man_%s_T" % i, "Man_%s_B" % i):
                self.assertIn(k, STRINGS); self.assertEqual(len(STRINGS[k]), len(LANGS))
                self.assertEqual(sorted(r[k]), sorted(LANGS))

    def test_braces_survive(self):
        self.assertEqual(manual.rows(["en"], {"en": [("a", "T {x}", "B {0}")]}), {"Man_a_T": ("T {{x}}",), "Man_a_B": ("B {{0}}",)})


if __name__ == "__main__":
    unittest.main()
