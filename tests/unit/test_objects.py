"""2026-10-23 (spec 2026-10-23-objects-tab-design): Objects tab - catalogue from the asset registry, mod scan, spawning, pictures."""
import json, unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph
import objects


def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]
def fns(g): return {n.get("function") for n in g["nodes"]}


class Rules(unittest.TestCase):
    def test_cat_order(self):
        cats = ["Mod:Zeta", "Office", "Map:Level_1", "Weapons", "mod:alpha", "Lamp", "Map:JodisOffice"]
        self.assertEqual(sorted(cats, key=lambda c: objects.cat_sort_str(c).lower()),
                         ["Lamp", "Office", "Map:JodisOffice", "Map:Level_1", "Weapons", "mod:alpha", "Mod:Zeta"])

    def test_mods_by_caption(self):
        """ui-test-150: mods sorted by the folder looked like several alphabetical groups - the row shows the mod's name."""
        self.assertLess(objects.cat_sort_str("Mod:WeaponAltUI_ACR", "ACR").lower(), objects.cat_sort_str("Mod:Ankle", "Ankle").lower())
        g = mgr_graph("Obj Cat Sort Str"); self.assertIn("Obj Cat Caption", fns(g))

    def test_pictures_one_tile_at_a_time(self):
        g = mgr_graph("Finish Photo"); self.assertEqual({x["id"]: x for x in g["nodes"]}["rbo"]["function"], "Obj Icon Done")
        self.assertNotIn("Rebuild Obj Tiles", fns(mgr_graph("Obj Icon Done"))); self.assertIn("Obj Next Icon", fns(mgr_graph("Obj Icon Done")))

    def test_left_rows_without_thumb(self):
        self.assertIn("No Thumb", fns(mgr_graph("Rebuild Obj Cats")))

    def test_in_cat(self):
        self.assertTrue(objects.in_cat("All", "Office", False)); self.assertTrue(objects.in_cat("Fav", "Office", True)); self.assertFalse(objects.in_cat("Fav", "Office", False))
        self.assertTrue(objects.in_cat("Mods", "mod:Brefg_Poses", False)); self.assertFalse(objects.in_cat("Mods", "Office", False))
        self.assertTrue(objects.in_cat("Mod:Brefg_Poses", "mod:Brefg_Poses", False))

    def test_matches(self):
        self.assertTrue(objects.matches("", "x", "y")); self.assertTrue(objects.matches("chair", "Office Chair", "SM_X"))
        self.assertTrue(objects.matches("sm_tire", "Tires", "SM_TiresBunch_a")); self.assertFalse(objects.matches("lamp", "Chair", "SM_Chair"))

    def test_graph_rules(self):
        g = mgr_graph("Obj Cat Sort Str"); self.assertEqual({n["in"]["A"] for n in calls(g, "Concat_StrStr")}, {"1", "2", "4"})
        g = mgr_graph("Obj Shows"); self.assertEqual({n["in"]["bUseCase"] for n in calls(g, "Contains")}, {"false"})


class Names(unittest.TestCase):
    def test_display_name(self):
        for a, b in [("SM_ConcretePipe_c", "Concrete Pipe c"), ("ConcreteBlock_a", "Concrete Block a"), ("SM_TiresBunch_a", "Tires Bunch a"),
                     ("S_1_Unit_Plane", "1 Unit Plane"), ("SM_Chair", "Chair"), ("Bottle", "Bottle"), ("SM_HDRBox", "HDRBox")]:
            self.assertEqual(objects.display_name(a), b, a)

    def test_category(self):
        self.assertEqual(objects.category("/Game/Project/Models/Office"), "Office")
        self.assertEqual(objects.category("/Game/Project/Models/Office/Chairs"), "Office")
        self.assertEqual(objects.category("/Game/Project/Models/Weapon/Pistol"), "Weapons")
        self.assertEqual(objects.category("/Game/Project/Maps/JodisOffice/Props"), "Map:JodisOffice")
        self.assertEqual(objects.category("/Game/Mod/Ankle/StarterContent/Props"), "Mod:Ankle")
        for p in ("/Game/Mod/AltUI", "/Game/Mod/AltUI/Mat", "/Game/Project/Character/Jodi", "/Engine/BasicShapes", "/Game/Project/Models"):
            self.assertIsNone(objects.category(p), p)


class Catalogue(unittest.TestCase):
    def test_scan_game(self):
        g = mgr_graph("Obj Scan"); f = fns(g)
        self.assertTrue({"GetAssetRegistry", "GetAssetsByClass", "Obj Category"} <= f)
        self.assertEqual(calls(g, "GetAssetsByClass")[0]["in"]["ClassName"], "StaticMesh")
        self.assertIn("ObjScanned", {n.get("var") for n in g["nodes"] if n["kind"] == "get"})

    def test_scan_mods_from_cache_and_queue(self):
        """ui-test-148: one scan of /Game/Mod/ held the game 33 s -> cache + one folder per step, no scan in Obj Scan Mods itself."""
        g = mgr_graph("Obj Scan Mods"); f = fns(g)
        self.assertTrue({"LoadGameFromSlot", "GetDataTableRowNames", "Obj Take Folder", "K2_SetTimer"} <= f)
        self.assertNotIn("ScanPathsSynchronous", f)
        self.assertEqual(calls(g, "K2_SetTimer")[0]["in"]["FunctionName"], "Obj Scan Step")
        self.assertEqual(calls(g, "LoadGameFromSlot")[0]["in"]["SlotName"], objects.CACHE_SLOT)
        self.assertIn("ObjModsScanned", {n.get("var") for n in g["nodes"] if n["kind"] == "get"})

    def test_cache_loaded_in_one_pass(self):
        """ui-test-151: a pass over all cached paths per folder took ~5 s at the first opening."""
        self.assertFalse([n for n in mgr_graph("Obj Take Folder")["nodes"] if n["kind"] == "foreach"])
        self.assertIn("Map_Contains", fns(mgr_graph("Obj Scan Mods")))

    def test_scan_step(self):
        g = mgr_graph("Obj Scan Step"); f = fns(g)
        self.assertTrue({"ScanPathsSynchronous", "GetAssetsByPath", "Obj Add Path", "SaveGameToSlot", "Rebuild Objects"} <= f)
        self.assertEqual(calls(g, "ScanPathsSynchronous")[0]["in"]["bForceRescan"], "@gf.ObjForce")
        self.assertEqual(calls(g, "K2_SetTimer")[0]["in"]["FunctionName"], "Obj Scan Step")
        self.assertEqual(calls(g, "SaveGameToSlot")[0]["in"]["SlotName"], objects.CACHE_SLOT)

    def test_rescan(self):
        g = mgr_graph("Obj Rescan"); sets = {n["var"]: n["in"] for n in g["nodes"] if n["kind"] == "set"}
        self.assertEqual(sets["ObjForce"]["ObjForce"], "true"); self.assertEqual(sets["ObjModsScanned"]["ObjModsScanned"], "false")
        import gen_manager_ui as ui
        self.assertIn(("ObjRescan", "Obj Rescan", None), ui.MENU_ACTIONS)

    def test_scan_folders(self):
        """ui-test-149: map paks keep their content in the folder without "Map_"."""
        self.assertEqual(objects.scan_folders("Map_LowPolyJunglePack"), ["Map_LowPolyJunglePack", "LowPolyJunglePack"])
        self.assertEqual(objects.scan_folders("ToxicVelvet"), ["ToxicVelvet"]); self.assertEqual(objects.scan_folders("Map_"), ["Map_"])
        self.assertEqual(objects.scan_folders(objects.OWN_MOD), [])
        g = mgr_graph("Obj Scan Mods"); self.assertEqual(len(calls(g, "Obj Take Folder")), 3)   # row, row without Map_, Extra
        self.assertIn(objects.MAP_PREFIX, [n["in"].get("InPrefix") for n in calls(g, "StartsWith")])

    def test_scan_all(self):
        """The full scan finds folders named unlike any pak (TKA_StripClub in ToxicVelvet.pak); they go to Extra, read back while they exist."""
        g = mgr_graph("Obj Scan All Step"); f = fns(g)
        self.assertTrue({"ScanPathsSynchronous", "GetSubPaths", "K2_SetTimer"} <= f)
        self.assertEqual(calls(g, "ScanPathsSynchronous")[0]["in"]["InPaths"], "@arr.Array")
        self.assertIn("Extra", {n.get("var") for n in g["nodes"] if n["kind"] == "get"})
        self.assertIn("DirectoryExists", fns(mgr_graph("Obj Scan Mods")))
        self.assertEqual(calls(mgr_graph("Obj Scan All"), "K2_SetTimer")[0]["in"]["FunctionName"], "Obj Scan All Step")
        import gen_manager_ui as ui
        self.assertIn(("ObjScanAll", "Obj Scan All", None), ui.MENU_ACTIONS)

    def test_take_folder_once(self):
        g = mgr_graph("Obj Take Folder"); self.assertIn("ObjSeen", {n.get("var") for n in g["nodes"] if n["kind"] == "get"})

    def test_mod_category_ignores_case(self):
        """ui-test-148: categories arrive as "mod:<Mod>" too (a name keeps its first spelling) - no case-sensitive "Mod:" test anywhere."""
        for fname in ("Obj Scan", "Obj Shows", "Rebuild Obj Cats"):
            g = mgr_graph(fname); sw = [n for n in calls(g, "StartsWith") if n["in"]["InPrefix"] == "Mod:"]
            self.assertTrue(sw, fname)
            for n in sw: self.assertEqual(n["in"]["SearchCase"], "IgnoreCase", fname)

    def test_category_graph_prefixes(self):
        g = mgr_graph("Obj Category"); pre = {n["in"]["InPrefix"] for n in calls(g, "StartsWith")}
        self.assertEqual(pre, set(objects.ROOTS))

    def test_spawn(self):
        g = mgr_graph("Obj Spawn"); f = fns(g)
        self.assertTrue({"Set Model", "Set Physics", "LineTraceSingle"} <= f)
        self.assertTrue(any(n["kind"] == "spawn" for n in g["nodes"]))


class Pictures(unittest.TestCase):
    def test_capture_sets_photo_kind(self):
        g = mgr_graph("Capture Obj Icon"); sets = {n["var"]: n["in"] for n in g["nodes"] if n["kind"] == "set"}
        self.assertEqual(sets["PhotoKind"]["PhotoKind"], "Object"); self.assertIn("PhotoOnly", sets)
        self.assertTrue({"Capture Photo", "SetVisibleInSceneCaptureOnly", "Set Model"} <= fns(g))

    def test_icon_from_file(self):
        g = mgr_graph("Obj Icon"); self.assertIn("ImportFileAsTexture2D", fns(g))
        self.assertIn(objects.ICON_DIR, [n.get("in", {}).get("B") for n in g["nodes"]])

    def test_finish_photo_object_branch(self):
        g = mgr_graph("Finish Photo"); n = {x["id"]: x for x in g["nodes"]}
        self.assertEqual(n["iso"]["in"]["B"], "Object")
        self.assertIn(["bo:else", "bw", "dsw", "wrm", "rrm", "rws", "rwm"], g["exec"])


class Tab(unittest.TestCase):
    def test_after_ragdolls(self):
        import gen_manager_ui as ui
        self.assertEqual(ui.TOP_TABS[ui.TOP_TABS.index("Navigation") + 1], "Objects"); self.assertEqual(ui.TOP_TABS[-1], "TV")

    def test_tile_click_spawns(self):
        g = mgr_graph("On Item Clicked"); self.assertIn("Obj Tile Clicked", fns(g))
        self.assertIn("Obj Spawn", fns(mgr_graph("Obj Tile Clicked")))
        self.assertNotIn("Conv_StringToInt", fns(mgr_graph("Obj Tile Clicked")))   # the tile's name is the path, not an index

    def test_context_menu(self):
        self.assertIn("On Obj Context", fns(mgr_graph("On Item Context")))
        import gen_manager_ui as ui
        for a in (("ObjFav", "Toggle Obj Favorite", "ContextItem"), ("ObjSpawnPhys", "Obj Spawn Phys", "ContextItem"), ("ObjMore", "Obj More", None)):
            self.assertIn(a, ui.MENU_ACTIONS)
        self.assertNotIn("ObjProbe", [a[0] for a in ui.MENU_ACTIONS])

    def test_left_column_click(self):
        self.assertIn("Select Obj Cat", fns(mgr_graph("Select Slot")))
        g = mgr_graph("Rebuild Obj Cats"); self.assertTrue({"Obj Cat Caption", "Add Obj Cat"} <= fns(g))

    def test_tiles_sorted_filtered_paged(self):
        g = mgr_graph("Rebuild Obj Tiles"); f = fns(g)
        self.assertTrue({"Obj Shows", "Obj Icon", "Is Obj Favorite", "Add Obj Tile", "Add Obj More", "Obj Next Icon"} <= f)
        self.assertIn("ObjOrder", {n.get("var") for n in g["nodes"] if n["kind"] == "get"})

    def test_note_added_everywhere(self):
        for fname in ("Obj Scan", "Obj Add Path"): self.assertIn("Obj Note Added", fns(mgr_graph(fname)), fname)
        self.assertEqual(len(calls(mgr_graph("Obj Note Added"), "Sort Key")), 4)   # model name + category, two keys each

    def test_select_page(self):
        self.assertIn("Rebuild Objects", fns(mgr_graph("Select Page")))


class Move(unittest.TestCase):
    """Bauschritt 3: objects move like the ragdolls (spec table)."""
    def test_scaled(self):
        self.assertAlmostEqual(objects.scaled(1.0, 1), 1.1); self.assertAlmostEqual(objects.scaled(1.0, -1), 1 / 1.1)
        self.assertEqual(objects.scaled(19.0, 5), objects.SCALE_MAX); self.assertEqual(objects.scaled(0.06, -5), objects.SCALE_MIN)

    def test_begin_drag_picks_objects_after_figures(self):
        g = mgr_graph("Begin Jodi Drag"); f = fns(g)
        self.assertTrue({"Rag Pick", "Obj Pick", "Obj Begin Drag"} <= f)
        self.assertIn(["brg:else", "bopk", "obd", "oret"], g["exec"])

    def test_begin_drag_paths(self):
        g = mgr_graph("Obj Begin Drag"); f = fns(g)
        self.assertTrue({"GrabComponentAtLocationWithRotation", "Set Physics", "Body"} <= f)   # physics: handle; right: fixed while turning
        sets = {n["var"] for n in g["nodes"] if n["kind"] == "set"}
        self.assertTrue({"ObjDrag", "RagGrab", "RagClick", "RagMove", "ObjReactivate", "JodiDrag"} <= sets); self.assertIn("Obj Select", f)

    def test_drag_routes(self):
        self.assertIn("Obj Drag Update", fns(mgr_graph("Jodi Drag"))); self.assertIn("Obj Drag End", fns(mgr_graph("End Jodi Drag")))
        self.assertIn("Obj Wheel", fns(mgr_graph("Rag Lift")))
        g = mgr_graph("Obj Wheel"); self.assertTrue({"SetActorScale3D", "K2_AddActorWorldOffset", "MultiplyMultiply_FloatFloat"} <= fns(g))
        self.assertEqual(calls(g, "FClamp")[0]["in"]["Max"], str(objects.SCALE_MAX))
        self.assertIn("RotatorFromAxisAndAngle", fns(mgr_graph("Obj Drag Update")))
        self.assertIn("Set Physics", fns(mgr_graph("Obj Drag End")))

    def test_frame_edges(self):
        import gen_prop
        e = gen_prop.frame_edges(); self.assertEqual(len(e), 12); self.assertEqual(len(set(e)), 12)
        self.assertEqual(sorted(a for a, *_ in e), [0] * 4 + [1] * 4 + [2] * 4)
        self.assertTrue(all(a not in (b, c) for a, b, _, c, _ in e))

    def test_select_shows_frame(self):
        g = mgr_graph("Obj Select"); self.assertEqual([n["in"]["on"] for n in calls(g, "Show Frame")], ["false", "true"])
        for fname in ("Obj Tile Clicked", "Obj Spawn Phys", "Obj Begin Drag", "Obj Sel Copy"): self.assertIn("Obj Select", fns(mgr_graph(fname)), fname)

    def test_selected_block(self):
        g = mgr_graph("Obj Sel Refresh"); self.assertTrue({"Set Obj Sel", "Set Obj Fields", "Obj Icon"} <= fns(g))
        g = mgr_graph("Obj Fields Commit"); self.assertTrue({"Get Obj Fields", "K2_SetActorTransform", "Set Physics", "Fit Frame"} <= fns(g))
        import gen_manager_ui as ui
        for a in ("ObjSelPhys", "ObjSelFloor", "ObjSelCopy", "ObjSelRemove"): self.assertIn(a, [x[0] for x in ui.MENU_ACTIONS])

    def test_wheel_on_held_physics_object(self):
        """ui-test-153: the wheel zoomed the camera while an object with physics was held."""
        self.assertIn("Obj Grab Wheel", fns(mgr_graph("Rag Lift")))
        sets = {n["var"]: n["in"] for n in mgr_graph("Obj Begin Drag")["nodes"] if n["kind"] == "set"}
        self.assertEqual(sets["ObjGrab"]["ObjGrab"], "true")
        self.assertIn("RagGrabLift", {n.get("var") for n in mgr_graph("Ragdoll Grab Update")["nodes"] if n["kind"] == "get"})

    def test_wheel_on_held_ragdoll_part(self):
        """2026-10-23 (user): same control for figures - the wheel lifts the held part of an active figure."""
        g = mgr_graph("Rag Lift"); self.assertIn("Ragdoll Grab Update", fns(g))
        sets = {n["var"] for n in mgr_graph("Begin Jodi Drag")["nodes"] if n["kind"] == "set"}; self.assertIn("RagGrabLift", sets)
        self.assertIn("RagMove", {n["var"] for n in mgr_graph("Rag Pin Grab")["nodes"] if n["kind"] == "set"})

    def test_fields_keep_focus_on_enter(self):
        import json, os
        w = json.load(open(os.path.join(os.path.dirname(objects.__file__), "..", "40_widgets.json")))
        def walk(t):
            yield t
            for c in t.get("children", []): yield from walk(c)
        found = {}
        for a in w["assets"]:
            if a.get("widget_tree"):
                for n in walk(a["widget_tree"]):
                    if n.get("name", "").startswith("ObjF") and n.get("class", "").endswith("EditableTextBox"): found[n["name"]] = n.get("props", {})
        self.assertEqual(len(found), 7, found.keys())
        for k, p in found.items(): self.assertIs(p.get("ClearKeyboardFocusOnCommit"), False, k)

    def test_ctrl_reaches_the_wheel(self):
        g = mgr_graph("Ragdoll Mode Step"); self.assertEqual(calls(g, "Rag Lift")[0]["in"]["ctrl"], "@ctl.ReturnValue")


class World(unittest.TestCase):
    """Bauschritt 4: in the world, positions, scenes (SG_Props)."""
    def test_left_column_world(self):
        g = mgr_graph("Rebuild Obj Cats"); f = fns(g); self.assertIn("Obj Scenes Here", f)
        self.assertTrue({objects.CAT_WORLD, objects.CAT_SCENES} <= {n["in"].get("slot") for n in calls(g, "Init")})

    def test_right_side_routes(self):
        self.assertTrue({"Rebuild Obj World", "Rebuild Obj Scenes", "Rebuild Obj Tiles"} <= fns(mgr_graph("Rebuild Obj Right")))

    def test_scene_save_replaces_same_name_level(self):
        g = mgr_graph("Save Obj Scene"); f = fns(g); self.assertTrue({"Where", "Array_Set", "Array_Add", "SaveGameToSlot", "EqualEqual_StriStri"} <= f)
        self.assertEqual(calls(g, "SaveGameToSlot")[0]["in"]["SlotName"], objects.PROPS_SLOT)

    def test_scene_load_replaces_and_counts_missing(self):
        g = mgr_graph("Load Obj Scene"); f = fns(g); self.assertTrue({"Obj Remove All", "Obj Spawn", "K2_SetActorTransform", "Set Physics", "Pop Notice"} <= f)

    def test_place_same_model_only(self):
        g = mgr_graph("Apply Obj Place"); self.assertIn("EqualEqual_StrStr", fns(g))
        g = mgr_graph("Save Obj Place"); self.assertEqual(len([n for n in calls(g, "EqualEqual_StrStr")]), 2)   # level + model (name: StriStri)

    def test_chips_and_links(self):
        self.assertTrue({"Load Obj Scene", "Apply Obj Place"} <= fns(mgr_graph("Select SubTab")))
        self.assertTrue({"Load Obj Scene", "Apply Obj Place"} <= fns(mgr_graph("Context Chip Apply")))
        self.assertTrue({"Delete Obj Scene", "Delete Obj Place"} <= fns(mgr_graph("Context Chip Delete")))
        self.assertIn("Obj World Action", fns(mgr_graph("On Menu Action")))

    def test_world_on_top(self):
        """2026-10-24 (user): WORLD above CATALOGUE in the left column - the chain starts with the WORLD head."""
        g = mgr_graph("Rebuild Obj Cats"); ent = next(c for c in g["exec"] if c[0] == "entry")
        self.assertEqual(ent[:3], ["entry", "cl", "hww_cr"])

    def test_world_rows_follow_click_in_world(self):
        """ui-test-160: selecting an object in the world left the "›" mark of In the world on the old row."""
        self.assertIn("Rebuild Obj World", fns(mgr_graph("Obj Begin Drag")))

    def test_deselect(self):
        """2026-10-24 (user): an object could be selected but not deselected - Selected block link + "Select" on the selected row."""
        import gen_manager_ui as ui
        self.assertIn(("ObjSelNone", "Obj Sel None", None), ui.MENU_ACTIONS)
        g = mgr_graph("Obj Sel None"); self.assertEqual([n["in"]["actor"] for n in g["nodes"] if n.get("function") == "Obj Select"], ["None"])
        self.assertIn("Rebuild Obj World", fns(g))
        g = mgr_graph("Obj World Action"); self.assertIn("None", [n["in"]["actor"] for n in g["nodes"] if n.get("function") == "Obj Select"])
        self.assertIn("Obj_Deselect", json.dumps(mgr_graph("Rebuild Obj World")))

    def test_search_filters_world_pages(self):
        """2026-10-24 (user): the search box built catalogue tiles on the WORLD pages; now it filters their rows."""
        self.assertIn("Rebuild Obj Right", fns(mgr_graph("On Obj Search Changed")))
        self.assertNotIn("Rebuild Obj Tiles", fns(mgr_graph("On Obj Search Changed")))
        for name in ("Rebuild Obj World", "Rebuild Obj Scenes"):
            g = mgr_graph(name); self.assertTrue(any("ObjSearchText" in str(n) for n in g["nodes"]), name); self.assertIn("Contains", fns(g), name)


if __name__ == "__main__":
    unittest.main()
