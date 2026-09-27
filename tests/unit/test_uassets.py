import unittest, os, sys, re
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, "..", "..")
sys.path.insert(0, os.path.join(W, "scripts"))
import bodyscale_groups as bg
import weapon_skins as ws

U = os.path.join(W, "uassets")
REF = rb"/Game/[\w/.]+"


def read(name):
    return open(os.path.join(U, name), "rb").read()


class ShippedUassets(unittest.TestCase):
    """uassets/ holds editor copies of generated assets so mods can be built against them in the editor: two for
    bodies, two for weapons. Every bpgen run rewrites them with a fresh package GUID, so the copies are checked by
    content, never by bytes."""

    def test_struct_members(self):
        b = read("S_BodyScale.uasset")
        self.assertEqual(set(m.decode() for m in re.findall(rb"\w+_\d+_[0-9A-F]{32}", b)),
                         set(n for _, n in bg.struct_members()))
        self.assertIn(b"UserDefinedStructEditorData", b)   # an editor asset, not a cooked one

    def test_struct_references_nothing_but_itself(self):
        # modders drop the file into their own project: a reference to game content would make it unopenable there
        self.assertEqual(set(re.findall(REF, read("S_BodyScale.uasset"))), {bg.STRUCT_PATH.encode()})

    def test_abp_variables_and_bones(self):
        b = read("ABP_BodyScale.uasset")
        for v in [v for v, _, _ in bg.GROUPS] + [v for v, _ in bg.SHIFTS]:
            self.assertIn(v.encode(), b, v)
        for bone in set(sum([bs for _, bs, _ in bg.GROUPS], []) + sum([bs for _, bs in bg.SHIFTS], [])):
            self.assertIn(bone.encode(), b, bone)

    def test_abp_references_only_the_skeleton(self):
        refs = set(re.findall(REF, read("ABP_BodyScale.uasset")))
        self.assertIn(b"/Game/Project/Character/Jodi/Body/Female_Skeleton", refs)   # from the kit, the modder has it
        self.assertEqual([r for r in refs if not r.startswith((b"/Game/Project/", bg.ABP_PATH.encode()))], [])

    def test_weapon_struct_members(self):
        for name, members in (("S_WeaponSkin.uasset", ws.struct_members()),
                              ("S_WeaponModel.uasset", ws.model_struct_members())):
            b = read(name)
            self.assertEqual(set(m.decode() for m in re.findall(rb"\w+_\d+_[0-9A-F]{32}", b)),
                             set(n for _, n, _ in members), name)
            self.assertIn(b"UserDefinedStructEditorData", b, name)   # an editor asset, not a cooked one

    def test_weapon_structs_reference_nothing_but_themselves(self):
        # a modder drops the file into their own project: a reference to game content would make it unopenable there
        for name, path in (("S_WeaponSkin.uasset", ws.STRUCT_PATH),
                           ("S_WeaponModel.uasset", ws.MODEL_STRUCT_PATH)):
            self.assertEqual(set(re.findall(REF, read(name))), {path.encode()}, name)


if __name__ == "__main__": unittest.main()
