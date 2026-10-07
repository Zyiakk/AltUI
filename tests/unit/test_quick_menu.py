"""Quick menu (docs/specs/2026-10-03-quick-menu-design.md): data, strings, settings, graphs."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
from strings import STRINGS, LANGS
import gen_manager, gen_manager_ui as ui
from tests.unit.test_options_cats import graph, calls, after

QUICK_STRINGS = ["OptCat_Quick", "Lbl_QuickKey", "Lbl_QuickInWheel", "Lbl_QuickAvailable", "Lbl_QuickEmpty", "Lbl_QuickKeyTaken", "QuickGrp_Camera",
                 "QuickGrp_Outfits", "QuickGrp_Looks", "QuickGrp_Faces", "QuickGrp_Presets", "QuickGrp_Poses", "QuickGrp_Tabs", "QuickGrp_ModEntries",
                 "Quick_FreeCam", "Quick_Photo", "Quick_Panel", "Quick_PoseStop", "Quick_Outfit", "Quick_Preset", "Quick_SpeedToggle"]


class QuickData(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(ui.QUICK_MAX, 32); self.assertEqual(ui.QUICK_FIXED, ["freecam", "photo", "panel", "posestop", "ragdoll", "ragdolltoggle", "ragdollclear", "ragdollmode", "ragdollaim", "speedtoggle"])

    def test_strings(self):
        for k in QUICK_STRINGS: self.assertEqual(len(STRINGS[k]), len(LANGS), k)

    def test_settings(self):
        rows = {(m, s) for m, s, _, _ in gen_manager.SETTINGS}
        self.assertIn(("QuickKey", "QuickKey"), rows); self.assertIn(("QuickItems", "QuickItems"), rows)

    def test_find_covers_every_kind(self):
        g = graph("50_manager_ui.json", "Quick Find")
        kinds = {n["in"]["B"] for n in g["nodes"] if n.get("function") == "EqualEqual_StrStr" and n["id"].startswith("qe_")}
        self.assertEqual(kinds, set(ui.QUICK_FIXED) | {"tab", "pose", "modentry", "outfit", "look", "face", "preset", "modfield", "modaction"})


    def test_run_calls(self):
        g = graph("50_manager_ui.json", "Run Quick Item")
        for kind, fns in (("freecam", ["Open Panel", "Start Free Cam"]), ("photo", ["Open Panel", "Start Photo Mode"]), ("panel", ["Open Panel"]),
                          ("posestop", ["Stop Pose"]), ("tab", ["Open Panel", "Select Page"]), ("pose", ["Pose Clicked"]),
                          ("modentry", ["Open Panel", "Select Page", "Select Mod Entry"]), ("outfit", ["On Outfit Clicked"]), ("look", ["Apply Look"]),
                          ("face", ["On Face Clicked"]), ("preset", ["Preset Clicked"]), ("speedtoggle", ["Toggle Move"])):
            reach = after(g, "qb_" + kind)
            for f in fns: self.assertTrue(any(n in reach for n in calls(g, f)), (kind, f))


    def test_wheel_widgets(self):
        a = {x["path"].rsplit("/", 1)[1]: x for x in json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json")))["assets"]}
        self.assertTrue({"OnMouseMove", "OnKeyUp", "OnKeyDown", "OnMouseButtonUp", "Add Sector", "Set Center", "Init Center"} <= {f["name"] for f in a["W_QuickWheel"]["functions"]})
        self.assertTrue({"Init", "Set Marked"} <= {f["name"] for f in a["W_QuickSector"]["functions"]})
        self.assertIn("M_QuickSector", json.dumps(a["W_QuickSector"]["widget_tree"]))

    def test_key_opens_wheel_only_when_free(self):
        eg = next(x for x in json.load(open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")))["assets"] if x["path"].endswith("/BP_AltUIManager"))["event_graph"]
        self.assertIn(["kAny:Pressed", "bq", "oqw"], eg["exec"])
        bq = next(n for n in eg["nodes"] if n["id"] == "bq"); self.assertIn("@qb.", json.dumps(bq))
        qb = next(n for n in eg["nodes"] if n["id"] == "qb"); self.assertEqual(qb["in"], {"A": "@qa.ReturnValue", "B": "@ie.yes"})


    def test_options_block(self):
        import gen_widgets
        self.assertEqual(gen_widgets.OPT_CAT_ROWS["Quick"], ["LblQuickControl", "RowQuickKey", "RowQuickAlpha", "LblQuickInWheel", "QuickInWheel", "LblQuickAvailable", "QuickAvailable"])
        g = graph("50_manager_ui.json", "Rebuild Options"); c = calls(g, "Rebuild Quick Options"); self.assertEqual(len(c), 1)
        eqs = {n["id"] for n in g["nodes"] if n.get("function") == "EqualEqual_NameName" and "Quick" in n.get("in", {}).values()}
        br = [n["id"] for n in g["nodes"] if n.get("kind") == "branch" and any(("@%s." % e) in json.dumps(n) for e in eqs)]
        self.assertEqual(len(br), 1); self.assertIn(c[0], after(g, br[0])); self.assertNotIn(c[0], after(g, br[0] + ":else"))

    def test_menu_actions(self):
        g = graph("50_manager_ui.json", "On Menu Action"); self.assertIn(calls(g, "Quick Action")[0], after(g, "bq"))
        prefixes = {n["in"]["InPrefix"] for n in g["nodes"] if n.get("function") == "StartsWith"}
        self.assertTrue({"QKey", "QUp:", "QDown:", "QDel:"} <= prefixes)
        qa = graph("50_manager_ui.json", "Quick Action"); self.assertTrue(calls(qa, "Quick Move") and calls(qa, "Quick Remove"))

    def test_key_capture(self):
        self.assertTrue(calls(graph("50_manager_ui.json", "Key Captured"), "Quick Key Captured"))
        self.assertIn("QuickCapture", json.dumps(graph("50_manager_ui.json", "Capturing Key")))


    def test_mod_actions(self):
        import modui as mu
        self.assertEqual([n for n, _, _ in mu.ACTION_MEMBERS], ["Caption", "Icon", "Actor", "Key", "Order"])
        run = graph("50_manager_ui.json", "Run Quick Item")
        msgs = [n for n in run["nodes"] if n.get("kind") == "message"]
        self.assertEqual({n["function"] for n in msgs}, {mu.GET_VALUE, mu.ON_CHANGED})
        for k in ("modfield", "modaction"): self.assertIn("qma", after(run, "qb_" + k))


    def test_centre_disc_fills_the_hole_only(self):
        # QUICK_INNER is a share of the RADIUS: the dark centre may cover the ring's hole, never the labels at 68 % of the radius
        import gen_widgets as gw
        a = {x["path"].rsplit("/", 1)[1]: x for x in json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json")))["assets"]}
        def find(n, name):
            if n.get("name") == name: return n
            for c in n.get("children", []):
                r = find(c, name)
                if r: return r
        wheel = find(a["W_QuickWheel"]["widget_tree"], "Wheel")["props"]["WidthOverride"]
        centre = find(a["W_QuickWheel"]["widget_tree"], "CenterBox")["props"]["WidthOverride"]
        self.assertLessEqual(centre / wheel, gw.QUICK_INNER); self.assertGreater(centre / wheel, gw.QUICK_INNER * 0.9)

    def test_row_without_icon_keeps_its_space(self):
        a = {x["path"].rsplit("/", 1)[1]: x for x in json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json")))["assets"]}
        init = next(f for f in a["W_QuickRow"]["functions"] if f["name"] == "Init")["graph"]
        vis = {n["in"]["InVisibility"] for n in init["nodes"] if n.get("function") == "SetVisibility" and "IconBox" in json.dumps(n["in"])}
        self.assertEqual(vis, {"Visible", "Hidden", "Collapsed"})   # Visible with an icon (pooled rows), Hidden for items without, Collapsed only for headings


    def test_initials_without_icon(self):
        a = {x["path"].rsplit("/", 1)[1]: x for x in json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json")))["assets"]}
        g = next(f for f in a["W_QuickSector"]["functions"] if f["name"] == "Init")["graph"]
        self.assertTrue({"ParseIntoArray", "ToUpper"} <= {n.get("function") for n in g["nodes"]})
        bf = next(n for n in g["nodes"] if n["id"] == "bf"); self.assertIn("@shw.", json.dumps(bf))   # name line: few sectors OR no icon



class QuickIcons(unittest.TestCase):
    def test_panel_and_tabs_have_icons(self):
        """"Open AltUI" shows the panel icon, a tab item its tab's icon (the tab bar's textures)."""
        self.assertEqual(ui.QUICK_FIXED_ICON["panel"], ui.T_ALTUI)
        g = graph("50_manager_ui.json", "Quick Item Icon")
        texs = {n["in"]["QTex"] for n in g["nodes"] if n.get("kind") == "set" and "QTex" in n.get("in", {})}
        self.assertTrue(set(ui.TAB_ICONS.values()) | {ui.T_ALTUI} <= texs, texs)
        for page in ui.TOP_TABS: self.assertIn("st_" + page, after(g, "q" + "b_tab"))



class QuickOptionsLook(unittest.TestCase):
    def test_rows_striped_headings_restart(self):
        """Zebra stripes like the slot conflicts: every row gets tinted from QStripe, every heading resets it, the wheel list starts at 0."""
        g = graph("50_manager_ui.json", "Rebuild Quick Options")
        inits = [n for n in g["nodes"] if n.get("function") == "Init" and "mode" in n.get("in", {})]
        self.assertTrue(inits and all("tinted" in n["in"] for n in inits))
        resets = [n for n in g["nodes"] if n.get("kind") == "set" and n.get("var") == "QStripe" and n["in"].get("QStripe") == "0"]
        heads = [n for n in inits if n["in"]["mode"] == "2"]
        self.assertEqual(len(resets), len(heads) + 1)

    def test_key_link_fills_the_widest_text(self):
        import gen_widgets
        self.assertIn(("quickkeywidth", "QuickKeyWidth"), gen_widgets.PANEL_TEXTS); self.assertIn(("quickkeywidth", "Lbl_KeyPress"), ui.PANEL_STRINGS)


    def test_key_text_centred_by_design(self):
        """The link text fills its link and is centred (design time): a runtime alignment is lost in 4.27 before the widget is built."""
        import gen_widgets
        lbl = []
        def walk(t):
            if t.get("name") == "Label": lbl.append(t)
            for c in t.get("children") or []: walk(c)
        walk(gen_widgets.w_text_button()["widget_tree"])
        self.assertEqual(lbl[0]["props"].get("Justification"), "Center"); self.assertIn("Fill", lbl[0]["slot"]["Size"])


if __name__ == "__main__": unittest.main()
