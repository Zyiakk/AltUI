"""Actions tab: the quick menu settings in a tab of their own (docs/superpowers/specs/2026-10-26-actions-tab-design.md)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_weapon_look_melee import function
from test_options_cats import graph, after, calls
import vlist as vl


def nodes(g): return {x["id"]: x for x in g["nodes"]}


class ScrollOff(unittest.TestCase):
    def test_state_var(self):
        v = {x["name"]: x for x in vl.state_vars("Qa")}
        self.assertIn("QaScrollOff", v); self.assertEqual(v["QaScrollOff"]["type"], "float")

    def test_scroll_to_adds_the_offset_and_clears_it(self):
        for L in ("Qa", "Ofl", "Clo"):
            g = function(L + " Window Update"); n = nodes(g)
            self.assertEqual(n["sd2"]["function"], "Add_FloatFloat", L)
            self.assertEqual(n["sd2"]["in"], {"A": "@sd1.ReturnValue", "B": "@gsof.%sScrollOff" % L}, L)
            self.assertEqual(n["sby"]["in"]["delta"], "@sd2.ReturnValue", L)
            self.assertEqual(n["ssof"]["in"], {L + "ScrollOff": "0.0"}, L)
            self.assertTrue(any(c[c.index("sstn"):c.index("sstn") + 2] == ["sstn", "ssof"] for c in g["exec"] if "sstn" in c), L)


import gen_widgets as gw, gen_manager, gen_manager_ui as ui
from strings import STRINGS, LANGS


def wfn(name):
    """A function of the widget blueprints (40_widgets.json)."""
    return graph("40_widgets.json", name)


class Tab(unittest.TestCase):
    def test_after_options(self):
        self.assertEqual(ui.TOP_TABS[ui.TOP_TABS.index("Options") + 1], "Actions")

    def test_strings(self):
        for k in ("Tab_Actions", "Act_NoHits"): self.assertEqual(len(STRINGS[k]), len(LANGS), k)
        self.assertNotIn("OptCat_Quick", STRINGS)

    def test_options_without_quick(self):
        self.assertNotIn("Quick", gw.OPT_CATS); self.assertNotIn("Quick", gw.OPT_CAT_ROWS)
        g = graph("50_manager_ui.json", "Rebuild Options"); self.assertEqual(calls(g, "Rebuild Quick Options"), [])

    def test_page_and_scroll(self):
        self.assertIn("ActScroll", gw.SCROLL_PAGES); self.assertIn("ActCatScroll", gw.SCROLL_PAGES)
        w = json.dumps(json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json"))))
        for wn in ("ActionsBox", "ActCats", "ActSearch", "ActHint", "ActScroll", "ActWheelBlock", "ActKeysBlock", "QuickAvailable"): self.assertIn('"%s"' % wn, w, wn)

    def test_qa_bound_to_act_scroll(self):
        g = wfn("Qa View"); self.assertTrue(any(x.get("var") == "ActScroll" for x in g["nodes"]))

    def test_qa_visible_on_actions(self):
        g = function("Qa Window Update")
        self.assertTrue(any(x.get("function") == "EqualEqual_NameName" and "Actions" in x.get("in", {}).values() for x in g["nodes"]))
        self.assertTrue(any(x.get("function") == "Act Avail" for x in g["nodes"]))

    def test_settings(self):
        rows = {(m, s): (k, d) for m, s, k, d in gen_manager.SETTINGS}
        self.assertEqual(rows[("ActCat", "LastActCat")], ("name", None))

    def test_options_cat_quick_falls_back(self):
        g = graph("30_manager.json", "Load Settings")
        eq = [x for x in g["nodes"] if x.get("function") == "EqualEqual_NameName" and x.get("in", {}).get("B") == "Quick"]
        self.assertEqual(len(eq), 1)
        st = [x for x in g["nodes"] if x.get("kind") == "set" and x.get("var") == "OptionsCat" and "General" in json.dumps(x)]
        self.assertEqual(len(st), 1)


class CatalogFilter(unittest.TestCase):
    def test_no_more_rebuild_quick_available(self):
        self.assertFalse(any(f["name"] == "Rebuild Quick Available" for a in json.load(open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")))["assets"] for f in a.get("functions", [])))
        g = function("Rebuild Quick Options"); self.assertEqual(calls(g, "Rebuild Quick Available"), []); self.assertEqual(len(calls(g, "Act Refresh")), 1)

    def test_catalog_captions_once(self):
        g = function("Act Catalog Build")
        self.assertGreaterEqual(len(calls(g, "Quick Item Caption")), 1)
        get = {x["id"]: x.get("var") for x in g["nodes"] if x.get("kind") == "get"}
        adds = {get.get(x["in"]["TargetArray"][1:].split(".")[0]) for x in g["nodes"] if x.get("function") in ("Array_Add", "Array_AddUnique")}
        self.assertTrue({"QcItems", "QcCat", "QcCap", "ActCats"} <= adds, adds)

    def test_filter_is_strings_only(self):
        g = function("Act Filter")
        for f in ("Quick Find", "Quick Item Caption", "Quick Item Icon"): self.assertEqual(calls(g, f), [], f)
        c = [x for x in g["nodes"] if x.get("function") == "Contains"]; self.assertEqual(len(c), 1)
        self.assertEqual(c[0]["in"]["bUseCase"], "false"); self.assertIn("QcCap", json.dumps(g))
        sets = {x.get("var") for x in g["nodes"]}; self.assertTrue({"QaRowsDirty", "QaDirty"} <= sets)

    def test_refresh_only_dirty(self):
        g = function("Act Refresh"); self.assertEqual(calls(g, "Act Filter"), []); self.assertEqual(calls(g, "Act Catalog Build"), [])
        self.assertIn("QaDirty", {x.get("var") for x in g["nodes"]})


class LeftColumn(unittest.TestCase):
    def test_select_slot_branch(self):
        g = function("Select Slot"); n = nodes(g)
        sac = [k for k, x in n.items() if x.get("function") == "Select Act Cat"]; self.assertEqual(len(sac), 1)
        br = [k for k, x in n.items() if x.get("function") == "EqualEqual_NameName" and x["in"].get("B") == "Actions"]; self.assertEqual(len(br), 1)
        self.assertIn(sac[0], after(g, "bpob:else"))

    def test_select_page_branch(self):
        g = graph("50_manager_ui.json", "Select Page"); n = nodes(g)
        for k, f in (("accb", "Act Catalog Build"), ("acrc", "Rebuild Act Cats"), ("acsc", "Set Act Cat"), ("acrq", "Rebuild Quick Options")): self.assertEqual(n[k]["function"], f)
        c = next(c for c in g["exec"] if "accb" in c); idx = [c.index(k) for k in ("bAct", "accb", "acrc", "acsc", "acrq") if k in c]
        self.assertEqual(len(idx), 5); self.assertEqual(idx, sorted(idx))   # in this order (Task 5 / 6 add steps in between)

    def test_select_act_cat(self):
        g = function("Select Act Cat"); n = nodes(g)
        order = [n[k].get("function") or n[k].get("var") for c in g["exec"] for k in c if k in n]
        for f in ("ActCat", "Set Act Cat", "Rebuild Act Cats", "Act Filter", "Save Settings"): self.assertIn(f, order, f)
        self.assertLess(order.index("ActCat"), order.index("Act Filter"))

    def test_left_rows(self):
        g = function("Rebuild Act Cats"); s = json.dumps(g)
        for k in ("Lbl_QuickInWheel", "Lbl_KeyBinds", "Lbl_QuickAvailable", "Obj_All", "QuickGrp_ModActions"): self.assertIn(k, s, k)
        self.assertIn("ActCatN", s); self.assertIn("ActHitN", s)

    def test_gone_mod_falls_back_to_all(self):
        g = function("Act Catalog Build")
        self.assertTrue(any(x.get("kind") == "set" and x.get("var") == "ActCat" and x["in"].get("ActCat") == "All" for x in g["nodes"]))


class Search(unittest.TestCase):
    def test_key_up_reads_act_search(self):
        ku = next(f["graph"] for a in json.load(open(os.path.join(H, "..", "..", "assets", "40_widgets.json")))["assets"] if a["path"].endswith("/W_AltUI") for f in a.get("functions", []) if f["name"] == "OnKeyUp")
        self.assertTrue(any(x.get("function") == "On Act Search Changed" for x in ku["nodes"]))
        self.assertTrue(any(x.get("function") == "HasKeyboardFocus" and "ActSearch" in json.dumps(x) for x in ku["nodes"]))

    def test_changed_filters_and_goes_to_top(self):
        g = function("On Act Search Changed"); fs = [x.get("function") for x in g["nodes"]]
        for f in ("Act Filter", "Rebuild Act Cats", "Act Scroll Top"): self.assertIn(f, fs, f)
        self.assertIn("ActSearchText", {x.get("var") for x in g["nodes"]})

    def test_clear_action(self):
        g = graph("50_manager_ui.json", "On Menu Action"); self.assertIn("ClearActSearch", json.dumps(g))

    def test_clear_link_built_on_entering(self):
        g = graph("50_manager_ui.json", "Select Page")
        self.assertTrue(any(x.get("function") == "Init" and x.get("in", {}).get("action") == "ClearActSearch" for x in g["nodes"]))


class Anchor(unittest.TestCase):
    def test_save_reads_the_top_row(self):
        s = json.dumps(function("Act Anchor Save"))
        for v in ("QaA", "QaRowStart", "QaRowY", "QaVTop", "ActAnchorKey", "ActAnchorOff"): self.assertIn(v, s, v)

    def test_restore_sets_scroll_to_with_air(self):
        g = function("Act Anchor Restore")
        so = [x for x in g["nodes"] if x.get("var") == "QaScrollOff" and x.get("kind") == "set"]; self.assertEqual(len(so), 1)
        self.assertTrue(any(x.get("function") == "Add_FloatFloat" and str(float(ui.sz(8))) in x["in"].values() for x in g["nodes"]))
        self.assertTrue(any(x.get("function") == "Act Scroll Top" for x in g["nodes"]))   # key gone -> top

    def test_wiring(self):
        g = function("Select Act Cat"); n = nodes(g); fs = [n[k].get("function") or n[k].get("var") for c in g["exec"] for k in c if k in n]
        self.assertLess(fs.index("Act Anchor Save"), fs.index("ActCat")); self.assertLess(fs.index("Act Filter"), fs.index("Act Anchor Restore"))
        sp = graph("50_manager_ui.json", "Select Page"); self.assertTrue(calls(sp, "Act Anchor Save")); self.assertTrue(calls(sp, "Act Anchor Restore"))
        self.assertTrue(calls(function("Close Panel"), "Act Anchor Save"))
        self.assertIn("ActAnchorKey", json.dumps(function("On Act Search Changed")))
        self.assertIn("ActAnchorKey", json.dumps(graph("50_manager_ui.json", "On Menu Action")))


class PlayTest175(unittest.TestCase):
    """Findings of the play test (open-since-2.8.0: 173.1, 173.8, 175.3, 175.4, 175.5, 175.10)."""
    def test_keys_wait_on_the_actions_tab(self):
        n = nodes(function("Capturing Key"))
        self.assertEqual(n["iso"]["in"]["B"], "Actions")

    def test_opacity_row_polled_on_the_actions_tab(self):
        g = function("Poll Quick Alpha"); self.assertTrue(calls(g, "Set Quick Alpha")); self.assertIn("QuickAlpha", json.dumps(g))
        self.assertTrue(calls(graph("50_manager_ui.json", "Select Page"), "Show Quick Alpha"))
        self.assertIn("Poll Quick Alpha", json.dumps(json.load(open(os.path.join(H, "..", "..", "assets", "50_manager_ui.json")))))
        self.assertIn("ValQuickAlpha", json.dumps(wfn("Set Quick Alpha")))

    def test_mod_prefix_ignores_case(self):   # a name keeps the spelling of its first use: "mod:<pak>" from the Objects tab
        for f in ("Rebuild Act Cats", "Act Catalog Build", "Act Avail"):
            for x in function(f)["nodes"]:
                if x.get("function") == "StartsWith" and x["in"].get("InPrefix") == "Mod:": self.assertEqual(x["in"]["SearchCase"], "IgnoreCase", f)

    def test_hand_reset_link_built_for_hand(self):
        g = graph("50_manager_ui.json", "Rebuild Options")
        pairs = {(a, b) for c in g["exec"] for a, b in zip(c, c[1:])}
        self.assertIn(("boc_Hand", "chl"), pairs); self.assertFalse(any(b == "chl" and a != "boc_Hand" for a, b in pairs))
        self.assertEqual(gw.VAL_W["HandRange"], gw.VAL_W["HandBatch"]); self.assertGreaterEqual(gw.VAL_W["HandRange"], 130)


if __name__ == "__main__": unittest.main()
