"""Presets for mod pages (docs/specs/2026-10-28-mod-presets-design.md): contract, save per mod, capture / apply, tiles, quick menu."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
import modui as mu, json
# helpers of their own: test_modui_page.py stays private (release/snapshot.toml), this test is public (2.9.0 snapshot)
ASSETS = os.path.join(H, "..", "..", "assets")


def load(fname):
    with open(os.path.join(ASSETS, fname)) as f:
        return json.load(f)["assets"]


def fn_graph(name, files=("30_manager.json", "50_manager_ui.json")):
    if name + " Body" in {e.get("name") for f in files for a in load(f) for e in a.get("functions", [])}: name += " Body"   # KEEP_SCROLL wrapper
    for f in files:
        for a in load(f):
            for entry in a.get("functions", []):
                if entry.get("name") == name and entry.get("graph"): return entry["graph"]
    raise AssertionError("function %s not found" % name)


def nodes(g, **kw): return [n for n in g["nodes"] if all(n.get(k) == v for k, v in kw.items())]


def in_exec(g, node_id): return any(node_id == s.split(":")[0] for chain in g.get("exec", []) for s in chain)


def asset(path, fname="30_manager.json"):
    return next(a for a in load(fname) if a.get("path") == path)


class Contract(unittest.TestCase):
    def test_table_columns(self):
        self.assertEqual(mu.PRESETS_TABLE, "AltUI_Presets")
        self.assertEqual(mu.PRESET_STRUCT, "/Game/Mod/AltUI/S_AltUIModPreset")
        self.assertEqual([n for n, _, _ in mu.PRESET_MEMBERS], ["Entry", "Caption", "Icon", "Order", "Values"])

    def test_types(self):
        self.assertEqual(mu.PRESET_NUM_TYPES, ["Toggle", "Slider", "Number", "Choice"])
        self.assertEqual(mu.PRESET_TYPES, mu.PRESET_NUM_TYPES + ["Color", "Text"])
        for t in ("Key", "Button", "Info", "Header"): self.assertNotIn(t, mu.PRESET_TYPES)

    def test_structs_in_manager_json(self):
        s = asset(mu.S_MODPRESET)
        self.assertEqual([m["name"] for m in s["members"]], ["Entry", "Name", "Id", "Values", "Colors", "Texts", "Off"])
        sg = asset(mu.SG_MODPRESETS)
        self.assertEqual({v["name"] for v in sg["variables"]}, {"Version", "NextId", "Presets", "ShippedNames", "ShippedOff"})
        shipped = asset(mu.PRESET_STRUCT)["members"]
        self.assertEqual([m["name"] for m in shipped], ["Entry", "Caption", "Icon", "Order", "Values"])
        self.assertEqual(shipped[-1].get("value_type"), "string")

    def test_test_mod_table(self):
        t = asset("/Game/Mod/%s/%s" % (mu.TEST_MOD, mu.PRESETS_TABLE))
        self.assertEqual(set(t["rows"]), set(mu.TEST_PRESETS))


class Scan(unittest.TestCase):
    def test_table_loaded_by_path(self):
        g = fn_graph("Scan Mod Entries")
        self.assertTrue(any(n.get("function") == "Concat_StrStr" and n.get("in", {}).get("B") == "/%s.%s" % (mu.PRESETS_TABLE, mu.PRESETS_TABLE) for n in g["nodes"]))
        self.assertTrue(nodes(g, kind="call_self", function="Mod Shipped Pos"))
        adds = [n for n in g["nodes"] if n.get("function") == "Map_Add" and "ModShipped" in n.get("in", {}).get("TargetMap", "")]
        self.assertEqual(len(adds), 1); self.assertTrue(in_exec(g, adds[0]["id"]))

    def test_rows_need_their_entry(self):
        g = fn_graph("Scan Mod Entries")
        self.assertTrue(any(n.get("function") == "Map_Contains" and "ModEntries" in n.get("in", {}).get("TargetMap", "") and n["id"].startswith("p") for n in g["nodes"]))

    def test_order(self):
        g = fn_graph("Mod Shipped Pos")
        self.assertTrue(any(n.get("function") == "Map_Find" and "ModShipped" in n.get("in", {}).get("TargetMap", "") for n in g["nodes"]))


class Store(unittest.TestCase):
    def test_slot_per_mod(self):
        g = fn_graph("Mod Preset Slot")
        self.assertTrue(any(n.get("function") == "Concat_StrStr" and n.get("in", {}).get("A") == mu.PRESET_SLOT_PREFIX for n in g["nodes"]))

    def test_key_split(self):
        g = fn_graph("Mod Key Split")
        self.assertTrue(any(n.get("function") == "Split" and n.get("in", {}).get("InStr") == "/" and n["in"].get("SearchDir") == "FromStart" for n in g["nodes"]))

    def test_load_once_per_mod(self):
        g = fn_graph("Mod Preset Save")
        self.assertTrue(any(n.get("function") == "Map_Find" and "ModPresetSaves" in n.get("in", {}).get("TargetMap", "") for n in g["nodes"]))
        for f in ("DoesSaveGameExist", "LoadGameFromSlot", "CreateSaveGameObject"):
            ns = nodes(g, function=f); self.assertTrue(ns, f); self.assertTrue(in_exec(g, ns[0]["id"]), f)
        self.assertFalse(nodes(g, function="SaveGameToSlot"), "loading never writes")
        self.assertTrue(any(n.get("function") == "NotEqual_IntInt" and n.get("in", {}).get("B") == str(mu.PRESET_VERSION) for n in g["nodes"]))

    def test_write_reports_failure(self):
        g = fn_graph("Write Mod Presets")
        sv = nodes(g, function="SaveGameToSlot"); self.assertEqual(len(sv), 1); self.assertTrue(in_exec(g, sv[0]["id"]))
        self.assertTrue(nodes(g, kind="call_self", function="Pop Notice"))

    def test_strings(self):
        from strings import STRINGS, LANGS
        for k in ("Lbl_ModPreset", "Lbl_ModPresetSaveFail", "Btn_SaveModPreset", "Btn_SaveModPresetFront", "Btn_SaveModPresetView"):
            self.assertIn(k, STRINGS); self.assertEqual(len(STRINGS[k]), len(LANGS)); self.assertTrue(all(STRINGS[k]), k)


class Values(unittest.TestCase):
    def test_capture_reads_by_type(self):
        g = fn_graph("Capture Mod Values")
        for f in (mu.GET_VALUE, mu.GET_COLOR, mu.GET_TEXT):
            m = nodes(g, kind="message", function=f); self.assertEqual(len(m), 1, f); self.assertTrue(in_exec(g, m[0]["id"]), f)
        self.assertFalse(nodes(g, kind="message", function=mu.GET_KEY), "a key never goes into a preset")
        types = {n["in"]["B"] for n in g["nodes"] if n.get("function") == "EqualEqual_NameName" and n.get("in", {}).get("B") in mu.TYPES}
        self.assertEqual(types, set(mu.PRESET_TYPES))

    def test_colours_before_numbers(self):
        """Play test 2026-10-29: the example lamp's colour field switches its choice to "Custom" - a choice applied after it wins."""
        g = fn_graph("Apply Mod Values")
        loops = [n for n in g["nodes"] if n.get("kind") == "foreach"]; self.assertEqual(len(loops), 2)
        first, second = loops[0]["id"], loops[1]["id"]
        self.assertTrue(any(c[:2] == [first + ":Completed", second] for c in g["exec"]), "numbers after colours / texts")
        def reached(start):
            seen, todo = set(), [start]
            while todo:
                x = todo.pop()
                for c in g["exec"]:
                    ids = [i.split(":")[0] for i in c]
                    if x in ids[:-1] or c[0] == x: 
                        for i in ids[ids.index(x) + 1:] if x in ids else ids: 
                            if i not in seen: seen.add(i); todo.append(i)
            return seen
        msg = {n["id"]: n.get("function") for n in g["nodes"] if n.get("kind") == "message"}
        self.assertEqual({msg[i] for i in reached(first) if i in msg and i not in reached(second)} - {mu.ON_CHANGED}, {mu.ON_COLOR, mu.ON_TEXT})

    def test_unticked_left_out(self):
        g = fn_graph("Apply Mod Values")
        self.assertEqual(sum(1 for n in g["nodes"] if n.get("function") == "Array_Contains" and n.get("in", {}).get("TargetArray") == "@tp.Off"), 2)
        st = fn_graph("Shipped To Tmp"); self.assertIn("ShippedOff", str(st))
        for f in ("Set Mod Preset Name", "Update Mod Preset", "Mod Preset Toggle Off"):   # the unticked keys survive renaming / updating
            mk = [n for n in fn_graph(f)["nodes"] if n.get("kind") == "make" and n.get("struct") == mu.S_MODPRESET]
            self.assertTrue(mk and all("Off" in n.get("in", {}) for n in mk), f)

    def test_apply_sends_by_type(self):
        g = fn_graph("Apply Mod Values")
        for f in (mu.ON_CHANGED, mu.ON_COLOR, mu.ON_TEXT):
            m = nodes(g, kind="message", function=f); self.assertEqual(len(m), 1, f); self.assertTrue(in_exec(g, m[0]["id"]), f)
        self.assertFalse(nodes(g, kind="message", function=mu.ON_KEY))
        self.assertTrue(nodes(g, function="FClamp"), "slider / number clamped")
        self.assertTrue(nodes(g, function="Round"), "choice rounded")
        self.assertTrue(nodes(g, function="IsValid"), "no actor: nothing")

    def test_shipped_values_read_by_field_type(self):
        g = fn_graph("Shipped To Tmp")
        self.assertTrue(nodes(g, function="IsNumeric"))
        self.assertTrue(nodes(g, kind="call_self", function="Hex To Color"))
        self.assertTrue(any(n.get("function") == "EqualEqual_StriStri" and n.get("in", {}).get("B") == "true" for n in g["nodes"]))

    def test_entry_actor_in_chain(self):
        g = fn_graph("Mod Entry Actor")
        ga = nodes(g, function="GetActorOfClass"); self.assertEqual(len(ga), 1); self.assertTrue(in_exec(g, ga[0]["id"]))


class Tiles(unittest.TestCase):
    def test_tiles_on_the_page(self):
        self.assertTrue(nodes(fn_graph("Rebuild Mod Fields"), kind="call_self", function="Rebuild Mod Presets"))
        g = fn_graph("Rebuild Mod Presets")
        self.assertTrue(nodes(g, function="Add Mod Preset Tile"))
        self.assertTrue(nodes(g, function="Set Mod Presets Shown"))
        self.assertTrue(any(n.get("function") == "Concat_StrStr" and n.get("in", {}).get("A") == "ship:" for n in g["nodes"]))

    def test_widget(self):
        a = {x["path"].rsplit("/", 1)[1]: x for x in load("40_widgets.json")}
        self.assertIn("W_ModPresetButton", a)
        self.assertTrue({"Clear Mod Preset Tiles", "Add Mod Preset Tile", "Set Mod Presets Shown"} <= {f["name"] for f in a["W_AltUI"]["functions"]})

    def test_shipped_not_deleted_or_updated(self):
        for f in ("Delete Mod Preset", "Update Mod Preset", "Mod Preset Move"):
            self.assertTrue(nodes(fn_graph(f), kind="call_self", function="Mod Preset Is Own"), f)

    def test_add_captures_and_writes(self):
        g = fn_graph("Add Mod Preset")
        for f in ("Capture Mod Values", "Write Mod Presets", "Capture Mod Preset Photo", "Rebuild Mod Presets"):
            self.assertTrue(nodes(g, kind="call_self", function=f), f)

    def test_apply(self):
        g = fn_graph("Apply Mod Preset")
        for f in ("Mod Preset To Tmp", "Apply Mod Values"): self.assertTrue(nodes(g, kind="call_self", function=f), f)
        self.assertTrue(nodes(fn_graph("Mod Preset To Tmp"), kind="call_self", function="Shipped To Tmp"))
        g = fn_graph("On Mod Preset Clicked")
        for f in ("Add Mod Preset", "Apply Mod Preset"): self.assertTrue(nodes(g, kind="call_self", function=f), f)

    def test_photo_kind(self):
        g = fn_graph("Finish Photo")
        self.assertTrue(any(n.get("in", {}).get("B") == "ModPreset" for n in g["nodes"]))
        self.assertTrue(nodes(g, kind="call_self", function="Rebuild Mod Presets"))
        cap = fn_graph("Capture Mod Preset Photo")
        self.assertTrue(any("ModPresets/" in str(n.get("in", {}).get("B", "")) for n in cap["nodes"]))

    def test_menu_actions(self):
        import gen_manager_ui as ui
        acts = {a for a, _, _ in ui.MENU_ACTIONS}
        for a in ("ModPresetApply", "ModPresetRename", "ModPresetUpdate", "ModPresetUpdateView", "ModPresetDelete",
                  "ModPresetLeft", "ModPresetRight", "ModPresetFirst", "ModPresetLast"):
            self.assertIn(a, acts)
        g = fn_graph("On Mod Preset Context")
        self.assertTrue(any(n.get("function") == "Concat_StrStr" and n.get("in", {}).get("A") == "modpreset:" for n in g["nodes"]))
        for a in ("ModPresetView", "ModPresetPhoto", "ModPresetPhotoView"): self.assertIn(a, acts)

    def test_move_keeps_the_source(self):
        """Play test 2026-10-29: Mod Preset Is Own on the target set MPIdx - the target was moved onto itself, nothing moved."""
        g = fn_graph("Mod Preset Move")
        for f in ("Array_Get", "Array_Remove"):
            n = nodes(g, function=f)[0]; key = "Index" if f == "Array_Get" else "IndexToRemove"
            src = n["in"][key].split(".")[0][1:]; self.assertEqual(nodes(g, id=src)[0].get("var"), "MPFrom", f)

    def test_shipped_photo(self):
        """Shipped presets: a new photo ("ship_<row>.png"), their values stay the mod's."""
        g = fn_graph("Update Mod Preset")
        self.assertEqual(len(nodes(g, kind="call_self", function="Capture Mod Preset Photo")), 2)
        self.assertTrue(any(n.get("in", {}).get("To") == "ship_" for n in g["nodes"]))
        self.assertTrue(nodes(fn_graph("Mod Preset Tile Icon"), kind="call_self", function="Mod Preset Icon"))

    def test_content_view(self):
        g = fn_graph("Rebuild Mod Preset Content"); js = str(g)
        self.assertIn("MPOff:", js); self.assertTrue(nodes(g, function="Set Check")); self.assertTrue(nodes(g, kind="call_self", function="Mod Preset To Tmp"))
        self.assertTrue(nodes(fn_graph("Rebuild Content"), kind="call_self", function="Rebuild Mod Preset Content"))
        self.assertIn("ViewMPTile", str(fn_graph("Content Open"))); self.assertIn("ViewMPTile", str(fn_graph("Close Content")))
        a = fn_graph("On Menu Action"); self.assertIn("MPOff:", str(a)); self.assertTrue(nodes(a, kind="call_self", function="Mod Preset Toggle Off"))
        t = fn_graph("Mod Preset Toggle Off")
        for f in ("Write Mod Presets", "Rebuild Content"): self.assertTrue(nodes(t, kind="call_self", function=f), f)


class Quick(unittest.TestCase):
    def test_kind_everywhere(self):
        for f in ("Quick Find", "Quick Item Caption", "Quick Item Icon", "Run Quick Item", "Quick Item Live"):
            g = fn_graph(f)
            self.assertTrue(any(n.get("function") == "EqualEqual_StrStr" and n.get("in", {}).get("B") == "modpreset" for n in g["nodes"]), f)
        self.assertTrue(nodes(fn_graph("Quick Item Live"), kind="call_self", function="Mod Entry Actor"))

    def test_run_goes_through_apply(self):
        g = fn_graph("Run Mod Preset")
        for f in ("Apply Mod Values", "Mod Entry Actor", "Shipped To Tmp"): self.assertTrue(nodes(g, kind="call_self", function=f), f)

    def test_item_does_not_touch_the_page(self):
        for f in ("Mod Preset Item", "Run Mod Preset", "Mod Preset Item Icon", "Mod Preset Save"):
            g = fn_graph(f)
            self.assertFalse([n for n in g["nodes"] if n.get("kind") == "set" and n.get("var") == "MPSave"], f)

    def test_catalog_offers_presets(self):
        g = fn_graph("Act Catalog Build")
        self.assertTrue(any(n.get("function") == "Concat_StrStr" and n.get("in", {}).get("A") == "modpreset:" for n in g["nodes"]))
        # play test 2026-10-29: the prefix "modpreset:<entry>|" was kept in QStr, which Quick Item Caption (per item) overwrites -
        # the 2nd preset became "<caption of the 1st>2" (no picture, greyed out)
        writes = {n["var"] for n in nodes(fn_graph("Quick Item Caption"), kind="set")}
        pre = [n for n in g["nodes"] if n.get("kind") == "set" and any("xqpp2" in str(v) for v in n.get("in", {}).values())]
        self.assertEqual(len(pre), 1); self.assertNotIn(pre[0]["var"], writes)
