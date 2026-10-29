"""2026-10-24: a follower / NPC figure in a pose via the quick menu (spec docs/superpowers/specs/2026-10-24-npc-pose-design.md).
The figure stays a real character: zombies find it (Character List, bCanBeDamaged, other Character Type) and attack it; the first
hit ends the pose, the AI stays held until "Figure: stop pose"."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, assets, MGR

P_CPB = "/Game/Project/Classes/Character_Player_Base"


def by_id(g): return {n["id"]: n for n in g["nodes"]}


class Stubs(unittest.TestCase):
    def test_cpb_has_out_montage_and_change_action(self):
        parts = [a for a in assets() if a.get("path") == P_CPB]
        self.assertTrue(any("Action Out Montage" in [v["name"] for v in a.get("variables", [])] for a in parts))
        self.assertTrue(any("Change Action Animation" in [f["name"] for f in a.get("functions", [])] for a in parts))


class Pose(unittest.TestCase):
    def test_target_takes_followers_and_npcs(self):
        g = mgr_graph("Fol Pose Target"); b = by_id(g)
        self.assertEqual(b["cand"]["in"]["B"], "@nf.ReturnValue")   # in the world and not fallen - no mode check
        self.assertFalse(any(n.get("function") == "EqualEqual_IntInt" for n in g["nodes"]))
        self.assertIn(["fe:Completed", "return"], g["exec"])

    def test_pose_holds_ai_remembers_and_plays(self):
        g = mgr_graph("Fol Pose"); b = by_id(g)
        self.assertEqual(b["isj"]["in"]["B"], "1")   # KIND_JASON -> notice
        self.assertEqual(b["haun"]["function"], "UnPossess")
        self.assertEqual(b["prow"]["in"]["Value"], "@entry.name"); self.assertEqual(b["prot"]["in"]["Value"], "@rot.ReturnValue")
        self.assertEqual(b["pp"]["function"], "Fol Pose Play")
        self.assertIn(["bpd:else", "haadd", "haun", "prow"], g["exec"]); self.assertIn(["bj:else", "bfa", "bpd", "prow"], g["exec"])
        self.assertIn(["prow", "prot", "padd", "phr", "pp"], g["exec"])

    def test_play_montage_of_the_row(self):
        b = by_id(mgr_graph("Fol Pose Play"))
        self.assertEqual(b["pm"]["function"], "Play Montage"); self.assertEqual(b["pm"]["in"]["AnimMontage"], "@pb.Montage")
        self.assertEqual(b["row"]["in"]["RowName"], "@fr.Value")

    def test_end_stands_up_and_gives_the_ai_back(self):
        g = mgr_graph("Fol Pose End"); b = by_id(g)
        self.assertEqual(b["pom"]["in"]["AnimMontage"], "@gom.Action Out Montage"); self.assertEqual(b["ms"]["function"], "Montage_Stop")
        self.assertEqual(b["caa"]["in"]["Anim"], "None"); self.assertEqual(b["rapo"]["function"], "Possess")
        self.assertEqual(b["od"]["function"], "Fol Order"); self.assertEqual(b["od"]["in"]["order"], "@rb.Order")
        self.assertFalse(any(n.get("var") == "bCanBeDamaged" for n in g["nodes"]))   # the pose does not touch the attackable switch

    def test_watch_poses_again_after_a_hit(self):
        g = mgr_graph("Fol Pose Watch"); b = by_id(g)
        self.assertEqual(b["hurt"]["in"]["A"], "@hp.Health"); self.assertEqual(b["mk"]["in"]["Value"], "@hp.Health")
        self.assertEqual(b["play"]["function"], "IsAnyMontagePlaying"); self.assertEqual(b["pp"]["function"], "Fol Pose Play")
        self.assertIn(["bpl:else", "pp", "rmh"], g["exec"]); self.assertIn(["bpe:else", "srot"], g["exec"])
        self.assertEqual(b["srot"]["in"]["NewRotation"], "@fro.Value")

    def test_watch_and_guard_run_every_tick(self):
        eg = [a["event_graph"] for a in assets() if a.get("path") == MGR and a.get("event_graph")][-1]   # 50_manager_ui.json wins
        b = by_id(eg); self.assertEqual(b["tfpw"]["function"], "Fol Pose Watch"); self.assertEqual(b["tfg"]["function"], "Fol Guard")
        self.assertTrue(any(c[i:i + 5] == ["tns", "tfpw", "tfg", "trpw", "tbr"] for c in eg["exec"] for i in range(len(c))))


class Loop(unittest.TestCase):
    def test_sit_floor_gets_its_loop(self):
        g = mgr_graph("Fol Pose Play"); b = by_id(g)
        self.assertEqual(b["lm0"]["in"]["B"], "/Game/Project/Character/Jodi/Montages/Action/Female_Action_SitFloor_In.Female_Action_SitFloor_In")
        self.assertEqual(b["lca0"]["in"]["Anim"], "@lcl0.AsAnim Sequence"); self.assertEqual(b["lca0"]["in"]["Montage"], "@lco0.AsAnim Montage")
        self.assertIn(["pm", "lb0", "lal0", "lao0", "lca0"], g["exec"]); self.assertIn(["lb0:else", "lcn"], g["exec"])


class Attackable(unittest.TestCase):
    def test_switch_is_bCanBeDamaged_and_saved(self):
        g = mgr_graph("Fol Set Attackable"); b = by_id(g)
        self.assertEqual(b["dmg"]["var"], "bCanBeDamaged"); self.assertEqual(b["dmg"]["in"]["bCanBeDamaged"], "@entry.on")
        self.assertEqual(b["pm"]["in"]["NoAttack"], "@no.ReturnValue")

    def test_spawn_uses_the_switch(self):
        b = by_id(mgr_graph("Fol Spawn")); self.assertEqual(b["ninv"]["in"]["A"], "@rb.NoAttack")
        self.assertEqual(b["dmg"]["in"]["bCanBeDamaged"], "@ninv.ReturnValue"); self.assertEqual(b["jdmg"]["in"]["bCanBeDamaged"], "@ninv.ReturnValue")

    def test_invulnerable_is_undead_not_unattackable(self):
        b = by_id(mgr_graph("Fol Set Invulnerable")); self.assertEqual(b["dmg"]["var"], "undead time")
        g = by_id(mgr_graph("Fol Guard")); self.assertEqual(g["ud"]["var"], "undead time"); self.assertEqual(g["fill"]["in"]["Health"], "@hm.Health Max")

    def test_gear_menu_toggles(self):
        m = by_id(mgr_graph("Fol Menu")); self.assertEqual(m["mi5"]["in"]["action"], "Fol:Attack")
        a = by_id(mgr_graph("Fol Menu Action")); self.assertEqual(a["atk"]["function"], "Fol Set Attackable"); self.assertEqual(a["atk"]["in"]["on"], "@rb.NoAttack")


class Quick(unittest.TestCase):
    def test_run_dispatches(self):
        b = by_id(mgr_graph("Run Quick Item"))
        self.assertEqual(b["fpo"]["function"], "Fol Pose"); self.assertEqual(b["fpo"]["in"]["name"], "@pn.ReturnValue")
        self.assertEqual(b["fps"]["function"], "Fol Pose Stop")

    def test_caption_and_find(self):
        c = by_id(mgr_graph("Quick Item Caption")); self.assertEqual(c["fpc"]["in"]["B"], "@pt2.title")
        f = mgr_graph("Quick Find"); self.assertIn(["qb_folpose", "pe"], f["exec"])

    def test_available_group(self):
        g = mgr_graph("Act Catalog Build")
        self.assertTrue(any(n.get("function") == "Concat_StrStr" and n["in"].get("A") == "folpose:" for n in g["nodes"]))


if __name__ == "__main__":
    unittest.main()
