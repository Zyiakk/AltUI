"""Face tab page: a tab after Body Shape, the page rebuilt on select, a group click, one W_FaceRow per entry of the
chosen group with its state from FaceValues, the two links, the note, and the saved faces (tiles, menu, photo)."""
import unittest, os, sys, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, "..", "..", "assets", "gen"))
import face as fc
from test_face_core import fn_graph, nodes, in_exec, load


class FacePage(unittest.TestCase):
    def test_tab_and_page(self):
        g = fn_graph("Rebuild TopTabs"); pages = [n["in"].get("page") for n in g["nodes"] if n.get("function") == "Init"]
        self.assertEqual(pages.index("Face"), pages.index("Body") + 1)
        self.assertTrue(nodes(fn_graph("Select Page"), kind="call_self", function="Rebuild Face Page"))
        self.assertTrue(nodes(fn_graph("Select Slot"), kind="call_self", function="Select Face Group"))
        sp = next(f for a in load("40_widgets.json") if a.get("path", "").endswith("/W_AltUI") for f in a["functions"] if f["name"] == "Set Page")["graph"]
        self.assertIn("Face", [n["in"]["B"] for n in sp["nodes"] if n.get("function") == "EqualEqual_NameName"])

    def test_groups(self):
        g = fn_graph("Rebuild Face Groups")
        self.assertEqual([n["in"]["slot"] for n in g["nodes"] if n.get("function") == "Init"], fc.GROUPS + [fc.SAVED])

    def test_rows(self):
        g = fn_graph("Rebuild Face Right")
        inits = [n for n in g["nodes"] if n.get("function") == "Init" and n.get("class", "").endswith("W_FaceRow")]
        self.assertEqual([n["in"]["key"] for n in inits], [e[0] for e in fc.ENTRIES])
        for n in inits: self.assertTrue(in_exec(g, n["id"]))
        self.assertEqual(len([n for n in g["nodes"] if n.get("function") == "Set State"]), len(fc.ENTRIES))
        self.assertEqual({n["in"]["action"] for n in g["nodes"] if n.get("function") == "Init" and n.get("class", "").endswith("W_TextButton")}, {"FaceAllFixed", "FaceAllGame", "FaceAddToggle"})
        self.assertTrue(nodes(g, function="K2_GetAllMorphTargetNames"))

    def test_saved_faces(self):
        self.assertIn(fc.FACES_SLOT, json.dumps(fn_graph("Load Faces"))); self.assertIn(fc.FACES_SLOT, json.dumps(fn_graph("Save Faces")))
        self.assertTrue(nodes(fn_graph("On Face Clicked"), kind="call_self", function="Add Face"))
        self.assertTrue(nodes(fn_graph("Apply Saved Face"), kind="call_self", function="Apply Face"))
        cap = fn_graph("Capture Face Photo"); self.assertIn("Face_", json.dumps(cap)); self.assertTrue(nodes(cap, kind="set", var="PhotoKind"))
        self.assertTrue(nodes(fn_graph("Finish Photo"), kind="call_self", function="Rebuild Face Page"))
        btn = next(a for a in load("40_widgets.json") if a.get("path") == "/Game/Mod/AltUI/W_FaceButton")
        md = next(f for f in btn["functions"] if f["name"] == "OnMouseButtonDown")["graph"]
        self.assertEqual({n.get("function") for n in md["nodes"] if n.get("kind") == "call"} & {"On Face Clicked", "On Face Context"}, {"On Face Clicked", "On Face Context"})


if __name__ == "__main__":
    unittest.main()
