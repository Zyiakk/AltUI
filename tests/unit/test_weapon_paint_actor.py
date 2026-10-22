"""A stored game paint must survive a new weapon actor, and a spray paint must survive the storage box.

Sync Weapon Paint took any difference between the weapon's Gun Data.PaintName and AppliedPaint for a repaint by the game.
A new actor (picked up from the shooting range wall after a restart) brings the wall gun's unpainted Gun Data, and the
chosen paint was deleted on every new match (Discord 2026-10-21). Now only the actor dressed last can have been repainted;
Poll Weapons takes a spray paint over at once, so the box (new actor on the way out) cannot lose it either."""
import unittest
from test_weapon_look_melee import function


def nodes(g): return {x["id"]: x for x in g["nodes"]}


class WeaponPaintActor(unittest.TestCase):
    def test_dress_weapon_reads_the_old_actor_before_overwriting_it(self):
        g = function("Dress Weapon"); n = nodes(g)
        self.assertEqual(n["fwa0"]["in"]["TargetMap"], "@gwa0.WeaponActors")
        self.assertEqual(n["same0"]["in"], {"A": "@fwa0.Value", "B": "@fw.Value"})
        self.assertTrue(any(c[c.index("pss") + 1] == "wsa" for c in g["exec"] if "pss" in c))
        self.assertEqual(n["swp"]["in"]["same"], "@gpss.PaintSameActor")

    def test_repaint_counts_only_on_the_same_actor(self):
        n = nodes(function("Sync Weapon Paint"))
        self.assertEqual(n["kch"]["in"], {"A": "@kch0.ReturnValue", "B": "@entry.same"})
        self.assertEqual(n["u2"]["in"], {"A": "@nfs.ReturnValue", "B": "@pn.ReturnValue"})   # no own choice: any actor's paint

    def test_poll_takes_a_spray_paint_over_at_once(self):
        g = function("Poll Weapons"); n = nodes(g)
        self.assertIn(["b:else", "snd", "pcg", "pb", "pap"], g["exec"])
        self.assertEqual(n["pne"]["in"], {"A": "@pbd.PaintName", "B": "@pfa.Value"})
        self.assertEqual(n["pap"]["function"], "Apply Weapon Look")


if __name__ == "__main__": unittest.main()
