"""2026-10-19 (spec 2026-10-19-usage-design): Manage > Usage - which mods are in use, where, and which are not."""
import unittest, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen")); sys.path.insert(0, H)
from test_fol_tab import mgr_graph, fn_graph, asset
import strings, strings_fr

KEYS = ["Cat_Usage", "Usage_Count", "Usage_UnusedHead", "Usage_Unknown", "Usage_Now", "Usage_Look", "Usage_Preset",
        "Usage_FavClothes", "Usage_FavHair", "Usage_FavLook", "Usage_FavPose", "Usage_FavWeapon", "Usage_Follower", "Usage_Bag",
        "Usage_RagPreset", "Usage_Idle", "Usage_Weapon", "Usage_Outfit"]
CARD = "/Game/Mod/AltUI/W_UsageCard"; ROW = "/Game/Mod/AltUI/W_UsageRow"; TXT = "/Game/Mod/AltUI/W_TextButton"
PANEL = "/Game/Mod/AltUI/W_AltUI"


def calls(g, f): return [n for n in g["nodes"] if n.get("function") == f]


class Texts(unittest.TestCase):
    def test_all_languages(self):
        for k in KEYS:
            self.assertEqual(len(strings.STRINGS[k]), 7, k); self.assertIn(k, strings_fr.FR, k)
        for s in strings.STRINGS["Usage_Count"]: self.assertIn("%s", s)

    def test_cat_keys(self):
        # place cats, their plurals and the kind column are looked up by a key built at run time
        import gen_manager_ui as ui
        for k in list(ui.USAGE_CATS) + [c + "_Pl" for c in ui.USAGE_PLURAL] + ["Usage_K_" + k for k in ui.USAGE_KINDS]:
            self.assertEqual(len(strings.STRINGS[k]), 7, k); self.assertIn(k, strings_fr.FR, k)


def wnames(tree):
    out = [tree["name"]]
    for c in tree.get("children", []): out += wnames(c)
    return out


class Tiles(unittest.TestCase):
    def test_card(self):
        a = asset(CARD); names = [f["name"] for f in a["functions"]]
        for f in ("Init", "Set Count", "Add Link", "Add Row", "Compute Colors"): self.assertIn(f, names)
        for wn in ("Bg", "Title", "Pak", "Count", "Links", "Rows"): self.assertIn(wn, wnames(a["widget_tree"]))

    def test_row_columns(self):
        a = asset(ROW); init = [f for f in a["functions"] if f["name"] == "Init"][0]
        self.assertEqual([p["name"] for p in init["inputs"]], ["a", "b", "c", "wa", "wb", "dim"])
        for wn in ("ABox", "BBox", "A", "B", "C", "Links"): self.assertIn(wn, wnames(a["widget_tree"]))

    def test_small_links(self):
        self.assertIn("Set Font Size", [f["name"] for f in asset(TXT)["functions"]])

    def test_panel_head_toggle(self):
        self.assertIn("Set Manage Head Visible", [f["name"] for f in asset(PANEL)["functions"]])


class Scan(unittest.TestCase):
    def test_sources(self):
        g = mgr_graph("Scan Usage"); fns = {n.get("function") for n in g["nodes"]}
        for f in ("Take Snapshot", "Content Snapshot", "Usage Add Snap", "Usage Add", "Load Fol Save", "Load Rag Save", "Load Drawers", "Usage Mod Of", "Usage Place"): self.assertIn(f, fns, f)
        cats = {n["in"]["cat"] for n in calls(g, "Usage Place")}
        self.assertEqual(cats, {"Usage_Outfit", "Usage_Look", "Usage_Preset", "Usage_Follower", "Usage_RagPreset", "Usage_PropScene", "Usage_PropPlace", "Usage_Drawer"})   # drawers: 2026-10-24
        gets = {n.get("var") for n in g["nodes"] if n.get("kind") == "get"}
        for v in ("Favorites", "WeaponSkins", "WeaponModels", "WeaponSounds", "IdleStyle", "IdlePose", "FolSave", "RagSave", "UsageWhere", "UsageMods", "ViewSnap", "ViewTitle"): self.assertIn(v, gets, v)
        self.assertEqual({n["in"]["kind"] for n in calls(g, "Content Snapshot")}, {"Outfit", "Look", "Preset"})

    def test_favourite_prefixes(self):
        pre = {n["in"]["InPrefix"] for n in mgr_graph("Scan Usage")["nodes"] if n.get("function") == "StartsWith"}
        self.assertEqual(pre, {"hair:", "makeup:", "pose:", "model:", "sound:", "skin:"})

    def test_snap_parts(self):
        kinds = sorted(n["in"]["kind"] for n in calls(mgr_graph("Usage Add Snap"), "Usage Add"))
        self.assertEqual(kinds, ["body", "hair", "item", "look", "look"])

    def test_mod_of(self):
        fns = {n.get("function") for n in mgr_graph("Usage Mod Of")["nodes"]}
        self.assertTrue({"Origin Mod", "Row Mod", "Array_Contains"} <= fns)

    def test_place_once(self):
        self.assertTrue(calls(mgr_graph("Usage Add"), "Contains"))


class Page(unittest.TestCase):
    def test_category(self):
        import gen_manager_ui as ui
        cats = [c for c, _ in ui.MANAGE_CATS]; self.assertEqual(cats[cats.index("Mods") + 1], "Usage")
        self.assertIn("Usage", ui.MANAGE_NO_ONLY_MODS); self.assertNotIn("Usage", ui.MANAGE_CHIP_CATS); self.assertNotIn("Usage", ui.MANAGE_SUBS)

    def test_rebuild_manage_branches(self):
        g = mgr_graph("Rebuild Manage"); self.assertTrue(calls(g, "Rebuild Usage")); self.assertTrue(calls(g, "Set Manage Head Visible"))

    def test_scan_before_counts(self):
        self.assertTrue(calls(mgr_graph("Rebuild Manage Cats"), "Scan Usage"))
        self.assertTrue(calls(mgr_graph("Manage Rows"), "Usage Mod Shown"))

    def test_scan_only_on_usage_page(self):
        g = mgr_graph("Rebuild Manage Cats")   # ui-test-132 #9: no scan cost on the other Manage pages
        self.assertTrue([n for n in g["nodes"] if n.get("function") == "EqualEqual_NameName" and n.get("in", {}).get("B") == "Usage"])
        self.assertTrue([n for n in g["nodes"] if n.get("var") == "UsageScanned"])

    def test_view_content_action(self):
        g = mgr_graph("On Menu Action")
        self.assertTrue([n for n in g["nodes"] if n.get("in", {}).get("InPrefix") == "UsageMod:"])
        self.assertTrue(calls(g, "Open Mod Content"))

    def test_tiles(self):
        g = mgr_graph("Rebuild Usage"); fns = {n.get("function") for n in g["nodes"]}
        for f in ("Usage Lists", "Usage Mod Shown", "Usage Part Shown", "Usage Part Name", "Usage Kind", "Usage Places", "Usage Mod Caption", "Add Link", "Add Row",
                  "Set Count", "Set Font Size", "Add Manage Row", "Set Manage Head Visible"): self.assertIn(f, fns, f)
        self.assertEqual(len(calls(g, "Add Manage Row")), 3)   # a tile per mod in use, the unused tile, the not detectable tile
        dims = sorted(n["in"]["dim"] for n in g["nodes"] if n.get("function") == "Init" and "wa" in n.get("in", {}))
        self.assertEqual(dims, ["false", "true", "true"])   # piece rows normal, the rows of unused / not detectable mods grey
        self.assertEqual(len(calls(g, "Set Font Size")), 3)

    def test_pak_name(self):
        g = mgr_graph("Rebuild Usage")
        self.assertEqual(len([n for n in g["nodes"] if n.get("in", {}).get("B") == ".pak"]), 3)

    def test_places_format(self):
        g = mgr_graph("Usage Places"); fns = {n.get("function") for n in g["nodes"]}
        for f in ("ParseIntoArray", "Usage Cat Flush", "Usage Run Flush", "Usage Name Add"): self.assertIn(f, fns, f)
        self.assertIn("–", {n.get("in", {}).get("B") for n in mgr_graph("Usage Run Flush")["nodes"]})
        self.assertIn(" · ", {n.get("in", {}).get("B") for n in mgr_graph("Usage Cat Flush")["nodes"]})

    def test_lists(self):
        g = mgr_graph("Usage Lists"); self.assertEqual(len(calls(g, "Sort Chips")), 3)
        gets = {n.get("var") for n in g["nodes"] if n.get("kind") == "get"}
        self.assertTrue({"ModList", "BodyMods", "IdleMods", "UsageMods"} <= gets)


if __name__ == "__main__":
    unittest.main()
