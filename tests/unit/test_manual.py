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

    def test_sections(self):
        self.assertEqual(manual.parse("## A {#a}\nintro\n\n### Head\ntext\n- y\n"), [("a", "A", "intro\n\n§§Head§§\ntext\n• y")])
        with self.assertRaises(ValueError): manual.parse("## A {#a}\nx §§ y")

    def test_same_sections_in_every_language(self):
        # the manager splits at SEP: every language has the same number of sections per chapter
        ref = {i: b.count(manual.SEP) for i, _, b in manual.load("en")}
        for lang in LANGS:
            self.assertEqual({i: b.count(manual.SEP) for i, _, b in manual.load(lang)}, ref, lang)

    def test_sections_have_heading_and_text(self):
        # Rebuild Kodex: part 0 = intro, then heading / text pairs; an empty heading or text would show a bare line
        for lang in LANGS:
            for i, _, b in manual.load(lang):
                parts = b.split(manual.SEP)
                self.assertTrue(parts[0].strip(), (lang, i, "intro"))
                for k in range(1, len(parts), 2):
                    self.assertTrue(parts[k].strip(), (lang, i, k)); self.assertTrue(parts[k + 1].strip(), (lang, i, parts[k]))

    def test_no_missing_glyphs(self):
        # the panel font has no triangle symbols: they show as "?" in game
        for lang in LANGS:
            for i, t, b in manual.load(lang):
                for ch in "▾▸▶▼◀►▲△▽◂▴":
                    self.assertNotIn(ch, t + b, (lang, i, ch))

    def test_braces_survive(self):
        self.assertEqual(manual.rows(["en"], {"en": [("a", "T {x}", "B {0}")]}), {"Man_a_T": ("T {{x}}",), "Man_a_B": ("B {{0}}",)})


if __name__ == "__main__":
    unittest.main()
