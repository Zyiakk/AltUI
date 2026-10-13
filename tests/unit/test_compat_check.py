"""compat_check: which parameter / member type differences break AltUI's calls and which do not."""
import unittest, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
import compat_check as c


class SameKind(unittest.TestCase):
    def test_primitives_must_match(self):
        self.assertTrue(c.same_kind("Name", "Name")); self.assertFalse(c.same_kind("Name", "String")); self.assertFalse(c.same_kind("float", "int"))

    def test_object_subclass_passes(self):
        self.assertTrue(c.same_kind("Jodi_Base_C", "Jodi_C")); self.assertTrue(c.same_kind("-> Clothes_Comp_C", "-> SkeletalMeshComponent"))

    def test_containers_keep_their_kind(self):
        self.assertTrue(c.same_kind("Array<Name>", "Array<Name>")); self.assertFalse(c.same_kind("Array<Name>", "Set<Name>"))

    def test_ptypes_drops_ref_marks(self):
        f = {"params": ["const& clothes: Name", "out damage: float"], "ret": None}
        g = {"params": ["ref clothes: Name", "out damage: float"], "ret": None}
        self.assertEqual(c.ptypes(f), c.ptypes(g))


if __name__ == "__main__":
    unittest.main()
