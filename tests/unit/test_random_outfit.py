"""2026-11-10: Clothes tab, status bar bottom right: "Random outfit" - one random wearable piece from every slot; its context menu
(right click) has a table Undress | Dress per slot (RandNoUndress / RandNoDress, saved)."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from test_fol_tab import mgr_graph


def by_id(g): return {n["id"]: n for n in g["nodes"]}


class RandomOutfit(unittest.TestCase):
    def test_status_link_on_the_clothes_page(self):
        g = mgr_graph("Rebuild Status"); b = by_id(g)
        self.assertEqual(b["iscl"]["in"]["B"], "Clothes")
        self.assertEqual(b["rdi"]["in"]["action"], "RandomOutfit"); self.assertEqual(b["ard"]["function"], "Add Status Right")
        self.assertIn(["bcl", "rro2_cr", "smrd", "rdi", "ard"], g["exec"])
        for src in ("bws:else", "bnr", "arl"): self.assertIn([src, "bcl"], g["exec"])   # reached on every page

    def test_menu_action(self):
        import gen_manager_ui as m
        self.assertIn(("RandomOutfit", "Random Outfit", None), m.MENU_ACTIONS)

    def test_one_wearable_piece_per_slot(self):
        g = mgr_graph("Random Outfit"); b = by_id(g)
        self.assertEqual(b["unk"]["in"]["B"], "Unknown")
        self.assertEqual(b["rcs"]["function"], "Random Candidates"); self.assertEqual(b["rcs"]["in"]["slot"], "@fs.Array Element")
        self.assertIn(["fs", "bok", "cfs", "bcf", "rcs", "bany", "rwa"], g["exec"])
        c = mgr_graph("Random Candidates"); cb = by_id(c)   # what the slot shows (drawer, hidden left out) and may be put on
        self.assertEqual(cb["fi"]["function"], "Filtered Items"); self.assertEqual(cb["fi"]["in"]["group"], "None"); self.assertEqual(cb["fi"]["in"]["onlyOwned"], "false")
        self.assertEqual(cb["cw"]["function"], "Can Wear"); self.assertIn(["fc", "cw", "bcw", "rca"], c["exec"])
        # the colours: merged like an outfit, with the current slot colours (204/7)
        self.assertEqual(b["mk"]["in"]["SlotColors"], "@gsc9.SlotColors"); self.assertEqual(b["smg"]["in"]["SnapMerge"], "true")
        self.assertEqual(b["ri"]["function"], "RandomIntegerInRange"); self.assertEqual(b["ri"]["in"]["Min"], "0")
        self.assertEqual(b["as"]["function"], "Apply Snapshot"); self.assertEqual(b["as"]["in"]["keep"], "false")
        self.assertEqual(b["mk"]["in"]["Worn"], "@grw3.RandWorn")
        self.assertIn(["entry", "ph", "ts", "rwc", "rkc", "fw"], g["exec"])   # undo-able
        self.assertIn(["fs:Completed", "smo", "smg", "as"], g["exec"])

    def test_undress_off_keeps_the_piece_and_blocks_its_slot(self):
        g = mgr_graph("Random Outfit"); b = by_id(g)
        self.assertEqual(b["keep"]["in"]["TargetArray"], "@gnu.RandNoUndress")
        self.assertIn(["fw", "bkp", "rwk", "rka"], g["exec"])   # the kept piece stays in the snapshot, its slot noted
        self.assertEqual(b["nod"]["in"]["TargetArray"], "@gnd.RandNoDress")
        self.assertEqual(b["mul"]["in"]["TargetArray"], "@gms.MultiSlots")   # a slot holding several still gets a new piece
        self.assertEqual(b["cfs"]["function"], "Conflicting Slots"); self.assertEqual(b["cfs"]["in"]["worn"], "@grkp.RandKept")
        self.assertIn(["fs", "bok", "cfs", "bcf", "rcs", "bany", "rwa"], g["exec"])

    def test_right_click_opens_the_table(self):
        g = mgr_graph("On Link Context"); b = by_id(g)
        self.assertEqual(b["isr"]["in"]["B"], "RandomOutfit"); self.assertEqual(b["orm"]["function"], "Open Random Menu")
        self.assertIn(["b:else", "oma"], g["exec"]); self.assertEqual(b["oma"]["function"], "On Menu Action")   # other links as before
        g = mgr_graph("Open Random Menu"); b = by_id(g)
        self.assertEqual(b["hi"]["in"]["head"], "true"); self.assertEqual(b["ri"]["in"]["head"], "false")
        self.assertEqual(b["ri"]["in"]["undress"], "@nu.ReturnValue"); self.assertEqual(b["ri"]["in"]["dress"], "@nd.ReturnValue")

    def test_box_change_saved(self):
        g = mgr_graph("Random Slot Changed"); b = by_id(g)
        self.assertEqual(b["urm"]["in"]["TargetArray"], "@ug1.RandNoUndress"); self.assertEqual(b["drm"]["in"]["TargetArray"], "@dg1.RandNoDress")
        self.assertIn(["ub:else", "uad", "sv"], g["exec"]); self.assertIn(["db:else", "dad", "sv"], g["exec"])
        self.assertEqual(b["sv"]["function"], "Save Settings")

    def test_saved_settings(self):
        import gen_manager as m
        for k in ("RandNoUndress", "RandNoDress"): self.assertIn((k, k, "copy", None), m.SETTINGS)


if __name__ == "__main__":
    unittest.main()
