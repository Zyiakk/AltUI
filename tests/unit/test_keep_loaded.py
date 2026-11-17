"""2026-11-16: the manager class with all it references (~16 MB of Blueprint) was loaded anew at every main menu and level start - the
2-3 s hang under the game's fade. One ItemTable row whose ActorClass is the manager class keeps it loaded until the game ends."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def load(f):
    with open(os.path.join(ASSETS, f)) as fh: return json.load(fh)["assets"]


def fn_graph(name):
    for f in ("30_manager.json", "50_manager_ui.json"):
        for a in load(f):
            for e in a.get("functions", []):
                if e.get("name") == name and e.get("graph"): return e["graph"]
    raise AssertionError(name)


class KeepLoaded(unittest.TestCase):
    def test_keep_table(self):
        t = [a for a in load("30_manager.json") if a.get("path") == "/Game/Mod/AltUI/AltUI_KeepLoaded"]
        self.assertEqual(len(t), 1)
        row = t[0]["rows"]["AltUI_Keep"]
        self.assertEqual(row["ActorClass"], "/Game/Mod/AltUI/BP_AltUIManager.BP_AltUIManager_C")
        self.assertEqual((row["Price"], row["HyperBoxGroup"]), (0, "None"))   # the game's vending machine takes Price > 0, the hyper box its groups

    def test_appended_once(self):
        g = fn_graph("Keep Loaded"); n = {x["id"]: x for x in g["nodes"]}
        self.assertEqual(n["ap"]["function"], "AppendDataTableRow"); self.assertEqual(n["ap"]["in"]["DestTable"], "/Game/Project/Tables/ItemTable")
        self.assertIn(["b:else", "ap"], g["exec"])

    def test_begin_play_calls_it_on_both_paths(self):
        eg = next(a for a in load("50_manager_ui.json") if a.get("event_graph") and a.get("path", "").endswith("BP_AltUIManager"))["event_graph"]
        main = next(c for c in eg["exec"] if c[:2] == ["bvg", "cpc"]); self.assertEqual(main[2], "kpl")   # before the main menu / level split (cj)
        self.assertIn(["sta", "cpc"], eg["exec"])

    def test_left_out_of_fingerprint_and_inventory(self):
        g = fn_graph("Game Fingerprint")
        self.assertTrue([x for x in g["nodes"] if x.get("function") == "DoesDataTableRowExist" and x["in"].get("RowName") == "AltUI_Keep"])
        inv = fn_graph("Inv Fill Cat"); self.assertIn(["fe", "bkp", "ir", "bg"], [c[:4] for c in inv["exec"]])


if __name__ == "__main__":
    unittest.main()
