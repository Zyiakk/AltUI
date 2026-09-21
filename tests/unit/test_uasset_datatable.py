import unittest, os, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "scripts"))
from uasset_pkg import Package
from uasset_datatable import make_mod_table
import uasset_props


def decode(pkg):
    d = tempfile.mkdtemp(); p = os.path.join(d, "t.uasset"); pkg.save(p)
    return next(iter(uasset_props.dump(p).values()))


class Build(unittest.TestCase):
    def test_mod_table(self):
        pkg = make_mod_table("/Game/Mod/Body_Test", "Body Test", "converted body mod", ["ClothesGroup", "Clothes"], 1.0)
        t = decode(pkg)
        self.assertEqual(t["class"], "DataTable"); self.assertEqual(t["props"]["RowStruct"], "import:DLC_Struct (UserDefinedStruct)")
        row = t["rows"]["Body_Test"]
        self.assertEqual(row["Caption_2_CF40F849410064585CC285AFBAD051F2"], "Body Test")
        self.assertEqual(row["Desc_19_4AD3659040D04182C7F9D9AD8B806911"], "converted body mod")
        self.assertEqual(row["Tables_21_CE3E42574FF40670AE5465BCDC6ABBCB"], ["ClothesGroup", "Clothes"])
        self.assertAlmostEqual(row["Version_22_F42E252047240C6B9DE76395F37B9ED2"], 1.0)
        e = pkg.exports[0]
        self.assertEqual((len(e.deps_ser_before_ser), len(e.deps_create_before_ser), len(e.deps_ser_before_create)), (1, 0, 2))
        self.assertIn("/Game/Mod/Body_Test/TKA_Mod_Table", pkg.names)
        # round trip through reader/writer
        again = Package.from_bytes(*pkg.write()); self.assertEqual(again.write(), pkg.write())


if __name__ == "__main__":
    unittest.main()


class BodyScaleTable(unittest.TestCase):
    def test_row(self):
        import bodyscale_groups as bg
        from uasset_datatable import make_body_scale_table
        defaults = {v: [1.0, 1.0, 1.0] for v, _, _ in bg.GROUPS}; defaults["Breasts"] = [1.3, 1.2, 1.15]
        pkg = make_body_scale_table("/Game/Mod/Body_T", defaults)
        t = decode(pkg); row = t["rows"]["Default"]
        self.assertEqual([round(row[bg.member_internal(0, "Breasts")][k], 3) for k in "xyz"], [1.3, 1.2, 1.15])
        self.assertEqual(len(row), len(bg.GROUPS)); self.assertEqual(row[bg.member_internal(9, "Feet")], {"x": 1.0, "y": 1.0, "z": 1.0})
        # struct import must point at AltUI's struct
        self.assertTrue(any(im.class_name == "UserDefinedStruct" and im.object_name == "S_BodyScale" for im in pkg.imports))
        self.assertTrue(any(im.class_name == "Package" and im.object_name == bg.STRUCT_PATH for im in pkg.imports))
if __name__ == "__main__": unittest.main()
