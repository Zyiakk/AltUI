"""scripts/altui_names.py – AltUI_Names.sav <-> JSON."""
import unittest, os, sys, json, tempfile, subprocess
H = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(H, "..", "..", "scripts"); sys.path.insert(0, S)
import altui_names as an, savegame_gvas as gv
EMPTY = {"mods": {}, "groups": {}, "items": {}, "hair": {}, "skins": {}, "makeup": {}}


class Convert(unittest.TestCase):
    def test_to_json_sections(self):
        sg = gv.new_names_save(); sg.set_map("Names", {"item:A": "Alpha", "mod:M": "Mod M", "skin:S": "Skin S", "weird": "ignored"})
        self.assertEqual(an.to_json(sg), dict(EMPTY, items={"A": "Alpha"}, mods={"M": "Mod M"}, skins={"S": "Skin S"}))

    def test_to_json_kind_case_insensitive(self):
        # the game writes the kind prefix with whatever case the first writer used ("Group:", "Item:", "Hair:" next to "mod:"); FNames compare
        # case-insensitively in the game - a case-sensitive export dropped 67 of a user's 228 names (2026-09-21). Keys keep their row case.
        sg = gv.new_names_save(); sg.set_map("Names", {"Group:Kpop": "K-Pop", "Item:Dress05": "Kleid", "HAIR:Hair_1": "Bob", "mod:M": "Mod M"})
        self.assertEqual(an.to_json(sg), dict(EMPTY, groups={"Kpop": "K-Pop"}, items={"Dress05": "Kleid"}, hair={"Hair_1": "Bob"}, mods={"M": "Mod M"}))

    def test_from_json_replaces_and_skips_empty(self):
        sg = gv.new_names_save(); sg.set_map("Names", {"item:Old": "x"})
        n = an.from_json(sg, {"items": {"A": "Alpha", "B": "  ", "C": " Cee "}, "groups": {"G": "Gee"}, "unknown": {"Z": "z"}})
        self.assertEqual(n, 3); self.assertEqual(sg.get("Names"), {"item:A": "Alpha", "item:C": "Cee", "group:G": "Gee"})


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, os.path.join(S, "altui_names.py")] + list(args), capture_output=True, text=True)

    def test_export_missing_writes_skeleton(self):
        d = tempfile.mkdtemp(); sav = os.path.join(d, "AltUI_Names.sav"); out = os.path.join(d, "n.json")
        r = self.run_cli("export", sav, "-o", out); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.load(open(out, encoding="utf-8")), EMPTY); self.assertFalse(os.path.exists(sav))

    def test_import_creates_backup_and_file(self):
        d = tempfile.mkdtemp(); sav = os.path.join(d, "AltUI_Names.sav"); src = os.path.join(d, "n.json")
        json.dump(dict(EMPTY, items={"Jietouwaitao": "Straßenjacke"}, mods={"Wanba_New_001": "夏"}), open(src, "w", encoding="utf-8"), ensure_ascii=False)
        r = self.run_cli("import", src, sav); self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("items: 1", r.stdout)
        self.assertEqual(gv.load(sav).get("Names"), {"item:Jietouwaitao": "Straßenjacke", "mod:Wanba_New_001": "夏"}); self.assertFalse(os.path.exists(sav + ".bak"))
        r = self.run_cli("import", src, sav); self.assertEqual(r.returncode, 0); self.assertTrue(os.path.exists(sav + ".bak"))
        r = self.run_cli("export", sav, "-o", os.path.join(d, "back.json")); self.assertEqual(r.returncode, 0)
        self.assertEqual(json.load(open(os.path.join(d, "back.json"), encoding="utf-8"))["items"], {"Jietouwaitao": "Straßenjacke"})

    def test_bad_json_is_an_error(self):
        d = tempfile.mkdtemp(); src = os.path.join(d, "n.json"); open(src, "w").write("[1,2]")
        r = self.run_cli("import", src, os.path.join(d, "x.sav")); self.assertNotEqual(r.returncode, 0); self.assertIn("object", r.stderr)


if __name__ == "__main__":
    unittest.main()
