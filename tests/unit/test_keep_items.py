"""2026-10-24: keep pieces through look / outfit changes (spec internal design notes).
KeepItems = marked pieces (only the menu changes it), SnapWorn = worn pieces a look / outfit put on. Apply Snapshot with
keep = true leaves the marked pieces the player put on and skips what would push them off."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, asset, MGR


def by_id(g): return {n["id"]: n for n in g["nodes"]}


class Mark(unittest.TestCase):
    def test_saved_lists(self):
        sg = [v["name"] for v in asset("/Game/Mod/AltUI/SG_AltUI")["variables"]]
        mg = [v["name"] for v in asset(MGR)["variables"]]
        for v in ("KeepItems", "SnapWorn"):
            self.assertIn(v, sg); self.assertIn(v, mg)

    def test_toggle_saves_and_redraws(self):
        g = mgr_graph("Toggle Keep Item"); b = by_id(g)
        self.assertEqual(b["rm"]["in"]["TargetArray"], "@gk.KeepItems"); self.assertEqual(b["add"]["in"]["TargetArray"], "@gk2.KeepItems")
        self.assertIn(["sv", "bo", "rl"], g["exec"])

    def test_menu_row_and_action(self):
        g = mgr_graph("On Item Context"); b = by_id(g)
        self.assertEqual(b["mi22"]["in"]["action"], "Keep"); self.assertEqual(b["iki"]["function"], "Is Kept Item")
        d = mgr_graph("On Menu Action")
        self.assertTrue(any(n.get("function") == "Toggle Keep Item" for n in d["nodes"]))

    def test_hand_wear_and_take_off_end_look_origin(self):
        for f in ("Wear", "Take Off"):
            g = mgr_graph(f); b = by_id(g)
            self.assertEqual(b["nsw"]["function"], "Note Self Worn"); self.assertTrue(any(c[:2] == ["entry", "nsw"] for c in g["exec"]), f)
        n = by_id(mgr_graph("Note Self Worn")); self.assertEqual(n["rm"]["in"]["TargetArray"], "@gs.SnapWorn")


W_BTN = "/Game/Mod/AltUI/W_ClothesButton"


def widget_graph(path, name):
    for f in asset(path)["functions"]:
        if f["name"] == name: return f["graph"]
    raise AssertionError(name)


class Badge(unittest.TestCase):
    def test_badge_order_damaged_kept_fav(self):
        b = by_id(widget_graph(W_BTN, "Init"))
        self.assertEqual(b["ks"]["in"]["B"], "@fs.ReturnValue"); self.assertEqual(b["ks"]["in"]["bPickA"], "@gkp.Kept")
        self.assertEqual(b["ds"]["in"]["B"], "@ks.ReturnValue")
        self.assertIn("Kept", [v["name"] for v in asset(W_BTN)["variables"]])

    def test_clothes_list_sets_kept_before_init(self):
        g = mgr_graph("Clo Init Tile"); b = by_id(g)
        self.assertEqual(b["sk"]["var"], "Kept"); self.assertEqual(b["sk"]["in"]["Kept"], "@ikt.yes")
        self.assertIn(["entry", "sm", "dm", "tip", "sk", "init"], g["exec"])


class Snapshot(unittest.TestCase):
    def test_callers_pass_keep(self):
        want = {("On Outfit Clicked", "as"): "true", ("Apply Look", "ap"): "@entry.keep", ("Rag Load Next", "as"): "false",
                ("Rag Load Next", "back"): "false", ("Undo", "ap"): "false", ("Redo", "ap"): "false", ("Start Next Snapshot", "asn"): "@gnk.NextKeep"}
        for (f, nid), v in want.items():
            self.assertEqual(by_id(mgr_graph(f))[nid]["in"]["keep"], v, f)
        self.assertEqual(by_id(mgr_graph("Spawn Look Ragdoll"))["al"]["in"]["keep"], "false")   # the ragdoll shows the look itself
        self.assertEqual(by_id(mgr_graph("On Look Clicked"))["ap"]["in"]["keep"], "true")

    def test_collect_then_skip_kept_take_off(self):
        g = mgr_graph("Apply Snapshot"); b = by_id(g)
        self.assertEqual(b["ck"]["function"], "Collect Kept"); self.assertEqual(b["ck"]["in"]["keep"], "@entry.keep")
        self.assertTrue(any(c[i:i + 3] == ["rs", "ck", "sn"] for c in g["exec"] for i in range(len(c))))
        self.assertEqual(b["kk"]["in"]["TargetArray"], "@gko.KeptOn"); self.assertIn(["b1:else", "bkk"], g["exec"]); self.assertIn(["bkk:else", "to"], g["exec"])

    def test_blocked_pieces_go_to_the_notice(self):
        g = mgr_graph("Apply Snapshot"); b = by_id(g)
        self.assertEqual(b["bbk"]["function"], "Blocked By Kept"); self.assertEqual(b["pka"]["in"]["TargetArray"], "@gpk.PendingKept")
        self.assertIn(["f2", "bbk", "bbl", "pka"], g["exec"]); self.assertIn(["bbl:else", "fi", "bu", "au"], g["exec"])
        self.assertEqual(b["spk"]["in"]["PendingKeep"], "@entry.keep"); self.assertEqual(b["snk"]["in"]["NextKeep"], "@entry.keep")

    def test_queue_records_what_a_look_put_on(self):
        g = mgr_graph("Wear Queue Step"); b = by_id(g)
        self.assertEqual(b["swa"]["in"]["TargetArray"], "@gsw.SnapWorn"); self.assertEqual(b["bpk"]["in"]["Condition"], "@gpk.PendingKeep")
        self.assertIn(["tc_fo:Completed", "we2", "bwe2", "bpk"], g["exec"]); self.assertIn(["bkn:else", "we", "bwe", "bpk"], g["exec"])
        self.assertIn(["bpk", "swa", "b3"], g["exec"]); self.assertIn(["bpk:else", "b3"], g["exec"])

    def test_blocked_by_kept_rules(self):
        b = by_id(mgr_graph("Blocked By Kept"))
        self.assertEqual(b["kis"]["function"], "Keep In Slot"); self.assertEqual(b["cw"]["function"], "Conflicts With"); self.assertEqual(b["fr"]["function"], "Is Freed")
        self.assertEqual(b["hit"]["in"]["B"], "@known.ReturnValue")

class Finish(unittest.TestCase):
    def test_kept_colours_survive(self):
        g = mgr_graph("Finish Apply Snapshot"); b = by_id(g)
        self.assertEqual(b["wkc"]["function"], "Look Colors"); self.assertEqual(b["wkc"]["in"]["snap"], "@gps.PendingSnap")
        self.assertEqual(b["rdc"]["in"]["next"], "@wkc.slot"); self.assertEqual(b["ssc9"]["in"]["SlotColors"], "@wkc.slot"); self.assertEqual(b["smc9"]["in"]["MakeupColors"], "@wkc.makeup")
        self.assertTrue(any(c[i:i + 3] == ["umt", "wkc", "rdc"] for c in g["exec"] for i in range(len(c))))
        lc = by_id(mgr_graph("Look Colors")); self.assertEqual(lc["wkc"]["function"], "With Kept Colors")   # replaced (undo, ragdoll): as before

    def test_looks_and_outfits_merge_undo_replaces(self):
        """2026-11-01: a look / outfit merges its colours into the save's (SnapMerge), undo / redo and the ragdoll's way back replace."""
        for f in ("Apply Look", "On Outfit Clicked"):
            g = mgr_graph(f); b = by_id(g); self.assertEqual(b["smg"]["in"]["SnapMerge"], "true", f)
            self.assertTrue(any(c[i:i + 2] == ["smg", n] for c in g["exec"] for i in range(len(c)) for n in ("ap", "as")), f)
        for f in ("Undo", "Redo", "Rag Load Next"):
            self.assertFalse(any(n.get("var") == "SnapMerge" for n in mgr_graph(f)["nodes"]), f)
        a = by_id(mgr_graph("Apply Snapshot")); self.assertEqual(a["spmg"]["in"]["PendingMerge"], "@gmg1.SnapMerge"); self.assertEqual(a["smg0"]["in"]["SnapMerge"], "false")
        self.assertEqual(by_id(mgr_graph("Start Next Snapshot"))["smg"]["in"]["SnapMerge"], "@gnmg.NextMerge")

    def test_notice_has_its_own_line(self):
        g = mgr_graph("Finish Apply Snapshot"); b = by_id(g)
        self.assertEqual(b["snt"]["function"], "Snap Notice Text"); self.assertIn(["fmk:Completed", "snt", "bms"], g["exec"])
        self.assertIn(["bms:else", "mpop", "rs2"], g["exec"]); self.assertIn(["bms", "rs2"], g["exec"])
        n = by_id(mgr_graph("Snap Notice Text"))
        self.assertEqual(n["j2"]["in"]["SourceArray"], "@g2.PendingKept"); self.assertEqual(n["jn"]["in"]["Separator"], "\n")   # one line per kind (not owned: its own, 2026-11-01)


if __name__ == "__main__":
    unittest.main()
