"""2026-11-09 (internal design notes): context menus scroll when taller than the screen,
outfits can be updated with what she wears, "Update (keep photo)" wherever there is "Update (photo from the front)". The outfit
ids on the real Blueprints: tests/editor/test_outfit_ids.py."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, asset, fn_graph
import gen_manager_ui as ui, strings

M = "/Game/Mod/AltUI"
KEEP = {"Look": "Update Look", "Preset": "Update Preset", "ModPreset": "Update Mod Preset", "Face": "Update Face", "BodyPreset": "Update Body Preset"}
MENUS = {"Look": "On Look Context", "Preset": "On Preset Context", "ModPreset": "On Mod Preset Context", "Face": "On Face Context", "BodyPreset": "On Body Preset Context"}


def by_id(g): return {n["id"]: n for n in g["nodes"]}
def row_actions(g): return [n["in"].get("action") for n in g["nodes"] if n.get("function") == "Init" and "action" in n.get("in", {})]


class ContextMenuScrolls(unittest.TestCase):
    def test_rows_sit_in_a_capped_scroll_box(self):
        a = asset(M + "/W_ContextMenu")
        def find(n, name):
            if n.get("name") == name: return n
            for c in n.get("children") or []:
                r = find(c, name)
                if r: return r
        t = a["widget_tree"]; box = find(t, "RowsBox"); self.assertEqual(box["class"], "/Script/UMG.SizeBox")
        sc = box["children"][0]; self.assertEqual((sc["class"], sc["name"]), ("/Script/UMG.ScrollBox", "RowsScroll"))
        self.assertEqual(sc["children"][0]["name"], "Rows")
        g = fn_graph(M + "/W_ContextMenu", "Place At"); b = by_id(g)
        self.assertEqual(b["smh"]["function"], "SetMaxDesiredHeight")
        self.assertIn(["entry", "vg", "smh", "fl", "sp"], g["exec"])   # capped before the layout prepass that measures it


class UpdateKeepPhoto(unittest.TestCase):
    def test_every_update_skips_icon_and_photo_when_keeping(self):
        for k, name in KEEP.items():
            g = mgr_graph(name); b = by_id(g)
            self.assertIn("@gk.PhotoKeep", b["bk"]["in"].values(), k)
            els = [c for c in g["exec"] if c[0] == "bk:else"]; self.assertEqual(len(els), 1, k)
            self.assertIn("rmi", els[0], k)   # the icon cache entry only goes on the photo path
            on_keep = [c for c in g["exec"] if "bk" in c and c[0] != "bk:else"]; self.assertTrue(on_keep, k)
            self.assertNotIn("rmi", on_keep[0][on_keep[0].index("bk"):], k)

    def test_keep_wrappers_set_and_clear_the_flag(self):
        for k, name in KEEP.items():
            g = mgr_graph(name + " Keep"); b = by_id(g)
            self.assertEqual(b["u"]["function"], name)
            self.assertIn(["entry", "on", "u", "off"], g["exec"])

    def test_menus_and_actions(self):
        acts = {a: f for a, f, _ in ui.MENU_ACTIONS}
        for k, name in KEEP.items():
            self.assertEqual(acts[k + "UpdateKeep"], name + " Keep")
            r = row_actions(mgr_graph(MENUS[k])); self.assertIn(k + "UpdateKeep", r, k)
            self.assertEqual(r.index(k + "UpdateKeep"), r.index(k + "UpdateView") + 1, k)

    def test_texts(self):
        for key in ("Menu_UpdateKeep", "Menu_Update"):
            self.assertEqual(len(strings.STRINGS[key]), 7); self.assertTrue(all(strings.STRINGS[key]), key)   # six languages + French


class OutfitUpdate(unittest.TestCase):
    def test_menu_row_after_rename(self):
        r = row_actions(mgr_graph("On Outfit Context")); self.assertEqual(r.index("OutfitUpdate"), r.index("OutfitRename") + 1)
        self.assertEqual({a: f for a, f, _ in ui.MENU_ACTIONS}["OutfitUpdate"], "Update Outfit")

    def test_update_appends_with_the_game_then_replaces(self):
        g = mgr_graph("Update Outfit"); b = by_id(g)
        self.assertEqual(b["ap"]["function"], "Add Preset")
        self.assertIn(["entry", "bov", "e", "sb", "ap", "rp", "sv", "ro"], g["exec"])   # ids before the append

    def test_replace_rekeys_and_renews_colours(self):
        g = mgr_graph("Replace Outfit With Last"); b = by_id(g)
        self.assertIn(["entry", "bok", "set", "rm", "rk", "oi", "so", "ck", "sck", "fc"], g["exec"])
        self.assertEqual(b["rk"]["function"], "Rekey Outfit Ids"); self.assertEqual(b["roc"]["function"], "Remember Outfit Colors")
