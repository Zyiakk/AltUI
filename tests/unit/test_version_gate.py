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

    def test_begin_play_goes_through_the_gate(self):
        self.assertIn(["bp", "vgt", "bvg"], self.eg["exec"])
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
