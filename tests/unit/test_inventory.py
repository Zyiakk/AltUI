import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "assets", "gen"))
import inventory as inv


class InventoryData(unittest.TestCase):
    def test_groups(self):
        self.assertEqual(inv.INV_GROUPS, ["Weapon", "Ammo", "Equipment", "Tool"])

    def test_kind(self):
        self.assertEqual(inv.kind_of(3, 2), "gun"); self.assertEqual(inv.kind_of(3, 0), "weapon"); self.assertEqual(inv.kind_of(3, 16), "weapon")
        self.assertEqual(inv.kind_of(4, 0), "ammo"); self.assertEqual(inv.kind_of(0, 4), "usable"); self.assertEqual(inv.kind_of(5, 0), "usable")
        self.assertEqual(inv.kind_of(1, 0), "other"); self.assertEqual(inv.kind_of(2, 0), "other")

    def test_left(self):
        self.assertEqual(inv.left_action("bag"), "Store1"); self.assertEqual(inv.left_action("box"), "Take1")

    def test_menus(self):
        self.assertEqual(inv.menu("bag", "gun"), ["Use", "Check", "Drop1", "Shortcut1", "Shortcut2", "Unload", "Attach"])
        self.assertEqual(inv.menu("bag", "ammo"), ["Check", "StoreHalf", "StoreAll", "Drop1", "DropAll"])
        self.assertEqual(inv.menu("bag", "usable"), ["Use", "Check", "StoreHalf", "StoreAll", "Drop1", "DropAll", "Shortcut1", "Shortcut2"])
        self.assertEqual(inv.menu("box", "ammo"), ["TakeHalf", "TakeAll", "Check"])
        self.assertEqual(inv.menu("box", "gun"), ["Check"])

    def test_catalog(self):
        self.assertEqual(inv.left_action("cat"), "CatBag1")
        self.assertEqual(inv.menu("cat", "ammo"), ["CatBag1", "CatBag5", "CatBox1", "CatBox5", "Check"])
        self.assertEqual(inv.menu("cat", "gun"), ["CatBag1", "Check"])
        self.assertEqual(inv.menu("cat", "collect"), ["CatBag1", "CatBag5", "Check"])
        self.assertEqual(inv.CAT_GROUP, "Collect")

    def test_actions_known(self):
        for b, kinds in (("bag", inv.KINDS), ("box", inv.KINDS), ("cat", inv.KINDS + ["collect"])):
            for k in kinds:
                self.assertTrue(set(inv.menu(b, k)) <= set(inv.ACTIONS), (b, k))


if __name__ == "__main__":
    unittest.main()
