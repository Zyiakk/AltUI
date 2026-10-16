"""2026-10-16: clean copy of a look / updating keeps missing parts, follower hairstyle from the look, measured pose name, repeat poses,
one-row tab bar."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, asset
import gen_widgets as gw


def by_id(g): return {n["id"]: n for n in g["nodes"]}
def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]


class LookMissing(unittest.TestCase):
    def test_update_keeps_what_she_could_not_put_on(self):
        g = mgr_graph("Update Look"); self.assertIn(["entry", "sid", "ts", "km", "stl", "set", "rmi", "sv", "cap", "rl"], g["exec"])
        self.assertEqual(by_id(g)["mk"]["in"]["Snap"], "@km.snap")
        k = mgr_graph("Keep Missing"); self.assertTrue(calls(k, "Can Wear")); self.assertTrue(calls(k, "Find Item"))

    def test_clean_copy_is_a_new_look_after_the_original(self):
        g = mgr_graph("Look Clean Copy"); b = by_id(g)
        self.assertEqual(b["ins"]["function"], "Array_Insert"); self.assertEqual(b["mk"]["in"]["Snap"], "@cs.clean")
        self.assertFalse(calls(g, "Array_Set"))   # the original is never written
        self.assertTrue(calls(g, "ExportRenderTarget"))   # its own photo file

    def test_clean_removes_only_what_is_not_installed(self):
        g = mgr_graph("Clean Snap"); self.assertFalse(calls(g, "Can Wear"))   # not owned stays
        tables = {n["in"]["Table"] for n in calls(g, "DoesDataTableRowExist")}; self.assertEqual(len(tables), 2)

    def test_menu_row_only_with_something_to_clean(self):
        g = mgr_graph("On Look Context"); self.assertTrue(calls(g, "Look Has Missing"))
        self.assertTrue(any("Menu_LookClean" in str(n.get("in")) for n in g["nodes"]))


class FollowerHair(unittest.TestCase):
    def test_poll_waits_for_the_whole_look(self):
        g = mgr_graph("Look Ragdoll Poll"); self.assertEqual(by_id(g)["stn"]["in"]["B"], "@nsp.ReturnValue")

    def test_hairstyle_from_the_look(self):
        b = by_id(mgr_graph("Finish Look Follower")); self.assertEqual(b["hsel"]["in"]["A"], "@hla.ReturnValue"); self.assertEqual(b["hla"]["in"]["InName"], "@lks.Hair")
        self.assertEqual(by_id(mgr_graph("Spawn Look Follower"))["sli"]["var"], "FolLookIdx")


class Poses(unittest.TestCase):
    def test_scan_link_names_the_pose(self):
        g = mgr_graph("Scan Tick"); self.assertTrue(any(c[:5] == ["bd:else", "sinc", "pt", "stt", "pc"] for c in g["exec"]))

    def test_loop_restarts_only_on_a_natural_end(self):
        g = mgr_graph("Pose Loop Tick"); b = by_id(g)
        self.assertEqual(b["nn"]["in"]["B"], "None"); self.assertEqual(b["cr"]["in"]["B"], "@glr.LoopRow")
        self.assertIn(["entry", "b0", "bours", "bend", "skeep", "sp", "play", "srow"], g["exec"])
        self.assertTrue(any("slr" in c for c in mgr_graph("Pose Clicked")["exec"]))


class OneRowTabs(unittest.TestCase):
    def test_steps_shrink_then_cut(self):
        sizes = [s // 100 for s in gw.TOP_FIT_STEPS]; self.assertEqual(sizes, sorted(sizes, reverse=True))
        self.assertEqual(gw.TOP_FIT_STEPS[0] % 100, 0); self.assertEqual(gw.TOP_FIT_STEPS[-1] % 100, 4)

    def test_tab_keeps_its_full_caption(self):
        names = {f["name"] for f in asset(gw.W_TOP)["functions"]}; self.assertIn("Set Fit", names)


class TabRowChips(unittest.TestCase):
    def test_chip_click_reaches_select_tab_style(self):
        """TabRow0/1 went to Select Layout at first (the dispatcher knew only TabStyle / TabIconPos)."""
        import json
        from test_fol_tab import assets
        found = False
        for a in assets():
            for f in a.get("functions", []):
                g = f.get("graph") or {}
                if any(n.get("in", {}).get("InPrefix") == "TabRow" for n in g.get("nodes", [])): found = True
        self.assertTrue(found)


class BackgroundLayers(unittest.TestCase):
    """ui-test-105: the background colour lies over the picture, each with its own opacity slider."""
    def test_bg_colour_is_left_alone(self):
        sbi = next(f["graph"] for f in asset(gw.W_PANEL)["functions"] if f["name"] == "Set Bg Image")
        self.assertFalse(any(n.get("function") == "SetBrushColor" for n in sbi["nodes"]))

    def test_pattern_opacity_slider(self):
        self.assertIn(("BgImgAlpha", "Pattern opacity"), gw.OPTION_ROWS); self.assertIn("RowBgImgAlpha", gw.OPT_CAT_ROWS["Theme"])
        b = by_id(mgr_graph("Apply Bg Image")); self.assertEqual(b["set"]["in"]["alpha"], "@ga.BgImgAlpha")

    def test_thirty_own_files_and_card_stock(self):
        import theme_images as ti
        self.assertEqual(ti.USER_MAX, 30)
        for k in ("Bone", "Eggshell", "Laid", "Nimbus", "Emboss"):
            self.assertIn(k, [b[0] for b in ti.BACKGROUNDS]); self.assertIn(k, [b[0] for b in ti.BUTTONS])


class PictureFilters(unittest.TestCase):
    """Hue / sepia / invert for both pictures (M_ImageBox), and the pattern opacity text (showed 0 %: a second pct_text with another
    signature further down the file took over)."""
    def test_opacity_text_is_a_percentage(self):
        for name in ("Rebuild Options", "Poll Options"):
            n = next(n for n in mgr_graph(name)["nodes"] if n.get("function") == "Set Option Values")
            self.assertEqual(n["in"]["bgimgalpha text"], "@ox_bia_t.ReturnValue", name)

    def test_filters_on_both_instances(self):
        for name in ("Apply Bg Image", "Apply Button Image"):
            pars = {n["in"].get("ParameterName") for n in mgr_graph(name)["nodes"] if n.get("function") == "SetScalarParameterValue"}
            self.assertLessEqual({"Hue", "Sepia", "Invert"}, pars, name)

    def test_background_draws_through_the_material(self):
        sbi = next(f["graph"] for f in asset(gw.W_PANEL)["functions"] if f["name"] == "Set Bg Image")
        self.assertEqual(sum(1 for n in sbi["nodes"] if n.get("function") == "SetBrushResourceToMaterial"), 2)


class ThemeSections(unittest.TestCase):
    """2026-10-16: Options > Theme in sections (colours, background picture, button picture, schemes), reset in the status bar."""
    def test_sections_group_their_rows(self):
        rows = gw.OPT_CAT_ROWS["Theme"]
        for sec, members in (("SecThemeColors", ["ThemeGrid", "RowBgAlpha", "RowTileAlpha"]), ("SecBgPic", ["RowBgImage", "RowBgImgAlpha", "RowBgFit", "RowBgInv"]),
                             ("SecBtnPic", ["RowBtnImage", "RowBtnHue", "RowBtnInv"]), ("SecThemeSchemes", ["RowThemeSave", "RowThemePresets"])):
            i = rows.index(sec); nxt = min([rows.index(s) for s in ("SecThemeColors", "SecBgPic", "SecBtnPic", "SecThemeSchemes") if rows.index(s) > i] + [len(rows)])
            for m in members: self.assertTrue(i < rows.index(m) < nxt, (sec, m))
        self.assertNotIn("ThemeLinks", rows)

    def test_reset_in_the_status_bar(self):
        g = mgr_graph("Rebuild Status"); b = by_id(g)
        self.assertEqual(b["tri"]["in"]["action"], "ThemeReset")
        self.assertTrue(any(n.get("function") == "Rebuild Status" for n in mgr_graph("Select Option Cat")["nodes"]))


class ThemesWithPictures(unittest.TestCase):
    """ui-test-105 round 4: saved themes keep the pictures too; the hint stands before both picture sections; filters in gamma space."""
    def test_save_and_apply_carry_the_pictures(self):
        mk = by_id(mgr_graph("Save Theme Preset"))["mk"]["in"]; self.assertEqual(mk["HasImages"], "true"); self.assertEqual(mk["BtnInvert"], "@giBtnInvert.BtnInvert")
        g = mgr_graph("Apply Theme Preset"); self.assertEqual(by_id(g)["bhi"]["in"]["Condition"], "@br.HasImages")

    def test_hint_before_the_picture_sections(self):
        rows = gw.OPT_CAT_ROWS["Theme"]; self.assertLess(rows.index("LblImgHint"), rows.index("SecBgPic")); self.assertGreater(rows.index("LblImgHint"), rows.index("RowTileAlpha"))

    def test_filters_in_gamma_space(self):
        src = open(os.path.join(H, "..", "..", "scripts", "quickmenu", "material.py")).read()
        self.assertIn("pow(saturate(C), 1.0 / 2.2)", src)


class FreeCamOptions(unittest.TestCase):
    """2026-10-16: Options > Camera - free camera without collision / at any distance from Jodi."""
    def test_rows_and_settings(self):
        self.assertLessEqual({"RowFreeNoCollide", "RowFreeNoLimit"}, set(gw.OPT_CAT_ROWS["Camera"]))
        import gen_manager
        rows = {m for m, _, _, _ in gen_manager.SETTINGS}; self.assertLessEqual({"FreeNoCollide", "FreeNoLimit"}, rows)

    def test_step_honours_both(self):
        g = mgr_graph("Free Cam Step"); b = by_id(g)
        self.assertEqual(b["tgt"]["in"]["bPickA"], "@gfnl.FreeNoLimit"); self.assertEqual(b["tr"]["in"]["End"], "@tgt.ReturnValue")
        self.assertIn(["bnc:else", "tr", "bh", "bio", "baw", "sl2"], g["exec"]); self.assertEqual(b["slnc"]["in"]["NewLocation"], "@tgt.ReturnValue")


class NoNotices(unittest.TestCase):
    """2026-10-16: Options > General 'No notices' - AltUI's are not raised, the game's notice widget stays invisible."""
    def test_pop_notice_stops_first(self):
        g = mgr_graph("Pop Notice"); self.assertIn(["entry", "bnn"], g["exec"]); self.assertEqual(by_id(g)["bnn"]["in"]["Condition"], "@gnn.NoNotices")

    def test_tick_keeps_the_game_widget_hidden(self):
        b = by_id(mgr_graph("Notice Tick")); self.assertEqual(b["want"]["in"]["bPickA"], "@gnn.NoNotices")
        self.assertIn("RowNoNotices", gw.OPT_CAT_ROWS["General"])


class MercenaryCopy(unittest.TestCase):
    """ui-test-105 #9: the Mercenary's gun hangs on GunSocket (a component, socket None) - it went to the figure's origin; shots heard."""
    def test_helper_component_goes_relative_to_its_bone(self):
        g = mgr_graph("Finish Zombie Ragdoll"); self.assertIn(["bonm:else", "shb", "srl", "det2", "att2", "srt2"], g["exec"])
        self.assertEqual(by_id(g)["att2"]["in"]["SocketName"], "@gsb2.RagSockTmp")

    def test_no_ai_while_waiting(self):
        g = mgr_graph("Look Ragdoll Poll"); self.assertIn(["entry", "bzp", "zpa", "bzg", "zdc", "c0"], g["exec"])
