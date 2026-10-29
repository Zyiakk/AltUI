"""Applying a look names what it could not put on: besides clothes also eye and make-up rows that no table has any more
(the mod was removed or renamed its rows). Before, the game just skipped such a row and the eye colour (AltUI's own map)
came on alone - it looked as if the look had lost its eyes."""
import unittest, os, json

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")
P_EYE_T = "/Game/Project/Tables/EyeTable"; P_MAKEUP_T = "/Game/Project/Tables/MakeupTable"


def fn_graph(name):
    for f in ("30_manager.json", "50_manager_ui.json"):
        for a in json.load(open(os.path.join(ASSETS, f)))["assets"]:
            for entry in a.get("functions", []):
                if entry.get("name") == name and entry.get("graph"):
                    return entry["graph"]
    raise AssertionError("function %s not found" % name)


def succ(g):
    """exec successors: source (node id or "id:pin") -> ids of the next nodes."""
    out = {}
    for chain in g["exec"]:
        for a, b in zip(chain, chain[1:]):
            out.setdefault(a, set()).add(b.split(":")[0])
    return out


def reachable(g, start, goal):
    s, seen, todo = succ(g), set(), [start]
    while todo:
        x = todo.pop()
        if x == goal: return True
        if x in seen: continue
        seen.add(x); todo += list(s.get(x, ())) + list(s.get(x + ":else", ())) + list(s.get(x + ":Completed", ()))
    return False


class LookMissing(unittest.TestCase):
    def setUp(self):
        self.g = fn_graph("Finish Apply Snapshot"); self.by = {n["id"]: n for n in self.g["nodes"]}

    def test_rows_of_the_snapshots_makeup_map_are_checked_against_both_tables(self):
        self.assertEqual(self.by["mkk"]["in"]["TargetMap"], "@bs.Makeup")
        tables = {self.by[i]["in"]["Table"] for i in ("mxe", "mxm")}
        self.assertEqual(tables, {P_EYE_T, P_MAKEUP_T})
        self.assertEqual(self.by["bmx"]["in"]["Condition"], "@mxo.ReturnValue")

    def test_a_missing_row_goes_into_the_popup_list(self):
        self.assertEqual(self.by["mxa"]["in"]["TargetArray"], "@gpmx.PendingMissing")
        self.assertIn(["bmx:else", "mxa"], self.g["exec"])

    def test_the_check_runs_before_the_popup(self):
        self.assertIn(["fmk:Completed", "snt", "bms"], self.g["exec"])
        self.assertTrue(reachable(self.g, "entry", "fmk"), "the check is not on the path of Finish Apply Snapshot")


if __name__ == "__main__":
    unittest.main()
