"""Body presets (internal design notes): presets per body chip on the Body Shape page."""
import json, os, sys, unittest
H = os.path.dirname(os.path.abspath(__file__)); ASSETS = os.path.join(H, "..", "..", "assets")
sys.path.insert(0, os.path.join(ASSETS, "gen"))
import body_presets as bp


def assets(f):
    with open(os.path.join(ASSETS, f)) as fh: return json.load(fh)["assets"]


def asset(path):
    for f in ("10_stubs.json", "30_manager.json", "40_widgets.json", "50_manager_ui.json"):
        for a in assets(f):
            if a.get("path") == path: return a
    raise AssertionError(path)


def fn_graph(name):
    for f in ("30_manager.json", "50_manager_ui.json"):
        for a in assets(f):
            for e in a.get("functions", []):
                if e.get("name") == name and e.get("graph"): return e["graph"]
    raise AssertionError(name)


def nodes(g, **kw): return [n for n in g["nodes"] if all(n.get(k) == v for k, v in kw.items())]


def members(a): return [m["name"] for m in a.get("members", a.get("fields", []))]


def var_names(a): return [v["name"] for v in a.get("variables", [])]


class Data(unittest.TestCase):
    def test_struct(self):
        self.assertEqual(members(asset(bp.S_BODYPRESET)), [n for n, _ in bp.MEMBERS])

    def test_save_game(self):
        self.assertEqual(var_names(asset(bp.SG_BODYPRESETS)), ["Version", "NextId", "Presets"])

    def test_folded_is_a_setting(self):
        import gen_manager as gm
        self.assertIn(("BodyPresetsFolded", "BodyPresetsFolded", "copy", None), gm.SETTINGS)
        self.assertIn("BodyPresetsFolded", var_names(asset("/Game/Mod/AltUI/SG_AltUI")))


class Store(unittest.TestCase):
    def test_load_never_writes(self):
        g = fn_graph("Load Body Presets")
        for f in ("DoesSaveGameExist", "LoadGameFromSlot", "CreateSaveGameObject"): self.assertTrue(nodes(g, function=f), f)
        self.assertFalse(nodes(g, function="SaveGameToSlot"))
        self.assertTrue(any(n.get("function") == "NotEqual_IntInt" and n.get("in", {}).get("B") == str(bp.VERSION) for n in g["nodes"]))
        self.assertTrue(any(n.get("in", {}).get("SlotName") == bp.SLOT for n in g["nodes"]))

    def test_save_reports_failure(self):
        g = fn_graph("Save Body Presets")
        self.assertEqual(len(nodes(g, function="SaveGameToSlot")), 1)
        self.assertTrue(nodes(g, kind="call_self", function="Pop Notice"))


class Ops(unittest.TestCase):
    def test_tiles_only_this_body(self):
        g = fn_graph("Collect Body Preset Tiles"); js = json.dumps(g)
        self.assertIn("CurrentBody", js); self.assertTrue(nodes(g, function="EqualEqual_NameName")); self.assertTrue(nodes(g, function="Array_Add"))
        self.assertFalse([n for n in g["nodes"] if "Panel" in json.dumps(n)], "no panel here")

    def test_add_takes_all_sliders(self):
        g = fn_graph("Add Body Preset"); js = json.dumps(g)
        self.assertTrue(nodes(g, kind="call_self", function="Body Scale Factors"))
        for k in ("Boobs Size", "Waist", "NextId", "CurrentBody"): self.assertIn(k, js)
        self.assertTrue(nodes(g, kind="call_self", function="Save Body Presets")); self.assertTrue(nodes(g, kind="call_self", function="Capture Body Preset Photo"))

    def test_update_keeps_name_and_id(self):
        js = json.dumps(fn_graph("Update Body Preset"))
        self.assertIn('"Name": "@bb.Name"', js); self.assertIn('"Id": "@gid.TmpI"', js); self.assertIn('"Body": "@bb.Body"', js)
        self.assertIn("BodyPresetIcons", js)

    def test_apply_sets_factors_and_breast_waist(self):
        g = fn_graph("Apply Body Preset Data"); js = json.dumps(g)
        self.assertTrue(nodes(g, kind="call_self", function="Set Body Scale Factors"))
        self.assertTrue(nodes(g, kind="call_self", function="Body Scale Factors"))   # pads an older, shorter array
        for k in ('"var": "Boobs Size"', '"var": "Waist"', '"var": "BoobsChanged"', '"var": "MakeupDirty"'): self.assertIn(k, js)
        self.assertTrue(nodes(g, kind="call_self", function="Refresh Body Page")); self.assertTrue(nodes(g, kind="call_self", function="Save Appearance Data"))

    def test_rename_cuts_to_max(self):
        js = json.dumps(fn_graph("Set Body Preset Name")); self.assertIn('"Count": "%d"' % bp.NAME_MAX, js)


class Photo(unittest.TestCase):
    def test_capture(self):
        g = fn_graph("Capture Body Preset Photo"); js = json.dumps(g)
        self.assertIn(bp.PHOTO_DIR, js); self.assertIn('"PhotoKind": "%s"' % bp.PHOTO_KIND, js)
        self.assertTrue(nodes(g, kind="call_self", function="Capture Photo"))

    def test_icon_cached(self):
        g = fn_graph("Body Preset Icon"); js = json.dumps(g)
        self.assertTrue(nodes(g, function="ImportFileAsTexture2D")); self.assertIn("BodyPresetIcons", js); self.assertIn(bp.PHOTO_DIR, js)

    def test_finish_photo_branch(self):
        g = fn_graph("Finish Photo"); js = json.dumps(g)
        self.assertIn('"B": "%s"' % bp.PHOTO_KIND, js); self.assertIn("BodyPresetIcons", js)
        self.assertTrue(nodes(g, kind="call_self", function="Rebuild Body Presets"))


class Page(unittest.TestCase):
    def test_widget_and_panel(self):
        w = asset("/Game/Mod/AltUI/W_BodyPresetButton")
        self.assertTrue({"Init", "Begin Rename", "OnMouseButtonDown"} <= {f["name"] for f in w["functions"]})
        js = json.dumps(w); self.assertIn("On Body Preset Clicked", js); self.assertIn("On Body Preset Context", js); self.assertIn("Set Body Preset Name", js)
        p = json.dumps(asset("/Game/Mod/AltUI/W_AltUI"))
        for k in ("BodyPresetBar", "BodyPresetTiles", "BodyPresetBox", "Add Body Preset Tile", "Set Body Presets Shown"): self.assertIn(k, p)

    def test_rebuild_shows_only_tiles_of_the_body(self):
        g = fn_graph("Rebuild Body Presets")
        self.assertTrue(nodes(g, kind="call_self", function="Collect Body Preset Tiles"))
        self.assertTrue(nodes(g, kind="call_self", function="Body Preset Icon"))
        self.assertIn("BodyPresetsFolded", json.dumps(g)); self.assertIn("BodyPresetsFold", json.dumps(g))

    def test_rebuild_body_draws_presets(self):
        self.assertTrue(nodes(fn_graph("Rebuild Body"), kind="call_self", function="Rebuild Body Presets"))

    def test_menu(self):
        js = json.dumps(fn_graph("On Body Preset Context"))
        for a in ("BodyPresetApply", "BodyPresetRename", "BodyPresetUpdate", "BodyPresetUpdateView", "BodyPresetDelete", "BodyPresetLeft", "QuickCtx", bp.QUICK_KIND + ":"):
            self.assertIn(a, js)
        import gen_manager_ui as ui
        acts = {a for a, _, _ in ui.MENU_ACTIONS}
        self.assertTrue({"BodyPresetApply", "BodyPresetRename", "BodyPresetUpdate", "BodyPresetUpdateView", "BodyPresetDelete", "BodyPresetsFold",
                         "BodyPresetLeft", "BodyPresetRight", "BodyPresetFirst", "BodyPresetLast"} <= acts)

    def test_move_within_the_body(self):
        g = fn_graph("Body Preset Move In Array"); js = json.dumps(g)
        self.assertIn("BodyPresetTiles", js); self.assertTrue(nodes(g, function="Array_Remove")); self.assertTrue(nodes(g, function="Array_Insert"))
        self.assertFalse(nodes(g, kind="call_self", function="Save Body Presets"))
        m = fn_graph("Body Preset Move")
        for f in ("Body Preset Move In Array", "Save Body Presets", "Rebuild Body Presets"): self.assertTrue(nodes(m, kind="call_self", function=f), f)

    def test_strings(self):
        from strings import STRINGS
        import strings_fr
        fr = strings_fr.FR
        for k in ("Btn_SaveBodyPreset", "Btn_SaveBodyPresetFront", "Btn_SaveBodyPresetView", "Msg_BodyMissing", "QuickGrp_BodyPresets"):
            self.assertIn(k, STRINGS); self.assertTrue(all(STRINGS[k]), k); self.assertIn(k, fr)


class Quick(unittest.TestCase):
    def test_item(self):
        g = fn_graph("Body Preset Item"); js = json.dumps(g, ensure_ascii=False)
        for k in ("BodyCaptions", "BodyMods", "Chip_Standard", " › "): self.assertIn(k, js)
        self.assertTrue(nodes(g, kind="call_self", function="Scan Body Mods"))

    def test_run_switches_body_first(self):
        g = fn_graph("Run Body Preset")
        for f in ("Body Preset Item", "Apply Body", "Apply Body Preset Data"): self.assertTrue(nodes(g, kind="call_self", function=f), f)
        self.assertIn("Msg_BodyMissing", json.dumps(g))

    def test_every_dispatcher(self):
        for name in ("Quick Find", "Quick Item Caption", "Quick Item Icon", "Run Quick Item", "Quick Item Live"):
            self.assertIn('"B": "%s"' % bp.QUICK_KIND, json.dumps(fn_graph(name)), name)
        self.assertIn("QuickGrp_BodyPresets", json.dumps(fn_graph("Act Catalog Build")))


if __name__ == "__main__":
    unittest.main()
