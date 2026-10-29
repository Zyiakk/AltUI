"""2026-10-24: keep pieces through look / outfit changes (spec docs/superpowers/specs/2026-10-24-keep-items-design.md).
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
        self.assertEqual(b["wkc"]["function"], "With Kept Colors"); self.assertEqual(b["wkc"]["in"]["next"], "@bs.SlotColors")
        self.assertEqual(b["rdc"]["in"]["next"], "@wkc.colors"); self.assertEqual(b["ssc9"]["in"]["SlotColors"], "@wkc.colors")
        self.assertTrue(any(c[i:i + 3] == ["umt", "wkc", "rdc"] for c in g["exec"] for i in range(len(c))))

    def test_notice_has_its_own_line(self):
        g = mgr_graph("Finish Apply Snapshot"); b = by_id(g)
        self.assertEqual(b["snt"]["function"], "Snap Notice Text"); self.assertIn(["fmk:Completed", "snt", "bms"], g["exec"])
        self.assertIn(["bms:else", "mpop", "rs2"], g["exec"]); self.assertIn(["bms", "rs2"], g["exec"])
        n = by_id(mgr_graph("Snap Notice Text"))
        self.assertEqual(n["kj"]["in"]["SourceArray"], "@gk.PendingKept"); self.assertEqual(n["sep"]["in"]["A"], "\n")


if __name__ == "__main__":
    unittest.main()
