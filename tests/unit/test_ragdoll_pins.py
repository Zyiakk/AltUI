"""2026-10-17 (spec 2026-10-17-ragdoll-festhalten-design): ragdoll parts pinned in the air, joint markers, poses keep joint states."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, fn_graph, asset
RAG = "/Game/Mod/AltUI/BP_AltUIRagdoll"


def by_id(g): return {n["id"]: n for n in g["nodes"]}
def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]
def rag(name): return fn_graph(RAG, name)


class Pins(unittest.TestCase):
    def test_pin_is_a_world_constraint_locked_on_all_axes(self):
        g = rag("Make Pin"); b = by_id(g)
        self.assertEqual(b["scc"]["in"]["Component2"], "None"); self.assertEqual(b["scc"]["in"]["BoneName1"], "@entry.bone")
        for k in ("lx", "ly", "lz"): self.assertEqual(b[k]["in"]["ConstraintType"], "LCM_Locked")
        for k in ("s1", "s2", "tw"): self.assertIn("ACM_Locked", b[k]["in"].values())

    def test_freeze_keeps_the_names(self):
        self.assertTrue(calls(rag("Freeze"), "Clear Pins"))
        self.assertFalse(calls(rag("Clear Pins"), "Array_Clear"))   # Pinned stays, only the constraints go

    def test_activate_makes_them_again(self):
        g = rag("Activate"); self.assertTrue(calls(g, "Make Pin"))
        self.assertEqual(by_id(g)["gpn"]["var"], "Pinned")

    def test_unpin_all_forgets_them(self):
        g = rag("Unpin All"); self.assertTrue(calls(g, "Clear Pins")); self.assertTrue(calls(g, "Array_Clear"))


class Markers(unittest.TestCase):
    def test_every_grabbable_body_gets_one(self):
        import gen_ragdoll as gr
        self.assertEqual(gr.MARKER_BONES[0], "pelvis"); self.assertEqual(len(gr.MARKER_BONES), 18)

    def test_one_sphere_with_our_marker_material(self):
        """ui-test-116: core + hull showed only the hull (the core sits inside its limb); one sphere, M_JointMarker fades it by depth."""
        g = rag("Build Markers"); self.assertEqual({n["in"].get("Material") for n in calls(g, "SetMaterial")}, {"/Game/Mod/AltUI/Mat/M_JointMarker"})
        self.assertEqual(len(calls(g, "AddComponentByClass")), 1)
        self.assertTrue(all(n["in"]["NewMesh"] == "/Engine/BasicShapes/Sphere" for n in calls(g, "SetStaticMesh")))
        self.assertTrue(all(n["in"]["Channel"] == "ECC_Destructible" for n in calls(g, "SetCollisionObjectType")))
        self.assertTrue(all(n["in"]["NewCastShadow"] == "false" for n in calls(g, "SetCastShadow")))
        src = open(os.path.join(H, "..", "..", "scripts", "quickmenu", "material.py")).read()
        self.assertIn("disable_depth_test", src); self.assertIn("MaterialExpressionSceneDepth", src)

    def test_depth_band_per_body_part(self):
        """ui-test-116 round 2: one band for all - torso spheres never pale, far ones barely. Near = the part's thickness."""
        import gen_ragdoll as gr
        self.assertEqual(set(gr.MARK_NEAR), set(gr.MARKER_BONES)); self.assertGreater(gr.MARK_NEAR["spine_02"], gr.MARK_NEAR["hand_l"])
        pars = {n["in"]["ParameterName"] for n in calls(rag("Build Markers"), "SetScalarParameterValue")}; self.assertEqual(pars, {"Near", "Far", "Pale"})

    def test_hidden_markers_catch_no_click(self):
        g = rag("Show Markers"); b = by_id(g); self.assertEqual(b["bon"]["in"]["Condition"], "@entry.on")
        self.assertEqual(b["cq"]["in"]["NewType"], "QueryOnly"); self.assertEqual(b["cn"]["in"]["NewType"], "NoCollision")

    def test_colour_order(self):
        b = by_id(rag("Refresh Markers"))
        self.assertEqual(b["c3"]["in"]["bPickA"], "@ip.ReturnValue")   # pinned wins over locked over loose

    def test_state_changes_recolour(self):
        for f in ("Toggle Joint", "Toggle Loose", "Pin", "Unpin", "Unpin All", "Set Joint States"):
            self.assertTrue(calls(rag(f), "Refresh Markers"), f)


class Data(unittest.TestCase):
    def test_fields(self):
        import gen_manager as gm
        self.assertIn("Pinned", [m["name"] for m in asset(gm.S_RAGFIG)["members"]])
        self.assertLessEqual({"Locked", "Loose", "HasJoints"}, {m["name"] for m in asset(gm.S_RAGPOSE)["members"]})
        self.assertIn(("RagMarkersOff", "RagMarkersOff", "copy", None), gm.SETTINGS)

    def test_texts_in_all_languages(self):
        import strings
        for k in ("Rag_Pinned", "Rag_UnpinAll", "Rag_MarkersOn", "Rag_MarkersOff"):
            self.assertEqual(len(strings.STRINGS[k]), 7, k)


class Grab(unittest.TestCase):
    def test_spheres_first(self):
        g = mgr_graph("Rag Pick"); b = by_id(g)
        self.assertEqual(b["hrs"]["function"], "GetHitResultUnderCursorForObjects")
        self.assertEqual(b["ot"]["in"]["[0]"], "ObjectTypeQuery6")
        self.assertTrue(calls(mgr_graph("Begin Jodi Drag"), "Rag Pick"))

    def test_grab_unpins_and_remembers(self):
        g = mgr_graph("Begin Jodi Drag"); self.assertTrue(calls(g, "Unpin"))
        sets = {n.get("var") for n in g["nodes"] if n.get("kind") == "set"}; self.assertLessEqual({"RagGrabActor", "RagGrabBone"}, sets)

    def test_right_click_while_grabbing_pins(self):
        g = mgr_graph("Rag Pin Grab"); self.assertTrue(calls(g, "ReleaseComponent")); self.assertTrue(calls(g, "Pin"))
        self.assertTrue(calls(mgr_graph("Ragdoll Mode Step"), "Rag Pin Grab"))
        import gen_widgets as gw
        self.assertIn("Rag Pin Grab", open(gw.__file__).read())

    def test_panel_checks_the_grab_before_the_hover(self):
        """ui-test-116 log: during the drag the panel holds the mouse - the catcher is not hovered when the right button comes."""
        g = fn_graph("/Game/Mod/AltUI/W_AltUI", "OnMouseButtonDown")
        self.assertTrue(any("bpg" in c and "bh" not in c[:c.index("bpg")] for c in g["exec"]))
        self.assertIn(["bpg:else", "bh", "bd", "bj", "return"], g["exec"])


class Visibility(unittest.TestCase):
    def test_apply_at_every_switch(self):
        for f in ("Select Page", "Open Panel", "Close Panel", "Start Ragdoll Mode", "Stop Free Cam", "Start Free Cam", "Start Photo Mode", "End Photo Mode", "Rag Refresh", "Toggle Rag Markers"):
            self.assertTrue(calls(mgr_graph(f), "Apply Rag Markers"), f)
        self.assertTrue(calls(mgr_graph("Apply Rag Markers"), "Show Markers"))

    def test_status_bar_and_header(self):
        g = mgr_graph("Rebuild Status"); acts = {n["in"].get("action") for n in calls(g, "Init")}
        self.assertLessEqual({"RagMarkers", "RagRemoveAll"}, acts)
        self.assertNotIn("RagRemoveAll", str(mgr_graph("Rebuild Ragdolls")))
        self.assertIn("Rag_UnpinAll", str(mgr_graph("Rebuild Ragdolls")))


class Saves(unittest.TestCase):
    def test_scene_keeps_pins(self):
        self.assertIn("Pinned", next(n for n in mgr_graph("Save Rag Preset")["nodes"] if n.get("struct", "").endswith("S_RagFigure"))["in"])
        self.assertTrue(any(n.get("var") == "Pinned" for n in mgr_graph("Rag Load Apply")["nodes"] if n.get("kind") == "set"))

    def test_pose_keeps_joint_states(self):
        mk = next(n for n in mgr_graph("Save Rag Pose")["nodes"] if n.get("struct", "").endswith("S_RagPose"))["in"]
        self.assertEqual(mk["HasJoints"], "true"); self.assertIn("Locked", mk); self.assertIn("Loose", mk)
        g = mgr_graph("Load Rag Pose"); self.assertTrue(calls(g, "Set Joint States")); self.assertEqual(by_id(g)["bhj"]["in"]["Condition"], "@bp.HasJoints")

    def test_store_keeps_joint_states(self):
        """ui-test-116 #15: Store Rag Pose made the struct again from its fields - without the joint states (HasJoints false)."""
        mk = by_id(mgr_graph("Store Rag Pose"))["mp"]["in"]
        self.assertEqual(mk.get("HasJoints"), "@bi.HasJoints"); self.assertEqual(mk.get("Locked"), "@bi.Locked"); self.assertEqual(mk.get("Loose"), "@bi.Loose")


if __name__ == "__main__":
    unittest.main()
