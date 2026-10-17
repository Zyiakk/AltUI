"""2026-10-17: the game's untargeted follow / attack order (a sound "NpcOrder" every NPC controller of Jodi hears) made AltUI's NPCs
follow; Fol Npc Guard puts them back to waiting, Fol Sync never takes "follow" into an NPC's record."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph
import followers as fol


def by_id(g): return {n["id"]: n for n in g["nodes"]}


class NpcGuard(unittest.TestCase):
    def test_guard_only_npcs_back_to_stay(self):
        g = mgr_graph("Fol Npc Guard"); b = by_id(g)
        self.assertEqual(b["isn"]["in"]["B"], str(fol.MODE_NPC)); self.assertEqual(b["st"]["function"], "Change Order"); self.assertEqual(b["st"]["in"]["order"], fol.ORDER_STAY)
        self.assertEqual({b["cf"]["in"]["B"], b["ca"]["in"]["B"]}, {fol.ORDER_FOLLOW, "NpcAttack"})
        self.assertIn(["fe", "ix", "bix", "bn", "bok", "ct", "bb", "st"], g["exec"])

    def test_timer_with_the_level(self):
        b = by_id(mgr_graph("Fol Level Start")); self.assertEqual(b["tg"]["in"]["FunctionName"], "Fol Npc Guard")
        self.assertLessEqual(fol.FOL_NPC_GUARD, 0.5)

    def test_sync_keeps_wait_for_npcs(self):
        b = by_id(mgr_graph("Fol Sync")); self.assertEqual(b["cnpc"]["in"]["B"], str(fol.MODE_NPC)); self.assertEqual(b["csel"]["in"]["bPickA"], "@cok.ReturnValue")


if __name__ == "__main__": unittest.main()
