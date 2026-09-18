"""Error exits of a graph must be wired or explicitly waived: a `get_row` whose `Row Not Found` pin and an impure
`cast` whose `CastFailed` pin are not in any exec chain silently end the function there (2026-09-15: `Apply Snapshot`
stopped half-way when the look's hairstyle row was missing). `"miss": "ignore"` on the node documents that ending
the chain is the intended behaviour (typically: loop body over the table's own row names, or "nothing to do").
A node with exec pins that is in no chain never runs: a `set`, `branch` or `foreach` declared but not chained is dead
code (2026-09-18: `Rebuild List` declared the `CachedOnlyVanilla` set without chaining it, so the tick saw a changed
check box every frame and rebuilt the list endlessly - the game froze)."""
import unittest, os, sys, glob, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
sys.path.insert(0, H); from test_graph_ids import graphs, ASSETS

EXITS = {"get_row": "Row Not Found", "cast": "CastFailed", "class_cast": "CastFailed"}


def unwired_exits(g):
    """[(id, pin)] of error exits that are neither chained nor waived"""
    chained = {step for chain in g["exec"] for step in chain[:-1]}
    out = []
    for n in g["nodes"]:
        pin = EXITS.get(n["kind"])
        if not pin or n.get("miss") == "ignore": continue
        if n["kind"] != "get_row" and n.get("pure", True): continue   # pure casts have no exec pins
        if "%s:%s" % (n["id"], pin) not in chained: out.append((n["id"], pin))
    return out


EXEC_KINDS = {"set", "branch", "foreach", "spawn", "macro"}


def unchained_nodes(g):
    """ids of exec-carrying nodes that appear in no exec chain"""
    chained = {step.split(":")[0] for chain in g["exec"] for step in chain}
    return [n["id"] for n in g["nodes"] if n["kind"] in EXEC_KINDS and n["id"] not in chained]


class GraphPaths(unittest.TestCase):
    def test_unchained_node_is_detected(self):
        g = {"nodes": [{"id": "s1", "kind": "set"}, {"id": "s2", "kind": "set"}, {"id": "b", "kind": "branch"}, {"id": "v", "kind": "get"}], "exec": [["entry", "s1", "b"], ["b:else", "s1"]]}
        self.assertEqual(unchained_nodes(g), ["s2"])

    def test_generated_assets_chain_every_exec_node(self):
        files = sorted(glob.glob(os.path.join(ASSETS, "*.json"))); self.assertTrue(files)
        for f in files:
            for g in graphs(json.load(open(f))):
                self.assertEqual(unchained_nodes(g), [], os.path.basename(f) + " " + ", ".join(n["id"] for n in g["nodes"][:3]))

    def test_unwired_exit_is_detected(self):
        g = {"nodes": [{"id": "row", "kind": "get_row"}, {"id": "c", "kind": "cast", "pure": False}, {"id": "p", "kind": "cast", "pure": True}], "exec": [["entry", "row", "c"]]}
        self.assertEqual(unwired_exits(g), [("row", "Row Not Found"), ("c", "CastFailed")])
        g["exec"].append(["row:Row Not Found", "c"]); g["nodes"][1]["miss"] = "ignore"
        self.assertEqual(unwired_exits(g), [])

    def test_generated_assets_wire_or_waive_error_exits(self):
        files = sorted(glob.glob(os.path.join(ASSETS, "*.json"))); self.assertTrue(files)
        for f in files:
            for g in graphs(json.load(open(f))):
                self.assertEqual(unwired_exits(g), [], os.path.basename(f) + " " + ", ".join(n["id"] for n in g["nodes"][:3]))
