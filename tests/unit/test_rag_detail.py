"""Ragdoll fingers and eyes (docs/specs/2026-10-26-ragdoll-finger-augen-design.md): data, figure, manager, tab, saving."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
import cfg
import rag_detail as rd


class Data(unittest.TestCase):
    def test_bones(self):
        self.assertEqual(len(rd.FINGER_BONES), 30); self.assertEqual(rd.FINGER_BONES[0], "thumb_01_l"); self.assertEqual(rd.FINGER_BONES[15], "thumb_01_r")
        self.assertEqual(rd.FINGER_BONES[1 * 15 + 4 * 3 + 2], "pinky_03_r")
        self.assertEqual(rd.DETAIL_BONES, rd.FINGER_BONES + ["Eye_L", "Eye_R"])
        self.assertEqual({rd.DETAIL_GROUP[b] for b in rd.FINGER_BONES[:15]}, {0}); self.assertEqual({rd.DETAIL_GROUP[b] for b in rd.FINGER_BONES[15:]}, {1})
        self.assertEqual(rd.DETAIL_GROUP["Eye_L"], 2)

    def test_ref_for_every_bone(self):
        self.assertEqual(set(rd.REF_ROT), set(rd.DETAIL_BONES))
        for s in ("thumb_01", "index_02", "pinky_03"):   # left and right share their local rotations (measured)
            for a, b in zip(rd.REF_ROT[s + "_l"], rd.REF_ROT[s + "_r"]): self.assertAlmostEqual(a, b, delta=0.05)

    def test_axes_and_angles(self):
        self.assertEqual(rd.curl_axis("index_02_l"), rd.CURL_AXIS); self.assertEqual(rd.curl_axis("thumb_01_r"), rd.THUMB1_AXIS)
        self.assertEqual(rd.curl_axis("thumb_03_l"), rd.CURL_AXIS)
        self.assertGreater(rd.curl_deg("middle_02_l"), 80); self.assertEqual(rd.spread_deg("thumb_01_l"), rd.SPREAD_DEG); self.assertEqual(rd.spread_deg("index_01_l"), 0.0)
        self.assertEqual(rd.LID_DEG, 40.0); self.assertEqual(set(rd.LID_AXIS), {"Eye_L", "Eye_R"})

    def test_hand_poses(self):
        names = [n for n, _ in rd.HAND_POSES]
        self.assertEqual(names, ["Open", "Relaxed", "Fist", "ThumbsUp", "Peace", "Point", "Hold", "Base"])
        self.assertLessEqual(len(names), 10)   # RagHand:<figure*100 + side*10 + pose>
        for n, v in rd.HAND_POSES:
            self.assertEqual(len(v), 6, n); self.assertTrue(all(0.0 <= x <= 1.0 for x in v), n)
        p = dict(rd.HAND_POSES); self.assertEqual(p["Base"], (0, 0, 0, 0, 0, 0)); self.assertEqual(p["Fist"][:5], (1, 1, 1, 1, 1))
        self.assertEqual(p["ThumbsUp"][:5], (0, 1, 1, 1, 1))

    def test_literals(self):
        self.assertEqual(rd.rot_lit((1.5, -2.0, 3.0)), "(Pitch=1.5,Yaw=-2.0,Roll=3.0)"); self.assertEqual(rd.vec_lit((0.0, 0.0, -1.0)), "(X=0.0,Y=0.0,Z=-1.0)")

    def test_measured_ref_matches_the_game(self):
        """The table equals what scripts/rag_detail_measure.py reads from the game's mesh (skipped without the game)."""
        sys.path.insert(0, os.path.join(H, "..", "..", "scripts"))
        import rag_detail_measure as m
        try: got = m.ref_rotators()
        except FileNotFoundError as e: self.skipTest(str(e))
        for b in rd.DETAIL_BONES:
            for a, c in zip(rd.REF_ROT[b], got[b]): self.assertAlmostEqual(a, c, delta=0.01, msg=b)


import gen_ragdoll


def rag_bp():
    return next(a for a in gen_ragdoll.build() if a.get("path") == gen_ragdoll.RAGDOLL)


def rag_fn(name):
    return next(f for f in rag_bp()["functions"] if f["name"] == name)


class Markers(unittest.TestCase):
    def test_functions(self):
        names = {f["name"] for f in rag_bp()["functions"]}
        self.assertLessEqual({"Has Detail", "Detail Kind", "Finger Of", "Finger Tip Base", "Build Detail Markers", "Show Details", "Detail Tick"}, names)
        for n in ("Has Detail", "Detail Kind", "Finger Of", "Finger Tip Base"): self.assertTrue(rag_fn(n).get("pure"), n)

    def test_vars(self):
        v = {x["name"] for x in rag_bp()["variables"]}
        self.assertLessEqual({"DetailBones", "Details", "DetailMids", "DetailGroup", "DetailBuilt", "DetailHold"}, v)

    def test_has_detail_needs_jodis_skeleton(self):
        js = json.dumps(rag_fn("Has Detail")); self.assertIn("Eye_L", js); self.assertIn("index_01_l", js)

    def test_build_uses_own_arrays(self):
        js = json.dumps(rag_fn("Build Detail Markers"))
        self.assertIn("DetailMids", js); self.assertNotIn("\"MarkerMids\"", js); self.assertIn("pinky_03_r", js); self.assertIn("Eye_R", js)

    def test_tick_by_camera_distance(self):
        js = json.dumps(rag_fn("Detail Tick"))
        for s in ("GetCameraLocation", "hand_l", "hand_r", "head", str(gen_ragdoll.DETAIL_NEAR), "DetailHold", "\"Active\""): self.assertIn(s, js)

    def test_show_markers_shows_details(self):
        self.assertIn("Show Details", json.dumps(rag_fn("Show Markers")))
        js = json.dumps(rag_fn("Show Details")); self.assertIn("K2_SetTimer", js); self.assertIn("K2_ClearTimer", js); self.assertIn("Detail Tick", js)


class Pose(unittest.TestCase):
    def test_functions(self):
        names = {f["name"] for f in rag_bp()["functions"]}
        need = {"Detail Begin", "Detail Put", "Detail Commit", "Curl Rot", "Lid Rot", "Curl Finger", "Finger Curl Of", "Apply Hand Pose", "Apply Lids",
                "Eye Lids Step", "Gaze From Target", "Set Gaze", "Look At", "Reset Eyes"}
        self.assertLessEqual(need, names)
        for n in ("Curl Rot", "Lid Rot", "Finger Curl Of", "Gaze From Target"): self.assertTrue(rag_fn(n).get("pure"), n)

    def test_compose_order(self):
        """Curl in the bone's space (A = delta, B = ref), lid in the parent's space (A = ref, B = delta)."""
        cr = rag_fn("Curl Rot")["graph"]["nodes"]; c = next(n for n in cr if n.get("function") == "ComposeRotators")
        self.assertEqual(c["in"]["B"], "@entry.ref"); self.assertTrue(c["in"]["A"].startswith("@d."))
        lr = rag_fn("Lid Rot")["graph"]["nodes"]; c = next(n for n in lr if n.get("function") == "ComposeRotators")
        self.assertEqual(c["in"]["A"], "@entry.ref"); self.assertTrue(c["in"]["B"].startswith("@d."))

    def test_curl_finger_uses_the_tables(self):
        js = json.dumps(rag_fn("Curl Finger"))
        for s in ("Detail Put", "Curl Rot", "ThumbSpread", rd.vec_lit(rd.THUMB1_AXIS)): self.assertIn(s, js)
        # base pose as MakeRotator nodes: a "(Pitch=..)" literal cooks as zero (bytecode check 2026-10-26)
        mr = [n for n in rag_fn("Curl Finger")["graph"]["nodes"] if n.get("function") == "MakeRotator"]
        self.assertEqual(len(mr), 30); p, y, r = rd.REF_ROT["middle_02_r"]
        self.assertIn({"Pitch": str(p), "Yaw": str(y), "Roll": str(r)}, [{k: n["in"][k] for k in ("Pitch", "Yaw", "Roll")} for n in mr])
        self.assertNotIn("Set Pose", js)   # Detail Commit shows it

    def test_hand_pose_commits_once(self):
        js = json.dumps(rag_fn("Apply Hand Pose")); self.assertEqual(js.count("\"Detail Commit\""), 1); self.assertEqual(js.count("\"Curl Finger\""), 5)

    def test_gaze_morphs(self):
        js = json.dumps(rag_fn("Set Gaze"))
        for m in ("Face_Eye2Left", "Face_Eye2Right", "Face_Eye2Up", "Face_Eye2Down", "GazeSet"): self.assertIn(m, js)

    def test_lids(self):
        js = json.dumps(rag_fn("Apply Lids")); self.assertIn("Eye_L", js); self.assertIn("Lid Rot", js); self.assertIn(str(rd.LID_DEG), js)
        self.assertNotIn("(Pitch=", js)   # wired MakeRotator: a rotator literal cooks as zero

    def test_test_events(self):
        js = json.dumps(rag_bp()["event_graph"])
        for s in ("Test Curl Rot", "Test Lid Rot", "Test Gaze"): self.assertIn(s, js)


def mgr_fns():
    d = json.load(open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")))
    mgr = next(a for a in d["assets"] if a["path"].endswith("BP_AltUIManager"))
    return {f["name"]: f for f in mgr["functions"]}


class Mouse(unittest.TestCase):
    def test_functions(self):
        fns = mgr_fns()
        for n in ("Mouse Px", "Rag Curl Begin", "Rag Curl Update", "Rag Eye Update", "Rag Detail End"): self.assertIn(n, fns)

    def test_begin_drag_detail_branch(self):
        js = json.dumps(mgr_fns()["Begin Jodi Drag"])
        for s in ("Detail Kind", "Rag Curl Begin", "RagEye", "RagEyeWhich", "DetailHold", "Eye_L"): self.assertIn(s, js)
        bj = mgr_fns()["Begin Jodi Drag"]["graph"]["exec"]
        self.assertIn(["bdt:else", "rjd"], bj)   # not a fine sphere: everything as before

    def test_drag_and_wheel(self):
        fns = mgr_fns()
        self.assertIn("Rag Curl Update", json.dumps(fns["Jodi Drag"])); self.assertIn("Rag Eye Update", json.dumps(fns["Jodi Drag"]))
        lift = json.dumps(fns["Rag Lift"]); self.assertIn("Eye Lids Step", lift); self.assertIn("RagEyeWhich", lift)
        self.assertIn("Rag Detail End", json.dumps(fns["End Jodi Drag"]))
        self.assertIn(str(rd.RAG_CURL_PX), json.dumps(fns["Rag Curl Update"]))
        self.assertIn("Look At", json.dumps(fns["Rag Eye Update"]))


from strings import STRINGS, LANGS


class Tab(unittest.TestCase):
    def test_rows(self):
        js = json.dumps(mgr_fns()["Rebuild Ragdolls Body"])   # the builder; "Rebuild Ragdolls" wraps it (scroll keeping)
        for s in ("Has Detail", "RagHand", "RagEyes", "Rag_HandL", "Rag_HandR", "Rag_Eyes", "Rag_EyesReset", "Rag_HandPose_ThumbsUp"): self.assertIn(s, js)

    def test_action(self):
        js = json.dumps(mgr_fns()["Ragdoll Action"])
        for s in ("\"RagHand\"", "\"RagEyes\"", "Apply Hand Pose", "Reset Eyes"): self.assertIn(s, js)

    def test_strings(self):
        keys = ["Rag_HandL", "Rag_HandR", "Rag_Eyes", "Rag_EyesReset"] + ["Rag_HandPose_" + n for n, _ in rd.HAND_POSES]
        for k in keys: self.assertEqual(len(STRINGS[k]), len(LANGS), k)
        import strings_fr
        for k in keys: self.assertIn(k, strings_fr.FR, k)


import gen_manager


class Saving(unittest.TestCase):
    def struct_fields(self, path):
        a = next(x for x in gen_manager.assets if x.get("path") == path)
        return [m["name"] for m in a["members"]]

    def test_fields(self):
        for p in (gen_manager.S_RAGFIG, gen_manager.S_RAGPOSE): self.assertEqual(self.struct_fields(p)[-3:], ["GazeSide", "GazeUp", "HasGaze"], p)

    def test_save_and_load(self):
        fns = mgr_fns()
        for n in ("Save Rag Preset", "Save Rag Pose", "Store Rag Pose"): self.assertIn("HasGaze", json.dumps(fns[n]), n)
        for n in ("Rag Load Apply", "Load Rag Pose"):
            js = json.dumps(fns[n]); self.assertIn("Set Gaze", js); self.assertIn("HasGaze", js)


if __name__ == "__main__":
    unittest.main()
