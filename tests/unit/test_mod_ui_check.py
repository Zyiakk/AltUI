"""scripts/mod_ui_check.py and the text IDs of the cooked example mod (spec 2026-11-15-mod-table-text-ids)."""
import os, sys, tempfile, unittest
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts"))
import mod_ui_check as mc
import pak11_extract

EXAMPLE = os.path.join(H, "..", "..", "examples", "AltUIMod_Example", "AltUIMod_Example.pak")


class Cooked(unittest.TestCase):
    def test_example_has_its_own_namespaces(self):
        cells = mc.pak_texts(EXAMPLE)
        self.assertTrue(cells)
        for asset, row, col, ns, key, text in cells:
            self.assertEqual(ns, "/Game/Mod/AltUIMod_Example/" + os.path.basename(asset), (row, col))   # the cook kept the package path
        ids = {(os.path.basename(a), r, c): (k, t) for a, r, c, ns, k, t in cells}
        self.assertEqual(ids[("AltUI_Fields", "Lamp_Light", "Label")], ("Lamp_Light_Label", "Light"))
        self.assertEqual(ids[("AltUI_Fields", "Lamp_Colour", "Options[0]")][0], "Lamp_Colour_Options_Index0")
        self.assertEqual(ids[("AltUI_Entries", "Lamp", "Caption")], ("Lamp_Caption", "Example lamp"))

    def test_example_alone_has_no_collision(self):
        self.assertEqual(mc.collisions({"a.pak": mc.pak_texts(EXAMPLE)}), [])


class Collisions(unittest.TestCase):
    def cell(self, key, text): return ("/Game/Mod/X/AltUI_Fields", key.split("_")[0], "Label", "AltUI_Fields", key, text)

    def test_same_id_other_text_in_two_paks(self):
        hits = mc.collisions({"A.pak": [self.cell("Size_Label", "Moon size")], "B.pak": [self.cell("Size_Label", "Scale")]})
        self.assertEqual([h[0] for h in hits], [("AltUI_Fields", "Size_Label")])
        self.assertEqual(sorted(u[0] for u in hits[0][1]), ["A.pak", "B.pak"])

    def test_same_text_or_same_pak_is_no_collision(self):
        self.assertEqual(mc.collisions({"A.pak": [self.cell("Size_Label", "Size")], "B.pak": [self.cell("Size_Label", "Size")]}), [])
        self.assertEqual(mc.collisions({"A.pak": [self.cell("Size_Label", "a"), self.cell("Size_Label", "b")]}), [])

    def test_member_names_without_guid(self):
        got = list(mc.texts({"Label_8_5E509861919FC75AF40D50F0CC290677": {"text": "x", "ns": "n", "key": "k"},
                             "Options_9_5E509861919FC75AF40D50F0CC290677": [{"text": "a", "ns": "n", "key": "k0"}, "invariant"]}, ""))
        self.assertEqual(got, [("Label", "n", "k", "x"), ("Options[0]", "n", "k0", "a")])

    def test_exit_code(self):
        self.assertEqual(mc.main([EXAMPLE]), 0)


class GameExe(unittest.TestCase):
    def test_found_from_content_paks_and_from_mods(self):
        with tempfile.TemporaryDirectory() as d:
            game = os.path.join(d, "TheKillingAntidote")
            os.makedirs(os.path.join(game, "Binaries", "Win64")); os.makedirs(os.path.join(game, "Content", "Paks")); os.makedirs(os.path.join(game, "Mods"))
            exe = os.path.join(game, "Binaries", "Win64", "TheKillingAntidote-Win64-Shipping.exe"); open(exe, "wb").close()
            self.assertEqual(pak11_extract.game_exe(os.path.join(game, "Content", "Paks", "x.pak")), exe)
            self.assertEqual(pak11_extract.game_exe(os.path.join(game, "Mods", "x.pak")), exe)
            self.assertIsNone(pak11_extract.game_exe(os.path.join(d, "x.pak")))


if __name__ == "__main__": unittest.main()
