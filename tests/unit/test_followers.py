"""followers.py: when a figure comes on a level start, where it comes, which status line it shows (spec 2026-10-09)."""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "gen"))
import followers as f

F, N, FOL, STAY = f.MODE_FOLLOWER, f.MODE_NPC, f.ORDER_FOLLOW, f.ORDER_STAY


class LevelStart(unittest.TestCase):
    def test_following_follower_comes_everywhere(self):
        self.assertTrue(f.comes_on_level_start(True, False, F, FOL, "Lv1", "Lv2"))

    def test_waiting_follower_and_npc_only_in_their_level(self):
        for mode, order in ((F, STAY), (N, STAY)):
            self.assertTrue(f.comes_on_level_start(True, False, mode, order, "Lv1", "Lv1"))
            self.assertFalse(f.comes_on_level_start(True, False, mode, order, "Lv1", "Lv2"))

    def test_inactive_and_fallen_never(self):
        self.assertFalse(f.comes_on_level_start(False, False, F, FOL, "Lv1", "Lv1"))
        self.assertFalse(f.comes_on_level_start(True, True, F, FOL, "Lv1", "Lv1"))


class Place(unittest.TestCase):
    def test_follower_that_follows_comes_to_jodi(self):
        self.assertFalse(f.spawn_at_place(F, FOL, "Lv1", "Lv1"))

    def test_others_at_their_place_in_their_level(self):
        self.assertTrue(f.spawn_at_place(F, STAY, "Lv1", "Lv1"))
        self.assertTrue(f.spawn_at_place(N, STAY, "Lv1", "Lv1"))

    def test_other_level_to_jodi(self):   # activated / revived elsewhere: in front of Jodi
        self.assertFalse(f.spawn_at_place(N, STAY, "Lv1", "Lv2"))


class State(unittest.TestCase):
    def test_order(self):
        self.assertEqual(f.state_key(F, FOL, True, False), f.STATE_FOLLOWS)
        self.assertEqual(f.state_key(F, STAY, True, False), f.STATE_WAITS)
        self.assertEqual(f.state_key(N, STAY, True, False), f.STATE_NPC)
        self.assertEqual(f.state_key(F, FOL, False, False), f.STATE_INACTIVE)
        self.assertEqual(f.state_key(F, FOL, False, True), f.STATE_FALLEN)


class Clothes(unittest.TestCase):
    def test_old_record_has_no_clothes_worn_or_hair(self):
        self.assertTrue(f.is_old_record([], [], ""))
        self.assertFalse(f.is_old_record(["Top01"], ["Top01"], ""))
        self.assertFalse(f.is_old_record([], [], "Hair03"))   # a look without clothes is no old record

    def test_back_to_jodi_unless_she_has_it(self):
        self.assertTrue(f.back_to_jodi("Top01", ["Pants02"]))
        self.assertFalse(f.back_to_jodi("Top01", ["Top01", "Pants02"]))   # the wardrobe keeps it anyway

    def test_relook_returns_what_the_new_look_lacks(self):
        self.assertEqual(f.relook_returns(["Top01", "Pants02", "Boots03"], ["Pants02", "Dress05"]), ["Top01", "Boots03"])

    def test_slot_keys_of_one_piece(self):
        keys = ["Top01#0", "Top01#2", "Top011#0", "Pants02#1"]
        self.assertEqual(f.slot_keys_of("Top01", keys), ["Top01#0", "Top01#2"])

    def test_new_pieces(self):
        self.assertEqual(f.new_pieces(["Top01"], ["Top01", "Hat04"]), ["Hat04"])

    def test_tile_prefixes_do_not_collide(self):
        self.assertFalse(f.TILE_FOL_CLOTHES.startswith("fol:"))   # fol_tile_parse tests "fol:"
        self.assertNotEqual(f.TILE_BAG_CLOTHES.split(":")[0], "bag")   # Inv Tile Parse's backpack tiles are "bag:<item>"


if __name__ == "__main__":
    unittest.main()
