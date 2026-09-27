import unittest, os, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, "..", "..")
sys.path.insert(0, os.path.join(W, "scripts")); sys.path.insert(0, os.path.join(W, "assets", "gen"))
import weapon_skins as ws
import gen_weaponexample as ex


class WeaponExample(unittest.TestCase):
    """The generated example against the weapon contract: mod prefix, table rows, texture."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.assets = ex.build(self.dir)
        self.by_path = {a["path"]: a for a in self.assets}

    def test_mod_name_starts_with_the_prefix_altui_scans_for(self):
        mod = ex.MOD.rsplit("/", 1)[1]
        self.assertTrue(mod.startswith(ws.MOD_PREFIXES[0]), mod)
        for a in self.assets:
            self.assertTrue(a["path"].startswith(ex.MOD + "/"), a["path"])

    def test_skin_table_follows_the_contract(self):
        t = self.by_path[ex.MOD + "/" + ws.TABLE_NAME]
        self.assertEqual(t["row_struct"], ws.STRUCT_PATH)
        (row_name, row), = t["rows"].items()
        self.assertEqual(row_name, ex.ROW)
        self.assertEqual(row["Weapon"], "UMP45")
        self.assertIn(row["Weapon"], ws.WEAPONS)
        self.assertEqual(row["MainTex"], ex.TEX + "." + ex.TEX.rsplit("/", 1)[1])
        self.assertEqual(set(row) - {"Weapon", "Caption", "MainTex"}, set())   # only replace what is replaced

    def test_row_name_carries_the_mod_name(self):
        # AltUI keys owner and weapon by row name - a bare "Checker" would collide with the next mod's
        self.assertTrue(ex.ROW.startswith(ex.MOD.rsplit("/", 1)[1]), ex.ROW)

    def test_mod_table_row_is_named_like_the_folder(self):
        t = self.by_path[ex.MOD + "/TKA_Mod_Table"]
        (row_name, row), = t["rows"].items()
        self.assertEqual(row_name, ex.MOD.rsplit("/", 1)[1])
        self.assertEqual(row["Tables"], [])            # weapon tables are not appended to the game's

    def test_texture_is_generated_next_to_the_manifest(self):
        t = self.by_path[ex.TEX]
        self.assertEqual(t["type"], "texture")
        self.assertTrue(os.path.isfile(os.path.join(self.dir, t["file"])), t["file"])


if __name__ == "__main__": unittest.main()
