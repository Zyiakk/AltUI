"""W_FaceRow: one entry of the face tab. Its tick reports a moved slider (which also ticks the box) or a flipped box
to Manager.Face Row Changed; Set State takes the manager's value without echoing it back."""
import unittest, os, json
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")


def widget():
    with open(os.path.join(ASSETS, "40_widgets.json")) as f:
        for a in json.load(f)["assets"]:
            if a.get("path") == "/Game/Mod/AltUI/W_FaceRow": return a
    raise AssertionError("W_FaceRow missing")


class FaceRow(unittest.TestCase):
    def test_functions(self):
        names = {f["name"] for f in widget()["functions"]}
        self.assertTrue({"Init", "Set State", "Slider Pos", "Slider Value", "Update Look", "Tick", "Compute Colors"} <= names)

    def test_tick_reports(self):
        tk = next(f for f in widget()["functions"] if f["name"] == "Tick")["graph"]
        rep = [n for n in tk["nodes"] if n.get("function") == "Face Row Changed"]
        self.assertEqual(len(rep), 1)
        moved = [n for n in tk["nodes"] if n.get("function") == "Set State" and n["in"].get("fixed") == "true"]
        self.assertEqual(len(moved), 1)   # a moved slider ticks the box


if __name__ == "__main__":
    unittest.main()
