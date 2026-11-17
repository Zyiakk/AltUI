"""AltUI appends the rows of a mod's extra tables to the game's tables, skips rows that exist, and does so in the main menu
(before a level restores its weapons) as well as in a level (before the catalog is built)."""
import unittest, os, json
H = os.path.dirname(os.path.abspath(__file__)); ASSETS = os.path.join(H, "..", "..", "assets")


def manager():
    for f in sorted(os.listdir(ASSETS)):
        if f.endswith(".json"):
            for a in json.load(open(os.path.join(ASSETS, f))).get("assets", []):
                for fn in a.get("functions", []):
                    if fn["name"] == "Merge Extra Tables":
                        return a, fn
    raise AssertionError("no Merge Extra Tables")


class MergeExtraTables(unittest.TestCase):
    def test_appends_both_tables_through_the_native_function(self):
        _, fn = manager()
        calls = [n for n in fn["graph"]["nodes"] if n.get("function") == "AppendDataTableRow"]
        self.assertEqual(len(calls), 2)
        self.assertTrue(all(c["class"] == "/Script/TheKillingAntidote.McoreFunctionLibrary" for c in calls))
        self.assertEqual(sorted(c["in"]["DestTable"] for c in calls),
                         ["/Game/Project/Tables/ItemTable", "/Game/Project/Tables/WeaponTable"])

    def test_skips_rows_that_exist(self):
        _, fn = manager()
        self.assertEqual(sum(n.get("function") == "DoesDataTableRowExist" for n in fn["graph"]["nodes"]), 2)

    def test_runs_in_menu_and_level(self):
        a, _ = manager()
        calls = [n for n in a["event_graph"]["nodes"] if n.get("kind") == "call_self" and n.get("function") == "Merge Extra Tables"]
        self.assertEqual(len(calls), 2)

    def test_wiring_exists_not_branch_append(self):
        """Without the Not the rows would be appended only when they exist; without the branch every row, every manager."""
        _, fn = manager(); g = fn["graph"]; n = {x["id"]: x for x in g["nodes"]}
        for p in ("m0", "m1"):
            with self.subTest(table=p):
                self.assertIn([p + "_fr", p + "_ex", p + "_b", p + "_ap"], g["exec"])
                self.assertEqual(n[p + "_ex"]["in"]["RowName"], "@%s_fr.Array Element" % p)
                self.assertEqual(n[p + "_no"]["function"], "Not_PreBool"); self.assertEqual(n[p + "_no"]["in"]["A"], "@%s_ex.ReturnValue" % p)
                self.assertEqual(n[p + "_b"]["in"]["Condition"], "@%s_no.ReturnValue" % p)
                self.assertEqual(n[p + "_ap"]["in"]["rowName"], "@%s_fr.Array Element" % p); self.assertEqual(n[p + "_ap"]["in"]["SourceTable"], "@%s_ck.AsData Table" % p)
                self.assertEqual(n[p + "_ex"]["in"]["Table"], n[p + "_ap"]["in"]["DestTable"])
                self.assertFalse(any(c[0] == p + "_b:else" for c in g["exec"]))

    def test_mod_without_a_table_goes_on_with_the_next(self):
        _, fn = manager(); g = fn["graph"]; n = {x["id"]: x for x in g["nodes"]}
        # 2026-11-15: per table only the mods that have it (Mod File Index), one loop each; no file / no table: the body ends, the next mod follows
        self.assertIn(["entry", "m0_mf_s", "m0_fe"], g["exec"]); self.assertIn(["m0_fe:Completed", "m1_mf_s", "m1_fe"], g["exec"])
        for p in ("m0", "m1"):
            self.assertIn([p + "_fe", p + "_bx"], g["exec"]); self.assertIn([p + "_bx", p + "_ld", p + "_ck"], g["exec"]); self.assertIn([p + "_ck", p + "_rows", p + "_fr"], g["exec"])
            self.assertEqual(n[p + "_ck"].get("miss"), "ignore"); self.assertEqual(n[p + "_fe"]["in"]["Array"], "@%s_mf_l.ModFilesMerge" % p)
        self.assertFalse([x for x in g["nodes"] if x.get("in", {}).get("Table") == "/Game/Project/Tables/DLC_MainTable"])

    def test_merges_before_the_slot_groups_and_the_catalog(self):
        """A level's merge must be through before Build Catalog reads the tables; the menu's before a level's Jodi restores her weapons."""
        a, _ = manager(); ex = a["event_graph"]["exec"]
        main = next(c for c in ex if c[:2] == ["bvg", "cpc"])
        self.assertLess(main.index("swr"), main.index("mxl")); self.assertEqual(main[main.index("mxl") + 1], "isg")
        self.assertIn(["cjb:CastFailed", "mxl"], ex)
        self.assertTrue(any(c[0] == "cj:CastFailed" and c[1] == "mxm" for c in ex), ex)


if __name__ == "__main__":
    unittest.main()
