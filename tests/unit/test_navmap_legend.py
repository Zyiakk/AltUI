"""Map legend, marker kinds, fullscreen map, round minimap (spec 2026-11-19 map-legend-fullscreen-round)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_options_cats import graph, calls
from strings import STRINGS, LANGS
import strings_fr, navmap as nm, gen_manager as gm, gen_textures, bpdsl
A = os.path.join(H, "..", "..", "assets")


def g(name): return graph("50_manager_ui.json", name)
def fns(gr): return [n.get("function") for n in gr["nodes"]]
def js(gr): return json.dumps(gr)
def widgets(): return json.load(open(os.path.join(A, "40_widgets.json")))["assets"]
def widget(suffix): return [a for a in widgets() if a["path"].endswith(suffix)][0]


class Assets(unittest.TestCase):
    def test_textures(self):
        paths = [a["path"] for a in gen_textures.build(A)]
        for t in ("T_MapRing", "T_MapDead", "T_MapVend", "T_MapLower", "T_MapHatch", "T_MapRingFrame"): self.assertIn(bpdsl.M + "/" + t, paths, t)

    def test_circle_material(self):
        mat = open(os.path.join(H, "..", "..", "scripts", "quickmenu", "material.py")).read()
        self.assertIn('"/Game/Mod/AltUI/Mat/M_MapCircle"', mat); self.assertIn("map_circle()", mat); self.assertIn('"Round"', mat); self.assertIn('"Texture"', mat)
        sh = open(os.path.join(H, "..", "..", "scripts", "quickmenu", "material.sh")).read(); self.assertEqual(sh.count("M_MapCircle"), 3)

    def test_trading_stub(self):
        stubs = json.load(open(os.path.join(A, "10_stubs.json")))["assets"]
        self.assertIn(bpdsl.P_TRADING, [a["path"] for a in stubs])


class Kinds(unittest.TestCase):
    def test_kind_of(self):
        k = g("Map Kind Of"); j = js(k)
        self.assertIn("Is Alive ?", fns(k)); self.assertIn('"Health"', j); self.assertIn("FolActors", j)
        for c in (bpdsl.P_JASON, bpdsl.P_CNPC, bpdsl.P_ZOMBIE): self.assertIn(c, j)
        self.assertIn('"bHidden"', j)   # zombies placed hidden until a trigger shows them are no markers (play test 2026-11-20)

    def test_redraw_kinds(self):
        r = g("Map Redraw"); j = js(r)
        for t in (nm.T_RING, nm.T_DEAD, nm.T_VEND, nm.T_DOT, nm.T_BED): self.assertIn(t, j)
        for c in (nm.COL_NPC, nm.COL_HOSTILE, nm.COL_DEAD, nm.COL_VEND): self.assertIn(c, j)
        self.assertIn("Map Kind Hidden", fns(r)); self.assertIn(bpdsl.P_CB, j); self.assertIn("MapSeen", j); self.assertIn("Map Rebuild Legend", fns(r))
        ex = r["exec"]; flat = [x for c in ex for x in c]
        # dead first (pass 1), then the dots, then the ring on top
        self.assertTrue(any(c[0] == "kd:Completed" and c[1] == "kp2" for c in ex)); self.assertTrue(any(c[0] == "kp2:Completed" and c[1] == "kp3" for c in ex))
        self.assertIn("kdmb", flat)

    def test_bed_click_respects_hidden(self):
        self.assertIn("Map Kind Hidden", fns(g("Map Release")))

    def test_vends_scanned(self):
        self.assertTrue(calls(g("Map Open"), "Map Scan Vends")); self.assertTrue(calls(g("Map Scan Beds"), "Map Scan Vends"))
        self.assertIn(bpdsl.P_TRADING, js(g("Map Scan Vends")))

    def test_hidden_keys(self):
        self.assertEqual(nm.KIND_KEYS, ("", "fol", "npc", "zombie", "hostile", "dead", "bed", "vend"))
        names = {s[0] for s in gm.SETTINGS}
        for k in ("MapHidden", "MapNoLegend"): self.assertIn(k, names)
        self.assertGreaterEqual(nm.MARK_POOL, 96)


class Legend(unittest.TestCase):
    def test_item_widget(self):
        it = widget("/W_MapLegItem"); names = [f["name"] for f in it["functions"]]
        self.assertIn("Init", names); self.assertIn("OnMouseButtonDown", names); self.assertIn("Map Legend Toggle", js(it))
        # clickable entries are chips (background, hover, hand cursor), the others plain dim text (play test 2026-11-19)
        self.assertIn("Apply Colors", names); j = js(it); [self.assertIn(x, j) for x in ("ColChip", "ColChipHover", "ColTextDim", '"Hand"', '"Default"')]

    def test_panel_rows(self):
        panel = js(widget("/W_AltUI")["widget_tree"])
        self.assertLess(panel.index('"NavMap"'), panel.index('"MapLegend"')); self.assertLess(panel.index('"MapLegend"'), panel.index('"NavHint"'))
        nv = widget("/W_NavMap"); self.assertIn("T_MapHatch.T_MapHatch", js(nv["widget_tree"]))   # the full object path (it was "<folder>.T_MapHatch": white)
        self.assertIn("Set Ground", [f["name"] for f in nv["functions"]]); r = js(g("Map Redraw")); self.assertIn("ColBg", r); self.assertIn("Set Ground", r)

    def test_rebuild(self):
        r = g("Map Rebuild Legend"); f = fns(r)
        self.assertEqual(f.count("Add Map Legend"), 1 + 7 + 2)   # Jodi, the kinds, the two grounds
        for x in ("Clear Map Legend", "Set Map Legend Shown", "Map Kind Hidden"): self.assertIn(x, f)
        j = js(r); self.assertIn("MapNoLegend", j); self.assertIn("MapSeen", j); self.assertIn(nm.T_HATCH, j); self.assertIn(nm.T_LOWER, j)
        t = g("Map Legend Toggle"); self.assertIn("Save Settings", fns(t)); self.assertIn("MapHidden", js(t))

    def test_option_row(self):
        import gen_widgets as gw
        rows = gw.OPT_CAT_ROWS["Map"]; self.assertLess(rows.index("RowMapOn"), rows.index("RowMapLegend")); self.assertIn("RowMiniShape", rows)
        self.assertIn("MapNoLegend", js(g("Poll Map Options"))); self.assertIn("MapNoLegend", js(g("Rebuild Map Options")))

    def test_strings(self):
        keys = ["Map_Leg_" + k for k in ("Jodi", "Bed", "Vend", "Fol", "Npc", "Zombie", "Hostile", "Dead", "Unexplored", "Lower")] + \
               ["Map_LegTip", "Lbl_MapLegend", "Map_Full", "Map_Close", "Quick_MapFull", "Lbl_MiniShape", "Mini_Square", "Mini_Round"]
        for k in keys: self.assertEqual(len(STRINGS[k]), len(LANGS), k); self.assertIn(k, strings_fr.FR, k)


class Fullscreen(unittest.TestCase):
    def test_layer(self):
        tree = widget("/W_AltUI")["widget_tree"]; layer = [c for c in tree["children"] if c["name"] == "MapFull"][0]
        self.assertEqual(layer["props"]["Visibility"], "Collapsed"); self.assertGreater(layer["slot"]["ZOrder"], 5)
        t = js(layer)
        for wn in ('"FullMap"', "MapFullLinks", "MapFullLabel", "MapFullLegend"): self.assertIn(wn, t)
        self.assertIn(nm.W_NAVMAP, t)
        body = [c for c in layer["children"][0]["children"][0]["children"] if c["name"] == "MapFullBody"][0]   # legend under the map
        self.assertEqual([c["name"] for c in body["children"]], ["FullMap", "MapFullLegend"]); self.assertEqual(body["class"], "/Script/UMG.VerticalBox")

    def test_open_close(self):
        o = g("Map Full Open"); f = fns(o)
        for x in ("Open Panel", "Select Page", "Set Map Full", "Get Full Map", "Map Rebuild Links", "Map Redraw"): self.assertIn(x, f, x)
        self.assertIn("MapFullPrevPage", js(o)); self.assertIn(str(nm.FULL_RIM), js(o))
        c = g("Map Full Close"); self.assertIn("Close Panel", fns(c)); self.assertIn("Map Full Reset", fns(c)); self.assertIn("MapFullFromPanel", js(c))
        self.assertIn("Get Nav Map", fns(g("Map Full Reset")))

    def test_keys(self):
        pk = g("Panel Key Close"); ch = [c for c in pk["exec"] if c[0] == "entry"][0]; self.assertEqual(ch[:3], ["entry", "bmf", "cmf"])
        self.assertTrue(calls(g("Close Panel"), "Map Full Reset"))
        self.assertIn("Map Full Key", js(widget("/W_AltUI")))
        k = g("Map Full Key"); self.assertIn("MapFullArm", js(k)); self.assertIn('"mapfull"', js(k))
        self.assertIn("QFromKey", js(g("Bind Run")))

    def test_quick_and_link(self):
        import gen_manager_ui as ui
        self.assertIn("mapfull", ui.QUICK_FIXED); self.assertEqual(ui.QUICK_FIXED_TEXT["mapfull"], "Quick_MapFull"); self.assertIn("mapfull", ui.QUICK_FIXED_ICON)
        self.assertTrue(calls(g("Run Quick Item"), "Map Full Toggle"))
        self.assertIn(("MapFull", "Map Full Toggle"), nm.ACTIONS); self.assertIn("Map_Full", js(g("Map Rebuild Links")))


class RoundMini(unittest.TestCase):
    def test_widget(self):
        m = widget("/W_MiniMap"); t = js(m["widget_tree"])
        self.assertIn("/Script/UMG.RetainerBox", t); self.assertIn("M_MapCircle", t)
        self.assertIn("Set Round", [f["name"] for f in m["functions"]]); self.assertIn(nm.T_RINGFRAME, js(m))

    def test_setting(self):
        self.assertIn("MiniRound", {s[0] for s in gm.SETTINGS}); self.assertTrue(calls(g("Mini Tick"), "Set Round"))
        r = g("Rebuild Map Options"); self.assertEqual(fns(r).count("Add MiniShape Chip"), 2)
        self.assertTrue(calls(g("Select SubTab"), "Select Mini Shape"))


if __name__ == "__main__":
    unittest.main()
