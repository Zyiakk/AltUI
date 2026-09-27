import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, "..", "..")
sys.path.insert(0, os.path.join(W, "scripts")); sys.path.insert(0, os.path.join(W, "assets", "gen"))
import weapon_skins as ws
import gen_weaponexample as ex
from pakio import open_pak

MOD = ex.MOD.rsplit("/", 1)[1]                      # the folder name is the generator's, never a second spelling
E = os.path.join(W, "examples", MOD)


class WeaponExampleShipped(unittest.TestCase):
    """The files under examples/ against what the generator produces."""

    def test_editor_assets_are_there(self):
        for name in ("T_ExampleSkin", "Mod_WeaponSkin", "TKA_Mod_Table"):
            p = os.path.join(E, "editor", name + ".uasset")
            self.assertTrue(os.path.isfile(p), p)

    def test_skin_table_points_at_the_altui_struct(self):
        b = open(os.path.join(E, "editor", "Mod_WeaponSkin.uasset"), "rb").read()
        self.assertIn(ws.STRUCT_PATH.encode(), b)
        self.assertIn(ex.ROW.encode(), b)

    def test_pak_holds_the_three_assets_under_the_mod_folder(self):
        pk = open_pak(os.path.join(E, MOD + ".pak"))
        keys = [k for k in pk.files if k.endswith(".uasset")]
        self.assertEqual(sorted(os.path.basename(k)[:-7] for k in keys),
                         ["Mod_WeaponSkin", "TKA_Mod_Table", "T_ExampleSkin"])
        self.assertIn(MOD, pk.mount)

    def test_pak_ships_no_altui_asset(self):
        # the structs belong to AltUI.pak: a copy here would replace AltUI's for everyone who installs the example
        pk = open_pak(os.path.join(E, MOD + ".pak"))
        self.assertEqual([k for k in pk.files if "AltUI/" in k], [])


if __name__ == "__main__": unittest.main()
