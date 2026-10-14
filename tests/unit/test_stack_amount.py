"""A chosen amount of a stack (docs/specs/2026-10-14-stack-amount-design.md): which tiles get the amount block, its rows,
the slider / field range and the start value."""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "assets", "gen"))
import inventory as inv


class AmountTables(unittest.TestCase):
    def test_actions_exist(self):
        for a in ("StoreN", "TakeN", "CatBagN", "CatBoxN"):
            self.assertIn(a, inv.ACTIONS)

    def test_rows(self):
        self.assertEqual(inv.amount_rows("bag", "ammo"), ["StoreN"])
        self.assertEqual(inv.amount_rows("box", "usable"), ["TakeN"])
        self.assertEqual(inv.amount_rows("cat", "ammo"), ["CatBagN", "CatBoxN"])
        self.assertEqual(inv.amount_rows("cat", "collect"), ["CatBagN"])
        for box in ("bag", "box", "cat"):
            self.assertEqual(inv.amount_rows(box, "gun"), [])
        self.assertEqual(inv.FOL_AMOUNT_ROWS, {"jodi": ["GiveN"], "fol": ["TakeN", "TakeBoxN"]})

    def test_has_amount(self):
        self.assertTrue(inv.has_amount("bag", "ammo", 2, True)); self.assertFalse(inv.has_amount("bag", "ammo", 1, True))
        self.assertFalse(inv.has_amount("bag", "gun", 5, False)); self.assertTrue(inv.has_amount("box", "weapon", 3, False))
        self.assertTrue(inv.has_amount("cat", "ammo", 0, True)); self.assertFalse(inv.has_amount("cat", "weapon", 0, False))

    def test_stack_range(self):
        self.assertEqual(inv.amount_range(2, 0, False), (1, 2, 1, 2))
        self.assertEqual(inv.amount_range(7, 0, False), (1, 7, 4, 7))
        self.assertEqual(inv.amount_range(300, 30, False), (1, 300, 150, 300))

    def test_catalog_range(self):
        self.assertEqual(inv.amount_range(0, 30, True), (1, 300, 30, inv.AMOUNT_FIELD_MAX))
        self.assertEqual(inv.amount_range(0, 0, True), (1, 10, 1, inv.AMOUNT_FIELD_MAX))   # pick 0 counts as 1


if __name__ == "__main__":
    unittest.main()


class AmountStrings(unittest.TestCase):
    def test_all_languages_with_placeholder(self):
        import strings
        keys = ["Menu_Inv_StoreN", "Menu_Inv_TakeN", "Menu_Inv_CatBagN", "Menu_Inv_CatBoxN", "Fol_GiveN", "Fol_TakeN", "Fol_TakeBoxN"]
        rows = strings.rows()
        for k in keys + ["Menu_Amount"]:
            for lang in strings.LANGS:
                with self.subTest(key=k, lang=lang):
                    t = rows[k][lang]
                    self.assertTrue(t)
                    if k in keys: self.assertEqual(t.count("%s"), 1)


def _walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from _walk(v)
    elif isinstance(o, list):
        for v in o: yield from _walk(v)


def _asset(fname, suffix):
    import json
    with open(os.path.join(os.path.dirname(__file__), "..", "..", "assets", fname), encoding="utf-8") as f:
        return next(o for o in _walk(json.load(f)) if str(o.get("path", "")).endswith(suffix))


class AmountWidget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w = _asset("40_widgets.json", "/W_MenuAmount"); cls.fns = {f["name"]: f for f in cls.w["functions"]}

    def calls(self, fn, target):
        return [n for n in self.fns[fn]["graph"]["nodes"] if n.get("function") == target]

    def test_functions(self):
        for f in ("Init", "Tick", "OnKeyDown", "OnKeyUp", "OnMouseButtonDown"):
            self.assertIn(f, self.fns)

    def test_tick_couples_both_ways(self):
        ex = self.fns["Tick"]["graph"]["exec"]
        self.assertIn(["entry", "bf", "btn", "tsl", "tlv", "tss", "tms"], ex)          # typed -> slider + manager
        self.assertIn(["bf:else", "bsn", "ssl", "ssv", "sms", "bfn"], ex)               # dragged -> manager + field
        self.assertEqual(len(self.calls("Tick", "Menu Amount Set")), 2)
        self.assertEqual(self.calls("Tick", "Clamp")[0]["in"]["Max"], "@gfm.FMax")

    def test_keys(self):
        self.assertTrue(self.calls("OnKeyUp", "On Menu Action")); self.assertTrue(self.calls("OnKeyUp", "Close Menu"))
        for k in ("OnKeyDown", "OnKeyUp"):
            keys = {n["in"]["B"] for n in self.calls(k, "EqualEqual_KeyKey")}
            self.assertEqual(keys, {"Escape", "Enter"})


class AmountManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json
        with open(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "50_manager_ui.json"), encoding="utf-8") as f:
            cls.fns = {o["name"]: o for o in _walk(json.load(f)) if isinstance(o.get("graph"), dict) and "name" in o}

    def test_set_renames_every_row(self):
        g = self.fns["Menu Amount Set"]["graph"]; nodes = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(nodes["rp"]["in"]["From"], "%s"); self.assertEqual(nodes["ri"]["function"], "Init")
        self.assertIn(["entry", "s", "fe"], g["exec"]); self.assertIn(["fe", "ri"], g["exec"])

    def test_guard_leaves_menu_fields_alone(self):
        g = self.fns["Focus Guard"]["graph"]
        self.assertTrue(any(n.get("function") == "HasFocusedDescendants" and n["in"]["self"].endswith(".Menu") for n in g["nodes"]))


class AmountInventory(AmountManager):
    def test_context_has_the_blocks(self):
        g = self.fns["On Inv Context"]["graph"]; nodes = {n["id"]: n for n in g["nodes"]}
        firsts = {k: nodes[k + "_ini"]["in"]["first"] for k in ("abag", "abox", "acat", "acol")}
        self.assertEqual(firsts, {"abag": "Inv:StoreN", "abox": "Inv:TakeN", "acat": "Inv:CatBagN", "acol": "Inv:CatBagN"})
        acts = sorted(n["in"]["InString"] for n in g["nodes"] if n.get("function") == "Conv_StringToName" and n["id"].startswith("acat_"))
        self.assertIn("Inv:CatBoxN", acts)
        self.assertEqual(nodes["acat_ini"]["in"]["fmax"], str(inv.AMOUNT_FIELD_MAX))
        self.assertEqual(nodes["abag_ini"]["in"]["hi"], "@acn.InvCtxCount")
        for ch in g["exec"]:   # a gun's rows go straight to Cancel
            if ch[0] in ("k_bag_gunb", "k_box_gunb"): self.assertNotIn("abag", ch); self.assertNotIn("abox", ch); self.assertEqual(ch[-1], "mr99_cr")

    def test_actions_use_the_amount(self):
        g = self.fns["Inv Action"]["graph"]; nodes = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(nodes["a_storenx"]["in"]["num"], "@a_storenma.MenuAmount")
        self.assertEqual(nodes["a_takenx"]["in"]["num"], "@a_takenma.MenuAmount")
        self.assertEqual(nodes["a_catbagnx"]["in"]["count"], "@a_catbagnma.MenuAmount"); self.assertEqual(nodes["a_catbagnx"]["in"]["packs"], "0")
        self.assertEqual(nodes["a_catbag5x"]["in"]["count"], "0")

    def test_catalog_count_replaces_packs(self):
        for f in ("Inv Cat Bag", "Inv Cat Box"):
            nodes = {n["id"]: n for n in self.fns[f]["graph"]["nodes"]}
            self.assertEqual(nodes["pc"]["in"]["A"], "@entry.count"); self.assertEqual(nodes["n"]["in"]["A"], "@pc.ReturnValue")


class AmountFollowers(AmountManager):
    def test_context_blocks(self):
        g = self.fns["On Fol Context"]["graph"]; nodes = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(nodes["ajd_ini"]["in"]["first"], "FolT:GiveN"); self.assertEqual(nodes["afl_ini"]["in"]["first"], "FolT:TakeN")
        acts = sorted(n["in"]["InString"] for n in g["nodes"] if n.get("function") == "Conv_StringToName" and n["id"].startswith("afl_"))
        self.assertEqual(acts, ["FolT:TakeBoxN", "FolT:TakeN"])
        self.assertIn(["air", "abd", "ajd"], g["exec"])   # Inv Row / Inv Box Count run before the test

    def test_actions(self):
        g = self.fns["Fol Tile Action"]["graph"]; nodes = {n["id"]: n for n in g["nodes"]}
        self.assertEqual(nodes["gn"]["in"]["num"], "@gma.MenuAmount"); self.assertEqual(nodes["tn"]["in"]["box"], "false"); self.assertEqual(nodes["tbn"]["in"]["box"], "true")
        for k, n in (("bGiveN", "gn"), ("bTakeN", "tn"), ("bTakeBoxN", "tbn")):
            self.assertIn([k, n], g["exec"])
