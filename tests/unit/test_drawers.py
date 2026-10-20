"""2026-10-20 (spec 2026-10-20-drawers-design): drawers in the Clothes tab - bar, piece menu with a submenu, filter, saved."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph
import strings, strings_fr

KEYS = ["Drawer_Default", "Drawer_Word", "Menu_Drawer", "Menu_DrawerNew", "Menu_DrawerRemoveHere", "Drawer_DeleteYes"]


def by_id(g): return {n["id"]: n for n in g["nodes"]}
def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]


class Drawers(unittest.TestCase):
    def test_texts(self):
        for k in KEYS: self.assertEqual(len(strings.STRINGS[k]), 7, k); self.assertIn(k, strings_fr.FR, k)
        for s in strings.STRINGS["Drawer_DeleteYes"]: self.assertIn("%s", s)

    def test_saved(self):
        import gen_manager as gm
        self.assertIn(("CurrentDrawer", "CurrentDrawer", "copy", None), gm.SETTINGS); self.assertEqual(gm.DRAWERS_SLOT, "AltUI_Drawers")

    def test_filter_and_counts(self):
        fi, sc = mgr_graph("Filtered Items"), mgr_graph("Slot Count")
        self.assertTrue([n for n in fi["nodes"] if n.get("var") == "DrawerSet"]); self.assertTrue([n for n in sc["nodes"] if n.get("var") == "DrawerCounts"])

    def test_piece_menu(self):
        b = by_id(mgr_graph("On Item Context")); self.assertEqual(b["mi20"]["in"]["action"], "Drw:Sub"); self.assertEqual(b["mi21"]["in"]["action"], "Drw:RemoveHere")

    def test_drawer_rows_skip_close_menu(self):
        g = mgr_graph("On Menu Action"); self.assertIn(["entry", "bdrw", "drw_a"], g["exec"]); self.assertIn(["bdrw:else", "cm", "blmp", "bscn"], g["exec"])
        self.assertTrue(calls(mgr_graph("Close Menu"), "RemoveFromParent"))
        self.assertTrue([n for n in mgr_graph("Close Menu")["nodes"] if n.get("var") == "SubMenu"])

    def test_bar_and_chips(self):
        self.assertTrue(calls(mgr_graph("Rebuild Left"), "Rebuild Drawer Bar")); self.assertTrue(calls(mgr_graph("Select SubTab"), "Drawer Chip"))
        self.assertTrue(calls(mgr_graph("SubTab Context"), "Drawer Tab Menu"))
        self.assertTrue(calls(mgr_graph("Drawer Menu Action"), "Drawer Submenu")); self.assertTrue(calls(mgr_graph("Drawer Menu Action"), "Drawer Delete"))


if __name__ == "__main__": unittest.main()
