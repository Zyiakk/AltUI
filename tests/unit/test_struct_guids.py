"""Struct members of our own structs need stable internal names (Name_idx_GUID): SaveGame data is matched by name + GUID,
a random GUID per build (FStructureEditorUtils::AddVariable) emptied AltUI_Looks.sav after every rebuild (2026-09-15)."""
import unittest, os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
from bpdsl import struct, param


class StructGuids(unittest.TestCase):
    def test_deterministic_internal_names(self):
        a = struct("/Game/Mod/X/S_A", [param("Name", "string"), param("Id", "int")])
        b = struct("/Game/Mod/X/S_A", [param("Name", "string"), param("Id", "int")])
        self.assertEqual([m["internal_name"] for m in a["members"]], [m["internal_name"] for m in b["members"]])
        for i, m in enumerate(a["members"]):
            self.assertRegex(m["internal_name"], r"^%s_%d_[0-9A-F]{32}$" % (m["name"], 2 + 2 * i))

    def test_depends_on_path_and_name(self):
        a = struct("/Game/Mod/X/S_A", [param("Name", "string")]); b = struct("/Game/Mod/X/S_B", [param("Name", "string")])
        self.assertNotEqual(a["members"][0]["internal_name"], b["members"][0]["internal_name"])

    def test_explicit_internal_name_kept(self):
        a = struct("/Game/P/S", [param("clothes", "name", "map", value_type="struct:/Script/CoreUObject.Color", internal_name="clothes_5_E1AD9C5C4635FD04BF2E71A226121A33")])
        self.assertEqual(a["members"][0]["internal_name"], "clothes_5_E1AD9C5C4635FD04BF2E71A226121A33")


if __name__ == "__main__": unittest.main()
