"""bodybones: where missing bones go into a body mesh's bone list (merged_order against the game mesh, plan_builtin without it)."""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
from bodybones import merged_order, plan_builtin

REF = ["root", "cam", "pelvis", "spine_01", "hand_r", "prop_r", "prop_r1", "prop_r2", "lowerarm_twist_01_r"]


class MergedOrder(unittest.TestCase):
    def test_missing_bones_go_to_their_game_index(self):
        mesh = [b for b in REF if b not in ("cam", "prop_r2")]
        self.assertEqual(merged_order(mesh, REF), REF)

    def test_extra_bones_of_the_body_stay_where_they_are(self):
        mesh = ["root", "pelvis", "spine_01", "hand_r", "hand_l_socket", "prop_r", "prop_r1", "lowerarm_twist_01_r"]
        self.assertEqual(merged_order(mesh, REF), ["root", "cam", "pelvis", "spine_01", "hand_r", "hand_l_socket", "prop_r", "prop_r1", "prop_r2", "lowerarm_twist_01_r"])

    def test_complete_mesh_unchanged(self):
        self.assertEqual(merged_order(list(REF), REF), REF)

    def test_other_order_is_refused(self):
        mesh = ["root", "spine_01", "pelvis", "hand_r", "prop_r", "prop_r1", "lowerarm_twist_01_r"]
        with self.assertRaises(ValueError): merged_order(mesh, REF)


class Builtin(unittest.TestCase):
    def test_cam_and_prop_r2_where_the_game_has_them(self):
        mesh = ["root", "pelvis", "hand_r", "prop_r", "prop_r1", "lowerarm_twist_01_r"]
        order, new = plan_builtin(mesh)
        self.assertEqual(order, ["root", "cam", "pelvis", "hand_r", "prop_r", "prop_r1", "prop_r2", "lowerarm_twist_01_r"])
        self.assertEqual([new[k][:2] for k in ("cam", "prop_r2")], [("Cam", "root"), ("Prop_R2", "hand_r")])
        self.assertTrue(all(len(new[k][3]) == 40 for k in new))   # FTransform as cooked: 10 floats

    def test_nothing_for_a_complete_mesh(self):
        self.assertEqual(plan_builtin(list(REF))[1], {})

    def test_not_without_parent(self):   # a mesh without hand_r gets no Prop_R2
        self.assertEqual(sorted(plan_builtin(["root", "pelvis"])[1]), ["cam"])


if __name__ == "__main__":
    unittest.main()
