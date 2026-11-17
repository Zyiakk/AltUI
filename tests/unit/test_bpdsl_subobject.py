import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
import bpdsl as b


class SubobjectDslTest(unittest.TestCase):
    def test_entry(self):
        d = b.subobject_defaults("/Game/X/BP", "CharacterMovement", MaxWalkSpeed=300.0, bOrientRotationToMovement=True, RotationRate="(Pitch=0,Yaw=420,Roll=0)")
        self.assertEqual(d, {"type": "subobject_defaults", "path": "/Game/X/BP", "component": "CharacterMovement",
                             "properties": {"MaxWalkSpeed": 300.0, "bOrientRotationToMovement": True, "RotationRate": "(Pitch=0,Yaw=420,Roll=0)"}})

    def test_refusals(self):
        with self.assertRaisesRegex(ValueError, "no properties"): b.subobject_defaults("/Game/X/BP", "Mesh")
        with self.assertRaisesRegex(ValueError, "component"): b.subobject_defaults("/Game/X/BP", "", A=1)
        with self.assertRaisesRegex(ValueError, "value"): b.subobject_defaults("/Game/X/BP", "Mesh", A=[1])


if __name__ == "__main__":
    unittest.main()
