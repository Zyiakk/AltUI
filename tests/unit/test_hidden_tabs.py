"""2026-11-13 (spec 2026-11-13-panel-load-time-design): weapon mod tables once per level and before the first weapon is dressed;
hidden tabs cost nothing (internal design notes)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph

SCANS = {"Scan Weapon Skins", "Scan Weapon Models", "Scan Weapon Sounds"}


def fns(g): return {n.get("function") for n in g["nodes"]}


class WeaponScans(unittest.TestCase):
    def test_open_panel_no_direct_scans(self):
        g = mgr_graph("Open Panel"); self.assertFalse(SCANS & fns(g)); self.assertIn("Ensure Weapon Scans", fns(g))
        self.assertIn("Apply All Weapon Looks", fns(g))   # the looks still follow on every open

    def test_ensure_once(self):
        # 2026-11-16: the scans (all tables) in Ensure Weapon Assets; Ensure Weapon Scans reads the cached names or calls it
        g = mgr_graph("Ensure Weapon Assets"); self.assertEqual(SCANS & fns(g), SCANS)
        self.assertIn(["entry", "b"], g["exec"]); self.assertEqual([c for c in g["exec"] if c[0] == "b:else"][0][:3], ["b:else", "sd", "sd2"])
        self.assertEqual([n["var"] for n in g["nodes"] if n["id"] in ("sd", "sd2")], ["WeaponAssetsDone", "WeaponScansDone"])
        g = mgr_graph("Ensure Weapon Scans"); self.assertIn(["entry", "b"], g["exec"])
        self.assertEqual([n for n in g["nodes"] if n["id"] == "sd"][0]["var"], "WeaponScansDone")

    def test_dressers_read_tables_first(self):
        """Before the panel's first open in a level a weapon was dressed with empty tables (mod skin as game paint, original model)."""
        for f in ("Apply Weapon Look On", "Dress Weapon", "Apply Weapon Sound", "Sync Weapon Paint", "Auto Gun Fit"):
            g = mgr_graph(f); first = [ch for ch in g["exec"] if ch and ch[0] == "entry"]
            self.assertTrue(first and first[0][1] == "ewsF", f)
            self.assertEqual([n for n in g["nodes"] if n["id"] == "ewsF"][0]["function"], "Ensure Weapon Scans", f)
        self.assertEqual(mgr_graph("Apply Weapon Look")["exec"][0][:2], ["entry", "dw"])   # through Dress Weapon



OFF_WHEN_HIDDEN = [("Obj Scan Step", "Objects"), ("Obj Next Icon", "Objects")]   # internal design notes, decision "aus"


class HiddenTabs(unittest.TestCase):
    def test_guarded(self):
        for f, page in OFF_WHEN_HIDDEN:
            g = mgr_graph(f); ids = {n["id"]: n for n in g["nodes"]}
            self.assertEqual(ids["tofG"]["function"], "Tab Off", f); self.assertEqual(ids["tofG"]["in"]["page"], page, f)
            self.assertIn(["entry", "tofB"], g["exec"], f)
            self.assertFalse([ch for ch in g["exec"] if ch and ch[0] == "tofB"], f)   # switched off: nothing follows

    def test_tab_off_is_hidden_tabs(self):
        g = mgr_graph("Tab Off"); self.assertEqual([n["var"] for n in g["nodes"] if n.get("kind") == "get"], ["HiddenTabs"])

    def test_scan_goes_on_when_shown(self):
        g = mgr_graph("Rebuild Objects")
        self.assertTrue([n for n in g["nodes"] if n.get("function") == "K2_SetTimer" and n["in"].get("FunctionName") == "Obj Scan Step"])

    def test_polls_only_on_their_page(self):
        from test_fol_tab import assets, MGR
        ev = [a["event_graph"] for a in assets() if a.get("path") == MGR and a.get("event_graph")][-1]
        ids = {n["id"]: n for n in ev["nodes"]}
        self.assertEqual(ids["tpcl"]["in"]["B"], "Clothes"); self.assertIn("tor2", json.dumps(ids["tb1"]))
        self.assertEqual(ids["tilk"]["in"]["B"], "Look")



class PerfMarks(unittest.TestCase):
    """Messbuild (ALTUI_PERFLOG): the first open per level measured in its parts; inside a measured function only its main path."""
    def test_nested_marks(self):
        import gen_manager_ui as m
        from bpdsl import G
        old = m.PERFLOG; m.PERFLOG = True
        try:
            g = G(); g.n("a", "call_self", function="Foo"); g.n("b", "call_self", function="Bar"); g.n("c", "call_self", function="Baz")
            g.foreach("fe", "@x.y"); g.chain("entry", "a", "fe", "b"); g.chain("fe", "c", "b")
            m.perf_marks(g, "Outer", extra={"fe": "Loop"})
            labels = [n["in"]["label"] for n in g.nodes if n.get("function") == "Perf Mark"]
            self.assertEqual(labels, ["Outer/Foo", "Loop"]); self.assertEqual(g.exec[1], ["fe", "c", "b"])
        finally: m.PERFLOG = old

    def test_wired_in(self):
        import gen_manager_ui as m
        src = open(m.__file__).read()
        for f in ("Rebuild Catalog If Dirty", "Rebuild Left", "Rebuild SubTabs", "Rebuild List", "Apply Theme"): self.assertIn('perf_marks(g, "%s")' % f, src)
        self.assertIn('"cw_cr": "CreateWidget W_Panel"', src)


if __name__ == "__main__": unittest.main()
