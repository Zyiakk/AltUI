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
        self.assertEqual(ui.QUICK_MAX, 32); self.assertEqual(ui.QUICK_FIXED, ["freecam", "photo", "panel", "posestop", "ragdoll", "ragdolltoggle", "ragdollclear", "ragdollmode", "ragdollaim", "speedtoggle", "folfollow", "folwait", "folallfollow", "folallwait", "slowmo", "freeze", "hidejodi", "hideui"])

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
        self.assertIn(["kAny:Pressed", "kbr", "bq", "oqw"], eg["exec"])   # own keys (Bind Run) first
        bq = next(n for n in eg["nodes"] if n["id"] == "bq"); self.assertIn("@qb.", json.dumps(bq))
        qb = next(n for n in eg["nodes"] if n["id"] == "qb"); self.assertEqual(qb["in"], {"A": "@qa.ReturnValue", "B": "@ie.yes"})


    def test_options_block(self):
        import gen_widgets
        self.assertEqual(gen_widgets.OPT_CAT_ROWS["Quick"], ["LblQuickControl", "RowQuickKey", "RowQuickAlpha", "LblQuickInWheel", "QuickInWheel", "LblKeyBinds", "KeyBindHint", "KeyBinds", "LblQuickAvailable", "QuickAvailable"])
        g = graph("50_manager_ui.json", "Rebuild Options"); c = calls(g, "Rebuild Quick Options"); self.assertEqual(len(c), 1)
        eqs = {n["id"] for n in g["nodes"] if n.get("function") == "EqualEqual_NameName" and "Quick" in n.get("in", {}).values()}
        br = [n["id"] for n in g["nodes"] if n.get("kind") == "branch" and any(("@%s." % e) in json.dumps(n) for e in eqs)]
        self.assertEqual(len(br), 1); self.assertIn(c[0], after(g, br[0])); self.assertNotIn(c[0], after(g, br[0] + ":else"))

    def test_menu_actions(self):
        g = graph("50_manager_ui.json", "On Menu Action"); self.assertIn(calls(g, "Quick Action")[0], after(g, "bq"))
        prefixes = {n["in"]["InPrefix"] for n in g["nodes"] if n.get("function") == "StartsWith"}
        self.assertTrue({"QKey", "QUp:", "QDown:", "QDel:", "BKey:", "BDel:"} <= prefixes)
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
        """Zebra stripes like the slot conflicts: every row gets tinted from QStripe, every heading resets it, the wheel list and the own keys start at 0."""
        g = graph("50_manager_ui.json", "Rebuild Quick Options")
        inits = [n for n in g["nodes"] if n.get("function") == "Init" and "mode" in n.get("in", {})]
        self.assertTrue(inits and all("tinted" in n["in"] for n in inits))
        resets = [n for n in g["nodes"] if n.get("kind") == "set" and n.get("var") == "QStripe" and n["in"].get("QStripe") == "0"]
        heads = [n for n in inits if n["in"]["mode"] == "2"]
        self.assertEqual(len(resets), len(heads) + 2)

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



class MenuClosesOnOtherTile(unittest.TestCase):
    def test_preview_click_closes_menu(self):
        """2026-10-16: a click on another tile closes an open context menu - the panel's preview (tunnel) handler, before the tile."""
        a = next(x for x in json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json")))["assets"] if x["path"].endswith("/W_AltUI"))
        g = next(f for f in a["functions"] if f["name"] == "OnPreviewMouseButtonDown")["graph"]
        self.assertIn(["entry", "cm", "bc", "cn", "return"], g["exec"])
        self.assertEqual(next(n for n in g["nodes"] if n["id"] == "cm")["function"], "Close Menu")
        self.assertEqual(next(n for n in g["nodes"] if n["id"] == "u")["function"], "Unhandled")   # the tile still gets the click


class OwnKeysCam(unittest.TestCase):
    def test_free_cam_hands_keys_on(self):
        """2026-10-16 ui-test-102 #7: the free cam's BP_CamInput consumes every key - its Pressed goes to Bind Run."""
        a = next(x for x in json.load(open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")))["assets"] if x["path"].endswith("/BP_CamInput"))
        eg = a["event_graph"]; self.assertIn(["k:Pressed", "bp0"], eg["exec"])
        self.assertEqual(next(n for n in eg["nodes"] if n["id"] == "bp0")["function"], "Bind Run")

    def test_stop_time_holds_the_photo_camera(self):
        """2026-10-16 ui-test-102 #9: the photo mode opens paused - the manager ticks when paused and then runs only Time Tick, which
        keeps the photo mode camera (Camera_Free, ticks when paused) at real speed."""
        g = graph("50_manager_ui.json", "Time Tick"); cpm = next(n for n in g["nodes"] if n["id"] == "cpm")
        self.assertEqual((cpm["var"], cpm["in"]["CustomTimeDilation"]), ("CustomTimeDilation", "@comp.ReturnValue"))
        eg = next(x for x in json.load(open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")))["assets"] if x["path"].endswith("/BP_AltUIManager"))["event_graph"]
        self.assertIn(["tick", "tbpz", "tpzt"], eg["exec"]); self.assertEqual(next(n for n in eg["nodes"] if n["id"] == "tpzt")["function"], "Time Tick")
        self.assertIn("tkwp", next(c for c in eg["exec"] if c[0] == "bvg"))


class OwnKeys(unittest.TestCase):
    """2026-10-15: own keys - key -> any quick menu item, saved; bound by a right click on an available item."""
    def test_saved(self):
        src = open(os.path.join(H, "..", "..", "assets", "gen", "gen_manager.py")).read()
        self.assertIn('("KeyBindKeys", "KeyBindKeys", "copy", None), ("KeyBindItems", "KeyBindItems", "copy", None)', src)

    def test_run_only_when_free(self):
        g = graph("50_manager_ui.json", "Bind Run")
        self.assertEqual(calls(g, "Run Quick Item"), ["run"]); self.assertIn(["entry", "b", "sr", "run"], g["exec"])
        ins = {n["id"]: n["in"] for n in g["nodes"] if "in" in n}
        self.assertEqual(ins["o1"], {"A": "@pnl.ReturnValue", "B": "@gqo.QuickOpen"}); self.assertEqual(ins["pnl"], {"A": "@gpo.PanelOpen", "B": "@cm0.ReturnValue"})   # camera modes: collapsed panel counts as closed
        self.assertEqual(ins["o2"]["B"], "@gso.SceneOn"); self.assertEqual(ins["o3"]["B"], "@ck.yes")

    def test_taken_keys_refused(self):
        g = graph("50_manager_ui.json", "Bind Key Captured"); ins = {n["id"]: n.get("in", {}) for n in g["nodes"]}
        self.assertEqual(ins["o2"], {"A": "@o1.ReturnValue", "B": "@e3.ReturnValue"})   # panel key / quick key / another item's key
        self.assertIn(["entry", "bt", "sht", "sb"], g["exec"])

    def test_right_click_binds(self):
        w = next(x for x in json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json")))["assets"] if x["path"].endswith("/W_QuickRow"))
        md = next(f for f in w["functions"] if f["name"] == "OnMouseButtonDown")["graph"]
        self.assertIn(["entry", "b", "br", "kb", "return"], md["exec"]); self.assertIn(["br:else", "t", "return"], md["exec"])


if __name__ == "__main__": unittest.main()
