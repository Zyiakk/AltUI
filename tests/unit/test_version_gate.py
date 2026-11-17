"""Version Gate: BeginPlay first compares the game fingerprint; nothing of the game is called before that, and the fingerprint
itself uses engine calls only (a changed game cannot break the check)."""
import unittest, os, json, sys
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, "..", ".."); ASSETS = os.path.join(W, "assets")
sys.path.insert(0, os.path.join(W, "scripts")); import compat_fp


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


class VersionGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        doc = json.load(open(os.path.join(ASSETS, "50_manager_ui.json"), encoding="utf-8"))
        cls.fns = {o["name"]: o for o in walk(doc) if isinstance(o.get("graph"), dict) and "name" in o}
        cls.eg = next(o for o in walk(doc) if str(o.get("path", "")).endswith("BP_AltUIManager"))["event_graph"]

    def test_fingerprint_leaves_out_tables_mods_write_to(self):
        """The game's own mod loader (TKA_GameInstance.Load DLC -> MergeDLCTables) merges mod rows into ClothesTable, HatsTable,
        HairstyleTable, AnimationTable, EyeTable, GunPaint, LevelTable, MakeupTable, MakeupTypeTable, SkinTable, and ClothesGroup
        grows as well (game test 2026-10-11 with clothing mods: ClothesTable 4117 rows instead of 272, ClothesGroup 209 instead of 15)."""
        merged = {"ClothesTable", "ClothesGroup", "HatsTable", "HairstyleTable", "AnimationTable", "EyeTable", "GunPaint", "LevelTable",
                  "MakeupTable", "MakeupTypeTable", "SkinTable"}
        self.assertFalse({p.rsplit("/", 1)[-1] for p in compat_fp.FP_TABLES} & merged)
        self.assertTrue(compat_fp.FP_TABLES)

    def test_fingerprint_takes_out_rows_altui_appended_itself(self):
        """Merge Extra Tables appends mod rows to ItemTable, and every manager checks the fingerprint before it merges: the menu's
        sees 117, the next one 118. So the count leaves out each row of a mod's Mod_ExtraItemTable that ItemTable has by now:
        117 - 0 before the merge, 118 - 1 after it, and the text stays the baseline's."""
        g = self.fns["Game Fingerprint"]["graph"]; n = {x["id"]: x for x in g["nodes"]}; i = compat_fp.FP_TABLES.index("/Game/Project/Tables/ItemTable")
        # the table's own count minus the sum goes into the text, and -1 for a missing table stays -1
        self.assertEqual(n["n%d" % i]["in"]["B"], "-1"); sub = n["n%d" % i]["in"]["A"][1:].split(".")[0]
        self.assertEqual(sub, "fkd"); sub = n["fkd"]["in"]["A"][1:].split(".")[0]   # Keep Loaded's row comes off last (test below)
        self.assertEqual(n[sub]["function"], "Subtract_IntInt")
        self.assertEqual(n[sub]["in"]["A"], "@ln%d.ReturnValue" % i)
        self.assertEqual(n[n[sub]["in"]["B"][1:].split(".")[0]]["var"], "FpExtraRows")
        # the other tables stay plain row counts
        for j in range(len(compat_fp.FP_TABLES)):
            if j != i: self.assertEqual(n["n%d" % j]["in"]["A"], "@ln%d.ReturnValue" % j)
        # the loop: the mods that have the table (Mod File Index, 2026-11-15), its table by path, its rows, only those ItemTable has
        self.assertEqual(n["fxm_f"]["in"]["TargetMap"], "@fxm_g.ModFiles"); self.assertEqual(n["fm"]["in"]["Array"], "@fxm_l.ModFilesFp")
        self.assertFalse([x for x in g["nodes"] if x.get("in", {}).get("Table") == "/Game/Project/Tables/DLC_MainTable"])
        self.assertEqual(n["fx_n2s"]["in"]["InName"], "@fm.Array Element"); self.assertIn("/Mod_ExtraItemTable.Mod_ExtraItemTable", n["fx_c2"]["in"]["B"])
        self.assertEqual(n["fxr"]["in"]["Table"], "@fx_ck.AsData Table"); self.assertEqual(n["ff"]["in"]["Array"], "@fxr.OutRowNames")
        self.assertEqual(n["fxe"]["function"], "DoesDataTableRowExist"); self.assertEqual(n["fxe"]["in"], {"Table": "@ck%d.AsData Table" % i, "RowName": "@ff.Array Element"})
        self.assertEqual(n["fxb"]["in"]["Condition"], "@fxe.ReturnValue")
        self.assertEqual(n["fxa"]["function"], "Add_IntInt"); self.assertEqual(n[n["fxa"]["in"]["A"][1:].split(".")[0]]["var"], "FpExtraRows"); self.assertEqual(n["fxa"]["in"]["B"], "1")
        self.assertEqual(n["fxs"]["in"]["FpExtraRows"], "@fxa.ReturnValue"); self.assertEqual(n["fxz"]["in"]["FpExtraRows"], "0")
        # exec: the sum starts at 0 after ItemTable is loaded, the rest of the tables follow when the mods are through; a mod without the table goes on with the next
        ex = g["exec"]
        self.assertTrue(any(c[-6:] == ["ld%d" % i, "rn%d" % i, "fkx", "fxz", "fxm_s", "fm"] for c in ex), ex)   # fkx: Keep Loaded's row
        self.assertIn(["fm", "fx_bx"], ex); self.assertIn(["fx_bx", "fx_ld", "fx_ck"], ex); self.assertIn(["fx_ck", "fxr", "ff"], ex); self.assertIn(["ff", "fxe", "fxb", "fxs"], ex)
        self.assertTrue(any(c[0] == "fm:Completed" and c[-1] == "return" for c in ex), ex)
        self.assertEqual(n["fx_ck"].get("miss"), "ignore"); self.assertFalse(any(c[0] in ("fx_ck:CastFailed", "fxb:else") for c in ex))
        self.assertFalse(any("fm:Completed" in c[1:] for c in ex))

    def test_fingerprint_stays_engine_only(self):
        """The sum uses the loader's list and engine table calls: nothing of the game's classes, nothing of AltUI's own functions."""
        for x in self.fns["Game Fingerprint"]["graph"]["nodes"]:
            self.assertNotEqual(x["kind"], "call_self", x)
            self.assertFalse(str(x.get("class", "")).startswith("/Game/"), x)

    def test_every_merge_target_in_the_fingerprint_is_taken_out(self):
        """A table Merge Extra Tables writes to and the fingerprint counts needs its subtraction, or the gate trips on AltUI's own rows."""
        merge = [x["in"]["DestTable"] for x in self.fns["Merge Extra Tables"]["graph"]["nodes"] if x.get("function") == "AppendDataTableRow"]
        sub = {x["in"]["A"] for x in self.fns["Game Fingerprint"]["graph"]["nodes"] if x.get("function") == "Subtract_IntInt" and x["id"] != "fkd"}
        self.assertEqual(sub, {"@ln%d.ReturnValue" % compat_fp.FP_TABLES.index(t) for t in merge if t in compat_fp.FP_TABLES})
        # Keep Loaded's row (2026-11-16) comes off the result: the count less the mods' rows, less 1 once AltUI ran
        n = {x["id"]: x for x in self.fns["Game Fingerprint"]["graph"]["nodes"]}
        self.assertEqual(n["fkd"]["in"], {"A": "@fxd.ReturnValue", "B": "@fks.ReturnValue"}); self.assertEqual(n["fkx"]["in"]["RowName"], "AltUI_Keep")

    def test_begin_play_goes_through_the_gate(self):
        self.assertIn(["bp", "mfi", "vgt", "bvg"], self.eg["exec"])   # the file index first: the fingerprint reads it
        self.assertTrue(any(c[:2] == ["bvg", "cpc"] for c in self.eg["exec"]))
        self.assertIn(["sta", "cpc"], self.eg["exec"])

    def test_fingerprint_and_gate_touch_no_game_class(self):
        for fn in ("Game Fingerprint", "Version Gate", "Show Version Warning", "Version Continue", "Version Off"):
            with self.subTest(fn=fn):
                for n in self.fns[fn]["graph"]["nodes"]:
                    self.assertFalse(str(n.get("cls", "")).startswith("/Game/Project"), (fn, n))

    def test_expected_fingerprint_is_the_baseline(self):
        base = json.load(open(os.path.join(W, "knowledge", "compat_baseline.json")))
        n = {x["id"]: x for x in self.fns["Version Gate"]["graph"]["nodes"]}
        self.assertEqual(n["eq"]["in"]["B"], base["fingerprint"])
        self.assertEqual(len(base["fingerprint"].split(";")), len(compat_fp.FP_TABLES))


if __name__ == "__main__":
    unittest.main()
