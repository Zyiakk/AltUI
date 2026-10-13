"""Followers tab and figure (game test 2026-10-10): never both top columns folded; the rows are a table (fixed columns, every chip
in its own); a figure goes through the game's start of a runtime spawn (anim class, order), without the game's random NPC
appearance and default clothes."""
import unittest, os, sys, json

H = os.path.dirname(os.path.abspath(__file__)); ASSETS = os.path.join(H, "..", "..", "assets")
sys.path.insert(0, os.path.join(ASSETS, "gen"))
import followers as fol


def assets():
    for f in sorted(os.listdir(ASSETS)):
        if f.endswith(".json") and f[0].isdigit():
            with open(os.path.join(ASSETS, f)) as fh: data = json.load(fh)
            yield from data["assets"]


def asset(path):
    return next(a for a in assets() if a.get("path") == path)


def fn_graph(owner, name):
    for f in asset(owner).get("functions", []):
        if f.get("name") == name and f.get("graph"): return f["graph"]
    raise AssertionError("%s not in %s" % (name, owner))


MGR = "/Game/Mod/AltUI/BP_AltUIManager"


def mgr_graph(name):
    g = None   # 50_manager_ui.json overrides 30_manager.json (files in order)
    for a in assets():
        if a.get("path") != MGR: continue
        for f in a.get("functions", []):
            if f.get("name") == name and f.get("graph"): g = f["graph"]
    return g


class FoldColumns(unittest.TestCase):
    def test_folding_one_unfolds_the_other(self):
        g = mgr_graph("Fol Chip"); by = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(by["soBag"].get("var"), "FolFoldBox"); self.assertEqual(by["soBox"].get("var"), "FolFoldBag")
        self.assertIn(["entry", "bfBag", "sfBag", "soBag", "svs"], g["exec"])

    def test_a_saved_double_fold_is_undone(self):
        g = mgr_graph("Rebuild Followers"); self.assertTrue(any(n["id"] == "snx" and n.get("var") == "FolFoldBox" for n in g["nodes"]))


class TableRows(unittest.TestCase):
    def test_every_chip_has_its_column(self):
        row = asset(fol.W_FOLROW); names = {f["name"] for f in row["functions"]}
        for k, _ in fol.FOL_COLS: self.assertIn("Set Chip " + k, names)
        self.assertNotIn("Add Chip", names)
        calls = {n["function"] for n in mgr_graph("Rebuild Followers")["nodes"] if n.get("function", "").startswith("Set Chip ")}
        self.assertEqual(calls, {"Set Chip " + k for k, _ in fol.FOL_COLS})

    def test_columns_fit_every_language(self):
        import strings
        for k, keys in fol.FOL_COLS:
            longest = max(len(t) for key in keys for t in strings.STRINGS[key])
            self.assertGreaterEqual(fol.col_width(keys), longest * fol.CHIP_CHAR, k)


class RuntimeStart(unittest.TestCase):
    def test_spawn_runs_the_games_start(self):
        g = mgr_graph("Fol Spawn")
        self.assertTrue(any(n.get("function") == "on Spawn in Runtime" for n in g["nodes"]))
        # also when the controller cast fails (no master set), and before the bag is filled
        self.assertIn(["ct:CastFailed", "osr"], g["exec"])
        main = next(c for c in g["exec"] if c[0] == "entry")
        self.assertLess(main.index("osr"), main.index("cgn"))

    def test_the_figure_keeps_its_look(self):
        names = {f["name"]: f for f in asset("/Game/Mod/AltUI/BP_AltUIFollower")["functions"]}
        for n in ("Init Npc Appearance",):   # Check Appearence is the game's again since 2026-10-12 (RealClothes)
            self.assertIn(n, names); self.assertTrue(names[n].get("override")); self.assertFalse(names[n]["graph"]["nodes"], n)


class RealClothes(unittest.TestCase):
    """2026-10-12: the figure wears the game's clothes and hair (docs/specs/2026-10-12-follower-echte-kleidung-design.md). Heels come
    from Clothes_Comp.Wear again (the copy of 2026-10-10 is gone), Check Appearence is the game's, the bag gets its pieces before the start."""
    FOL = "/Game/Mod/AltUI/BP_AltUIFollower"

    def test_clothes_are_taken_while_jodi_wears_the_look(self):
        g = mgr_graph("Finish Look Follower"); main = next(c for c in g["exec"] if c[0] == "fwc:Completed")
        prev = next(c for c in g["exec"] if c[0] == "fm:Completed")
        self.assertIn("swn", prev, "worn pieces read before Undo"); self.assertIn("un", main)
        self.assertIn("Worn", next(n for n in g["nodes"] if n["id"] == "nr")["in"])

    def test_check_appearence_only_underwear(self):
        """ui-test-88 #10/#11: the game's Check Appearence put the whole default outfit on a look without clothes; Jodi gets underwear only."""
        names = [f.get("name") for f in asset(self.FOL).get("functions", [])]
        self.assertIn("Init Npc Appearance", names)   # still nothing: no random NPC
        g = fn_graph(self.FOL, "Check Appearence")
        self.assertTrue(any(n.get("function") == "check clothes covering" for n in g["nodes"]))
        self.assertNotIn("Default Clothes", json.dumps(g))

    def test_no_heel_copy(self):
        self.assertNotIn("LookHeel", json.dumps(asset(self.FOL)))
        self.assertFalse(any(n.get("function") == "Set Heel Height" for n in fn_graph(self.FOL, "Apply Look")["nodes"]))

    def test_set_look_fills_bag_before_start(self):
        g = json.dumps(fn_graph(self.FOL, "Set Look"))
        for s in ("Save Player Clothes", "Append Clothes", "Clothes Colors", "Save Clothes Damaged"):
            self.assertIn(s, g)

    def test_sync_reads_clothes(self):
        g = json.dumps(mgr_graph("Fol Sync"))
        for s in ("Clothes in bag", "Get Wearing Clothes Names", "Clothes Colors", "Save Clothes Damaged"):
            self.assertIn(s, g)

    def test_a_piece_from_the_games_swap_gets_its_colours_at_once(self):
        """ui-test-88 #6: a jacket coloured in AltUI went over blue - its slot colours came only with the 10 s sync."""
        g = mgr_graph("Fol Level Start")
        self.assertTrue(any(n.get("function") == "K2_SetTimer" and n["in"].get("FunctionName") == "Fol Watch" for n in g["nodes"]))
        self.assertLessEqual(fol.FOL_WATCH, 0.05)
        w = json.dumps(mgr_graph("Fol Watch")); self.assertIn("FolBagCount", w); self.assertIn("Fol Sync", w)
        g = mgr_graph("Fol Watch"); first = next(c for c in g["exec"] if c[0] == "entry")
        self.assertEqual(first[1:3], ["bvi", "bop"], "nothing else before the swap dialog is known to be shown")
        self.assertIn("InventoryNpc", w)
        self.assertIn("FolBagCount", json.dumps(mgr_graph("Fol Sync")))

    def test_remove_and_relook_return_clothes(self):
        self.assertIn("Fol Clothes To Jodi", json.dumps(mgr_graph("Fol Remove")))
        self.assertIn("Fol Record Clothes To Jodi", json.dumps(mgr_graph("Fol Remove")))
        g = json.dumps(mgr_graph("Finish Look Follower"))
        self.assertIn("Fol Clothes To Jodi", g); self.assertIn("Fol Record Clothes To Jodi", g)

    def test_tab_has_clothes_tiles_and_actions(self):
        rb = json.dumps(mgr_graph("Rebuild Followers"))
        self.assertIn(fol.TILE_FOL_CLOTHES, rb); self.assertIn(fol.TILE_BAG_CLOTHES, rb); self.assertIn("Fol_OldLook", rb)
        clk = json.dumps(mgr_graph("On Fol Clicked"))
        self.assertIn("Fol Clothes Take", clk); self.assertIn("Fol Clothes Give", clk)
        both = json.dumps(mgr_graph("On Fol Context")) + json.dumps(mgr_graph("Fol Tile Action"))
        for a in ("TakeOff", "Repair", "RepairAll"): self.assertIn("FolT:" + a, both)

    def test_repair_costs_a_sewing_kit(self):
        self.assertIn(fol.SEWING_KIT, json.dumps(mgr_graph("Fol Repair")))

    def test_give_carries_damage_colour_and_slot_colours(self):
        g = json.dumps(mgr_graph("Fol Clothes Give"))
        for s in ("Store Clothes Damage", "Save Clothes Color", "Remove Clothing From Bag", "Put Item to Bag", "Fol Apply Slot Colors", "Fol_OldLookGive"):
            self.assertIn(s, g)

    def test_give_returns_displaced_pieces_and_refreshes(self):
        """ui-test-89 #7: what a given piece pushes off its slot stays in the figure's bag (the game only takes it off) - to Jodi;
        AltUI's own state (Backpack tab) follows."""
        g = json.dumps(mgr_graph("Fol Clothes Give"))
        for s in ("is clothes wearing", "Fol Clothes To Jodi", "Refresh State"): self.assertIn(s, g)
        self.assertIn("Refresh State", json.dumps(mgr_graph("Fol Clothes Take")))

    def test_notices_above_the_panel(self):
        """ui-test-89 #15/#16: the game's notice widget lies on the player screen, under AltUI's panel (viewport, ZOrder 100)."""
        n = {x["id"]: x for x in mgr_graph("Pop Notice")["nodes"]}
        self.assertEqual(n["au"]["function"], "Get Attention UI"); self.assertEqual(n["av"]["function"], "AddToViewport")
        self.assertGreater(int(n["av"]["in"]["ZOrder"]), 100)

    def test_apply_look_sets_body_material_and_hair(self):
        g = json.dumps(fn_graph(self.FOL, "Apply Look"))
        for s in ("Body Material", "Change Hairstyle Ex"):
            self.assertIn(s, g)


if __name__ == "__main__":
    unittest.main()
