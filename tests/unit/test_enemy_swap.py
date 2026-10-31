"""2026-10-31: E on a living look enemy opened the game's swap dialog (Jodi.Send NPC Order asks nothing of the NPC); Fol Watch (every
FOL_WATCH s while the dialog is shown) closes it through Enemy Swap Guard as Esc does; a dead enemy can be looted."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, assets

P_INVNPC = "/Game/Project/UserInterface/Widgets/InventoryNpc"


def by_id(g): return {n["id"]: n for n in g["nodes"]}


class EnemySwap(unittest.TestCase):
    def test_watch_calls_the_guard_while_the_dialog_is_shown(self):
        g = mgr_graph("Fol Watch"); b = by_id(g)
        self.assertEqual(b["esg"]["function"], "Enemy Swap Guard"); self.assertEqual(b["esg"]["in"]["dlg"], "@gin.InventoryNpc")
        self.assertIn(["entry", "bvi", "bop", "esg", "b", "ks", "fe"], g["exec"])

    def test_guard_closes_only_on_a_living_enemy(self):
        g = mgr_graph("Enemy Swap Guard"); b = by_id(g)
        self.assertIn("@gie.IsEnemy", json.dumps(b["bie"]))
        self.assertEqual(b["al"]["in"]["A"], "@ghp.Health"); self.assertEqual(b["cl"]["function"], "Click Button")
        self.assertIn(["entry", "cf", "bie", "bal", "cl", "pn"], g["exec"])
        self.assertFalse(any(c[0] in ("bie:else", "bal:else") for c in g["exec"]))   # not an enemy / dead: the dialog stays

    def test_stub_has_npc_and_close_button(self):
        names = {v["name"] for a in assets() if a.get("path") == P_INVNPC for v in a.get("variables", [])}
        self.assertLessEqual({"Npc", "ImageButton_Close"}, names)

    def test_notice_in_all_languages(self):
        import strings
        self.assertEqual(len(strings.STRINGS["En_NoSwap"]), 7)


if __name__ == "__main__":
    unittest.main()
