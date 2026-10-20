"""2026-10-20 (spec 2026-10-20-ragdoll-glied-drehen-design): right drag below a loose joint turns that limb about the joint, the
wheel twists it; the turn goes into the held pose."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, fn_graph
RAG = "/Game/Mod/AltUI/BP_AltUIRagdoll"


def by_id(g): return {n["id"]: n for n in g["nodes"]}
def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]


class Turn(unittest.TestCase):
    def test_right_drag_turns_the_loose_root(self):
        b = by_id(mgr_graph("Begin Jodi Drag"))
        self.assertEqual(b["tbt"]["function"], "Begin Turn"); self.assertEqual(b["tbt"]["in"]["bone"], "@tlr.root")
        self.assertEqual(b["tbt"]["in"]["point"], "@gpkp.RagPickPoint")

    def test_drag_and_wheel(self):
        self.assertTrue(calls(mgr_graph("Jodi Drag"), "Rag Turn Update"))
        self.assertTrue(calls(mgr_graph("Rag Turn Update"), "Turn Toward"))
        self.assertTrue(calls(mgr_graph("Rag Lift"), "Twist"))
        self.assertTrue([n for n in mgr_graph("End Jodi Drag")["nodes"] if n.get("var") == "RagTurn"])

    def test_turn_goes_into_the_held_pose(self):
        g = fn_graph(RAG, "Apply Turn"); self.assertTrue(calls(g, "Set Pose")); self.assertTrue(calls(g, "Turn Local"))
        self.assertTrue(calls(fn_graph(RAG, "Begin Turn"), "SnapshotPose"))


if __name__ == "__main__": unittest.main()
