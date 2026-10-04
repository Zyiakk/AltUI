"""Face tab core: FaceValues goes onto Jodi's mesh with SetMorphTarget (every face morph removed first, the entries set
with bRemoveZeroWeight = false), a row change edits FaceValues, and every place that replaces the mesh or the look
applies the face again."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
import face as fc

ASSETS = os.path.join(H, "..", "..", "assets")


def load(fname):
    with open(os.path.join(ASSETS, fname)) as f:
        return json.load(f)["assets"]


def fn_graph(name, files=("30_manager.json", "50_manager_ui.json")):
    for f in files:
        for a in load(f):
            for entry in a.get("functions", []):
                if entry.get("name") == name and entry.get("graph"):
                    return entry["graph"]
    raise AssertionError("function %s not found" % name)


def event_graph():
    for a in load("50_manager_ui.json"):
        if a.get("path", "").endswith("BP_AltUIManager") and a.get("event_graph"):
            return a["event_graph"]


def nodes(g, **kw):
    return [n for n in g["nodes"] if all(n.get(k) == v for k, v in kw.items())]


def in_exec(g, node_id):
    return any(node_id == s.split(":")[0] for chain in g.get("exec", []) for s in chain)


class FaceCore(unittest.TestCase):
    def test_apply_face(self):
        g = fn_graph("Apply Face"); sm = nodes(g, function="SetMorphTarget")
        removed = [n for n in sm if n["in"]["bRemoveZeroWeight"] == "true"]; kept = [n for n in sm if n["in"]["bRemoveZeroWeight"] == "false"]
        self.assertEqual(sorted(n["in"]["MorphTargetName"] for n in removed), sorted(fc.MORPHS))
        self.assertEqual(sorted(n["in"]["MorphTargetName"] for n in kept), sorted(fc.MORPHS))   # one per morph, only when set
        for n in sm: self.assertTrue(in_exec(g, n["id"]), n["id"])
        self.assertNotIn("Mouth_Close", [n["in"]["MorphTargetName"] for n in sm])   # virtual: folded into Mouth_AH

    def test_expressions_blend(self):
        g = fn_graph("Apply Face")
        self.assertTrue(nodes(g, kind="get", var="FaceAdd"))
        ah = next(n for n in nodes(g, function="SetMorphTarget") if n["in"]["MorphTargetName"] == "Mouth_AH CDG KN" and n["in"]["bRemoveZeroWeight"] == "false")
        sub = [n for n in g["nodes"] if n.get("function") == "Subtract_FloatFloat"]
        self.assertTrue(any(ah["in"]["Value"] == "@%s.ReturnValue" % n["id"] for n in sub))   # Mouth_AH = open - close
        for e in fc.EXPRESSIONS:
            s = next(n for n in nodes(g, function="SetMorphTarget") if n["in"]["MorphTargetName"] == e and n["in"]["bRemoveZeroWeight"] == "false")
            self.assertTrue(s["in"]["Value"].startswith("@"), e)

    def test_row_changed_covers_every_morph(self):
        g = fn_graph("Face Row Changed")
        names = {n["in"]["Value"] for n in nodes(g, function="MakeLiteralName")}
        self.assertTrue(set(fc.MORPHS) <= names)
        self.assertTrue(nodes(g, kind="call_self", function="Apply Face"))
        self.assertEqual({n["in"]["B"] for n in nodes(g, function="EqualEqual_NameName")}, {e[0] for e in fc.ENTRIES})

    def test_hooks_apply_the_face(self):
        for f in ("Apply Body", "Finish Apply Snapshot", "Face All Fixed", "Face All Game"):
            self.assertTrue(nodes(fn_graph(f), kind="call_self", function="Apply Face"), f)
        self.assertTrue(nodes(event_graph(), kind="call_self", function="Apply Face"))   # BeginPlay, at once (no level-load timer since 2026-09-29)

    def test_snapshots_carry_the_face(self):
        for f in ("Take Snapshot", "On Outfit Clicked"):
            mk = [n for n in fn_graph(f)["nodes"] if n.get("kind") == "make" and n.get("struct", "").endswith("S_Snapshot")]
            self.assertTrue(mk and all("Face" in n["in"] for n in mk), f)
        self.assertTrue(nodes(fn_graph("Finish Apply Snapshot"), kind="set", var="FaceValues"))

    def test_saved_on_close(self):
        g = fn_graph("Save Appearance Data"); self.assertTrue(nodes(g, kind="call_self", function="Save Settings"))

    def test_probe_is_gone(self):
        for f in ("30_manager.json", "50_manager_ui.json"):
            self.assertNotIn("Face Probe", open(os.path.join(ASSETS, f)).read())


if __name__ == "__main__":
    unittest.main()
