"""Share JSON in Blueprint (share_bp.py): tokenizer, readers, writers."""
import json, os, sys, unittest
H = os.path.dirname(os.path.abspath(__file__)); ASSETS = os.path.join(H, "..", "..", "assets")
sys.path.insert(0, os.path.join(ASSETS, "gen"))
import share_format as sf


def fn_graph(name):
    """The graph of a function; a scroll-keeping one (KEEP_SCROLL) has it in "<name> Body"."""
    for f in ("30_manager.json", "50_manager_ui.json"):
        for a in json.load(open(os.path.join(ASSETS, f)))["assets"]:
            for e in a.get("functions", []):
                if e.get("name") == name + " Body" and e.get("graph"): return e["graph"]
    for f in ("30_manager.json", "50_manager_ui.json"):
        for a in json.load(open(os.path.join(ASSETS, f)))["assets"]:
            for e in a.get("functions", []):
                if e.get("name") == name and e.get("graph"): return e["graph"]
    raise AssertionError(name)


def nodes(g, **kw): return [n for n in g["nodes"] if all(n.get(k) == v for k, v in kw.items())]


class Tokenizer(unittest.TestCase):
    """The big text is touched once: split at every quote (strings and the parts between them), the parts between at every comma -
    every later step works on short strings. 2026-10-31: character by character took ~0.66 s for 50 looks (and hit the editor's
    runaway-loop guard); calls that took the whole text copied it every time (3.1 s)."""
    def test_split_once(self):
        g = fn_graph("Share Tokenize")
        sp = nodes(g, function="ParseIntoArray"); self.assertEqual(len(sp), 1); self.assertEqual(sp[0]["in"]["Delimiter"], '"')
        self.assertEqual(sp[0]["in"]["CullEmptyStrings"], "false")
        for f in ("GetCharacterArrayFromString", "GetSubstring", "Mid", "FindSubstring"): self.assertFalse(nodes(g, function=f), f)
        self.assertFalse([n for n in g["nodes"] if n.get("name") == "WhileLoop"])

    def test_parts_between_strings_split_at_commas(self):
        sp = nodes(fn_graph("Sh Tok Out"), function="ParseIntoArray"); self.assertEqual(sp[0]["in"]["Delimiter"], ",")
        g = fn_graph("Sh Tok Out"); self.assertTrue(nodes(g, function="IsNumeric")); self.assertTrue(nodes(g, function="IsEmpty"))   # no loop for most pieces

    def test_every_token_kind(self):
        js = "".join(json.dumps(fn_graph(f)) for f in ("Share Tokenize", "Sh Tok In", "Sh Tok Out", "Sh Tok Piece", "Sh Tok Value"))
        for k in ("{", "}", "[", "]", ":", ","): self.assertIn('"%s"' % k, js)
        for v in sf.TOK.values(): self.assertIn('"kind": "%d"' % v, js)

    def test_plain_strings_need_no_loop(self):
        g = fn_graph("Sh Tok In"); self.assertTrue(nodes(g, function="Contains"))

    def test_escapes(self):
        js = json.dumps(fn_graph("Sh Unescape"))
        for e in ('\\\\n', '\\\\t', '\\\\r', '\\\\"', '\\\\/'): self.assertIn(e, js)

class Primitives(unittest.TestCase):
    def test_functions_exist(self):
        for f in ("Sh Peek", "Sh Next", "Sh Expect", "Sh R Str", "Sh R Num", "Sh R Bool", "Sh R Color", "Sh R BColor", "Sh Skip Value",
                  "Sh W Raw", "Sh W Str", "Sh W Key", "Sh W Num", "Sh W Bool", "Sh W Color", "Sh W BColor", "Sh Esc"):
            fn_graph(f)

    def test_skip_is_bounded(self):
        g = fn_graph("Sh Skip Value")
        self.assertTrue([n for n in g["nodes"] if n.get("name") == "ForLoopWithBreak"])
        self.assertIn(str(sf.MAX_TOKENS), json.dumps(g))

    def test_escape_covers_the_format(self):
        tos = [n["in"]["To"] for n in fn_graph("Sh Esc")["nodes"] if n.get("function") == "Replace"]
        self.assertEqual(tos, ["\\\\", '\\"', "\\n", "\\t", "\\r"])
        self.assertEqual([n["in"]["From"] for n in fn_graph("Sh Esc")["nodes"] if n.get("function") == "Replace"][0], "\\")   # backslashes first


class Schemas(unittest.TestCase):
    def test_writer_writes_every_field(self):
        for sname, sch in (("Snap", sf.SNAP_SCHEMA), ("Mut", sf.MUT_SCHEMA), ("Outfit", sf.OUTFIT_SCHEMA), ("Face", sf.FACE_SCHEMA), ("BodyP", sf.BODYP_SCHEMA),
                           ("ModP", sf.MODP_SCHEMA), ("App", sf.APP_SCHEMA)):
            keys = [n["in"]["k"] for n in fn_graph("Sh W " + sname)["nodes"] if n.get("function") == "Sh W Key" and not n["in"]["k"].startswith("@")]
            self.assertEqual(keys, [n for n, _ in sch], sname)

    def test_reader_knows_every_field_and_skips_others(self):
        g = fn_graph("Sh R Snap")
        self.assertEqual([n["in"]["B"] for n in g["nodes"] if n.get("id", "").startswith("ke")], [n for n, _ in sf.SNAP_SCHEMA])
        self.assertTrue(nodes(g, kind="call_self", function="Sh Skip Value"))
        self.assertTrue([n for n in g["nodes"] if n.get("name") == "ForLoopWithBreak"])

    def test_outfit_struct(self):
        st = [a for a in json.load(open(os.path.join(ASSETS, "30_manager.json")))["assets"] if a.get("path", "").endswith("/S_ShareOutfit")][0]
        self.assertEqual([m["name"] for m in st.get("members", st.get("fields", []))], ["Name", "Pieces", "SlotColors"])


class Document(unittest.TestCase):
    def test_functions(self):
        for f in ("Share Begin", "Share Add Look", "Share Add Outfit", "Share End", "Share Parse", "Share Read Entry", "Share Read Entries", "Share Read Mods", "Share Read Refs", "Share Read Ref"):
            fn_graph(f)

    def test_look_export_refs(self):
        g = fn_graph("Share Add Look")
        for f in ("Sh W Snap", "Item Mod", "Hair Mod", "Look Mod", "Display Name"): self.assertTrue(nodes(g, kind="call_self", function=f), f)

    def test_parse_checks_the_header(self):
        js = json.dumps(fn_graph("Share Parse"))
        for k in ('"B": "altui"', '"B": "version"', '"B": "entries"', '"B": "mods"', '"B": "%s"' % sf.FORMAT, "Share_ErrFormat", "Share_ErrVersion"): self.assertIn(k, js)

    def test_entry_reads_data_after_kind(self):
        g = fn_graph("Share Read Entry"); js = json.dumps(g)
        for f in ("Sh R Snap", "Sh R Outfit", "Share Read Refs"): self.assertTrue(nodes(g, kind="call_self", function=f), f)
        self.assertIn("ShDataPos", js); self.assertIn("ShEndPos", js)


class CheckImport(unittest.TestCase):
    def test_check_lists_missing_mods(self):
        g = fn_graph("Share Check"); js = json.dumps(g)
        for k in ("Share_N_look", "Share_Unknown", "Share_MissLine", "Share_AllThere", "%mod", "%pak", "%items", "%entries"): self.assertIn(k, js)
        self.assertTrue(nodes(g, kind="call_self", function="Share Ref Exists"))

    def test_import_new_entries(self):
        g = fn_graph("Share Import"); js = json.dumps(g)
        for f in ("Clean Snap", "Share Missing", "Outfit Id", "Set Outfit Name By Key", "Save Looks", "Save Outfits"): self.assertTrue(nodes(g, kind="call_self", function=f), f)
        self.assertIn("NextId", js); self.assertIn("OutfitColors", js)


class Ui(unittest.TestCase):
    def test_layer_in_the_panel(self):
        p = json.dumps([a for a in json.load(open(os.path.join(ASSETS, "40_widgets.json")))["assets"] if a["path"].endswith("/W_AltUI")][0])
        for k in ("ShareLayer", "ShareEdit", "ShareStatus", "ShareLinks", "MultiLineEditableTextBox", "Share Show", "Share Text", "Share Is Open"): self.assertIn(k, p)

    def test_menus_and_status(self):
        import gen_manager_ui as ui
        acts = {a for a, _, _ in ui.MENU_ACTIONS}
        self.assertTrue({"LookExport", "OutfitExport", "ShareImport", "ShareCheck", "ShareAll", "ShareClean", "ShareClose"} <= acts)
        self.assertIn('"LookExport"', json.dumps(fn_graph("On Look Context"))); self.assertIn('"OutfitExport"', json.dumps(fn_graph("On Outfit Context")))
        self.assertIn('"ShareImport"', json.dumps(fn_graph("Rebuild Status")))

    def test_keys_stay_in_the_field(self):
        w = [a for a in json.load(open(os.path.join(ASSETS, "40_widgets.json")))["assets"] if a["path"].endswith("/W_AltUI")][0]
        ku = [f for f in w["functions"] if f["name"] == "OnKeyUp"][0]; self.assertIn("ShareEdit", json.dumps(ku))
        self.assertTrue(nodes(fn_graph("Panel Key Close"), kind="call_self", function="Share Close"))


class ExportPart2(unittest.TestCase):
    def test_functions_and_refs(self):
        for k in ("Face", "Appearance", "Body Preset", "Mod Preset"): fn_graph("Share Add " + k); fn_graph("Share Export " + k)
        a = fn_graph("Share Add Appearance"); self.assertTrue(nodes(a, kind="call_self", function="Hair Mod")); self.assertTrue(nodes(a, kind="call_self", function="Look Mod"))
        self.assertIn("PresetColors", json.dumps(a))
        b = json.dumps(fn_graph("Share Add Body Preset")); self.assertIn('"Value": "body"', b)
        m = fn_graph("Share Add Mod Preset"); self.assertTrue(nodes(m, kind="call_self", function="Mod Preset Is Own"))
        self.assertIn('"Value": "modentry"', json.dumps(fn_graph("Share Add Mod Preset At")))


class ReadPart2(unittest.TestCase):
    def test_entry_reads_every_kind(self):
        g = fn_graph("Share Read Entry"); js = json.dumps(g)
        for f in ("Sh R Snap", "Sh R Outfit", "Sh R Face", "Sh R App", "Sh R BodyP", "Sh R ModP"): self.assertTrue(nodes(g, kind="call_self", function=f), f)
        for k in sf.KINDS: self.assertIn('"B": "%s"' % k, js)

    def test_count_line_lists_kinds(self):
        js = json.dumps(fn_graph("Share Check"))
        for k in sf.KINDS: self.assertIn("Share_N_" + k, js)
        self.assertIn('"B": "modentry"', json.dumps(fn_graph("Share Ref Exists")))


class ImportPart2(unittest.TestCase):
    def test_import_every_kind(self):
        g = fn_graph("Share Import"); js = json.dumps(g)
        for f in ("Save Faces", "Save Body Presets", "Mod Preset Save", "Write Mod Presets", "Mod Key Split", "Share Free Icon Number", "Set Custom Name", "Rebuild Face Page",
                  "Rebuild Body Presets", "Rebuild Mod Presets", "Rebuild Look"):
            self.assertTrue(nodes(g, kind="call_self", function=f), f)
        self.assertTrue(nodes(g, function="Save Makeup Preset")); self.assertIn("PresetColors", js)
        lits = {n["in"]["Value"] for n in nodes(g, function="MakeLiteralName")}
        for k in sf.KINDS: self.assertIn(k, lits)   # ShImpN counts every kind

    def test_free_icon_number_skips_files(self):
        """A deleted preset leaves Preset_<n>.jpg behind and the game's Get Available Icon Number reuses n (it only looks at Data):
        an imported preset (no photo) would show the old one."""
        js = json.dumps(fn_graph("Share Free Icon Number")); self.assertIn("FileExists", js); self.assertIn("SaveGames/Makeup/Preset_", js); self.assertIn("IconNumber", js)


class MenusPart2(unittest.TestCase):
    def test_context_menus_export(self):
        import gen_manager_ui as ui
        acts = {a: (f, v) for a, f, v in ui.MENU_ACTIONS}
        for act, f, ctx, menu in (("FaceExport", "Share Export Face", "ContextFace", "On Face Context"), ("PresetExport", "Share Export Appearance", "ContextPreset", "On Preset Context"),
                                  ("BodyPresetExport", "Share Export Body Preset", "ContextBodyPreset", "On Body Preset Context"),
                                  ("ModPresetExport", "Share Export Mod Preset", "ContextModPreset", "On Mod Preset Context")):
            self.assertEqual(acts.get(act), (f, ctx)); self.assertIn('"%s"' % act, json.dumps(fn_graph(menu)), menu)

    def test_body_preset_export_takes_the_tile(self):
        """The menu passes the tile (ContextBodyPreset); Share Add Body Preset takes the array index."""
        self.assertTrue(nodes(fn_graph("Share Export Body Preset"), kind="call_self", function="Body Preset Index"))

    def test_mod_preset_export_only_own(self):
        g = fn_graph("On Mod Preset Context"); js = json.dumps(g)
        self.assertIn("ModPresetExport", js)
        import gen_manager_ui as ui, inspect
        self.assertIn('"ModPresetExport": "@own.yes"', inspect.getsource(ui.f_on_mod_preset_context))

    def test_import_in_the_status_bar_of_every_page(self):
        js = json.dumps(fn_graph("Rebuild Status"))
        for page in ("Looks", "Outfits", "Face", "Look", "Body", "Mods"): self.assertIn('"B": "%s"' % page, js)
        import gen_manager_ui as ui, inspect
        src = inspect.getsource(ui.f_rebuild_status)
        for page in ("Looks", "Outfits", "Face", "Look", "Body", "Mods"): self.assertIn('"%s"' % page, src[src.index("share as JSON"):])


class CollectionPage(unittest.TestCase):
    def test_page_keys(self):
        g = fn_graph("Share Page Keys"); js = json.dumps(g)
        for f in ("Scan Mod Entries", "Mod Preset Save", "Outfit Name", "Preset Shown Name", "Share Body Caption", "Usage Mod Caption"):
            self.assertTrue(nodes(g, kind="call_self", function=f), f)
        for k in sf.KINDS: self.assertIn('"%s:"' % k, js)
        self.assertIn("ModPresetSaves", js)   # paks loaded in this session (an import) count too

    def test_manage_rows_share(self):
        g = fn_graph("Manage Rows"); self.assertIn('"B": "Share"', json.dumps(g)); self.assertTrue(nodes(g, kind="call_self", function="Share Page Keys"))



class Selection(unittest.TestCase):
    def test_mod_preset_shares_the_code(self):
        self.assertTrue(nodes(fn_graph("Share Add Mod Preset"), kind="call_self", function="Share Add Mod Preset At"))

    def test_selected_text(self):
        g = fn_graph("Share Selected Text")
        for f in ("Share Begin", "Share Add Look", "Share Add Outfit", "Share Add Face", "Share Add Appearance", "Share Add Body Preset", "Share Add Mod Preset At", "Share End"):
            self.assertTrue(nodes(g, kind="call_self", function=f), f)
        self.assertIn("ShPageKeys", json.dumps(g)); self.assertIn("ShareSel", json.dumps(g))

    def test_actions(self):
        import gen_manager_ui as ui
        js = json.dumps(fn_graph("On Menu Action"))
        for p in ("ShTick:", "ShAll:", "ShNone:"): self.assertIn('"InPrefix": "%s"' % p, js)
        self.assertIn(("ShareExportSel", "Share Export Selected", None), ui.MENU_ACTIONS)
        self.assertTrue(nodes(fn_graph("Share Tick"), function="Set Check")); self.assertTrue(nodes(fn_graph("Share Tick Kind"), function="Set Check"))



class Page(unittest.TestCase):
    def test_category(self):
        import gen_manager_ui as ui
        self.assertIn(("Share", "Cat_Share"), ui.MANAGE_CATS); self.assertIn("Share", ui.MANAGE_NO_ONLY_MODS)
        g = fn_graph("Rebuild Manage"); self.assertTrue(nodes(g, kind="call_self", function="Rebuild Share Page")); self.assertIn('"B": "Share"', json.dumps(g))

    def test_page(self):
        g = fn_graph("Rebuild Share Page"); js = json.dumps(g)
        for w in ("W_LinkRow", "W_ContentSection", "W_ValueRow"): self.assertIn(w, js)
        self.assertTrue(nodes(g, function="Set Check")); self.assertIn("ShPageRows", js)
        for k in ["Share_H_" + k for k in sf.KINDS] + ["Share_SelAll", "Share_SelNone", "Share_PageNote", "Share_PageEmpty"]: self.assertIn(k, js)
        for p in ("ShAll:", "ShNone:", "ShTick:"): self.assertIn(p, js)

    def test_layout(self):
        """Play test 2026-11-01: the note on top, a heading closer to its own table than to the one above, rows over the whole width."""
        g = fn_graph("Rebuild Share Page"); js = json.dumps(g)
        self.assertLess(js.index("Share_PageNote"), js.index("Share_H_look"))
        self.assertTrue(nodes(g, function="Set Gap")); self.assertTrue(nodes(g, function="Set Wide"))
        modes = [n["in"]["mode"] for n in nodes(g, function="Set Head Mode")]; self.assertEqual(set(modes), {"3"})

    def test_export_without_ticks_opens_empty(self):
        g = fn_graph("Share Export Selected"); opens = nodes(g, kind="call_self", function="Open Share Export")
        self.assertEqual(len(opens), 2); self.assertIn("", [n["in"]["text"] for n in opens])

    def test_ticks_reset(self):
        for f in ("Select Manage Cat", "Open Panel"): self.assertIn("ShareSel", json.dumps(fn_graph(f)), f)
        for a in json.load(open(os.path.join(ASSETS, "50_manager_ui.json")))["assets"]:   # the Select Page wrapper: only on another page
            for e in a.get("functions", []):
                if e.get("name") == "Select Page" and e.get("graph"): self.assertIn("ShareSel", json.dumps(e["graph"]))
        self.assertNotIn("ShareSel", json.dumps(fn_graph("Select Page")))

    def test_status_bar(self):
        js = json.dumps(fn_graph("Rebuild Status"))
        for k in ("ShareExportSel", "Btn_ShareExportN", "ShareImport", '"B": "Manage"', '"B": "Share"'): self.assertIn(k, js)

    def test_import_redraws_the_page(self):
        g = fn_graph("Share Import"); js = json.dumps(g); self.assertIn('"B": "Manage"', js); self.assertTrue(nodes(g, kind="call_self", function="Rebuild Manage"))

    def test_texts(self):
        import strings, strings_fr
        for k in ["Cat_Share", "Btn_ShareExportN", "Share_SelAll", "Share_SelNone", "Share_PageNote", "Share_PageEmpty", "Share_NoBody"] + ["Share_H_" + k for k in sf.KINDS]:
            self.assertEqual(len(strings.STRINGS[k]), 7, k); self.assertTrue(all(strings.STRINGS[k]), k); self.assertIn(k, strings_fr.FR, k)


def widget(path):
    for a in json.load(open(os.path.join(ASSETS, "40_widgets.json")))["assets"]:
        if a.get("path", "").endswith(path): return a
    raise AssertionError(path)


def wfn(asset, name):
    for e in asset.get("functions", []):
        if e.get("name") == name: return e
    raise AssertionError(name)


class AlreadyHere(unittest.TestCase):
    """Play test 2026-11-01: an entry saved here exactly so is not imported again; "Everything is installed" read as "all of it is here"."""
    def test_check_drops_first(self):
        g = fn_graph("Share Check"); self.assertTrue(nodes(g, kind="call_self", function="Share Drop Existing"))
        js = json.dumps(g)
        for k in ("Share_Dup", "Share_NothingNew", "ShDupN", "ShDupNames"): self.assertIn(k, js)

    def test_drop_compares_the_export_data(self):
        g = fn_graph("Share Drop Existing"); js = json.dumps(g)
        for w in ("Snap", "Outfit", "Face", "App", "BodyP", "ModP"): self.assertTrue(nodes(g, kind="call_self", function="Sh W " + w), w)
        for v in ("ShLooks", "ShOutfits", "ShFaces", "ShApps", "ShBodyPresets", "ShModPresets", "ShRefs"): self.assertIn(v, js)
        self.assertTrue(nodes(g, function="Array_Remove")); self.assertTrue(nodes(g, kind="call_self", function="Share Outfit Data"))

    def test_outfit_shares_the_code(self):
        self.assertTrue(nodes(fn_graph("Share Add Outfit"), kind="call_self", function="Share Outfit Data"))

    def test_nothing_left_only_close(self):
        g = fn_graph("Share Check Click"); self.assertTrue(any("ck.left" in json.dumps(n) for n in g["nodes"]))

    def test_texts(self):
        import strings, strings_fr
        for k in ("Share_Dup", "Share_DupNoNames", "Share_NothingNew", "Share_AllThere"):
            self.assertEqual(len(strings.STRINGS[k]), 7, k); self.assertIn(k, strings_fr.FR)
        self.assertNotIn("Everything", strings.STRINGS["Share_AllThere"][0])

    def test_status_after_category(self):
        """The status bar's "Export (n)…" / "Import…" showed only after the first tick."""
        self.assertTrue(nodes(fn_graph("Select Manage Cat"), kind="call_self", function="Rebuild Status"))


class PiecesWithoutRef(unittest.TestCase):
    """Play test 2026-11-01 (outfit from Gonnor): "everything there", then "Not available" for four pieces - mod pieces the sender's
    AltUI could not tell the mod of carry no reference; and installed pieces not owned could not be put on either."""
    def test_check_scans_pieces(self):
        g = fn_graph("Share Check"); self.assertTrue(nodes(g, kind="call_self", function="Share Scan Pieces"))
        js = json.dumps(g)
        for k in ("Share_MissUnknown", "Share_Unowned", "ShUnowned"): self.assertIn(k, js)

    def test_scan(self):
        g = fn_graph("Share Scan Pieces")
        for f in ("Find Item", "Share Has Ref", "Can Wear", "Display Name"): self.assertTrue(nodes(g, kind="call_self", function=f), f)
        self.assertIn("ShRefs", json.dumps(g)); self.assertIn("ShOutfits", json.dumps(g)); self.assertIn("ShLooks", json.dumps(g))

    def test_popup_says_not_owned(self):
        self.assertIn("Msg_LookUnowned", json.dumps(fn_graph("Snap Notice Text")))
        self.assertIn("PendingUnowned", json.dumps(fn_graph("Wear Queue Step")))

    def test_texts(self):
        import strings, strings_fr
        for k in ("Msg_LookUnowned", "Share_Unowned", "Share_MissUnknown"):
            self.assertEqual(len(strings.STRINGS[k]), 7, k); self.assertIn(k, strings_fr.FR)


class TypeCase(unittest.TestCase):
    """Gonnor's outfit 2026-11-01: refs came as "Clothes" (the game's FName spelling); a case-sensitive compare matched no type."""
    def test_ref_exists_ignores_case(self):
        g = fn_graph("Share Ref Exists"); self.assertFalse(nodes(g, function="EqualEqual_StrStr")); self.assertTrue(nodes(g, function="EqualEqual_StriStri"))

    def test_export_writes_lower_case(self):
        self.assertTrue(nodes(fn_graph("Share Add Look"), function="ToLower"))


class ShareWindowTheme(unittest.TestCase):
    """Play test 2026-11-01: the share window looks like the panel - its picture with the filters, background colour, frame, text field."""
    def test_tree(self):
        js = json.dumps(widget("/W_AltUI")["widget_tree"])
        for k in ("ShareImgLayer", "ShareScale", "ShareImage", "ShareTile", "ShareBg", "ShareFrame"): self.assertIn('"%s"' % k, js)

    def test_picture_follows(self):
        p = widget("/W_AltUI"); g = wfn(p, "Set Bg Image")["graph"]
        self.assertTrue(nodes(g, kind="call_self", function="Set Share Bg Image"))
        self.assertIn("ShareImgLayer", json.dumps(wfn(p, "Set Share Bg Image")["graph"]))

    def test_colours(self):
        js = json.dumps(wfn(widget("/W_AltUI"), "Apply Theme")["graph"])
        for k in ("ShareLayer", "ShareFrame", "ShareBg", "ColDim", "Theme Multi Edit Box"): self.assertIn(k, js)
        js = json.dumps(fn_graph("Theme Multi Edit Box")); self.assertIn("ColInput", js); self.assertIn("ColScroll", js); self.assertIn("ScrollBarStyle", js)

    def test_text_field(self):
        """Play test 2026-11-01: the JSON was tiny and its scroll bars the engine's white ones."""
        js = json.dumps(widget("/W_AltUI")["widget_tree"]); i = js.index('"ShareEdit"'); part = js[i - 2000:i + 2000]
        self.assertIn("T_ScrollThumb", part); self.assertIn("TextStyle", part); self.assertIn("AutoWrapText", part)


if __name__ == "__main__":
    unittest.main()
