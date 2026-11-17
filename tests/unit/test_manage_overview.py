"""2026-11-16 (open-since-2.12.0 A2): Manage › Overview - the first category, a status table of the mods and the only place of
"Read mods again" (it stood above the search on some categories only)."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from test_fol_tab import mgr_graph


def by_id(g): return {n["id"]: n for n in g["nodes"]}


class Overview(unittest.TestCase):
    def test_first_category_without_count(self):
        import gen_manager_ui as m
        self.assertEqual(m.MANAGE_CATS[0], ("Overview", "Cat_Overview")); self.assertIn("Overview", m.MANAGE_NO_ONLY_MODS)
        b = by_id(mgr_graph("Rebuild Manage Cats")); self.assertEqual(b["ti0"]["in"]["count"], "-1")

    def test_rebuild_manage_dispatches(self):
        g = mgr_graph("Rebuild Manage"); b = by_id(g)
        self.assertEqual(b["ico"]["in"]["B"], "Overview"); self.assertEqual(b["rov"]["function"], "Rebuild Manage Overview")
        self.assertIn(["bsp:else", "bov", "rov"], g["exec"])

    def test_rows_and_rescan_link(self):
        g = mgr_graph("Rebuild Manage Overview"); b = by_id(g)
        self.assertEqual(b["ews"]["function"], "Ensure Weapon Scans")   # weapon counts need the names
        self.assertEqual(b["iok"]["in"]["TargetMap"], "@gio.ItemOriginMod")
        for k, kind in enumerate(("item", "hair", "look", "pose")): self.assertEqual(b["kl%d" % k]["in"]["Value"], kind)
        for k, v in enumerate(("SkinOwner", "ModelOwner", "SoundOwner")): self.assertEqual(b["wl%d" % k]["in"]["TargetMap"], "@gw%d.%s" % (k, v))
        self.assertEqual(b["sdt"]["function"], "Stamp Date"); self.assertEqual(b["sdt"]["in"]["t"], "@gra.ReadAt")
        self.assertEqual(b["lra"]["in"]["Value"], "ModRescan"); self.assertEqual(b["lrin"]["in"]["action"], "@lra.ReturnValue")
        self.assertEqual(b["lrad"]["in"]["self"], "@lw.AsW_LinkRow")   # the link sits in the row below the table

    def test_rescan_gone_from_search_links(self):
        b = by_id(mgr_graph("Rebuild Manage Links")); self.assertNotIn("ri", b)

    def test_read_at_saved_with_the_file_index(self):
        from test_fol_tab import mgr_graph as mg
        g = mg("Mod File Index"); b = by_id(g)
        self.assertEqual(b["nst"]["function"], "Now Stamp"); self.assertEqual(b["prd"]["in"]["ReadAt"], "@nst.t")


class TooltipWraps(unittest.TestCase):
    def test_long_tip_wraps(self):
        """Play test 2026-11-17 (J5): the shared-name list of a mod ran off the screen in one line - every W_Tooltip wraps at ~80 characters (at ~40 it ran off the top)."""
        import json
        from test_share_bp import widget
        js = json.dumps(widget("/W_Tooltip")["widget_tree"]); self.assertIn('"WrapTextAt"', js)


if __name__ == "__main__":
    unittest.main()
