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


class StubWithoutCooked(unittest.TestCase):
    class G:
        tmp = "/nonexistent"
        def dump(self, path): return {"class": {}}
        def var(self, path, n): return None

    def run_compare(self, decl):
        r = {"BROKEN": [], "NOTE": []}
        c.compare("blueprint", "/Game/X/Y", "/nonexistent/cooked/Y", self.G(), decl, r)
        return r["BROKEN"]

    def test_blueprint_without_variables_needs_no_cooked_stub(self):
        self.assertEqual(self.run_compare({"variables": []}), [])
        self.assertEqual(self.run_compare({}), [])

    def test_blueprint_with_variables_without_cooked_stub_checks_the_declaration(self):
        self.assertTrue(any("variable 'A' gone" in b for b in self.run_compare({"variables": [{"name": "A", "type": "int"}]})))


class StubFromDeclaration(unittest.TestCase):
    """Stubs only other mods use (KillingEdge's notify classes) are never cooked by AltUI's build: their variables are checked from the
    declaration in 10_stubs.json against the game's class."""
    class G:
        tmp = "/nonexistent"
        game = {"BoneName": "Name", "DamageScale": "float", "Reset Check State": "bool", "Shake Class": "Class<CameraShakeBase>", "Voice": "SoundBase", "Owner": "Jodi_C"}
        def dump(self, path): return {"class": {}}
        def var(self, path, n): return self.game.get(n)

    def run_compare(self, variables, kind="blueprint"):
        r = {"BROKEN": [], "NOTE": []}
        c.compare(kind, "/Game/X/Y", "/nonexistent/cooked/Y", self.G(), {"variables": variables}, r)
        return r

    def test_declared_types_map_to_the_game_spelling(self):
        self.assertEqual(c.decl_type("name"), "Name"); self.assertEqual(c.decl_type("float"), "float"); self.assertEqual(c.decl_type("bool"), "bool")
        self.assertEqual(c.decl_type("class:/Script/Engine.CameraShakeBase"), "Class<CameraShakeBase>")
        self.assertEqual(c.decl_type("object:/Script/Engine.SoundBase"), "SoundBase")
        self.assertEqual(c.decl_type("object:/Game/Project/Character/Jodi/Jodi"), "Jodi_C")
        self.assertIsNone(c.decl_type("struct:/Script/CoreUObject.Vector"))   # not mapped: only the name is checked

    def test_matching_declaration_is_clean(self):
        r = self.run_compare([{"name": "BoneName", "type": "name"}, {"name": "DamageScale", "type": "float"}, {"name": "Shake Class", "type": "class:/Script/Engine.CameraShakeBase"}])
        self.assertEqual(r["BROKEN"], []); self.assertEqual(r["NOTE"], [])

    def test_wrong_or_missing_variable_is_broken(self):
        self.assertTrue(any("'DamageScale' is float" in b for b in self.run_compare([{"name": "DamageScale", "type": "int"}])["BROKEN"]))
        self.assertTrue(any("'Damage Scale' gone" in b for b in self.run_compare([{"name": "Damage Scale", "type": "float"}])["BROKEN"]))

    def test_object_subclass_is_a_note(self):
        r = self.run_compare([{"name": "Owner", "type": "object:/Game/Project/Character/Jodi/Jodi_Base"}])
        self.assertEqual(r["BROKEN"], []); self.assertEqual(len(r["NOTE"]), 1)

    def test_imported_stub_without_cooked_file_is_broken(self):
        r = {"BROKEN": [], "NOTE": []}
        c.compare("blueprint", "/Game/X/Y", "/nonexistent/cooked/Y", self.G(), {"variables": [{"name": "BoneName", "type": "name"}]}, r, imported={"/Game/X/Y"})
        self.assertEqual(len(r["BROKEN"]), 1); self.assertIn("cooked stub missing", r["BROKEN"][0])

    def test_unimported_stub_without_cooked_file_uses_the_declaration(self):
        r = {"BROKEN": [], "NOTE": []}
        c.compare("blueprint", "/Game/X/Y", "/nonexistent/cooked/Y", self.G(), {"variables": [{"name": "BoneName", "type": "name"}]}, r, imported={"/Game/Other"})
        self.assertEqual(r["BROKEN"], [])

    def test_object_stub_needs_nothing_cooked(self):
        self.assertEqual(self.run_compare([], kind="object_stub")["BROKEN"], [])


if __name__ == "__main__":
    unittest.main()
