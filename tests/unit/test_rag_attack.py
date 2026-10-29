"""2026-10-25: attackable ragdolls via an invisible proxy figure (spec docs/superpowers/specs/2026-10-25-ragdoll-attackable-design.md)."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, assets, asset, fn_graph, MGR

RAGDOLL = "/Game/Mod/AltUI/BP_AltUIRagdoll"; S_RAGFIG = "/Game/Mod/AltUI/S_RagFigure"


def by_id(g): return {n["id"]: n for n in g["nodes"]}


class Switch(unittest.TestCase):
    def test_ragdoll_var_and_saved_field(self):
        self.assertIn("Attackable", [v["name"] for v in asset(RAGDOLL)["variables"]])
        st = next(a for a in assets() if a.get("path") == S_RAGFIG)
        self.assertEqual([m["name"] for m in st["members"]][-4:], ["Attackable", "GazeSide", "GazeUp", "HasGaze"])   # appended at the end: the other members keep their internal names (index in it); gaze since 2026-10-26

    def test_human_check(self):
        g = mgr_graph("Rag Is Human"); vals = {n["in"].get("B") for n in g["nodes"] if n.get("function") == "EqualEqual_StrStr"}
        self.assertIn("/Game/Project/Character/Npc/NPC_Female.NPC_Female_C", vals); self.assertIn("/Game/Project/Human/Mercenary.Mercenary_C", vals)

    def test_link_only_for_humans(self):
        g = mgr_graph("Rebuild Ragdolls"); b = by_id(g)
        self.assertEqual(b["hu"]["function"], "Rag Is Human"); self.assertIn(["bhu", "latw_cr", "latsm", "latin", "latad", "bpn"], g["exec"])
        self.assertIn(["bhu:else", "bpn"], g["exec"])

    def test_action_toggles(self):
        b = by_id(mgr_graph("Ragdoll Action"))
        self.assertEqual(b["sat"]["var"], "Attackable"); self.assertEqual(b["sat"]["in"]["Attackable"], "@nat.ReturnValue")

    def test_save_and_load(self):
        self.assertEqual(by_id(mgr_graph("Save Rag Preset"))["mf"]["in"]["Attackable"], "@gAttackable.Attackable")
        self.assertEqual(by_id(mgr_graph("Rag Load Apply"))["sat"]["in"]["Attackable"], "@bf.Attackable")


class Proxy(unittest.TestCase):
    def test_spawn_hidden_undying_attackable(self):
        g = mgr_graph("Rag Proxy Spawn"); b = by_id(g)
        self.assertEqual(b["sp"]["class"], "/Game/Mod/AltUI/BP_AltUIFollower")
        self.assertEqual(b["hid"]["in"]["bNewHidden"], "true"); self.assertEqual(b["dm"]["function"], "DisableMovement")
        self.assertEqual(b["cr"]["in"]["Channel"], "ECC_Pawn"); self.assertEqual(b["cr"]["in"]["NewResponse"], "ECR_Ignore")
        self.assertEqual(b["dmg"]["in"]["bCanBeDamaged"], "true"); self.assertEqual(b["ud"]["var"], "undead time")

    def test_watch_reconciles(self):
        g = mgr_graph("Rag Proxy Watch"); b = by_id(g)
        self.assertEqual(b["spn"]["function"], "Rag Proxy Spawn"); self.assertEqual(b["mv"]["function"], "K2_SetActorLocation")
        self.assertEqual(b["un"]["function"], "UnPossess"); self.assertEqual(b["kill"]["function"], "K2_DestroyActor")
        self.assertIn(["bwant:else", "bhas2", "kill", "rmp"], g["exec"])

    def test_watch_runs_every_tick(self):
        eg = [a["event_graph"] for a in assets() if a.get("path") == MGR and a.get("event_graph")][-1]
        self.assertTrue(any(c[i:i + 3] == ["tfg", "trpw", "tbr"] for c in eg["exec"] for i in range(len(c))))


class Hit(unittest.TestCase):
    def test_jolt_active_or_frozen(self):
        g = fn_graph(RAGDOLL, "Hit Jolt"); b = by_id(g)
        self.assertEqual(b["imp"]["function"], "AddImpulse"); self.assertEqual(b["imp"]["in"]["bVelChange"], "true")
        self.assertEqual(b["snp"]["function"], "SnapshotPose"); self.assertIn(["bac:else", "bha", "br0"], g["exec"])   # a second hit loosens its limb too
        self.assertIn(["bha:else", "snp", "sha", "br0"], g["exec"])   # the pose before the first hit only
        self.assertTrue(any(n.get("function") == "Loosen Below" for n in g["nodes"]))

    def test_back_restores_the_pose(self):
        g = fn_graph(RAGDOLL, "Hit Back"); b = by_id(g)
        self.assertEqual(b["sp"]["function"], "Set Pose"); self.assertEqual(b["sp"]["in"]["snap"], "@ghp.HitPose")
        self.assertEqual(b["off"]["in"]["bSimulate"], "false"); self.assertIn(["entry", "bac", "grv0", "sha0"], g["exec"])   # activated meanwhile: physics stays

    def test_hit_from_the_nearest_zombie(self):
        b = by_id(mgr_graph("Rag Hit"))
        self.assertEqual(b["za"]["in"]["ActorClass"], "/Game/Project/Zombie/Zombie_Base"); self.assertEqual(b["hj"]["function"], "Hit Jolt")

    def test_watch_detects_hits_and_springs_back(self):
        g = mgr_graph("Rag Proxy Watch"); b = by_id(g)
        self.assertEqual(b["hurt"]["in"]["A"], "@php.Health"); self.assertEqual(b["rh"]["function"], "Rag Hit")
        self.assertEqual(b["hb"]["function"], "Hit Back"); self.assertIn(["bhu", "rh", "fill"], g["exec"])


if __name__ == "__main__":
    unittest.main()
